import json
import logging
import os
from typing import Any, Dict, List, Optional

import aiohttp

# Dhisana utils (adjust imports to your project structure)
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ────────────────────────────────────────────────────────────────
# 1. API-key retrieval helper (mirrors your existing pattern)
# ────────────────────────────────────────────────────────────────
def get_serper_dev_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Grab SERPER_API_KEY from tool_config or environment.

    Raises:
        ValueError: If the Serper.dev integration has not been configured.
    """
    SERPER_API_KEY = None
    if tool_config:
        serper_cfg = next(
            (c for c in tool_config if c.get("name") == "serperdev"), None
        )
        if serper_cfg:
            kv = {i["name"]: i["value"] for i in serper_cfg.get("configuration", [])}
            SERPER_API_KEY = kv.get("apiKey")
    SERPER_API_KEY = SERPER_API_KEY or os.getenv("SERPER_API_KEY")
    if not SERPER_API_KEY:
        raise ValueError(
            "Serper.dev integration is not configured. Please configure the connection to Serper.dev in Integrations."
        )
    return SERPER_API_KEY


# ────────────────────────────────────────────────────────────────
# 2. Result normaliser
# ────────────────────────────────────────────────────────────────
def _normalise_local_result_serper(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a Serper 'places' / 'placeResults' item onto Dhisana's schema.
    """
    cid = raw.get("cid") or raw.get("placeId") or raw.get("place_id")
    maps_url = f"https://maps.google.com/?cid={cid}" if cid else ""

    return {
        "full_name":            raw.get("title", ""),
        "organization_name":    raw.get("title", ""),
        "phone":                raw.get("phoneNumber") or raw.get("phone", ""),
        "organization_website": raw.get("website", ""),
        "rating":               raw.get("rating"),
        "reviews":              raw.get("reviews"),
        "address":              raw.get("address", ""),
        "google_maps_url":      maps_url,
    }


# ────────────────────────────────────────────────────────────────
# 3. Search helper (decorated for Dhisana agents)
# ────────────────────────────────────────────────────────────────
@assistant_tool
async def search_local_business_serper(
    query: str,
    number_of_results: int = 20,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    location: Optional[str] = None,
) -> List[str]:
    """
    Fetch Google-Maps local business results via Serper.dev and return a
    List[str] of JSON-encoded business objects in Dhisana's schema.

    Args:
        query: Main search string (e.g. "coffee shops").
        number_of_results: Total rows desired.
        offset: Page offset (page index starts at 0).
        tool_config: Optional Dhisana tool-config containing the API key.
        location: Optional "San Jose, CA" style hint to refine results.
    """
    if not query:
        logger.warning("Empty query.")
        return []

    # ── caching
    cache_key = f"local_serper_{query}_{number_of_results}_{offset}_{location or ''}"
    cached = retrieve_output("search_local_serper", cache_key)
    if cached is not None:
        return cached

    api_key = get_serper_dev_api_access_token(tool_config)
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    url = "https://google.serper.dev/places"

    page_size = 20  # Serper returns ≤20 rows per page
    page = offset + 1
    collected: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession() as session:
        while len(collected) < number_of_results:
            payload = {
                "q": query,
                "page": page,
                "type": "places",   # explicit although /places path implies it
                "autocorrect": True,
                "gl": "us",
                "hl": "en",
            }
            if location:
                payload["location"] = location

            try:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        # Bubble up API errors
                        try:
                            err = await resp.json()
                        except Exception:
                            err = await resp.text()
                        logger.warning("Serper Places error: %s", err)
                        return [json.dumps({"error": err})]
                    data = await resp.json()
            except Exception as exc:
                logger.exception("Serper Places request failed.")
                return [json.dumps({"error": str(exc)})]

            # Handle both field names
            places = (
                data.get("places")
                or data.get("placeResults")
                or data.get("local_results")
                or []
            )
            if not places:
                break

            collected.extend(places)
            if len(collected) >= number_of_results:
                break
            page += 1

    # normalise → serialise
    serialised = [
        json.dumps(_normalise_local_result_serper(p))
        for p in collected[:number_of_results]
    ]
    cache_output("search_local_serper", cache_key, serialised)
    logger.info("Returned %d local businesses for '%s'", len(serialised), query)
    return serialised
