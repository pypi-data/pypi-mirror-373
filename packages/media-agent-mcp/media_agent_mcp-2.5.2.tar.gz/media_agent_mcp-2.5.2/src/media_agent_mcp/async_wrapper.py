#!/usr/bin/env python3
"""Async wrapper module for MCP tools using threading.

This module provides async wrappers for all MCP tools without modifying the original functions.
It uses threading to make synchronous functions asynchronous.
"""

import asyncio
import concurrent.futures
import functools
import json
import logging
from typing import Any, Callable, Dict, List, Optional

# Import original functions
from media_agent_mcp.storage import upload_to_tos
from media_agent_mcp.video import concat_videos, extract_last_frame
from media_agent_mcp.video.subtitle import add_subtitles_to_video
from media_agent_mcp.audio.combiner import combine_audio_video_from_urls
from media_agent_mcp.ai_models.seedream import generate_image
from media_agent_mcp.ai_models.seedance import generate_video
from media_agent_mcp.ai_models.seededit import seededit
from media_agent_mcp.ai_models.openaiedit import openaiedit
from media_agent_mcp.media_selectors.image_selector import select_best_image
from media_agent_mcp.media_selectors.video_selector import select_best_video
from media_agent_mcp.audio.tts import get_voice_speaker, get_tts_video
from media_agent_mcp.ai_models.tts import tts
from media_agent_mcp.install_tools import check_ffmpeg
from media_agent_mcp.ai_models.omni_human import generate_video_from_omni_human

logger = logging.getLogger(__name__)

# Thread pool executor for running sync functions
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


def async_wrapper(sync_func: Callable) -> Callable:
    """Decorator to wrap synchronous functions as async using threading.
    
    Args:
        sync_func: The synchronous function to wrap
        
    Returns:
        Async version of the function
    """
    @functools.wraps(sync_func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, sync_func, *args, **kwargs)
    return wrapper


def json_response_wrapper(func: Callable) -> Callable:
    """Wrapper to ensure consistent JSON response format.
    
    Args:
        func: Function to wrap
        
    Returns:
        Function that returns JSON string
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
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
                    return json.dumps({
                        "status": "success",
                        "data": {"url": result},
                        "message": "Operation completed successfully"
                    })
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return json.dumps({
                "status": "error",
                "data": None,
                "message": f"Error: {str(e)}"
            })
    return wrapper


# Async wrapped functions
@async_wrapper
@json_response_wrapper
def _sync_video_concat(video_urls: List[str]) -> str:
    """Synchronous video concatenation wrapper."""
    return concat_videos(video_urls)


@async_wrapper
@json_response_wrapper
def _sync_video_last_frame(video_url: str) -> str:
    """Synchronous video last frame extraction wrapper."""
    return extract_last_frame(video_url)


@async_wrapper
@json_response_wrapper
def _sync_combine_audio_video(video_url: str, audio_url: str, delay_ms: float = 0.0) -> str:
    """Synchronous audio video combination wrapper."""
    return combine_audio_video_from_urls(video_url, audio_url, delay_ms)


@async_wrapper
@json_response_wrapper
def _sync_seedream_generate_image(prompt: str, size: str = "1024x1024") -> str:
    """Synchronous image generation wrapper."""
    return generate_image(prompt, size=size)


@async_wrapper
@json_response_wrapper
def _sync_seedance_generate_video(prompt: str, first_frame_image: str, 
                                 last_frame_image: str = None, duration: int = 5, 
                                 resolution: str = "720p") -> str:
    """Synchronous video generation wrapper."""
    if not prompt and not first_frame_image:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": "Error: Either prompt or first_frame_image must be provided"
        })
    
    return generate_video(
        prompt=prompt,
        first_frame_image=first_frame_image,
        last_frame_image=last_frame_image,
        duration=duration,
        resolution=resolution
    )


@async_wrapper
@json_response_wrapper
def _sync_omni_human_generate_video(image_url: str, audio_url: str) -> str:
    """Synchronous Omni Human video generation wrapper.
    
    Args:
        image_url: The URL of the input image
        audio_url: The URL of the input audio
    
    Returns:
        result: The generated video URL or JSON string
    """
    return generate_video_from_omni_human(image_url, audio_url)


@async_wrapper
@json_response_wrapper
def _sync_seededit(image_url: str, prompt: str, charactor_keep: bool = False) -> str:
    """Synchronous image editing wrapper."""
    return seededit(
        image_url=image_url,
        prompt=prompt
    )


@async_wrapper
@json_response_wrapper
def _sync_vlm_vision_task(messages: List) -> str:
    """Synchronous VLM vision task wrapper."""
    from media_agent_mcp.ai_models.seed16 import process_vlm_task
    return process_vlm_task(messages)


@async_wrapper
def _sync_image_selector(image_paths: List[str], prompt: str) -> str:
    """Synchronous image selector wrapper."""
    try:
        result = select_best_image(image_paths, prompt)
        return json.dumps({
            "status": "success",
            "data": result,
            "message": "Image selection completed successfully"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Image selection failed: {str(e)}"
        })


@async_wrapper
def _sync_video_selector(video_paths: List[str], prompt: str) -> str:
    """Synchronous video selector wrapper."""
    try:
        result = select_best_video(video_paths, prompt)
        return json.dumps({
            "status": "success",
            "data": result,
            "message": "Video selection completed successfully"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Video selection failed: {str(e)}"
        })


@async_wrapper
def _sync_tos_save_content(content: str, file_extension: str = "txt", 
                          object_key: Optional[str] = None) -> str:
    """Synchronous TOS content save wrapper."""
    import tempfile
    import os
    
    try:
        # Create temporary file with content
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{file_extension}', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Upload to TOS
            result = upload_to_tos(temp_file_path, object_key)
            return json.dumps(result)
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"TOS save failed: {str(e)}"
        })


# Public async API
async def async_video_concat_tool(video_urls: List[str]) -> str:
    """Async video concatenation tool."""
    return await _sync_video_concat(video_urls)


async def async_video_last_frame_tool(video_url: str) -> str:
    """Async video last frame extraction tool."""
    return await _sync_video_last_frame(video_url)


async def async_combine_audio_video_tool(video_url: str, audio_url: str, delay_ms: float = 0.0) -> str:
    """Async audio video combination tool."""
    return await _sync_combine_audio_video(video_url, audio_url, delay_ms)


async def async_seedream_generate_image_tool(prompt: str, size: str = "1024x1024") -> str:
    """Async image generation tool."""
    return await _sync_seedream_generate_image(prompt, size)


async def async_seedance_generate_video_tool(prompt: str, first_frame_image: str, 
                                            last_frame_image: str = None, duration: int = 5, 
                                            resolution: str = "720p") -> str:
    """Async video generation tool."""
    return await _sync_seedance_generate_video(prompt, first_frame_image, last_frame_image, duration, resolution)


async def async_omni_human_tool(image_url: str, audio_url: str) -> str:
    """Async Omni Human video generation tool.
    
    Args:
        image_url: The URL of the input image
        audio_url: The URL of the input audio
    
    Returns:
        result: JSON string result from wrapper
    """
    return await _sync_omni_human_generate_video(image_url, audio_url)


async def async_seededit_tool(image_url: str, prompt: str, charactor_keep: bool = False) -> str:
    """Async image editing tool."""
    result = await _sync_seededit(image_url, prompt, charactor_keep)
    return json.loads(result)


async def async_vlm_vision_task_tool(messages: List) -> str:
    """Async VLM vision task tool."""
    return await _sync_vlm_vision_task(messages)


async def async_image_selector_tool(image_paths: List[str], prompt: str) -> str:
    """Async image selector tool."""
    return await _sync_image_selector(image_paths, prompt)


async def async_video_selector_tool(video_paths: List[str], prompt: str) -> str:
    """Async video selector tool."""
    return await _sync_video_selector(video_paths, prompt)

@async_wrapper
@json_response_wrapper
def _sync_openaiedit(image_urls: List[str], prompt: str, size: str = "1024x1024") -> str:
    """Synchronous image editing wrapper for openaiedit."""
    return openaiedit(image_urls=image_urls, prompt=prompt, size=size)

async def async_openaiedit_tool(image_urls: List[str], prompt: str, size: str = "1024x1024") -> str:
    """Async image editing tool for openaiedit."""
    result = await _sync_openaiedit(image_urls, prompt, size)
    return json.loads(result)


@async_wrapper
@json_response_wrapper
def _sync_get_voice_speaker(language: str, gender: str) -> str:
    """Synchronous wrapper for getting available TTS speakers."""
    return get_voice_speaker(language, gender)


@async_wrapper
@json_response_wrapper
def _sync_get_tts_video(video_url: str, speaker_id: str, text: str, can_summarize: bool = False) -> str:
    """Synchronous wrapper for generating TTS video."""
    return get_tts_video(video_url, speaker_id, text, can_summarize)


async def async_get_voice_speaker_tool(language: str, gender: str) -> str:
    """Async tool for getting available TTS speakers."""
    return await _sync_get_voice_speaker(language, gender)


async def async_get_tts_video_tool(video_url: str, speaker_id: str, text: str, can_summarize: bool = False) -> str:
    """Async tool for generating TTS video."""
    return await _sync_get_tts_video(video_url, speaker_id, text, can_summarize)


@async_wrapper
@json_response_wrapper
def _sync_tts(text: str, speaker_id: str) -> str:
    """Synchronous wrapper for TTS generation.
    
    Args:
        text: Text to convert to speech
        speaker_id: Speaker ID for voice selection
    
    Returns:
        result: The generated audio URL or error message
    """
    return tts(text, speaker_id)


async def async_tts_tool(text: str, speaker_id: str) -> str:
    """Async tool for TTS generation.
    
    Args:
        text: Text to convert to speech
        speaker_id: Speaker ID for voice selection
    
    Returns:
        result: JSON string result from wrapper
    """
    result = await _sync_tts(text, speaker_id)
    return json.loads(result)


@async_wrapper
def _sync_add_subtitles_to_video(video_url: str, subtitles_input: str, font_name: Optional[str] = None, font_color: Optional[str] = None, position: Optional[str] = None) -> str:
    """Synchronous wrapper for adding subtitles to video.
    If font_name or font_color is None, the underlying tool will auto-select using Seed1.6.
    """
    try:
        result = add_subtitles_to_video(video_url, subtitles_input, font_name=font_name, font_color=font_color, position=position)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Subtitle processing failed: {str(e)}"
        })


async def async_add_subtitles_to_video_tool(video_url: str, subtitles_input: str, font_name: Optional[str] = None, font_color: Optional[str] = None, position: Optional[str] = None) -> str:
    """Async tool for adding subtitles to video. If font_name or font_color is None, auto-select using Seed1.6."""
    return await _sync_add_subtitles_to_video(video_url, subtitles_input, font_name, font_color, position)


@async_wrapper
@json_response_wrapper
def _sync_install_tools() -> str:
    """Synchronous wrapper for installing development tools."""
    return check_ffmpeg()


@async_wrapper
@json_response_wrapper
def _sync_stack_videos(main_video_url: str, secondary_video_url: str) -> str:
    """Synchronous wrapper for stacking videos."""
    from media_agent_mcp.video.stack import stack_videos
    return stack_videos(main_video_url, secondary_video_url)


async def async_video_stack_tool(main_video_url: str, secondary_video_url: str) -> str:
    """
    Asynchronously stacks the main video (bottom) and secondary video (top), automatically matches the main video duration, and uploads to TOS.
    
    Args:
        main_video_url: Main video URL
        secondary_video_url: Secondary video URL
    
    Returns:
        Dictionary containing status, TOS URL, and message
    """
    return await _sync_stack_videos(main_video_url, secondary_video_url)


async def async_install_tools_plugin() -> str:
    """Async tool for installing development tools."""
    return await _sync_install_tools()


async def async_tos_save_content_tool(content: str, file_extension: str = "txt", 
                                     object_key: Optional[str] = None) -> str:
    """Async TOS content save tool."""
    return await _sync_tos_save_content(content, file_extension, object_key)


def cleanup_executor():
    """Clean up the thread pool executor."""
    global _executor
    if _executor:
        _executor.shutdown(wait=True)
        _executor = None