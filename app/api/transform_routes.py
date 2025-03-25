"""
Transform Routes Module.

This module contains the API routes for data transformations using FastAPI.
"""

from fastapi import APIRouter, HTTPException, Request
from app.core.transform_kgout_pxlsviz_service import TransformKGOutPxLSVizService
from app.models.pxlsviz import PxLSVizTransformRequest, PxLSVizResponse
from app.utils.logger import get_logger
from app.middleware.context import get_request_id

logger = get_logger()
router = APIRouter(prefix="/api/v1/transform", tags=["transformations"])

@router.post("/pxlsviz", response_model=PxLSVizResponse)
async def transform_to_pxlsviz(request: Request, transform_request: PxLSVizTransformRequest) -> PxLSVizResponse:
    """
    Transform input JSON data into PxLSViz format.
    
    Args:
        request: The FastAPI request object
        transform_request: The validated request containing input JSON and parameters
        
    Returns:
        PxLSVizResponse: The transformed data in PxLSViz format
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Log the raw request body for debugging
        body = await request.body()
        logger.debug(
            "Received raw request body for transformation",
            extra={
                "request_id": get_request_id(),
                "raw_body": body.decode()
            }
        )
        
        result = await TransformKGOutPxLSVizService.transform_to_pxlsviz(
            transform_request.input_json,
            transform_request.parameters
        )
        
        return PxLSVizResponse(**result)
        
    except Exception as e:
        error_message = f"Error transforming data: {str(e)}"
        logger.error(
            error_message,
            extra={
                "request_id": get_request_id(),
                "error": str(e)
            }
        )
        raise HTTPException(status_code=500, detail=error_message) 