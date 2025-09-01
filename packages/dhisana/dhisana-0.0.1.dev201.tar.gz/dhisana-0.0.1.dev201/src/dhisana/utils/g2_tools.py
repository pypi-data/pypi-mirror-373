import asyncio
import logging
import os
from typing import Optional

import aiohttp
import backoff

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Backoff configuration for handling rate limits and retries
@backoff.on_exception(
    backoff.expo,
    (aiohttp.ClientResponseError, aiohttp.ClientConnectorError),
    max_tries=5,
    giveup=lambda e: e.status != 429,
    factor=2,
)
async def fetch_g2_data(endpoint: str, params: Optional[dict] = None) -> dict:
    """
    Fetch data from a specified G2 API endpoint.

    Parameters:
    - endpoint (str): The API endpoint to fetch data from.
    - params (dict, optional): Query parameters to include in the request.

    Returns:
    - dict: JSON response from the API.
    """
    # Retrieve G2 API token from environment variables
    G2_API_TOKEN = os.getenv('G2_API_TOKEN')
    if not G2_API_TOKEN:
        raise EnvironmentError("G2 API token not found in environment variables.")

    # Base URL for G2 API
    BASE_URL = 'https://data.g2.com/api/v2'

    url = f"{BASE_URL}/{endpoint}"
    headers = {'Authorization': f'Bearer {G2_API_TOKEN}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                logger.warning("Rate limit exceeded. Retrying...")
                await asyncio.sleep(30)
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message="Rate limit exceeded",
                    headers=response.headers
                )
            else:
                error_message = await response.text()
                logger.error(f"Failed to fetch data: {error_message}")
                response.raise_for_status()

async def get_product_info(product_id: str) -> dict:
    """
    Retrieve information for a specific product from G2.

    Parameters:
    - product_id (str): UUID of the product.

    Returns:
    - dict: JSON response containing product information.
    """
    endpoint = f'products/{product_id}'
    return await fetch_g2_data(endpoint)

async def get_product_reviews(product_id: str, page: int = 1, page_size: int = 10) -> dict:
    """
    Retrieve user reviews for a specific product from G2.

    Parameters:
    - product_id (str): UUID of the product.
    - page (int, optional): Page number for pagination (default is 1).
    - page_size (int, optional): Number of reviews per page (default is 10).

    Returns:
    - dict: JSON response containing user reviews.
    """
    endpoint = f'products/{product_id}/reviews'
    params = {'page[number]': page, 'page[size]': page_size}
    return await fetch_g2_data(endpoint, params)

async def get_buyer_intent_data() -> dict:
    """
    Retrieve buyer intent data from G2.

    Note: Access to buyer intent data may require specific permissions or subscriptions.

    Returns:
    - dict: JSON response containing buyer intent data.
    """
    endpoint = 'buyer_intent'  # Replace with the actual endpoint if different
    return await fetch_g2_data(endpoint)

