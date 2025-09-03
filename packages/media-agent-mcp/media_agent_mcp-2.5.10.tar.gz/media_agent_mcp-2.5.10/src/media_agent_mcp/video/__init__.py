"""Video processing module for Media Agent MCP.

This module provides video processing functionality including concatenation,
frame extraction, and video selection.
"""

from .processor import concat_videos, extract_last_frame
from .stack import stack_videos

__all__ = ["concat_videos", "extract_last_frame", "stack_videos"]