"""Seedance video generation module.

This module provides functionality for generating videos using the Seedance AI model.
Based on ModelArk Video Generation API documentation with async polling.
"""
import logging
import os
import time
from typing import Dict, Any

import requests

logger = logging.getLogger(__name__)


def generate_video(prompt: str = "", first_frame_image: str = None, last_frame_image: str = None, 
                  duration: int = 5, resolution: str = "720p",
                  fps: int = 24, seed: int = -1, **kwargs) -> Dict[str, Any]:
    """Generate a video using Seedance model with first/last frame images.
    
    Args:
        prompt: Text prompt for video generation (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Video duration in seconds (5 or 10)
        resolution: Video resolution (480p, 720p, 1080p)
        ratio: Aspect ratio (21:9, 16:9, 4:3, 1:1, 3:4, 9:16, 9:21, adaptive)
        fps: Frames per second (24)
        seed: Random seed for reproducibility (-1 for random)
        **kwargs: Additional parameters
        
    Returns:
        JSON response with status, data (video URL), and message
    """
    try:
        # Get API configuration from environment
        api_key = os.getenv('ARK_API_KEY')
        seedance_ep = os.getenv('SEEDANCE_EP', 'seedance-1-0-lite-i2v-250428')
        if not api_key or not seedance_ep:
            raise ValueError("ARK_API_KEY environment variable must be set")
        
        # API endpoint for video generapyttion tasks
        endpoint = "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks"

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Determine model based on input type
        model = os.getenv('SEEDANCE_EP', 'seedance-1-0-lite-i2v-250428')
        
        # Prepare content array for the request
        content = []
        
        # Add text content if prompt is provided
        if prompt:
            text_content = prompt
            # Add parameters to the prompt
            text_content += f" --rs {resolution} --dur {duration} --fps {fps}"
            if seed != -1:
                text_content += f" --seed {seed}"
            
            content.append({
                "type": "text",
                "text": text_content
            })
        
        # Add first frame image if provided
        if first_frame_image:
            content.append({
                "role": "first_frame",
                "type": "image_url",
                "image_url": {
                    "url": first_frame_image
                }
            })
        
        if last_frame_image and first_frame_image:
            content.append({
                "role": "last_frame",
                "type": "image_url", 
                "image_url": {
                    "url": last_frame_image
                }
            })
        
        # Prepare request payload according to API documentation
        payload = {
            'model': model,
            'content': content
        }
        
        logger.info(f"Starting video generation with Seedance: {prompt[:100]}...")
        
        # Make initial API request to start video generation
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {
                "status": "error",
                "data": None,
                "message": error_msg
            }
        
        result = response.json()
        
        # Extract task ID for polling
        if 'id' not in result:
            return {
                "status": "error",
                "data": None,
                "message": "No task ID in response"
            }
        
        task_id = result['id']
        logger.info(f"Video generation task started with ID: {task_id}")
        
        # Poll for completion
        return _poll_video_status(task_id, api_key)
        
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - video generation request took too long"
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
        error_msg = f"Unexpected error in Seedance generation: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "data": None,
            "message": error_msg
        }


def _poll_video_status(task_id: str, api_key: str, max_wait_time: int = 300) -> Dict[str, Any]:
    """Poll video generation status until completion.
    
    Args:
        task_id: The task ID to poll
        api_key: API key for authentication
        max_wait_time: Maximum time to wait in seconds
        
    Returns:
        JSON response with status, data (video URL), and message
    """
    query_endpoint = f"https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{task_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(query_endpoint, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Status query failed: {response.status_code} - {response.text}")
                time.sleep(5)
                continue
            
            result = response.json()
            status = result.get('status')
            
            logger.info(f"Video generation status: {status}")
            
            if status == 'succeeded':
                # Extract video URL from response
                if 'content' in result and 'video_url' in result['content']:
                    video_url = result['content']['video_url']
                    if video_url:
                        logger.info(f"Video generated successfully: {video_url}")
                        return {
                            "status": "success",
                            "data": {"video_url": video_url},
                            "message": "Video generated successfully"
                        }
                    else:
                        return {
                            "status": "error",
                            "data": None,
                            "message": "No video URL in completed response"
                        }
                else:
                    return {
                        "status": "error",
                        "data": None,
                        "message": "No video content in completed response"
                    }
            
            elif status == 'failed':
                error_detail = result.get('error', {}).get('message', 'Unknown error')
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Video generation failed - {error_detail}"
                }
            
            elif status in ['queued', 'running']:
                # Continue polling
                time.sleep(0.5)
                continue
            
            else:
                logger.warning(f"Unknown status: {status}")
                time.sleep(0.5)
                continue
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error polling status: {str(e)}")
            time.sleep(0.5)
            continue
        except Exception as e:
            logger.error(f"Unexpected error polling status: {str(e)}")
            time.sleep(0.5)
            continue
    
    return f"Error: Video generation timed out after {max_wait_time} seconds"


if __name__ == '__main__':
    # Example usage
    video_url = generate_video(
        prompt="the woman slowly moves",
        first_frame_image="https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(1).jpg",
        # last_frame_image="https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(2).jpg",
        duration=12,
        resolution="1080p",
        ratio="16:9",
        fps=24,
        seed=42
    )

    print(f"Generated video URL: {video_url}")