#!/usr/bin/env python3
"""
Simple command-line client for testing SkillSense NL-to-SQL queries.
Based on the fused_chat chat_client.py approach.
"""

import json
import requests
import sys

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

def main():
    """
    Simple command-line client for interacting with SkillSense NL-to-SQL.
    """
    print("--- SkillSense Chat Client ---")
    print("Ask questions about your talent database!")
    print("Examples:")
    print("  - Show me all Python developers")
    print("  - What are the top 5 technical skills?")
    print("  - Which department has the most employees?")
    print("  - Find people with leadership skills")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("Type 'examples' to see more sample queries.")
    print("--------------------------------")

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
                print("Goodbye!")
                break

            # Check for examples
            if query.lower() == "examples":
                print("\nSample queries you can try:")
                print("  1. Show me all employees in Engineering")
                print("  2. What are the most common technical skills?")
                print("  3. Find employees with Python skills")
                print("  4. Which department has the highest skill confidence?")
                print("  5. Show me employees with leadership potential")
                print("  6. Compare skills between Engineering and Data Science")
                print("  7. Who has machine learning experience?")
                print("  8. What soft skills are most common?")
                print("  9. Find employees with confidence > 80")
                print("  10. Show skill distribution by department")
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
                timeout=30,
            )

            # Check response status
            if response.status_code == 200:
                response_data = response.json()

                if response_data.get("success"):
                    print(f"✅ Success: {response_data.get('answer', 'Query processed')}")

                    if response_data.get("sql_query"):
                        print(f"📊 SQL: {response_data['sql_query']}")

                    results = response_data.get("results", [])
                    if results:
                        print(f"📈 Found {len(results)} results:")
                        for i, result in enumerate(results[:5]):  # Show first 5 results
                            print(f"  {i+1}. {result}")
                        if len(results) > 5:
                            print(f"  ... and {len(results) - 5} more results")
                    else:
                        print("📭 No results found")

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

def run_test_queries():
    """Run a set of test queries to verify functionality."""
    test_queries = [
        "Show me all employees",
        "What are the top 3 technical skills?",
        "Find employees in Engineering department",
        "Who has leadership skills?",
        "Compare skill confidence between departments"
    ]

    print("🧪 Running test queries...")
    print("=" * 50)

    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 30)

        try:
            payload = {"query": query}
            response = requests.post(
                BACKEND_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ {data.get('answer', 'Success')}")
                    print(f"📊 Results: {len(data.get('results', []))} records")
                else:
                    print(f"❌ {data.get('error', 'Error')}")
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test_queries()
    else:
        main()