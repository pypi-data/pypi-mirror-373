"""Math Agent Implementation using Cadence SDK."""

from typing import List

from cadence_sdk import BaseAgent
from cadence_sdk.base.metadata import PluginMetadata


class MathAgent(BaseAgent):
    """Math operations and problem-solving agent using SDK."""

    def __init__(self, metadata: PluginMetadata):
        """Initialize the math agent."""
        super().__init__(metadata)

    def get_tools(self) -> List:
        """Get available math tools."""
        from .tools import math_tools

        return math_tools

    def get_system_prompt(self) -> str:
        """Get system prompt for the math agent."""
        return (
            "You are the Math Agent, specialized in mathematical operations and calculations. "
            "You have access to tools for: addition, subtraction, multiplication, division, "
            "exponentiation (power), and modulo operations. "
            "\n\n"
            "Always use the provided tools to perform calculations rather than doing math "
            "mentally. This ensures accuracy and allows the user to see your work."
            "Do not make up the answer if it's no tools suitable for calculation. \n"
        )
