# backend/app/services/jd_service.py

from datetime import datetime
from typing import List, Dict, Any

# ==========================================
# IMPORTING YOUR POWERFUL UTILS ENGINE
# ==========================================
# We rename 'analyze_job_description' from jd_matcher to 'extract_jd_details' 
# here so it doesn't conflict with the service function's name below.
from app.utils.jd_matcher import analyze_job_description as extract_jd_details
from app.utils.scoring_engine import score_developer_for_jd

def debug_log(message: str) -> None:
    """Helper function to trace and debug JD Service execution steps."""
    print(f"[JD SERVICE DEBUG] {message}")

def analyze_job_description(db, jd_request) -> Dict[str, Any]:
    """
    Coordinates the database, text extraction, and the scoring engine.
    """
    debug_log("Executing analyze_job_description using UTILS engine...")
    
    jd_text = jd_request.jd_description
    
    # 1. Use your jd_matcher.py to deeply analyze the JD
    # It returns a dict: {"skills": [...], "experience_required": ...}
    jd_analysis = extract_jd_details(jd_text)
    extracted_skills = jd_analysis.get("skills", [])
    experience_required = jd_analysis.get("experience_required", 0)
    
    if not extracted_skills:
        debug_log("No skills extracted. Returning empty match.")
        return {
            "jd_id": 999,
            "jd_title": jd_request.jd_title or "AI Job Match",
            "jd_description": jd_text,
            "extracted_skills": [],
            "experience_required": experience_required or jd_request.experience_required or 0,
            "search_timestamp": datetime.now(),
            "matched_developers": []
        }

    # 2. Get all developers from the database
    try:
        from app.models.developer_model import Developer 
        developers = db.query(Developer).all()
        debug_log(f"Found {len(developers)} developers in database.")
    except Exception as e:
        debug_log(f"Database error querying developers: {e}")
        developers = []

    # 3. Match using your robust scoring_engine.py
    raw_matches = []
    
    for dev in developers:
        # Format the developer's skills into the exact dictionary shape scoring_engine.py expects
        dev_skill_dicts = []
        for ds in getattr(dev, 'skills', []):
            if hasattr(ds, 'skill'):
                dev_skill_dicts.append({
                    "skill": ds.skill.skill_name.lower().strip(),
                    "proficiency": ds.proficiency_level or 1,
                    "years": 0  # Default to 0 if experience_years isn't directly on the skill mapping
                })
        
        if not dev_skill_dicts:
            continue
            
        # Call the strict math function from scoring_engine.py
        # Returns: {"total_score": int, "match_percentage": float, "matched_skills": list, ...}
        score_data = score_developer_for_jd(extracted_skills, dev_skill_dicts)
        
        match_percentage = score_data.get("match_percentage", 0.0)
        
        # Only keep candidates who actually matched something (e.g., > 0%)
        if match_percentage > 0:
            raw_matches.append({
                "developer_id": dev.id,
                "name": dev.name,
                "score": match_percentage / 100.0, # Convert back to decimal for frontend (0.85 = 85%)
                "matched_skills": score_data.get("matched_skills", [])
            })

    # 4. Sort strictly by score, then by ID to prevent shuffling ties
    # Using a tuple: sort by score descending (-), then ID ascending
    sorted_matches = sorted(raw_matches, key=lambda x: (-x["score"], x["developer_id"]))

    # 5. Return the payload perfectly formatted for your FastAPI response schema
    return {
        "jd_id": 999, 
        "jd_title": jd_request.jd_title or "AI Job Match",
        "jd_description": jd_text,
        "extracted_skills": extracted_skills,
        "experience_required": experience_required or jd_request.experience_required or 0,
        "search_timestamp": datetime.now(),
        "matched_developers": [
            {
                "developer_id": m["developer_id"],
                "developer_name": m["name"],
                "match_score": m["score"],
                "experience_years": 0, # Note: Frontend calculates real yrs
                "matched_skills": m["matched_skills"]
            } for m in sorted_matches
        ]
    }