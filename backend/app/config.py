# Handles environment variables like database URL, JWT secret, and app settings
import os
from dotenv import load_dotenv

def debug_log(message: str) -> None:
    """Reusable debug logging function for tracking configuration loading."""
    print(f"[CONFIG DEBUG] {message}")

debug_log("Loading environment variables from .env file")
load_dotenv()

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
debug_log(f"Database URL loaded: {DATABASE_URL}")

# ==========================================
# JWT AUTHENTICATION CONFIGURATION
# ==========================================
SECRET_KEY = os.getenv("SECRET_KEY", "DEFAULT_INSECURE_SECRET_KEY_DO_NOT_USE_IN_PROD")
if SECRET_KEY == "DEFAULT_INSECURE_SECRET_KEY_DO_NOT_USE_IN_PROD":
    debug_log("WARNING: Using default insecure SECRET_KEY. Please set SECRET_KEY in .env for production.")
else:
    debug_log("Secret key loaded securely")
    
ALGORITHM = os.getenv("ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except ValueError:
    debug_log("WARNING: Invalid ACCESS_TOKEN_EXPIRE_MINUTES value. Defaulting to 60.")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    
debug_log(f"JWT Configuration loaded (Algorithm: {ALGORITHM}, Expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} mins)")

# ==========================================
# LLM CONFIGURATION (HuggingFace DeepSeek-V3)
# ==========================================
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not HUGGINGFACEHUB_API_TOKEN:
    debug_log("WARNING: HUGGINGFACEHUB_API_TOKEN is not set in .env. LLM features may fail.")
else:
    debug_log("HuggingFace API token loaded")
    
LLM_REPO_ID = os.getenv("LLM_REPO_ID", "deepseek-ai/DeepSeek-V3")

try:
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
except ValueError:
    debug_log("WARNING: Invalid TEMPERATURE value. Defaulting to 0.0.")
    TEMPERATURE = 0.0
    
debug_log(f"LLM Configuration loaded (Repo: {LLM_REPO_ID}, Temp: {TEMPERATURE})")

def display_config() -> None:
    """
    Helper function to display the loaded configuration for debugging purposes.
    Safely hides sensitive information like tokens and secret keys.
    """
    debug_log("--- Current Configuration State ---")
    debug_log(f"DATABASE_URL: {DATABASE_URL}")
    debug_log(f"ALGORITHM: {ALGORITHM}")
    debug_log(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
    debug_log(f"LLM_REPO_ID: {LLM_REPO_ID}")
    debug_log(f"TEMPERATURE: {TEMPERATURE}")
    debug_log("SECRET_KEY: [HIDDEN]")
    debug_log("HUGGINGFACEHUB_API_TOKEN: [HIDDEN]" if HUGGINGFACEHUB_API_TOKEN else "[NOT SET]")
    debug_log("-----------------------------------")