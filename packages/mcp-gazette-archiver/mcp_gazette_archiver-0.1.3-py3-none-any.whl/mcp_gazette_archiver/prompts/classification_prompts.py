"""
Classification Prompts for MCP
Provides prompts for AI-powered document classification
"""

from typing import Dict, Any, List
from fastmcp import FastMCP


def get_classification_prompts(mcp: FastMCP) -> None:
    """
    Register classification prompts with the MCP server
    """
    
    @mcp.prompt("gazette-classifier")
    def create_classification_prompt(
        document_title: str,
        document_url: str,
        document_date: str,
        additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a classification prompt for a gazette document
        
        Args:
            document_title: Title of the gazette document
            document_url: URL of the document
            document_date: Publication date of the document
            additional_context: Additional context like keywords, description, etc.
        
        Returns:
            Structured classification prompt for AI processing
        """
        
        classification_prompt = {
            "document_info": {
                "title": document_title,
                "url": document_url,
                "date": document_date,
                "context": additional_context or {}
            },
            "classification_task": {
                "categories": [
                    "Government Appointments",
                    "Regulations & Rules",
                    "Public Notices",
                    "Legal Acts & Bills",
                    "Ministry Orders",
                    "Financial Notifications",
                    "Land & Property",
                    "Education",
                    "Health",
                    "Transport",
                    "Environment",
                    "Trade & Commerce",
                    "Other"
                ],
                "languages": ["en", "si", "ta"],
                "priority_levels": ["high", "medium", "low"],
                "urgency_indicators": ["immediate_action", "standard", "informational"]
            },
            "instructions": [
                "Analyze the document title and classify it into the most appropriate category",
                "Determine the primary language of the document",
                "Assess the priority level based on content urgency",
                "Identify if the document requires immediate action",
                "Provide a brief summary (1-2 sentences) of what the document is about",
                "Extract key entities mentioned (ministries, departments, individuals, locations)"
            ]
        }
        
        return classification_prompt
    
    @mcp.prompt("batch-classifier")
    def create_batch_classification_prompt(
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a batch classification prompt for multiple documents
        
        Args:
            documents: List of documents with title, url, date, and context
        
        Returns:
            Batch classification prompt for efficient processing
        """
        
        batch_prompt = {
            "documents": documents,
            "classification_schema": {
                "primary_categories": [
                    "Government Appointments",
                    "Regulations & Rules", 
                    "Public Notices",
                    "Legal Acts & Bills",
                    "Ministry Orders",
                    "Financial Notifications",
                    "Land & Property",
                    "Education",
                    "Health",
                    "Transport",
                    "Environment",
                    "Trade & Commerce",
                    "Other"
                ],
                "sub_categories": {
                    "Government Appointments": ["Senior Officials", "Board Members", "Committee Members"],
                    "Regulations & Rules": ["New Regulations", "Amendments", "Repeals"],
                    "Public Notices": ["Tenders", "Auctions", "Public Hearings"],
                    "Legal Acts & Bills": ["New Acts", "Amendments", "Repeals"],
                    "Ministry Orders": ["Administrative Orders", "Policy Directives"],
                    "Financial Notifications": ["Budget", "Grants", "Fees", "Taxes"]
                }
            },
            "processing_instructions": [
                "Process each document individually",
                "Assign primary category and sub-category if applicable",
                "Determine language (en/si/ta)",
                "Assess urgency level",
                "Provide confidence score (0-1) for each classification",
                "Flag documents that need manual review (confidence < 0.7)",
                "Generate concise summary for each document"
            ],
            "output_format": {
                "document_id": "original document identifier",
                "primary_category": "main classification",
                "sub_category": "detailed classification (optional)",
                "language": "en|si|ta",
                "urgency": "high|medium|low",
                "confidence": "0.0-1.0",
                "summary": "brief document summary",
                "key_entities": ["list of important entities"],
                "requires_review": "true|false"
            }
        }
        
        return batch_prompt
