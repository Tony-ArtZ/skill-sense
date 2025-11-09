#!/usr/bin/env python3
"""
Agentic Query Processor for SkillSense Platform.
Uses an LLM-based agent to dynamically select and execute tools (RAG or NL-to-SQL).
"""

import json
import asyncio
import traceback
from typing import Dict, List, Any
from simple_nl_to_sql import SimpleNLToSQL
from rag_manager import RAGManager
from managers.llm_manager import LLMManager

class AgenticQueryProcessor:
    def __init__(self, rag_manager: RAGManager, llm_manager: LLMManager, nl_to_sql_processor: SimpleNLToSQL):
        self.rag_manager = rag_manager
        self.llm_manager = llm_manager
        self.nl_to_sql = nl_to_sql_processor
        self.planner_llm = llm_manager.get_llm("planner")

    async def process_query(self, question: str) -> Dict[str, Any]:
        """
        Process query using an agentic approach to select and execute tools.
        """
        try:
            print(f"🧠 Agent processing query: {question}")

            plan = await self._generate_plan(question)
            print(f"📝 Agent Plan: {plan}")

            # Handle conversational plan
            if plan.get("tools_to_use") == ["conversational_tool"]:
                print("💬 Handling conversational query.")
                return {
                    "success": True, "question": question,
                    "answer": "Hello! I'm SkillSense. I can tell you anything about the talent in your database and documents. How can I help you today?",
                    "query_type": "conversational", "sql_query": None, "results": [], "rag_sources": [],
                    "result_count": 0, "components": {}
                }

            tasks = []
            if "sql_tool" in plan["tools_to_use"]:
                print("➕ Adding SQL tool to execution plan...")
                tasks.append(self.nl_to_sql.process_query(question))
            if "rag_tool" in plan["tools_to_use"]:
                print("➕ Adding RAG tool to execution plan...")
                tasks.append(self.rag_manager.semantic_search_and_generate(question))

            sql_result, rag_result = None, None
            if tasks:
                print(f"🚀 Executing {len(tasks)} tools concurrently...")
                try:
                    # Add a server-side timeout to prevent indefinite hangs
                    results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=300.0)
                    print("✅ All tools executed.")
                except asyncio.TimeoutError:
                    print("❌ Tool execution timed out on the server.")
                    return {"success": False, "question": question, "error": "Agent tool execution timed out after 290 seconds.", "query_type": "error", "answer": "Sorry, the request took too long to process.", "result_count": 0}
                
                # Unpack results based on the plan
                if "sql_tool" in plan["tools_to_use"]:
                    sql_result = results.pop(0)
                if "rag_tool" in plan["tools_to_use"]:
                    rag_result = results.pop(0)
            
            sql_result = sql_result or {"success": False, "answer": "", "results": [], "sql_query": None}
            rag_result = rag_result or {"success": False, "answer": "", "sources": []}

            combined_answer = await self._combine_results(question, sql_result, rag_result)
            
            query_type = "hybrid" if "sql_tool" in plan["tools_to_use"] and "rag_tool" in plan["tools_to_use"] else "sql" if "sql_tool" in plan["tools_to_use"] else "rag" if "rag_tool" in plan["tools_to_use"] else "unknown"

            return {
                "success": True, "question": question, "answer": combined_answer,
                "sql_query": sql_result.get("sql_query"), "results": sql_result.get("results", []),
                "rag_sources": rag_result.get("sources", []), "query_type": query_type,
                "result_count": len(sql_result.get("results", [])) + len(rag_result.get("sources", [])),
                "components": {"sql_success": sql_result.get("success", False), "rag_success": rag_result.get("success", False)}
            }

        except Exception as e:
            print(f"❌ Agentic query processing failed: {str(e)}")
            traceback.print_exc() # Print the full traceback
            return {"success": False, "question": question, "error": str(e), "query_type": "error", "answer": "Sorry, I encountered an error processing your question.", "result_count": 0}

    async def _generate_plan(self, question: str) -> Dict[str, Any]:
        # ... (This method is now async but its internal logic is the same)
        tool_descriptions = {
            "sql_tool": {
                "description": "Searches and retrieves structured data about employees, their skills, departments, and roles from a database. Use for questions about who, what, where, how many.",
                "example_questions": ["How many Python developers do we have?", "List all employees in the Engineering department."]
            },
            "rag_tool": {
                "description": "Searches the content of unstructured documents (like resumes, project descriptions, performance reviews) to find qualitative information, examples, and experiences. Use for questions about 'what does X say about Y' or 'show me examples of Z'.",
                "example_questions": ["What leadership experience does Alice have?", "Show me examples of projects where Bob used Java."]
            },
            "conversational_tool": {
                "description": "Responds to simple greetings, small talk, or conversational questions where no data is required.",
                "example_questions": ["hello", "hi", "how are you?", "thanks"]
            }
        }
        prompt = f"""You are an intelligent agent designed to select the best tool(s) to answer a user's question.
You have access to the following tools:

{json.dumps(tool_descriptions, indent=2)}

Based on the user's question, your task is to output a JSON object indicating the tools to use.
The JSON object must have a key named "tools_to_use".
The value for "tools_to_use" must be a list of strings.
The strings in the list must be one of: "sql_tool", "rag_tool", "conversational_tool".

Examples:
- For a question like "List all engineers", you would output: {{\"tools_to_use\": [\"sql_tool\"]}}
- For a question like "What does the resume say?", you would output: {{\"tools_to_use\": [\"rag_tool\"]}}
- For a question like "hello", you would output: {{\"tools_to_use\": [\"conversational_tool\"]}}
- For a question like "Compare skills with resume", you would output: {{\"tools_to_use\": [\"sql_tool\", \"rag_tool\"]}}

Do not add any explanation or reasoning. Output only the JSON object.

User Question: "{question}"

JSON Response:"""
        
        planner_llm = self.llm_manager.get_llm("planning")
        response = await asyncio.to_thread(planner_llm.invoke, prompt)
        response_content = response.content.strip()
        
        # ... (The robust JSON parsing logic remains the same)
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        if json_start == -1 or json_end == 0: raise ValueError("No JSON object found in LLM response.")
        json_string = response_content[json_start:json_end]
        plan = json.loads(json_string)
        if "tools_to_use" not in plan or not isinstance(plan["tools_to_use"], list): raise ValueError("Invalid plan format from LLM.")
        return plan

    async def _combine_results(self, question: str, sql_result: Dict, rag_result: Dict) -> str:
        """Combine results from SQL and RAG into a unified answer."""
        try:
            # Use the concise summary from the SQL tool instead of raw results to reduce prompt size
            sql_summary = sql_result.get('summary', 'No information from database.')
            rag_summary = rag_result.get('answer', 'No information from documents.')

            # If only one tool was used, just return its answer directly
            if not sql_result.get("success"):
                return rag_summary
            if not rag_result.get("success"):
                return sql_summary

            prompt = f"""You are a talent analytics expert. Your task is to synthesize information from a database query and a document search into a single, comprehensive answer.

Question: {question}

Summary from Database Query:
{sql_summary}

Summary from Document Search:
{rag_summary}

Instructions:
1.  Create a unified, well-structured answer based on the summaries provided.
2.  Do not simply repeat the summaries. Synthesize them into a coherent response.
3.  If one summary is empty or says no results were found, base your answer on the other one.
4.  If both are empty, state that no information could be found.

Comprehensive Answer:"""

            print("[SYNTHESIS_TRACE] About to call final LLM...")
            llm = self.llm_manager.get_llm("default")
            response = await asyncio.to_thread(llm.invoke, prompt)
            print("[SYNTHESIS_TRACE] Final LLM call complete.")
            return response.content.strip()

        except Exception as e:
            print(f"❌ Error in _combine_results: {e}")
            # Fallback to simple concatenation in case of synthesis failure
            return f"SQL Tool: {sql_result.get('summary', 'N/A')}\n\nRAG Tool: {rag_result.get('answer', 'N/A')}"

    def get_system_stats(self) -> Dict[str, Any]:
        # This method does not need to be async as it's not I/O bound
        return {
            "rag_stats": self.rag_manager.get_document_stats(),
            "query_routing": {"supported_types": ["sql_tool", "rag_tool", "hybrid"], "routing_method": "LLM-based agentic planning"}
        }