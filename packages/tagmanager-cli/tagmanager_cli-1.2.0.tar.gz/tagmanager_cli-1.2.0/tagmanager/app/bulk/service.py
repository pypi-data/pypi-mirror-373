import os
import glob
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import fnmatch

from ..helpers import load_tags, save_tags


def find_files_by_pattern(pattern: str, base_path: str = ".") -> List[str]:
    """
    Find files matching a glob pattern.
    
    :param pattern: Glob pattern (e.g., "*.py", "**/*.txt")
    :param base_path: Base directory to search from
    :return: List of absolute file paths
    """
    # Convert to absolute path
    base_path = os.path.abspath(base_path)
    
    # Handle different pattern types
    if pattern.startswith("**/"):
        # Recursive pattern
        search_pattern = os.path.join(base_path, pattern)
        files = glob.glob(search_pattern, recursive=True)
    elif "/" in pattern or "\\" in pattern:
        # Pattern with path
        if not os.path.isabs(pattern):
            search_pattern = os.path.join(base_path, pattern)
        else:
            search_pattern = pattern
        files = glob.glob(search_pattern, recursive=True)
    else:
        # Simple pattern, search recursively
        search_pattern = os.path.join(base_path, "**", pattern)
        files = glob.glob(search_pattern, recursive=True)
    
    # Filter out directories, return only files
    return [f for f in files if os.path.isfile(f)]


def bulk_add_tags(pattern: str, tags: List[str], base_path: str = ".", dry_run: bool = False) -> Dict:
    """
    Add tags to all files matching a pattern.
    
    :param pattern: File pattern to match
    :param tags: List of tags to add
    :param base_path: Base directory to search from
    :param dry_run: If True, don't actually modify tags, just show what would be done
    :return: Dictionary with operation results
    """
    # Find matching files
    matching_files = find_files_by_pattern(pattern, base_path)
    
    if not matching_files:
        return {
            'success': False,
            'message': f'No files found matching pattern: {pattern}',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    if dry_run:
        return {
            'success': True,
            'message': f'Would add tags {tags} to {len(matching_files)} files',
            'files_processed': len(matching_files),
            'files_found': matching_files,
            'dry_run': True
        }
    
    # Load existing tags
    data = load_tags()
    files_modified = 0
    
    # Add tags to each matching file
    for file_path in matching_files:
        # Normalize path
        normalized_path = os.path.normpath(file_path)
        
        # Get existing tags or create empty list
        existing_tags = data.get(normalized_path, [])
        
        # Add new tags (avoid duplicates)
        updated_tags = list(existing_tags)
        for tag in tags:
            if tag not in updated_tags:
                updated_tags.append(tag)
        
        # Update if tags were added
        if len(updated_tags) > len(existing_tags):
            data[normalized_path] = updated_tags
            files_modified += 1
    
    # Save updated tags
    if files_modified > 0:
        save_success = save_tags(data)
        if not save_success:
            return {
                'success': False,
                'message': 'Failed to save tags',
                'files_processed': 0,
                'files_found': matching_files,
                'dry_run': False
            }
    
    return {
        'success': True,
        'message': f'Added tags {tags} to {files_modified} files',
        'files_processed': files_modified,
        'files_found': matching_files,
        'dry_run': False
    }


def bulk_remove_by_tag(tag: str, dry_run: bool = False) -> Dict:
    """
    Remove all files that have a specific tag.
    
    :param tag: Tag to search for and remove files
    :param dry_run: If True, don't actually modify tags, just show what would be done
    :return: Dictionary with operation results
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    # Find files with the specified tag (case-insensitive)
    files_to_remove = []
    for file_path, tags in data.items():
        if any(t.lower() == tag.lower() for t in tags):
            files_to_remove.append(file_path)
    
    if not files_to_remove:
        return {
            'success': False,
            'message': f'No files found with tag: {tag}',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    if dry_run:
        return {
            'success': True,
            'message': f'Would remove {len(files_to_remove)} files with tag: {tag}',
            'files_processed': len(files_to_remove),
            'files_found': files_to_remove,
            'dry_run': True
        }
    
    # Remove files from tags
    files_removed = 0
    for file_path in files_to_remove:
        if file_path in data:
            del data[file_path]
            files_removed += 1
    
    # Save updated tags
    if files_removed > 0:
        save_success = save_tags(data)
        if not save_success:
            return {
                'success': False,
                'message': 'Failed to save tags',
                'files_processed': 0,
                'files_found': files_to_remove,
                'dry_run': False
            }
    
    return {
        'success': True,
        'message': f'Removed {files_removed} files with tag: {tag}',
        'files_processed': files_removed,
        'files_found': files_to_remove,
        'dry_run': False
    }


def bulk_retag(from_tag: str, to_tag: str, dry_run: bool = False) -> Dict:
    """
    Rename a tag across all files (replace old tag with new tag).
    
    :param from_tag: Current tag name to replace
    :param to_tag: New tag name
    :param dry_run: If True, don't actually modify tags, just show what would be done
    :return: Dictionary with operation results
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    # Find files with the old tag (case-insensitive)
    files_to_update = []
    for file_path, tags in data.items():
        if any(t.lower() == from_tag.lower() for t in tags):
            files_to_update.append(file_path)
    
    if not files_to_update:
        return {
            'success': False,
            'message': f'No files found with tag: {from_tag}',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    if dry_run:
        return {
            'success': True,
            'message': f'Would rename tag "{from_tag}" to "{to_tag}" in {len(files_to_update)} files',
            'files_processed': len(files_to_update),
            'files_found': files_to_update,
            'dry_run': True
        }
    
    # Update tags
    files_updated = 0
    for file_path in files_to_update:
        if file_path in data:
            tags = data[file_path]
            updated_tags = []
            tag_found = False
            
            for tag in tags:
                if tag.lower() == from_tag.lower():
                    # Replace with new tag (avoid duplicates)
                    if to_tag not in updated_tags:
                        updated_tags.append(to_tag)
                    tag_found = True
                else:
                    updated_tags.append(tag)
            
            if tag_found:
                data[file_path] = updated_tags
                files_updated += 1
    
    # Save updated tags
    if files_updated > 0:
        save_success = save_tags(data)
        if not save_success:
            return {
                'success': False,
                'message': 'Failed to save tags',
                'files_processed': 0,
                'files_found': files_to_update,
                'dry_run': False
            }
    
    return {
        'success': True,
        'message': f'Renamed tag "{from_tag}" to "{to_tag}" in {files_updated} files',
        'files_processed': files_updated,
        'files_found': files_to_update,
        'dry_run': False
    }


def bulk_remove_tag_from_files(tag: str, dry_run: bool = False) -> Dict:
    """
    Remove a specific tag from all files (but keep the files in the system).
    
    :param tag: Tag to remove from all files
    :param dry_run: If True, don't actually modify tags, just show what would be done
    :return: Dictionary with operation results
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    # Find files with the specified tag (case-insensitive)
    files_to_update = []
    for file_path, tags in data.items():
        if any(t.lower() == tag.lower() for t in tags):
            files_to_update.append(file_path)
    
    if not files_to_update:
        return {
            'success': False,
            'message': f'No files found with tag: {tag}',
            'files_processed': 0,
            'files_found': [],
            'dry_run': dry_run
        }
    
    if dry_run:
        return {
            'success': True,
            'message': f'Would remove tag "{tag}" from {len(files_to_update)} files',
            'files_processed': len(files_to_update),
            'files_found': files_to_update,
            'dry_run': True
        }
    
    # Remove tag from files
    files_updated = 0
    files_to_delete = []  # Files that end up with no tags
    
    for file_path in files_to_update:
        if file_path in data:
            tags = data[file_path]
            updated_tags = [t for t in tags if t.lower() != tag.lower()]
            
            if len(updated_tags) != len(tags):  # Tag was actually removed
                if updated_tags:
                    data[file_path] = updated_tags
                else:
                    # File has no tags left, mark for deletion
                    files_to_delete.append(file_path)
                files_updated += 1
    
    # Remove files with no tags
    for file_path in files_to_delete:
        del data[file_path]
    
    # Save updated tags
    if files_updated > 0:
        save_success = save_tags(data)
        if not save_success:
            return {
                'success': False,
                'message': 'Failed to save tags',
                'files_processed': 0,
                'files_found': files_to_update,
                'dry_run': False
            }
    
    message = f'Removed tag "{tag}" from {files_updated} files'
    if files_to_delete:
        message += f' ({len(files_to_delete)} files removed completely as they had no remaining tags)'
    
    return {
        'success': True,
        'message': message,
        'files_processed': files_updated,
        'files_found': files_to_update,
        'dry_run': False
    }
