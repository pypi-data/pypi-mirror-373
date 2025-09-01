import asyncio
import hashlib
import json
import logging
import os
import re
import aiohttp
import backoff

from dhisana.schemas.sales import LeadsQueryFilters, CompanyQueryFilters
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.assistant_tool_tag import assistant_tool
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, List, Optional, Union

from dhisana.utils.clean_properties import cleanup_properties

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_apollo_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the APOLLO_API_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The APOLLO_API_KEY access token.

    Raises:
        ValueError: If the Apollo integration has not been configured.
    """
    APOLLO_API_KEY = None

    if tool_config:
        logger.debug(f"Tool config provided: {tool_config}")
        apollo_config = next(
            (item for item in tool_config if item.get("name") == "apollo"), None
        )
        if apollo_config:
            config_map = {
                item["name"]: item["value"]
                for item in apollo_config.get("configuration", [])
                if item
            }
            APOLLO_API_KEY = config_map.get("apiKey")
        else:
            logger.warning("No 'apollo' config item found in tool_config.")
    else:
        logger.debug("No tool_config provided or it's None.")

    # Check environment variable if no key found yet
    APOLLO_API_KEY = APOLLO_API_KEY or os.getenv("APOLLO_API_KEY")

    if not APOLLO_API_KEY:
        logger.error("Apollo integration is not configured.")
        raise ValueError(
            "Apollo integration is not configured. Please configure the connection to Apollo in Integrations."
        )

    return APOLLO_API_KEY


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_person_info_from_apollo(
    linkedin_url: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    fetch_valid_phone_number: Optional[bool] = False,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Fetch a person's details from Apollo using LinkedIn URL, email, or phone number.
    
    Parameters:
    - **linkedin_url** (*str*, optional): LinkedIn profile URL of the person.
    - **email** (*str*, optional): Email address of the person.
    - **phone** (*str*, optional): Phone number of the person.
    - **fetch_valid_phone_number** (*bool*, optional): If True, include phone numbers in the API response. Defaults to False.

    Returns:
    - **dict**: JSON response containing person information.
    """
    logger.info("Entering enrich_person_info_from_apollo")

    APOLLO_API_KEY = get_apollo_access_token(tool_config)

    if not linkedin_url and not email and not phone:
        logger.warning("No linkedin_url, email, or phone provided. At least one is required.")
        return {'error': "At least one of linkedin_url, email, or phone must be provided"}

    headers = {
        "X-Api-Key": f"{APOLLO_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {}
    if linkedin_url:
        logger.debug(f"LinkedIn URL provided: {linkedin_url}")
        data['linkedin_url'] = linkedin_url
        cached_response = retrieve_output("enrich_person_info_from_apollo", linkedin_url)
        if cached_response is not None:
            logger.info(f"Cache hit for LinkedIn URL: {linkedin_url}")
            return cached_response
    if email:
        logger.debug(f"Email provided: {email}")
        data['email'] = email
    if phone:
        logger.debug(f"Phone provided: {phone}")
        data['phone_numbers'] = [phone]  # Apollo expects a list for phone numbers
    
    # Add reveal_phone_number parameter if fetch_valid_phone_number is True
    if fetch_valid_phone_number:
        logger.debug("fetch_valid_phone_number flag is True, including phone numbers in API response")
        data['reveal_phone_number'] = True

    url = 'https://api.apollo.io/api/v1/people/match'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    if linkedin_url:
                        cache_output("enrich_person_info_from_apollo", linkedin_url, result)
                    logger.info("Successfully retrieved person info from Apollo.")
                    return result
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    await asyncio.sleep(30)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers
                    )
                else:
                    result = await response.json()
                    logger.warning(f"enrich_person_info_from_apollo error: {result}")
                    return {'error': result}
        except Exception as e:
            logger.exception("Exception occurred while fetching person info from Apollo.")
            return {'error': str(e)}


@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def lookup_person_in_apollo_by_name(
    full_name: str,
    company_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Fetch a person's details from Apollo using their full name and optionally company name.

    Parameters:
    - **full_name** (*str*): Full name of the person.
    - **company_name** (*str*, optional): Name of the company where the person works.
    - **tool_config** (*list*, optional): Tool configuration for API keys.

    Returns:
    - **dict**: JSON response containing person information.
    """
    logger.info("Entering lookup_person_in_apollo_by_name")

    if not full_name:
        logger.warning("No full_name provided.")
        return {'error': "Full name is required"}

    APOLLO_API_KEY = get_apollo_access_token(tool_config)
    headers = {
        "X-Api-Key": f"{APOLLO_API_KEY}",
        "Content-Type": "application/json"
    }

    # Construct the query payload
    data = {
        "q_keywords": f"{full_name} {company_name}" if company_name else full_name,
        "page": 1,
        "per_page": 10
    }

    # Build a cache key that includes full_name and company_name (if provided)
    # so that results are correctly cached and retrieved.
    key_item = f"lookup_person_in_apollo_by_name_{full_name}_{company_name or ''}".lower()

    # Attempt to retrieve a cached response first
    cached_response = retrieve_output("lookup_person_in_apollo_by_name", key_item)
    if cached_response is not None:
        logger.info(f"Cache hit for user: {full_name}, company: {company_name or ''}")
        return cached_response

    url = 'https://api.apollo.io/api/v1/mixed_people/search'
    logger.debug(f"Making request to Apollo with payload: {data}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    logger.info("Successfully looked up person by name on Apollo.")
                    cache_output("lookup_person_in_apollo_by_name", key_item, result)
                    return result
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    await asyncio.sleep(30)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers
                    )
                else:
                    result = await response.json()
                    logger.warning(f"lookup_person_in_apollo_by_name error: {result}")
                    return {'error': result}
        except Exception as e:
            logger.exception("Exception occurred while looking up person by name.")
            return {'error': str(e)}

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=30,
)
async def enrich_organization_info_from_apollo(
    organization_domain: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Fetch an organization's details from Apollo using the organization domain.
    
    Parameters:
    - **organization_domain** (*str*, optional): Domain of the organization.

    Returns:
    - **dict**: JSON response containing organization information.
    """
    logger.info("Entering enrich_organization_info_from_apollo")

    APOLLO_API_KEY = get_apollo_access_token(tool_config)

    if not organization_domain:
        logger.warning("No organization domain provided.")
        return {'error': "organization domain must be provided"}

    headers = {
        "X-Api-Key": f"{APOLLO_API_KEY}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json"
    }

    cached_response = retrieve_output("enrich_organization_info_from_apollo", organization_domain)
    if cached_response is not None:
        logger.info(f"Cache hit for organization domain: {organization_domain}")
        return cached_response

    url = f'https://api.apollo.io/api/v1/organizations/enrich?domain={organization_domain}'
    logger.debug(f"Making GET request to Apollo for organization domain: {organization_domain}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    cache_output("enrich_organization_info_from_apollo", organization_domain, result)
                    logger.info("Successfully retrieved organization info from Apollo.")
                    return result
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers
                    )
                else:
                    result = await response.json()
                    logger.warning(f"Error from Apollo while enriching org info: {result}")
                    return {'error': result}
        except Exception as e:
            logger.exception("Exception occurred while fetching organization info from Apollo.")
            return {'error': str(e)}



@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=5,
    giveup=lambda e: e.status != 429,
    factor=2,
)
async def fetch_apollo_data(session, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    logger.info("Entering fetch_apollo_data")
    key_data = f"{url}_{json.dumps(payload, sort_keys=True)}"
    key_hash = hashlib.sha256(key_data.encode()).hexdigest()
    logger.debug(f"Cache key hash: {key_hash}")

    cached_response = retrieve_output("fetch_apollo_data", key_hash)
    if cached_response is not None:
        logger.info("Cache hit for fetch_apollo_data.")
        return cached_response

    logger.debug("No cache hit. Making POST request to Apollo.")
    async with session.post(url, headers=headers, json=payload) as response:
        logger.debug(f"Received response status: {response.status}")
        if response.status == 200:
            result = await response.json()
            cache_output("fetch_apollo_data", key_hash, result)
            logger.info("Successfully fetched data from Apollo and cached it.")
            return result
        elif response.status == 429:
            msg = "Rate limit exceeded"
            logger.warning(msg)
            raise aiohttp.ClientResponseError(
                request_info=response.request_info,
                history=response.history,
                status=response.status,
                message=msg,
                headers=response.headers
            )
        else:
            logger.error(f"Unexpected status code {response.status} from Apollo. Raising exception.")
            response.raise_for_status()


async def search_people_with_apollo(
    tool_config: Optional[List[Dict[str, Any]]] = None,
    dynamic_payload: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    logger.info("Entering search_people_with_apollo")

    if not dynamic_payload:
        logger.warning("No payload given; returning empty result.")
        return []

    api_key = get_apollo_access_token(tool_config)
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    url = "https://api.apollo.io/api/v1/mixed_people/search"
    logger.info(f"Sending payload to Apollo (single page): {json.dumps(dynamic_payload, indent=2)}")

    async with aiohttp.ClientSession() as session:
        data = await fetch_apollo_data(session, url, headers, dynamic_payload)
        if not data:
            logger.error("No data returned from Apollo.")
            return []

        people = data.get("people", [])
        contacts = data.get("contacts", [])
        return people + contacts

def fill_in_properties_with_preference(input_user_properties: dict, person_data: dict) -> dict:
    """
    For each property:
      - If input_user_properties already has a non-empty value, keep it.
      - Otherwise, take the value from person_data if available.
    """

    def is_empty(value):
        """Returns True if the value is None, empty string, or only whitespace."""
        return value is None or (isinstance(value, str) and not value.strip())

    # Email
    if is_empty(input_user_properties.get("email")):
        input_user_properties["email"] = person_data.get("email", "")

    # Phone
    if is_empty(input_user_properties.get("phone")):
        # person_data["contact"] might not be defined, so we chain get calls
        input_user_properties["phone"] = ((person_data.get("contact", {}) or {})
                                          .get("sanitized_phone", ""))

    # Full name
    # Because `person_data.get("name")` has precedence over input_user_properties,
    # we only update it if input_user_properties is empty/None for "full_name".
    if is_empty(input_user_properties.get("full_name")) and person_data.get("name"):
        input_user_properties["full_name"] = person_data["name"]

    # First name
    if is_empty(input_user_properties.get("first_name")) and person_data.get("first_name"):
        input_user_properties["first_name"] = person_data["first_name"]

    # Last name
    if is_empty(input_user_properties.get("last_name")) and person_data.get("last_name"):
        input_user_properties["last_name"] = person_data["last_name"]

    # LinkedIn URL
    if is_empty(input_user_properties.get("user_linkedin_url")) and person_data.get("linkedin_url"):
        input_user_properties["user_linkedin_url"] = person_data["linkedin_url"]

    # Organization data
    org_data = person_data.get("organization") or {}
    if org_data:
        # Primary domain
        if is_empty(input_user_properties.get("primary_domain_of_organization")) and org_data.get("primary_domain"):
            input_user_properties["primary_domain_of_organization"] = org_data["primary_domain"]

        # Organization name
        if is_empty(input_user_properties.get("organization_name")) and org_data.get("name"):
            input_user_properties["organization_name"] = org_data["name"]

        # Organization LinkedIn URL
        if is_empty(input_user_properties.get("organization_linkedin_url")) and org_data.get("linkedin_url"):
            input_user_properties["organization_linkedin_url"] = org_data["linkedin_url"]

        # Organization website
        if is_empty(input_user_properties.get("organization_website")) and org_data.get("website_url"):
            input_user_properties["organization_website"] = org_data["website_url"]

        # Keywords
        if is_empty(input_user_properties.get("keywords")) and org_data.get("keywords"):
            input_user_properties["keywords"] = ", ".join(org_data["keywords"])

    # Title / Job Title
    if is_empty(input_user_properties.get("job_title")) and person_data.get("title"):
        input_user_properties["job_title"] = person_data["title"]

    # Headline
    if is_empty(input_user_properties.get("headline")) and person_data.get("headline"):
        input_user_properties["headline"] = person_data["headline"]

    # Summary about lead (fallback to headline if summary is missing, or if none set yet)
    if is_empty(input_user_properties.get("summary_about_lead")) and person_data.get("headline"):
        input_user_properties["summary_about_lead"] = person_data["headline"]

    # City/State -> lead_location
    city = person_data.get("city", "")
    state = person_data.get("state", "")
    if is_empty(input_user_properties.get("lead_location")) and (city or state):
        lead_location = f"{city}, {state}".strip(", ")
        input_user_properties["lead_location"] = lead_location

    # Filter out placeholder emails
    if input_user_properties.get("email") and "domain.com" in input_user_properties["email"].lower():
        input_user_properties["email"] = ""

    return input_user_properties


async def search_leads_with_apollo(
    query: LeadsQueryFilters,
    max_items_to_search: Optional[int] = 10,
    example_url: Optional[str] = None,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict]:
    logger.info("Entering search_leads_with_apollo")

    max_items = max_items_to_search or 10
    if max_items > 2500:
        logger.warning("Requested max_items_to_search > 2000, overriding to 2000.")
        max_items = 2500

    # -----------------------------
    # A) example_url -> parse query
    # -----------------------------
    if example_url:
        logger.debug(f"example_url provided: {example_url}")

        parsed_url = urlparse(example_url)
        query_string = parsed_url.query

        if not query_string and "?" in parsed_url.fragment:
            fragment_query = parsed_url.fragment.split("?", 1)[1]
            query_string = fragment_query

        query_params = parse_qs(query_string)

        page_list = query_params.get("page", ["1"])
        per_page_list = query_params.get("per_page", ["100"])

        try:
            page_val = int(page_list[-1])
        except ValueError:
            page_val = 1

        try:
            per_page_val = int(per_page_list[-1])
        except ValueError:
            per_page_val = min(max_items, 100)

        dynamic_payload: Dict[str, Any] = {
            "page": page_val,
            "per_page": per_page_val,
        }

        # You can augment this mapping if you have more custom fields
        mapping = {
            "personLocations": "person_locations",
            "organizationNumEmployeesRanges": "organization_num_employees_ranges",
            "personTitles": "person_titles",
            # Important: handle personNotTitles as well
            "personNotTitles": "person_not_titles",

            "qOrganizationJobTitles": "q_keywords",
            "sortAscending": "sort_ascending",
            "sortByField": "sort_by_field",
            "contactEmailStatusV2": "contact_email_status",
            "searchSignalIds": "search_signal_ids",
            "organizationLatestFundingStageCd": "organization_latest_funding_stage_cd",
            "revenueRange[max]": "revenue_range_max",
            "revenueRange[min]": "revenue_range_min",
            "currentlyUsingAnyOfTechnologyUids": "currently_using_any_of_technology_uids",
            "organizationIndustryTagIds": "organization_industry_tag_ids",
            "notOrganizationIds": "not_organization_ids",
        }

        for raw_key, raw_value_list in query_params.items():
            # Strip off [] if present so we can do a snake_case transform
            if raw_key.endswith("[]"):
                key = raw_key[:-2]
            else:
                key = raw_key

            # If the mapping has this raw_key or the stripped key, use it:
            if raw_key in mapping:
                key = mapping[raw_key]
            elif key in mapping:
                key = mapping[key]
            else:
                # fallback: convert camelCase -> snake_case
                key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()

            # If there's only one item, let's pull it out as a single str
            # otherwise, keep it a list
            if len(raw_value_list) == 1:
                final_value: Union[str, List[str]] = raw_value_list[0]
            else:
                final_value = raw_value_list

            # Known booleans
            if key in ("sort_ascending",):
                val_lower = str(final_value).lower()
                final_value = val_lower in ("true", "1", "yes")

            # Parse numeric fields
            if key in ("page", "per_page"):
                try:
                    final_value = int(final_value)
                except ValueError:
                    pass

            # Join arrays for q_keywords
            if key == "q_keywords" and isinstance(final_value, list):
                final_value = " ".join(final_value)

            # ---------------------------------------------
            # Force any param that originated from `[]` to
            # be a list, even if there's only one value.
            # Or handle known array-likely parameters:
            # ---------------------------------------------
            if raw_key.endswith("[]"):
                # Guaranteed to treat it as a list
                if isinstance(final_value, str):
                    final_value = [final_value]
            else:
                # Or if we have a known array param
                if key in (
                    "person_locations",
                    "person_titles",
                    "person_seniorities",
                    "organization_locations",
                    "q_organization_domains",
                    "contact_email_status",
                    "organization_ids",
                    "organization_num_employees_ranges",
                    "person_not_titles",  # <--- added so single item is forced into list
                ):
                    if isinstance(final_value, str):
                        final_value = [final_value]

            dynamic_payload[key] = final_value

        # Remove invalid sort
        if dynamic_payload.get("sort_by_field") == "[none]":
            dynamic_payload.pop("sort_by_field")

        if "per_page" not in query_params:
            dynamic_payload["per_page"] = min(max_items, 100)

    # -----------------------------------
    # B) No example_url -> build from `query`
    # -----------------------------------
    else:
        dynamic_payload = {
            "person_titles": query.person_current_titles or [],
            "person_locations": query.person_locations or [],
            "search_signal_ids": query.filter_by_signals or [],
            "q_keywords": query.search_keywords or "",
            "organization_num_employees_ranges": (
                query.organization_num_employees_ranges
                or [f"{query.min_employees_in_organization or 1},{query.max_employees_in_organization or 1000}"]
            ),
            "page": 1,
            "per_page": min(max_items, 100),
        }
        if query.sort_by_field is not None:
            dynamic_payload["sort_by_field"] = query.sort_by_field
        if query.sort_ascending is not None:
            dynamic_payload["sort_ascending"] = query.sort_ascending

    # -----------------------------
    # C) Fetch multiple pages
    # -----------------------------
    all_people: List[Dict[str, Any]] = []
    total_fetched = 0

    current_page = int(dynamic_payload.get("page", 1))
    per_page = int(dynamic_payload.get("per_page", min(max_items, 100)))

    while total_fetched < max_items:
        page_payload = dict(dynamic_payload)
        page_payload["page"] = current_page
        page_payload["per_page"] = per_page

        logger.debug(f"Fetching page {current_page}, per_page {per_page}")
        page_results = await search_people_with_apollo(tool_config=tool_config, dynamic_payload=page_payload)

        if not page_results:
            break

        all_people.extend(page_results)
        page_count = len(page_results)
        total_fetched += page_count

        if page_count < per_page or total_fetched >= max_items:
            break

        current_page += 1

    logger.info(f"Fetched a total of {len(all_people)} items from Apollo (across pages).")

    # -----------------------------------------------
    # Convert raw results -> dictionary objects
    # -----------------------------------------------
    leads: List[Dict[str, Any]] = []
    for user_data_from_apollo in all_people:
        person_data = user_data_from_apollo

        input_user_properties: Dict[str, Any] = {}

        additional_props = input_user_properties.get("additional_properties") or {}
        input_user_properties = fill_in_properties_with_preference(input_user_properties, person_data)
        
        person_data = cleanup_properties(person_data)    
        
        additional_props["apollo_person_data"] = json.dumps(person_data)
        input_user_properties["additional_properties"] = additional_props

        leads.append(input_user_properties)

    logger.info(f"Converted {len(leads)} Apollo records into dictionaries.")
    return leads


async def search_leads_with_apollo_page(
    query: LeadsQueryFilters,
    page: Optional[int] = 1,
    per_page: Optional[int] = 25,
    example_url: Optional[str] = None,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Fetch a single page of Apollo leads using ``page`` and ``per_page``.

    This helper performs one request to the Apollo API and returns the fetched
    leads along with comprehensive pagination metadata.

    Args:
        query: LeadsQueryFilters object containing search criteria
        page: Page number to fetch (1-indexed, defaults to 1)
        per_page: Number of results per page (defaults to 25)
        example_url: Optional URL to parse search parameters from
        tool_config: Optional tool configuration for API keys

    Returns:
        Dict containing:
        - current_page: The current page number
        - per_page: Number of results per page
        - total_entries: Total number of results available
        - total_pages: Total number of pages available
        - has_next_page: Boolean indicating if more pages exist
        - next_page: Next page number (None if no more pages)
        - results: List of lead dictionaries for this page
    """
    logger.info("Entering search_leads_with_apollo_page")

    if example_url:
        parsed_url = urlparse(example_url)
        query_string = parsed_url.query

        if not query_string and "?" in parsed_url.fragment:
            fragment_query = parsed_url.fragment.split("?", 1)[1]
            query_string = fragment_query

        query_params = parse_qs(query_string)

        dynamic_payload: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }

        mapping = {
            "personLocations": "person_locations",
            "organizationNumEmployeesRanges": "organization_num_employees_ranges",
            "personTitles": "person_titles",
            "personNotTitles": "person_not_titles",
            "qOrganizationJobTitles": "q_keywords",
            "sortAscending": "sort_ascending",
            "sortByField": "sort_by_field",
            "contactEmailStatusV2": "contact_email_status",
            "searchSignalIds": "search_signal_ids",
            "organizationLatestFundingStageCd": "organization_latest_funding_stage_cd",
            "revenueRange[max]": "revenue_range_max",
            "revenueRange[min]": "revenue_range_min",
            "currentlyUsingAnyOfTechnologyUids": "currently_using_any_of_technology_uids",
            "organizationIndustryTagIds": "organization_industry_tag_ids",
            "notOrganizationIds": "not_organization_ids",
        }

        for raw_key, raw_value_list in query_params.items():
            if raw_key.endswith("[]"):
                key = raw_key[:-2]
            else:
                key = raw_key

            if raw_key in mapping:
                key = mapping[raw_key]
            elif key in mapping:
                key = mapping[key]
            else:
                key = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

            if len(raw_value_list) == 1:
                final_value: Union[str, List[str]] = raw_value_list[0]
            else:
                final_value = raw_value_list

            if key in ("sort_ascending",):
                val_lower = str(final_value).lower()
                final_value = val_lower in ("true", "1", "yes")

            if key in ("page", "per_page"):
                try:
                    final_value = int(final_value)
                except ValueError:
                    pass

            if key == "q_keywords" and isinstance(final_value, list):
                final_value = " ".join(final_value)

            if raw_key.endswith("[]"):
                if isinstance(final_value, str):
                    final_value = [final_value]
            else:
                if key in (
                    "person_locations",
                    "person_titles",
                    "person_seniorities",
                    "organization_locations",
                    "q_organization_domains",
                    "contact_email_status",
                    "organization_ids",
                    "organization_num_employees_ranges",
                    "person_not_titles",
                ):
                    if isinstance(final_value, str):
                        final_value = [final_value]

            dynamic_payload[key] = final_value

        if dynamic_payload.get("sort_by_field") == "[none]":
            dynamic_payload.pop("sort_by_field")

    # -----------------------------------
    # B) No example_url -> build from `query`
    # -----------------------------------
    else:
        dynamic_payload = {
            "person_titles": query.person_current_titles or [],
            "person_locations": query.person_locations or [],
            "search_signal_ids": query.filter_by_signals or [],
            "q_keywords": query.search_keywords or "",
            "organization_num_employees_ranges": (
                query.organization_num_employees_ranges
                or [f"{query.min_employees_in_organization or 1},{query.max_employees_in_organization or 1000}"]
            ),
        }
        if query.sort_by_field is not None:
            dynamic_payload["sort_by_field"] = query.sort_by_field
        if query.sort_ascending is not None:
            dynamic_payload["sort_ascending"] = query.sort_ascending

    page_payload = dict(dynamic_payload)
    page_payload["page"] = page
    page_payload["per_page"] = per_page

    print(f"Fetching Apollo page {page} with per_page {per_page}..."
          f" Payload: {json.dumps(page_payload, indent=2)}")

    # Get the full Apollo API response with pagination metadata
    api_key = get_apollo_access_token(tool_config)
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    url = "https://api.apollo.io/api/v1/mixed_people/search"
    
    async with aiohttp.ClientSession() as session:
        apollo_response = await fetch_apollo_data(session, url, headers, page_payload)
        if not apollo_response:
            return {"current_page": page, "per_page": per_page, "total_entries": 0, "total_pages": 0, "has_next_page": False, "results": []}

        # Extract pagination metadata
        pagination = apollo_response.get("pagination", {})
        current_page = pagination.get("page", page)
        total_entries = pagination.get("total_entries", 0)
        total_pages = pagination.get("total_pages", 0)
        per_page_actual = pagination.get("per_page", per_page)
        
        # Determine if there are more pages
        has_next_page = current_page < total_pages
        
        # Extract people and contacts
        people = apollo_response.get("people", [])
        contacts = apollo_response.get("contacts", [])
        page_results = people + contacts

    leads: List[Dict[str, Any]] = []
    for person_data in page_results:
        input_user_properties: Dict[str, Any] = {}
        additional_props = input_user_properties.get("additional_properties") or {}
        input_user_properties = fill_in_properties_with_preference(input_user_properties, person_data)
        person_data = cleanup_properties(person_data)
        additional_props["apollo_person_data"] = json.dumps(person_data)
        input_user_properties["additional_properties"] = additional_props
        leads.append(input_user_properties)

    logger.info(f"Converted {len(leads)} Apollo records into dictionaries (single page mode). Page {current_page} of {total_pages}")
    
    return {
        "current_page": current_page,
        "per_page": per_page_actual,
        "total_entries": total_entries,
        "total_pages": total_pages,
        "has_next_page": has_next_page,
        "next_page": current_page + 1 if has_next_page else None,
        "results": leads
    }

@assistant_tool
async def get_organization_domain_from_apollo(
    organization_id: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Fetch an organization's domain from Apollo using the organization ID.

    Parameters:
    - organization_id (str): ID of the organization.

    Returns:
    - dict: Contains the organization's ID and domain, or an error message.
    """
    logger.info("Entering get_organization_domain_from_apollo")

    if not organization_id:
        logger.warning("No organization_id provided.")
        return {'error': 'organization_id must be provided'}

    try:
        result = await get_organization_details_from_apollo(organization_id, tool_config=tool_config)
        if 'error' in result:
            return result
        domain = result.get('primary_domain')
        if domain:
            logger.info("Successfully retrieved domain from Apollo organization details.")
            return {'organization_id': organization_id, 'domain': domain}
        else:
            logger.warning("Domain not found in the organization details.")
            return {'error': 'Domain not found in the organization details'}
    except Exception as e:
        logger.exception("Exception occurred in get_organization_domain_from_apollo.")
        return {'error': str(e)}


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=60,
)
async def get_organization_details_from_apollo(
    organization_id: str,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Fetch an organization's details from Apollo using the organization ID.

    Parameters:
    - organization_id (str): ID of the organization.

    Returns:
    - dict: Organization details or an error message.
    """
    logger.info("Entering get_organization_details_from_apollo")

    APOLLO_API_KEY = get_apollo_access_token(tool_config)
    if not organization_id:
        logger.warning("No organization_id provided.")
        return {'error': "Organization ID must be provided"}

    headers = {
        "X-Api-Key": APOLLO_API_KEY,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Accept": "application/json"
    }

    cached_response = retrieve_output("get_organization_details_from_apollo", organization_id)
    if cached_response is not None:
        logger.info(f"Cache hit for organization ID: {organization_id}")
        return cached_response

    url = f'https://api.apollo.io/api/v1/organizations/{organization_id}'
    logger.debug(f"Making GET request to Apollo for organization ID: {organization_id}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    org_details = result.get('organization', {})
                    if org_details:
                        cache_output("get_organization_details_from_apollo", organization_id, org_details)
                        logger.info("Successfully retrieved organization details from Apollo.")
                        return org_details
                    else:
                        logger.warning("Organization details not found in the response.")
                        return {'error': 'Organization details not found in the response'}
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    limit_minute = response.headers.get('x-rate-limit-minute')
                    limit_hourly = response.headers.get('x-rate-limit-hourly')
                    limit_daily = response.headers.get('x-rate-limit-daily')
                    logger.info(f"get_organization_details_from_apollo x-rate-limit-minute: {limit_minute}")
                    logger.info(f"get_organization_details_from_apollo x-rate-limit-hourly: {limit_hourly}")
                    logger.info(f"get_organization_details_from_apollo x-rate-limit-daily: {limit_daily}")
                    logger.warning(msg)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers
                    )
                else:
                    result = await response.json()
                    logger.warning(f"get_organization_details_from_apollo error: {result}")
                    return {'error': result}
        except Exception as e:
            logger.exception("Exception occurred while fetching organization details from Apollo.")
            return {'error': str(e)}


async def enrich_user_info_with_apollo(
    input_user_properties: Dict[str, Any],
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Enriches the user info (input_user_properties) with data from Apollo.
    Attempts direct enrichment if LinkedIn URL or email is provided; otherwise,
    performs a name-based search. Updates the user_properties dictionary in place.

    Parameters:
    - input_user_properties (Dict[str, Any]): A dictionary with user details.
    - tool_config (List[Dict], optional): Apollo tool configuration.

    Returns:
    - Dict[str, Any]: Updated input_user_properties with enriched data from Apollo.
    """
    logger.info("Entering enrich_user_info_with_apollo")

    if not input_user_properties:
        logger.warning("No input_user_properties provided; returning empty dict.")
        return {}

    linkedin_url = input_user_properties.get("user_linkedin_url", "")
    email = input_user_properties.get("email", "")
    user_data_from_apollo = None

    logger.debug(f"Properties => LinkedIn URL: {linkedin_url}, Email: {email}")

    # If LinkedIn url or email is present, attempt direct enrichment
    if linkedin_url or email:
        try:
            user_data_from_apollo = await enrich_person_info_from_apollo(
                linkedin_url=linkedin_url,
                email=email,
                tool_config=tool_config
            )
        except Exception:
            logger.exception("Exception occurred while enriching person info from Apollo by LinkedIn or email.")
    else:
        # Fallback to name-based lookup
        first_name = input_user_properties.get("first_name", "")
        last_name = input_user_properties.get("last_name", "")
        full_name = input_user_properties.get("full_name", f"{first_name} {last_name}").strip()
        company = input_user_properties.get("organization_name", "")

        if not full_name:
            logger.warning("No full_name or (first_name + last_name) provided.")
            input_user_properties["found_user_in_apollo"] = False
            return input_user_properties

        logger.debug(f"Looking up Apollo by name: {full_name}, company: {company}")
        try:
            search_result = await lookup_person_in_apollo_by_name(
                full_name=full_name,
                company_name=company,
                tool_config=tool_config
            )

            # Extract people and contacts from the search result
            people = search_result.get("people", [])
            contacts = search_result.get("contacts", [])
            results = people + contacts
            logger.info(f"Name-based lookup returned {len(results)} results from Apollo.")

            for person in results:
                person_name = person.get("name", "").lower()
                person_first_name = person.get("first_name", "").lower()
                person_last_name = person.get("last_name", "").lower()
                person_company = (person.get("organization", {}) or {}).get("name", "").lower()

                # Match the full name or first/last name and company
                if (
                    (person_name == full_name.lower() or
                     (person_first_name == first_name.lower() and person_last_name == last_name.lower()))
                    and (not company or person_company == company.lower())
                ):
                    logger.info(f"Found matching person {person.get('name')} in Apollo. Enriching data.")
                    linkedin_url = person.get("linkedin_url", "")
                    if linkedin_url:
                        try:
                            user_data_from_apollo = await enrich_person_info_from_apollo(
                                linkedin_url=linkedin_url,
                                tool_config=tool_config
                            )
                        except Exception:
                            logger.exception("Exception occurred during second stage Apollo enrichment.")
                    if user_data_from_apollo:
                        break
        except Exception:
            logger.exception("Exception occurred while performing name-based lookup in Apollo.")

    if not user_data_from_apollo:
        logger.debug("No user data returned from Apollo.")
        input_user_properties["found_user_in_apollo"] = False
        return input_user_properties

    # At this point, user_data_from_apollo likely has "person" key
    person_data = user_data_from_apollo.get("person", {})
    additional_props = input_user_properties.get("additional_properties") or {}
    

    # Fill missing contact info if not already present
    if not input_user_properties.get("email"):
        input_user_properties["email"] = person_data.get("email", "")
    if not input_user_properties.get("phone"):
        input_user_properties["phone"] = (person_data.get("contact", {}) or {}).get("sanitized_phone", "")

    # Map fields
    if person_data.get("name"):
        input_user_properties["full_name"] = person_data["name"]
    if person_data.get("first_name"):
        input_user_properties["first_name"] = person_data["first_name"]
    if person_data.get("last_name"):
        input_user_properties["last_name"] = person_data["last_name"]
    if person_data.get("linkedin_url"):
        input_user_properties["user_linkedin_url"] = person_data["linkedin_url"]

    if person_data.get("organization"):
        org_data = person_data["organization"] or {}
        if org_data.get("primary_domain"):
            input_user_properties["primary_domain_of_organization"] = org_data["primary_domain"]
        if org_data.get("name"):
            input_user_properties["organization_name"] = org_data["name"]
        if org_data.get("linkedin_url"):
            input_user_properties["organization_linkedin_url"] = org_data["linkedin_url"]
        if org_data.get("website_url"):
            input_user_properties["organization_website"] = org_data["website_url"]
        if org_data.get("keywords"):
            input_user_properties["keywords"] = ", ".join(org_data["keywords"])

    if person_data.get("title"):
        input_user_properties["job_title"] = person_data["title"]
    if person_data.get("headline"):
        input_user_properties["headline"] = person_data["headline"]
        # If there's no summary_about_lead, reuse the person's headline
        if not input_user_properties.get("summary_about_lead"):
            input_user_properties["summary_about_lead"] = person_data["headline"]

    # Derive location
    city = person_data.get("city", "")
    state = person_data.get("state", "")
    if city or state:
        input_user_properties["lead_location"] = f"{city}, {state}".strip(", ")

    # Verify name match
    first_matched = bool(
        input_user_properties.get("first_name")
        and person_data.get("first_name") == input_user_properties["first_name"]
    )
    last_matched = bool(
        input_user_properties.get("last_name")
        and person_data.get("last_name") == input_user_properties["last_name"]
    )
    if first_matched and last_matched:
        logger.info("Matching user found and data enriched from Apollo.")
        input_user_properties["found_user_in_apollo"] = True
    
    person_data = cleanup_properties(person_data)
    additional_props["apollo_person_data"] = json.dumps(person_data)
    input_user_properties["additional_properties"] = additional_props

    return input_user_properties


async def search_companies_with_apollo(
    tool_config: Optional[List[Dict[str, Any]]] = None,
    dynamic_payload: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Search for companies using Apollo's organizations/search endpoint.
    
    Args:
        tool_config: Apollo API configuration
        dynamic_payload: Search parameters for the API call
        
    Returns:
        List of company/organization dictionaries
    """
    logger.info("Entering search_companies_with_apollo")

    if not dynamic_payload:
        logger.warning("No payload given; returning empty result.")
        return []

    api_key = get_apollo_access_token(tool_config)
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    url = "https://api.apollo.io/api/v1/organizations/search"
    logger.info(f"Sending payload to Apollo organizations endpoint (single page): {json.dumps(dynamic_payload, indent=2)}")

    async with aiohttp.ClientSession() as session:
        data = await fetch_apollo_data(session, url, headers, dynamic_payload)
        if not data:
            logger.error("No data returned from Apollo organizations search.")
            return []

        organizations = data.get("organizations", [])
        accounts = data.get("accounts", [])  # Apollo sometimes returns accounts as well
        return organizations + accounts


def fill_in_company_properties(company_data: dict) -> dict:
    """
    Convert Apollo company/organization data into a standardized format.
    
    Args:
        company_data: Raw company data from Apollo API
        
    Returns:
        Dictionary with standardized company properties
    """
    company_properties = {}

    # Basic company information
    company_properties["organization_name"] = company_data.get("name", "")
    company_properties["primary_domain"] = company_data.get("primary_domain", "")
    company_properties["website_url"] = company_data.get("website_url", "")
    company_properties["organization_linkedin_url"] = company_data.get("linkedin_url", "")
    
    # Location information
    company_properties["organization_city"] = company_data.get("city", "")
    company_properties["organization_state"] = company_data.get("state", "")
    company_properties["organization_country"] = company_data.get("country", "")
    
    # Create a combined location string
    location_parts = [
        company_data.get("city", ""),
        company_data.get("state", ""),
        company_data.get("country", "")
    ]
    company_properties["organization_location"] = ", ".join([part for part in location_parts if part])

    # Company size and financial info
    company_properties["employee_count"] = company_data.get("estimated_num_employees", 0)
    company_properties["annual_revenue"] = company_data.get("annual_revenue", 0)
    
    # Industry and business info
    company_properties["industry"] = company_data.get("industry", "")
    company_properties["keywords"] = ", ".join(company_data.get("keywords", []))
    company_properties["description"] = company_data.get("description", "")
    
    # Funding and growth
    company_properties["founded_year"] = company_data.get("founded_year", "")
    company_properties["funding_stage"] = company_data.get("latest_funding_stage", "")
    company_properties["total_funding"] = company_data.get("total_funding", 0)
    
    # Technology stack
    tech_stack = company_data.get("technology_names", [])
    if tech_stack:
        company_properties["technology_stack"] = ", ".join(tech_stack)
    
    # Apollo-specific IDs
    company_properties["apollo_organization_id"] = company_data.get("id", "")
    
    # Additional metadata
    company_properties["phone"] = company_data.get("phone", "")
    company_properties["facebook_url"] = company_data.get("facebook_url", "")
    company_properties["twitter_url"] = company_data.get("twitter_url", "")
    
    # Store raw data for reference
    company_properties["additional_properties"] = {
        "apollo_organization_data": json.dumps(cleanup_properties(company_data))
    }

    return company_properties


@assistant_tool
async def search_companies_with_apollo_page(
    query: CompanyQueryFilters,
    page: Optional[int] = 1,
    per_page: Optional[int] = 25,
    example_url: Optional[str] = None,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Fetch a single page of Apollo companies using ``page`` and ``per_page``.

    This helper performs one request to the Apollo API and returns the fetched
    companies along with comprehensive pagination metadata.

    Args:
        query: CompanyQueryFilters object containing search criteria
        page: Page number to fetch (1-indexed, defaults to 1)
        per_page: Number of results per page (defaults to 25)
        example_url: Optional URL to parse search parameters from
        tool_config: Optional tool configuration for API keys

    Returns:
        Dict containing:
        - current_page: The current page number
        - per_page: Number of results per page
        - total_entries: Total number of results available
        - total_pages: Total number of pages available
        - has_next_page: Boolean indicating if more pages exist
        - next_page: Next page number (None if no more pages)
        - results: List of company dictionaries for this page
    """
    logger.info("Entering search_companies_with_apollo_page")

    if example_url:
        parsed_url = urlparse(example_url)
        query_string = parsed_url.query

        if not query_string and "?" in parsed_url.fragment:
            fragment_query = parsed_url.fragment.split("?", 1)[1]
            query_string = fragment_query

        query_params = parse_qs(query_string)

        dynamic_payload: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }

        # Organization-specific URL parameter mapping
        mapping = {
            "organizationLocations": "organization_locations",
            "organizationNumEmployeesRanges": "organization_num_employees_ranges",
            "organizationIndustries": "organization_industries",
            "organizationIndustryTagIds": "organization_industry_tag_ids",
            "qKeywords": "q_keywords",
            "qOrganizationDomains": "q_organization_domains",
            "sortAscending": "sort_ascending",
            "sortByField": "sort_by_field",
            "organizationLatestFundingStageCd": "organization_latest_funding_stage_cd",
            "revenueRange[max]": "revenue_range_max",
            "revenueRange[min]": "revenue_range_min",
            "currentlyUsingAnyOfTechnologyUids": "currently_using_any_of_technology_uids",
            "organizationIds": "organization_ids",
            "notOrganizationIds": "not_organization_ids",
            "qOrganizationSearchListId": "q_organization_search_list_id",
            "qNotOrganizationSearchListId": "q_not_organization_search_list_id",
        }

        for raw_key, raw_value_list in query_params.items():
            if raw_key.endswith("[]"):
                key = raw_key[:-2]
            else:
                key = raw_key

            if raw_key in mapping:
                key = mapping[raw_key]
            elif key in mapping:
                key = mapping[key]
            else:
                key = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

            if len(raw_value_list) == 1:
                final_value: Union[str, List[str]] = raw_value_list[0]
            else:
                final_value = raw_value_list

            if key in ("sort_ascending",):
                val_lower = str(final_value).lower()
                final_value = val_lower in ("true", "1", "yes")

            if key in ("page", "per_page", "revenue_range_min", "revenue_range_max"):
                try:
                    final_value = int(final_value)
                except ValueError:
                    pass

            if key == "q_organization_keyword_tags":
                # Handle both string and list inputs, split by comma if string
                if isinstance(final_value, str):
                    # Split by comma and strip whitespace
                    final_value = [tag.strip() for tag in final_value.split(",") if tag.strip()]
                elif isinstance(final_value, list):
                    # If it's already a list, flatten any comma-separated items
                    flattened = []
                    for item in final_value:
                        if isinstance(item, str) and "," in item:
                            flattened.extend([tag.strip() for tag in item.split(",") if tag.strip()])
                        else:
                            flattened.append(item)
                    final_value = flattened

            if raw_key.endswith("[]"):
                if isinstance(final_value, str):
                    final_value = [final_value]
            else:
                if key in (
                    "organization_locations",
                    "organization_industries",
                    "organization_industry_tag_ids",
                    "q_organization_domains",
                    "q_organization_keyword_tags",
                    "organization_ids",
                    "not_organization_ids",
                    "organization_num_employees_ranges",
                    "currently_using_any_of_technology_uids",
                    "organization_latest_funding_stage_cd",
                ):
                    if isinstance(final_value, str):
                        final_value = [final_value]

            dynamic_payload[key] = final_value

        if dynamic_payload.get("sort_by_field") == "[none]":
            dynamic_payload.pop("sort_by_field")

    # -----------------------------------
    # B) No example_url -> build from `query`
    # -----------------------------------
    else:
        dynamic_payload = {}
        
        # Only add fields if they have values (Apollo doesn't like empty arrays)
        if query.organization_locations:
            dynamic_payload["organization_locations"] = query.organization_locations
        if query.organization_industries:
            dynamic_payload["organization_industries"] = query.organization_industries
        if query.organization_industry_tag_ids:
            dynamic_payload["organization_industry_tag_ids"] = query.organization_industry_tag_ids
            
        # Handle employee ranges
        employee_ranges = []
        if query.organization_num_employees_ranges:
            employee_ranges = query.organization_num_employees_ranges
        elif query.min_employees or query.max_employees:
            employee_ranges = [f"{query.min_employees or 1},{query.max_employees or 1000}"]
        
        if employee_ranges:
            dynamic_payload["organization_num_employees_ranges"] = employee_ranges

        # Add optional parameters only if they have values
        if query.q_keywords:
            # Split comma-separated keywords into an array for company search
            if isinstance(query.q_keywords, str):
                keyword_tags = [tag.strip() for tag in query.q_keywords.split(",") if tag.strip()]
            else:
                keyword_tags = query.q_keywords
            dynamic_payload["q_organization_keyword_tags"] = keyword_tags
        if query.q_organization_domains:
            dynamic_payload["q_organization_domains"] = query.q_organization_domains
        if query.revenue_range_min is not None:
            dynamic_payload["revenue_range_min"] = query.revenue_range_min
        if query.revenue_range_max is not None:
            dynamic_payload["revenue_range_max"] = query.revenue_range_max
        if query.organization_latest_funding_stage_cd:
            dynamic_payload["organization_latest_funding_stage_cd"] = query.organization_latest_funding_stage_cd
        if query.currently_using_any_of_technology_uids:
            dynamic_payload["currently_using_any_of_technology_uids"] = query.currently_using_any_of_technology_uids
        if query.organization_ids:
            dynamic_payload["organization_ids"] = query.organization_ids
        if query.not_organization_ids:
            dynamic_payload["not_organization_ids"] = query.not_organization_ids
        if query.q_organization_search_list_id:
            dynamic_payload["q_organization_search_list_id"] = query.q_organization_search_list_id
        if query.q_not_organization_search_list_id:
            dynamic_payload["q_not_organization_search_list_id"] = query.q_not_organization_search_list_id
        if query.sort_by_field is not None:
            dynamic_payload["sort_by_field"] = query.sort_by_field
        if query.sort_ascending is not None:
            dynamic_payload["sort_ascending"] = query.sort_ascending

    # Remove sorting parameters that may not be supported by organizations endpoint
    if "sort_by_field" in dynamic_payload:
        dynamic_payload.pop("sort_by_field")
    if "sort_ascending" in dynamic_payload:
        dynamic_payload.pop("sort_ascending")

    page_payload = dict(dynamic_payload)
    page_payload["page"] = page
    page_payload["per_page"] = per_page
    
    # Clean up the payload - remove empty arrays and None values that Apollo doesn't like
    cleaned_payload = {}
    for key, value in page_payload.items():
        if value is not None:
            if isinstance(value, list):
                # Only include non-empty lists
                if value:
                    cleaned_payload[key] = value
            else:
                cleaned_payload[key] = value
    
    # Ensure page and per_page are always included
    cleaned_payload["page"] = page
    cleaned_payload["per_page"] = per_page

    print(f"Fetching Apollo companies page {page} with per_page {per_page}..."
          f" Payload: {json.dumps(cleaned_payload, indent=2)}")

    # Get the full Apollo API response with pagination metadata
    api_key = get_apollo_access_token(tool_config)
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    url = "https://api.apollo.io/api/v1/organizations/search"
    
    async with aiohttp.ClientSession() as session:
        apollo_response = await fetch_apollo_data(session, url, headers, cleaned_payload)
        if not apollo_response:
            return {
                "current_page": page, 
                "per_page": per_page, 
                "total_entries": 0, 
                "total_pages": 0, 
                "has_next_page": False, 
                "results": []
            }

        # Extract pagination metadata
        pagination = apollo_response.get("pagination", {})
        current_page = pagination.get("page", page)
        total_entries = pagination.get("total_entries", 0)
        total_pages = pagination.get("total_pages", 0)
        per_page_actual = pagination.get("per_page", per_page)
        
        # Determine if there are more pages
        has_next_page = current_page < total_pages
        
        # Extract organizations and accounts
        organizations = apollo_response.get("organizations", [])
        accounts = apollo_response.get("accounts", [])
        page_results = organizations + accounts

    companies: List[Dict[str, Any]] = []
    for company_data in page_results:
        company_properties = fill_in_company_properties(company_data)
        companies.append(company_properties)

    logger.info(f"Converted {len(companies)} Apollo company records into standardized dictionaries (single page mode). Page {current_page} of {total_pages}")
    
    return {
        "current_page": current_page,
        "per_page": per_page_actual,
        "total_entries": total_entries,
        "total_pages": total_pages,
        "has_next_page": has_next_page,
        "next_page": current_page + 1 if has_next_page else None,
        "results": companies
    }
