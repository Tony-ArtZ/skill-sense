#!/usr/bin/env python3
"""
Simple NL-to-SQL processor for SkillSense.
Direct approach without complex workflow for hackathon demo.
"""

import json
import sqlite3
from typing import Dict, List, Any
from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager

class SimpleNLToSQL:
    def __init__(self):
        self.db_manager = DatabaseManager("data/talent_database.db")
        self.llm_manager = LLMManager()

    def process_query(self, question: str) -> Dict[str, Any]:
        """Process natural language query using direct NL-to-SQL."""
        try:
            print(f"🔍 Processing query: {question}")

            # Get database schema
            schema = self.db_manager.get_schema()
            print(f"📊 Schema loaded: {len(schema)} tables")

            # Generate SQL directly
            sql_query = self._generate_sql(question, schema)
            print(f"📝 Generated SQL: {sql_query}")

            # Execute query
            results = self.db_manager.execute_query(sql_query)
            print(f"✅ Query executed: {len(results)} results")

            # Generate natural language summary
            summary = self._summarize_results(question, results)
            print(f"💬 Summary: {summary}")

            return {
                "success": True,
                "question": question,
                "sql_query": sql_query,
                "results": results,
                "summary": summary,
                "result_count": len(results)
            }

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "sql_query": None,
                "results": [],
                "summary": f"Sorry, I couldn't process your question about '{question}'. Please try rephrasing it.",
                "result_count": 0
            }

    def _generate_sql(self, question: str, schema: str) -> str:
        """Generate SQL query from natural language."""

        prompt = f"""You are an expert SQLite developer for talent analytics. Convert the following natural language question to a SQL query.

Database Schema:
{schema}

Question: {question}

Requirements:
1. Use proper SQLite syntax
2. Include appropriate JOINs when needed
3. Use LIKE for partial matches on skill names and departments
4. Add ORDER BY for ranking queries
5. Use GROUP BY for aggregations
6. Return ONLY the SQL query, no explanations or markdown

SQL Query:"""

        try:
            response = self.llm_manager.get_llm("default").invoke(prompt)
            sql_query = response.content.strip()

            # Clean up the response
            if sql_query.startswith("```sql"):
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            elif sql_query.startswith("```"):
                sql_query = sql_query.replace("```", "").strip()

            return sql_query
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")

    def _summarize_results(self, question: str, results: List[Dict]) -> str:
        """Generate natural language summary of results."""

        if not results:
            return f"No results found for your question about '{question}'."

        # For small result sets, provide detailed summary
        if len(results) <= 10:
            result_summary = json.dumps(results, indent=2)

            prompt = f"""Given this database query and results, provide a natural language summary:

Question: {question}

Results:
{result_summary}

Provide a clear, concise answer in natural language. Focus on the key findings."""

            try:
                response = self.llm_manager.get_llm("default").invoke(prompt)
                return response.content.strip()
            except:
                # Fallback to simple summary
                return f"Found {len(results)} results for your question about '{question}'."
        else:
            return f"Found {len(results)} results for your question about '{question}'."

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            result = self.db_manager.execute_query("SELECT COUNT(*) as count FROM employees")
            return len(result) > 0 and result[0].get('count', 0) > 0
        except:
            return False

# Create a simple processor instance
simple_processor = SimpleNLToSQL()