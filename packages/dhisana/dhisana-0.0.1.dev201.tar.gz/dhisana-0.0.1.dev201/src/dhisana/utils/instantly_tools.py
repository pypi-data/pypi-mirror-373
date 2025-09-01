import os
import aiohttp
import logging
from typing import List, Dict, Any
from dhisana.utils.assistant_tool_tag import assistant_tool

logging.basicConfig(level=logging.INFO)
base_url = 'https://api.instantly.ai/v1'

# Manage instantly lists for campaigns

def get_api_key_and_headers() -> Dict[str, str]:
    api_key = os.environ.get('INSTANTLY_API_KEY')
    if not api_key:
        raise ValueError(
            "Instantly integration is not configured. Please configure the connection to Instantly in Integrations."
        )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return headers

async def _handle_response(response: aiohttp.ClientResponse) -> Any:
    if response.status == 200:
        return await response.json()
    elif response.status == 429:
        raise aiohttp.ClientResponseError(
            request_info=response.request_info,
            history=response.history,
            status=response.status,
            message="Rate limit exceeded",
            headers=response.headers
        )
    else:
        error_message = await response.text()
        logging.error(f"Error {response.status}: {error_message}")
        response.raise_for_status()

@assistant_tool
async def add_leads_to_campaign(campaign_id: str, leads: List[Dict[str, str]]) -> Any:
    """
    Add leads to a campaign.

    Args:
        campaign_id (str): The ID of the campaign.
        leads (List[Dict[str, str]]): A list of leads to add, where each lead is represented as a dictionary.

    Returns:
        Any: The response from the API.
    """
    url = f"{base_url}/lead/add"
    payload = {
        "campaign_id": campaign_id,
        "leads": leads
    }
    headers = get_api_key_and_headers()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await _handle_response(response)

@assistant_tool
async def delete_leads_from_campaign(campaign_id: str, lead_emails: List[str]) -> Any:
    """
    Delete leads from a campaign.

    Args:
        campaign_id (str): The ID of the campaign.
        lead_emails (List[str]): A list of lead emails to delete.

    Returns:
        Any: The response from the API.
    """
    url = f"{base_url}/lead/delete"
    payload = {
        "campaign_id": campaign_id,
        "leads": lead_emails
    }
    headers = get_api_key_and_headers()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await _handle_response(response)

@assistant_tool
async def update_lead_variables(lead_email: str, variables: Dict[str, str]) -> Any:
    """
    Update variables for a lead.

    Args:
        lead_email (str): The email of the lead.
        variables (Dict[str, str]): A dictionary of variables to update.

    Returns:
        Any: The response from the API.
    """
    url = f"{base_url}/lead/variable/update"
    payload = {
        "lead": lead_email,
        "variables": variables
    }
    headers = get_api_key_and_headers()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await _handle_response(response)

@assistant_tool
async def set_lead_variables(lead_email: str, variables: Dict[str, str]) -> Any:
    """
    Set variables for a lead.

    Args:
        lead_email (str): The email of the lead.
        variables (Dict[str, str]): A dictionary of variables to set.

    Returns:
        Any: The response from the API.
    """
    url = f"{base_url}/lead/variable/set"
    payload = {
        "lead": lead_email,
        "variables": variables
    }
    headers = get_api_key_and_headers()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await _handle_response(response)

@assistant_tool
async def is_lead_in_campaign(campaign_id: str, lead_email: str) -> bool:
    """
    Check if a lead is in a campaign.

    Args:
        campaign_id (str): The ID of the campaign.
        lead_email (str): The email of the lead.

    Returns:
        bool: True if the lead is in the campaign, False otherwise.
    """
    url = f"{base_url}/campaign/leads"
    params = {
        "campaign_id": campaign_id
    }
    headers = get_api_key_and_headers()
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await _handle_response(response)
            leads = data.get("leads", [])
            return any(lead["email"] == lead_email for lead in leads)