"""
This module provides a set of functions to enrich lead and organization information
using various enrichment tools such as Apollo or ProxyCurl. It also allows
extraction and validation of domains from user-provided links or company websites.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field
import mdformat

from dhisana.utils.check_email_validity_tools import process_email_properties
from dhisana.utils.company_utils import normalize_company_name
from dhisana.utils.field_validators import (
    normalize_linkedin_url,
    normalize_linkedin_company_url,
    normalize_salesnav_url,
    normalize_linkedin_company_salesnav_url,
    validate_and_clean_email,
    validation_organization_domain,
    validate_website_url
)
from dhisana.utils.apollo_tools import enrich_user_info_with_apollo
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.domain_parser import get_domain_from_website, is_excluded_domain
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal
from dhisana.utils.proxy_curl_tools import (
    enrich_job_info_from_proxycurl,
    enrich_organization_info_from_proxycurl,
    enrich_user_info_with_proxy_curl,
)
from dhisana.utils.research_lead import research_company_with_full_info_ai, research_lead_with_full_info_ai
from dhisana.utils.serpapi_search_tools import (
    find_organization_linkedin_url_with_google_search,
    find_user_linkedin_url_google,
    find_user_linkedin_url_with_serper,
    get_company_website_from_linkedin_url,
)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Allowed Enrichment Tools
# ----------------------------------------------------------------------
ALLOWED_ENRICHMENT_TOOLS = ["proxycurl", "apollo", "zoominfo"]

USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP = {
    "apollo": enrich_user_info_with_apollo,
    "proxycurl": enrich_user_info_with_proxy_curl,
}


# ----------------------------------------------------------------------
# BasicLeadInformation model
# ----------------------------------------------------------------------
class BasicLeadInformation(BaseModel):
    full_name: str = Field(..., description="Full name of the lead")
    first_name: str = Field(..., description="First name of the lead")
    last_name: str = Field(..., description="Last name of the lead")
    email: str = Field(..., description="Email address of the lead")
    primary_domain_of_organization: str = Field(..., description="Primary domain of the organization")
    job_title: str = Field(..., description="Job Title of the lead")
    phone: str = Field(..., description="Phone number of the lead")
    headline: str = Field(..., description="Headline of the lead")
    lead_location: str = Field(..., description="Location of the lead")
    organization_name: str = Field(..., description="Current Company where lead works")
    common_connections: int = Field(..., description="Number of common connections with the lead. Default 0")
    followers_count: int = Field(..., description="Number of followers of the lead. Default 0")
    tenure_in_current_role: str = Field(..., description="Tenure in the current role")
    tenure_in_current_company: str = Field(..., description="Tenure in the current company")
    connection_degree: str = Field(..., description="Degree of connection with the lead (1st, 2nd, 3rd)")
    is_premium_account: bool = Field(..., description="Is the lead a premium account. Default is false.")
    country_code: str = Field(..., description="Alpha-2 ISO3166 country code eg. US")


# ----------------------------------------------------------------------
# Helper: chunkify
# ----------------------------------------------------------------------
def chunkify(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Splits a list into sublists (chunks) of size `chunk_size`.
    """
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


# ----------------------------------------------------------------------
# Function: cleanup_user_name
# ----------------------------------------------------------------------
def cleanup_user_name(cloned_properties: dict) -> dict:
    """
    Cleans up user name fields: 'full_name', 'first_name', 'last_name'.
    Returns the updated dictionary. If values are invalid or placeholders, sets them to ''.
    """
    if not isinstance(cloned_properties, dict):
        return {}

    def normalize(name: str) -> str:
        if not name or not isinstance(name, str):
            return ""
        # Common placeholders or invalid tokens
        invalid_tokens = [
            "null", "none", "na", "n.a", "notfound", "error",
            "na.", "na,", "notavilable", "notavailable", ""
        ]
        stripped = name.strip().lower()
        if stripped in invalid_tokens:
            return ""

        # Remove anything in parentheses
        stripped = re.sub(r"\(.*?\)", "", stripped)
        # Remove anything after '|'
        stripped = stripped.split("|", 1)[0]
        # Remove extra non-alphanumeric characters (but allow whitespace)
        stripped = re.sub(r"[^a-zA-Z0-9\s]", "", stripped)
        
        # Capitalize the first letter of each word, and lowercase the rest
        return " ".join(word.capitalize() for word in stripped.strip().split())

    full_name = normalize(cloned_properties.get("full_name"))
    first_name = normalize(cloned_properties.get("first_name"))
    last_name  = normalize(cloned_properties.get("last_name"))

    # If full_name is empty, build from first_name + last_name
    if first_name and last_name and not full_name:
        full_name = (first_name + " " + last_name).strip()

    cloned_properties["full_name"] = full_name
    cloned_properties["first_name"] = first_name
    cloned_properties["last_name"] = last_name
    
    return cloned_properties


# ----------------------------------------------------------------------
# LLM-based cleanup for single lead
# ----------------------------------------------------------------------
async def get_clean_lead_info_with_llm(lead_info_str: str, tool_config: Optional[dict]) -> Dict[str, Any]:
    """
    Takes a JSON string representation of partial lead info,
    returns a cleaned-up lead dictionary matching BasicLeadInformation fields.
    """
    prompt = f"""
    Given the following data about a lead and the organization they work for, 
    extract and clean up the lead information. 
    - Format 'full_name' properly.
    - Format 'first_name' and 'last_name' so they're capitalized properly if available.
    - Make sure 'organization_name' is properly capitalized if provided.
    - Do not invent data that isn't provided.

    Data:
    {lead_info_str}

    The output format is in JSON. The expected fields match BasicLeadInformation.
    """
    lead_info, status = await get_structured_output_internal(
        prompt,
        BasicLeadInformation,
        model="gpt-4.1-mini",
        tool_config=tool_config
    )
    if status == "ERROR":
        return {}
    return lead_info.model_dump()


# ----------------------------------------------------------------------
# Helper: is_personal_email_domain
# ----------------------------------------------------------------------
def is_personal_email_domain(domain: str) -> bool:
    """
    Very simple check to see if the domain is one of the common free/personal
    email providers. Could expand this list or integrate a third-party API
    for more accuracy.
    """
    common_free_domains = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "protonmail.com", "icloud.com", "aol.com", "mail.com",
        "pm.me", "yandex.com", "gmx.com"
    }
    domain = domain.strip().lower()
    return (domain in common_free_domains) or domain.endswith(".edu")


# ----------------------------------------------------------------------
# Main validation & cleanup function
# ----------------------------------------------------------------------
async def validate_and_cleanup(
    cloned_properties: dict,
    tool_config: Optional[dict] = None,
    use_strict_check: bool = False
) -> dict:
    """
    Wrapper to validate & normalize various properties in a dictionary.

    1) Clean up/validate typical fields.
    2) If name fields appear invalid, fallback to LLM-based name inference.
    3) If 'primary_domain_of_organization' AND 'organization_website' are both empty,
       but there's a valid corporate email, use that as the domain.
    4) (Optional) Enrich the organization info from the name if needed.
    """

    if not isinstance(cloned_properties, dict):
        return {}

    # ------------------------------------------------------------------
    # Step 1: Normalize typical fields
    # ------------------------------------------------------------------
    cloned_properties["user_linkedin_url"] = normalize_linkedin_url(
        cloned_properties.get("user_linkedin_url")
    )
    cloned_properties["user_linkedin_salesnav_url"] = normalize_salesnav_url(
        cloned_properties.get("user_linkedin_salesnav_url")
    )
    cloned_properties["organization_linkedin_url"] = normalize_linkedin_company_url(
        cloned_properties.get("organization_linkedin_url")
    )
    cloned_properties["organization_linkedin_salesnav_url"] = normalize_linkedin_company_salesnav_url(
        cloned_properties.get("organization_linkedin_salesnav_url")
    )
    cloned_properties["email"] = validate_and_clean_email(
        cloned_properties.get("email")
    )
    cloned_properties["primary_domain_of_organization"] = validation_organization_domain(
        cloned_properties.get("primary_domain_of_organization")
    )
    cloned_properties["organization_website"] = validate_website_url(
        cloned_properties.get("organization_website")
    )
    cloned_properties["organization_name"] = normalize_company_name(
        cloned_properties.get("organization_name")
    )

    # ------------------------------------------------------------------
    # Step 2: Basic name-check. If invalid => LLM fallback.
    # ------------------------------------------------------------------
    def has_special_characters(val: str) -> bool:
        return bool(re.search(r"[^a-zA-Z0-9\s]", val))

    def is_invalid_name(val: str) -> bool:
        return (len(val.strip()) < 3) or has_special_characters(val)

    full_name = cloned_properties.get("full_name", "")
    first_name = cloned_properties.get("first_name", "")
    last_name = cloned_properties.get("last_name", "")
    if (not full_name or full_name.startswith("None")):
        full_name = ""
    if (not first_name or first_name.startswith("None")):
        first_name = ""
    if (not last_name or last_name.startswith("None")):
        last_name = ""
        
    if (
        is_invalid_name(full_name)
        or is_invalid_name(first_name)
        or is_invalid_name(last_name)
    ):
        # Check if we have a valid LinkedIn URL - if so, skip LLM as ProxyCurl will fill the data
        user_linkedin_url = cloned_properties.get("user_linkedin_url", "").strip()
        if not user_linkedin_url:
            lead_info_str = str(cloned_properties)
            logger.info(
                "Detected invalid name fields. Using LLM to infer/correct name fields."
            )
            # Attempt LLM-based cleanup
            new_lead_info = await get_clean_lead_info_with_llm(lead_info_str, tool_config=tool_config)
            if new_lead_info:
                cloned_properties["full_name"] = new_lead_info.get("full_name", "")
                cloned_properties["first_name"] = new_lead_info.get("first_name", "")
                cloned_properties["last_name"] = new_lead_info.get("last_name", "")
        else:
            logger.info("Valid LinkedIn URL found. Skipping LLM cleanup as ProxyCurl will enrich the data.")
    else:
        # Use the cheaper logic
        cloned_properties = cleanup_user_name(cloned_properties)

    # ------------------------------------------------------------------
    # Step 3: If domain & website are empty but there's a corporate email
    # ------------------------------------------------------------------
    # - If email is present, check if domain is personal or corporate
    # - If corporate, set primary_domain_of_organization from email domain
    # ------------------------------------------------------------------
    domain_empty = not cloned_properties.get("primary_domain_of_organization")
    website_empty = not cloned_properties.get("organization_website")
    email = cloned_properties.get("email", "")

    if domain_empty and website_empty and email:
        # parse domain from email
        extracted_domain = email.split("@")[-1].strip().lower()
        if extracted_domain and (not is_personal_email_domain(extracted_domain)):
            # This is a "corporate" email domain, so use it
            cloned_properties["primary_domain_of_organization"] = extracted_domain
            cloned_properties["organization_website"] = f"https://www.{extracted_domain}"
            logger.info("Set primary_domain_of_organization from corporate email domain.")
    
    if domain_empty and not website_empty:
        from urllib.parse import urlparse
        parsed_website = urlparse(cloned_properties["organization_website"])
        possible_domain = parsed_website.netloc.replace("www.", "")
        if possible_domain:
            cloned_properties["primary_domain_of_organization"] = possible_domain
            logger.info("Set primary_domain_of_organization from organization_website domain.")
    return cloned_properties

@assistant_tool
async def enrich_lead_information(
    user_properties: Dict[str, Any],
    use_strict_check: bool = True,
    get_valid_email: bool = True,
    company_research_instructions: str = "",
    lead_research_instructions: str = "",
    enrich_company_information: bool = True,
    enrich_lead_information: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    logger.debug("Starting enrich_lead_information with user_properties: %s", user_properties)
    cloned_properties = dict(user_properties)

    cloned_properties = await validate_and_cleanup(cloned_properties, tool_config=tool_config, use_strict_check=use_strict_check)
    
    cloned_properties = await enrich_user_info(
        input_properties=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )
    if use_strict_check and not cloned_properties.get("user_linkedin_url") and not cloned_properties.get("email"):
        return cloned_properties

    await enrich_organization_info_from_name(
        row=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )

    cloned_properties = await enrich_with_provider(cloned_properties, tool_config)

    await enrich_organization_info_from_name(
        row=cloned_properties,
        use_strict_check=use_strict_check,
        tool_config=tool_config,
    )

    if get_valid_email:
        await process_email_properties(cloned_properties, tool_config)

    # ------------------------------------------------------------------
    # Supplement missing follower count or name information using Serper
    # ------------------------------------------------------------------
    linkedin_url = cloned_properties.get("user_linkedin_url", "").strip()
    follower_count = cloned_properties.get("linkedin_follower_count")
    first_name = cloned_properties.get("first_name")
    if (
        linkedin_url
        and (follower_count is None or (isinstance(follower_count, str) and not follower_count.strip()) or not first_name)
    ):
        serper_result = await find_user_linkedin_url_with_serper(
            linkedin_url, tool_config=tool_config
        )
        if serper_result:
            if follower_count is None or (
                isinstance(follower_count, str) and not follower_count.strip()
            ):
                cloned_properties["linkedin_follower_count"] = serper_result.get(
                    "linkedin_follower_count", 0
                )
            if not first_name:
                cloned_properties["first_name"] = serper_result.get("first_name", "")
                cloned_properties["last_name"] = serper_result.get("last_name", "")

    cloned_properties = await validate_and_cleanup(
        cloned_properties, tool_config=tool_config, use_strict_check=use_strict_check
    )

    research_summary = cloned_properties.get("research_summary", "")

    if enrich_lead_information:
        summary = await research_lead_with_full_info_ai(
            cloned_properties, lead_research_instructions, tool_config=tool_config
        )
        if summary:
            research_summary = summary.get("research_summary", "")

    if enrich_company_information:
        company_company_properties = {
            "organization_name": cloned_properties.get("organization_name", ""),
            "primary_domain_of_organization": cloned_properties.get("primary_domain_of_organization", ""),
            "organization_website": cloned_properties.get("organization_website", ""),
        }
        company_summary = await research_company_with_full_info_ai(
            company_company_properties,
            company_research_instructions,
            tool_config=tool_config,
        )
        if company_summary:
            markdown_text = research_summary + "\n\n#### " + company_summary.get(
                "research_summary", ""
            )
            formatted_markdown = mdformat.text(markdown_text)
            research_summary = re.sub(
                r'^(#{1,6})\s+', '##### ', formatted_markdown, flags=re.MULTILINE
            )

    cloned_properties["research_summary"] = research_summary
    return cloned_properties


class UserInfoFromGithubProfileId(BaseModel):
    first_name: str
    last_name: str
    full_name: str
    linkedin_url: str
    github_url: str
    email: str
    twitter_handle: str
    website: str
    location: str


def extract_id_from_salesnav_url(url_key: str) -> str:
    """
    Extract the Sales Navigator lead ID from a URL like
    'https://www.linkedin.com/sales/lead/<ID>?...'
    """
    if not url_key:
        return ""
    match = re.search(r"linkedin\.com/sales/lead/([^/?#,]+)", url_key, re.IGNORECASE)
    if not match:
        return ""
    # strip out any non-word or hyphen chars
    return re.sub(r"[^\w-]", "", match.group(1))

def proxy_linkedin_url(user_linkedin_salesnav_url: str) -> str:
    """
    Given a Sales Navigator URL, return the corresponding public LinkedIn URL.
    Raises ValueError if the ID cannot be extracted.
    """
    salesnav_id = extract_id_from_salesnav_url(user_linkedin_salesnav_url)
    if not salesnav_id:
        raise ValueError("Could not extract ID from Sales Nav URL.")
    return f"https://www.linkedin.com/in/{salesnav_id}"

# -------------------------------------------------------------------
# (Pseudo) get_structured_output_internal, find_user_linkedin_url_google
# and other references assumed to exist in your environment.
# -------------------------------------------------------------------

async def get_user_linkedin_url_from_github_profile(
    github_profile_id: str,
    lead_properties: dict, 
    instructions: str, 
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Attempt to locate a user's LinkedIn profile URL from their GitHub profile ID via web search.
    Also gather basic user info (first/last name) if possible.
    """
    instructions = f"""
        Give user information from user GitHub handle; try to locate the LinkedIn profile URL
        for the user using web search.
        ---
        Github profile id: 
        {github_profile_id}
        Company Data include name, domain and website:
        {lead_properties}

        Instructions:
        {instructions}
        ---
        Use websearch to locate the LinkedIn profile url for the user if present.
        
        **Output**:
        Return your final output as valid JSON with the following structure:
        {{
            "first_name": "...",
            "last_name": "...",
            "full_name": "...",
            "linkedin_url": "...",
            "github_url": "...",
            "email": "...",
            "twitter_handle": "...",
            "website": "...",
            "location": "..."
        }}
    """

    # Example call to structured output function
    response, status = await get_structured_output_internal(
        instructions, 
        UserInfoFromGithubProfileId, 
        model="gpt-4.1-mini", 
        use_web_search=True,
        tool_config=tool_config
    )
    if status == "SUCCESS":
        return response
    else:
        return {}

async def enrich_user_info(
    input_properties: Dict[str, Any],
    use_strict_check: bool,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Attempt to find or fix a user's LinkedIn URL using name, title, location, 
    company info or GitHub profile handle if present. If still not found, 
    but user_linkedin_salesnav_url exists, we fall back to creating a 
    proxy URL from the Sales Navigator link.
    """
    logger.debug("Starting enrich_user_info for: %s", input_properties.get("full_name"))
    user_linkedin_url = (input_properties.get("user_linkedin_url") or "").strip()
    input_properties["linkedin_url_match"] = False
    github_profile_id = (input_properties.get("github_profile_id") or "").strip()

    # 1) If we do not have a user_linkedin_url, try getting it from GitHub
    if not user_linkedin_url:
        if github_profile_id:
            response = await get_user_linkedin_url_from_github_profile(
                github_profile_id=github_profile_id,
                lead_properties=input_properties,
                instructions="Use web search to find the user's LinkedIn profile from GitHub handle if present.",
                tool_config=tool_config,
            )
            user_linkedin_url = response.get("linkedin_url", "")
            if user_linkedin_url:
                input_properties["user_linkedin_url"] = user_linkedin_url
                if not input_properties.get("first_name"):
                    input_properties["first_name"] = response.get("first_name", "")
                if not input_properties.get("last_name"):
                    input_properties["last_name"] = response.get("last_name", "")
                if not input_properties.get("email"):
                    input_properties["email"] = response.get("email", "")
                if not input_properties.get("lead_location"):
                    input_properties["lead_location"] = response.get("location", "")
                return input_properties

        # 2) If still no LinkedIn URL, try name/title/org searching
        full_name = (input_properties.get("full_name") or "").strip()
        if not full_name:
            first_name = (input_properties.get("first_name", "") or "").strip()
            last_name = (input_properties.get("last_name", "") or "").strip()
            full_name = f"{first_name} {last_name}".strip()

        title = input_properties.get("job_title", "") or ""
        location = input_properties.get("lead_location", "") or ""
        org_name = (input_properties.get("organization_name", "") or "").strip()
        org_domain = (input_properties.get("primary_domain_of_organization", "") or "").strip()

        if full_name and (org_name or org_domain or title):
            # This function does a google-based search for the user's LinkedIn
            found_linkedin_url = await find_user_linkedin_url_google(
                user_name=full_name,
                user_title=title,
                user_location=location,
                user_company=org_name,
                user_company_domain=org_domain,
                use_strict_check=use_strict_check,
                tool_config=tool_config,
            )
            if found_linkedin_url:
                user_linkedin_url = found_linkedin_url
                input_properties["user_linkedin_url"] = user_linkedin_url

        # 3) Final fallback: if STILL no user_linkedin_url, 
        #    but user_linkedin_salesnav_url is present, use proxy
        if not input_properties.get("user_linkedin_url"):
            salesnav_url = input_properties.get("user_linkedin_salesnav_url", "")
            if salesnav_url:
                try:
                    proxy_url = proxy_linkedin_url(salesnav_url)
                    input_properties["user_linkedin_url"] = proxy_url
                    logger.debug("Falling back to proxy LinkedIn URL from SalesNav: %s", proxy_url)
                except ValueError:
                    # If we can't parse an ID from the sales nav URL, skip
                    logger.warning("Could not parse ID from user_linkedin_salesnav_url: %s", salesnav_url)

    return input_properties



async def enrich_with_provider(
    cloned_properties: Dict[str, Any],
    tool_config: Optional[List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Enrich user/lead data using one of the allowed provider tools (e.g., Apollo, ZoomInfo).
    The tool_config should specify which tool(s) to use.

    :param cloned_properties: Dictionary containing user/lead details to be enriched.
    :param tool_config: List of tool configuration dicts, e.g. [{"name": "apollo"}, ...].
    :return: The updated dictionary after enrichment.
    :raises ValueError: If no tool_config is provided or no suitable enrichment tool is found.
    """
    if not tool_config:
        raise ValueError("No tool configuration found.")

    chosen_tool_func = None
    for allowed_tool_name in ALLOWED_ENRICHMENT_TOOLS:
        for item in tool_config:
            logger.debug("Selected tool: %s", item.get("name"))
            if item.get("name") == allowed_tool_name and allowed_tool_name in USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP:
                chosen_tool_func = USER_LOOKUP_TOOL_NAME_TO_FUNCTION_MAP[allowed_tool_name]
                break
        if chosen_tool_func:
            break

    if not chosen_tool_func:
        raise ValueError("No suitable email validation tool found in tool_config.")

    return await chosen_tool_func(cloned_properties, tool_config)


async def enrich_organization_info_from_name(
    row: Dict[str, str],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Given a dictionary (treated like a CSV row) containing 'organization_name',
    'organization_linkedin_url', and 'website' keys, enrich the row only if the
    domain and website are currently empty.
    """
    org_name_key = "organization_name"
    org_domain_key = "primary_domain_of_organization"
    website_key = "organization_website"

    org_name = (row.get(org_name_key) or "").strip()
    logger.debug("Enriching organization info from name: %s", org_name)
    if org_name.lower() in ["none", "freelance"]:
        row[org_name_key] = ""
        org_name = ""

    # If there's no organization name, just return
    if not org_name:
        return

    # If domain or website is already present, we consider it enriched
    if row.get(org_domain_key) or row.get(website_key):
        return
    await set_organization_domain(row, use_strict_check, tool_config)


async def set_organization_domain(
    row: Dict[str, str],
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Update the row with a 'primary_domain_of_organization' based on 'website' or
    search results if the domain is absent.
    """
    org_name_key = "organization_name"
    org_domain_key = "primary_domain_of_organization"
    website_key = "organization_website"
    linkedin_url_key = "organization_linkedin_url"

    existing_domain = (row.get(org_domain_key) or "").strip()
    org_name = (row.get(org_name_key) or "").strip()
    logger.debug("Setting organization domain for organization: %s", org_name)
    logger.debug("Check existing_domain: %s", existing_domain)
    logger.debug("Check org_name: %s", org_name)

    if not existing_domain:
        company_website = (row.get(website_key) or "").strip()
        logger.debug("Check company_website: %s", company_website)
        extracted_domain = ""
        logger.debug("Initial extracted_domain: %s", extracted_domain)
        if not company_website and row.get(linkedin_url_key):
            company_website = await get_company_website_from_linkedin_url(row.get(linkedin_url_key))
            if company_website:
                logger.debug("Found company website from LinkedIn URL: %s", company_website)
                row[website_key] = company_website

        if company_website:
            extracted_domain = get_domain_from_website(company_website)
            logger.debug("extracted domain from website: %s", extracted_domain)
            if extracted_domain and is_excluded_domain(extracted_domain):
                extracted_domain = ""
                company_website = ""

        if not extracted_domain and not use_strict_check and org_name:
            logger.debug("Performing Google search to find domain for org_name: %s", org_name)
            company_info = await get_company_domain_from_llm_web_search(
                company_name=org_name,
                lead_info=row,
                location="US",
                tool_config=tool_config
            )
            if company_info and isinstance(company_info, dict):
                # If the LLM found a domain, set it
                if company_info.get("primary_domain_of_organization") and not row[org_domain_key]:
                    row[org_domain_key] = company_info["primary_domain_of_organization"]

                # If the LLM found an organization website, set it
                if company_info.get("organization_website") and not row[website_key]:
                    row[website_key] = company_info["organization_website"]

                # If there's a LinkedIn URL from LLM, set it
                if company_info.get("organization_linkedin_url") and not row[linkedin_url_key]:
                    row[linkedin_url_key] = company_info["organization_linkedin_url"]
                    
                if company_info.get("organization_name") and not row[org_name_key]:
                    row[org_name_key] = company_info["organization_name"]

        row[org_domain_key] = extracted_domain or ""
        logger.debug("Final domain selected: %s", row[org_domain_key])
        row[website_key] = company_website or ""

    # If there's still no website but we have a domain, set a default website
    company_website = (row.get(website_key) or "").strip()
    if existing_domain and not company_website:
        row[website_key] = f"https://www.{existing_domain}"


async def get_organization_linkedin_url(lead: Dict[str, Any], tools: Optional[List[Dict[str, Any]]]) -> str:
    """
    Retrieve the organization's LinkedIn URL using the company name, domain, and search tools.
    Returns an empty string if the organization name is missing.
    """
    name = lead.get("organization_name", "").strip()
    if not name:
        return ""

    linkedin_url = await find_organization_linkedin_url_with_google_search(
        name,
        company_location="US",
        company_domain=lead.get("primary_domain_of_organization"),
        use_strict_check=True,
        tool_config=tools,
    )
    return linkedin_url


async def enrich_organization_info_from_company_url(
    organization_linkedin_url: str,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Given an organization LinkedIn URL, attempt to enrich its data (e.g. name, website)
    via ProxyCurl. If data is found, set domain, then return the dict. Otherwise, return {}.
    """

    # Call ProxyCurl to enrich
    company_data = await enrich_organization_info_from_proxycurl(
        organization_linkedin_url=organization_linkedin_url,
        tool_config=tool_config
    )

    # If ProxyCurl returned any data, set domain, then return
    if company_data and isinstance(company_data, dict):
        await set_organization_domain(company_data, use_strict_check, tool_config)
        summary = await research_company_with_full_info_ai(company_data, "", tool_config=tool_config)
        if summary:
            company_data["organization_details"] = summary.get("research_summary", "")
        return company_data

    return {}


async def enrich_organization_info_from_job_url(
    job_url: str,
    use_strict_check: bool = True,
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Given a LinkedIn job posting URL, fetch job details using Proxycurl.
    If job details are successfully retrieved, extract organization information
    and return them in a dictionary. If not found, return {}.
    """
    # Validate the job URL.
    if "linkedin.com/jobs/view/" not in job_url:
        logger.debug("URL is not a valid LinkedIn job posting; skipping enrichment.")
        return {}

    # Normalize the job URL to use 'www.linkedin.com'
    parsed = urlparse(job_url)
    normalized_job_url = parsed._replace(netloc="www.linkedin.com").geturl()

    logger.debug(f"Fetching job info from Proxycurl for URL: {normalized_job_url}")
    try:
        job_info = await enrich_job_info_from_proxycurl(
            normalized_job_url, tool_config=tool_config
        )
    except Exception:
        logger.exception("Exception occurred while fetching job info from Proxycurl.")
        return {}

    if not job_info:
        logger.debug("No job info returned from Proxycurl; skipping enrichment.")
        return {}

    # Extract organization details from the 'company' key.
    company_data = job_info.get("company", {})

    # Make sure we have a company name before proceeding
    if company_data and company_data.get("name", ""):
        result = {
            "organization_name": company_data.get("name", ""),
            "organization_linkedin_url": company_data.get("url", ""),
            # Include the website if provided
            "organization_website": company_data.get("website", "")
        }

        # Refine domain and possibly fix the website
        await set_organization_domain(result, use_strict_check, tool_config)
        return result

    return {}


class CompanyInfoFromName(BaseModel):
    organization_name: str
    primary_domain_of_organization: str
    organization_website: str
    organization_linkedin_url: str


@assistant_tool
async def get_company_domain_from_llm_web_search(
    company_name: str,
    lead_info: dict,
    location: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Tries to find relevant company info (name, domain, website, LinkedIn URL) from the company name
    using an LLM with web search. Returns a dictionary with keys:
      {
         "organization_name": str,
         "primary_domain_of_organization": str,
         "organization_website": str,
         "organization_linkedin_url": str
      }
    or an empty dict on failure.
    """
    logger.info("Entering get_company_domain_from_llm_web_search")

    cleaned_name = company_name.replace(" ", "")
    if not cleaned_name or company_name.lower() in ["none", "freelance"]:
        logger.debug("Invalid or excluded company_name provided.")
        return {}

    query = f"\"{company_name}\" official website"
    if location:
        query += f", {location}"

    try:
        logger.debug(f"Performing LLM search with query: {query}")
        # Build instructions for the LLM
        instructions = f"""
        Given the following information, find the company name, website, and domain information.
        ---
        Company name:
        {company_name}
        
        Additional lead info:
        {lead_info}
        
        Search and gather any domain/website info or LinkedIn details.
        DO NOT make up information about company. 
        Find based on the domain in the leads email if its a corporate email, company name if sepcified to find the company name, website and domain.
        
        **Output**:
        Return your final output as valid JSON with the following structure:
        {{
          "organization_name": "...",
          "primary_domain_of_organization": "...",
          "organization_website": "...",
          "organization_linkedin_url": "..."
        }}
        """
        response, status = await get_structured_output_internal(
            instructions,
            CompanyInfoFromName,
            model="gpt-4.1-mini",
            use_web_search=True,
            tool_config=tool_config
        )
        if status == "SUCCESS":
            # Return the dictionary form of the model
            return response.model_dump()
        else:
            return {}
    except Exception:
        logger.exception("Exception during get_company_domain_from_llm_web_search.")
        return {}
