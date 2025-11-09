#!/usr/bin/env python3
"""
FastAPI server for SkillSense Platform.
Provides REST API endpoints for talent analytics.
"""

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Import our managers
from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager
from managers.ontology_manager import OntologyManager
from managers.prompt_manager import PromptManager
from managers.web_scraper import WebScraperManager
from simple_nl_to_sql import SimpleNLToSQL
from rag_manager import RAGManager
from agentic_query_processor import AgenticQueryProcessor

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    print("🚀 Initializing managers...")
    app.state.db_manager = DatabaseManager("data/talent_database.db")
    app.state.llm_manager = LLMManager()
    app.state.ontology_manager = OntologyManager("config/skills_ontology.json")
    app.state.prompt_manager = PromptManager()
    app.state.web_scraper = WebScraperManager()
    app.state.rag_manager = RAGManager()
    app.state.simple_nl_to_sql = SimpleNLToSQL(db_manager=app.state.db_manager, llm_manager=app.state.llm_manager)
    app.state.agentic_processor = AgenticQueryProcessor(rag_manager=app.state.rag_manager, llm_manager=app.state.llm_manager, nl_to_sql_processor=app.state.simple_nl_to_sql, ontology_manager=app.state.ontology_manager)
    print("✅ All managers initialized successfully!")
    yield
    print("👋 Shutting down SkillSense API Server...")

# Initialize FastAPI app
app = FastAPI(
    title="SkillSense API",
    description="AI-Powered Talent Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    answer: str
    sql_query: Optional[str] = None
    results: Optional[List[Dict]] = None
    rag_sources: Optional[List[Dict]] = None
    query_type: Optional[str] = None
    error: Optional[str] = None

class IngestURLRequest(BaseModel):
    url: str
    employee_id: int
    document_type: str = "web_source"

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SkillSense API - AI-Powered Talent Intelligence Platform",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    try:
        request.app.state.db_manager.execute_query("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def natural_language_query(req: Request, query_request: QueryRequest):
    """Process natural language queries using agentic RAG + NL-to-SQL."""
    try:
        result = await req.app.state.agentic_processor.process_query(query_request.query)
        return QueryResponse(
            success=result["success"],
            answer=result.get("answer", ""),
            sql_query=result.get("sql_query"),
            results=result.get("results", []),
            rag_sources=result.get("rag_sources", []),
            query_type=result.get("query_type"),
            error=result.get("error")
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            answer="",
            sql_query=None,
            results=[],
            rag_sources=[],
            query_type="error",
            error=f"Query processing failed: {str(e)}"
        )

@app.post("/upload/document")
async def upload_document(employee_id: int = Form(...), file: UploadFile = File(...)):
    """Endpoint to upload a document for an employee."""
    try:
        temp_dir = "uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        result = await app.state.rag_manager.add_document(file_path, employee_id)
        
        if result.get("success"):
            return JSONResponse(status_code=200, content=result)
        else:
            return JSONResponse(status_code=400, content={"error": result.get("error", "Failed to process document")})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"An unexpected error occurred: {str(e)}"})

@app.post("/ingest-url")
async def ingest_url(request: IngestURLRequest, req: Request):
    """Endpoint to scrape a URL and ingest its content into the RAG system."""
    try:
        scraped_text = await req.app.state.web_scraper.scrape_url(request.url)
        if not scraped_text:
            raise HTTPException(status_code=400, detail="Could not scrape any content from the URL.")

        # --- DEBUGGING STEP: Save scraped content to a file ---
        with open("scraped_content.txt", "w", encoding="utf-8") as f:
            f.write(scraped_text)
        print("📝 DEBUG: Scraped content saved to scraped_content.txt")
        # --- END DEBUGGING STEP ---

        # Create a temporary file to hold the scraped content

        temp_dir = "uploads"
        os.makedirs(temp_dir, exist_ok=True)
        sanitized_filename = "".join(c for c in request.url if c.isalnum())[-50:] + ".txt"
        file_path = os.path.join(temp_dir, sanitized_filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(scraped_text)

        result = await req.app.state.rag_manager.add_document(
            file_path=file_path,
            employee_id=request.employee_id,
            document_type=request.document_type
        )
        
        if result.get("success"):
            return JSONResponse(status_code=200, content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to process scraped content"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/rag/stats")
async def get_rag_stats(request: Request):
    """Get RAG system statistics."""
    try:
        stats = request.app.state.rag_manager.get_document_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agentic/stats")
async def get_agentic_stats(request: Request):
    """Get agentic system statistics."""
    try:
        stats = request.app.state.agentic_processor.get_system_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))