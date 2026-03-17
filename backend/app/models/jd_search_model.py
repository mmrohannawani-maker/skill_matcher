# Stores job description searches done by sales team

# app/models/jd_search_model.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
# Import Base from the central database configuration
from app.database.base import Base

def debug_log(message: str) -> None:
    """
    Reusable debug logging function to track model loading and instance creation.
    """
    print(f"[JD_SEARCH_MODEL DEBUG] {message}")

# Log when the model file is first loaded by the application
debug_log("JD Search model loaded successfully")

class JDSearch(Base):
    """
    JDSearch Table Model
    
    What this table represents:
    This table stores the history of Job Description (JD) searches performed 
    by the Sales team. It captures the raw requirements, extracted skills, 
    and the user who initiated the search.
    
    Why JD searches are stored:
    Storing searches allows the system to re-run matching algorithms as new 
    developers are added, track the evolution of hiring requirements, and 
    provide a "Saved Searches" feature for Sales users.
    
    How it helps reporting and analytics:
    By persisting this data, the organization can generate "Skill Gap Reports" 
    by comparing requested JD skills against available developer skills, 
    identifying which technologies are most in demand.
    """
    __tablename__ = "jd_searches"

    # Unique identifier for the search record
    id = Column(Integer, primary_key=True, index=True)

    # An optional short title or internal reference for the JD
    jd_title = Column(String, nullable=True)

    # The full, raw text of the Job Description pasted by the Sales user
    jd_description = Column(String, nullable=False)

    # A comma-separated string or JSON-style list of keywords/skills 
    # identified within the JD text
    extracted_skills = Column(String, nullable=True)

    # The minimum years of experience specified in the JD
    experience_required = Column(Integer, default=0)

    # Foreign key referencing the 'users' table (the Sales person)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # The exact timestamp when the search was performed
    search_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Optional field for Sales users to add context or status notes
    notes = Column(String, nullable=True)

    # Relationship to the User model to track authorship
    user = relationship("User")

    def __init__(self, **kwargs):
        """
        Initialize the JDSearch instance and trigger a debug log for tracking.
        """
        super().__init__(**kwargs)
        title = getattr(self, 'jd_title', 'Untitled')
        debug_log(f"New JD search instance created: {title}")