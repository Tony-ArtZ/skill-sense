"""
TextQL Workflow - A wrapper for the NL-to-SQL workflow
This provides a simplified interface for the multimodal tools
"""
from typing import Dict, Any
from managers.database_manager import DatabaseManager
from managers.llm_manager import LLMManager
from managers.ontology_manager import OntologyManager
from managers.prompt_manager import PromptManager


class TextQlWorkflow:
    """Wrapper class for TextQL workflow functionality"""
    
    def __init__(self, ontology_file: str, db_connection_string: str, 
                 engine_type: str = "sqlite", schema_name: str = None):
        """Initialize the TextQL workflow with database and ontology configuration"""
        self.ontology_file = ontology_file
        self.db_connection_string = db_connection_string
        self.engine_type = engine_type
        self.schema_name = schema_name
        
        # Initialize managers
        self.db_manager = DatabaseManager(
            db_connection_string=db_connection_string,
            engine_type=engine_type,
            schema_name=schema_name
        )
        self.llm_manager = LLMManager()
        self.ontology_manager = OntologyManager(ontology_file)
        self.prompt_manager = PromptManager()
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Run the TextQL workflow for a given natural language query
        
        Args:
            query: Natural language question about the database
            
        Returns:
            Dictionary containing the results and metadata
        """
        try:
            # Get schema
            schema = self.db_manager.get_schema()
            
            # Generate SQL using LLM
            sql_query = self._generate_sql(query, schema)
            
            # Execute query
            results = self.db_manager.execute_query(sql_query)
            
            # Generate summary
            summary = self._generate_summary(query, results, sql_query)
            
            return {
                "answer": summary,
                "final_answer": summary,
                "sql_query": sql_query,
                "executed_sql": sql_query,
                "results": results,
                "status": "SUCCESS"
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "final_answer": f"Error processing query: {str(e)}",
                "sql_query": "",
                "executed_sql": "",
                "results": [],
                "status": "ERROR",
                "error": str(e)
            }
    
    def _generate_sql(self, query: str, schema: str) -> str:
        """Generate SQL query from natural language"""
        llm = self.llm_manager.get_llm("default")
        
        prompt = f"""Given the following database schema:

{schema}

Generate a SQL query to answer this question: {query}

Return ONLY the SQL query, nothing else. Do not include markdown formatting or explanations."""
        
        response = llm.invoke(prompt)
        
        # Extract SQL from response
        if hasattr(response, 'content'):
            sql = response.content
        else:
            sql = str(response)
        
        # Clean up the SQL
        sql = sql.strip().replace("```sql", "").replace("```", "").strip()
        
        return sql
    
    def _generate_summary(self, query: str, results: list, sql_query: str) -> str:
        """Generate natural language summary of results"""
        if not results:
            return "No results found for your query."
        
        llm = self.llm_manager.get_llm("default")
        
        # Limit results for summary if too many
        limited_results = results[:100] if len(results) > 100 else results
        
        prompt = f"""Given this question: {query}

The following SQL query was executed:
{sql_query}

And returned these results:
{limited_results}

Provide a clear, concise natural language answer to the original question based on these results.
If there are many results, summarize them appropriately."""
        
        response = llm.invoke(prompt)
        
        if hasattr(response, 'content'):
            return response.content
        return str(response)
