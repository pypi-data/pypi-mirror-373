import json
from pydantic import BaseModel, Field
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.built_with_api_tools import (
    get_company_info_from_builtwith,
    get_company_info_from_builtwith_by_name,
)
from dhisana.utils.dataframe_tools import get_structured_output
from dhisana.utils.google_custom_search import search_google_custom


class QualifyCompanyBasedOnTechUsage(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    company_domain: str = Field(..., description="Domain of the company")
    built_with_technology_to_check: str = Field(
        ..., description="Which technology we are checking for usage in the company."
    )
    is_built_with_technology: bool = Field(
        ..., description="True if the input technology is used by the company based on input data."
    )
    reasoning_on_built_with: str = Field(
        ..., description="Summary of built with technology in company and why is_built_with_technology is set to True or False."
    )


def get_technologies(data, keyword):
    """
    Check if the keyword is found in the data JSON string.

    Args:
        data (dict): The data returned by BuiltWith API.
        keyword (str): The keyword to search for.

    Returns:
        bool: True if the keyword is found, False otherwise.
    """
    data_str = json.dumps(data).lower()
    keyword_lower = keyword.lower()
    return keyword_lower in data_str

@assistant_tool
async def find_tech_usage_in_company(
    company_domain: str,
    company_name: str,
    technology_to_look_for: str,
    company_information: str
):
    """
    Determine if a company is using a specific technology.

    Args:
        company_domain (str): The domain name of the company's website.
        company_name (str): The name of the company.
        technology_to_look_for (str): The technology to look for.
        company_information (str): Additional company information.

    Returns:
        str: A JSON string containing the structured output.
    """
    if not company_name:
        return json.dumps({
            "company_name": company_name,
            "is_built_with_technology": "False",
            "reasoning_on_built_with": "Company name is missing."
        })
        
    if not company_domain:
        company_data_buildwith = await get_company_info_from_builtwith_by_name(company_name)
        company_domain = company_data_buildwith.get('Lookup', '')
    else:
        company_data_buildwith = await get_company_info_from_builtwith(company_domain)
    
    # Search for job postings on the company's website mentioning the technology
    search_google_results = ""
    if company_domain:
        company_domain_search = f"site:{company_domain} \"{company_name}\" \"{technology_to_look_for}\""
        search_google_results = await search_google_custom(company_domain_search, 2)

    # Search LinkedIn for people at the company with skills in the technology
    linked_in_search = f"site:linkedin.com/in \"{company_name}\" \"{technology_to_look_for}\" intitle:\"{company_name}\" -intitle:\"followers\" -intitle:\"connections\" -intitle:\"profiles\" -inurl:\"dir/+\""
    people_with_skills_results = await search_google_custom(linked_in_search, 2)
    
    # Search LinkedIn for posts mentioning the company and technology
    linked_in_posts_search = f"site:linkedin.com/posts \"{company_name}\" \"{technology_to_look_for}\" intitle:\"{company_name}\" -intitle:\"members\" -intitle:\"connections\""
    linkedin_posts_search = await search_google_custom(linked_in_posts_search, 4)
    
    # Search Twitter/X for posts mentioning the company and technology
    twitter_posts_search_query = f'site:x.com "{company_name}" "{technology_to_look_for}" -intitle:"status"'
    twitter_posts_search_results = await search_google_custom(twitter_posts_search_query, 4)
    
    # General search results
    general_search_results_query = f"\"{company_name}\" \"{technology_to_look_for}\""
    general_search_results = await search_google_custom(general_search_results_query, 4)

    # Get technologies used by the company from BuiltWith
    tech_found_in_builtwith = []
    if company_domain:
        tech_found_in_builtwith = get_technologies(company_data_buildwith, technology_to_look_for)
        
    # Prepare the prompt for structured output
    prompt = f"""
        Mark the company as qualified in is_built_with_technology if the company {company_name} is using technology {technology_to_look_for}.
        DO NOT make up information.
        Give reasoning why the company is is_built_with_technology based on one of the reasons:
        1. There is a job posting on the company website for that technology.
        2. There are people with that skill in the given company which were found on linked in google search.
        3. BuiltWith shows the company uses the tech that is input.
        4. LinkedIn posts search results show a strong indication of the company using the technology.
        5. Twitter/X posts search results show a strong indication of the company using the technology.
        6. General search results show a strong indication of the company using the technology.
        
        Input Company Name: {company_name}
        Technology to look for: {technology_to_look_for}
        Google search results on company website for technology:
        {search_google_results}

        Google search on LinkedIn for people with skills:
        {people_with_skills_results}
        
        LinkedIn posts search for the company:
        {linkedin_posts_search}
        
        Twitter/X posts search for the company:
        {twitter_posts_search_results}
        
        General Search results:
        {general_search_results}
        
        Input Company Details To Lookup:
        {company_information}
        
        BuiltWith shows technology used: {tech_found_in_builtwith}
    """

    # Get structured output based on the prompt
    output, _ = await get_structured_output(prompt, QualifyCompanyBasedOnTechUsage)
    return json.dumps(output.dict())