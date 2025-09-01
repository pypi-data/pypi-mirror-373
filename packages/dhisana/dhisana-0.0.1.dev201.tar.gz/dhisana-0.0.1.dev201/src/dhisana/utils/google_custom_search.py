import asyncio
import json
import logging
import os
import aiohttp
from typing import Any, Dict, List, Optional

import backoff
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import retrieve_output, cache_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_google_custom_search_keys(tool_config: Optional[List[Dict]] = None) -> (str, str):
    """
    Retrieve the Google Custom Search API key (GOOGLE_SEARCH_KEY) and CX
    from the provided tool_config or environment variables.

    tool_config example:
    [
      {
        "name": "google_custom_search",
        "configuration": [
          {"name": "apiKey", "value": "XXX"},
          {"name": "cx", "value": "YYY"}
        ]
      }
    ]

    Returns:
        (api_key, cx) tuple.

    Raises:
        ValueError: If the Google Custom Search integration has not been configured.
    """
    api_key = None
    cx = None

    if tool_config:
        logger.debug("Looking for Google Custom Search config in tool_config.")
        gcs_config = next((cfg for cfg in tool_config if cfg.get("name") == "google_custom_search"), None)
        if gcs_config:
            config_map = {
                item["name"]: item["value"]
                for item in gcs_config.get("configuration", [])
                if item
            }
            api_key = config_map.get("apiKey")
            cx = config_map.get("cx")
        else:
            logger.debug("No 'google_custom_search' config item found in tool_config.")

    # Fall back to environment variables if not found in tool_config
    api_key = api_key or os.environ.get('GOOGLE_SEARCH_KEY')
    cx = cx or os.environ.get('GOOGLE_SEARCH_CX')

    if not api_key or not cx:
        raise ValueError(
            "Google Custom Search integration is not configured. Please configure the connection to Google Custom Search in Integrations."
        )

    return api_key, cx


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=60,
)
async def search_google_custom_search(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    as_oq: Optional[str] = None
) -> List[str]:
    """
    Search Google using the Google Custom Search JSON API and return the results
    as a list of JSON strings in SerpAPI-like format:
      { "position", "title", "link", "snippet" }

    Parameters:
    - query (str): The search query.
    - number_of_results (int): The number of results to return. Default 10.
    - offset (int): The index offset for results (pagination). Default 0.
    - tool_config (Optional[List[Dict]]): Tool config containing "google_custom_search" keys.
    - as_oq (Optional[str]): Optional additional query terms, appended to 'query'.
    
    Returns:
    - List[str]: A list of JSON-serialized objects each containing title/link/snippet/position.
    """
    logger.info("Entering search_google_custom_search")

    # Construct the final query
    full_query = query
    if as_oq:
        full_query += f" {as_oq}"

    # Retrieve keys from tool_config or environment
    try:
        api_key, cx = get_google_custom_search_keys(tool_config)
    except ValueError as e:
        error_msg = str(e)
        logger.error(error_msg)
        return [json.dumps({"error": error_msg})]

    # We apply pagination via "start" parameter in Google Custom Search
    # "start" = 1 means the 1st result; offset means skip 'offset' results
    # So if offset=0 => start=1, if offset=10 => start=11, etc.
    start_index = offset + 1

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": full_query,
        "num": number_of_results,
        "start": start_index
    }

    cache_key = f"{full_query}_{number_of_results}_{offset}"
    cached_response = retrieve_output("search_google_custom_search", cache_key)
    if cached_response is not None:
        logger.info("Cache hit for search_google_custom_search.")
        return cached_response

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()

                    # Check for spelling suggestion
                    if "spelling" in result and "correctedQuery" in result["spelling"]:
                        corrected_query = result["spelling"]["correctedQuery"]
                        logger.warning(f"Spelling suggestion detected ({corrected_query}). Retrying with original query.")
                        # Force original query (no changes).
                        params["q"] = full_query
                        async with session.get(url, params=params) as retry_response:
                            if retry_response.status == 200:
                                retry_result = await retry_response.json()
                                normalized_results = _normalize_google_items(retry_result.get('items', []))
                            else:
                                retry_content = await retry_response.text()
                                return [json.dumps({"error": retry_content})]
                    else:
                        # Normal path
                        normalized_results = _normalize_google_items(result.get('items', []))

                    serialized_results = [json.dumps(item) for item in normalized_results]
                    cache_output("search_google_custom_search", cache_key, serialized_results)
                    await asyncio.sleep(1)  # small delay (optional)
                    return serialized_results

                elif response.status == 429:
                    logger.warning("search_google_custom_search: Rate limit (429).")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message="Rate limit exceeded",
                        headers=response.headers
                    )
                else:
                    error_json = await response.json()
                    logger.warning(f"search_google_custom_search request failed: {error_json}")
                    return [json.dumps({"error": error_json})]

    except aiohttp.ClientResponseError:
        # Let backoff handle the re-raise
        raise
    except Exception as e:
        logger.exception("Exception during search_google_custom_search.")
        return [json.dumps({"error": str(e)})]


def _normalize_google_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert Google Custom Search 'items' into SerpAPI/Serper.dev-like format:
        { position, title, link, snippet }
    """
    normalized = []
    for i, item in enumerate(items):
        normalized_item = {
            "position": i + 1,
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", "")
        }
        normalized.append(normalized_item)
    return normalized


@assistant_tool
async def search_google_places(
    query: str,
    location_bias: dict = None,
    number_of_results: int = 3
):
    """
    Search Google Places API (New) and return the results as an array of serialized JSON strings.

    Parameters:
    - **query** (*str*): The search query.
    - **location_bias** (*dict*): Optional. A dictionary with 'latitude', 'longitude', and 'radius' (in meters) to bias the search.
    - **number_of_results** (*int*): The number of results to return.
    """
    GOOGLE_SEARCH_KEY = os.environ.get('GOOGLE_SEARCH_KEY')
    if not GOOGLE_SEARCH_KEY:
        return {
            'error': "Google Places integration is not configured. Please configure the connection to Google Places in Integrations."
        }

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_SEARCH_KEY,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.websiteUri,places.rating,places.reviews'
    }

    request_body = {
        "textQuery": query
    }

    if location_bias:
        request_body["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": location_bias.get("latitude"),
                    "longitude": location_bias.get("longitude")
                },
                "radius": location_bias.get("radius", 5000)  # Default to 5 km if radius not provided
            }
        }

    # Create a cache key that includes query, number_of_results, and location_bias
    location_bias_str = json.dumps(location_bias, sort_keys=True) if location_bias else "None"
    cache_key = f"{query}:{number_of_results}:{location_bias_str}"
    cached_response = retrieve_output("search_google_places", cache_key)
    if cached_response is not None:
        return cached_response

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=request_body) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result.get('error', {}).get('message', 'Unknown error')}

                # Extract the required number of results
                places = result.get('places', [])[:number_of_results]

                # Serialize each place result to JSON string
                serialized_results = [json.dumps(place) for place in places]

                # Cache the response
                cache_output("search_google_places", cache_key, serialized_results)

                return serialized_results
    except Exception as e:
        return {'error': str(e)}

