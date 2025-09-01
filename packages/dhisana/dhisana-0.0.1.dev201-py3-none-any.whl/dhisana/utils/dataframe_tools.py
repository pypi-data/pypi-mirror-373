# Tools to mainpulate dataframes. Convert any Natural Language query to a pandas query and process data frames..

import logging
import os
import json
import csv
from typing import List, Optional
from fastapi import HTTPException
import pandas as pd
from pydantic import BaseModel
import time
import os
from openai import LengthFinishReasonError, AsyncOpenAI, OpenAIError
import csv
from dhisana.utils.cache_output_tools import cache_output
from dhisana.utils.assistant_tool_tag import assistant_tool
import hashlib
import json
import glob

from dhisana.utils.cache_output_tools import retrieve_output

class FileItem:
    def __init__(self, file_path: str):
        self.file_path = file_path

class FileList:
    def __init__(self, files: List[FileItem]):
        self.files = files

class PandasQuery(BaseModel):
    pandas_query: str
    

@assistant_tool   
async def get_structured_output(message: str, response_type, model: str = "gpt-4.1-mini"):
    """
    Asynchronously retrieves structured output from the OpenAI API based on the input message.

    :param message: The input message to be processed by the OpenAI API.
    :param response_type: The expected format of the response (e.g., JSON).
    :param model: The model to be used for processing the input message. Defaults to "gpt-4.1-mini".
    :return: A tuple containing the parsed response and a status string ('SUCCESS' or 'FAIL').
    """
    try:
        # Use the class name instead of serializing the class
        response_type_str = response_type.__name__
        
        # Create unique hashes for message and response_type
        message_hash = hashlib.md5(message.encode('utf-8')).hexdigest()
        response_type_hash = hashlib.md5(response_type_str.encode('utf-8')).hexdigest()
        
        # Generate the cache key
        cache_key = f"{message_hash}:{response_type_hash}"
        cached_response = retrieve_output("get_structured_output", cache_key)
        if cached_response is not None:
            parsed_cached_response = response_type.parse_raw(cached_response)
            return parsed_cached_response, 'SUCCESS'

        client = AsyncOpenAI()
        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": "Extract structured content from input. Output is in JSON Format."},
                {"role": "user", "content": message},
            ],
            response_format=response_type,
            temperature=0.0
        )

        response = completion.choices[0].message
        if response.parsed:
            # Cache the successful response
            cache_output("get_structured_output", cache_key, response.parsed.json())
            return response.parsed, 'SUCCESS'
        elif response.refusal:
            logging.warning("ERROR: Refusal response: %s", response.refusal)
            return response.refusal, 'FAIL'
        
    except LengthFinishReasonError as e:
        logging.error(f"Too many tokens: {e}")
        raise HTTPException(status_code=502, detail="The request exceeded the maximum token limit.")
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with the OpenAI API.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": str(e)}, 'FAIL'

@assistant_tool
async def query_dataframes(user_query: str, input_files: Optional[List[str]], output_file_path: Optional[str] = None) -> str:
    """
    Query multiple dataframes based on a user query and write the output dataframe to a specified output file path.

    Args:
        user_query (str): User query in natural language.
        input_files (List[str]): List of paths to CSV files to be loaded into dataframes.
        output_file_path (Optional[str]): Path to the output file where the resulting dataframe will be saved.
            If not specified, a unique file path will be generated in '/tmp/run_interim_outputs/'.

    Returns:
        str: A JSON string representing the FileList containing the path to the output file if created,
             or an error message if an error occurred.
    """
    max_retries = 3
    if not input_files or not user_query:
        return json.dumps({"files": []})

    if not output_file_path:
        output_folder = '/tmp/run_interim_outputs/'
        os.makedirs(output_folder, exist_ok=True)
        unique_number = int(time.time() * 1000)
        output_file_name = f'query_dataframe_{unique_number}.csv'
        output_file_path = os.path.join(output_folder, output_file_name)
    else:
        output_folder = os.path.dirname(output_file_path)
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)

    data_frames = []
    df_names = []
    for idx, file in enumerate(input_files):
        if os.path.getsize(file) == 0:
            continue
        df = pd.read_csv(file)
        data_frames.append(df)
        df_name = f'df{idx+1}'
        df_names.append(df_name)

    if not data_frames:
        return json.dumps({"files": []})

    schema_info = ""
    for df_name, df in zip(df_names, data_frames):
        schema_info += f"DataFrame '{df_name}' columns: {', '.join(df.columns)}\n"

    error_message = ""

    for attempt in range(max_retries):
        message = f"""
        You are an expert data analyst. Given the following DataFrames and their schemas:

        {schema_info}

        Write a pandas query to answer the following question:

        \"\"\"{user_query}\"\"\"

        Your query should use the provided DataFrames ({', '.join(df_names)}) and produce a DataFrame named 'result_df'. Do not include any imports or explanations; only provide the pandas query code that assigns the result to 'result_df'.
        """
        if error_message:
            message += f"\nThe previous query returned the following error:\n{error_message}\nPlease fix the query."

        pandas_query_result, status = await get_structured_output(message, PandasQuery)
        if status == 'SUCCESS' and pandas_query_result and pandas_query_result.pandas_query:
            pandas_query = pandas_query_result.pandas_query
            local_vars = {name: df for name, df in zip(df_names, data_frames)}
            global_vars = {}
            try:
                exec(pandas_query, global_vars, local_vars)
                result_df = local_vars.get('result_df')
                if result_df is None:
                    error_message = "The query did not produce a DataFrame named 'result_df'."
                    if attempt == max_retries - 1:
                        return json.dumps({"error": error_message})
                    continue
                break
            except Exception as e:
                error_message = str(e)
                if attempt == max_retries - 1:
                    return json.dumps({"error": error_message})
                continue
        else:
            if attempt == max_retries - 1:
                return json.dumps({"error": "Failed to get a valid pandas query after multiple attempts."})
            continue

    result_df.to_csv(output_file_path, index=False)

    file_list = FileList(files=[FileItem(file_path=output_file_path)])

    def file_item_to_dict(file_item):
        return {"file_path": file_item.file_path}

    file_list_dict = {
        "files": [file_item_to_dict(file_item) for file_item in file_list.files]
    }
    file_list_json = json.dumps(file_list_dict, indent=2)
    return file_list_json

@assistant_tool
async def load_csv_file(input_file_path: str):
    """
    Loads data from a CSV file and returns it as a list of dictionaries.

    Args:
        input_file_path (str): The path to the input CSV file.

    Returns:
        List[Dict[str, Any]]: List of rows from the CSV file, where each row is a dictionary.
    """
    with open(input_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
 


@assistant_tool
async def merge_csv_files(input_folder_path: str, extension: str, required_fields=[], dedup_by_fields=[], sort_by_fields=[], output_file_path: str ="") -> str:
    # Step 1: List all CSV files in the input folder with the given extension
    all_files = glob.glob(os.path.join(input_folder_path, f"*.{extension}"))
    
    # Step 2: Read each CSV file into a DataFrame
    df_list = []
    for file in all_files:
        df = pd.read_csv(file)
        df_list.append(df)
    
    # Step 3: Concatenate all DataFrames
    merged_df = pd.concat(df_list, ignore_index=True)
    
    # Step 4: Filter rows where required fields are not empty
    if required_fields:
        merged_df = merged_df.dropna(subset=required_fields)
    
    # Step 5: Remove duplicate rows based on the dedup fields
    if dedup_by_fields:
        merged_df = merged_df.drop_duplicates(subset=dedup_by_fields)
    
    # Step 6: Sort the DataFrame by the sort fields
    if sort_by_fields:
        merged_df = merged_df.sort_values(by=sort_by_fields)
    
    # Step 7: Write the final DataFrame to the output file
    merged_df.to_csv(output_file_path, index=False)
    
    return output_file_path