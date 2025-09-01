import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel

from dhisana.utils.generate_structured_output_internal import get_structured_output_internal
from dhisana.utils.proxy_curl_tools import (
    get_proxycurl_access_token,
    fill_in_missing_properties,
    transform_company_data,
)
from dhisana.utils.cache_output_tools import cache_output
from urllib.parse import urlparse, urlunparse
from dhisana.utils.clean_properties import cleanup_properties
from dhisana.utils.assistant_tool_tag import assistant_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ────────────────────────────
# 🛠  Small generic helpers
# ────────────────────────────
def _remove_empty_values(d: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *d* without keys whose value is empty, None, or zero for integers."""
    cleaned = {}
    for k, v in d.items():
        # Skip None values
        if v is None:
            continue
        # Skip empty strings or whitespace-only strings
        elif isinstance(v, str) and v.strip() == "":
            continue
        # Skip empty lists/arrays
        elif isinstance(v, list) and len(v) == 0:
            continue
        # Skip zero values for integer fields (assuming they're not meaningful for search)
        elif isinstance(v, int) and v == 0:
            continue
        # Keep all other values
        else:
            cleaned[k] = v
    return cleaned


def _build_common_params(
    search_params: BaseModel,
    max_entries: int,
    enrich_profiles: bool,
) -> Dict[str, Any]:
    """Convert a Pydantic model into Proxycurl query params, removing empty/None values."""
    params = search_params.model_dump(exclude_none=True)
    params = _remove_empty_values(params)

    params["page_size"] = max_entries if max_entries > 0 else 5
    params["enrich_profiles"] = "enrich" if enrich_profiles else "skip"
    params["use_cache"] = "if-present"
    return params


# ────────────────────────────
# 📄  Search parameter schemas
# ────────────────────────────
class PeopleSearchParams(BaseModel):
    current_role_title: Optional[str] = None
    current_company_industry: Optional[str] = None
    current_company_employee_count_min: Optional[int] = None
    current_company_employee_count_max: Optional[int] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    summary: Optional[str] = None
    current_job_description: Optional[str] = None
    past_job_description: Optional[str] = None


class CompanySearchParams(BaseModel):
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    type: Optional[str] = None
    follower_count_min: Optional[int] = None
    follower_count_max: Optional[int] = None
    name: Optional[str] = None
    industry: Optional[str] = None
    employee_count_max: Optional[int] = None
    employee_count_min: Optional[int] = None
    description: Optional[str] = None
    founded_after_year: Optional[int] = None
    founded_before_year: Optional[int] = None
    funding_amount_max: Optional[int] = None
    funding_amount_min: Optional[int] = None
    funding_raised_after: Optional[str] = None
    funding_raised_before: Optional[str] = None
    public_identifier_in_list: Optional[str] = None
    public_identifier_not_in_list: Optional[str] = None


class JobSearchParams(BaseModel):
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    when: Optional[str] = None
    flexibility: Optional[str] = None
    geo_id: Optional[int] = None
    keyword: Optional[str] = None
    search_id: Optional[str] = None


# ────────────────────────────
# 👤  People search
# ────────────────────────────
@assistant_tool
async def proxycurl_people_search_leads(
    search_params: PeopleSearchParams,
    max_entries: int = 5,
    enrich_profiles: bool = False,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Search for leads on Proxycurl based on a plain‑English ICP description."""

    params = _build_common_params(search_params, max_entries, enrich_profiles)

    try:
        api_key = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return []

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://enrichlayer.com/api/v2/search/person"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.error("Proxycurl search error %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:
        logger.exception("Exception during Proxycurl search: %s", exc)
        return []

    leads: List[Dict[str, Any]] = []
    for item in (data.get("results") or [])[:max_entries]:
        lead: Dict[str, Any] = {
            "user_linkedin_url": item.get("linkedin_profile_url"),
        }
        profile = item.get("profile") or {}
        if profile:
            # Fill lead fields using profile data
            lead = fill_in_missing_properties(lead, profile)
            first_exp = (profile.get("experiences") or [{}])[0]
            lead.setdefault("organization_name", first_exp.get("company", ""))
            lead.setdefault(
                "organization_linkedin_url",
                first_exp.get("company_linkedin_profile_url", ""),
            )

            additional_props = lead.get("additional_properties") or {}
            additional_props["pc_person_data"] = json.dumps(
                cleanup_properties(profile)
            )
            lead["additional_properties"] = additional_props

            linkedin_url = lead.get("user_linkedin_url")
            if linkedin_url:
                cache_output(
                    "enrich_person_info_from_proxycurl", linkedin_url, profile
                )

        if cleaned := cleanup_properties(lead):
            leads.append(cleaned)

    return leads


# ────────────────────────────
# 🏢  Company search
# ────────────────────────────
@assistant_tool
async def proxycurl_company_search_leads(
    search_params: CompanySearchParams,
    max_entries: int = 5,
    enrich_profiles: bool = False,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Search for companies on Proxycurl based on given parameters."""

    params = _build_common_params(search_params, max_entries, enrich_profiles)

    try:
        api_key = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return []

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://enrichlayer.com/api/v2/search/company"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.error("Proxycurl company search error %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:
        logger.exception("Exception during Proxycurl company search: %s", exc)
        return []

    companies: List[Dict[str, Any]] = []
    for item in (data.get("results") or [])[:max_entries]:
        company: Dict[str, Any] = {
            "organization_linkedin_url": item.get("linkedin_profile_url"),
        }
        profile = item.get("profile") or {}
        if profile:
            # Copy mapped properties from the enriched profile
            transformed = transform_company_data(profile)
            company.update(transformed)

            # Store the raw profile JSON for reference
            additional_props = company.get("additional_properties") or {}
            additional_props["pc_company_data"] = json.dumps(
                cleanup_properties(profile)
            )
            company["additional_properties"] = additional_props

            linkedin_url = company.get("organization_linkedin_url") or ""
            if linkedin_url and "linkedin.com/company" in linkedin_url:
                parsed_url = urlparse(linkedin_url)
                if parsed_url.netloc != "www.linkedin.com":
                    standardized_netloc = "www.linkedin.com"
                    standardized_path = parsed_url.path
                    if not standardized_path.startswith("/company/"):
                        standardized_path = "/company" + standardized_path
                    standardized_url = urlunparse(
                        parsed_url._replace(
                            netloc=standardized_netloc,
                            path=standardized_path,
                        )
                    )
                else:
                    standardized_url = linkedin_url
                if standardized_url and not standardized_url.endswith("/"):
                    standardized_url += "/"
                cache_output(
                    "enrich_organization_info_from_proxycurl",
                    standardized_url,
                    transformed,
                )

        if cleaned := cleanup_properties(company):
            companies.append(cleaned)

    return companies


# ────────────────────────────
# 💼  Job search
# ────────────────────────────
@assistant_tool
async def proxycurl_job_search(
    search_params: JobSearchParams,
    max_entries: int = 5,
    enrich_profiles: bool = False,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """List jobs posted by a company using Proxycurl's job search API."""

    # Job search endpoint does not support enrich_profiles
    params = _build_common_params(search_params, max_entries, enrich_profiles=enrich_profiles)

    try:
        api_key = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return []

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://enrichlayer.com/api/v2/company/job"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.error("Proxycurl job search error %s", resp.status)
                    return []
                data = await resp.json()
    except Exception as exc:
        logger.exception("Exception during Proxycurl job search: %s", exc)
        return []

    job_entries: List[Dict[str, Any]] = []
    for item in (data.get("job") or data.get("jobs") or [])[:max_entries]:
        job: Dict[str, Any] = {
            "organization_name": item.get("company"),
            "organization_linkedin_url": item.get("company_url"),
            "job_title": item.get("job_title"),
            "job_posting_url": item.get("job_url"),
            "list_date": item.get("list_date"),
            "location": item.get("location"),
        }
        additional_props = job.get("additional_properties") or {}
        additional_props["pc_job_data"] = json.dumps(item)
        job["additional_properties"] = additional_props

        job_url = job.get("job_posting_url")
        if job_url:
            cache_output("enrich_job_info_from_proxycurl", job_url, item)
        if cleaned := cleanup_properties(job):
            job_entries.append(cleaned)

    return job_entries


# ────────────────────────────
# 📊  Job count
# ────────────────────────────
@assistant_tool
async def proxycurl_job_count(
    search_params: JobSearchParams,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Get the count of jobs posted by a company using Proxycurl's job count API."""

    # Job count endpoint does not support enrich_profiles or max_entries
    params = search_params.model_dump(exclude_none=True)
    params = _remove_empty_values(params)
    
    # Job count endpoint doesn't need page_size or enrich_profiles
    if "page_size" in params:
        del params["page_size"]

    try:
        api_key = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return {"count": 0}

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://enrichlayer.com/api/v2/company/job/count"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.error("Proxycurl job count error %s", resp.status)
                    return {"count": 0}
                data = await resp.json()
    except Exception as exc:
        logger.exception("Exception during Proxycurl job count: %s", exc)
        return {"count": 0}

    return {"count": data.get("count", 0)}


# ────────────────────────────
# 🔍  Company Profile - Get Search ID
# ────────────────────────────
@assistant_tool
async def proxycurl_get_company_search_id(
    company_url: str,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Get a company's search ID using Proxycurl's Company Profile endpoint.
    
    The search_id is required for other Proxycurl endpoints like job search and job count.
    
    Args:
        company_url: LinkedIn company profile URL (e.g., "https://www.linkedin.com/company/microsoft/")
        tool_config: Optional tool configuration containing API key
        
    Returns:
        Dictionary containing search_id and basic company info, or error info if failed
    """

    try:
        api_key = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return {"error": str(e), "search_id": None}

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://enrichlayer.com/api/v2/company"
    
    params = {
        "url": company_url,
        "use_cache": "if-present",
        "fallback_to_cache": "on-error"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    logger.error("Proxycurl company profile error %s", resp.status)
                    return {"error": f"HTTP {resp.status}", "search_id": None}
                data = await resp.json()
    except Exception as exc:
        logger.exception("Exception during Proxycurl company profile lookup: %s", exc)
        return {"error": str(exc), "search_id": None}

    # Extract the key information
    search_id = data.get("search_id")
    name = data.get("name")
    linkedin_internal_id = data.get("linkedin_internal_id")
    industry = data.get("industry")
    
    result = {
        "search_id": search_id,
        "name": name,
        "linkedin_internal_id": linkedin_internal_id,
        "industry": industry,
        "company_url": company_url
    }
    
    if search_id:
        logger.info(f"Successfully retrieved search_id '{search_id}' for company '{name}'")
    else:
        logger.warning(f"No search_id found for company at {company_url}")
        result["error"] = "No search_id found in response"
    
    return result