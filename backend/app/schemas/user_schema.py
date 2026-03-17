# Validation schemas for user login, creation, and responses

# app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

def debug_log(message: str) -> None:
    """
    Helper function to log debug messages for User schemas.
    """
    print(f"[USER_SCHEMA DEBUG] {message}")

debug_log("User schemas loaded successfully")

"""
What are schemas?
Pydantic schemas act as data validators and serializers in FastAPI.
They define the exact shape of data that the API expects to receive (Requests) 
and the exact shape of data the API will return (Responses).

How they protect sensitive data:
By explicitly defining separate schemas for creating a user (UserCreate) 
and returning a user (UserResponse), we tightly control what data flows in and out.
Any extra fields sent by a malicious user are automatically stripped or rejected,
and we only expose fields we explicitly define in the response models.

Why the password should not appear in the response schema:
The UserResponse schema dictates the payload sent back to the client. 
If the password (even hashed) is included in this schema, it exposes sensitive 
authentication data to the frontend, creating a critical security vulnerability.
By omitting it here, FastAPI guarantees it never leaves the server.
"""

class UserBase(BaseModel):
    """
    Shared properties for User models.
    Provides the foundational fields used across multiple schemas.
    """
    name: str
    email: EmailStr
    role: str


class UserCreate(UserBase):
    """
    Schema used when an Admin creates a new user.
    Inherits name, email, and role from UserBase, and requires a plaintext password.
    """
    password: str


class UserLogin(BaseModel):
    """
    Schema used strictly for authenticating an existing user.
    Only requires the fields necessary to verify identity.
    """
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """
    Schema used for returning user data in API responses.
    Adds database-generated fields like id and created_at.
    Intentionally excludes the password field.
    """
    id: int
    created_at: datetime

    class Config:
        """
        Pydantic config subclass.
        orm_mode = True tells Pydantic to read the data even if it is not a dict,
        but an ORM model (like our SQLAlchemy User model). It will access attributes
        using dot notation (e.g., user.id instead of user['id']).
        """
        from_attributes = True