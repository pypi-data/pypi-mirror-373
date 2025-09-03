import json
import os


def load_file(file_path: str) -> list[dict]:
    """
    Load a .json file content that's stored in JSONL format.
    """
    result = []
    with open(file_path) as f:
        file = f.readlines()
        for line in file:
            result.append(json.loads(line))
    return result


def write_list_of_dicts_to_file(filename, data, subdir=None, append_mode=False) -> None:
    """
    Write a list of dictionaries to a file.
    If `subdir` is provided, the file will be written to the subdirectory.
    """
    if subdir:
        # Ensure the (possibly nested) subdirectory exists
        os.makedirs(subdir, exist_ok=True)

        # Construct the full path to the file
        filename = os.path.join(subdir, os.path.basename(filename))

    # Write the list of dictionaries to the file in JSON format
    with open(filename, "a" if append_mode else "w", encoding="utf-8") as f:
        for i, entry in enumerate(data):
            # Go through each key-value pair in the dictionary to make sure the values are JSON serializable
            entry = make_json_serializable(entry)
            json_str = json.dumps(entry, ensure_ascii=False) + "\n"
            f.write(json_str)


def make_json_serializable(value):
    if isinstance(value, dict):
        # If the value is a dictionary, we need to go through each key-value pair recursively
        return {k: make_json_serializable(v) for k, v in value.items()}
    elif isinstance(value, list):
        # If the value is a list, we need to process each element recursively
        return [make_json_serializable(item) for item in value]
    else:
        # Try to serialize the value directly, and if it fails, convert it to a string
        try:
            json.dumps(value, ensure_ascii=False)
            return value
        except (TypeError, ValueError):
            return str(value)
