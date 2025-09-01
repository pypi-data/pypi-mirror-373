import aiohttp
import logging
from typing import Optional
from dhisana.utils.assistant_tool_tag import assistant_tool

@assistant_tool
async def push_to_clay_table(
    data: dict,
    webhook: Optional[str] = None,
    api_key: Optional[str] = None,
):
    """
    Push data to the Clay webhook.

    Parameters:
    - **data** (*dict*): Data to send to the webhook.
    - **webhook** (*str*, optional): The webhook URL.
    - **api_key** (*str*, optional): The authentication token.

    Returns:
    - **dict**: Response message or error.
    """
    if not api_key:
        return {
            'error': "Clay integration is not configured. Please configure the connection to Clay in Integrations."
        }

    if not webhook:
        return {'error': "Webhook URL not provided"}

    headers = {
        "Content-Type": "application/json",
        "x-clay-webhook-auth": api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook, headers=headers, json=data) as response:
            result = await response.text()
            if response.status == 200:
                return {'message': result}
            else:
                logging.warning(f"push_to_clay_table failed: {result}")
                return {'error': result}