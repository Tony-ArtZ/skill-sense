import json
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser


class PromptManager:
    def __init__(self, prompts_file="config/prompts.json"):
        self.prompts_file = prompts_file
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from JSON configuration file"""
        try:
            with open(self.prompts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Prompts file {self.prompts_file} not found, using default prompts")
            return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, Any]:
        """Fallback default prompts"""
        return {
            "route_query": {
                "system": "You are an expert at routing user queries. Decide if it needs 'direct' or 'plan' route.",
                "user_template": "Query: {query}",
                "output_parser": "json"
            }
        }

    def get_prompt_config(self, prompt_name: str) -> Dict[str, Any]:
        """Get configuration for a specific prompt"""
        return self.prompts.get(prompt_name, {})

    def render_prompt(self, prompt_name: str, **kwargs) -> ChatPromptTemplate:
        """Render a prompt template with provided variables"""
        config = self.get_prompt_config(prompt_name)

        if not config:
            raise ValueError(f"Prompt configuration not found: {prompt_name}")

        system_message = config.get("system", "")
        user_template = config.get("user_template", "")

        messages = [
            ("system", system_message),
            ("user", user_template)
        ]

        return ChatPromptTemplate.from_messages(messages)

    def get_output_parser(self, prompt_name: str):
        """Get the appropriate output parser for a prompt"""
        config = self.get_prompt_config(prompt_name)
        parser_type = config.get("output_parser", "str")

        if parser_type == "json":
            return JsonOutputParser()
        else:
            return StrOutputParser()

    def create_chain(self, prompt_name: str, llm, **kwargs):
        """Create a complete chain with prompt, LLM, and output parser"""
        prompt_template = self.render_prompt(prompt_name)
        output_parser = self.get_output_parser(prompt_name)

        return prompt_template | llm | output_parser

    def update_prompt(self, prompt_name: str, new_config: Dict[str, Any]):
        """Update a prompt configuration"""
        self.prompts[prompt_name] = new_config
        self._save_prompts()

    def add_prompt(self, prompt_name: str, config: Dict[str, Any]):
        """Add a new prompt configuration"""
        self.prompts[prompt_name] = config
        self._save_prompts()

    def _save_prompts(self):
        """Save current prompts to file"""
        with open(self.prompts_file, 'w') as f:
            json.dump(self.prompts, f, indent=2)

    def list_prompts(self) -> list:
        """List all available prompt names"""
        return list(self.prompts.keys())

    def validate_prompt(self, prompt_name: str) -> bool:
        """Validate that a prompt has required configuration"""
        config = self.get_prompt_config(prompt_name)
        required_keys = ["system", "user_template"]
        return all(key in config for key in required_keys)