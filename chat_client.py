#!/usr/bin/env python3
"""
Simple command-line client for testing SkillSense NL-to-SQL queries.
Based on the fused_chat chat_client.py approach.
"""

import json
import requests
import sys
import os

# --- Configuration ---
BACKEND_URL = "http://localhost:8001/query"
ONTOLOGY_FILE = "config/skills_ontology.json"
DB_CONNECTION_STRING = "sqlite:///data/talent_database.db"

def test_connection():
    """Test if the API server is running."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_document(file_path, employee_id=1):
    """Upload a document to the RAG system."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            data = {'employee_id': employee_id}

            response = requests.post(
                "http://localhost:8001/upload/document",
                files=files,
                data=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Document uploaded successfully!")
                print(f"📄 Chunks processed: {result.get('chunks_processed', 0)}")
                print(f"🆔 Document ID: {result.get('doc_id')}")
            else:
                print(f"❌ Upload failed: {response.text}")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")

def show_system_stats():
    """Show system statistics."""
    try:
        # Get RAG stats
        rag_response = requests.get("http://localhost:8001/rag/stats", timeout=80)
        if rag_response.status_code == 200:
            rag_stats = rag_response.json().get('data', {})
            print("📚 RAG System Statistics:")
            print(f"  📄 Total document chunks: {rag_stats.get('total_chunks', 0)}")
            print(f"  📁 Total documents: {rag_stats.get('total_documents', 0)}")
            print(f"  🔍 FAISS index size: {rag_stats.get('index_size', 0)}")
            print()

        # Get hybrid stats
        hybrid_response = requests.get("http://localhost:8001/hybrid/stats", timeout=100)
        if hybrid_response.status_code == 200:
            hybrid_stats = hybrid_response.json().get('data', {})
            print("🔀 Hybrid System Statistics:")
            query_routing = hybrid_stats.get('query_routing', {})
            print(f"  🧠 Supported query types: {', '.join(query_routing.get('supported_types', []))}")
            print(f"  📊 Routing method: {query_routing.get('routing_method', 'Unknown')}")
            print()

    except Exception as e:
        print(f"❌ Stats error: {str(e)}")

def main():
    """
    Hybrid command-line client for interacting with SkillSense RAG + NL-to-SQL.
    """
    print("--- SkillSense Hybrid Chat Client ---")
    print("🧠 Ask questions using BOTH structured data AND uploaded documents!")
    print()
    print("📊 NL-to-SQL Examples (Database Queries):")
    print("  - Show me all Python developers")
    print("  - What are the top 5 technical skills?")
    print("  - Which department has the most employees?")
    print("  - Find people with leadership skills")
    print()
    print("📚 RAG Examples (Document Search):")
    print("  - What leadership experience does Alice have?")
    print("  - What projects has Bob worked on?")
    print("  - Show me examples of Python experience")
    print("  - What does Alice's resume say about machine learning?")
    print()
    print("🔀 Hybrid Examples (Both Systems):")
    print("  - Tell me about Alice's skills and experience")
    print("  - What projects has Alice demonstrated in her resume?")
    print("  - Compare Alice's stated skills with her documented experience")
    print()
    print("📤 Commands:")
    print("  upload <file_path>     - Upload document for RAG search")
    print("  stats                  - Show system statistics")
    print("  examples               - Show more sample queries")
    print("  help                   - Show this help")
    print("  exit/quit              - End conversation")
    print("=" * 60)

    # Test connection first
    if not test_connection():
        print("❌ Error: Cannot connect to the API server.")
        print("Please make sure the server is running:")
        print("  python api_server.py")
        return

    print("✅ Connected to SkillSense API successfully!")
    print()

    while True:
        try:
            # Get user input
            query = input("You: ").strip()

            # Check for exit commands
            if query.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break

            # Check for help
            if query.lower() == "help":
                print("\n📖 Available Commands:")
                print("  📤 upload <file_path>     - Upload document for RAG search")
                print("  📊 stats                  - Show system statistics")
                print("  📝 examples               - Show sample queries")
                print("  ❓ help                   - Show this help")
                print("  🚪 exit/quit              - End conversation")
                print("  <any question>         - Ask about talent data or documents")
                print()
                continue

            # Check for upload command
            if query.lower().startswith("upload "):
                file_path = query[7:].strip()
                upload_document(file_path)
                print()
                continue

            # Check for stats command
            if query.lower() == "stats":
                show_system_stats()
                continue

            # Check for examples
            if query.lower() == "examples":
                print("\n📊 NL-to-SQL Examples (Database Queries):")
                print("  1. Show me all employees in Engineering")
                print("  2. What are the most common technical skills?")
                print("  3. Find employees with Python skills")
                print("  4. Which department has the highest skill confidence?")
                print("  5. Show me employees with leadership potential")
                print()
                print("📚 RAG Examples (Document Search):")
                print("  6. What leadership experience does Alice have?")
                print("  7. What projects has she worked on?")
                print("  8. Show me examples of her Python experience")
                print("  9. What does her resume say about machine learning?")
                print()
                print("🔀 Hybrid Examples (Both Systems):")
                print("  10. Tell me about Alice's skills and experience")
                print("  11. Compare her skills with her documented experience")
                print()
                continue

            # Skip empty input
            if not query:
                continue

            print(f"🔍 Processing: {query}")
            print("-" * 50)

            # Construct the request payload
            payload = {"query": query}

            # Send the request to the backend
            response = requests.post(
                BACKEND_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=300,
            )

            # Check response status
            if response.status_code == 200:
                response_data = response.json()

                if response_data.get("success"):
                    # Show query type
                    query_type = response_data.get("query_type", "unknown")
                    type_emoji = {"rag": "📚", "sql": "🗄️", "hybrid": "🔀", "fallback": "🔄"}.get(query_type, "❓")
                    print(f"{type_emoji} Query Type: {query_type.upper()}")

                    print(f"✅ {response_data.get('answer', 'Query processed')}")

                    # Show SQL if available
                    if response_data.get("sql_query"):
                        print(f"📊 SQL: {response_data['sql_query']}")

                    # --- Display Logic ---
                    sql_results = response_data.get("results", [])
                    rag_sources = response_data.get("rag_sources", [])

                    # Show SQL query if it exists
                    if response_data.get("sql_query"):
                        print(f"📊 SQL: {response_data['sql_query']}")

                    # Display structured SQL results if they exist
                    if sql_results:
                        print(f"📈 Database Results: {len(sql_results)} records")
                        for i, result in enumerate(sql_results[:3]):  # Show first 3 results
                            print(f"  {i+1}. {result}")
                        if len(sql_results) > 3:
                            print(f"  ... and {len(sql_results) - 3} more results")

                    # Display RAG sources if they exist
                    if rag_sources:
                        print(f"📚 Document Sources: {len(rag_sources)} relevant chunks")
                        for i, source in enumerate(rag_sources[:2]):  # Show first 2 sources
                            print(f"  {i+1}. Employee {source.get('employee_id', 'N/A')} (Score: {source.get('similarity_score', 0.0):.2f})")
                            print(f"     Snippet: {source.get('snippet', 'N/A')[:100]}...")
                    
                    # Only show a "no results" message if no detailed data was found at all
                    if not sql_results and not rag_sources:
                        answer = response_data.get('answer', '').lower()
                        if "no results found" in answer or "no relevant information" in answer:
                            print("📭 No detailed results found.")

                else:
                    print(f"❌ Error: {response_data.get('error', 'Unknown error')}")

            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")

            print()  # Add spacing between queries

        except requests.exceptions.Timeout:
            print("❌ Error: Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            print("❌ Error: Cannot connect to server. Make sure it's running with 'python api_server.py'")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def run_benchmark():
    """Run the comprehensive benchmark suite."""
    
    benchmark_suite = {
        "SQL-Only": [
            "Show me all Python developers",
            "What are the top 5 technical skills in the company?",
            "Which department has the most employees?",
            "Find people with leadership skills",
            "Count employees by department",
            "Show me engineers with confidence > 80%",
            "What are the most common skills in Engineering?",
            "Find employees who joined in 2023",
        ],
        "RAG-Only": [
            "What leadership experience does Alice have?",
            "Show me examples of Python projects from resumes",
            "What does Alice's resume say about machine learning?",
            "Find examples of communication skills in documents",
            "What projects has Alice demonstrated?",
            "Show me experience with cloud technologies",
            "What management experience is documented?",
            "Find examples of teamwork in uploaded files",
        ],
        "Hybrid": [
            "Tell me about Alice's skills and experience",
            "Compare Alice's stated skills with her documented experience",
            "Find Python developers and show me their project examples",
            "Verify Alice's skills with evidence from her resume",
            "Show me leaders and demonstrate their experience",
            "Who has both technical and soft skills? Show proof",
            "Find the best Python developer with project evidence",
            "Validate skills mentioned in performance reviews",
        ],
        "Complex Agentic": [
            "Who is the best full-stack developer? Prove it with data",
            "Find me a team leader with both technical skills and management experience",
            "Show me the most well-rounded engineer with documented proof",
            "Who would be best for a project manager role? Show evidence",
            "Find candidates for senior developer role with demonstrated leadership",
        ]
    }

    print("🧪 Running Comprehensive Benchmark Suite...")
    print("=" * 70)

    if not test_connection():
        print("❌ Error: Cannot connect to the API server.")
        print("Please make sure the server is running with 'uvicorn api_server:app --reload'")
        return

    for category, queries in benchmark_suite.items():
        print(f"\n--- Testing Category: {category} ---")
        for i, query in enumerate(queries, 1):
            print(f"\n[{category} {i}/{len(queries)}] Query: {query}")
            print("-" * 50)

            try:
                payload = {"query": query}
                response = requests.post(
                    BACKEND_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=300,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        query_type = data.get("query_type", "unknown").upper()
                        answer = data.get('answer', 'No answer returned.')
                        print(f"  ✅ Agent Response:")
                        print(f"  - Query Type: {query_type}")
                        print(f"  - Answer: {answer.strip()}")
                    else:
                        print(f"  ❌ Agent Error: {data.get('error', 'Unknown error')}")
                else:
                    print(f"  ❌ HTTP Error {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                print("  ❌ Client Error: Request timed out after 300 seconds.")
            except Exception as e:
                print(f"  ❌ Client Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Benchmark Complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_benchmark()
    else:
        main()