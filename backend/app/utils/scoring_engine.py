# Calculates developer match score based on skills, experience, and rating

# backend/app/utils/scoring_engine.py

# ==========================================
# DEPENDENCY INSTALLATION:
# pip install langchain langchain-community huggingface_hub
# ==========================================

import os
import json
import copy
from typing import List, Dict, Any

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.messages import HumanMessage
from dotenv import load_dotenv
from pathlib import Path

# Load .env file with debugging
env_path = Path(__file__).parent.parent.parent / '.env'  # Goes up 3 levels
print(f"[DEBUG] Looking for .env at: {env_path}")
print(f"[DEBUG] File exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"[DEBUG] Token loaded: {'✅' if huggingfacehub_api_token else '❌'}")

try:
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="deepseek-ai/DeepSeek-V3",
        task="text-generation",
        temperature=0,
        huggingfacehub_api_token=huggingfacehub_api_token,
        max_new_tokens=512
    )
    llm = ChatHuggingFace(llm=llm_endpoint)
    print("scoring engine llm initialized")
except Exception as e:
    llm = None

# -------------------------------------------------------------------
# DEBUGGING SYSTEM
# -------------------------------------------------------------------
def debug_log(message: str) -> None:
    """Helper function to trace and debug scoring engine operations."""
    print(f"[SCORING ENGINE DEBUG] {message}")

# -------------------------------------------------------------------
# ALGORITHM FUNCTIONS
# -------------------------------------------------------------------
def calculate_skill_score(required_skills: List[str], developer_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rewards developers for matching skills. No negative penalties to prevent 0% results.
    """
    debug_log("Starting skill scoring calculation (Bonus Only)")
    
    score = 0
    matched_skills = []
    missing_skills = []
    
    normalized_req_skills = [skill.lower().strip() for skill in required_skills]
    dev_skill_map = {str(ds.get("skill", "")).lower().strip(): ds for ds in developer_skills}
        
    for req_skill in normalized_req_skills:
        if req_skill in dev_skill_map:
            matched_skills.append(req_skill)
            dev_skill = dev_skill_map[req_skill]
            
            # 1. Proficiency Points (1 to 5 mapping to +2 to +10)
            proficiency = int(dev_skill.get("proficiency", 1))
            score += (proficiency * 2)
            
            # 2. Experience Points
            years = int(dev_skill.get("years", 0))
            if years <= 1: score += 1
            elif years <= 3: score += 3
            elif years <= 5: score += 5
            else: score += 7
        else:
            missing_skills.append(req_skill)
            # [REMOVED] score -= 5 (No more penalty!)

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }

def calculate_match_percentage(score: int, max_score: int) -> float:
    """
    Converts a raw point score into a percentage from 0 to 100.
    """
    if max_score <= 0:
        return 0.0
        
    percentage = (score / max_score) * 100.0
    
    # Ensure the percentage remains bounded between 0 and 100
    bounded_percentage = max(0.0, min(100.0, percentage))
    
    return round(bounded_percentage, 2)


def score_developer_for_jd(required_skills: List[str], developer_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Core function to evaluate a developer's compatibility with a Job Description.
    [MODIFIED] Removed all LLM calls to prevent 402 API exhaustion and speed up the loop.
    """
    # Handle empty required skills edge case
    if not required_skills:
         return {
            "total_score": 0,
            "match_percentage": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "explanation": "No required skills provided for matching."
        }
    
    # Step 1: Calculate raw points using pure math (No API Calls)
    score_data = calculate_skill_score(required_skills, developer_skills)
    total_score = score_data["score"]
    
    # Step 2: Compute maximum possible score
    # Max score assumes: (Max Proficiency [10] + Max Experience [7]) * Number of Skills
    max_possible_score = len(required_skills) * 17
    
    # Step 3: Compute percentage
    match_percentage = calculate_match_percentage(total_score, max_possible_score)
    
    return {
        "total_score": total_score,
        "match_percentage": match_percentage,
        "matched_skills": score_data["matched_skills"],
        "missing_skills": score_data["missing_skills"],
        # Provide a simple, fast fallback explanation
        "explanation": f"Matched {len(score_data['matched_skills'])} out of {len(required_skills)} required skills."
    }

# -------------------------------------------------------------------
# LLM HELPER FUNCTIONS (Kept for Global/Standalone Use, Removed from Loop)
# -------------------------------------------------------------------

def detect_semantic_skill_matches(required_skills: List[str], developer_skills: List[str]) -> Dict[str, str]:
    if not llm or not required_skills or not developer_skills:
        return {}
    prompt = f"Match equivalent technologies...\nRequired Skills:\n{required_skills}\nDeveloper Skills:\n{developer_skills}\nReturn ONLY JSON."
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return json.loads(response.content.strip().replace("```json", "").replace("```", "").strip())
    except:
        return {}

def get_skill_importance_weights(required_skills: List[str]) -> Dict[str, int]:
    default_weights = {skill: 1 for skill in required_skills}
    if not llm or not required_skills:
        return default_weights
    prompt = f"Assign importance weight (1-3) to each skill.\nSkills:\n{required_skills}\nReturn ONLY JSON."
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        weights_map = json.loads(response.content.strip().replace("```json", "").replace("```", "").strip())
        return {skill: int(weights_map.get(skill, 1)) for skill in required_skills}
    except:
        return default_weights

def generate_match_explanation(result: Dict[str, Any]) -> str:
    if not llm:
        return "Explanation unavailable."
    prompt = f"Explain the developer match result in simple terms...\nMatched: {result.get('matched_skills', [])}\nMissing: {result.get('missing_skills', [])}\nPercentage: {result.get('match_percentage', 0)}%\nReturn ONLY text explanation."
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except:
        return "Explanation unavailable."