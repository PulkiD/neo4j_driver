"""
PxLSViz Models Module.

This module contains Pydantic models for PxLSViz transformation request and response validation.
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field

class PxLSVizTransformRequest(BaseModel):
    """
    Pydantic model for PxLSViz transformation request.
    
    Attributes:
        input_json (List[Dict[str, Dict[str, Any]]]): The input JSON data to transform
        parameters (Dict[str, Any], optional): Transformation parameters. Defaults to empty dict.
    """
    input_json: List[Dict[str, Dict[str, Any]]] = Field(..., description="The input JSON data to transform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Transformation parameters")

class PxLSVizNode(BaseModel):
    """
    Pydantic model for a node in PxLSViz format.
    """
    id: str = Field(..., description="Node identifier")
    # Add any other common node properties here

class PxLSVizRelationship(BaseModel):
    """
    Pydantic model for a relationship in PxLSViz format.
    """
    id: str = Field(..., description="Relationship identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Relationship type")
    # Add any other common relationship properties here

class PxLSVizResponse(BaseModel):
    """
    Pydantic model for PxLSViz transformation response.
    
    Attributes:
        nodes (List[Dict[str, Any]]): List of transformed nodes
        relationships (List[Dict[str, Any]]): List of transformed relationships
    """
    nodes: List[Dict[str, Any]] = Field(..., description="List of transformed nodes")
    relationships: List[Dict[str, Any]] = Field(..., description="List of transformed relationships") 