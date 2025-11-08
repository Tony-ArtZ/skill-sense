from typing import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from managers import LLMManager, PromptManager
from tools import inspect_database_schema, run_textql_workflow


# The state definition without memory
class MainAgentState(TypedDict):
    input: str
    original_query: str  # Track original user query to prevent loops
    messages: list[BaseMessage]  # No accumulation without memory


class WorkflowManager:
    """Manages the new tool-calling agent workflow."""

    def __init__(self):
        self.llm_manager = LLMManager()
        self.prompt_manager = PromptManager()

    def create_workflow(self, checkpointer=None):
        """Creates the robust tool-calling agent workflow using prebuilt nodes."""

        tools = [run_textql_workflow, inspect_database_schema]
        tool_node = ToolNode(tools)

        # 1. Define the Agent
        # Load the main agent prompt from config
        prompt_config = self.prompt_manager.get_prompt_config("main_agent")
        system_message = prompt_config["system"]

        # No MessagesPlaceholder needed without memory
        # The prompt will be constructed manually in the agent function
        llm = self.llm_manager.get_llm("default")
        llm_with_tools = llm.bind_tools(tools)

        def agent(state: MainAgentState):
            """Agent node that processes the state and returns AI messages"""
            print("--- NODE: Running Agent ---")
            # Always use original_query to prevent infinite loops with generated SQL
            original_query = state["original_query"]
            print(f"Processing original query: {original_query}")
            # Process only the original user query, never generated SQL
            response = llm_with_tools.invoke(
                [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": original_query},
                ]
            )
            return {"messages": [response]}

        # 2. Define the Graph
        workflow = StateGraph(MainAgentState)
        workflow.add_node("agent", agent)  # The agent node
        workflow.add_node("tools", ToolNode(tools))  # The tool execution node

        workflow.set_entry_point("agent")

        # This conditional edge decides whether to call tools or end
        def after_agent(state):
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                print(f"Tool calls detected, message count: {len(state['messages'])}")
                return "tools"
            return END

        workflow.add_conditional_edges("agent", after_agent)

        # After tools are called, check if we should continue or end
        def should_continue_after_tools(state):
            """Check if tools provided a complete answer or if we need to continue"""
            last_message = state["messages"][-1]

            print(f"DEBUG: Checking tool response type: {type(last_message)}")
            if hasattr(last_message, "content"):
                content = last_message.content
                print(f"DEBUG: Tool content type: {type(content)}")
                print(f"DEBUG: FULL Tool content:")
                print(f"--- START CONTENT ---")
                print(str(content))
                print(f"--- END CONTENT ---")
                print(f"DEBUG: Content length: {len(str(content))}")

                # Handle dict content (structured tool response)
                if isinstance(content, dict):
                    print(f"DEBUG: Dict content keys: {list(content.keys())}")
                    # If the tool returned a complete answer, end the workflow
                    if "final_answer" in content or "answer" in content:
                        print("Tool provided final_answer in dict - ending workflow")
                        return END
                    # If the tool returned an error, also end the workflow
                    elif "error" in content:
                        print("Tool returned error in dict - ending workflow")
                        return END
                    # If the tool returned structured data, check if it's a complete response
                    elif "results" in content:
                        # For schema inspection, results ARE the complete answer
                        if content.get("comment") and any(keyword in content["comment"].lower() for keyword in ["available tables", "database schema", "schema information"]):
                            print("Tool provided complete schema information - ending workflow")
                            return END
                        else:
                            print("Tool provided results data - continuing workflow")
                            return "agent"
                    # Default case: continue the workflow

                # Handle string content (most common case from TextQL workflow and schema inspection)
                elif isinstance(content, str):
                    # Check for JSON string responses
                    if content.strip().startswith("{"):
                        try:
                            import json
                            parsed_content = json.loads(content)
                            print(f"DEBUG: Parsed JSON content keys: {list(parsed_content.keys())}")
                            if "final_answer" in parsed_content or "answer" in parsed_content:
                                print("Tool provided JSON with final_answer - ending workflow")
                                return END
                        except json.JSONDecodeError:
                            print("DEBUG: JSON parsing failed, trying eval for dict string representation")
                            # Try to handle string representation of dictionary
                            try:
                                # This handles the case where dict() was called but not serialized
                                if content.startswith("{") and content.endswith("}"):
                                    import ast
                                    parsed_content = ast.literal_eval(content)
                                    if isinstance(parsed_content, dict):
                                        print(f"DEBUG: Parsed dict string content keys: {list(parsed_content.keys())}")
                                        if "final_answer" in parsed_content or "answer" in parsed_content:
                                            print("Tool provided dict string with final_answer - ending workflow")
                                            return END
                            except (ValueError, SyntaxError):
                                print("DEBUG: Dict string parsing failed, treating as plain text")

                    # Check for schema inspection responses (plain strings with specific patterns)
                    if any(keyword in content.lower() for keyword in [
                        "available tables in the database",
                        "table schema",
                        "columns in the",
                        "error: table",
                        "an error occurred while inspecting the schema"
                    ]) or content.lower().startswith("table "):
                        print("Tool provided schema information in plain string - ending workflow")
                        return END

                    # Check for content indicators of complete answers
                    if (
                        "answer" in content.lower()
                        or "brand" in content.lower()
                        or "revenue" in content.lower()
                        or "executed_sql" in content.lower()
                        or "final answer" in content.lower()
                    ):
                        print(
                            "Tool provided complete answer in string format - ending workflow"
                        )
                        return END
                    elif "error" in content.lower() or "no response" in content.lower():
                        print("Tool returned error or empty response - ending workflow")
                        return END

            # Default: go back to agent for further processing
            print(
                "Tools completed but no complete answer detected, going back to agent"
            )
            return "agent"

        workflow.add_conditional_edges("tools", should_continue_after_tools)

        return workflow.compile(checkpointer=checkpointer)
