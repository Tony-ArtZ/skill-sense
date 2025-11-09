import os
import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


class LLMManager:
    def __init__(self):
        # Initialize different LLMs for different tasks using OpenRouter
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        # Use OpenRouter for all models with temperature=0 for deterministic behavior
        self.llm = ChatOpenAI(
            api_key=openrouter_key,
            base_url='https://openrouter.ai/api/v1',
            model="x-ai/grok-4-fast",
            temperature=0,
            request_timeout=80
        )           # Default LLM for most tasks

        self.planner_llm = ChatOpenAI(
            api_key=openrouter_key,
            base_url='https://openrouter.ai/api/v1',
            model="x-ai/grok-4-fast",
            temperature=0,
            request_timeout=80
        )       # Specialized for planning

        self.reflector_llm = ChatOpenAI(
            api_key=openrouter_key,
            base_url='https://openrouter.ai/api/v1',
            model="x-ai/grok-4-fast",
            temperature=0,
            request_timeout=80
        )   # Specialized for reflection/validation

    def get_llm(self, task_type="default"):
        """Get appropriate LLM based on task type"""
        if task_type == "planning":
            return self.planner_llm
        elif task_type == "reflection":
            return self.reflector_llm
        else:
            return self.llm

    def update_model(self, task_type, model_name):
        """Update model for a specific task type"""
        if task_type == "default":
            self.llm = ChatOpenAI(model=model_name)
        elif task_type == "planning":
            self.planner_llm = ChatOpenAI(model=model_name)
        elif task_type == "reflection":
            self.reflector_llm = ChatOpenAI(model=model_name)

    def get_models_info(self):
        """Get information about current models"""
        return {
            "default": self.llm.model,
            "planning": self.planner_llm.model,
            "reflection": self.reflector_llm.model
        }