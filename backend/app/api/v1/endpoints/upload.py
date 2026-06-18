from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import tempfile

from app.services.duckdb_service import load_file_to_duckdb, extract_schema
from app.models.data_schema import UploadResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    # Check extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ['.csv', '.xls', '.xlsx']:
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
    # Save the file to a temporary location
    try:
        fd, temp_path = tempfile.mkstemp(suffix=ext.lower())
        os.close(fd)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Load into DuckDB
        table_name = load_file_to_duckdb(temp_path, file.filename)
        
        # Extract Schema
        schema_info = extract_schema(table_name)
        
        # Cleanup temp file
        os.remove(temp_path)
        
        return UploadResponse(
            message="File successfully loaded into DuckDB",
            table_name=table_name,
            schema_info=schema_info
        )
        
    except Exception as e:
        # Try to clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))
