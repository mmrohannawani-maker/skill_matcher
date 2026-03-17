# API schemas for skill data

# app/schemas/skill_schema.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

def debug_log(message: str) -> None:
    """Helper function to log debug messages for Skill schemas."""
    print(f"[SKILL_SCHEMA DEBUG] {message}")

debug_log("Skill schemas loaded successfully")

"""
What skills represent in the system:
Skills are the specific technologies, tools, and languages (e.g., Python, AWS, Docker) 
recognized within the organization. These are managed by admins and serve as the 
basis for matching developers to job requirements.

Difference between Create, Update, and Response schemas:
- SkillBase: The foundation holding shared attributes across all operations.
- SkillCreate: Inherits from the base; used for initial creation where all required fields are validated.
- SkillUpdate: All fields are optional, allowing for partial modifications of an existing skill.
- SkillResponse: Includes backend-generated fields like `id` and `created_at` for data returning to clients.

Why ORM mode is required:
`orm_mode = True` enables the Pydantic response models to seamlessly serialize 
SQLAlchemy objects. Instead of expecting a Python dictionary, Pydantic will extract 
attributes directly using dot notation (e.g., `skill.skill_name`).
"""

class SkillBase(BaseModel):
    """Common attributes for a Skill."""
    skill_name: str
    category: Optional[str] = None
    description: Optional[str] = None


class SkillCreate(SkillBase):
    """Schema for validating data when an Admin creates a new Skill."""
    pass


class SkillUpdate(BaseModel):
    """
    Schema for validating data when updating a Skill.
    All fields are optional to support partial updates.
    """
    skill_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class SkillResponse(SkillBase):
    """
    Schema for formatting the API response for a Skill.
    Includes database-generated fields.
    """
    id: int
    created_at: datetime

    class Config:
        """Enables compatibility with SQLAlchemy ORM models."""
        from_attributes = True