import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import requests
from media_agent_mcp.storage.tos_client import upload_to_tos


def stack_videos(main_video_url: str, secondary_video_url: str) -> Dict[str, Any]:
    """
    Calls the backend service to stack two videos vertically.

    Args:
        main_video_url: URL of the main video (bottom).
        secondary_video_url: URL of the secondary video (top).

    Returns:
        A dictionary containing the response from the server.
    """
    base_url = os.getenv('BE_BASE_URL', 'http://127.0.0.1:5000')
    url = f"{base_url}/stack-videos"
    payload = {
        "main_video_url": main_video_url,
        "secondary_video_url": secondary_video_url,
    }
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        tmp = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name)
        with open(tmp, "wb") as f:
            f.write(response.content)
        upload_result = upload_to_tos(str(tmp))
        os.remove(tmp)
        if upload_result["status"] == "success":
            return {"status": "success", "data": {"url": upload_result["data"]["url"]}, "message": "ok"}
        else:
            return {"status": "error", "data": None, "message": upload_result["message"]}
    else:
        return {"status": "error", "data": None, "message": response.text}


if __name__ == '__main__':
    print(stack_videos(
        main_video_url='https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4',
        secondary_video_url='https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4'
    ))