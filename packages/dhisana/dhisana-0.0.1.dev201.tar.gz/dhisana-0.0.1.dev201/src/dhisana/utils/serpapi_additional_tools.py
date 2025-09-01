import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import urllib

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.web_download_parse_tools import fetch_html_content
from dhisana.utils.search_router import search_google_with_tools

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
async def search_google_maps(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google Maps using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_maps")
    if not query:
        logger.warning("Empty query string provided for search_google_maps.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_maps"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Maps with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('local_results', [])]
                logger.info(f"Returning {len(serialized_results)} map results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_maps request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_google_news(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google News using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_news")
    if not query:
        logger.warning("Empty query string provided for search_google_news.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_news"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google News with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('news_results', [])]
                logger.info(f"Returning {len(serialized_results)} news results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_news request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_job_postings(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search for job postings using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_job_postings")
    if not query:
        logger.warning("Empty query string provided for search_job_postings.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_jobs"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Jobs with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('jobs_results', [])]
                logger.info(f"Returning {len(serialized_results)} job posting results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_job_postings request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_google_images(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google Images using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_images")
    if not query:
        logger.warning("Empty query string provided for search_google_images.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_images"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Images with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('images_results', [])]
                logger.info(f"Returning {len(serialized_results)} image results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_images request.")
        return [json.dumps({"error": str(e)})]


@assistant_tool
async def search_google_videos(
    query: str,
    number_of_results: int,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google Videos using SERP API and return the results as an array of serialized JSON strings.
    
    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return.
    """
    logger.info("Entering search_google_videos")
    if not query:
        logger.warning("Empty query string provided for search_google_videos.")
        return []

    SERPAPI_KEY = get_serp_api_access_token(tool_config)
    params = {
        "q": query,
        "num": number_of_results,
        "api_key": SERPAPI_KEY,
        "engine": "google_videos"
    }
    url = "https://serpapi.com/search"

    logger.debug(f"Searching Google Videos with params: {params}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                logger.debug(f"Received status: {response.status}")
                result = await response.json()
                if response.status != 200:
                    logger.warning(f"Non-200 response from SERP API: {result}")
                    return [json.dumps({"error": result})]

                serialized_results = [json.dumps(item) for item in result.get('video_results', [])]
                logger.info(f"Returning {len(serialized_results)} video results.")
                return serialized_results
    except Exception as e:
        logger.exception("Exception during search_google_videos request.")
        return [json.dumps({"error": str(e)})]
