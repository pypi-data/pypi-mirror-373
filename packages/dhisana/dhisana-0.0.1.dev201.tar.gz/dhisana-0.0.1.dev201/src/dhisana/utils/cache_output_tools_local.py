import os
import hashlib
import json
import logging

CACHE_PATH = os.environ.get('AGENT_CACHE_PATH', '/tmp/dhisana_ai/cache_run_outputs/')

def cache_output(tool_name, key, value, ttl=None):
    """
    Cache the output of a function using the provided key and value.

    Parameters:
    tool_name (str): Name of the tool whose output is being cached.
    key (str): The cache key.
    value (Any): The value to be cached.
    ttl (int, optional): The time-to-live (TTL) for the cached value in seconds.

    Returns:
    bool: True if the value was successfully cached, False otherwise.
    """
    # Ensure the cache directory exists
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    # Create a hash of the key
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Create the cache file path
    cache_file_path = os.path.join(CACHE_PATH, f"{tool_name}_{key_hash}.json")

    # Create the cache data
    cache_data = {
        'value': value,
        'ttl': ttl
    }

    # Write the cache data to the file
    try:
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, 'w') as cache_file:
            json.dump(cache_data, cache_file)
        return True
    except IOError as e:
        logging.error(f"IOError while writing to cache file {cache_file_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error while writing to cache file {cache_file_path}: {e}")
        return False


def retrieve_output(tool_name, key):
    """
    Retrieve the cached output for a given tool and cache key.

    Parameters:
    tool_name (str): Name of the tool whose output is being retrieved.
    key (str): The cache key.

    Returns:
    Any: The cached value if found, None otherwise.
    """
    # Create a hash of the key
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Create the cache file path
    cache_file_path = os.path.join(CACHE_PATH, f"{tool_name}_{key_hash}.json")

    # Read the cache data from the file
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, 'r') as cache_file:
                cache_data = json.load(cache_file)
                return cache_data['value']
        except IOError as e:
            logging.error(f"Error retrieving cache for tool '{tool_name}' with key '{key}': {e}")
            return None
    else:
        return None