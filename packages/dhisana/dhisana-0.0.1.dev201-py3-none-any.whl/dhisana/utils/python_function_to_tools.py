# Convert python function to OPENAI function spec and add it to allowed list.
# This allows passing any python function to the assistant API for orchestration.

import inspect
from typing import List, Union, get_type_hints, get_args, get_origin


def get_function_spec_from_python_function(func):
    # Get function name
    func_name = func.__name__
    # Get docstring for the description
    description = inspect.getdoc(func) or ""
    # Get function signature
    signature = inspect.signature(func)
    # Get type hints
    type_hints = get_type_hints(func)

    # Build parameters
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }

    for param_name, param in signature.parameters.items():
        param_schema = {}
        param_type = type_hints.get(param_name, str)

        # Determine the JSON schema type based on the annotation
        origin = get_origin(param_type)
        args = get_args(param_type)

        if origin is Union and type(None) in args:
            # Optional type
            actual_type = args[0]
        else:
            actual_type = param_type

        if actual_type == str:
            param_schema["type"] = "string"
        elif actual_type == int:
            param_schema["type"] = "integer"
        elif actual_type == float:
            param_schema["type"] = "number"
        elif actual_type == bool:
            param_schema["type"] = "boolean"
        elif origin in [list, List]:
            param_schema["type"] = "array"
            param_schema["items"] = {"type": "string"}
        else:
            param_schema["type"] = "string"  # Default to string

        # Parameter description can be empty or populated from elsewhere
        param_schema["description"] = ""

        parameters["properties"][param_name] = param_schema

        # if param.default == inspect.Parameter.empty:
        parameters["required"].append(param_name)

    # Truncate description if it exceeds 1024 characters. OpenAI API has a limit of 1024 characters for description.
    if len(description) > 1024:
        description = description[:1021] + '...'
    
    function_spec = {
        "type": "function",
        "function": {
            "name": func_name,
            "strict": True,
            "description": description,
            "parameters": parameters
        }
    }

    return function_spec

async def convert_functions_to_openai_spec(functions):
    function_specs = []
    for func_name, func in functions.items():
        spec = get_function_spec_from_python_function(func)
        function_specs.append(spec)
    return function_specs