"""
Archive Query Prompts for MCP
Provides prompt templates for querying gazette archives
"""

from typing import Dict, Any, List
from fastmcp import FastMCP


def get_archive_query_prompts(mcp: FastMCP) -> None:
    """
    Register archive query prompts with the MCP server
    """
    
    @mcp.prompt("gazette-query")
    def create_archive_query(
        query_type: str,
        date_range: Dict[str, int] = None,
        keywords: List[str] = None,
        language: str = None,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Generate a structured query for searching the gazette archive
        
        Args:
            query_type: Type of query ('search', 'summary', 'count', 'details')
            date_range: Dictionary with 'start_year', 'start_month', 'start_day', 'end_year', 'end_month', 'end_day'
            keywords: List of keywords to search for
            language: Language filter ('en', 'si', 'ta')
            category: Document category to filter by
        
        Returns:
            Structured query object ready for archive search
        """
        
        prompt_template = {
            "query_type": query_type,
            "filters": {},
            "instructions": []
        }
        
        # Date range filtering
        if date_range:
            prompt_template["filters"]["date_range"] = date_range
            prompt_template["instructions"].append(
                f"Filter documents from {date_range.get('start_year', 'any')}-{date_range.get('start_month', 'any')}-{date_range.get('start_day', 'any')} "
                f"to {date_range.get('end_year', 'any')}-{date_range.get('end_month', 'any')}-{date_range.get('end_day', 'any')}"
            )
        
        # Keyword search
        if keywords:
            prompt_template["filters"]["keywords"] = keywords
            prompt_template["instructions"].append(
                f"Search for documents containing: {', '.join(keywords)}"
            )
        
        # Language filtering
        if language:
            prompt_template["filters"]["language"] = language
            prompt_template["instructions"].append(f"Filter by language: {language}")
        
        # Category filtering
        if category:
            prompt_template["filters"]["category"] = category
            prompt_template["instructions"].append(f"Filter by category: {category}")
        
        # Query-specific instructions
        if query_type == "search":
            prompt_template["instructions"].append(
                "Return matching documents with full metadata including title, date, category, and download links"
            )
        elif query_type == "summary":
            prompt_template["instructions"].append(
                "Provide a summary of matching documents including count, date range, and key categories"
            )
        elif query_type == "count":
            prompt_template["instructions"].append(
                "Return only the count of matching documents"
            )
        elif query_type == "details":
            prompt_template["instructions"].append(
                "Return detailed information for each matching document including full content if available"
            )
        
        return prompt_template
   