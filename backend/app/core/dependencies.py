# Provides reusable FastAPI dependencies like database session

from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.user_model import User
from app.core.security import oauth2_scheme, decode_access_token

def debug_log(message: str) -> None:
    """Reusable debug logging function for tracking dependency operations."""
    print(f"[DEPENDENCIES DEBUG] {message}")

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session for a request.
    Ensures the session is closed safely after the request completes.
    """
    debug_log("Creating new database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        debug_log("Closing database session")
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract, decode, and validate the current user from the JWT token.
    """
    debug_log("Token received, attempting to authenticate user")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        debug_log("Decoding token")
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            debug_log("Authentication failure: 'sub' (user id) missing from token payload")
            raise credentials_exception
    except Exception as e:
        debug_log(f"Authentication failure: Token decoding error - {str(e)}")
        raise credentials_exception

    debug_log(f"Token decoded successfully. Looking up user ID: {user_id}")
    
    try:
        user_id_int = int(user_id)
    except ValueError:
        debug_log("Authentication failure: Invalid user ID format in token")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    
    if user is None:
        debug_log(f"Authentication failure: User ID {user_id} not found in database")
        raise credentials_exception
        
    debug_log(f"User {user.email} authenticated successfully")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the current authenticated user is active.
    """
    debug_log(f"Validating active status for user: {current_user.email}")
    
    if hasattr(current_user, "is_active") and not current_user.is_active:
        debug_log(f"Authentication failure: User {current_user.email} is inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
        
    debug_log(f"User {current_user.email} is active and validated")
    return current_user