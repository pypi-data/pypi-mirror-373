from ..helpers import load_tags
from ...configReader import config
from typing import List, Optional, Set


def search_files_by_tags(tags: List[str], match_all: bool = False, exact_match: bool = False) -> List[str]:
    """
    Search for files by tags.

    :param tags: A list of tags to search for.
    :param match_all: If True, only return files that match all tags.
    :param exact_match: If True, only return files that match tags exactly.
    :return: A list of files that match the tags.
    """
    data = load_tags()  # Assuming load_tags() fetches your data structure
    matched_files: Set[str] = set()

    for file, file_tags in data.items():
        if exact_match:
            # Use exact matching
            compare = lambda tag, file_tag: tag.lower() == file_tag.lower()
        else:
            # Use partial, case-insensitive matching
            compare = lambda tag, file_tag: tag.lower() in file_tag.lower()

        if match_all:
            if all(compare(tag, file_tag) for tag in tags for file_tag in file_tags):
                matched_files.add(file)
        else:
            if any(compare(tag, file_tag) for tag in tags for file_tag in file_tags):
                matched_files.add(file)

    file_or_path = config['LIST_ALL']['DISPLAY_FILE_AS']
    max_path_length = int(config['LIST_ALL']['MAX_PATH_LENGTH'])

    if file_or_path == 'FILENAME':
        for file in matched_files:
            matched_files.remove(file)
            matched_files.add(file.split('\\')[-1])

    for file in matched_files:
        if len(file) > max_path_length:
            matched_files.remove(file)
            matched_files.add(file[:max_path_length-3] + '...')
    return list(matched_files)


def search_files_by_path(query: str) -> List[str]:
    """
    Search for files whose paths contain the query.

    :param query: The path or part of the path to search for.
    :return: A list of files that match the path query.
    """
    data = load_tags()
    return [file for file in data if query.lower() in file.lower()]


def combined_search(tags: Optional[List[str]] = None,
                    path_query: Optional[str] = None,
                    match_all_tags: bool = False) -> List[str]:
    """
    Perform a combined search by tags and/or path.

    :param tags: A list of tags to search for.
    :param path_query: The path or part of the path to search for.
    :param match_all_tags: If True, only return files that match all tags.
    :return: A list of files that match the search criteria.
    """
    if not tags and not path_query:
        return []

    tag_matched_files = search_files_by_tags(tags, match_all_tags) if tags else load_tags().keys()
    path_matched_files = search_files_by_path(path_query) if path_query else load_tags().keys()

    return list(set(tag_matched_files) & set(path_matched_files))
