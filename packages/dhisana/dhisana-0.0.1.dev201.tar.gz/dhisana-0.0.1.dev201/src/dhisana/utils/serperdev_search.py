import json
import os
from typing import Any, Dict, List, Optional
import aiohttp

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# If you have these utils in your project, import them; otherwise, remove them or replace them.
from dhisana.utils.cache_output_tools import cache_output, retrieve_output


def get_serper_dev_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the Serper.dev API access token from the provided tool configuration
    or from the SERPER_API_KEY environment variable.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration.
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The Serper.dev API access token.

    Raises:
        ValueError: If the Serper.dev integration has not been configured.
    """
    logger.info("Entering get_serper_dev_api_access_token")
    SERPER_API_KEY = None

    if tool_config:
        logger.debug(f"Tool config provided: {tool_config}")
        serper_config = next(
            (item for item in tool_config if item.get("name") == "serperdev"), None
        )
        if serper_config:
            config_map = {
                item["name"]: item["value"]
                for item in serper_config.get("configuration", [])
                if item
            }
            SERPER_API_KEY = config_map.get("apiKey")
        else:
            logger.warning("No 'serperdev' config item found in tool_config.")
    else:
        logger.debug("No tool_config provided or it's None.")

    SERPER_API_KEY = SERPER_API_KEY or os.getenv("SERPER_API_KEY")
    if not SERPER_API_KEY:
        logger.error("Serper.dev integration is not configured.")
        raise ValueError(
            "Serper.dev integration is not configured. Please configure the connection to Serper.dev in Integrations."
        )

    logger.info("Retrieved SERPER_API_KEY successfully.")
    return SERPER_API_KEY



async def search_google_serper(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    as_oq: Optional[str] = None
) -> List[str]:
    """
    Search Google using Serper.dev. Mimics the signature and usage of the old SerpAPI function,
    and normalizes the response JSON objects so that they contain:
      - "title"
      - "link"
      - "snippet"
      - "position"

    This ensures consistency with SerpAPI-based code.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The total number of results to return. Default is 10.
    - offset (int): The "page offset" to start from (used to compute the page).
    - tool_config (Optional[List[Dict]]): Configuration containing the Serper.dev API token, etc.
    - as_oq (Optional[str]): Optional additional query terms, appended to 'query'.
    
    Returns:
    - List[str]: A list of organic search results, each serialized as a JSON string 
                 with "title", "link", "snippet", and "position".
    """
    logger.info("Entering search_google_serper")

    if not query:
        logger.warning("Empty query string provided.")
        return []

    # Combine main query with optional terms
    full_query = query
    if as_oq:
        full_query += f" {as_oq}"

    # Check cache
    cache_key = f"{full_query}_{number_of_results}_{offset}"
    cached_response = retrieve_output("search_google_serper", cache_key)
    if cached_response is not None:
        logger.info("Cache hit for search_google_serper.")
        return cached_response

    # Retrieve your Serper.dev API key (replace with your own function if needed)
    SERPER_API_KEY = get_serper_dev_api_access_token(tool_config)

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    # Serper.dev uses 'page' to paginate. We need to calculate the page number based on offset.
    # Serper.dev uses 1-based indexing for pages, so we need to adjust accordingly
    # e.g., if offset is 0, we want page 1; if offset is 10, we want page 2, etc.
    # Assuming number_of_results is the number of results per page.
    # If offset is 0, we want the first page,
    # if offset is 10 and number_of_results is 10, we want the second page, etc.
    # This means we can calculate the page as follows:
    # page = (offset // number_of_results) + 1
    # If offset is 0, page will be 1; if offset is 10 and number_of_results is 10, page will be 2.
    # This is consistent with how Serper.dev handles pagination.
    page = 1 if offset == 0 else (offset // number_of_results) + 1
    all_results: List[Dict[str, Any]] = []

    # We'll collect results from "organic", converting each to a SerpAPI-like format.
    async with aiohttp.ClientSession() as session:
        while len(all_results) < number_of_results:
            payload = {
                "q": full_query,
                "gl": "us",        # geolocation
                "hl": "en",        # language
                "autocorrect": True,
                "page": page,
                "num": number_of_results,
                "type": "search"   # or 'news', 'images', etc., if needed
            }

            logger.debug(f"Requesting Serper.dev page {page} for query '{full_query}'.")
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        try:
                            error_content = await response.json()
                        except Exception:
                            error_content = await response.text()
                        logger.warning(f"Non-200 response from Serper.dev: {error_content}")
                        return [json.dumps({"error": error_content})]

                    result_json = await response.json()
            except Exception as e:
                logger.exception("Exception during Serper.dev request.")
                return [json.dumps({"error": str(e)})]

            organic_results = result_json.get("organic", [])
            if not organic_results:
                logger.debug("No more organic results returned; stopping.")
                break

            all_results.extend(organic_results)
            page += 1

            if len(all_results) >= number_of_results:
                break

    # Limit to the requested number_of_results
    all_results = all_results[:number_of_results]

    # Convert each Serper.dev result to a SerpAPI-like format
    # SerpAPI typically returns objects with keys: "position", "title", "link", "snippet", etc.
    normalized_results = []
    for idx, item in enumerate(all_results):
        # item from Serper.dev might have: { "title": "...", "link": "...", "snippet": "..." }
        # If the field name for snippet is different, change accordingly. 
        # But as of serper.dev docs, "snippet" is used.
        normalized_item = {
            "position": idx + 1,
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            # Copy any other fields if you want them
        }
        normalized_results.append(json.dumps(normalized_item))

    logger.info(f"Found {len(normalized_results)} normalized results for query '{full_query}'.")
    cache_output("search_google_serper", cache_key, normalized_results)

    return normalized_results

