# Extracts keywords from job description text

# backend/app/utils/jd_matcher.py

# ==========================================
# DEPENDENCY INSTALLATION:
# pip install spacy
# python -m spacy download en_core_web_sm
# pip install langchain langchain-community huggingface_hub
# ==========================================

import re
import os
import string
from collections import Counter
from typing import List, Dict, Any

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


# 

# Optional spaCy support
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# -------------------------------------------------------------------
# LLM CONFIGURATION
# -------------------------------------------------------------------
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from langchain.messages import HumanMessage

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
    print("jd matcher llm initialized")
except Exception as e:
    llm = None

# -------------------------------------------------------------------
# DEBUGGING SYSTEM
# -------------------------------------------------------------------
def debug_log(message: str) -> None:
    """Helper function to trace and debug JD Matching operations."""
    print(f"[JD MATCHER DEBUG] {message}")

# -------------------------------------------------------------------
# MASTER SKILL DICTIONARY
# -------------------------------------------------------------------
# A flat set of normalized skill names mapped from the categories
MASTER_SKILL_SET = {
    # .NET & Microsoft Ecosystem
    ".net aspire", ".net core", ".net framework", "asp.net mvc", "c#", "blazor", 
    "ado.net", "entity framework", "linq", "dapper", "wpf", "winforms", "iis",
    "bicep", "powershell", "power bi", "power apps", "power automate", "sharepoint",

    # Programming Languages
    "python", "java", "javascript", "typescript", "go", "c++", "c", "ruby", "php", "kotlin", "swift",
    
    # Frontend & UI
    "react", "angular", "vue.js", "next.js", "html", "css", "bootstrap", "sass", 
    "material ui", "jquery", "kendo ui", "devexpress", "figma", "adobe illustrator", "canva",
    
    # Backend & Frameworks
    "fastapi", "django", "flask", "node.js", "nest.js", "spring", "ruby on rails", 
    "grpc", "graphql", "microservices", "cqrs", "onion architecture", "event-driven architecture",
    
    # Databases
    "postgresql", "mysql", "mongodb", "sqlite", "redis", "cosmosdb", "dynamodb",
    "sql server", "mariadb", "elasticsearch", "firebase",
    
    # Cloud & DevOps (AWS / Azure / GCP)
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "jenkins", "ansible",
    "azure devops", "azure functions", "aws lambda", "ec2", "s3", "rds", "cloudwatch",
    "ci/cd", "github actions", "gitlab", "bitbucket",
    
    # AI & Machine Learning
    "machine learning", "artificial intelligence", "deep learning", "pandas", "numpy", 
    "tensorflow", "pytorch", "chatgpt", "deepseek", "gemini", "grok", "perplexity", 
    "hugging face", "github copilot", "cursor", "ai agents",
    
    # Messaging & Integration
    "kafka", "rabbitmq", "sqs", "zapier", "n8n", "api gateway", 
    
    # Security & Auth
    "oauth", "jwt", "okta", "azure ad", "rbac", "authorize.net", "stripe", "paypal", "razorpay",
    
    # Testing & Mobile
    "selenium", "playwright", "jmeter", "xunit", "flutter", "ionic", "cordova", "android", "ios",
    
    # CMS & Tools
    "sitecore", "umbraco", "servicenow", "jira", "trello", "clickup", "git", "postman", "swagger"
}

# -------------------------------------------------------------------
# JD MATCHER FUNCTIONS
# -------------------------------------------------------------------

def clean_text(text: str) -> str:
    print(f"\n[jd_matcher.py] [clean_text] INPUT: text of length {len(text) if text else 0}")
    """
    Cleans the raw job description text by converting to lowercase, 
    removing punctuation (except specific cases like '.', '+', '#'), 
    and normalizing whitespace.
    """
    if not text:
        print("[jd_matcher.py] [clean_text] OUTPUT: empty string")
        return ""
        
    text = text.lower()
    
    # We want to keep periods for "node.js" and pluses for "c++"
    allowed_punct = ".+#"
    translator = str.maketrans('', '', ''.join(set(string.punctuation) - set(allowed_punct)))
    cleaned = text.translate(translator)
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    print(f"[jd_matcher.py] [clean_text] OUTPUT: cleaned text of length {len(cleaned)}")
    return cleaned

def tokenize_text(text: str) -> List[str]:
    print(f"\n[jd_matcher.py] [tokenize_text] INPUT: text of length {len(text) if text else 0}")
    """
    Splits the cleaned JD text into tokens. Uses spaCy if available for 
    smarter tokenization, otherwise falls back to simple whitespace splitting.
    """
    if not text:
        print("[jd_matcher.py] [tokenize_text] OUTPUT: []")
        return []

    debug_log("Tokenizing job description")
    
    if SPACY_AVAILABLE:
        doc = nlp(text)
        # Filter out stop words and basic punctuation for cleaner token stream
        tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
        print(f"[jd_matcher.py] [tokenize_text] OUTPUT (SpaCy): {len(tokens)} tokens")
        
        return tokens
        
    else:
        tokens = text.split()
        print(f"[jd_matcher.py] [tokenize_text] OUTPUT (Split): {len(tokens)} tokens")
        return tokens

def extract_skills(job_description: str) -> List[str]:
    print(f"\n[jd_matcher.py] [extract_skills] INPUT: JD length {len(job_description) if job_description else 0}")
    """
    Analyzes the job description and extracts known technical skills based
    on the master dictionary. Handles both single and multi-word skills.
    """
    debug_log("Starting skill extraction")
    
    if not job_description:
        print("[jd_matcher.py] [extract_skills] OUTPUT: []")
        return []

    cleaned_text = clean_text(job_description)
    tokens = tokenize_text(cleaned_text)
    
    extracted_skills = set()
    
    # 1. Single-word token matching
    for token in tokens:
        if token in MASTER_SKILL_SET:
            debug_log(f"Skill detected: {token}")
            extracted_skills.add(token)

    # 2. Multi-word skill matching (e.g., "machine learning")
    multi_word_skills = {skill for skill in MASTER_SKILL_SET if " " in skill}
    for mw_skill in multi_word_skills:
        # Simple string inclusion check in the cleaned text
        if mw_skill in cleaned_text:
            debug_log(f"Multi-word skill detected: {mw_skill}")
            extracted_skills.add(mw_skill)

    skill_list = list(extracted_skills)
    debug_log(f"Total extracted skills: {len(skill_list)}")
    print(f"[jd_matcher.py] [extract_skills] OUTPUT: {skill_list}")
    return skill_list

def extract_experience(job_description: str) -> int:
    print(f"\n[jd_matcher.py] [extract_experience] INPUT: JD length {len(job_description) if job_description else 0}")
    """
    Uses regex patterns to detect the required years of experience.
    Returns the integer value, or 0 if none is found.
    """
    if not job_description:
        print("[jd_matcher.py] [extract_experience] OUTPUT: 0")
        return 0
        
    # Look for patterns like "3 years", "5+ years", "minimum 4 years"
    pattern = r'(?i)(?:minimum\s+)?(\d+)(?:\+|(?:\s+to\s+\d+))?\s*(?:-\s*\d+\s*)?years?'
    
    matches = re.findall(pattern, job_description)
    
    if matches:
        try:
            # If multiple are found, usually the max is the safest bet or the first one depending on context.
            # We will take the maximum number found in the context of "years".
            years = max([int(m) for m in matches])
            debug_log(f"Detected experience requirement: {years} years")
            print(f"[jd_matcher.py] [extract_experience] OUTPUT: {years}")
            return years
        except ValueError:
            pass
            
    debug_log("No experience requirement detected. Defaulting to 0.")
    print("[jd_matcher.py] [extract_experience] OUTPUT: 0")
    return 0

# -------------------------------------------------------------------
# LLM ENHANCEMENT FUNCTIONS
# -------------------------------------------------------------------

def extract_skills_with_llm(job_description: str) -> List[str]:
    print(f"\n[jd_matcher.py] [extract_skills_with_llm] INPUT: JD length {len(job_description) if job_description else 0}")
    if not llm: 
        print("[jd_matcher.py] [extract_skills_with_llm] OUTPUT: [] (LLM is None)")
        return []
    
    # [STRICT PROMPT]
    prompt = f"""Extract technical skills from the JD below. 
    Return ONLY the skill names separated by commas. 
    Do NOT include introductory text, explanations, or formatting like bullet points.
    
    JD: {job_description}"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = response.content.strip()
        print(f"[jd_matcher.py] [extract_skills_with_llm] RAW LLM RESPONSE: '{result}'")
        
        # [CLEANING STEP] Split by comma and strip any remaining whitespace/newlines
        skills = [s.strip().lower() for s in result.split(",") if s.strip() and len(s.strip()) < 30]
        print(f"[jd_matcher.py] [extract_skills_with_llm] OUTPUT: {skills}")
        return skills
    except Exception as e:
        print(f"[jd_matcher.py] [extract_skills_with_llm] ERROR: {str(e)}")
        print("[jd_matcher.py] [extract_skills_with_llm] OUTPUT: [] (Failed)")
        return []

def normalize_skills_with_llm(skills: List[str]) -> List[str]:
    print(f"\n[jd_matcher.py] [normalize_skills_with_llm] INPUT: {skills}")
    if not llm or not skills: 
        print(f"[jd_matcher.py] [normalize_skills_with_llm] OUTPUT: {skills} (LLM None or empty list)")
        return skills
    
    skills_str = ", ".join(skills)
    # [STRICT PROMPT]
    prompt = f"""Clean and normalize this list of technologies: {skills_str}
    Return ONLY a clean comma-separated list. 
    Do NOT include chat, notes, or bold text (**). 
    If you don't know a skill, just return it as is."""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = response.content.strip()
        print(f"[jd_matcher.py] [normalize_skills_with_llm] RAW LLM RESPONSE: '{result}'")
        
        # [CLEANING STEP] Force removal of common AI conversational garbage
        clean_result = re.sub(r'(?i)here is|normalized|clean|list|skills|note:.*', '', result).strip()
        normalized = [s.strip().lower() for s in clean_result.split(",") if s.strip()]
        
        final_output = normalized if normalized else skills
        print(f"[jd_matcher.py] [normalize_skills_with_llm] OUTPUT: {final_output}")
        return final_output
    except Exception as e:
        print(f"[jd_matcher.py] [normalize_skills_with_llm] ERROR: {str(e)}")
        print(f"[jd_matcher.py] [normalize_skills_with_llm] OUTPUT: {skills} (Fallback to original)")
        return skills

def extract_experience_with_llm(job_description: str) -> int:
    print(f"\n[jd_matcher.py] [extract_experience_with_llm] INPUT: JD length {len(job_description) if job_description else 0}")
    """
    Uses LLM to infer the minimum years of experience required.
    """
    if not llm:
        print("[jd_matcher.py] [extract_experience_with_llm] OUTPUT: 0 (LLM None)")
        return 0
        
    debug_log("Calling LLM for experience extraction")
    prompt = f"From the following job description extract the minimum years of experience required.\n\nReturn ONLY a number.\n\nJob Description:\n{job_description}"
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = response.content.strip()
        debug_log(f"LLM returned experience: {result}")
        print(f"[jd_matcher.py] [extract_experience_with_llm] RAW LLM RESPONSE: '{result}'")
        
        # Safely extract the number from the string
        match = re.search(r'\d+', result)
        if match:
            extracted_val = int(match.group())
            print(f"[jd_matcher.py] [extract_experience_with_llm] OUTPUT: {extracted_val}")
            return extracted_val
        
        print("[jd_matcher.py] [extract_experience_with_llm] OUTPUT: 0 (No number found)")
        return 0
    except Exception as e:
        debug_log(f"LLM error: {str(e)}")
        debug_log("LLM experience extraction failed, returning 0")
        print(f"[jd_matcher.py] [extract_experience_with_llm] ERROR: {str(e)}")
        print("[jd_matcher.py] [extract_experience_with_llm] OUTPUT: 0 (Failed)")
        return 0

# -------------------------------------------------------------------
# MAIN COORDINATION FUNCTION
# -------------------------------------------------------------------

def analyze_job_description(job_description: str) -> Dict[str, Any]:
    print(f"\n[jd_matcher.py] [analyze_job_description] INPUT: JD length {len(job_description) if job_description else 0}")
    """
    Main entry point for analyzing a JD. 
    Coordinates skill and experience extraction and returns a structured result.
    Enhanced with LLM-based fallback and merging mechanisms.
    """
    debug_log("Starting Clean JD analysis")
    
    if not job_description or not isinstance(job_description, str):
        debug_log("Invalid or empty job description provided.")
        fallback_res = {
            "skills": [],
            "experience_required": 0
        }
        print(f"[jd_matcher.py] [analyze_job_description] OUTPUT: {fallback_res}")
        return fallback_res

    # Extract skills using both methods
    rule_skills = extract_skills(job_description)
    llm_skills = extract_skills_with_llm(job_description)
    
    debug_log("Merging rule-based and AI skills")
    
    # [MODIFIED] Use a cleaner merge logic to avoid bloat
    combined_skills = list(set(rule_skills).union(set(llm_skills)))
    
    # [MODIFIED] Filter out very short strings (noise) and pure numbers
    clean_combined_skills = [s for s in combined_skills if len(s) > 1 and not s.isdigit()]

    # Normalize the final combined skill set
    final_skills = normalize_skills_with_llm(clean_combined_skills)

    print(f"[jd_matcher.py] Final Skills Variable: {final_skills}")
    
    # Extract experience, fallback to LLM if rule-based fails to find a requirement
    experience = extract_experience(job_description)
    if experience == 0:
        experience = extract_experience_with_llm(job_description)
        
    # [MODIFIED] Ensure experience caps out logically to avoid crazy numbers
    if experience > 40:
        debug_log(f"Experience capped from {experience} to 10")
        experience = 10
    
    debug_log("JD analysis complete")
    
    final_result = {
        "skills": final_skills,
        "experience_required": experience
    }
    print(f"[jd_matcher.py] [analyze_job_description] OUTPUT: {final_result}\n")
    return final_result