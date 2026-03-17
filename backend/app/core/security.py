# Handles password hashing and JWT token creation

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Import configuration values
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# -------------------------------------------------------------------
# DEBUGGING SYSTEM
# -------------------------------------------------------------------
def debug_log(message: str) -> None:
    """Helper function to trace and debug security utility operations."""
    print(f"[SECURITY DEBUG] {message}")

# -------------------------------------------------------------------
# SECURITY CONFIGURATION
# -------------------------------------------------------------------
# Passlib configuration for bcrypt password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# -------------------------------------------------------------------
# PASSWORD UTILITIES
# -------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Generates a secure bcrypt hash from a plaintext password."""
    debug_log("Hashing a new password")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    debug_log("Verifying password hash")
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if not is_valid:
        debug_log("Password verification failed")
    return is_valid

# -------------------------------------------------------------------
# JWT UTILITIES
# -------------------------------------------------------------------
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT access token.
    Adds 'exp' claim based on configuration.
    """
    debug_log("Initiating token creation")
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        debug_log("JWT token created successfully")
        return encoded_jwt
    except Exception as e:
        debug_log(f"Critical error during token encoding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate security token"
        )

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises 401 Unauthorized if the token is invalid or expired.
    """
    debug_log("Decoding access token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        debug_log("Token decoded and signature validated")
        return payload
    except JWTError as e:
        debug_log(f"Token decoding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# -------------------------------------------------------------------
# TOKEN VALIDATION HELPERS
# -------------------------------------------------------------------
def get_current_user_from_token(token: str) -> Dict[str, Any]:
    """
    Standalone helper to extract user information from a JWT payload.
    Used as a low-level validation step before database retrieval.
    """
    debug_log("Validating token and extracting user payload")
    payload = decode_access_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        debug_log("Token validation error: 'sub' claim missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    debug_log(f"Token validated for user ID: {user_id}")
    return payload