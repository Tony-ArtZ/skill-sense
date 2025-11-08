import json

from langchain_core.tools import tool
from logger import logger
from managers import DatabaseManager
from textql_workflow import TextQlWorkflow  # Import the original workflow

# This global context is a simplified way to pass request-specific data to the tools.
_tool_context = {}


def set_tool_context(ontology_file, db_connection_string, engine_type, schema_name):
    global _tool_context
    _tool_context = {
        "ontology_file": ontology_file,
        "db_connection_string": db_connection_string,
        "engine_type": engine_type,
        "schema_name": schema_name,
    }


@tool
def run_textql_workflow(query: str) -> dict:
    """Use this tool when the user asks a question that requires fetching data from the database, running calculations, or generating a SQL query to answer.

    IMPORTANT: The input should be the user's NATURAL LANGUAGE question, not SQL. For example:
    - Good: "Find me all employees from Andhra Pradesh"
    - Bad: "SELECT * FROM Employees WHERE state = 'Andhra Pradesh'"

    This tool will handle the SQL generation and execution automatically."""
    logger.info(f"--- TOOL: Running TextQL Workflow for query: {query} ---")
    if not _tool_context:
        return {"error": "Tool context not set. Cannot connect to the database."}

    try:
        # Instantiate and run the original TextQl workflow with the provided context
        textql_runner = TextQlWorkflow(
            ontology_file=_tool_context["ontology_file"],
            db_connection_string=_tool_context["db_connection_string"],
            engine_type=_tool_context["engine_type"],
            schema_name=_tool_context["schema_name"],
        )
        result = textql_runner.run(query)

        # Debug: Print what we actually got back from the workflow
        logger.info(f"[TOOL DEBUG] Result from workflow: {result}")
        logger.info(f"[TOOL DEBUG] Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

        # The final answer from the internal workflow is what we return to the main agent
        raw_answer = result.get(
            "final_answer", result.get("answer", "The workflow completed, but produced no final_answer.")
        )

        # Extract SQL from the result state directly
        executed_sql = result.get("executed_sql", "")
        logger.info(f"[TOOL DEBUG] SQL query from result state: {executed_sql}")
        logger.info(f"[TOOL DEBUG] Raw answer type: {type(raw_answer)}")

        # Also check for sql_query in the result (different field name)
        if not executed_sql:
            executed_sql = result.get("sql_query", "")
            logger.info(f"[TOOL DEBUG] SQL query from sql_query field: {executed_sql}")

        # Try to parse structured JSON response from the workflow
        try:
            # Check if the answer is a JSON string with executed_sql
            if isinstance(raw_answer, str) and raw_answer.strip().startswith("{"):
                parsed_answer = json.loads(raw_answer)
                if "executed_sql" in parsed_answer:
                    # This is a structured response with SQL
                    logger.info(f"[TOOL DEBUG] Found SQL in structured response: {parsed_answer.get('executed_sql', '')[:100]}...")
                    return {
                        "final_answer": parsed_answer.get("final_answer", raw_answer),
                        "executed_sql": parsed_answer.get("executed_sql", ""),
                        "status": parsed_answer.get("status", "SUCCESS"),
                        "comment": "The TextQL workflow completed successfully with SQL information.",
                    }
        except (json.JSONDecodeError, AttributeError):
            # Not a JSON response, use the raw answer
            logger.info(f"[TOOL DEBUG] JSON parsing failed, trying dict string parsing")
            # Try to handle string representation of dictionary
            try:
                if raw_answer.startswith("{") and raw_answer.endswith("}"):
                    import ast
                    parsed_answer = ast.literal_eval(raw_answer)
                    if isinstance(parsed_answer, dict) and "executed_sql" in parsed_answer:
                        logger.info(f"[TOOL DEBUG] Found SQL in dict string response: {parsed_answer.get('executed_sql', '')[:100]}...")
                        return {
                            "final_answer": parsed_answer.get("final_answer", raw_answer),
                            "executed_sql": parsed_answer.get("executed_sql", ""),
                            "status": parsed_answer.get("status", "SUCCESS"),
                            "comment": "The TextQL workflow completed successfully with SQL information.",
                        }
            except (ValueError, SyntaxError):
                logger.info(f"[TOOL DEBUG] Dict string parsing failed, using raw answer")
                pass

        # If we have SQL from the result state, include it directly
        if executed_sql:
            logger.info(f"[TOOL DEBUG] Including SQL from result state: {executed_sql[:100]}...")
            # Return structured response with SQL for the agentic layer to extract
            return {
                "final_answer": raw_answer,
                "executed_sql": executed_sql,
                "status": "SUCCESS",
                "comment": "The TextQL workflow completed successfully with SQL extracted from result state.",
            }

        # Fallback: return the original format
        logger.info(f"[TOOL DEBUG] No SQL found, returning original format")
        return {
            "final_answer": raw_answer,
            "status": "SUCCESS",
            "comment": "The TextQL workflow completed successfully and this is the final answer. No further steps are needed.",
        }
    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        logger.error(f"EXCEPTION IN TEXTQL WORKFLOW: {error_trace}")
        return {
            "error": "The TextQL workflow failed with an internal exception.",
            "details": f"The following exception occurred: {str(e)}. This is likely an internal error in the tool. Retrying with the same query will probably fail again. The full traceback is: {error_trace}",
        }


@tool
def inspect_database_schema(table_name: str = None) -> str:
    """Use this tool when the user asks a question about the database's structure, such as 'What tables are available?', 'What are the columns in the orders table?', or 'Describe the Employees table'."""
    logger.info(f"--- TOOL: Inspecting schema for table: {table_name or 'all'} ---")
    if not _tool_context:
        return "Error: Tool context not set. Cannot connect to the database."

    try:
        db_manager = DatabaseManager(
            db_connection_string=_tool_context["db_connection_string"],
            engine_type=_tool_context["engine_type"],
            schema_name=_tool_context["schema_name"],
        )
        schema_info = db_manager.get_schema()

        if table_name:
            for line in schema_info.split("\n"):
                if line.lower().startswith(f"table {table_name.lower()}"):
                    return line
            return f"Error: Table '{table_name}' not found."
        else:
            table_names = [
                line.split(":")[0].replace("Table ", "")
                for line in schema_info.split("\n")
                if line
            ]
            return f"Available tables in the database:\n{', '.join(table_names)}"
    except Exception as e:
        return f"An error occurred while inspecting the schema: {str(e)}"
