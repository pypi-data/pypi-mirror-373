import os
from ..helpers import load_tags, save_tags, normalized_levenshtein_distance


def path_tags(file_path: str) -> list:
    """
    List tags of a file by file path
    :param file_path: that you want to list tags for
    :return: list of tags for the file
    """
    file_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
    print(file_path)
    tags = load_tags()
    # find with
    return tags.get(file_path, [])


def fuzzy_search_path(search_query: str) -> str:
    """
    Search tags by fuzzy search using normalized levenshtein distance.
    Returns the most similar file path as a string.
    :param search_query: String to search for
    :return: The file path that is most similar to the search query
    """
    try:
        tags = load_tags()  # Ensure this function is defined and returns a dictionary
    except Exception as e:
        print(f"Error loading tags: {e}")
        return ""

    if not tags:
        return ""

    dist = []
    for file_path in tags.keys():
        similarity = normalized_levenshtein_distance(search_query, file_path)
        dist.append((similarity, file_path))

    # Sort by descending similarity
    dist.sort(key=lambda tup: -tup[0])

    # Return the top result as a string, or an empty string if no results
    return dist[0][1] if dist else ""





