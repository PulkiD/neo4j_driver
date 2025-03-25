"""
Query Routes Module.

This module contains the API routes for executing Neo4j queries using FastAPI.
"""

from fastapi import APIRouter, HTTPException, Request
from app.core.readkg_service import ReadKGService
from app.models.query import QueryRequest, QueryResponse
from app.utils.logger import get_logger
from app.middleware.context import get_request_id

logger = get_logger()
router = APIRouter(prefix="/api/v1", tags=["queries"])

@router.post("/read", response_model=QueryResponse)
async def execute_query(request: Request, query_request: QueryRequest) -> QueryResponse:
    """
    Execute a Cypher query endpoint.
    
    Args:
        request: The FastAPI request object
        query_request: The validated query request containing the Cypher query and parameters
        
    Returns:
        QueryResponse: The query results or error response
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Log the raw request body for debugging
        body = await request.body()
        logger.debug(
            "Received raw request body",
            extra={
                "request_id": get_request_id(),
                "raw_body": body.decode()
            }
        )
        
        result = await ReadKGService.execute_cypher_query(
            query_request.query,
            query_request.parameters
        )
        
        if result.status == "error":
            raise HTTPException(status_code=400, detail=result.error)
            
        return result
        
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        logger.error(
            error_message,
            extra={
                "request_id": get_request_id(),
                "error": str(e),
                "query": query_request.query if hasattr(query_request, 'query') else None,
                "parameters": query_request.parameters if hasattr(query_request, 'parameters') else None
            }
        )
        raise HTTPException(status_code=500, detail=error_message) 