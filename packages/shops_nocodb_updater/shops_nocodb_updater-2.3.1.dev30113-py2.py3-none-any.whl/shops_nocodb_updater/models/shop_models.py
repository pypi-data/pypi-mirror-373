from enum import Enum
from typing import Optional, Dict, Any, List, Set, Union

from pydantic import Field

from .base import NocodbModel, AttachmentObject
from .types import LongText


class Currency(str, Enum):
    USD = "USD"
    RUB = "RUB"
    CZK = "CZK"
    UAH = "UAH"
    GBP = "GBP"
    EUR = "EUR"

# Define models
class ShopCategory(NocodbModel):
    __external_id_field__ = "External ID"
    __skip_update_attributes__ = [] # ["image"]

    # Define field mappings once at class level
    __field_mappings__ = {
        "name": {"RU": "Название", "EN": "Name"},
        "image": {"RU": "Изображение", "EN": "Image"},
        "external_id": {"RU": "External ID", "EN": "External ID"}
        # "parent_categories": {"RU": "Назначить родительскую категорию", "EN": "Set parent category"}
    }

    id: str
    name: str
    image: Optional[AttachmentObject] = None
    # parent_categories: Optional[List['ShopCategory']] = []

    @classmethod
    def __nocodb_field_name__(cls, field_key: str, lang: Optional[str] = None) -> str:
        """Get localized NocoDB field name for a given field key

        Args:
            field_key: Key of the field in __field_mappings__
            lang: Language code (EN or RU), defaults to client's language

        Returns:
            Localized field name
        """
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        return cls.__field_mappings__[field_key][lang]

    def __nocodb_table_schema__(self, lang: Optional[str] = None) -> dict:
        """Get expected NocoDB table schema to ensure type consistency

        Args:
            lang: Language code (EN or RU), defaults to client's language

        Returns:
            Dictionary mapping field names to their expected NocoDB types
        """
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        return {
            self.__nocodb_field_name__("name", lang): str,
            self.__nocodb_field_name__("image", lang): AttachmentObject,
            self.__nocodb_field_name__("external_id", lang): str
        }

    def __skip_update_column_names__(self, lang: Optional[str] = None) -> list[str]:
        column_names: list[str] = []
        if not self.__skip_update_attributes__:
            return column_names
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        for attribute in self.__skip_update_attributes__:
            column_names.append(self.__nocodb_field_name__(attribute, lang))
        return column_names

    def __mapper__(self, lang: Optional[str] = None) -> dict:
        """Map instance data to NocoDB format

        Args:
            lang: Language code (EN or RU), defaults to client's language

        Returns:
            Dictionary with mapped data in NocoDB format
        """
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        mapped_data: Dict[str, Any] = {
            "id": self.id,
            self.__nocodb_field_name__("name", lang): self.name,
            self.__nocodb_field_name__("external_id", lang): self.id
        }

        # Format image data for NocoDB
        if self.image:
            image_field = self.__nocodb_field_name__("image", lang)
            mapped_data[image_field] = [
                {
                    "url": str(self.image.url),
                    "title": f"image-{self.id}.jpg",
                    "mimetype": "image/jpeg"
                }
            ]
        if self.__skip_update_attributes__:
            for skip_attr in self.__skip_update_attributes__:
                mapped_data.pop(self.__nocodb_field_name__(skip_attr, lang), None)

        return mapped_data


class RuCheckoutModes(str, Enum):
    PAYMENT = "Оплата"
    BOOKING = "Бронирование"


class EnCheckoutModes(str, Enum):
    PAYMENT = "Payment"
    BOOKING = "Booking"


class ShopProduct(NocodbModel):
    __external_id_field__ = "External ID"
    __skip_update_attributes__ = []  # [e.g: "image"]

    # Define field mappings once at class level
    __field_mappings__ = {
        "name": {"RU": "Название", "EN": "Name"},
        "description": {"RU": "Описание", "EN": "Description"},
        "images": {"RU": "Изображения", "EN": "Images"},
        "price": {"RU": "Стоимость", "EN": "Price"},
        "final_price": {"RU": "Стоимость со скидкой", "EN": "Discounted price"},
        "currency": {"RU": "Валюта", "EN": "Currency"},
        "stock_qty": {"RU": "Доступное количество", "EN": "Available quantity"},
        "external_id": {"RU": "External ID", "EN": "External ID"},
        "checkout_mode": {"RU": "Режим оформления", "EN": "Checkout mode"},
    }

    id: str
    name: str
    price: float
    description: Optional[str] = None
    final_price: Optional[float] = None
    currency: Optional[Currency] = None
    stock_qty: Optional[int] = None
    images: Optional[List[AttachmentObject]] = Field(
        default=None,
        description="Shop product images",
        json_schema_extra={"nocodb_type": "Attachment"}
    )
    extra_attributes: Optional[List[Dict[str, str]]] = None
    categories: Optional[List['ShopCategory']] = []
    checkout_mode: Optional[List[Union[RuCheckoutModes, EnCheckoutModes]]] = []

    @classmethod
    def __nocodb_field_name__(cls, field_key: str, lang: Optional[str] = None) -> str:
        """Get localized NocoDB field name for a given field key

        Args:
            field_key: Key of the field in __field_mappings__
            lang: Language code (EN or RU), defaults to client's language

        Returns:
            Localized field name
        """
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        return cls.__field_mappings__[field_key][lang]

    def __nocodb_table_schema__(self, lang: Optional[str] = None) -> dict:
        """Get expected NocoDB table schema to ensure type consistency

        Args:
            lang: Language code (EN or RU), defaults to client's language

        Returns:
            Dictionary mapping field names to their expected NocoDB types
        """
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        schema = {
            self.__nocodb_field_name__("name", lang): str,
            self.__nocodb_field_name__("description", lang): LongText,
            self.__nocodb_field_name__("images", lang): AttachmentObject,
            self.__nocodb_field_name__("price", lang): float,
            self.__nocodb_field_name__("final_price", lang): float,
            self.__nocodb_field_name__("currency", lang): Currency,
            self.__nocodb_field_name__("stock_qty", lang): int,
            self.__nocodb_field_name__("external_id", lang): str,
            self.__nocodb_field_name__("checkout_mode", lang): List[RuCheckoutModes] if lang == "RU" else List[EnCheckoutModes]
        }

        # Add extra attributes to schema if they exist
        if hasattr(self, 'extra_attributes') and self.extra_attributes:
            for attr in self.extra_attributes:
                if attr.get("name"):
                    schema[attr["name"]] = str  # Extra attributes are always stored as strings

        return schema

    def __mapper__(self, lang: Optional[str] = None) -> dict:
        """Map instance data to NocoDB format

        Args:
            lang: Language code (EN or RU), defaults to client's language

        Returns:
            Dictionary with mapped data in NocoDB format
        """
        if lang is None:
            lang = "EN"  # Default to English if no language specified
        mapped_data = {
            "id": self.id,
            self.__nocodb_field_name__("name", lang): self.name,
            self.__nocodb_field_name__("external_id", lang): self.id,
            self.__nocodb_field_name__("price", lang): self.price
        }

        # Add optional fields if they exist
        if self.description:
            mapped_data[self.__nocodb_field_name__("description", lang)] = self.description

        if self.final_price:
            mapped_data[self.__nocodb_field_name__("final_price", lang)] = self.final_price

        if self.currency:
            mapped_data[self.__nocodb_field_name__("currency", lang)] = self.currency

        if self.stock_qty is not None:
            mapped_data[self.__nocodb_field_name__("stock_qty", lang)] = self.stock_qty

        # Format images for NocoDB
        if self.images:
            images = []
            for i, attachment in enumerate(self.images):
                images.append({
                    "url": attachment.url,
                    "title": f"image-{self.id}-{i}.jpg",
                    "mimetype": "image/jpeg",
                    "buffer": attachment.buffer
                })
            mapped_data[self.__nocodb_field_name__("images", lang)] = images

        # Add extra attributes
        if self.extra_attributes:
            for attr in self.extra_attributes:
                if attr.get("name") and attr.get("description"):
                    mapped_data[attr["name"]] = attr["description"]

        if self.checkout_mode:
            mapped_data[self.__nocodb_field_name__("checkout_mode", lang)] = ",".join(self.checkout_mode)

        if self.__skip_update_attributes__:
            for skip_attr in self.__skip_update_attributes__:
                mapped_data.pop(self.__nocodb_field_name__(skip_attr, lang), None)
        return mapped_data

    @classmethod
    def from_dict(cls, data: dict, lang: str = "EN") -> "ShopProduct":
        """
        Create a ShopProduct instance from a dict with localized field names.
        """
        kwargs = {}
        for attr, mapping in cls.__field_mappings__.items():
            field_name = mapping.get(lang)
            if field_name in data:
                kwargs[attr] = data[field_name]
        if "id" not in kwargs and "Id" in data:
            kwargs["id"] = data["Id"]
        kwargs["id"] = str(kwargs["id"])
        print(f"Loading from the dict: {data}, parsed to: {kwargs}")
        return cls(**kwargs)