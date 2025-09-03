"""Video processing module.

This module provides video processing functionality including concatenation and frame extraction.
Uses pure OpenCV for video processing without FFmpeg dependencies.
"""
import logging
import os
import tempfile
import time
import uuid
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse

import cv2
import numpy as np
import requests
import subprocess

from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.install_tools.installer import which_ffmpeg


FFMPEG_PATH = which_ffmpeg()
logger = logging.getLogger(__name__)


def get_video_info(video_path: str) -> Tuple[int, int, float, int]:
    """Get video information using OpenCV.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Tuple of (width, height, fps, frame_count)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    cap.release()
    return width, height, fps, frame_count


def get_video_codec_and_format(video_path: str, high_quality: bool = True) -> Tuple[int, str]:
    """Get video codec information for output video with quality optimization.
    
    Args:
        video_path: Path to the video file
        high_quality: Whether to prioritize quality over compatibility
        
    Returns:
        Tuple of (fourcc_code, file_extension)
    """
    # Test codec availability by creating a temporary video writer
    def test_codec(fourcc_code, width=640, height=480, fps=30.0):
        """Test if a codec is available by trying to create a VideoWriter."""
        try:
            temp_path = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
            writer = cv2.VideoWriter(temp_path, fourcc_code, fps, (width, height))
            is_opened = writer.isOpened()
            writer.release()
            
            # Clean up test file
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return is_opened
        except:
            return False
    
    if high_quality:
        # Prioritize quality codecs for high-quality concatenation
        codecs_to_try = [
            ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264 - best quality and compatibility
            ('avc1', cv2.VideoWriter_fourcc(*'avc1')),  # H.264 alternative
            ('X264', cv2.VideoWriter_fourcc(*'X264')),  # H.264 alternative
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # XVID - good quality
            ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4 - decent quality
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),  # Motion JPEG - larger files but good quality
        ]
        logger.info("Testing available video codecs for high-quality output...")
    else:
        # Standard compatibility-focused codec selection
        codecs_to_try = [
            ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264 - best browser compatibility
            ('avc1', cv2.VideoWriter_fourcc(*'avc1')),  # H.264 alternative
            ('X264', cv2.VideoWriter_fourcc(*'X264')),  # H.264 alternative
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # XVID - good compatibility
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),  # Motion JPEG - widely supported
            ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4 - last resort
        ]
        logger.info("Testing available video codecs for browser compatibility...")
    
    for codec_name, fourcc in codecs_to_try:
        if test_codec(fourcc):
            logger.info(f"Using codec: {codec_name} (high_quality={high_quality})")
            return fourcc, '.mp4'
        else:
            logger.debug(f"Codec {codec_name} not available")
    
    # If no codec works, fall back to mp4v without testing
    logger.warning("No tested codecs available, using mp4v as fallback")
    return cv2.VideoWriter_fourcc(*'mp4v'), '.mp4'


def download_video_from_url(url: str) -> Dict[str, Any]:
    """Download video from URL to a temporary file.
    
    Args:
        url: URL of the video to download
        
    Returns:
        JSON response with status, data (file path), and message
    """
    try:
        # Parse URL to get file extension
        parsed_url = urlparse(url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.mp4'
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download the video
        logger.info(f"Downloading video from {url}...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"Video downloaded to {temp_path}")
        return {
            "status": "success",
            "data": {"file_path": temp_path},
            "message": "Video downloaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error downloading video from {url}: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error downloading video from {url}: {e}"
        }


def concat_videos(video_urls: list, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Concatenate multiple videos into one by delegating the work to the backend service.
    
    Args:
        video_urls: List of video URLs to concatenate in order.
        output_path: Ignored – kept for backward-compatibility; result will be stored in a temporary file.
    
    Returns:
        JSON-style dict with keys {status, data (tos_url), message}.
    """
    try:
        if not video_urls:
            return {
                "status": "error",
                "data": None,
                "message": "No video URLs provided"
            }
    
        # Call backend service
        backend_base = os.getenv("BE_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
        endpoint = f"{backend_base}/concat-videos"
        logger.info(f"Calling backend concat service: {endpoint}")
    
        resp = requests.post(endpoint, json={"video_urls": video_urls}, stream=True, timeout=1800)
        if resp.status_code != 200:
            try:
                err_json = resp.json()
                msg = err_json.get("message") or resp.text
            except Exception:
                msg = resp.text
            logger.error(f"Backend concat service failed: {msg}")
            return {
                "status": "error",
                "data": None,
                "message": f"Backend concat service returned {resp.status_code}: {msg}"
            }
    
        # Save concatenated video to a temporary file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                tmp_file.write(chunk)
        tmp_file.close()
        local_path = tmp_file.name
        logger.info(f"Received concatenated video to {local_path}")
    
        # Upload to TOS
        try:
            tos_url = upload_to_tos(local_path)
            logger.info(f"Uploaded concatenated video to TOS: {tos_url}")
        finally:
            try:
                os.unlink(local_path)
            except Exception:
                pass
    
        return {
            "status": "success",
            "data": {"tos_url": tos_url},
            "message": "Videos concatenated and uploaded successfully"
        }
    except Exception as e:
        logger.exception(f"Error in concat_videos: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error concatenating videos: {str(e)}"
        }


def extract_last_frame(video_input: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract the last frame from a video as an image and upload to TOS.
    
    Args:
        video_input: URL or path to the video file
        output_path: Optional output path for the extracted frame
    
    Returns:
        JSON response with status, data (TOS URL), and message
    """
    temp_video_file = None
    
    try:
        # Handle URL or local file path
        if video_input.startswith(('http://', 'https://')):
            # Download video from URL
            download_result = download_video_from_url(video_input)
            if download_result["status"] == "error":
                return download_result
            video_path = download_result["data"]["file_path"]
            temp_video_file = video_path
        elif os.path.exists(video_input):
            video_path = video_input
        else:
            return {
                "status": "error",
                "data": None,
                "message": f"Video file {video_input} not found"
            }
        
        if not output_path:
            output_path = f"last_frame_{uuid.uuid4().hex}.jpg"
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                "status": "error",
                "data": None,
                "message": f"Could not open video {video_path}"
            }
        
        # Get total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Video has no frames"
            }
        
        # Set position to last frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
        
        # Read the last frame
        ret, frame = cap.read()
        
        if ret:
            # Save the frame
            cv2.imwrite(output_path, frame)
            cap.release()
            logger.info(f"Last frame extracted: {output_path}")
            
            # Upload frame to TOS
            try:
                tos_url = upload_to_tos(output_path)
                logger.info(f"Frame uploaded to TOS: {tos_url}")
                
                # Clean up local frame file
                try:
                    os.unlink(output_path)
                    logger.info(f"Cleaned up local frame file: {output_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up local file {output_path}: {e}")
                
                return {
                    "status": "success",
                    "data": {"tos_url": tos_url},
                    "message": "Last frame extracted and uploaded successfully"
                }
            except Exception as e:
                logger.error(f"Error uploading frame to TOS: {e}")
                return {
                    "status": "error",
                    "data": None,
                    "message": f"Error uploading to TOS: {str(e)}"
                }
        else:
            cap.release()
            return {
                "status": "error",
                "data": None,
                "message": "Could not read the last frame"
            }
            
    except Exception as e:
        logger.error(f"Error extracting last frame: {e}")
        return {
            "status": "error",
            "data": None,
            "message": f"Error extracting last frame: {str(e)}"
        }
    finally:
        # Clean up temporary video file if downloaded
        if temp_video_file and os.path.exists(temp_video_file):
            try:
                os.unlink(temp_video_file)
                logger.info(f"Cleaned up temporary video file: {temp_video_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary video file {temp_video_file}: {e}")


if __name__ == '__main__':
    # Example usage
    video_urls = [
        "https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-08-28/3a0f9d2f2d324513ba759f77007d6f46.mp4",
        "https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-08-28/33e2fd83b961483187e2d461de895764.mp4"
    ]

    concatenated_video = concat_videos(video_urls)
    print(f"Concatenated video URL: {concatenated_video}")

    # last_frame_url = extract_last_frame('/Users/carey/Downloads/input.mp4')
    # print(f"Last frame URL: {last_frame_url}")