import logging
from typing import Any, Dict, List, Optional

import openai  # Remove if not required outside get_structured_output_internal
from pydantic import BaseModel

from dhisana.utils.generate_structured_output_internal import get_structured_output_internal

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SalesNavQuery(BaseModel):
    """
    Pydantic model representing the final LinkedIn Sales Navigator URL.
    """
    linkedin_salenav_url_with_query_parameters: str


async def generate_salesnav_people_search_url(
    english_description: str = "",
    user_input_salesnav_url: str = "",
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate a single LinkedIn Sales Navigator URL based on the user's plain-English
    description of filters and parameters or a provided Sales Navigator URL.

    This function leverages an LLM (via get_structured_output_internal) to parse
    the user's requirements (e.g., connection degree, seniority, region, etc.)
    and build a properly encoded Sales Navigator people-search URL.

    The function handles these scenarios:
    1. Both `english_description` and `user_input_salesnav_url` are provided.
    2. Only `user_input_salesnav_url` is provided (no `english_description`).
    3. Only `english_description` is provided (no `user_input_salesnav_url`).
    4. Neither is provided -> returns an error.

    Args:
        english_description: A plain-English description of desired filters
            (e.g., "Find me 2nd-degree connections in the IT industry who changed jobs recently").
        user_input_salesnav_url: If the user has provided a Sales Navigator URL to use. (default "").
        tool_config: Optional list of dictionaries containing configuration details
            for the LLM or related tools.

    Returns:
        A dictionary with a single key: "linkedin_salenav_url_with_query_parameters".
        This maps to a string containing the fully qualified Sales Navigator URL.

    Raises:
        ValueError: If neither english_description nor user_input_salesnav_url is provided.
        Exception: If the LLM call fails or cannot generate a valid URL.
    """

    # Explanation of potential filters to guide the model
    supported_filters_explanation = """
        Sales Navigator filters include (not exhaustive):
            - PAST_COLLEAGUE
            - CURRENT_TITLE
            - PAST_TITLE
            - CURRENT_COMPANY
            - PAST_COMPANY
            - GEOGRAPHY (REGION)
            - INDUSTRY
            - SCHOOL
            - CONNECTION (RELATIONSHIP)
            - CONNECTIONS_OF
            - GROUP
            - COMPANY_HEADCOUNT
            - COMPANY_TYPE
            - SENIORITY_LEVEL
            - YEARS_IN_POSITION
            - YEARS_IN_COMPANY
            - FOLLOWING_YOUR_COMPANY (FOLLOWS_YOUR_COMPANY)
            - VIEWED_YOUR_PROFILE
            - CHANGED_JOBS (RECENTLY_CHANGED_JOBS)
            - POSTED_ON_LINKEDIN
            - MENTIONED_IN_NEWS
            - TECHNOLOGIES_USED
            - ANNUAL_REVENUE
            - LEAD_INTERACTIONS (e.g. Viewed Profile, Messaged)
            - SAVED_LEADS_AND_ACCOUNTS
            - WITH_SHARED_EXPERIENCES
            - FIRST_NAME
            - LAST_NAME
            - FUNCTION
            - YEARS_OF_EXPERIENCE
            - YEARS_AT_CURRENT_COMPANY
            - YEARS_IN_CURRENT_POSITION
            - COMPANY_HEADQUARTERS
            - keywords
        """

    # System message to guide the LLM
    system_message = (
        "You are a helpful AI Assistant that converts an English description of "
        "LinkedIn Sales Navigator search requirements into a valid LinkedIn Sales Navigator people-search URL. "
        "Your output MUST be a single valid URL with properly encoded parameters. "
        "No extra commentary or text is allowed. If you are unsure about a filter, make your best guess or omit it."
    )

    # Examples to help the LLM
    few_examples_of_queries = (
        "\n 1. Below is an example search url with filter --  company headcount 11-500, seniority level CXO, Current Job Title Chief Marketing Officer," 
        "Geography United States, Connection 2nd-degree connections, and Recently Changed jobs: \n"
        "\nhttps://www.linkedin.com/sales/search/people?query="
        "(recentSearchParam%3A(id%3A4390717732%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList"
        "((id%3AC%2Ctext%3A11-50%2CselectionType%3AINCLUDED)%2C(id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)))%2C(type%3AREGION%2Cvalues%3AList"
        "((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ARECENTLY_CHANGED_JOBS%2Cvalues%3AList((id%3ARPC%2Ctext%3AChanged%2520jobs%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ARELATIONSHIP%2Cvalues%3AList((id%3AS%2Ctext%3A2nd%2520degree%2520connections%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))))\n\n"
        "\n 2. Below is Another example search url with filters --  company headcount 201-500, seniority level CXO, Current Job Title Chief Executive Officer," 
        "Geography United States, Connection 1st-degree connections, and Recently Posted on LinkedIn: \n"
        "https://www.linkedin.com/sales/search/people?query="
        "(recentSearchParam%3A(id%3A4390717732%2CdoLogHistory%3Atrue)%2C"
        "filters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AREGION%2Cvalues%3AList((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ARELATIONSHIP%2Cvalues%3AList((id%3AF%2Ctext%3A1st%2520degree%2520connections%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A8%2Ctext%3AChief%2520Executive%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3APOSTED_ON_LINKEDIN%2Cvalues%3AList((id%3ARPOL%2CselectionType%3AINCLUDED)))))&viewAllFilters=true\n"
        "\n3. Below is example to Exclude people who have viewed your profile recently or messaged recently: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)"
        "%2Cfilters%3AList((type%3ALEAD_INTERACTIONS%2Cvalues%3AList((id%3ALIVP%2Ctext%3AViewed%2520profile%2CselectionType%3AEXCLUDED)"
        "%2C(id%3ALIMP%2Ctext%3AMessaged%2CselectionType%3AEXCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))))"
        "\n 4. Below is example to exclude people who are in your saved leads or accounts list: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters%3A"
        "List((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))%2C"
        "(type%3ASAVED_LEADS_AND_ACCOUNTS%2Cvalues%3AList((id%3ASL%2Ctext%3AAll%2520my%2520saved%2520leads%2CselectionType%3AEXCLUDED)%2C"
        "(id%3ASA%2Ctext%3AAll%2520my%2520saved%2520accounts%2CselectionType%3AEXCLUDED)))))"
        "\n 5. Below is example to include people with whom you have shared experiences or is past collegue: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2C"
        "filters%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))%2C"
        "(type%3AWITH_SHARED_EXPERIENCES%2Cvalues%3AList((id%3ACOMM%2Ctext%3AShared%2520experiences%2CselectionType%3AINCLUDED)))%2C"
        "(type%3ARELATIONSHIP%2Cvalues%3AList((id%3AS%2Ctext%3A2nd%2520degree%2520connections%2CselectionType%3AINCLUDED)))"
        "%2C(type%3APAST_COLLEAGUE%2Cvalues%3AList((id%3APCOLL%2CselectionType%3AINCLUDED)))))"
        "\n 6. Below is example to track leads who viewed your profile recently or followed your company page: \n"
        "https://www.linkedin.com/sales/search/people?query="
        "(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A716%2Ctext%3AChief%2520Marketing%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AVIEWED_YOUR_PROFILE%2Cvalues%3AList((id%3AVYP%2Ctext%3AViewed%2520your%2520profile%2520recently%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AFOLLOWS_YOUR_COMPANY%2Cvalues%3AList((id%3ACF%2CselectionType%3AINCLUDED)))))&viewAllFilters=true"
        "\n 7. Below is example Of somer personal filters like name school industry that can be used: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)"
        "%2Cfilters%3AList((type%3AREGION%2Cvalues%3AList((id%3A102221843%2Ctext%3ANorth%2520America%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AINDUSTRY%2Cvalues%3AList((id%3A6%2Ctext%3ATechnology%252C%2520Information%2520and%2520Internet%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A153%2Ctext%3AChief%2520Technology%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AYEARS_OF_EXPERIENCE%2Cvalues%3AList((id%3A4%2Ctext%3A6%2520to%252010%2520years%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ASCHOOL%2Cvalues%3AList((id%3A1792%2Ctext%3AStanford%2520University%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AFIRST_NAME%2Cvalues%3AList((text%3AJohn%2CselectionType%3AINCLUDED)))%2C(type%3ALAST_NAME%2Cvalues%3A"
        "List((text%3ADoe%2CselectionType%3AINCLUDED)))%2C(type%3AGROUP%2Cvalues%3AList((id%3A5119103%2Ctext%3AMobile%2520Integration%2520Cloud%2520Services%2CselectionType%3AINCLUDED)))))viewAllFilters=true"
        "\n 8. Example of some role related filters you can use like job title, seniority level, years at current company: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters"
        "%3AList((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A153%2Ctext%3AChief%2520Technology%2520Officer%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AFUNCTION%2Cvalues%3AList((id%3A8%2Ctext%3AEngineering%2CselectionType%3AINCLUDED)%2C(id%3A25%2Ctext%3ASales%2CselectionType%3AINCLUDED)"
        "%2C(id%3A15%2Ctext%3AMarketing%2CselectionType%3AINCLUDED)))%2C(type%3ASENIORITY_LEVEL%2Cvalues%3AList((id%3A120%2Ctext%3ASenior%2CselectionType%3AINCLUDED)"
        "%2C(id%3A310%2Ctext%3ACXO%2CselectionType%3AINCLUDED)%2C(id%3A110%2Ctext%3AEntry%2520Level%2CselectionType%3AEXCLUDED)))"
        "%2C(type%3APAST_TITLE%2Cvalues%3AList((id%3A5%2Ctext%3ADirector%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AYEARS_AT_CURRENT_COMPANY%2Cvalues%3AList((id%3A3%2Ctext%3A3%2520to%25205%2520years%2CselectionType%3AINCLUDED)))"
        "%2C(type%3AYEARS_IN_CURRENT_POSITION%2Cvalues%3AList((id%3A3%2Ctext%3A3%2520to%25205%2520years%2CselectionType%3AINCLUDED)))))"
        "\n 9. Example of some lead company related filters you can use like company headcount, company name, previous company etc: \n"
        "https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A4395364884%2CdoLogHistory%3Atrue)%2Cfilters%3Ac"
        "List((type%3ACURRENT_TITLE%2Cvalues%3AList((id%3A136%2Ctext%3AVice%2520President%2520of%2520Sales%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACURRENT_COMPANY%2Cvalues%3AList((id%3Aurn%253Ali%253Aorganization%253A5289249%2Ctext%3AArangoDB%2CselectionType%3AINCLUDED%2Cparent%3A(id%3A0))))"
        "%2C(type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AC%2Ctext%3A11-50%2CselectionType%3AINCLUDED)))"
        "%2C(type%3APAST_COMPANY%2Cvalues%3AList((id%3Aurn%253Ali%253Aorganization%253A828370%2Ctext%3ANeo4j%2CselectionType%3AINCLUDED%2Cparent%3A(id%3A0))))"
        "%2C(type%3ACOMPANY_TYPE%2Cvalues%3AList((id%3AP%2Ctext%3APrivately%2520Held%2CselectionType%3AINCLUDED)%2C(id%3AC%2Ctext%3APublic%2520Company%2CselectionType%3AINCLUDED)))"
        "%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A103644278%2Ctext%3AUnited%2520States%2CselectionType%3AINCLUDED)))))"
        "Below is example of using custom keywords to search for people having neo4j in profile: \n"
        "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2Ckeywords%3Aneo4j)\n"
    )


    # 1. Validate presence of input
    if not english_description and not user_input_salesnav_url:
        raise ValueError("Error: Neither english_description nor user_input_salesnav_url was provided.")

    # 2. Build the user_prompt conditionally
    if english_description and user_input_salesnav_url:
        # Case 1: Both present
        user_prompt = f"""
            {system_message}

            The user wants to build a Sales Navigator people-search URL for LinkedIn.
            They have described the desired filters in plain English as follows:
            "{english_description}"

            Sales navigator URL provided by user:
            {user_input_salesnav_url}

            The supported filters are described below (for your reference):
            {supported_filters_explanation}

            Some example URLs:
            {few_examples_of_queries}

            Do the following step by step:
            1. Think about the filters required to query the leads.
            2. Since the user provided a URL, incorporate or validate that URL.
            3. Look at the examples and supported filters to build the query.
            4. Make sure the URL generated is valid. Don't make up filters not in the list.
            Double-check to ensure the URL is in valid Sales Navigator format with properly-encoded parameters.
            Output MUST be valid JSON with only 'linkedin_salenav_url_with_query_parameters' as a key.
        """
    elif not english_description and user_input_salesnav_url:
        # Case 2: Only user_input_salesnav_url
        user_prompt = f"""
            {system_message}

            The user has only provided a Sales Navigator URL to use:
            {user_input_salesnav_url}

            You do not have an English description of desired filters. Please use or validate
            the provided Sales Navigator URL. The supported filters are described below (for your reference):
            {supported_filters_explanation}

            Some example URLs:
            {few_examples_of_queries}

            Output MUST be valid JSON with only 'linkedin_salenav_url_with_query_parameters' as a key.
        """
    else:
        # Case 3: Only english_description
        user_prompt = f"""
            {system_message}

            They have described the desired filters in plain English as follows:
            "{english_description}"

            The supported filters are described below (for your reference):
            {supported_filters_explanation}

            Some example URLs:
            {few_examples_of_queries}

            Do the following step by step:
            1. Think about the filters required to query the leads based on the English description.
            2. Look at the examples and supported filters to build the query.
            3. Make sure the URL generated is valid. Don't make up filters not in the list.
            Double-check to ensure the URL is in valid Sales Navigator format with properly-encoded parameters.
            Output MUST be valid JSON with only 'linkedin_salenav_url_with_query_parameters' as a key.
        """

    logger.info("Generating Sales Navigator people-search URL from description: '%s'", english_description)

    # 3. Call your structured-output helper
    response, status = await get_structured_output_internal(
        user_prompt,
        SalesNavQuery,
        tool_config=tool_config
    )

    if status != "SUCCESS" or not response:
        raise Exception("Error generating the Sales Navigator URL.")

    logger.info("Successfully generated Sales Navigator URL.")
    return response.dict()
