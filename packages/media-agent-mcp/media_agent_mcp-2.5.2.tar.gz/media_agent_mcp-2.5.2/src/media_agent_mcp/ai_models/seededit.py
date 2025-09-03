import os
from typing import Dict, Any
from loguru import logger
import requests



def seededit(image_url, prompt, return_url=True, scale=5.5, seed=-1) -> Dict[str, Any]:
    """
    Perform image editing using the seededit

    :param image_url: URL of the input image.
    :param prompt: The editing prompt.
    :param return_url: Whether to return image URL or base64 string.
    :param scale: Text influence scale (1, 10).
    :param seed: Random seed for reproducibility.
    :return: JSON response with status, data (TOS URL), and message.
    """
    try:
        if not os.getenv("ARK_API_KEY", ""):
            return {
                "status": "error",
                "data": None,
                "message": "ARK_API_KEY environment variable must be set"
            }

        headers = {
            "Authorization": "Bearer " + os.environ.get("ARK_API_KEY", "")
        }

        form = {
            "model": os.getenv('SEEDEDIT_EP', 'seededit-3-0-i2i-250628'),
            "image": image_url,
            'prompt': prompt,
            'response_format': "url",
            'guidance_scale': scale,
            'seed': seed,
            'watermark': False
        }

        logger.info(f'[DEBUG]SeedEdit Request form: {form}')

        response = requests.post(
            url=os.getenv('ARK_BASE_URL', 'https://ark.ap-southeast.bytepluses.com/api/v3/') + 'images/generations',
            json=form,
            headers=headers
        )

        ret = {
            "status": "success",
            "data": {"image_url": response.json()['data'][0]['url']},
            "message": "Image edited successfully"
        }
        
        return ret

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error in seededit: {str(e)}"
        }


if __name__ == '__main__':
    prompt = """
    dance with a ball
    """

    print(seededit(
        image_url='https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-07-28/5f12203b3cb949e0b82cbcac45a1a7c9.jpg',
        prompt=prompt
    ))

