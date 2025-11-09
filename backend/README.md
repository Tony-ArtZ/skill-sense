# SkillSense Mock Backend

A fully functional mock Node.js backend that implements the complete SkillSense API specification with realistic data and artificial delays to simulate real AI processing.

## 🚀 Quick Start

```bash
# Install dependencies
bun install

# Run development server (with auto-reload)
bun run dev

# Or run directly
bun run index.ts
```

Server will start on **http://localhost:8001**

## ✨ Features

- ✅ **All OpenAPI Endpoints Implemented**
- ✅ **Demo Script Support** - Optimized for "Project Phoenix" narrative (see `/DEMO_SCRIPT.md`)
- ✅ **Realistic Artificial Delays** (200ms-2000ms based on operation complexity)
- ✅ **CORS Enabled** - Works with frontend on any port
- ✅ **Rich Mock Data** - 5 employees, 14 skills, realistic relationships
- ✅ **Intelligent Query Matching** - Supports all demo scenarios
- ✅ **Multimodal Upload Simulation** - Resume and video processing

## 📡 Key Endpoints

- `POST /query` - Natural language queries ⭐ **THE MAIN FEATURE**
- `GET /employees` - List all employees
- `GET /employees/:id/skills` - Get employee skills with evidence
- `GET /analytics/skills-distribution` - Skills across organization
- `POST /upload/resume` - Upload and process resume
- `POST /upload/video` - Upload and process video interview

See full endpoint list: `curl http://localhost:8001`

## 🎭 Demo Script Support

This backend powers the complete "Project Phoenix" demo narrative with intelligent responses for:

1. **"Who are the best candidates to lead Project Phoenix?"** - HYBRID query
2. **"Does Alice's resume show experience with Python?"** - RAG query
3. **"Compare Alice and Bob for the project"** - ADVANCED_HYBRID with hidden skill discovery
4. **"Show me junior React developers"** - Pure SQL query
5. **"Generate final team proposal"** - Comprehensive analysis

Each query type has realistic processing delays and detailed evidence-backed responses.

## 🧪 Testing

```bash
# Health check
curl http://localhost:8001/health

# Test demo query
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the best candidates to lead Project Phoenix?"}'

# Get all employees
curl http://localhost:8001/employees
```

## 📊 Mock Data

- **5 Employees** (Alice, Bob, Carlos, Diana, Ethan)
- **14 Skills** (Python, JavaScript, React, Leadership, etc.)
- **Evidence Sources** (Resume, Video, Reviews, GitHub, Peer feedback)
- **Multimodal profiles** with confidence scores

## ⏱️ Artificial Delays

- Standard queries: 200-500ms
- AI processing: 300-800ms
- Document upload: 500-1000ms
- Video upload: 1000-2000ms
- Complex analysis: Up to 1500ms

These make the demo feel authentic and allow presenters to narrate what's happening.

## 📖 Full Documentation

See `/DEMO_SCRIPT.md` for complete demo narrative and presentation guide.

---

Built with [Bun](https://bun.sh) 🥟 - Fast, modern JavaScript runtime
