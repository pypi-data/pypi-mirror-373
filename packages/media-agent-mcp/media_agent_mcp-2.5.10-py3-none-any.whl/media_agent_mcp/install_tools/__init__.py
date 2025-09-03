"""Install tools module for managing system dependencies."""

from .installer import check_ffmpeg

__all__ = ['check_ffmpeg']