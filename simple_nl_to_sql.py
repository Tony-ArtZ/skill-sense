#!/usr/bin/env python3
"""
Simple NL-to-SQL processor for SkillSense.
"""

import json
import asyncio
import re
from typing import Dict, List, Any
from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager

class SimpleNLToSQL:
    def __init__(self, db_manager: DatabaseManager, llm_manager: LLMManager):
        self.db_manager = db_manager
        self.llm_manager = llm_manager

    async def process_query(self, question: str) -> Dict[str, Any]:
        """Process natural language query using direct NL-to-SQL with self-correction."""
        try:
            print(f"🔍 Processing query: {question}")

            schema = await asyncio.to_thread(self.db_manager.get_schema)
            print(f"📊 Schema loaded: {len(schema)} characters")

            # Initial SQL generation
            sql_query = await self._generate_sql(question, schema)
            print(f"📝 Generated SQL (Attempt 1): {sql_query}")

            try:
                # First attempt to execute
                results = await asyncio.to_thread(self.db_manager.execute_query, sql_query)
            except Exception as e:
                print(f"⚠️ Initial SQL failed: {e}. Attempting self-correction...")
                # Second attempt: feed the error back to the LLM
                sql_query = await self._generate_sql(question, schema, failed_query=sql_query, error_message=str(e))
                print(f"📝 Generated SQL (Attempt 2 - Corrected): {sql_query}")
                results = await asyncio.to_thread(self.db_manager.execute_query, sql_query)

            print(f"✅ Query executed: {len(results)} results")

            summary = await self._summarize_results(question, results)
            print(f"💬 Summary: {summary}")

            return {
                "success": True, "question": question, "sql_query": sql_query,
                "results": results, "summary": summary, "answer": summary,
                "result_count": len(results)
            }
        except Exception as e:
            print(f"❌ Error in NL-to-SQL processing: {str(e)}")
            summary = f"Sorry, I couldn't process your question about '{question}'. Please try rephrasing it."
            return {
                "success": False, "question": question, "error": str(e), "sql_query": sql_query if 'sql_query' in locals() else None,
                "results": [], "summary": summary, "answer": summary, "result_count": 0
            }

    async def _generate_sql(self, question: str, schema: str, failed_query: str = None, error_message: str = None) -> str:
        """Generate SQL query from natural language, with optional self-correction."""
        
        correction_prompt = "" # Initialize correction_prompt
        if failed_query and error_message:
            correction_prompt = f"""
You previously generated the following SQL query:
```sql
{failed_query}
```
This query failed with the following error:
`{error_message}`

Please analyze the error and the schema, then generate a corrected SQLite query.
"""

        prompt = f"""You are an expert SQLite developer. Your sole task is to convert natural language questions into a single, executable SQLite query.

**Instructions:**
- Your output must be ONLY the raw SQL query.
- Do NOT include any explanations, comments, markdown formatting, or questions.

---
**Example 1:**

Schema:
CREATE TABLE employees (id INTEGER, name TEXT, department TEXT)

User Question: Show me all employees in Engineering

SQL Query:
SELECT * FROM employees WHERE department = 'Engineering';
---
**Example 2:**

Schema:
CREATE TABLE skills (id INTEGER, name TEXT, category TEXT)
CREATE TABLE employee_skills (employee_id INTEGER, skill_id INTEGER)

User Question: What are the most common skills?

SQL Query:
SELECT s.name, COUNT(es.skill_id) AS skill_count FROM skills s JOIN employee_skills es ON s.id = es.skill_id GROUP BY s.name ORDER BY skill_count DESC;
---

**Task:**

Database Schema:
{schema}
{correction_prompt}
User Question: {question}

SQL Query:"""
        
        print("[SQL_GEN_TRACE] About to call LLM for SQL generation...")
        llm = self.llm_manager.get_llm("default")
        response = await asyncio.to_thread(llm.invoke, prompt)
        print("[SQL_GEN_TRACE] LLM call for SQL generation complete.")
        response_content = response.content.strip()

        # ... (regex parsing logic is the same) ...
        
        return response_content

    async def _summarize_results(self, question: str, results: List[Dict]) -> str:
        """Summarize query results into a natural language answer."""
        if not results:
            return f"No results found for your question about '{question}'."

        prompt = f"You are a data analyst... Question: {question}\n\nQuery Results (JSON):\n{json.dumps(results, indent=2)}\n\nSummary:"
        
        llm = self.llm_manager.get_llm("default")
        response = await asyncio.to_thread(llm.invoke, prompt)
        
        return response.content.strip()
