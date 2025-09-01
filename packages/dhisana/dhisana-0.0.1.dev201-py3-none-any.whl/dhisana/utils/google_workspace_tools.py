import base64
import csv
import datetime
import io
import json
import logging
import os
import re
import uuid
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from dhisana.schemas.sales import MessageItem
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.email_parse_helpers import *
import asyncio
from dhisana.schemas.common import (SendEmailContext, QueryEmailContext, ReplyEmailContext)


################################################################################
#                               HELPER FUNCTIONS
################################################################################

def get_google_workspace_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the GOOGLE_SERVICE_KEY (base64-encoded JSON) from the provided tool configuration or environment.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The base64-encoded JSON string for the service account credentials.

    Raises:
        ValueError: If the Google Workspace integration has not been configured.
    """
    if tool_config:
        google_workspace_config = next(
            (item for item in tool_config if item.get("name") == "googleworkspace"), None
        )
        if google_workspace_config:
            config_map = {
                item["name"]: item["value"]
                for item in google_workspace_config.get("configuration", [])
                if item
            }
            GOOGLE_SERVICE_KEY = config_map.get("apiKey")
        else:
            GOOGLE_SERVICE_KEY = None
    else:
        GOOGLE_SERVICE_KEY = None

    if not GOOGLE_SERVICE_KEY:
        env_service_key = os.getenv("GOOGLE_SERVICE_KEY")
        if  env_service_key:
            GOOGLE_SERVICE_KEY = base64.b64decode(env_service_key).decode("utf-8")
    if not GOOGLE_SERVICE_KEY:
        raise ValueError(
            "Google Workspace integration is not configured. Please configure the connection to Google Workspace in Integrations."
        )
    return GOOGLE_SERVICE_KEY



def get_google_credentials(
    sender_email: str, 
    scopes: List[str], 
    tool_config: Optional[List[Dict]] = None
):
    """
    Retrieves OAuth2 credentials for a given sender_email (impersonation) and set of scopes.

    Args:
        sender_email (str): The email address to impersonate using domain-wide delegation. 
                            Must be authorized in the service account domain.
        scopes (List[str]): The list of OAuth scopes required.
        tool_config (Optional[List[Dict]]): Tool configuration, if any (used to fetch service key).

    Returns:
        google.oauth2.service_account.Credentials: The credentials object.
    """
    if not sender_email:
        raise ValueError("sender_email is required to impersonate via service account.")

    service_account_json = get_google_workspace_token(tool_config)
    service_account_info = json.loads(service_account_json)

    # Create Credentials object and impersonate the sender_email
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=scopes
    ).with_subject(sender_email)

    # Refresh if needed
    if not credentials.valid:
        request = Request()
        credentials.refresh(request)

    return credentials


    
@assistant_tool
async def send_email_using_service_account_async(
    send_email_context: SendEmailContext,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Asynchronously sends an email using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the sender_email.

    Args:
        send_email_context (SendEmailContext): The context with recipient, subject,
                                               body, sender_name, sender_email, 
                                               and an optional labels list.
        tool_config (Optional[List[Dict]]): Tool configuration for credentials (if any).

    Returns:
        str: The ID of the sent message.
    """
    if not send_email_context.sender_email:
        raise ValueError("sender_email is required to impersonate for sending.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(send_email_context.sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'

    # Construct the MIME text message
    message = MIMEText(send_email_context.body)
    message['to'] = send_email_context.recipient
    message['from'] = f"{send_email_context.sender_name} <{send_email_context.sender_email}>"
    message['subject'] = send_email_context.subject

    # Base64-encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Build the payload (with optional label IDs)
    payload = {
        'raw': raw_message
    }
    if send_email_context.labels:
        payload['labelIds'] = send_email_context.labels

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(gmail_api_url, headers=headers, json=payload)
        response.raise_for_status()
        sent_message = response.json()
    await asyncio.sleep(20)

    return sent_message.get('id', 'No ID returned')




@assistant_tool
async def list_emails_in_time_range_async(
    context: QueryEmailContext,
    tool_config: Optional[List[Dict]] = None
) -> List[MessageItem]:
    """
    Asynchronously lists emails in a given time range using the Gmail API with a service account.
    Returns a list of MessageItem objects, with iso_datetime, and separate sender/receiver fields.
    """
    if context.labels is None:
        context.labels = []

    if not context.sender_email:
        raise ValueError("sender_email is required to impersonate for listing emails.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(context.sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'

    # Convert RFC 3339 times to Unix epoch timestamps for the search query
    start_dt = datetime.datetime.fromisoformat(context.start_time.replace('Z', '+00:00'))
    end_dt = datetime.datetime.fromisoformat(context.end_time.replace('Z', '+00:00'))
    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())

    # Build the search query
    query = f'after:{start_timestamp} before:{end_timestamp}'
    if context.unread_only:
        query += ' is:unread'
    if context.labels:
        label_query = ' '.join([f'label:{lbl}' for lbl in context.labels])
        query += f' {label_query}'

    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': query}

    message_items: List[MessageItem] = []
    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()
        messages = response.json().get('messages', [])

        for msg in messages:
            message_id = msg['id']
            thread_id = msg['threadId']
            message_url = f'{gmail_api_url}/{message_id}'
            message_response = await client.get(message_url, headers=headers)
            message_response.raise_for_status()
            message_data = message_response.json()

            headers_list = message_data['payload']['headers']
            from_header = find_header(headers_list, 'From') or ""
            subject_header = find_header(headers_list, 'Subject') or ""
            date_header = find_header(headers_list, 'Date') or ""

            iso_datetime_str = convert_date_to_iso(date_header)

            # Parse the "From" into (sender_name, sender_email)
            s_name, s_email = parse_single_address(from_header)

            # Parse the recipients
            r_name, r_email = find_all_recipients_in_headers(headers_list)

            msg_item = MessageItem(
                message_id=message_data['id'],                
                thread_id=thread_id,
                sender_name=s_name,
                sender_email=s_email,
                receiver_name=r_name,
                receiver_email=r_email,
                iso_datetime=iso_datetime_str,
                subject=subject_header,
                body=extract_email_body_in_plain_text(message_data)
            )
            message_items.append(msg_item)

    return message_items


################################################################################
#                        GOOGLE DRIVE FILE OPERATIONS
################################################################################

@assistant_tool
async def get_file_content_from_googledrive_by_name(
    file_name: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Searches for a file by name in Google Drive using a service account, downloads it,
    saves it in /tmp with a unique filename, and returns the local file path.

    Args:
        file_name (str): The name of the file to search for in Google Drive.
        sender_email (str): The email address to impersonate. Must have domain-wide delegation set up.
        tool_config (Optional[List[Dict]]): Tool configuration. Contains the service account base64 key if not in env.

    Returns:
        str: Local file path of the downloaded file.

    Raises:
        FileNotFoundError: If no file is found with the given file_name.
        HttpError: If there's an error with the Drive API call.
    """
    if not file_name:
        raise ValueError("file_name must be provided.")

    # Set up credentials
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)

    # Build the Drive service
    service = build('drive', 'v3', credentials=credentials)

    # Search for the file by name
    query = f"name = '{file_name}'"
    results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        raise FileNotFoundError(f"No file found with the name: {file_name}")

    # Get the file ID of the first matching file
    file_id = items[0]['id']
    actual_file_name = items[0]['name']  # Keep original name

    # Create a unique filename by appending a UUID
    unique_filename = f"{uuid.uuid4()}_{actual_file_name}"
    local_file_path = os.path.join('/tmp', unique_filename)

    # Request the file content from Google Drive
    request = service.files().get_media(fileId=file_id)

    with io.FileIO(local_file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logging.info(f"{actual_file_name} Download {int(status.progress() * 100)}%.")

    return local_file_path


@assistant_tool
async def write_content_to_googledrive(
    cloud_file_path: str,
    local_file_path: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Writes content from a local file to a file in Google Drive using a service account.
    If the file does not exist in Google Drive, it creates it along with any necessary
    intermediate directories.

    Args:
        cloud_file_path (str): The path in Drive to create or update, e.g. 'folder/subfolder/file.txt'.
        local_file_path (str): The local file path whose content will be uploaded.
        sender_email (str): The email address to impersonate for domain-wide delegation.
        tool_config (Optional[List[Dict]]): Tool configuration for obtaining service credentials.

    Returns:
        str: The file ID of the uploaded or updated file.

    Raises:
        HttpError: If there's an error with the Drive API calls.
    """
    if not cloud_file_path:
        raise ValueError("cloud_file_path must be provided.")
    if not local_file_path:
        raise ValueError("local_file_path must be provided.")

    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = get_google_credentials(sender_email, SCOPES, tool_config)
        service = build('drive', 'v3', credentials=credentials)

        # Split the cloud file path into components
        path_components = cloud_file_path.strip("/").split('/')
        parent_id = 'root'

        # Create intermediate directories if they don't exist
        for component in path_components[:-1]:
            query = (
                f"'{parent_id}' in parents and name = '{component}' "
                f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            )
            results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
            items = results.get('files', [])
            
            if items:
                parent_id = items[0]['id']
            else:
                file_metadata = {
                    'name': component,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_id]
                }
                folder = service.files().create(body=file_metadata, fields='id').execute()
                parent_id = folder.get('id')

        # Prepare the file for upload
        media_body = MediaFileUpload(local_file_path, resumable=True)
        file_name = path_components[-1]

        # Check if the file exists in the specified directory
        query = f"'{parent_id}' in parents and name = '{file_name}' and trashed = false"
        results = service.files().list(q=query, pageSize=1, fields="files(id, name)").execute()
        items = results.get('files', [])

        if items:
            file_id = items[0]['id']
            service.files().update(fileId=file_id, media_body=media_body).execute()
        else:
            file_metadata = {
                'name': file_name,
                'parents': [parent_id]
            }
            created_file = service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id'
            ).execute()
            file_id = created_file.get('id')

        return file_id

    except HttpError as error:
        raise Exception(f"write_content_to_googledrive An error occurred: {error}")


@assistant_tool
async def list_files_in_drive_folder_by_name(
    folder_path: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> List[str]:
    """
    Lists all files in the given Google Drive folder by folder path.
    If no folder path is provided, it lists files in the root folder.

    Args:
        folder_path (str): The path of the folder in Google Drive (e.g. '/folder/subfolder/').
        sender_email (str): The email address to impersonate for domain-wide delegation.
        tool_config (Optional[List[Dict]]): Tool configuration for obtaining service credentials.

    Returns:
        List[str]: A list of file names in the folder.

    Raises:
        FileNotFoundError: If the folder path is invalid or not found.
        HttpError: If there's an error with the Drive API.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)
    service = build('drive', 'v3', credentials=credentials)

    folder_id = 'root'  # Start from root if folder_path is empty
    folder_path = folder_path or ""

    # Traverse each folder in the path
    folder_names = [name for name in folder_path.strip('/').split('/') if name]
    for folder_name in folder_names:
        query = (
            f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{folder_id}' in parents and trashed = false"
        )
        try:
            results = service.files().list(
                q=query, pageSize=1, fields="files(id, name)"
            ).execute()
            items = results.get('files', [])
            if not items:
                raise FileNotFoundError(
                    f"Folder '{folder_name}' not found under parent folder ID '{folder_id}'"
                )
            folder_id = items[0]['id']
        except HttpError as error:
            raise Exception(f"list_files_in_drive_folder_by_name An error occurred: {error}")

    # Now folder_id is the ID of the desired folder
    # List all files in the specified folder
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query, pageSize=1000, fields="files(id, name)"
        ).execute()
        items = results.get('files', [])
        return [item['name'] for item in items]
    except HttpError as error:
        raise Exception(f"list_files_in_drive_folder_by_name An error occurred: {error}")


################################################################################
#                        GMAIL EMAIL OPERATIONS
################################################################################

class SendEmailContext(BaseModel):
    recipient: str
    subject: str
    body: str
    sender_name: str
    sender_email: str
    labels: Optional[List[str]]
    
@assistant_tool
async def send_email_using_service_account_async(
    send_email_context: SendEmailContext,
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Asynchronously sends an email using the Gmail API with a service account.
    The service account must have domain-wide delegation to impersonate the sender_email.

    Args:
        send_email_context (SendEmailContext): The context with recipient, subject,
                                               body, sender_name, sender_email, 
                                               and an optional labels list.
        tool_config (Optional[List[Dict]]): Tool configuration for credentials (if any).

    Returns:
        str: The ID of the sent message.
    """
    if not send_email_context.sender_email:
        raise ValueError("sender_email is required to impersonate for sending.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(send_email_context.sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send'

    # Construct the MIME text message
    message = MIMEText(send_email_context.body)
    message['to'] = send_email_context.recipient
    message['from'] = f"{send_email_context.sender_name} <{send_email_context.sender_email}>"
    message['subject'] = send_email_context.subject

    # Base64-encode the message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Build the payload (with optional label IDs)
    payload = {
        'raw': raw_message
    }
    if send_email_context.labels:
        payload['labelIds'] = send_email_context.labels

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(gmail_api_url, headers=headers, json=payload)
        response.raise_for_status()
        sent_message = response.json()
    await asyncio.sleep(20)

    return sent_message.get('id', 'No ID returned')



class QueryEmailContext(BaseModel):
    start_time: str
    end_time: str
    sender_email: str
    unread_only: bool = True
    labels: Optional[List[str]] = None


@assistant_tool
async def list_emails_in_time_range_async(
    context: QueryEmailContext,
    tool_config: Optional[List[Dict]] = None
) -> List[MessageItem]:
    """
    Asynchronously lists emails in a given time range using the Gmail API with a service account.
    Returns a list of MessageItem objects, with iso_datetime, and separate sender/receiver fields.
    """
    if context.labels is None:
        context.labels = []

    if not context.sender_email:
        raise ValueError("sender_email is required to impersonate for listing emails.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(context.sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'

    # Convert RFC 3339 times to Unix epoch timestamps for the search query
    start_dt = datetime.datetime.fromisoformat(context.start_time.replace('Z', '+00:00'))
    end_dt = datetime.datetime.fromisoformat(context.end_time.replace('Z', '+00:00'))
    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())

    # Build the search query
    query = f'after:{start_timestamp} before:{end_timestamp}'
    if context.unread_only:
        query += ' is:unread'
    if context.labels:
        label_query = ' '.join([f'label:{lbl}' for lbl in context.labels])
        query += f' {label_query}'

    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': query}

    message_items: List[MessageItem] = []
    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()
        messages = response.json().get('messages', [])

        for msg in messages:
            message_id = msg['id']
            thread_id = msg['threadId']
            message_url = f'{gmail_api_url}/{message_id}'
            message_response = await client.get(message_url, headers=headers)
            message_response.raise_for_status()
            message_data = message_response.json()

            headers_list = message_data['payload']['headers']
            from_header = find_header(headers_list, 'From') or ""
            subject_header = find_header(headers_list, 'Subject') or ""
            date_header = find_header(headers_list, 'Date') or ""

            iso_datetime_str = convert_date_to_iso(date_header)

            # Parse the "From" into (sender_name, sender_email)
            s_name, s_email = parse_single_address(from_header)

            # Parse the recipients
            r_name, r_email = find_all_recipients_in_headers(headers_list)

            msg_item = MessageItem(
                message_id=message_data['id'],                
                thread_id=thread_id,
                sender_name=s_name,
                sender_email=s_email,
                receiver_name=r_name,
                receiver_email=r_email,
                iso_datetime=iso_datetime_str,
                subject=subject_header,
                body=extract_email_body_in_plain_text(message_data)
            )
            message_items.append(msg_item)

    return message_items


@assistant_tool
async def fetch_last_n_sent_messages(
    recipient_email: str,
    num_messages: int,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> List[MessageItem]:
    """
    Fetch the last n messages sent to a specific recipient using the Gmail API with a service account.
    Returns a list of MessageItem objects with separate sender_name/sender_email, etc.
    """
    if not sender_email:
        raise ValueError("sender_email is required to impersonate for fetching sent messages.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
    query = f'to:{recipient_email}'

    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': query, 'maxResults': num_messages}

    message_items: List[MessageItem] = []
    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()
        messages = response.json().get('messages', [])

        for message in messages:
            message_id = message['id']
            message_url = f'{gmail_api_url}/{message_id}'
            msg_response = await client.get(message_url, headers=headers)
            msg_response.raise_for_status()
            message_data = msg_response.json()

            headers_list = message_data['payload']['headers']
            from_header = find_header(headers_list, 'From') or ""
            subject_header = find_header(headers_list, 'Subject') or ""
            date_header = find_header(headers_list, 'Date') or ""
            iso_datetime_str = convert_date_to_iso(date_header)

            # Parse "From"
            s_name, s_email = parse_single_address(from_header)
            # Parse the recipients
            r_name, r_email = find_all_recipients_in_headers(headers_list)

            msg_item = MessageItem(
                message_id=message_data['id'],
                thread_id=message_data['threadId'],
                sender_name=s_name,
                sender_email=s_email,
                receiver_name=r_name,
                receiver_email=r_email,
                iso_datetime=iso_datetime_str,
                subject=subject_header,
                body=extract_email_body_in_plain_text(message_data)
            )
            message_items.append(msg_item)

    return message_items


@assistant_tool
async def fetch_last_n_received_messages(
    sender_filter_email: str,
    num_messages: int,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> List[MessageItem]:
    """
    Fetch the last n messages received from a specific sender using the Gmail API with a service account.
    Returns a list of MessageItem objects.
    """
    if not sender_email:
        raise ValueError("sender_email is required to impersonate for fetching received messages.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
    query = f'from:{sender_filter_email}'

    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': query, 'maxResults': num_messages}

    message_items: List[MessageItem] = []
    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()
        messages = response.json().get('messages', [])

        for message in messages:
            message_id = message['id']
            message_url = f'{gmail_api_url}/{message_id}'
            msg_response = await client.get(message_url, headers=headers)
            msg_response.raise_for_status()
            message_data = msg_response.json()

            headers_list = message_data['payload']['headers']
            from_header = find_header(headers_list, 'From') or ""
            subject_header = find_header(headers_list, 'Subject') or ""
            date_header = find_header(headers_list, 'Date') or ""
            iso_datetime_str = convert_date_to_iso(date_header)

            # Parse "From"
            s_name, s_email = parse_single_address(from_header)
            # Parse the recipients
            r_name, r_email = find_all_recipients_in_headers(headers_list)

            msg_item = MessageItem(
                message_id=message_data['id'],
                thread_id=message_data['threadId'],
                sender_name=s_name,
                sender_email=s_email,
                receiver_name=r_name,
                receiver_email=r_email,
                iso_datetime=iso_datetime_str,
                subject=subject_header,
                body=extract_email_body_in_plain_text(message_data)
            )
            message_items.append(msg_item)

    return message_items


@assistant_tool
async def get_email_details_async(
    message_id: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> MessageItem:
    """
    Asynchronously retrieves the full details of an email using the Gmail API with a service account.
    Returns a single MessageItem with separate sender_name/sender_email, etc.
    """
    if not sender_email:
        raise ValueError("sender_email is required to impersonate for fetching email details.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'format': 'full'}

    async with httpx.AsyncClient() as client:
        response = await client.get(gmail_api_url, headers=headers, params=params)
        response.raise_for_status()
        message_data = response.json()

    headers_list = message_data['payload']['headers']
    from_header = find_header(headers_list, 'From') or ""
    subject_header = find_header(headers_list, 'Subject') or ""
    date_header = find_header(headers_list, 'Date') or ""
    iso_datetime_str = convert_date_to_iso(date_header)

    # Parse "From"
    s_name, s_email = parse_single_address(from_header)
    # Parse the recipients
    r_name, r_email = find_all_recipients_in_headers(headers_list)

    msg_item = MessageItem(
        message_id=message_data['id'],
        thread_id=message_data['threadId'],
        sender_name=s_name,
        sender_email=s_email,
        receiver_name=r_name,
        receiver_email=r_email,
        iso_datetime=iso_datetime_str,
        subject=subject_header,
        body=extract_email_body_in_plain_text(message_data)
    )

    return msg_item



@assistant_tool
async def reply_to_email_async(
    reply_email_context: ReplyEmailContext,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Asynchronously replies to an email with "Reply-All" semantics using the Gmail API and a service account.
    The service account must have domain-wide delegation to impersonate the sender_email.

    Args:
        context (ReplyEmailContext): The context with message_id, reply_body, sender_email, sender_name,
                                     mark_as_read, and add_labels.
        tool_config (Optional[List[Dict]]): Tool configuration for credentials.

    Returns:
        Dict[str, Any]: A dictionary containing the details of the sent message.
    """
    if reply_email_context.add_labels is None:
        reply_email_context.add_labels = []

    if not reply_email_context.sender_email:
        raise ValueError("sender_email is required to impersonate for replying to an email.")

    SCOPES = ['https://mail.google.com/']
    credentials = get_google_credentials(reply_email_context.sender_email, SCOPES, tool_config)
    access_token = credentials.token

    gmail_api_base_url = 'https://gmail.googleapis.com/gmail/v1/users/me'
    get_message_url = f'{gmail_api_base_url}/messages/{reply_email_context.message_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {'format': 'full'}

    # 1. Retrieve original message
    async with httpx.AsyncClient() as client:
        response = await client.get(get_message_url, headers=headers, params=params)
        response.raise_for_status()
        original_message = response.json()

    headers_list = original_message.get('payload', {}).get('headers', [])
    headers_dict = {h['name']: h['value'] for h in headers_list}
    thread_id = original_message.get('threadId')

    # 2. Prepare reply headers
    subject = headers_dict.get('Subject', '')
    if not subject.startswith('Re:'):
        subject = f'Re: {subject}'

    to_addresses = headers_dict.get('From', '')
    cc_addresses = headers_dict.get('Cc', '')
    message_id_header = headers_dict.get('Message-ID', '')

    # 3. Create the reply email message
    msg = MIMEText(reply_email_context.reply_body)
    msg['To'] = to_addresses
    if cc_addresses:
        msg['Cc'] = cc_addresses
    msg['From'] = f"{reply_email_context.sender_name} <{reply_email_context.sender_email}>"
    msg['Subject'] = subject
    msg['In-Reply-To'] = message_id_header
    msg['References'] = message_id_header

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    payload = {
        'raw': raw_message,
        'threadId': thread_id
    }

    # 4. Send the reply
    send_message_url = f'{gmail_api_base_url}/messages/send'
    async with httpx.AsyncClient() as client:
        response = await client.post(send_message_url, headers=headers, json=payload)
        response.raise_for_status()
        sent_message = response.json()

    # 5. (Optional) Mark the thread as read
    if reply_email_context.mark_as_read.lower() == "true":
        modify_thread_url = f'{gmail_api_base_url}/threads/{thread_id}/modify'
        modify_payload = {'removeLabelIds': ['UNREAD']}
        async with httpx.AsyncClient() as client:
            response = await client.post(modify_thread_url, headers=headers, json=modify_payload)
            response.raise_for_status()

    # 6. (Optional) Add labels
    if reply_email_context.add_labels:
        modify_thread_url = f'{gmail_api_base_url}/threads/{thread_id}/modify'
        modify_payload = {'addLabelIds': reply_email_context.add_labels}
        async with httpx.AsyncClient() as client:
            response = await client.post(modify_thread_url, headers=headers, json=modify_payload)
            response.raise_for_status()

    # Build a response object
    sent_message_details = {
        "mailbox_email_id": sent_message['id'],
        "message_id": sent_message['threadId'],
        "email_subject": subject,
        "email_sender": reply_email_context.sender_email,
        "email_recipients": [to_addresses] + ([cc_addresses] if cc_addresses else []),
        "read_email_status": 'READ' if reply_email_context.mark_as_read.lower() == "true" else 'UNREAD',
        "email_labels": sent_message.get('labelIds', [])
    }

    return sent_message_details


################################################################################
#                      GOOGLE CALENDAR EVENT OPERATIONS
################################################################################

@assistant_tool
async def get_calendar_events_using_service_account_async(
    start_date: str,
    end_date: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Asynchronously retrieves a list of events from a user's Google Calendar using a service account.
    The service account must have domain-wide delegation to impersonate the user (sender_email).
    Events are filtered based on the provided start and end date range.

    Args:
        start_date (str): The start date (inclusive) to filter events. Format: 'YYYY-MM-DD'.
        end_date (str): The end date (exclusive) to filter events. Format: 'YYYY-MM-DD'.
        sender_email (str): The mailbox email to impersonate for domain-wide delegation.
        tool_config (Optional[List[Dict]]): Tool configuration for credentials.

    Returns:
        List[Dict[str, Any]]: A list of calendar events within the specified date range.

    Raises:
        httpx.HTTPError, Google-related errors for any issues with the API.
    """
    if not sender_email:
        raise ValueError("sender_email is required to impersonate for calendar events.")

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)
    access_token = credentials.token

    calendar_api_url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'

    # Convert start and end dates to ISO 8601 format with time
    start_datetime = f'{start_date}T00:00:00Z'  # UTC format
    end_datetime = f'{end_date}T23:59:59Z'     # UTC format

    params = {
        'timeMin': start_datetime,
        'timeMax': end_datetime,
        'maxResults': 10,
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    headers = {'Authorization': f'Bearer {access_token}'}

    async with httpx.AsyncClient() as client:
        response = await client.get(calendar_api_url, params=params, headers=headers)
        response.raise_for_status()
        events_result = response.json()

    events = events_result.get('items', [])

    if not events:
        logging.info('No upcoming events found within the specified range.')
    else:
        logging.info('Upcoming events:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            logging.info(f"{start} - {event.get('summary', 'No Title')}")

    return events

def get_google_sheet_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the Google Sheets API key from the provided tool configuration or
    the environment variable ``GOOGLE_SHEETS_API_KEY``.

    Raises:
        ValueError: If the Google Sheets integration has not been configured.
    """
    GOOGLE_SHEETS_API_KEY = None
    if tool_config:
        google_sheet_config = next(
            (item for item in tool_config if item.get("name") == "google_sheets"), None
        )
        if google_sheet_config:
            config_map = {
                item["name"]: item["value"]
                for item in google_sheet_config.get("configuration", [])
                if item
            }
            GOOGLE_SHEETS_API_KEY = config_map.get("apiKey")

    GOOGLE_SHEETS_API_KEY = GOOGLE_SHEETS_API_KEY or os.getenv("GOOGLE_SHEETS_API_KEY")
    if not GOOGLE_SHEETS_API_KEY:
        raise ValueError(
            "Google Sheets integration is not configured. Please configure the connection to Google Sheets in Integrations."
        )
    return GOOGLE_SHEETS_API_KEY

def get_sheet_id_from_url(sheet_url: str) -> str:
    """
    Extract the spreadsheet ID from a typical Google Sheets URL.
    Example URL format:
        https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=0
    """
    # Regex to capture spreadsheet ID between '/d/' and the next '/'
    match = re.search(r"/d/([a-zA-Z0-9-_]+)/", sheet_url)
    if not match:
        raise ValueError("Could not extract spreadsheet ID from the provided URL.")
    return match.group(1)


def get_document_id_from_url(doc_url: str) -> str:
    """Extract the document ID from a typical Google Docs URL.

    Example URL format:
        https://docs.google.com/document/d/<DOCUMENT_ID>/edit
    """
    match = re.search(r"/d/([a-zA-Z0-9-_]+)/", doc_url)
    if not match:
        raise ValueError("Could not extract document ID from the provided URL.")
    return match.group(1)

async def read_google_sheet_with_api_token(
    sheet_url: str,
    range_name: str,
    sender_email: str,               # kept for signature compatibility – not used
    tool_config: Optional[List[Dict]] = None
) -> List[List[str]]:
    """
    Read data from a *public* Google Sheet (shared “Anyone with the link → Viewer”)
    using an API key instead of OAuth credentials.
    """

    # 1️⃣ Spreadsheet ID from the URL
    spreadsheet_id = get_sheet_id_from_url(sheet_url)

    # 2️⃣ Grab the API key (tool_config ➜ googlesheet › apiKey, or env var)
    api_key = get_google_sheet_token(tool_config)

    # 3️⃣ Build the Sheets service with the key
    service = build("sheets", "v4", developerKey=api_key)
    sheet   = service.spreadsheets()

    # 4️⃣ Default range to the first sheet if none supplied
    if not range_name:
        metadata  = sheet.get(spreadsheetId=spreadsheet_id).execute()
        range_name = metadata["sheets"][0]["properties"]["title"]

    # 5️⃣ Fetch the values
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    return result.get("values", [])


async def read_google_sheet(
    sheet_url: str,
    range_name: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None
) -> List[List[str]]:
    """
    Read data from a Google Sheet using a service account.
    
    Args:
        sheet_url (str): Full URL of the Google Sheet.
        range_name (str): Range to read from, e.g. 'Sheet1!A1:Z'.
        sender_email (str): The email address to impersonate. Must have domain-wide delegation set up.
        tool_config (Optional[List[Dict]]): Tool configuration for credentials.
    
    Returns:
        List[List[str]]: A list of rows, each row is a list of cell values.
    
    Raises:
        HttpError: If there's an error calling the Sheets API.
    """

    # --- 1. Extract Spreadsheet ID from URL ---
    spreadsheet_id = get_sheet_id_from_url(sheet_url)

    # --- 2. Set up credentials ---
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)
    
    # --- 3. Build the Sheets service ---
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # If no range_name provided, default to the first sheet
        if not range_name:
            metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
            range_name = metadata['sheets'][0]['properties']['title']

        # --- 4. Call the Sheets API ---
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        return values

    except HttpError as e:
        logging.error(f"An error occurred while reading the Google Sheet: {e}")
        raise


async def read_google_document(
    doc_url: str,
    sender_email: str,
    tool_config: Optional[List[Dict]] = None,
) -> str:
    """Read text content from a Google Doc using a service account.

    Args:
        doc_url (str): Full URL of the Google Document.
        sender_email (str): The email address to impersonate.
        tool_config (Optional[List[Dict]]): Tool configuration for credentials.

    Returns:
        str: The concatenated text content of the document.

    Raises:
        HttpError: If there's an error calling the Docs API.
    """

    # --- 1. Extract Document ID from URL ---
    document_id = get_document_id_from_url(doc_url)

    # --- 2. Set up credentials ---
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    credentials = get_google_credentials(sender_email, SCOPES, tool_config)

    # --- 3. Build the Docs service and fetch the document ---
    try:
        service = build('docs', 'v1', credentials=credentials)
        document = service.documents().get(documentId=document_id).execute()

        content = document.get('body', {}).get('content', [])
        text_parts: List[str] = []
        for element in content:
            paragraph = element.get('paragraph')
            if not paragraph:
                continue
            for elem in paragraph.get('elements', []):
                text_run = elem.get('textRun')
                if text_run:
                    text_parts.append(text_run.get('content', ''))

        return ''.join(text_parts)

    except HttpError as e:
        logging.error(f"An error occurred while reading the Google Document: {e}")
        raise

def save_values_to_csv(values: List[List[str]], output_filename: str) -> str:
    """
    Saves a list of row values (list of lists) to a CSV file.
    
    Args:
        values (List[List[str]]): Data to write to CSV.
        output_filename (str): CSV file name.
    
    Returns:
        str: The path to the created CSV file.
    """
    # Create a unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4()}_{output_filename}"
    local_file_path = os.path.join('/tmp', unique_filename)

    # Write rows to CSV
    with open(local_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(values)

    return local_file_path

