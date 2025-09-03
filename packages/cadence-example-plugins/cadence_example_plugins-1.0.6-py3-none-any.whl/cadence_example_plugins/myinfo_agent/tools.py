import os

from cadence_sdk import tool


def _get_bot_config() -> dict:
    """Get bot configuration from environment variables."""
    return {
        "bot_name": os.environ.get("CADENCE_BOT_NAME", "Cadence AI"),
        "bot_description": os.environ.get("CADENCE_BOT_DESCRIPTION", "Multiple Agents Chatbot System"),
        "bot_creator": os.environ.get("CADENCE_BOT_CREATOR", "JonasKahn"),
        "bot_specialization": os.environ.get("CADENCE_BOT_SPECIALIZATION", "Business"),
        "bot_version": os.environ.get("CADENCE_BOT_VERSION", "1.0.6"),
    }


@tool
def my_info() -> str:
    """Get detail chatbot information"""
    config = _get_bot_config()
    return (
        f"I'm {config['bot_name']} - {config['bot_description']}, "
        f"I was specialized design for {config['bot_specialization']}, "
        f"created by {config['bot_creator']}, version {config['bot_version']}."
    )


my_info_tools = [my_info]
