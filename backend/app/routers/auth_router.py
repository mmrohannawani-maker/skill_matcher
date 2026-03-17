# Login and authentication endpoints

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Database dependencies
from app.core.dependencies import get_db

# Schemas
# Assuming UserResponse and TokenResponse are defined in user_schema
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin

# Services
from app.services import auth_service

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# ROUTER INITIALIZATION
# -------------------------------------------------------------------
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# -------------------------------------------------------------------
# DEBUG LOG HELPER FUNCTIONS
# -------------------------------------------------------------------
def log_router_start(endpoint_name: str) -> None:
    """Logs when an endpoint is entered."""
    logger.debug(f"[AUTH ROUTER] Entering {endpoint_name} endpoint")

def log_router_success(endpoint_name: str) -> None:
    """Logs when an endpoint completes successfully."""
    logger.debug(f"[AUTH ROUTER] {endpoint_name.capitalize()} successful")

def log_router_error(endpoint_name: str, error: Exception) -> None:
    """Logs when an exception occurs in an endpoint."""
    logger.error(f"[AUTH ROUTER] Error in {endpoint_name} endpoint: {error}")

# -------------------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------------

@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.
    Requires email, password, and basic profile information.
    """
    log_router_start("register")
    try:
        # Call the authentication service to handle business logic
        new_user = auth_service.register_user(db=db, user_data=user_data)
        
        log_router_success("register")
        return new_user
        
    except HTTPException as http_exc:
        # Re-raise known HTTP exceptions (e.g., 400 Email already registered)
        log_router_error("register", http_exc)
        raise http_exc
    except Exception as e:
        # Catch unexpected errors and return a 500 Internal Server Error
        log_router_error("register", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )

@router.post(
    "/login", 
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and get token"
)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user using email and password.
    Returns a JWT access token upon successful authentication.
    """
    log_router_start("login")
    try:
        # Call the authentication service to verify credentials and generate token
        token_response = auth_service.login_user(db=db, login_data=login_data)
        
        log_router_success("login")
        return token_response
        
    except HTTPException as http_exc:
        # Re-raise known HTTP exceptions (e.g., 401 Invalid credentials)
        log_router_error("login", http_exc)
        raise http_exc
    except Exception as e:
        # Catch unexpected errors and return a 500 Internal Server Error
        log_router_error("login", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login."
        )