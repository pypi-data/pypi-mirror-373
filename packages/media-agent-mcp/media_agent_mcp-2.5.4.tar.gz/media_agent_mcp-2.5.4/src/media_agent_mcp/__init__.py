"""Media Agent MCP Server - A Model Context Protocol server for media processing."""

from . import ai_models, media_selectors, storage, video
from .server import main
from .async_server import main as async_main
from . import async_wrapper

__version__ = "0.1.0"
__all__ = ['ai_models', 'media_selectors', 'storage', 'video', 'main', 'async_main', 'async_wrapper']