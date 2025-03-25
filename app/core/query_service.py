"""
Query Service Module.

This module contains the business logic for executing and processing Neo4j queries.
"""

from app.core.db import get_db
from app.utils.logger import get_logger

logger = get_logger()

class QueryService:
    """Service class for handling Neo4j query operations."""

    @staticmethod
    def execute_cypher_query(query: str, params: dict = None) -> dict:
        """
        Execute a Cypher query and format the results.
        
        Args:
            query (str): The Cypher query to execute
            params (dict, optional): Parameters for the query. Defaults to None.
            
        Returns:
            dict: A dictionary containing the query results and metadata
            
        Raises:
            Exception: If there's an error executing the query
        """
        try:
            logger.info(f"Executing query: {query}")
            db = get_db()
            results = db.execute_query(query, params)
            
            formatted_results = {
                "status": "success",
                "count": len(results),
                "results": results,
                "metadata": {
                    "query": query,
                    "parameters": params or {}
                }
            }
            
            logger.info(f"Query executed successfully. Found {len(results)} results.")
            return formatted_results
            
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "error": error_message,
                "metadata": {
                    "query": query,
                    "parameters": params or {}
                }
            } 