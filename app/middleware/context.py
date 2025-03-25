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
        request_id_context.set(request_id)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Initialize database connection if not already initialized
        db = get_db()
        
        # Log request details
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else None
            }
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Log response details
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            # Log error details
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e)
                }
            )
            raise
        finally:
            # Clear request context
            request_id_context.set("")

def get_request_id() -> str:
    """
    Get the current request ID from context.
    
    Returns:
        str: The current request ID or empty string if not in request context
    """
    return request_id_context.get() 