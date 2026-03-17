# Logic for managing skills

# backend/app/services/skill_service.py
#
# Libraries to install:
# pip install sqlalchemy langchain langchain-huggingface huggingface_hub

import os
import json
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.skill_model import Skill
from app.models.developer_skill_model import DeveloperSkill
from app.schemas.skill_schema import SkillCreate, SkillUpdate

# LLM Imports
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.messages import HumanMessage

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

# LLM Model Initialization
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
    print("skills service lllm initialized")
except Exception as e:
    llm = None

def debug_log(message: str) -> None:
    """Reusable debug logging function for tracking skill service operations."""
    print(f"[SKILL SERVICE DEBUG] {message}")

def create_skill(db: Session, skill: SkillCreate) -> Optional[Skill]:
    """
    Creates a new skill in the database. 
    Checks if a skill with the same name already exists to prevent duplicates.
    Enhanced with AI normalization, categorization, and description generation.
    """
    debug_log("Attempting to create skill")
    
    # 1. AI Name Normalization
    original_name = skill.skill_name
    normalized_name = ai_normalize_skill_name(original_name)
    skill.skill_name = normalized_name
    
    debug_log(f"Skill name: {skill.skill_name}")
    
    try:
        # 2. AI Semantic Duplicate Detection
        debug_log("Checking for existing skills for semantic duplicate detection")
        all_existing_skills = [s.skill_name for s in db.query(Skill.skill_name).all()]
        
        if ai_detect_duplicate_skill(skill.skill_name, all_existing_skills):
            debug_log(f"AI detected '{skill.skill_name}' as a semantic duplicate. Searching for exact match.")
            # Even if AI detects duplicate, we check exact or normalized match in DB
            existing_skill = db.query(Skill).filter(Skill.skill_name == skill.skill_name).first()
            if existing_skill:
                return existing_skill

        # 3. Standard Duplicate Check
        existing_skill = db.query(Skill).filter(Skill.skill_name == skill.skill_name).first()
        if existing_skill:
            debug_log(f"Skill '{skill.skill_name}' already exists. Returning existing skill.")
            return existing_skill

        # 4. AI Category Inference
        if not skill.category:
            skill.category = ai_detect_skill_category(skill.skill_name)
            debug_log(f"AI inferred category: {skill.category}")

        # 5. AI Description Generation
        if not skill.description:
            skill.description = ai_generate_skill_description(skill.skill_name)
            debug_log("AI generated description")

        debug_log("Creating new skill")
        new_skill = Skill(
            skill_name=skill.skill_name,
            category=skill.category,
            description=skill.description
        )
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill)
        debug_log(f"Successfully created skill with ID: {new_skill.id}")
        return new_skill
    except Exception as e:
        debug_log(f"Error creating skill: {str(e)}")
        db.rollback()
        raise

def get_all_skills(db: Session) -> List[Skill]:
    """Retrieves all skills stored in the database."""
    debug_log("Fetching all skills from database")
    try:
        skills = db.query(Skill).all()
        debug_log(f"Retrieved {len(skills)} skills")
        return skills
    except Exception as e:
        debug_log(f"Error fetching all skills: {str(e)}")
        raise

def get_skill_by_id(db: Session, skill_id: int) -> Optional[Skill]:
    """Fetches a specific skill by its primary key ID."""
    debug_log(f"Fetching skill with id: {skill_id}")
    try:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            debug_log(f"Skill with id {skill_id} not found")
        return skill
    except Exception as e:
        debug_log(f"Error fetching skill ID {skill_id}: {str(e)}")
        raise

def update_skill(db: Session, skill_id: int, skill_data: SkillUpdate) -> Optional[Skill]:
    """Updates an existing skill's attributes."""
    debug_log(f"Updating skill with id: {skill_id}")
    try:
        skill = get_skill_by_id(db, skill_id)
        if not skill:
            return None

        update_data = skill_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(skill, key, value)

        db.commit()
        db.refresh(skill)
        debug_log(f"Successfully updated skill ID {skill_id}")
        return skill
    except Exception as e:
        debug_log(f"Error updating skill ID {skill_id}: {str(e)}")
        db.rollback()
        raise

def delete_skill(db: Session, skill_id: int) -> bool:
    """
    Deletes a skill from the database. 
    Also handles cascading deletion of related developer_skill mappings.
    """
    debug_log(f"Deleting skill with id: {skill_id}")
    try:
        skill = get_skill_by_id(db, skill_id)
        if not skill:
            return False

        # First, delete related entries in developer_skills junction table
        db.query(DeveloperSkill).filter(DeveloperSkill.skill_id == skill_id).delete(synchronize_session=False)
        
        # Then delete the skill itself
        db.delete(skill)
        db.commit()
        debug_log(f"Successfully deleted skill ID {skill_id} and related mappings")
        return True
    except Exception as e:
        debug_log(f"Error deleting skill ID {skill_id}: {str(e)}")
        db.rollback()
        raise

def get_developers_with_skill(db: Session, skill_id: int) -> List[DeveloperSkill]:
    """Queries the developer_skills table to find all developers linked to a specific skill."""
    debug_log(f"Fetching developers with skill id: {skill_id}")
    try:
        # Verify skill exists first
        if not get_skill_by_id(db, skill_id):
            return []

        developer_skills = db.query(DeveloperSkill).filter(DeveloperSkill.skill_id == skill_id).all()
        debug_log(f"Found {len(developer_skills)} developers linked to skill ID {skill_id}")
        return developer_skills
    except Exception as e:
        debug_log(f"Error fetching developers for skill ID {skill_id}: {str(e)}")
        raise

# -------------------------------------------------------------------
# NEW LLM HELPER FUNCTIONS
# -------------------------------------------------------------------

def ai_normalize_skill_name(skill_name: str) -> str:
    """Uses LLM to standardize messy skill names."""
    if not llm: return skill_name
    debug_log(f"LLM normalizing skill name: {skill_name}")
    try:
        prompt = f"Normalize this technology skill name to its standard official format (e.g., 'python3' -> 'Python', 'reactjs' -> 'React'). Return ONLY the normalized name. Skill: {skill_name}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM normalization failed: {str(e)}")
        return skill_name

def ai_detect_skill_category(skill_name: str) -> str:
    """Uses LLM to detect the category of a technology skill."""
    if not llm: return "Other"
    debug_log(f"LLM detecting category for: {skill_name}")
    categories = ["Programming Language", "Frontend", "Backend", "Database", "Cloud", "DevOps", "AI/ML", "Testing", "Other"]
    try:
        prompt = f"Categorize the technology '{skill_name}' into one of these: {', '.join(categories)}. Return ONLY the category name."
        response = llm.invoke([HumanMessage(content=prompt)])
        result = response.content.strip()
        return result if result in categories else "Other"
    except Exception as e:
        debug_log(f"LLM category detection failed: {str(e)}")
        return "Other"

def ai_generate_skill_description(skill_name: str) -> str:
    """Uses LLM to generate a professional description for a technology."""
    if not llm: return ""
    debug_log(f"LLM generating description for: {skill_name}")
    try:
        prompt = f"Write a professional one-sentence description for the technology skill '{skill_name}'. Example for FastAPI: 'FastAPI is a modern Python web framework used to build high-performance APIs with automatic documentation and asynchronous support.'"
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM description generation failed: {str(e)}")
        return ""

def ai_detect_duplicate_skill(skill_name: str, existing_skills: List[str]) -> bool:
    """Uses LLM to detect if a skill is a semantic duplicate of an existing one."""
    if not llm or not existing_skills: return False
    debug_log(f"LLM checking if '{skill_name}' is a semantic duplicate")
    try:
        # Check first 100 skills to keep prompt size manageable
        skills_subset = existing_skills[:100]
        prompt = f"Is the technology '{skill_name}' a semantic duplicate of any of these existing skills? (e.g., 'JS' is a duplicate of 'JavaScript'). Existing skills: {skills_subset}. Return ONLY 'True' or 'False'."
        response = llm.invoke([HumanMessage(content=prompt)])
        return "true" in response.content.lower()
    except Exception as e:
        debug_log(f"LLM duplicate detection failed: {str(e)}")
        return False