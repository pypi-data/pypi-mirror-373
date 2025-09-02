import json
from typing import List, Dict


def read_jsonl_file(file_path: str) -> List[Dict]:
    """
    Reads a JSON Lines (JSONL) file and returns its content
    as a list of dictionaries.

    Args:
        file_path (str): The path to the JSONL file.

    Returns:
        List[Dict]: A list of dictionaries,
                    one for each JSON object in the file.
    """
    result = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  # Ignore empty lines
                    result.append(json.loads(line))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Error reading or parsing file {file_path}: {e}")
    return result
