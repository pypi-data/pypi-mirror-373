import os
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import itertools

from ..helpers import load_tags


def find_duplicate_tags() -> Dict:
    """
    Find files that have identical tag sets.
    
    :return: Dictionary with duplicate analysis results
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'duplicates': {},
            'total_files': 0,
            'duplicate_groups': 0
        }
    
    # Group files by their tag sets (convert to sorted tuple for hashability)
    tag_groups = defaultdict(list)
    
    for file_path, tags in data.items():
        # Sort tags to ensure consistent grouping
        tag_signature = tuple(sorted(tags))
        tag_groups[tag_signature].append(file_path)
    
    # Find groups with more than one file (duplicates)
    duplicates = {
        tag_signature: files 
        for tag_signature, files in tag_groups.items() 
        if len(files) > 1
    }
    
    total_duplicate_files = sum(len(files) for files in duplicates.values())
    
    return {
        'success': True,
        'message': f'Found {len(duplicates)} groups with identical tags ({total_duplicate_files} files total)',
        'duplicates': duplicates,
        'total_files': len(data),
        'duplicate_groups': len(duplicates),
        'duplicate_files_count': total_duplicate_files
    }


def find_orphaned_files() -> Dict:
    """
    Find files that have no tags or empty tag lists.
    
    :return: Dictionary with orphaned files analysis
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No files found in tag system',
            'orphans': [],
            'total_files': 0,
            'orphan_count': 0
        }
    
    # Find files with no tags or empty tag lists
    orphans = []
    for file_path, tags in data.items():
        if not tags or len(tags) == 0:
            orphans.append(file_path)
    
    return {
        'success': True,
        'message': f'Found {len(orphans)} orphaned files (no tags)',
        'orphans': orphans,
        'total_files': len(data),
        'orphan_count': len(orphans)
    }


def calculate_tag_similarity(tags1: List[str], tags2: List[str]) -> float:
    """
    Calculate similarity between two tag sets using Jaccard similarity.
    
    :param tags1: First set of tags
    :param tags2: Second set of tags
    :return: Similarity score between 0 and 1
    """
    if not tags1 and not tags2:
        return 1.0
    
    if not tags1 or not tags2:
        return 0.0
    
    set1 = set(tag.lower() for tag in tags1)
    set2 = set(tag.lower() for tag in tags2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def find_similar_files(target_file: str, similarity_threshold: float = 0.3) -> Dict:
    """
    Find files with similar tags to a target file.
    
    :param target_file: Path to the target file
    :param similarity_threshold: Minimum similarity score (0-1)
    :return: Dictionary with similar files analysis
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'similar_files': [],
            'target_file': target_file,
            'target_tags': []
        }
    
    # Normalize target file path
    target_file = os.path.normpath(target_file)
    
    # Find target file in data (case-insensitive search)
    target_tags = None
    actual_target_path = None
    
    for file_path, tags in data.items():
        if os.path.normpath(file_path).lower() == target_file.lower():
            target_tags = tags
            actual_target_path = file_path
            break
    
    if target_tags is None:
        return {
            'success': False,
            'message': f'Target file not found in tag system: {target_file}',
            'similar_files': [],
            'target_file': target_file,
            'target_tags': []
        }
    
    if not target_tags:
        return {
            'success': False,
            'message': f'Target file has no tags: {target_file}',
            'similar_files': [],
            'target_file': actual_target_path,
            'target_tags': []
        }
    
    # Calculate similarity with all other files
    similar_files = []
    
    for file_path, tags in data.items():
        if file_path == actual_target_path:
            continue  # Skip the target file itself
        
        if not tags:
            continue  # Skip files with no tags
        
        similarity = calculate_tag_similarity(target_tags, tags)
        
        if similarity >= similarity_threshold:
            similar_files.append({
                'file_path': file_path,
                'tags': tags,
                'similarity': similarity,
                'common_tags': list(set(tag.lower() for tag in target_tags).intersection(
                    set(tag.lower() for tag in tags)
                )),
                'unique_tags': list(set(tag.lower() for tag in tags) - 
                                  set(tag.lower() for tag in target_tags))
            })
    
    # Sort by similarity (highest first)
    similar_files.sort(key=lambda x: x['similarity'], reverse=True)
    
    return {
        'success': True,
        'message': f'Found {len(similar_files)} files similar to {os.path.basename(actual_target_path)}',
        'similar_files': similar_files,
        'target_file': actual_target_path,
        'target_tags': target_tags,
        'similarity_threshold': similarity_threshold
    }


def find_tag_clusters(min_cluster_size: int = 2) -> Dict:
    """
    Find clusters of files that share common tags.
    
    :param min_cluster_size: Minimum number of files in a cluster
    :return: Dictionary with cluster analysis
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'clusters': {},
            'total_files': 0
        }
    
    # Count tag occurrences
    tag_to_files = defaultdict(list)
    
    for file_path, tags in data.items():
        for tag in tags:
            tag_to_files[tag.lower()].append(file_path)
    
    # Find clusters (tags with multiple files)
    clusters = {}
    for tag, files in tag_to_files.items():
        if len(files) >= min_cluster_size:
            clusters[tag] = {
                'files': files,
                'file_count': len(files),
                'percentage': (len(files) / len(data)) * 100
            }
    
    # Sort clusters by file count
    sorted_clusters = dict(sorted(clusters.items(), 
                                key=lambda x: x[1]['file_count'], 
                                reverse=True))
    
    return {
        'success': True,
        'message': f'Found {len(sorted_clusters)} tag clusters',
        'clusters': sorted_clusters,
        'total_files': len(data),
        'min_cluster_size': min_cluster_size
    }


def find_isolated_files(max_shared_tags: int = 1) -> Dict:
    """
    Find files that share very few tags with other files (isolated files).
    
    :param max_shared_tags: Maximum number of shared tags to be considered isolated
    :return: Dictionary with isolated files analysis
    """
    data = load_tags()
    
    if not data:
        return {
            'success': False,
            'message': 'No tagged files found',
            'isolated_files': [],
            'total_files': 0
        }
    
    isolated_files = []
    
    for target_file, target_tags in data.items():
        if not target_tags:
            continue
        
        max_shared = 0
        most_similar_file = None
        
        # Compare with all other files
        for other_file, other_tags in data.items():
            if target_file == other_file or not other_tags:
                continue
            
            # Count shared tags (case-insensitive)
            shared_count = len(set(tag.lower() for tag in target_tags).intersection(
                set(tag.lower() for tag in other_tags)
            ))
            
            if shared_count > max_shared:
                max_shared = shared_count
                most_similar_file = other_file
        
        # If this file shares few tags with others, it's isolated
        if max_shared <= max_shared_tags:
            isolated_files.append({
                'file_path': target_file,
                'tags': target_tags,
                'max_shared_tags': max_shared,
                'most_similar_file': most_similar_file
            })
    
    return {
        'success': True,
        'message': f'Found {len(isolated_files)} isolated files',
        'isolated_files': isolated_files,
        'total_files': len(data),
        'max_shared_tags': max_shared_tags
    }


def format_duplicates_result(result: Dict) -> str:
    """Format duplicate tags results for display."""
    output = []
    output.append("🔍 Duplicate Tags Analysis")
    output.append("=" * 50)
    output.append("")
    
    if not result['success']:
        output.append(f"❌ {result['message']}")
        return "\n".join(output)
    
    if result['duplicate_groups'] == 0:
        output.append("✅ No duplicate tag sets found!")
        output.append(f"📊 Analyzed {result['total_files']} files")
        return "\n".join(output)
    
    output.append(f"📊 Analysis Summary:")
    output.append(f"   Total files: {result['total_files']}")
    output.append(f"   Duplicate groups: {result['duplicate_groups']}")
    output.append(f"   Files with duplicates: {result['duplicate_files_count']}")
    output.append("")
    
    output.append("🔄 Duplicate Groups:")
    for i, (tag_signature, files) in enumerate(result['duplicates'].items(), 1):
        tags_display = ", ".join(tag_signature) if tag_signature else "No tags"
        output.append(f"   Group {i}: [{tags_display}]")
        for j, file_path in enumerate(files, 1):
            filename = os.path.basename(file_path)
            output.append(f"      {j}. {filename}")
        output.append("")
    
    return "\n".join(output)


def format_orphans_result(result: Dict) -> str:
    """Format orphaned files results for display."""
    output = []
    output.append("🏚️  Orphaned Files Analysis")
    output.append("=" * 50)
    output.append("")
    
    if not result['success']:
        output.append(f"❌ {result['message']}")
        return "\n".join(output)
    
    if result['orphan_count'] == 0:
        output.append("✅ No orphaned files found!")
        output.append(f"📊 All {result['total_files']} files have tags")
        return "\n".join(output)
    
    output.append(f"📊 Analysis Summary:")
    output.append(f"   Total files: {result['total_files']}")
    output.append(f"   Orphaned files: {result['orphan_count']}")
    output.append(f"   Percentage orphaned: {(result['orphan_count'] / result['total_files'] * 100):.1f}%")
    output.append("")
    
    output.append("🏚️  Orphaned Files:")
    for i, file_path in enumerate(result['orphans'], 1):
        filename = os.path.basename(file_path)
        output.append(f"   {i}. {filename}")
        if i >= 20:  # Limit display
            remaining = len(result['orphans']) - 20
            output.append(f"   ... and {remaining} more files")
            break
    
    return "\n".join(output)


def format_similar_result(result: Dict) -> str:
    """Format similar files results for display."""
    output = []
    target_name = os.path.basename(result['target_file']) if result['target_file'] else "Unknown"
    output.append(f"🔗 Similar Files to '{target_name}'")
    output.append("=" * 50)
    output.append("")
    
    if not result['success']:
        output.append(f"❌ {result['message']}")
        return "\n".join(output)
    
    if not result['similar_files']:
        output.append("❌ No similar files found!")
        output.append(f"📊 Target file tags: {', '.join(result['target_tags'])}")
        return "\n".join(output)
    
    output.append(f"📊 Target File: {target_name}")
    output.append(f"🏷️  Target Tags: {', '.join(result['target_tags'])}")
    output.append(f"🎯 Similarity Threshold: {result.get('similarity_threshold', 0.3):.1f}")
    output.append("")
    
    output.append(f"🔗 Similar Files ({len(result['similar_files'])} found):")
    for i, similar in enumerate(result['similar_files'], 1):
        filename = os.path.basename(similar['file_path'])
        similarity_pct = similar['similarity'] * 100
        output.append(f"   {i}. {filename} ({similarity_pct:.1f}% similar)")
        
        if similar['common_tags']:
            output.append(f"      🤝 Common: {', '.join(similar['common_tags'])}")
        if similar['unique_tags']:
            output.append(f"      ✨ Unique: {', '.join(similar['unique_tags'])}")
        output.append("")
        
        if i >= 10:  # Limit display
            remaining = len(result['similar_files']) - 10
            output.append(f"   ... and {remaining} more files")
            break
    
    return "\n".join(output)
