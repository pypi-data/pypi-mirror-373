import json
import logging
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dhisana.utils.assistant_tool_tag import assistant_tool

# Adjust these imports to your actual module paths:
from dhisana.utils.serpapi_google_search import search_google_serpai
from dhisana.utils.serperdev_search import search_google_serper
from dhisana.utils.google_custom_search import search_google_custom_search
# Only SERP API Supported as of now

def detect_search_provider(tool_config: Optional[List[Dict]] = None) -> Optional[str]:
    """
    Detect which search provider is available in tool_config, in priority order:
    1. serperdev
    2. serpapi
    3. google_custom_search

    Returns:
        - 'serperdev' if Serper.dev config is found
        - 'serpapi' if SerpAPI config is found
        - 'google_custom_search' if Custom Search config is found
        - None if no known provider config is found
    """
    if not tool_config:
        return None

    # 1) Check if 'serperdev' provider is available
    serper_config = next((cfg for cfg in tool_config if cfg.get("name") == "serperdev"), None)
    if serper_config:
        config_map = {
            item["name"]: item["value"]
            for item in serper_config.get("configuration", [])
            if item
        }
        if "apiKey" in config_map and config_map["apiKey"]:
            return "serperdev"

    # # 2) Check if 'serpapi' provider is available
    serpapi_config = next((cfg for cfg in tool_config if cfg.get("name") == "serpapi"), None)
    if serpapi_config:
        config_map = {
            item["name"]: item["value"]
            for item in serpapi_config.get("configuration", [])
            if item
        }
        if "apiKey" in config_map and config_map["apiKey"]:
            return "serpapi"

    # 3) Check if 'google_custom_search' is available
    custom_search_config = next((cfg for cfg in tool_config if cfg.get("name") == "google_custom_search"), None)
    if custom_search_config:
        config_map = {
            item["name"]: item["value"]
            for item in custom_search_config.get("configuration", [])
            if item
        }
        if "apiKey" in config_map and "cx" in config_map:
            return "google_custom_search"

    # No recognized provider found
    return None


@assistant_tool
async def search_google_with_tools(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    as_oq: Optional[str] = None
) -> List[str]:
    """
    Common router function that searches using whichever provider is available in tool_config:
      1. Serper.dev (priority)
      2. SerpAPI
      3. Google Custom Search (last fallback)

    Parameters:
    - query (str): The search query
    - number_of_results (int): Number of results to return
    - offset (int): Offset for pagination or 'page' for some providers
    - tool_config (Optional[List[Dict]]): Configuration for possible providers
    - as_oq (Optional[str]): Additional optional search terms appended to 'query'

    Returns:
    - List[str]: A list of JSON-serialized results, or an error message if no provider is available.
    """
    logger.info("Entering search_google_with_tools")

    if not query:
        logger.warning("Empty query string provided to search_google_with_tools.")
        return []

    provider = detect_search_provider(tool_config)
    logger.debug(f"Detected provider: {provider}")

    if provider == "serperdev":
        logger.info("Using Serper.dev provider")
        return await search_google_serper(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            as_oq=as_oq
        )
    elif provider == "serpapi":
        logger.info("Using SerpAPI provider")
        return await search_google_serpai(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            as_oq=as_oq
        )
    elif provider == "google_custom_search":
        logger.info("Using Google Custom Search provider")
        return await search_google_custom_search(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            as_oq=as_oq
        )
    else:
        logger.error("No supported search provider found in tool_config.")
        return [json.dumps({"error": "No supported search provider found."})]
