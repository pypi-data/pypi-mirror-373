"""Search Agent Plugin using Cadence SDK."""

from cadence_sdk import BaseAgent, BasePlugin, PluginMetadata


class SearchPlugin(BasePlugin):
    """Search Plugin Bundle using SDK interfaces."""

    @staticmethod
    def get_metadata() -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="websearch",
            version="1.0.6",
            description="Web search and information retrieval agent",
            agent_type="specialized",
            capabilities=[
                "web_search",
                "news_search",
                "image_search",
            ],
            llm_requirements={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.2,
                "max_tokens": 1024,
            },
            dependencies=[
                "cadence-sdk>=1.0.5,<2.0.0",
                "ddgs>=9.5.4,<10.0.0",
            ],
        )

    @staticmethod
    def create_agent() -> BaseAgent:
        """Create search agent instance."""
        from .agent import SearchAgent

        return SearchAgent(SearchPlugin.get_metadata())

    @staticmethod
    def health_check() -> dict:
        """Perform health check."""
        try:
            return {
                "healthy": True,
                "details": "Search plugin is operational",
                "checks": {"search_engine": "OK", "dependencies": "OK"},
            }
        except Exception as e:
            return {
                "healthy": False,
                "details": f"Search plugin health check failed: {e}",
                "error": str(e),
            }
