"""
Vector-store and file helpers that work with **either** OpenAI or Azure OpenAI,
using the shared factory functions defined in `dhisana.utils.fetch_openai_config`.

Only the client initialisation lines changed; all business logic is untouched.
"""

import json
import logging
import re
import traceback
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

import openai  # still needed for openai.NotFoundError
from dhisana.utils.fetch_openai_config import (
    create_openai_client,     # synchronous client
)

# ---------------------------------------------------------------------------
# Vector-store helpers
# ---------------------------------------------------------------------------


async def create_vector_store(
    vector_store_name: str,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Create a new vector store and return its metadata."""
    normalized_name = re.sub(r"[^a-z0-9_]+", "_", vector_store_name.lower())[:64]
    client = create_openai_client(tool_config)

    try:
        vs = client.vector_stores.create(name=normalized_name)
        return {
            "id": vs.id,
            "name": vs.name,
            "created_at": vs.created_at,
            "file_count": vs.file_counts.completed,
        }
    except Exception as e:
        logging.error(f"Error creating vector store: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def delete_vector_store(
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None,
) -> None:
    """Delete a vector store by ID."""
    client = create_openai_client(tool_config)
    try:
        client.vector_stores.delete(vector_store_id=vector_store_id)
    except Exception as e:
        logging.error(f"Error deleting vector store {vector_store_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------------------------------------------------------------
# File-upload helpers
# ---------------------------------------------------------------------------


async def upload_file_openai_and_vector_store(
    file_path_or_bytes: Any,
    file_name: str,
    mime_type: str,
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None,
):
    """Upload a file and attach it to a vector store (purpose = assistants / vision)."""
    client = create_openai_client(tool_config)
    purpose = "vision" if mime_type in {"image/jpeg", "image/png"} else "assistants"

    try:
        if isinstance(file_path_or_bytes, str):
            file_upload = client.files.create(
                file=open(file_path_or_bytes, "rb"),
                purpose=purpose,
            )
        elif isinstance(file_path_or_bytes, bytes):
            file_upload = client.files.create(
                file=(file_name, file_path_or_bytes, mime_type),
                purpose=purpose,
            )
        else:
            raise ValueError("Unknown file content type. Must be path or bytes.")

        if purpose == "assistants" and vector_store_id:
            client.vector_stores.files.create(
                vector_store_id=vector_store_id, file_id=file_upload.id
            )
        return file_upload
    except Exception as e:
        logging.error(f"Error uploading file {file_name}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def upload_file_openai(
    file_path_or_bytes: Any,
    file_name: str,
    mime_type: str,
    tool_config: Optional[List[Dict]] = None,
):
    """Upload a standalone file (not attached to a vector store)."""
    client = create_openai_client(tool_config)
    purpose = "vision" if mime_type in {"image/jpeg", "image/png"} else "assistants"

    try:
        if isinstance(file_path_or_bytes, str):
            file_upload = client.files.create(
                file=open(file_path_or_bytes, "rb"),
                purpose=purpose,
            )
        else:
            file_upload = client.files.create(
                file=(file_name, file_path_or_bytes, mime_type),
                purpose=purpose,
            )
        return file_upload
    except Exception as e:
        logging.error(f"Error uploading file {file_name}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def attach_file_to_vector_store(
    file_id: str,
    vector_store_id: str,
    tool_config: Optional[List[Dict]] = None,
):
    """Attach an already-uploaded file to a vector store."""
    client = create_openai_client(tool_config)
    try:
        return client.vector_stores.files.create(
            vector_store_id=vector_store_id, file_id=file_id
        )
    except Exception as e:
        logging.error(
            f"Error attaching file {file_id} to vector store {vector_store_id}: {e}"
        )
        raise HTTPException(status_code=400, detail=str(e))


async def delete_files(
    file_ids: List[str],
    vector_store_id: Optional[str] = None,
    tool_config: Optional[List[Dict]] = None,
):
    """Delete files from vector store (if given) and OpenAI storage."""
    client = create_openai_client(tool_config)

    for fid in file_ids:
        try:
            if vector_store_id:
                client.vector_stores.files.delete(
                    vector_store_id=vector_store_id, file_id=fid
                )
            client.files.delete(file_id=fid)
        except openai.NotFoundError:
            logging.warning(f"File not found: {fid}")
        except Exception as e:
            logging.error(f"Error deleting file {fid}: {e}\n{traceback.format_exc()}")

# ---------------------------------------------------------------------------
# RAG / Responses helpers
# ---------------------------------------------------------------------------


async def run_file_search(
    query: str,
    vector_store_id: str,
    model: str = "gpt-4.1-mini",
    max_num_results: int = 5,
    store: bool = True,
    tool_config: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Single-shot file_search + answer with the new Responses API."""
    client = create_openai_client(tool_config)

    try:
        rsp = client.responses.create(
            input=query,
            model=model,
            store=store,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                    "max_num_results": max_num_results,
                }
            ],
        )

        if len(rsp.output) > 1 and rsp.output[1].content:
            fs_chunk = rsp.output[1].content[0]
            annotations = fs_chunk.annotations or []
            retrieved_files = list({ann.filename for ann in annotations})
            return {
                "answer": fs_chunk.text,
                "retrieved_files": retrieved_files,
                "annotations": annotations,
            }

        return {
            "answer": rsp.output_text,
            "retrieved_files": [],
            "annotations": [],
        }
    except Exception as e:
        logging.error(f"Error in run_file_search: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))


async def run_response_text(
    prompt: str,
    model: str = "gpt-4.1-mini",
    max_tokens: int = 2048,
    store: bool = True,
    tool_config: Optional[List[Dict]] = None,
) -> (str, str):
    """Plain text completion via the Responses API."""
    client = create_openai_client(tool_config)

    try:
        rsp = client.responses.create(
            input=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            store=store,
        )
        return rsp.output_text, "success"
    except Exception as e:
        logging.error(f"Error in run_response_text: {e}\n{traceback.format_exc()}")
        return f"An error occurred: {e}", "error"


async def run_response_structured(
    prompt: str,
    response_format: dict,
    model: str = "gpt-4.1-mini",
    max_tokens: int = 1024,
    store: bool = True,
    tool_config: Optional[List[Dict]] = None,
) -> (Any, str):
    """Structured JSON output via Responses API."""
    client = create_openai_client(tool_config)

    try:
        rsp = client.responses.create(
            input=[{"role": "user", "content": prompt}],
            model=model,
            max_tokens=max_tokens,
            store=store,
            text={"format": response_format},
        )
        if rsp.output:
            raw = rsp.output[0].content[0].text
            try:
                return json.loads(raw), "success"
            except json.JSONDecodeError:
                return raw, "error"
        return "No output returned", "error"
    except Exception as e:
        logging.error(
            f"Error in run_response_structured: {e}\n{traceback.format_exc()}"
        )
        return f"An error occurred: {e}", "error"
