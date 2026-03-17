# Endpoints to manage technology skills

# app/routers/skill_router.py

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
from app.schemas.skill_schema import SkillCreate, SkillUpdate, SkillResponse

# Services
from app.services import skill_service

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# ROUTER INITIALIZATION
# -------------------------------------------------------------------
router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)

# -------------------------------------------------------------------
# DEBUG LOG HELPER FUNCTIONS
# -------------------------------------------------------------------
def log_router_start(endpoint_name: str) -> None:
    """Logs when an endpoint execution begins."""
    logger.debug(f"[SKILL ROUTER] Entering {endpoint_name} endpoint")

def log_router_success(endpoint_name: str) -> None:
    """Logs when an endpoint completes successfully."""
    logger.debug(f"[SKILL ROUTER] {endpoint_name.capitalize()} successful")

def log_router_error(endpoint_name: str, error: Exception) -> None:
    """Logs errors or exceptions in an endpoint."""
    logger.error(f"[SKILL ROUTER] Error in {endpoint_name} endpoint: {error}")

# -------------------------------------------------------------------
# CRUD ENDPOINTS
# -------------------------------------------------------------------

@router.post(
    "/", # [MODIFIED] Changed from "" to "/" to prevent 307 Redirect CORS blocks
    response_model=SkillResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill"
)
def create_skill(skill_data: SkillCreate, db: Session = Depends(get_db)):
    """
    Create a new skill entry in the master database.
    Includes AI-powered normalization and semantic duplicate detection.
    """
    log_router_start("create skill")
    try:
        new_skill = skill_service.create_skill(db=db, skill=skill_data)
        if not new_skill:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill could not be created or already exists."
            )
        log_router_success("create skill")
        return new_skill
    except HTTPException as http_exc:
        log_router_error("create skill", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("create skill", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the skill."
        )

@router.get(
    "/",  # [MODIFIED] Changed from "" to "/" to prevent 307 Redirect CORS blocks
    response_model=List[SkillResponse], 
    status_code=status.HTTP_200_OK,
    summary="Get all skills"
)
def get_all_skills(db: Session = Depends(get_db)):
    """
    Retrieve a complete list of all skills stored in the system.
    """
    log_router_start("get all skills")
    try:
        skills = skill_service.get_all_skills(db=db)
        log_router_success("get all skills")
        return skills
    except Exception as e:
        log_router_error("get all skills", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching skills."
        )

@router.get(
    "/{skill_id}", 
    response_model=SkillResponse, 
    status_code=status.HTTP_200_OK,
    summary="Get a specific skill by ID"
)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information about a specific skill using its ID.
    """
    log_router_start("get skill by id")
    try:
        skill = skill_service.get_skill_by_id(db=db, skill_id=skill_id)
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with ID {skill_id} not found."
            )
        log_router_success("get skill by id")
        return skill
    except HTTPException as http_exc:
        log_router_error("get skill by id", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("get skill by id", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the skill."
        )

@router.put(
    "/{skill_id}", 
    response_model=SkillResponse, 
    status_code=status.HTTP_200_OK,
    summary="Update skill details"
)
def update_skill(skill_id: int, skill_data: SkillUpdate, db: Session = Depends(get_db)):
    """
    Update the attributes of an existing skill (e.g., category, description).
    """
    log_router_start("update skill")
    try:
        updated_skill = skill_service.update_skill(db=db, skill_id=skill_id, skill_data=skill_data)
        if not updated_skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with ID {skill_id} not found."
            )
        log_router_success("update skill")
        return updated_skill
    except HTTPException as http_exc:
        log_router_error("update skill", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("update skill", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the skill."
        )

@router.delete(
    "/{skill_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete a skill"
)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    """
    Remove a skill from the system. Cascades to remove developer mappings.
    """
    log_router_start("delete skill")
    try:
        success = skill_service.delete_skill(db=db, skill_id=skill_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with ID {skill_id} not found."
            )
        log_router_success("delete skill")
        return {"message": f"Skill with ID {skill_id} successfully deleted."}
    except HTTPException as http_exc:
        log_router_error("delete skill", http_exc)
        raise http_exc
    except Exception as e:
        log_router_error("delete skill", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the skill."
        )