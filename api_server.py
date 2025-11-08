#!/usr/bin/env python3
"""
FastAPI server for SkillSense Platform.
Provides REST API endpoints for talent analytics.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import os
import json
from datetime import datetime

# Import our managers
from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager
from managers.ontology_manager import OntologyManager
from managers.prompt_manager import PromptManager
from simple_nl_to_sql import SimpleNLToSQL

# Initialize FastAPI app
app = FastAPI(
    title="SkillSense API",
    description="AI-Powered Talent Intelligence Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for managers
db_manager = None
llm_manager = None
ontology_manager = None
prompt_manager = None
simple_nl_to_sql = None

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None

class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str
    role: str
    join_date: str

class SkillCreate(BaseModel):
    skill_name: str
    category: str
    normalized_name: str

class EmployeeSkillCreate(BaseModel):
    employee_id: int
    skill_id: int
    confidence: int
    source_type: str
    evidence: str
    is_implicit: bool = False

class QueryResponse(BaseModel):
    success: bool
    answer: str
    sql_query: Optional[str] = None
    results: Optional[List[Dict]] = None
    error: Optional[str] = None

def initialize_managers():
    """Initialize all managers on startup."""
    global db_manager, llm_manager, ontology_manager, prompt_manager, simple_nl_to_sql

    if not all([db_manager, llm_manager, ontology_manager, prompt_manager, simple_nl_to_sql]):
        db_manager = DatabaseManager("data/talent_database.db")
        llm_manager = LLMManager()
        ontology_manager = OntologyManager("config/skills_ontology.json")
        prompt_manager = PromptManager()
        simple_nl_to_sql = SimpleNLToSQL()

# @app.on_event("startup")
# async def startup_event():
#     """Initialize the application."""
#     print("🚀 Starting SkillSense API Server...")
#     initialize_managers()
#     print("✅ All managers initialized successfully!")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SkillSense API - AI-Powered Talent Intelligence Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db_manager.execute_query("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest):
    """Process natural language queries using simple NL-to-SQL."""
    try:
        initialize_managers()

        # Use the simple NL-to-SQL processor
        result = simple_nl_to_sql.process_query(request.query)

        return QueryResponse(
            success=result["success"],
            answer=result["summary"],
            sql_query=result["sql_query"],
            results=result["results"],
            error=result.get("error")
        )

    except Exception as e:
        return QueryResponse(
            success=False,
            answer="",
            sql_query=None,
            results=[],
            error=f"Query processing failed: {str(e)}"
        )

@app.get("/employees")
async def get_employees():
    """Get all employees."""
    try:
        query = "SELECT id, name, email, department, role, join_date FROM employees ORDER BY name"
        results = db_manager.execute_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int):
    """Get a specific employee."""
    try:
        query = "SELECT * FROM employees WHERE id = ?"
        results = db_manager.execute_query(query, (employee_id,))
        if not results:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"success": True, "data": results[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/{employee_id}/skills")
async def get_employee_skills(employee_id: int):
    """Get skills for a specific employee."""
    try:
        query = """
        SELECT s.skill_name, s.category, es.confidence, es.source_type,
               es.evidence, es.is_implicit, es.video_timestamp
        FROM employee_skills es
        JOIN skills s ON es.skill_id = s.id
        WHERE es.employee_id = ?
        ORDER BY es.confidence DESC
        """
        results = db_manager.execute_query(query, (employee_id,))
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skills")
async def get_skills():
    """Get all skills."""
    try:
        query = "SELECT * FROM skills ORDER BY category, skill_name"
        results = db_manager.execute_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/departments")
async def get_departments():
    """Get all departments."""
    try:
        query = "SELECT * FROM departments ORDER BY name"
        results = db_manager.execute_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/skills-distribution")
async def get_skills_distribution():
    """Get skills distribution analytics."""
    try:
        query = """
        SELECT s.category, COUNT(*) as skill_count,
               AVG(es.confidence) as avg_confidence
        FROM employee_skills es
        JOIN skills s ON es.skill_id = s.id
        GROUP BY s.category
        ORDER BY skill_count DESC
        """
        results = db_manager.execute_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/department-skills")
async def get_department_skills():
    """Get skills analysis by department."""
    try:
        query = """
        SELECT e.department, s.category, COUNT(*) as count,
               AVG(es.confidence) as avg_confidence
        FROM employee_skills es
        JOIN employees e ON es.employee_id = e.id
        JOIN skills s ON es.skill_id = s.id
        GROUP BY e.department, s.category
        ORDER BY e.department, count DESC
        """
        results = db_manager.execute_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...), employee_id: int = None):
    """Upload and process a resume file."""
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # This would integrate with GoogleAgent for processing
        # For now, just acknowledge the upload
        return {
            "success": True,
            "message": f"Resume {file.filename} uploaded successfully",
            "file_path": file_path,
            "employee_id": employee_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/video")
async def upload_video(file: UploadFile = File(...), employee_id: int = None):
    """Upload and process a video interview."""
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # This would integrate with GoogleAgent for video processing
        # For now, just acknowledge the upload
        return {
            "success": True,
            "message": f"Video {file.filename} uploaded successfully",
            "file_path": file_path,
            "employee_id": employee_id,
            "processing_status": "queued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ontology")
async def get_ontology():
    """Get the current skills ontology."""
    try:
        ontology = ontology_manager.get_ontology()
        return {"success": True, "data": ontology}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
async def get_database_schema():
    """Get the database schema."""
    try:
        schema = db_manager.get_schema()
        return {"success": True, "data": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_server():
    """Start the FastAPI server."""
    import uvicorn
    print("🚀 Starting SkillSense API Server...")
    initialize_managers()
    print("✅ All managers initialized successfully!")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)

if __name__ == "__main__":
    start_server()