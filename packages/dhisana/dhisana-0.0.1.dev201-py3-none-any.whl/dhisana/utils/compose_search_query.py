import logging
import os
import json
import re
from typing import Any, Dict, List, Optional

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel

# If these are your local imports, leave them as is. Otherwise adjust paths as needed.
from dhisana.utils.company_utils import normalize_company_name
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GoogleSearchQuery(BaseModel):
    """
    Pydantic model representing the three Google search queries generated.
    google_search_queries has a list of 3 search query strings.
    """
    google_search_queries: List[str]


async def generate_google_search_queries(
    lead: Dict[str, Any],
    english_description: str,
    intent_signal_type: str,
    example_query: str = "",
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate three Google search queries based on a plain-English description,
    incorporating the following logic:
      1. First consider searching LinkedIn and the organization's own website for relevant info.
      2. Then consider searching Instagram, Twitter, Github, Yelp, Crunchbase, Bloomberg,
         or reputable news/financial sites for relevant qualification info.
      3. If lead["primary_domain_of_organization"] is not empty, ALWAYS include one query
         that searches the domain with something like:
            site:<primary_domain_of_organization> "about this company"
      4. Make sure lead["organization_name"] is part of every query.

    Args:
        lead: Dictionary containing information about the lead, including 'organization_name'.
        english_description: The user's plain-English description.
        intent_signal_type: A string indicating the intent signal type.
        example_query: Optional user-provided example.
        tool_config: Optional list of dictionaries containing tool configuration.

    Returns:
        A dictionary with a single key: "google_search_queries", mapping to a list of
        exactly three search query strings.
    """
    # Pull out relevant values
    org_name = lead.get("organization_name", "").strip()
    org_name = normalize_company_name(org_name)
    primary_domain = lead.get("primary_domain_of_organization", "").strip()

    system_message = (
        "You are a helpful AI Assistant that converts an English description of search requirements "
        "into valid Google search queries.\n\n"
        "Important instructions:\n"
        "1. Always include the organization name in every query.\n"
        "2. First consider ways to use LinkedIn or the company's own website to gather info.\n"
        "3. Then consider how Google can leverage Instagram, Twitter, Github, Yelp, Crunchbase, Bloomberg, "
        "   or reputable news/financial sites to figure out relevant info for qualification.\n"
        "4. You MUST generate exactly three Google search queries. No extra commentary.\n"
        "5. If you're unsure about a filter, make your best guess or omit it.\n"
        f"6. Primary domain of organization is: {primary_domain}\n\n"
        f"7. Organization name is: {org_name}\n"
        "8. In any site:linkedin.com search, make sure intitle:<organization_name> is present.\n\n"
        "Output must be valid JSON with the structure:\n"
        "{\n"
        '   "google_search_queries": ["search query1", "search query2", "search query3"]\n'
        "}"
    )

    few_shot_example_queries_lines = [
        'Examples (like Neo4j used in company):',
        f'- site:linkedin.com/in "{org_name}" "Neo4j" intitle:"{org_name}" -intitle:Neo4j -intitle:"profiles" ',
        'Other examples to ssearch by title, news etc',
        f'- site:linkedin.com/in "{org_name}" "Data Engineer" intitle:"{org_name}" -intitle:"profiles" ',
        f'- site:linkedin.com/jobs/view/ "{org_name}" "hiring" "angular developer" intitle:"{org_name}"',
        f'- site:news.google.com "{org_name}" "funding" OR "acquisition" OR "partnership"',
        f'- site:crunchbase.com "{org_name}" "funding"',
        f'- site:bloomberg.com "{org_name}" "financial news"'
    ]
    if primary_domain:
        few_shot_example_queries_lines.append(f'- site:{primary_domain} Job Openings')
        few_shot_example_queries_lines.append(f'- site:{primary_domain} Case Studies')
    few_shot_example_queries_lines.append(f'- "{org_name}" "competitors" OR "versus" OR "vs" "market share" "compare"')

    few_shot_example_queries = "\n".join(few_shot_example_queries_lines)

    user_prompt = f"""
{system_message}

The user wants to build Google search queries for:
"{english_description}"

Some example queries:
{few_shot_example_queries}

Lead info:
{json.dumps(lead, indent=2)}

Example query (if provided):
{example_query}

Intent signal type:
{intent_signal_type}

Please generate exactly three queries in JSON format as:
{{
    "google_search_queries": ["query1", "query2", "query3"]
}}
Remember to include "{org_name}" in each query.
"""

    logger.info("Generating Google search queries from description: %s", english_description)

    # Call your structured-output helper
    response, status = await get_structured_output_internal(
        user_prompt,
        GoogleSearchQuery,
        tool_config=tool_config
    )

    if status != "SUCCESS" or not response:
        raise Exception("Error generating the Google search queries.")

    queries_dict = response.model_dump()

    # Ensure that each query includes org_name
    fixed_queries = []
    for q in queries_dict["google_search_queries"]:
        if org_name and org_name.lower() not in q.lower() and not q.lower().startswith(f'site:{primary_domain}'):
            q = f'{q} "{org_name}"'
        fixed_queries.append(q.strip())

    queries_dict["google_search_queries"] = fixed_queries

    # Ensure the domain-based query is included if primary_domain is present.
    if primary_domain:
        domain_query = f'site:{primary_domain}'
        if all(domain_query.lower() not in x.lower() for x in queries_dict["google_search_queries"]):
            queries_dict["google_search_queries"].append(domain_query)

    logger.info("Search queries to be returned: %s", queries_dict["google_search_queries"])
    return queries_dict


async def get_search_results_for_insights(
    lead: Dict[str, Any],
    english_description: str,
    intent_signal_type: str,
    example_query: str = "",
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Uses generate_google_search_queries() to get up to four Google queries,
    then calls search_google() for each query in parallel to fetch results.

    For special intent signals, specialized queries are composed directly 
    (e.g., searching LinkedIn for job postings with specific roles/technologies).

    Args:
        lead: Dictionary containing information about the lead.
        english_description: The user's plain-English description.
        intent_signal_type: A string indicating the intent signal type.
        example_query: Optional user-provided example.
        tool_config: Optional list of dictionaries containing tool configuration.

    Returns:
        A list of dictionaries, where each dictionary contains:
        {
            "query": <the google query used>,
            "results": <a JSON string of search results array>
        }
    """
    results_of_queries: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # Specialized approach for recognized intent signal types
    # ---------------------------------------------------------
    if intent_signal_type == "intent_find_tech_usage_in_leads_current_company":
        company_name = lead.get("organization_name", "")
        company_name = normalize_company_name(company_name)
        organization_linkedin_url = lead.get("organization_linkedin_url", "")
        if company_name:
            google_queries = await get_google_queries_for_technology_used(
                english_description,
                company_name=company_name,
                tool_config=tool_config
            )
            if google_queries:
                job_posting_links = await find_tech_reference_by_google_search(
                    company_name,
                    google_queries,
                    organization_linkedin_url,
                    tool_config
                )
                results_of_queries.append({
                    "query": f"Find tech usage references by {company_name} using {google_queries} in Google search",
                    "results": json.dumps(job_posting_links)
                })

    elif intent_signal_type == "intent_find_tech_usage_in_leads_previous_company":
        previous_company_name = lead.get("previous_organization_name", "")
        previous_company_name = normalize_company_name(previous_company_name)
        previous_organization_linkedin_url = lead.get("previous_organization_linkedin_url", "")
        if previous_company_name:
            google_queries = await get_google_queries_for_technology_used(
                english_description,
                company_name=previous_company_name,
                tool_config=tool_config
            )
            if google_queries:
                job_posting_links = await find_tech_reference_by_google_search(
                    previous_company_name,
                    google_queries,
                    previous_organization_linkedin_url,
                    tool_config
                )
                results_of_queries.append({
                    "query": f"Find tech usage references by previous {previous_company_name} using {google_queries} in Google search",
                    "results": json.dumps(job_posting_links)
                })

    elif intent_signal_type == "intent_find_champion_changed_job":
        # For current
        company_name = normalize_company_name(lead.get("organization_name", ""))
        organization_linkedin_url = lead.get("organization_linkedin_url", "")
        if company_name:
            google_queries = await get_google_queries_for_technology_used(
                english_description,
                company_name=company_name,
                tool_config=tool_config
            )
            if google_queries:
                current_company_job_posting_links = await find_tech_reference_by_google_search(
                    company_name,
                    google_queries,
                    organization_linkedin_url,
                    tool_config
                )
                results_of_queries.append({
                    "query": f"Find tech usage references by current company {company_name} using {google_queries} in Google search",
                    "results": json.dumps(current_company_job_posting_links)
                })

        # For previous
        previous_company_name = normalize_company_name(lead.get("previous_organization_name", ""))
        previous_organization_linkedin_url = lead.get("previous_organization_linkedin_url", "")
        if previous_company_name:
            google_queries = await get_google_queries_for_technology_used(
                english_description,
                company_name=previous_company_name,
                tool_config=tool_config
            )
            if google_queries:
                prev_company_job_posting_links = await find_tech_reference_by_google_search(
                    previous_company_name,
                    google_queries,
                    previous_organization_linkedin_url,
                    tool_config
                )
                results_of_queries.append({
                    "query": f"Find tech usage references by previous company {previous_company_name} using {google_queries} in Google search",
                    "results": json.dumps(prev_company_job_posting_links)
                })

    elif intent_signal_type == "intent_find_job_opening_with_role_in_company":
        company_name = normalize_company_name(lead.get("organization_name", ""))
        organization_linkedin_url = lead.get("organization_linkedin_url", "")
        if company_name and organization_linkedin_url:
            google_query = await get_google_query_for_specific_role(
                english_description,
                company_name=company_name,
                tool_config=tool_config
            )
            if google_query.strip():
                job_posting_links = await find_job_postings_google_search(
                    company_name,
                    google_query,
                    organization_linkedin_url,
                    tool_config
                )
                results_of_queries.append({
                    "query": f"Find job by role in {company_name} using {google_query} in Google search",
                    "results": json.dumps(job_posting_links)
                })

    elif intent_signal_type == "intent_find_person_with_title_in_company":
        company_name = normalize_company_name(lead.get("organization_name", ""))
        organization_linkedin_url = lead.get("organization_linkedin_url", "")
        if company_name and organization_linkedin_url:
            google_query = await get_google_query_for_specific_title(
                english_description,
                company_name=company_name,
                tool_config=tool_config
            )
            if google_query.strip():
                job_posting_links = await find_job_postings_google_search(
                    company_name,
                    google_query,
                    organization_linkedin_url,
                    tool_config
                )
                results_of_queries.append({
                    "query": f"Find people with specific title in {company_name} using {google_query} in Google search",
                    "results": json.dumps(job_posting_links)
                })

    else:
        # ---------------------------------------------------------
        # Generic approach for unknown or general intent signals
        # ---------------------------------------------------------
        response_dict = await generate_google_search_queries(
            lead=lead,
            english_description=english_description,
            intent_signal_type=intent_signal_type,
            example_query=example_query,
            tool_config=tool_config
        )

        # Extract and limit the queries to a maximum of four
        queries = response_dict.get("google_search_queries", [])
        queries = queries[:4]

        # Execute searches in parallel
        coroutines = [
            search_google(query, number_of_results=3, tool_config=tool_config)
            for query in queries
        ]
        results = await asyncio.gather(*coroutines)

        for query, query_results in zip(queries, results):
            results_of_queries.append({
                "query": query,
                "results": json.dumps(query_results)
            })

    # Return the compiled list of search results
    return results_of_queries


def get_serp_api_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the SERPAPI_KEY access token from the provided tool configuration
    or from the environment variable SERPAPI_KEY.

    Raises:
        ValueError: If the SerpAPI integration has not been configured.
    """
    serpapi_key = None
    if tool_config:
        serpapi_config = next(
            (item for item in tool_config if item.get("name") == "serpapi"),
            None
        )
        if serpapi_config:
            config_map = {
                item["name"]: item["value"]
                for item in serpapi_config.get("configuration", [])
                if item
            }
            serpapi_key = config_map.get("apiKey")

    # Fallback to environment variable if not found in tool_config
    serpapi_key = serpapi_key or os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        raise ValueError(
            "SerpAPI integration is not configured. Please configure the connection to SerpAPI in Integrations."
        )
    return serpapi_key


async def search_google(
    query: str,
    number_of_results: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Search Google using SERP API and return the results as a list of JSON strings.

    Args:
        query: The search query.
        number_of_results: Number of organic results to return.
        tool_config: Optional list of dictionaries containing tool configuration.

    Returns:
        A list of JSON strings, each representing one search result.
        If any error occurs, returns a list with a single JSON-encoded error dict.
    """
    serpapi_key = get_serp_api_access_token(tool_config)

    # Check cache first
    cached_response = retrieve_output("search_google_serp", query)
    if cached_response is not None:
        return cached_response

    params = {
        "q": query,
        "num": number_of_results,
        "api_key": serpapi_key
    }

    url = "https://serpapi.com/search"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_data = await response.text()
                    return [json.dumps({"error": error_data})]

                result = await response.json()
                # Serialize each result to a JSON string
                serialized_results = [
                    json.dumps(item) for item in result.get('organic_results', [])
                ]
                # Cache results
                cache_output("search_google_serp", query, serialized_results)
                return serialized_results
    except Exception as exc:
        return [json.dumps({"error": str(exc)})]


class TechnologyUsedCheck(BaseModel):
    """
    Pydantic model representing the technology keywords to look for.
    technologies_used: list of strings describing the sought-after technologies.
    """
    technologies_used: List[str]
    location_to_filter_by: str


async def get_google_queries_for_technology_used(
    english_description: str,
    company_name: str,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """
    Extract technology keywords from the English description to build a LinkedIn job-focused query.
    
    Args:
        english_description: The user's plain-English description.
        company_name: Name of the company to search around.
        tool_config: Optional tool configuration for structured-output or SERP.

    Returns:
        A list of Google queries that includes the company name and discovered technology keywords.
    """
    prompt = f"""
Given the English description, list any technologies that the user is trying to verify for {company_name}.
Find if there is a location to filter search by and fill location_to_filter_by. If none specified, default is United States.

User input:
{english_description}

Output must be valid JSON, e.g.:
{{
  "technologies_used": ["someTech", "anotherTech"],
  "location_to_filter_by": "United States"
}}
"""
    response, status = await get_structured_output_internal(
        prompt=prompt,
        response_format=TechnologyUsedCheck,
        effort="high",
        model="gpt-4.1-mini",
        tool_config=tool_config
    )

    # Build up to two queries if we have technologies
    if status == "SUCCESS" and response and response.technologies_used:
        queries = []
        tech_used_quoted = " OR ".join([f'"{tech}"' for tech in response.technologies_used])
        queries.append(
            f'site:linkedin.com (({tech_used_quoted}) AND ("{company_name}") AND ("{response.location_to_filter_by}"))'
        )
        queries.append(
            f'site:x.com (({tech_used_quoted}) AND ("{company_name}"))'
        )
        return queries
    else:
        return []


class TechnologyAndRoleCheck(BaseModel):
    """
    Pydantic model representing the technology keywords and role(s) to look for.
    """
    technologies_used: List[str]
    roles_looking_for: List[str]
    location_to_filter_by: str


async def get_google_query_for_specific_role(
    english_description: str,
    company_name: str,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Extract role and technology keywords from the English description to build a LinkedIn jobs query.
    
    Args:
        english_description: The user's plain-English description.
        company_name: Name of the company to search around.
        tool_config: Optional tool configuration.

    Returns:
        A single Google query string with role(s) and technology keywords.
    """
    prompt = f"""
Given the English description, identify any specific roles and technologies for {company_name}.
Find if there is a location to filter search by and fill location_to_filter_by. If none specified, default is United States.

User input:
{english_description}

Output must be valid JSON, e.g.:
{{
  "technologies_used": ["Angular", "Python"],
  "roles_looking_for": ["Developer", "Team Lead"],
  "location_to_filter_by": "United States"
}}
"""
    response, status = await get_structured_output_internal(
        prompt=prompt,
        response_format=TechnologyAndRoleCheck,
        effort="high",
        model="gpt-4.1-mini",
        tool_config=tool_config
    )

    if status == "SUCCESS" and response:
        tech_used_part = " OR ".join([f'"{tech}"' for tech in response.technologies_used]) if response.technologies_used else ""
        roles_part = " OR ".join([f'"{role}"' for role in response.roles_looking_for]) if response.roles_looking_for else ""
        return (
            f'site:linkedin.com/in ({tech_used_part}) AND ({roles_part}) '
            f'AND ("{company_name}") AND ("{response.location_to_filter_by}") -intitle:"profiles" '
        ).strip()
    else:
        return ""


class CheckForPeopleWithTitle(BaseModel):
    """
    Pydantic model for extracting job titles from an English description.
    """
    job_titles: List[str]
    location_to_filter_by: str = "United States"


async def get_google_query_for_specific_title(
    english_description: str,
    company_name: str,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Extract job titles (and location) from the English description to build a LinkedIn /in query.
    
    Args:
        english_description: The user's plain-English description.
        company_name: Name of the company to search around.
        tool_config: Optional tool configuration.

    Returns:
        A single Google query string with job titles and the company name.
    """
    prompt = f"""
Given the English description, identify any specific job titles that the user wants to find at {company_name}.
Find if there is location to filter search by and fill location_to_filter_by. If none specified default is United States.

User input:
{english_description}

Output must be valid JSON, e.g.:
{{
  "job_titles": ["CTO", "Head of Engineering"],
  "location_to_filter_by": "United States"
}}
"""
    response, status = await get_structured_output_internal(
        prompt=prompt,
        response_format=CheckForPeopleWithTitle,
        effort="high",
        tool_config=tool_config
    )

    if status == "SUCCESS" and response:
        titles_part = " OR ".join([f'"{title}"' for title in response.job_titles]) if response.job_titles else ""
        return (
            f'site:linkedin.com/in ({titles_part}) AND ("{company_name}") '
            f'AND ("{response.location_to_filter_by}") -intitle:"profiles" '
        ).strip()
    else:
        return ""


# TODO: fix with playwright implementation.
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"
}


async def _get_html_content_from_url(url: str) -> str:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            return await response.text()


async def _clean_html_content(html_content: str) -> BeautifulSoup:
    if not html_content:
        return BeautifulSoup("", 'html.parser')
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(['script', 'style', 'meta', 'code', 'svg']):
        element.decompose()
    return soup


async def find_job_postings_google_search(
    company_name: str,
    google_query: str,
    organization_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """
    Find job postings on LinkedIn for a given company using a Google Search query.

    Args:
        company_name (str): The name of the company.
        google_query (str): The Google query to run.
        organization_linkedin_url (Optional[str]): The LinkedIn URL of the company.
        tool_config: Optional list of dictionaries containing tool configuration.

    Returns:
        A list of discovered job posting links.
    """
    logger.info("Entering find_job_postings_google_search with query: %s", google_query)
    if not google_query.strip():
        return []

    job_posting_links = []

    try:
        results = await search_google(google_query.strip(), number_of_results=10, tool_config=tool_config)
    except Exception:
        logger.exception("Error searching for job postings via Google.")
        return []

    if not isinstance(results, list) or len(results) == 0:
        logger.debug("No results returned for this query.")
        return []

    for result_item in results:
        try:
            result_json = json.loads(result_item)
        except json.JSONDecodeError:
            logger.debug("Failed to parse JSON from the search result.")
            continue

        link = result_json.get('link', '')
        if not link:
            logger.debug("No link found in result JSON.")
            continue

        try:
            page_content = await _get_html_content_from_url(link)
            soup = await _clean_html_content(page_content)
        except Exception:
            logger.exception("Error fetching or parsing the job posting page.")
            continue

        page_links = [a.get('href') for a in soup.find_all('a', href=True)]

        company_match = False
        if organization_linkedin_url:
            partial_url = re.sub(r'^https?:\/\/(www\.)?', '', organization_linkedin_url).rstrip('/')
            for page_link in page_links:
                if (
                    page_link
                    and partial_url in page_link
                    and 'public_jobs_topcard-org-name' in page_link
                ):
                    company_match = True
                    break

        if company_match:
            job_posting_links.append(link)

    logger.info("Found %d job posting links for query '%s'.", len(job_posting_links), google_query)
    return job_posting_links


async def find_tech_reference_by_google_search(
    company_name: str,
    google_queries: List[str],
    organization_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """
    Find pages referencing certain technologies or job postings on LinkedIn for a given company 
    using a list of Google queries.

    Args:
        company_name (str): The name of the company.
        google_queries (List[str]): The Google queries to run.
        organization_linkedin_url (Optional[str]): The LinkedIn URL of the company.
        tool_config (Optional[List[Dict[str, Any]]]): Optional list of dictionaries containing tool configuration.

    Returns:
        List[str]: A list of discovered links referencing the technologies/job postings.
    """
    linkedin_reference_links = []
    for google_query in google_queries:
        logger.info("Entering find_tech_reference_by_google_search with query: %s", google_query)
        if not google_query.strip():
            continue

        try:
            results = await search_google(google_query.strip(), number_of_results=10, tool_config=tool_config)
        except Exception:
            logger.exception("Error searching for job postings via Google.")
            continue

        if not isinstance(results, list) or len(results) == 0:
            logger.debug("No results returned for this query.")
            continue

        for result_item in results:
            try:
                result_json = json.loads(result_item)
            except json.JSONDecodeError:
                logger.debug("Failed to parse JSON from the search result.")
                continue

            link = result_json.get('link', '')
            if not link:
                logger.debug("No link found in result JSON.")
                continue

            linkedin_reference_links.append(link)

        logger.info(
            "Accumulated %d links so far for query '%s'.",
            len(linkedin_reference_links),
            google_query
        )

    return linkedin_reference_links
