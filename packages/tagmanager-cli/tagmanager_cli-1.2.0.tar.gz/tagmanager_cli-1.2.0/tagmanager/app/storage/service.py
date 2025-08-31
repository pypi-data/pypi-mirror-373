

from ...config_manager import get_config
import os


def get_tag_file_path():
    """Get the tag file path from configuration, with fallback to legacy config"""
    try:
        # Try new configuration system first
        tag_path = get_config('storage.tag_file_path', '~/file_tags.json')
    except:
        # Fallback to legacy configuration
        from ...configReader import config
        tag_path = config['DEFAULT']['TAG_FILE']
    
    # Expand ~ to home directory
    return os.path.expanduser(tag_path)


def show_storage_location():
    return get_tag_file_path()


def open_storage_location():
    tag_file = get_tag_file_path()
    if os.name == 'nt':  # Windows
        os.startfile(tag_file)
    elif os.name == 'posix':  # macOS and Linux
        os.system(f'open "{tag_file}"' if os.uname().sysname == 'Darwin' else f'xdg-open "{tag_file}"')