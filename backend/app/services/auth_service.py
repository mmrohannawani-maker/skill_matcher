# Handles authentication logic like password verification and JWT generation
# backend/app/services/auth_service.py

# ==========================================
# DEPENDENCY INSTALLATION:
# pip install python-jose[cryptography] passlib[bcrypt] sqlalchemy fastapi
# pip install langchain-huggingface python-dotenv
# ==========================================

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# LangChain / HuggingFace Imports
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# Import the Database Model and Pydantic Schema
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserLogin

# Load environment variables
#load_dotenv()

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Passlib configuration for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from dotenv import load_dotenv
from pathlib import Path

# Load .env file with debugging
env_path = Path(__file__).parent.parent.parent / '.env'  # Goes up 3 levels: services/ -> app/ -> backend/
print(f"[DEBUG] Looking for .env at: {env_path}")
print(f"[DEBUG] File exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"[DEBUG] Token loaded: {'✅' if huggingfacehub_api_token else '❌'}")
print(f"[DEBUG] Token value: {huggingfacehub_api_token[:10] if huggingfacehub_api_token else 'None'}...")


# -------------------------------------------------------------------
# LLM CONFIGURATION
# -------------------------------------------------------------------
# huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

try:
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-V3",
        task="text-generation",
        temperature=0,
        huggingfacehub_api_token=huggingfacehub_api_token,
        max_new_tokens=512
    )

    # Then wrap it with ChatHuggingFace
    llm = ChatHuggingFace(llm=llm_endpoint)
except Exception as e:
    print(f"[AUTH SERVICE DEBUG] LLM Initialization failed: {str(e)}")
    llm = None

# -------------------------------------------------------------------
# DEBUGGING SYSTEM
# -------------------------------------------------------------------
def debug_log(message: str) -> None:
    """Helper function to trace and debug Auth Service execution steps."""
    print(f"[AUTH SERVICE DEBUG] {message}")

debug_log("Auth Service loaded successfully")

# -------------------------------------------------------------------
# LLM SECURITY HELPER FUNCTIONS
# -------------------------------------------------------------------

def analyze_login_attempt(email: str) -> str:
    """Uses LLM to analyze if a login attempt might be suspicious."""
    if not llm:
        return "Security analysis unavailable (LLM not initialized)."
    
    debug_log(f"Calling LLM for login attempt analysis: {email}")
    prompt = f"A login attempt occurred for email: {email}. Analyze if this could be suspicious activity such as brute force or abnormal pattern. Return a short security note."
    
    try:
        response = llm.invoke(prompt)
        insight = response.content.strip()
        debug_log(f"LLM Login Insight: {insight}")
        return insight
    except Exception as e:
        debug_log(f"LLM login analysis failed: {str(e)}")
        return "Analysis failed."

def analyze_registration_risk(email: str, role: str) -> str:
    """Uses LLM to determine if the registration might look suspicious."""
    if not llm:
        return "Risk analysis unavailable."

    debug_log(f"Calling LLM for registration risk: {email} as {role}")
    prompt = f"A user registered with email {email} and role {role}. Check if anything about this registration could indicate suspicious behavior."

    try:
        response = llm.invoke(prompt)
        insight = response.content.strip()
        debug_log(f"LLM Registration Risk: {insight}")
        return insight
    except Exception as e:
        debug_log(f"LLM registration analysis failed: {str(e)}")
        return "Analysis failed."

def generate_security_log(event: str, email: str) -> str:
    """Uses the LLM to generate a readable security log summary."""
    if not llm:
        return f"Event: {event}, User: {email}"

    debug_log(f"Generating LLM security log for event: {event}")
    prompt = f"Generate a short security log message for event '{event}' involving user {email}."

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM log generation failed: {str(e)}")
        return f"Event: {event}, User: {email}"

# -------------------------------------------------------------------
# PASSWORD UTILITIES
# -------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Takes a plaintext password and returns a hashed representation."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plaintext password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

# -------------------------------------------------------------------
# JWT UTILITIES
# -------------------------------------------------------------------
def create_access_token(data: dict) -> str:
    """
    Creates a JSON Web Token containing the user's data and an expiration time.
    """
    debug_log("Starting JWT token creation")
    to_encode = data.copy()
    
    # Calculate expiration time and append to the payload
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode and sign the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    debug_log("JWT token created successfully")
    
    return encoded_jwt

# -------------------------------------------------------------------
# AUTHENTICATION BUSINESS LOGIC
# -------------------------------------------------------------------
def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Handles the business logic for registering a new user.
    Ensures email uniqueness, hashes the password, and saves the record.
    """
    debug_log("Starting user registration")
    debug_log(f"Checking if email exists: {user_data.email}")
    
    # 1. Check if the user already exists in the database
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        debug_log(f"Registration failed: Email {user_data.email} already registered")
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # 2. Hash the plaintext password
    hashed_pw = hash_password(user_data.password)
    debug_log("Password hashed successfully")
    
    # 3. Create the database model instance
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_pw,
        role=user_data.role
    )
    
    # 4. Save and persist to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 5. LLM Security Intelligence Integration
    risk_report = analyze_registration_risk(new_user.email, new_user.role)
    debug_log(f"Registration Risk Analysis Result: {risk_report}")
    
    debug_log(f"User registration successful for {user_data.email}")
    return new_user

def login_user(db: Session, login_data: UserLogin) -> dict:
    """
    Handles the business logic for user login.
    Verifies credentials and returns a generated JWT token.
    """
    debug_log(f"Attempting login for email: {login_data.email}")
    
    # 1. Fetch user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        debug_log("Login failed: User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 2. Verify the provided password against the stored hash
    if not verify_password(login_data.password, user.password_hash):
        debug_log("Login failed: Incorrect password")
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    debug_log("Password verified successfully")
    
    # 3. LLM Security Intelligence Integration
    login_insight = analyze_login_attempt(user.email)
    debug_log(f"Login Attempt Analysis Result: {login_insight}")
    
    # 4. Generate the JWT access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    debug_log("User login successful")
    
    # 5. Return token response
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str, db: Session) -> User:
    """
    Decodes the provided JWT token to extract the user ID, 
    then retrieves and returns the corresponding user from the database.
    """
    debug_log("Attempting to get current user from token")
    
    try:
        # 1. Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            debug_log("Token validation failed: No user ID found in payload")
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
    except Exception as e:
        debug_log(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
        
    # 2. Fetch the user from the DB
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        debug_log("Token valid, but user no longer exists in DB")
        raise HTTPException(status_code=401, detail="User not found")
        
    debug_log(f"Current user retrieved successfully: {user.email}")
    
    # 3. Return the user object
    return user