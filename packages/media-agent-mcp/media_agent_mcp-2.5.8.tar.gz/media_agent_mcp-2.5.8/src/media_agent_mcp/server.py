#!/usr/bin/env python3
"""Media Agent MCP Server - A Model Context Protocol server for media processing.

This server provides 10 tools for media processing:
1. TOS - Save content as URL
2. Video Concat - Concatenate two videos
3. Video Last Frame - Get the last frame from a video
4. Combine Audio Video - Combine video and audio with optional delay
5. Seedream - Creating images (AI model)
6. Seedance (lite & pro) - Creating videos (AI model)
7. Seededit - Maintain the main character (AI model)
8. Seed1.6 (VLM) - Do vision tasks in workflow (AI model)
9. Image Selector - Choose the best one from images
10. Video Selector - Choose the best video from videos
"""

import argparse
import logging
from typing import Optional, Dict, Any
import json
from dotenv import load_dotenv
import uvicorn

from mcp.server.fastmcp import FastMCP

# Import modules
from media_agent_mcp.storage import upload_to_tos
from media_agent_mcp.video import concat_videos, extract_last_frame, stack_videos
from media_agent_mcp.audio.combiner import combine_audio_video_from_urls
from media_agent_mcp.ai_models.seedream import generate_image
from media_agent_mcp.ai_models.seedance import generate_video
from media_agent_mcp.ai_models.seededit import seededit
from media_agent_mcp.ai_models.omni_human import generate_video_from_omni_human
from media_agent_mcp.ai_models.tts import tts
from media_agent_mcp.media_selectors.image_selector import select_best_image
from media_agent_mcp.media_selectors.video_selector import select_best_video

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (will be configured in main function)
load_dotenv()
mcp = FastMCP("Media-Agent-MCP")


@mcp.tool()
def video_concat_tool(video_urls: list[str]) -> str:
    """
    Concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate in order
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = concat_videos(video_urls)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"url": result},
                    "message": "Videos concatenated successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in video_concat_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def video_last_frame_tool(video_url: str) -> str:
    """
    Extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL or path to the video file
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Extract last frame and upload to TOS
        result = extract_last_frame(video_url)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"url": result},
                    "message": "Last frame extracted successfully"
                }
                return json.dumps(success_result)
            
    except Exception as e:
        logger.error(f"Error in video_last_frame_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def combine_audio_video_tool(video_url: str, audio_url: str, delay_ms: float = 0.0) -> str:
    """
    Combine video and audio from URLs with optional delay.
    
    Args:
        video_url: URL of the video file
        audio_url: URL of the audio file
        delay_ms: Delay in milliseconds for the audio to start
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = combine_audio_video_from_urls(video_url, audio_url, delay_ms)
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error in combine_audio_video_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seedream_generate_image_tool(prompt: str, size: str = "1024x1024") -> str:
    """
    Generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = generate_image(prompt, size=size)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"image_url": result},
                    "message": "Image generated successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in seedream_generate_image_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seedance_generate_video_tool(prompt: str, first_frame_image: str,
                                      last_frame_image: str = None, duration: int = 5, 
                                      resolution: str = "720p") -> str:
    """
    Generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Validate duration
        if duration not in [5, 10]:
            return json.dumps({
                "status": "error",
                "data": None,
                "message": "Duration must be 5 or 10 seconds"
            })
        
        # Validate resolution
        if resolution not in ["480p", "720p"]:
            return json.dumps({
                "status": "error",
                "data": None,
                "message": "Resolution must be 480p or 720p"
            })
        
        result = generate_video(prompt, first_frame_image, last_frame_image, duration, resolution)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"video_url": result},
                    "message": "Video generated successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in seedance_generate_video_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seededit_tool(image_url: str, prompt: str, seed: int = -1, scale: float = 0.5, charactor_keep: bool = False) -> str:
    """
    Edit an image using Seededit AI model while maintaining character consistency.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        seed: Random seed for reproducibility (-1 for random)
        scale: Guidance scale for editing (0.1 to 1.0)
        charactor_keep: Whether to keep character consistency
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = seededit(image_url, prompt, scale=scale, seed=seed)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"image_url": result},
                    "message": "Image edited successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in seededit_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def vlm_vision_task_tool(messages: list) -> str:
    """
    Perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Import VLM module
        from media_agent_mcp.ai_models.vlm import vlm_vision_task
        
        result = vlm_vision_task(messages)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"response": result},
                    "message": "VLM task completed successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in vlm_vision_task_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def omni_human_tool(image_url: str, audio_url: str) -> str:
    """
    Generate a video using Omni Human AI model.

    Args:
        image_url: URL of the input image.
        audio_url: URL of the input audio.

    Returns:
        JSON string with status, data, and message.
    """
    try:
        result = generate_video_from_omni_human(image_url, audio_url)
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"video_url": result},
                    "message": "Video generated successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in omni_human_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def tts_tool(text: str, speaker_id: str) -> str:
    """
    Synthesize speech using TTS AI model.

    Args:
        text: Text to synthesize.
        speaker_id: Speaker ID for the voice.

    Returns:
        JSON string with status, data, and message.
    """
    try:
        result = tts(text, speaker_id)
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"audio_url": result},
                    "message": "Speech synthesized successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in tts_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def image_selector_tool(image_paths: list[str], prompt: str) -> str:
    """
    Select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = select_best_image(image_paths, prompt)
        
        if isinstance(result, dict) and result.get("status") == "success":
            success_result = {
                "status": "success",
                "data": result.get("data"),
                "message": "Image selected successfully"
            }
            return json.dumps(success_result)
        else:
            return json.dumps({
                "status": "error",
                "data": None,
                "message": f"Error: {str(result)}"
            })
    except Exception as e:
        logger.error(f"Error in image_selector_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def video_selector_tool(video_paths: list[str], prompt: str) -> str:
    """
    Select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = select_best_video(video_paths, prompt)
        
        if isinstance(result, dict) and result.get("status") == "success":
            success_result = {
                "status": "success",
                "data": result.get("data"),
                "message": "Video selected successfully"
            }
            return json.dumps(success_result)
        else:
            return json.dumps({
                "status": "error",
                "data": None,
                "message": f"Error: {str(result)}"
            })
    except Exception as e:
        logger.error(f"Error in video_selector_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def tos_save_content_tool(content: str, file_extension: str = "txt",
                               object_key: Optional[str] = None) -> str:
    """
    Save content to TOS and return URL.
    
    Args:
        content: Content to save
        file_extension: File extension for the content (default: txt)
        object_key: Optional key to use for the object in TOS
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = upload_to_tos(content, file_extension, object_key)
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                success_result = {
                    "status": "success",
                    "data": {"url": result},
                    "message": "Content saved successfully"
                }
                return json.dumps(success_result)
    except Exception as e:
        logger.error(f"Error in tos_save_content_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='stdio',
                        help='Transport method: sse or stdio (default: stdio)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8000)')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    
    args = parser.parse_args()
    
    if args.version:
        print("Media Agent MCP Server v0.1.0")
        return
    
    logger.info("Starting Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")
    
    logger.info("Available tools:")
    logger.info("  1. video_last_frame_tool - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool - Generate images with AI")
    logger.info("  4. seedance_generate_video_tool - Generate videos with AI")
    logger.info("  5. seededit_tool - Edit images while maintaining character")
    logger.info("  6. vlm_vision_task_tool - Perform vision tasks with OpenAI-compatible messages")
    logger.info("  7. image_selector_tool - Select best image using VLM model")
    logger.info("  8. video_selector_tool - Select best video using VLM model")
    logger.info("  9. tos_save_content_tool - Save content to TOS and get URL")
    logger.info("  10. omni_human_tool - Generate a video using Omni Human AI model")
    logger.info("  11. tts_tool - Synthesize speech using TTS AI model")
    logger.info("")
    
    # Configure and run the server
    if args.transport == 'sse':
        # SSE transport
        uvicorn.run(mcp.create_sse_app(), host=args.host, port=args.port)
    else:
        # STDIO transport (default)
        mcp.run()


if __name__ == "__main__":
    main()