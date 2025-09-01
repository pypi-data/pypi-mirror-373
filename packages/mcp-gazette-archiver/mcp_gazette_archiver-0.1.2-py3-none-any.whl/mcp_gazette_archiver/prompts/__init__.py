"""
MCP Prompts for Gazette Archiver
Provides prompt templates and query builders for MCP clients
"""

from .archive_queries import get_archive_query_prompts
from .classification_prompts import get_classification_prompts

__all__ = [
    "get_archive_query_prompts",
    "get_classification_prompts"
]
