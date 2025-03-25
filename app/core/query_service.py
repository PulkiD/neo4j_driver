"""
Query Service Module.

This module contains the business logic for executing and processing Neo4j queries.
"""

from app.core.db import get_db
from app.utils.logger import get_logger
from app.models.query import QueryResponse
from app.middleware.context import get_request_id

logger = get_logger()

class QueryService:
    """Service class for handling Neo4j query operations."""

    @staticmethod
    async def execute_cypher_query(query: str, params: dict = None) -> QueryResponse:
        """
        Execute a Cypher query and format the results.
        
        Args:
            query (str): The Cypher query to execute
            params (dict, optional): Parameters for the query. Defaults to None.
            
        Returns:
            QueryResponse: A Pydantic model containing the query results and metadata
            
        Raises:
            Exception: If there's an error executing the query
        """
        request_id = get_request_id()
        try:
            logger.info(
                f"Executing query: {query}",
                extra={
                    "request_id": request_id,
                    "query": query,
                    "parameters": params
                }
            )
            
            db = get_db()
            results = await db.execute_query(query, params)
            
            formatted_results = QueryResponse(
                status="success",
                count=len(results),
                results=results,
                metadata={
                    "query": query,
                    "parameters": params or {},
                    "request_id": request_id
                }
            )
            
            logger.info(
                f"Query executed successfully. Found {len(results)} results.",
                extra={
                    "request_id": request_id,
                    "result_count": len(results)
                }
            )
            return formatted_results
            
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            logger.error(
                error_message,
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "query": query,
                    "parameters": params
                }
            )
            return QueryResponse(
                status="error",
                error=error_message,
                metadata={
                    "query": query,
                    "parameters": params or {},
                    "request_id": request_id
                }
            ) 