#!/usr/bin/env python3
"""
SkillSense: AI-Powered Talent Intelligence Platform
Main entry point for the hackathon application.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager
from managers.ontology_manager import OntologyManager
from managers.prompt_manager import PromptManager
from managers.workflow_manager import WorkflowManager

def initialize_system():
    """Initialize all system components."""

    print("🚀 Initializing SkillSense Platform...")

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Initialize managers
    db_manager = DatabaseManager("data/talent_database.db")
    llm_manager = LLMManager()
    ontology_manager = OntologyManager("config/skills_ontology.json")
    prompt_manager = PromptManager()

    print("✅ All managers initialized successfully!")

    return {
        'db_manager': db_manager,
        'llm_manager': llm_manager,
        'ontology_manager': ontology_manager,
        'prompt_manager': prompt_manager
    }

def demo_query_system():
    """Run a demo of the query system."""

    print("\n🎯 Running Demo Queries...")

    managers = initialize_system()

    # Sample queries to showcase capabilities
    demo_queries = [
        "Show me all Python developers",
        "Which department has the most Machine Learning experts?",
        "Find employees with leadership skills",
        "Show the top 5 most common technical skills",
        "Compare skill confidence between Engineering and Data Science departments"
    ]

    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 50)

        # This will be implemented with the actual query processing
        # For now, just showing the structure
        print("Processing query...")
        print("✅ Query processed successfully!")

def setup_environment():
    """Set up the development environment."""

    print("🔧 Setting up development environment...")

    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

    # Initialize database if it doesn't exist
    if not os.path.exists("data/talent_database.db"):
        print("📊 Initializing database...")
        from setup_database import main as setup_db
        setup_db()
    else:
        print("✅ Database already exists")

    print("✅ Environment setup complete!")

def main():
    """Main entry point."""

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                   SkillSense Platform                        ║
    ║            AI-Powered Talent Intelligence                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "setup":
            setup_environment()
        elif command == "demo":
            demo_query_system()
        elif command == "server":
            from api_server import start_server
            start_server()
        else:
            print("Available commands:")
            print("  setup   - Set up the development environment")
            print("  demo    - Run demo queries")
            print("  server  - Start the API server")
    else:
        print("Welcome to SkillSense!")
        print("\nGetting started:")
        print("1. python main.py setup    # Set up environment")
        print("2. python main.py server   # Start API server")
        print("3. python main.py demo     # Run demo queries")
        print("\nOr run: python main.py --help for more options")

if __name__ == "__main__":
    main()