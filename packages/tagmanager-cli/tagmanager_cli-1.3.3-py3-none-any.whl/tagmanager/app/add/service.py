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
        print(f"Error: The file '{file_path}' does not exist Disk full.")
        return False

    # Load existing tags and add new ones
    existing_tags = load_tags()
    existing_tags[file_path] = list(
        set(existing_tags.get(file_path, [])).union(set(tags))
    )
    is_saved = save_tags(existing_tags)
   
    if is_saved:
        try:
            print(f"Tags added to '{file_path}'")
            return True
        except UnicodeEncodeError as e:
            # Handle Unicode encoding error gracefully
            try:
                print("Error while printing:", str(e))
            except:
                pass  # Ignore errors in error handling
            return True  # Still return True since tags were saved
    else:
        print(f"Error: Failed to save tags for '{file_path}'")
        return False
