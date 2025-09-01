# dhisana/email_providers.py
#
# Generic e-mail wrapper helpers for Dhisana.
# ---------------------------------------------------------------

import logging
from typing import Any, Dict, List, Optional, Sequence

from dhisana.schemas.common import (
    SendEmailContext,
    QueryEmailContext,
    ReplyEmailContext,
)
from dhisana.schemas.sales import MessageItem
from dhisana.utils.google_workspace_tools import (
    send_email_using_service_account_async,
    list_emails_in_time_range_async,
    reply_to_email_async as gw_reply_to_email_async,
)
from dhisana.utils.smtp_email_tools import (
    send_email_via_smtp_async,
    list_emails_in_time_range_imap_async,
    reply_to_email_via_smtp_async,
)

# --------------------------------------------------------------------------- #
#  Provider-selection helpers
# --------------------------------------------------------------------------- #


def _find_provider_cfg(
    tool_cfg: Optional[Sequence[Dict]], provider_name: str
) -> Optional[Dict]:
    """
    Return the *first* config-dict whose ``name`` matches *provider_name*.
    """
    if not tool_cfg:
        return None
    return next((c for c in tool_cfg if c.get("name") == provider_name), None)


def _smtp_creds_for_sender(smtp_cfg: Dict, sender_email: str) -> Optional[Dict[str, str]]:
    """
    Given an SMTP provider config and a sender address, return the matching
    ``username`` / ``password`` plus server settings, or ``None``.
    """
    try:
        usernames = [
            u.strip()
            for u in next(f for f in smtp_cfg["configuration"] if f["name"] == "usernames")[
                "value"
            ].split(",")
            if u.strip()
        ]
        passwords = [
            p.strip()
            for p in next(f for f in smtp_cfg["configuration"] if f["name"] == "passwords")[
                "value"
            ].split(",")
        ]
        if len(usernames) != len(passwords):
            logging.warning(
                "smtpEmail config: usernames/passwords length mismatch – skipping"
            )
            return None

        if sender_email not in usernames:
            return None

        idx = usernames.index(sender_email)

        def _field(name: str, default):
            try:
                return next(f for f in smtp_cfg["configuration"] if f["name"] == name)[
                    "value"
                ]
            except StopIteration:
                return default

        return {
            "username": usernames[idx],
            "password": passwords[idx],
            "smtp_host": _field("smtpEndpoint", "smtp.gmail.com"),
            "smtp_port": int(_field("smtpPort", 587)),
            "imap_host": _field("imapEndpoint", "imap.gmail.com"),
            "imap_port": int(_field("imapPort", 993)),
        }
    except Exception:
        logging.exception("Failed to parse smtpEmail config")
        return None


# --------------------------------------------------------------------------- #
#  Public wrapper APIs
# --------------------------------------------------------------------------- #

async def send_email_async(
    send_email_context: SendEmailContext,
    tool_config: Optional[List[Dict]] = None,
    *,
    provider_order: Sequence[str] = ("smtpEmail", "googleworkspace"),
):
    """
    Send an e-mail using the first *configured* provider in *provider_order*.

    Returns whatever the underlying provider helper returns:

        * SMTP              → Tuple[int, bytes]  (status-code, server-msg)
        * Google Workspace  → str                (message-id)
    """
    # ------------------------------------------------------------------ #
    # 1) Try the preferred providers in order
    # ------------------------------------------------------------------ #
    for provider in provider_order:
        # 1a) SMTP
        if provider == "smtpEmail":
            smtp_cfg = _find_provider_cfg(tool_config, "smtpEmail")
            if not smtp_cfg:
                continue

            creds = _smtp_creds_for_sender(smtp_cfg, send_email_context.sender_email)
            if not creds:
                # No creds for this sender – fall through.
                continue

            return await send_email_via_smtp_async(
                send_email_context,
                smtp_server=creds["smtp_host"],
                smtp_port=creds["smtp_port"],
                username=creds["username"],
                password=creds["password"],
                use_starttls=(creds["smtp_port"] == 587),
            )

        # 1b) Google Workspace
        elif provider == "googleworkspace":
            gw_cfg = _find_provider_cfg(tool_config, "googleworkspace")
            if not gw_cfg:
                continue

            return await send_email_using_service_account_async(
                send_email_context, tool_config
            )

        # -- future providers slot --------------------------------------

    # ------------------------------------------------------------------ #
    # 2) FINAL FALLBACK — use *first* SMTP credentials if available
    # ------------------------------------------------------------------ #
    smtp_cfg = _find_provider_cfg(tool_config, "smtpEmail")
    if smtp_cfg:
        try:
            usernames = [
                u.strip()
                for u in next(
                    f for f in smtp_cfg["configuration"] if f["name"] == "usernames"
                )["value"].split(",")
                if u.strip()
            ]
            passwords = [
                p.strip()
                for p in next(
                    f for f in smtp_cfg["configuration"] if f["name"] == "passwords"
                )["value"].split(",")
            ]
            if usernames and len(usernames) == len(passwords):
                # Build a fake SendEmailContext for the fallback user, so that
                # the underlying SMTP helper still sends the intended message
                # but authenticates with the first available mailbox.
                fallback_sender = usernames[0]
                creds = _smtp_creds_for_sender(smtp_cfg, fallback_sender)

                if creds:
                    logging.info(
                        "Fallback: no provider matched – using first SMTP creds (%s).",
                        creds["username"],
                    )
                    return await send_email_via_smtp_async(
                        send_email_context,
                        smtp_server=creds["smtp_host"],
                        smtp_port=creds["smtp_port"],
                        username=creds["username"],
                        password=creds["password"],
                        use_starttls=(creds["smtp_port"] == 587),
                    )
        except Exception:
            logging.exception("SMTP fallback failed")

    # ------------------------------------------------------------------ #
    # 3) Nothing worked
    # ------------------------------------------------------------------ #
    raise RuntimeError("No suitable e-mail provider configured for this sender.")


async def list_emails_async(
    query_email_context: QueryEmailContext,
    tool_config: Optional[List[Dict]] = None,
    *,
    provider_order: Sequence[str] = ("smtpEmail", "googleworkspace"),
) -> List[MessageItem]:
    """
    List e-mails (see ``QueryEmailContext``) using the first configured provider.

    Always returns ``List[MessageItem]``.
    """
    for provider in provider_order:
        if provider == "smtpEmail":
            smtp_cfg = _find_provider_cfg(tool_config, "smtpEmail")
            if not smtp_cfg:
                continue

            creds = _smtp_creds_for_sender(smtp_cfg, query_email_context.sender_email)
            if not creds:
                continue

            return await list_emails_in_time_range_imap_async(
                query_email_context,
                imap_server=creds["imap_host"],
                imap_port=creds["imap_port"],
                username=creds["username"],
                password=creds["password"],
            )

        elif provider == "googleworkspace":
            gw_cfg = _find_provider_cfg(tool_config, "googleworkspace")
            if not gw_cfg:
                continue
            return await list_emails_in_time_range_async(query_email_context, tool_config)

        # --- future providers go here ---

    raise RuntimeError("No suitable inbox provider configured for this sender.")


# ─────────────────────────────────────────────────────────────────────────────
# New public helper: reply_email_async
# ─────────────────────────────────────────────────────────────────────────────
async def reply_email_async(
    reply_email_context: ReplyEmailContext,
    tool_config: Optional[List[Dict]] = None,
    *,
    provider_order: Sequence[str] = ("smtpEmail", "googleworkspace"),
) -> Dict[str, Any]:
    """
    Reply (reply-all) to an e-mail using the first *configured* provider
    in *provider_order*.

    Returns the provider’s reply-metadata dictionary.
    """
    for provider in provider_order:
        # ------------------------------------------------------------------
        # 1) SMTP
        # ------------------------------------------------------------------
        if provider == "smtpEmail":
            smtp_cfg = _find_provider_cfg(tool_config, "smtpEmail")
            if not smtp_cfg:
                continue

            creds = _smtp_creds_for_sender(smtp_cfg, reply_email_context.sender_email)
            if not creds:
                continue

            return await reply_to_email_via_smtp_async(
                reply_email_context,
                smtp_server=creds["smtp_host"],
                smtp_port=creds["smtp_port"],
                imap_server=creds["imap_host"],
                imap_port=creds["imap_port"],
                username=creds["username"],
                password=creds["password"],
                use_starttls_smtp=(creds["smtp_port"] == 587),
            )

        # ------------------------------------------------------------------
        # 2) Google Workspace service-account
        # ------------------------------------------------------------------
        elif provider == "googleworkspace":
            gw_cfg = _find_provider_cfg(tool_config, "googleworkspace")
            if not gw_cfg:
                continue

            return await gw_reply_to_email_async(reply_email_context, tool_config)

        # -- future providers slot -----------------------------------------

    raise RuntimeError("No suitable reply-capable e-mail provider configured.")
