import { serve } from "bun";

// Mock data
const employees = [
  {
    id: 1,
    name: "Alice Chen",
    email: "alice@company.com",
    department: "Engineering",
    position: "Senior Software Engineer",
    hire_date: "2020-03-15",
    confidence_score: 0.92,
  },
  {
    id: 2,
    name: "Bob Martinez",
    email: "bob@company.com",
    department: "Engineering",
    position: "Full Stack Developer",
    hire_date: "2021-06-01",
    confidence_score: 0.85,
  },
  {
    id: 3,
    name: "Carlos Rodriguez",
    email: "carlos@company.com",
    department: "Engineering",
    position: "Tech Lead",
    hire_date: "2019-01-10",
    confidence_score: 0.88,
  },
  {
    id: 4,
    name: "Diana Park",
    email: "diana@company.com",
    department: "Data Science",
    position: "ML Engineer",
    hire_date: "2021-09-20",
    confidence_score: 0.9,
  },
  {
    id: 5,
    name: "Ethan Williams",
    email: "ethan@company.com",
    department: "Design",
    position: "UI/UX Designer",
    hire_date: "2022-02-14",
    confidence_score: 0.87,
  },
];

const skills = [
  { id: 1, name: "Python", category: "Programming Language" },
  { id: 2, name: "JavaScript", category: "Programming Language" },
  { id: 3, name: "React", category: "Framework" },
  { id: 4, name: "Node.js", category: "Framework" },
  { id: 5, name: "Machine Learning", category: "Domain" },
  { id: 6, name: "API Design", category: "Technical" },
  { id: 7, name: "PostgreSQL", category: "Database" },
  { id: 8, name: "Docker", category: "DevOps" },
  { id: 9, name: "Leadership", category: "Soft Skill" },
  { id: 10, name: "Communication", category: "Soft Skill" },
  { id: 11, name: "TypeScript", category: "Programming Language" },
  { id: 12, name: "AWS", category: "Cloud" },
  { id: 13, name: "Figma", category: "Design Tool" },
  { id: 14, name: "TensorFlow", category: "ML Framework" },
];

const employeeSkills = [
  // Alice - Senior Software Engineer
  {
    employee_id: 1,
    skill_id: 1,
    proficiency: 0.95,
    evidence_sources: ["resume", "video"],
  },
  {
    employee_id: 1,
    skill_id: 2,
    proficiency: 0.9,
    evidence_sources: ["resume", "github"],
  },
  {
    employee_id: 1,
    skill_id: 6,
    proficiency: 0.92,
    evidence_sources: ["resume", "review"],
  },
  {
    employee_id: 1,
    skill_id: 7,
    proficiency: 0.88,
    evidence_sources: ["resume"],
  },
  {
    employee_id: 1,
    skill_id: 9,
    proficiency: 0.85,
    evidence_sources: ["video", "review"],
  },

  // Bob - Full Stack Developer
  {
    employee_id: 2,
    skill_id: 2,
    proficiency: 0.92,
    evidence_sources: ["resume", "github"],
  },
  {
    employee_id: 2,
    skill_id: 3,
    proficiency: 0.88,
    evidence_sources: ["resume", "github"],
  },
  {
    employee_id: 2,
    skill_id: 4,
    proficiency: 0.85,
    evidence_sources: ["resume"],
  },
  {
    employee_id: 2,
    skill_id: 11,
    proficiency: 0.9,
    evidence_sources: ["resume", "github"],
  },

  // Carlos - Tech Lead
  {
    employee_id: 3,
    skill_id: 1,
    proficiency: 0.88,
    evidence_sources: ["resume"],
  },
  {
    employee_id: 3,
    skill_id: 2,
    proficiency: 0.87,
    evidence_sources: ["resume"],
  },
  {
    employee_id: 3,
    skill_id: 8,
    proficiency: 0.85,
    evidence_sources: ["resume", "review"],
  },
  {
    employee_id: 3,
    skill_id: 9,
    proficiency: 0.93,
    evidence_sources: ["video", "review"],
  },
  {
    employee_id: 3,
    skill_id: 10,
    proficiency: 0.9,
    evidence_sources: ["video", "review"],
  },

  // Diana - ML Engineer
  {
    employee_id: 4,
    skill_id: 1,
    proficiency: 0.94,
    evidence_sources: ["resume", "github"],
  },
  {
    employee_id: 4,
    skill_id: 5,
    proficiency: 0.92,
    evidence_sources: ["resume", "video"],
  },
  {
    employee_id: 4,
    skill_id: 14,
    proficiency: 0.89,
    evidence_sources: ["resume", "github"],
  },
  {
    employee_id: 4,
    skill_id: 7,
    proficiency: 0.82,
    evidence_sources: ["resume"],
  },

  // Ethan - UI/UX Designer
  {
    employee_id: 5,
    skill_id: 13,
    proficiency: 0.95,
    evidence_sources: ["resume", "portfolio"],
  },
  {
    employee_id: 5,
    skill_id: 3,
    proficiency: 0.75,
    evidence_sources: ["resume"],
  },
  {
    employee_id: 5,
    skill_id: 10,
    proficiency: 0.88,
    evidence_sources: ["video", "review"],
  },
];

const departments = [
  { id: 1, name: "Engineering", employee_count: 3 },
  { id: 2, name: "Data Science", employee_count: 1 },
  { id: 3, name: "Design", employee_count: 1 },
];

// Mock ontology
const ontology = {
  version: "1.0.0",
  categories: [
    {
      name: "Programming Language",
      skills: ["Python", "JavaScript", "TypeScript", "Java", "C++"],
    },
    {
      name: "Framework",
      skills: ["React", "Node.js", "Django", "FastAPI", "Next.js"],
    },
    {
      name: "Domain",
      skills: [
        "Machine Learning",
        "Data Science",
        "Web Development",
        "Mobile Development",
      ],
    },
  ],
};

// Mock uploaded files storage
const uploadedFiles: any[] = [];

// Mock document content storage for RAG queries
const documentStore: Map<string, string> = new Map();

// Pre-populate with demo documents
documentStore.set("project_phoenix_brief.txt", `
Project Phoenix - Critical Initiative Brief

OVERVIEW:
Project Phoenix is a mission-critical initiative to rebuild our customer-facing API platform with modern, scalable architecture. Timeline: 6 months. High visibility with executive leadership.

REQUIRED SKILLS:
- Python (primary language, 5+ years experience)
- FastAPI or similar async framework
- API design and RESTful principles
- Database optimization (PostgreSQL)
- Leadership and team coordination (3+ direct reports)
- Experience with high-traffic systems (10,000+ requests/second)
- Low-latency system design

TEAM COMPOSITION NEEDED:
- 1 Project Lead (senior level, proven track record)
- 1 Tech Lead (mentorship focus)
- 2-3 Backend Engineers
- 1 Frontend Engineer (API testing tools)

SUCCESS CRITERIA:
- Complete API migration with zero downtime
- Achieve 99.9% uptime SLA
- Reduce average response time by 40%
- Comprehensive API documentation
`);

documentStore.set("alice_resume.docx", `
ALICE CHEN
Senior Software Engineer
alice.chen@techcorp.com | LinkedIn: /in/alicechen | GitHub: @alicechen

SUMMARY
Senior software engineer with 7+ years building high-performance APIs and distributed systems. Proven track record leading technical teams and delivering mission-critical infrastructure. Expertise in Python, FastAPI, and low-latency system design.

EXPERIENCE

Senior Software Engineer | TechCorp | March 2020 - Present
• Led development of low-latency trading API using Python and FastAPI
• Managed team of 6 engineers across 3 major product releases
• Built APIs handling 15,000+ requests/second with 99.95% uptime
• Reduced API response time by 60% through caching optimization and query tuning
• Architected microservices infrastructure serving 2M+ daily active users
• Implemented PostgreSQL query optimizations (40% performance improvement)

Software Engineer | StartupCo | June 2018 - March 2020
• Built RESTful APIs serving 1M+ daily active users
• Mentored 3 junior developers to mid-level positions
• Designed and implemented real-time data processing pipeline
• Led migration from monolithic architecture to microservices

Junior Developer | DevShop | Jan 2017 - May 2018
• Developed backend services in Python/Django
• Contributed to API design and documentation

LEADERSHIP & MANAGEMENT
• Direct management of 6 engineers (2020-Present)
• Led cross-functional initiatives between Engineering, Product, and Design teams
• Mentored 5+ junior engineers throughout career
• Coordinated technical planning for 3 major product launches
• Built team culture focused on documentation and knowledge sharing

TECHNICAL SKILLS
Languages: Python (Expert), JavaScript (Advanced), TypeScript (Intermediate), SQL
Frameworks: FastAPI, Django, Flask, React
Databases: PostgreSQL, Redis, MongoDB
Tools: Docker, Kubernetes, AWS, Git, CI/CD
Specialties: API Design, Low-latency Systems, Database Optimization, Microservices

EDUCATION
B.S. Computer Science | Stanford University | 2016
`);

documentStore.set("bob_review.pdf", `
PERFORMANCE REVIEW - CONFIDENTIAL
Employee: Bob Martinez
Position: Full Stack Developer
Review Period: January 2024 - December 2024
Reviewer: Sarah Johnson, Engineering Manager
Date: December 15, 2024

OVERALL RATING: Exceeds Expectations (4.5/5.0)

TECHNICAL PERFORMANCE:
Bob has demonstrated consistently strong technical capabilities throughout the review period. His JavaScript and React work is of exceptional quality - clean, maintainable, and well-tested. He completed the customer dashboard redesign 2 weeks ahead of schedule and under budget.

STANDOUT QUALITIES:
What truly distinguishes Bob from his peers is something that doesn't appear in his job description: his extraordinary documentation skills. Bob doesn't just write code; he documents everything with meticulous care. Every API endpoint he creates includes comprehensive examples, error cases, and integration guides. Every React component has clear usage documentation with props explained and edge cases covered.

This year, Bob took the initiative to create our entire team's onboarding documentation - a 40-page guide that reduced new hire ramp-up time from 3 weeks to 1 week. When asked why he invests so much time in documentation, Bob said: "Good docs are how you scale a team. They're a force multiplier."

IMPLICIT LEADERSHIP:
While Bob is not formally in a leadership role, his impact extends far beyond his individual contributions. Through his documentation work, he exhibits what I call "silent leadership" - making the entire team more effective without direct authority. Three junior developers specifically cited Bob's documentation as the reason they could contribute to complex features independently.

Bob has also demonstrated patient mentoring skills. He volunteers for code review duty and provides thoughtful, educational feedback. His reviews don't just catch bugs; they teach principles.

COLLABORATION & TEAMWORK:
Bob excels at cross-functional collaboration. Product managers specifically request to work with him because of his clear communication and proactive problem-solving. During the Q3 incident, Bob stayed late to help debug an issue outside his area of responsibility, demonstrating strong team commitment.

AREAS FOR DEVELOPMENT:
Bob could benefit from being more visible in high-stakes meetings. His technical skills and implicit leadership qualities suggest he's ready for more formal leadership responsibilities, but he needs to advocate for himself more assertively.

He sometimes over-engineers solutions, seeking perfection when "good enough" would suffice. This perfectionism, while producing high-quality work, occasionally impacts velocity.

PYTHON SKILLS NOTE:
While Bob's primary work is in JavaScript/TypeScript, he has quietly developed strong Python skills this year. He contributed to our data pipeline projects and picked up Python/FastAPI quickly - his code quality was indistinguishable from our Python specialists' work within weeks.

RECOMMENDATIONS:
• Consider Bob for technical leadership track (Tech Lead or Engineering Manager)
• Assign him to projects requiring strong API design and documentation
• Provide opportunities for Bob to practice public speaking/presentation skills
• Leverage his mentoring abilities more formally in our junior developer program

UNTAPPED POTENTIAL:
Bob has significant untapped leadership potential. His combination of technical excellence, documentation skills, patient teaching style, and quiet influence suggests he could excel as a Tech Lead or Project Lead, particularly on projects requiring strong communication and knowledge transfer.

Next Level Skills Demonstrated: API Design, Technical Documentation, Mentorship, Cross-functional Collaboration

Recommended for: Promotion to Senior Full Stack Developer, Leadership Development Program
`);

// Artificial delay helper
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// CORS headers
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

const server = serve({
  port: 8001,
  async fetch(req) {
    const url = new URL(req.url);
    const path = url.pathname;
    const method = req.method;

    // Handle CORS preflight
    if (method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    console.log(`${method} ${path}`);

    try {
      // Add artificial delay (200-500ms)
      await delay(Math.random() * 300 + 200);

      // Root endpoint
      if (path === "/" && method === "GET") {
        return Response.json(
          {
            message: "SkillSense API - Mock Backend",
            version: "1.0.0",
            status: "operational",
          },
          { headers: corsHeaders }
        );
      }

      // Health check
      if (path === "/health" && method === "GET") {
        return Response.json(
          { status: "healthy", timestamp: new Date().toISOString() },
          { headers: corsHeaders }
        );
      }

      // Natural language query
      if (path === "/query" && method === "POST") {
        const body = await req.json();
        const query = body.query?.toLowerCase() || "";

        await delay(Math.random() * 500 + 300); // Extra delay for AI processing

        let answer = "";
        let sql_query = "";
        let results: any[] = [];
        let query_type = "HYBRID"; // Default

        // Demo Scenario 1: Project Phoenix Leadership
        if (
          query.includes("project phoenix") ||
          (query.includes("best candidate") && query.includes("lead"))
        ) {
          query_type = "HYBRID";
          sql_query =
            "SELECT e.*, AVG(es.proficiency) as avg_proficiency FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE s.name IN ('Python', 'API Design', 'Leadership') GROUP BY e.id HAVING avg_proficiency > 0.85 ORDER BY avg_proficiency DESC";
          results = [
            {
              id: 1,
              name: "Alice Chen",
              department: "Engineering",
              position: "Senior Software Engineer",
              confidence_score: 0.92,
              avg_proficiency: 0.92,
              match_score: 0.95,
              key_skills: [
                "Python (95%)",
                "API Design (92%)",
                "Leadership (85%)",
              ],
            },
            {
              id: 3,
              name: "Carlos Rodriguez",
              department: "Engineering",
              position: "Tech Lead",
              confidence_score: 0.88,
              avg_proficiency: 0.89,
              match_score: 0.88,
              key_skills: [
                "Leadership (93%)",
                "Python (88%)",
                "Communication (90%)",
              ],
            },
          ];
          answer =
            "Based on Project Phoenix requirements, I recommend 2 strong candidates:\n\n**1. Alice Chen (Senior Software Engineer)** - 95% match\n- Python proficiency: 95% (proven in high-traffic API development)\n- API Design: 92% (built trading APIs handling 15k+ requests/second)\n- Leadership: 85% (managed team of 6 engineers)\n- Evidence: Resume (Trading API project), Video interview (communication), Performance data\n- Confidence: 92%\n\n**2. Carlos Rodriguez (Tech Lead)** - 88% match\n- Leadership: 93% (peer-validated mentorship, team cohesion builder)\n- Python: 88% (solid technical foundation)\n- Communication: 90% (cross-functional coordination)\n- Evidence: Peer feedback (360 reviews), Past collaboration with Alice\n- Confidence: 88%\n\n**Recommendation:** Alice is the strongest technical fit with direct experience in the required tech stack. Carlos excels in team leadership and would complement Alice well as Tech Lead.";
        }

        // Demo Scenario 2: Alice's Resume Evidence
        else if (
          query.includes("alice") &&
          (query.includes("resume") || query.includes("experience")) &&
          (query.includes("python") || query.includes("leadership"))
        ) {
          query_type = "RAG";
          results = [
            {
              document: "alice_resume.docx",
              section: "Work Experience",
              evidence:
                "Senior Software Engineer, TechCorp (2020-Present): Led development of low-latency trading APIs using Python and FastAPI, handling 15,000+ requests/second with 99.95% uptime.",
              confidence: 0.95,
            },
            {
              document: "alice_resume.docx",
              section: "Leadership",
              evidence:
                "Managed team of 6 engineers across 3 major product releases. Mentored 3 junior developers to mid-level positions. Cross-functional coordination with Product and Design teams.",
              confidence: 0.92,
            },
          ];
          answer =
            "Yes, Alice's resume demonstrates strong experience in both areas:\n\n**Python Experience:**\n- 7+ years of professional Python development\n- Built high-performance trading APIs using Python and FastAPI\n- Handled 15,000+ requests/second with 99.95% uptime\n- Reduced API response time by 60% through optimization\n- Evidence Source: Resume, Section: Work Experience\n\n**Leadership Experience:**\n- Led team of 6 engineers on critical infrastructure projects\n- Managed 3 major product releases\n- Mentored 3 junior developers to mid-level positions\n- Coordinated cross-functional initiatives between Engineering and Product\n- Evidence Source: Resume, Section: Leadership & Management\n\n**Confidence Level: High (92%)** based on detailed, verifiable claims with specific metrics.";
        }

        // Demo Scenario 3: Alice vs Bob Comparison
        else if (
          (query.includes("compare") ||
            query.includes("versus") ||
            query.includes("vs")) &&
          (query.includes("alice") || query.includes("bob"))
        ) {
          query_type = "ADVANCED_HYBRID";
          await delay(Math.random() * 500 + 300); // Extra delay for multi-document analysis
          sql_query =
            "SELECT e.name, s.name as skill, es.proficiency FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE e.id IN (1, 2)";
          results = [
            {
              candidate: "Alice Chen",
              primary_skills: [
                "Python (95%)",
                "API Design (92%)",
                "Leadership (85%)",
              ],
              match_score: 0.95,
              documents: ["alice_resume.docx", "video_interview.mp4"],
            },
            {
              candidate: "Bob Martinez",
              primary_skills: [
                "JavaScript (92%)",
                "React (88%)",
                "TypeScript (90%)",
              ],
              match_score: 0.7,
              documents: ["bob_performance_review.pdf"],
              hidden_skills: ["Documentation Excellence (implicit)"],
            },
          ];
          answer =
            "**Comparative Analysis: Alice Chen vs Bob Martinez for Project Phoenix**\n\n**Technical Skills:**\n- **Alice:** Strong Python (95%), FastAPI (92%), API Design (93%) - Perfect match for backend requirements\n- **Bob:** Strong JavaScript (92%), React (88%), Node.js (85%) - Better suited for frontend work\n\n**Leadership & Collaboration:**\n- **Alice:** Proven team leadership (6 direct reports), cross-functional coordination, 3 major releases\n- **Bob:** Performance review highlights 'exceptional documentation skills' and 'patient mentoring' - implicit leadership qualities\n\n**Project Phoenix Fit:**\n- **Alice:** 95% match - Direct experience with required tech stack and proven project leadership\n- **Bob:** 70% match - Strong engineer but tech stack mismatch; could contribute to frontend components or API documentation\n\n**Hidden Insight:** 💎 Bob's performance review reveals he 'documented every API endpoint with comprehensive examples' - an implicit skill in API design that doesn't appear on his resume. His manager notes: \"This silent leadership through documentation has made our entire team more effective.\"\n\n**Recommendation:** Alice is the clear choice for Project Lead. Consider Bob for:\n1. Frontend integration work (React/TypeScript strength)\n2. API documentation lead (hidden talent)\n3. Mentorship resource (patient teaching style)\n\n**Evidence Sources:**\n- Alice: Resume (TechCorp experience), Video interview, Performance data\n- Bob: Performance review (2024 annual), GitHub contributions";
        }

        // Demo Scenario 4: Junior React Developers
        else if (
          (query.includes("junior") ||
            query.includes("less than") ||
            query.includes("< 2 years")) &&
          query.includes("react")
        ) {
          query_type = "SQL";
          sql_query =
            "SELECT e.*, es.proficiency, s.name as skill FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE s.name = 'React' AND DATEDIFF(CURRENT_DATE, e.hire_date) < 730";
          results = [
            {
              id: 5,
              name: "Ethan Williams",
              department: "Design",
              position: "UI/UX Designer",
              hire_date: "2022-02-14",
              proficiency: 0.75,
              years_experience: 2.7,
            },
          ];
          answer =
            "Found 1 engineer matching your criteria:\n\n**Ethan Williams** - UI/UX Designer (hired Feb 2022, ~2.7 years experience)\n- React proficiency: 75%\n- Also skilled in: Figma (95%), Communication (88%)\n- **Note:** While listed as Designer, has coding capabilities and fresh perspective\n\n**Insight:** Ethan brings unique value:\n- Design background provides UX perspective for frontend work\n- Recent hire means up-to-date with modern React patterns\n- Growth trajectory shows rapid skill acquisition\n\nWould you like me to search for additional frontend developers with React experience (relaxing the experience constraint)?";
        }

        // Demo Scenario 5: Final Team Proposal
        else if (
          query.includes("team proposal") ||
          query.includes("team recommendation") ||
          (query.includes("final") && query.includes("team"))
        ) {
          query_type = "ADVANCED_HYBRID";
          await delay(Math.random() * 700 + 400); // Longest delay for comprehensive analysis
          results = [
            {
              role: "Project Lead",
              candidate: "Alice Chen",
              match_score: 0.95,
            },
            {
              role: "Tech Lead",
              candidate: "Carlos Rodriguez",
              match_score: 0.88,
            },
            {
              role: "Frontend Engineer",
              candidate: "Ethan Williams",
              match_score: 0.75,
            },
          ];
          answer =
            "**Project Phoenix Team Proposal**\n\n**Project Lead: Alice Chen** ⭐\n- **Rationale:** 95% technical match, proven leadership with 6 direct reports, experience with exact tech stack (Python/FastAPI), high confidence score (92%)\n- **Evidence:** Resume (Trading API leadership at TechCorp), Video interview (clear communication), Performance data (consistent high performer)\n- **Key Strengths:** Low-latency systems, 15k+ req/sec experience, 99.95% uptime track record\n\n**Tech Lead: Carlos Rodriguez** 🎯\n- **Rationale:** Exceptional mentorship (93% leadership proficiency), strong Python skills (88%), peer reviews highlight 'builds team cohesion'\n- **Evidence:** Peer feedback (360 reviews), Past collaboration data (worked with Alice on 2 previous projects), Communication assessment (video analysis)\n- **Key Strengths:** Team building, cross-training, conflict resolution\n\n**Frontend Engineer: Ethan Williams** 🚀\n- **Rationale:** React proficiency (75%), design background provides UX perspective, growth potential\n- **Evidence:** Recent hire (fresh perspective), Design portfolio (user-centric thinking), Documented learning agility\n- **Key Strengths:** UI/UX expertise, modern React patterns, rapid skill acquisition\n\n**Team Dynamics Assessment:**\n- ✅ Alice + Carlos: Proven collaboration (2 past projects), complementary skills\n- ✅ Skill coverage: Backend (Alice), Leadership (Carlos), Frontend/UX (Ethan)\n- ⚠️ Risk: Junior frontend resource - recommend senior frontend support or pair with Bob for documentation\n\n**Recommended Addition:**\n- **Bob Martinez** (Part-time) - API Documentation lead\n- Leverages his hidden documentation talent\n- Supports Ethan in frontend integration\n\n**Project Success Probability: 88%**\n\nThis team covers all Project Phoenix requirements with evidence-backed skill validation, proven team chemistry, and balanced experience levels.";
        }

        // Generic queries
        else if (query.includes("python") && query.includes("expert")) {
          query_type = "SQL";
          sql_query =
            "SELECT e.*, es.proficiency FROM employees e JOIN employee_skills es ON e.id = es.employee_id JOIN skills s ON es.skill_id = s.id WHERE s.name = 'Python' AND es.proficiency > 0.90";
          results = [
            { ...employees[0], proficiency: 0.95 },
            { ...employees[3], proficiency: 0.94 },
          ];
          answer =
            "I found 2 Python experts with proficiency above 90%: Alice Chen (95%) and Diana Park (94%).";
        } else if (query.includes("engineer")) {
          query_type = "SQL";
          sql_query =
            "SELECT * FROM employees WHERE department = 'Engineering'";
          results = employees.filter((e) => e.department === "Engineering");
          answer = `Found ${results.length} engineers in the Engineering department.`;
        } else if (query.includes("skill") && query.includes("distribution")) {
          query_type = "SQL";
          sql_query =
            "SELECT s.name, COUNT(*) as count FROM skills s JOIN employee_skills es ON s.id = es.skill_id GROUP BY s.name ORDER BY count DESC";
          results = [
            { name: "Python", count: 3 },
            { name: "JavaScript", count: 3 },
            { name: "React", count: 2 },
          ];
          answer = "Here's the skills distribution across all employees.";
        } else if (query.includes("alice")) {
          query_type = "SQL";
          sql_query = "SELECT * FROM employees WHERE name LIKE '%Alice%'";
          results = [employees[0]];
          answer =
            "Alice Chen is a Senior Software Engineer with high expertise in Python, API Design, and Leadership.";
        } else {
          query_type = "GENERAL";
          answer =
            "I can help you query the talent database. Try asking about:\n- Specific skills (e.g., 'Python experts')\n- Project requirements (e.g., 'best candidates for Project Phoenix')\n- Employee comparisons (e.g., 'compare Alice and Bob')\n- Team composition (e.g., 'junior React developers')";
          results = employees.slice(0, 3);
        }

        return Response.json(
          {
            success: true,
            answer,
            sql_query,
            results,
            query_type,
            processing_time_ms: Math.round(Math.random() * 500 + 300),
          },
          { headers: corsHeaders }
        );
      }

      // Get all employees
      if (path === "/employees" && method === "GET") {
        return Response.json(
          {
            success: true,
            count: employees.length,
            data: employees,
          },
          { headers: corsHeaders }
        );
      }

      // Get specific employee
      if (
        path.startsWith("/employees/") &&
        !path.includes("/skills") &&
        method === "GET"
      ) {
        const id = parseInt(path.split("/")[2]);
        const employee = employees.find((e) => e.id === id);

        if (!employee) {
          return Response.json(
            { success: false, error: "Employee not found" },
            { status: 404, headers: corsHeaders }
          );
        }

        return Response.json(
          { success: true, data: employee },
          { headers: corsHeaders }
        );
      }

      // Get employee skills
      if (path.match(/\/employees\/\d+\/skills/) && method === "GET") {
        const id = parseInt(path.split("/")[2]);
        const employee = employees.find((e) => e.id === id);

        if (!employee) {
          return Response.json(
            { success: false, error: "Employee not found" },
            { status: 404, headers: corsHeaders }
          );
        }

        const empSkills = employeeSkills
          .filter((es) => es.employee_id === id)
          .map((es) => {
            const skill = skills.find((s) => s.id === es.skill_id);
            return {
              ...skill,
              proficiency: es.proficiency,
              evidence_sources: es.evidence_sources,
            };
          });

        return Response.json(
          {
            success: true,
            employee: employee.name,
            count: empSkills.length,
            data: empSkills,
          },
          { headers: corsHeaders }
        );
      }

      // Get all skills
      if (path === "/skills" && method === "GET") {
        return Response.json(
          {
            success: true,
            count: skills.length,
            data: skills,
          },
          { headers: corsHeaders }
        );
      }

      // Get departments
      if (path === "/departments" && method === "GET") {
        return Response.json(
          {
            success: true,
            count: departments.length,
            data: departments,
          },
          { headers: corsHeaders }
        );
      }

      // Analytics - Skills distribution
      if (path === "/analytics/skills-distribution" && method === "GET") {
        const distribution = skills
          .map((skill) => {
            const count = employeeSkills.filter(
              (es) => es.skill_id === skill.id
            ).length;
            const avgProficiency =
              employeeSkills
                .filter((es) => es.skill_id === skill.id)
                .reduce((sum, es) => sum + es.proficiency, 0) / (count || 1);

            return {
              skill_name: skill.name,
              category: skill.category,
              employee_count: count,
              avg_proficiency: Math.round(avgProficiency * 100) / 100,
            };
          })
          .filter((s) => s.employee_count > 0);

        return Response.json(
          {
            success: true,
            count: distribution.length,
            data: distribution,
          },
          { headers: corsHeaders }
        );
      }

      // Analytics - Department skills
      if (path === "/analytics/department-skills" && method === "GET") {
        const deptSkills = departments.map((dept) => {
          const deptEmployees = employees.filter(
            (e) => e.department === dept.name
          );
          const deptEmployeeIds = deptEmployees.map((e) => e.id);
          const deptEmpSkills = employeeSkills.filter((es) =>
            deptEmployeeIds.includes(es.employee_id)
          );

          const skillCounts: any = {};
          deptEmpSkills.forEach((es) => {
            const skill = skills.find((s) => s.id === es.skill_id);
            if (skill) {
              if (!skillCounts[skill.name]) {
                skillCounts[skill.name] = { count: 0, total_proficiency: 0 };
              }
              skillCounts[skill.name].count++;
              skillCounts[skill.name].total_proficiency += es.proficiency;
            }
          });

          const topSkills = Object.entries(skillCounts)
            .map(([name, data]: [string, any]) => ({
              skill: name,
              count: data.count,
              avg_proficiency:
                Math.round((data.total_proficiency / data.count) * 100) / 100,
            }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 5);

          return {
            department: dept.name,
            employee_count: dept.employee_count,
            top_skills: topSkills,
          };
        });

        return Response.json(
          {
            success: true,
            data: deptSkills,
          },
          { headers: corsHeaders }
        );
      }

      // Upload resume
      if (path === "/upload/resume" && method === "POST") {
        await delay(Math.random() * 1000 + 500); // Longer delay for file processing

        const formData = await req.formData();
        const file = formData.get("file");
        const employeeId = url.searchParams.get("employee_id");

        if (!file) {
          return Response.json(
            { success: false, error: "No file provided" },
            { status: 400, headers: corsHeaders }
          );
        }

        const filename = (file as File).name;
        
        // Check if it's a demo file and store appropriate content
        let extractedSkills: any[] = [];
        let documentType = "resume";
        
        if (filename.includes("alice") || filename.includes("Alice")) {
          // Store Alice's resume content
          if (!documentStore.has(filename)) {
            documentStore.set(filename, documentStore.get("alice_resume.docx") || "");
          }
          extractedSkills = [
            { name: "Python", proficiency: 0.95, confidence: 0.90 },
            { name: "FastAPI", proficiency: 0.92, confidence: 0.88 },
            { name: "API Design", proficiency: 0.93, confidence: 0.85 },
            { name: "Leadership", proficiency: 0.87, confidence: 0.82 },
            { name: "PostgreSQL", proficiency: 0.88, confidence: 0.80 },
          ];
        } else if (filename.includes("bob") || filename.includes("Bob") || filename.includes("review")) {
          // Store Bob's performance review
          documentType = "performance_review";
          if (!documentStore.has(filename)) {
            documentStore.set(filename, documentStore.get("bob_review.pdf") || "");
          }
          extractedSkills = [
            { name: "JavaScript", proficiency: 0.92, confidence: 0.88 },
            { name: "React", proficiency: 0.88, confidence: 0.85 },
            { name: "TypeScript", proficiency: 0.90, confidence: 0.86 },
            { name: "Documentation", proficiency: 0.95, confidence: 0.90 },
            { name: "Mentorship", proficiency: 0.85, confidence: 0.75 },
            { name: "Python", proficiency: 0.78, confidence: 0.70 },
          ];
        } else if (filename.includes("phoenix") || filename.includes("Phoenix") || filename.includes("brief")) {
          // Store project requirements
          documentType = "project_brief";
          if (!documentStore.has(filename)) {
            documentStore.set(filename, documentStore.get("project_phoenix_brief.txt") || "");
          }
          extractedSkills = [
            { name: "Python", proficiency: 0.95, confidence: 0.90 },
            { name: "FastAPI", proficiency: 0.90, confidence: 0.85 },
            { name: "API Design", proficiency: 0.92, confidence: 0.88 },
            { name: "Leadership", proficiency: 0.88, confidence: 0.80 },
            { name: "PostgreSQL", proficiency: 0.85, confidence: 0.78 },
          ];
        } else {
          // Generic document
          extractedSkills = [
            { name: "Python", proficiency: 0.90, confidence: 0.85 },
            { name: "Machine Learning", proficiency: 0.85, confidence: 0.80 },
            { name: "API Design", proficiency: 0.88, confidence: 0.82 },
          ];
        }

        const upload = {
          id: uploadedFiles.length + 1,
          type: documentType,
          filename,
          employee_id: employeeId ? parseInt(employeeId) : null,
          uploaded_at: new Date().toISOString(),
          status: "processed",
          extracted_skills: extractedSkills,
          document_stored: true,
        };

        uploadedFiles.push(upload);

        console.log(`📄 Uploaded and indexed: ${filename} (${extractedSkills.length} skills extracted)`);

        return Response.json(
          {
            success: true,
            message: `${documentType === "project_brief" ? "Project brief" : documentType === "performance_review" ? "Performance review" : "Resume"} processed successfully`,
            data: upload,
          },
          { headers: corsHeaders }
        );
      }

      // Upload video
      if (path === "/upload/video" && method === "POST") {
        await delay(Math.random() * 2000 + 1000); // Even longer delay for video processing

        const formData = await req.formData();
        const file = formData.get("file");
        const employeeId = url.searchParams.get("employee_id");

        if (!file) {
          return Response.json(
            { success: false, error: "No file provided" },
            { status: 400, headers: corsHeaders }
          );
        }

        // Mock video analysis
        const analysis = {
          transcript:
            "Sample interview transcript discussing technical projects and leadership experience...",
          confidence_scores: {
            technical: 0.87,
            communication: 0.92,
            leadership: 0.85,
          },
          extracted_skills: [
            { name: "Communication", proficiency: 0.92, confidence: 0.88 },
            { name: "Leadership", proficiency: 0.85, confidence: 0.82 },
          ],
          sentiment: "positive",
        };

        const upload = {
          id: uploadedFiles.length + 1,
          type: "video",
          filename: (file as File).name,
          employee_id: employeeId ? parseInt(employeeId) : null,
          uploaded_at: new Date().toISOString(),
          status: "processed",
          analysis,
        };

        uploadedFiles.push(upload);

        return Response.json(
          {
            success: true,
            message: "Video processed successfully",
            data: upload,
          },
          { headers: corsHeaders }
        );
      }

      // Get uploaded documents
      if (path === "/uploads" && method === "GET") {
        return Response.json(
          {
            success: true,
            count: uploadedFiles.length,
            data: uploadedFiles,
          },
          { headers: corsHeaders }
        );
      }

      // Submit text requirements (alternative to file upload)
      if (path === "/requirements" && method === "POST") {
        await delay(Math.random() * 500 + 300);
        
        const body = await req.json();
        const text = (body as any).text || (body as any).requirements || "";
        const title = (body as any).title || "Project Requirements";
        
        if (!text) {
          return Response.json(
            { success: false, error: "No text provided" },
            { status: 400, headers: corsHeaders }
          );
        }

        // Store the text as a document
        const filename = `${title.toLowerCase().replace(/\s+/g, "_")}.txt`;
        documentStore.set(filename, text);

        // Extract skills from text (simple keyword matching)
        const skillKeywords = ["python", "javascript", "react", "leadership", "api", "fastapi", "postgresql", "docker", "aws"];
        const extractedSkills = skillKeywords
          .filter(skill => text.toLowerCase().includes(skill))
          .map(skill => ({
            name: skill.charAt(0).toUpperCase() + skill.slice(1),
            proficiency: 0.90,
            confidence: 0.85
          }));

        const upload = {
          id: uploadedFiles.length + 1,
          type: "text_requirements",
          filename,
          uploaded_at: new Date().toISOString(),
          status: "processed",
          extracted_skills: extractedSkills,
          document_stored: true,
        };

        uploadedFiles.push(upload);

        console.log(`📝 Text requirements stored: ${filename} (${extractedSkills.length} skills extracted)`);

        return Response.json(
          {
            success: true,
            message: "Requirements processed successfully",
            data: upload,
          },
          { headers: corsHeaders }
        );
      }

      // Get ontology
      if (path === "/ontology" && method === "GET") {
        return Response.json(
          {
            success: true,
            data: ontology,
          },
          { headers: corsHeaders }
        );
      }

      // Get database schema
      if (path === "/schema" && method === "GET") {
        const schema = {
          tables: [
            {
              name: "employees",
              columns: [
                "id",
                "name",
                "email",
                "department",
                "position",
                "hire_date",
                "confidence_score",
              ],
            },
            {
              name: "skills",
              columns: ["id", "name", "category"],
            },
            {
              name: "employee_skills",
              columns: [
                "employee_id",
                "skill_id",
                "proficiency",
                "evidence_sources",
              ],
            },
            {
              name: "departments",
              columns: ["id", "name", "employee_count"],
            },
          ],
        };

        return Response.json(
          {
            success: true,
            data: schema,
          },
          { headers: corsHeaders }
        );
      }

      // 404 Not Found
      return Response.json(
        {
          success: false,
          error: "Endpoint not found",
          path,
          method,
        },
        { status: 404, headers: corsHeaders }
      );
    } catch (error: any) {
      console.error("Error:", error);
      return Response.json(
        {
          success: false,
          error: error.message || "Internal server error",
        },
        { status: 500, headers: corsHeaders }
      );
    }
  },
});

console.log(
  `🚀 SkillSense Mock Backend running on http://localhost:${server.port}`
);
console.log(`📊 Endpoints available:`);
console.log(`   GET  /health`);
console.log(`   POST /query               🎯 Main NL query endpoint`);
console.log(`   GET  /employees`);
console.log(`   GET  /employees/:id`);
console.log(`   GET  /employees/:id/skills`);
console.log(`   GET  /skills`);
console.log(`   GET  /departments`);
console.log(`   GET  /analytics/skills-distribution`);
console.log(`   GET  /analytics/department-skills`);
console.log(`   POST /upload/resume       📄 Upload resumes/reviews`);
console.log(`   POST /upload/video        🎥 Upload video interviews`);
console.log(`   POST /requirements        ✍️  Submit text requirements`);
console.log(`   GET  /uploads             📋 List uploaded documents`);
console.log(`   GET  /ontology`);
console.log(`   GET  /schema`);
console.log(``);
console.log(`📚 Pre-loaded demo documents:`);
console.log(`   - project_phoenix_brief.txt`);
console.log(`   - alice_resume.docx`);
console.log(`   - bob_review.pdf`);
console.log(``);
console.log(`🎬 Demo Script Support:`);
console.log(`   ✓ "Who are the best candidates to lead Project Phoenix?"`);
console.log(`   ✓ "Does Alice's resume show experience with Python and leadership?"`);
console.log(`   ✓ "Compare Alice's skills with Bob's skills from his review"`);
console.log(`   ✓ "Show me junior React developers"`);
console.log(`   ✓ "Generate a final team proposal for Project Phoenix"`);
