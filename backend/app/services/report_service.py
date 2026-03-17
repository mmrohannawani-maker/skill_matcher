# backend/app/services/report_service.py

# ==========================================
# DEPENDENCY INSTALLATION:
# pip install sqlalchemy langchain-huggingface python-dotenv
# (collections, typing, and datetime are built-in)
# ==========================================

import os
import json
from typing import List, Dict, Any
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func
from dotenv import load_dotenv

# Models and Database
from app.models.developer_model import Developer
from app.models.skill_model import Skill
from app.models.developer_skill_model import DeveloperSkill

# LangChain / HuggingFace Imports
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# Load environment variables
# load_dotenv()

# -------------------------------------------------------------------
# DEBUGGING SYSTEM
# -------------------------------------------------------------------
def debug_log(message: str) -> None:
    """Reusable debug logging function for tracking report generation operations."""
    print(f"[REPORT SERVICE DEBUG] {message}")

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
# LLM INITIALIZATION
# -------------------------------------------------------------------
debug_log("Initializing DeepSeek-V3 via HuggingFaceEndpoint...")
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
    debug_log("report service LLM initialized successfully")
except Exception as e:
    debug_log(f"LLM Initialization Error: {str(e)}")
    llm = None

# -------------------------------------------------------------------
# EXISTING BUSINESS LOGIC (UNTOUCHED)
# -------------------------------------------------------------------

def get_skill_availability_report(db: Session) -> List[Dict[str, Any]]:
    """Counts the number of developers associated with each skill."""
    debug_log("Generating skill availability report")
    try:
        results = (
            db.query(Skill.skill_name, func.count(DeveloperSkill.developer_id).label("dev_count"))
            .join(DeveloperSkill, Skill.id == DeveloperSkill.skill_id)
            .group_by(Skill.id, Skill.skill_name)
            .all()
        )
        report = [{"skill": name, "developers": count} for name, count in results]
        return report
    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return []

def get_top_experts(db: Session, skill_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Finds developers with the highest proficiency and experience."""
    debug_log(f"Calculating top experts for {skill_name}")
    try:
        normalized_skill = skill_name.lower().strip()
        results = (
            db.query(Developer, DeveloperSkill)
            .join(DeveloperSkill, Developer.id == DeveloperSkill.developer_id)
            .join(Skill, Skill.id == DeveloperSkill.skill_id)
            .filter(Skill.skill_name == normalized_skill)
            .order_by(DeveloperSkill.proficiency_level.desc(), DeveloperSkill.years_of_experience.desc())
            .limit(limit).all()
        )
        return [{
            "developer": dev.name,
            "skill": normalized_skill,
            "proficiency": ds.proficiency_level,
            "years_experience": ds.years_of_experience
        } for dev, ds in results]
    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return []

def get_available_developers(db: Session) -> List[Dict[str, Any]]:
    """Returns developers currently marked as available."""
    debug_log("Fetching available developers")
    try:
        available_devs = db.query(Developer).filter(Developer.availability == True).all()
        return [{"name": dev.name, "role": dev.current_role or "Unassigned"} for dev in available_devs]
    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return []

def get_skill_gap_report(db: Session) -> List[Dict[str, Any]]:
    """Identifies skills with low expert availability (proficiency >= 4)."""
    debug_log("Generating skill gap report")
    try:
        all_skills = db.query(Skill).all()
        dev_skills = db.query(DeveloperSkill).all()
        expert_counts = defaultdict(int)
        for ds in dev_skills:
            if ds.proficiency_level >= 4:
                expert_counts[ds.skill_id] += 1
        report = [{"skill": s.skill_name, "experts": expert_counts[s.id]} for s in all_skills if expert_counts[s.id] < 2]
        report.sort(key=lambda x: x["experts"])
        return report
    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return []

def get_organization_skill_summary(db: Session) -> Dict[str, int]:
    """Returns high-level summary metrics."""
    debug_log("Generating organization skill summary metrics")
    try:
        return {
            "total_developers": db.query(Developer).count(),
            "total_skills": db.query(Skill).count(),
            "total_skill_mappings": db.query(DeveloperSkill).count()
        }
    except Exception as e:
        debug_log(f"Error: {str(e)}")
        return {"total_developers": 0, "total_skills": 0, "total_skill_mappings": 0}

# -------------------------------------------------------------------
# NEW LLM-POWERED INSIGHT FUNCTIONS (DEEPSEEK-V3)
# -------------------------------------------------------------------

def generate_llm_insight(prompt: str) -> str:
    """Helper function to call DeepSeek-V3 and return a summarized response."""
    if llm is None:
        return "AI analysis unavailable (LLM not initialized)"
    
    debug_log("Generating AI insights via DeepSeek-V3")
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        debug_log(f"LLM Error: {str(e)}")
        return "AI analysis unavailable"

def analyze_skill_distribution_with_llm(db: Session) -> Dict[str, Any]:
    """AI analysis of workforce balance and skill clusters."""
    raw_data = get_skill_availability_report(db)
    prompt = f"You are a workforce analytics expert. Analyze this engineering skill distribution data: {json.dumps(raw_data)}. Provide insights on workforce balance, overrepresented vs rare skills, and recommendations."
    return {"raw_data": raw_data, "ai_insight": generate_llm_insight(prompt)}

def analyze_skill_gaps_with_llm(db: Session) -> Dict[str, Any]:
    """AI reasoning on critical missing skills and hiring risks."""
    raw_data = get_skill_gap_report(db)
    prompt = f"Analyze this Skill Gap Report (skills with < 2 experts): {json.dumps(raw_data)}. Identify critical risks, hiring recommendations, and training opportunities."
    return {"raw_data": raw_data, "ai_insight": generate_llm_insight(prompt)}

def analyze_expert_distribution_with_llm(db: Session, skill_name: str) -> Dict[str, Any]:
    """AI insights on knowledge bottlenecks and succession risk."""
    raw_data = get_top_experts(db, skill_name)
    prompt = f"Analyze expert distribution for {skill_name}: {json.dumps(raw_data)}. Explain expertise concentration and possible knowledge bottlenecks or succession risks."
    return {"raw_data": raw_data, "ai_insight": generate_llm_insight(prompt)}

def generate_executive_summary(db: Session) -> Dict[str, Any]:
    """High-level summary for CTO/HR leadership."""
    summary = get_organization_skill_summary(db)
    gaps = get_skill_gap_report(db)
    availability = get_skill_availability_report(db)
    
    prompt = f"As a CTO Advisor, generate an executive summary based on these metrics: {json.dumps(summary)}, gaps: {json.dumps(gaps)}, and availability: {json.dumps(availability)}. Highlight overall health, top 3 risks, and 3 recommendations."
    return {
        "raw_data": {"summary": summary, "gaps": gaps, "availability": availability},
        "ai_insight": generate_llm_insight(prompt)
    }