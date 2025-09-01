import json
import logging
import os
from typing import Any, Dict, List, Optional

import aiohttp

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_serper_dev_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """Retrieve the SERPER_API_KEY from tool_config or environment.

    Raises:
        ValueError: If the Serper.dev integration has not been configured.
    """
    key = None
    if tool_config:
        cfg = next((c for c in tool_config if c.get("name") == "serperdev"), None)
        if cfg:
            kv = {i["name"]: i["value"] for i in cfg.get("configuration", [])}
            key = kv.get("apiKey")
    key = key or os.getenv("SERPER_API_KEY")
    if not key:
        raise ValueError(
            "Serper.dev integration is not configured. Please configure the connection to Serper.dev in Integrations."
        )
    return key


def _normalise_job_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map a Serper job result onto a simplified schema."""
    apply_link = ""
    if isinstance(raw.get("apply_link"), str):
        apply_link = raw.get("apply_link")
    apply_options = raw.get("apply_options") or raw.get("apply_links") or []
    if not apply_link and isinstance(apply_options, list) and apply_options:
        first = apply_options[0]
        if isinstance(first, dict):
            apply_link = first.get("link") or first.get("apply_link") or ""

    return {
        "job_title": raw.get("title", ""),
        "company_name": raw.get("company_name") or raw.get("company", ""),
        "location": raw.get("location", ""),
        "via": raw.get("via", ""),
        "description": raw.get("description", ""),
        "job_posting_url": raw.get("link") or apply_link,
    }


@assistant_tool
async def search_google_jobs_serper(
    query: str,
    number_of_results: int = 10,
    offset: int = 0,
    tool_config: Optional[List[Dict]] = None,
    location: Optional[str] = None,
) -> List[str]:
    """Search Google Jobs via Serper.dev and return normalised JSON strings."""
    if not query:
        logger.warning("Empty query provided to search_google_jobs_serper")
        return []

    cache_key = f"jobs_serper_{query}_{number_of_results}_{offset}_{location or ''}"
    cached = retrieve_output("search_google_jobs_serper", cache_key)
    if cached is not None:
        return cached

    api_key = get_serper_dev_api_access_token(tool_config)
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    url = "https://google.serper.dev/search"  # ← fixed endpoint

    page = offset + 1
    collected: List[Dict[str, Any]] = []

    async with aiohttp.ClientSession() as session:
        while len(collected) < number_of_results:
            payload = {
                "q": query,
                "page": page,
                "type": "jobs",        # keeps us in the Jobs vertical
                "autocorrect": True,
                "gl": "us",
                "hl": "en",
            }
            if location:
                payload["location"] = location
            try:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        try:
                            err = await resp.json()
                        except Exception:
                            err = await resp.text()
                        logger.warning("Serper jobs error: %s", err)
                        return [json.dumps({"error": err})]
                    data = await resp.json()
            except Exception as exc:
                logger.exception("Serper jobs request failed")
                return [json.dumps({"error": str(exc)})]

            jobs = (
                data.get("jobs")
                or data.get("job_results")
                or data.get("jobs_results")
                or []
            )
            if not jobs:
                break
            collected.extend(jobs)
            if len(collected) >= number_of_results:
                break
            page += 1

    serialised = [
        json.dumps(_normalise_job_result(j)) for j in collected[:number_of_results]
    ]
    cache_output("search_google_jobs_serper", cache_key, serialised)
    logger.info("Returned %d job results for '%s'", len(serialised), query)
    return serialised
