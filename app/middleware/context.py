"""
Context Middleware Module.

This module provides middleware for request context management,
database connection handling, and request-scoped logging.
"""

import uuid
from contextvars import ContextVar
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.core.db import get_db
from app.utils.logger import get_logger

# Context variables for request-scoped data
request_id_context: ContextVar[str] = ContextVar("request_id", default="")
logger = get_logger()

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for managing request context, database connections,
    and request-scoped logging.
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process each request through the middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            
        Returns:
            Response: The response from the endpoint
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        token = request_id_context.set(request_id)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Initialize database connection if not already initialized
        db = await get_db()
        
        # Log request details
        logger.info(
            f"Processing request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path
            }
        )
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Clean up request context using the token
            request_id_context.reset(token)

def get_request_id() -> str:
    """
    Get the current request ID from context.
    
    Returns:
        str: The current request ID or empty string if not in request context
    """
    return request_id_context.get() 