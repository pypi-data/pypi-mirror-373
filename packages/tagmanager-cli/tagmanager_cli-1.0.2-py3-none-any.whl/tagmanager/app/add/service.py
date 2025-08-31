import os
from ..helpers import load_tags, save_tags


def add_tags(file_path: str, tags: list) -> bool:
    """
    Takes an existing file path and adds tags to it. If the file path does not exist, it will return False.
    :param file_path: that is already in the tag file
    :param tags: non-empty list of tags to add
    :return: True if successful, False otherwise
    """
    file_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return False

    existing_tags = load_tags()
    existing_tags[file_path] = list(set(existing_tags.get(file_path, [])).union(set(tags)))
    save_tags(existing_tags)

    try:
        print(f"Tags added to '{file_path}'\n".encode('utf-8', 'replace').decode('utf-8'))
        return True
    except UnicodeEncodeError as e:
        print("Error while printing:", e)
        return False
