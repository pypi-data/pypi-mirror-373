"""Seedream image generation module.

This module provides functionality for generating images using the Seedream AI model.
Based on ModelArk Image Generation API documentation.
"""
import logging
import os
from typing import Dict, Any

import requests

logger = logging.getLogger(__name__)


def generate_image(prompt: str, size: str = "1024x1024", guidance_scale: float = 2.5, 
                  watermark: bool = False, seed: int = -1, **kwargs) -> Dict[str, Any]:
    """Generate an image using Seedream model.
    
    Args:
        prompt: Text prompt for image generation
        size: Image size (e.g., "1024x1024", "864x1152", etc.), Must be between [512x512, 2048x2048]
        guidance_scale: Controls prompt alignment (1-10)
        watermark: Whether to add watermark
        seed: Random seed for reproducibility (-1 for random)
        **kwargs: Additional parameters
        
    Returns:
        JSON response with status, data (image URL), and message
    """
    try:
        # Get API configuration from environment
        api_key = os.getenv('ARK_API_KEY')
        seedream_ep = os.getenv('SEEDREAM_EP', 'seedream-3-0-t2i-250415')

        if not api_key or not seedream_ep:
            raise ValueError("ARK_API_KEY environment variable must be set")
        
        # API endpoint for image generation
        endpoint = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Prepare request payload according to API documentation
        payload = {
            'model': seedream_ep,
            'prompt': prompt,
            'response_format': 'url',
            'size': size,
            'guidance_scale': guidance_scale,
            'watermark': watermark
        }
        
        # Add seed if specified
        if seed != -1:
            payload['seed'] = seed
        
        logger.info(f"Generating image with Seedream: {prompt[:100]}...")
        
        # Make API request
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract image URL from response
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0].get('url')
                if image_url:
                    logger.info(f"Image generated successfully: {image_url}")
                    return {
                        "status": "success",
                        "data": {"image_url": image_url},
                        "message": "Image generated successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "data": None,
                        "message": "No image URL in response"
                    }
            else:
                return {
                    "status": "error",
                    "data": None,
                    "message": "No image data in response"
                }
        else:
            error_msg = f"API request failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {
                "status": "error",
                "data": None,
                "message": error_msg
            }
            
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - image generation took too long"
        logger.error(error_msg)
        return {
            "status": "error",
            "data": None,
            "message": error_msg
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "data": None,
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"Unexpected error in Seedream generation: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "data": None,
            "message": error_msg
        }


if __name__ == "__main__":
    # Test the function
    prompt = "A serene landscape with mountains and a lake"
    image_url = generate_image(prompt)
    print(image_url)