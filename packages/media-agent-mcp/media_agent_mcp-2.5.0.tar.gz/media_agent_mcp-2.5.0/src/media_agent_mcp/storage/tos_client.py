"""TOS (Temporary Object Storage) client module.

This module provides functionality for uploading files to TOS and managing storage operations.
"""

import datetime
import logging
import os
import uuid
from typing import Optional, Dict, Any

import tos

logger = logging.getLogger(__name__)


def get_tos_client():
    """
    Creates and returns a TOS client using environment variables for authentication.
    
    Returns:
        A TOS client instance.
    """
    try:
        # Retrieve AKSK information from environment variables
        ak = os.getenv('TOS_ACCESS_KEY')
        sk = os.getenv('TOS_SECRET_KEY')
        endpoint = os.getenv('TOS_ENDPOINT', "tos-ap-southeast-1.bytepluses.com")
        region = os.getenv('TOS_REGION', "ap-southeast-1")
        
        if not ak or not sk:
            raise ValueError("TOS_ACCESS_KEY and TOS_SECRET_KEY environment variables must be set")
            
        client = tos.TosClientV2(ak, sk, endpoint, region)
        return client
    except Exception as e:
        logger.error(f"Error creating TOS client: {str(e)}")
        raise


def upload_to_tos(file_path: str, object_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Uploads a file to TOS and returns the URL.
    
    Args:
        file_path: Path to the file to upload.
        object_key: Optional key to use for the object in TOS. If not provided, a UUID will be generated.
        
    Returns:
        JSON response with status, data (URL), and message.
    """
    try:
        client = get_tos_client()
        bucket_name = os.getenv('TOS_BUCKET_NAME')
        
        if not bucket_name:
            return {
                "status": "error",
                "data": None,
                "message": "TOS_BUCKET_NAME environment variable must be set"
            }
            
        if not object_key:
            # Generate a unique object key if not provided
            file_extension = os.path.splitext(file_path)[1]
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            object_key = f"media_agent/{date_str}/{uuid.uuid4().hex}{file_extension}"
        
        # Upload the file
        with open(file_path, 'rb') as f:
            client.put_object(bucket_name, object_key, content=f)
            
        # Construct the URL
        endpoint = os.getenv('TOS_ENDPOINT', "tos-ap-southeast-1.bytepluses.com")
        url = f"https://{bucket_name}.{endpoint}/{object_key}"
        
        return {
            "status": "success",
            "data": {"url": url},
            "message": "File uploaded successfully to TOS"
        }
    except Exception as e:
        logger.error(f"Error uploading to TOS: {str(e)}")
        return {
            "status": "error",
            "data": None,
            "message": f"Failed to upload file to TOS: {str(e)}"
        }


if __name__ == '__main__':
    # Example usage
    try:
        file_path = '/Users/carey/Downloads/input.mp4'  # Replace with your file path
        url = upload_to_tos(file_path)
        print(f"File uploaded successfully: {url}")
    except Exception as e:
        print(f"Error: {str(e)}")