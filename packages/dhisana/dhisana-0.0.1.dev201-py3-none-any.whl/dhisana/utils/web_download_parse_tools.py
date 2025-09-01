# Tools to download and parse web content.
# Uses plyaWright to fetch HTML content from a URL, parse HTML content as text, and extract structured data from HTML content.

import csv
import logging
import os
from bs4 import BeautifulSoup
import html2text
from playwright.async_api import async_playwright
from dhisana.utils.assistant_tool_tag import assistant_tool
from urllib.parse import urlparse
import re
from datetime import datetime
from dhisana.utils.dataframe_tools import get_structured_output


@assistant_tool
def parse_html_content_as_text(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False  # Keeps links in the markdown
    h.ignore_images = True  # Removes images
    return h.handle(html_content)

@assistant_tool
async def standardize_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
        parsed_url = urlparse(url)
    if parsed_url.hostname and parsed_url.hostname.count('.') == 1:
        url = url.replace(parsed_url.hostname, "www." + parsed_url.hostname)
    return url

@assistant_tool
async def fetch_html_content(url):
    url = await standardize_url(url)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        logging.info(f"Requesting {url}")
        try:
            await page.goto(url, timeout=10000)
            return await page.content()
        except Exception as e:
            logging.info(f"Failed to fetch {url}: {e}")
            return ""
        finally:
            await browser.close()

@assistant_tool
async def get_html_content_from_url(url):
    html_content = await fetch_html_content(url)
    return await clean_html_content(html_content)

@assistant_tool
async def get_text_content_from_url(url):
    html_content = await fetch_html_content(url)
    return await parse_text_content(html_content)

@assistant_tool
async def parse_text_content(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(['script', 'style', 'meta', 'code', 'svg']):
        element.decompose()
    return soup.get_text(separator=' ', strip=True)

@assistant_tool
async def clean_html_content(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(['script', 'style', 'meta', 'code', 'svg']):
        element.decompose()
    return str(soup)

@assistant_tool
async def process_files_in_folder_for_leads(folder_path: str, file_extension: str, response_list_type, response_item_type, output_file: str):
    """
    Process files in a folder, extract structured data, and write to a CSV file using properties from response_item_type.

    Parameters:
    - folder_path (str): The path to the folder containing files.
    - file_extension (str): The file extension to filter files (e.g., '.html').
    - response_list_type: The type of response expected from get_structured_output.
    - response_item_type: The Pydantic model for each item in the response.
    - output_file (str): The path where the output CSV file will be saved.

    Returns:
    - str: The file path of the generated CSV file.
    """

    # Ensure the parent directory of output_file exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Use the properties from response_item_type for headers
    keys = list(response_item_type.__fields__.keys())

    # Open the CSV file in write mode initially to write the header
    with open(output_file, 'w', newline='') as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=keys)
        dict_writer.writeheader()

    # Process each file and append to the CSV file
    for file_name in os.listdir(folder_path):
        if file_name.endswith(file_extension):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                html_content = file.read()
                parsed_content = parse_html_content_as_text(html_content)
                prompt = "Extract structured content from input. Output is in JSON Format. DO NOT make up values. Use what is provided in input. \n\n Input: " + parsed_content
                prompt = prompt[:1040000]  # Limit prompt length to 1040000 characters
                structured_data, result = await get_structured_output(parsed_content, response_list_type)
                if result != 'SUCCESS':
                    logging.warning(f"Failed to extract structured data from {file_name}: {structured_data}")
                    continue
                for item in structured_data.data:
                    # Append each item to the CSV file immediately
                    with open(output_file, 'a', newline='') as csv_file:
                        dict_writer = csv.DictWriter(csv_file, fieldnames=keys)
                        dict_writer.writerow(item.dict())

    return output_file

@assistant_tool
async def process_files_in_folder_for_linkedin_urls(folder_path: str, file_extension: str):
    """
    Process files in a folder, extract LinkedIn URLs, and write to a CSV file.

    Parameters:
    - folder_path (str): The path to the folder containing files.
    - file_extension (str): The file extension to filter files (e.g., '*.html').

    Returns:
    - str: The file path of the generated CSV file.
    """
    linkedin_urls = set()

    for file_name in os.listdir(folder_path):
        if file_name.endswith(file_extension):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    url = link['href']
                    if re.match(r'^https://www\.linkedin\.com/in/[^?]+', url):
                        linkedin_urls.add(url.split('?')[0])  # Remove query parameters

    # Write the LinkedIn URLs to a CSV file
    csv_file_path = os.path.join(folder_path, 'linkedin_urls.csv')
    with open(csv_file_path, 'w', newline='') as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=['id', 'linkedin_url'])
        dict_writer.writeheader()
        for url in linkedin_urls:
            unique_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            dict_writer.writerow({'id': unique_id, 'linkedin_url': url})

    return csv_file_path

@assistant_tool
async def get_lead_urls_from_sales_nav_search_results(folder_path: str, file_extension: str, output_file_path: str):
    linkedin_urls = set()

    for file_name in os.listdir(folder_path):
        if file_name.endswith(file_extension):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    url = link['href']
                    match = re.match(r'^/sales/lead/([^,]+),', url)
                    if match:
                        lead_id = match.group(1)
                        linkedin_urls.add(lead_id)

    # Write the LinkedIn URLs to a CSV file at the output_file_path
    with open(output_file_path, 'w', newline='') as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=['id', 'linkedin_url'])
        dict_writer.writeheader()
        for lead_id in sorted(linkedin_urls):
            linkedin_url = f'https://www.linkedin.com/in/{lead_id}'
            dict_writer.writerow({'id': lead_id, 'linkedin_url': linkedin_url})

    return output_file_path

