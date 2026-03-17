# Mapping table between developers and their skills

# app/models/developer_skill_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

def debug_log(message: str) -> None:
    """Helper function to log debug messages for DeveloperSkill operations."""
    print(f"[DEVELOPER_SKILL_MODEL DEBUG] {message}")

debug_log("DeveloperSkill model loaded successfully")

class DeveloperSkill(Base):
    """
    DeveloperSkill Table Model
    
    What this table does:
    Acts as an association table (many-to-many relationship) linking the 
    'developers' and 'skills' tables. It stores context-specific data 
    about a developer's knowledge of a particular skill.
    """
    __tablename__ = "developer_skills"

    # Unique identifier for this specific developer-skill mapping
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking to the developers table
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)

    # Foreign key linking to the skills table
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    # Developer's proficiency rating for this skill (typically 1 to 5)
    proficiency_level = Column(Integer, nullable=False)

    # Total years of hands-on experience the developer has with this skill
    years_of_experience = Column(Integer, default=0)

    # The most recent year the developer actively used this skill (e.g., 2023)
    last_used_year = Column(Integer)

    # Optional field storing any relevant certification names/links for this skill
    certification = Column(String, nullable=True)

    # Timestamp of when this skill association was added
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship linking back to the Developer model
    developer = relationship("Developer", back_populates="skills")

    # Relationship linking back to the Skill model
    skill = relationship("Skill", back_populates="developers")

    def __init__(self, **kwargs):
        """
        Override the default initialization to add debug logging.
        """
        super().__init__(**kwargs)
        dev_id = getattr(self, 'developer_id', 'Unknown')
        sk_id = getattr(self, 'skill_id', 'Unknown')
        debug_log(f"Initialized DeveloperSkill object: developer_id={dev_id}, skill_id={sk_id}")