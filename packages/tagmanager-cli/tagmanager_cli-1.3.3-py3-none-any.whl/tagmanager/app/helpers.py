import json
import os
from ..config_manager import get_config


path = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(path)


def get_tag_file_path():
    """Get the tag file path from configuration, with fallback to legacy config"""
    try:
        # Try new configuration system first
        tag_path = get_config("storage.tag_file_path", "~/file_tags.json")
    except:
        # Fallback to legacy configuration
        from ..configReader import config

        tag_path = config["DEFAULT"]["TAG_FILE"]

    # Expand ~ to home directory
    return os.path.expanduser(tag_path)


TAG_FILE = get_tag_file_path()


def load_tags() -> dict:
    """
    Load tags from the tag file
    :return: json object of tags
    """
    if not os.path.exists(TAG_FILE):
        return {}
    try:
        with open(TAG_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, PermissionError, OSError):
        return {}


def save_tags(tags: dict) -> bool:
    """
    Save tags to the tag file in mode 'w' (overwrite) and encoding 'utf-8'
    :param tags: Tags to save in dict format {file_path: [tags]}
    :return: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(TAG_FILE), exist_ok=True)

        with open(TAG_FILE, "w", encoding="utf-8") as file:
            json.dump(tags, file, indent=4)
        return True
    
    except OSError as e:
        print(f"Error while saving tags Disk full: {e}")
        return False
    except Exception as e:
        print("Error while saving tags:", e)
        return False


def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalized_levenshtein_distance(s1, s2):
    if len(s1) == 0 and len(s2) == 0:
        return 1.0  # Both strings are empty, hence identical

    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    return (max_len - distance) / max_len
