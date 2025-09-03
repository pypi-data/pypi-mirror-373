"""Seed1.6 VLM module.

This module provides functionality for vision-language tasks using the Seed1.6 model.
Based on ModelArk Chat API documentation with blocking requests.
"""
import logging
import os
from typing import Dict, Any, List

import requests

logger = logging.getLogger(__name__)


def process_vlm_task(messages: List[Dict[str, Any]], max_tokens: int = 4096,
                    temperature: float = 0.7, top_p: float = 0.9, is_json: bool = False, **kwargs) -> Dict[str, Any]:
    """Process a vision-language task using Seed1.6 model with blocking request.
    
    Args:
        messages: List of messages in OpenAI format
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0-2)
        top_p: Nucleus sampling parameter (0-1)
        **kwargs: Additional parameters
        
    Returns:
        JSON response with status, data (response text), and message
    """
    try:
        # Get API configuration from environment
        api_key = os.getenv('ARK_API_KEY')
        vlm_ep = os.getenv('VLM_EP', 'seed-1-6-250615')
        if not api_key and not vlm_ep:
            raise ValueError("ARK_API_KEY environment variable must be set")
        
        # API endpoint for chat completions
        endpoint = "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Prepare request payload according to API documentation
        payload = {
            'model': vlm_ep,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'stream': False,  # Blocking request
            # 'thinking':{
            #     'type': 'disabled'
            # }
        }

        if is_json:
            payload['response_format'] = {'type': 'json_object'}
        
        logger.info(f"Processing VLM task with Seed1.6: {len(messages)} messages, message: {messages}")
        
        # Make blocking API request
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=120  # Longer timeout for VLM tasks
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract response text
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    response_text = choice['message']['content']
                    logger.info(f"VLM task completed successfully")
                    return {
                        "status": "success",
                        "data": {"response": response_text},
                        "message": "VLM task completed successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "data": None,
                        "message": "No content in response message"
                    }
            else:
                return {
                    "status": "error",
                    "data": None,
                    "message": "No choices in response"
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
        error_msg = "Request timeout - VLM task took too long"
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
        error_msg = f"Unexpected error in Seed1.6 VLM task: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "data": None,
            "message": error_msg
        }


if __name__ == '__main__':
    # Example usage
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe the image in detail."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(2).jpg"
                    }
                }
            ]
            }
        ]

    response = process_vlm_task(messages)
    print(response)