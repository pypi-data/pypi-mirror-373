""" Serialize to json Methods"""
import json
from typing import Any


def serialize_list_to_json(list_to_serialize : list) -> list:
    """Serialize a list into a json object

    Args:
        list_to_serialize (list): List to convert into a json list

    Returns:
        list: Json list, made of serialized objects.
    """
    if len(list_to_serialize) < 1:
        return []

    serialized_list = list()
    for element in list_to_serialize:
        serialized_list.append(element.to_json())

    return serialized_list

def get_json_from_file(file_path: str) -> Any:
    """Get the json context object, from the json file
    Args:
        file_path (str): Path to the json file.
    Returns:
        Any: Json object from the file, or empty dict if error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except TypeError as e:
        print(f"Type error while processing file: '{file_path}'. Error: '{e}'")
        return {}
    except FileNotFoundError as e:
        print(f"File not found: '{file_path}'. Exception: '{e}'")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file: '{file_path}'. Exception: '{e}'")
        return {}
    finally:
        if 'file' in locals():
             file.close()