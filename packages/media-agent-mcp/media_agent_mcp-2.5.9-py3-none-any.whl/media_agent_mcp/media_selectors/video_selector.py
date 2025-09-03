"""Image selection module.

This module provides functionality for selecting the best image from multiple options.
"""

import json
import logging
from typing import List

from media_agent_mcp.ai_models.seed16 import process_vlm_task

logger = logging.getLogger(__name__)


def select_best_video(video_urls: List[str], prompt: str) -> dict:
    """Select the best image from a list of images based on criteria.
    
    Args:
        video_urls: List of paths to images to choose from
        prompt: The ideal image description
        
    Returns:
        Url to the selected best image
    """
    try:
        if not video_urls:
            return {
                "choice": None,
                "reason": "Error: No images provided",
                "url": None
            }
        
        system_prompt = f"""
        # Role
        You are an efficient Video Curation AI Agent.
        
        # Core Mission
        Your sole objective is: based on the user's prompt, to select the single most relevant and highest-quality video from a given list of candidate videos, and directly output its index number from the list.
        
        # Workflow
        Although your final output is very simple, you must still strictly follow the internal thought process below to ensure the accuracy of your selection:
        
        Analyze User Prompt:
        
        Identify the core theme, extract keywords, and determine the user's intent and sentiment.
        
        Analyze Candidate Videos:
        
        You will receive a list containing images extracted from multiple video frames, with the videos numbered sequentially (1st, 2nd, ...).
        
        Carefully analyze all available information for each video, such as its theme, visuals, accuracy, and transcript (text content).
        
        Evaluate & Score:
        
        Based on your understanding of the user's needs, internally score and rank each candidate video according to the "Evaluation Criteria" below.
        
        Final Decision:
        
        Based on the overall score, select the single highest-ranking and best-matching video.
        
        # Evaluation Criteria
        When making your decision, you must internally consider the following dimensions in order of importance:
        
        # Content Relevance - [Highest Priority]
        - Is the core content of the video highly consistent with the theme of the user's prompt?
        
        # User Intent Alignment
        - Does the style and type of the video match the user's potential intent (e.g., to learn, to be entertained, to be inspired)?
        
        # Information Quality & Depth
        - Does the video provide valuable and accurate information?
        
        ## Overall Video Quality
        - Are the items generated in the video correct?
        - Is the text garbled?
        - Are the objects logical?
        - Is the video is consistent?
        
        ## Do not choose videos like:
        1. Please avoid selecting videos that are physically illogical, like a person with three arms or a person with a head on the chest.
        
        # Constraints & Rules
        Absolutely do not output any extra text, explanations, reasons, punctuation, or sentences. Only a number is needed.
        You must choose from the video list provided to you. Fabricating information is strictly forbidden.

        # output format, strictly json
        {{
            "reason": [
                {{"video": "0", "reason": "reason1", "score": "score1"}},
                {{"video": "1", "reason": "reason2", "score": "score2"}},
                {{"video": "2", "reason": "reason3", "score": "score3"}}
            ]
            "choice": "the index"
        }}
        # example
        Images：video1, video2, video3
        Description：“Show a slightly messy Nasi Padang takeaway box.”  
        → Output：{{
            "reason": [
                {{"video": "0", "reason": "0 is the most suitable video, as it aligns with the description", "score": "0.88"}},
                {{"video": "1", "reason": "the person in this video has three legs, which is not consistent with the description", "score": "0.2"}},
                {{"video": "2", "reason": "The video's background is a busy street, which is not consistent with the description", "score": "0.1"}}
            ],
            "choice": "0"
        }}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        messages += [
            {"role": "user", "content": [
                {"type": "text", "text": f"this is video {i}"},
                {"type": "video_url", "video_url": {"url": video_urls[i]}}
            ]} for i in range(len(video_urls))
        ]
        messages.append({"role": "user", "content": f"Video Prompt:{prompt}\n Please choose the best video according to the prompt above."})

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
                "url": video_urls[0] if video_urls else None
            }
        
        try:
            response_json = json.loads(response)
            choice_index = int(response_json['choice'])
            choosed_url = video_urls[choice_index]

            return {
                "choice": choice_index,
                "reason": response_json['reason'],
                "url": choosed_url
            }

        except Exception as e:
            logger.error(f"[VLM]Error parsing response: {e}")
            return {
                "status": "error",
                "choice": None,
                "reason": f"Error parsing response: {str(e)}",
                "url": video_urls[0]
            }

    except Exception as e:
        logger.error(f"Error selecting image: {e}")
        return {
            "status": "error",
            "choice": None,
            "reason": f"Error selecting image: {str(e)}",
            "url": video_urls[0] if video_urls else None
        }


if __name__ == '__main__':
    # Example usage
    images = [
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4",
        "https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205817458400000000000000000000ffffc0a850948120ae.mp4"
    ]
    prompt = "生成一个很开心的自拍的男生"

    best_image = select_best_video(images, prompt)
    print(f"The best image selected is: {best_image}")