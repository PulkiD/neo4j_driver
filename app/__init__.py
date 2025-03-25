"""
Main application module.

This module initializes the FastAPI application and registers all routers.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.query_routes import router as query_router
from app.utils.logger import get_logger
from app.middleware.context import RequestContextMiddleware

logger = get_logger()

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: The configured FastAPI application instance
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize FastAPI app
    app = FastAPI(
        title="Neo4j Driver API",
        description="A FastAPI-based driver for Neo4j database operations",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request context middleware
    app.add_middleware(RequestContextMiddleware)
    
    # Register routers
    app.include_router(query_router)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    logger.info("FastAPI application initialized successfully")
    return app

# Create the FastAPI application instance
app = create_app() 