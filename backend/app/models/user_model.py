# Database model for users (Admin, Developer, Sales)

# app/models/user_model.py

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.base import Base

def debug_print(message: str) -> None:
    """
    Custom debug print function for tracking model loading and object instantiation.
    """
    print(f"[DEBUG - USER_MODEL] {message}")

debug_print("Loading User model schema...")

class User(Base):
    """
    User model representing the 'users' table in the database.
    Stores authentication and profile information for system users.
    """
    __tablename__ = "users"

    # Unique identifier for the user; primary key automatically increments
    id = Column(Integer, primary_key=True, index=True)

    # Full name of the user; cannot be null
    name = Column(String, nullable=False)

    # User's email address; used as a login identifier, must be unique and indexed for fast lookups
    email = Column(String, unique=True, index=True, nullable=False)

    # Securely hashed password string; never store plaintext passwords
    password_hash = Column(String, nullable=False)

    # Authorization role for the user; defaults to "admin"
    role = Column(String, default="admin", nullable=False)

    # Automatically records the timestamp when the user record is created
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        """
        Override the default __init__ to add debug logging when a new User instance is created.
        """
        super().__init__(**kwargs)
        # Using getattr to safely print email even if it wasn't provided in kwargs yet
        debug_print(f"Instantiated new User object: email='{getattr(self, 'email', 'None')}'")