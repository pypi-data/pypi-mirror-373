"""
Unified OpenAI / Azure OpenAI helper (no env-fallback for secrets)
=================================================================

Resolution order
----------------
1. If `tool_config` has a **"openai"** block  → public OpenAI
2. Else if it has an **"azure_openai"** block → Azure OpenAI
3. Otherwise                            → raise ValueError

`api_key` **and** `endpoint` (for Azure) must therefore be supplied in
`tool_config`.  They will never be read from the host environment.

Optional:
  • `AZURE_OPENAI_API_VERSION` – defaults to 2025-03-01-preview
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple, Union

from openai import AsyncOpenAI, OpenAI, AzureOpenAI, AsyncAzureOpenAI


# ─────────────────────────────────────────────────────────────────────────────
# 1. Helpers: config parsing
# ─────────────────────────────────────────────────────────────────────────────

def _extract_config(
    tool_config: Optional[List[Dict]], provider_name: str
) -> Dict[str, str]:
    """Return the config map for the requested provider name, else {}."""
    if not tool_config:
        return {}
    block = next((b for b in tool_config if b.get("name") == provider_name), {})
    return {entry["name"]: entry["value"] for entry in block.get("configuration", []) if entry}


def _discover_credentials(
    tool_config: Optional[List[Dict]] = None,
) -> Tuple[str, str, Optional[str]]:
    """
    Return (provider, api_key, endpoint_or_None).

    provider ∈ {"public", "azure"}
    """
    # 1️⃣ Public OpenAI
    openai_cfg = _extract_config(tool_config, "openai")
    if openai_cfg:
        key = openai_cfg.get("apiKey")
        if not key:
            raise ValueError(
                "OpenAI integration is not configured. Please configure the connection to OpenAI in Integrations."
            )
        return "public", key, None

    # 2️⃣ Azure OpenAI
    azure_cfg = _extract_config(tool_config, "azure_openai")
    if azure_cfg:
        key = azure_cfg.get("apiKey")
        endpoint = azure_cfg.get("endpoint")
        if not key or not endpoint:
            raise ValueError(
                "Azure OpenAI integration is not configured. Please configure the connection to Azure OpenAI in Integrations."
            )
        return "azure", key, endpoint

    # 3️⃣ Neither block present → error
    raise ValueError(
        "OpenAI integration is not configured. Please configure the connection to OpenAI in Integrations."
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Client factories
# ─────────────────────────────────────────────────────────────────────────────

def _api_version() -> str:
    """Return the Azure API version (env-controlled, no secret)."""
    return os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")


def create_openai_client(
    tool_config: Optional[List[Dict]] = None,
) -> Union[OpenAI, AzureOpenAI]:
    """
    Return a *synchronous* client:
        • openai.OpenAI      – public service
        • openai.AzureOpenAI – Azure
    """
    provider, key, endpoint = _discover_credentials(tool_config)

    if provider == "public":
        return OpenAI(api_key=key)

    # Azure
    return AzureOpenAI(api_key=key, azure_endpoint=endpoint, api_version=_api_version())


def create_async_openai_client(
    tool_config: Optional[List[Dict]] = None,
) -> AsyncOpenAI:
    """
    Return an *async* client (AsyncOpenAI).

    For Azure we pass both `azure_endpoint` and `api_version`.
    """
    provider, key, endpoint = _discover_credentials(tool_config)

    if provider == "public":
        return AsyncOpenAI(api_key=key)

    return AsyncAzureOpenAI(
        api_key=key,
        azure_endpoint=endpoint,
        api_version=_api_version(),
    )



# ─────────────────────────────────────────────────────────────────────────────
# 3. Convenience helper (legacy)
# ─────────────────────────────────────────────────────────────────────────────

def get_openai_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """Return just the API key (legacy helper)."""
    _, key, _ = _discover_credentials(tool_config)
    return key
