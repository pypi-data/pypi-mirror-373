import mimetypes
import secrets
from typing import Dict, List, Any, Type

from shops_nocodb_updater.models.base import NocodbModel


def get_mimetype_and_extension(url: str):
    """
    Get the MIME type and file extension from a URL.
    
    Args:
        url: URL to analyze
        
    Returns:
        Tuple of (mimetype, extension)
    """
    # Guess mimetype and extension based on the URL
    mimetype, _ = mimetypes.guess_type(url)
    if mimetype:
        extension = mimetype.split("/")[-1]
    else:
        # Default to JPEG if type can't be determined
        mimetype = "image/jpeg"
        extension = "jpeg"
    return mimetype, extension


def format_image_data(url: str) -> Dict[str, Any]:
    """
    Format image data for NocoDB compatibility.
    
    Args:
        url: Image URL
        
    Returns:
        Dictionary with formatted image data
    """
    mimetype, extension = get_mimetype_and_extension(url)
    return {
        "url": url,
        "title": f"{secrets.token_hex(6)}.{extension}",
        "mimetype": mimetype
    }


def format_image_list(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Format a list of image URLs for NocoDB compatibility.
    
    Args:
        urls: List of image URLs
        
    Returns:
        List of dictionaries with formatted image data
    """
    return [format_image_data(url) for url in urls]


class ModelMapper:
    """
    Base class for mapping between external data and NocoDB models.
    Inherit from this class to create custom mappers for specific models.
    """
    
    def __init__(self, model_class: Type[NocodbModel]):
        """
        Initialize the model mapper.
        
        Args:
            model_class: The NocodbModel class to map to/from
        """
        self.model_class = model_class
        
    def map_to_nocodb(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map external data to NocoDB format.
        Override this method in subclasses to implement custom mapping.
        
        Args:
            external_data: External data to map
            
        Returns:
            Mapped data for NocoDB
        """
        return external_data
        
    def map_from_nocodb(self, nocodb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map NocoDB data to external format.
        Override this method in subclasses to implement custom mapping.
        
        Args:
            nocodb_data: NocoDB data to map
            
        Returns:
            Mapped data for external use
        """
        return nocodb_data
        
    def batch_map_to_nocodb(self, external_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map a list of external data to NocoDB format.
        
        Args:
            external_data_list: List of external data to map
            
        Returns:
            List of mapped data for NocoDB
        """
        return [self.map_to_nocodb(item) for item in external_data_list]
        
    def batch_map_from_nocodb(self, nocodb_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map a list of NocoDB data to external format.
        
        Args:
            nocodb_data_list: List of NocoDB data to map
            
        Returns:
            List of mapped data for external use
        """
        return [self.map_from_nocodb(item) for item in nocodb_data_list] 