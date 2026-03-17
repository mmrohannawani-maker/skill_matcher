# Endpoints to generate dashboard reports
# ==========================================
# DEPENDENCY INSTALLATION:
# pip install fastapi
# pip install sqlalchemy
# ==========================================

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Database dependencies
from app.core.dependencies import get_db

# Services
from app.services import report_service

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# ROUTER INITIALIZATION
# -------------------------------------------------------------------
router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# -------------------------------------------------------------------
# DEBUG LOG HELPER FUNCTIONS
# -------------------------------------------------------------------
def log_router_start(endpoint_name: str) -> None:
    """Logs when an endpoint execution begins."""
    logger.debug(f"[REPORT ROUTER] Endpoint started: {endpoint_name}")

def log_router_success(endpoint_name: str) -> None:
    """Logs when an endpoint completes successfully."""
    logger.debug(f"[REPORT ROUTER] Endpoint completed successfully")

def log_router_error(endpoint_name: str, error: Exception) -> None:
    """Logs errors or exceptions in an endpoint."""
    logger.error(f"[REPORT ROUTER] Error in endpoint: {error}")

# -------------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------------



@router.get(
    "/skill-distribution",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get skill distribution analytics"
)
def get_skill_distribution(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns analytics about how skills are distributed across developers.
    """
    endpoint_name = "generate_skill_distribution"
    log_router_start(endpoint_name)
    try:
        report = report_service.generate_skill_distribution_report(db)
        log_router_success(endpoint_name)
        return report
    except Exception as e:
        log_router_error(endpoint_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal report generation error while fetching skill distribution."
        )


@router.get(
    "/developer-availability",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get developer availability metrics"
)
def get_developer_availability(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns how many developers are available vs assigned.
    """
    endpoint_name = "generate_developer_availability"
    log_router_start(endpoint_name)
    try:
        report = report_service.generate_developer_availability_report(db)
        log_router_success(endpoint_name)
        return report
    except Exception as e:
        log_router_error(endpoint_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal report generation error while fetching developer availability."
        )


@router.get(
    "/top-developers",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get top-rated developers"
)
def get_top_developers(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Returns the highest rated developers in the organization.
    """
    endpoint_name = "get_top_developers"
    log_router_start(endpoint_name)
    try:
        report = report_service.get_top_developers_report(db)
        log_router_success(endpoint_name)
        return report
    except Exception as e:
        log_router_error(endpoint_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal report generation error while fetching top developers."
        )


@router.get(
    "/ai-insights",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get AI-generated skill insights"
)
def get_ai_insights(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns AI-generated insights about organization skill trends.
    """
    endpoint_name = "generate_ai_insights"
    log_router_start(endpoint_name)
    try:
        report = report_service.generate_ai_skill_insights(db)
        log_router_success(endpoint_name)
        return report
    except Exception as e:
        log_router_error(endpoint_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal report generation error while generating AI insights."
        )


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get high-level organization summary"
)
def get_organization_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns a high-level summary of the organization (total devs, skills, etc.).
    """
    endpoint_name = "generate_organization_summary"
    log_router_start(endpoint_name)
    try:
        report = report_service.generate_organization_summary(db)
        log_router_success(endpoint_name)
        return report
    except Exception as e:
        log_router_error(endpoint_name, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal report generation error while fetching organization summary."
        )