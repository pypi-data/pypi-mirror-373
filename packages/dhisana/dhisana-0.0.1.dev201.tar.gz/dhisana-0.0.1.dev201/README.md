# Dhisana Python SDK

A Python SDK for interacting with Dhisana AI services.

## Installation

```bash
pip install dhisana
```

## Usage

```python
from dhisana.utils.agent_tools import (
    search_google_maps,
    enrich_people_with_apollo,
    search_google,
    search_google_jobs,
    search_google_news,
    get_html_content_from_url,
    parse_html_content,
    extract_image_links,
    extract_head_section_from_html_content,
    get_email_if_exists,
    search_crunchbase,
    search_people_with_apollo,
    search_companies_with_apollo,
    enrich_company_with_apollo,
    get_job_postings_from_apollo
)
# Your code here
```

## Steps to Create and Publish the Package

### Ensure you have the latest versions of setuptools and wheel

```bash
pip install --upgrade setuptools wheel
```

### Build the Package

```bash
pip install .
```

### Upload to PyPI

First, install twine:

```bash
pip install --upgrade build twine
python -m build
pip install twine
```

### Then upload your package (you'll need a PyPI account)

```bash
twine upload dist/\*
```

### Install the Package Locally for Testing

You can install the package locally to test it before uploading:

```bash
pip install -e .
```

The -e flag installs the package in editable mode, which is useful during development.

## Run Tests

```bash
pip install pytest
pytest tests/
```

### Using the Package in Other Projects

Once your package is published to PyPI, other users can install it using:

```bash
pip install dhisana
```

They can then import your SDK as:

```bash
from dhisana.utils.agent_tools import (
    search_google_maps,
    enrich_people_with_apollo,
    search_google,
    search_google_jobs,
    search_google_news,
    get_html_content_from_url,
    parse_html_content,
    extract_image_links,
    extract_head_section_from_html_content,
    get_email_if_exists,
    search_crunchbase,
    search_people_with_apollo,
    search_companies_with_apollo,
    enrich_company_with_apollo,
    get_job_postings_from_apollo
)

# Use the functionalities provided by your SDK
```

### To use locally

```bash
pip install -e /path/to/other/project
```

### To use CLI

You can use the CLI provided by the Dhisana AI SDK. To see the available commands and options, use:

```bash
dhisana --help
```

This will display:

```bash
Usage: dhisana [OPTIONS] COMMAND [ARGS]...

    Dhisana AI SDK CLI.

Options:
    --help  Show this message and exit.

Commands:
    dataset-cli     Commands for managing datasets.
    model-cli       Commands for managing models.
    prediction-cli  Commands for running predictions.
```

## Proxycurl Job Leads Example

Set `PROXY_CURL_API_KEY` in your environment before running functions that call Proxycurl.

```bash
export PROXY_CURL_API_KEY=your_api_key
```

Example usage to search for SDR roles and retrieve hiring manager leads:

```python
import asyncio
from dhisana.utils.proxy_curl_tools import find_leads_by_job_openings_proxy_curl

async def main():
    leads = await find_leads_by_job_openings_proxy_curl(
        {"job_title": "SDR", "location": "United States"},
        hiring_manager_roles=["VP of Sales", "Head of Sales"],
    )
    print(leads)

asyncio.run(main())
```

## Proxycurl Job Search Example

Use `proxycurl_job_search` to list jobs posted by a company. Parameters mirror
Proxycurl's job search endpoint.

### Parameters

- `job_type` – one of `full-time`, `part-time`, `contract`, `internship`,
  `temporary`, `volunteer`, or `anything`.
- `experience_level` – `internship`, `entry_level`, `associate`,
  `mid_senior_level`, `director`, or `anything`.
- `when` – posted time such as `yesterday`, `past-week`, `past-month`, or
  `anytime`.
- `flexibility` – `remote`, `on-site`, `hybrid`, or `anything`.
- `geo_id` – location identifier, e.g. `92000000` for worldwide.
- `keyword` – keyword to match in the job title.
- `search_id` – company search identifier from the Company Profile API.

Example usage:

```python
import asyncio
from dhisana.utils.proxycurl_search_leads import JobSearchParams, proxycurl_job_search

async def main():
    jobs = await proxycurl_job_search(
        JobSearchParams(
            search_id="2790400",
            keyword="engineer",
            job_type="full-time",
            experience_level="mid_senior_level",
            when="past-month",
            flexibility="remote",
            geo_id=92000000,
        ),
        max_entries=2,
    )
    print(jobs)

asyncio.run(main())
```

## Proxycurl Get Company Search ID Example

Use `proxycurl_get_company_search_id` to retrieve a company's search ID, which is required for other Proxycurl operations like job searches. This function calls Proxycurl's Company Profile endpoint.

### Function Parameters

- `company_url` – LinkedIn company profile URL (e.g., `https://www.linkedin.com/company/microsoft/`)
- `tool_config` – Optional tool configuration containing API key

### Return Value

Returns a dictionary with:

- `search_id` – The company's search ID (required for job operations)
- `name` – Company name
- `linkedin_internal_id` – LinkedIn's internal company ID
- `industry` – Company industry
- `company_url` – The original URL provided
- `error` – Error message (if any errors occurred)

Example usage:

```python
import asyncio
from dhisana.utils.proxycurl_search_leads import (
    proxycurl_get_company_search_id,
    proxycurl_job_count,
    JobSearchParams
)

async def main():
    # Get company search ID
    company_result = await proxycurl_get_company_search_id(
        "https://www.linkedin.com/company/microsoft/"
    )

    if company_result.get("search_id"):
        print(f"Company: {company_result['name']}")
        print(f"Search ID: {company_result['search_id']}")

        # Use the search ID for job operations
        job_params = JobSearchParams(search_id=company_result["search_id"])
        job_count = await proxycurl_job_count(job_params)
        print(f"Total jobs: {job_count.get('count', 0)}")
    else:
        print(f"Error: {company_result.get('error')}")

asyncio.run(main())
```
