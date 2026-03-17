# Base class for all SQLAlchemy models

# app/database/base.py

from sqlalchemy.orm import declarative_base

# The Base class serves as the central declarative registry for SQLAlchemy.
# All ORM models (e.g., User, Developer, Skill) will inherit from this Base class.
# This allows SQLAlchemy to track all models and map them to the database schema accurately.
Base = declarative_base()