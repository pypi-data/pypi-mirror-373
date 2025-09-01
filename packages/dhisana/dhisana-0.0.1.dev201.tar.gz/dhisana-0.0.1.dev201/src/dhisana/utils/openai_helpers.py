# Helper functions to call OpenAI Assistant

from datetime import datetime, timezone
import inspect
import os
import csv
import json
import hashlib
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field, create_model
from fastapi import HTTPException
from openai import AsyncOpenAI, OpenAIError, pydantic_function_tool

from dhisana.utils import cache_output_tools
# from dhisana.utils.trasform_json import GLOBAL_GENERATED_PYTHON_CODE

from .agent_tools import GLOBAL_DATA_MODELS, GLOBAL_TOOLS_FUNCTIONS
from .google_workspace_tools import get_file_content_from_googledrive_by_name, write_content_to_googledrive
from .agent_tools import GLOBAL_OPENAI_ASSISTANT_TOOLS
from .openapi_spec_to_tools import (
    OPENAPI_TOOL_CONFIGURATIONS,
    OPENAPI_GLOBAL_OPENAI_ASSISTANT_TOOLS,
    OPENAPI_CALLABALE_FUNCTIONS,
)

# This file has functions to execute the agent workflow using provided spec and OpenAPI.
# Also has helper functions to extract structured data from the agent response.
# TODO: we need to enhance the Agent workflow handling. 
# TODO: Move the OpenAI related helper functions to a separate file.

def get_openai_access_token(tool_config: Optional[List[Dict]] = None) -> str:
    """
    Retrieves the OPENAI_API_KEY access token from the provided tool configuration.

    Args:
        tool_config (list): A list of dictionaries containing the tool configuration. 
                            Each dictionary should have a "name" key and a "configuration" key,
                            where "configuration" is a list of dictionaries containing "name" and "value" keys.

    Returns:
        str: The OPENAI_API_KEY access token.

    Raises:
        ValueError: If the OpenAI integration has not been configured.
    """
    if tool_config:
        openai_config = next(
            (item for item in tool_config if item.get("name") == "openai"), None
        )
        if openai_config:
            config_map = {
                item["name"]: item["value"]
                for item in openai_config.get("configuration", [])
                if item
            }
            OPENAI_API_KEY = config_map.get("apiKey")
        else:
            OPENAI_API_KEY = None
    else:
        OPENAI_API_KEY = None

    OPENAI_API_KEY = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError(
            "OpenAI integration is not configured. Please configure the connection to OpenAI in Integrations."
        )
    return OPENAI_API_KEY

async def read_from_google_drive(path):
    return await get_file_content_from_googledrive_by_name(file_name=path)

# Function to get headers for OpenAPI tools
def get_headers(toolname):
    headers = OPENAPI_TOOL_CONFIGURATIONS.get(toolname, {}).get("headers", {})
    return headers


def get_params(toolname):
    params = OPENAPI_TOOL_CONFIGURATIONS.get(toolname, {}).get("params", {})
    return params


async def run_assistant(client, assistant, thread, prompt, response_type, allowed_tools):
    """
    Runs the assistant with the given parameters.
    """
    await send_initial_message(client, thread, prompt)
    allowed_tool_items = get_allowed_tool_items(allowed_tools)
    response_format = get_response_format(response_type)

    max_iterations = 5
    iteration_count = 0

    while iteration_count < max_iterations:
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            response_format=response_format,
            tools=allowed_tool_items,
        )

        while run.status == 'requires_action':
            if iteration_count >= max_iterations:
                logging.info("Exceeded maximum number of iterations for requires_action.")
                await client.beta.threads.runs.cancel(run_id=run.id, thread_id=thread.id)
                return "FAIL"

            tool_outputs = await handle_required_action(run)
            if tool_outputs:
                run = await submit_tool_outputs(client, thread, run, tool_outputs)
            else:
                break
            iteration_count += 1
            logging.info("Iteration count: %s", iteration_count)

        if run.status == 'completed':
            status = await handle_run_completion(client, thread, run)
            return status
        elif run.status == 'failed' and run.last_error.code == 'rate_limit_exceeded':
            logging.info("Rate limit exceeded. Retrying in 30 seconds...")
            await asyncio.sleep(30)
        elif run.status == 'expired':
            logging.info("Run expired. Creating a new run...")
        else:
            logging.info(f"Run status: {run.status}")
            return run.status

        iteration_count += 1
        if (iteration_count >= max_iterations):
            logging.info("Exceeded maximum number of iterations.")
            await client.beta.threads.runs.cancel(run_id=run.id, thread_id=thread.id)
            return 'FAIL'
        logging.info("Iteration count: %s", iteration_count)
    
    return "FAIL"

async def handle_run_completion(client, thread, run):
    if run.status == 'completed':
        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
    else:
        return run.status


async def send_initial_message(client, thread, prompt):
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )


def get_allowed_tool_items(allowed_tools):
    allowed_tool_items = [
        tool for tool in GLOBAL_OPENAI_ASSISTANT_TOOLS
        if tool['type'] == 'function' and tool['function']['name'] in allowed_tools
    ]
    allowed_tool_items.extend([
        tool for tool in OPENAPI_GLOBAL_OPENAI_ASSISTANT_TOOLS
        if tool['type'] == 'function' and tool['function']['name'] in allowed_tools
    ])
    return allowed_tool_items


def get_response_format(response_type):
    return {
        'type': 'json_schema',
        'json_schema': {
            "name": response_type.__name__,
            "schema": response_type.model_json_schema()
        }
    }


async def handle_required_action(run):
    tool_outputs = []
    current_batch_size = 0
    max_batch_size = 256 * 1024  # 256 KB
    logging.info(f"Handling required action")

    if hasattr(run, 'required_action') and hasattr(run.required_action, 'submit_tool_outputs'):
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            function, openai_function = get_function(tool.function.name)
            if function:
                output_str, output_size = await invoke_function(function, tool, openai_function)
                if current_batch_size + output_size > max_batch_size:
                    tool_outputs.append(
                        {"tool_call_id": tool.id, "output": ""})
                else:
                    tool_outputs.append(
                        {"tool_call_id": tool.id, "output": output_str})
                    current_batch_size += output_size
            else:
                logging.info(f"Function {tool.function.name} not found.")
                tool_outputs.append(
                    {"tool_call_id": tool.id, "output": "No results found"})

    return tool_outputs


def get_function(function_name):
    function = GLOBAL_TOOLS_FUNCTIONS.get(function_name)
    openai_function = False
    if not function:
        function = OPENAPI_CALLABALE_FUNCTIONS.get(function_name)
        openai_function = True
    return function, openai_function


async def invoke_function(function, tool, openai_function):
    try:
        function_args = json.loads(tool.function.arguments)
        logging.info(f"Invoking function {tool.function.name} with args: {function_args}\n")
              
        if openai_function:
            output = await invoke_openapi_function(function, function_args, tool.function.name)
        else:
            if asyncio.iscoroutinefunction(function):
                output = await function(**function_args)
            else:
                output = function(**function_args)
        output_str = json.dumps(output)
        output_size = len(output_str.encode('utf-8'))
        logging.info(f"\nOutput from function {tool.function.name}: {output_str[:256]}\n")
              
        return output_str, output_size
    except Exception as e:
        logging.info(f"invoke_function Error invoking function {tool.function.name}: {e}")
        return "No results found", 0


async def invoke_openapi_function(function, function_args, function_name):

    json_body = function_args.get("json", None)
    path_params = function_args.get("path_params", None)
    fn_args = {"path_params": path_params, "data": json_body}
    headers = get_headers(function_name)

    query_params = function_args.get("params", {})
    params = get_params(function_name)
    query_params.update(params)
    status, reason, text = await function(
        name=function_name,
        fn_args=fn_args,
        headers=headers,
        params=query_params,
    )
    logging.info(f"\nOutput from function {function_name}: {status} {reason}\n")
    return {
        "status_code": status,
        "text": text,
        "reason": reason,
    }


async def submit_tool_outputs(client, thread, run, tool_outputs):
    try:
        return await client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    except Exception as e:
        logging.info(f"Failed to submit tool outputs: ${e}")
        return run


async def handle_run_completion(client, thread, run):
    if run.status == 'completed':
        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
    else:
        logging.info(f"Run status: {run.status}")
        return run.status



async def extract_and_structure_data(client, assistant, thread, prompt, task_inputs, response_type, allowed_tools):
    # Replace placeholders in the prompt with task inputs
    formatted_prompt = prompt
    for key, value in task_inputs.items():
        placeholder = "{{ inputs." + key + " }}"
        formatted_prompt = formatted_prompt.replace(placeholder, str(value))
    
    # Create a hash of the formatted prompt
    prompt_hash = hashlib.md5(formatted_prompt.encode()).hexdigest()
    
    # Retrieve cached response if available
    cached_response = cache_output_tools.retrieve_output("extract_and_structure_data", prompt_hash)
    if cached_response is not None:
        return cached_response
    
    # Run the assistant and cache the output if successful
    output = await run_assistant(client, assistant, thread, formatted_prompt, response_type, allowed_tools)
    if output and output != 'FAIL':
        cache_output_tools.cache_output("extract_and_structure_data", prompt_hash, output)
    
    return output

class RowItem(BaseModel):
    column_value: str
    
class GenericList(BaseModel):
    rows: List[RowItem]
    
def lookup_response_type(name: str):
    for model in GLOBAL_DATA_MODELS:
        if model.__name__ == name:
            return model
    return GenericList  # Default response type


async def process_agent_request(row_batch: List[Dict], workflow: Dict, custom_instructions: str) -> List[Dict]:
    """
    Process agent request using the OpenAI client.
    """
    #TODO: handle timezone here.
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    todays_date = datetime.now(timezone.utc).isoformat()        
    todays_day = datetime.now(timezone.utc).strftime('%d')    
    instructions = f"Hi, You are an AI Assistant. Help the user with their tasks.\n\n Todays date is: {todays_date} Todays day is {todays_day} \n\n{custom_instructions}\n\n"
    try:
        client = AsyncOpenAI()
        assistant = await client.beta.assistants.create(
            name="AI Assistant",
            instructions=instructions,   
            tools=[],
            model="gpt-4.1-mini"
        )
        thread = await client.beta.threads.create()
        parsed_outputs = []
        task_outputs = {}  # Dictionary to store outputs of tasks
        input_list = {}
        input_list['initial_input_list'] = {
            "data": row_batch,
            "format": "list"
            }
        task_outputs['initial_input'] = input_list
        for task in workflow['tasks']:
            # Process each task
            task_outputs = await process_task(client, assistant, thread, task, task_outputs)
        # Collect the final output
        parsed_outputs.append(task_outputs)
        return parsed_outputs
    except Exception as e:
        logging.warning(f"process_agent_request An error occurred: {e}", exc_info=True)
        return [{"error": f"Error Processing Leads. process_agent_request process_agent_request An error occurred: {e}"}]
    finally:
        try:
            await client.beta.assistants.delete(assistant.id)
        except Exception as e:
            logging.info(f"Error deleting assistant: {e}")


async def process_task(client, assistant, thread, task, task_outputs):
    """
    Process a single task in the workflow.
    """
    # Prepare inputs
    task_inputs = await prepare_task_inputs(task, task_outputs)

    # Run the operation
    output = await run_task_operation(client, assistant, thread, task, task_inputs)

    # Store outputs
    await store_task_outputs(task, output, task_outputs)

    return task_outputs

async def read_csv_rows(file_path):
    rows = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            rows.append(row)
    return rows

async def prepare_task_inputs(task, task_outputs):
    """
    Prepare the inputs for a task based on its input specifications.
    """
    inputs = task.get('inputs', {})
    task_inputs = {}
    for input_name, input_spec in inputs.items():
        source = input_spec.get('source', {})
        source_type = source.get('type', '')
        format = input_spec.get('format', 'list')
        if source_type == 'inline':
            # Get from inline source
            input_data = source.get('data')
        elif source_type == 'task_output':
            # Get from previous task output
            task_id = source.get('task_id')
            output_key = source.get('output_key')
            previous_task_output = task_outputs.get(task_id, {})            
            if isinstance(previous_task_output, dict):
                output_item = previous_task_output.get(output_key)
                input_data = output_item['data']
            else:
                input_data = previous_task_output
        
            # Ensure input_data is a list
            if not isinstance(input_data, list):
                input_data = [input_data]
        elif source_type == 'google_drive':
            # Handle Google Drive source
            path = source.get('location')
            input_data_path = await read_from_google_drive(path)
            input_data = await read_csv_rows(input_data_path)
        elif source_type == 'local_path':
            # Handle local path source
            input_data_path = source.get('location')
            input_data = await read_csv_rows(input_data_path)
        else:
            input_data = None
        if input_data:
            task_inputs[input_name] = { 
                                        "format": format, 
                                        "data" : input_data
            }
    return task_inputs

async def process_using_ai_assistant(prompt_template, task_inputs, client, assistant, thread, response_type, allowed_tools, task):
    outputs = []
    for key, value in task_inputs.items():
        format = value.get('format', 'list')
        items = value.get('data')
        if format == 'list':
            for item in items:
                formatted_prompt = prompt_template.replace(
                    "{{ inputs." + key + " }}", json.dumps(item)
                )
                # Run assistant with prompt
                logging.info(formatted_prompt)
                output = await extract_and_structure_data(
                    client, assistant, thread, formatted_prompt, task_inputs, response_type, allowed_tools
                )
                if output and output == 'FAIL':
                    pass
                output_json = None
                if isinstance(output, str):
                    try:
                        output_json = json.loads(output)
                    except json.JSONDecodeError:
                        pass
                if (
                    output_json
                    and isinstance(output_json, dict)
                    and 'data' in output_json
                    and isinstance(output_json['data'], list)
                ):
                    # Deserialize the JSON to responseType
                    items_deserialized = [response_type.parse_obj(item) for item in output_json['data']]
                    # Iterate over items_deserialized
                    for item in items_deserialized:
                        # Serialize each item back to JSON
                        serialized_item = json.dumps(item.dict())
                        outputs.append(serialized_item)
                elif output_json and isinstance(output_json, dict):
                    output_deserialized = response_type.parse_obj(output_json)
                    outputs.append(json.dumps(output_deserialized.dict()))
                else:
                    logging.warning("output_json is None or not a dict")
                if outputs and len(outputs) > 0:
                    interim_return_val = {
                        "data": outputs,
                        "format": "list"
                    }
                    await store_task_outputs_interim_checkpoint(task, interim_return_val, task_inputs)
        else:
            # Handle other formats if necessary
            pass
    return outputs

async def process_transform_json(task_inputs, response_type, task):
    outputs = []
    task_id = task.get('id')
    for input_name, input_info in task_inputs.items():
        data_format = input_info.get('format', 'list')
        input_info.get('transform_function_name', f"{task_id}_transform_input_json")
        items = input_info.get('data')
        if data_format == 'list':
            if items and len(items) > 0:
                # Generate the transformation function
                # if GLOBAL_GENERATED_PYTHON_CODE.get(transform_function_name, ''):
                #     transformation_function = GLOBAL_GENERATED_PYTHON_CODE[transform_function_name]
                # else:
                #     function_name = await transform_json_with_type(
                #         items[0],
                #         response_type,
                #         transform_function_name
                #     )
                #     transformation_function = GLOBAL_GENERATED_PYTHON_CODE[function_name]
                transformation_function = lambda x: x
                for item in items:
                    input_json = json.loads(item)
                    output_json = transformation_function(input_json)
                    output_deserialized = response_type.parse_obj(output_json)
                    outputs.append(json.dumps(output_deserialized.dict()))
                if outputs:
                    interim_return_val = {
                        "data": outputs,
                        "format": "list"
                    }
                    await store_task_outputs_interim_checkpoint(task, interim_return_val, task_inputs)
        else:
            # Handle other formats if necessary
            pass
    return outputs

async def process_function_call(operation, task_inputs, outputs):
    function_name = operation.get('function', '')
    args = operation.get('args', [])
    function = GLOBAL_TOOLS_FUNCTIONS.get(function_name)
    if function is None:
        raise Exception(f"Function {function_name} not found.")

    for key, value in task_inputs.items():
        format = value.get('format', 'list')
        items = value.get('data')
        item_parse_args_with_llm = operation.get('args_llm_parsed', 'False')
        if format == 'list':
            for item in items:
                # Prepare function keyword arguments
                if item_parse_args_with_llm == 'True':
                    function_kwargs, status = await get_function_call_arguments(
                        item, function_name
                    )
                    if status == 'FAIL':
                        continue
                else:
                    function_kwargs = {arg: item.get(arg, '') for arg in args}
                if asyncio.iscoroutinefunction(function):
                    output = await function(**function_kwargs)
                else:
                    output = function(**function_kwargs)
                process_output(output, outputs)
        else:
            # Prepare function arguments
            function_kwargs = {
                arg: task_inputs.get(arg, {}).get("data", '') for arg in args
            }
            if asyncio.iscoroutinefunction(function):
                output = await function(**function_kwargs)
            else:
                output = function(**function_kwargs)
            process_output(output, outputs)
    return outputs

def process_output(output, outputs):
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict):
                outputs.append(json.dumps(item))
            else:
                outputs.append(item)
    else:
        outputs.append(output)
                 
async def run_task_operation(client, assistant, thread, task, task_inputs):
    """
    Execute the operation defined in the task.
    """
    operation = task.get('operation', {})
    operation_type = operation.get('type', '')
    allowed_tools = operation.get('allowed_tools', [])
    response_type_name = operation.get('response_type', 'GenericList')
    response_type = lookup_response_type(response_type_name)
    outputs = []

    if operation_type == 'ai_assistant_call':
        prompt_template = operation.get('prompt', '')
        outputs = await process_using_ai_assistant(
            prompt_template, task_inputs, client, assistant, thread, response_type, allowed_tools, task
        )
    elif operation_type == 'ai_transform_input_json':
        outputs = await process_transform_json(
            task_inputs, response_type, task
        )
    elif operation_type == 'python_callable':
        outputs = await process_function_call(operation, task_inputs, outputs)
    return {
        "data": outputs,
        "format": "list"
    }

async def store_task_outputs_interim_checkpoint(task, output, task_outputs):
    """
    Store the outputs of a task for use in subsequent tasks.
    """
    outputs = task.get('outputs', {})
    if outputs:
        for output_name, output_spec in outputs.items():
            destination = output_spec.get('destination', {})
            if destination:
                dest_type = destination.get('type')
                path_template = destination.get('path_template')
                if path_template:
                    current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    current_timestamp = '_interim'
                    path = path_template.replace('{timestamp}', current_timestamp)
                    path = path.replace('{task_id}', task['id'])
                    local_path = path

                    if dest_type == 'google_drive':
                        local_path = os.path.join('/tmp', task['id'], path)

                    if dest_type == 'google_drive' or dest_type == 'local_path':
                        directory = os.path.dirname(local_path)
                        if directory and not os.path.exists(directory):
                            os.makedirs(directory)
                        logging.info(f"Writing output to {local_path}\n")

                        if output.get("format", "") == 'list':
                            data_list = []
                            for item in output.get("data", []):
                                try:
                                    data_list.append(json.loads(item))
                                except json.JSONDecodeError:
                                    # Handle or log the invalid JSON item
                                    pass
                            # Write the full list first with a 'full_list' prefix
                            def get_prefixed_path(file_path, prefix):
                                directory, filename = os.path.split(file_path)
                                name, ext = os.path.splitext(filename)
                                prefixed_filename = f"{prefix}_{name}{ext}"
                                return os.path.join(directory, prefixed_filename)

                            full_list_local_path = get_prefixed_path(local_path, 'full_list')
                            full_list_directory = os.path.dirname(full_list_local_path)
                            if full_list_directory and not os.path.exists(full_list_directory):
                                os.makedirs(full_list_directory)
                            logging.info(f"Writing full list output to {full_list_local_path}\n")

                            with open(full_list_local_path, 'w') as full_file:
                                if data_list and len(data_list) > 0:
                                    headers = [key for key in data_list[0].keys()]
                                    writer = csv.DictWriter(full_file, fieldnames=headers)
                                    writer.writeheader()
                                    for data in data_list:
                                        filtered_data = {key: value for key, value in data.items() if key in headers}
                                        writer.writerow(filtered_data)
                                else:
                                    writer = csv.DictWriter(full_file, fieldnames=[])
                                    writer.writeheader()
    return task_outputs

def filter_data_list(data_list, filter_by):
    """
    Filter the data_list based on conditions specified in filter_by.
    Supported operators: 'gt', 'lt', 'eq', 'gte', 'lte', 'ne'
    """
    from operator import gt, lt, eq, ge, le, ne

    operator_map = {
        'gt': gt,
        'lt': lt,
        'eq': eq,
        'gte': ge,
        'lte': le,
        'ne': ne
    }

    filtered_list = []
    for item in data_list:
        include_item = True
        for property_name, conditions in filter_by.items():
            value = item.get(property_name)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                include_item = False
                break
            for op, compare_value in conditions.items():
                op_func = operator_map.get(op)
                if op_func is None:
                    continue  # Unsupported operator
                try:
                    # Convert values to float for comparison if possible
                    item_value = float(value)
                    compare_value = float(compare_value)
                except (ValueError, TypeError):
                    item_value = value
                if not op_func(item_value, compare_value):
                    include_item = False
                    break
            if not include_item:
                break
        if include_item:
            filtered_list.append(item)
    return filtered_list

def convert_value(value):
    """
    Convert the value to the appropriate type for sorting.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return ""
    try:
        return float(value)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass
    return str(value)

def filter_and_sort(data_list, output_spec):
    """
    Filter and sort the data_list based on the output_spec.
    """
    required_properties = output_spec.get('required_properties', [])
    if required_properties:
        data_list = remove_empty_property_rows(data_list, required_properties)
    
    dedup_by = output_spec.get('deduplication_properties', [])
    if dedup_by:
        data_list = deduplicate_list_by_properties(data_list, dedup_by)
    
    sort_by_asc = output_spec.get('sort_by_asc', [])
    sort_by_desc = output_spec.get('sort_by_desc', [])
    
    # Combine sort fields with their corresponding order
    sort_fields = [(key, True) for key in sort_by_asc] + [(key, False) for key in sort_by_desc]
    logging.info(f"Sorting by: {sort_fields}")
    
    # Sort from least significant to most significant key
    for key, ascending in reversed(sort_fields):
        data_list = sorted(
            data_list,
            key=lambda x: convert_value(x.get(key)),
            reverse=not ascending
        )
    
    filter_by = output_spec.get('filter_by', {})
    if filter_by:
        data_list = filter_data_list(data_list, filter_by)
    
    return data_list

# Store the output of a task run.
async def store_task_outputs(task, output, task_outputs):
    """
    Store the outputs of a task for use in subsequent tasks.
    """
    outputs = task.get('outputs', {})
    if outputs:
        for output_name, output_spec in outputs.items():
            # Store output in task_outputs using task id and output_name
            if task['id'] not in task_outputs:
                task_outputs[task['id']] = {}

            destination = output_spec.get('destination', {})
            if destination:
                dest_type = destination.get('type')
                path_template = destination.get('path_template')
                if path_template:
                    current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    path = path_template.replace('{timestamp}', current_timestamp)
                    path = path.replace('{task_id}', task['id'])
                    local_path = path

                    if dest_type == 'google_drive':
                        local_path = os.path.join('/tmp', task['id'], path)

                    if dest_type == 'google_drive' or dest_type == 'local_path':
                        directory = os.path.dirname(local_path)
                        if directory and not os.path.exists(directory):
                            os.makedirs(directory)
                        logging.info(f"Writing output to {local_path}\n")

                        if output.get("format", "") == 'list':
                            data_list = []
                            for item in output.get("data", []):
                                try:
                                    data_list.append(json.loads(item))
                                except json.JSONDecodeError:
                                    # Handle or log the invalid JSON item
                                    pass
                            logging.info(f"Total count: {len(data_list)}")

                            # Write the full list first with a 'full_list' prefix
                            def get_prefixed_path(file_path, prefix):
                                directory, filename = os.path.split(file_path)
                                name, ext = os.path.splitext(filename)
                                prefixed_filename = f"{prefix}_{name}{ext}"
                                return os.path.join(directory, prefixed_filename)

                            full_list_local_path = get_prefixed_path(local_path, 'full_list')
                            full_list_directory = os.path.dirname(full_list_local_path)
                            if full_list_directory and not os.path.exists(full_list_directory):
                                os.makedirs(full_list_directory)
                            logging.info(f"Writing full list output to {full_list_local_path}\n")

                            with open(full_list_local_path, 'w') as full_file:
                                if data_list and len(data_list) > 0:
                                    headers = [key for key in data_list[0].keys()]
                                    writer = csv.DictWriter(full_file, fieldnames=headers)
                                    writer.writeheader()
                                    for data in data_list:
                                        filtered_data = {key: value for key, value in data.items() if key in headers}
                                        writer.writerow(filtered_data)
                                else:
                                    writer = csv.DictWriter(full_file, fieldnames=[])
                                    writer.writeheader()

                            if data_list and len(data_list) > 0:
                                data_list = filter_and_sort(data_list, output_spec)
                                if data_list and len(data_list) > 0:
                                    logging.info(f"Deduped and removed count: {len(data_list)}")
                                    headers = [key for key, value in data_list[0].items() if isinstance(value, (str, int, float, bool))]
                                    with open(local_path, 'w') as file:
                                        writer = csv.DictWriter(file, fieldnames=headers)
                                        writer.writeheader()
                                        for data in data_list:
                                            filtered_data = {key: value for key, value in data.items() if key in headers}
                                            writer.writerow(filtered_data)
                                else:
                                    writer = csv.DictWriter(full_file, fieldnames=[])
                                    writer.writeheader()
                            else:
                                with open(local_path, 'w') as file:
                                    writer = csv.DictWriter(file, fieldnames=[])
                                    writer.writeheader()
                        else:
                            with open(local_path, 'w') as file:
                                file.write(str(output))
                    else:
                        pass
                if dest_type == 'google_drive':
                    await write_to_google_drive(path, local_path)

                task_outputs[task['id']][output_name] = output
    else:
        task_outputs[task['id']] = output

# Remove rows with None or empty values for the specified properties.
def remove_empty_property_rows(data_list, properties):
    """
    Remove rows with None or empty values for the specified properties.
    """
    filtered_list = []
    for item in data_list:
        empty = False
        for property_name in properties:
            value = item.get(property_name)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                empty = True
                break
        if not empty:
            filtered_list.append(item)
    return filtered_list

# Deduplicate list by given input properties.
def deduplicate_list_by_properties(data_list, properties):
    """
    Deduplicate a list of dictionaries by a list of properties in order.
    Only deduplicate if the property value is not None or empty, strip spaces, and compare in lowercase.
    """
    for property_name in properties:
        seen = set()
        deduplicated_list = []
        for item in data_list:
            value = item.get(property_name)
            value = str(value or "").strip().lower()
            if value == "":
                deduplicated_list.append(item)
            elif value not in seen:
                seen.add(value)
                deduplicated_list.append(item)
        data_list = deduplicated_list
    return data_list

async def write_to_google_drive(cloud_path, local_path):
    # Placeholder function for writing to Google Drive
    await write_content_to_googledrive(cloud_path, local_path)
    logging.info(f"Writing to Google Drive at {cloud_path} {local_path}")


# Get a dynamic pyndantic model that corresponds to the function signature
def get_dynamic_model(function_name: str, function: Callable) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic BaseModel subclass based on the parameters of the given function.

    Args:
        function_name (str): The name of the function.
        function (Callable): The function object.

    Returns:
        Type[BaseModel]: A dynamically created Pydantic model class.
    """
    # Retrieve the function's signature
    signature = inspect.signature(function)
    fields = {}

    for param_name, param in signature.parameters.items():
        # Extract the parameter's type annotation
        annotation = param.annotation if param.annotation is not inspect.Parameter.empty else Any

        # Determine if the parameter has a default value
        if param.default is not inspect.Parameter.empty:
            default_value = param.default
        else:
            default_value = ...

        # Create a Field with a description
        field_info = Field(
            default=default_value,
            description=f"Parameter '{param_name}' of type '{annotation.__name__}'"
        )

        # Add the field to the fields dictionary
        fields[param_name] = (annotation, field_info)

    # Create and return the dynamic model
    dynamic_model = create_model(
        f"{function_name}_Arguments",
        __base__=BaseModel,
        **fields
    )

    return dynamic_model

# Given a function definition and input string extract the function call arguments using OpenAI API
async def get_function_call_arguments(input_text: str, function_name: str) -> Tuple[Dict[str, Any], str]:
    """
    Extracts function call arguments from the input text using OpenAI's API.

    Args:
        input_text (str): The input text containing the function call.
        function_name (str): The name of the function to extract arguments for.

    Returns:
        Tuple[Dict[str, Any], str]: A tuple containing the function arguments as a dictionary and a status message.
    """
    try:
        # Retrieve the function and its parameters
        function, _ = get_function(function_name)
        
        # Generate a dynamic Pydantic model based on the function's parameters
        dynamic_model = get_dynamic_model(function_name, function)
        
        # Define the tool using the dynamic model
        tool = pydantic_function_tool(dynamic_model)
        
        # Construct the prompt
        prompt = f"Extract the arguments for the function '{function_name}' from the following input:\n\n{input_text}"
        
        # Initialize the OpenAI client
        client = AsyncOpenAI()
        
        # Make the API call
        response = await client.beta.chat.completions.parse(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Extract function arguments in JSON format."},
                {"role": "user", "content": prompt},
            ],
            tools=[tool],
            response_format=dynamic_model
        )
        
        # Extract the function call arguments from the response
        parsed_output = vars(response.choices[0].message.parsed)
        return parsed_output, 'SUCCESS'
    
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")

