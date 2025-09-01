# Sales force CRM Tools
# TODO: This needs to be tested and validated like the HubSpot CRM tools.

import json
import os
import requests
from dhisana.utils.assistant_tool_tag import assistant_tool
from simple_salesforce import Salesforce
from urllib.parse import urljoin
from typing import Any, Dict, List, Optional

# Mapping between our internal property names and Salesforce Contact fields
CONTACT_FIELD_MAPPING: Dict[str, str] = {
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "Email",
    "phone": "Phone",
    "job_title": "Title",
    "user_linkedin_url": "LinkedIn_URL__c",
}

# Mapping between our internal property names and Salesforce Account fields
COMPANY_FIELD_MAPPING: Dict[str, str] = {
    "organization_name": "Name",
    "primary_domain_of_organization": "Website",
    "organization_website": "Website",
    "phone": "Phone",
}


def _map_contact_to_internal(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Salesforce contact to our internal schema."""
    account = record.get("Account", {}) or {}
    return {
        "first_name": record.get("FirstName"),
        "last_name": record.get("LastName"),
        "email": record.get("Email"),
        "phone": record.get("Phone"),
        "job_title": record.get("Title"),
        "user_linkedin_url": record.get("LinkedIn_URL__c"),
        "organization_name": account.get("Name"),
        "organization_website": account.get("Website"),
    }


def _map_account_to_internal(record: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Salesforce account to our internal schema."""
    return {
        "organization_name": record.get("Name"),
        "organization_website": record.get("Website"),
        "phone": record.get("Phone"),
        "primary_domain_of_organization": record.get("Website"),
    }


def _create_salesforce_client(tool_config: Optional[List[Dict]] = None) -> Salesforce:
    """Create a Salesforce client from tool_config or environment variables.

    Supports two authentication flows:
      1. Username/password/security token (simple_salesforce default).
      2. OAuth2 password grant using client_id/client_secret.
    The second flow is preferred for production access.

    Raises:
        ValueError: If the Salesforce integration has not been configured.
    """

    username = password = security_token = domain = None
    client_id = client_secret = None

    if tool_config:
        sf_conf = next((c for c in tool_config if c.get("name") == "salesforce"), None)
        if sf_conf:
            cfg_map = {
                item.get("name"): item.get("value")
                for item in sf_conf.get("configuration", [])
                if item
            }
            username = cfg_map.get("username")
            password = cfg_map.get("password")
            security_token = cfg_map.get("security_token")
            domain = cfg_map.get("domain")
            client_id = cfg_map.get("client_id")
            client_secret = cfg_map.get("client_secret")

    username = username or os.getenv("SALESFORCE_USERNAME")
    password = password or os.getenv("SALESFORCE_PASSWORD")
    security_token = security_token or os.getenv("SALESFORCE_SECURITY_TOKEN")
    domain = domain or os.getenv("SALESFORCE_DOMAIN", "login")
    client_id = client_id or os.getenv("SALESFORCE_CLIENT_ID")
    client_secret = client_secret or os.getenv("SALESFORCE_CLIENT_SECRET")

    if not all([username, password, security_token]):
        raise ValueError(
            "Salesforce integration is not configured. Please configure the connection to Salesforce in Integrations."
        )

    # If client credentials are provided, perform OAuth2 password grant
    if client_id and client_secret:
        token_url = f"https://{domain}.salesforce.com/services/oauth2/token"
        try:
            resp = requests.post(
                token_url,
                data={
                    "grant_type": "password",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "username": username,
                    "password": f"{password}{security_token}",
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            access_token = data["access_token"]
            instance_url = data["instance_url"]
            return Salesforce(instance_url=instance_url, session_id=access_token)
        except Exception as e:
            raise ValueError(f"Failed to authenticate with Salesforce: {e}")

    # Fallback to simple_salesforce username/password login
    return Salesforce(
        username=username,
        password=password,
        security_token=security_token,
        domain=domain,
    )

@assistant_tool
async def run_salesforce_crm_query(query: str):
    """
    Executes a Salesforce SOQL query and returns the results as JSON.
    Use this to query Salesforce CRM data like Contacts, Leads, Company etc.

    Parameters:
    query (str): The SOQL query string to execute.

    Returns:
    str: JSON string containing the query results or error message.

    Raises:
    ValueError: If Salesforce credentials are not found.
    ValueError: If the query is empty.
    Exception: If the query fails or returns no results.
    """
    if not query.strip():
        return json.dumps({"error": "The query string cannot be empty"})

    try:
        sf = _create_salesforce_client()

        # Execute the query
        result = sf.query_all(query)
        if not result['records']:
            return json.dumps({"error": "No records found for the provided query"})
    except Exception as e:
        return json.dumps({"error": f"Query failed: {e}"})

    # Return the results as a JSON string
    return json.dumps(result)

@assistant_tool
async def fetch_salesforce_contact_info(contact_id: str = None, email: str = None, tool_config: Optional[List[Dict]] = None):
    """
    Fetch contact information from Salesforce using the contact's Salesforce ID or email.

    Parameters:
    contact_id (str): Unique Salesforce contact ID.
    email (str): Contact's email address.

    Returns:
    dict: JSON response containing contact information.

    Raises:
    ValueError: If Salesforce credentials are not provided or if neither contact_id nor email is provided.
    ValueError: If no contact is found.
    """
    try:
        sf = _create_salesforce_client(tool_config)
    except Exception as e:
        return json.dumps({"error": str(e)})

    if not contact_id and not email:
        return json.dumps({"error": "Either Salesforce contact ID or email must be provided"})

    try:

        if contact_id:
            # Fetch contact by ID
            contact = sf.Contact.get(contact_id)
        else:
            # Sanitize email input
            sanitized_email = email.replace("'", "\\'")
            query = f"""
            SELECT Id, Name, Email, Phone, MobilePhone, Title, Department, MailingAddress, LastActivityDate, LeadSource,
                   Account.Id, Account.Name, Account.Industry, Account.Website, Account.Phone, Account.BillingAddress
            FROM Contact 
            WHERE Email = '{sanitized_email}'
            """
            result = sf.query(query)
            if result['totalSize'] == 0:
                return json.dumps({"error": "No contact found with the provided email"})
            contact = result['records'][0]

        mapped = _map_contact_to_internal(contact)
        return json.dumps(mapped)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch contact information: {e}"})
    

@assistant_tool
async def read_salesforce_list_entries(object_type: str, listview_name: str, entries_count: int, tool_config: Optional[List[Dict]] = None):
    """
    Reads entries from a Salesforce list view and returns the results as JSON.
    Retrieves up to the specified number of entries.

    Parameters:
    object_type (str): The Salesforce object type (e.g., 'Contact').
    listview_name (str): The name of the list view to read from.
    entries_count (int): The number of entries to read.

    Returns:
    str: JSON string containing the list entries or error message.
    """
    if not listview_name.strip() or not object_type.strip():
        return json.dumps({"error": "The object type and list view name cannot be empty"})

    if entries_count <= 0:
        return json.dumps({"error": "Entries count must be a positive integer"})

    try:
        sf = _create_salesforce_client(tool_config)

        # Step 1: Get List View ID
        list_views_url = urljoin(sf.base_url, f"sobjects/{object_type}/listviews")
        list_views_response = sf._call_salesforce('GET', list_views_url)

        if list_views_response.status_code != 200:
            return json.dumps({"error": f"Failed to retrieve list views: {list_views_response.text}"})

        list_views_data = list_views_response.json()
        list_view = next(
            (lv for lv in list_views_data['listviews'] if lv['label'] == listview_name),
            None
        )

        if not list_view:
            return json.dumps({"error": "List view not found"})

        # Step 2: Fetch entries with pagination
        entries_url = urljoin(sf.base_url, list_view['resultsUrl'])
        records = []

        while len(records) < entries_count and entries_url:
            entries_response = sf._call_salesforce('GET', entries_url)
            if entries_response.status_code != 200:
                return json.dumps({"error": f"Failed to retrieve entries: {entries_response.text}"})

            entries_data = entries_response.json()
            entries = entries_data.get('records', [])
            records.extend(entries)

            if len(records) >= entries_count:
                break

            # Check for next page
            next_page_url = entries_data.get('nextPageUrl')
            if next_page_url:
                entries_url = urljoin(sf.base_url, next_page_url)
            else:
                entries_url = None  # No more pages

        # Trim the records to the desired count
        records = records[:entries_count]

        if not records:
            return json.dumps({"error": "No entries found for the specified list view"})

    except Exception as e:
        return json.dumps({"error": f"Query failed: {e}"})

    # Return the results as a JSON string
    return json.dumps(records)


@assistant_tool
async def fetch_salesforce_list_views(object_type: str, tool_config: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    """Return available list views for a Salesforce object."""
    try:
        sf = _create_salesforce_client(tool_config)
        url = urljoin(sf.base_url, f"sobjects/{object_type}/listviews")
        resp = sf._call_salesforce("GET", url)
        if resp.status_code != 200:
            return {"error": resp.text}
        data = resp.json()
        return data.get("listviews", [])
    except Exception as e:
        return {"error": str(e)}


@assistant_tool
async def fetch_salesforce_list_records(
    object_type: str,
    listview_name: str,
    offset: int = 0,
    limit: int = 10,
    tool_config: Optional[List[Dict]] = None,
) -> List[Dict[str, Any]]:
    """Fetch records from a Salesforce list view with offset and limit."""
    try:
        sf = _create_salesforce_client(tool_config)
        url = urljoin(sf.base_url, f"sobjects/{object_type}/listviews")
        lv_resp = sf._call_salesforce("GET", url)
        if lv_resp.status_code != 200:
            return {"error": lv_resp.text}
        lv_data = lv_resp.json()
        list_view = next((lv for lv in lv_data.get("listviews", []) if lv.get("label") == listview_name), None)
        if not list_view:
            return {"error": "List view not found"}
        next_url = urljoin(sf.base_url, list_view["resultsUrl"])
        records: List[Dict[str, Any]] = []
        skipped = 0
        collected = 0
        while next_url and collected < limit:
            resp = sf._call_salesforce("GET", next_url)
            if resp.status_code != 200:
                return {"error": resp.text}
            data = resp.json()
            for rec in data.get("records", []):
                if skipped < offset:
                    skipped += 1
                else:
                    records.append(rec)
                    collected += 1
                    if collected >= limit:
                        break
            next_page = data.get("nextPageUrl")
            next_url = urljoin(sf.base_url, next_page) if next_page else None
        return records
    except Exception as e:
        return {"error": str(e)}


@assistant_tool
async def create_salesforce_contact(properties: Dict[str, Any], tool_config: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Create a contact in Salesforce."""
    try:
        sf = _create_salesforce_client(tool_config)
        result = sf.Contact.create(properties)
        return result
    except Exception as e:
        return {"error": str(e)}


@assistant_tool
async def update_salesforce_contact(contact_id: str, properties: Dict[str, Any], tool_config: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Update an existing Salesforce contact."""
    try:
        sf = _create_salesforce_client(tool_config)
        sf.Contact.update(contact_id, properties)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


def _find_contact_id(
    sf: Salesforce,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Optional[str]:
    """Return the first matching contact ID or None."""
    if email:
        sanitized = email.replace("'", "\\'")
        q = f"SELECT Id FROM Contact WHERE Email = '{sanitized}' LIMIT 1"
    elif first_name and last_name:
        q = (
            "SELECT Id FROM Contact WHERE FirstName = '"
            + first_name.replace("'", "\\'")
            + "' AND LastName = '"
            + last_name.replace("'", "\\'")
            + "' LIMIT 1"
        )
    else:
        return None
    res = sf.query(q)
    return res["records"][0]["Id"] if res.get("records") else None


def _find_account_id(sf: Salesforce, website: Optional[str] = None, name: Optional[str] = None) -> Optional[str]:
    """Return the first matching account ID or None."""
    if website:
        sanitized = website.replace("'", "\\'")
        q = f"SELECT Id FROM Account WHERE Website = '{sanitized}' LIMIT 1"
    elif name:
        sanitized = name.replace("'", "\\'")
        q = f"SELECT Id FROM Account WHERE Name = '{sanitized}' LIMIT 1"
    else:
        return None
    res = sf.query(q)
    return res["records"][0]["Id"] if res.get("records") else None


@assistant_tool
async def update_crm_contact_record_function(
    contact_values: Dict[str, Any],
    is_update: bool,
    salesforce_contact_id: Optional[str] = None,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Create or update a Salesforce contact."""
    try:
        sf = _create_salesforce_client(tool_config)
    except Exception as e:
        return {"error": str(e)}

    properties: Dict[str, Any] = {}
    for k, v in contact_values.items():
        field = CONTACT_FIELD_MAPPING.get(k)
        if field and v is not None:
            properties[field] = v

    if first_name:
        properties.setdefault("FirstName", first_name)
    if last_name:
        properties.setdefault("LastName", last_name)
    if email:
        properties.setdefault("Email", email)

    if is_update:
        cid = salesforce_contact_id or _find_contact_id(sf, email=email, first_name=first_name, last_name=last_name)
        if cid:
            sf.Contact.update(cid, properties)
            return sf.Contact.get(cid)

    result = sf.Contact.create(properties)
    return result


@assistant_tool
async def update_crm_company_record_function(
    company_values: Dict[str, Any],
    is_update: bool,
    salesforce_company_id: Optional[str] = None,
    organization_name: Optional[str] = None,
    organization_website: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Create or update a Salesforce Account."""
    try:
        sf = _create_salesforce_client(tool_config)
    except Exception as e:
        return {"error": str(e)}

    properties: Dict[str, Any] = {}
    for k, v in company_values.items():
        field = COMPANY_FIELD_MAPPING.get(k)
        if field and v is not None:
            properties[field] = v

    if organization_name:
        properties.setdefault("Name", organization_name)
    if organization_website:
        properties.setdefault("Website", organization_website)

    if is_update:
        aid = salesforce_company_id or _find_account_id(sf, website=organization_website, name=organization_name)
        if aid:
            sf.Account.update(aid, properties)
            return sf.Account.get(aid)

    result = sf.Account.create(properties)
    return result

