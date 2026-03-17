# Reads Excel files and inserts developer skill data into database
# backend/app/services/excel_service.py
# ==========================================
# DEPENDENCY INSTALLATION:
# pip install pandas openpyxl sqlalchemy
# pip install langchain
# pip install langchain-huggingface
# pip install huggingface_hub
# ==========================================
import pandas as pd
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.developer_model import Developer
from app.models.skill_model import Skill
from app.models.developer_skill_model import DeveloperSkill
from app.database.connection import SessionLocal

# LLM Imports
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.messages import HumanMessage

from dotenv import load_dotenv
from pathlib import Path

# Load .env file with debugging
env_path = Path(__file__).parent.parent.parent / '.env'
print(f"[DEBUG] Looking for .env at: {env_path}")
print(f"[DEBUG] File exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"[DEBUG] Token loaded: {'✅' if huggingfacehub_api_token else '❌'}")
print(f"[DEBUG] Token value: {huggingfacehub_api_token[:10] if huggingfacehub_api_token else 'None'}...")

# LLM Model Configuration
try:
    huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    print(f"[DEBUG] Attempting to initialize LLM with token: {huggingfacehub_api_token[:10]}...")

    llm_endpoint = HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-V3",
        task="text-generation",
        temperature=0,
        huggingfacehub_api_token=huggingfacehub_api_token,
        max_new_tokens=512
    )

    llm = ChatHuggingFace(llm=llm_endpoint)
    print("[DEBUG] excel service LLM initialized successfully!")
except Exception as e:
    llm = None
    print(f"[DEBUG] LLM initialization FAILED: {type(e).__name__}: {str(e)}")

def debug_log(message: str) -> None:
    """Reusable debug logging function for tracking Excel ingestion operations."""
    print(f"[EXCEL SERVICE DEBUG] {message}")

def load_excel_file(file_path: str) -> pd.DataFrame:
    debug_log(f"Attempting to load Excel file: {file_path}")
    try:
        df = pd.read_excel(file_path)
        debug_log("Excel file loaded successfully")
        return df
    except Exception as e:
        debug_log(f"Failed to load Excel file. Error: {str(e)}")
        raise

def identify_skill_columns(df: pd.DataFrame) -> List[str]:
    debug_log("Identifying skill columns")
    metadata_columns = {
        'timestamp', 'name', 'full name', 'email', 'email address', 
        'mobile number', 'department', 'role', 'availability', 'years_of_experience',
        'let us know if you know other technologies not mentioned in the form'
    }
    all_columns = df.columns.tolist()

    skill_columns = []
    for col in all_columns:
        if str(col).lower().strip() not in metadata_columns:
            skill_columns.append(col)
            
    debug_log(f"Detected skill columns: {', '.join([str(c) for c in skill_columns])}")
    return skill_columns

def create_or_get_skill(db: Session, skill_name: str) -> Skill:
    normalized_name = ai_normalize_skill_name(skill_name).lower().strip()
    skill = db.query(Skill).filter(Skill.skill_name == normalized_name).first()

    if not skill:
        skill = Skill(skill_name=normalized_name)
        db.add(skill)
        db.flush()
        debug_log(f"Skill created: {normalized_name}")
        
    return skill

def create_or_get_developer(db: Session, name: str, email: str, department: str = "", role: str = "", availability: bool = True) -> Developer:
    normalized_email = str(email).lower().strip()
    developer = db.query(Developer).filter(Developer.email == normalized_email).first()

    if not developer:
        developer = Developer(
            name=str(name).strip(),
            email=normalized_email,
            department=str(department).strip() if department else None,
            current_role=str(role).strip() if role else None,
            availability=availability
        )
        db.add(developer)
        db.flush()
        debug_log(f"Developer created: {developer.name}")
        
    return developer

def process_excel_data(file_path: str, db: Session) -> Dict[str, Any]:
    debug_log(f"Starting to process Excel data from {file_path}")
    stats = {"rows_processed": 0, "developers_created": 0, "skills_mapped": 0}

    try:
        df = load_excel_file(file_path)
    except Exception:
        return stats

    original_columns = df.columns.tolist()
    skill_columns = identify_skill_columns(df)
    col_map = {str(col).lower().strip(): col for col in original_columns}

    ACCEPTED_NAME_HEADERS = {'name', 'full name', 'developer name', 'name (responses)'}
    ACCEPTED_EMAIL_HEADERS = {'email', 'email address', 'email_address', 'email address (responses)'}

    name_col = next((col_map[h] for h in ACCEPTED_NAME_HEADERS if h in col_map), None)
    email_col = next((col_map[h] for h in ACCEPTED_EMAIL_HEADERS if h in col_map), None)
    
    dept_col = col_map.get('department')
    role_col = col_map.get('role')
    avail_col = col_map.get('availability')

    if not name_col or not email_col:
        debug_log("Critical Error: Excel sheet is missing required 'Name' or 'Email' columns.")
        return stats

    # --- [MODIFIED] Helper Function to parse mixed numeric/text proficiencies ---
    def parse_proficiency(val: Any) -> int:
        if pd.isna(val): return 0
        
        # Text-to-Number Mapping
        text_map = {
            "beginner": 1, "basic": 1, "novice": 1,
            "intermediate": 3, "average": 3, "competent": 3,
            "advanced": 4, "proficient": 4,
            "expert": 5, "master": 5
        }
        
        val_str = str(val).strip().lower()
        if val_str in text_map:
            return text_map[val_str]
            
        try:
            # Handle standard numbers or strings containing numbers
            return int(float(val))
        except (ValueError, TypeError):
            return 0 # Default to 0 if it's unreadable text

    try:
        existing_names = [d.name for d in db.query(Developer.name).all()]

        for index, row in df.iterrows():
            debug_log(f"Processing row {index + 1}")
            
            row_insight = ai_analyze_row_quality(row.to_dict())
            debug_log(f"AI Quality Insight (Row {index+1}): {row_insight}")

            raw_name = row[name_col]
            raw_email = row[email_col]
            
            if pd.isna(raw_name) or pd.isna(raw_email):
                debug_log(f"Row {index + 1} skipped due to missing name or email")
                continue

            if ai_detect_duplicate_developer(str(raw_name), str(raw_email), existing_names):
                debug_log(f"Possible duplicate detected for {raw_name}. Proceeding with standard logic.")

            department_val = row[dept_col] if dept_col and pd.notna(row[dept_col]) else ""
            role_val = row[role_col] if role_col and pd.notna(row[role_col]) else ""
            
            # [MODIFIED] Use the new safe parser for role inference
            current_row_skills = []
            for s_col in skill_columns:
                prof = parse_proficiency(row[s_col])
                if prof > 0:
                    current_row_skills.append(s_col)

            if not role_val and current_row_skills:
                role_val = ai_infer_developer_role(current_row_skills)
                debug_log(f"AI inferred role: {role_val}")

            availability_val = True
            if avail_col and pd.notna(row[avail_col]):
                val = str(row[avail_col]).lower().strip()
                availability_val = val in ['true', 'yes', '1', 'y']

            existing_dev = db.query(Developer).filter(Developer.email == str(raw_email).lower().strip()).first()
            
            developer = create_or_get_developer(
                db=db,
                name=raw_name,
                email=raw_email,
                department=department_val,
                role=role_val,
                availability=availability_val
            )

            if not existing_dev:
                stats["developers_created"] += 1
            
            stats["rows_processed"] += 1

            # [MODIFIED] Use the new safe parser for database insertion
            for skill_col in skill_columns:
                proficiency = parse_proficiency(row[skill_col])
                
                if proficiency > 0:
                    skill = create_or_get_skill(db, skill_col)
                    
                    existing_mapping = db.query(DeveloperSkill).filter(
                        DeveloperSkill.developer_id == developer.id,
                        DeveloperSkill.skill_id == skill.id
                    ).first()
                    
                    if not existing_mapping:
                        estimated_years = max(1, proficiency - 1)
                        
                        dev_skill = DeveloperSkill(
                            developer_id=developer.id,
                            skill_id=skill.id,
                            proficiency_level=proficiency,
                            years_of_experience=estimated_years
                        )
                        db.add(dev_skill)
                        #debug_log(f"Skill mapped successfully: {skill.skill_name} to {developer.name}")
                        stats["skills_mapped"] += 1 
                    else:
                        if existing_mapping.proficiency_level != proficiency:
                            existing_mapping.proficiency_level = proficiency
                            debug_log(f"Updated proficiency for {skill.skill_name} mapped to {developer.name}")

        db.commit()
        debug_log("Database transaction committed safely")
        return stats
        
    except Exception as e:
        db.rollback()
        debug_log(f"Error during database operations. Transaction rolled back. Exception: {str(e)}")
        return stats

# -------------------------------------------------------------------
# NEW LLM HELPER FUNCTIONS
# -------------------------------------------------------------------

def ai_normalize_skill_name(skill_name: str) -> str:
    if not llm: return skill_name
    #debug_log(f"LLM normalizing skill name: {skill_name}")
    try:
        prompt = f"Normalize this technology skill name into a standardized version (e.g., 'reactjs' -> 'React'). Return ONLY the name. Skill: {skill_name}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
       # debug_log(f"LLM normalization failed: {str(e)}")
        return skill_name

def ai_extract_skills_from_text(text: str) -> List[str]:
    if not llm: return []
    debug_log("LLM extracting skills from text")
    try:
        prompt = f"Extract a JSON list of technology skills from this text. Return ONLY the JSON list. Text: {text}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return json.loads(response.content.strip())
    except Exception as e:
        debug_log(f"LLM skill extraction failed: {str(e)}")
        return []

def ai_infer_developer_role(skills: List[str]) -> str:
    if not llm: return ""
    debug_log("LLM inferring developer role")
    try:
        prompt = f"Based on these skills: {', '.join(skills)}, what is the most likely professional job title/role? Return ONLY the title."
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM role inference failed: {str(e)}")
        return ""

def ai_analyze_row_quality(row_data: dict) -> str:
    if not llm: return "Analysis unavailable"
    try:
        prompt = f"Analyze this developer row data for quality/completeness. Return a 1-sentence insight. Data: {row_data}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM quality analysis failed: {str(e)}")
        return "Row processed"

def ai_detect_duplicate_developer(name: str, email: str, existing_names: List[str]) -> bool:
    if not llm or not existing_names: return False
    try:
        prompt = f"Is the name '{name}' likely a duplicate of any name in this list? {existing_names[:50]}. Return ONLY 'True' or 'False'."
        response = llm.invoke([HumanMessage(content=prompt)])
        return "true" in response.content.lower()
    except Exception as e:
        debug_log(f"LLM duplicate detection failed: {str(e)}")
        return False