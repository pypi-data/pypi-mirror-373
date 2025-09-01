from __future__ import annotations

# ─── Standard library ──────────────────────────────────────────────────────────
import html
import json
import os
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

# ─── Third-party packages ──────────────────────────────────────────────────────
import aiohttp
from bs4 import BeautifulSoup
from fastapi import Query
from markdown import markdown
from pydantic import BaseModel

# ─── Internal / application imports ────────────────────────────────────────────
from dhisana.schemas.sales import HUBSPOT_TO_LEAD_MAPPING, HubSpotLeadInformation
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.clean_properties import cleanup_properties
import logging

# --------------------------------------------------------------------
# 1. Retrieve HubSpot Access Token
# --------------------------------------------------------------------
def get_hubspot_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the HubSpot access token from the provided tool configuration.

    Raises:
        ValueError: If the HubSpot integration has not been configured.
    """
    if tool_config:
        hubspot_config = next(
            (item for item in tool_config if item.get("name") == "hubspot"), None
        )
        if hubspot_config:
            config_map = {
                item["name"]: item["value"]
                for item in hubspot_config.get("configuration", [])
                if item
            }
            # Check for OAuth access token in nested oauth_tokens structure first, then fall back to API key
            oauth_tokens = config_map.get("oauth_tokens")
            if oauth_tokens and isinstance(oauth_tokens, dict):
                HUBSPOT_ACCESS_TOKEN = oauth_tokens.get("access_token")
            else:
                HUBSPOT_ACCESS_TOKEN = config_map.get("access_token") or config_map.get("apiKey")
        else:
            HUBSPOT_ACCESS_TOKEN = None
    else:
        HUBSPOT_ACCESS_TOKEN = None

    HUBSPOT_ACCESS_TOKEN = HUBSPOT_ACCESS_TOKEN or os.getenv("HUBSPOT_API_KEY")
    if not HUBSPOT_ACCESS_TOKEN:
        raise ValueError(
            "HubSpot integration is not configured. Please configure the connection to HubSpot in Integrations."
        )
    return HUBSPOT_ACCESS_TOKEN


# --------------------------------------------------------------------
# 2. Search HubSpot Objects (Contacts, Companies, Deals, etc.)
#    with offset, limit, order_by, order
# --------------------------------------------------------------------
@assistant_tool
async def search_hubspot_objects(
    object_type: str,
    offset: int = 0,
    limit: int = 10,
    order_by: Optional[str] = None,
    order: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    filter_groups: Optional[List[Dict[str, Any]]] = None,
    query: Optional[str] = None,
    properties: Optional[List[str]] = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Search for HubSpot objects (contacts, companies, deals, tickets, etc.) using filters, filter groups, or query.
    Now supports offset, limit, order_by, and order using repeated calls to the V3 search endpoint.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not object_type:
        return {'error': "HubSpot object type must be provided"}

    # We need at least one of filters, filter_groups, or query
    if not any([filters, filter_groups, query]):
        return {'error': "At least one of filters, filter_groups, or query must be provided"}

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/search"

    # Build the base payload
    base_payload: Dict[str, Any] = {}
    if filters:
        base_payload["filterGroups"] = [{"filters": filters}]
    if filter_groups:
        base_payload["filterGroups"] = filter_groups
    if query:
        base_payload["query"] = query
    if properties:
        base_payload["properties"] = properties

    # Handle sorting
    if order_by:
        direction = str(order).lower() if order else "asc"
        base_payload["sorts"] = [f"{order_by} {direction}"]

    accumulated_results = []
    count_skipped = 0
    count_collected = 0
    after = None

    async with aiohttp.ClientSession() as session:
        while True:
            needed = limit - count_collected
            if needed <= 0:
                break

            # HubSpot typically limits page size to 100
            # But we also must accommodate offset skipping.
            page_limit = min(100, needed + offset - count_skipped)
            if page_limit <= 0:
                # offset is too large for the available data
                break

            payload = dict(base_payload)
            payload["limit"] = page_limit
            if after:
                payload["after"] = after

            async with session.post(url, headers=headers, json=payload) as response:
                result = await response.json()
                if response.status != 200:
                    return {'error': result}

                results_list = result.get('results', [])
                paging_info = result.get('paging', {})
                after = paging_info.get('next', {}).get('after')

                # Emulate offset-based skipping
                for record in results_list:
                    if count_skipped < offset:
                        count_skipped += 1
                    else:
                        accumulated_results.append(record)
                        count_collected += 1

                    if count_collected >= limit:
                        break

            if not after or count_collected >= limit:
                break

    return {
        "total": len(accumulated_results),
        "results": accumulated_results
    }


# --------------------------------------------------------------------
# 3. Fetch Companies in CRM (Pagination) 
#    with offset, limit, order_by, order
# --------------------------------------------------------------------
@assistant_tool
async def fetch_companies_in_crm(
    list_name: Optional[str] = None,
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, gt=0, le=2000, description="Max number of records to return"),
    order_by: Optional[str] = Query(None, description="Field to order by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    tool_config: Optional[List[Dict]] = None
) -> List[Dict]:
    """
    Fetch companies in HubSpot CRM, optionally from a specific list.
    Now supports offset, limit, order_by, and order using HubSpot V3 endpoints.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    # For V3 companies endpoint, we can pass "sort=-createdate" for descending, etc.
    sort_param = None
    if order_by:
        # If order == "desc", prefix with "-"
        direction_prefix = "-" if order.lower() == "desc" else ""
        sort_param = f"{direction_prefix}{order_by}"

    accumulated_companies = []
    count_skipped = 0
    count_collected = 0
    after = None

    async with aiohttp.ClientSession() as session:
        if list_name:
            # If fetching companies from a named list
            list_info = await fetch_hubspot_list_by_name(list_name, 'companies', tool_config)
            if list_info is None or "list" not in list_info:
                raise Exception(f"List '{list_name}' not found.")
            list_id = list_info["list"]["listId"]

            memberships_url = f"https://api.hubapi.com/crm/v3/lists/{list_id}/memberships"

            while True:
                if count_collected >= limit:
                    break

                fetch_amount = min(100, (limit + offset) - (count_skipped + count_collected))
                if fetch_amount <= 0:
                    break

                params = {"limit": fetch_amount}
                if after:
                    params["after"] = after

                async with session.get(memberships_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_details = await response.text()
                        raise Exception(f"Error: Received status code {response.status} with details: {error_details}")
                    result = await response.json()

                    memberships = result.get('results', [])
                    after = result.get('paging', {}).get('next', {}).get('after')
                    record_ids = [member['recordId'] for member in memberships]

                    if record_ids:
                        batch_url = "https://api.hubapi.com/crm/v3/objects/companies/batch/read"
                        batch_data = {
                            "properties": [
                                "name", "domain", "annualrevenue", "numberofemployees",
                                "description", "linkedin_company_page", "city", "state", "zip"
                            ],
                            "inputs": [{"id": rid} for rid in record_ids]
                        }
                        async with session.post(batch_url, headers=headers, json=batch_data) as company_response:
                            if company_response.status != 200:
                                error_details = await company_response.text()
                                raise Exception(f"Error fetching company details: {company_response.status} "
                                                f"with details: {error_details}")
                            company_result = await company_response.json()
                            new_companies = company_result.get('results', [])

                            for comp in new_companies:
                                if count_skipped < offset:
                                    count_skipped += 1
                                else:
                                    accumulated_companies.append(comp)
                                    count_collected += 1
                                if count_collected >= limit:
                                    break

                if not after or count_collected >= limit:
                    break

        else:
            # No list_name: fetch from /crm/v3/objects/companies
            base_url = "https://api.hubapi.com/crm/v3/objects/companies"

            while True:
                if count_collected >= limit:
                    break

                fetch_amount = min(100, (limit + offset) - (count_skipped + count_collected))
                if fetch_amount <= 0:
                    break

                params = {
                    "limit": fetch_amount,
                    "properties": [
                        "name", "domain", "annualrevenue", "numberofemployees",
                        "description", "linkedin_company_page", "city", "state", "zip"
                    ],
                }
                if after:
                    params["after"] = after
                if sort_param:
                    params["sort"] = sort_param

                async with session.get(base_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_details = await response.text()
                        raise Exception(f"Error: Received status code {response.status} with details: {error_details}")
                    result = await response.json()

                    new_companies = result.get('results', [])
                    after = result.get('paging', {}).get('next', {}).get('after')

                    for comp in new_companies:
                        if count_skipped < offset:
                            count_skipped += 1
                        else:
                            accumulated_companies.append(comp)
                            count_collected += 1

                        if count_collected >= limit:
                            break

                if not after or count_collected >= limit:
                    break

    return accumulated_companies


def transform_hubspot_contact_to_lead_info(
    hubspot_contact_properties: Dict[str, Any]
) -> HubSpotLeadInformation:
    """
    Convert a raw HubSpot property dict into a HubSpotLeadInformation object.
    - Maps standard fields from HUBSPOT_TO_LEAD_MAPPING.
    - Detects LinkedIn URLs.
    - Cleans up empty fields in additional_properties; Pydantic expects a dict.
    """
    result = {
        "full_name": "",
        "first_name": "",
        "last_name": "",
        "email": "",
        "user_linkedin_url": "",
        "primary_domain_of_organization": "",
        "job_title": "",
        "phone": "",
        "headline": "",
        "lead_location": "",
        "organization_name": "",
        "organization_website": "",
        "organization_linkedin_url": "",
    }
    result["additional_properties"] = {}

    # 1) Map standard HubSpot properties to lead fields
    for hubspot_prop, raw_value in hubspot_contact_properties.items():
        if hubspot_prop in HUBSPOT_TO_LEAD_MAPPING:
            mapped_field = HUBSPOT_TO_LEAD_MAPPING[hubspot_prop]
            result[mapped_field] = str(raw_value) if raw_value else ""

        # 2) Detect LinkedIn user/company URLs
        value_str = str(raw_value)
        if "linkedin.com/in/" in value_str and is_valid_url(value_str):
            result["user_linkedin_url"] = value_str
        if "linkedin.com/company/" in value_str and is_valid_url(value_str):
            result["organization_linkedin_url"] = value_str

    # 3) Build "full_name" if missing
    if not result["full_name"]:
        fn = result["first_name"].strip()
        ln = result["last_name"].strip()
        result["full_name"] = (fn + " " + ln).strip()

    # 4) Copy any unmapped fields into additional_properties
    additional_info = {}
    standard_mapped_keys = set(HUBSPOT_TO_LEAD_MAPPING.keys()) | {
        "user_linkedin_url", "organization_linkedin_url"
    }
    for k, v in hubspot_contact_properties.items():
        if k not in standard_mapped_keys and v is not None and str(v).strip():
            additional_info[k] = str(v).strip()

    # 5) Clean up empties in the additional info
    cleaned_dict = cleanup_properties(additional_info)

    # Do NOT serialize; assign the dictionary directly
    result["additional_properties"]["hubspot_lead_information"] = json.dumps(cleaned_dict)

    # 6) Construct the Pydantic model
    return HubSpotLeadInformation(**result)

@assistant_tool
async def fetch_hubspot_list_records(
    list_id: str,
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, gt=0, le=2000, description="Max number of records to return"),
    order_by: Optional[str] = Query(None, description="Field to order by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    tool_config: Optional[List[Dict]] = None
) -> List[HubSpotLeadInformation]:
    """
    Fetch contact records from a specific HubSpot list using the v3 API,
    then transform each one to a HubSpotLeadInformation.
    """
    HUBSPOT_ACCESS_TOKEN = get_hubspot_access_token(tool_config)
    if not list_id:
        raise ValueError("HubSpot list ID must be provided")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    membership_url = f"https://api.hubapi.com/crm/v3/lists/{list_id}/memberships"
    accumulated_ids = []
    count_skipped = 0
    count_collected = 0
    after = None

    async with aiohttp.ClientSession() as session:
        # 1) Page through memberships (contact IDs)
        while True:
            if count_collected >= limit:
                break

            fetch_amount = min(100, (limit + offset) - (count_skipped + count_collected))
            if fetch_amount <= 0:
                break

            params = {"limit": fetch_amount}
            if after:
                params["after"] = after

            async with session.get(membership_url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_details = await response.text()
                    raise Exception(
                        f"Error: Could not fetch list memberships. "
                        f"Status code {response.status}. Details: {error_details}"
                    )
                memberships_data = await response.json()
                memberships = memberships_data.get('results', [])
                after = memberships_data.get('paging', {}).get('next', {}).get('after')

                for m in memberships:
                    cid = m['recordId']
                    if count_skipped < offset:
                        count_skipped += 1
                    else:
                        accumulated_ids.append(cid)
                        count_collected += 1
                    if count_collected >= limit:
                        break

            if not after or count_collected >= limit:
                break

        if not accumulated_ids:
            return []

        # 2) Fetch batch contact details
        batch_read_url = "https://api.hubapi.com/crm/v3/objects/contacts/batch/read"
        all_properties = await _fetch_all_contact_properties(headers)

        contact_leads = []
        batch_size = 100
        for i in range(0, len(accumulated_ids), batch_size):
            batch_ids = accumulated_ids[i:i + batch_size]
            payload = {
                "properties": all_properties,
                "inputs": [{"id": cid} for cid in batch_ids]
            }
            async with session.post(batch_read_url, headers=headers, json=payload) as r:
                if r.status != 200:
                    error_details = await r.text()
                    raise Exception(
                        f"Error fetching batch contact details. "
                        f"Status code {r.status}. Details: {error_details}"
                    )
                batch_data = await r.json()
                contact_leads.extend(batch_data.get('results', []))

        # 3) Local sorting if requested
        if order_by:
            reverse_sort = (order.lower() == "desc")
            contact_leads.sort(
                key=lambda c: c.get("properties", {}).get(order_by, ""),
                reverse=reverse_sort
            )

        # 4) Transform each contact to HubSpotLeadInformation
        final_leads: List[HubSpotLeadInformation] = []
        for c in contact_leads:
            # Combine top-level ID if you also want to store it
            properties = c.get("properties", {})
            # properties["id"] = c.get("id", "")   # optionally store the contact ID in the properties
            lead_info = transform_hubspot_contact_to_lead_info(properties)
            final_leads.append(lead_info)

        return final_leads


async def _fetch_all_contact_properties(headers: Dict[str, str]) -> List[str]:
    """
    Helper to fetch all contact property names from HubSpot via the V3 properties API.
    """
    properties_url = "https://api.hubapi.com/crm/v3/properties/contacts"
    async with aiohttp.ClientSession() as session:
        async with session.get(properties_url, headers=headers) as prop_resp:
            if prop_resp.status != 200:
                error_details = await prop_resp.text()
                raise Exception(
                    f"Error fetching contact properties. "
                    f"Status {prop_resp.status}. Details: {error_details}"
                )
            prop_data = await prop_resp.json()
            return [p["name"] for p in prop_data.get("results", [])]



@assistant_tool
async def list_all_crm_lists(
    payload: Optional[Dict] = None,
    list_type: str = "contacts",
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, gt=0, le=2000, description="Max number of records to return"),
    order_by: Optional[str] = Query(None, description="Field to order by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetches CRM lists from HubSpot with optional offset, limit, order_by, and order.
    Sorting is now handled server-side by including the sort criteria in the payload.
    Defaults to searching for contact lists.
    """
    object_type_map = {
        "contacts": "0-1",
        "companies": "0-2",
        "deals": "0-3"
    }
    order_by = str(order_by or "name")
    order = str(order or "asc").lower()

    HUBSPOT_ACCESS_TOKEN = get_hubspot_access_token(tool_config)
    
    # Build the base payload for the "crm/v3/lists/search" endpoint
    if payload is None:
        payload = {
            "listIds": [],
            "offset": offset,  # Use the provided offset
            "query": "",
            "count": limit,    # Use limit as the count parameter for HubSpot
            "processingTypes": [],
            "additionalProperties": []
        }
    payload["offset"] = offset
    payload["count"] = limit
    
    # Include sorting parameters if order_by is provided.
    # HubSpot expects a "sorts" array with propertyName and direction ("ASCENDING" or "DESCENDING").
    if order_by:
        payload["sorts"] = [{
            "propertyName": order_by,
            "direction": "DESCENDING" if order.lower() == "desc" else "ASCENDING"
        }]
    else:
        # Optionally, set a default sort if none is provided.
        payload["sorts"] = [{
            "propertyName": "name",
            "direction": "ASCENDING"
        }]

    object_id = object_type_map.get(list_type, "0-1")
    url = "https://api.hubapi.com/crm/v3/lists/search"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    all_results = []
    count_skipped = 0
    count_collected = 0

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_details = await response.text()
                    raise Exception(
                        f"Error: Received status code {response.status} with details: {error_details}"
                    )
                data = await response.json()
                page_lists = data.get("lists", [])
                has_more = data.get("hasMore", False)
                next_offset = data.get("offset", None)

                # Filter results by objectTypeId
                filtered_lists = [lst for lst in page_lists if lst.get("objectTypeId") == object_id]

                for lst_obj in filtered_lists:
                    if count_skipped < offset:
                        count_skipped += 1
                    else:
                        all_results.append(lst_obj)
                        count_collected += 1
                    if count_collected >= limit:
                        break

                if not has_more or count_collected >= limit or next_offset is None:
                    break

                # Update offset for next page
                payload["offset"] = next_offset

    return all_results



# --------------------------------------------------------------------
# 6. fetch_hubspot_list_by_name (Helper)
# --------------------------------------------------------------------
async def fetch_hubspot_list_by_name(
    list_name: str,
    list_type: str = 'contacts',
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch information for a specific HubSpot list using the list's name.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not list_name:
        raise ValueError("HubSpot list name must be provided")

    object_type_ids = {
        'contacts': '0-1',
        'companies': '0-2',
        'deals': '0-3',
        'tickets': '0-5',
    }
    object_type_id = object_type_ids.get(list_type.lower())
    if not object_type_id:
        raise ValueError(f"Invalid list type '{list_type}'. Valid types are: {list(object_type_ids.keys())}")

    url = f"https://api.hubapi.com/crm/v3/lists/object-type-id/{object_type_id}/name/{list_name}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                list_info = await response.json()
                return list_info
            elif response.status == 404:
                raise Exception(f"List with name '{list_name}' not found for object type '{list_type}'")
            else:
                error_details = await response.text()
                raise Exception(f"Error: Received status code {response.status} with details: {error_details}")


# --------------------------------------------------------------------
# 7. Single Object / Non-paginated Tools (Unchanged)
# --------------------------------------------------------------------
@assistant_tool
async def fetch_hubspot_object_info(
    object_type: str,
    object_id: Optional[str] = None,
    object_ids: Optional[List[str]] = None,
    associations: Optional[List[str]] = None,
    properties: Optional[List[str]] = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch information for any HubSpot object(s) (contacts, companies, deals, tickets, lists, etc.)
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not object_id and not object_ids:
        return {'error': "HubSpot object ID(s) must be provided"}
    if not object_type:
        return {'error': "HubSpot object type must be provided"}

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {}
    if properties:
        params['properties'] = ','.join(properties)
    if associations:
        params['associations'] = ','.join(associations)

    try:
        async with aiohttp.ClientSession() as session:
            if object_type.lower() == 'lists':
                # Handle lists endpoint
                if object_id:
                    url = f"https://api.hubapi.com/contacts/v1/lists/{object_id}"
                    async with session.get(url, headers=headers, params=params) as response:
                        result = await response.json()
                        if response.status != 200:
                            return {'error': result}
                        return result
                else:
                    return {'error': "For object_type 'lists', object_id must be provided"}
            else:
                if object_ids:
                    # Batch read
                    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/batch/read"
                    payload = {
                        "inputs": [{"id": oid} for oid in object_ids]
                    }
                    if properties:
                        payload["properties"] = properties
                    if associations:
                        payload["associations"] = associations
                    async with session.post(url, headers=headers, json=payload) as response:
                        result = await response.json()
                        if response.status != 200:
                            return {'error': result}
                        return result
                else:
                    # Single object read
                    url = f"https://api.hubapi.com/crm/v3/objects/{object_type}/{object_id}"
                    async with session.get(url, headers=headers, params=params) as response:
                        result = await response.json()
                        if response.status != 200:
                            return {'error': result}
                        return result
    except Exception as e:
        return {'error': str(e)}
    

def is_valid_url(url: str) -> bool:
    """
    Check if the given string is a well-formed http/https URL.
    """
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


@assistant_tool
async def update_hubspot_contact_properties(
    contact_id: str,
    properties: dict,
    tool_config: Optional[List[Dict]] = None
):
    """
    Update contact properties in HubSpot for a given contact ID.
    [Unchanged single-object logic...]
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not contact_id:
        raise ValueError("HubSpot contact ID must be provided")

    if not properties:
        raise ValueError("Properties dictionary must be provided")

    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = { "properties": properties }

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Error: Received status code {response.status}")
            result = await response.json()
            return result


# --------------------------------------------------------------------
# 1) Update HubSpot "lead" properties (via V3)
#    (Assuming your "lead" is a custom object named "leads" in HubSpot)
# --------------------------------------------------------------------
@assistant_tool
async def update_hubspot_lead_properties(
    lead_id: str,
    properties: dict,
    tool_config: Optional[List[Dict]] = None
):
    """
    Update lead (custom object) properties in HubSpot for a given lead ID (v3).
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    
    if not lead_id:
        raise ValueError("HubSpot lead ID must be provided")
    if not properties:
        raise ValueError("Properties dictionary must be provided")

    url = f"https://api.hubapi.com/crm/v3/objects/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"properties": properties}

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=payload) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Error updating lead: {response.status} => {result}")
            return result


# --------------------------------------------------------------------
# 2) Fetch HubSpot Company Info (via V3)
#    - If company_id is given, do a direct GET.
#    - Else if name/domain is provided, do a search.
# --------------------------------------------------------------------
@assistant_tool
async def fetch_hubspot_company_info(
    company_id: str = None,
    name: str = None,
    domain: str = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch company information from HubSpot using the company's HubSpot ID,
    or by searching via 'name' or 'domain'. Returns the first match if searching.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    
    if not any([company_id, name, domain]):
        raise ValueError("At least one of 'company_id', 'name', or 'domain' must be provided.")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        # ---------------------------------------------------------
        # Case 1: If we have a company_id, do a direct GET
        # ---------------------------------------------------------
        if company_id:
            url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
            params = {"properties": "name,domain,industry,city,state,linkedin_company_page,numberofemployees,annualrevenue"}
            async with session.get(url, headers=headers, params=params) as resp:
                company_info = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error fetching company by ID: {resp.status} => {company_info}")
                return company_info

        # ---------------------------------------------------------
        # Case 2: Otherwise, do a search by name/domain
        # ---------------------------------------------------------
        search_url = "https://api.hubapi.com/crm/v3/objects/companies/search"
        filters = []
        if name:
            filters.append({"propertyName": "name", "operator": "EQ", "value": name})
        if domain:
            filters.append({"propertyName": "domain", "operator": "EQ", "value": domain})
        
        payload = {
            "filterGroups": [
                {
                    "filters": filters
                }
            ],
            "properties": ["name","domain","industry","city","state","linkedin_company_page","numberofemployees","annualrevenue"],
            "limit": 1
        }

        async with session.post(search_url, headers=headers, json=payload) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise Exception(f"Error searching company: {resp.status} => {data}")

            results = data.get("results", [])
            if not results:
                raise Exception("No matching company found for the given search criteria.")

            # Return first match
            return results[0]


# --------------------------------------------------------------------
# 3) Update HubSpot Company Info (via V3)
#    - If company_id is provided, update that record
#    - Else if domain is provided, first search by domain to find the ID
# --------------------------------------------------------------------
@assistant_tool
async def update_hubspot_company_info(
    company_id: str = None,
    domain: str = None,
    city: str = None,
    state: str = None,
    number_of_employees: int = None,
    description: str = None,
    linkedin_company_page: str = None,
    annual_revenue: float = None,
    industry: str = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Update company information in HubSpot using the company's HubSpot ID or domain.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)

    if not company_id and not domain:
        raise ValueError("Either 'company_id' or 'domain' must be provided.")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        # ---------------------------------------------------------
        # If no company_id but domain is provided -> find company_id first
        # ---------------------------------------------------------
        if not company_id and domain:
            search_url = "https://api.hubapi.com/crm/v3/objects/companies/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {"propertyName": "domain", "operator": "EQ", "value": domain}
                        ]
                    }
                ],
                "limit": 1
            }
            async with session.post(search_url, headers=headers, json=search_payload) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error searching company by domain: {resp.status} => {data}")

                results = data.get("results", [])
                if not results:
                    raise Exception(f"No company found with the provided domain '{domain}'.")
                company_id = results[0]["id"]

        # ---------------------------------------------------------
        # Build properties to update
        # ---------------------------------------------------------
        update_payload = {"properties": {}}
        if city is not None:
            update_payload["properties"]["city"] = city
        if state is not None:
            update_payload["properties"]["state"] = state
        if number_of_employees is not None:
            update_payload["properties"]["numberofemployees"] = number_of_employees
        if description is not None:
            update_payload["properties"]["description"] = description
        if linkedin_company_page is not None:
            update_payload["properties"]["linkedin_company_page"] = linkedin_company_page
        if annual_revenue is not None:
            update_payload["properties"]["annualrevenue"] = annual_revenue
        if industry is not None:
            update_payload["properties"]["industry"] = industry

        # ---------------------------------------------------------
        # PATCH to update the company
        # ---------------------------------------------------------
        patch_url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
        async with session.patch(patch_url, headers=headers, json=update_payload) as resp:
            updated_data = await resp.json()
            if resp.status != 200:
                raise Exception(f"Error updating company: {resp.status} => {updated_data}")

        return updated_data


# --------------------------------------------------------------------
# 5) Get Last N Notes for a Customer (via V3)
#    - If customer_id is None but email is provided, find contact ID
#    - Then list associated notes from /contacts/{id}/associations/notes
#    - Sort by created date descending, return top n
# --------------------------------------------------------------------
@assistant_tool
async def get_last_n_notes_for_customer(
    customer_id: str = None,
    email: str = None,
    n: int = 5,
    tool_config: Optional[List[Dict]] = None
):
    """
    Retrieve the last n notes attached to a customer (contact) in HubSpot using the customer's ID or email.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not (customer_id or email):
        raise ValueError("Either 'customer_id' or 'email' must be provided.")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    # -------------------------------------------------------------
    # 1) If no contact ID, lookup by email
    # -------------------------------------------------------------
    async with aiohttp.ClientSession() as session:
        if not customer_id:
            search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {"propertyName": "email", "operator": "EQ", "value": email}
                        ]
                    }
                ],
                "limit": 1
            }
            async with session.post(search_url, headers=headers, json=search_payload) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error searching contact by email: {resp.status} => {data}")

                results = data.get("results", [])
                if not results:
                    raise Exception(f"No contact found with email '{email}'.")
                customer_id = results[0]["id"]

        # -------------------------------------------------------------
        # 2) Fetch associated notes
        #    GET /crm/v3/objects/contacts/{contact_id}/associations/notes
        #    We'll gather all and then pick the last n by created time.
        # -------------------------------------------------------------
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{customer_id}/associations/notes"
        notes = []
        after = None
        while True:
            params = {
                "limit": 100,  # fetch up to 100 at a time
            }
            if after:
                params["after"] = after

            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error fetching contact->notes associations: {resp.status} => {data}")

                results = data.get("results", [])
                notes.extend(results)
                paging = data.get("paging", {})
                after = paging.get("next", {}).get("after")

            if not after:
                break

        if not notes:
            return []

        # We'll fetch each note object fully in batch or individually
        # For brevity, let's do a batch read:
        note_ids = [n["id"] for n in notes]

        if not note_ids:
            return []

        # Build batch read for notes:
        batch_read_url = "https://api.hubapi.com/crm/v3/objects/notes/batch/read"
        payload = {
            "properties": ["hs_note_body","hs_createdate"],
            "inputs": [{"id": nid} for nid in note_ids]
        }
        async with session.post(batch_read_url, headers=headers, json=payload) as resp:
            batch_data = await resp.json()
            if resp.status != 200:
                raise Exception(f"Error batch-reading notes: {resp.status} => {batch_data}")

        full_notes = batch_data.get("results", [])
        # Sort by created date descending
        # Typically it's in "properties" -> "hs_createdate"
        full_notes.sort(
            key=lambda x: x.get("properties", {}).get("hs_createdate", ""),
            reverse=True
        )

        # Return top n
        return full_notes[:n]


# --------------------------------------------------------------------
# 5b) Get Last N Call Logs for a Lead (via V3)
#     - Use lead information to look up the contact by email or by
#       firstname/lastname and company name
#     - Then list associated calls from /contacts/{id}/associations/calls
#     - Sort by created date descending and return the top n
# --------------------------------------------------------------------
@assistant_tool
async def get_last_n_calls_for_lead(
    lead_info: HubSpotLeadInformation,
    n: int = 5,
    tool_config: Optional[List[Dict]] = None,
):
    """
    Retrieve the last ``n`` call log records for a contact in HubSpot
    based on provided ``lead_info`` (email or name & company).
    """

    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not lead_info:
        raise ValueError("lead_info must be provided")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        # -------------------------------------------------------------
        # 1) Find contact ID via email or name/company
        # -------------------------------------------------------------
        search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        if lead_info.email:
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": lead_info.email,
                            }
                        ]
                    }
                ],
                "limit": 1,
            }
        else:
            filters = []
            if lead_info.first_name:
                filters.append(
                    {
                        "propertyName": "firstname",
                        "operator": "EQ",
                        "value": lead_info.first_name,
                    }
                )
            if lead_info.last_name:
                filters.append(
                    {
                        "propertyName": "lastname",
                        "operator": "EQ",
                        "value": lead_info.last_name,
                    }
                )
            if lead_info.organization_name:
                filters.append(
                    {
                        "propertyName": "company",
                        "operator": "EQ",
                        "value": lead_info.organization_name,
                    }
                )
            if not filters:
                raise ValueError(
                    "lead_info must include email or name and company information"
                )
            search_payload = {"filterGroups": [{"filters": filters}], "limit": 1}

        async with session.post(
            search_url, headers=headers, json=search_payload
        ) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise Exception(
                    f"Error searching contact by lead info: {resp.status} => {data}"
                )

            results = data.get("results", [])
            if not results:
                raise Exception("No contact found with the provided lead information")
            contact_id = results[0]["id"]

        # -------------------------------------------------------------
        # 2) Fetch associated calls
        # -------------------------------------------------------------
        assoc_url = (
            f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/calls"
        )
        calls = []
        after = None
        while True:
            params = {"limit": 100}
            if after:
                params["after"] = after

            async with session.get(assoc_url, headers=headers, params=params) as resp:
                assoc_data = await resp.json()
                if resp.status != 200:
                    raise Exception(
                        f"Error fetching contact->calls associations: {resp.status} => {assoc_data}"
                    )

                calls.extend(assoc_data.get("results", []))
                after = assoc_data.get("paging", {}).get("next", {}).get("after")

            if not after:
                break

        if not calls:
            return []

        call_ids = [c["id"] for c in calls]
        batch_url = "https://api.hubapi.com/crm/v3/objects/calls/batch/read"
        payload = {
            "properties": [
                "hs_call_title",
                "hs_call_body",
                "hs_createdate",
                "hs_call_duration",
            ],
            "inputs": [{"id": cid} for cid in call_ids],
        }
        async with session.post(batch_url, headers=headers, json=payload) as resp:
            batch_data = await resp.json()
            if resp.status != 200:
                raise Exception(
                    f"Error batch-reading calls: {resp.status} => {batch_data}"
                )

        full_calls = batch_data.get("results", [])
        full_calls.sort(
            key=lambda x: x.get("properties", {}).get("hs_createdate", ""),
            reverse=True,
        )
        return full_calls[:n]


# --------------------------------------------------------------------
# 6) Fetch HubSpot Contact Associations (via V3)
#    - e.g., fetch a contact's associated companies, deals, tickets, etc.
# --------------------------------------------------------------------
@assistant_tool
async def fetch_hubspot_contact_associations(
    contact_id: str,
    to_object_type: str,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch associations from a contact to other objects in HubSpot (v3).
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not contact_id:
        raise ValueError("HubSpot contact ID must be provided.")
    if not to_object_type:
        raise ValueError("Target object type must be provided (e.g. 'companies').")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    # Per the V3 docs, the endpoint is:
    # GET /crm/v3/objects/contacts/{contactId}/associations/{toObjectType}
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/{to_object_type}"

    all_associations = []
    after = None

    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "limit": 100,
            }
            if after:
                params["after"] = after

            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error fetching contact associations: {resp.status} => {data}")

                results = data.get("results", [])
                all_associations.extend(results)
                paging = data.get("paging", {})
                after = paging.get("next", {}).get("after")

            if not after:
                break

    return all_associations

@assistant_tool
async def fetch_hubspot_lead_info(
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    linkedin_url: str = None,
    phone_number: str = None,
    hubspot_id: str = None,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch lead information from a custom "leads" object in HubSpot, based on:
      - hubspot_id (directly)
      - OR searching by any combination of: first_name, last_name, email, linkedin_url, phone_number
    Then optionally fetch & merge association info (companies, notes, etc.).
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    # If hubspot_id is given, do a direct GET:
    async with aiohttp.ClientSession() as session:
        if hubspot_id:
            # -----------------------------------------------------
            # Direct fetch of the lead by ID
            # -----------------------------------------------------
            url = f"https://api.hubapi.com/crm/v3/objects/leads/{hubspot_id}"
            params = {"properties": "firstname,lastname,email,phone,linkedin_url"}
            async with session.get(url, headers=headers, params=params) as resp:
                lead_info = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error fetching lead by ID: {resp.status} => {lead_info}")
        else:
            # -----------------------------------------------------
            # Build a search query from non-empty parameters
            # -----------------------------------------------------
            filters = []
            if first_name:
                filters.append({
                    "propertyName": "firstname", "operator": "EQ", "value": first_name
                })
            if last_name:
                filters.append({
                    "propertyName": "lastname", "operator": "EQ", "value": last_name
                })
            if email:
                filters.append({
                    "propertyName": "email", "operator": "EQ", "value": email
                })
            if linkedin_url:
                filters.append({
                    "propertyName": "hs_linkedin_url", "operator": "EQ", "value": linkedin_url
                })
            if phone_number:
                filters.append({
                    "propertyName": "phone", "operator": "EQ", "value": phone_number
                })

            if not filters:
                raise ValueError("At least one search parameter must be provided (or hubspot_id).")

            search_url = "https://api.hubapi.com/crm/v3/objects/leads/search"
            payload = {
                "filterGroups": [
                    {
                        "filters": filters
                    }
                ],
                "properties": ["firstname","lastname","email","phone","hs_linkedin_url"],
                "limit": 1
            }

            async with session.post(search_url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error searching lead: {resp.status} => {data}")

                results = data.get("results", [])
                if not results:
                    raise Exception("No lead found with the provided parameters.")
                lead_info = results[0]

        # By here, we have a lead object with "id" in lead_info["id"]
        lead_id = lead_info["id"]

        # ---------------------------------------------------------
        # (Optional) fetch associated companies
        # ---------------------------------------------------------
        assoc_url = f"https://api.hubapi.com/crm/v3/objects/leads/{lead_id}/associations/companies"
        async with session.get(assoc_url, headers=headers) as resp:
            companies_data = await resp.json()
            if resp.status == 200:
                lead_info["companies"] = companies_data.get("results", [])
            else:
                lead_info["companies"] = []

        # ---------------------------------------------------------
        # (Optional) fetch associated notes
        # ---------------------------------------------------------
        notes_url = f"https://api.hubapi.com/crm/v3/objects/leads/{lead_id}/associations/notes"
        async with session.get(notes_url, headers=headers) as resp:
            notes_data = await resp.json()
            if resp.status == 200:
                lead_info["notes"] = notes_data.get("results", [])
            else:
                lead_info["notes"] = []

        # ---------------------------------------------------------
        # (Optional) fetch associated calls, tasks, etc.
        # If you want to mirror "activities," you'd do:
        # calls => /leads/{id}/associations/calls
        # tasks => /leads/{id}/associations/tasks
        # etc.
        # (Skipping here for brevity)
        # ---------------------------------------------------------

        return lead_info


# --------------------------------------------------------------------
# 2) Fetch HubSpot Contact Info (V3) with optional custom tags
# --------------------------------------------------------------------
@assistant_tool
async def fetch_hubspot_contact_info(
    hubspot_id: str = None,
    email: str = None,
    tool_config: Optional[List[Dict]] = None,
    custom_tag_property_name: str = None
):
    """
    Fetch contact information from HubSpot, including associated companies, notes, tasks, calls, meetings, and optionally custom tags.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not hubspot_id and not email:
        raise ValueError("Either hubspot_id or email must be provided.")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepare base properties list
    base_properties = ["email", "firstname", "lastname", "phone", "hs_linkedin_url"]
    if custom_tag_property_name:
        base_properties.append(custom_tag_property_name)

    contact_info = None

    async with aiohttp.ClientSession() as session:
        # ---------------------------------------------------------
        # 1) If we have hubspot_id, fetch directly
        # ---------------------------------------------------------
        if hubspot_id:
            url = f"https://api.hubapi.com/crm/v3/objects/contacts/{hubspot_id}"
            params = {"properties": ",".join(base_properties)}
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                contact_info = data
        else:
            # -----------------------------------------------------
            # 2) Otherwise, search by email to find contact_id
            # -----------------------------------------------------
            search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {"propertyName": "email", "operator": "EQ", "value": email}
                        ]
                    }
                ],
                "properties": base_properties,
                "limit": 1
            }
            async with session.post(search_url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error searching contact by email: {resp.status} => {data}")

                results = data.get("results", [])
                if not results:
                    raise Exception(f"No contact found with email '{email}'.")
                contact_info = results[0]

        contact_id = contact_info["id"]

        # Utility to fetch associated object
        async def fetch_associated_objects(object_type: str):
            url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/{object_type}"
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data.get("results", [])
                return []

        contact_info["companies"] = await fetch_associated_objects("companies")
        contact_info["notes"] = await fetch_associated_objects("notes")
        contact_info["tasks"] = await fetch_associated_objects("tasks")
        contact_info["calls"] = await fetch_associated_objects("calls")
        contact_info["meetings"] = await fetch_associated_objects("meetings")

        return contact_info



# --------------------------------------------------------------------
# 3) Fetch Last N Activities for a Contact (V3 version)
#    "Activities" typically means calls, tasks, notes, meetings, emails, ...
#    Because there's no single "activities" object in v3, we do multiple calls 
#    and combine the results, then pick the newest `num_events`.
# --------------------------------------------------------------------
@assistant_tool
async def fetch_last_n_activities(
    email: str,
    num_events: int,
    tool_config: Optional[List[Dict]] = None
):
    """
    Fetch the last n "activities" for a contact (calls, tasks, notes, meetings, emails)
    by email, using HubSpot V3 associations.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not email:
        raise ValueError("Email must be provided")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        # -----------------------------------------------------
        # 1) Find contact ID by email
        # -----------------------------------------------------
        search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": "email", "operator": "EQ", "value": email}
                    ]
                }
            ],
            "properties": ["email", "firstname", "lastname"],
            "limit": 1
        }
        async with session.post(search_url, headers=headers, json=payload) as response:
            data = await response.json()
            if response.status != 200:
                raise Exception(f"Error searching contact by email: {response.status} => {data}")
            results = data.get("results", [])
            if not results:
                raise Exception(f"No contact found with email '{email}'.")
            contact_id = results[0]["id"]

        # -----------------------------------------------------
        # 2) Gather associations for each relevant activity type
        #    We'll fetch calls, tasks, notes, meetings, and emails.
        # -----------------------------------------------------
        all_activity_records = []

        for activity_type in ["calls", "tasks", "notes", "meetings", "emails"]:
            assoc_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}/associations/{activity_type}"
            after = None
            activity_refs = []
            while True:
                params = {"limit": 100}
                if after:
                    params["after"] = after

                async with session.get(assoc_url, headers=headers, params=params) as resp:
                    assoc_data = await resp.json()
                    if resp.status != 200:
                        raise Exception(f"Error fetching contact associations to {activity_type}: "
                                        f"{resp.status} => {assoc_data}")

                    results = assoc_data.get("results", [])
                    activity_refs.extend(results)

                    paging = assoc_data.get("paging", {})
                    after = paging.get("next", {}).get("after")
                    if not after:
                        break

            if not activity_refs:
                continue

            # Now we do a batch read for each object type
            # The V3 batch read endpoint: /crm/v3/objects/{activity_type}/batch/read
            # We'll sort by "hs_createdate" later.
            batch_url = f"https://api.hubapi.com/crm/v3/objects/{activity_type}/batch/read"
            object_ids = [ref["id"] for ref in activity_refs]
            payload = {
                "properties": ["hs_createdate","hs_note_body","hs_call_body","subject"],  # or any relevant props
                "inputs": [{"id": oid} for oid in object_ids]
            }

            async with session.post(batch_url, headers=headers, json=payload) as resp:
                read_data = await resp.json()
                if resp.status != 200:
                    raise Exception(f"Error batch reading {activity_type}: {resp.status} => {read_data}")
                objects = read_data.get("results", [])
                # Mark each object with a "type" field so we can distinguish them later
                for obj in objects:
                    obj["activity_type"] = activity_type
                all_activity_records.extend(objects)

        # -----------------------------------------------------
        # 3) Sort by created date descending, return top `num_events`
        #    Typically "hs_createdate" is the creation timestamp
        # -----------------------------------------------------
        def get_created_date(obj):
            return obj.get("properties", {}).get("hs_createdate", "")

        all_activity_records.sort(key=get_created_date, reverse=True)
        return all_activity_records[:num_events]


# --------------------------------------------------------------------
# New Pydantic model to hold company info
# --------------------------------------------------------------------
class HubSpotCompanyInformation(BaseModel):
    organization_name: str = ""
    organization_website: str = ""
    primary_domain_of_organization: str = ""
    additional_properties: Dict[str, Any] = {}

# --------------------------------------------------------------------
# Helper: transform raw company properties to HubSpotCompanyInformation
# --------------------------------------------------------------------
def transform_hubspot_company_properties_to_company_info(
    hubspot_company_properties: Dict[str, Any]
) -> HubSpotCompanyInformation:
    """
    Convert raw company properties from HubSpot into a HubSpotCompanyInformation object.
    
    - organization_name -> from property "name"
    - organization_website -> from property "website" (if present; fallback to empty)
    - primary_domain_of_organization -> from property "domain"
    - Everything else into additional_properties["hubspot_company_information"] as a JSON string.
    """
    result = {
        "organization_name": str(hubspot_company_properties.get("name", "")).strip(),
        "organization_website": str(hubspot_company_properties.get("website", "")).strip(),
        "primary_domain_of_organization": str(hubspot_company_properties.get("domain", "")).strip(),
        "additional_properties": {},
    }

    # Standard mapped keys we do NOT copy into additional_properties
    standard_keys = {"name", "website", "domain"}

    # Gather everything else into additional_properties
    additional_info = {}
    for k, v in hubspot_company_properties.items():
        if k not in standard_keys and v is not None and str(v).strip():
            additional_info[k] = str(v).strip()

    # Cleanup
    cleaned_dict = cleanup_properties(additional_info)
    result["additional_properties"]["hubspot_company_information"] = json.dumps(cleaned_dict)

    return HubSpotCompanyInformation(**result)

# --------------------------------------------------------------------
# Fetch a company list's memberships, batch-read the company details,
# transform them, and return.
# --------------------------------------------------------------------
@assistant_tool
async def fetch_hubspot_company_list_records(
    list_id: str,
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, gt=0, le=2000, description="Max number of records to return"),
    order_by: Optional[str] = Query(None, description="Field to order by"),
    order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    tool_config: Optional[List[Dict]] = None
) -> List[HubSpotCompanyInformation]:
    """
    Fetch company records from a specific HubSpot list using the v3 API.
    - Accumulates up to `limit` company IDs from the list memberships.
    - Batch reads the company details.
    - Transforms to HubSpotCompanyInformation objects.
    - (Optionally) sorts locally by `order_by` ascending or descending.
    """

    # 1) Retrieve HubSpot Access Token
    HUBSPOT_ACCESS_TOKEN = get_hubspot_access_token(tool_config)
    if not list_id:
        raise ValueError("HubSpot company list ID must be provided")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Memberships URL for the given list
    membership_url = f"https://api.hubapi.com/crm/v3/lists/{list_id}/memberships"

    # Accumulate company IDs
    accumulated_ids = []
    count_skipped = 0
    count_collected = 0
    after = None

    async with aiohttp.ClientSession() as session:
        # 2) Page through the list memberships to find company IDs
        while True:
            if count_collected >= limit:
                break

            # The # to request in this page
            fetch_amount = min(100, (limit + offset) - (count_skipped + count_collected))
            if fetch_amount <= 0:
                break

            params = {"limit": fetch_amount}
            if after:
                params["after"] = after

            async with session.get(membership_url, headers=headers, params=params) as response:
                if response.status != 200:
                    error_details = await response.text()
                    raise Exception(
                        f"Error: Could not fetch list memberships. "
                        f"Status code {response.status}. Details: {error_details}"
                    )
                memberships_data = await response.json()
                memberships = memberships_data.get("results", [])
                after = memberships_data.get("paging", {}).get("next", {}).get("after")

                for m in memberships:
                    company_id = m["recordId"]
                    if count_skipped < offset:
                        count_skipped += 1
                    else:
                        accumulated_ids.append(company_id)
                        count_collected += 1
                    if count_collected >= limit:
                        break

            if not after or count_collected >= limit:
                break

        # If no IDs, return an empty list
        if not accumulated_ids:
            return []

        # 3) Batch read the company details
        batch_read_url = "https://api.hubapi.com/crm/v3/objects/companies/batch/read"

        # For demonstration, let's fetch all standard/available props.
        # Or, you can fetch a subset, like ["name", "domain", "website", "linkedin_company_page"] etc.
        all_properties = await _fetch_all_company_properties(headers)

        company_records = []
        batch_size = 100
        for i in range(0, len(accumulated_ids), batch_size):
            chunk_ids = accumulated_ids[i : i + batch_size]
            payload = {
                "properties": all_properties,
                "inputs": [{"id": cid} for cid in chunk_ids]
            }

            async with session.post(batch_read_url, headers=headers, json=payload) as r:
                if r.status != 200:
                    error_details = await r.text()
                    raise Exception(
                        f"Error fetching batch company details. "
                        f"Status code {r.status}. Details: {error_details}"
                    )
                batch_data = await r.json()
                company_records.extend(batch_data.get("results", []))

        # 4) Local sorting if requested
        if order_by:
            reverse_sort = (order.lower() == "desc")
            company_records.sort(
                key=lambda c: c.get("properties", {}).get(order_by, ""),
                reverse=reverse_sort
            )

        # 5) Transform each record into HubSpotCompanyInformation
        final_companies: List[HubSpotCompanyInformation] = []
        for record in company_records:
            properties = record.get("properties", {})
            company_info = transform_hubspot_company_properties_to_company_info(properties)
            final_companies.append(company_info)

        return final_companies

# --------------------------------------------------------------------
# Helper function to retrieve all properties available for companies
# --------------------------------------------------------------------
async def _fetch_all_company_properties(headers: Dict[str, str]) -> List[str]:
    """
    Fetches all company property names via the HubSpot v3 properties API.
    You could also hardcode a list if you'd prefer fewer properties.
    """
    properties_url = "https://api.hubapi.com/crm/v3/properties/companies"
    async with aiohttp.ClientSession() as session:
        async with session.get(properties_url, headers=headers) as prop_resp:
            if prop_resp.status != 200:
                error_details = await prop_resp.text()
                raise Exception(
                    f"Error fetching company properties. "
                    f"Status {prop_resp.status}. Details: {error_details}"
                )
            prop_data = await prop_resp.json()
            return [p["name"] for p in prop_data.get("results", [])]


@assistant_tool
async def lookup_contact_by_name_and_domain(
    first_name: str,
    last_name: str,
    domain: str,
    tool_config: Optional[List[Dict]] = None
) -> Union[HubSpotLeadInformation, dict]:
    """
    Look up a HubSpot contact by first name, last name, and a "primary_domain_of_organization"
    (which you store on the contact record). If found, transform via transform_hubspot_contact_to_lead_info
    and return the HubSpotLeadInformation object; otherwise return {}.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not HUBSPOT_API_KEY:
        return {}
    
    if not all([first_name, last_name, domain]):
        return {}

    # 1) Build filters
    filters = [
        {"propertyName": "firstname", "operator": "EQ", "value": first_name},
        {"propertyName": "lastname", "operator": "EQ", "value": last_name},
        {"propertyName": "primary_domain_of_organization", "operator": "EQ", "value": domain},
    ]

    # 2) Perform the search
    search_response = await search_hubspot_objects(
        object_type="contacts",
        filters=filters,
        limit=1,
        tool_config=tool_config,
        properties=[  # request at least these properties
            "firstname", "lastname", "email", "phone", "jobtitle",
            "headline", "primary_domain_of_organization",
            "company", "domain"  # or any additional fields you need
        ]
    )

    # 3) Check if results exist
    results = search_response.get("results", [])
    if not results:
        return {}

    # 4) Take the first match and transform
    contact_record = results[0]
    contact_properties = contact_record.get("properties", {})
    transformed = transform_hubspot_contact_to_lead_info(contact_properties)
    return transformed


@assistant_tool
async def lookup_contact_by_email(
    email: str,
    tool_config: Optional[List[Dict]] = None
) -> Union[HubSpotLeadInformation, dict]:
    """
    Look up a HubSpot contact by email. If found, transform via transform_hubspot_contact_to_lead_info
    and return the HubSpotLeadInformation object; otherwise return {}.
    """
    if not email:
        return {}
    
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not HUBSPOT_API_KEY:
        return {}

    # 1) Build filter
    filters = [
        {"propertyName": "email", "operator": "EQ", "value": email},
    ]

    # 2) Perform the search
    search_response = await search_hubspot_objects(
        object_type="contacts",
        filters=filters,
        limit=1,
        tool_config=tool_config,
        properties=[
            "firstname", "lastname", "email", "phone", "jobtitle",
            "headline", "primary_domain_of_organization",
            "company", "domain"
        ]
    )

    # 3) Check if results exist
    results = search_response.get("results", [])
    if not results:
        return {}

    # 4) Take the first match and transform
    contact_record = results[0]
    contact_properties = contact_record.get("properties", {})
    transformed = transform_hubspot_contact_to_lead_info(contact_properties)
    return transformed






# ──────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────────────────────────────────────
def md_to_html(md: str) -> str:
    """Render Markdown to HTML that HubSpot notes can display."""
    return markdown(md, extensions=["extra", "sane_lists"])


def html_to_text(html_str: str) -> str:
    """Strip tags so the value is safe for a plain-text HS property."""
    return BeautifulSoup(html_str, "html.parser").get_text("\n")


def build_note_html(cv: Dict[str, Any]) -> str:
    """Create a neat, labelled HTML block for the HubSpot note body."""
    parts: List[str] = []
    parts.append("<p><strong>Dhisana AI Lead Research & Engagement Summary</strong></p>")

    def para(label: str, val: Optional[str]):
        if val:
            parts.append(
                f"<p><strong>{html.escape(label)}:</strong> "
                f"{html.escape(val)}</p>"
            )

    para("Name", f"{cv.get('first_name', '')} {cv.get('last_name', '')}".strip())
    para("Email", cv.get("email"))
    para("LinkedIn", cv.get("user_linkedin_url"))
    para("Phone", cv.get("phone"))
    para("Job Title", cv.get("job_title"))
    para("Organization", cv.get("organization_name"))
    para("Domain", cv.get("organization_domain"))

    md_summary = cv.get("research_summary")
    if md_summary:
        parts.append("<p><strong>Research Summary:</strong></p>")
        parts.append(md_to_html(md_summary))

    return "".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# Mapping between internal names and HubSpot property names
# ──────────────────────────────────────────────────────────────────────────────
PROPERTY_MAPPING: Dict[str, str] = {
    "first_name": "firstname",
    "last_name": "lastname",
    "email": "email",
    "phone": "phone",
    "job_title": "jobtitle",
    "primary_domain_of_organization": "domain",
    "user_linkedin_url": "hs_linkedin_url",
    "research_summary": "dhisana_research_summary",
    "organization_name": "company",
    # add "website": "website" if present in your schema
}

# Properties that we conditionally fill-in (only if empty in HS)
CONDITIONAL_UPDATE_PROPS = {
    "jobtitle",
    "company",
    "phone",
    "domain",
    "hs_linkedin_url",
    "website",
}

# Properties we *never* modify once the record exists
IMMUTABLE_ON_UPDATE = {"firstname", "lastname", "email"}


def _is_empty(val: Optional[str]) -> bool:
    return val is None or (isinstance(val, str) and not val.strip())


# ──────────────────────────────────────────────────────────────────────────────
# Main upsert entry-point (updated for flexible tag field)
# ──────────────────────────────────────────────────────────────────────────────
async def update_crm_contact_record_function(
    contact_values: Dict[str, Any],
    is_update: bool,
    hubspot_contact_id: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company_domain: Optional[str] = None,
    user_linkedin_url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    tag_property: Optional[str] = None,          # ← NEW
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Create or update a HubSpot contact.

    Args
    ----
    tag_property:
        The HS property that stores your semicolon-delimited tag list
        (e.g. ``"dhisana_contact_tags"``).  
        • If supplied *and* present in the portal, it will be used.  
        • If absent, we silently fall back to ``"my_tags"`` if available.  
        • If neither exists, tags are skipped without error.
    """

    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    valid_props = await _fetch_all_contact_properties(headers)

    # ─── 0) Build note HTML + plain-text summary ─────────────────────────────
    note_html: str = build_note_html(contact_values)
    note_plain: str = html_to_text(note_html)

    # ─── 1) Map contact_values → HS property dict ────────────────────────────
    incoming_props: Dict[str, Any] = {}
    for k, v in contact_values.items():
        if v is None:
            continue
        mapped = PROPERTY_MAPPING.get(k)
        if mapped and mapped in valid_props:
            incoming_props[mapped] = v

    # ─── 1-b) Handle tags ----------------------------------------------------
    if tags:
        # pick the first tag field that actually exists
        prop_name: Optional[str] = None
        if tag_property and tag_property in valid_props:
            prop_name = tag_property
        elif "my_tags" in valid_props:
            prop_name = "my_tags"

        if prop_name:
            incoming_props[prop_name] = ";".join(tags)

    # ─── 2) Upsert logic ─────────────────────────────────────────────────────
    found_contact_id: Optional[str] = None
    if is_update:
        found_contact_id = hubspot_contact_id or await _find_existing_contact(
            email,
            user_linkedin_url,
            first_name,
            last_name,
            company_domain,
            valid_props,
            tool_config,
        )

    if found_contact_id:
        # ─── Existing contact -------------------------------------------------
        contact_data = await _get_contact_by_id(found_contact_id, headers)
        current = contact_data.get("properties", {})

        hubspot_props: Dict[str, Any] = {}
        for prop, val in incoming_props.items():
            if prop in IMMUTABLE_ON_UPDATE:
                continue
            if prop in CONDITIONAL_UPDATE_PROPS:
                # only fill if currently blank
                if _is_empty(current.get(prop)):
                    hubspot_props[prop] = val
            else:
                hubspot_props[prop] = val

        # merge/update dhisana_lead_information
        if "dhisana_lead_information" in valid_props:
            if note_plain:
                merged = (current.get("dhisana_lead_information") or "").strip()
                merged = f"{merged}\n\n{note_plain}" if merged else note_plain
                hubspot_props["dhisana_lead_information"] = merged
        elif note_html:
            await create_hubspot_note_for_customer(
                customer_id=found_contact_id,
                note=note_html,
                tool_config=tool_config,
            )

        if hubspot_props:
            update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{found_contact_id}"
            async with aiohttp.ClientSession() as s:
                async with s.patch(
                    update_url, headers=headers, json={"properties": hubspot_props}
                ) as r:
                    res = await r.json()
                    if r.status != 200:
                        raise RuntimeError(f"Update failed {r.status}: {res}")
                    return res
        return contact_data

    # ─── Create new contact ──────────────────────────────────────────────────
    return await _create_new_contact_with_note_or_property(
        incoming_props,
        note_html,
        note_plain,
        valid_props,
        headers,
        tool_config,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Contact creation helper
# ──────────────────────────────────────────────────────────────────────────────
async def _create_new_contact_with_note_or_property(
    properties: Dict[str, Any],
    note_html: str,
    note_plain: str,
    valid_props: List[str],
    headers: Dict[str, str],
    tool_config: Optional[List[Dict]],
) -> Dict[str, Any]:
    """Create contact, store lead info either in property or as a note."""
    if "dhisana_lead_information" in valid_props and note_plain:
        properties["dhisana_lead_information"] = note_plain

    create_result = await _create_new_hubspot_contact(properties, headers)

    if note_html and "dhisana_lead_information" not in valid_props:
        new_id = create_result.get("id")
        if new_id:
            await create_hubspot_note_for_customer(
                customer_id=new_id, note=note_html, tool_config=tool_config
            )
    return create_result


# ──────────────────────────────────────────────────────────────────────────────
# Misc. helpers
# ──────────────────────────────────────────────────────────────────────────────
async def _find_existing_contact(
    email: Optional[str],
    linkedin_url: Optional[str],
    first: Optional[str],
    last: Optional[str],
    domain: Optional[str],
    valid_props: List[str],
    tool_cfg: Optional[List[Dict]],
) -> Optional[str]:
    """Return contact ID if a matching record exists, else None."""
    filters = []
    if email:
        filters.append({"propertyName": "email", "operator": "EQ", "value": email})
    elif linkedin_url and "hs_linkedin_url" in valid_props:
        filters.append(
            {"propertyName": "hs_linkedin_url", "operator": "EQ", "value": linkedin_url}
        )
    elif first and last and domain:
        filters.extend(
            [
                {"propertyName": "firstname", "operator": "EQ", "value": first},
                {"propertyName": "lastname", "operator": "EQ", "value": last},
                {"propertyName": "domain", "operator": "EQ", "value": domain},
            ]
        )

    if not filters:
        return None

    res = await search_hubspot_objects(
        object_type="contacts",
        filters=filters,
        limit=1,
        tool_config=tool_cfg,
        properties=[
            "email",
            "firstname",
            "lastname",
            "domain",
            "dhisana_lead_information",
            "company",
            "jobtitle",
            "phone",
            "hs_linkedin_url",
        ],
    )
    hits = res.get("results", [])
    return hits[0]["id"] if hits else None


async def _create_new_hubspot_contact(
    properties: Dict[str, Any], headers: Dict[str, str]
) -> Dict[str, Any]:
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json={"properties": properties}) as r:
            data = await r.json()
            if r.status not in (200, 201):
                raise RuntimeError(f"Create contact failed {r.status}: {data}")
            return data


async def _fetch_all_contact_properties(headers: Dict[str, str]) -> List[str]:
    url = "https://api.hubapi.com/crm/v3/properties/contacts"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers) as r:
            if r.status != 200:
                raise RuntimeError(f"Prop fetch failed {r.status}: {await r.text()}")
            data = await r.json()
            return [p["name"] for p in data.get("results", [])]


async def _get_contact_by_id(contact_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers) as r:
            data = await r.json()
            if r.status != 200:
                raise RuntimeError(f"Fetch contact {contact_id} failed: {r.status} {data}")
            return data


# ──────────────────────────────────────────────────────────────────────────────
# Note creation
# ──────────────────────────────────────────────────────────────────────────────
async def create_hubspot_note_for_customer(
    customer_id: str | None = None,
    email: str | None = None,
    note: str | None = None,
    tool_config: Optional[List[Dict]] = None,
):
    """
    Create a rich-text note and attach it to a contact (associationTypeId 202).
    `note` must be **HTML**.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    if not (customer_id or email):
        raise ValueError("Either customer_id or email is required.")
    if not note:
        raise ValueError("Note content must be provided.")

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as s:
        if not customer_id:
            search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {"propertyName": "email", "operator": "EQ", "value": email}
                        ]
                    }
                ],
                "limit": 1,
            }
            async with s.post(search_url, headers=headers, json=payload) as r:
                js = await r.json()
                if r.status != 200 or not js.get("results"):
                    raise RuntimeError(f"Contact lookup failed {r.status}: {js}")
                customer_id = js["results"][0]["id"]

        create_url = "https://api.hubapi.com/crm/v3/objects/notes"
        payload = {
            "properties": {
                "hs_note_body": note,
                "hs_timestamp": int(time.time() * 1000),
            },
            "associations": [
                {
                    "to": {"id": customer_id, "type": "contact"},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 202,
                        }
                    ],
                }
            ],
        }
        async with s.post(create_url, headers=headers, json=payload) as r:
            res = await r.json()
            if r.status != 201:
                raise RuntimeError(f"Create note failed {r.status}: {res}")
            return res



# ──────────────────────────────────────────────────────────────────────────────
# Mapping between internal names ⇢ HubSpot company property names
# ──────────────────────────────────────────────────────────────────────────────
COMPANY_PROPERTY_MAPPING: Dict[str, str] = {
    "organization_name": "name",
    "primary_domain_of_organization": "domain",
    "organization_website": "website",
}

# Only fill these if currently blank in HS
CONDITIONAL_UPDATE_PROPS = {"domain", "website"}


# ──────────────────────────────────────────────────────────────────────────────
# Main upsert entry-point
# ──────────────────────────────────────────────────────────────────────────────
async def update_crm_company_record_function(
    company_values: Dict[str, Any],
    is_update: bool,
    hubspot_company_id: Optional[str] = None,
    organization_name: Optional[str] = None,
    domain: Optional[str] = None,
    organization_website: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Create **or** update a HubSpot *company*.

    Parameters
    ----------
    company_values:
        Arbitrary key/value dict using **internal** names  
        (``organization_name``, ``primary_domain_of_organization``, etc.)
    is_update:
        • ``True``  → do a best-effort lookup + patch if found  
        • ``False`` → always create a fresh company
    hubspot_company_id:
        Pass a known HS ID to force an update to that record.
    """
    HUBSPOT_API_KEY = get_hubspot_access_token(tool_config)
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
    }

    # ─── 1) Resolve allowed property names ───────────────────────────────────
    valid_props = await _fetch_all_company_properties(headers)

    incoming_props: Dict[str, Any] = {}
    # a) from dict …
    for k, v in company_values.items():
        if v is None:
            continue
        mapped = COMPANY_PROPERTY_MAPPING.get(k)
        if mapped and mapped in valid_props:
            incoming_props[mapped] = v

    # b) from explicit kwargs (fallbacks)
    if organization_name and "name" in valid_props:
        incoming_props.setdefault("name", organization_name)
    if domain and "domain" in valid_props:
        incoming_props.setdefault("domain", domain)
    if organization_website and "website" in valid_props:
        incoming_props.setdefault("website", organization_website)

    # ─── 2) Upsert logic ─────────────────────────────────────────────────────
    found_company_id: Optional[str] = None
    if is_update:
        found_company_id = hubspot_company_id or await _find_existing_company(
            domain=domain,
            name=organization_name,
            valid_props=valid_props,
            tool_cfg=tool_config,
        )

    if found_company_id:
        logging.info("↻ Updating existing company %s", found_company_id)
        return await _patch_company(
            company_id=found_company_id,
            incoming_props=incoming_props,
            headers=headers,
        )

    logging.info("⊕ Creating new company with props: %s", incoming_props)
    return await _create_new_hubspot_company(incoming_props, headers)


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────
async def _patch_company(
    company_id: str,
    incoming_props: Dict[str, Any],
    headers: Dict[str, str],
) -> Dict[str, Any]:
    """Patch only the changed / conditionally-empty properties."""
    current = await _get_company_by_id(company_id, headers)
    if not current:
        raise RuntimeError(f"Company {company_id} vanished during update step.")

    current_props = current.get("properties", {})
    hubspot_props: Dict[str, Any] = {}

    for prop, val in incoming_props.items():
        if prop in CONDITIONAL_UPDATE_PROPS:
            if _is_empty(current_props.get(prop)):
                hubspot_props[prop] = val
        else:
            hubspot_props[prop] = val

    if not hubspot_props:
        logging.info("No new data to patch for company %s; skipping.", company_id)
        return current

    url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
    async with aiohttp.ClientSession() as s:
        async with s.patch(url, headers=headers, json={"properties": hubspot_props}) as r:
            res = await r.json()
            if r.status != 200:
                raise RuntimeError(f"Company update failed {r.status}: {res}")
            return res


async def _create_new_hubspot_company(
    properties: Dict[str, Any], headers: Dict[str, str]
) -> Dict[str, Any]:
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json={"properties": properties}) as r:
            data = await r.json()
            if r.status not in (200, 201):
                raise RuntimeError(f"Create company failed {r.status}: {data}")
            return data


async def _find_existing_company(
    domain: Optional[str],
    name: Optional[str],
    valid_props: List[str],
    tool_cfg: Optional[List[Dict]],
) -> Optional[str]:
    """Return company ID if a matching record exists, else None."""
    filters = []
    if domain:
        filters.append({"propertyName": "domain", "operator": "EQ", "value": domain})
    if not filters and name:
        filters.append({"propertyName": "name", "operator": "EQ", "value": name})

    if not filters:
        return None

    res = await search_hubspot_objects(
        object_type="companies",
        filters=filters,
        limit=1,
        tool_config=tool_cfg,
        properties=["name", "domain", "website"],
    )
    hits = res.get("results", [])
    return hits[0]["id"] if hits else None


async def _fetch_all_company_properties(headers: Dict[str, str]) -> List[str]:
    url = "https://api.hubapi.com/crm/v3/properties/companies"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers) as r:
            if r.status != 200:
                raise RuntimeError(f"Company prop fetch failed {r.status}: {await r.text()}")
            data = await r.json()
            return [p["name"] for p in data.get("results", [])]


async def _get_company_by_id(company_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    url = f"https://api.hubapi.com/crm/v3/objects/companies/{company_id}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers) as r:
            data = await r.json()
            if r.status != 200:
                raise RuntimeError(f"Fetch company {company_id} failed: {r.status} {data}")
            return data
