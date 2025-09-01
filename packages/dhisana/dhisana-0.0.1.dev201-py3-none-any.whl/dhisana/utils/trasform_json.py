import json
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_structured_output_internal import get_structured_output_internal

GLOBAL_GENERATED_PYTHON_CODE = {}
import logging
logger = logging.getLogger(__name__)

class GeneratedPythonCode(BaseModel):
    python_code: str


@assistant_tool
async def transform_json_code(
    input_json: str, 
    output_json: str, 
    function_name: str, 
    tool_config: Optional[List[Dict]] = None
) -> str:
    """
    Use LLM to generate python code to transform JSON from format X to format Y.
    Save that to a GLOBAL variable.

    Args:
        input_json (str): Example input JSON.
        output_json (str): Example output JSON.
        function_name (str): The generated python function should be saved as.
        tool_config (Optional[List[Dict]]): Optional tool configuration.

    Returns:
        str: Function name that was saved to the global scope.
    """
    max_retries = 3
    error_message = ""

    for attempt in range(max_retries):
        # Prepare the message
        message = f"""
        Given the following input and output JSON schemas, generate a Python function that transforms the input JSON to the output JSON.
        Example Input JSON:
        {input_json}
        Example Output JSON:
        {output_json}
        Name the function as:
        {function_name}
        Check for NoneType in code before any concatenation and make sure errors do not happen like 
        "unsupported operand type(s) for +: 'NoneType' and 'str'".
        Preserve the output type to be of the type in output JSON. Convert input field to string and 
        assign to output field if types don't match.
        Return the function code in 'python_code'. Do not include any imports or explanations; only 
        provide the '{function_name}' code that takes 'input_json' as input and returns the transformed 
        'output_json' as output.
        """
        if error_message:
            message += f"\nThe previous attempt returned the following error:\n{error_message}\nPlease fix the function."

        # Get structured output
        generated_python_code, status = await get_structured_output_internal(message, GeneratedPythonCode, tool_config=tool_config)
        if status == 'SUCCESS' and generated_python_code and generated_python_code.python_code:
            function_string = generated_python_code.python_code
            # Execute the generated function
            try:
                exec(function_string, globals())
                # Test the function
                input_data = json.loads(input_json)
                output_data = globals()[function_name](input_data)
                if output_data:
                    # Store the function code
                    GLOBAL_GENERATED_PYTHON_CODE[function_name] = globals()[function_name]
                    return function_name
                else:
                    error_message = "The function did not produce the expected output."
            except Exception as e:
                error_message = str(e)
        else:
            error_message = "Failed to generate valid Python code."

        if attempt == max_retries - 1:
            raise RuntimeError(f"Error executing generated function after {max_retries} attempts: {error_message}")


@assistant_tool
async def transform_json_with_type(
    input_json_str: str, 
    response_type: Type[BaseModel], 
    function_name: str, 
    tool_config: Optional[List[Dict]] = None
):
    """
    Transforms the input JSON into the format specified by the given Pydantic response type.

    Args:
        input_json_str (str): The input JSON string to be transformed.
        response_type (Type[BaseModel]): The Pydantic model defining the desired output format.
        function_name (str): The name of the function to generate and execute.
        tool_config (Optional[List[Dict]]): Optional tool configuration.

    Returns:
        The transformed JSON string matching the response_type format.
    """
    # Create a sample instance of the Pydantic model
    sample_instance = response_type.construct()
    # Convert the instance to JSON
    response_type_json_str = sample_instance.json()
    return await transform_json_code(input_json_str, response_type_json_str, function_name, tool_config=tool_config)


# ----------------------------------------------------
# Property Mapping (LLM-based)
# ----------------------------------------------------
class PropertyMapping(BaseModel):
    input_property_name: str
    mapped_property_name: str


class PropertyMappingList(BaseModel):
    properties: List[PropertyMapping]


async def create_property_mapping(
    sample_input: Dict[str, Any],
    required_fields: List[str],
    entity_type: str,
    tool_config: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, str]:
    """
    Generate a property mapping from the input fields to the required fields for either a
    Lead or an Account (Company). Calls an LLM to produce a JSON dictionary of field mappings.

    :param sample_input: A sample dictionary from the input data.
    :param required_fields: A list of fields we want to map to (e.g. ["organization_name", "first_name"]).
    :param entity_type: "lead" or "account", used in the prompt to clarify context for the LLM.
    :param tool_config: Optional LLM config.

    :return: Dict of {"existingField": "requiredFieldName", ...}
    """
    # We'll only show the top-level of sample_input in the prompt for brevity
    truncated_sample = {k: str(sample_input[k])[:128] for k in list(sample_input.keys())}

    # Prepare a textual prompt for the LLM
    user_prompt = f"""
    The user has data representing a {entity_type} but the fields may not match the required format.
    Required fields are: {required_fields}.
    A sample of the input is: {json.dumps(truncated_sample, indent=2)}

    Please output a JSON output mapping input_property_name to mapped_property_name.
    You MUST map only one input property to one output property.
    If a input property does not match any required field, you can skip mapping it. Map the best match.
    DO NOT map the same input property to multiple output properties.
    """

    logger.info(f"Asking LLM to create property mapping for entity_type='{entity_type}'...")

    response, status = await get_structured_output_internal(
        prompt=user_prompt,
        response_format=PropertyMappingList,
        effort="high",
        model="gpt-4.1-mini",
        tool_config=tool_config
    )
    if status == "SUCCESS" and response and response.properties:
        mapping = {}
        for prop in response.properties:
            mapping[prop.input_property_name] = prop.mapped_property_name
        return mapping
    else:
        logger.warning("Could not generate property mapping from LLM. Returning empty mapping.")
        return {}

