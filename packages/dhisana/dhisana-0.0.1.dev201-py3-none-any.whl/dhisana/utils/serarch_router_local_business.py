import json
import logging
from typing import Any, Dict, List, Optional

from dhisana.utils.assistant_tool_tag import assistant_tool

# Your provider-specific helpers (paths may differ in your repo)
from dhisana.utils.serperdev_local_business import search_local_business_serper
from dhisana.utils.serpapi_local_business_search import search_local_business_serpai

# Re-use your existing provider detector
from dhisana.utils.search_router import detect_search_provider  # or copy the function shown earlier

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@assistant_tool
async def search_local_business_with_tools(
    query: str,
    number_of_results: int = 20,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    location: Optional[str] = None,
) -> List[str]:
    """
    Router that returns local-business (Google Maps) results using whichever
    provider is configured in `tool_config`.

    Priority order:
      1. Serper.dev   – uses `search_local_business_serper`
      2. SerpApi      – uses `search_local_business_serpai`

    Args:
        query:               Search string (e.g. "plumbers near Almaden Valley").
        number_of_results:   Desired row count (will paginate if > provider page size).
        offset:              Page offset (0-based; converted to provider-specific page or start).
        tool_config:         Dhisana tool-configuration blob listing available providers.
        location:            Optional city/region hint (Serper + SerpApi both accept it).

    Returns:
        List[str]: Each element is a JSON-encoded dict with keys:
                   full_name, organization_name, phone, organization_website,
                   rating, reviews, address, google_maps_url.
                   If no provider is configured, returns one item with an "error" key.
    """
    if not query:
        logger.warning("Empty query received by local-business router.")
        return []

    provider = detect_search_provider(tool_config)
    logger.debug("Local-business router chose provider: %s", provider)

    if provider == "serperdev":
        logger.info("Routing to Serper.dev local-business helper.")
        return await search_local_business_serper(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            location=location,
        )

    if provider == "serpapi":
        logger.info("Routing to SerpApi local-business helper.")
        return await search_local_business_serpai(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            location=location,
        )

    logger.error("No supported local-business provider found in tool_config.")
    return [json.dumps({"error": "No supported local-business provider configured."})]
