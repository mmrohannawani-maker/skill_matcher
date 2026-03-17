# Endpoint to upload and process skill matrix Excel file

# app/routers/excel_router.py

import os
import shutil
import tempfile
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Database dependencies
from app.core.dependencies import get_db

# Services
from app.services import excel_service

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# ROUTER INITIALIZATION
# -------------------------------------------------------------------
router = APIRouter(
    prefix="/excel",
    tags=["Excel Upload"]
)

# -------------------------------------------------------------------
# DEBUG LOG HELPER FUNCTIONS
# -------------------------------------------------------------------
def log_router_start(endpoint_name: str) -> None:
    """Logs when endpoint execution begins."""
    logger.debug(f"[EXCEL ROUTER] {endpoint_name.capitalize()} endpoint triggered")

def log_router_success(endpoint_name: str) -> None:
    """Logs successful completion."""
    logger.debug(f"[EXCEL ROUTER] {endpoint_name.capitalize()} completed successfully")

def log_router_error(endpoint_name: str, error: Exception) -> None:
    """Logs exceptions."""
    logger.error(f"[EXCEL ROUTER] Error during {endpoint_name}: {str(error)}")

# -------------------------------------------------------------------
# ENDPOINTS
# -------------------------------------------------------------------



@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload an Excel file containing developer data"
)
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Accepts an Excel file upload (.xlsx, .xls) and processes the data to 
    bulk create developer profiles and assign skills using AI enhancements.
    """
    log_router_start("upload")
    
    # Validate file extension
    filename = file.filename or ""
    if not filename.endswith((".xlsx", ".xls")):
        error_msg = f"Invalid file format: {filename}. Only .xlsx and .xls are supported."
        log_router_error("upload", Exception(error_msg))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # # Save uploaded file to a temporary location for pandas to read
    # temp_file_path = ""
    # try:
    #     # Create a temporary file
    #     fd, temp_file_path = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
    #     with os.fdopen(fd, "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
            
    #     # Call the service layer to process the file
    #     # Assuming the service method process_excel_file handles the DB injection and returns stats
    #     result = excel_service.process_excel_file(file_path=temp_file_path, db=db)
        
    #     log_router_success("upload")
    #     return result

    # except HTTPException as http_exc:
    #     log_router_error("upload", http_exc)
    #     raise http_exc
    # except Exception as e:
    #     log_router_error("upload", e)
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="An unexpected error occurred during Excel processing."
    #     )
    # finally:
    #     # Clean up the temporary file safely
    #     if temp_file_path and os.path.exists(temp_file_path):
    #         try:
    #             os.remove(temp_file_path)
    #         except Exception as cleanup_error:
    #             logger.warning(f"[EXCEL ROUTER] Failed to remove temp file {temp_file_path}: {cleanup_error}")
    # Define a persistent directory
    UPLOAD_DIR = "app/excel"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save file to project folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Call service (Note: Changed function name to match your service)
        result = excel_service.process_excel_data(file_path=file_path, db=db)
        
        log_router_success("upload")
        return result
    except Exception as e:
        log_router_error("upload", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/template",
    summary="Download Excel template for developer ingestion"
)
async def get_excel_template():
    """
    Returns a downloadable Excel template to help users format 
    their developer data correctly for bulk upload.
    """
    log_router_start("template download")
    try:
        # The service generates/locates the template and returns the file path
        template_path = excel_service.generate_excel_template()
        
        if not template_path or not os.path.exists(template_path):
            raise FileNotFoundError("Template file could not be generated or found.")
            
        log_router_success("template download")
        
        return FileResponse(
            path=template_path,
            filename="Developer_Ingestion_Template.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        log_router_error("template download", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the Excel template."
        )


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Get Excel ingestion system status"
)
def get_excel_status() -> Dict[str, Any]:
    """
    Returns simple system information and configuration regarding 
    the Excel bulk ingestion feature.
    """
    log_router_start("status check")
    try:
        status_info = {
            "supported_formats": ["xlsx", "xls"],
            "max_file_size_mb": 10,
            "ai_processing": True
        }
        log_router_success("status check")
        return status_info
    except Exception as e:
        log_router_error("status check", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve system status."
        )