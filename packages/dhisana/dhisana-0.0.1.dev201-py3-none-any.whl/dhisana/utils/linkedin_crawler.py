# Login and Crawl linked in for relevant information in background.
import asyncio
import os
import sys
import logging
from typing import List, Optional
from pydantic import BaseModel
from playwright.async_api import async_playwright
import pandas as pd

from dhisana.utils.dataframe_tools import get_structured_output
from dhisana.utils.web_download_parse_tools import parse_html_content_as_text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for structured data
class LinkedInUserProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    num_of_connections: Optional[int] = None
    num_of_followers: Optional[int] = None
    summary: Optional[str] = None
    experience: Optional[List[str]] = None
    education: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    accomplishments: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    profile_url: Optional[str] = None

class SalesNavigatorInsights(BaseModel):
    sales_navigator_insight: Optional[str] = None
    key_signals: Optional[str] = None
    common_connection_paths: Optional[List[str]] = None


async def get_html_content_from_url_internal(page, url):
    """
    Navigate to a URL using Playwright and retrieve the page content.
    """
    logging.info(f"Requesting {url}")
    try:
        await page.goto(url, timeout=10000)
        html_content = await page.content()
        return parse_html_content_as_text(html_content)
    except Exception as e:
        logging.info(f"Failed to fetch {url}: {e}")
        return ""




async def login_to_linkedin(page, email, password, headless):
    """
    Log into LinkedIn using the provided email and password.
    """
    await page.goto("https://www.linkedin.com/uas/login")
    await page.wait_for_load_state('load')

    await page.get_by_label("Email or Phone").click()
    await page.get_by_label("Email or Phone").fill(email)
    await page.get_by_label("Password").click()
    await page.get_by_label("Password").fill(password)
    await page.locator("#organic-div form").get_by_role("button", name="Sign in", exact=True).click()
    await page.wait_for_load_state('load')

    if "checkpoint/challenge" in page.url:
        if not headless:
            logger.warning("Captcha page encountered! Human intervention is needed.")
            max_iterations = 25
            for attempt in range(max_iterations):
                await asyncio.sleep(3)  # Wait for 3 seconds before checking again
                await page.wait_for_load_state('load')  # Ensure the page is loaded
                if "checkpoint/challenge" not in page.url:
                    logger.info("Captcha solved. Continuing with the process.")
                    break
            else:
                logger.error(f"Captcha not solved after {max_iterations} attempts. Exiting.")
                sys.exit(1)
            await asyncio.sleep(3)
        else:
            logger.error("Captcha page encountered! Aborting due to headless mode.")
            sys.exit(1)

async def extract_from_page(page, url, response_type):
    """
    Extract structured data from a web page using OpenAI's API.
    """
    # Get page HTML content
    content_text = await get_html_content_from_url_internal(page, url)
    if not content_text:
        return None, 'FAIL'

    # Get structured content using OpenAI's API
    extract_content, status = await get_structured_output(content_text, response_type)
    return extract_content, status

async def extract_user_content_from_linkedin(linkedin_id:str, output_csv_path:str):
    """
    Main function to orchestrate scraping and data extraction.
    """
    email = os.environ.get("LINKEDIN_EMAIL")
    password = os.environ.get("LINKEDIN_PASSWORD")

    if not email or not password:
        logger.error("LinkedIn credentials not found in environment variables.")
        return {"status": "FAIL", "message": "LinkedIn credentials not found in environment variables."}

    # Start the browser using Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Login to LinkedIn
        await login_to_linkedin(page, email, password, False)

        # List of LinkedIn profiles to scrape
        job_profiles = [
            f"https://www.linkedin.com/in/{linkedin_id}/",
            # Add more profile URLs as needed
        ]

        # Extract data from profiles
        outputs = []
        for profile in job_profiles:
            output, status = await extract_from_page(page, profile, LinkedInUserProfile)
            if status == 'SUCCESS':
                outputs.append(output)
            else:
                outputs.append({})
                logger.error(f"Failed to extract data from {profile}")

        # Create a DataFrame from the outputs and save to CSV
        df = pd.DataFrame(outputs)
        csv_file_path = '/tmp/profile_data.csv'
        df.to_csv(csv_file_path, index=False)
        logger.info(f"Saved profile data to {csv_file_path}")

        # List of Sales Navigator insights URLs to scrape
        sales_navigator_insights = [
            f"https://www.linkedin.com/in/{linkedin_id}/details/sales-lead-insights-details/",
            # Add more URLs as needed
        ]

        # Extract data from Sales Navigator insights
        insights_outputs = []
        for profile in sales_navigator_insights:
            output, status = await extract_from_page(page, profile, SalesNavigatorInsights)
            if status == 'SUCCESS':
                insights_outputs.append(output)
            else:
                insights_outputs.append({})
                logger.error(f"Failed to extract data from {profile}")

        # Create a DataFrame from the outputs and save to CSV
        df_insights = pd.DataFrame(insights_outputs)
        insights_csv_file_path = output_csv_path
        df_insights.to_csv(insights_csv_file_path, index=False)
        logger.info(f"Saved Sales Navigator insights to {insights_csv_file_path}")

        # Close the browser
        await browser.close()
        return {"status": "SUCCESS", "message": f"Data extraction completed successfully to {insights_csv_file_path}."}