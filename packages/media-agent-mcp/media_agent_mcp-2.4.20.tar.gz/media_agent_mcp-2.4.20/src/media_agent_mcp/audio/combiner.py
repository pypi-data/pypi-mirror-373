from __future__ import annotations

from ast import main
import os
import tempfile
from typing import Any, Dict

import requests
from loguru import logger

from media_agent_mcp.storage.tos_client import upload_to_tos


def combine_audio_video_from_urls(
    video_url: str, audio_url: str, delay_ms: float = 0.0
) -> Dict[str, Any]:
    """
    Combines video and audio from URLs by calling the backend service.

    Args:
        video_url: The URL of the video file.
        audio_url: The URL of the audio file.
        delay_ms: The delay in milliseconds for the audio to start.

    Returns:
        A dictionary containing the status and the TOS URL of the combined video.
    """
    try:
        backend_base = os.getenv("BE_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
        endpoint = f"{backend_base}/combine-audio-video"
        payload = {
            "video_url": video_url,
            "audio_url": audio_url,
            "audio_start_time": delay_ms,
        }

        logger.info(f"Calling backend to combine audio and video: {endpoint}")
        resp = requests.post(endpoint, json=payload, stream=True, timeout=300)
        logger.info(f"Backend response status: {resp.status_code}, headers: {dict(resp.headers)}")

        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    temp_file.write(chunk)
            temp_file_path = temp_file.name

        logger.info(f"Combined video saved temporarily to {temp_file_path}")

        # Upload the combined video to TOS
        upload_result = upload_to_tos(temp_file_path)

        # Clean up the temporary file
        os.unlink(temp_file_path)

        if upload_result["status"] == "success":
            tos_url = upload_result["data"]["url"]
            logger.info(f"Successfully uploaded combined video to TOS: {tos_url}")
            return {"status": "success", "data": {"url": tos_url}, "message": "ok"}
        else:
            logger.error(
                f"Failed to upload combined video to TOS: {upload_result.get('message')}"
            )
            return {"status": "error", "data": None, "message": upload_result.get("message")}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling backend for audio/video combination: {e}")
        if e.response is not None:
            logger.error(f"Backend response: {e.response.text}")
            return {"status": "error", "data": None, "message": f"Backend error: {e.response.text}"}
        return {"status": "error", "data": None, "message": str(e)}
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return {"status": "error", "data": None, "message": str(e)}

if __name__ == "__main__":
    # Example usage
    video_url = "https://media-agent.tos-ap-southeast-1.bytepluses.com/media_agent/2025-08-04/0ea1ab1f540643cc800c1847fc5aa924.mp4"
    audio_url = "https://demo-bucket-hll.tos-ap-southeast-1.bytepluses.com/tmp/AlertValueKellyCarllyle.mp3"
    result = combine_audio_video_from_urls(video_url, audio_url, delay_ms=500)
    print(result)