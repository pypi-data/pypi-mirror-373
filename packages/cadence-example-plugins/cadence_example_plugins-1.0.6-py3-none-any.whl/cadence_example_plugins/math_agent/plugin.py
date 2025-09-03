"""Math Agent Plugin using Cadence SDK."""

from cadence_sdk import BaseAgent, BasePlugin, PluginMetadata


class MathPlugin(BasePlugin):
    """Math Plugin Bundle using SDK interfaces."""

    @staticmethod
    def get_metadata() -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="mathematics",
            version="1.0.6",
            description="Mathematical calculations and arithmetic operations agent",
            agent_type="specialized",
            capabilities=["addition", "subtraction", "multiplication", "division", "power", "modulo"],
            llm_requirements={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.2,
                "max_tokens": 1024,
            },
            dependencies=["cadence-sdk>=1.0.5,<2.0.0"],
        )

    @staticmethod
    def create_agent() -> BaseAgent:
        """Create math agent instance."""
        from .agent import MathAgent

        return MathAgent(MathPlugin.get_metadata())

    @staticmethod
    def health_check() -> dict:
        """Perform health check."""
        try:
            from .tools import add, multiply, subtract

            # The @tool decorator returns a LangChain Tool object. When called directly,
            # it expects a Runnable config, causing errors like "'int' has no attribute parent_run_id".
            # Use the underlying Python function if available (Tool.func), otherwise the object itself.
            add_func = getattr(add, "func", add)
            subtract_func = getattr(subtract, "func", subtract)
            multiply_func = getattr(multiply, "func", multiply)

            assert add_func(2, 3) == 5
            assert subtract_func(5, 3) == 2
            assert multiply_func(2, 4) == 8

            return {
                "healthy": True,
                "details": "Math plugin is operational",
                "checks": {"basic_operations": "OK", "tool_availability": "OK"},
            }
        except Exception as e:
            return {
                "healthy": False,
                "details": f"Math plugin health check failed: {e}",
                "error": str(e),
            }
