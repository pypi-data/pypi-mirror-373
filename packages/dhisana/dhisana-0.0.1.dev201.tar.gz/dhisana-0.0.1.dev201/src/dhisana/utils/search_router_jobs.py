import json
import logging
from typing import Any, Dict, List, Optional

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.search_router import detect_search_provider
from dhisana.utils.serperdev_google_jobs import search_google_jobs_serper
from dhisana.utils.serpapi_google_jobs import search_google_jobs_serpapi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@assistant_tool
async def search_google_jobs_with_tools(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    location: Optional[str] = None,
) -> List[str]:
    """Router that searches Google Jobs using the configured provider."""
    if not query:
        logger.warning("Empty query received by jobs router")
        return []

    provider = detect_search_provider(tool_config)
    logger.debug("Jobs router chose provider: %s", provider)

    if provider == "serperdev":
        logger.info("Routing to Serper.dev job search helper")
        return await search_google_jobs_serper(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            location=location,
        )

    if provider == "serpapi":
        logger.info("Routing to SerpApi job search helper")
        return await search_google_jobs_serpapi(
            query=query,
            number_of_results=number_of_results,
            offset=offset,
            tool_config=tool_config,
            location=location,
        )

    logger.error("No supported jobs provider found in tool_config")
    return [json.dumps({"error": "No supported jobs provider configured."})]
