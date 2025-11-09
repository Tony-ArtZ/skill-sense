# SkillSense Demo: "Project Phoenix" Scenario

## Executive Summary

This demo showcases SkillSense's AI-Powered Talent Intelligence Platform through a realistic business scenario: assembling a team for a critical new project called "Project Phoenix."

**The Challenge:** A manager needs to quickly find the best internal candidates with the right mix of technical and leadership skills, validate their experience through multiple data sources, and build an optimal team.

**The Solution:** SkillSense combines structured database queries (SQL), unstructured document analysis (RAG), and multimodal data processing to provide intelligent, evidence-backed talent recommendations.

---

## Demo Flow: The Complete Story

### Pre-Demo Setup

**What You Need:**

- SkillSense backend running on `http://localhost:8001`
- Frontend running on `http://localhost:3000`
- Sample data files ready:
  - `project_phoenix_brief.txt` - Project requirements
  - `alice_resume.docx` - Senior candidate resume
  - `bob_performance_review.pdf` - Mid-level developer review
  - `carlos_peer_feedback.json` - Tech lead 360 reviews

**System Status Check:**

```bash
# Verify backend is running
curl http://localhost:8001/health

# Check database has employees
curl http://localhost:8001/employees
```

---

## Act 1: Understanding the Project Requirements

**Scene:** Manager receives a new project brief and needs to understand what skills are required.

### Action 1: Ingest the Project Brief

**What the user does:**

1. Open SkillSense frontend
2. Navigate to "Ingestion" tab
3. Upload `project_phoenix_brief.txt`
4. Click "Process Sources"

**What happens behind the scenes:**

- Backend receives document
- Text extraction and parsing (200-500ms delay)
- Skills identified: Python, FastAPI, API Design, Leadership, Team Collaboration
- Confidence scoring applied
- Document indexed for RAG queries

**Expected Response:**

```json
{
  "success": true,
  "message": "Resume processed successfully",
  "data": {
    "id": 1,
    "type": "resume",
    "filename": "project_phoenix_brief.txt",
    "status": "processed",
    "extracted_skills": [
      { "name": "Python", "proficiency": 0.9, "confidence": 0.85 },
      { "name": "API Design", "proficiency": 0.88, "confidence": 0.82 }
    ]
  }
}
```

**Presenter Talking Points:**

- "The agent has now consumed the project requirements"
- "It understands both explicit skills (Python, FastAPI) and implicit needs (leadership, collaboration)"
- "This creates a searchable knowledge base for decision-making"

---

## Act 2: Finding the Best Candidate (Hybrid Query)

**Scene:** Manager asks a strategic question that requires combining project requirements with employee database.

### Action 2: Natural Language Query

**What the user does:**

1. Switch to "Query" tab
2. Type: "Who are the best candidates to lead Project Phoenix?"
3. Click "Search"

**What happens behind the scenes:**

- Query classification: **HYBRID** (requires both RAG and SQL)
- RAG component: Retrieves Project Phoenix requirements from uploaded brief
- SQL component: Queries employees with matching skills
- Cross-reference: Matches employee skills against project needs
- Ranking: Scores candidates based on skill proficiency and confidence
- Synthesis: Generates natural language explanation

**Expected Response:**

```json
{
  "success": true,
  "answer": "Based on Project Phoenix requirements, I recommend 2 strong candidates:\n\n1. Alice Chen (Senior Software Engineer) - 95% Python proficiency, proven API design experience, strong leadership evidence from both resume and video interviews. Confidence: 92%\n\n2. Carlos Rodriguez (Tech Lead) - 93% leadership proficiency with peer-validated mentorship skills, solid Python background (88%), excellent communication. Confidence: 88%\n\nAlice is the strongest technical fit, while Carlos excels in team leadership.",
  "sql_query": "SELECT e.*, AVG(es.proficiency) as avg_proficiency FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE s.name IN ('Python', 'API Design', 'Leadership') GROUP BY e.id HAVING avg_proficiency > 0.85 ORDER BY avg_proficiency DESC",
  "results": [
    {
      "id": 1,
      "name": "Alice Chen",
      "department": "Engineering",
      "position": "Senior Software Engineer",
      "confidence_score": 0.92,
      "avg_proficiency": 0.92
    },
    {
      "id": 3,
      "name": "Carlos Rodriguez",
      "department": "Engineering",
      "position": "Tech Lead",
      "confidence_score": 0.88,
      "avg_proficiency": 0.89
    }
  ]
}
```

**Showcase Moment:**

- Point out "Query Type: HYBRID" in logs/response
- Highlight that agent combined:
  - Project brief content (RAG)
  - Employee database (SQL)
  - Multimodal evidence (resume + video)
- Show confidence scores and evidence sources

**Presenter Talking Points:**

- "This is where the magic happens - hybrid reasoning"
- "The agent didn't just search a database, it understood context"
- "Every recommendation is backed by multiple evidence sources"
- "Notice the confidence scores - the system knows what it knows"

---

## Act 3: Deep Dive - Validating Alice's Experience

**Scene:** Alice looks promising. Let's verify her claims with documentary evidence.

### Action 3A: Upload Alice's Resume

**What the user does:**

1. Stay in "Ingestion" tab
2. Upload `alice_resume.docx`
3. Select employee: "Alice Chen"
4. Click "Process Sources"

**What happens behind the scenes:**

- Document parsing (DOCX extraction)
- Skills extraction using NLP
- Experience timeline analysis
- Project history identification
- Evidence linking to existing profile
- Additional delay (500-1000ms for processing)

**Expected Response:**

```json
{
  "success": true,
  "message": "Resume processed successfully",
  "data": {
    "id": 2,
    "type": "resume",
    "filename": "alice_resume.docx",
    "employee_id": 1,
    "status": "processed",
    "extracted_skills": [
      { "name": "Python", "proficiency": 0.95, "confidence": 0.9 },
      { "name": "FastAPI", "proficiency": 0.92, "confidence": 0.88 },
      { "name": "API Design", "proficiency": 0.93, "confidence": 0.85 },
      { "name": "Leadership", "proficiency": 0.87, "confidence": 0.8 }
    ]
  }
}
```

### Action 3B: Evidence-Based Query

**What the user does:**

1. Switch to "Query" tab
2. Type: "Does Alice's resume show experience with Python and leadership?"
3. Click "Search"

**What happens behind the scenes:**

- Query classification: **RAG** (document-specific)
- Semantic search in Alice's resume chunks
- Extract relevant paragraphs/sentences
- Confidence scoring on extracted evidence
- Citation generation

**Expected Response:**

```json
{
  "success": true,
  "answer": "Yes, Alice's resume demonstrates strong experience in both areas:\n\n**Python Experience:**\n- 5+ years of professional Python development\n- Built high-performance trading APIs handling 10,000+ requests/second\n- Led migration of legacy systems to Python/FastAPI architecture\n- Evidence Source: Resume, Section: Work Experience\n\n**Leadership Experience:**\n- Led team of 6 engineers on critical infrastructure projects\n- Mentored 3 junior developers to mid-level positions\n- Coordinated cross-functional initiatives between Engineering and Product\n- Evidence Source: Resume, Section: Leadership & Management\n\nConfidence Level: High (92%) based on detailed, verifiable claims.",
  "results": [
    {
      "document": "alice_resume.docx",
      "evidence": "Senior Software Engineer, TechCorp (2020-Present): Led development of low-latency trading APIs using Python and FastAPI...",
      "confidence": 0.95
    }
  ]
}
```

**Showcase Moment:**

- Point to specific document citations
- Show direct quotes from resume
- Highlight evidence-backed claims vs assumptions
- Demonstrate cross-referencing with video interview data

**Presenter Talking Points:**

- "The system doesn't just say 'yes' - it provides proof"
- "Every claim is linked to a specific source document"
- "This is crucial for hiring decisions - verifiable evidence"
- "Notice how it combines resume claims with other data sources"

---

## Act 4: Comparative Analysis - Alice vs Bob

**Scene:** Bob is another strong candidate. Let's compare both using their most recent documents.

### Action 4A: Upload Bob's Performance Review

**What the user does:**

1. Go to "Ingestion" tab
2. Upload `bob_performance_review.pdf`
3. Select employee: "Bob Martinez"
4. Click "Process Sources"

**Expected Response:**

```json
{
  "success": true,
  "message": "Resume processed successfully",
  "data": {
    "id": 3,
    "type": "resume",
    "filename": "bob_performance_review.pdf",
    "employee_id": 2,
    "status": "processed",
    "extracted_skills": [
      { "name": "JavaScript", "proficiency": 0.92, "confidence": 0.88 },
      { "name": "React", "proficiency": 0.88, "confidence": 0.85 },
      { "name": "Documentation", "proficiency": 0.9, "confidence": 0.75 }
    ]
  }
}
```

### Action 4B: Cross-Document Comparison

**What the user does:**

1. Switch to "Query" tab
2. Type: "Compare Alice's skills from her resume with Bob's skills from his performance review for Project Phoenix"
3. Click "Search"

**What happens behind the scenes:**

- Query classification: **ADVANCED HYBRID** (multi-document RAG + SQL)
- RAG queries on both documents simultaneously
- Skills extraction and normalization
- Proficiency comparison with context
- Project requirement matching
- Recommendation synthesis

**Expected Response:**

```json
{
  "success": true,
  "answer": "**Comparative Analysis: Alice Chen vs Bob Martinez for Project Phoenix**\n\n**Technical Skills:**\n- Alice: Strong Python (95%), FastAPI (92%), API Design (93%) - Perfect match for backend requirements\n- Bob: Strong JavaScript (92%), React (88%), Node.js (85%) - Better suited for frontend work\n\n**Leadership & Collaboration:**\n- Alice: Proven team leadership (5+ direct reports), cross-functional coordination\n- Bob: Performance review highlights 'exceptional documentation skills' and 'patient mentoring' - implicit leadership qualities\n\n**Project Phoenix Fit:**\n- Alice: 95% match - Direct experience with required tech stack and proven project leadership\n- Bob: 70% match - Strong engineer but tech stack mismatch; could contribute to frontend components\n\n**Recommendation:** Alice is the clear choice for Project Lead. Consider Bob for frontend integration work or as a strong mentorship resource.\n\n**Hidden Insight:** Bob's performance review reveals he 'documented every API endpoint with examples' - an implicit skill in API design that doesn't appear on his resume.",
  "sql_query": "SELECT e.name, s.name as skill, es.proficiency FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE e.id IN (1, 2)",
  "results": [
    {
      "candidate": "Alice Chen",
      "primary_skills": ["Python", "API Design", "Leadership"],
      "match_score": 0.95
    },
    {
      "candidate": "Bob Martinez",
      "primary_skills": ["JavaScript", "React", "Documentation"],
      "match_score": 0.7
    }
  ]
}
```

**Showcase Moment - THE BIG ONE:**

- This is the most impressive demonstration
- Agent analyzed TWO different document types (.docx and .pdf)
- Found an **implicit skill** (API documentation) from narrative text
- Cross-referenced with structured database
- Provided nuanced, context-aware recommendation

**Presenter Talking Points:**

- "This is the power of multimodal intelligence"
- "The agent read a narrative performance review and extracted implicit skills"
- "Bob's 'documentation excellence' wasn't in his resume - it was hidden in his manager's review"
- "This is how you discover hidden talent in your organization"
- "No human could analyze this many sources this quickly"

---

## Act 5: Efficient SQL Query - Finding Junior Developers

**Scene:** For balance, we also need a junior developer with specific frontend skills.

### Action 5: Pure SQL Query

**What the user does:**

1. In "Query" tab, type: "Show me all engineers with less than 2 years of experience who know React"
2. Click "Search"

**What happens behind the scenes:**

- Query classification: **SQL** (structured, specific criteria)
- Direct database query (fastest path)
- No RAG needed - all data is structured
- Response time: <300ms

**Expected Response:**

```json
{
  "success": true,
  "answer": "Found 1 engineer matching your criteria:\n\nEthan Williams - UI/UX Designer (hired Feb 2022, ~2 years experience)\n- React proficiency: 75%\n- Also skilled in: Figma (95%), Communication (88%)\n- Note: While listed as Designer, has coding capabilities\n\nWould you like me to search for additional frontend developers with React experience?",
  "sql_query": "SELECT e.*, es.proficiency, s.name as skill FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE s.name = 'React' AND DATEDIFF(CURRENT_DATE, e.hire_date) < 730 AND e.department = 'Engineering'",
  "results": [
    {
      "id": 5,
      "name": "Ethan Williams",
      "department": "Design",
      "position": "UI/UX Designer",
      "hire_date": "2022-02-14",
      "proficiency": 0.75
    }
  ]
}
```

**Showcase Moment:**

- Point out the speed (instant response)
- Agent chose the RIGHT tool for the job
- No unnecessary RAG queries
- Efficient resource utilization

**Presenter Talking Points:**

- "The agent knows when to use simple tools"
- "Pure SQL query - no AI overhead needed"
- "This is important for scalability"
- "Complex reasoning when needed, efficiency when possible"

---

## Act 6: Advanced Analytics Dashboard

**Scene:** Let's see the big picture - organization-wide talent intelligence.

### Action 6: View Analytics

**What the user does:**

1. Switch to "Analytics" tab
2. View automatically loaded dashboards

**What's displayed:**

**Skills Distribution:**

- Python: 3 employees, avg proficiency 92%
- JavaScript: 3 employees, avg proficiency 90%
- React: 2 employees, avg proficiency 82%
- Leadership: 2 employees, avg proficiency 89%

**Department Analysis:**

- Engineering: 3 employees, top skills [Python, JavaScript, API Design]
- Data Science: 1 employee, top skills [Python, ML, TensorFlow]
- Design: 1 employee, top skills [Figma, React, Communication]

**Skill Gaps:**

- High demand: DevOps skills (only 1 employee)
- Missing: Cloud architecture (AWS representation low)
- Opportunity: Cross-train designers in frontend development

**Presenter Talking Points:**

- "This is strategic workforce planning"
- "See skill gaps before they become problems"
- "Data-driven hiring and training decisions"
- "Track skill evolution across the organization"

---

## The Finale: Team Recommendation

### Action 7: Final Team Assembly

**What the user does:**

1. Type: "Generate a final team proposal for Project Phoenix with justifications based on all available data"

**Expected Response:**

```json
{
  "success": true,
  "answer": "**Project Phoenix Team Proposal**\n\n**Project Lead: Alice Chen**\n- Rationale: 95% technical match, proven leadership with 5+ direct reports, experience with exact tech stack (Python/FastAPI), high confidence score (92%)\n- Evidence: Resume (API project leadership), Video interview (communication clarity), Performance data (consistent high performer)\n\n**Tech Lead: Carlos Rodriguez**\n- Rationale: Exceptional mentorship (93% leadership proficiency), strong Python skills (88%), peer reviews highlight 'builds team cohesion'\n- Evidence: Peer feedback (360 reviews), Past collaboration data (worked with Alice on 2 previous projects), Communication assessment (video analysis)\n\n**Frontend Engineer: Ethan Williams**\n- Rationale: React proficiency (75%), design background provides UX perspective, growth potential\n- Evidence: Recent hire (fresh perspective), Design portfolio (user-centric thinking), Documented learning agility\n\n**Team Dynamics Assessment:**\n- Alice + Carlos: Proven collaboration (past projects), complementary skills\n- Skill coverage: Backend (Alice), Leadership (Carlos), Frontend/UX (Ethan)\n- Risk: Junior frontend resource - recommend senior frontend support\n\n**Confidence Level: 88%**\n\nThis team covers all Project Phoenix requirements with evidence-backed skill validation and proven team chemistry.",
  "results": [
    /* team composition data */
  ]
}
```

---

## Summary: What We Demonstrated

### Technical Capabilities

1. **Multimodal Data Ingestion**

   - Text documents (.txt, .docx)
   - PDFs with parsing
   - Video analysis (mentioned)
   - Structured data (SQL)

2. **Query Intelligence**

   - SQL queries (structured data)
   - RAG queries (document content)
   - Hybrid queries (combined reasoning)
   - Query classification (automatic tool selection)

3. **Evidence-Based Reasoning**

   - Source citation
   - Confidence scoring
   - Cross-reference validation
   - Hidden skill discovery

4. **Strategic Analytics**
   - Skills distribution
   - Gap analysis
   - Team composition
   - Hiring recommendations

### Business Value

1. **Speed**: Minutes instead of days for talent discovery
2. **Accuracy**: Evidence-backed recommendations vs gut feeling
3. **Discovery**: Finds hidden talent and implicit skills
4. **Scalability**: Handles growing employee base effortlessly
5. **Compliance**: Auditable decision trail with source citations

### The "Wow" Moments Recap

1. ⚡ **Hybrid Query** - Combining project brief with employee database
2. 🔍 **Evidence Extraction** - Pulling specific quotes from Alice's resume
3. 🎯 **Cross-Document Analysis** - Comparing resume vs performance review
4. 💎 **Hidden Skill Discovery** - Finding Bob's implicit documentation expertise
5. 🚀 **Speed vs Complexity** - Choosing optimal query strategy
6. 📊 **Strategic Intelligence** - Organization-wide talent insights

---

## Technical Notes for Demo Presenters

### Mock Backend Behavior

**Artificial Delays:**

- Standard queries: 200-500ms
- Document processing: 500-1000ms
- Video processing: 1000-2000ms
- AI query processing: 300-800ms

**Why delays matter:** They simulate real AI processing time and make the demo feel authentic. Users expect some processing time for complex analysis.

### Pre-Demo Checklist

- [ ] Backend running on port 8001
- [ ] Frontend running on port 3000
- [ ] Browser cache cleared
- [ ] Sample files ready in accessible location
- [ ] Test all endpoints with curl/Postman
- [ ] Verify all 5 employees in database
- [ ] Check analytics endpoints return data
- [ ] Practice the narrative flow (5-10 minutes total)

### Troubleshooting

**If queries return empty results:**

- Check backend logs for errors
- Verify database has sample data: `curl localhost:8001/employees`
- Restart backend server

**If uploads fail:**

- Check file size limits
- Verify CORS headers
- Check network tab for errors

**If frontend doesn't update:**

- Hard refresh (Ctrl+Shift+R)
- Check API endpoint URLs
- Verify backend CORS settings

---

## Customization for Different Audiences

### For Technical Audiences (Developers/Architects)

- Show SQL queries generated
- Explain query classification algorithm
- Demonstrate RAG embedding process
- Discuss vector database architecture
- Show API response structures

### For Business Audiences (HR/Executives)

- Focus on time savings
- Highlight accuracy improvements
- Emphasize risk reduction
- Show ROI calculations
- Demonstrate compliance features

### For Investors

- Market size and opportunity
- Scalability story
- Competitive advantages
- Technology moat
- Customer acquisition strategy

---

## Next Steps After Demo

1. **Immediate:** "Would you like to see this with your own employee data?"
2. **Short-term:** "We can pilot this with your HR team in 2 weeks"
3. **Long-term:** "Let's discuss integration with your HRIS system"

---

## Appendix: Sample Data Files

### project_phoenix_brief.txt

```
Project Phoenix - Internal Initiative Brief

Overview:
Project Phoenix is a critical initiative to rebuild our customer-facing API platform
with modern, scalable architecture. The project has a 6-month timeline and high
visibility with executive leadership.

Required Skills:
- Python (primary language)
- FastAPI or similar async framework experience
- API design and RESTful principles
- Database optimization (PostgreSQL preferred)
- Leadership and team coordination
- Experience with high-traffic systems (10k+ req/sec)

Team Composition:
- 1 Project Lead (senior level, 5+ years experience)
- 1 Tech Lead (mentorship focus)
- 2-3 Backend Engineers
- 1 Frontend Engineer (for API testing tools)

Success Criteria:
- Complete API migration with zero downtime
- Achieve 99.9% uptime SLA
- Reduce average response time by 40%
- Document all endpoints thoroughly
```

### alice_resume.docx (content summary)

```
Alice Chen
Senior Software Engineer
alice.chen@email.com | LinkedIn: /in/alicechen

SUMMARY
Senior software engineer with 7+ years building high-performance APIs and distributed
systems. Proven track record leading technical teams and delivering mission-critical
infrastructure.

EXPERIENCE

Senior Software Engineer | TechCorp | 2020-Present
- Led development of low-latency trading API using Python and FastAPI
- Managed team of 6 engineers across 3 major product releases
- Reduced API response time by 60% through caching and optimization
- Handled 15,000+ requests/second with 99.95% uptime

Software Engineer | StartupCo | 2018-2020
- Built RESTful APIs serving 1M+ daily active users
- Mentored 3 junior developers to mid-level positions
- Implemented PostgreSQL query optimizations (40% improvement)

SKILLS
Technical: Python, FastAPI, Django, PostgreSQL, Redis, Docker, AWS
Leadership: Team management, Technical mentoring, Cross-functional coordination
```

### bob_performance_review.pdf (content summary)

```
Performance Review - Bob Martinez
Period: Jan 2024 - Dec 2024
Position: Full Stack Developer
Reviewer: Sarah Johnson, Engineering Manager

TECHNICAL PERFORMANCE: Exceeds Expectations

Bob has demonstrated strong technical capabilities throughout the year. His JavaScript
and React work has been consistently high quality. What really stands out is his
attention to detail and documentation.

Bob has a unique talent that isn't captured in his job description: he documents
everything exceptionally well. Every API endpoint he builds includes comprehensive
examples, every component has clear usage docs, and he even created our team's
onboarding guide. This "silent leadership" through documentation has made our entire
team more effective.

AREAS OF STRENGTH:
- Clean, maintainable code
- Excellent problem-solving
- Patient mentorship with junior devs (though not officially a mentor)
- Documentation excellence (implicit skill)

DEVELOPMENT AREAS:
- Could take on more high-visibility projects
- Sometimes too perfectionist (good problem to have)

RECOMMENDATION: Strong performer, consider for tech lead track
```

---

**End of Demo Script**

This demo tells a complete story from problem to solution, showcasing every major
feature in a natural, compelling narrative that resonates with real business needs.
