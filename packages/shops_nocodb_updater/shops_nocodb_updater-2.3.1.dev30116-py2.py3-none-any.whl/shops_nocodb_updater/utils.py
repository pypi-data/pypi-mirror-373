import io
import logging
import os
import tempfile
import hashlib
from typing import Optional
import httpx
import aiofiles # type: ignore
from PIL import Image

from shops_nocodb_updater.models.base import AttachmentObject

logger = logging.getLogger(__name__)


def needs_update(client, existing_record, new_data, schema, skip_update_column_names):
    """
    Check if a record needs to be updated.
    
    Args:
        existing_record: Existing record
        new_data: New data
        
    Returns:
        True if update is needed, False otherwise
    """
    for key, value in new_data.items():
        value_target_type = schema.get(key)
        if key in skip_update_column_names:
            logger.debug(f"Skip update for {key} {value}")
            continue
        elif not value_target_type:
            raise ValueError(f"Field {key} not found in schema! -> {schema}")
        elif key in existing_record:
            if value_target_type == AttachmentObject:
                if existing_record[key] and not value:
                    logger.debug(f"Set empty attachment field {key} {existing_record[key]} -> {value}")
                    return True
                elif not existing_record[key] and value or existing_record[key] and len(existing_record[key]) != len(value):
                    logger.debug(f"Update attachment {key} {existing_record[key]} -> {value}")
                    return True
                for i, attachment in enumerate(value):
                    if not client.is_duplicate_attachment(
                        existing_record[key][i],
                        attachment
                    ):
                        logger.debug(f"Update attachment {key} {existing_record[key]} -> {value}")
                        return True
                logger.debug(f"Duplicate attachment found for {key}")
            elif key in existing_record and existing_record[key] != value:
                logger.debug(f"Record needs to be updated for {key} {existing_record[key]} -> {value}")
                return True
    return False

def get_file_md5(file_path: str) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

async def download_file(url: str) -> tuple[int, str, Optional[tuple[int, int]], str]:
    """
    Download any file from URL and return its size, file path, dimensions, and filename.
    The file is saved to a temporary file with MD5 hash prefix.
    
    Returns:
        tuple: (file_size, file_path, dimensions, filename)
            dimensions is None for non-image files or (width, height) for images
            filename is the basename of the file with hash prefix
    """
    logger.info(f"Downloading file from {url}")

    # Use httpx directly with follow_redirects=True
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)

        if response.status_code != 200:
            logger.warning(f"Failed to download file from {url}, status: {response.status_code}")
            raise Exception(f"Failed to download file from {url}, status: {response.status_code}")

        file_data = response.content

        if not file_data or len(file_data) == 0:
            logger.warning(f"Empty file data received from {url}")
            raise Exception(f"Empty file data received from {url}")

        file_size = len(file_data)
        logger.info(f"Downloaded file size: {file_size} bytes from {response.url}")

        # Try to determine if it's an image and get dimensions
        dimensions = None
        file_extension = None
        try:
            img = Image.open(io.BytesIO(file_data))
            width, height = img.size
            dimensions = (width, height)
            logger.info(f"File is an image with dimensions: {width}x{height}")
            file_extension = f".{img.format.lower()}" if img.format else ".jpg"
        except Exception as e:
            logger.info(f"File is not an image or could not be opened: {e}")
            # Extract extension from URL or use .bin as fallback
            if "." in url.split("/")[-1]:
                file_extension = "." + url.split("/")[-1].split(".")[-1]
            else:
                file_extension = ".bin"

        # Extract original filename from URL
        original_filename = url.split("/")[-1].split("?")[0]
        if not original_filename or original_filename == "":
            original_filename = f"downloaded_file{file_extension}"

        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Save the file temporarily to calculate hash
        async with aiofiles.open(temp_file_path, 'wb') as f:
            await f.write(file_data)
        
        # Calculate MD5 hash and use it as prefix
        downloaded_file_hash = get_file_md5(temp_file_path)
        file_hash_short = downloaded_file_hash[:12]
        
        # Create a new filename with the hash prefix
        temp_dir = os.path.dirname(temp_file_path)
        
        # Use original filename from URL when possible, but ensure it has extension
        if "." not in original_filename:
            original_filename += file_extension
            
        new_filename = f"{file_hash_short}_{original_filename}"
        new_temp_file_path = os.path.join(temp_dir, new_filename)
        
        # Rename the file
        os.rename(temp_file_path, new_temp_file_path)
        save_path = new_temp_file_path
        
        logger.info(f"Using temporary file with hash prefix: {save_path}")
        logger.info(f"File saved to {save_path}")
        
        return file_size, save_path, dimensions, new_filename


async def download_image(url: str) -> tuple[int, int, int, str, str]:
    """
    Download image from URL and return its dimensions, size, file path, and filename.
    
    Returns:
        tuple: (width, height, image_size, file_path, filename)
    """
    file_size, file_path, dimensions, filename = await download_file(url)
    
    if dimensions is None:
        raise Exception(f"Downloaded file is not an image: {url}")
    
    width, height = dimensions
    return width, height, file_size, file_path, filename


async def clean_all_records():
    pass