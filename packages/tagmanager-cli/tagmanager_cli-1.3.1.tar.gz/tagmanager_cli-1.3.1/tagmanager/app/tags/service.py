import os
import sys
import re
from ..helpers import load_tags
from typing import List, Optional, Set


def get_system_command(file_path: str) -> Optional[str]:
    """ Returns the appropriate system command based on the OS. """
    if sys.platform.startswith('darwin'):
        return f"open {file_path}"
    elif sys.platform.startswith('win32'):
        return f"explorer {file_path}"
    elif sys.platform.startswith('linux'):
        return f"xdg-open {file_path}"
    else:
        return None


def open_file_or_directory(path: str) -> None:
    """ Opens a file or directory based on the provided path and OS. """
    if os.path.isdir(path):
        command = get_system_command(path)
        if command:
            os.system(command)
        else:
            print('Unsupported OS')
    elif os.path.isfile(path):
        if sys.platform.startswith('darwin'):
            os.system(f"open {path}")
        elif sys.platform.startswith('win32'):
            os.startfile(path)
        elif sys.platform.startswith('linux'):
            os.system(f"xdg-open {path}")
        else:
            print('Unsupported OS')
    else:
        print('Unsupported OS')


def display_menu(items: List[str]) -> str:
    """ Display a menu of items and prompt the user to make a selection. """
    print("Select a file to open:")
    for index, item in enumerate(items, start=1):
        print(f"{index}. {item}")
    print("q. Quit")
    return input("Enter choice: ")


def get_user_choice(items: List[str]) -> Optional[str]:
    """ Gets and validates the user's choice. """
    while True:
        choice = display_menu(items)
        if choice == 'q':
            return None
        try:
            choice_index = int(choice) - 1
            return items[choice_index]
        except (IndexError, ValueError):
            print("Invalid choice, try again.")


def open_list_files_by_tag_result(files: List[str], show_path: bool = False) -> Optional[str]:
    """ Opens a list of files based on the tag result. """
    if not files:
        print("No files found with that tag.")
        return None

    selected_file = get_user_choice(files)
    if selected_file and not show_path:
        open_file_or_directory(selected_file)
    return selected_file


def list_all_tags() -> List[str]:
    """ Lists all unique tags. """
    tags = load_tags()
    all_tags: Set[str] = set()
    for file_tags in tags.values():
        all_tags.update(file_tags)
    return sorted(list(all_tags))


def search_files_by_tag(tag: str, exact: bool = False) -> List[str]:
    """ Searches for files by tag. """
    tags = load_tags()
    matched_files: List[str] = []
    for file, file_tags in tags.items():
        if exact and tag in file_tags:
            matched_files.append(file)
        elif any(re.search(tag, file_tag, re.IGNORECASE) for file_tag in file_tags):
            matched_files.append(file)
    return matched_files


def search_tags(tag: str) -> List[str]:
    """ Searches for tags. """
    tags = load_tags()
    matched_tags: Set[str] = set()
    for file_tags in tags.values():
        matched_tags.update(
            file_tag for file_tag in file_tags if re.search(tag, file_tag, re.IGNORECASE)
        )
    return list(matched_tags)