from typing import Any, Dict
import base64
import re

def decode_base64(data: str) -> str:
    """
    Decode a base64- or web-safe-base64-encoded string.
    """
    if not data:
        return ""
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

def html_to_text(html: str) -> str:
    """
    (Optional) Convert HTML to plain text using a simple regex.
    This is not bulletproof for all HTML, but often fine for short email bodies.
    """
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)     # <br> to newline
    text = re.sub(r'<.*?>', '', text)                                # remove remaining tags
    return text.strip()

def get_text_content(payload: Dict[str, Any]) -> str:
    """
    Recursively extract 'text/plain' content from the Gmail message payload.
    If no text/plain is found, fallback to 'text/html' (converted to plain text).
    """
    # If there's a direct 'parts' list, we may need to walk each part.
    if 'parts' in payload:
        extracted = []
        for part in payload['parts']:
            extracted.append(get_text_content(part))
        return "\n".join(filter(None, extracted))
    
    # If this part has a mimeType and a body, try to decode.
    mime_type = payload.get('mimeType', '')
    body_data = payload.get('body', {}).get('data', '')
    
    # If it's text/plain, decode base64 and return
    if mime_type == 'text/plain' and body_data:
        return decode_base64(body_data)
    
    # If it's text/html (and we haven't returned text/plain yet), fallback
    if mime_type == 'text/html' and body_data:
        html_content = decode_base64(body_data)
        return html_to_text(html_content)
    
    return ""

def trim_repeated_quoted_lines(text: str) -> str:
    """
    (Optional) Try to remove repeated or quoted content from replies.
    This is a naive approach—real-world heuristics can get quite complicated.
    """
    # Common patterns: lines starting with ">"
    # or lines starting with "On <date>, <someone> wrote:"
    lines = text.splitlines()
    filtered_lines = []
    for line in lines:
        if line.startswith(">"):
            continue
        # You can add more heuristics for removing signature blocks or repeated disclaimers
        filtered_lines.append(line)
    return "\n".join(filtered_lines).strip()

def extract_email_content_for_llm(email_details: Dict[str, Any]) -> str:
    """
    Cleans up, extracts, and formats the relevant text content from a single Gmail message.
    If you want the entire thread, call the Gmail API for all messages in the thread and
    combine them. This function handles one message in detail, recursively extracting
    text from multiple MIME parts.
    """
    if not email_details or 'payload' not in email_details:
        return "No valid email details found."

    # Extract basic headers
    headers_map = {h['name']: h['value'] for h in email_details['payload'].get('headers', [])}
    
    sender = headers_map.get('From', 'Unknown Sender')
    receiver = headers_map.get('To', 'Unknown Receiver')
    date = headers_map.get('Date', 'Unknown Date')
    subject = headers_map.get('Subject', 'No Subject')
    
    # Recursively get text from payload
    body = get_text_content(email_details['payload'])
    
    # Optionally remove some repeated lines
    body = trim_repeated_quoted_lines(body)
    
    # Format final string
    formatted_content = (
        f"From: {sender}\n"
        f"To: {receiver}\n"
        f"Date: {date}\n"
        f"Subject: {subject}\n\n"
        f"{body}"
    )
    
    return formatted_content
