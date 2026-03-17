# Endpoint where sales paste JD to find matching developers

# app/routers/jd_router.py

# ==========================================
# DEPENDENCY INSTALLATION:
# pip install fastapi sqlalchemy
# ==========================================

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Database dependencies
from app.core.dependencies import get_db

# Schemas
from app.schemas.jd_schema import JDCreate, JDSearchResponse

# Services
from app.services import jd_service

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# ROUTER INITIALIZATION
# -------------------------------------------------------------------
router = APIRouter(
    prefix="/jd",
    tags=["Job Description Matching"]
)

# -------------------------------------------------------------------
# DEBUG LOG HELPER FUNCTIONS
# -------------------------------------------------------------------
def log_router_start(endpoint_name: str) -> None:
    """Logs when an endpoint execution begins."""
    logger.debug(f"[JD ROUTER] Entering {endpoint_name} endpoint")

def log_router_success(endpoint_name: str) -> None:
    """Logs when an endpoint completes successfully."""
    logger.debug(f"[JD ROUTER] {endpoint_name.capitalize()} completed successfully")

def log_router_error(endpoint_name: str, error: Exception) -> None:
    """Logs errors or exceptions in an endpoint."""
    logger.error(f"[JD ROUTER] Error in {endpoint_name} endpoint: {error}")

# -------------------------------------------------------------------
# ENDPOINTS
# -------------------------------------------------------------------



@router.post(
    "/analyze",
    response_model=JDSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a job description and find best matching developers"
)
def analyze_job_description(jd_request: JDCreate, db: Session = Depends(get_db)):
    """
    Accepts raw job description text.
    Delegates to jd_service to perform NLP skill extraction, AI inference, 
    developer matching, and scoring. Returns structured match results.
    """
    log_router_start("analyze")
    try:
        match_results = jd_service.analyze_job_description(db=db, jd_request=jd_request)
        if not match_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid job description input or analysis failed."
            )
        log_router_success("analyze")
        return match_results
    except HTTPException as http_exc:
        log_router_error("analyze", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("analyze", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during job description analysis."
        )

@router.get(
    "/history",
    response_model=List[JDSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Fetch all previous JD search records"
)
def get_jd_history(db: Session = Depends(get_db)):
    """
    Retrieves the history of all previously analyzed job descriptions
    and their search results.
    """
    log_router_start("get history")
    try:
        history = jd_service.get_jd_history(db=db)
        log_router_success("get history")
        return history
    except Exception as e:
        log_router_error("get history", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching JD search history."
        )

@router.get(
    "/history/{search_id}",
    response_model=JDSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Fetch a single JD search record"
)
def get_jd_record(search_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific job description search record by its ID.
    """
    log_router_start("get single record")
    try:
        record = jd_service.get_jd_by_id(db=db, search_id=search_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"JD search record with ID {search_id} not found."
            )
        log_router_success("get single record")
        return record
    except HTTPException as http_exc:
        log_router_error("get single record", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("get single record", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the JD search record."
        )

@router.delete(
    "/history/{search_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a JD search record"
)
def delete_jd_record(search_id: int, db: Session = Depends(get_db)):
    """
    Deletes a specific job description search record from the history.
    """
    log_router_start("delete record")
    try:
        success = jd_service.delete_jd_record(db=db, search_id=search_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"JD search record with ID {search_id} not found."
            )
        log_router_success("delete record")
        return {"message": f"JD search record with ID {search_id} successfully deleted."}
    except HTTPException as http_exc:
        log_router_error("delete record", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("delete record", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the JD search record."
        )