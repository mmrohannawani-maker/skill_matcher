# Schema for JD matching request and response

# app/schemas/jd_schema.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

def debug_log(message: str) -> None:
    """Helper function to log debug messages for JD schemas."""
    print(f"[JD_SCHEMA DEBUG] {message}")

debug_log("JD schemas loaded successfully")

"""
What Job Description schemas represent:
These schemas define the data structures for handling Job Descriptions (JDs) 
within the system. They validate incoming data when Sales users submit new 
requirements and structure the outgoing data containing matched developers.

How JDCreate is used when Sales submits a JD:
When a Sales user pastes a JD into the system, the frontend sends a payload 
validated against `JDCreate`. This ensures we capture the required description 
and the ID of the user creating the search before any database insertion.

How JDMatchResult represents developers matched to the JD:
Once the matching engine processes the JD, it returns a list of developers 
scored against the extracted skills. `JDMatchResult` shapes this individual 
developer data, including their match score and specific overlapping skills.

Why ORM mode is required for FastAPI responses:
`orm_mode = True` allows Pydantic to read data directly from SQLAlchemy ORM 
objects rather than strictly requiring Python dictionaries. It automatically 
translates database models into the defined response schema.
"""

class JDBase(BaseModel):
    """
    Common fields shared across Job Description schemas.
    """
    jd_title: Optional[str] = None
    jd_description: str
    experience_required: Optional[int] = None
    notes: Optional[str] = None


class JDCreate(JDBase):
    """
    Schema for validating data when a Sales user creates a new JD search.
    Inherits base JD fields and requires the user ID of the creator.
    """
    created_by_user_id: int


class JDExtractedSkills(BaseModel):
    """
    Schema representing the skills extracted from a raw JD text by the backend.
    """
    jd_id: int
    extracted_skills: List[str]


class JDMatchResult(BaseModel):
    """
    Schema representing a single developer matched against a JD.
    Includes their computed match score and relevant experience.
    """
    developer_id: int
    developer_name: str
    match_score: float
    experience_years: int
    matched_skills: List[str]


class JDSearchResponse(BaseModel):
    """
    Schema for formatting the final API response of a JD search.
    Includes the parsed JD details and the list of matched developers.
    """
    jd_id: int
    jd_title: Optional[str] = None
    jd_description: str
    extracted_skills: List[str]
    experience_required: Optional[int] = None
    search_timestamp: datetime
    matched_developers: List[JDMatchResult]

    class Config:
        """Enables compatibility with SQLAlchemy ORM models."""
        from_attributes = True