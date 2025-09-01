import json
import os
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ──────────────────────────────────────────────────────────────────────────
#  Re-use the get_serp_api_access_token helper you already have.
# ──────────────────────────────────────────────────────────────────────────
def _normalise_local_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a single SerpApi `local_results` item to the standard format.
    – Falls back to ''/None when fields are absent.
    – Derives `google_maps_url` from the `links.directions` entry when present,
      otherwise constructs a CID-based URL from data_cid / place_id.
    """
    # ── unpack links ──────────────────────────────────────────────────────────
    links = raw.get("links") or {}
    if isinstance(links, list):                     # older payloads: list of dicts
        links = {x.get("type") or x.get("name"): x.get("link")
                  for x in links if isinstance(x, dict)}

    # ── compute Google Maps URL ───────────────────────────────────────────────
    cid = raw.get("data_cid") or raw.get("place_id")
    google_maps_url = links.get("directions") or (f"https://maps.google.com/?cid={cid}" if cid else "")

    # ── return unified schema ─────────────────────────────────────────────────
    return {
        "full_name":            raw.get("title", ""),
        "organization_name":    raw.get("title", ""),
        "phone":                raw.get("phone") or raw.get("phone_number") or "",
        "organization_website": raw.get("website") or links.get("website") or "",
        "rating":               raw.get("rating"),
        "reviews":              raw.get("reviews"),
        "address":              raw.get("address", ""),
        "google_maps_url":      google_maps_url,
    }


@assistant_tool
async def search_local_business_serpai(
    query: str,
    number_of_results: int = 20,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    location: Optional[str] = None,
) -> List[str]:
    """
    Fetch Google Local results with SerpApi and return a list of businesses
    normalised to Dhisana's local-business schema (serialized as JSON strings).

    Args:
        query:               Search term (e.g. "coffee shops near me").
        number_of_results:   Total items desired.
        offset:              Result offset (multiples of 20 on desktop).
        tool_config:         Optional Dhisana tool-config blob holding the API key.
        location:            Optional human location string (e.g. "San Jose, CA").
    """
    if not query:
        logger.warning("Empty query string provided.")
        return []

    # ── cache key
    cache_key = f"local_{query}_{number_of_results}_{offset}_{location or ''}"
    cached = retrieve_output("search_local_serp", cache_key)
    if cached is not None:
        return cached

    # ── api key
    from your_module import get_serp_api_access_token  # adjust import if needed
    SERPAPI_KEY = get_serp_api_access_token(tool_config)

    page_size = 20               # Google Local desktop page size
    start_index = offset
    collected: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession() as session:
        while len(collected) < number_of_results:
            to_fetch = min(page_size, number_of_results - len(collected))

            params = {
                "engine": "google_local",
                "type": "search",
                "q": query,
                "api_key": SERPAPI_KEY,
                "start": start_index,
                "num": to_fetch,
            }
            if location:
                params["location"] = location

            logger.debug("SerpApi local request params: %s", params)

            try:
                async with session.get("https://serpapi.com/search", params=params) as resp:
                    if resp.status != 200:
                        try:
                            err = await resp.json()
                        except Exception:
                            err = await resp.text()
                        logger.warning("SerpApi error: %s", err)
                        return [json.dumps({"error": err})]
                    payload = await resp.json()
            except Exception as exc:
                logger.exception("Request failed.")
                return [json.dumps({"error": str(exc)})]

            local_results = payload.get("local_results", [])
            if not local_results:
                break

            collected.extend(local_results)
            start_index += to_fetch

    # truncate & normalise
    normalised = [_normalise_local_result(r) for r in collected[:number_of_results]]
    serialised = [json.dumps(item) for item in normalised]

    cache_output("search_local_serp", cache_key, serialised)
    logger.info("Returned %d local businesses for '%s'", len(serialised), query)
    return serialised
