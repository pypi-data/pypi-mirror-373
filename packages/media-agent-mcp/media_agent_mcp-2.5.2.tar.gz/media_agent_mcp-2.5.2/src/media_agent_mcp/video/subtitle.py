"""Subtitle rendering utilities using FFmpeg.

This module renders subtitles (plain text or SRT) onto a video using FFmpeg.  It handles:
1. Automatic line-wrapping for long text.
2. Custom font / colour via `.ttf` files placed in *video/fonts*.
3. On-demand download of five free Google Fonts.
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
import tempfile
import textwrap
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import urlparse

import requests

from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.video.processor import download_video_from_url

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Font management
# ---------------------------------------------------------------------------
FONTS_DIR = Path(__file__).parent / "fonts"

# Font map: font display name -> (download_url_or_None, relative_file_name)
AVAILABLE_FONTS: Dict[str, Tuple[Optional[str], str]] = {
    # English fonts (local)
    "EduNSWACTCursive": (None, "en/EduNSWACTCursive-VariableFont_wght.ttf"),
    "MozillaText": (None, "en/MozillaText-VariableFont_wght.ttf"),
    "RobotoCondensed": (None, "en/Roboto_Condensed-Regular.ttf"),

    # Chinese fonts (local)
    "MaShanZheng": (None, "zh/MaShanZheng-Regular.ttf"),
    "NotoSerifSC": (None, "zh/NotoSerifSC-VariableFont_wght.ttf"),
    "ZCOOLXiaoWei": (None, "zh/ZCOOLXiaoWei-Regular.ttf"),
}

# Font metadata for automatic selection: style and recommended usage
FONT_META: Dict[str, Dict[str, str]] = {
    # English
    "EduNSWACTCursive": {
        "style": "Handwritten cursive; lively, friendly, informal diary-like tone.",
        "suitable_videos": "Vlogs, lifestyle clips, travel diaries, personal notes, playful ads."
    },
    "MozillaText": {
        "style": "Neutral, modern humanist sans; highly legible and balanced.",
        "suitable_videos": "Explainers, tutorials, product demos, UI/tech content, corporate."
    },
    "RobotoCondensed": {
        "style": "Compact, modern sans; impactful with efficient width for tight layouts.",
        "suitable_videos": "News, sports, fast-paced edits, vertical reels with narrow safe areas."
    },

    # Chinese
    "MaShanZheng": {
        "style": "Casual handwritten Chinese; warm and approachable with personal touch.",
        "suitable_videos": "Vlogs, lifestyle, cooking/home, casual promotions, relaxed storytelling."
    },
    "NotoSerifSC": {
        "style": "Serif Chinese; formal, stable, and highly readable in longer passages.",
        "suitable_videos": "Documentaries, knowledge/explainers, interviews, subtitles with long text."
    },
    "ZCOOLXiaoWei": {
        "style": "Display serif inspired by traditional styles; cultural and elegant.",
        "suitable_videos": "Food/city discovery, culture/heritage, travel, title-like expressive captions."
    },
}

SRT_TIMING_RE = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")


def ensure_font(font_name: str) -> Path:
    """
    Return the local font path.

    Raises:
        ValueError: If the font name is not supported.
        FileNotFoundError: If the font file does not exist locally.
    """
    # Allow absolute or direct file path to be provided
    p = Path(font_name)
    if p.suffix.lower() in {".ttf", ".otf"} and p.exists():
        return p

    if font_name not in AVAILABLE_FONTS:
        raise ValueError(f"Unsupported font {font_name}. Choices: {list(AVAILABLE_FONTS)}")

    _, fname = AVAILABLE_FONTS[font_name]
    fpath = FONTS_DIR / fname
    if not fpath.exists():
        raise FileNotFoundError(
            f"Font file {fpath} not found. Please ensure the font is available in {FONTS_DIR}."
        )
    return fpath


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _hex_to_ass(colour: str) -> str:
    colour = colour.lstrip("#")
    if len(colour) != 6:
        raise ValueError("Colour must be 6-digit hex")
    r, g, b = colour[0:2], colour[2:4], colour[4:6]
    return f"&H00{b}{g}{r}&"


def _wrap_lines(txt: str, width: int = 40) -> List[str]:
    lines: List[str] = []
    for para in txt.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return lines


def _probe_duration(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError("ffprobe failed")
    return float(res.stdout.strip())


def _seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp (HH:MM:SS,mmm)."""
    hrs, rem = divmod(seconds, 3600)
    mins, secs = divmod(rem, 60)
    msec = int((secs % 1) * 1000)
    return f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d},{msec:03d}"


def _parse_time_token(tok: str) -> float:
    """Parse a time token which can be seconds or HH:MM:SS(.mmm)."""
    if ":" in tok:
        parts = tok.split(":")
        parts = [float(p) for p in parts]
        while len(parts) < 3:
            parts.insert(0, 0.0)  # pad to [hh, mm, ss]
        hrs, mins, secs = parts
        return hrs * 3600 + mins * 60 + secs
    return float(tok)


def _create_srt(text: str) -> Path:
    """Create an SRT file from plain text or simple time-range lines.

    Supported input formats:
    1. Plain text – single block lasting full video (END placeholder).
    2. Timed lines – each line starts with "start-end " where start/end can be seconds
       or HH:MM:SS(.mmm). Example::

           0-2 Hello world
           2-3 Another line
    """
    tmp = Path(tempfile.NamedTemporaryFile(suffix=".srt", delete=False).name)

    timed_lines: List[str] = []
    pattern = re.compile(r"^\s*([\d:.]+)\s*-\s*([\d:.]+)\s+(.*)$")
    for ln in text.split("\n"):
        if not ln.strip():
            continue  # skip empty lines
        m = pattern.match(ln)
        if m:
            start_s = _parse_time_token(m.group(1))
            end_s = _parse_time_token(m.group(2))
            caption = _wrap_lines(m.group(3))
            timed_lines.append((start_s, end_s, caption))  # type: ignore[arg-type]
        else:
            timed_lines = []  # invalidate timed mode and fall back
            break

    content: List[str] = []
    if timed_lines:
        for idx, (st, ed, cap_lines) in enumerate(timed_lines, 1):
            content.append(str(idx))
            content.append(f"{_seconds_to_timestamp(st)} --> {_seconds_to_timestamp(ed)}")
            content.extend(cap_lines)
            content.append("")
    else:
        # Fallback: plain text shown for entire video (replaced later)
        lines = _wrap_lines(text)
        content = [
            "1",
            "00:00:00,000 --> {END}",
            *lines,
            "",
        ]

    tmp.write_text("\n".join(content), encoding="utf-8")
    return tmp


# New helpers for drawtext flow ------------------------------------------------
Cue = Tuple[float, float, str]


def _parse_srt_content(text: str) -> List[Cue]:
    """
    Args:
        text: SRT formatted subtitle content

    Returns:
        result: List of cues as tuples (start_seconds, end_seconds, caption_text)
    """
    # Normalize line endings
    blocks = re.split(r"\r?\n\r?\n+", text.strip())
    cues: List[Cue] = []
    ts_re = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})$")
    for blk in blocks:
        lines = [ln for ln in blk.splitlines() if ln.strip() != ""]
        if not lines:
            continue
        # Optional index line at top
        if len(lines) >= 2 and ts_re.match(lines[1]):
            ts_line = lines[1]
            text_lines = lines[2:]
        elif ts_re.match(lines[0]):
            ts_line = lines[0]
            text_lines = lines[1:]
        else:
            continue
        m = ts_re.match(ts_line)
        if not m:
            continue
        # Convert SRT timestamps HH:MM:SS,mmm to HH:MM:SS.mmm then to seconds
        st = _parse_time_token(m.group(1).replace(",", "."))
        ed = _parse_time_token(m.group(2).replace(",", "."))
        # Keep original line breaks for SRT content
        caption = "\n".join(text_lines)
        cues.append((st, ed, caption))
    return cues


def _parse_simple_timed(text: str) -> List[Cue]:
    """
    Args:
        text: Lines like "start-end caption" with times in seconds or HH:MM:SS(.mmm)

    Returns:
        result: List of cues parsed from the simple timed format
    """
    pattern = re.compile(r"^\s*([\d:.]+)\s*-\s*([\d:.]+)\s+(.*)$")
    cues: List[Cue] = []
    for ln in text.splitlines():
        if not ln.strip():
            continue
        m = pattern.match(ln)
        if not m:
            return []
        st = _parse_time_token(m.group(1))
        ed = _parse_time_token(m.group(2))
        caption = "\n".join(_wrap_lines(m.group(3)))
        cues.append((st, ed, caption))
    return cues


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

DEFAULT_FONT_SIZE = 60  # Fixed size for subtitles
DEFAULT_ALIGNMENT = 2  # Bottom-center in ASS/SSA


def _auto_select_style(video_url: str, subtitles_input: str) -> Tuple[str, str]:
    """
    Args:
        video_url: The original video URL; must be http(s) for VLM analysis
        subtitles_input: Subtitle content to infer language (helps fallback)

    Returns:
        result: (font_name, font_color) chosen via Seed1.6 or heuristics
    """
    # Lazy import to avoid hard dependency during module import
    try:
        from media_agent_mcp.ai_models.seed16 import process_vlm_task  # type: ignore
    except Exception:
        process_vlm_task = None  # type: ignore

    allowed_fonts = list(AVAILABLE_FONTS.keys())
    default_color = "#FFFFFF"

    # Simple language hint from subtitle content
    has_cjk = bool(re.search(r"[\u4e00-\u9fff]", subtitles_input or ""))

    # If we cannot call the model, pick a safe default by language
    if not isinstance(video_url, str) or not video_url.startswith(("http://", "https://")) or process_vlm_task is None:
        font = "NotoSerifSC" if has_cjk else "MozillaText"
        return font, default_color

    # Build concise font guide
    desc_lines = []
    for name, meta in FONT_META.items():
        desc_lines.append(f"{name}: style={meta['style']}; suitable={meta['suitable_videos']}")

    system_prompt = (
        "You are a professional subtitle stylist. Choose one font and a hex color for subtitles that maximize readability and match the video's tone.\n"
        f"Allowed font_name values (choose exactly one): {', '.join(allowed_fonts)}\n"
        "Rules:\n"
        "- Output strictly in JSON with keys: font_name, font_color.\n"
        "- font_color must be a hex color in the form #RRGGBB.\n"
        "- Consider contrast and aesthetics across the whole video.\n"
        "- If content seems Chinese, prefer a Chinese font; otherwise choose an English font.\n"
        " - The color of the font should contrast with the color at the bottom of the video. They must not be the same; otherwise, the font will be unclear. For example, if the bottom of the video is black, the font color should be white.\n"
        "- Do not use dark colors for the font.\n"
        "Font guide:\n- " + "\n- ".join(desc_lines)
    )

    user_content: List[Dict[str, Any]] = [
        {"type": "text", "text": "Analyze the video and pick the best subtitle style. Output JSON only."},
        {"type": "video_url", "video_url": {"url": video_url}},
    ]
    if subtitles_input:
        user_content.insert(0, {"type": "text", "text": f"Subtitle language hint: {subtitles_input[:500]}"})

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    try:
        resp = process_vlm_task(messages, is_json=True)  # type: ignore
        logger.info(f'[AutoFontSelect]{resp}')
        response_text = (resp or {}).get("data", {}).get("response", "")
        import json as _json
        parsed = _json.loads(response_text) if response_text else {}
        font = parsed.get("font_name")
        color = parsed.get("font_color")

        if font not in AVAILABLE_FONTS:
            font = "NotoSerifSC" if has_cjk else "MozillaText"
        if not isinstance(color, str) or not re.match(r"^#?[0-9A-Fa-f]{6}$", color or ""):
            color = default_color
        if not color.startswith("#"):
            color = f"#{color}"
        return font, color
    except Exception as e:
        logger.error(f"Auto style selection failed: {e}")
        font = "NotoSerifSC" if has_cjk else "MozillaText"
        return font, default_color


def add_subtitles_to_video(
    video_url: str,
    subtitles_input: str,
    font_name: Optional[str] = None,
    font_color: Optional[str] = None,
    output_path: Optional[str] = None,
    position: Optional[str] = None,
) -> Dict[str, Any]:
    """Add subtitles to video and upload result to TOS.

    Args:
        video_url: Video URL or local path
        subtitles_input: SRT content, SRT file/URL, or simple timed lines
        font_name: Font display name (see AVAILABLE_FONTS) or absolute .ttf/.otf path. If None, auto-selected.
        font_color: Hex color like #FFFF00. If None, auto-selected.
        output_path: Optional output mp4 path; if not provided, a temp name will be used
        position: Optional position of subtitles: top, middle, or bottom. Defaults to bottom.

    Returns:
        result: JSON dict with status/data/message
    """
    try:
        # Auto-select font/color when missing (Seed1.6 or heuristics)
        if not font_name or not font_color:
            sel_font, sel_color = _auto_select_style(video_url, subtitles_input)
            if not font_name:
                font_name = sel_font
            if not font_color:
                font_color = sel_color

        # Call Flask subtitle rendering service
        base_url = os.getenv('BE_BASE_URL', 'http://127.0.0.1:5000')
        service_url = f"{base_url}/render"
        payload = {
            "video_url": video_url,
            "subtitles_input": subtitles_input,
            "font_name": font_name,
            "font_color": font_color,
        }
        if position:
            payload["position"] = position
        resp = requests.post(service_url, json=payload, timeout=1800)

        # Handle error responses (JSON)
        if resp.status_code != 200:
            try:
                err = resp.json()
                return {"status": err.get("status", "error"), "data": None, "message": err.get("message", "Subtitle service error")}
            except Exception:
                return {"status": "error", "data": None, "message": f"Subtitle service HTTP {resp.status_code}: {resp.text}"}

        # Write binary video to a temp (or provided) path for TOS upload
        if output_path is None:
            output_path = f"video_sub_{uuid.uuid4().hex}.mp4"
        with open(output_path, "wb") as f:
            f.write(resp.content)

        # Upload to TOS
        url = upload_to_tos(output_path)
        try:
            os.unlink(output_path)
        except Exception:
            pass
        return {"status": "success", "data": {"tos_url": url}, "message": "Subtitles added"}

    except Exception as e:
        logger.exception("Subtitle error: %s", e)
        return {"status": "error", "data": None, "message": f"{e}"}


if __name__ == '__main__':
    text = """1
00:00:00,000 --> 00:00:02,000
This is a test subtitle.

2
00:00:03,000 --> 00:00:5,000
This is another subtitle line.
    """

    print(add_subtitles_to_video(
        video_url='https://carey.tos-ap-southeast-1.bytepluses.com/demo/02175205870921200000000000000000000ffffc0a85094bda733.mp4',
        subtitles_input='hello',
    ))