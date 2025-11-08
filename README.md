# SkillSense: AI-Powered Talent Intelligence Platform

## Overview
A hackathon project that combines NL-to-SQL analytics with multimodal AI to revolutionize talent management and skills discovery.

## Features
- **Multimodal Skills Extraction**: Analyze resumes, videos, and interviews
- **Natural Language Analytics**: Ask complex business questions about talent
- **Evidence-Based Validation**: Cross-reference claims across multiple sources
- **Hidden Skills Discovery**: Uncover talents that traditional systems miss

## Architecture
- **Backend**: FastAPI with SQLite database
- **NL-to-SQL**: Advanced query processing using LangGraph
- **Multimodal AI**: Video/audio analysis with Google Gemini
- **Frontend**: Modern web interface (lovable)

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py

# Run API server
python api_server.py

# Access web interface
http://localhost:8001
```

## Project Structure
```
Hackathon/
├── managers/          # Core business logic managers
├── nodes/             # Workflow orchestration nodes
├── multimodal/        # Video/audio AI processing
├── api/               # FastAPI endpoints
├── frontend/          # Web interface
├── data/              # Database and sample data
├── config/            # Configuration files
└── tests/             # Test files
```

## Key Differentiators
- Hybrid RAG + NL-to-SQL architecture
- Multimodal skills validation
- Business intelligence for talent analytics
- Evidence-based confidence scoring