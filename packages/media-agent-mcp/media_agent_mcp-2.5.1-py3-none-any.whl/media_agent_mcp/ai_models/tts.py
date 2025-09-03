import base64
import json
import math
import os
import requests
import datetime
import uuid
import tos
from media_agent_mcp.storage.tos_client import get_tos_client
from media_agent_mcp.audio.speed_controller import process_tts_result

def get_audio_duration_from_backend(audio_url: str) -> int:
    """
    Get audio duration from backend API
    
    Args:
        audio_url: The URL of the audio file
    
    Returns:
        duration_seconds: Duration in seconds (int, rounded up)
    """
    try:
        # Get backend base URL from environment variable
        be_base_url = os.getenv('BE_BASE_URL')
        if not be_base_url:
            # Fallback: return default 12 seconds if no backend URL configured
            print("Warning: BE_BASE_URL not configured, using default duration")
            return 12
        
        # Construct full API URL
        api_url = f"{be_base_url.rstrip('/')}/get-audio-duration"
        
        # Call backend API to get audio duration
        response = requests.post(api_url, json={'audio_url': audio_url}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                duration = data.get('data', {}).get('duration_seconds', 12)
                return math.ceil(duration)
            else:
                print(f"Backend API error: {data.get('message', 'Unknown error')}")
                return 12
        else:
            print(f"Backend API request failed with status {response.status_code}")
            return 12
    except Exception as e:
        print(f"Error getting audio duration from backend: {e}")
        return 12

def tts(text: str, speaker_id: str):
    """
    Args:
        text: The text to convert to speech
        speaker_id: The speaker voice ID
    
    Returns:
        result: Dictionary containing audio_url and duration_seconds (int, rounded up)
    """
    app_id = os.environ.get("TTS_APP_KEY")
    access_key = os.environ.get("TTS_ACCESS_KEY")
    resource_id = os.environ.get("RESOURCE_ID", "volc.service_type.1000009")
    speaker = speaker_id

    if not app_id or not access_key or not resource_id:
        return None

    url = "https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/unidirectional"

    headers = {
        "X-Api-App-Id": app_id,
        "X-Api-Access-Key": access_key,
        "X-Api-Resource-Id": resource_id,
        "X-Api-App-Key": "aGjiRDfUWi",
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }

    additions = {
        "disable_markdown_filter": True,
        "enable_language_detector": True,
        "enable_latex_tn": True,
        "disable_default_bit_rate": True,
        "max_length_to_filter_parenthesis": 0,
        "cache_config": {
            "text_type": 1,
            "use_cache": True
        }
    }

    additions_json = json.dumps(additions)

    payload = {
        "user": {"uid": "12345"},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "additions": additions_json,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000
            }
        }
    }
    session = requests.Session()
    response = None
    try:
        response = session.post(url, headers=headers, json=payload, stream=True)

        audio_data = bytearray()
        for chunk in response.iter_lines(decode_unicode=True):
            if not chunk:
                continue
            data = json.loads(chunk)
            if data.get("code", 0) == 0 and "data" in data and data["data"]:
                chunk_audio = base64.b64decode(data["data"])
                audio_data.extend(chunk_audio)
            if data.get("code", 0) == 20000000:
                break
            if data.get("code", 0) > 0:
                print(f"error response:{data}")
                break

        # Directly upload bytes to TOS
        try:
            client = get_tos_client()
            bucket_name = os.getenv('TOS_BUCKET_NAME')

            if not bucket_name:
                print("TOS_BUCKET_NAME environment variable must be set")
                return None

            # Generate a unique object key
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            object_key = f"media_agent/{date_str}/{uuid.uuid4().hex}.mp3"

            client.put_object(bucket_name, object_key, content=bytes(audio_data))

            # Construct the URL
            endpoint = os.getenv('TOS_ENDPOINT', "tos-ap-southeast-1.bytepluses.com")
            file_url = f"https://{bucket_name}.{endpoint}/{object_key}"
            
            # Get audio duration from backend API
            duration_seconds = get_audio_duration_from_backend(file_url)
            
            tts_result = {
                "audio_url": file_url,
                "duration_seconds": duration_seconds
            }
            
            # Apply speed control if audio exceeds 12 seconds
            return process_tts_result(tts_result, target_duration=12)
        except Exception as e:
            print(f"Error uploading audio to TOS: {e}")
            return None

    except Exception as e:
        print(f"request error: {e}")
        return None
    finally:
        if response:
            response.close()
        session.close()


if __name__ == '__main__':
    text = "…というわけで、今週の都市伝説は ドッペルゲンガー ！自分とそっくりの人物に三度会うと、死んじゃうってやつですね！怖い！"
    speaker_id = "multi_male_jingqiangkanye_moon_bigtts"
    # speaker_id = "zh_female_shaoergushi_mars_bigtts"
    result = tts(text, speaker_id)
    print(result)