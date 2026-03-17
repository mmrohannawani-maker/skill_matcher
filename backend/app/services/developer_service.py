# Logic for developer creation, update, and search

# backend/app/services/developer_service.py

# ==========================================
# DEPENDENCY INSTALLATION:
# pip install langchain langchain-huggingface huggingface_hub
# ==========================================

import os
import json
# [MODIFIED] Added joinedload to eager-load the skills relationship
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from app.models.developer_model import Developer
from app.models.skill_model import Skill
from app.models.developer_skill_model import DeveloperSkill
from app.schemas.developer_schema import DeveloperCreate, DeveloperUpdate

# LangChain / HuggingFace Imports
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.messages import HumanMessage


def debug_log(message: str) -> None:
    """Helper function to trace and debug Developer Service operations."""
    print(f"[DEVELOPER SERVICE DEBUG] {message}")

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


debug_log("Initializing DeepSeek-V3 for Developer Service...")
try:
    #huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-V3",
        task="text-generation",
        temperature=0,
        huggingfacehub_api_token=huggingfacehub_api_token,
        max_new_tokens=512
    )

    # Then wrap it with ChatHuggingFace
    llm = ChatHuggingFace(llm=llm_endpoint)
    debug_log(" developer service LLM initialized successfully")
except Exception as e:
    debug_log(f"LLM Initialization Error: {str(e)}")
    llm = None


# -------------------------------------------------------------------
# ORIGINAL CRUD OPERATIONS
# -------------------------------------------------------------------

def create_developer(db: Session, developer: DeveloperCreate) -> Developer:
    """
    Creates a new developer record in the database.
    """
    debug_log("Creating new developer")
    debug_log(f"Developer name: {developer.name}")

    try:
        new_developer = Developer(
            name=developer.name,
            email=developer.email,
            years_of_experience=developer.years_of_experience,
            department=developer.department,
            current_role=developer.current_role,
            availability=developer.availability,
        )
        db.add(new_developer)
        db.commit()
        db.refresh(new_developer)
        debug_log(f"Successfully created developer with ID: {new_developer.id}")
        return new_developer
    except Exception as e:
        debug_log(f"Failed to create developer: {str(e)}")
        db.rollback()
        raise


def get_all_developers(db: Session) -> List[Developer]:
    """
    Retrieves a list of all developer records from the database.
    """
    debug_log("Fetching all developers")
    try:
        # [MODIFIED] Added .options(joinedload(Developer.skills)) to fetch skills instantly
        developers = db.query(Developer).options(joinedload(Developer.skills)).all()
        debug_log(f"Found {len(developers)} developers")
        return developers
    except Exception as e:
        debug_log(f"Error fetching all developers: {str(e)}")
        raise


def get_developer_by_id(db: Session, developer_id: int) -> Optional[Developer]:
    """
    Retrieves a specific developer record by their ID.
    """
    debug_log(f"Fetching developer with id: {developer_id}")
    try:
        # [MODIFIED] Added .options(joinedload(Developer.skills)) here as well
        developer = db.query(Developer).options(joinedload(Developer.skills)).filter(Developer.id == developer_id).first()
        if not developer:
            debug_log(f"Developer with ID {developer_id} not found")
        return developer
    except Exception as e:
        debug_log(f"Error fetching developer ID {developer_id}: {str(e)}")
        raise


def update_developer(db: Session, developer_id: int, developer_data: DeveloperUpdate) -> Optional[Developer]:
    """
    Updates an existing developer's profile information.
    """
    debug_log(f"Updating developer: {developer_id}")
    try:
        developer = get_developer_by_id(db, developer_id)
        if not developer:
            return None

        update_data = developer_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(developer, key, value)

        db.commit()
        db.refresh(developer)
        debug_log(f"Successfully updated developer {developer_id}")
        return developer
    except Exception as e:
        debug_log(f"Error updating developer ID {developer_id}: {str(e)}")
        db.rollback()
        raise


def delete_developer(db: Session, developer_id: int) -> bool:
    """
    Removes a developer record from the database.
    """
    debug_log(f"Deleting developer: {developer_id}")
    try:
        developer = get_developer_by_id(db, developer_id)
        if not developer:
            return False

        db.delete(developer)
        db.commit()
        debug_log(f"Successfully deleted developer {developer_id}")
        return True
    except Exception as e:
        debug_log(f"Error deleting developer ID {developer_id}: {str(e)}")
        db.rollback()
        raise


def add_skill_to_developer(db: Session, developer_id: int, skill_id: int, proficiency_level: int) -> Optional[DeveloperSkill]:
    """
    Links a developer to a specific skill with a given proficiency level.
    """
    debug_log(f"Assigning skill {skill_id} to developer {developer_id}")
    try:
        # Verify developer exists
        developer = get_developer_by_id(db, developer_id)
        if not developer:
            debug_log(f"Developer ID {developer_id} not found. Cannot add skill.")
            return None

        # Verify skill exists
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            debug_log(f"Skill ID {skill_id} not found. Cannot add skill.")
            return None

        # Check for existing assignment to avoid duplicates
        existing_assignment = db.query(DeveloperSkill).filter(
            DeveloperSkill.developer_id == developer_id,
            DeveloperSkill.skill_id == skill_id
        ).first()

        if existing_assignment:
            debug_log(f"Skill {skill_id} is already assigned to developer {developer_id}")
            # Optionally update proficiency here instead of raising an error
            existing_assignment.proficiency_level = proficiency_level
            db.commit()
            db.refresh(existing_assignment)
            return existing_assignment

        new_developer_skill = DeveloperSkill(
            developer_id=developer_id,
            skill_id=skill_id,
            proficiency_level=proficiency_level
        )
        db.add(new_developer_skill)
        db.commit()
        db.refresh(new_developer_skill)
        debug_log(f"Successfully assigned skill {skill_id} to developer {developer_id}")
        return new_developer_skill
    except Exception as e:
        debug_log(f"Error assigning skill {skill_id} to developer {developer_id}: {str(e)}")
        db.rollback()
        raise


def get_developer_skills(db: Session, developer_id: int) -> List[DeveloperSkill]:
    """
    Retrieves all skills assigned to a specific developer.
    """
    debug_log(f"Fetching skills for developer {developer_id}")
    try:
        skills = db.query(DeveloperSkill).filter(DeveloperSkill.developer_id == developer_id).all()
        debug_log(f"Found {len(skills)} skills for developer {developer_id}")
        return skills
    except Exception as e:
        debug_log(f"Error fetching skills for developer {developer_id}: {str(e)}")
        raise


# -------------------------------------------------------------------
# NEW LLM HELPER FUNCTIONS
# -------------------------------------------------------------------

def _safe_llm_call(prompt: str, fallback: str) -> str:
    """Internal helper to execute LLM calls safely."""
    if llm is None:
        debug_log("LLM is not initialized. Using fallback.")
        return fallback
        
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM execution failed: {str(e)}")
        return fallback


def generate_developer_summary(developer: Developer, skills: List[str]) -> str:
    """
    Uses the LLM to generate a human-readable professional summary for a developer.
    """
    debug_log(f"Calling LLM for developer summary for ID: {developer.id}")
    
    fallback = f"{developer.name} is a {developer.current_role} with {developer.years_of_experience} years of experience."
    
    prompt = f"""
    Write a concise, professional 1-sentence summary for this software developer.
    Do not use introductory phrases like "Here is a summary:".

    Name: {developer.name}
    Role: {developer.current_role}
    Years of Experience: {developer.years_of_experience}
    Department: {developer.department}
    Skills: {', '.join(skills) if skills else 'None listed'}
    """
    
    result = _safe_llm_call(prompt, fallback)
    debug_log("LLM developer summary generated successfully.")
    return result


def suggest_additional_skills(developer: Developer, current_skills: List[str]) -> List[str]:
    """
    Uses the LLM to suggest related technologies the developer might know or should learn.
    """
    debug_log(f"Calling LLM to suggest additional skills for ID: {developer.id}")
    
    fallback = []
    
    prompt = f"""
    Based on the following developer profile, suggest 3 to 5 highly relevant technical skills or tools they should learn next or might already know.
    Return ONLY a JSON list of strings. Do not include markdown formatting or explanations.

    Role: {developer.current_role}
    Current Skills: {', '.join(current_skills) if current_skills else 'None'}
    """
    
    response = _safe_llm_call(prompt, "[]")
    
    try:
        # Attempt to parse the expected JSON list
        clean_response = response.replace("```json", "").replace("```", "").strip()
        suggestions = json.loads(clean_response)
        if isinstance(suggestions, list):
            debug_log(f"LLM generated {len(suggestions)} skill suggestions.")
            return [str(s) for s in suggestions]
    except json.JSONDecodeError:
        debug_log("Failed to parse LLM skill suggestions as JSON.")
        
    return fallback


def interpret_developer_search_query(query: str) -> Dict[str, Any]:
    """
    Uses the LLM to parse a natural language search query into structured filters.
    """
    debug_log(f"Calling LLM to interpret search query: '{query}'")
    
    fallback = {"role": None, "experience": None, "skills": []}
    
    prompt = f"""
    Extract search parameters from the following natural language query to find software developers.
    Return ONLY a JSON object with these exact keys: "role" (string or null), "experience" (string or null), and "skills" (list of strings).
    Do not include markdown or explanations.

    Query: "{query}"
    """
    
    response = _safe_llm_call(prompt, json.dumps(fallback))
    
    try:
        clean_response = response.replace("```json", "").replace("```", "").strip()
        parsed_query = json.loads(clean_response)
        if isinstance(parsed_query, dict):
            debug_log("LLM successfully interpreted the search query.")
            return parsed_query
    except json.JSONDecodeError:
        debug_log("Failed to parse LLM search interpretation as JSON.")
        
    return fallback


def analyze_developer_skill_gap(developer: Developer, skills: List[str]) -> str:
    """
    Uses the LLM to provide insights into potential knowledge gaps in a developer's profile.
    """
    debug_log(f"Calling LLM for skill gap analysis for ID: {developer.id}")
    
    fallback = "Insufficient data to perform a comprehensive skill gap analysis."
    
    if not skills:
        return "This developer has no recorded skills to analyze."
        
    prompt = f"""
    Analyze the skill profile of this developer and identify one major technical gap or area of improvement based on typical industry standards for their role.
    Be concise (1-2 sentences). Do not be overly critical.

    Role: {developer.current_role}
    Experience: {developer.years_of_experience} years
    Current Skills: {', '.join(skills)}
    """
    
    result = _safe_llm_call(prompt, fallback)
    debug_log("LLM skill gap analysis generated successfully.")
    return result