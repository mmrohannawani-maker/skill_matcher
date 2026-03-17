# Entry point of the FastAPI application where all routers are registered

import logging
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import iterate_in_threadpool

# [MODIFIED] GLOBAL LOGGING SILENCERS
# We do this FIRST so it catches libraries as they load
logging.basicConfig(level=logging.WARNING)
silenced_loggers = ["httpcore", "httpx", "h2", "hpack"]
for logger_name in silenced_loggers:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Database Imports
from app.database.connection import engine
from app.database.base import Base

# Router Imports
from app.routers import (
    auth_router,
    developer_router,
    skill_router,
    jd_router,
    report_router,
    excel_router
)

# Debug Logging
def debug_log(message: str) -> None:
    # We use print here so your manual debug messages still show up
    print(f"[APP MAIN DEBUG] {message}")

# Application Initialization
debug_log("Starting FastAPI application")
app = FastAPI(
    title="Developer Skill Intelligence API",
    description="API for managing developer skills, job matching, and analytics.",
    version="1.0.0"
)

# List of origins allowed to access the backend
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "*"  # Temporary: Allow all origins to rule out CORS as the problem
]

# Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_final_responses(request: Request, call_next):
    # Process the request and get the response
    response = await call_next(request)
    
    # We only want to debug our specific data endpoints
    if "/developers/" in request.url.path or "/skills/" in request.url.path:
        # Note: Added color print formatting for better visibility in terminal
        print(f"\n\x1b[33m >>> BACKEND RESPONSE DEBUG: {request.url.path} <<<\x1b[0m")
        
        # Capture the response body
        response_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        
        try:
            data = json.loads(response_body[0].decode())
            if isinstance(data, list) and len(data) > 0:
                print(f"TOTAL ITEMS: {len(data)}")
                print(f"FIRST ITEM SAMPLE: {json.dumps(data[0], indent=2)}")
            else:
                print(f"RESPONSE DATA: {data}")
        except Exception as e:
            print(f"Could not parse response body: {e}")
            
    return response

# Database Initialization
debug_log("Creating database tables")
Base.metadata.create_all(bind=engine)

# Router Registration
debug_log("Registering routers")
app.include_router(auth_router.router)
app.include_router(developer_router.router)
app.include_router(skill_router.router)
app.include_router(jd_router.router)
app.include_router(report_router.router)
app.include_router(excel_router.router)

# Startup Events
@app.on_event("startup")
async def startup_event() -> None:
    debug_log("Application startup complete")

# Shutdown Events
@app.on_event("shutdown")
async def shutdown_event() -> None:
    debug_log("Server shutting down")

# Root Endpoint
@app.get("/", tags=["Health"])
async def root_health_check() -> dict:
    return {
        "message": "Developer Skill Intelligence API running"
    }