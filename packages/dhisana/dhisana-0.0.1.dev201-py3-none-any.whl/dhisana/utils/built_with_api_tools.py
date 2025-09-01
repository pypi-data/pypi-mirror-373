import json
import os
import aiohttp
from typing import Optional
import os
import aiohttp
import backoff
from dhisana.utils.cache_output_tools import cache_output,retrieve_output
from dhisana.utils.assistant_tool_tag import assistant_tool
from typing import Optional
from typing import Optional, List, Dict

def get_builtwith_api_key(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the BUILTWITH_API_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The BUILTWITH_API_KEY access token.

    Raises:
        ValueError: If the BuiltWith integration has not been configured.
    """
    if tool_config:
        builtwith_config = next(
            (item for item in tool_config if item.get("name") == "builtwith"), None
        )
        if builtwith_config:
            config_map = {
                item["name"]: item["value"]
                for item in builtwith_config.get("configuration", [])
                if item
            }
            BUILTWITH_API_KEY = config_map.get("apiKey")
        else:
            BUILTWITH_API_KEY = None
    else:
        BUILTWITH_API_KEY = None

    BUILTWITH_API_KEY = BUILTWITH_API_KEY or os.getenv("BUILTWITH_API_KEY")
    if not BUILTWITH_API_KEY:
        raise ValueError(
            "BuiltWith integration is not configured. Please configure the connection to BuiltWith in Integrations."
        )
    return BUILTWITH_API_KEY

# Use BuiltWith API to find tech stack and financials of a company
@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def get_company_info_from_builtwith(
    company_domain: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
):
    """
    Fetch a company's technology details from BuiltWith using the company domain.
    
    Parameters:
    - **company_domain** (*str*, optional): Domain of the company.

    Returns:
    - **dict**: JSON response containing technology information.
    """
    BUILTWITH_API_KEY = get_builtwith_api_key(tool_config=tool_config)

    if not company_domain:
        return {'error': "Company domain must be provided"}

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json"
    }

    cached_response = retrieve_output("get_company_info_from_builtwith", company_domain)  # Replace with your caching logic if needed
    if cached_response is not None:
        return cached_response

    url = f'https://api.builtwith.com/v19/api.json?KEY={BUILTWITH_API_KEY}&LOOKUP={company_domain}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                cache_output("get_company_info_from_builtwith", company_domain, result)  # Replace with your caching logic if needed
                return result
            elif response.status == 429:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                try:
                    result = await response.json()
                    return {'error': result}
                except Exception as e:
                    return {'error': f"Unexpected error: {str(e)}"}

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def get_company_financials_from_builtwith(
    company_domain: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
):
    """
    Fetch a company's financial details from BuiltWith using the company domain.
    
    Parameters:
    - **company_domain** (*str*, optional): Domain of the company.

    Returns:
    - **dict**: JSON response containing financial information.
    """
    BUILTWITH_API_KEY = get_builtwith_api_key(tool_config=tool_config)

    if not company_domain:
        return {'error': "Company domain must be provided"}

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "accept": "application/json"
    }

    cached_response = retrieve_output("get_company_financials_from_builtwith", company_domain)  # Replace with your caching logic if needed
    if cached_response is not None:
        return cached_response

    url = f'https://api.builtwith.com/v19/financial.json?KEY={BUILTWITH_API_KEY}&LOOKUP={company_domain}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                cache_output("get_company_financials_from_builtwith", company_domain, result)  # Replace with your caching logic if needed
                return result
            elif response.status == 429:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                try:
                    result = await response.json()
                    return {'error': result}
                except Exception as e:
                    return {'error': f"Unexpected error: {str(e)}"}

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def get_company_info_from_builtwith_by_name(company_name: str, tool_config: Optional[List[Dict]] = None):
    """
    Fetch a company's technology details from BuiltWith using the company name.

    Parameters:
    - company_name (str): Name of the company.

    Returns:
    - dict: JSON response containing technology information or error details.
    """
    BUILTWITH_API_KEY = get_builtwith_api_key(tool_config=tool_config)

    if not company_name:
        return {'error': "Company name must be provided"}

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Accept": "application/json"
    }

    # Step 1: Use Company To URL API to get the company's domain
    company_to_url_api = f'https://ctu.builtwith.com/ctu2/api.json?KEY={BUILTWITH_API_KEY}&COMPANY={company_name}'
    company_info = retrieve_output("get_company_info_from_builtwith_by_name", company_name)  
    if company_info:
        company_domain = company_info.get('Domain')
        return await get_company_info_from_builtwith(company_domain)

    async with aiohttp.ClientSession() as session:
        async with session.get(company_to_url_api, headers=headers) as response:
            if response.status == 200:
                company_data = await response.json()
                if isinstance(company_data, list) and company_data:
                    company_info = company_data[0]
                    company_domain = company_info.get('Domain')
                    if not company_domain:
                        return {'error': "Domain not found for the given company name"}
                    cache_output("get_company_info_from_builtwith_by_name", company_name, company_info)
                    return await get_company_info_from_builtwith(company_domain)
                else:
                    return {'error': "No results found for the given company name"}
            elif response.status == 429:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                try:
                    error_data = await response.json()
                    return {'error': error_data}
                except Exception as e:
                    return {'error': f"Unexpected error: {str(e)}"}    

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def is_tech_used_in_company(
    company_domain: Optional[str] = None, 
    company_name: Optional[str] = None, 
    keyword: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None
) -> bool:
    if not company_domain and not company_name:
        return False

    if not keyword:
        return False

    if company_domain:
        company_data_buildwith = await get_company_info_from_builtwith(company_domain, tool_config=tool_config)
    elif company_name:
        company_data_buildwith = await get_company_info_from_builtwith_by_name(company_name, tool_config=tool_config)
        company_domain = company_data_buildwith.get('Lookup', '')

    data_str = json.dumps(company_data_buildwith).lower()
    keyword_lower = keyword.lower()
    return keyword_lower in data_str

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=2,
    giveup=lambda e: e.status != 429,
    factor=10,
)
async def get_company_domain_from_name(
    company_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> str:
    if not company_name:
        return ''

    company_data_buildwith = await get_company_info_from_builtwith_by_name(company_name, tool_config=tool_config)
    company_domain = company_data_buildwith.get('Lookup', '')
    return company_domain

