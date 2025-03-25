"""
Query Routes Module.

This module contains the API routes for executing Neo4j queries.
"""

from flask import Blueprint, request, jsonify
from app.core.query_service import QueryService
from app.utils.logger import get_logger

logger = get_logger()
query_bp = Blueprint('query', __name__)

@query_bp.route('/api/v1/query', methods=['POST'])
def execute_query():
    """
    Execute a Cypher query endpoint.
    
    Expected JSON payload:
    {
        "query": "MATCH (n) RETURN n LIMIT 5",
        "parameters": {} (optional)
    }
    
    Returns:
        JSON response with query results or error message
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Query is required in the request body'
            }), 400
            
        query = data.get('query')
        params = data.get('parameters', {})
        
        logger.info(f"Received query request: {query}")
        result = QueryService.execute_cypher_query(query, params)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        logger.error(error_message)
        return jsonify({
            'status': 'error',
            'error': error_message
        }), 500 