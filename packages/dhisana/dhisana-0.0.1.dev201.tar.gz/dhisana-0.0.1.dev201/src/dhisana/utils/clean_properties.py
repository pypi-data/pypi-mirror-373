from typing import Any, Dict, List
import copy
from typing import Any, Dict, List, Optional



def remove_empty(data: Any) -> Any:
    """
    Recursively remove empty or null-like values from JSON/dict data.
    
    - Removes None or 'null' (case-insensitive) strings.
    - Removes empty strings.
    - Removes empty lists and dicts.
    - Returns `None` if the entire structure becomes empty.
    """
    if isinstance(data, dict):
        cleaned_dict: Dict[str, Any] = {}
        for key, value in data.items():
            cleaned_value = remove_empty(value)
            if cleaned_value is not None:
                cleaned_dict[key] = cleaned_value
        
        # Return None if dictionary is empty after cleaning
        return cleaned_dict if cleaned_dict else None

    elif isinstance(data, list):
        cleaned_list: List[Any] = []
        for item in data:
            cleaned_item = remove_empty(item)
            if cleaned_item is not None:
                cleaned_list.append(cleaned_item)
        
        # Return None if list is empty after cleaning
        return cleaned_list if cleaned_list else None

    else:
        # Base/primitive case
        # Remove None or empty strings or strings "null" (case-insensitive)
        if data is None:
            return None
        if isinstance(data, str):
            if not data.strip() or data.lower() == "null":
                return None
        return data


def cleanup_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    In-place style: returns a cleaned copy (so the original isn't mutated).
    """
    cleaned = remove_empty(properties)
    return cleaned if cleaned is not None else {}




def cleanup_email_context(user_properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a cleaned copy of user_properties:
      - Removes null/empty values recursively.
      - Removes fields with keys that look like an 'id' or 'guid'.
      - Explicitly sets external_openai_vector_store_id to None if present.
    """
    clone_context = copy.deepcopy(user_properties)

    if isinstance(clone_context.get('external_known_data'), dict) \
       and 'external_openai_vector_store_id' in clone_context['external_known_data']:
        clone_context['external_known_data']['external_openai_vector_store_id'] = None

    cleaned = _remove_empty_and_ids(clone_context)
    return cleaned if cleaned is not None else {}

def _remove_empty_and_ids(data: Any) -> Optional[Any]:
    """
    Recursively remove:
      - None values
      - Empty strings or "null" strings (case-insensitive)
      - Empty lists/dicts
      - Keys whose names look like IDs (e.g., containing "id" or "guid")
    Returns None if the resulting object is empty.
    """
    if isinstance(data, dict):
        result: Dict[str, Any] = {}
        for key, value in data.items():
            if _is_id_key(key):
                continue
            cleaned_value = _remove_empty_and_ids(value)
            if not _is_empty_value(cleaned_value):
                result[key] = cleaned_value
        return result if result else None

    elif isinstance(data, list):
        result: List[Any] = []
        for item in data:
            cleaned_item = _remove_empty_and_ids(item)
            if not _is_empty_value(cleaned_item):
                result.append(cleaned_item)
        return result if result else None

    else:
        if _is_empty_value(data):
            return None
        return data

def _is_id_key(key: str) -> bool:
    """
    Identify if a key is ID-like by checking if 'id' or 'guid' appears in its name (case-insensitive),
    or if it ends with _id, _ids, or _by.
    """
    key_lower = key.lower()
    return (
        'id' in key_lower
        or 'guid' in key_lower
        or key_lower.endswith('_id')
        or key_lower.endswith('_ids')
        or key_lower.endswith('_by')
    )

def _is_empty_value(value: Any) -> bool:
    """
    Determine if a value is considered "empty" for removal.
    This includes:
     - None
     - Empty string
     - String "null" (case-insensitive)
     - Empty list or dict
    """
    if value is None:
        return True
    if isinstance(value, str):
        if not value.strip() or value.lower() == "null":
            return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False