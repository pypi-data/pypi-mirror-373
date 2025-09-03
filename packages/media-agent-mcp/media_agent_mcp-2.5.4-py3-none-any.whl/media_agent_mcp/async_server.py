#!/usr/bin/env python3
"""Async Media Agent MCP Server - A Model Context Protocol server for media processing with async support.

This server provides 11 async tools for media processing using threading:
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
11. TTS - Convert text to speech and return audio URL

All tools are wrapped with threading to provide async functionality without modifying original functions.
"""

import argparse
import asyncio
import logging
from typing import List, Optional
import json
from dotenv import load_dotenv
import uvicorn
from functools import wraps

def async_retry(max_retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error_message = None
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    if isinstance(result, dict) and result.get('status') == 'error':
                        last_error_message = result.get('message', 'Unknown error')
                        logger.warning(f"Attempt {attempt + 1} of {max_retries} failed for {func.__name__}. Error: {last_error_message}. Retrying in {delay}s...")
                        if attempt < max_retries - 1:  # Don't sleep on the last attempt
                            await asyncio.sleep(delay)
                        continue
                    return result
                except Exception as e:
                    last_exception = str(e)
                    logger.error(f"Attempt {attempt + 1} of {max_retries} failed for {func.__name__} with exception: {e}. Retrying in {delay}s...")
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        await asyncio.sleep(delay)
            
            # Use the last actual error message instead of generic retry message
            final_error_message = last_error_message or last_exception or f"Function {func.__name__} failed after {max_retries} retries"
            logger.error(f"Function {func.__name__} failed after {max_retries} retries. Last error: {final_error_message}")
            return {"status": "error", "data": None, "message": final_error_message}
        return wrapper
    return decorator

from mcp.server.fastmcp import FastMCP

# Import async wrappers
from media_agent_mcp.async_wrapper import (
    async_video_concat_tool, async_video_last_frame_tool, 
    async_combine_audio_video_tool,
    async_seedream_generate_image_tool, async_seedance_generate_video_tool, 
    async_seededit_tool, async_vlm_vision_task_tool, 
    async_image_selector_tool, async_video_selector_tool, 
    async_tos_save_content_tool, cleanup_executor,
    async_openaiedit_tool,
    async_get_voice_speaker_tool, async_get_tts_video_tool,
    async_tts_tool,
    async_add_subtitles_to_video_tool,
    async_install_tools_plugin,
    async_video_stack_tool,
    async_omni_human_tool
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (will be configured in main function)
load_dotenv()
mcp = FastMCP("Media-Agent-MCP-Async")


@mcp.tool()
@async_retry()
async def video_concat_tool(video_urls: List[str]) -> dict:
    """
    Asynchronously concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_concat_tool(video_urls)
    return result


@mcp.tool()
@async_retry()
async def video_last_frame_tool(video_url: str) -> dict:
    """
    Asynchronously extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL of the video file
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_last_frame_tool(video_url)
    return result


@mcp.tool()
@async_retry()
async def combine_audio_video_tool(video_url: str, audio_url: str, delay_ms: float = 0.0) -> dict:
    """
    Asynchronously combine video and audio from URLs with optional delay.
    
    Args:
        video_url: URL of the video file
        audio_url: URL of the audio file
        delay_ms: Delay in milliseconds for the audio to start
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_combine_audio_video_tool(video_url, audio_url, delay_ms)
    return result


@mcp.tool()
@async_retry()
async def seedream_generate_image_tool(prompt: str, size: str = "1024x1024") -> dict:
    """
    Asynchronously generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seedream_generate_image_tool(prompt, size)
    return result


@mcp.tool()
@async_retry()
async def seedance_generate_video_tool(prompt: str, first_frame_image: str, 
                                            last_frame_image: str = None, duration: int = 5, 
                                            resolution: str = "720p") -> dict:
    """
    Asynchronously generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seedance_generate_video_tool(prompt, first_frame_image, last_frame_image, duration, resolution)
    return result


@mcp.tool()
@async_retry()
async def seededit_tool(image_url: str, prompt: str) -> dict:
    """
    Asynchronously edit an image using the OpenAI Images API.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_seededit_tool(image_url, prompt)
    return result


@mcp.tool()
@async_retry()
async def openaiedit_tool(image_urls: List[str], prompt: str, size: str = "1024x1024") -> dict:
    """
    Asynchronously edit an image using the OpenAI Images API.
    
    Args:
        image_urls: List of input image URLs for editing (1 to 4 images)
        prompt: Text prompt for image editing
        size: The size of the generated images. Must be one of "256x256", "512x512", or "1024x1024".
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_openaiedit_tool(image_urls, prompt, size)
    return result


@async_retry()
async def vlm_vision_task_tool(messages: List) -> dict:
    """
    Asynchronously perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_vlm_vision_task_tool(messages)
    return result


@mcp.tool()
@async_retry()
async def image_selector_tool(image_paths: List[str], prompt: str) -> dict:
    """
    Asynchronously select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
        
    Returns:
        Dictionary with status, data, and message
    """
    try:
        result = await async_image_selector_tool(image_paths, prompt)
    except Exception as e:
        logger.error(f"Error in image_selector_tool: {str(e)}")
        result = {"status": "error", "data": None, "message": str(e)}
    
    return result


@mcp.tool()
@async_retry()
async def video_selector_tool(video_paths: List[str], prompt: str) -> dict:
    """
    Asynchronously select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_video_selector_tool(video_paths, prompt)
    return result


@async_retry()
async def tos_save_content_tool(content: str, file_extension: str = "txt", 
                                     object_key: Optional[str] = None) -> dict:
    """
    Asynchronously save content to TOS and return URL.
    
    Args:
        content: Content to save
        file_extension: File extension for the content (default: txt)
        object_key: Optional key to use for the object in TOS
        
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_tos_save_content_tool(content, file_extension, object_key)
    return result


# Utility function for concurrent execution
async def run_multiple_tools_concurrently(*coroutines):
    """
    Run multiple async tools concurrently.
    
    Args:
        *coroutines: Variable number of coroutines to run concurrently
        
    Returns:
        List of results from all coroutines
    """
    return await asyncio.gather(*coroutines, return_exceptions=True)


@mcp.tool()
@async_retry()
async def get_voice_speaker_tool(language: str, gender: str) -> dict:
    """
    Asynchronously get available TTS speakers filtered by language and gender.
    
    Args:
        language: Language enum (English, Chinese, American English, Australian English, British English, Japanese, Spanish)
        gender: Gender enum (Male, Female)
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_get_voice_speaker_tool(language, gender)
    return result


@mcp.tool()
@async_retry()
async def get_tts_video_tool(video_url: str, speaker_id: str, text: str, can_summarize: bool = False) -> dict:
    """
    Asynchronously generate a TTS voiceover and combine it with a video.
    Audio will be automatically centered in the video.
    
    Args:
        video_url: URL of the source video
        speaker_id: ID of the speaker to use for TTS
        text: Text to convert to speech
        can_summarize: Whether to summarize the text when audio is too long
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_get_tts_video_tool(video_url, speaker_id, text, can_summarize)
    return result


@mcp.tool()
@async_retry()
async def add_subtitles_to_video(video_url: str, subtitles_input: str, font_name: Optional[str] = None, font_color: Optional[str] = None, position: Optional[str] = None) -> dict:
    """
    Asynchronously add subtitles to a video with automatic styling and multi-line text support.
    If font_name or font_color is not provided, the tool will call Seed1.6 to analyze the video and auto-select based on predefined font descriptions.
    
    Args:
        video_url: URL of the video file to add subtitles to
        subtitles_input: SRT format subtitle content or path to SRT file. 
                        Example SRT format:
                        "1\n00:00:01,000 --> 00:00:04,000\nHello, this is the first subtitle line\nThis is a second line\n\n2\n00:00:05,000 --> 00:00:08,000\n这是第二条字幕\n支持中文和多行文本"
        font_name: Optional font name or absolute font path. If None, auto-selected.
        font_color: Optional hex color like #FFFF00. If None, auto-selected.
        position: Optional subtitle position: top, middle, or bottom. Defaults to bottom.
    
    Returns:
        Dictionary with status, data (video URL with subtitles), and message
    """
    result = await async_add_subtitles_to_video_tool(video_url, subtitles_input, font_name, font_color, position)
    return result


@mcp.tool()
@async_retry()
async def video_stack_tool(main_video_url: str, secondary_video_url: str) -> dict:
    """
    Asynchronously stacks the main video (bottom) and secondary video (top), automatically matches the main video duration, and uploads to TOS.
    
    Args:
        main_video_url: Main video URL
        secondary_video_url: Secondary video URL
    
    Returns:
        Dictionary containing status, TOS URL, and message
    """
    result = await async_video_stack_tool(main_video_url, secondary_video_url)
    return result

# @mcp.tool()
# @async_retry()
# async def install_tools_plugin() -> dict:
#     """
#     Asynchronously install development tools (ffmpeg and ffprobe) if not present, or return version and path if already installed.
    
#     Returns:
#         Dictionary with status, data (tools info), and message
#     """
#     result = await async_install_tools_plugin()
#     return result


@mcp.tool()
@async_retry()
async def omni_human_tool(image_url: str, audio_url: str) -> dict:
    """
    Asynchronously generate a video using Omni Human AI model.
    
    Args:
        image_url: URL of the input image
        audio_url: URL of the input audio
    
    Returns:
        Dictionary with status, data, and message
    """
    result = await async_omni_human_tool(image_url, audio_url)
    return result


@mcp.tool()
@async_retry()
async def tts_tool(text: str, speaker_id: str) -> dict:
    """
    Asynchronously convert text to speech and upload to TOS.
    
    Args:
        text: Text to convert to speech
        speaker_id: Speaker ID for voice selection
    
    Returns:
        Dictionary with status, data (audio URL), and message
    """
    result = await async_tts_tool(text, speaker_id)
    return result


def main():
    """Main entry point for the Async MCP server."""
    import os
    import sys
    import subprocess
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Async Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='stdio',
                        help='Transport method: sse or stdio (default: stdio)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8000)')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    parser.add_argument('--run-be', action='store_true',
                        help='Run the backend server')
    parser.add_argument('--be-host', type=str, default='0.0.0.0',
                        help='Host for backend server (default: 0.0.0.0)')
    parser.add_argument('--be-port', type=int, default=5000,
                        help='Port for backend server (default: 8001)')

    args = parser.parse_args()

    if args.version:
        print("Async Media Agent MCP Server v0.1.0")
        return

    if args.run_be:
        logger.info(f"Starting backend server on {args.be_host}:{args.be_port}...")
        be_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'be'))
        if not os.path.isdir(be_path):
            logger.error(f"Backend directory not found at: {be_path}")
            return
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import sys, app; "
                        "flask_app = getattr(app, '_flask_app', getattr(app, 'app', None)); "
                        "assert flask_app is not None, 'No Flask application instance found in app.py'; "
                        "flask_app.run(host=sys.argv[1], port=int(sys.argv[2]), debug=False)"
                    ),
                    args.be_host,
                    str(args.be_port),
                ],
                cwd=be_path,
                check=True
            )
        except FileNotFoundError:
            logger.error("`uvicorn` command not found. Please ensure it is installed in your environment.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start backend server: {e}")
        return

    logger.info("Starting Async Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")

    logger.info("Available async tools:")
    logger.info("  1. video_last_frame_tool_async - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool_async - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool_async - Generate images with AI (async)")
    logger.info("  4. seedance_generate_video_tool_async - Generate videos with AI (async)")
    logger.info("  5. seededit_tool_async - Edit images while maintaining character (async)")
    logger.info("  6. vlm_vision_task_tool_async - Perform vision tasks with OpenAI-compatible messages (async)")
    logger.info("  7. image_selector_tool_async - Select best image using VLM model (async)")
    logger.info("  8. video_selector_tool_async - Select best video using VLM model (async)")
    logger.info("  9. add_subtitles_to_video_async - Add subtitles to video with automatic styling")
    logger.info(" 10. get_voice_speaker_tool_async - Get available TTS speakers")
    logger.info(" 11. get_tts_video_tool_async - Generate TTS voiceover and merge with video")
    logger.info(" 12. video_stack_tool_async - 垂直堆叠视频并上传至TOS")
    logger.info(" 13. install_tools_plugin_async - Install development tools (ffmpeg and ffprobe)")
    logger.info(" 14. omni_human_tool_async - Generate a video using Omni Human AI model")
    logger.info("")
    logger.info("All tools support concurrent execution using asyncio.gather() or run_multiple_tools_concurrently()")

    try:
        # Start the server with specified transport
        if args.transport == 'sse':
            logger.info(f"Starting async SSE server on {args.host}:{args.port}")
            mcp.settings.host = args.host
            mcp.settings.port = args.port
            mcp.run(transport="sse")
        else:
            # Default stdio transport
            mcp.run(transport="stdio")
    finally:
        # Clean up thread pool executor on shutdown
        logger.info("Cleaning up thread pool executor...")
        cleanup_executor()


if __name__ == "__main__":
    main()