import os
import aiohttp
import backoff
import logging
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

# Use hubspot to resolve company name to domain name. Clearbit is not part of Hubspot.

@assistant_tool
@backoff.on_exception(
    backoff.expo,
    aiohttp.ClientResponseError,
    max_tries=3,
    giveup=lambda e: e.status != 429,
    factor=60,
)
async def get_company_domain_from_breeze(company_name: str):
    """
    Fetch a company's domain from HubSpot's Breeze Intelligence using the company name.

    Parameters:
    - company_name (str): Name of the company.

    Returns:
    - dict: JSON response containing the domain or an error message.
    """
    HUBSPOT_API_KEY = os.environ.get('HUBSPOT_API_KEY')
    if not HUBSPOT_API_KEY:
        return {
            'error': "HubSpot integration is not configured. Please configure the connection to HubSpot in Integrations."
        }

    if not company_name:
        return {'error': "Company name must be provided"}

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Accept": "application/json"
    }

    # Check if response is already cached
    cached_response = retrieve_output("get_company_domain_from_breeze", company_name)
    if cached_response is not None:
        return cached_response

    url = "https://api.hubapi.com/crm/v3/objects/companies/search"

    # Define the request body for searching companies by name
    body = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "name",
                        "operator": "EQ",
                        "value": company_name
                    }
                ]
            }
        ],
        "properties": ["domain"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            if response.status == 200:
                result = await response.json()
                results = result.get('results', [])
                if results:
                    company_data = results[0]
                    domain = company_data.get('properties', {}).get('domain')
                    if domain:
                        cache_output("get_company_domain_from_breeze", company_name, {"domain": domain})
                        return {"domain": domain}
                    else:
                        return {'error': "Domain not found for the given company name"}
                else:
                    return {'error': "No company found with the given name"}
            elif response.status == 429:
                logging.warning("Rate limit hi in get_company_domain_from_breeze")
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
