"""Search Agent Implementation using Cadence SDK."""

from datetime import datetime, timezone
from typing import List

from cadence_sdk import BaseAgent
from cadence_sdk.base.metadata import PluginMetadata
from langchain_core.messages import SystemMessage


class SearchAgent(BaseAgent):
    """Web search and information retrieval agent using SDK."""

    def __init__(self, metadata: PluginMetadata):
        """Initialize the search agent."""
        super().__init__(metadata)

    def get_tools(self) -> List:
        """Get available search tools."""
        from .tools import search_tools

        return search_tools

    def get_system_prompt(self) -> str:
        """Get system prompt for the search agent."""
        return """You are the Search Agent, specialized in web search and information retrieval.

SYSTEM STATE:
- Current Time (UTC): {current_time}

Your responsibilities:
    - Understand user search intent and information needs
    - Choose the most appropriate search tool for each query
    - Execute targeted searches with relevant keywords
    - Analyze and summarize search results clearly
    - Provide comprehensive, well-organized responses
    - Cite sources when presenting information
    - Offer follow-up search suggestions when helpful
    - Always clarify question if necessary before answer
Search capabilities:
    - Use web_search for general information queries
    - Use search_news for current events and recent developments
    - Use search_images when visual content or image descriptions are needed
Important:
    - Do not make up the answer if it's out of search capabilities.
Always use the provided search tools to find current information rather than relying on training data.
Present findings clearly and organize information in a helpful, accessible format.
"""

    def create_agent_node(self):
        """Create a graph node that injects the current time into the system prompt."""

        def agent_node(state: dict) -> dict:
            """Callable agent node that formats the prompt before invoking the model."""
            prompt_template = self.get_system_prompt()
            current_time_utc = datetime.now(timezone.utc).isoformat()
            formatted_prompt = prompt_template.format(current_time=current_time_utc)

            messages = [SystemMessage(content=formatted_prompt)] + state["messages"]
            response = self._bound_model.invoke(messages)
            return {"messages": [response]}

        return agent_node
