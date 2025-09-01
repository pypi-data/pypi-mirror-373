# dhisana/email_io.py
# ─────────────────────────────────────────────────────────────────────────────
# Standard library
# ─────────────────────────────────────────────────────────────────────────────
import asyncio
import datetime
import email
import email.utils
import hashlib
import imaplib
import logging
import re
import uuid
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

# ─────────────────────────────────────────────────────────────────────────────
# Third-party libraries
# ─────────────────────────────────────────────────────────────────────────────
import aiosmtplib

# ─────────────────────────────────────────────────────────────────────────────
# Project-internal modules
# ─────────────────────────────────────────────────────────────────────────────
from dhisana.schemas.sales import MessageItem
from dhisana.schemas.common import ReplyEmailContext
from dhisana.utils.google_workspace_tools import (
    QueryEmailContext,
    SendEmailContext,
)


# --------------------------------------------------------------------------- #
#  Helper / Utility
# --------------------------------------------------------------------------- #

def _imap_date(iso_dt: Union[str, datetime]) -> str:
    """
    Convert an ISO 8601 datetime or datetime object into IMAP date format: DD-Mmm-YYYY.
    
    Examples:
        "2025-04-22T00:00:00Z" or datetime -> "22-Apr-2025"
    """
    if isinstance(iso_dt, datetime):
        dt_obj = iso_dt
    else:
        # handle Zulu‑UTC suffix
        dt_obj = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
    return dt_obj.strftime("%d-%b-%Y")


def _to_datetime(val: Union[datetime, str]) -> datetime:
    """
    Accept a datetime or a string and return a timezone-aware datetime.
    Tries ISO-8601 first; falls back to RFC-2822 (email Date header format).
    """
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)

    # Try ISO-8601 (e.g. 2025-04-24T15:28:00 or 2025-04-24 15:28:00±hh:mm)
    try:
        dt = datetime.fromisoformat(val)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    # Fall back to RFC-2822 (e.g. "Thu, 24 Apr 2025 15:28:00 -0700")
    try:
        return email.utils.parsedate_to_datetime(val)
    except Exception as exc:
        raise TypeError(
            f"start_time/end_time must be datetime or ISO/RFC-2822 string, got {val!r}"
        ) from exc


# --------------------------------------------------------------------------- #
#  Outbound -- SMTP
# --------------------------------------------------------------------------- #

async def send_email_via_smtp_async(
    ctx: SendEmailContext,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    *,
    use_starttls: bool = True,
) -> str:
    """
    Send a single e-mail over SMTP and return the RFC 5322 Message-ID that
    we set in the outbound message.

    This is crucial for correlating the sent message with what we see in IMAP
    later. We generate a unique Message-ID, and the IMAP server should preserve it.

    Returns
    -------
    str
        The Message-ID of the sent message (e.g., "<uuid@yourdomain.com>").
    """
    msg = MIMEText(ctx.body, _charset="utf-8")
    msg["From"] = f"{ctx.sender_name} <{ctx.sender_email}>"
    msg["To"] = ctx.recipient
    msg["Subject"] = ctx.subject

    # Generate a real RFC 5322 Message-ID
    domain_part = ctx.sender_email.split("@", 1)[-1] or "local"
    generated_id = f"<{uuid.uuid4()}@{domain_part}>"
    msg["Message-ID"] = generated_id

    smtp_kwargs = dict(
        hostname=smtp_server,
        port=smtp_port,
        username=username,
        password=password,
    )
    # Decide whether to use STARTTLS or TLS
    if use_starttls:
        smtp_kwargs["start_tls"] = True
    else:
        smtp_kwargs["tls"] = True

    try:
        # aiosmtplib.send returns a (code, response) tuple, but no server message ID.
        # We rely on the real Message-ID we have just set.
        await aiosmtplib.send(msg, **smtp_kwargs)
        logging.info("SMTP send OK – msg id %s", generated_id)
        await asyncio.sleep(20)
        return generated_id
    except Exception:
        logging.exception("SMTP send failed")
        raise


# --------------------------------------------------------------------------- #
#  Inbound -- IMAP
# --------------------------------------------------------------------------- #

def _parse_email_msg(raw_bytes: bytes) -> MessageItem:
    """
    Convert raw RFC-822 bytes into a MessageItem.

    We read the real "Message-ID", "In-Reply-To", and "References" headers
    to produce correct message_id and thread_id.

    If the email lacks a Message-ID, we generate a fallback using SHA-256
    of the body + a UTC timestamp, but normally real emails will have one.
    """
    msg = email.message_from_bytes(raw_bytes)

    # Helper for reading headers
    hdr = lambda h: msg.get(h, "")

    sender_name, sender_email = email.utils.parseaddr(hdr("From"))
    receiver_name, receiver_email = email.utils.parseaddr(hdr("To"))

    # Body: prefer the first text/plain part
    body: str = ""
    if msg.is_multipart():
        for part in msg.walk():
            if (
                part.get_content_type() == "text/plain"
                and "attachment" not in str(part.get("Content-Disposition", ""))
            ):
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    # Parse the Date header to get a timezone-aware datetime
    try:
        dt = email.utils.parsedate_to_datetime(hdr("Date"))
        dt_utc = dt.astimezone(timezone.utc)
    except Exception:
        dt_utc = datetime.utcnow()

    sent_iso = dt_utc.isoformat()
    ts_compact = dt_utc.strftime("%m-%d-%y-%H-%M")

    # Get the real Message-ID, or generate a fallback
    message_id = hdr("Message-ID").strip()
    if not message_id:
        # Fallback if none present
        body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        message_id = f"<{body_hash}-{ts_compact}@fallback.local>"

    # Determine a thread_id from References / In-Reply-To
    references = hdr("References").strip()
    in_reply_to = hdr("In-Reply-To").strip()

    if references:
        # Typically the first or last entry in References is the root; you can choose
        ref_ids = references.split()
        # Let's pick the *first* as the thread root
        thread_id = ref_ids[0]
    elif in_reply_to:
        # If there's no References but there's In-Reply-To, use that as thread ID
        thread_id = in_reply_to
    else:
        # No references or in-reply-to => this is the start of a new thread
        thread_id = message_id

    return MessageItem(
        message_id=message_id,
        thread_id=thread_id,
        sender_name=sender_name,
        sender_email=sender_email,
        receiver_name=receiver_name,
        receiver_email=receiver_email,
        iso_datetime=sent_iso,
        subject=hdr("Subject"),
        body=body,
    )


async def list_emails_in_time_range_imap_async(
    ctx: QueryEmailContext,
    imap_server: str,
    imap_port: int,
    username: str,
    password: str,
    *,
    mailbox: str = "INBOX",
    use_ssl: bool = True,
) -> List[MessageItem]:
    """
    Return all messages whose INTERNALDATE lies in [ctx.start_time, ctx.end_time).

    Uses `SINCE <date>` and `BEFORE <date+1>` for day-level search, then does
    a second-precision filter in Python to return only the correct messages.
    """
    start_dt = _to_datetime(ctx.start_time)
    end_dt = _to_datetime(ctx.end_time)

    def _worker() -> List[MessageItem]:
        conn = (
            imaplib.IMAP4_SSL(imap_server, imap_port)
            if use_ssl
            else imaplib.IMAP4(imap_server, imap_port)
        )
        try:
            conn.login(username, password)
            conn.select(mailbox, readonly=True)

            # Build coarse search window
            since_str = _imap_date(start_dt)
            before_str = _imap_date(end_dt + timedelta(days=1))  # BEFORE is exclusive
            criteria = ["SINCE", since_str, "BEFORE", before_str]
            if ctx.unread_only:
                criteria.insert(0, "UNSEEN")

            status, msg_nums = conn.search(None, *criteria)
            if status != "OK":
                logging.warning("IMAP search failed: %s %s", status, criteria)
                return []

            raw_ids = msg_nums[0]
            if not raw_ids:
                return []

            items: List[MessageItem] = []
            for num in raw_ids.split():
                # Precise filter on INTERNALDATE
                int_status, int_data = conn.fetch(num, "(INTERNALDATE)")
                if int_status != "OK" or not int_data or not int_data[0]:
                    continue

                m = re.search(
                    r'INTERNALDATE "([^"]+)"', int_data[0].decode(errors="ignore")
                )
                if not m:
                    continue
                msg_dt = email.utils.parsedate_to_datetime(m.group(1))

                if not (start_dt <= msg_dt < end_dt):
                    continue

                fetch_status, data = conn.fetch(num, "(RFC822)")
                if fetch_status == "OK" and data and data[0]:
                    items.append(_parse_email_msg(data[0][1]))

            return items

        finally:
            try:
                conn.close()
            except Exception:
                pass
            conn.logout()

    return await asyncio.to_thread(_worker)


# --------------------------------------------------------------------------- #
#  Reply-All via IMAP (fetch original) + SMTP (send reply)
# --------------------------------------------------------------------------- #

async def reply_to_email_via_smtp_async(
    ctx: ReplyEmailContext,
    *,
    smtp_server: str,
    smtp_port: int,
    imap_server: str,
    imap_port: int,
    username: str,
    password: str,
    mailbox: str = "INBOX",
    use_ssl_imap: bool = True,
    use_starttls_smtp: bool = True,
) -> Dict[str, Any]:
    """
    Fetch the original message via IMAP (by Message-ID) and send a Reply-All
    over SMTP.  Credentials assumed to be the same USER/PASS for both protocols.

    Returns dict with keys that mimic your Gmail helper's shape.
    """

    # 1. Locate & pull the original message (blocking -> run in executor)
    def _fetch_original() -> Optional[bytes]:
        conn = (
            imaplib.IMAP4_SSL(imap_server, imap_port)
            if use_ssl_imap
            else imaplib.IMAP4(imap_server, imap_port)
        )
        try:
            conn.login(username, password)
            conn.select(mailbox, readonly=False)  # can set flags if needed
            # Search for the exact Message-ID header
            status, nums = conn.search(None, "HEADER", "Message-ID", ctx.message_id)
            if status != "OK" or not nums[0]:
                logging.warning("IMAP search for %r returned %s", ctx.message_id, nums)
                return None
            num = nums[0].split()[0]
            _, data = conn.fetch(num, "(RFC822)")
            if ctx.mark_as_read.lower() == "true":
                conn.store(num, "+FLAGS", "\\Seen")
            return data[0][1] if data and data[0] else None
        finally:
            try:
                conn.close()
            except Exception:
                pass
            conn.logout()

    raw_original = await asyncio.to_thread(_fetch_original)
    if raw_original is None:
        raise RuntimeError(f"Could not locate original message with ID {ctx.message_id!r}")

    original = email.message_from_bytes(raw_original)
    hdr = lambda h: original.get(h, "")

    # 2. Derive reply headers
    to_addrs = hdr("Reply-To") or hdr("From")
    cc_addrs = hdr("Cc")
    subject = hdr("Subject")
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    orig_msg_id = hdr("Message-ID")  # parent's ID

    # Build the References header by appending the parent's ID
    existing_refs = hdr("References")
    if existing_refs:
        references = existing_refs.strip() + " " + orig_msg_id
    else:
        references = orig_msg_id

    # 3. Build the MIMEText reply
    msg = MIMEText(ctx.reply_body, _charset="utf-8")
    msg["From"] = f"{ctx.sender_name} <{ctx.sender_email}>"
    msg["To"] = to_addrs
    if cc_addrs:
        msg["Cc"] = cc_addrs
    msg["Subject"] = subject
    msg["In-Reply-To"] = orig_msg_id
    msg["References"] = references

    # Generate a new Message-ID for this reply
    domain_part = ctx.sender_email.split("@", 1)[-1] or "local"
    reply_msg_id = f"<{uuid.uuid4()}@{domain_part}>"
    msg["Message-ID"] = reply_msg_id

    # 4. Send via SMTP
    smtp_kwargs = dict(
        hostname=smtp_server,
        port=smtp_port,
        username=username,
        password=password,
    )
    if use_starttls_smtp:
        smtp_kwargs["start_tls"] = True
    else:
        smtp_kwargs["tls"] = True

    await aiosmtplib.send(msg, **smtp_kwargs)

    # 5. There's no universal "label" concept in generic IMAP, so ignore add_labels
    if ctx.add_labels:
        logging.warning("add_labels ignored – generic IMAP has no label concept")

    # 6. Build response dictionary
    recipients: List[str] = [to_addrs]
    if cc_addrs:
        recipients.append(cc_addrs)

    return {
        "mailbox_email_id": reply_msg_id,  # the new reply's ID
        "message_id": reply_msg_id,        # the new reply's ID
        "email_subject": subject,
        "email_sender": ctx.sender_email,
        "email_recipients": recipients,
        "read_email_status": "READ" if ctx.mark_as_read.lower() == "true" else "UNREAD",
        "email_labels": [],  # Not applicable for IMAP
    }
