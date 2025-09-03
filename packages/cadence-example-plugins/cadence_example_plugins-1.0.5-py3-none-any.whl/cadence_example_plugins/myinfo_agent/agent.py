import os
from typing import List

from cadence_sdk import BaseAgent, PluginMetadata
from langchain_core.tools import Tool

from .tools import my_info_tools


class MyInfoAgent(BaseAgent):

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata, parallel_tool_calls=False)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from environment variables."""
        return {
            "bot_name": os.environ.get("CADENCE_BOT_NAME", "Cadence AI"),
            "bot_description": os.environ.get("CADENCE_BOT_DESCRIPTION", "Multiple Agents Chatbot System"),
            "bot_creator": os.environ.get("CADENCE_BOT_CREATOR", "JonasKahn"),
            "bot_specialization": os.environ.get("CADENCE_BOT_SPECIALIZATION", "Business"),
            "bot_version": os.environ.get("CADENCE_BOT_VERSION", "1.0.5"),
        }

    def get_tools(self) -> List[Tool]:
        return my_info_tools

    def get_system_prompt(self) -> str:
        return f"""You're {self.config['bot_name']}, your goal is to help user understand, get to know who you are"""
