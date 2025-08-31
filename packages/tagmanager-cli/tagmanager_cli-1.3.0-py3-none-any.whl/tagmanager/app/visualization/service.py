import os
import math
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from pathlib import Path

from ..helpers import load_tags


def create_tree_structure(files_with_tags: Dict[str, List[str]]) -> Dict:
    """
    Create a tree structure from file paths and their tags.
    
    :param files_with_tags: Dictionary of file paths and their tags
    :return: Tree structure for visualization
    """
    tree = {}
    
    for file_path, tags in files_with_tags.items():
        # Normalize path and split into parts
        normalized_path = os.path.normpath(file_path)
        path_parts = Path(normalized_path).parts
        
        # Build tree structure
        current_level = tree
        
        for i, part in enumerate(path_parts):
            if part not in current_level:
                current_level[part] = {
                    'type': 'directory' if i < len(path_parts) - 1 else 'file',
                    'children': {},
                    'tags': tags if i == len(path_parts) - 1 else [],
                    'path': os.path.join(*path_parts[:i+1])
                }
            current_level = current_level[part]['children']
    
    return tree


def render_tree(tree: Dict, prefix: str = "", is_last: bool = True, show_tags: bool = True) -> List[str]:
    """
    Render tree structure as ASCII art.
    
    :param tree: Tree structure to render
    :param prefix: Current prefix for indentation
    :param is_last: Whether this is the last item at current level
    :param show_tags: Whether to show tags for files
    :return: List of rendered lines
    """
    lines = []
    items = list(tree.items())
    
    for i, (name, node) in enumerate(items):
        is_last_item = i == len(items) - 1
        
        # Choose the appropriate tree characters
        if is_last_item:
            current_prefix = "└── "
            next_prefix = "    "
        else:
            current_prefix = "├── "
            next_prefix = "│   "
        
        # Format the current item
        if node['type'] == 'file':
            icon = "📄"
            if show_tags and node['tags']:
                tags_str = f" 🏷️  [{', '.join(node['tags'])}]"
            else:
                tags_str = ""
            line = f"{prefix}{current_prefix}{icon} {name}{tags_str}"
        else:
            icon = "📁"
            line = f"{prefix}{current_prefix}{icon} {name}/"
        
        lines.append(line)
        
        # Recursively render children
        if node['children']:
            child_lines = render_tree(
                node['children'], 
                prefix + next_prefix, 
                is_last_item,
                show_tags
            )
            lines.extend(child_lines)
    
    return lines


def create_tag_cloud_data(files_with_tags: Dict[str, List[str]]) -> List[Tuple[str, int, float]]:
    """
    Create tag cloud data with frequency and relative sizes.
    
    :param files_with_tags: Dictionary of file paths and their tags
    :return: List of tuples (tag, count, relative_size)
    """
    # Count tag frequencies
    tag_counter = Counter()
    for tags in files_with_tags.values():
        for tag in tags:
            tag_counter[tag] += 1
    
    if not tag_counter:
        return []
    
    # Calculate relative sizes (normalized to 1.0-5.0 scale)
    max_count = max(tag_counter.values())
    min_count = min(tag_counter.values())
    
    tag_data = []
    for tag, count in tag_counter.most_common():
        if max_count == min_count:
            relative_size = 3.0  # Default size if all tags have same frequency
        else:
            # Scale from 1.0 to 5.0
            relative_size = 1.0 + 4.0 * (count - min_count) / (max_count - min_count)
        
        tag_data.append((tag, count, relative_size))
    
    return tag_data


def render_tag_cloud(tag_data: List[Tuple[str, int, float]], width: int = 80) -> List[str]:
    """
    Render tag cloud as ASCII art with different sizes.
    
    :param tag_data: List of (tag, count, relative_size) tuples
    :param width: Maximum width for the cloud
    :return: List of rendered lines
    """
    if not tag_data:
        return ["No tags found."]
    
    lines = []
    current_line = ""
    current_length = 0
    
    # Size indicators
    size_chars = {
        1: "·",  # Smallest
        2: "•",
        3: "●",  # Medium
        4: "◆",
        5: "★"   # Largest
    }
    
    for tag, count, size in tag_data:
        # Determine size character
        size_level = min(5, max(1, round(size)))
        size_char = size_chars[size_level]
        
        # Format tag with size indicator and count
        tag_display = f"{size_char} {tag}({count})"
        
        # Check if we need a new line
        if current_length + len(tag_display) + 2 > width and current_line:
            lines.append(current_line.rstrip())
            current_line = ""
            current_length = 0
        
        # Add tag to current line
        if current_line:
            current_line += "  "
            current_length += 2
        
        current_line += tag_display
        current_length += len(tag_display)
    
    # Add the last line
    if current_line:
        lines.append(current_line.rstrip())
    
    return lines


def create_ascii_bar_chart(data: Dict[str, int], title: str = "Chart", max_width: int = 50) -> List[str]:
    """
    Create ASCII bar chart.
    
    :param data: Dictionary of labels and values
    :param title: Chart title
    :param max_width: Maximum width of bars
    :return: List of rendered lines
    """
    if not data:
        return [title, "No data available."]
    
    lines = [title, "=" * len(title), ""]
    
    # Find maximum value for scaling
    max_value = max(data.values())
    if max_value == 0:
        return lines + ["No data to display."]
    
    # Calculate label width for alignment
    max_label_width = max(len(str(label)) for label in data.keys())
    
    # Create bars
    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        # Calculate bar length
        bar_length = int((value / max_value) * max_width)
        bar = "█" * bar_length
        
        # Format line
        percentage = (value / sum(data.values())) * 100
        line = f"{str(label).ljust(max_label_width)} │{bar} {value} ({percentage:.1f}%)"
        lines.append(line)
    
    return lines


def create_ascii_histogram(data: List[int], title: str = "Histogram", bins: int = 10) -> List[str]:
    """
    Create ASCII histogram.
    
    :param data: List of numeric values
    :param title: Chart title
    :param bins: Number of bins
    :return: List of rendered lines
    """
    if not data:
        return [title, "No data available."]
    
    lines = [title, "=" * len(title), ""]
    
    # Calculate bins
    min_val = min(data)
    max_val = max(data)
    
    if min_val == max_val:
        lines.append(f"All values are {min_val}")
        return lines
    
    bin_width = (max_val - min_val) / bins
    bin_counts = [0] * bins
    
    # Count values in each bin
    for value in data:
        bin_index = min(bins - 1, int((value - min_val) / bin_width))
        bin_counts[bin_index] += 1
    
    # Find maximum count for scaling
    max_count = max(bin_counts)
    if max_count == 0:
        return lines + ["No data to display."]
    
    # Create histogram
    max_bar_width = 40
    for i, count in enumerate(bin_counts):
        bin_start = min_val + i * bin_width
        bin_end = min_val + (i + 1) * bin_width
        
        # Calculate bar length
        bar_length = int((count / max_count) * max_bar_width)
        bar = "█" * bar_length
        
        # Format bin range
        range_str = f"{bin_start:.1f}-{bin_end:.1f}"
        line = f"{range_str.ljust(12)} │{bar} {count}"
        lines.append(line)
    
    return lines


def generate_tree_view() -> str:
    """Generate tree view of all tagged files."""
    files_with_tags = load_tags()
    
    if not files_with_tags:
        return "📁 No tagged files found."
    
    # Create tree structure
    tree = create_tree_structure(files_with_tags)
    
    # Render tree
    lines = ["🌳 Tagged Files Tree View", "=" * 50, ""]
    
    if tree:
        tree_lines = render_tree(tree, show_tags=True)
        lines.extend(tree_lines)
    else:
        lines.append("No files to display.")
    
    lines.append("")
    lines.append(f"📊 Total files: {len(files_with_tags)}")
    
    return "\n".join(lines)


def generate_tag_cloud() -> str:
    """Generate tag cloud visualization."""
    files_with_tags = load_tags()
    
    if not files_with_tags:
        return "☁️  No tags found."
    
    # Create tag cloud data
    tag_data = create_tag_cloud_data(files_with_tags)
    
    lines = ["☁️  Tag Cloud", "=" * 50, ""]
    
    if tag_data:
        lines.append("Legend: ★ Most frequent  ◆ Very frequent  ● Frequent  • Less frequent  · Least frequent")
        lines.append("")
        
        cloud_lines = render_tag_cloud(tag_data, width=80)
        lines.extend(cloud_lines)
        
        lines.append("")
        lines.append(f"📊 Total unique tags: {len(tag_data)}")
        lines.append(f"📊 Total tag instances: {sum(count for _, count, _ in tag_data)}")
    else:
        lines.append("No tags to display.")
    
    return "\n".join(lines)


def generate_stats_charts() -> str:
    """Generate ASCII charts for statistics."""
    files_with_tags = load_tags()
    
    if not files_with_tags:
        return "📊 No data available for charts."
    
    lines = ["📊 TagManager Statistics Charts", "=" * 50, ""]
    
    # 1. Tags per file distribution
    tags_per_file = [len(tags) for tags in files_with_tags.values()]
    tag_count_distribution = Counter(tags_per_file)
    
    chart1_lines = create_ascii_bar_chart(
        {f"{count} tags": freq for count, freq in tag_count_distribution.items()},
        "📈 Files by Tag Count"
    )
    lines.extend(chart1_lines)
    lines.append("")
    
    # 2. Tag frequency chart
    all_tags = []
    for tags in files_with_tags.values():
        all_tags.extend(tags)
    
    tag_frequency = Counter(all_tags)
    top_tags = dict(tag_frequency.most_common(10))
    
    chart2_lines = create_ascii_bar_chart(
        top_tags,
        "🏷️  Top 10 Most Used Tags"
    )
    lines.extend(chart2_lines)
    lines.append("")
    
    # 3. Tag count histogram
    if len(tags_per_file) > 1:
        chart3_lines = create_ascii_histogram(
            tags_per_file,
            "📊 Tag Count Distribution Histogram"
        )
        lines.extend(chart3_lines)
        lines.append("")
    
    # 4. Summary statistics
    lines.append("📋 Summary Statistics")
    lines.append("=" * 20)
    lines.append(f"Total files: {len(files_with_tags)}")
    lines.append(f"Total unique tags: {len(set(all_tags))}")
    lines.append(f"Average tags per file: {len(all_tags) / len(files_with_tags):.2f}")
    lines.append(f"Most tagged file: {max(len(tags) for tags in files_with_tags.values())} tags")
    lines.append(f"Least tagged file: {min(len(tags) for tags in files_with_tags.values())} tags")
    
    return "\n".join(lines)
