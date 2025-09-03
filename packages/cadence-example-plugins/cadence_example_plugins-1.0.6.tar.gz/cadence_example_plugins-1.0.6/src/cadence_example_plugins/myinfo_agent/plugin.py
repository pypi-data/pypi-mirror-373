from cadence_sdk import BaseAgent, BasePlugin, PluginMetadata


class MyInfoPlugin(BasePlugin):
    @staticmethod
    def get_metadata() -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="myinfo",
            version="1.0.6",
            description="Chatbot - self introduction, information",
            agent_type="specialized",
            capabilities=["my_info"],
            llm_requirements={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.1,
                "max_tokens": 1024,
            },
            dependencies=["cadence-sdk>=1.0.5,<2.0.0"],
        )

    @staticmethod
    def create_agent() -> BaseAgent:
        """Create math agent instance."""
        from .agent import MyInfoAgent

        return MyInfoAgent(MyInfoPlugin.get_metadata())
