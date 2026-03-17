# Stores technology skills like React, Python, AWS

# app/models/skill_model.py

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.base import Base
from sqlalchemy.orm import relationship


def debug_log(message: str) -> None:
    """Helper function to log debug messages for Skill model operations."""
    print(f"[SKILL_MODEL DEBUG] {message}")

debug_log("Skill model loaded successfully")

class Skill(Base):
    """
    Skill Table Model
    
    What this table represents:
    This table serves as a centralized master dictionary of all technology skills,
    tools, frameworks, and platforms recognized within the organization 
    (e.g., Python, React, AWS, Docker).
    
    Why the skill table exists:
    It ensures data consistency and standardization across the platform. 
    By having a central repository managed by admin users, it prevents duplicate 
    or misspelled skill entries (e.g., preventing both 'NodeJS' and 'Node.js' 
    from being entered separately).
    
    How it connects to developer skills:
    This table does not store user-specific proficiency. Instead, it acts as a 
    reference entity. The 'developer_skills' junction table will link a Developer's ID 
    to a Skill's ID from this table to define their specific proficiency level 
    and years of experience with this technology.
    """
    __tablename__ = "skills"

    # Unique identifier for the skill; auto-increments
    id = Column(Integer, primary_key=True, index=True)

    # Standardized name of the technology/skill; must be unique and is indexed for quick searches
    skill_name = Column(String, unique=True, index=True, nullable=False)

    # Optional grouping category for the skill (e.g., 'Frontend', 'Backend', 'DevOps')
    category = Column(String, nullable=True)

    # Optional detailed explanation of what this skill encompasses
    description = Column(String, nullable=True)

    # Timestamp indicating when this skill was officially added to the system dictionary
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # [REQUIRED CHANGE] Added relationship to fix the 'no property developers' error
    # This allows skill.developers to return a list of DeveloperSkill objects
    developers = relationship("DeveloperSkill", back_populates="skill")

    def __init__(self, **kwargs):
        """
        Override default initialization to include debug logging.
        Tracks when a new Skill object is instantiated in memory.
        """
        super().__init__(**kwargs)
        name = getattr(self, 'skill_name', 'Unknown')
        debug_log(f"Skill instance created: skill_name='{name}'")