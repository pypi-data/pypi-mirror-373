import os
import json
import logging
from typing import Dict, List, Optional, Tuple

import aiohttp
import backoff

from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.assistant_tool_tag import assistant_tool


def get_zoominfo_credentials_from_config(
    tool_config: Optional[List[Dict]] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve ZoomInfo API key and secret from tool_config (looking for 'name' == 'zoominfo'),
    or fall back to environment variables if not found.

    Args:
        tool_config (List[Dict], optional): Configuration list that may contain ZoomInfo credentials.

    Returns:
        Tuple[str, str]: (zoominfo_api_key, zoominfo_api_secret), either from tool_config or environment.
    """
    zoominfo_api_key = None
    zoominfo_api_secret = None

    if tool_config:
        zoominfo_config = next(
            (item for item in tool_config if item.get("name") == "zoominfo"),
            None
        )
        if zoominfo_config:
            # Convert the list of dicts under 'configuration' to a simple map {name: value}
            config_map = {
                cfg["name"]: cfg["value"]
                for cfg in zoominfo_config.get("configuration", [])
                if cfg
            }
            zoominfo_api_key = config_map.get("apiKey")
            zoominfo_api_secret = config_map.get("apiSecret")

    # Fall back to environment variables if not found in tool_config
    zoominfo_api_key = zoominfo_api_key or os.environ.get("ZOOMINFO_API_KEY")
    zoominfo_api_secret = zoominfo_api_secret or os.environ.get("ZOOMINFO_API_SECRET")

    return zoominfo_api_key, zoominfo_api_secret


@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, Exception),
    max_tries=3,
    # Give up if the exception isn't a 429 (rate limit)
    giveup=lambda e: not (isinstance(e, aiohttp.ClientResponseError) and e.status == 429),
    factor=2,
)
async def get_zoominfo_access_token(
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Obtain a ZoomInfo access token using credentials from the provided tool_config
    or environment variables.

    Args:
        tool_config (List[Dict], optional): Configuration list that may contain ZoomInfo credentials.

    Raises:
        EnvironmentError: If the ZoomInfo integration has not been configured.
        Exception: If the ZoomInfo API authentication fails.

    Returns:
        str: The ZoomInfo JWT access token.
    """
    zoominfo_api_key, zoominfo_api_secret = get_zoominfo_credentials_from_config(tool_config)

    if not zoominfo_api_key or not zoominfo_api_secret:
        raise EnvironmentError(
            "ZoomInfo integration is not configured. Please configure the connection to ZoomInfo in Integrations."
        )

    headers = {"Content-Type": "application/json"}
    data = {"username": zoominfo_api_key, "password": zoominfo_api_secret}
    url = "https://api.zoominfo.com/authenticate"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_result = await response.json()
                return json_result.get("accessToken")
            else:
                error_result = await response.json()
                raise Exception(f"Failed to authenticate with ZoomInfo API: {error_result}")


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, Exception),
    max_tries=3,
    giveup=lambda e: not (isinstance(e, aiohttp.ClientResponseError) and e.status == 429),
    factor=2,
)
async def enrich_person_info_from_zoominfo(
    linkedin_url: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> dict:
    """
    Fetch a person's details from ZoomInfo using LinkedIn URL, email, or phone number.

    Args:
        linkedin_url (str, optional): LinkedIn profile URL of the person.
        email (str, optional): Email address of the person.
        phone (str, optional): Phone number of the person.
        tool_config (List[Dict], optional): Configuration list that may contain ZoomInfo credentials.

    Returns:
        dict: JSON response containing person information, or an error message.
    """
    access_token = await get_zoominfo_access_token(tool_config)
    if not access_token:
        return {"error": "Failed to obtain ZoomInfo access token"}

    if not linkedin_url and not email and not phone:
        return {"error": "At least one of linkedin_url, email, or phone must be provided"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data: Dict[str, List[str]] = {}
    cache_key_value = None

    # Build request and check cache
    if linkedin_url:
        data["personLinkedinUrls"] = [linkedin_url]
        cache_key_value = linkedin_url
    if email:
        data["personEmails"] = [email]
    if phone:
        data["personPhones"] = [phone]

    if cache_key_value:
        cached_response = retrieve_output(
            "enrich_person_info_from_zoominfo",
            cache_key_value
        )
        if cached_response is not None:
            return cached_response

    url = "https://api.zoominfo.com/person/contact"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_result = await response.json()
                # Cache if LinkedIn URL was used
                if cache_key_value:
                    cache_output(
                        "enrich_person_info_from_zoominfo",
                        cache_key_value,
                        json_result
                    )
                return json_result
            elif response.status == 429:
                logging.warning("enrich_person_info_from_zoominfo Rate limit hit")
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
                    f"enrich_person_info_from_zoominfo failed with status "
                    f"{response.status}: {error_result}"
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
async def enrich_organization_info_from_zoominfo(
    organization_domain: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> dict:
    """
    Fetch an organization's details from ZoomInfo using the organization domain.

    Args:
        organization_domain (str, optional): Domain of the organization.
        tool_config (List[Dict], optional): Configuration list that may contain ZoomInfo credentials.

    Returns:
        dict: JSON response containing organization information, or an error message.
    """
    access_token = await get_zoominfo_access_token(tool_config)
    if not access_token:
        return {"error": "Failed to obtain ZoomInfo access token"}

    if not organization_domain:
        return {"error": "Organization domain must be provided"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    cached_response = retrieve_output(
        "enrich_organization_info_from_zoominfo",
        organization_domain
    )
    if cached_response is not None:
        return cached_response

    data = {"companyDomains": [organization_domain]}
    url = "https://api.zoominfo.com/company/enrich"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                json_result = await response.json()
                cache_output(
                    "enrich_organization_info_from_zoominfo",
                    organization_domain,
                    json_result
                )
                return json_result
            elif response.status == 429:
                logging.warning("enrich_organization_info_from_zoominfo Rate limit hit")
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
                    f"enrich_organization_info_from_zoominfo failed with status "
                    f"{response.status}: {error_result}"
                )
                return {"error": error_result}


async def enrich_user_info_with_zoominfo(
    input_user_properties: dict,
    tool_config: Optional[List[Dict]]
) -> dict:
    """
    Update user info using ZoomInfo data. Checks LinkedIn URL, fetches data, and updates 
    the user's properties accordingly.

    Args:
        input_user_properties (dict): Existing properties about the user.
        tool_config (List[Dict], optional): Configuration list that may contain ZoomInfo credentials.

    Returns:
        dict: Updated user properties dictionary with ZoomInfo data.
    """
    linkedin_url = input_user_properties.get("user_linkedin_url", "")
    if not linkedin_url:
        input_user_properties["linkedin_url_match"] = False
        return input_user_properties

    linkedin_data = await enrich_person_info_from_zoominfo(
        linkedin_url=linkedin_url,
        tool_config=tool_config
    )
    if not linkedin_data:
        input_user_properties["linkedin_url_match"] = False
        return input_user_properties

    # person_data is extracted from the top-level "person" key in the response
    person_data = linkedin_data.get("person", {})
    additional_props = input_user_properties.get("additional_properties") or {}

    # Store the data under a "zoominfo_person_data" key instead of "apollo_person_data"
    additional_props["zoominfo_person_data"] = json.dumps(person_data)
    input_user_properties["additional_properties"] = additional_props

    # Fill missing contact info
    if not input_user_properties.get("email"):
        input_user_properties["email"] = person_data.get("email", "")
    if not input_user_properties.get("phone"):
        input_user_properties["phone"] = person_data.get("contact", {}).get("sanitized_phone", "")

    # Map fields
    if person_data.get("name"):
        input_user_properties["full_name"] = person_data["name"]
    if person_data.get("first_name"):
        input_user_properties["first_name"] = person_data["first_name"]
    if person_data.get("last_name"):
        input_user_properties["last_name"] = person_data["last_name"]
    if person_data.get("linkedin_url"):
        input_user_properties["user_linkedin_url"] = person_data["linkedin_url"]
    if (
        person_data.get("organization")
        and person_data["organization"].get("primary_domain")
    ):
        input_user_properties["primary_domain_of_organization"] = (
            person_data["organization"]["primary_domain"]
        )
    if person_data.get("title"):
        input_user_properties["job_title"] = person_data["title"]
    if person_data.get("headline"):
        input_user_properties["headline"] = person_data["headline"]
    if (
        person_data.get("organization")
        and person_data["organization"].get("name")
    ):
        input_user_properties["organization_name"] = person_data["organization"]["name"]
    if (
        person_data.get("organization")
        and person_data["organization"].get("website_url")
    ):
        input_user_properties["organization_website"] = person_data["organization"]["website_url"]
    if person_data.get("headline") and not input_user_properties.get("summary_about_lead"):
        input_user_properties["summary_about_lead"] = person_data["headline"]
    if (
        person_data.get("organization")
        and person_data["organization"].get("keywords")
    ):
        input_user_properties["keywords"] = ", ".join(person_data["organization"]["keywords"])

    # Derive location
    if person_data.get("city") or person_data.get("state"):
        input_user_properties["lead_location"] = (
            f"{person_data.get('city', '')}, {person_data.get('state', '')}".strip(", ")
        )

    # Match checks
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
