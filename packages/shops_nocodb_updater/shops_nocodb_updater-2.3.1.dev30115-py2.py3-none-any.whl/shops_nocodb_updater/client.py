import asyncio
import inspect
import logging
import mimetypes
import os  # Add this import for file operations
from datetime import datetime
from typing import List, Type, get_origin, get_args, ForwardRef, Dict, Optional, Union, Any, TypeVar, cast
import httpx
from pydantic import HttpUrl
from enum import Enum
from io import BytesIO, BufferedReader
from typing import cast

from shops_nocodb_updater.models.shop_models import ShopCategory, ShopProduct
from shops_nocodb_updater.models.base import NocodbModel, AttachmentObject
from shops_nocodb_updater.models.types import LongText
from shops_nocodb_updater.utils import download_image, needs_update

# Set default timeouts (in seconds)
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)

T = TypeVar('T', bound=NocodbModel)

class NocodbClient:
    """
    Client for interacting with NocoDB API.
    Provides methods for CRUD operations and syncing external records.
    """
    
    def __init__(
        self,
        nocodb_host: str,
        api_key: str,
        project_id: str,
        api_version: str = "v1",
        request_delay: float = 0.5,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the NocoDB client.
        
        Args:
            nocodb_host: The NocoDB host
            api_key: The API key
            project_id: The project ID
            api_version: The API version to use (default: "v1")
            logger: Optional logger
        """
        self.NOCODB_HOST = nocodb_host
        self.API_KEY = api_key
        self.project_id = project_id
        self.API_VERSION = api_version
        self.language = "EN"  # Default language
        self.custom_fields = {HttpUrl: {"func": ["isURL"], "args": [""], "msg": ["Validation failed : isURL"]}}
        
        self.logger = logger or logging.getLogger(__name__)
        
        self.httpx_client = httpx.AsyncClient(
            headers={
                "xc-token": self.API_KEY,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        self.batch_size = 50
        self._cached_existing_lookup_maps: dict[str, dict[str, dict]] = {}  # {table_id: {external_id: record, ...}, ...}
        self._id_maps: dict[str, dict[str, dict]] = {}                      # {table_id: {external_id: record, ...}, ...}

        self.request_delay = request_delay 
        
        
    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if self.request_delay:
            await asyncio.sleep(self.request_delay)
        return await self.httpx_client.request(method, url, **kwargs)
    
    def construct_get_params(
        self,
        required_fields: Optional[list] = None,
        projection: Optional[list] = None,
        extra_where: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        """
        Construct query parameters for GET requests.
        
        Args:
            required_fields: Fields that must not be null
            projection: Fields to include in the response
            extra_where: Additional where conditions
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Dictionary of query parameters
        """
        extra_params = {}
        if projection:
            extra_params["fields"] = ",".join(projection)
        if required_fields:
            extra_params["where"] = ""
            for field in required_fields:
                extra_params["where"] += f"({field},isnot,null)~and"
            extra_params["where"] = extra_params["where"].rstrip("~and")
        if extra_where:
            if not extra_params.get("where"):
                extra_params["where"] = extra_where
            else:
                extra_params["where"] += f"~and{extra_where}"
        if offset:
            extra_params["offset"] = str(offset)
        if limit:
            extra_params["limit"] = str(limit)
        return extra_params
    
    def map_pydantic_type_to_nocodb_type(self, field_type: type) -> str:
        """Maps Pydantic field types to NocoDB column types."""
        type_mapping = {
            str: "SingleLineText",
            int: "Number",
            float: "Decimal",
            bool: "Checkbox",
            dict: "JSON",
            list: "JSON",
            List: "JSON",
            Dict: "JSON",
            HttpUrl: "URL",
            LongText: "LongText",
            AttachmentObject: "Attachment"
        }
        
        # Handle Enum types
        if inspect.isclass(field_type) and issubclass(field_type, Enum):
            return "SingleSelect"
            
        origin_type = get_origin(field_type)
        if origin_type in type_mapping:
            return type_mapping[origin_type]

        # Fallback to the base type if it's directly in the mapping
        if field_type in type_mapping:
            return type_mapping[field_type]
        # Default to text if type is not explicitly mapped
        return type_mapping.get(field_type, "SingleLineText")

    def resolve_forward_ref(self, field_type, global_ns=None, local_ns=None):
        """Resolves ForwardRef to the actual type."""
        if isinstance(field_type, ForwardRef):
            recursive_guard = set()  # Initialize the recursive guard
            field_type = _eval_type(field_type, global_ns, local_ns, recursive_guard)
        return field_type

    def map_pydantic_type_to_nocodb_type_dt(self, field_type: type) -> str:
        """Maps Pydantic field types to NocoDB column types."""
        type_mapping = {
            str: "TEXT",
            int: "bigint",
            float: "decimal",
            bool: "boolean",
            dict: "json",
            list: "json",
            List: "json",
            Dict: "json",
            HttpUrl: "text"
        }
        origin_type = get_origin(field_type)
        if origin_type in type_mapping:
            return type_mapping[origin_type]

        # Fallback to the base type if it's directly in the mapping
        if field_type in type_mapping:
            return type_mapping[field_type]
        # Default to text if type is not explicitly mapped
        return type_mapping.get(field_type, "text")

    def get_enum_options(self, field_type: type) -> list:
        """Get options for enum type fields."""
        if not (inspect.isclass(field_type) and issubclass(field_type, Enum)):
            return []
            
        options = []
        for i, member in enumerate(field_type):
            options.append({
                "title": member.value,
                "color": "#cfdffe",  # Default color, can be customized
                "order": i + 1
            })
        return options

    async def get_table_records(self, table_id: str, filter_string: str = "") -> List[dict]:
        """Fetches all records from the NocoDB table."""
        records = []
        offset = 0
        limit = 100
        while True:
            result = await self.get_table_records_paginated(
                table_id,
                offset=offset,
                limit=limit,
                filter_string=filter_string
            )
            records.extend(result["list"])
            if result["pageInfo"]["isLastPage"]:
                break
            offset += limit
        return records

    async def count_table_records(self, table_name: str) -> int:
        url = f"{self.NOCODB_HOST}/api/v2/tables/{table_name}/records/count"
        response = await self._request("GET", url)
        if response.status_code == 200:
            return response.json().get("count", 0)
        raise Exception(response.text)
    
    def get_custom_field_data(self, field_type: Union[Type[Any], HttpUrl]) -> dict:
        """Get custom field data for a given field type"""
        http_url_origin = get_origin(HttpUrl) or HttpUrl
        if isinstance(field_type, type) and issubclass(field_type, http_url_origin):
            return self.custom_fields.get(HttpUrl, {})
        return {}

    def __get_type_declaration__(self, model: Type[NocodbModel], field_name: str, field_type: Type) -> dict:
        # Handle regular 
        origin = get_origin(field_type)
        args = get_args(field_type)
        column_name = field_name.replace(" ", "_").lower()
        self.logger.debug(f"Got check for {column_name} which has origin {origin} and args {args}")
        if args:
            self.logger.debug(f"RES {origin in (list, List)} ------ {args} ------ {inspect.isclass(args[0]) } ------ {issubclass(args[0], Enum)}")
        if inspect.isclass(field_type) and issubclass(field_type, NocodbModel):
            target_table_id = field_type.__tableid__
            target_table_title = field_type.__name__  # Use the model name as the table title
            target_table_column = f"{field_type.__tableid__}_id"  # Example of a target table column format
            target_table_view_id = None  # Assuming no specific view ID, modify if needed

            return {
                "custom": self.get_custom_field_data(field_type),
                "title": field_name,
                "column_name": column_name,
                "uidt": "LinkToAnotherRecord",
                "userHasChangedTitle": False,
                "meta": {
                    "fk_related_model_id": target_table_id,
                    "fk_related_model_column": target_table_column,
                    "fk_related_model_title": target_table_title,
                    "fk_related_model_view_id": target_table_view_id
                },
                "rqd": False,
                "pk": False,
                "ai": False,
                "cdf": None,
                "un": False,
                "dtx": "specificType",
                "dt": "varchar",
                "dtxp": "",
                "dtxs": " ",
                "altered": 2,
                "table_name": model.__tableid__,  # Use tableid instead of metadata
                # "view_id": None,  # We don't need view_id for type declaration
            }

        # Handle AttachmentObject type
        elif inspect.isclass(field_type) and issubclass(field_type, AttachmentObject):
            return {
                "custom": {},
                "title": field_name,
                "column_name": column_name,
                "uidt": "Attachment",
                "userHasChangedTitle": False,
                "meta": {"defaultViewColOrder": 10},
                "rqd": False,
                "pk": False,
                "ai": False,
                "cdf": None,
                "un": False,
                "dtx": "specificType",
                "dt": "text",
                "dtxp": "",
                "dtxs": " ",
                "altered": 8,
                "table_name": model.__tableid__,
                # "view_id": None,
                "base_id": self.project_id
            }

        elif origin in (list, List) and args and inspect.isclass(args[0]) and issubclass(args[0], Enum):
            # Handle Enum types
            enum_class = args[0]
            options = self.get_enum_options(enum_class)
            dtxp = ",".join([f"'{opt['title']}'" for opt in options])
            return {
                "custom": {},
                "title": field_name,
                "column_name": column_name,
                "uidt": "MultiSelect",
                "dt": "text",
                "dtx": "specificType",
                "dtxp": dtxp,
                "dtxs": " ",
                "altered": 2,
                "table_name": model.__tableid__,
                "meta": {},
                "rqd": False,
                "pk": False,
                "ai": False,
                # "cdf": None,
                "cdf": False,
                "un": False,
                "colOptions": {
                    "options": options
                },
                "extra": {
                    "options": options,
                    "optionsMap": {opt["title"]: opt for opt in options}
                }
            }

        # Single Enum
        elif inspect.isclass(field_type) and issubclass(field_type, Enum):
            options = self.get_enum_options(field_type)
            return {
                "custom": self.get_custom_field_data(field_type),
                "title": field_name,
                "column_name": column_name,
                "uidt": "SingleSelect",
                "dt": "text",
                "dtx": "specificType",
                "dtxp": f"'{options[0]['title']}'" if options else "",
                "dtxs": "",
                "altered": 2,
                "table_name": model.__tableid__,
                "meta": {},
                "rqd": False,
                "pk": False,
                "ai": False,
                "cdf": None,
                "un": False,
                "colOptions": {
                    "options": options
                }
            }
        
        elif origin == list:
            linked_model_type = get_args(field_type)[0]
            linked_model_type = self.resolve_forward_ref(linked_model_type, global_ns=globals(), local_ns=locals())
            if inspect.isclass(linked_model_type) and issubclass(linked_model_type, NocodbModel):
                target_table_id = linked_model_type.__tableid__
                target_table_title = linked_model_type.__name__  # Use the model name as the table title
                target_table_column = f"{linked_model_type.__tableid__}_id"  # Example of a target table column format
                target_table_view_id = None  # Assuming no specific view ID, modify if needed

                return {
                    "custom": self.get_custom_field_data(field_type),
                    "title": field_name,
                    "column_name": column_name,
                    "uidt": "LinkToAnotherRecord",
                    "userHasChangedTitle": False,
                    "meta": {
                        "fk_related_model_id": target_table_id,
                        "fk_related_model_column": target_table_column,
                        "fk_related_model_title": target_table_title,
                        "fk_related_model_view_id": target_table_view_id,
                        "is_mm": True
                    },
                    "rqd": False,
                    "pk": False,
                    "ai": False,
                    "cdf": None,
                    "un": False,
                    "dtx": "specificType",
                    "dt": "varchar",
                    "dtxp": "",
                    "dtxs": " ",
                    "altered": 2,
                    "table_name": model.__tableid__,  # Use tableid instead of metadata
                    # "view_id": None,  # We don't need view_id for type declaration
                }
        elif field_type == datetime:
            return {
                "custom": self.get_custom_field_data(field_type),
                "title": field_name,
                "column_name": column_name,
                "uidt": "DateTime",
                "userHasChangedTitle": False,
                "meta": {
                    "date_format": "YYYY-MM-DD",
                    "time_format": "HH:mm",
                    "is12hrFormat": False
                },
                "rqd": False,
                "pk": False,
                "ai": False,
                "cdf": None,
                "un": False,
                "dtx": "specificType",
                "dt": "timestamp",
                "dtxp": "",
                "dtxs": " ",
                "altered": 2,
                "table_name": model.__tableid__
            }
        

        return {
            "custom": self.get_custom_field_data(field_type),
            "title": field_name,
            "column_name": column_name,
            "uidt": self.map_pydantic_type_to_nocodb_type(field_type),
            "userHasChangedTitle": False,
            "meta": {},
            "rqd": False,
            "pk": False,
            "ai": False,
            "cdf": None,
            "un": False,
            "dtx": "specificType",
            "dt": self.map_pydantic_type_to_nocodb_type_dt(field_type),
            "dtxp": "",
            "dtxs": " ",
            "altered": 2,
            "table_name": model.__tableid__,  # Use tableid instead of metadata
            # "view_id": None,  # We don't need view_id for type declaration
        }
    
    def merge_fields_before_update(self, existing_column: dict, type_declaration: dict, field_type: type) -> dict:
        """Merges fields before updating a column."""

        if field_type == AttachmentObject:
            type_declaration = {**existing_column, **type_declaration}

        return type_declaration

    async def apply_migrations(
            self,
            model: T,
            migrate_existing_columns: bool = False,
            create_new_columns: bool = False,
            language: str = "EN",
    ) -> None:
        """Initializes a table schema based on the provided Pydantic model."""
        if not model.__metadata__:
            model.__metadata__ = await self.get_table_metadata(model.__tableid__)
        existing_columns = {col["title"]: col for col in model.__metadata__["columns"]}
        existing_column_names = {col["column_name"]: col for col in model.__metadata__["columns"]}

        for field_name, field_type in model.__nocodb_table_schema__(lang=language).items():
            self.logger.debug(f"Checking schema column for {field_name}")
            type_declaration = self.__get_type_declaration__(type(model), field_name, field_type)
            existing_column_data = existing_columns.get(field_name) or existing_column_names.get(type_declaration["column_name"])
            if existing_column_data:
                if self.record_needs_update(existing_column_data, type_declaration, exlude_fields=["meta", "dtxp", "dtxs"]):
                    self.logger.warning(f"Column {field_name} needs update of type {field_type}")
                    if migrate_existing_columns:
                        # Possible we need to set fk_model_id if it's a link to another record
                        type_declaration = self.merge_fields_before_update(
                            existing_column_data,
                            type_declaration,
                            field_type)
                        self.logger.warning(f"Type declaration for '{field_name}' is {type_declaration}")
                        await self.update_column(existing_column_data["id"], type_declaration)
                    else:
                        raise Exception(f"Column {field_name} requires type update")
            else:
                self.logger.debug(f"Column '{field_name}' does not exist")
                if create_new_columns:
                    await self.create_column(model.__tableid__, type_declaration)

    async def update_record(self, table_id: str, record_id: str, record_data: dict) -> dict:
        """Update a record in NocoDB
        
        Args:
            table_id: The table ID
            record_id: The record ID
            record_data: The record data to update
            
        Returns:
            The updated record
        """
        if not record_id:
            raise ValueError("record_id cannot be None")
            
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/data/v1/{self.project_id}/{table_id}/{record_id}"
        response = await self._request("PATCH", url, json=record_data)
        if response.status_code != 200:
            raise Exception(response.text)
        return response.json()

    async def create_table_record(self, table_id: str, record: dict, external_id_field: str) -> None:
        """
        Create a new record in a table.
        
        Args:
            table_id: The table ID
            record: The record data
            external_id_field: External ID field name
        """
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/data/{table_id}/records"
        record_data = record.copy()
        external_id = record.get("id", "")
        if external_id:
            record_data[external_id_field] = external_id
        
        response = await self._request("POST", url, json=record_data)
        if response.status_code != 200:
            raise Exception(response.text)

    async def delete_table_record(self, table_name: str, records_id: List[int]) -> dict:
        """
        Delete a record from a table.
        
        Args:
            table_name: The table name or ID
            record_id: The record ID
            
        Returns:
            The response data
        """
        list_payload = [{"Id": record_id} for record_id in records_id]
        url = f"{self.NOCODB_HOST}/api/v2/tables/{table_name}/records"
        response = await self._request("DELETE", url, json=list_payload)
        return response.json()
    
    async def get_project_metadata(self) -> dict:
        """
        Get the project metadata.
        
        Returns:
            The project metadata
        """
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/meta/projects/{self.project_id}/tables?includeM2M=false"
        response = await self._request("GET", url)
        if response.status_code == 200:
            return response.json()
        raise Exception(response.text)

    async def get_table_metadata(self, table_id: str) -> dict:
        """
        Get a table metadata.
        
        Args:
            table_id: The table ID
            
        Returns:
            The table metadata
        """
        if self.API_VERSION == "v1":
            url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/meta/tables/{table_id}"
        else:
            url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/tables/{table_id}"
            
        response = await self._request("GET", url)
        if response.status_code == 200:
            return response.json()
        raise Exception(response.text)

    async def create_column(self, table_id: str, column_data: dict) -> dict:
        """
        Create a column in a table.
        
        Args:
            table_id: The table ID
            column_data: The column data
            
        Returns:
            The response data
        """
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/meta/tables/{table_id}/columns"
        response = await self._request("POST", url, json=column_data)
        if response.status_code == 200:
            return response.json()
        raise Exception(response.text)

    async def update_column(self, column_id: str, column_data: dict) -> dict:
        """
        Update an existing column in a table.
        
        Args:
            column_id: The ID of the column to update
            column_data: The updated column data
            
        Returns:
            The response data
        """
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/meta/columns/{column_id}"
        response = await self._request("PATCH", url, json=column_data)

        if response.status_code == 200:
            return response.json()

        raise Exception(f"Error: {response.status_code}, Response: {response.text}")

    async def ensure_external_id_column(self, table_id: str, external_id_field: str) -> None:
        """
        Ensure the external ID column exists in the table.
        
        Args:
            table_id: The table ID
            external_id_field: The external ID field name
        """
        try:
            metadata = await self.get_table_metadata(table_id)
            column_list = metadata.get("columns", [])
            
            # Check if the column already exists
            existing_columns = [col.get("column_name") for col in column_list]
            if external_id_field in existing_columns:
                self.logger.debug(f"Column {external_id_field} already exists")
                return
                
            # Create the column if it doesn't exist
            self.logger.info(f"Creating external ID column: {external_id_field}")
            await self.create_column(
                table_id,
                {
                    "column_name": external_id_field,
                    "title": "External ID",
                    "uidt": "SingleLineText"
                },
            )
        except Exception as e:
            # If the error is about duplicate column, we can ignore it
            if "Duplicate column" in str(e):
                self.logger.debug(f"Column {external_id_field} already exists (detected from error)")
                return
            # Otherwise, re-raise the exception
            raise

    async def get_table_records_paginated(
            self,
            table_id: str,
            offset: int = 0,
            limit: int = 100,
            filter_string: str = ""
    ) -> dict:
        """Fetches a paginated list of records from the NocoDB table."""
        url = f"{self.NOCODB_HOST}/api/v2/tables/{table_id}/records"
        params = self.construct_get_params(
            offset=offset,
            limit=limit,
            extra_where=filter_string,
        )
        response = await self._request("GET", url, params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(response.text)
    
    async def upload_file_to_nocodb(self, table_id: str, column_id: str, file_name: str, file_path: Optional[str] = None, file_buffer: Optional[BytesIO] = None):
        """
        Upload a file to NocoDB for an attachment field
        
        Args:
            table_id: The NocoDB table ID
            column_name: The column name for the attachment
            file_path: Path to the file to upload or file_buffer is required
            file_buffer: File bytes or file_path is required
            file_name: File name containing hash prefix
        
        Returns:
            dict: Attachment metadata from NocoDB
        """
        # Construct the upload URL
        upload_path = f"noco/{self.project_id}/{table_id}/{column_id}"
        upload_url = f"{self.NOCODB_HOST}/api/v1/db/storage/upload?path={upload_path}"
        
        self.logger.info(f"Uploading file to NocoDB: {upload_url}")
        
        if file_path:
            files = {
                "files": (
                    file_name, 
                    open(file_path, "rb"), 
                    mimetypes.guess_type(file_path)[0] or "application/octet-stream"
                )
            }
        elif file_buffer:
            file_buffer.seek(0)

            files = {
                "files": (
                    file_name,
                    cast(BufferedReader, file_buffer),
                    mimetypes.guess_type(file_name)[0] or "application/octet-stream"
                )
            }
        else:
            raise Exception(f"One of required file_buffer or file_path")

        headers = self.httpx_client.headers.copy()
        headers.pop("Content-Type", None)
        response = await httpx.AsyncClient().post(
            upload_url,
            files=files,
            headers=headers,
            timeout=30,
        )
        if response.status_code != 200:
            error_text = response.text
            raise ValueError(f"Failed to upload file: {response.status_code} - {error_text}")
        
        result = response.json()
        self.logger.info(f"File upload successful: {result}")
        return result[0]

    def is_duplicate_attachment(self, existing_attachment: dict, new_attachment: dict) -> bool:
        """
        Check if an attachment is a duplicate by comparing key fields.
        
        Args:
            existing_attachment: Existing attachment data
            new_attachment: New attachment data
            
        Returns:
            True if attachments are duplicates, False otherwise
        """
        # Compare key fields that identify a unique attachment
        if new_attachment.get('path'):
            # We are comparing temporary file with existing attachment
            if existing_attachment['title'] == new_attachment['title']:
                # we must upload new attachment and fill url field in new_attachment
                return True
            return False
        else:
            key_fields = ['url', 'title', 'mimetype']
            for field in key_fields:
                self.logger.debug(f"Attachment missing field {field}, skipping duplicate check")
                # if field not in existing_attachment or field not in new_attachment:
                #     self.logger.debug(f"Attachment missing field {field}, skipping duplicate check")
                #     return False
                if existing_attachment[field] != new_attachment[field]:
                    self.logger.debug(f"Attachment {field} mismatch: {existing_attachment[field]} != {new_attachment[field]}")
                    return False
        return True

    def record_needs_update(self, nocodb_record: dict, external_record: dict, exlude_fields: Optional[list[str]] = None) -> bool:
        """Check if a record needs to be updated based on field values"""
        if exlude_fields is None:
            exlude_fields = []
        for field, value in external_record.items():
            if field in exlude_fields:
                continue
            if field not in nocodb_record:
                continue
            if type(nocodb_record[field]) == dict:
                return self.record_needs_update(nocodb_record[field], value, exlude_fields=exlude_fields)
            elif type(nocodb_record[field]) == list and type(value) == list:
                # Special handling for attachment lists
                if field.lower() in ['images', 'image', 'attachments']:
                    # Check if all new attachments exist in the current list
                    for new_attachment in value:
                        found = False
                        for existing_attachment in nocodb_record[field]:
                            if self.is_duplicate_attachment(existing_attachment, new_attachment):
                                found = True
                                break
                        if not found:
                            self.logger.debug(f"New attachment found: {new_attachment}")
                            return True
                    # Check if all current attachments exist in the new list
                    for existing_attachment in nocodb_record[field]:
                        found = False
                        for new_attachment in value:
                            if self.is_duplicate_attachment(existing_attachment, new_attachment):
                                found = True
                                break
                        if not found:
                            self.logger.debug(f"Attachment removed: {existing_attachment}")
                            return True
                else:
                    # For non-attachment lists, compare each element
                    for i in range(len(value)):
                        return self.record_needs_update(nocodb_record[field][i], value[i], exlude_fields=exlude_fields)
            elif nocodb_record[field] != value:
                self.logger.debug(f"Record needs update for {field} {nocodb_record[field]} ---> {value}")
                return True
        return False

    def format_external_record(self, external_record: dict, m2m_column_names: List[str]) -> dict:
        """
        Format an external record for NocoDB compatibility.
        
        Args:
            external_record: The external record
            m2m_column_names: Names of many-to-many columns to skip
            
        Returns:
            Formatted record
        """
        return {k: v for k, v in external_record.items() if k not in m2m_column_names}
        
    async def link_table_record(
        self, 
        base_id: str, 
        fk_model_id: str, 
        record_id: str, 
        source_column_id: str, 
        linked_record_id: str
    ) -> dict:
        """
        Link two records together.
        
        Args:
            base_id: The ID of the database base
            fk_model_id: The ID of the linked model
            record_id: The ID of the source record
            source_column_id: The ID of the source column
            linked_record_id: The ID of the linked record
            
        Returns:
            The response data
        """
        path = f"/api/v1/db/data/noco/{base_id}/{fk_model_id}/{record_id}/mm/{source_column_id}/{linked_record_id}"
        response = await self._request("POST", self.NOCODB_HOST + path)
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to link records: {response.text}")
        raise Exception(response.text)
        
    async def unlink_table_record(
        self, 
        base_id: str, 
        fk_model_id: str, 
        record_id: str, 
        source_column_id: str, 
        linked_record_id: str
    ) -> dict:
        """
        Unlink two records.
        
        Args:
            base_id: The ID of the database base
            fk_model_id: The ID of the linked model
            record_id: The ID of the source record
            source_column_id: The ID of the source column
            linked_record_id: The ID of the linked record
            
        Returns:
            The response data
        """
        path = f"/api/v1/db/data/noco/{base_id}/{fk_model_id}/{record_id}/mm/{source_column_id}/{linked_record_id}"
        response = await self._request("DELETE", self.NOCODB_HOST + path)
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to unlink records: {response.text}")
        raise Exception(response.text)

    async def get_linked_records(
            self,
            base_id: str,
            fk_model_id: str,
            record_id: str,
            source_column_id: str
    ):
        """
        Fetch linked records for a given source record and column, handling pagination.

        Parameters:
        - base_id: The ID of the database base.
        - fk_model_id: The ID of the linked column.
        - record_id: The ID of the source record.
        - source_column_id: The ID of the source column.

        Returns:
        - A list of all linked records.

        Raises:
        - Exception if the request fails.
        """
        path = f"/api/v1/db/data/noco/{base_id}/{fk_model_id}/{record_id}/mm/{source_column_id}"
        limit = 30
        offset = 0
        all_records = []

        while True:
            # Construct the query with limit and offset for pagination
            query = f"?limit={limit}&offset={offset}"
            response = await self._request("GET", self.NOCODB_HOST + path + query)

            if response.status_code == 200:
                data = response.json()
                records = data.get("list", [])
                all_records.extend(records)

                # Check if we've retrieved all records
                if data.get("pageInfo", {}).get("isLastPage", False):
                    break

                # Increment offset for the next batch of records
                offset += limit
            else:
                raise Exception(f"Failed to fetch linked records: {response.text}")

        return all_records

    async def link_synced_records(
        self,
        model,
        linked_model,
        external_records: list[dict],
        source_records_map: dict,
        target_records_map: dict,
        map_records_key: str,
        column_name: str,
    ) -> int:
        """
        Link records based on external data using the correct NocoDB API endpoints.
        Also unlinks records that are no longer related.
        
        Args:
            model: The model class for the source records
            linked_model: The model class for the target records
            external_records: The external data containing the relationships
            source_records_map: Mapping of external product IDs to NocoDB IDs (not used with new implementation)
            target_records_map: Mapping of external category IDs to NocoDB IDs (not used with new implementation)
            map_records_key: Linked field between source_records_map and target_records_map, nested fields is allowed, example 'category.id'
            column_name: The column name in the source table that links to the target table
            
        Returns:
            The number of records updated (linked + unlinked)
        """
        table_id = model.__tableid__
        self.logger.info(f"Starting link_synced_records for table {table_id}, column {column_name}")
        
        # Get table metadata to find the link column
        metadata = await self.get_table_metadata(table_id)
        
        # Find the link column
        linked_column = None
        for col in metadata.get("columns", []):
            if col.get("title") == column_name:
                linked_column = col
                self.logger.debug(f"Found link column with id: {col.get('id')}")
                break
                
        if not linked_column:
            self.logger.error(f"Linked column {column_name} was not found in {table_id}")
            return 0
        
        # Get column options for linking details from colOptions
        col_options = linked_column.get("colOptions", {})
        fk_related_model_id = col_options.get("fk_related_model_id")
        column_id = linked_column.get("id")
        
        self.logger.info(f"Link column details: id={column_id}, fk_related_model_id={fk_related_model_id}")
        
        if not fk_related_model_id:
            self.logger.error(f"Could not determine related model ID for column {column_name}")
            return 0
        
        linked_table_records = await self.get_table_records(fk_related_model_id)
        # Create mappings
        external_id_field = model.__external_id_field__
        target_external_id_field = linked_model.__external_id_field__
        
        self.logger.info(f"Using external ID fields: source={external_id_field}, target={target_external_id_field}")
        
        target_id_to_name = {}
        for record in linked_table_records:
            record_id = record["Id"]
            external_id = record.get("External ID")
            target_id_to_name[str(record_id)] = external_id
        
        # Map external records by ID
        external_records_map = {str(record["id"]): record for record in external_records}

        self.logger.debug(f"source_records_map: {source_records_map}")
        self.logger.debug(f"target_records_map: {target_records_map}")
        self.logger.debug(f"external_records_map: {external_records_map}")
        self.logger.info(f"Map sizes: source={len(source_records_map) if source_records_map else 0}, target={len(target_records_map) if target_records_map else 0}, external={len(external_records_map) if external_records_map else 0}")
        # Prepare for linking/unlinking
        update_count = 0
        
        # Track what relationships should exist
        desired_relationships: dict[str, list[str]] = {}  # {source_id: [target_id1, target_id2, ...]}
        
        # First identify all desired relationships based on external data
        for ext_id, external_record in external_records_map.items():
            if ext_id not in source_records_map:
                self.logger.error(f"Product with external ID {ext_id} not found in NocoDB, all external records must be synced before link records")
                continue
                
            source_record = source_records_map[ext_id]
            source_record_id = source_record.get("Id")  # Get the NocoDB record ID
            
            if not source_record_id:
                self.logger.error(f"No ID found for source record with external ID {ext_id}, source_records_map format: [external_id: <nocodb_record>, ...] nocodb_record must have 'Id' attribute")
                continue
                
            target_external_id_field_value = external_record
            for key in map_records_key.split("."):
                if isinstance(target_external_id_field_value, list):
                    target_external_id_field_value = [
                        item.get(key) for item in target_external_id_field_value if isinstance(item, dict)
                    ]
                elif isinstance(target_external_id_field_value, dict):
                    target_external_id_field_value = target_external_id_field_value.get(key) # type: ignore

            if not target_external_id_field_value:
                self.logger.debug(f"Failed to extract value of target ID field using {map_records_key} from {external_record}")
                continue
            elif type(target_external_id_field_value) != list:
                target_external_id_field_values = [str(target_external_id_field_value)]
            else:
                target_external_id_field_values = [str(target_external_id_field_value_item) for target_external_id_field_value_item in target_external_id_field_value]
            # Ensure category_id is a string (hashable)

            self.logger.debug(
                f"Extracted [{target_external_id_field_value}] of target ID field using for {ext_id}")

            # Find the target record by external ID
            for target_external_id_field_value in target_external_id_field_values: # type: ignore
                if target_external_id_field_value not in target_records_map:
                    self.logger.error(f"Record with external ID {target_external_id_field_value} not found in NocoDB, records must exist before link records")
                    continue

                target_record = target_records_map[target_external_id_field_value]
                target_record_id = target_record.get("Id")  # Get the NocoDB record ID

                if not target_record_id:
                    self.logger.debug(f"No ID found for target record with external ID {target_external_id_field_value}, source_records_map format: [external_id: <nocodb_record>, ...] nocodb_record must have 'Id' attribute")
                    continue

                # Add to desired relationships
                if source_record_id not in desired_relationships:
                    desired_relationships[source_record_id] = []
                desired_relationships[source_record_id].append(str(target_record_id))

        # Now process each source record to link/unlink as needed
        for ext_id, source_record in source_records_map.items():
            source_record_id = source_record.get("Id")
            if not source_record_id:
                self.logger.error(f"Empty Id field of nocodb record: {source_record}")
                continue
                
            try:
                existing_records = await self.get_linked_records(
                    base_id=self.project_id,
                    fk_model_id=table_id,
                    record_id=source_record_id,
                    source_column_id=column_id,
                )
                existing_links = [str(record["Id"]) for record  in existing_records]
                self.logger.info(f"Extracted existing links for {ext_id}: {existing_links}")
                
                # Determine what links to add and remove
                desired_links = desired_relationships.get(source_record_id, [])
                links_to_add = [link for link in desired_links if link not in existing_links]
                links_to_remove = [link for link in existing_links if link not in desired_links]
                
                self.logger.info(f"Source {ext_id}: existing={existing_links}, desired={desired_links}, to_add={links_to_add}, to_remove={links_to_remove}")
                
                # Add new links
                for target_id in links_to_add:
                    self.logger.info(f"Linking product {ext_id} (ID: {source_record_id}) to category with ID: {target_id}")

                    # Add link
                    await self.link_table_record(
                        base_id=self.project_id,
                        fk_model_id=table_id,
                        record_id=source_record_id,
                        source_column_id=column_id,
                        linked_record_id=target_id,
                    )
                    update_count += 1
                
                # Remove old links
                for target_id in links_to_remove:
                    self.logger.info(f"Unlinking product {ext_id} (ID: {source_record_id}) from category ID: {target_id}")

                    await self.unlink_table_record(
                        base_id=self.project_id,
                        fk_model_id=table_id,
                        record_id=source_record_id,
                        source_column_id=column_id,
                        linked_record_id=target_id,
                    )
                    update_count += 1
                        
            except Exception as e:
                self.logger.error(f"Error processing record {ext_id}: {str(e)}")
                
        self.logger.info(f"Completed linking/unlinking, {update_count} update operations performed")
        return update_count
        
    def get_query_params(self, params: dict) -> dict:
        """
        Format query parameters for the NocoDB API.
        
        Args:
            params: The query parameters
            
        Returns:
            The query parameters
        """
        if not params:
            return {}
            
        if self.API_VERSION == "v1":
            # For v1 API, use different parameter names
            query_params = {}
            
            # Handle fields
            if "fields" in params:
                query_params["fields"] = params["fields"]
                
            # Handle where conditions
            if "where" in params:
                # v1 API uses a different format for filters
                conditions = []
                for field, value in params["where"].items():
                    if isinstance(value, dict):
                        # Handle operators
                        for op, val in value.items():
                            conditions.append(f"({field},{self._map_operator(op)},{val})")
                    else:
                        # Equality condition
                        conditions.append(f"({field},eq,{value})")
                        
                if conditions:
                    query_params["where"] = ",".join(conditions)
                    
            # Handle limit and offset
            if "limit" in params:
                query_params["limit"] = params["limit"]
            if "offset" in params:
                query_params["offset"] = params["offset"]
                
            return query_params
        else:
            # v2 API format
            return params
            
    def _map_operator(self, op: str) -> str:
        """Map operators from v2 to v1 format"""
        operator_map = {
            "eq": "eq",
            "neq": "neq", 
            "gt": "gt",
            "lt": "lt",
            "gte": "gte",
            "lte": "lte",
            "like": "like",
            "nlike": "nlike",
            "in": "in"
        }
        return operator_map.get(op, "eq")

    async def query_record(self, table_id: str, record_id: str) -> Optional[dict]:
        url = f"{self.NOCODB_HOST}/api/v2/tables/{table_id}/records/{record_id}"
        response = await self.httpx_client.get(url)
        if response.status_code == 200:
            return response.json()
        self.logger.info("Failed to find record %s in %s: %s, returning 404", record_id, url, response.text)
        raise Exception(404, "Record not found")


    async def query_records(self, table_id: str, params: Optional[dict[Any, Any]] = None) -> list:
        """
        Query records from a table.
        
        Args:
            table_id: The table ID
            params: The query parameters
            
        Returns:
            A list of records
        """
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/tables/{table_id}/records"
        query_params = self.get_query_params(params or {})
        
        response = await self._request("GET", url, params=query_params)
        if response.status_code == 200:
            if self.API_VERSION == "v1":
                return response.json().get("list", [])
            else:
                return response.json().get("list", [])
        raise Exception(response.text)

    async def create_record(self, table_id: str, record_data: dict) -> dict:
        """
        Create a record in a table.
        
        Args:
            table_id: The table ID
            record_data: The record data
            
        Returns:
            The response data
        """
        url = f"{self.NOCODB_HOST}/api/{self.API_VERSION}/db/data/noco/{self.project_id}/{table_id}"
        response = await self._request("POST", url, json=record_data)
        if response.status_code == 200:
            return response.json()
        raise Exception(response.text)
    
    async def process_temporary_attachments(self, model: NocodbModel, record_data: dict, **mapper_kwargs) -> dict:
        """
        Process temporary attachments for a record.
        
        Args:
            model: The model class for the record
            record_data: The record data
        """
        if not model.__metadata__:
            model.__metadata__ = await self.get_table_metadata(model.__tableid__)
        existing_columns = {col["title"]: col for col in model.__metadata__["columns"]}
        from pprint import pprint
        pprint(existing_columns)
        schema = model.__nocodb_table_schema__(**mapper_kwargs)
        attachment_fields = [field for field, value_type in schema.items() if value_type == AttachmentObject]
        for attachment_field in attachment_fields:
            print(f"Process attachemnt field: {attachment_field}")
            uploaded_attachments = []
            temporary_file_paths = record_data.get(attachment_field, [])
            if temporary_file_paths:
                print(f"Process file path: {temporary_file_paths}")
                for temporary_file_path in temporary_file_paths:
                    print(f"Process: {temporary_file_path}")
                    if temporary_file_path.get("path"):
                        file_path = temporary_file_path['path']
                        self.logger.debug(f"Uploading attachment {file_path} to NocoDB")
                        attachment_column_id = existing_columns[attachment_field].get("id")
                        response = await self.upload_file_to_nocodb(
                            model.__tableid__,
                            attachment_column_id,
                            file_name=temporary_file_path['title'],
                            file_path=file_path
                        )
                        uploaded_attachments.append(response)
                        
                        # Clean up temporary file after successful upload
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                self.logger.debug(f"Removed temporary file: {file_path}")
                        except Exception as e:
                            self.logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")
                    elif temporary_file_path.get("buffer") and temporary_file_path.get("title"):
                        # logic for in-memory file
                        buffer: BytesIO = temporary_file_path["buffer"]
                        filename: str = temporary_file_path["title"]
                        self.logger.debug(f"Uploading in-memory attachment {filename} to NocoDB")
                        from pprint import pprint
                        pprint(uploaded_attachments)
                        attachment_column_id = existing_columns[attachment_field].get("id")

                        response = await self.upload_file_to_nocodb(
                            model.__tableid__,
                            attachment_column_id,
                            file_name=temporary_file_path['title'],
                            file_buffer=buffer
                        )
                        print(f"Upload response: {response}")
                        uploaded_attachments.append(response)
                    else:
                        self.logger.debug(f"Attachment {temporary_file_path} is not a temporary file, skipping")
                        uploaded_attachments.append(temporary_file_path)
            record_data[attachment_field] = uploaded_attachments
        return record_data

    async def upsert_record(self, nocodb_record_model: NocodbModel, upload_attachments: bool = False,
                            **mapper_kwargs) -> dict:
        """
        Upserts a single record into NocoDB: creates if 'id' is missing, updates if present.

        Args:
            nocodb_record_model (NocodbModel): Record data loaded to model
            upload_attachments (bool): Whether to handle attachment fields
            **mapper_kwargs: Additional arguments for schema/mapping

        Returns:
            dict: Created or updated record
        """
        table_id = nocodb_record_model.__tableid__
        schema = nocodb_record_model.__nocodb_table_schema__(**mapper_kwargs)
        skip_update_cols = nocodb_record_model.__skip_update_column_names__(**mapper_kwargs)

        record_id = nocodb_record_model.id # type: ignore
        if record_id:
            try:
                int(record_id)
            except ValueError:
                raise Exception(f"Record ID {record_id} must be an integer, it's an internal ID of record")

        raw_record = nocodb_record_model.__mapper__(**mapper_kwargs)
        del raw_record['id']

        if record_id:
            existing = await self.query_record(table_id, record_id)
            if existing:
                if upload_attachments:
                    attachment_fields = [f for f, t in schema.items() if t == AttachmentObject]
                    for attachment_field in attachment_fields:
                        temporary_file_paths = []
                        attachments = raw_record.get(attachment_field)
                        if attachments:
                            for att in attachments:
                                file_size, width, height, path, filename = await download_image(att["url"])
                                temporary_file_paths.append({
                                    "path": path,
                                    "width": width,
                                    "height": height,
                                    "size": file_size,
                                    "mimetype": "image/jpeg",
                                    "title": filename
                                })
                        raw_record[attachment_field] = temporary_file_paths

                if needs_update(self, existing, raw_record, schema, skip_update_cols):
                    record = await self.process_temporary_attachments(nocodb_record_model, raw_record, **mapper_kwargs)
                    return await self.update_record(table_id, record_id, record)
                else:
                    return existing  # no changes needed
            else:
                self.logger.warning(f"Record with ID {record_id} not found in table {table_id}, creating new one")

        # Create new record path
        if upload_attachments:
            attachment_fields = [f for f, t in schema.items() if t == AttachmentObject]
            for attachment_field in attachment_fields:
                temporary_file_paths = []
                attachments = raw_record.get(attachment_field)
                if attachments:
                    for att in attachments:
                        file_size, width, height, path, filename = await download_image(att["url"])
                        temporary_file_paths.append({
                            "path": path,
                            "width": width,
                            "height": height,
                            "size": file_size,
                            "mimetype": "image/jpeg",
                            "title": filename
                        })
                raw_record[attachment_field] = temporary_file_paths

        record = await self.process_temporary_attachments(nocodb_record_model, raw_record, **mapper_kwargs)
        from pprint import pprint
        pprint(record)
        return await self.create_record(table_id, record)

    async def synchronize_records(self, records_by_model: dict, upload_attachments: bool = False, remove_obsolete_records: bool = False, **mapper_kwargs):
        """
        Accepts a dictionary mapping model identifiers (or table_ids) to lists of records.
        Processes each list in batches and optionally removes obsolete records.
        Returns a combined mapping of table_id -> (external_id -> record).
        
        Example of records_by_model:
            {
                model_A: [record1, record2, ...],
                model_B: [recordX, recordY, ...]
            }
        """
        for model, records in records_by_model.items():
            # Process in batches if the list is large
            for i in range(0, len(records), self.batch_size):
                batch = records[i : i + self.batch_size]
                await self.synchronize_batch_records(batch, upload_attachments=upload_attachments, **mapper_kwargs)
                self.logger.info(f"Synchronized batch of {len(batch)} records for model {model}. CHECK FAST")
                
            self.logger.info(f"Synchronization complete for model {model.__name__}")
            await self.finalize_synchronization(model, remove_obsolete_records)

        return self._id_maps


    async def synchronize_batch_records(self, records: list, upload_attachments: bool = False, **mapper_kwargs):
        """
        Process a batch of records for one model (table).
        Updates/creates records in NocoDB and updates the cache maps.
        """
        if not records:
            self.logger.warning("No data to synchronize in batch")
            raise ValueError("No data to synchronize in batch")

        # Use the first record to get model-specific info
        nocodb_model      = records[0]
        table_id          = nocodb_model.__tableid__
        external_id_field = nocodb_model.__external_id_field__
        schema            = nocodb_model.__nocodb_table_schema__(**mapper_kwargs)
        skip_update_cols  = nocodb_model.__skip_update_column_names__(**mapper_kwargs)

        # Initialize or get the cache for this table
        if table_id not in self._cached_existing_lookup_maps:
            existing_records = await self.get_table_records(table_id)
            self._cached_existing_lookup_maps[table_id] = {}
            for rec in existing_records:
                ext_id = rec.get(external_id_field)
                if ext_id:
                    self._cached_existing_lookup_maps[table_id][ext_id] = rec
        existing_lookup_map = self._cached_existing_lookup_maps[table_id]

        # Initialize or get the id_map for this table
        if table_id not in self._id_maps:
            self._id_maps[table_id] = {}
        id_map = self._id_maps[table_id]

        # Ensure the external ID column exists
        await self.ensure_external_id_column(table_id, external_id_field)

        self.logger.info(f"Syncing batch of {len(records)} records for table {table_id}")
        # Map records into data dictionaries
        data = [record.__mapper__(**mapper_kwargs) for record in records]
        
        batch_stats = {
            "processed": 0,
            "created": 0,
            "updated": 0
        }
        for record_data in data:
            external_id = str(record_data.get("id", ""))
            if not external_id:
                self.logger.debug("Skipping record with missing external id")
                continue

            # Remove original id and ensure external_id_field is set
            del record_data["id"]
                
            # Include external ID in the record data
            if external_id_field not in record_data:
                record_data[external_id_field] = external_id

            if upload_attachments:
                # That means we need to upload attachments to NocoDB
                # We need to get the attachments fields from the record
                # We need to download external attachments to the file system
                # Later we will compare checksum of the file and existing attachment in NocoDB
                attachment_fields = [field for field, value_type in schema.items() if value_type == AttachmentObject]
                for attachment_field in attachment_fields:
                    temporary_file_paths = []
                    external_attachment_values = record_data.get(attachment_field)
                    if external_attachment_values:
                        for external_attachment_value in external_attachment_values:
                            self.logger.debug(f"Downloading attachment {external_attachment_value['url']} to the file system")
                            file_size, width, height, file_path, filename = await download_image(external_attachment_value['url'])
                            temporary_file_paths.append({
                                "path": file_path,
                                "width": width,
                                "height": height,
                                "size": file_size,
                                "mimetype": "image/jpeg",
                                "title": filename
                            })
                    record_data[attachment_field] = temporary_file_paths

                
            # Check if record exists
            if external_id in existing_lookup_map:
                # Update existing record
                existing_record = existing_lookup_map[external_id]
                record_id = existing_record.get("Id")
                if not record_id:
                    self.logger.warning(f"Record {external_id} exists but has no ID, skipping update")
                    continue

                # Check if update is needed
                if needs_update(self, existing_record, record_data, schema, skip_update_cols):
                    record_data = await self.process_temporary_attachments(nocodb_model, record_data, **mapper_kwargs)
                    self.logger.debug(f"Updating record {external_id} for table {table_id}")
                    updated = await self.update_record(table_id, record_id, record_data)
                    id_map[external_id] = updated
                    existing_lookup_map[external_id] = updated  # refresh the cache
                    batch_stats["updated"] += 1
                else:
                    id_map[external_id] = existing_record
                    batch_stats["processed"] += 1
            else:
                record_data = await self.process_temporary_attachments(nocodb_model, record_data, **mapper_kwargs)
                self.logger.debug(f"Creating new record {external_id} for table {table_id}")
                created = await self.create_record(table_id, record_data)
                id_map[external_id] = created
                existing_lookup_map[external_id] = created
                batch_stats["created"] += 1
        self.logger.info(f"Batch sync complete for table {table_id}. Total synced: {len(id_map)}. Current batch stats: {batch_stats}")
        return id_map
    

    async def finalize_synchronization(
        self,
        nocodb_model: NocodbModel,
        remove_obsolete_records: bool = False
    ) -> dict:
        """
        Call once at the end of all your chunk-synchronizations.
        Optionally remove records in NocoDB that were never mentioned in any chunk (i.e. obsolete).
        Returns the final self._id_map.
        """
        table_id = nocodb_model.__tableid__
        existing_lookup_map = self._cached_existing_lookup_maps.get(table_id, {}) # type: ignore
        id_map = self._id_maps.get(table_id, {})  # type: ignore
        # We only know the obsolete external_ids if we fetched the existing_lookup_map initially
        if remove_obsolete_records and existing_lookup_map:
            all_external_ids_synced = set(id_map.keys())
            all_existing_ids = set(existing_lookup_map.keys())
            obsolete_external_ids = list(all_existing_ids - all_external_ids_synced)

            if obsolete_external_ids:
                self.logger.info(
                    f"Removing {len(obsolete_external_ids)} obsolete records from table {table_id}"
                )
                # Perform the deletions in suitable batch sizes
                for i in range(0, len(obsolete_external_ids), self.batch_size):
                    chunk = obsolete_external_ids[i : i + self.batch_size]
                    to_delete_ids = []
                    for external_id in chunk:
                        existing = existing_lookup_map[external_id]
                        if existing.get("Id"):
                            to_delete_ids.append(existing["Id"])
                            self.logger.debug(
                                f"Removing obsolete external_id={external_id}, nocodb Id={existing['Id']}"
                            )
                    if to_delete_ids:
                        await self.delete_table_record(table_id, to_delete_ids)

        self.logger.info(
            f"Finalization complete. Returning final id_map of length {len(id_map)}."
        )
        return id_map

    async def extract_shops_metadata(self) -> tuple[str, str, str]:
        """
        Determine the language of the NocoDB project by looking at the table names.

        Args:
            client: NocoDB client

        Returns:
            Language code ("EN" or "RU")
        """
        table_names = []
        category_table_id = None
        products_table_id = None
        language = None
        project_metadata = await self.get_project_metadata()
        for table in project_metadata["list"]:
            table_names.append(table["title"])
            if "Категории" in table["title"] or "Categories" in table["title"]:
                category_table_id = table["id"]
            elif "Products" in table["title"] or "Товары" in table["title"]:
                products_table_id = table["id"]

        if "Категории" in table_names:
            language = "RU"
        elif "Categories" in table_names:
            language = "EN"

        if not (language and products_table_id and category_table_id):
            raise Exception(f"Project init failed: {project_metadata}")

        return language, products_table_id, category_table_id

    async def sync_external_connector(self,
                                      external_products_data: list[dict],
                                      external_categories_data: list[dict],
                                      remove_obsolete_records: bool = False,
                                      skip_update_attributes_product: Optional[list[str]] = None,
                                      skip_update_attributes_category: Optional[list[str]] = None
                                      ):

        if not external_products_data:
            self.logger.info("No external data provided")
            return

        language, products_table_id, category_table_id = await self.extract_shops_metadata()

        ShopCategory.__tableid__ = category_table_id
        if skip_update_attributes_category:
            ShopCategory.__skip_update_attributes__ = skip_update_attributes_category
        ShopProduct.__tableid__ = products_table_id
        if skip_update_attributes_product:
            ShopProduct.__skip_update_attributes__ = skip_update_attributes_product

        categories = [ShopCategory(**item) for item in external_categories_data]
        products = [ShopProduct(**item) for item in external_products_data]

        # await self.apply_migrations(categories[0], migrate_existing_columns=False)
        # await self.apply_migrations(products[0], migrate_existing_columns=False)


        link_column_name = "Категория" if language == "RU" else "Category"
        synced_records = await self.synchronize_records({
            ShopProduct: products,
            ShopCategory: categories
        }, lang=language, remove_obsolete_records=remove_obsolete_records)
        num_linked = await self.link_synced_records(
            model=ShopProduct,
            linked_model=ShopCategory,
            external_records=external_products_data,
            source_records_map=synced_records.get(ShopProduct.__tableid__),
            target_records_map=synced_records.get(ShopCategory.__tableid__),
            map_records_key="category.id",
            column_name=link_column_name
        )

        self.logger.info(f"Linked products to categories: {num_linked}")

        link_column_name = "Назначить родительскую категорию" if language == "RU" else "Set parent category"
        num_linked = await self.link_synced_records(
            model=ShopCategory,
            linked_model=ShopCategory,
            external_records=external_categories_data,
            source_records_map=synced_records.get(ShopCategory.__tableid__),
            target_records_map=synced_records.get(ShopCategory.__tableid__),
            map_records_key="parent_categories.id",
            column_name=link_column_name
        )
        self.logger.info(f"Linked categories to parent categories: {num_linked}")

        self.logger.info("All sync operations completed successfully")
