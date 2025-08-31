from ..helpers import load_tags
from ...configReader import config
import os


def truncate(string, length):
    return (string[:length - 3] + '...') if len(string) > length else string


def print_list_tags_all_table():
    display_file_as = config["LIST_ALL"]["DISPLAY_FILE_AS"]
    max_len_config = int(config["LIST_ALL"]["MAX_PATH_LENGTH"])
    tags = load_tags()

    # Determine the maximum length for formatting
    file_lengths = [len(file) if display_file_as == "PATH" else len(os.path.split(file)[1]) for file in tags]
    max_file_len = min(max(file_lengths, default=0), max_len_config)

    max_tag_len = max((len(tag) for file in tags for tag in tags[file]), default=0)

    # Create header
    print(f"\n\n{'File'.ljust(max_file_len)} | Tags")
    print(f"{'-' * max_file_len}-+{'-' * max_tag_len}")

    # Print each file and its tags
    for file, file_tags in tags.items():
        truncated_tags = [truncate(tag, max_tag_len) for tag in file_tags]

        display_file = file if display_file_as == "PATH" else os.path.split(file)[1]
        display_file = truncate(display_file, max_file_len)

        tags_str = ', '.join(truncated_tags)
        print(f"{display_file.ljust(max_file_len)} | {tags_str}".encode('utf-8', 'replace').decode('utf-8'))
