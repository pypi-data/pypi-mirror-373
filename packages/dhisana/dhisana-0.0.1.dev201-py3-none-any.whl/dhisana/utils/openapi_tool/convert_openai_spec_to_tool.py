from __future__ import annotations

import json
from collections import defaultdict
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from fastapi import logger
from openapi_pydantic import Parameter
from pydantic import BaseModel, Field
import aiohttp
from typing import Any, Optional

from .api_models import INVALID_LOCATION_TEMPL, APIProperty, APIRequestBody
from .openapi_tool import HTTPVerb, OpenAPISpec

def _format_url(url: str, path_params: dict) -> str:
    expected_path_param = re.findall(r"{(.*?)}", url)
    new_params = {}
    for param in expected_path_param:
        clean_param = param.lstrip(".;").rstrip("*")
        val = path_params[clean_param]
        if isinstance(val, list):
            if param[0] == ".":
                sep = "." if param[-1] == "*" else ","
                new_val = "." + sep.join(val)
            elif param[0] == ";":
                sep = f"{clean_param}=" if param[-1] == "*" else ","
                new_val = f"{clean_param}=" + sep.join(val)
            else:
                new_val = ",".join(val)
        elif isinstance(val, dict):
            kv_sep = "=" if param[-1] == "*" else ","
            kv_strs = [kv_sep.join((k, v)) for k, v in val.items()]
            if param[0] == ".":
                sep = "."
                new_val = "."
            elif param[0] == ";":
                sep = ";"
                new_val = ";"
            else:
                sep = ","
                new_val = ""
            new_val += sep.join(kv_strs)
        else:
            if param[0] == ".":
                new_val = f".{val}"
            elif param[0] == ";":
                new_val = f";{clean_param}={val}"
            else:
                new_val = val
        new_params[param] = new_val
    return url.format(**new_params)

class APIOperation(BaseModel):
    """A model for a single API operation."""

    operation_id: str = Field(alias="operation_id")
    """The unique identifier of the operation."""

    description: Optional[str] = Field(alias="description")
    """The description of the operation."""

    base_url: str = Field(alias="base_url")
    """The base URL of the operation."""

    path: str = Field(alias="path")
    """The path of the operation."""

    method: HTTPVerb = Field(alias="method")
    """The HTTP method of the operation."""

    properties: Sequence[APIProperty] = Field(alias="properties")

    # TODO: Add parse in used components to be able to specify what type of
    # referenced object it is.
    # """The properties of the operation."""
    # components: Dict[str, BaseModel] = Field(alias="components")

    request_body: Optional[APIRequestBody] = Field(alias="request_body")
    """The request body of the operation."""

    @staticmethod
    def _get_properties_from_parameters(
        parameters: List[Parameter], spec: OpenAPISpec
    ) -> List[APIProperty]:
        """Get the properties of the operation."""
        properties = []
        for param in parameters:
            if APIProperty.is_supported_location(param.param_in):
                properties.append(APIProperty.from_parameter(param, spec))
            elif param.required:
                raise ValueError(
                    INVALID_LOCATION_TEMPL.format(
                        location=param.param_in, name=param.name
                    )
                )
            else:
                logger.warning(
                    INVALID_LOCATION_TEMPL.format(
                        location=param.param_in, name=param.name
                    )
                    + " Ignoring optional parameter"
                )
                pass
        return properties

    @classmethod
    def from_openapi_url(
        cls,
        spec_url: str,
        path: str,
        method: str,
    ) -> "APIOperation":
        """Create an APIOperation from an OpenAPI URL."""
        spec = OpenAPISpec.from_url(spec_url)
        return cls.from_openapi_spec(spec, path, method)


    @classmethod
    def from_openapi_spec(
        cls,
        spec: OpenAPISpec,
        path: str,
        method: str,
    ) -> "APIOperation":
        """Create an APIOperation from an OpenAPI spec."""
        operation = spec.get_operation(path, method)
        parameters = spec.get_parameters_for_operation(operation)
        properties = cls._get_properties_from_parameters(parameters, spec)
        operation_id = OpenAPISpec.get_cleaned_operation_id(spec, operation, path, method)
        request_body = spec.get_request_body_for_operation(operation)
        api_request_body = (
            APIRequestBody.from_request_body(request_body, spec)
            if request_body is not None
            else None
        )
        description = operation.description or operation.summary
        if not description and spec.paths is not None:
            description = spec.paths[path].description or spec.paths[path].summary
        return cls(
            operation_id=operation_id,
            description=description or "",
            base_url=spec.base_url,
            path=path,
            method=method,  # type: ignore[arg-type]
            properties=properties,
            request_body=api_request_body,
        )
def _openapi_params_to_json_schema(params: List[Parameter], spec: OpenAPISpec) -> dict:
    properties = {}
    required = []
    for p in params:
        if p.param_schema:
            schema = spec.get_schema(p.param_schema)
        else:
            media_type_schema = list(p.content.values())[0].media_type_schema  # type: ignore  # noqa: E501
            schema = spec.get_schema(media_type_schema)
        if p.description and not schema.description:
            schema.description = p.description
        properties[p.name] = json.loads(schema.json(exclude_none=True))
        if p.required:
            required.append(p.name)
    return {"type": "object", "properties": properties, "required": required}

def openapi_spec_to_openai_fn(
    spec: OpenAPISpec,
) -> Tuple[List[Dict[str, Any]], Callable]:
    """Convert a valid OpenAPI spec to the JSON Schema format expected for OpenAI
        functions.

    Args:
        spec: OpenAPI spec to convert.

    Returns:
        Tuple of the OpenAI functions JSON schema and a default function for executing
            a request based on the OpenAI function schema.
    """
    if not spec.paths:
        return [], lambda: None
    functions = []
    _name_to_call_map = {}
    for path in spec.paths:
        path_params = {
            (p.name, p.param_in): p for p in spec.get_parameters_for_path(path)
        }
        for method in spec.get_methods_for_path(path):
            request_args = {}
            op = spec.get_operation(path, method)
            op_params = path_params.copy()
            for param in spec.get_parameters_for_operation(op):
                op_params[(param.name, param.param_in)] = param
            params_by_type = defaultdict(list)
            for name_loc, p in op_params.items():
                params_by_type[name_loc[1]].append(p)
            param_loc_to_arg_name = {
                "query": "params",
                "header": "headers",
                "cookie": "cookies",
                "path": "path_params",
            }
            for param_loc, arg_name in param_loc_to_arg_name.items():
                if params_by_type[param_loc]:
                    request_args[arg_name] = _openapi_params_to_json_schema(
                        params_by_type[param_loc], spec
                    )
            request_body = spec.get_request_body_for_operation(op)
            # TODO: Support more MIME types.
            if request_body and request_body.content:
                media_types = {}
                for media_type, media_type_object in request_body.content.items():
                    if media_type_object.media_type_schema:
                        schema = spec.get_schema(media_type_object.media_type_schema)
                        media_types[media_type] = json.loads(
                            schema.json(exclude_none=True)
                        )
                if len(media_types) == 1:
                    media_type, schema_dict = list(media_types.items())[0]
                    key = "json" if media_type == "application/json" else "data"
                    request_args[key] = schema_dict
                elif len(media_types) > 1:
                    request_args["data"] = {"anyOf": list(media_types.values())}

            api_op = APIOperation.from_openapi_spec(spec, path, method)
            fn = {
                    "type": "function", 
                        "function":{
                        "name": api_op.operation_id,
                        "description": api_op.description,
                        "parameters": {
                            "type": "object",
                            "properties": request_args,
                        },
                    }
                }
            functions.append(fn)
            _name_to_call_map[fn["function"]["name"]] = {
                "method": method,
                "url": api_op.base_url + api_op.path,
            }
    
    async def default_call_api(
            name: str,
            fn_args: dict,
            headers: Optional[dict] = None,
            params: Optional[dict] = None,
            **kwargs: Any,
        ) -> Any:
        method = _name_to_call_map[name]["method"]
        url = _name_to_call_map[name]["url"]
        path_params = fn_args.pop("path_params", {})
        url = _format_url(url, path_params)
        if "data" in fn_args and isinstance(fn_args["data"], dict):
            fn_args["data"] = json.dumps(fn_args["data"])
        _kwargs = {**fn_args, **kwargs}
        if headers is not None:
            if "headers" in _kwargs:
                _kwargs["headers"].update(headers)
            else:
                _kwargs["headers"] = headers
        if params is not None:
            if "params" in _kwargs:
                _kwargs["params"].update(params)
            else:
                _kwargs["params"] = params
    
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **_kwargs) as response:
                return  response.status, response.reason, await response.text()

    return functions, default_call_api