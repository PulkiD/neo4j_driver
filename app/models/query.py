"""
Query Models Module.

This module contains Pydantic models for request and response validation.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """
    Pydantic model for query request validation.
    
    Attributes:
        query (str): The Cypher query to execute
        parameters (Dict[str, Any], optional): Query parameters. Defaults to empty dict.
    """
    query: str = Field(..., description="The Cypher query to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")

class QueryResponse(BaseModel):
    """
    Pydantic model for query response validation.
    
    Attributes:
        status (str): Response status (success/error)
        count (Optional[int]): Number of results
        results (Optional[List[Dict[str, Any]]]): Query results
        error (Optional[str]): Error message if status is error
        metadata (Dict[str, Any]): Query metadata
    """
    status: str = Field(..., description="Response status (success/error)")
    count: Optional[int] = Field(None, description="Number of results")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    error: Optional[str] = Field(None, description="Error message if status is error")
    metadata: Dict[str, Any] = Field(..., description="Query metadata") 