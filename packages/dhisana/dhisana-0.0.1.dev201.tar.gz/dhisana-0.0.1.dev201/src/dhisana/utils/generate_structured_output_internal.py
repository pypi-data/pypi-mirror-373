import asyncio
import hashlib
import json
import logging
import random

from fastapi import HTTPException
from pydantic import BaseModel

from openai import OpenAIError, RateLimitError
from openai.lib._parsing._completions import type_to_response_format_param

from json_repair import repair_json

from dhisana.utils import cache_output_tools
from dhisana.utils.fetch_openai_config import (
    _extract_config,
    create_async_openai_client,
)
from typing import Any, Dict, List, Optional, Tuple, Union

from openai import OpenAIError, RateLimitError
from pydantic import BaseModel



# ──────────────────────────────────────────────────────────────────────────────
# 2.  Vector-store utilities (unchanged logic, new client factory)
# ──────────────────────────────────────────────────────────────────────────────


async def get_vector_store_object(
    vector_store_id: str, tool_config: Optional[List[Dict]] = None
) -> Dict:
    client_async = create_async_openai_client(tool_config)
    try:
        return await client_async.vector_stores.retrieve(vector_store_id=vector_store_id)
    except OpenAIError as e:
        logging.error(f"Error retrieving vector store {vector_store_id}: {e}")
        return None

async def list_vector_store_files(
    vector_store_id: str, tool_config: Optional[List[Dict]] = None
) -> List:
    client_async = create_async_openai_client(tool_config)
    page = await client_async.vector_stores.files.list(vector_store_id=vector_store_id)
    return page.data


# ──────────────────────────────────────────────────────────────────────────────
# 3.  Core logic – only the client initialisation lines changed
# ──────────────────────────────────────────────────────────────────────────────

async def get_structured_output_internal(
    prompt: str,
    response_format: BaseModel,
    effort: str = "low",
    use_web_search: bool = False,
    model: str = "gpt-4.1-mini",
    tool_config: Optional[List[Dict]] = None,
    use_cache: bool = True
):
    """
    Makes a direct call to the new Responses API for structured output.

    On a 429 (rate-limit) error the call is retried once after
    20 s + random exponential back-off.
    """
    try:
        # ─── caching bookkeeping ────────────────────────────────────────────
        response_type_str = response_format.__name__
        message_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
        response_type_hash = hashlib.md5(response_type_str.encode("utf-8")).hexdigest()
        cache_key = f"{message_hash}:{response_type_hash}"

        if use_cache:
            cached_response = cache_output_tools.retrieve_output(
                "get_structured_output_internal", cache_key
            )
            if cached_response is not None:
                parsed_cached_response = response_format.parse_raw(cached_response)
                return parsed_cached_response, "SUCCESS"

        # ─── JSON schema for function calling ───────────────────────────────
        schema = type_to_response_format_param(response_format)
        json_schema_format = {
            "name": response_type_str,
            "type": "json_schema",
            "schema": schema["json_schema"]["schema"],
        }

        # ─── client initialisation (NEW) ────────────────────────────────────
        client_async = create_async_openai_client(tool_config)

        openai_cfg = _extract_config(tool_config, "openai")
        # TODO: Azure OpenAI does not support web_search yet
        if not openai_cfg:
            use_web_search = False

        # -------------------------------------------------------------------
        # Internal helper to perform ONE attempt
        # -------------------------------------------------------------------
        async def _make_request():
            if use_web_search and model.startswith("gpt-"):
                return await client_async.responses.create(
                    input=[
                        {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    model=model,
                    text={"format": json_schema_format},
                    tool_choice="required",
                    tools=[{"type": "web_search_preview"}],
                    store=False,
                )
            if model.startswith("o"):  # reasoning param only for "o" family
                return await client_async.responses.create(
                    input=[
                        {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    model=model,
                    reasoning={"effort": effort},
                    text={"format": json_schema_format},
                    store=False,
                )
            return await client_async.responses.create(
                input=[
                    {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                    {"role": "user", "content": prompt},
                ],
                model=model,
                text={"format": json_schema_format},
                store=False,
            )

        # -------------------------------------------------------------------
        # Call with one retry on 429
        # -------------------------------------------------------------------
        max_retries = 1
        attempt = 0
        while True:
            try:
                completion = await _make_request()
                break  # success → exit loop
            except (RateLimitError, OpenAIError) as e:
                # Detect 429 / rate-limit
                is_rl = (
                    isinstance(e, RateLimitError)
                    or getattr(e, "status_code", None) == 429
                    or "rate_limit" in str(e).lower()
                )
                if is_rl and attempt < max_retries:
                    attempt += 1
                    # 20 s base + exponential jitter
                    wait_time = 20 + random.uniform(0, 2 ** attempt)
                    logging.warning(
                        f"Rate-limit hit (429). Waiting {wait_time:.2f}s then retrying "
                        f"({attempt}/{max_retries})."
                    )
                    await asyncio.sleep(wait_time)
                    continue  # retry once
                logging.error(f"OpenAI API error: {e}")
                raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")

        # ─── handle model output (unchanged) ────────────────────────────────
        if completion and completion.output and len(completion.output) > 0:
            raw_text = None
            for out in completion.output:
                if out.type == "message" and out.content:
                    for content_item in out.content:
                        if hasattr(content_item, "text"):
                            raw_text = content_item.text
                            break
                        else:
                            logging.warning("request refused: %s", str(content_item))
                            return "Request refused.", "FAIL"
                    if raw_text:
                        break

            if not raw_text or not raw_text.strip():
                return "No text returned (possibly refusal or empty response)", "FAIL"

            try:
                parsed_obj = response_format.parse_raw(raw_text)
                cache_output_tools.cache_output(
                    "get_structured_output_internal", cache_key, parsed_obj.json()
                )
                return parsed_obj, "SUCCESS"

            except Exception:
                logging.warning("ERROR: Could not parse JSON from model output.")
                try:
                    fixed_json = repair_json(raw_text)
                    parsed_obj = response_format.parse_raw(fixed_json)
                    cache_output_tools.cache_output(
                        "get_structured_output_internal", cache_key, parsed_obj.json()
                    )
                    return parsed_obj, "SUCCESS"
                except Exception as e2:
                    logging.warning("JSON repair failed: %s", str(e2))
                    return raw_text, "FAIL"
        else:
            return "No output returned", "FAIL"

    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error.")



async def get_structured_output_with_mcp(
    prompt: str,
    response_format: BaseModel,
    effort: str = "low",
    use_web_search: bool = False,
    model: str = "gpt-4.1-mini",
    tool_config: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Union[BaseModel, str], str]:
    """
    Sends a JSON-schema-constrained prompt to an OpenAI model, with an MCP
    server configured as a `tool`.

    * If the model returns a tool call that *requires approval*, the function
      immediately returns a minimal object that satisfies `response_format`
      with `"APPROVAL_PENDING"` in `response_summary`, along with the status
      string ``"PENDING_APPROVAL"``.
    * Once the tool has executed (the provider returns `mcp_tool_result`) or
      the model replies directly with the JSON payload, the parsed object is
      cached and returned with status ``"SUCCESS"``.
    * Any MCP tool-listing messages are ignored.
    """
    # ─── Validate MCP configuration ────────────────────────────────────────────
    mcp_cfg = _extract_config(tool_config, "mcpServer") or {}
    server_label: str = mcp_cfg.get("serverLabel", "")
    server_url: str | None = mcp_cfg.get("serverUrl")
    api_key_header_name: str | None = mcp_cfg.get("apiKeyHeaderName")
    api_key_header_value: str | None = mcp_cfg.get("apiKeyHeaderValue")

    if not (server_url and api_key_header_name and api_key_header_value):
        raise HTTPException(400, detail="MCP server configuration incomplete.")

    # ─── Cache key (prompt + schema) ──────────────────────────────────────────
    response_type_str = response_format.__name__
    cache_key = (
        f"{hashlib.md5(prompt.encode()).hexdigest()}:"
        f"{hashlib.md5(response_type_str.encode()).hexdigest()}"
    )
    if (cached := cache_output_tools.retrieve_output("get_structured_output_with_mcp", cache_key)):
        return response_format.parse_raw(cached), "SUCCESS"

    # ─── JSON-schema format for `text` param ──────────────────────────────────
    schema_cfg = type_to_response_format_param(response_format)
    json_schema_format = {
        "name": response_type_str,
        "type": "json_schema",
        "schema": schema_cfg["json_schema"]["schema"],
    }

    # ─── Build tool list ──────────────────────────────────────────────────────
    tools: List[Dict[str, Any]] = [
        {
            "type": "mcp",
            "server_label": server_label,
            "server_url": server_url,
            "headers": {api_key_header_name: api_key_header_value},
            "require_approval": "never"
        }
    ]
    if use_web_search and model.startswith("gpt-"):
        tools.append({"type": "web_search_preview"})

    # ─── Async OpenAI client ──────────────────────────────────────────────────
    client_async = create_async_openai_client(tool_config)

    async def _make_request():
        kwargs: Dict[str, Any] = {
            "input": [
                {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                {"role": "user", "content": prompt},
            ],
            "model": model,
            "text": {"format": json_schema_format},
            "store": False,
            "tools": tools,
            "tool_choice": "required",
        }
        if model.startswith("o"):
            kwargs["reasoning"] = {"effort": effort}
        return await client_async.responses.create(**kwargs)

    # ─── Retry once for 429s ──────────────────────────────────────────────────
    for attempt in range(2):
        try:
            completion = await _make_request()
            break
        except (RateLimitError, OpenAIError) as exc:
            if attempt == 0 and (
                isinstance(exc, RateLimitError)
                or getattr(exc, "status_code", None) == 429
                or "rate_limit" in str(exc).lower()
            ):
                sleep_for = 20 + random.uniform(0, 2.0)
                logging.warning("429 rate-limit hit; retrying in %.1fs", sleep_for)
                await asyncio.sleep(sleep_for)
                continue
            logging.error("OpenAI API error: %s", exc)
            raise HTTPException(502, detail="Error communicating with the OpenAI API.") from exc
    else:  # pragma: no cover
        raise HTTPException(502, detail="OpenAI request retry loop failed.")

    # ─── Parse the model’s structured output ──────────────────────────────────
    if not (completion and completion.output):
        return "No output returned", "FAIL"

    raw_text: str | None = None
    status: str = "SUCCESS"

    for out in completion.output:
        # 1️⃣  Human approval required
        if out.type == "mcp_approval_request":
            logging.info("Tool call '%s' awaiting approval", out.name)
            placeholder_obj = response_format.parse_obj({"response_summary": "APPROVAL_PENDING"})
            return placeholder_obj, "PENDING_APPROVAL"

        # 2️⃣  Ignore capability listings
        if out.type == "mcp_list_tools":
            continue

        # 3️⃣  Tool finished: provider returned result object
        if out.type == "mcp_tool_result":
            try:
                # If result already matches schema, emit directly
                raw_text = (
                    json.dumps(out.result)
                    if isinstance(out.result, (dict, list))
                    else json.dumps({"response_summary": str(out.result)})
                )
            except Exception:  # pragma: no cover
                raw_text = json.dumps({"response_summary": "TOOL_EXECUTION_COMPLETE"})
            break

        # 4️⃣  Regular assistant message
        if out.type == "message" and out.content:
            for c in out.content:
                if hasattr(c, "text") and c.text:
                    raw_text = c.text
                    break
            if raw_text:
                break

        # 5️⃣  Anything else
        logging.debug("Unhandled output type: %s", out.type)

    if not raw_text or not raw_text.strip():
        return "No response", status

    # ─── Convert JSON -> pydantic object, with repair fallback ────────────────
    try:
        parsed_obj = response_format.parse_raw(raw_text)
    except Exception:
        logging.warning("Initial parse failed; attempting JSON repair")
        parsed_obj = response_format.parse_raw(repair_json(raw_text))

    # ─── Cache & return ───────────────────────────────────────────────────────
    cache_output_tools.cache_output(
        "get_structured_output_with_mcp", cache_key, parsed_obj.json()
    )
    return parsed_obj, status

async def get_structured_output_with_assistant_and_vector_store(
    prompt: str,
    response_format: BaseModel,
    vector_store_id: str,
    effort: str = "low",
    model="gpt-4.1-mini",
    tool_config: Optional[List[Dict]] = None,
    use_cache: bool = True
):
    """
    Same logic, now uses create_async_openai_client().
    """
    try:
        vector_store = await get_vector_store_object(vector_store_id, tool_config)
        if not vector_store:
            return await get_structured_output_internal(
                    prompt, response_format, tool_config=tool_config
                )
            
        files = await list_vector_store_files(vector_store_id, tool_config)
        if not files:
            return await get_structured_output_internal(
                prompt, response_format, tool_config=tool_config
            )

        response_type_str = response_format.__name__
        message_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
        response_type_hash = hashlib.md5(response_type_str.encode("utf-8")).hexdigest()
        cache_key = f"{message_hash}:{response_type_hash}"
        
        if use_cache:
            cached_response = cache_output_tools.retrieve_output(
                "get_structured_output_with_assistant_and_vector_store", cache_key
            )
            if cached_response is not None:
                parsed_cached_response = response_format.model_validate_json(cached_response)
                return parsed_cached_response, "SUCCESS"

        schema = type_to_response_format_param(response_format)
        json_schema_format = {
            "name": response_type_str,
            "type": "json_schema",
            "schema": schema["json_schema"]["schema"],
        }

        client_async = create_async_openai_client(tool_config)

        completion = await client_async.responses.create(
            input=[
                {"role": "system", "content": "You are a helpful AI. Output JSON only."},
                {"role": "user", "content": prompt},
            ],
            model=model,
            text={"format": json_schema_format},
            tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
            tool_choice="required",
            store=False,
        )

        if completion and completion.output and len(completion.output) > 0:
            raw_text = None
            for out in completion.output:
                if out.type == "message" and out.content and len(out.content) > 0:
                    raw_text = out.content[0].text
                    break

            if not raw_text or not raw_text.strip():
                raise HTTPException(status_code=502, detail="No response from the model.")

            try:
                parsed_obj = response_format.parse_raw(raw_text)
                cache_output_tools.cache_output(
                    "get_structured_output_with_assistant_and_vector_store",
                    cache_key,
                    parsed_obj.json(),
                )
                return parsed_obj, "SUCCESS"
            except Exception:
                logging.warning("Model returned invalid JSON.")
                return raw_text, "FAIL"
        else:
            return "No output returned", "FAIL"

    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error.")
