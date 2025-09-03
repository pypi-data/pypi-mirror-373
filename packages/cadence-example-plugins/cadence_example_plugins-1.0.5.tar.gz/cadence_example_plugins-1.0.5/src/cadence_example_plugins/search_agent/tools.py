"""Search Agent Tools using Cadence SDK."""

from cadence_sdk import tool
from ddgs import DDGS


@tool
def web_search(query: str) -> str:
    """Search the web for information using DuckDuckGo.

    Args:
        query: The search query

    Returns:
        Search results from the web
    """
    try:
        results = DDGS().text(query)
        return results[:500]
    except Exception as e:
        return f"Web search error: {str(e)}"


@tool
def search_news(query: str) -> str:
    """Search for recent news articles.

    Args:
        query: The news search query

    Returns:
        News search results
    """
    try:
        results = DDGS().news(query)
        return results[:500]
    except Exception as e:
        return f"News search error: {str(e)}"


@tool
def search_images(query: str) -> str:
    """Search for images and visual content related to the query.

    Args:
        query: The image search query

    Returns:
        Description of image search results
    """
    try:
        results = DDGS().images(query)
        return results[:500]
    except Exception as e:
        return f"Image search error: {str(e)}"


search_tools = [web_search, search_news, search_images]
