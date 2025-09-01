import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from dhisana.schemas.sales import SmartList
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal
from dhisana.utils.workflow_code_model import WorkflowPythonCode

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_leads_code(
    filters: str,
    example_url: str,
    max_pages: int = 1,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> Tuple[Dict[str, Any], str]:
    """
    Generate a workflow code (Python code) from an English description, specifically
    to create a list from Sales Navigator.

    Returns:
      A tuple of:
       - A dict containing {'workflow_python_code': '...'} 
       - A string representing status, e.g., 'SUCCESS' or 'ERROR'.
    """
    system_message = (
        "You are a helpful AI assistant who is an expert python coder. I want you to convert "
        "an English description of a requirement provided by user into an executable Python "
        "function called create_list_from_sales_navigator. Your output must be valid Python code. "
        "The provided example shows how the structure looks like and what methods you can use. "
        "Make sure the imports are present within the function definition itself. Make sure the "
        "logging library is imported and logger defined within the function. "
        "Use the output function signature:\n"
        "    async def create_list_from_sales_navigator(filters, example_url, max_pages, tool_config)\n"
    )

    example_of_workflow_code = (
        '''
        async def create_list_from_sales_navigator(filters, example_url, max_pages, tool_config):
            """
            Example workflow demonstrating how to create a list from Sales Navigator.
            Returns ("SUCCESS", unique_leads) or ("ERROR", []).
            """
            # Make sure required imports are there within the function definition itself.
            import asyncio
            import logging
            from typing import Any, Dict, List, Optional, Tuple
            from dhisana.utils.agent_task import execute_task
            from dhisana.utils.compose_salesnav_query import generate_salesnav_people_search_url

            # Make sure the logger is present.
            logger = logging.getLogger(__name__)
            logging.basicConfig(level=logging.INFO)

            try:
                logger.info("Starting custom_workflow execution")

                if not example_url:
                    # Generate a Sales Navigator URL
                    result = await generate_salesnav_people_search_url(
                        english_description=filters,
                        tool_config=tool_config
                    )
                    if not result:
                        logger.error("generate_salesnav_people_search_url returned no result")
                        return "ERROR", []

                    salesnav_url = result.get('linkedin_salenav_url_with_query_parameters', None)
                    logger.info("Sales Navigator URL obtained: %s", salesnav_url)

                    if not salesnav_url:
                        logger.warning("No valid URL returned; cannot proceed.")
                        return "ERROR", []
                else:
                    salesnav_url = example_url

                # Extract leads from the URL
                command_args = {
                    "salesnav_url_list_leads": salesnav_url,
                    "max_pages": max_pages,
                    "enrich_detailed_lead_information": False,
                    "enrich_detailed_company_information": False,
                }
                try:
                    extraction_result = await execute_task(
                        "extract_leads_information",
                        command_args,
                        tool_config=tool_config
                    )
                except Exception as exc:
                    logger.exception("Error while extracting leads: %s", exc)
                    return "ERROR", []

                leads = extraction_result.get('data', [])
                logger.info("Number of leads extracted: %d", len(leads))

                if not leads:
                    return "SUCCESS", []

                # Deduplicate leads
                unique_leads = {}
                for lead in leads:
                    lead_url = lead.get("user_linkedin_salesnav_url")
                    if lead_url:
                        unique_leads[lead_url] = lead

                deduped_leads = list(unique_leads.values())
                logger.info("Unique leads after deduplication: %d", len(deduped_leads))

                logger.info("Completed custom_workflow with success.")
                return "SUCCESS", deduped_leads

            except Exception as e:
                logger.exception("Exception in custom_workflow: %s", e)
                return "ERROR", []
        '''
    )

    # Short note if user has or hasn't provided a Sales Navigator URL
    user_provided_url = "Keep user_input_salesnav_url variable as empty."
    if "linkedin.com/sales/search/" in filters:
        user_provided_url = "Use user_input_salesnav_url as provided by user"

    # Explanation of possible filters
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
            - LEAD_INTERACTIONS (Viewed Profile, Messaged)
            - SAVED_LEADS_AND_ACCOUNTS
            - WITH_SHARED_EXPERIENCES
            - FIRST_NAME
            - LAST_NAME
            - FUNCTION
            - YEARS_OF_EXPERIENCE
            - YEARS_AT_CURRENT_COMPANY
            - YEARS_IN_CURRENT_POSITION
            - COMPANY_HEADQUARTERS
    """

    # Build the user prompt
    user_prompt = f"""
    {system_message}
    Do the following step by step:
    1. Think about the leads the user wants to query and filters to use for the same. 
    2. If the user has provided a sales navigator url use that.
    3. Take a look at the examples provided to construct the URL if user has not provided one. 
    4. Think about the code example provided and see how you will fill the english_request_for_salesnav_search and user_input_salesnav_url correctly.
    5. Generate the correct python code which takes care of above requirements. 
    6. Make sure the code is valid and returns results in the format ("SUCCESS", leads_list) or ("ERROR", []).
    7. Return the result in valid JSON format filled in workflow_python_code.

    The user wants to generate code in python that performs the following:

    "{filters}"

    {user_provided_url}

    Example of a workflow python code:
    {example_of_workflow_code}

    If user has provided a Sales Navigator URL set it to user_input_salesnav_url in the code 
    and pass as input to generate_salesnav_people_search_url.

    Each lead returned has at least:
    full_name, first_name, last_name, email, user_linkedin_salesnav_url, organization_linkedin_salesnav_url,
    user_linkedin_url, primary_domain_of_organization, job_title, phone, headline,
    lead_location, organization_name, organization_website, summary_about_lead, keywords,
    number_of_linkedin_connections

    Following are some common methods available:
    1. generate_salesnav_people_search_url - to generate Sales Navigator URL from plain English query.
       (Supported filters: {supported_filters_explanation})

    The output function signature MUST be:
      async def create_list_from_sales_navigator(filters, example_url, max_pages, tool_config):

    Double check to make sure the generated python code is valid and returns results in the format 
    ("SUCCESS", leads_list) or ("ERROR", []).
    Output HAS to be valid JSON like:
    {{
        "workflow_python_code": "code that has been generated"
    }}
    """

    # Invoke LLM to generate code
    response, status = await get_structured_output_internal(
        user_prompt,
        WorkflowPythonCode,
        tool_config=tool_config
    )

    # Return dict + status
    return response.model_dump(), status


async def generate_leads_salesnav(
    filter_object: Dict[str, Any],
    request: SmartList,
    example_url: str,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    1) Generates Python workflow code from user's filter_object + example_url.
    2) Executes the code to query Sales Navigator.
    3) Returns JSON with {"status": <STATUS>, "leads": [list_of_leads]} or an error message.
    """

    # Calculate max_pages from request
    # Each page is assumed to have ~20 leads
    pages = int(request.max_items_to_search / 20) if request.max_items_to_search else 1
    if pages < 1:
        pages = 1
    if pages > 90:
        pages = 90

    # Generate the code
    response, status = await generate_leads_code(
        filters=str(filter_object),
        example_url=example_url,
        max_pages=pages,
        tool_config=tool_config
    )

    # If successful, try to run the code
    if status == "SUCCESS" and response and response.get("workflow_python_code"):
        code = response["workflow_python_code"]
        if not code:
            return json.dumps({"error": "No workflow code generated.", "status": status})

        logger.info("Generated workflow code:\n%s", code)

        local_vars: Dict[str, Any] = {}
        global_vars: Dict[str, Any] = {}

        try:
            # Execute the generated code
            exec(code, global_vars, local_vars)
            create_fn = local_vars.get("create_list_from_sales_navigator")
            if not create_fn:
                raise RuntimeError("No 'create_list_from_sales_navigator' function found in generated code.")

            async def run_create_list(flt: str, ex_url: str, mx_pages: int, t_cfg: Optional[List[Dict[str, Any]]]):
                return await create_fn(flt, ex_url, mx_pages, t_cfg)

            # Invoke the function
            try:
                result = await run_create_list(str(filter_object), example_url, pages, tool_config)
            except Exception as e:
                logger.exception("Error while running create_list_from_sales_navigator.")
                return json.dumps({"status": "ERROR", "error": str(e)})

            # Expect a tuple like ("SUCCESS", leads_list) or ("ERROR", [])
            if not isinstance(result, tuple) or len(result) != 2:
                return json.dumps({
                    "status": "ERROR",
                    "error": "Workflow code did not return an expected (status, leads_list) tuple."
                })

            status_returned, leads_list = result
            if status_returned != "SUCCESS":
                return json.dumps({
                    "status": status_returned,
                    "error": "Workflow returned an error status.",
                    "leads": leads_list
                })

            # Return success + leads
            return json.dumps({
                "status": status_returned,
                "leads": leads_list
            })

        except Exception as e:
            logger.exception("Exception occurred while executing workflow code.")
            return json.dumps({"status": "ERROR", "error": str(e)})

    # If code generation failed or no code
    return json.dumps({"error": "No workflow code generated.", "status": status})
