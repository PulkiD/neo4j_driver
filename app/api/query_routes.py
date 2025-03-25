"""
Query Routes Module.

This module contains the API routes for executing Neo4j queries using FastAPI.
"""

from fastapi import APIRouter, HTTPException
from app.core.query_service import QueryService
from app.models.query import QueryRequest, QueryResponse
from app.utils.logger import get_logger

logger = get_logger()
router = APIRouter(prefix="/api/v1", tags=["queries"])

@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest) -> QueryResponse:
    """
    Execute a Cypher query endpoint.
    
    Args:
        request (QueryRequest): The query request containing the Cypher query and parameters
        
    Returns:
        QueryResponse: The query results or error response
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        logger.info(f"Received query request: {request.query}")
        result = await QueryService.execute_cypher_query(request.query, request.parameters)
        
        if result.status == "error":
            raise HTTPException(status_code=400, detail=result.error)
            
        return result
        
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message) 