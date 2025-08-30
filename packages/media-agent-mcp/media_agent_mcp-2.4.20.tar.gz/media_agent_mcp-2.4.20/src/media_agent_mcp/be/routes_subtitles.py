from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from flask import Blueprint, jsonify, request, send_file, after_this_request

from media_agent_mcp.be.utils import (
    SRT_TIMING_RE,
    DEFAULT_FONT_SIZE,
    ensure_font,
    _parse_srt_content,
    _parse_simple_timed,
    _probe_duration,
    _wrap_lines,
)

logger = logging.getLogger(__name__)

subtitles_bp = Blueprint("subtitles", __name__)


@subtitles_bp.post("/render")
def render_subtitles():
    try:
        data = request.get_json(silent=True) or {}
        video_input: Optional[str] = data.get("video_url")
        subtitles_input: Optional[str] = data.get("subtitles_input")
        font_name: Optional[str] = data.get("font_name")
        font_color: Optional[str] = data.get("font_color")
        position: Optional[str] = (data.get("position") or "bottom").lower()

        if not video_input or not subtitles_input or not font_name or not font_color:
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Fields video_url, subtitles_input, font_name, font_color are required"
            }), 400

        # Validate and map position
        if position not in {"top", "middle", "bottom"}:
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Invalid position. Allowed values: top, middle, bottom"
            }), 400
        if position == "top":
            y_expr = "2*lh"
        elif position == "middle":
            y_expr = "(h-text_h)/2"
        else:  # bottom
            y_expr = "h-text_h-2*lh"

        temp_files: List[Path] = []

        # Locate or download video
        if isinstance(video_input, str) and video_input.startswith(("http://", "https://")):
            import requests as _req
            dl_resp = _req.get(video_input, stream=True, timeout=600)
            dl_resp.raise_for_status()
            tmp_v = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name)
            with open(tmp_v, "wb") as f:
                for chunk in dl_resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            vpath = tmp_v
            temp_files.append(vpath)
        else:
            vpath = Path(video_input)
            if not vpath.exists():
                return jsonify({"status": "error", "data": None, "message": f"Video {vpath} not found"}), 400

        # Build cues from input (support SRT text, SRT file/URL, or simple timed lines)
        cues = []
        content_text: Optional[str] = None

        if SRT_TIMING_RE.search(subtitles_input):
            content_text = subtitles_input
        elif isinstance(subtitles_input, str) and (subtitles_input.lower().endswith(".srt") or os.path.exists(subtitles_input)):
            if subtitles_input.startswith(("http://", "https://")):
                import requests as _req
                resp = _req.get(subtitles_input, timeout=120)
                resp.raise_for_status()
                content_text = resp.content.decode("utf-8", errors="replace")
            else:
                content_text = Path(subtitles_input).read_text(encoding="utf-8")
        else:
            cues = _parse_simple_timed(subtitles_input)

        if content_text is not None:
            if "{END}" in content_text:
                dur = _probe_duration(vpath)
                import time as _t
                end_ts = _t.strftime("%H:%M:%S", _t.gmtime(dur)) + f",{int((dur % 1)*1000):03d}"
                content_text = content_text.replace("{END}", end_ts)
            cues = _parse_srt_content(content_text)

        if not cues:
            dur = _probe_duration(vpath)
            caption = "\n".join(_wrap_lines(subtitles_input))
            cues = [(0.0, dur, caption)]

        # Font path and color normalization
        font_file = ensure_font(font_name).resolve()
        color_value = font_color if not font_color.startswith('#') else f"0x{font_color[1:]}"

        # Build drawtext filter
        filter_parts: List[str] = []
        for st, ed, cap in cues:
            txt_path = Path(tempfile.NamedTemporaryFile(suffix=".txt", delete=False).name)
            txt_path.write_text(cap, encoding="utf-8")
            temp_files.append(txt_path)
            part = (
                "drawtext="
                f"fontfile='{font_file.as_posix()}':"
                f"textfile='{txt_path.as_posix()}':"
                f"fontcolor='{color_value}':"
                f"fontsize={DEFAULT_FONT_SIZE}:"
                "x=(w-text_w)/2:"
                f"y={y_expr}:"
                "line_spacing=6:"
                "bordercolor=black:borderw=2:"
                "shadowcolor=black:shadowx=1:shadowy=1:"
                f"enable='between(t,{st:.3f},{ed:.3f})'"
            )
            filter_parts.append(part)
        vf_str = ",".join(filter_parts)

        # Render via FFmpeg
        output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(vpath),
            "-vf", vf_str,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "copy",
            str(output_path),
        ]
        logger.debug("FFmpeg cmd: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if proc.returncode != 0:
            logger.error("FFmpeg error: %s", proc.stdout)
            # Cleanup
            for f in temp_files:
                try:
                    f.unlink(missing_ok=True)  # type: ignore[attr-defined]
                except Exception:
                    pass
            try:
                output_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
            except Exception:
                pass
            return jsonify({"status": "error", "data": None, "message": "FFmpeg failed -> " + proc.stdout}), 500

        @after_this_request
        def cleanup(response):
            # Remove temp artifacts after response is sent
            for f in temp_files:
                try:
                    f.unlink(missing_ok=True)  # type: ignore[attr-defined]
                except Exception:
                    pass
            try:
                output_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
            except Exception:
                pass
            return response

        return send_file(str(output_path), mimetype="video/mp4")

    except Exception as e:
        logger.exception("Subtitle service error: %s", e)
        return jsonify({"status": "error", "data": None, "message": str(e)}), 500