from typing import Optional, List, Dict, Any
from io import BytesIO
from pydantic import BaseModel

ID_FIELD = "Id"


class NocodbModel(BaseModel):
    """
    Base model for NocoDB tables. 
    Inherit from this class to define your NocoDB table models.
    """
    __tableid__: str  # The NocoDB table ID
    __skip_update_attributes__: Optional[List[str]] = None  # Keys to skip during data comparison
    __metadata__: Optional[Dict[str, Any]] = None  # Metadata for the table
    __external_id_field__: str = "External ID"  # The external ID field name

    id: str

    @classmethod
    def __nocodb_field_name__(cls, field_key: str, lang: Optional[str] = None) -> str:
        """Get localized NocoDB field name for a given field key
        
        Args:
            field_key: Key of the field in __field_mappings__
            lang: Language code (EN or RU), defaults to client's language
            
        Returns:
            Localized field name
        """
        raise NotImplementedError("Subclasses must implement __nocodb_field_name__")

    def __nocodb_table_schema__(cls, lang: Optional[str] = None) -> dict:
        """Get expected NocoDB table schema to ensure type consistency
        
        Args:
            lang: Language code (EN or RU), defaults to client's language
            
        Returns:
            Dictionary mapping field names to their expected NocoDB types
        """
        raise NotImplementedError("Subclasses must implement __nocodb_table_schema__")
    
    def __skip_update_column_names__(cls, lang: Optional[str] = None) -> list[str]:
        """Get list of column names to skip during data comparison
        
        Args:
            lang: Language code (EN or RU), defaults to client's language  

        Returns:
            List of column names to skip during data comparison
        """
        return []
    

    def __mapper__(self, lang: Optional[str] = None) -> dict:
        """Map instance data to NocoDB format
        
        Args:
            lang: Language code (EN or RU), defaults to client's language
            
        Returns:
            Dictionary with mapped data in NocoDB format
        """
        raise NotImplementedError("Subclasses must implement __mapper__")

    class Config:
        # Allow extra fields
        extra = "allow"


class PaginationResponseModel(BaseModel):
    """
    Model representing pagination information from NocoDB.
    """
    total_rows: int
    page: int
    page_size: int
    is_first_page: bool
    is_last_page: bool


def get_pagination_info(page_info: dict) -> PaginationResponseModel:
    """
    Convert NocoDB pagination info to a PaginationResponseModel.
    
    Args:
        page_info: The pagination info dictionary from NocoDB
        
    Returns:
        PaginationResponseModel with the parsed information
    """
    return PaginationResponseModel(
        total_rows=page_info["totalRows"],
        page=page_info["page"],
        page_size=page_info["pageSize"],
        is_first_page=page_info["isFirstPage"],
        is_last_page=page_info["isLastPage"],
    ) 


class AttachmentObject(BaseModel):
    """Represents a NocoDB attachment object structure"""

    class Config:
        arbitrary_types_allowed = True

    path: Optional[str] = None
    title: Optional[str] = None
    mimetype: Optional[str] = None
    size: int = 0
    signedPath: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    url: Optional[str] = None # Use to define external URL of attachment

    buffer: Optional[BytesIO] = None # only for uploading

    model_config = {
        "extra": "allow",  # Allow extra fields for future compatibility
        "arbitrary_types_allowed": True
    }