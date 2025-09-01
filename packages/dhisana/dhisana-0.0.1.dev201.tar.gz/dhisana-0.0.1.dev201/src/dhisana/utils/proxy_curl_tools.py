import asyncio
import json
import logging
import os
import re
import aiohttp
import backoff
from typing import Any, Dict, List, Optional

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output
from dhisana.utils.clean_properties import cleanup_properties
from dhisana.utils.search_router import search_google_with_tools
from urllib.parse import urlparse, urlunparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_proxycurl_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the PROXY_CURL_API_KEY access token from the provided tool configuration.

    Raises:
        ValueError: If the Proxycurl integration has not been configured.
    """
    PROXY_CURL_API_KEY = None

    if tool_config:
        logger.debug(f"Tool config provided: {tool_config}")
        proxy_curl_config = next(
            (item for item in tool_config if item.get("name") == "proxycurl"), None
        )
        if proxy_curl_config:
            config_map = {
                item["name"]: item["value"]
                for item in proxy_curl_config.get("configuration", [])
                if item
            }
            PROXY_CURL_API_KEY = config_map.get("apiKey")
        else:
            logger.warning("No 'proxycurl' config item found in tool_config.")
    else:
        logger.debug("No tool_config provided or it's None.")

    # Check environment variable if no key found yet
    PROXY_CURL_API_KEY = PROXY_CURL_API_KEY or os.getenv("PROXY_CURL_API_KEY")

    if not PROXY_CURL_API_KEY:
        logger.error("Proxycurl integration is not configured.")
        raise ValueError(
            "Proxycurl integration is not configured. Please configure the connection to Proxycurl in Integrations."
        )

    return PROXY_CURL_API_KEY


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_person_info_from_proxycurl(
    linkedin_url: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict:
    """
    Fetch a person's details from Proxycurl using LinkedIn URL, email, or phone number.

    Returns:
        dict: JSON response containing person information or an error.
    """
    logger.info("Entering enrich_person_info_from_proxycurl")

    try:
        API_KEY = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        return {"error": str(e)}

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    if not linkedin_url and not email and not phone:
        logger.warning("No linkedin_url, email, or phone provided. At least one is required.")
        return {'error': "At least one of linkedin_url, email, or phone must be provided"}

    # Check cache if linkedin_url is provided
    if linkedin_url:
        cached_response = retrieve_output("enrich_person_info_from_proxycurl", linkedin_url)
        if cached_response is not None and cached_response.get('error') is None:
            logger.info(f"Cache hit for LinkedIn URL: {linkedin_url}")
            return cached_response

    params = {}
    if linkedin_url:
        params['url'] = linkedin_url
    if email:
        params['email'] = email
    else:
        # Request Proxycurl to include personal emails when no email is provided
        params['personal_email'] = 'include'
    if phone:
        params['phone'] = phone

    url = 'https://enrichlayer.com/api/v2/profile'
    logger.debug(f"Making request to Proxycurl with params: {params}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=HEADERS, params=params) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    if linkedin_url:
                        cache_output("enrich_person_info_from_proxycurl", linkedin_url, result)
                    logger.info("Successfully retrieved person info from Proxycurl.")
                    return result
                elif response.status == 404:
                    msg = "Person not found"
                    logger.warning(msg)
                    return {'error': msg}
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    # Sleep and then return an error (no raise)
                    await asyncio.sleep(30)
                    return {'error': msg}
                else:
                    error_text = await response.text()
                    logger.error(f"Error from Proxycurl: {error_text}")
                    return {'error': error_text}
        except Exception as e:
            logger.exception("Exception occurred while fetching person info from Proxycurl.")
            return {"error": str(e)}


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def lookup_person_in_proxy_curl_by_name(
    first_name: str,
    last_name: str,
    company_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict:
    """
    Look up a person in Proxycurl by first and last name, optionally a company name.

    Returns:
        dict: JSON response containing search results or an error.
    """
    logger.info("Entering lookup_person_in_proxy_curl_by_name")

    if not first_name or not last_name:
        logger.warning("First name or last name missing for lookup.")
        return {'error': "Full name is required"}

    try:
        API_KEY = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        return {"error": str(e)}

    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {
        'first_name': first_name,
        'last_name': last_name,
        'page_size': '1',
    }
    if company_name:
        params['current_company_name'] = company_name

    key = f"{first_name} {last_name} {company_name}".strip()
    if key:
        cached_response = retrieve_output("lookup_person_in_proxycurl_by_name", key)
        if cached_response is not None:
            logger.info(f"Cache hit for name lookup key: {key}")
            return cached_response

    url = 'https://enrichlayer.com/api/v2/search/person'
    logger.debug(f"Making request to Proxycurl with params: {params}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    cache_output("lookup_person_in_proxycurl_by_name", key, result)
                    logger.info("Successfully retrieved person search info from Proxycurl.")
                    return result
                elif response.status == 404:
                    msg = "Person not found"
                    logger.warning(msg)
                    if key:
                        cache_output("lookup_person_in_proxycurl_by_name", key, {'error': msg})
                    return {'error': msg}
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    await asyncio.sleep(30)
                    return {'error': msg}
                else:
                    result = await response.json()
                    logger.warning(f"lookup_person_in_proxycurl_by_name error: {result}")
                    return {'error': result}
        except Exception as e:
            logger.exception("Exception occurred while looking up person by name.")
            return {"error": str(e)}


def transform_company_data(data: dict) -> dict:
    """
    Transform the company data by mapping:
      - 'name' to 'organization_name'
      - 'website' to 'organization_website'
      - 'industry' to 'organization_industry'
      - 'hq' or 'headquarters' to 'organization_hq_location'
        in the format "city, state, country" (skipping empty parts).
    Copies over all other properties except the ones that are mapped.
    If data is empty, returns an empty dictionary.
    """
    if not data:
        return {}

    transformed = {}

    # Map name, website, and industry
    if "name" in data:
        transformed["organization_name"] = data["name"]
    if "website" in data:
        transformed["organization_website"] = data["website"]
    if "industry" in data:
        transformed["organization_industry"] = data["industry"]
        
    if "company_size" in data:
        transformed["company_size_list"] = data["company_size"]
    
    if "company_size_on_linkedin" in data:
        transformed["organization_size"] = data["company_size_on_linkedin"]
        transformed["company_size"] = data["company_size_on_linkedin"]

    # Determine headquarters info from "hq" or "headquarters"
    hq_data = data.get("hq") or data.get("headquarters")
    if hq_data:
        if isinstance(hq_data, dict):
            city = hq_data.get("city", "")
            state = hq_data.get("geographic_area", "")
            country = hq_data.get("country", "")
            # Join non-empty parts with a comma and a space
            parts = [part for part in (city, state, country) if part]
            transformed["organization_hq_location"] = ", ".join(parts)
        else:
            # If hq_data is not a dict, assume it's already in the desired format
            transformed["organization_hq_location"] = hq_data

    # Copy all other properties, excluding those already mapped
    for key, value in data.items():
        if key not in ("name", "website", "industry", "hq", "headquarters", "company_size"):
            transformed[key] = value

    return transformed


@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_organization_info_from_proxycurl(
    organization_domain: Optional[str] = None,
    organization_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict:
    """
    Fetch an organization's details from Proxycurl using either the organization domain or LinkedIn URL.
    
    Returns:
        dict: Transformed JSON response containing organization information,
              or {'error': ...} on error, or empty dict if not found.
    """
    logger.info("Entering enrich_organization_info_from_proxycurl")

    try:
        API_KEY = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        return {"error": str(e)}

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    if not organization_domain and not organization_linkedin_url:
        logger.warning("No organization domain or LinkedIn URL provided.")
        return {}

    # If LinkedIn URL is provided, standardize it and fetch data
    if organization_linkedin_url:
        logger.debug(f"Organization LinkedIn URL provided: {organization_linkedin_url}")
        if "linkedin.com/company" not in organization_linkedin_url:
            logger.warning("Invalid LinkedIn URL provided." + organization_linkedin_url)
            return {}
        parsed_url = urlparse(organization_linkedin_url)
        if parsed_url.netloc != 'www.linkedin.com':
            standardized_netloc = 'www.linkedin.com'
            standardized_path = parsed_url.path
            if not standardized_path.startswith('/company/'):
                standardized_path = '/company' + standardized_path
            standardized_url = urlunparse(
                parsed_url._replace(netloc=standardized_netloc, path=standardized_path)
            )
            if standardized_url and not standardized_url.endswith('/'):
                standardized_url += '/'
        else:
            standardized_url = organization_linkedin_url
            if standardized_url and not standardized_url.endswith('/'):
                standardized_url += '/'

        # Check cache for standardized LinkedIn URL
        cached_response = retrieve_output("enrich_organization_info_from_proxycurl", standardized_url)
        if cached_response is not None:
            logger.info(f"Cache hit for organization LinkedIn URL: {standardized_url}")
            cached_response = transform_company_data(cached_response)
            return cached_response

        # Fetch details using standardized LinkedIn URL
        url = 'https://enrichlayer.com/api/v2/company'
        params = {
            'url': standardized_url,
            'use_cache': 'if-present',
            'fallback_to_cache': 'on-error',
        }
        logger.debug(f"Making request to Proxycurl with params: {params}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=HEADERS, params=params) as response:
                    logger.debug(f"Received response status: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        transformed_result = transform_company_data(result)
                        cache_output("enrich_organization_info_from_proxycurl", standardized_url, transformed_result)
                        logger.info("Successfully retrieved and transformed organization info from Proxycurl by LinkedIn URL.")
                        return transformed_result
                    elif response.status == 429:
                        msg = "Rate limit exceeded"
                        logger.warning(msg)
                        await asyncio.sleep(30)
                        return {"error": msg}
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from Proxycurl organization info fetch by URL: {error_text}")
                        return {}
            except Exception as e:
                logger.exception("Exception occurred while fetching organization info from Proxycurl by LinkedIn URL.")
                return {"error": str(e)}

    # If organization domain is provided, resolve domain to LinkedIn URL and fetch data
    if organization_domain:
        logger.debug(f"Organization domain provided: {organization_domain}")
        cached_response = retrieve_output("enrich_organization_info_from_proxycurl", organization_domain)
        if cached_response is not None:
            logger.info(f"Cache hit for organization domain: {organization_domain}")
            return cached_response

        resolve_url = 'https://enrichlayer.com/api/v2/company/resolve'
        params = {'domain': organization_domain}
        logger.debug(f"Making request to Proxycurl to resolve domain with params: {params}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(resolve_url, headers=HEADERS, params=params) as response:
                    logger.debug(f"Received response status: {response.status}")
                    if response.status == 200:
                        company_data = await response.json()
                        company_url = company_data.get('url')
                        if company_url:
                            parsed_url = urlparse(company_url)
                            if parsed_url.netloc != 'www.linkedin.com':
                                standardized_netloc = 'www.linkedin.com'
                                standardized_path = parsed_url.path
                                if not standardized_path.startswith('/company/'):
                                    standardized_path = '/company' + standardized_path
                                standardized_url = urlunparse(
                                    parsed_url._replace(netloc=standardized_netloc, path=standardized_path)
                                )
                            else:
                                standardized_url = company_url

                            profile_url = 'https://enrichlayer.com/api/v2/company'
                            try:
                                async with session.get(profile_url, headers=HEADERS, params={'url': standardized_url}) as profile_response:
                                    logger.debug(f"Received profile response status: {profile_response.status}")
                                    if profile_response.status == 200:
                                        result = await profile_response.json()
                                        transformed_result = transform_company_data(result)
                                        cache_output("enrich_organization_info_from_proxycurl", organization_domain, transformed_result)
                                        logger.info("Successfully retrieved and transformed organization info from Proxycurl by domain.")
                                        return transformed_result
                                    elif profile_response.status == 429:
                                        msg = "Rate limit exceeded"
                                        logger.warning(msg)
                                        await asyncio.sleep(30)
                                        return {"error": msg}
                                    else:
                                        error_text = await profile_response.text()
                                        logger.error(f"Error from Proxycurl organization profile fetch by resolved domain: {error_text}")
                                        return {}
                            except Exception as e:
                                logger.exception("Exception occurred while fetching organization profile data.")
                                return {"error": str(e)}
                        else:
                            logger.warning("Company URL not found for the provided domain.")
                            return {}
                    elif response.status == 429:
                        msg = "Rate limit exceeded"
                        logger.warning(msg)
                        await asyncio.sleep(30)
                        return {"error": msg}
                    elif response.status == 404:
                        msg = "Item not found"
                        logger.warning(msg)
                        cache_output("enrich_organization_info_from_proxycurl", organization_domain, {})
                        return {}
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from Proxycurl domain resolve: {error_text}")
                        return {}
            except Exception as e:
                logger.exception("Exception occurred while resolving organization domain on Proxycurl.")
                return {"error": str(e)}

    return {}


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def enrich_job_info_from_proxycurl(
    job_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict:
    """
    Fetch a job's details from Proxycurl using the job URL.

    Returns:
        dict: JSON response containing job information or error.
    """
    logger.info("Entering enrich_job_info_from_proxycurl")

    try:
        API_KEY = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        return {"error": str(e)}

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    if not job_url:
        logger.warning("No job URL provided.")
        return {'error': "Job URL must be provided"}

    # Check cache
    cached_response = retrieve_output("enrich_job_info_from_proxycurl", job_url)
    if cached_response is not None:
        logger.info(f"Cache hit for job URL: {job_url}")
        return cached_response

    params = {'url': job_url}
    api_endpoint = 'https://enrichlayer.com/api/v2/job'
    logger.debug(f"Making request to Proxycurl for job info with params: {params}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_endpoint, headers=HEADERS, params=params) as response:
                logger.debug(f"Received response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    cache_output("enrich_job_info_from_proxycurl", job_url, result)
                    logger.info("Successfully retrieved job info from Proxycurl.")
                    return result
                elif response.status == 429:
                    msg = "Rate limit exceeded"
                    logger.warning(msg)
                    await asyncio.sleep(30)
                    return {'error': msg}
                elif response.status == 404:
                    msg = "Job not found"
                    logger.warning(msg)
                    cache_output("enrich_job_info_from_proxycurl", job_url, {'error': msg})
                    return {'error': msg}
                else:
                    error_text = await response.text()
                    logger.error(f"Error from Proxycurl: {error_text}")
                    return {'error': error_text}
        except Exception as e:
            logger.exception("Exception occurred while fetching job info from Proxycurl.")
            return {"error": str(e)}


@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def search_recent_job_changes(
    job_titles: List[str],
    locations: List[str],
    max_items_to_return: int = 100,
    tool_config: Optional[List[Dict]] = None
) -> List[dict]:
    """
    Search for individuals with specified job titles and locations who have recently changed jobs.

    Returns:
        List[dict]: List of individuals matching the criteria, or empty list on failure/error.
    """
    logger.info("Entering search_recent_job_changes")

    try:
        API_KEY = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return []

    HEADERS = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    url = 'https://enrichlayer.com/api/v2/search/person'
    results = []
    page = 1
    per_page = min(max_items_to_return, 100)

    logger.debug(f"Starting search with job_titles={job_titles}, locations={locations}, max_items={max_items_to_return}")

    async with aiohttp.ClientSession() as session:
        while len(results) < max_items_to_return:
            params = {
                'job_title': ','.join(job_titles),
                'location': ','.join(locations),
                'page': page,
                'num_records': per_page
            }
            logger.debug(f"Request params: {params}")

            try:
                async with session.get(url, headers=HEADERS, params=params) as response:
                    logger.debug(f"Received response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        people = data.get('persons', [])
                        if not people:
                            logger.info("No more people found, ending search.")
                            break
                        results.extend(people)
                        logger.info(f"Fetched {len(people)} results on page {page}. Total so far: {len(results)}")
                        page += 1
                        if len(results) >= max_items_to_return:
                            logger.info("Reached max items limit.")
                            break
                    elif response.status == 429:
                        msg = "Rate limit exceeded"
                        logger.warning(msg)
                        await asyncio.sleep(30)
                        # Without raising, won't trigger another backoff retry
                        # so just continue or break as desired:
                        continue
                    else:
                        error_text = await response.text()
                        logger.error(f"Error while searching recent job changes: {error_text}")
                        break
            except Exception:
                logger.exception("Exception occurred while searching recent job changes.")
                break

    return results[:max_items_to_return]


@assistant_tool
async def find_matching_job_posting_proxy_curl(
    company_name: str,
    keywords_check: List[str],
    optional_keywords: List[str],
    organization_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None  
) -> List[str]:
    """
    Find job postings on LinkedIn for a given company using Google Custom Search,
    then optionally validate those links with Proxycurl.

    Returns:
        List[str]: A list of matching job posting links.
    """
    logger.info("Entering find_matching_job_posting_proxy_curl")

    if not company_name:
        logger.warning("No company name provided.")
        return []
    
    if not keywords_check:
        logger.warning("No keywords_check provided, defaulting to an empty list.")
        keywords_check = []

    if not optional_keywords:
        logger.warning("No optional_keywords provided, defaulting to an empty list.")
        optional_keywords = []

    keywords_list = [kw.strip().lower() for kw in keywords_check]
    job_posting_links = []

    # Build the search query
    keywords_str = ' '.join(f'"{kw}"' for kw in keywords_check)
    optional_keywords_str = ' '.join(f'{kw}' for kw in optional_keywords)
    query = f'site:*linkedin.com/jobs/view/ "{company_name}" {keywords_str} {optional_keywords_str}'
    logger.debug(f"Google search query: {query}")

    # First Google search attempt
    results = await search_google_with_tools(query.strip(), 1, tool_config=tool_config)
    if not isinstance(results, list) or len(results) == 0:
        logger.info("No results found. Attempting fallback query without optional keywords.")
        query = f'site:*linkedin.com/jobs/view/ "{company_name}" {keywords_str}'
        results = await search_google_with_tools(query.strip(), 1, tool_config=tool_config)
        if not isinstance(results, list) or len(results) == 0:
            logger.info("No job postings found in fallback search either.")
            return job_posting_links

    # Process each search result
    for result_item in results:
        try:
            result_json = json.loads(result_item)
        except json.JSONDecodeError:
            logger.debug("Skipping invalid JSON result.")
            continue

        link = result_json.get('link', '')
        if not link:
            logger.debug("No link in result; skipping.")
            continue
        
        if "linkedin.com/jobs/view/" not in link:
            logger.debug("Link is not a LinkedIn job posting; skipping.")
            continue

        # Normalize the LinkedIn domain to www.linkedin.com
        parsed = urlparse(link)
        new_link = parsed._replace(netloc="www.linkedin.com").geturl()
        link = new_link

        # Use Proxycurl to enrich job info
        logger.debug(f"Fetching job info from Proxycurl for link: {link}")
        json_result = await enrich_job_info_from_proxycurl(link, tool_config=tool_config)
        if not json_result or 'error' in json_result:
            logger.debug("No valid job info returned; skipping.")
            continue

        text = json.dumps(json_result).lower()

        # If the user gave an organization_linkedin_url, check if it matches
        company_match = False
        if organization_linkedin_url and json_result.get('company', {}):
            result_url = json_result.get('company', {}).get('url', '').lower()
            result_path = urlparse(result_url).path
            company_path = urlparse(organization_linkedin_url.lower()).path
            company_match = (result_path == company_path)
        else:
            company_match = False

        keywords_found = any(kw in text for kw in keywords_list)

        # If company matches and keywords are found, add to results
        if company_match and keywords_found:
            job_posting_links.append(link)

    logger.info(f"Found {len(job_posting_links)} matching job postings.")
    return job_posting_links


def fill_in_missing_properties(input_user_properties: dict, person_data: dict) -> dict:
    """
    If input_user_properties has a non-empty value for a field, keep it.
    Otherwise, use that field from person_data.
    """

    def is_empty(value):
        # Checks for None, empty string, or string with only whitespace
        return value is None or (isinstance(value, str) and not value.strip())

    # Email - use first personal email if input is empty
    if is_empty(input_user_properties.get("email")):
        personal_emails = person_data.get("personal_emails")
        if isinstance(personal_emails, list) and personal_emails:
            input_user_properties["email"] = personal_emails[0]

    # Phone
    if is_empty(input_user_properties.get("phone")):
        input_user_properties["phone"] = person_data.get("contact", {}).get("sanitized_phone", "")

    # Full name
    if person_data.get("full_name"):
        input_user_properties["full_name"] = person_data["full_name"]

    # First name
    if person_data.get("first_name"):
        input_user_properties["first_name"] = person_data["first_name"]

    # Last name
    if person_data.get("last_name"):
        input_user_properties["last_name"] = person_data["last_name"]

    # Occupation -> job_title
    if person_data.get("occupation"):
        input_user_properties["job_title"] = person_data["occupation"]

    # Headline
    if person_data.get("headline"):
        input_user_properties["headline"] = person_data["headline"]

    # Summary
    if is_empty(input_user_properties.get("summary_about_lead")) and person_data.get("summary"):
        input_user_properties["summary_about_lead"] = person_data["summary"]

    # Experiences
    experiences = person_data.get("experiences", [])
    if experiences:
        # Current role data
        
        input_user_properties["organization_name"] = experiences[0].get("company", "")

        org_url = experiences[0].get("company_linkedin_profile_url", "")
        if org_url and is_empty(input_user_properties.get("organization_linkedin_url")):
            input_user_properties["organization_linkedin_url"] = org_url

        # If there's a second experience, track it as previous
        if len(experiences) > 1:
            previous_org = experiences[1]
            prev_org_url = previous_org.get("company_linkedin_profile_url", "")

            if prev_org_url and is_empty(input_user_properties.get("previous_organization_linkedin_url")):
                input_user_properties["previous_organization_linkedin_url"] = prev_org_url

            if is_empty(input_user_properties.get("previous_organization_name")):
                input_user_properties["previous_organization_name"] = previous_org.get("company", "")

    # Combine city/state if available (and if lead_location is empty)
    if is_empty(input_user_properties.get("lead_location")):
        if person_data.get("city") or person_data.get("state"):
            combined = f"{person_data.get('city', '')}, {person_data.get('state', '')}"
            input_user_properties["lead_location"] = combined.strip(", ")
    
    # LinkedIn Followers Count
    if is_empty(input_user_properties.get("linkedin_follower_count")):
        input_user_properties["linkedin_follower_count"] = person_data.get("follower_count", 0)

    return input_user_properties



async def enrich_user_info_with_proxy_curl(input_user_properties: dict, tool_config: Optional[List[Dict]] = None) -> dict:
    """
    Enriches the user info (input_user_properties) with data from Proxycurl.
    If the user_linkedin_url is determined to be a proxy (acw* and length > 10),
    we skip calling enrich_person_info_from_proxycurl, keep the input as-is,
    and only perform the organization enrichment logic.

    Returns:
        dict: Updated input_user_properties with enriched data or
              with an error field if something goes wrong.
    """
    logger.info("Entering enrich_user_info_with_proxy_curl")

    if not input_user_properties:
        logger.warning("No input_user_properties provided; returning empty dict.")
        return {}

    linkedin_url = input_user_properties.get("user_linkedin_url", "")
    email = input_user_properties.get("email", "")
    user_data_from_proxycurl = None

    logger.debug(f"Attempting to enrich data for LinkedIn URL='{linkedin_url}', Email='{email}'")

    # ---------------------------------------------------------------
    # 1) Detect if the LinkedIn URL is a "proxy" URL (acw + length > 10)
    # ---------------------------------------------------------------
    def is_proxy_linkedin_url(url: str) -> bool:
        """
        Checks if the LinkedIn URL has an /in/<profile_id> path
        that starts with 'acw' and has length > 10, indicating a proxy.
        """
        match = re.search(r"linkedin\.com/in/([^/]+)", url, re.IGNORECASE)
        if match:
            profile_id = match.group(1)
            if profile_id.startswith("acw") and len(profile_id) > 10:
                return True
        return False

    if is_proxy_linkedin_url(linkedin_url):
        logger.info("The LinkedIn URL appears to be a proxy URL. Skipping user data enrichment from Proxycurl.")
        # We do NOT call enrich_person_info_from_proxycurl for user data.
        # We just set linkedin_url_match = False and enrich organization info if possible:
        input_user_properties["linkedin_url_match"] = False

        # Attempt organization enrichment if we have an organization_linkedin_url:
        company_data = {}
        if input_user_properties.get("organization_linkedin_url"):
            company_data = await enrich_organization_info_from_proxycurl(
                organization_linkedin_url=input_user_properties["organization_linkedin_url"],
                tool_config=tool_config
            )
            if company_data and not company_data.get("error"):
                if company_data.get("organization_linkedin_url"):
                    input_user_properties["organization_linkedin_url"] = company_data.get("organization_linkedin_url", "")
                if company_data.get("organization_name"):
                    input_user_properties["organization_name"] = company_data.get("organization_name", "")
                input_user_properties["organization_size"] = str(
                    company_data.get("company_size_on_linkedin", "")
                )
                input_user_properties["company_size"] = str(
                    company_data.get("company_size_on_linkedin", "")
                )
                input_user_properties["organization_industry"] = company_data.get("organization_industry", "")
                input_user_properties["industry"] = company_data.get("organization_industry", "")
                input_user_properties["organization_revenue"] = ""

        # Always clean & store any returned org info:
        additional_props = input_user_properties.get("additional_properties") or {}
        company_data = cleanup_properties(company_data)
        additional_props["pc_company_data"] = json.dumps(company_data)
        input_user_properties["additional_properties"] = additional_props

        logger.info("Returning after skipping user enrichment for proxy URL.")
        return input_user_properties

    # ----------------------------------------------------------------
    # 2) If not proxy, proceed with normal user enrichment logic
    # ----------------------------------------------------------------
    if linkedin_url or email:
        user_data = await enrich_person_info_from_proxycurl(
            linkedin_url=linkedin_url,
            email=email,
            tool_config=tool_config
        )
        if not user_data or 'error' in user_data:
            logger.warning("No valid person data found by LinkedIn or email.")
        else:
            user_data_from_proxycurl = user_data
            if linkedin_url:
                logger.info(f"User data found for LinkedIn URL: {linkedin_url}")
                input_user_properties["user_linkedin_url"] = linkedin_url
    else:
        # Otherwise, fallback to name-based lookup
        first_name = input_user_properties.get("first_name", "")
        last_name = input_user_properties.get("last_name", "")
        full_name = input_user_properties.get("full_name", "")

        if not first_name or not last_name:
            if full_name:
                name_parts = full_name.split(" ", 1)
                first_name = first_name or name_parts[0]
                if len(name_parts) > 1:
                    last_name = last_name or name_parts[1]

        if not full_name:
            full_name = f"{first_name} {last_name}".strip()

        company = input_user_properties.get("organization_name", "")
        logger.debug(f"Looking up person by name: {first_name} {last_name}, company: {company}")

        if first_name and last_name:
            lookup_result = await lookup_person_in_proxy_curl_by_name(
                first_name=first_name,
                last_name=last_name,
                company_name=company,
                tool_config=tool_config
            )
            # Expecting a dict (search_result)
            if lookup_result and not lookup_result.get('error'):
                results = lookup_result.get("results", [])
                person_company = ""
                for person in results:
                    linkedin_profile_url = person.get("linkedin_profile_url", "")
                    if linkedin_profile_url:
                        data_from_proxycurl = await enrich_person_info_from_proxycurl(
                            linkedin_url=linkedin_profile_url,
                            tool_config=tool_config
                        )
                        if data_from_proxycurl and not data_from_proxycurl.get('error'):
                            person_name = data_from_proxycurl.get("name", "").lower()
                            person_first_name = data_from_proxycurl.get("first_name", "").lower()
                            person_last_name = data_from_proxycurl.get("last_name", "").lower()
                            experiences = data_from_proxycurl.get('experiences', [])
                            for exp in experiences:
                                exp_company = exp.get("company", "").lower()
                                if exp_company == company.lower():
                                    person_company = exp_company
                                    break

                            if (
                                (person_name == full_name.lower() or
                                 (person_first_name == first_name.lower() and person_last_name == last_name.lower()))
                                and (not company or person_company == company.lower())
                            ):
                                logger.info(f"User data found for name: {full_name}")
                                input_user_properties["user_linkedin_url"] = linkedin_profile_url
                                user_data_from_proxycurl = data_from_proxycurl
                                break

    if not user_data_from_proxycurl:
        logger.debug("No user data returned from Proxycurl.")
        input_user_properties["linkedin_url_match"] = False
        return input_user_properties

    # ------------------------------------------------------------------
    # 3) If user data was found, sanitize & fill user properties
    # ------------------------------------------------------------------
    url_pattern = re.compile(r'(https?://[^\s]+)', re.IGNORECASE)

    def sanitize_urls_in_data(data):
        """
        Recursively walk through 'data' and remove any URL that is not under linkedin.com domain.
        """
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                sanitized[k] = sanitize_urls_in_data(v)
            return sanitized
        elif isinstance(data, list):
            return [sanitize_urls_in_data(item) for item in data]
        elif isinstance(data, str):
            def replace_non_linkedin(match):
                link = match.group(1)
                if "linkedin.com" not in (urlparse(link).netloc or ""):
                    return ""
                return link
            return re.sub(url_pattern, replace_non_linkedin, data)
        return data

    person_data = sanitize_urls_in_data(user_data_from_proxycurl)
    additional_props = input_user_properties.get("additional_properties") or {}

    # Check if there's a match on first/last name
    first_matched = (
        input_user_properties.get("first_name")
        and person_data.get("first_name") == input_user_properties["first_name"]
    )
    last_matched = (
        input_user_properties.get("last_name")
        and person_data.get("last_name") == input_user_properties["last_name"]
    )

    if first_matched and last_matched:
        input_user_properties["linkedin_url_match"] = True
        input_user_properties["linkedin_validation_status"] = "valid"

    input_user_properties = fill_in_missing_properties(input_user_properties, person_data)

    # ------------------------------------------------------------------
    # 4) Attempt organization enrichment if we have an org LinkedIn URL
    # ------------------------------------------------------------------
    company_data = {}
    if input_user_properties.get("organization_linkedin_url"):
        company_data = await enrich_organization_info_from_proxycurl(
            organization_linkedin_url=input_user_properties["organization_linkedin_url"],
            tool_config=tool_config
        )
        if company_data and not company_data.get("error"):
            if company_data.get("organization_linkedin_url"):
                input_user_properties["organization_linkedin_url"] = company_data.get("organization_linkedin_url", "")
            if company_data.get("organization_name"):
                input_user_properties["organization_name"] = company_data.get("organization_name", "")
            input_user_properties["organization_size"] = str(
                company_data.get("company_size_on_linkedin", "")
            )
            input_user_properties["company_size"] = str(
                company_data.get("company_size_on_linkedin", "")
            )
            input_user_properties["company_size_list"] = company_data.get("company_size", "")
            input_user_properties["organization_industry"] = company_data.get("organization_industry", "")
            input_user_properties["industry"] = company_data.get("organization_industry", "")
            input_user_properties["organization_revenue"] = ""

    person_data = cleanup_properties(person_data)
    additional_props["pc_person_data"] = json.dumps(person_data)

    company_data = cleanup_properties(company_data)
    additional_props["pc_company_data"] = json.dumps(company_data)
    input_user_properties["additional_properties"] = additional_props

    logger.info("Enrichment of user info with Proxycurl complete.")
    return input_user_properties





@assistant_tool
async def find_leads_by_job_openings_proxy_curl(
    query_params: Dict[str, Any],
    hiring_manager_roles: List[str],
    tool_config: Optional[List[Dict]] = None,
) -> List[Dict]:
    """Search LinkedIn job postings using Proxycurl and find hiring manager leads.

    Args:
        query_params: Dictionary of parameters to Proxycurl job search API. The
            key ``job_title`` is required. Other keys like ``location`` may also
            be supplied.
        hiring_manager_roles: List of job titles to lookup at the company for
            potential hiring managers.
        tool_config: Optional configuration containing Proxycurl credentials.

    Returns:
        A list of lead dictionaries with normalized keys such as
        ``first_name``, ``last_name``, ``user_linkedin_url``,
        ``organization_name``, and ``organization_linkedin_url``.
    """
    logger.info("Entering find_leads_by_job_openings_proxy_curl")

    if not isinstance(query_params, dict) or not query_params.get("job_title"):
        logger.warning("query_params must include 'job_title'")
        return []

    try:
        API_KEY = get_proxycurl_access_token(tool_config)
    except ValueError as e:
        logger.error(str(e))
        return []

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    job_search_url = "https://enrichlayer.com/api/v2/company/job"
    leads: List[Dict] = []

    # ------------------------------------------------------------------
    # 1) Look up job openings
    # ------------------------------------------------------------------
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(job_search_url, headers=headers, params=query_params) as resp:
                if resp.status == 200:
                    job_result = await resp.json()
                    jobs = job_result.get("results") or job_result.get("jobs") or []
                elif resp.status == 429:
                    logger.warning("Rate limit exceeded on job search")
                    await asyncio.sleep(30)
                    return []
                else:
                    error_text = await resp.text()
                    logger.error("Job search error %s: %s", resp.status, error_text)
                    return []
    except Exception:
        logger.exception("Exception while searching jobs on Proxycurl")
        return []

    # ------------------------------------------------------------------
    # 2) For each job, find leads for specified hiring manager roles
    # ------------------------------------------------------------------
    for job in jobs:
        company = job.get("company", {}) if isinstance(job, dict) else {}
        company_name = company.get("name", "")
        company_url = company.get("url", "")
        if not company_name:
            continue

        for role in hiring_manager_roles:
            employee_params = {
                "url": company_url,
                "role_search": role,
                "employment_status": "current",
                "page_size": 1,
            }
            employees = []
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://enrichlayer.com/api/v2/company/employees",
                        headers=headers,
                        params=employee_params,
                    ) as e_resp:
                        if e_resp.status == 200:
                            data = await e_resp.json()
                            employees = data.get("employees") or data.get("profiles") or []
                        elif e_resp.status == 429:
                            logger.warning("Rate limit exceeded while fetching employees")
                            await asyncio.sleep(30)
                            continue
            except Exception:
                logger.exception("Exception while fetching employees from Proxycurl")
                continue

            for emp in employees:
                profile_url = emp.get("linkedin_profile_url") or emp.get("profile_url")
                if not profile_url:
                    continue
                person = await enrich_person_info_from_proxycurl(
                    linkedin_url=profile_url, tool_config=tool_config
                )
                if not person or person.get("error"):
                    continue
                lead = {
                    "first_name": person.get("first_name", ""),
                    "last_name": person.get("last_name", ""),
                    "full_name": person.get("full_name", ""),
                    "user_linkedin_url": profile_url,
                    "job_title": person.get("occupation", role),
                    "organization_name": company_name,
                    "organization_linkedin_url": company_url,
                }
                cleaned = cleanup_properties(lead)
                if cleaned:
                    leads.append(cleaned)

    logger.info("Returning %d leads from Proxycurl job search", len(leads))
    return leads
