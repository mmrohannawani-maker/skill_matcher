# Stores developer profile information

# app/models/developer_model.py


from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base

def debug_print(message: str) -> None:
    """
    Utility function for debug logging when the model is loaded or instantiated.
    """
    print(f"[DEBUG - DEVELOPER_MODEL] {message}")

debug_print("Loading Developer model schema...")

class Developer(Base):
    """
    Developer model representing the 'developers' table in the database.
    Stores core profile information, experience, and current project availability.
    """
    __tablename__ = "developers"

    # Unique identifier for the developer record; auto-increments
    id = Column(Integer, primary_key=True, index=True)

    # Full name of the developer; cannot be null
    name = Column(String, nullable=False)

    # Professional email address; enforced as unique and indexed for fast lookups
    email = Column(String, unique=True, index=True, nullable=False)

    # Total years of professional working experience
    years_of_experience = Column(Integer, default=0)

    # The department or organization unit the developer belongs to
    department = Column(String)

    # Current official job title or role designation (e.g., Senior Backend Engineer)
    current_role = Column(String)

    # Flag indicating if the developer is currently available for new project assignments
    availability = Column(Boolean, default=True)

    # Timestamp of when the record was initially created; defaults to current UTC time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # [REQUIRED CHANGE] Added relationship to fix the 'no property skills' error
    skills = relationship("DeveloperSkill", back_populates="developer")

    def __init__(self, **kwargs):
        """
        Extends the base initialization to provide debug tracing when a new developer
        record is created in memory.
        """
        super().__init__(**kwargs)
        # Safely attempt to log the email or name during instantiation
        identifier = getattr(self, 'email', getattr(self, 'name', 'Unknown'))
        debug_print(f"Instantiated new Developer object: {identifier}")