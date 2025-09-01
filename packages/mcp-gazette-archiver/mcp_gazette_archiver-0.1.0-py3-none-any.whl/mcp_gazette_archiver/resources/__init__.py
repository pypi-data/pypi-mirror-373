"""
MCP Resources for Gazette Archiver
Provides data resources that can be accessed by MCP clients
"""

from .gazette_metadata import get_gazette_metadata_resource
from .archive_stats import get_archive_stats_resource

__all__ = [
    "get_gazette_metadata_resource",
    "get_archive_stats_resource"
]
