"""
Archive Statistics Resource for MCP
Provides statistical information about the gazette archive
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from fastmcp import FastMCP


def get_archive_stats_resource(mcp: FastMCP) -> None:
    """
    Register archive statistics resources with the MCP server
    """
    
    @mcp.resource("gazette://stats/summary")
    def get_archive_summary() -> Dict[str, Any]:
        """Get comprehensive archive statistics"""
        archive_path = Path("archive")
        
        if not archive_path.exists():
            return {"error": "Archive directory not found. Run archive operation first."}
        
        stats = {
            "total_years": 0,
            "total_documents": 0,
            "total_size_mb": 0,
            "yearly_breakdown": {},
            "languages": {},
            "categories": {}
        }
        
        try:
            # Count year directories
            year_dirs = [d for d in archive_path.iterdir() if d.is_dir() and d.name.isdigit()]
            stats["total_years"] = len(year_dirs)
            
            for year_dir in year_dirs:
                year = int(year_dir.name)
                year_stats = {
                    "documents": 0,
                    "size_mb": 0,
                    "months": {}
                }
                
                # Count PDF files
                pdf_files = list(year_dir.rglob("*.pdf"))
                year_stats["documents"] = len(pdf_files)
                stats["total_documents"] += len(pdf_files)
                
                # Calculate size
                total_size = sum(f.stat().st_size for f in pdf_files)
                year_stats["size_mb"] = round(total_size / (1024 * 1024), 2)
                stats["total_size_mb"] += year_stats["size_mb"]
                
                # Organize by month
                for pdf_file in pdf_files:
                    month = pdf_file.parent.name if pdf_file.parent != year_dir else "unknown"
                    if month not in year_stats["months"]:
                        year_stats["months"][month] = 0
                    year_stats["months"][month] += 1
                
                stats["yearly_breakdown"][str(year)] = year_stats
            
            # Read classification data if available
            classified_files = 0
            for year_dir in year_dirs:
                classified_csv = year_dir / "classified_metadata.csv"
                if classified_csv.exists():
                    with open(classified_csv, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            classified_files += 1
                            # Count by language and category
                            lang = row.get('language', 'unknown')
                            category = row.get('category', 'unknown')
                            stats["languages"][lang] = stats["languages"].get(lang, 0) + 1
                            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            stats["classified_documents"] = classified_files
            
            return stats
            
        except Exception as e:
            return {"error": f"Failed to calculate statistics: {str(e)}"}
    
    @mcp.resource("gazette://stats/failures")
    def get_failure_summary() -> Dict[str, Any]:
        """Get summary of failed downloads and errors"""
        archive_path = Path("archive")
        
        if not archive_path.exists():
            return {"error": "Archive directory not found."}
        
        failures = {
            "total_failures": 0,
            "failure_reasons": {},
            "yearly_failures": {}
        }
        
        try:
            year_dirs = [d for d in archive_path.iterdir() if d.is_dir() and d.name.isdigit()]
            
            for year_dir in year_dirs:
                year = year_dir.name
                failed_log = year_dir / "failed_logs.csv"
                unavailable_log = year_dir / "unavailable_logs.csv"
                
                year_failures = 0
                
                # Process failed downloads
                if failed_log.exists():
                    with open(failed_log, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            year_failures += 1
                            reason = row.get('error', 'unknown')
                            failures["failure_reasons"][reason] = failures["failure_reasons"].get(reason, 0) + 1
                
                # Process unavailable documents
                if unavailable_log.exists():
                    with open(unavailable_log, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            year_failures += 1
                            reason = "document_unavailable"
                            failures["failure_reasons"][reason] = failures["failure_reasons"].get(reason, 0) + 1
                
                failures["yearly_failures"][year] = year_failures
                failures["total_failures"] += year_failures
            
            return failures
            
        except Exception as e:
            return {"error": f"Failed to analyze failures: {str(e)}"}
