from .service import (
    get_overall_statistics,
    get_tag_statistics,
    get_file_count_distribution,
    format_overall_statistics,
    format_tag_statistics,
    format_file_count_distribution
)


def handle_stats_command(tag: str = None, file_count: bool = False):
    """
    Handle the stats command with different options.
    
    :param tag: Specific tag to analyze
    :param file_count: Whether to show file count distribution
    """
    if tag:
        # Show statistics for a specific tag
        stats = get_tag_statistics(tag)
        print(format_tag_statistics(stats))
    elif file_count:
        # Show file count distribution
        stats = get_file_count_distribution()
        print(format_file_count_distribution(stats))
    else:
        # Show overall statistics
        stats = get_overall_statistics()
        print(format_overall_statistics(stats))
