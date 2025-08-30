import requests
import json
import base64
import os
import tempfile
import subprocess
from loguru import logger
from typing import Dict, Any, List
from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.video.processor import download_video_from_url, get_video_info
from media_agent_mcp.ai_models.seed16 import process_vlm_task
from media_agent_mcp.install_tools.installer import which_ffmpeg


FFMPEG_PATH = which_ffmpeg()
FFPROBE_PATH = ""
if FFMPEG_PATH:
    FFPROBE_PATH = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe")


# Pre-defined voice mapping
VOICE_MAP = [
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "Tina", "gender": "female", "style": "Vivid", "speaker_id": "zh_female_shaoergushi_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "William", "gender": "male", "style": "Deep", "speaker_id": "zh_male_silang_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "James", "gender": "male", "style": "Clear", "speaker_id": "zh_male_jieshuonansheng_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "Grace", "gender": "female", "style": "Softe", "speaker_id": "zh_female_jitangmeimei_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "Sophia", "gender": "female", "style": "Warm", "speaker_id": "zh_female_tiexinnvsheng_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "Mia", "gender": "female", "style": "Vivid", "speaker_id": "zh_female_qiaopinvsheng_mars_bigtts"},
    {"scenario": "Dubbing", "language": ["english", "chinese"], "voice": "Ava", "gender": "female", "style": "Vivid", "speaker_id": "zh_female_mengyatou_mars_bigtts"},
    {"scenario": "General", "language": ["english", "chinese"], "voice": "Luna", "gender": "female", "style": "Clear", "speaker_id": "zh_female_cancan_mars_bigtts"},
    {"scenario": "General", "language": ["english", "chinese"], "voice": "Olivia", "gender": "female", "style": "Clear", "speaker_id": "zh_female_qingxinnvsheng_mars_bigtts"},
    {"scenario": "General", "language": ["english", "chinese"], "voice": "Lily", "gender": "female", "style": "Vivid", "speaker_id": "zh_female_linjia_mars_bigtts"},
    {"scenario": "General", "language": ["english", "chinese"], "voice": "Mark", "gender": "male", "style": "Warm", "speaker_id": "zh_male_wennuanahu_moon_bigtts"},
    {"scenario": "General", "language": ["english", "chinese"], "voice": "Ethan", "gender": "male", "style": "Clear", "speaker_id": "zh_male_shaonianzixin_moon_bigtts"},
    {"scenario": "General", "language": ["english", "chinese"], "voice": "Aria", "gender": "female", "style": "Vivid", "speaker_id": "zh_female_shuangkuaisisi_moon_bigtts"},
    {"scenario": "Fun", "language": ["english", "chinese - beijing accent"], "voice": "Thomas", "gender": "male", "style": "Fun", "speaker_id": "zh_male_jingqiangkanye_moon_bigtts"},
    {"scenario": "General", "language": ["english"], "voice": "Anna", "gender": "female", "style": "Soft", "speaker_id": "en_female_anna_mars_bigtts"},
    {"scenario": "General", "language": ["american english"], "voice": "Adam", "gender": "male", "style": "Clear", "speaker_id": "en_male_adam_mars_bigtts"},
    {"scenario": "General", "language": ["australian english"], "voice": "Sarah", "gender": "female", "style": "Soft", "speaker_id": "en_female_sarah_mars_bigtts"},
    {"scenario": "General", "language": ["australian english"], "voice": "Dryw", "gender": "male", "style": "Deep", "speaker_id": "en_male_dryw_mars_bigtts"},
    {"scenario": "General", "language": ["british english"], "voice": "Smith", "gender": "male", "style": "Deep", "speaker_id": "en_male_smith_mars_bigtts"},
    {"scenario": "Audio Book", "language": ["chinese"], "voice": "Edward", "gender": "male", "style": "Deep", "speaker_id": "zh_male_baqiqingshu_mars_bigtts"},
    {"scenario": "Audio Book", "language": ["chinese"], "voice": "Emma", "gender": "female", "style": "Soft", "speaker_id": "zh_female_wenroushunv_mars_bigtts"},
    {"scenario": "Role", "language": ["chinese"], "voice": "Charlotte", "gender": "female", "style": "Clear", "speaker_id": "zh_female_gaolengyujie_moon_bigtts"},
    {"scenario": "General", "language": ["chinese"], "voice": "Lila", "gender": "female", "style": "Clear", "speaker_id": "zh_female_linjianvhai_moon_bigtts"},
    {"scenario": "General", "language": ["chinese"], "voice": "Joseph", "gender": "male", "style": "Deep", "speaker_id": "zh_male_yuanboxiaoshu_moon_bigtts"},
    {"scenario": "General", "language": ["chinese"], "voice": "George", "gender": "male", "style": "Clear", "speaker_id": "zh_male_yangguangqingnian_moon_bigtts"},
    {"scenario": "Fun", "language": ["chinese - cantonese accent"], "voice": "Andrew", "gender": "male", "style": "Clear", "speaker_id": "zh_male_guozhoudege_moon_bigtts"},
    {"scenario": "Fun", "language": ["chinese - cantonese accent"], "voice": "Robert", "gender": "male", "style": "Fun", "speaker_id": "zh_female_wanqudashu_moon_bigtts"},
    {"scenario": "Fun", "language": ["chinese - sichuan accent"], "voice": "Elena", "gender": "female", "style": "Cute", "speaker_id": "zh_female_daimengchuanmei_moon_bigtts"},
    {"scenario": "Fun", "language": ["chinese - taiwanese accent"], "voice": "Isabella", "gender": "female", "style": "Vivid", "speaker_id": "zh_female_wanwanxiaohe_moon_bigtts"},
    {"scenario": "General", "language": ["japanese", "spanish"], "voice": "かずね", "gender": "male", "style": "Fun", "speaker_id": "multi_male_jingqiangkanye_moon_bigtts"},
    {"scenario": "General", "language": ["japanese", "spanish"], "voice": "はるこ", "gender": "female", "style": "Vivid", "speaker_id": "multi_female_shuangkuaisisi_moon_bigtts"},
    {"scenario": "General", "language": ["japanese", "spanish"], "voice": "ひろし", "gender": "male", "style": "Fun", "speaker_id": "multi_male_wanqudashu_moon_bigtts"},
    {"scenario": "General", "language": ["japanese"], "voice": "あけみ", "gender": "female", "style": "Clear", "speaker_id": "multi_female_gaolengyujie_moon_bigtts"}
]


def get_tts_resource_map():
    """
    Returns the pre-defined voice mapping.
    
    Returns:
        list: The complete VOICE_MAP list
    """
    return VOICE_MAP


def get_voice_speaker(language: str, gender: str) -> Dict[str, Any]:
    """
    Return available speakers that match the provided language and gender filters.
    
    Args:
        language: The language to filter by (enum): English | Chinese | American English | Australian English | British English | Japanese | Spanish
        gender: The gender to filter by (enum): Male | Female
    
    Returns:
        dict: JSON response with status, data (available_speakers list), and message
    """
    try:
        # Filter speakers based on language and gender
        available_speakers = []
        
        # Convert input language and gender to lowercase for case-insensitive matching
        language_lower = language.lower()
        gender_lower = gender.lower()

        for speaker in VOICE_MAP:
            # Check if the requested language is in the speaker's language list
            if language_lower in speaker["language"] and speaker["gender"] == gender_lower:
                available_speakers.append({
                    "speaker_id": speaker["speaker_id"],
                    "voice": speaker["voice"],
                    "style": speaker["style"],
                    "scenario": speaker["scenario"]
                })
        
        return {
            "status": "success",
            "data": {"available_speakers": available_speakers},
            "message": f"Found {len(available_speakers)} speakers for {language} {gender}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error getting voice speakers: {str(e)}"
        }


def get_audio_duration(audio_path: str) -> float:
    """
    Get audio duration in seconds using ffprobe.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        float: Duration in seconds
    """
    try:
        if not FFPROBE_PATH or not os.path.exists(FFPROBE_PATH):
            raise FileNotFoundError("ffprobe executable not found")
        cmd = [
            FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json', 
            '-show_format', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0.0


def speed_up_audio(audio_path: str, speed_factor: float, output_path: str) -> bool:
    """
    Speed up audio while preserving pitch using ffmpeg with enhanced quality filters.
    
    Args:
        audio_path: Path to input audio file
        speed_factor: Speed multiplier (e.g., 1.2 for 20% faster)
        output_path: Path for output audio file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not FFMPEG_PATH or not os.path.exists(FFMPEG_PATH):
            raise FileNotFoundError("ffmpeg executable not found")
        # Enhanced audio processing with quality preservation filters
        cmd = [
            FFMPEG_PATH, '-i', audio_path, 
            '-filter:a', f'atempo={speed_factor},highpass=f=80,lowpass=f=8000,dynaudnorm=p=0.9:s=5',
            '-ar', '24000',  # Ensure consistent sample rate
            '-ac', '2',      # Ensure stereo output
            '-b:a', '128k',  # Set audio bitrate for quality
            '-y', output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except Exception as e:
        print(f"Error speeding up audio: {e}")
        return False


def combine_video_audio(video_path: str, audio_path: str, output_path: str, video_duration: float, audio_duration: float) -> Dict[str, Any]:
    """
    Combine video with audio by calling backend service.

    Args:
        video_path: Path to input video file
        audio_path: Path to input audio file
        output_path: Path for output video file
        video_duration: Duration of the video in seconds
        audio_duration: Duration of the audio in seconds

    Returns:
        dict: A dictionary containing the status and an error message if applicable.
    """
    try:
        # Calculate audio start time to center it
        if audio_duration >= video_duration:
            audio_start_time = 0.0
        else:
            audio_start_time = (video_duration - audio_duration) / 2

        # Upload local files to TOS to get URLs
        video_upload = upload_to_tos(video_path, 'video/mp4')
        if video_upload['status'] == 'error':
            return video_upload
        video_url = video_upload['data']['url']

        audio_upload = upload_to_tos(audio_path, 'audio/mp3')
        if audio_upload['status'] == 'error':
            return audio_upload
        audio_url = audio_upload['data']['url']

        # Call backend
        backend_base = os.getenv('BE_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')
        endpoint = f'{backend_base}/combine-audio-video'
        payload = {
            'video_url': video_url,
            'audio_url': audio_url,
            'audio_start_time': audio_start_time * 1000  # Convert to ms if needed
        }
        resp = requests.post(endpoint, json=payload, stream=True, timeout=300)
        if resp.status_code != 200:
            return {'status': 'error', 'message': resp.text}

        # Save response to output_path
        with open(output_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return {'status': 'success'}

    except Exception as e:
        logger.error(f'Error combining video and audio via backend: {str(e)}')
        return {'status': 'error', 'message': str(e)}


def get_tts_video(video_url: str, speaker_id: str, text: str, can_summarize: bool = False) -> Dict[str, Any]:
    """
    Generate a TTS voiceover for the given video and return a video URL with the audio applied.
    Audio will be automatically centered in the video.
    
    Args:
        video_url: URL of the source video
        speaker_id: ID of the speaker to use for TTS
        text: Text to convert to speech
        can_summarize: Whether to summarize the text when audio is too long
    
    Returns:
        dict: JSON response with status, data (tts_video_url), and message
    """
    temp_files = []
    
    try:
        # Download the source video
        download_result = download_video_from_url(video_url)
        if download_result["status"] == "error":
            return download_result
        
        video_path = download_result["data"]["file_path"]
        temp_files.append(video_path)
        
        # Get video duration
        try:
            _, _, fps, frame_count = get_video_info(video_path)
            video_duration = frame_count / fps if fps > 0 else 0
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"Error getting video info: {str(e)}"
            }
        
        # Generate TTS audio
        audio_data = tts(text, speaker_id)
        if not audio_data:
            return {
                "status": "error",
                "data": None,
                "message": "Failed to generate TTS audio"
            }

        # Save audio to temporary file
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        temp_files.append(audio_path)

        with open(audio_path, 'wb') as f:
            f.write(audio_data)

        # Get audio duration
        audio_duration = get_audio_duration(audio_path)

        final_audio_path = audio_path
        current_text = text

        # Check if audio duration exceeds video duration
        if audio_duration > video_duration:
            # First, try speeding up audio (capped at 1.2x)
            logger.info(f'[Audio length: {audio_duration}]Audio duration exceeds video duration, attempting to speed up audio')
            speed_factor = 1.1

            # Apply speed-up if factor is greater than 1.0
            if speed_factor > 1.0:
                sped_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                temp_files.append(sped_audio_path)

                if speed_up_audio(audio_path, speed_factor, sped_audio_path):
                    final_audio_path = sped_audio_path
                    audio_duration = get_audio_duration(sped_audio_path)
                    logger.info(f'Speeded up audio duration: {audio_duration:.3f}s with factor {speed_factor:.3f}')
            else:
                logger.info(f'Audio duration difference is minimal ({required_speed:.3f}), skipping speed-up')

            # If still exceeds video duration after speeding up
            if audio_duration > video_duration:
                if can_summarize:
                    # Use seed16 to summarize the text
                    messages = [{
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes text to make it shorter while keeping the main message.Please give the response directly don't add on other comments or explanations.Must be short than the original text. Could delete some content"
                    },{
                        "role": "user",
                        "content": f"Please summarize the following text to make it shorter while keeping the main message: {text}"
                    }]

                    summary_result = process_vlm_task(messages)
                    if summary_result["status"] == "success":
                        summarized_text = summary_result["data"]["response"]
                        logger.info(f'Summarized_text: {summarized_text}')

                        # Generate new TTS with summarized text
                        new_audio_data = tts(summarized_text, speaker_id)
                        if new_audio_data:
                            new_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                            temp_files.append(new_audio_path)

                            with open(new_audio_path, 'wb') as f:
                                f.write(new_audio_data)

                            final_audio_path = new_audio_path
                            current_text = summarized_text
                            audio_duration = get_audio_duration(new_audio_path)

                            # Check if summarized audio still exceeds video duration
                            if audio_duration > video_duration:
                                return {
                                    "status": "error",
                                    "data": None,
                                    "message": f"Audio duration ({audio_duration:.2f}s) still exceeds video duration ({video_duration:.2f}s) even after summarization"
                                }
                else:
                    return {
                        "status": "error",
                        "data": None,
                        "message": f"Audio duration ({audio_duration:.2f}s) exceeds video duration ({video_duration:.2f}s) and summarization is not enabled"
                    }

        # Combine video and audio
        output_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        temp_files.append(output_video_path)

        combine_result = combine_video_audio(video_path, final_audio_path, output_video_path, video_duration, get_audio_duration(final_audio_path))
        if combine_result["status"] == "error":
            return {
                "status": "error",
                "data": None,
                "message": combine_result.get("message", "Failed to combine video with audio")
            }

        # Upload result to TOS
        upload_result = upload_to_tos(output_video_path)
        if upload_result["status"] == "error":
            return upload_result

        return {
            "status": "success",
            "data": {"tts_video_url": upload_result["data"]["url"]},
            "message": f"TTS video generated successfully with text: {current_text[:50]}..."
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error generating TTS video: {str(e)}"
        }
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                print(f"Failed to clean up temporary file {temp_file}: {e}")


def tts(text: str, speaker_id: str):
    """
    Synthesizes speech from text using a pre-defined voice.

    Args:
        text: The text to synthesize.
        speaker_id: The speaker ID to use for TTS.

    Returns:
        The synthesized audio data as a byte array.
    """
    app_id = os.environ.get("TTS_APP_KEY")
    access_key = os.environ.get("TTS_ACCESS_KEY")
    resource_id = os.environ.get("RESOURCE_ID")
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

        return audio_data

    except Exception as e:
        print(f"request error: {e}")
        return None
    finally:
        if response:
            response.close()
        session.close()


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()
    # Example usage:
    output_dir = "tts_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Test get_voice_speaker
    speakers = get_voice_speaker("English", "Female")
    print("Available speakers:", speakers)

    # Test TTS generation
    print('')
    for voice in VOICE_MAP:
        audio = tts("This is a test.", voice["speaker_id"])
        if audio:
            with open(os.path.join(output_dir, f"{voice['voice']}.mp3"), "wb") as f:
                f.write(audio)

        break

    # video URL for testing
    video_url = 'https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4'
    res = get_tts_video(
        video_url=video_url,
        speaker_id='zh_female_shaoergushi_mars_bigtts',
        text="I love dance, dance dance.I love dance, dance dance.I love dance, dance dance.I love dance, dance dance.I love dance, dance dance.",
        can_summarize=True
    )

    print(res)