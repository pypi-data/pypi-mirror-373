from __future__ import annotations

import logging
import os
import re
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fonts and parsing utilities
# ---------------------------------------------------------------------------
FONTS_DIR = Path(__file__).parent / "fonts"
FONTS_DIR.mkdir(parents=True, exist_ok=True)

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

SRT_TIMING_RE = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")
DEFAULT_FONT_SIZE = 60


def ensure_font(font_name: str) -> Path:
    """
    Args:
        font_name: Font display name (AVAILABLE_FONTS) or absolute .ttf/.otf path

    Returns:
        result: Local filesystem path to the font file
    """
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


def _wrap_lines(txt: str, width: int = 40) -> List[str]:
    """
    Args:
        txt: Text to wrap by width
        width: Max characters per line

    Returns:
        result: Wrapped lines
    """
    lines: List[str] = []
    for para in txt.split("\n"):
        lines.extend(textwrap.wrap(para, width=width) or [""])
    return lines


def _parse_time_token(tok: str) -> float:
    """
    Args:
        tok: Time token in seconds or HH:MM:SS(.mmm)

    Returns:
        result: Seconds as float
    """
    if ":" in tok:
        parts = tok.split(":")
        parts = [float(p) for p in parts]
        while len(parts) < 3:
            parts.insert(0, 0.0)
        hrs, mins, secs = parts
        return hrs * 3600 + mins * 60 + secs
    return float(tok)


def _probe_duration(path: Path) -> float:
    """
    Args:
        path: Path to media file

    Returns:
        result: Duration in seconds using ffprobe
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 or not res.stdout.strip():
        # Fallback for containers with no duration set, probe video stream
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0 or not res.stdout.strip():
             raise RuntimeError(f"ffprobe failed to get duration for {path}: {res.stderr}")

    return float(res.stdout.strip())


def _probe_has_audio(path: Path) -> bool:
    """
    Args:
        path: Path to media file

    Returns:
        result: True if the file has an audio stream, False otherwise.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        return False
    return "audio" in res.stdout.strip().lower()


def _probe_resolution(path: Path) -> Tuple[int, int]:
    """
    Args:
        path: Path to media file

    Returns:
        result: (width, height) of the first video stream using ffprobe
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        str(path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 or not res.stdout.strip():
        raise RuntimeError(f"ffprobe failed to get resolution for {path}: {res.stderr}")
    line = res.stdout.strip().splitlines()[0]
    try:
        w_str, h_str = line.split("x")
        return int(w_str), int(h_str)
    except Exception:
        raise RuntimeError(f"Unexpected ffprobe resolution output for {path}: {line}")


Cue = Tuple[float, float, str]


def _parse_srt_content(text: str) -> List[Cue]:
    """
    Args:
        text: SRT formatted subtitle content

    Returns:
        result: List of cues as tuples (start_seconds, end_seconds, caption_text)
    """
    blocks = re.split(r"\r?\n\r?\n+", text.strip())
    cues: List[Cue] = []
    ts_re = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})$")
    for blk in blocks:
        lines = [ln for ln in blk.splitlines() if ln.strip() != ""]
        if not lines:
            continue
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
        st = _parse_time_token(m.group(1).replace(",", "."))
        ed = _parse_time_token(m.group(2).replace(",", "."))
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


def download_video_from_url(url: str) -> Dict[str, Any]:
    """
    Args:
        url: HTTP/HTTPS URL of the video to download

    Returns:
        result: Dict with keys {status, data: {file_path}, message}
    """
    try:
        r = requests.get(url, stream=True, timeout=600)
        r.raise_for_status()
        suffix = ".mp4"
        try:
            from urllib.parse import urlparse
            name = Path(urlparse(url).path).name
            if "." in name:
                suffix = f".{name.split('.')[-1]}" or suffix
        except Exception:
            pass
        tmp = Path(tempfile.NamedTemporaryFile(suffix=suffix, delete=False).name)
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        return {"status": "success", "data": {"file_path": str(tmp)}, "message": "ok"}
    except Exception as e:
        logger.exception("Download failed: %s", e)
        return {"status": "error", "data": None, "message": str(e)}