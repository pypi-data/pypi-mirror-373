from ..helpers import load_tags, save_tags
import os


def remove_path(file_path: str) -> None:
    """
    Remove a file path from the tags file
    :param file_path: that you want to remove
    :return: None
    """

    #
    path = os.path.abspath(file_path)
    tags = load_tags()
    popped_tags = tags.pop(path, None)
    if popped_tags is None:
        print(f"Could not find {path} in TagManager")
        return None
    save_tags(tags)
    print(f"Removed {path} from TagManager")

    return None


def remove_invalid_paths() -> None:
    """
    Remove invalid paths from the tags file
    :return: None
    """
    to_remove = []
    tags = load_tags()
    for file_path in list(tags.keys()):
        if not os.path.exists(file_path):
            to_remove.append(file_path)
            tags.pop(file_path, None)
            print(f"Removed {file_path} from TagManager")

    if len(to_remove) == 0:
        print("No invalid paths found")
        return None

    save_tags(tags)
    return None


