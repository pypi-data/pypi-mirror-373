"""Storage module for Media Agent MCP.

This module provides storage functionality including TOS integration.
"""

from .tos_client import get_tos_client, upload_to_tos

__all__ = ['get_tos_client', 'upload_to_tos']