"""
Gazette Metadata Resource for MCP
Provides access to gazette metadata and document information
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastmcp import FastMCP


def get_gazette_metadata_resource(mcp: FastMCP) -> None:
    """
    Register gazette metadata resources with the MCP server
    """
    
    @mcp.resource("gazette://metadata/latest")
    def get_latest_metadata() -> Dict[str, Any]:
        """Get the latest gazette metadata from the archive"""
        meta_data_path = Path("meta_data/doc_metadata.json")
        
        if not meta_data_path.exists():
            return {"error": "No metadata found. Run archive operation first."}
        
        try:
            with open(meta_data_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Return latest entries (last 10)
            if isinstance(metadata, list):
                return {"latest_gazettes": metadata[-10:]}
            else:
                return {"metadata": metadata}
                
        except Exception as e:
            return {"error": f"Failed to read metadata: {str(e)}"}
    
    @mcp.resource("gazette://metadata/by-date/{year}/{month}/{day}")
    def get_metadata_by_date(year: int, month: int, day: int) -> Dict[str, Any]:
        """Get gazette metadata for a specific date"""
        meta_data_path = Path("meta_data/doc_metadata.json")
        
        if not meta_data_path.exists():
            return {"error": "No metadata found. Run archive operation first."}
        
        try:
            with open(meta_data_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Filter by date
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            filtered = []
            
            if isinstance(metadata, list):
                for item in metadata:
                    if item.get('date') == date_str:
                        filtered.append(item)
            
            return {
                "date": date_str,
                "gazettes": filtered,
                "count": len(filtered)
            }
            
        except Exception as e:
            return {"error": f"Failed to filter metadata: {str(e)}"}
    
    @mcp.resource("gazette://config/current")
    def get_current_config() -> Dict[str, Any]:
        """Get current configuration settings"""
        config_path = Path("gztarchiver_config.yaml")
        
        if not config_path.exists():
            return {"error": "Configuration file not found. Run setup first."}
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Return safe config (without sensitive keys)
            safe_config = {
                "archive": config.get("archive", {}),
                "scrape": config.get("scrape", {}),
                "output": config.get("output", {})
            }
            
            return safe_config
            
        except Exception as e:
            return {"error": f"Failed to read config: {str(e)}"}
