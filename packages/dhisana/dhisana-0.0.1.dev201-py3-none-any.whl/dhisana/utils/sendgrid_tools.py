import logging
import os
from typing import Optional, List, Dict
import aiohttp
from dhisana.utils.assistant_tool_tag import assistant_tool


def get_mailgun_notify_key(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the MAILGUN_NOTIFY_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The MAILGUN_NOTIFY_KEY access token.

    Raises:
        ValueError: If the Mailgun integration has not been configured.
    """
    if tool_config:
        mailgun_config = next(
            (item for item in tool_config if item.get("name") == "mailgun"), None
        )
        if mailgun_config:
            config_map = {
                item["name"]: item["value"]
                for item in mailgun_config.get("configuration", [])
                if item
            }
            MAILGUN_NOTIFY_KEY = config_map.get("apiKey")
        else:
            MAILGUN_NOTIFY_KEY = None
    else:
        MAILGUN_NOTIFY_KEY = None

    MAILGUN_NOTIFY_KEY = MAILGUN_NOTIFY_KEY or os.getenv("MAILGUN_NOTIFY_KEY")
    if not MAILGUN_NOTIFY_KEY:
        raise ValueError(
            "Mailgun integration is not configured. Please configure the connection to Mailgun in Integrations."
        )
    return MAILGUN_NOTIFY_KEY

def get_mailgun_notify_domain(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the MAILGUN_NOTIFY_DOMAIN from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The MAILGUN_NOTIFY_DOMAIN.

    Raises:
        ValueError: If the Mailgun integration has not been configured.
    """
    if tool_config:
        mailgun_config = next(
            (item for item in tool_config if item.get("name") == "mailgun"), None
        )
        if mailgun_config:
            config_map = {
                item["name"]: item["value"]
                for item in mailgun_config.get("configuration", [])
                if item
            }
            MAILGUN_NOTIFY_DOMAIN = config_map.get("notifyDomain")
        else:
            MAILGUN_NOTIFY_DOMAIN = None
    else:
        MAILGUN_NOTIFY_DOMAIN = None

    MAILGUN_NOTIFY_DOMAIN = MAILGUN_NOTIFY_DOMAIN or os.getenv("MAILGUN_NOTIFY_DOMAIN")
    if not MAILGUN_NOTIFY_DOMAIN:
        raise ValueError(
            "Mailgun integration is not configured. Please configure the connection to Mailgun in Integrations."
        )
    return MAILGUN_NOTIFY_DOMAIN

@assistant_tool
async def send_email_with_mailgun(sender: str, recipients: List[str], subject: str, message: str, tool_config: Optional[List[Dict]] = None):
    """
    Send an email using the Mailgun API.

    Parameters:
    - **sender** (*str*): The email address of the sender.
    - **recipients** (*List[str]*): A list of recipient email addresses.
    - **subject** (*str*): The subject of the email.
    - **message** (*str*): The HTML content of the email.
    """
    try:
        # Retrieve Mailgun API key and domain from tool configuration or environment variables
        api_key = get_mailgun_notify_key(tool_config)
        domain = get_mailgun_notify_domain(tool_config)

        # Prepare the data payload for the email
        data = {
            "from": sender,
            "to": recipients,
            "subject": subject,
            "html": message,
        }

        # Create an asynchronous HTTP session
        async with aiohttp.ClientSession() as session:
            # Send a POST request to the Mailgun API to send the email
            async with session.post(
                f"https://api.mailgun.net/v3/{domain}/messages",
                auth=aiohttp.BasicAuth("api", api_key),
                data=data,
            ) as response:
                # Return the response text
                return await response.text()
    except Exception as ex:
        # Log any exceptions that occur and return an error message
        logging.warning(f"Error sending email invite: {ex}")
        return {"error": str(ex)}