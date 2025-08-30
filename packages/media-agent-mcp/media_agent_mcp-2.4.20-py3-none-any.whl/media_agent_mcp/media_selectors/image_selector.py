"""Image selection module.

This module provides functionality for selecting the best image from multiple options.
"""

import json
import logging
from typing import List


from media_agent_mcp.ai_models.seed16 import process_vlm_task

logger = logging.getLogger(__name__)


def select_best_image(image_urls: List[str], prompt: str) -> dict:
    """Select the best image from a list of images based on criteria.
    
    Args:
        image_urls: List of paths to images to choose from
        prompt: The ideal image description
        
    Returns:
        Url to the selected best image
    """
    try:
        if not image_urls:
            return "Error: No images provided"
        
        system_prompt = f"""
# role 
You are a images evaluate agent, aim to choose the most suitable image according to the desciption

# selection criteria (highest → lowest priority)
1. **Semantic relevance** – the main subject, setting, and mood must align with the scene description.  
2. **Tone consistency** – lighting, color palette, realism, and cultural cues should match the overall style (vertical vlog, warm, authentic, etc.).  
3. **Technical quality** – sharp focus on the key subject, no obvious artifacts or distortion.  

# NEVER choose an image that …
- contains **garbled text**, unreadable characters, or **large areas of tiny text**.  
- is **off-topic** (food, culture, or location does not match the description).  
- shows strong motion blur, warped anatomy, broken perspective, or clear AI artifacts.  
- uses lighting or colors that clash with the established warm, look.
- Do not choose images do not conform to physical logic.

# note 
must choose one

# output format, strictly json
{{  
    "reason": [
        {{"image": "1", "reason": "reason1", "score": "score1"}},
        {{"image": "2", "reason": "reason2", "score": "score2"}},
        {{"image": "3", "reason": "reson3", "score": "score3"}}
    ],
    "choice": "the index"
}}
# example
Images：image1, image2, image3 
Desciption：“Show a slightly messy Nasi Padang takeaway box.”  
→ Output: {{
    "reason": [
        {{"image": "0", "reason": "1 is the most suitable image, as it aligns with the description", "score": "0.88"}},
        {{"image": "1", "reason": "the person in this image has three legs, which is not consistent with the description of a Nasi Padang takeaway box.", "score": "0.2"}},
        {{"image": "2", "reason": "The image's background is a busy street, which is not consistent with the description", "score": "0.1"}}
    ],
    "choice": "1"
}}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        messages += [
            {"role": "user", "content": [
                {"type": "text", "text": f"this is image {i}"},
                {"type": "image_url", "image_url": {"url": image_urls[i]}}
            ]} for i in range(len(image_urls))
        ]
        messages.append({"role": "user", "content": f"Image Prompt:{prompt}\n Please choose the best image according to the prompt above."})

        try:
            response = process_vlm_task(messages, is_json=True)
            response = response['data']['response']
            logger.info(f"model response: {response}")

        except Exception as e:
            logger.error(f"[VLM]Error selecting image: {e}")
            return {
                "status": "error",
                "choice": None,
                "reason": f"Error selecting image: {str(e)}",
                "url": image_urls[0] if image_urls else None
            }
        
        try:
            response_json = json.loads(response)
            choosed_url = image_urls[int(response_json['choice'])]

            return {
                "choice": response_json['choice'],
                "reason": response_json['reason'],
                "url": choosed_url
            }

        except Exception as e:
            logger.error(f"[VLM]Error parsing response: {e}")
            return {
                "status": "error",
                "choice": None,
                "reason": f"Error parsing response: {str(e)}",
                "url": image_urls[0]
            }

    except Exception as e:
        logger.error(f"Error selecting image: {e}")
        return {
            "status": "error",
            "choice": None,
            "reason": f"Error selecting image: {str(e)}",
            "url": image_urls[0] if image_urls else None
        }


if __name__ == '__main__':
    # Example usage
    images = [
        "https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(1).jpg",
        "https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(2).jpg"
    ]
    prompt = "一个女人愁眉苦脸"

    best_image = select_best_image(images, prompt)
    print(f"The best image selected is: {best_image}")