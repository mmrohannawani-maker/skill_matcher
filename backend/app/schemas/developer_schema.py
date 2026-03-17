# API schemas for developer data

# app/schemas/developer_schema.py

from pydantic import BaseModel, EmailStr
# [MODIFIED] Added 'List' to the imports to support the skills array
from typing import Optional, List
from datetime import datetime

def debug_log(message: str) -> None:
    """
    Helper function to trace schema loading and initialization.
    """
    print(f"[DEVELOPER_SCHEMA DEBUG] {message}")

debug_log("Developer schemas loaded successfully")

"""
Purpose of Developer Schemas:
Pydantic schemas are used to define the shape of data entering and leaving the API.
They validate incoming JSON payloads against strict typing rules and ensure outgoing
responses only contain the data we explicitly want to expose to the client.

Difference between Create, Update, and Response schemas:
- Create (DeveloperCreate): Defines the exact payload required to instantiate a new record. Inherits base requirements.
- Update (DeveloperUpdate): Makes all fields optional to support partial updates (e.g., PATCH requests) without requiring the full object.
- Response (DeveloperResponse): Structures the data returned to the user, appending database-generated metadata like 'id' and 'created_at'.

Why response schemas use ORM mode:
FastAPI handles SQLAlchemy model objects, but Pydantic expects Python dictionaries by default.
Enabling 'orm_mode = True' allows Pydantic to seamlessly parse SQLAlchemy ORM objects by 
reading attributes using dot notation (e.g., obj.id instead of obj["id"]).
"""

class DeveloperBase(BaseModel):
    """
    Common fields shared across all Developer schemas.
    Establishes the base data contract for a developer profile.
    """
    name: str
    email: EmailStr
    years_of_experience: int
    department: Optional[str] = None
    current_role: Optional[str] = None
    availability: bool


class DeveloperCreate(DeveloperBase):
    """
    Schema for validating incoming data when creating a new developer.
    Inherits all requirements from DeveloperBase.
    """
    pass


class DeveloperUpdate(BaseModel):
    """
    Schema for validating incoming data when updating an existing developer.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    years_of_experience: Optional[int] = None
    department: Optional[str] = None
    current_role: Optional[str] = None
    availability: Optional[bool] = None


# --- [NEW] Schema specifically for nested skills ---
class DeveloperSkillResponse(BaseModel):
    """
    Schema representing the many-to-many relationship data.
    Allows the developer's skills to pass through the API.
    """
    skill_id: int
    proficiency_level: int
    years_of_experience: int
    last_used_year: Optional[int] = None
    certification: Optional[str] = None

    class Config:
        from_attributes = True


class DeveloperResponse(DeveloperBase):
    """
    Schema for formatting the outgoing response of a developer record.
    Includes database-generated fields.
    """
    id: int
    created_at: datetime
    
    # [MODIFIED] Explicitly tell Pydantic to include the skills array
    skills: List[DeveloperSkillResponse] = []

    class Config:
        """
        Pydantic configuration class.
        from_attributes = True ensures compatibility with SQLAlchemy ORM models.
        """
        from_attributes = True