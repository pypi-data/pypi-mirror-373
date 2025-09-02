"""
Data formatters for Gazette Archiver MCP
Helper functions to format and structure data for MCP resources and prompts
"""

import json
from typing import Dict, Any, List
from datetime import datetime


def format_archive_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format raw archive data into a structured format for MCP resources
    
    Args:
        raw_data: Raw archive data from files
    
    Returns:
        Formatted data ready for MCP consumption
    """
    
    formatted = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "format_version": "1.0"
        },
        "data": {}
    }
    
    if isinstance(raw_data, list):
        formatted["data"]["documents"] = raw_data
        formatted["data"]["count"] = len(raw_data)
    elif isinstance(raw_data, dict):
        formatted["data"] = raw_data
    
    return formatted


def format_error_summary(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format error data into a summary for MCP resources
    
    Args:
        errors: List of error dictionaries
    
    Returns:
        Formatted error summary
    """
    
    error_summary = {
        "total_errors": len(errors),
        "error_types": {},
        "time_distribution": {},
        "severity_levels": {
            "critical": 0,
            "warning": 0,
            "info": 0
        }
    }
    
    for error in errors:
        error_type = error.get('type', 'unknown')
        error_summary["error_types"][error_type] = error_summary["error_types"].get(error_type, 0) + 1
        
        severity = error.get('severity', 'info')
        if severity in error_summary["severity_levels"]:
            error_summary["severity_levels"][severity] += 1
        
        # Group by date if available
        timestamp = error.get('timestamp')
        if timestamp:
            date_key = timestamp[:10]  # YYYY-MM-DD
            error_summary["time_distribution"][date_key] = error_summary["time_distribution"].get(date_key, 0) + 1
    
    return error_summary


def format_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Format date range for queries
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Structured date range object
    """
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        return {
            "start": {
                "year": start.year,
                "month": start.month,
                "day": start.day,
                "formatted": start_date
            },
            "end": {
                "year": end.year,
                "month": end.month,
                "day": end.day,
                "formatted": end_date
            },
            "duration_days": (end - start).days + 1
        }
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
