import uuid
from typing import List
from datetime import datetime, date
from dhisana.schemas.sales import MessageItem

DAY_NAMES = {
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday"
}

def is_day_line(line: str) -> bool:
    """Check if line is a simple day name (case-insensitive)."""
    return line.strip().lower() in DAY_NAMES

def parse_time_line(time_str: str) -> str:
    """
    Parse a time string like "6:38 PM" or "14:10" using today's date,
    returning an ISO8601 string. Returns an empty string if it fails.
    """
    today_str = date.today().strftime("%Y-%m-%d")
    for fmt in ["%I:%M %p", "%H:%M"]:
        try:
            dt = datetime.strptime(f"{today_str} {time_str}", f"%Y-%m-%d {fmt}")
            return dt.isoformat()
        except ValueError:
            pass
    return ""  # If we can’t parse it, return empty


def parse_conversation(conversation_text: str) -> List[MessageItem]:
    """
    Given raw text containing lines like:
      'Load more'
      'Thursday'
      'You'
      '6:38 PM'
      'Hello, ...'
    Parse them into MessageItems with empty subject/email,
    and return a list sorted from latest (top) to oldest (bottom).
    """
    # Split lines, remove empties and extra spaces
    lines = [line.strip() for line in conversation_text.split('\n') if line.strip()]

    messages: List[MessageItem] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip lines that say 'Load more' or day lines (Thursday, Monday, etc.)
        if line.lower().startswith("load more") or is_day_line(line):
            i += 1
            continue

        # This line should be the sender (e.g. "You" or "Madhukar Devaraju")
        sender = line
        i += 1
        if i >= len(lines):
            break

        # Next line should be the time
        time_line = lines[i]
        time_iso = parse_time_line(time_line)
        if not time_iso:
            # If we cannot parse the time here, skip it and move on
            i += 1
            continue
        i += 1

        # Collect body until the next recognized "sender" or "day" or "Load more" or valid time
        body_lines = []
        while i < len(lines):
            nxt = lines[i]
            if nxt.lower().startswith("load more") or is_day_line(nxt):
                # Reached a new block
                break
            if parse_time_line(nxt):
                # If nxt is a time line, it means a new message is coming
                break
            # Otherwise, treat it as part of the message body
            body_lines.append(nxt)
            i += 1

        # We have enough info to form one message
        body_text = "\n".join(body_lines).strip()
        message_item = MessageItem(
            message_id=str(uuid.uuid4()),
            thread_id=str(uuid.uuid4()),
            sender_name=sender,
            sender_email="",      # LinkedIn message => keep empty
            receiver_name="",     # keep empty by default
            receiver_email="",    # keep empty by default
            iso_datetime=time_iso,
            subject="",           # LinkedIn => keep empty
            body=body_text
        )
        messages.append(message_item)

    # Reverse the list so the latest is on top
    messages.reverse()
    return messages