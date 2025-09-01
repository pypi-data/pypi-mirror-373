# Implement the LinkedIn Sales Navigator Client Agent
# Looks for tasks from service like navigating to a URL, sending connection requests, sending messages, etc.
# Executes the tasks and sends the results back to the service.

import asyncio
from datetime import datetime
import json
import os
import logging
import re
from typing import List, Dict, Any
import html2text
from playwright.async_api import async_playwright, Page
import requests  # or aiohttp if you prefer async calls

import asyncio
import logging
import pyperclip

from playwright.async_api import Page
from bs4 import BeautifulSoup



logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global references
playwright_client = None
browser = None
context = None
page = None

SERVICE_URL = os.environ.get("AGENT_SERVICE_URL", "")
AGENT_ID = os.environ.get("AGENT_ID", "")
AGENT_API_KEY = os.environ.get("API_KEY", "")

# -------------------------------------------------------
# Command to execute on the page
# -------------------------------------------------------
async def navigate_to_url(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    """Example function for navigating to a given URL."""
    url = command_args.get('url', '')
    if url:
        await page.goto(url)
        await page.wait_for_timeout(2000)
    return {"status": "SUCCESS", "message": f"Navigated to {url}"}

async def click_lead_connect_menu(page: Page) -> Dict[str, Any]:
    overflow_button = await page.query_selector('button[aria-label="Open actions overflow menu"]')
    if not overflow_button:
        return {"status": "FAILURE", "message": "Actions overflow menu button not found"}
    await overflow_button.click()
    await page.wait_for_timeout(2000)
    return {"status": "SUCCESS", "message": "click_actions_overflow_menu executed"}


async def goto_url(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Navigates to the Sales Navigator search page and performs a search 
    with a LinkedIn URL or navigates directly to a Sales Navigator URL.

    Args:
        page: Playwright Page object.
        command_args: Dictionary containing 'linkedin_url' or 'salesnav_url'.

    Returns:
        Dictionary with navigation status and message.
    """
    user_linkedin_salesnav_url_by_name = command_args.get("user_linkedin_salesnav_url_by_name", "").strip()
    user_linkedin_salesnav_url = command_args.get("user_linkedin_salesnav_url", "").strip()
    salesnav_url_list_leads = command_args.get("salesnav_url_list_leads", "").strip()

    try:
        if user_linkedin_salesnav_url:
            # Step 1: Navigate directly to the provided Sales Navigator URL
            await page.goto(user_linkedin_salesnav_url)
            await page.wait_for_selector("body", timeout=5000)
            await page.wait_for_timeout(2000)
            return {"status": "SUCCESS", "message": "Navigated to Sales Navigator URL"}
        elif salesnav_url_list_leads:
            # Step 1: Navigate directly to the provided Sales Navigator URL
            await page.goto(salesnav_url_list_leads)
            await page.wait_for_selector("body", timeout=5000)
            await page.wait_for_timeout(2000)
            return {"status": "SUCCESS", "message": "Navigated to Sales Navigator URL"}
        elif user_linkedin_salesnav_url_by_name:
            # Step 2: Navigate to Sales Navigator search page
            await page.goto(user_linkedin_salesnav_url_by_name)
            await page.wait_for_selector("body", timeout=5000)
            # get current page content with a have href starting with /sales/lead/
            anchors = await page.query_selector_all('a[href^="/sales/lead/"]')
            unique_links = set()
            for anchor in anchors:
                link = await anchor.get_attribute("href")
                if link and link.startswith("/sales/lead/"):
                    link = "https://www.linkedin.com" + link
                if link:
                    unique_links.add(link)

            if not unique_links:
                return {"status": "ERROR", "message": "No lead links found in search results"}

            # go to the first link and return the status
            # TODO add additional logic to select the correct link
            first_link = list(unique_links)[0]
            await page.goto(first_link)
            await page.wait_for_selector("body", timeout=5000)
            await page.wait_for_timeout(2000)
            return {"status": "SUCCESS", "message": "Navigated to first search result"}
        else:
            return {"status": "ERROR", "message": "No URL provided"}

    except Exception as e:
        return {"status": "ERROR", "message": f"Navigation failed: {str(e)}"}

async def send_connection_request(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    
    await goto_url(page, command_args)
    # Not a sales lead page check
    if "/sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}

    response = await click_lead_connect_menu(page)
    if response["status"] == "FAILURE":
        return response

    # Check if there is a Pending button
    pending_button = await page.query_selector('button:has-text("Pending"), a:has-text("Pending")')
    if pending_button:
        return {"status": "SUCCESS", "message": "Connection request is already pending"}

    # Check if there is a Connect button
    connect_button = await page.query_selector('button:has-text("Connect"), a:has-text("Connect")')
    if not connect_button:
        first_degree = await page.query_selector('span:has-text("1st")')
        if first_degree:
            return {"status": "SUCCESS", "message": "User already connected"}
        else:
            return {"status": "FAILURE", "message": "Connect button not found"}

    await connect_button.click()
    await page.wait_for_timeout(2000)

    # Click the Send Invitation button if present
    send_invite_button = await page.query_selector('button:has-text("Send Invitation"), a:has-text("Send Invitation")')
    if not send_invite_button:
        return {"status": "FAILURE", "message": "Send Invitation button not found"}
    await send_invite_button.click()

    return {"status": "SUCCESS", "message": "Connection requested successfully"}

async def view_linkedin_profile(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    if "/sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}
    response = await click_lead_connect_menu(page)
    if response["status"] == "FAILURE":
        return response
    view_linedin_button = await page.query_selector('button:has-text("View LinkedIn profile"), a:has-text("View LinkedIn profile")')
    if not view_linedin_button:
        return {"status": "FAILURE", "message": "Connect button not found"}
    await view_linedin_button.click()
    return {"status": "SUCCESS", "message": "Connection requested successfully"}

async def find_button_by_name(page: Page, button_name: str) -> Any:
    buttons = await page.query_selector_all("button")
    for b in buttons:
        text_content = await b.inner_text()
        if button_name in text_content:
            return b
    return None

async def send_linkedin_message(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)

    if "/sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}

    message_button = await find_button_by_name(page, "Message")
    if not message_button:
        return {"status": "FAILURE", "message": "Message button not found"}
    await message_button.click()
    await page.wait_for_timeout(2000)

    textarea_message = await page.query_selector('textarea[name="message"]')
    if not textarea_message:
        return {"status": "FAILURE", "message": "Message text area not found"}

    message = command_args.get("message", "")
    if message:
        await textarea_message.fill(message)
        await page.wait_for_timeout(2000)
        send_button = await find_button_by_name(page, "Send")
        if not send_button:
            return {"status": "FAILURE", "message": "Message Send button not found"}
        await send_button.click()

    return {"status": "SUCCESS", "message": "Message sent successfully"}

def html_to_text(html_content: str) -> str:
    """Converts HTML content to text using html2text."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    return h.handle(html_content)

async def find_messages_container(page: Page) -> Any:
    section_messages = await page.query_selector('section[data-message-overlay-container]')
    if not section_messages:
        return None
    ul_elements = await section_messages.query_selector_all('ul')
    for ul in ul_elements:
        inner_html = await ul.inner_html()
        if "This is the" in inner_html:
            return ul
    return None

async def get_current_messages(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    if "/sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}
    message_button = await find_button_by_name(page, "Message")
    if not message_button:
        return {"status": "FAILURE", "message": "Message button not found"}
    await message_button.click()
    await page.wait_for_timeout(2000)
    section_messages = await find_messages_container(page)
    if not section_messages:
        return {"status": "FAILURE", "message": "Message container not found"}
    raw_html = await section_messages.inner_html()
    text_messages = html_to_text(raw_html)
    return {
        "status": "SUCCESS",
        "message": "Messages retrieved successfully",
        "data": text_messages
    }

# -----------------------------
# Extraction Helpers
# -----------------------------

async def scroll_to_bottom(page):
    """
    Scrolls to the bottom of the page in a manner similar to the JS code:
      1. If '#search-results-container' is present, scroll it in steps of 500px until the bottom.
      2. Otherwise, move the mouse to the page center-right, wheel-scroll by 1/4 of the total page 
         height, wait, and then return.
    """
    try:
        # Move the mouse roughly to the right-center of the page
        viewport = page.viewport_size
        if viewport is None:
            logger.error("Could not retrieve viewport size, cannot move the mouse.")
            return
        width, height = viewport["width"], viewport["height"]
        x = (width * 3) / 4
        y = height / 2
        await page.mouse.move(x, y)

        container = await page.query_selector("#search-results-container")
        if container:
            logger.info("Found '#search-results-container'. Scrolling within the container.")
            max_scroll_attempts = 10
            scroll_count = 0
            last_scroll_top = -1
            while scroll_count < max_scroll_attempts:
                await container.evaluate("el => el.scrollBy(0, 500)")
                await page.wait_for_timeout(3000)

                scroll_top = await container.evaluate("el => el.scrollTop")
                if scroll_top == last_scroll_top:
                    logger.info("Reached the bottom of '#search-results-container'.")
                    break
                last_scroll_top = scroll_top
                scroll_count += 1
        else:
            doc_height = await page.evaluate("() => document.body.scrollHeight")
            scroll_amount = doc_height // 4
            logger.info("'#search-results-container' not found. Scrolling the page directly by 1/4.")
            await page.mouse.wheel(0, scroll_amount)
            await page.wait_for_timeout(2000)

        logger.info("Completed scrolling.")
    except Exception as e:
        logger.error(f"Failed to execute scroll_to_bottom: {e}")

## Parsing HTML and sending relevant content back to service
def cleanup_html(html_content: str) -> str:
    """
    Cleans up the HTML content by removing <script>, <style>, <svg>, <meta>, <code> tags
    and inline styles/classes. This mimics the JS approach of removing unneeded items.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script, style, svg, meta, code elements
    for tag in soup(["script", "style", "svg", "meta", "code"]):
        tag.decompose()

    # Remove inline style and class attributes
    for attr_tag in soup.select("[style]"):
        del attr_tag["style"]
    for attr_tag in soup.select("[class]"):
        del attr_tag["class"]

    # Convert back to string
    cleaned_html = str(soup)
    return cleaned_html


async def extract_leads_from_current_page(page):
    """
    Extract leads from the current search or list page.
    Mirrors the logic from JS: looks for 'div[data-x-search-result="LEAD"]'
    or 'tr[data-row-id]' in /sales/lists/people pages. Extracts data-anonymize attributes,
    job title / tenure, about / experience, and cleans up the Sales Navigator links
    to match the JS approach (removing everything after the first comma, removing query params).
    """
    # Grab the HTML
    html_content = await page.content()
    cleaned_html = cleanup_html(html_content)

    soup = BeautifulSoup(cleaned_html, "html.parser")
    url = page.url

    # Select the correct DOM elements based on URL
    if "/sales/search/people" in url:
        lead_divs = soup.select('div[data-x-search-result="LEAD"]')
    elif "/sales/lists/people" in url:
        lead_divs = soup.select('tr[data-row-id]')
    else:
        lead_divs = soup.select('div[data-x-search-result="LEAD"]')

    leads = []
    if not lead_divs:
        logger.info("No lead divs found on page.")
        return [], "FAIL"

    for div in lead_divs:
        lead = {}

        # data-anonymize elements
        person_name_el = div.select_one('[data-anonymize="person-name"]')
        title_el = div.select_one('[data-anonymize="title"]')
        location_el = div.select_one('[data-anonymize="location"]')
        job_title_el = div.select_one('[data-anonymize="job-title"]')
        company_name_el = div.select_one('[data-anonymize="company-name"]')

        lead["full_name"] = person_name_el.get_text(strip=True) if person_name_el else ""
        lead["organization_name"] = company_name_el.get_text(strip=True) if company_name_el else ""
        lead["lead_location"] = location_el.get_text(strip=True) if location_el else ""

        # Match the JS logic for job_title vs job_tenure
        if "/sales/search/people" in url:
            lead["job_title"] = title_el.get_text(strip=True) if title_el else ""
            lead["job_tenure"] = job_title_el.get_text(strip=True) if job_title_el else ""
        elif "/sales/lists/people" in url:
            lead["job_title"] = job_title_el.get_text(strip=True) if job_title_el else ""
            lead["job_tenure"] = ""

        # Initialize these if you want placeholders (as in JS)
        lead["user_linkedin_url"] = ""
        lead["organization_linkedin_url"] = ""

        # About / Experience
        dt_elements = div.find_all("dt")
        for dt in dt_elements:
            label = dt.get_text(strip=True).lower()
            dd = dt.find_next_sibling("dd")
            if label == "about:":
                lead["about"] = dd.get_text(strip=True) if dd else ""
            elif label == "experience:":
                if dd:
                    # Join text from child spans
                    spans = dd.find_all("span")
                    lead["experience"] = " ".join(
                        s.get_text(" ", strip=True) for s in spans
                    )
                else:
                    lead["experience"] = ""

        # -- Sales Navigator link extraction (matching the JS approach) --
        lead_link_el = div.select_one('a[href^="/sales/lead/"]')
        if lead_link_el:
            href = lead_link_el.get("href") or ""
            # Example JS logic: match = href.match(/^\/sales\/lead\/([^?]+)/)
            match = re.match(r"^/sales/lead/([^?]+)", href)
            if match:
                linkedin_id = match.group(1)
                # Remove everything after the first comma, if any
                comma_index = linkedin_id.find(",")
                if comma_index != -1:
                    linkedin_id = linkedin_id[:comma_index]
                lead["user_linkedin_salesnav_url"] = f"https://www.linkedin.com/sales/lead/{linkedin_id}"
            else:
                # Fallback if we didn't match or want to keep the full URL
                lead["user_linkedin_salesnav_url"] = f"https://www.linkedin.com{href}"

        company_link_el = div.select_one('a[href^="/sales/company/"]')
        if company_link_el:
            href = company_link_el.get("href") or ""
            # Similar approach for company
            match = re.match(r"^/sales/company/([^?]+)", href)
            if match:
                linkedin_id = match.group(1)
                # Remove everything after the first comma
                comma_index = linkedin_id.find(",")
                if comma_index != -1:
                    linkedin_id = linkedin_id[:comma_index]
                lead["organization_linkedin_salesnav_url "] = f"https://www.linkedin.com/sales/company/{linkedin_id}"
            else:
                lead["organization_linkedin_salesnav_url "] = f"https://www.linkedin.com{href}"

        leads.append(lead)

    if not leads:
        return [], "FAIL"

    return leads, "SUCCESS"


async def extract_lead_from_current_page(page: Page):
    """
    Extract a single lead from a lead's detail page, mirroring the JS code logic 
    from 'encrichLeadWithProfileAndCompanyInfo'. This includes:
      - Clicking the overflow menu button before extraction
      - Parsing user LinkedIn URL via regex
      - Extracting phone, email, experience, education
      - Gathering all data-anonymize elements
    Returns ( [lead_dict], "SUCCESS" ) or ( [], "FAIL" ).
    """

    # 1) Attempt to click the overflow menu button (if it exists).
    button_selector = 'button[data-x--lead-actions-bar-overflow-menu]'
    button = await page.query_selector(button_selector)
    if button:
        await button.click()
        # Wait briefly for the menu's DOM updates to appear
        await page.wait_for_timeout(2000)
    else:
        # Not necessarily a fail; the page might still contain the required data
        # but we can log a warning if desired.
        # logger.warning("Overflow menu not found")
        pass

    # 2) Now extract the page’s content
    html_content = await page.content()
    cleaned_html = cleanup_html(html_content)
    soup = BeautifulSoup(cleaned_html, "html.parser")

    # 4) Regex to match e.g. https://www.linkedin.com/in/johndoe
    profile_regex = r"https:\/\/www\.linkedin\.com\/in\/[a-zA-Z0-9-]+"
    profile_match = re.search(profile_regex, cleaned_html)
    user_linkedin_url = profile_match.group(0) if profile_match else ""

    # 5) Extract key elements
    person_name_el = soup.select_one('[data-anonymize="person-name"]')
    company_name_el = soup.select_one('[data-anonymize="company-name"]')
    phone_el = soup.select_one('[data-anonymize="phone"]')
    email_el = soup.select_one('[data-anonymize="email"]')
    experience_el = soup.select_one('[data-x--lead--experience-section]')
    education_el = soup.select_one('[data-sn-view-name="feature-lead-education"]')

    # 6) Collect any other [data-anonymize] elements
    anonymize_elements = soup.select('[data-anonymize]')
    lead_information = [el.get_text(strip=True) for el in anonymize_elements]

    # 7) Build the lead dictionary
    lead_data = {
        "full_name": person_name_el.get_text(strip=True) if person_name_el else "",
        "organization_name": company_name_el.get_text(strip=True) if company_name_el else "",
        "user_linkedin_url": user_linkedin_url,
        "phone": phone_el.get_text(strip=True) if phone_el else "",
        "email": email_el.get_text(strip=True) if email_el else "",
        "experience": experience_el.get_text(strip=True) if experience_el else "",
        "education": education_el.get_text(strip=True) if education_el else "",
        # or json.dumps(lead_information) if you want a string
        "lead_information": lead_information,  
    }

    # 8) Return the single-lead list
    return [lead_data], "SUCCESS"



async def extract_accounts_from_current_page(page: Page):
    """
    Extract multiple companies (accounts) from the current page.
    Similar approach to extract_leads_from_current_page,
    but adapted for company DOM structure if needed.
    """
    html_content = await page.content()
    cleaned_html = cleanup_html(html_content)
    soup = BeautifulSoup(cleaned_html, "html.parser")

    # Example placeholders:
    accounts = []
    # If LinkedIn's accounts page uses data-x-search-result="COMPANY", then something like:
    company_divs = soup.select('div[data-x-search-result="COMPANY"]')
    for div in company_divs:
        company = {}
        # Parse out company name, location, etc.
        # For example:
        name_el = div.select_one('[data-anonymize="company-name"]')
        company["company_name"] = name_el.get_text(strip=True) if name_el else ""
        # Add more fields here ...
        accounts.append(company)

    if not accounts:
        return [], "FAIL"
    return accounts, "SUCCESS"


async def extract_account_from_current_page(page: Page):
    """
    Extract a single company (account) from an account detail page, mirroring the JS code logic.
    Includes:
      - Locating the 'Visit website' link
      - Collecting data-anonymize properties
    Returns ([company_dict], "SUCCESS") or ([], "FAIL").
    """

    # 1) Attempt to click the overflow menu button (if it exists).
    button_selector = 'button[data-x--account-actions--overflow-menu]'
    button = await page.query_selector(button_selector)
    if button:
        await button.click()
        # Wait briefly for the menu's DOM updates to appear
        await page.wait_for_timeout(2000)
    
    # 2) Check for a button whose innerHTML has the text "Copy LinkedIn.com URL". 
    #    If found, click it, then read from the clipboard.
    copy_linkedin_button = await page.query_selector('button:has-text("Copy LinkedIn.com URL")')
    if copy_linkedin_button:
        await copy_linkedin_button.click()
        # Wait briefly for the clipboard to be updated
        await page.wait_for_timeout(1000)
        copied_text = pyperclip.paste().strip()

    # 3) Get the HTML content and parse it
    html_content = await page.content()
    cleaned_html = cleanup_html(html_content)
    soup = BeautifulSoup(cleaned_html, "html.parser")

    # 4) Check for a required element to validate it's truly a company page
    name_el = soup.select_one('[data-anonymize="company-name"]')
    if not name_el:
        return [], "FAIL"

    # 5) Locate the "Visit website" link (if present).
    #    We'll look for an <a> whose text includes "Visit website" (case-insensitive)
    visit_website_el = soup.find("a", string=lambda text: text and "visit website" in text.lower())
    company_website_url = visit_website_el.get("href", "") if visit_website_el else ""

    # 6) Gather any data-anonymize properties in the page
    anonymize_elements = soup.select('[data-anonymize]')
    company_info = [el.get_text(strip=True) for el in anonymize_elements]

    # 7) Build the company dictionary
    company = {
        "company_name": name_el.get_text(strip=True),
        "company_website_in_linkedin_page": company_website_url,
        "company_info": company_info
    }

    # If we successfully copied the LinkedIn.com URL, place it into the dictionary
    if 'copied_text' in locals() and "linkedin.com/company/" in copied_text:
        company["organization_linkedin_url"] = copied_text

    return [company], "SUCCESS"



async def extract_from_page_with_pagination(page: Page,  command_args: Dict[str, Any]):
    """
    Extracts leads or accounts data from Sales Navigator with pagination.
    Mirrors the JS approach: 
      1) scroll/parse, 
      2) if next button is found & not disabled, click next, 
      3) repeat up to max_pages or until no more data.
    """
    leads_data = []
    current_page = 1
    url = page.url
    max_pages = command_args.get("max_pages", 2)

    while current_page <= max_pages:
        await asyncio.sleep(3)
        logger.info(f"Processing page {current_page}")
        await scroll_to_bottom(page)
        await asyncio.sleep(2)

        if "/sales/search/people" in url or "/sales/lists/people" in url:
            page_items, status = await extract_leads_from_current_page(page)
        elif "/sales/search/company" in url:
            page_items, status = await extract_accounts_from_current_page(page)
        elif "/sales/lead/" in url:
            page_items, status = await extract_lead_from_current_page(page)
        elif "/sales/company/" in url:
            page_items, status = await extract_account_from_current_page(page)
        else:
            logger.warning("URL does not match known patterns. Exiting pagination.")
            break

        if status == "FAIL" or not page_items:
            logger.info("Extraction failed or no items found. Ending pagination.")
            break

        leads_data.extend(page_items)

        # Attempt to click the "Next" button, as in the JS code that checks 'button[aria-label="Next"]'
        try:
            next_buttons = page.locator("button[aria-label='Next']")
            button_count = await next_buttons.count()
        
            if button_count == 0:
                logger.info("Next button not found. End of pagination.")
                break
        
            next_button = next_buttons.first
            if await next_button.is_disabled():
                logger.info("Next button is disabled. End of pagination.")
                break
        
            await next_button.wait_for(state="visible", timeout=2000)
            await next_button.click()
            await page.wait_for_load_state('load')
            current_page += 1
        
        except asyncio.TimeoutError:
            logger.error("Timeout while waiting for the Next button. Ending pagination.")
            break
        except Exception as e:
            logger.error(f"Failed to navigate to next page: {e}")
            break

    return leads_data

async def extract_leads(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    data = await extract_from_page_with_pagination(page, command_args)
    return {
        "status": "SUCCESS",
        "message": "Lead page HTML retrieved",
        "data": data,
    }

async def extract_companies(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    data = await extract_from_page_with_pagination(page, command_args)
    return {
        "status": "SUCCESS",
        "message": "Lead page HTML retrieved",
        "data": data,
    }
    
async def extract_lead(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    if "/sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}
    data = await extract_from_page_with_pagination(page, command_args)
    return {
        "status": "SUCCESS",
        "message": "Lead page HTML retrieved",
        "data": data,
    }

async def extract_company(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    if "/sales/company/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales company page"}
    data = await extract_from_page_with_pagination(page, command_args)
    return {
        "status": "SUCCESS",
        "message": "Company page HTML retrieved",
        "data": data,
    }

async def get_connection_status(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    if "/sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}
    first_degree = await page.query_selector('span:has-text("1st")')
    second_degree = await page.query_selector('span:has-text("2nd")')
    if first_degree:
        connection_status = "1st degree connection"
    elif second_degree:
        connection_status = "2nd degree connection"
    else:
        connection_status = "Not connected"
    return {
        "status": "SUCCESS",
        "message": "Connection status retrieved",
        "data": connection_status,
    }

async def get_activities_of_user(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "SUCCESS", "message": "get_activities_of_user executed"}

async def like_post_on_page(page: Page, command_args: Dict[str, Any]) -> Dict[str, str]:
    try:
        # Wait for the iframe to load
        iframe = await page.wait_for_selector('iframe', timeout=4000)
        if not iframe:
            return {"status": "ERROR", "message": "Iframe not found"}

        # Get the iframe content
        frame = await iframe.content_frame()
        if not frame:
            return {"status": "ERROR", "message": "Iframe content not found"}

        activity_section = await frame.query_selector('.fie-impression-container')
        if not activity_section:
            return {"status": "ERROR", "message": "Activity section not found"}

        facepile_section = await activity_section.query_selector("#reactors-facepile-id")
        if not facepile_section:
            return {"status": "ERROR", "message": "Facepile section not found"}

        facepile_text = await facepile_section.inner_html()
        reaction_count = facepile_text.count("linkedin.com/in/")
        min_reaction_count = command_args.get("min_reaction_count", 5)

        # Check all spans to ensure none have "mo ago" in their inner text
        spans = await frame.query_selector_all('span')
        for span in spans:
            span_text = await span.inner_text()
            if "mo ago" in span_text:
                return {"status": "ERROR", "message": "Post is too old"}

        if reaction_count > min_reaction_count:
            like_button = await frame.query_selector('button[aria-label="React Like"][aria-pressed]')
            if like_button:
                aria_pressed = await like_button.get_attribute('aria-pressed')
                if not aria_pressed or aria_pressed == "false":
                    await like_button.click()

        return {"status": "SUCCESS", "message": "like_post executed"}
    except Exception as e:
        print(f"Exception occurred: {e}")
        return {"status": "ERROR", "message": f"Exception occurred: {e}"}
    

async def like_recent_post(page: Page, command_args: Dict[str, Any]) -> Dict[str, Any]:
    await goto_url(page, command_args)
    if "sales/lead/" not in page.url:
        return {"status": "ERROR", "message": "Not a sales lead page"}

    try:
        activity_button = await find_button_by_name(page, "See all activities")
        if activity_button:
            await activity_button.click()
            await page.wait_for_selector('[aria-labelledby="recent-activity-panel-header"]', timeout=5000)
            await page.wait_for_timeout(4000)
        else:
            return {"status": "FAILURE", "message": "No Activities Button"}

        activity_section = await page.query_selector('[aria-labelledby="recent-activity-panel-header"]')
        if not activity_section:
            return {"status": "ERROR", "message": "Recent activity panel not found"}

        item_button = await activity_section.query_selector('button[data-x--recent-activity-side-panel--item-button]')
        if not item_button:
            return {"status": "ERROR", "message": "Activity item button not found"}
        await item_button.click()
        await page.wait_for_timeout(3000)
        
        react_result = await like_post_on_page(page, command_args)

        return react_result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# Service to do health check.
async def health_check(command_args: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "SUCCESS", "message": "Health check successful"}

command_to_function_mapping = {
    "navigate_to_url": navigate_to_url,
    "view_linkedin_profile": view_linkedin_profile,
    "send_connection_request": send_connection_request,
    "send_linkedin_message": send_linkedin_message,
    "get_current_messages": get_current_messages,
    "extract_leads_information": extract_leads,
    "extract_lead_information": extract_lead,
    "extract_company_information": extract_company,
    "extract_companies_information": extract_companies,
    "get_activities_of_user": get_activities_of_user,
    "like_recent_post": like_recent_post,
    "get_lead_connection_status": get_connection_status,
    "health_check": health_check,
}

# -----------------------------
# Login Helpers
# -----------------------------
async def login_to_linkedin(page: Page, email: str, password: str, headless: bool):
    """
    Logs into LinkedIn using the provided email and password.
    If credentials are not provided, waits for user to log in manually.
    """
    await page.goto("https://www.linkedin.com/uas/login?session_redirect=%2Fsales")
    await page.wait_for_load_state('load')
    
    if email and password:
        await page.get_by_label("Email or Phone").click()
        await page.get_by_label("Email or Phone").fill(email)
        await page.get_by_label("Password").click()
        await page.get_by_label("Password").fill(password)
        await page.locator("#organic-div form").get_by_role("button", name="Sign in", exact=True).click()
        await page.wait_for_load_state('load')
    else:
        logger.info("Waiting for user to log in manually...")
        try:
            await page.wait_for_url(lambda url: url == "https://www.linkedin.com/sales/home", timeout=0)
            logger.info("User logged in successfully.")
        except:
            logger.error("Timeout waiting for user to log in.")
            return 'FAIL'
    
    if "checkpoint/challenge" in page.url:
        if not headless:
            logger.warning("Captcha page encountered! Human intervention is needed.")
            while "checkpoint/challenge" in page.url:
                await asyncio.sleep(5)
                await page.wait_for_load_state('load')
                if "checkpoint/challenge" not in page.url:
                    logger.info("Captcha solved. Continuing with the process.")
                    break
            else:
                logger.error("Captcha not solved. Exiting.")
                return 'FAIL'
            await asyncio.sleep(3)
        else:
            logger.error("Captcha page encountered! Aborting due to headless mode.")
            return 'FAIL'
    
    return 'SUCCESS'




# ------------------------------------------------
# Service Polling & Command Execution (UPDATED)
# ------------------------------------------------
async def poll_service() -> List[Dict[str, Any]]:
    """
    Fetch command(s) from the service for a specific agent_id.
    """
    try:
        # Make sure we pass the agent_id as a query param
        url = f"{SERVICE_URL}/get_agent_tasks?agent_id={AGENT_ID}&api_key={AGENT_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            tasks = response.json()  # expecting a list of tasks
            logger.info(f"Polled {len(tasks)} task(s) from service.")
            return tasks
        else:
            logger.error(f"Failed to poll tasks. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error polling tasks: {e}")
    return []

async def update_agent_health_status(page) -> Dict[str, Any]:
    """
    Update the health status of the agent.
    """
    try:
        # Make sure we pass the agent_id as a query param
        log_status = await ensure_user_is_logged_in(page)
        if log_status:
            status = "LIVE_LOGGED_IN"
        else:
            status = "LIVE_NOT_LOGGED_IN"
        update_url = f"{SERVICE_URL}/update_agent_health?api_key={AGENT_API_KEY}"
        update_response = requests.post(update_url, params={"agent_id": AGENT_ID, "status": status})
        
        if update_response.status_code == 200:
            logger.info(f"Updated agent health status to {status}.")
            return {
                "status": "OK",
                "message": f"Agent health status updated to {status}."
            }
        else:
            logger.error(f"Failed to update agent health status. Status code: {update_response.status_code}")
    except Exception as e:
        logger.error(f"Error updating agent health status: {e}")
    return {
        "status": "ERROR",
        "message": "Failed to update agent health status."
    }
    
async def send_command_result_to_service(command_request_id: str, result: Dict[str, Any]) -> None:
    """
    Send the result of a command execution back to the service.
    """
    try:
        # The service endpoint expects a query param for agent_id and a JSON body
        url = f"{SERVICE_URL}/agent_task_result?agent_id={AGENT_ID}&api_key={AGENT_API_KEY}"
        payload = {
            "command_request_id": command_request_id,
            "result": result
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200 and response.status_code != 201:
            logger.error(f"Failed to send result. Status code: {response.status_code}")
        else:
            logger.info(f"Result for command_request_id={command_request_id} sent successfully.")
    except Exception as e:
        logger.error(f"Error sending command result: {e}")


async def ensure_user_is_logged_in(page: Page) -> bool:
    """
    Checks if user is logged in. If on captcha or login page, 
    waits for user intervention. Returns True if logged in, False otherwise.
    """
    if "checkpoint/challenge" in page.url or "login" in page.url:
        logger.warning("User is not fully logged in or is on a captcha page. Waiting for user intervention...")
        try:
            await page.wait_for_url("https://www.linkedin.com/sales/home", timeout=600_000)
            logger.info("User completed captcha/login process.")
            return True
        except:
            logger.error("User did not finish captcha/login in time.")
            return False
    return True


async def execute_command(page: Page, command_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a single command. Expects structure:
    {
      "command_request_id": "123",
      "command_name": "navigate_to_url",
      "command_args": {"url": "https://www.linkedin.com"},
    }
    """
    command_request_id = command_data.get("command_request_id")
    command_name = command_data.get("command_name")
    command_args = command_data.get("command_args", {})

    if not command_name or command_name not in command_to_function_mapping:
        return {"status": "FAIL", "message": "Invalid command"}

    is_logged_in = await ensure_user_is_logged_in(page)
    if not is_logged_in:
        return {"status": "FAIL", "message": "Not logged in or captcha not solved"}

    command_func = command_to_function_mapping[command_name]
    try:
        logger.info(f"Executing command: {command_name}")
        result = await command_func(page, command_args)
        return result
    except Exception as e:
        logger.error(f"Error executing command {command_name}: {e}")
        return {"status": "FAIL", "message": str(e), "command_request_id": command_request_id}
    
def log_to_journal(task, message):
    log_path = "/tmp/dhisana_ai/sales_nav_logs.log"
    with open(log_path, "a") as lf:
        lf.write(f"{datetime.now().isoformat()} | agent_id: {AGENT_ID} | cmd_id: {task.get('command_request_id', '')} | task: {json.dumps(task)} | message: {message}\n")
        
## Check throttling limits for linked in 
def check_and_update_throttling_limits(task: Dict[str, Any]) -> Dict[str, Any]:
    # Make sure directory exists
    os.makedirs("/tmp/dhisana_ai", exist_ok=True)

    # Logs
    log_to_journal(task, "task request")

    # File and lookup keys
    filepath = "/tmp/dhisana_ai/salesnav_throttlinglimits.json"
    agent_id = AGENT_ID
    cmd_id = task.get("command_name", "")
    today = datetime.now().strftime("%Y-%m-%d")

    # Defined limits
    daily_limits = {
        "send_connection_request": 10,
        "view_linkedin_profile": 500,
        "navigate_to_url": 500,
        "like_recent_post": 10,
        "send_linkedin_message": 10
    }
    limit = daily_limits.get(cmd_id, 25)

    # Load or init data
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        data = {}

    if agent_id not in data:
        data[agent_id] = {}
    if today not in data[agent_id]:
        data[agent_id][today] = {}

    usage = data[agent_id][today].get(cmd_id, 0)
    if usage >= limit:
        return {"status": "ERROR", "message": "Throttling limit reached"}

    # Increment counter
    data[agent_id][today][cmd_id] = usage + 1

    # Keep only last 7 days
    days = sorted(data[agent_id].keys(), reverse=True)
    if len(days) > 7:
        for old_day in days[7:]:
            del data[agent_id][old_day]

    # Save
    with open(filepath, "w") as f:
        json.dump(data, f)

    return {"status": "SUCCESS", "message": "Throttling limits checked"}


async def get_tasks_and_execute(page: Page):
    """
    Continuously polls the service for tasks, executes them, 
    and sends back the result.
    - Wait 30 seconds between polls
    - Wait 10 seconds between each command execution
    """
    while True:
        await update_agent_health_status(page)
        is_user_loggedin = await ensure_user_is_logged_in(page)
        if is_user_loggedin:
            tasks = await poll_service()
            if not tasks:
                logger.info("No tasks found. Will check again in 30 seconds.")
            else:
                logger.info(f"Received {len(tasks)} task(s). Processing...")

            for task_data in tasks:
                # Example task_data structure sent from the service:
                # {
                #   "command_request_id": "123",
                #   "command_name": "navigate_to_url",
                #   "command_args": {"url": "https://www.linkedin.com"},
                # }
                result_throttling = check_and_update_throttling_limits(task_data)
                if result_throttling.get("status") == "SUCCESS":
                    result = await execute_command(page, task_data)
                else:
                    result = result_throttling

                cmd_id = task_data.get("command_request_id", "")
                log_to_journal(task_data, f"task response -- {json.dumps(result)}")
                await send_command_result_to_service(cmd_id, result)

                if result_throttling.get("status") == "SUCCESS":
                    await asyncio.sleep(10)
                else: 
                    break

        await asyncio.sleep(30)


# -----------------------------
# Main Entry Point
# -----------------------------
async def initialize_agent():
    """
    Initializes the Playwright browser and logs in to LinkedIn.
    Then starts the loop to get tasks and execute them.
    """
    global browser, context, page

    email = os.environ.get("LINKEDIN_EMAIL", "")
    password = os.environ.get("LINKEDIN_PASSWORD", "")

    
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Login to LinkedIn
        login_status = await login_to_linkedin(page, email, password, headless=False)
        if login_status == 'FAIL':
            logger.error("Login failed due to captcha or incorrect credentials. Exiting.")
            return

        # After successful login, start the poll-execute loop
        await get_tasks_and_execute(page)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(initialize_agent())



