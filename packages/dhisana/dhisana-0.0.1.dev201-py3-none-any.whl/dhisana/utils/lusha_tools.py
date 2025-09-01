import os
import json
import logging
from typing import Dict, List, Optional

import aiohttp
import backoff

from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.assistant_tool_tag import assistant_tool


def get_lusha_credentials_from_config(
    tool_config: Optional[List[Dict]] = None
) -> Optional[str]:
    """
    Retrieve Lusha API key from the tool_config (looking for 'name' == 'lusha'),
    or fall back to environment variables if not found.

    Args:
        tool_config (List[Dict], optional): 
            Configuration list that may contain Lusha credentials.

    Returns:
        str: Lusha API key from tool_config or environment variables
    """
    lusha_api_key = None

    if tool_config:
        lusha_config = next(
            (item for item in tool_config if item.get("name") == "lusha"),
            None
        )
        if lusha_config:
            # Convert the list of dicts under 'configuration' to a map {name: value}
            config_map = {
                cfg["name"]: cfg["value"]
                for cfg in lusha_config.get("configuration", [])
                if cfg
            }
            lusha_api_key = config_map.get("apiKey")
            config_map.get("apiSecret")

    # Fallback to environment variables if not found in tool_config
    lusha_api_key = lusha_api_key or os.environ.get("LUSHA_API_KEY")
    if not lusha_api_key:
        raise ValueError(
            "Lusha integration is not configured. Please configure the connection to Lusha in Integrations."
        )
    return lusha_api_key


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, Exception),
    max_tries=3,
    giveup=lambda e: not (isinstance(e, aiohttp.ClientResponseError) and e.status == 429),
    factor=2,
)
async def enrich_person_info_from_lusha(
    linkedin_url: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> dict:
    """
    Fetch a person's details from Lusha using LinkedIn URL, email, or phone number.

    Args:
        linkedin_url (str, optional): LinkedIn profile URL of the person.
        email (str, optional): Email address of the person.
        phone (str, optional): Phone number of the person.
        tool_config (List[Dict], optional): Configuration list that may contain Lusha credentials.

    Returns:
        dict: JSON response containing person information, or an error message.
    """
    try:
        access_token = get_lusha_credentials_from_config(tool_config)
    except ValueError as e:
        return {"error": str(e)}

    if not linkedin_url and not email and not phone:
        return {"error": "At least one of linkedin_url, email, or phone must be provided"}

    # Adjust these details according to Lusha’s actual enrichment endpoint and request format
    url = "https://api.lusha.com/enrich/v1/person"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data: Dict[str, str] = {}
    cache_key_value = None

    if linkedin_url:
        data["linkedin_url"] = linkedin_url
        cache_key_value = linkedin_url
    if email:
        data["email"] = email
    if phone:
        data["phone"] = phone

    if cache_key_value:
        cached_response = retrieve_output("enrich_person_info_from_lusha", cache_key_value)
        if cached_response is not None:
            return cached_response

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_result = await response.json()
                if cache_key_value:
                    cache_output("enrich_person_info_from_lusha", cache_key_value, json_result)
                return json_result
            elif response.status == 429:
                logging.warning("enrich_person_info_from_lusha rate limit hit")
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                error_result = await response.json()
                logging.warning(
                    f"enrich_person_info_from_lusha failed with status {response.status}: {error_result}"
                )
                return {"error": error_result}


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, Exception),
    max_tries=3,
    giveup=lambda e: not (isinstance(e, aiohttp.ClientResponseError) and e.status == 429),
    factor=2,
)
async def enrich_organization_info_from_lusha(
    organization_domain: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> dict:
    """
    Fetch an organization's details from Lusha using the organization domain.

    Args:
        organization_domain (str, optional): Domain of the organization.
        tool_config (List[Dict], optional): Configuration list that may contain Lusha credentials.

    Returns:
        dict: JSON response containing organization information, or an error message.
    """
    access_token = get_lusha_credentials_from_config(tool_config)
    if not access_token:
        return {"error": "Failed to obtain Lusha access token"}

    if not organization_domain:
        return {"error": "Organization domain must be provided"}

    # Adjust these details according to Lusha’s actual company enrichment endpoint
    url = "https://api.lusha.com/enrich/v1/company"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    cached_response = retrieve_output("enrich_organization_info_from_lusha", organization_domain)
    if cached_response is not None:
        return cached_response

    data = {"domain": organization_domain}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_result = await response.json()
                cache_output("enrich_organization_info_from_lusha", organization_domain, json_result)
                return json_result
            elif response.status == 429:
                logging.warning("enrich_organization_info_from_lusha rate limit hit")
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                error_result = await response.json()
                logging.warning(
                    f"enrich_organization_info_from_lusha failed with status {response.status}: {error_result}"
                )
                return {"error": error_result}


async def enrich_user_info_with_lusha(
    input_user_properties: dict,
    tool_config: Optional[List[Dict]] = None
) -> dict:
    """
    Update user info using Lusha data. Checks LinkedIn URL, fetches data, and updates
    the user's properties accordingly.

    Args:
        input_user_properties (dict): Existing properties about the user.
        tool_config (List[Dict], optional): Configuration list that may contain Lusha credentials.

    Returns:
        dict: Updated user properties dictionary with Lusha data.
    """
    linkedin_url = input_user_properties.get("user_linkedin_url", "")
    if not linkedin_url:
        input_user_properties["linkedin_url_match"] = False
        return input_user_properties

    # Fetch person data from Lusha
    lusha_data = await enrich_person_info_from_lusha(
        linkedin_url=linkedin_url,
        tool_config=tool_config
    )
    if not lusha_data:
        input_user_properties["linkedin_url_match"] = False
        return input_user_properties

    person_data = lusha_data.get("person", {})
    additional_props = input_user_properties.get("additional_properties") or {}
    additional_props["lusha_person_data"] = json.dumps(person_data)
    input_user_properties["additional_properties"] = additional_props

    # Fill missing contact info
    if not input_user_properties.get("email"):
        input_user_properties["email"] = person_data.get("email", "")
    if not input_user_properties.get("phone"):
        input_user_properties["phone"] = person_data.get("phone", "")

    # Map some fields
    if person_data.get("name"):
        input_user_properties["full_name"] = person_data["name"]
    if person_data.get("first_name"):
        input_user_properties["first_name"] = person_data["first_name"]
    if person_data.get("last_name"):
        input_user_properties["last_name"] = person_data["last_name"]
    if person_data.get("linkedin_url"):
        input_user_properties["user_linkedin_url"] = person_data["linkedin_url"]
    if person_data.get("company") and person_data["company"].get("domain"):
        input_user_properties["primary_domain_of_organization"] = person_data["company"]["domain"]
    if person_data.get("title"):
        input_user_properties["job_title"] = person_data["title"]
    if person_data.get("headline"):
        input_user_properties["headline"] = person_data["headline"]
    if person_data.get("company") and person_data["company"].get("name"):
        input_user_properties["organization_name"] = person_data["company"]["name"]
    if person_data.get("company") and person_data["company"].get("website"):
        input_user_properties["organization_website"] = person_data["company"]["website"]
    if person_data.get("headline") and not input_user_properties.get("summary_about_lead"):
        input_user_properties["summary_about_lead"] = person_data["headline"]

    # Example: If Lusha provides a list of "keywords" in the company object
    if person_data.get("company") and person_data["company"].get("keywords"):
        input_user_properties["keywords"] = ", ".join(person_data["company"]["keywords"])

    # Derive location
    if person_data.get("city") or person_data.get("state"):
        input_user_properties["lead_location"] = (
            f"{person_data.get('city', '')}, {person_data.get('state', '')}".strip(", ")
        )

    # Check for a match
    first_matched = bool(
        input_user_properties.get("first_name")
        and person_data.get("first_name") == input_user_properties["first_name"]
    )
    last_matched = bool(
        input_user_properties.get("last_name")
        and person_data.get("last_name") == input_user_properties["last_name"]
    )
    if first_matched and last_matched:
        input_user_properties["linkedin_url_match"] = True

    return input_user_properties


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, Exception),
    max_tries=3,
    giveup=lambda e: not (isinstance(e, aiohttp.ClientResponseError) and e.status == 429),
    factor=2,
)
async def get_person_info_from_lusha(
    first_name: str,
    last_name: str,
    company_name: str,
    tool_config: Optional[List[Dict]] = None
) -> dict:
    """
    Calls Lusha v2 GET endpoint with firstName, lastName, and companyName.
    """
    lusha_api_key = get_lusha_credentials_from_config(tool_config)
    if not lusha_api_key:
        return {"error": "No Lusha API key found."}

    url = "https://api.lusha.com/v2/person"
    headers = {"api_key": lusha_api_key}
    params = {
        "firstName": first_name,
        "lastName": last_name,
        "companyName": company_name
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                logging.warning("get_person_info_from_lusha rate limit hit")
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                error_result = await response.json()
                logging.warning(
                    f"get_person_info_from_lusha failed with status {response.status}: {error_result}"
                )
                return {"error": error_result}