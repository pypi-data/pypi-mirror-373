from typing import Dict, List, Tuple, Optional
from collections import Counter
import os
from datetime import datetime

from ..helpers import load_tags


def get_overall_statistics() -> Dict:
    """
    Get overall statistics about the tag system.
    
    :return: Dictionary containing overall statistics
    """
    data = load_tags()
    
    if not data:
        return {
            'total_files': 0,
            'total_tags': 0,
            'unique_tags': 0,
            'avg_tags_per_file': 0,
            'files_without_tags': 0,
            'most_common_tags': [],
            'least_common_tags': [],
            'tag_distribution': {}
        }
    
    # Basic counts
    total_files = len(data)
    all_tags = []
    files_without_tags = 0
    
    for file_path, tags in data.items():
        if not tags:
            files_without_tags += 1
        else:
            all_tags.extend(tags)
    
    total_tags = len(all_tags)
    unique_tags = len(set(all_tags))
    avg_tags_per_file = total_tags / total_files if total_files > 0 else 0
    
    # Tag frequency analysis
    tag_counter = Counter(all_tags)
    most_common_tags = tag_counter.most_common(10)
    least_common_tags = tag_counter.most_common()[:-11:-1] if len(tag_counter) > 10 else []
    
    # Tag distribution (how many files have 1 tag, 2 tags, etc.)
    tag_distribution = Counter(len(tags) for tags in data.values())
    
    return {
        'total_files': total_files,
        'total_tags': total_tags,
        'unique_tags': unique_tags,
        'avg_tags_per_file': round(avg_tags_per_file, 2),
        'files_without_tags': files_without_tags,
        'most_common_tags': most_common_tags,
        'least_common_tags': least_common_tags,
        'tag_distribution': dict(tag_distribution)
    }


def get_tag_statistics(tag_name: str) -> Dict:
    """
    Get statistics for a specific tag.
    
    :param tag_name: Name of the tag to analyze
    :return: Dictionary containing tag-specific statistics
    """
    data = load_tags()
    
    if not data:
        return {
            'tag_name': tag_name,
            'files_with_tag': 0,
            'percentage_of_files': 0,
            'files': [],
            'co_occurring_tags': [],
            'file_types': {}
        }
    
    # Find files with this tag (case-insensitive)
    files_with_tag = []
    co_occurring_tags = []
    
    for file_path, tags in data.items():
        # Case-insensitive tag matching
        matching_tags = [t for t in tags if t.lower() == tag_name.lower()]
        if matching_tags:
            files_with_tag.append(file_path)
            # Add other tags from the same file for co-occurrence analysis
            other_tags = [t for t in tags if t.lower() != tag_name.lower()]
            co_occurring_tags.extend(other_tags)
    
    total_files = len(data)
    files_count = len(files_with_tag)
    percentage = (files_count / total_files * 100) if total_files > 0 else 0
    
    # Analyze co-occurring tags
    co_occurring_counter = Counter(co_occurring_tags)
    top_co_occurring = co_occurring_counter.most_common(10)
    
    # Analyze file types
    file_types = Counter()
    for file_path in files_with_tag:
        if '.' in file_path:
            extension = file_path.split('.')[-1].lower()
            file_types[extension] += 1
        else:
            file_types['no_extension'] += 1
    
    return {
        'tag_name': tag_name,
        'files_with_tag': files_count,
        'percentage_of_files': round(percentage, 2),
        'files': files_with_tag,
        'co_occurring_tags': top_co_occurring,
        'file_types': dict(file_types)
    }


def get_file_count_distribution() -> Dict:
    """
    Get distribution of files per tag.
    
    :return: Dictionary with tag distribution statistics
    """
    data = load_tags()
    
    if not data:
        return {
            'tags_by_file_count': [],
            'distribution_summary': {},
            'total_tags': 0
        }
    
    # Count files for each tag
    tag_file_counts = Counter()
    
    for file_path, tags in data.items():
        for tag in tags:
            tag_file_counts[tag] += 1
    
    # Sort tags by file count (descending)
    tags_by_file_count = tag_file_counts.most_common()
    
    # Create distribution summary (how many tags have 1 file, 2 files, etc.)
    file_count_distribution = Counter(tag_file_counts.values())
    
    return {
        'tags_by_file_count': tags_by_file_count,
        'distribution_summary': dict(file_count_distribution),
        'total_tags': len(tag_file_counts)
    }


def format_overall_statistics(stats: Dict) -> str:
    """Format overall statistics for display."""
    output = []
    output.append("📊 Tag Manager Statistics")
    output.append("=" * 50)
    output.append("")
    
    # Basic stats
    output.append("📁 File Statistics:")
    output.append(f"   Total files: {stats['total_files']}")
    output.append(f"   Files without tags: {stats['files_without_tags']}")
    output.append("")
    
    # Tag stats
    output.append("🏷️  Tag Statistics:")
    output.append(f"   Total tags: {stats['total_tags']}")
    output.append(f"   Unique tags: {stats['unique_tags']}")
    output.append(f"   Average tags per file: {stats['avg_tags_per_file']}")
    output.append("")
    
    # Most common tags
    if stats['most_common_tags']:
        output.append("🔥 Most Popular Tags:")
        for tag, count in stats['most_common_tags'][:5]:
            output.append(f"   {tag}: {count} files")
        output.append("")
    
    # Tag distribution
    if stats['tag_distribution']:
        output.append("📈 Tag Distribution:")
        for tag_count, file_count in sorted(stats['tag_distribution'].items()):
            plural = "files" if file_count != 1 else "file"
            tag_plural = "tags" if tag_count != 1 else "tag"
            output.append(f"   {file_count} {plural} have {tag_count} {tag_plural}")
    
    return "\n".join(output)


def format_tag_statistics(stats: Dict) -> str:
    """Format tag-specific statistics for display."""
    output = []
    output.append(f"🏷️  Statistics for tag: '{stats['tag_name']}'")
    output.append("=" * 50)
    output.append("")
    
    if stats['files_with_tag'] == 0:
        output.append("❌ No files found with this tag.")
        return "\n".join(output)
    
    # Basic stats
    output.append("📊 Usage Statistics:")
    output.append(f"   Files with this tag: {stats['files_with_tag']}")
    output.append(f"   Percentage of all files: {stats['percentage_of_files']}%")
    output.append("")
    
    # File types
    if stats['file_types']:
        output.append("📄 File Types:")
        for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            ext_display = f".{ext}" if ext != 'no_extension' else 'no extension'
            output.append(f"   {ext_display}: {count} files")
        output.append("")
    
    # Co-occurring tags
    if stats['co_occurring_tags']:
        output.append("🤝 Often Used With:")
        for tag, count in stats['co_occurring_tags'][:5]:
            output.append(f"   {tag}: {count} times")
        output.append("")
    
    # Files list (limited)
    if stats['files']:
        output.append("📁 Files with this tag:")
        for i, file_path in enumerate(stats['files'][:10], 1):
            # Show just filename for readability
            filename = os.path.basename(file_path)
            output.append(f"   {i}. {filename}")
        
        if len(stats['files']) > 10:
            output.append(f"   ... and {len(stats['files']) - 10} more files")
    
    return "\n".join(output)


def format_file_count_distribution(stats: Dict) -> str:
    """Format file count distribution for display."""
    output = []
    output.append("📊 Files per Tag Distribution")
    output.append("=" * 50)
    output.append("")
    
    if stats['total_tags'] == 0:
        output.append("❌ No tags found.")
        return "\n".join(output)
    
    output.append(f"📈 Total tags: {stats['total_tags']}")
    output.append("")
    
    # Distribution summary
    if stats['distribution_summary']:
        output.append("📊 Distribution Summary:")
        for file_count, tag_count in sorted(stats['distribution_summary'].items()):
            plural_tags = "tags" if tag_count != 1 else "tag"
            plural_files = "files" if file_count != 1 else "file"
            output.append(f"   {tag_count} {plural_tags} have {file_count} {plural_files}")
        output.append("")
    
    # Top tags by file count
    if stats['tags_by_file_count']:
        output.append("🏆 Tags with Most Files:")
        for tag, count in stats['tags_by_file_count'][:10]:
            output.append(f"   {tag}: {count} files")
        
        if len(stats['tags_by_file_count']) > 10:
            output.append(f"   ... and {len(stats['tags_by_file_count']) - 10} more tags")
    
    return "\n".join(output)
