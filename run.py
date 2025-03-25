"""
Application runner script.

This script is used to run the FastAPI application using uvicorn.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # Use the import string format: "module:app_instance"
        host="0.0.0.0",
        port=5001,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 