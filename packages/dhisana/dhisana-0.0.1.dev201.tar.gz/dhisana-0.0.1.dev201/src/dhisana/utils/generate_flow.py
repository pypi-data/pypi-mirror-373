from pydantic import BaseModel
from dhisana.utils.dataframe_tools import get_structured_output

# Generate a workflow spec give the description in Input. 
# TODO needs more work to generate the workflow spec with right tools and functions.
# Pydantic models for structured data
class Workflow(BaseModel):
    workflow_json: str

async def generate_workflow_json(instructions, avilable_functions):
    
    prompt = f"""Give user input in plain text generate a worklfow json that can use the instructions to automation workflow.
                --------------------------------------
                Specification of workflow:\n
                {{
                    "id": "<workflow_id>",
                    "name": "<Name of the workflow.>",
                    "description": "<Description of the workflow>",
                    "version": "1.0",
                    "dependencies": ["<dependent task_id> Empty for the first task"],
                    "tasks": [
                        {{
                        "id": "<task_id_1>",
                        "name": "<name of the task_id_1>",
                        "description": "<description of the task_id_1>",
                        "type": "task",
                        "dependencies": [],
                        "inputs": {{
                            "<input_key_1>": {{
                            "type": "GenericList",
                            "format": "list",
                            "source": {{
                                "type": "task_output",
                                "task_id": "<task_id output that is input is for>. Keep this as <initial_input> for first task",
                                "output_key": "<output key> keep this as initial_input_list for first task"
                            }}
                            }}
                        }},
                        "operation": {{
                            "type": "python_callable",
                            "function": "The python function name to invoke",
                            "args": [
                                "<arguments to pass to python function eg input_key_1>"
                            ]
                        }},
                        "outputs": {{
                            "<output_key_1>": {{
                            "type": "GenericList",
                            "format": "list",
                            "deduplication_properties": ["<de-duplication property name>"],
                            "required_properties": ["<required property name>"]
                            }}
                        }}
                        }},
                        {{
                        "id": "<task_id_2>",
                        "name": "<name of the task_id_2>",
                        "description": "<description of the task_id_2>",
                        "type": "task",
                        "dependencies": ["task_id_1"],
                        "inputs": {{
                            "<input_key_2>": {{
                            "type": "GenericList",
                            "format": "list",
                            "source": {{
                                "type": "task_output",
                                "task_id" : "task_id_1",
                                "output_key": "output_key_1"
                            }}
                            }}
                        }},
                        "operation": {{
                            "type": "python_callable",
                            "function": "The python function to invoke",
                            "args": [
                                "arguments to pass to python function eg input_key_2"
                            ]
                        }},
                        "outputs": {{
                            "<output_key_2>": {{
                            "type": "GenericList",
                            "format": "list",
                            "deduplication_properties": ["<de-duplication property name>"],
                            "required_properties": ["<required property name>"]
                            }}
                        }}
                    ]
                }}
                -------------------------------------
                You have the fullowing python function to invoke:
                {avilable_functions}
                --------------
                User instructions to convert to workflow:\n
                {instructions}
                """

    extract_content, status = await get_structured_output(prompt, Workflow)

    if status == "SUCCESS":
        return extract_content.workflow_json
    else:
        return ""
