# Creates database engine and session for sqlite connection

# app/database/connection.py

# ==========================================
# Install dependencies before running:
# pip install fastapi sqlalchemy
# ==========================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base

def debug_print(message: str) -> None:
    """
    Custom debug print function for tracking database connection and session operations.
    """
    print(f"[DEBUG - DATABASE] {message}")

# 1. Define the SQLite database URL
# Using a local file named skill_matcher.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./skill_matcher.db"

debug_print(f"Configuring database URL: {SQLALCHEMY_DATABASE_URL}")

# 2. Create the SQLAlchemy Engine
# The engine is the starting point for any SQLAlchemy application.
# It manages the database connections and connection pool.
# connect_args={"check_same_thread": False} is required for SQLite in FastAPI
# because FastAPI can use multiple threads to handle requests, but SQLite 
# by default only allows one thread to communicate with it.
debug_print("Creating SQLAlchemy engine...")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 3. Create a SessionLocal class
# Each instance of this class will be a database session.
# autocommit=False and autoflush=False are standard safe defaults for SQLAlchemy.
debug_print("Configuring SessionLocal factory...")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create all tables
# This binds the declarative Base metadata to the engine and creates the tables
# in the skill_matcher.db file if they do not already exist.
debug_print("Creating tables in the database (if they do not exist)...")
Base.metadata.create_all(bind=engine)

# 5. Dependency generator
# This function creates a new database session for each request and closes it 
# once the request is finished. It is injected into FastAPI route endpoints.
def get_db():
    """
    FastAPI dependency that provides a database session.
    Ensures the connection is safely closed after the request cycle completes.
    """
    debug_print("Opening new database session for incoming request...")
    db = SessionLocal()
    try:
        yield db
    finally:
        debug_print("Closing database session after request completion.")
        db.close()