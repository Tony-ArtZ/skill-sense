#!/usr/bin/env python3
"""
Initialize the talent database with sample data for hackathon demo.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

def create_database_schema():
    """Create the talent database schema."""

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    db_path = "data/talent_database.db"
    conn = sqlite3.connect(db_path)

    with open('config/skills_ontology.json', 'r') as f:
        ontology = json.load(f)

    # Create tables based on ontology
    cursor = conn.cursor()

    # Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            role TEXT,
            join_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Skills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT UNIQUE NOT NULL,
            category TEXT,
            normalized_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Employee skills table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            skill_id INTEGER,
            confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
            source_type TEXT CHECK (source_type IN ('resume', 'video', 'linkedin', 'review', 'github')),
            evidence TEXT,
            is_implicit BOOLEAN DEFAULT 0,
            video_timestamp TEXT,
            visual_confidence INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        )
    """)

    # Employee documents table (for RAG)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            document_type TEXT,
            content TEXT,
            file_path TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database schema created successfully!")

def load_sample_data():
    """Load sample hackathon demo data."""

    db_path = "data/talent_database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Sample departments
    departments = [
        ("Engineering", "Software development and technology"),
        ("Data Science", "Data analysis and machine learning"),
        ("Product", "Product management and strategy"),
        ("Design", "UX/UI design and user research"),
        ("Marketing", "Digital marketing and growth")
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO departments (name, description) VALUES (?, ?)",
        departments
    )

    # Sample employees with realistic data
    employees = [
        ("Alice Johnson", "alice@company.com", "Engineering", "Senior Software Engineer", "2023-01-15"),
        ("Bob Smith", "bob@company.com", "Data Science", "Machine Learning Engineer", "2022-06-01"),
        ("Carol Davis", "carol@company.com", "Engineering", "Full Stack Developer", "2023-03-10"),
        ("David Wilson", "david@company.com", "Product", "Senior Product Manager", "2022-11-20"),
        ("Eva Martinez", "eva@company.com", "Design", "UX Designer", "2023-02-28"),
        ("Frank Chen", "frank@company.com", "Engineering", "DevOps Engineer", "2022-09-15"),
        ("Grace Taylor", "grace@company.com", "Data Science", "Data Analyst", "2023-04-05"),
        ("Henry Lee", "henry@company.com", "Marketing", "Growth Marketer", "2022-12-10"),
        ("Isabella Rodriguez", "isabella@company.com", "Engineering", "Backend Developer", "2023-01-20"),
        ("Jack Brown", "jack@company.com", "Product", "Product Owner", "2022-08-30"),
        ("Kate Williams", "kate@company.com", "Design", "Product Designer", "2023-05-15"),
        ("Liam Jones", "liam@company.com", "Data Science", "Data Scientist", "2022-10-25"),
        ("Maria Garcia", "maria@company.com", "Engineering", "Frontend Developer", "2023-03-01"),
        ("Nathan Miller", "nathan@company.com", "Engineering", "Security Engineer", "2022-07-12"),
        ("Olivia Davis", "olivia@company.com", "Marketing", "Content Marketer", "2023-02-14")
    ]

    cursor.executemany(
        """INSERT OR IGNORE INTO employees
           (name, email, department, role, join_date)
           VALUES (?, ?, ?, ?, ?)""",
        employees
    )

    # Comprehensive skills list
    skills = [
        # Technical skills
        ("Python", "technical", "python"),
        ("JavaScript", "technical", "javascript"),
        ("React", "technical", "react"),
        ("Node.js", "technical", "node.js"),
        ("TypeScript", "technical", "typescript"),
        ("Machine Learning", "technical", "machine learning"),
        ("Docker", "technical", "docker"),
        ("Kubernetes", "technical", "kubernetes"),
        ("AWS", "technical", "aws"),
        ("SQL", "technical", "sql"),
        ("Git", "technical", "git"),
        ("Linux", "technical", "linux"),
        ("MongoDB", "technical", "mongodb"),
        ("PostgreSQL", "technical", "postgresql"),
        ("Redis", "technical", "redis"),
        ("GraphQL", "technical", "graphql"),
        ("Vue.js", "technical", "vue.js"),
        ("Angular", "technical", "angular"),
        ("Java", "technical", "java"),
        ("C++", "technical", "c++"),
        ("TensorFlow", "technical", "tensorflow"),
        ("PyTorch", "technical", "pytorch"),
        ("Tableau", "technical", "tableau"),
        ("Power BI", "technical", "power bi"),

        # Soft skills
        ("Leadership", "soft", "leadership"),
        ("Communication", "soft", "communication"),
        ("Teamwork", "soft", "teamwork"),
        ("Problem Solving", "soft", "problem solving"),
        ("Creativity", "soft", "creativity"),
        ("Time Management", "soft", "time management"),
        ("Adaptability", "soft", "adaptability"),
        ("Critical Thinking", "soft", "critical thinking"),
        ("Mentoring", "soft", "mentoring"),
        ("Public Speaking", "soft", "public speaking"),

        # Domain skills
        ("Analytics", "domain", "analytics"),
        ("E-commerce", "domain", "e-commerce"),
        ("Healthcare", "domain", "healthcare"),
        ("Finance", "domain", "finance"),
        ("Fintech", "domain", "fintech"),
        ("SaaS", "domain", "saas"),

        # Business skills
        ("Project Management", "business", "project management"),
        ("Strategic Planning", "business", "strategic planning"),
        ("Negotiation", "business", "negotiation"),
        ("Budget Management", "business", "budget management"),
        ("Agile", "business", "agile"),
        ("Scrum", "business", "scrum")
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO skills (skill_name, category, normalized_name) VALUES (?, ?, ?)",
        skills
    )

    # Generate realistic employee skills with varied confidence and sources
    source_types = ["resume", "video", "linkedin", "review", "github"]

    # Get employee and skill IDs
    cursor.execute("SELECT id, department FROM employees")
    employees_data = cursor.fetchall()

    cursor.execute("SELECT id, normalized_name FROM skills")
    skills_data = cursor.fetchall()

    # Skill assignments based on roles and departments
    skill_assignments = []

    for emp_id, dept in employees_data:
        # Each employee gets 8-15 skills
        num_skills = random.randint(8, 15)
        selected_skills = random.sample(skills_data, num_skills)

        for skill_id, skill_name in selected_skills:
            # Vary confidence based on source and skill relevance
            source = random.choice(source_types)

            if source == "video":
                base_confidence = random.randint(75, 95)
            elif source == "github":
                base_confidence = random.randint(80, 98)
            elif source == "resume":
                base_confidence = random.randint(60, 90)
            else:
                base_confidence = random.randint(50, 85)

            # Some skills are implicit (soft skills often are)
            is_implicit = skill_name in ["leadership", "communication", "teamwork", "creativity"] and random.random() > 0.6

            skill_assignments.append((
                emp_id, skill_id, base_confidence, source,
                f"Demonstrated {skill_name} proficiency in recent projects",
                is_implicit,
                None if source != "video" else f"{random.randint(1,5)}:{random.randint(10,59)}",
                base_confidence + 5 if source == "video" else None
            ))

    cursor.executemany(
        """INSERT INTO employee_skills
           (employee_id, skill_id, confidence, source_type, evidence, is_implicit, video_timestamp, visual_confidence)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        skill_assignments
    )

    # Add some sample documents for RAG
    documents = [
        (1, "resume", "Alice Johnson - Senior Software Engineer with 5 years experience in Python, Django, and React. Led development of microservices architecture serving 1M+ users. AWS certified solutions architect."),
        (2, "video", "Bob Smith discussing his machine learning projects, experience with TensorFlow and PyTorch, and how he improved model accuracy by 40% through feature engineering."),
        (3, "linkedin", "Carol Davis - Full Stack Developer passionate about creating intuitive user experiences. Proficient in JavaScript, Node.js, and modern web frameworks."),
        (4, "review", "David Wilson shows excellent strategic thinking and product vision. Successfully launched 3 products with 200% user growth. Great team leadership skills."),
        (5, "resume", "Eva Martinez - UX Designer with portfolio including mobile apps, web platforms, and enterprise software. Expert in user research, prototyping, and design systems."),
    ]

    cursor.executemany(
        "INSERT INTO employee_documents (employee_id, document_type, content) VALUES (?, ?, ?)",
        documents
    )

    conn.commit()
    conn.close()
    print("✅ Sample data loaded successfully!")
    print(f"📊 Created {len(employees)} employees and {len(skills)} skills")
    print(f"🔗 Generated {len(skill_assignments)} skill associations")

def main():
    """Initialize the complete database."""
    print("🚀 Setting up SkillSense database...")

    create_database_schema()
    load_sample_data()

    print("✨ Database setup complete! Ready to start building.")
    print("📁 Database location: data/talent_database.db")
    print("🎯 You can now run the application!")

if __name__ == "__main__":
    main()