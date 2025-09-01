"""
Email enrichment & validation module

Adds Findymail support on top of existing ZeroBounce, Hunter and Apollo flows.

Providers supported
-------------------
* Findymail   – email finder (`/search/name`) & verifier (`/verify`)
* Hunter      – email finder (`/email-finder`) & verifier (`/email-verifier`)
* ZeroBounce  – guess format (`/guessformat`) & verifier (`/validate`)
* Apollo      – enrichment fallback (re‑checked with ZeroBounce/Hunter)

Priority order
--------------
Validation:  Findymail → Hunter → ZeroBounce  
Guess/find:  Findymail → Hunter → ZeroBounce → Apollo
"""

from __future__ import annotations

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any

import aiohttp

# ────────────────────────────────────────────────────────────────────────────
# Dhisana utility imports
# ────────────────────────────────────────────────────────────────────────────
from dhisana.schemas.sales import HubSpotLeadInformation
from dhisana.utils.field_validators import validate_and_clean_email
from dhisana.utils.apollo_tools import enrich_user_info_with_apollo
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.cache_output_tools import cache_output, retrieve_output

logger = logging.getLogger(__name__)

# ===========================================================================
# 0.  FINDYMAIL HELPERS
# ===========================================================================
FINDYMAIL_BASE_URL = "https://app.findymail.com/api"


def get_findymail_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieve the Findymail API key either from tool_config or environment.
    Tool‑config JSON shape expected:
        {
          "name": "findymail",
          "configuration": [
              {"name": "apiKey", "value": "<API_KEY>"}
          ]
        }
    """
    if tool_config:
        fm_cfg = next(
            (item for item in tool_config if item.get("name") == "findymail"), None
        )
        if fm_cfg:
            cfg_map = {
                c["name"]: c["value"] for c in fm_cfg.get("configuration", []) if c
            }
            api_key = cfg_map.get("apiKey")
        else:
            api_key = None
    else:
        api_key = None

    api_key = api_key or os.getenv("FINDYMAIL_API_KEY")
    if not api_key:
        logger.warning(
            "Findymail integration is not configured. Please configure the connection to Findymail in Integrations."
        )
        return ""
    return api_key


# ===========================================================================
# 1.  ACCESS‑TOKEN HELPERS FOR EXISTING PROVIDERS
# ===========================================================================


def get_zero_bounce_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """Retrieve ZeroBounce key from config/env."""
    if tool_config:
        zb_cfg = next(
            (item for item in tool_config if item.get("name") == "zerobounce"), None
        )
        if zb_cfg:
            cfg_map = {
                c["name"]: c["value"] for c in zb_cfg.get("configuration", []) if c
            }
            api_key = cfg_map.get("apiKey")
        else:
            api_key = None
    else:
        api_key = None

    api_key = api_key or os.getenv("ZERO_BOUNCE_API_KEY")
    if not api_key:
        logger.warning(
            "ZeroBounce integration is not configured. Please configure the connection to ZeroBounce in Integrations."
        )
        return ""
    return api_key


def get_hunter_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """Retrieve Hunter.io key from config/env."""
    if tool_config:
        h_cfg = next(
            (item for item in tool_config if item.get("name") == "hunter"), None
        )
        if h_cfg:
            cfg_map = {
                c["name"]: c["value"] for c in h_cfg.get("configuration", []) if c
            }
            api_key = cfg_map.get("apiKey")
        else:
            api_key = None
    else:
        api_key = None

    api_key = api_key or os.getenv("HUNTER_API_KEY")
    if not api_key:
        logger.warning(
            "Hunter integration is not configured. Please configure the connection to Hunter in Integrations."
        )
        return ""
    return api_key


# ===========================================================================
# 2.  VALIDATION FUNCTIONS
# ===========================================================================


@assistant_tool
async def check_email_validity_with_findymail(
    email_id: str,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Validate deliverability using Findymail `/verify` endpoint.

    Returns
    -------
    {
        "email": str,
        "confidence": "high" | "low",
        "is_valid": bool
    }
    """
    logger.info("Entering check_email_validity_with_findymail: %s", email_id)

    if not email_id or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_id):
        return {"email": email_id, "confidence": "low", "is_valid": False}

    cache_key = f"findymail:{email_id}"
    cached = retrieve_output("findymail_validate", cache_key)
    if cached:
        return json.loads(cached[0])

    api_key = get_findymail_access_token(tool_config)
    if not api_key:
        return {"email": email_id, "confidence": "low", "is_valid": False}

    url = f"{FINDYMAIL_BASE_URL}/verify"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"email": email_id}, headers=headers) as r:
                if r.status != 200:
                    logger.warning("[Findymail] verify non‑200: %s", r.status)
                    result = {"email": email_id, "confidence": "low", "is_valid": False}
                else:
                    data = await r.json()
                    verified = bool(data.get("verified") or data.get("result") == "verified")
                    result = {
                        "email": email_id,
                        "confidence": "high" if verified else "low",
                        "is_valid": verified,
                    }
    except Exception as ex:
        logger.exception("[Findymail] verify exception: %s", ex)
        result = {"email": email_id, "confidence": "low", "is_valid": False}

    cache_output("findymail_validate", cache_key, [json.dumps(result)])
    return result


# ───── ZeroBounce mapping/validation ───────────────────────────────────────


def _map_zerobounce_status_to_confidence(status: str) -> str:
    status = status.lower()
    if status == "valid":
        return "high"
    if status in ("catch-all", "unknown"):
        return "medium"
    return "low"


@assistant_tool
async def check_email_validity_with_zero_bounce(
    email_id: str,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    logger.info("Entering check_email_validity_with_zero_bounce: %s", email_id)
    if not email_id or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_id):
        return {"email": email_id, "confidence": "low", "is_valid": False}

    cache_key = f"zerobounce:{email_id}"
    cached = retrieve_output("zerobounce_validate", cache_key)
    if cached:
        return json.loads(cached[0])

    api_key = get_zero_bounce_access_token(tool_config)
    if not api_key:
        return {"email": email_id, "confidence": "low", "is_valid": False}

    url = f"https://api.zerobounce.net/v2/validate?api_key={api_key}&email={email_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    logger.warning("[ZeroBounce] non‑200: %s", r.status)
                    result = {"email": email_id, "confidence": "low", "is_valid": False}
                else:
                    data = await r.json()
                    conf = _map_zerobounce_status_to_confidence(data.get("status", ""))
                    result = {
                        "email": email_id,
                        "confidence": conf,
                        "is_valid": conf == "high",
                    }
    except Exception as ex:
        logger.exception("[ZeroBounce] validate exception: %s", ex)
        result = {"email": email_id, "confidence": "low", "is_valid": False}

    cache_output("zerobounce_validate", cache_key, [json.dumps(result)])
    return result


# ───── Hunter mapping/validation ───────────────────────────────────────────


def _map_hunter_status_to_confidence(status: str) -> str:
    status = status.lower()
    if status == "deliverable":
        return "high"
    if status in ("unknown", "accept_all"):
        return "medium"
    return "low"


@assistant_tool
async def check_email_validity_with_hunter(
    email_id: str,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    logger.info("Entering check_email_validity_with_hunter: %s", email_id)
    if not email_id or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email_id):
        return {"email": email_id, "confidence": "low", "is_valid": False}

    cache_key = f"hunter:{email_id}"
    cached = retrieve_output("hunter_validate", cache_key)
    if cached:
        return json.loads(cached[0])

    api_key = get_hunter_access_token(tool_config)
    if not api_key:
        return {"email": email_id, "confidence": "low", "is_valid": False}

    url = f"https://api.hunter.io/v2/email-verifier?email={email_id}&api_key={api_key}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    logger.warning("[Hunter] non‑200: %s", r.status)
                    result = {"email": email_id, "confidence": "low", "is_valid": False}
                else:
                    data = await r.json()
                    res = data.get("data", {}).get("result", "")
                    conf = _map_hunter_status_to_confidence(res)
                    result = {
                        "email": email_id,
                        "confidence": conf,
                        "is_valid": conf == "high",
                    }
    except Exception as ex:
        logger.exception("[Hunter] validate exception: %s", ex)
        result = {"email": email_id, "confidence": "low", "is_valid": False}

    cache_output("hunter_validate", cache_key, [json.dumps(result)])
    return result


# ===========================================================================
# 3.  GUESS / FIND FUNCTIONS
# ===========================================================================


@assistant_tool
async def guess_email_with_findymail(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Use Findymail to guess an email.

    If ``user_linkedin_url`` is provided, the function queries ``/search/linkedin``.
    Otherwise it falls back to ``/search/name`` with ``first_name``/``last_name``
    and ``domain``. Only verified emails are returned and therefore considered
    high confidence.
    """
    logger.info("Entering guess_email_with_findymail")

    if user_linkedin_url:
        cache_key = f"findymail:{user_linkedin_url}"
    else:
        if not first_name or not last_name or not domain:
            return {"email": "", "email_confidence": "low"}
        cache_key = f"findymail:{first_name}_{last_name}_{domain}"

    api_key = get_findymail_access_token(tool_config)
    if not api_key:
        return {"email": "", "email_confidence": "low"}

    cached = retrieve_output("findymail_guess", cache_key)
    if cached:
        return json.loads(cached[0])

    if user_linkedin_url:
        url = f"{FINDYMAIL_BASE_URL}/search/linkedin"
        payload = {"linkedin_url": user_linkedin_url, "webhook_url": None}
    else:
        url = f"{FINDYMAIL_BASE_URL}/search/name"
        full_name = " ".join(filter(None, [first_name, middle_name, last_name]))
        payload = {"name": full_name, "domain": domain}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as r:
                if r.status != 200:
                    logger.warning("[Findymail] search non‑200: %s", r.status)
                    result = {"email": "", "email_confidence": "low"}
                else:
                    data = await r.json()
                    contact = data.get("contact")
                    found = contact.get("email", "") if contact else ""
                    if found:
                        result = {
                            "email": found,
                            "email_confidence": "high",
                            "contact_info": json.dumps(contact) if contact else "",
                        }
                    else:
                        result = {"email": "", "email_confidence": "low"}
    except Exception as ex:
        logger.exception("[Findymail] search exception: %s", ex)
        result = {"email": "", "email_confidence": "low"}

    cache_output("findymail_guess", cache_key, [json.dumps(result)])
    return result


# ───── ZeroBounce guess ────────────────────────────────────────────────────


@assistant_tool
async def guess_email_with_zero_bounce(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,  # unused
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    logger.info("Entering guess_email_with_zero_bounce")
    if not first_name or not last_name or not domain:
        return {"email": "", "email_confidence": "low"}

    api_key = get_zero_bounce_access_token(tool_config)
    if not api_key:
        return {"email": "", "email_confidence": "low"}

    cache_key = f"zerobounce:guess:{first_name}_{last_name}_{domain}_{middle_name or ''}"
    cached = retrieve_output("zerobounce_guess", cache_key)
    if cached:
        return json.loads(cached[0])

    url = (
        "https://api.zerobounce.net/v2/guessformat"
        f"?api_key={api_key}&domain={domain}"
        f"&first_name={first_name}&middle_name={middle_name or ''}&last_name={last_name}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    logger.warning("[ZeroBounce] guessformat non‑200: %s", r.status)
                    result = {"email": "", "email_confidence": "low"}
                else:
                    data = await r.json()
                    if "email_confidence" not in data:
                        data["email_confidence"] = (
                            "high" if data.get("email") else "low"
                        )
                    result = data
    except Exception as ex:
        logger.exception("[ZeroBounce] guess exception: %s", ex)
        result = {"email": "", "email_confidence": "low"}

    cache_output("zerobounce_guess", cache_key, [json.dumps(result)])
    return result


# ───── Hunter guess ────────────────────────────────────────────────────────


@assistant_tool
async def guess_email_with_hunter(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,  # unused
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    logger.info("Entering guess_email_with_hunter")
    if not first_name or not last_name or not domain:
        return {"email": "", "email_confidence": "low"}

    api_key = get_hunter_access_token(tool_config)
    if not api_key:
        return {"email": "", "email_confidence": "low"}

    url = (
        "https://api.hunter.io/v2/email-finder"
        f"?domain={domain}&first_name={first_name}&last_name={last_name}"
        f"&api_key={api_key}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status != 200:
                    logger.warning("[Hunter] email-finder non‑200: %s", r.status)
                    result = {"email": "", "email_confidence": "low"}
                else:
                    data = await r.json()
                    email = data.get("data", {}).get("email", "")
                    score = float(data.get("data", {}).get("score", 0) or 0)
                    if score >= 80:
                        conf = "high"
                    elif score >= 50:
                        conf = "medium"
                    else:
                        conf = "low"
                    result = {"email": email, "email_confidence": conf}
    except Exception as ex:
        logger.exception("[Hunter] guess exception: %s", ex)
        result = {"email": "", "email_confidence": "low"}

    return result


# ───── Apollo guess (fallback) ─────────────────────────────────────────────


@assistant_tool
async def guess_email_with_apollo(
    first_name: str,
    last_name: str,
    domain: str,
    user_linkedin_url: Optional[str] = None,
    middle_name: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    logger.info("Entering guess_email_with_apollo")
    if not first_name or not last_name or not domain:
        return {"email": "", "email_confidence": "low"}

    apollo_cfg = next(
        (item for item in tool_config or [] if item.get("name") == "apollo"), None
    )
    if not apollo_cfg:
        return {"email": "", "email_confidence": "low"}

    input_lead = {
        "first_name": first_name,
        "last_name": last_name,
        "primary_domain_of_organization": domain,
        "user_linkedin_url": user_linkedin_url or "",
    }

    try:
        enriched = await enrich_user_info_with_apollo(input_lead, tool_config)
    except Exception as ex:
        logger.exception("[Apollo] enrich exception: %s", ex)
        enriched = {}

    apollo_email = enriched.get("email", "")
    if not apollo_email:
        return {"email": "", "email_confidence": "low"}

    # quick re‑check with Hunter
    validation = await check_email_validity_with_hunter(apollo_email, tool_config)
    conf = validation.get("confidence", "low")
    return {"email": apollo_email, "email_confidence": conf}


# ─── Provider map
GUESS_EMAIL_TOOL_MAP = {
    "findymail": guess_email_with_findymail,
    "hunter": guess_email_with_hunter,
    "zerobounce": guess_email_with_zero_bounce,
    "apollo": guess_email_with_apollo,
}

# ===========================================================================
# 4.  AGGREGATORS
# ===========================================================================


@assistant_tool
async def check_email_validity(
    email_id: str,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Validate by provider priority:
        1) Findymail  2) Hunter  3) ZeroBounce
    """
    logger.info("Entering check_email_validity")
    if not tool_config:
        return {"email": email_id, "confidence": "low", "is_valid": False}

    names = [c.get("name") for c in tool_config if c.get("name")]
    priority = ["findymail", "hunter", "zerobounce"]

    result: Dict[str, Any] = {"email": email_id, "confidence": "low", "is_valid": False}

    for provider in priority:
        if provider not in names:
            continue
        if provider == "findymail":
            result = await check_email_validity_with_findymail(email_id, tool_config)
        elif provider == "hunter":
            result = await check_email_validity_with_hunter(email_id, tool_config)
        else:
            result = await check_email_validity_with_zero_bounce(email_id, tool_config)

        if result["confidence"] in ("high", "low"):
            break

    logger.info("Exiting check_email_validity with %s", result)
    return result


@assistant_tool
async def guess_email(
    first_name: str,
    last_name: str,
    domain: str,
    middle_name: Optional[str] = None,
    user_linkedin_url: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Guess by provider priority:
        1) Findymail  2) Hunter  3) ZeroBounce  4) Apollo
    """
    logger.info("Entering guess_email")
    if not tool_config:
        return {"email": "", "email_confidence": "low"}

    names = [c.get("name") for c in tool_config if c.get("name")]
    priority = ["findymail", "hunter", "zerobounce", "apollo"]

    result: Dict[str, Any] = {"email": "", "email_confidence": "low"}

    for provider in priority:
        if provider not in names:
            continue
        guess_fn = GUESS_EMAIL_TOOL_MAP[provider]
        result = await guess_fn(
            first_name,
            last_name,
            domain,
            user_linkedin_url,
            middle_name,
            tool_config,
        )
        if result.get("email_confidence") == "high":
            break

    logger.info("Exiting guess_email with %s", result)
    return result


# ===========================================================================
# 5.  PROCESS EMAIL PROPERTIES (unchanged except provider names usable)
# ===========================================================================


@assistant_tool
async def process_email_properties(
    input_properties: Dict[str, Any],
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Central orchestrator used elsewhere in Dhisana."""
    logger.info("Entering process_email_properties")

    first_name = input_properties.get("first_name", "")
    last_name = input_properties.get("last_name", "")
    email = validate_and_clean_email(input_properties.get("email", ""))
    additional_properties = input_properties.get("additional_properties", {})
    user_linkedin_url = input_properties.get("user_linkedin_url", "")
    domain = input_properties.get("primary_domain_of_organization", "")

    if email:
        val = await check_email_validity(email, tool_config)
        if val["is_valid"] and val["confidence"] == "high":
            input_properties["email_validation_status"] = "valid"
        else:
            input_properties["email_validation_status"] = "invalid"
    else:
        if not domain:
            input_properties["email_validation_status"] = "invalid"
            input_properties["email"] = ""
        else:
            # Try HubSpot lookup first (disabled by default)
            hubspot_lead_info = None
            # hubspot_lead_info = await lookup_contact_by_name_and_domain(
            #     first_name, last_name, domain, tool_config=tool_config
            # )
            if (
                hubspot_lead_info
                and isinstance(hubspot_lead_info, HubSpotLeadInformation)
                and hubspot_lead_info.email
            ):
                hubspot_email = hubspot_lead_info.email
                val = await check_email_validity(hubspot_email, tool_config)
                if val["is_valid"] and val["confidence"] == "high":
                    input_properties["email"] = hubspot_email
                    input_properties["email_validation_status"] = "valid"
                else:
                    g = await guess_email(
                        first_name,
                        last_name,
                        domain,
                        "",
                        user_linkedin_url,
                        tool_config,
                    )
                    if is_guess_usable(g):
                        input_properties["email"] = g["email"]
                        if g["email_confidence"] == "high":
                            input_properties["email_validation_status"] = "valid"
                        else:
                            input_properties["email_validation_status"] = "invalid"
                            additional_properties["guessed_email"] = g["email"]
            else:
                g = await guess_email(
                    first_name,
                    last_name,
                    domain,
                    "",
                    user_linkedin_url,
                    tool_config,
                )
                input_properties["email"] = g["email"]
                if is_guess_usable(g) and g["email_confidence"] == "high":
                    input_properties["email_validation_status"] = "valid"
                else:
                    input_properties["email_validation_status"] = "invalid"
                    additional_properties["guessed_email"] = g["email"]

    input_properties["additional_properties"] = additional_properties
    logger.info("Exiting process_email_properties")
    return input_properties


# ===========================================================================
# 6.  HELPER FUNCTIONS
# ===========================================================================


async def safe_read_json_or_text(response: aiohttp.ClientResponse) -> Any:
    """Attempt JSON parsing; fallback to text."""
    try:
        return await response.json()
    except Exception:  # noqa: BLE001
        return await response.text()


def extract_domain(email: str) -> str:
    """user@domain.com → domain.com"""
    return email.split("@")[-1].strip() if "@" in email else ""


def is_guess_usable(guess_result: Dict[str, Any]) -> bool:
    """Treat high/medium as usable."""
    if not guess_result:
        return False
    return guess_result.get("email_confidence", "").lower() in ("high", "medium")
