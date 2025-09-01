import json
import os
from typing import Dict, List, Optional
import aiohttp

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_serp_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the SERPAPI_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The SERPAPI_KEY access token.

    Raises:
        ValueError: If the SerpAPI integration has not been configured.
    """
    logger.info("Entering get_serp_api_access_token")
    SERPAPI_KEY = None

    if tool_config:
        logger.debug(f"Tool config provided: {tool_config}")
        serpapi_config = next(
            (item for item in tool_config if item.get("name") == "serpapi"), None
        )
        if serpapi_config:
            config_map = {
                item["name"]: item["value"]
                for item in serpapi_config.get("configuration", [])
                if item
            }
            SERPAPI_KEY = config_map.get("apiKey")
        else:
            logger.warning("No 'serpapi' config item found in tool_config.")
    else:
        logger.debug("No tool_config provided or it's None.")

    SERPAPI_KEY = SERPAPI_KEY or os.getenv("SERPAPI_KEY")
    if not SERPAPI_KEY:
        logger.error("SerpAPI integration is not configured.")
        raise ValueError(
            "SerpAPI integration is not configured. Please configure the connection to SerpAPI in Integrations."
        )

    logger.info("Retrieved SERPAPI_KEY successfully.")
    return SERPAPI_KEY


@assistant_tool
async def search_google_serpai(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    as_oq: Optional[str] = None,   # optional terms
) -> List[str]:
    """
    Google search via SerpAPI that returns a *uniform* list of JSON strings.
    Each item is guaranteed to contain a 'link' key, even when the result
    originally came from image/news blocks.

    Blocks handled:
        • organic_results   – keeps SerpAPI structure
        • inline_images     – maps  source  -> link
        • news_results      – already has link
    """
    logger.info("Entering search_google_serpai")
    if not query:
        logger.warning("Empty query string provided.")
        return []

    cache_key = f"{query}_{number_of_results}_{offset}_{as_oq or ''}"
    if cached := retrieve_output("search_google_serp", cache_key):
        logger.info("Cache hit for search_google_serp.")
        return cached

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    base_url    = "https://serpapi.com/search"

    page_size     = number_of_results
    start_index   = 0 if offset == 0 else offset + 1  # SerpAPI Pagination Mechanism: Uses the start parameter to specify the first result (zero-indexed)
    all_items: list[dict] = []
    seen_links:   set[str] = set()     # dedupe across blocks/pages

    # ------------------------------------------------------------------ #
    # helpers                                                            #
    # ------------------------------------------------------------------ #
    def _extract_block_results(block: str, data: list[dict]) -> list[dict]:
        """Return items from a given block in unified format (must include link)."""
        mapped: list[dict] = []

        if block == "organic_results":
            for it in data:
                link = it.get("link")
                if link:
                    mapped.append(it)                   # keep original shape
        elif block == "inline_images":
            for it in data:
                link = it.get("source")                 # image-pack URL
                if link:
                    mapped.append({
                        "title":  it.get("title"),
                        "link":   link,
                        "type":  "inline_image",
                        "source_name": it.get("source_name"),
                        "thumbnail":  it.get("thumbnail"),
                    })
        elif block == "news_results":
            for it in data:
                link = it.get("link")
                if link:
                    mapped.append(it)                   # already fine
        return mapped
    # ------------------------------------------------------------------ #

    async with aiohttp.ClientSession() as session:
        while len(all_items) < number_of_results:
            to_fetch = min(page_size, number_of_results - len(all_items))
            params = {
                "engine":   "google",
                "api_key":  SERPAPI_KEY,
                "q":        query,
                "num":      to_fetch,
                "start":    start_index,
                "location": "United States",
            }
            if as_oq:
                params["as_oq"] = as_oq

            logger.debug(f"SERP API GET → {params}")

            try:
                async with session.get(base_url, params=params) as resp:
                    if resp.status != 200:
                        try:
                            err = await resp.json()
                        except Exception:
                            err = await resp.text()
                        logger.warning(f"SerpAPI {resp.status=}: {err}")
                        return [json.dumps({"error": err})]
                    result = await resp.json()
            except Exception as e:
                logger.exception("SerpAPI request failed")
                return [json.dumps({"error": str(e)})]

            # ------------------ harvest every supported block ------------------
            page_items: list[dict] = []
            for block_name in ("organic_results", "inline_images", "news_results"):
                data = result.get(block_name) or []
                page_items.extend(_extract_block_results(block_name, data))

            # dedupe & accumulate
            new_added = 0
            for it in page_items:
                link = it["link"]
                if link not in seen_links:
                    seen_links.add(link)
                    all_items.append(it)
                    new_added += 1
                    if len(all_items) >= number_of_results:
                        break
            logger.debug(f"Added {new_added} items (total={len(all_items)})")

            # stop if Google gave us nothing new
            if new_added == 0:
                logger.debug("No more items returned; stopping.")
                break

            start_index += to_fetch   # next Google results page

    # truncate and serialise
    all_items = all_items[:number_of_results]
    serialised = [json.dumps(it) for it in all_items]
    cache_output("search_google_serp", cache_key, serialised)

    logger.info(f"Returning {len(serialised)} items for '{query}'")
    return serialised