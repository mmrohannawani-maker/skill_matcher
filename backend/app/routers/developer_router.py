# Endpoints for developer CRUD operations

# app/routers/developer_router.py

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
from app.schemas.developer_schema import DeveloperCreate, DeveloperUpdate, DeveloperResponse

# Services
from app.services import developer_service

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# ROUTER INITIALIZATION
# -------------------------------------------------------------------
router = APIRouter(
    prefix="/developers",
    tags=["Developers"]
)

# -------------------------------------------------------------------
# DEBUG LOG HELPER FUNCTIONS
# -------------------------------------------------------------------
def log_router_start(endpoint_name: str) -> None:
    """Logs when an endpoint is entered."""
    logger.debug(f"[DEVELOPER ROUTER] Entering {endpoint_name} endpoint")

def log_router_success(endpoint_name: str) -> None:
    """Logs when an endpoint completes successfully."""
    logger.debug(f"[DEVELOPER ROUTER] {endpoint_name.capitalize()} successful")

def log_router_error(endpoint_name: str, error: Exception) -> None:
    """Logs when an exception occurs in an endpoint."""
    logger.error(f"[DEVELOPER ROUTER] Error in {endpoint_name} endpoint: {error}")

# -------------------------------------------------------------------
# CRUD ENDPOINTS
# -------------------------------------------------------------------

@router.post(
    "", 
    response_model=DeveloperResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a developer profile"
)
def create_developer(developer_data: DeveloperCreate, db: Session = Depends(get_db)):
    """
    Create a new developer profile in the system.
    """
    log_router_start("create developer")
    try:
        new_developer = developer_service.create_developer(db=db, developer=developer_data)
        log_router_success("create developer")
        return new_developer
    except HTTPException as http_exc:
        log_router_error("create developer", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("create developer", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the developer."
        )

@router.get(
    "", 
    response_model=List[DeveloperResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get all developers"
)
def get_all_developers(db: Session = Depends(get_db)):
    """
    Retrieve a list of all developer profiles.
    """
    log_router_start("get all developers")
    try:
        developers = developer_service.get_all_developers(db=db)
        log_router_success("get all developers")
        return developers
    except Exception as e:
        log_router_error("get all developers", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching developers."
        )

@router.get(
    "/{developer_id}", 
    response_model=DeveloperResponse, 
    status_code=status.HTTP_200_OK,
    summary="Get a single developer profile"
)
def get_developer(developer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific developer profile by their ID.
    """
    log_router_start("get single developer")
    try:
        developer = developer_service.get_developer_by_id(db=db, developer_id=developer_id)
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Developer with ID {developer_id} not found."
            )
        log_router_success("get single developer")
        return developer
    except HTTPException as http_exc:
        log_router_error("get single developer", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("get single developer", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the developer."
        )

@router.put(
    "/{developer_id}", 
    response_model=DeveloperResponse, 
    status_code=status.HTTP_200_OK,
    summary="Update developer information"
)
def update_developer(developer_id: int, developer_data: DeveloperUpdate, db: Session = Depends(get_db)):
    """
    Update an existing developer's profile information.
    """
    log_router_start("update developer")
    try:
        updated_developer = developer_service.update_developer(db=db, developer_id=developer_id, developer_data=developer_data)
        if not updated_developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Developer with ID {developer_id} not found."
            )
        log_router_success("update developer")
        return updated_developer
    except HTTPException as http_exc:
        log_router_error("update developer", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("update developer", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the developer."
        )

@router.delete(
    "/{developer_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete a developer profile"
)
def delete_developer(developer_id: int, db: Session = Depends(get_db)):
    """
    Remove a developer profile from the system.
    """
    log_router_start("delete developer")
    try:
        success = developer_service.delete_developer(db=db, developer_id=developer_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Developer with ID {developer_id} not found."
            )
        log_router_success("delete developer")
        return {"message": f"Developer with ID {developer_id} successfully deleted."}
    except HTTPException as http_exc:
        log_router_error("delete developer", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("delete developer", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the developer."
        )