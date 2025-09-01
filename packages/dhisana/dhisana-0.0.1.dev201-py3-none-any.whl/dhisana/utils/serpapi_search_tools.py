import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup
import urllib
from pydantic import BaseModel

from dhisana.utils.serperdev_search import search_google_serper
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_internal,
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dhisana.utils.search_router import search_google_with_tools
from dhisana.utils.assistant_tool_tag import assistant_tool

from dhisana.utils.web_download_parse_tools import fetch_html_content


class LeadSearchResult(BaseModel):
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    job_title: str = ""
    linkedin_follower_count: int = 0
    lead_location: str = ""
    summary_about_lead: str = ""
    user_linkedin_url: str = ""


async def get_structured_output(text: str, tool_config: Optional[List[Dict]] = None) -> LeadSearchResult:
    """Parse text snippet into ``LeadSearchResult`` using OpenAI."""

    prompt = (
        "Extract lead details from the text below.\n"
        "If follower counts are mentioned, convert values like '1.5k+ followers' to an integer (e.g. 1500).\n"
        f"Return JSON matching this schema:\n{json.dumps(LeadSearchResult.model_json_schema(), indent=2)}\n\n"
        f"Text:\n{text}"
    )
    result, status = await get_structured_output_internal(
        prompt, LeadSearchResult, model = "gpt-4.1-nano", tool_config=tool_config
    )
    if status != "SUCCESS" or result is None:
        return LeadSearchResult()
    return result


@assistant_tool
async def find_user_linkedin_url_with_serper(
    user_linkedin_url: str,
    tool_config: Optional[List[Dict]] = None,
) -> Optional[Dict]:
    """Search Google via Serper.dev for ``user_linkedin_url`` and parse lead details."""

    if not user_linkedin_url:
        return None

    normalized_input = extract_user_linkedin_page(user_linkedin_url)
    results = await search_google_serper(user_linkedin_url, 10, tool_config=tool_config)
    for item_json in results:
        try:
            item = json.loads(item_json)
        except Exception:
            continue
        link = item.get("link", "")
        if not link:
            continue
        if extract_user_linkedin_page(link) == normalized_input:
            text = " ".join(
                [item.get("title", ""), item.get("subtitle", ""), item.get("snippet", "")] 
            ).strip()
            structured = await get_structured_output(text, tool_config=tool_config)
            structured.user_linkedin_url = normalized_input
            return json.loads(structured.model_dump_json())
    return None


@assistant_tool
async def get_company_domain_from_google_search(
    company_name: str,
    location: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Tries to find the company domain from the company name using Google (SerpAPI or Serper.dev).
    """
    logger.info("Entering get_company_domain_from_google_search")

    company_name_no_spaces = company_name.replace(" ", "")
    if not company_name_no_spaces or company_name.lower() in ["none", "freelance"]:
        logger.debug("Invalid or excluded company_name provided.")
        return ""

    query = f"\"{company_name}\" official website"
    if location:
        query = f"\"{company_name}\" official website, {location}"

    try:
        logger.debug(f"Performing search with query: {query}")
        result = await search_google_with_tools(query, 1, tool_config=tool_config)
        if not isinstance(result, list) or len(result) == 0:
            logger.debug("No results for first attempt, retrying with fallback query.")
            query = f"{company_name} official website"
            result = await search_google_with_tools(query, 1, tool_config=tool_config)
            if not isinstance(result, list) or len(result) == 0:
                logger.debug("No results from fallback query either.")
                return ''
    except Exception:
        logger.exception("Exception during get_company_domain_from_google_search.")
        return ''

    exclude_compan_names = ["linkedin", "wikipedia", "facebook", "instagram", "twitter", "youtube", "netflix"]
    if any(exclude_name in company_name.lower() for exclude_name in exclude_compan_names):
        logger.debug("Company name is in excluded list, returning empty domain.")
        return ""

    try:
        result_json = json.loads(result[0])
    except (json.JSONDecodeError, IndexError) as e:
        logger.debug(f"Failed to parse the JSON from the result: {str(e)}")
        return ''

    link = result_json.get('link', '')
    if not link:
        logger.debug("No link found in the first search result.")
        return ''

    parsed_url = urlparse(link)
    domain = parsed_url.netloc.lower()
    if domain.startswith('www.'):
        domain = domain[4:]

    excluded_domains = [
        "linkedin.com", "wikipedia.org", "usa.gov", "facebook.com",
        "instagram.com", "twitter.com", "x.com", "google.com", "youtube.com",
        "netflix.com", "freelance.com", "zoominfo.com", "reditt.com"
    ]
    excluded_domains_lower = [d.lower() for d in excluded_domains]

    if any(domain == d or domain.endswith(f".{d}") for d in excluded_domains_lower):
        logger.debug(f"Domain {domain} is in the excluded list.")
        return ""

    logger.info(f"Found domain {domain}")
    return domain


@assistant_tool
async def get_signal_strength(
    domain_to_search: str,
    keywords: List[str],
    in_title: List[str] = [],
    not_in_title: List[str] = [],
    negative_keywords: List[str] = [],
    tool_config: Optional[List[Dict]] = None
) -> int:
    """
    Find how strong a match for the keywords in search is by checking
    how many search results contain all desired keywords in the snippet.
    """
    logger.info("Entering get_signal_strength")

    if not keywords and not domain_to_search:
        logger.warning("No domain to search or keywords provided.")
        return 0

    query_parts = []
    if domain_to_search:
        query_parts.append(f"site:{domain_to_search}")
    for kw in keywords:
        query_parts.append(f"\"{kw}\"")
    for kw in in_title:
        query_parts.append(f'intitle:"{kw}"')
    for kw in not_in_title:
        query_parts.append(f'-intitle:"{kw}"')
    for kw in negative_keywords:
        query_parts.append(f'-"{kw}"')

    final_query = " ".join(query_parts).strip()
    if not final_query:
        logger.debug("Constructed query is empty, returning score=0.")
        return 0

    logger.debug(f"Performing get_signal_strength search with query: {final_query}")
    try:
        results = await search_google_with_tools(final_query, 5, tool_config=tool_config)
    except Exception:
        logger.exception("Exception occurred while searching for signal strength.")
        return 0

    if not isinstance(results, list) or len(results) == 0:
        logger.debug("No results found; returning 0.")
        return 0

    score = 0
    for result_item in results:
        try:
            result_json = json.loads(result_item)
            snippet_text = result_json.get('snippet', '').lower()
            if all(kw.lower() in snippet_text for kw in keywords):
                logger.debug(f"Found match in snippet: {snippet_text[:60]}...")
                score += 1
            if score == 5:
                break
        except (json.JSONDecodeError, KeyError):
            logger.debug("Failed to decode or parse snippet from a result.")
            continue

    logger.info(f"Final signal strength score: {score}")
    return score


def extract_user_linkedin_page(url: str) -> str:
    """
    Extracts and returns the user page part of a LinkedIn URL.
    Ensures the domain is www.linkedin.com and removes any suffix path or query parameters.
    """
    logger.debug(f"Entering extract_user_linkedin_page with URL: {url}")
    if not url:
        return ""

    normalized_url = re.sub(r"(https?://)?([\w\-]+\.)?linkedin\.com", "https://www.linkedin.com", url)
    match = re.match(r"https://www.linkedin.com/in/([\w\-]+)", normalized_url)
    if match:
        page = f"https://www.linkedin.com/in/{match.group(1)}"
        logger.debug(f"Extracted user LinkedIn page: {page}")
        return page

    logger.debug("No valid LinkedIn user page found.")
    return ""


@assistant_tool
async def find_user_linkedin_url_google(
    user_name: str,
    user_title: str,
    user_location: str,
    user_company: str,
    user_company_domain: str = "",
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Find the LinkedIn URL for a user based on their name, title, location, and company.
    """
    logger.info("Entering find_user_linkedin_url_google")

    if not user_name:
        logger.warning("No user_name provided.")
        return ""

    if use_strict_check:
        queries = [
            f'site:linkedin.com/in ("{user_name}")  ({user_company} | {user_company_domain}) ( {user_title} | ) intitle:"{user_name}" -intitle:"profiles" '
        ]
    else:
        queries = [
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_title}" "{user_company}" intitle:"{user_name}" -intitle:"profiles" ',
            f'site:linkedin.com/in "{user_name}" "{user_location}" "{user_company}" intitle:"{user_name}" -intitle:"profiles" ',
            f'site:linkedin.com/in "{user_name}", {user_location} intitle:"{user_name}" -intitle:"profiles" ',
            f'site:linkedin.com/in "{user_name}" intitle:"{user_name}"'
        ]

    async with aiohttp.ClientSession() as session:
        for query in queries:
            if not query.strip():
                continue
            logger.debug(f"Searching with query: {query}")
            try:
                results = await search_google_with_tools(query.strip(), 1, tool_config=tool_config)
            except Exception:
                logger.exception("Error searching for LinkedIn user URL.")
                continue

            if not isinstance(results, list) or len(results) == 0:
                logger.debug("No results for this query, moving to next.")
                continue

            try:
                result_json = json.loads(results[0])
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link in first search result.")
                continue

            parsed_url = urlparse(link)
            if 'linkedin.com/in' in (parsed_url.netloc + parsed_url.path):
                link = extract_user_linkedin_page(link)
                logger.info(f"Found LinkedIn user page: {link}")
                return link

    logger.info("No matching LinkedIn user page found.")
    return ""


@assistant_tool
async def find_user_linkedin_url_by_job_title_google(
    user_title: str,
    user_location: str,
    user_company: str,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Find the LinkedIn URL for a user based on their job_title, location, and company.
    """
    logger.info("Entering find_user_linkedin_url_by_job_title_google")

    queries = [
        f'site:linkedin.com/in "{user_company}" AND "{user_title}" -intitle:"profiles" ',
    ]

    async with aiohttp.ClientSession() as session:
        for query in queries:
            if not query.strip():
                continue
            logger.debug(f"Searching with query: {query}")

            try:
                results = await search_google_with_tools(query.strip(), 1, tool_config=tool_config)
            except Exception:
                logger.exception("Error searching for LinkedIn URL by job title.")
                continue

            if not isinstance(results, list) or len(results) == 0:
                logger.debug("No results for this query, moving to next.")
                continue

            try:
                result_json = json.loads(results[0])
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link in the first search result.")
                continue

            parsed_url = urlparse(link)
            if 'linkedin.com/in' in (parsed_url.netloc + parsed_url.path):
                link = extract_user_linkedin_page(link)
                logger.info(f"Found LinkedIn user page by job title: {link}")
                return link

    logger.info("No matching LinkedIn user page found by job title.")
    return ""


@assistant_tool
async def find_user_linkedin_url_by_google_search(
    queries: List[str],
    number_of_results: int = 5,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Find LinkedIn user URLs based on provided Google search queries.
    """
    logger.info("Entering find_user_linkedin_url_by_google_search")
    found_urls = []

    for query in queries:
        if not query.strip():
            continue
        logger.debug(f"Searching with query: {query}")

        try:
            results = await search_google_with_tools(query.strip(), number_of_results, tool_config=tool_config)
        except Exception:
            logger.exception("Error searching for LinkedIn URL using Google search.")
            continue

        if not isinstance(results, list) or len(results) == 0:
            logger.debug("No results for this query, moving to next.")
            continue

        try:
            result_json = json.loads(results[0])
        except (json.JSONDecodeError, IndexError):
            logger.debug("Failed to parse JSON from the search result.")
            continue

        link = result_json.get('link', '')
        if not link:
            logger.debug("No link in the first search result.")
            continue

        parsed_url = urlparse(link)
        if 'linkedin.com/in' in (parsed_url.netloc + parsed_url.path):
            link = extract_user_linkedin_page(link)
            logger.info(f"Found LinkedIn user page: {link}")
            found_urls.append(link)

    if not found_urls:
        logger.info("No matching LinkedIn user page found based on provided queries.")
    return found_urls


def extract_company_page(url: str) -> str:
    """
    Extracts and returns the company page part of a LinkedIn URL.
    Ensures the domain is www.linkedin.com and removes any suffix path or query parameters.
    """
    logger.debug(f"Entering extract_company_page with URL: {url}")
    if not url:
        return ""

    normalized_url = re.sub(r"(https?://)?([\w\-]+\.)?linkedin\.com", "https://www.linkedin.com", url)
    match = re.match(r"https://www.linkedin.com/company/([\w\-]+)", normalized_url)
    if match:
        company_page = f"https://www.linkedin.com/company/{match.group(1)}"
        logger.debug(f"Extracted LinkedIn company page: {company_page}")
        return company_page

    logger.debug("No valid LinkedIn company page found.")
    return ""


@assistant_tool
async def find_organization_linkedin_url_with_google_search(
    company_name: str,
    company_location: Optional[str] = None,
    company_domain: Optional[str] = None,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict]] = None,
) -> str:
    """
    Find the LinkedIn URL for a company based on its name and optional location using Google search.
    """
    logger.info("Entering find_organization_linkedin_url_with_google_search")

    if not company_name:
        logger.warning("No company_name provided.")
        return ""

    if use_strict_check:
        queries = [f'site:linkedin.com/company "{company_name}" {company_domain} -intitle:"jobs" ']
    else:
        if company_location:
            queries = [
                f'site:linkedin.com/company "{company_name}" {company_location} -intitle:"jobs" ',
                f'site:linkedin.com/company "{company_name}" -intitle:"jobs" ',
                f'site:linkedin.com/company {company_name} {company_location} -intitle:"jobs" ',
            ]
        else:
            queries = [
                f'site:linkedin.com/company "{company_name}" -intitle:"jobs" ',
                f'site:linkedin.com/company {company_name} -intitle:"jobs" '
            ]

    async with aiohttp.ClientSession() as session:
        for query in queries:
            if not query.strip():
                continue

            logger.debug(f"Searching with query: {query}")
            try:
                results = await search_google_with_tools(query.strip(), 1, tool_config=tool_config)
            except Exception:
                logger.exception("Error searching for organization LinkedIn URL.")
                continue

            if not isinstance(results, list) or len(results) == 0:
                logger.debug("No results for this query, moving to next.")
                continue

            try:
                result_json = json.loads(results[0])
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link found in the first result.")
                continue

            parsed_url = urlparse(link)
            if 'linkedin.com/company' in (parsed_url.netloc + parsed_url.path):
                link = extract_company_page(link)
                logger.info(f"Found LinkedIn company page: {link}")
                return link

    logger.info("No matching LinkedIn company page found.")
    return ""


async def get_external_links(url: str) -> List[str]:
    """
    Fetch external links from a given URL by parsing its HTML content.
    """
    logger.debug(f"Entering get_external_links for URL: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True) as response:
                logger.debug(f"Received status for external links: {response.status}")
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    external_links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('http') and not href.startswith(url):
                            external_links.append(href)
                    logger.debug(f"Found {len(external_links)} external links.")
                    return external_links
                else:
                    logger.warning(f"Non-200 status ({response.status}) while fetching external links.")
                    return []
    except Exception:
        logger.exception("Exception occurred while fetching external links.")
        return []


async def get_resolved_linkedin_links(url: str) -> List[str]:
    """
    Fetch HTML content from a URL and return any LinkedIn.com/company links found.
    """
    logger.debug(f"Entering get_resolved_linkedin_links for URL: {url}")
    try:
        content = await fetch_html_content(url)
    except Exception:
        logger.exception("Exception occurred while fetching HTML content.")
        return []

    linkedin_links = re.findall(r'https://www\.linkedin\.com/company/[^\s]+', content)
    unique_links = list(set(linkedin_links))
    logger.debug(f"Found {len(unique_links)} LinkedIn links.")
    return unique_links


@assistant_tool
async def get_company_website_from_linkedin_url(linkedin_url: str) -> str:
    """
    Attempt to extract a company's website from its LinkedIn URL by 
    scanning external links that contain "trk=about_website".
    """
    logger.info("Entering get_company_website_from_linkedin_url")

    if not linkedin_url:
        logger.debug("Empty LinkedIn URL provided, returning empty string.")
        return ""

    try:
        links = await get_external_links(linkedin_url)
    except Exception:
        logger.exception("Exception occurred while getting external links for LinkedIn URL.")
        return ""

    for link in links:
        if 'trk=about_website' in link:
            parsed_link = urllib.parse.urlparse(link)
            query_params = urllib.parse.parse_qs(parsed_link.query)
            if 'url' in query_params:
                encoded_url = query_params['url'][0]
                company_website = urllib.parse.unquote(encoded_url)
                logger.info(f"Extracted company website: {company_website}")
                return company_website
    logger.debug("No company website link found with 'trk=about_website'.")
    return ""
