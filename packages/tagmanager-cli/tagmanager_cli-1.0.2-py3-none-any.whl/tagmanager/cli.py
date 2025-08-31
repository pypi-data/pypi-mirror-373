#!/usr/bin/env python3
"""
TagManager CLI Entry Point

This module provides the main entry point for the TagManager CLI application.
"""

import sys
from typing import List, Optional

import typer

from .app.add.service import add_tags
from .app.bulk.handler import handle_bulk_add, handle_bulk_remove, handle_bulk_retag
from .app.filter.handler import (
    handle_filter_duplicates, handle_filter_orphans, handle_filter_similar,
    handle_filter_clusters, handle_filter_isolated
)
from .app.list_all.service import print_list_tags_all_table
from .app.paths.service import path_tags, fuzzy_search_path
from .app.remove.service import remove_path, remove_invalid_paths
from .app.search.service import combined_search, search_files_by_path, search_files_by_tags
from .app.stats.handler import handle_stats_command
from .app.storage.service import show_storage_location, open_storage_location
from .app.tags.service import list_all_tags, search_files_by_tag, open_list_files_by_tag_result
from .app.visualization.handler import handle_tree_view, handle_tag_cloud, handle_stats_charts


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

app = typer.Typer(
    name="tm",
    help="TagManager - The Ultimate Command-Line File Tagging System",
    no_args_is_help=True
)


@app.command()
def add(
    file: str = typer.Argument(..., help="Path to the file"),
    tags: List[str] = typer.Option(..., "-t", "--tags", help="Tags to add")
):
    """Add tags to a file"""
    add_tags(file, tags)


@app.command()
def remove(
    path: Optional[str] = typer.Option(None, "-p", "--path", help="Path to the file"),
    invalid: bool = typer.Option(False, "-i", "--invalid", help="Remove invalid paths from tags")
):
    """Remove path from tags"""
    if path:
        remove_path(path)
    elif invalid:
        remove_invalid_paths()
    else:
        typer.echo("No arguments provided")


@app.command("ls")
def list_all(
    all: Optional[str] = typer.Option(None, "--all", help="Not implemented"),
    ext: Optional[str] = typer.Option(None, "--ext", help="Not implemented"),
    tree: bool = typer.Option(False, "--tree", help="Display files in tree view")
):
    """List files and tags in a table or tree view"""
    if tree:
        handle_tree_view()
    else:
        print_list_tags_all_table()


@app.command()
def path(
    filepath: str = typer.Argument(..., help="Path to the file"),
    fuzzy: bool = typer.Option(False, "-f", "--fuzzy", help="Type of search to use"),
    folder: bool = typer.Option(False, "-F", "--folder", help="Search for a folder instead of a file"),
    exact: bool = typer.Option(False, "-e", "--exact", help="Exact match for file path")
):
    """List tags of a file"""
    if fuzzy:
        print(fuzzy_search_path(filepath))
    else:
        print(path_tags(filepath))


@app.command()
def tags(
    search: Optional[str] = typer.Option(None, "-s", "--search", help="List files by a specific tag"),
    open: bool = typer.Option(False, "-o", "--open", help="Open the file"),
    exact: bool = typer.Option(False, "-e", "--exact", help="Exact match for tag"),
    where: bool = typer.Option(False, "-w", "--where", help="Display the path of the file"),
    cloud: bool = typer.Option(False, "--cloud", help="Display tags as a visual cloud")
):
    """List all tags or display as a cloud"""
    if cloud:
        handle_tag_cloud()
    elif search and open:
        open_list_files_by_tag_result(
            search_files_by_tag(search, exact)
        )
    elif search:
        result = search_files_by_tag(search, exact)
        for i, file in enumerate(result, start=1):
            print(f"{i}. {file}")
    else:
        for i, tag in enumerate(list_all_tags(), start=1):
            print(f"{i}. {tag}")


@app.command()
def storage(
    open: bool = typer.Option(False, "-o", "--open", help="Open the storage location")
):
    """Display storage location of the tag file"""
    if open:
        open_storage_location()
    else:
        print(show_storage_location())


@app.command()
def search(
    tags: Optional[List[str]] = typer.Option(None, "-t", "--tags", help="List of tags to search for"),
    path: Optional[str] = typer.Option(None, "-p", "--path", help="Path query to search for"),
    match_all: bool = typer.Option(False, "-a", "--match_all", help="Match all specified tags (AND operation)"),
    exact: bool = typer.Option(False, "-e", "--exact", help="Exact match for tags"),
    open: bool = typer.Option(False, "-o", "--open", help="Open the file")
):
    """Search files by tags or path"""
    if tags and path:
        # Combined search by tags and path
        result = combined_search(tags, path, match_all)
    elif tags:
        # Search by tags only
        result = search_files_by_tags(tags, match_all, exact)
    elif path:
        # Search by path only
        result = search_files_by_path(path)
    else:
        typer.echo("No search criteria provided.")
        typer.echo("Example: tm search -t python -p C:\\Users\\User\\Documents")
        typer.echo("Example: tm search -t python -t linux")
        typer.echo("Example: tm search -p C:\\Users\\User\\Documents")
        typer.echo("Example: tm search -p C:\\Users\\User\\Documents -p C:\\Users\\User\\Downloads")
        return

    if result:
        for i, file in enumerate(result, start=1):
            print(f"{i}. {file}")
        print()
    else:
        print("No files found matching the criteria.")


# Create bulk subcommand group
bulk_app = typer.Typer(help="Bulk operations for managing tags")
app.add_typer(bulk_app, name="bulk")

# Create filter subcommand group
filter_app = typer.Typer(help="Smart filtering and analysis of tagged files")
app.add_typer(filter_app, name="filter")


@bulk_app.command("add")
def bulk_add(
    pattern: str = typer.Argument(..., help="File pattern to match (e.g., '*.py', '**/*.txt')"),
    tags: List[str] = typer.Option(..., "--tags", "-t", help="Tags to add to matching files"),
    base_path: str = typer.Option(".", "--path", "-p", help="Base directory to search from"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without making changes")
):
    """Add tags to all files matching a pattern"""
    handle_bulk_add(pattern, tags, base_path, dry_run)


@bulk_app.command("remove")
def bulk_remove(
    tag: Optional[str] = typer.Option(None, "--tag", help="Remove all files with this tag"),
    remove_tag: Optional[str] = typer.Option(None, "--remove-tag", help="Remove this tag from all files"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without making changes")
):
    """Remove files by tag or remove tag from all files"""
    handle_bulk_remove(tag, remove_tag, dry_run)


@bulk_app.command("retag")
def bulk_retag(
    from_tag: str = typer.Option(..., "--from", help="Current tag name to replace"),
    to_tag: str = typer.Option(..., "--to", help="New tag name"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be done without making changes")
):
    """Rename a tag across all files"""
    handle_bulk_retag(from_tag, to_tag, dry_run)


@filter_app.command("duplicates")
def filter_duplicates():
    """Find files with identical tag sets"""
    handle_filter_duplicates()


@filter_app.command("orphans")
def filter_orphans():
    """Find files with no tags"""
    handle_filter_orphans()


@filter_app.command("similar")
def filter_similar(
    file_path: str = typer.Argument(..., help="Path to the target file"),
    threshold: float = typer.Option(0.3, "--threshold", "-t", help="Similarity threshold (0.0-1.0)")
):
    """Find files with similar tags to a target file"""
    handle_filter_similar(file_path, threshold)


@filter_app.command("clusters")
def filter_clusters(
    min_size: int = typer.Option(2, "--min-size", "-s", help="Minimum number of files in a cluster")
):
    """Find clusters of files sharing common tags"""
    handle_filter_clusters(min_size)


@filter_app.command("isolated")
def filter_isolated(
    max_shared: int = typer.Option(1, "--max-shared", "-m", help="Maximum shared tags to be considered isolated")
):
    """Find files that share few tags with others"""
    handle_filter_isolated(max_shared)


@app.command()
def stats(
    tag: Optional[str] = typer.Option(None, "--tag", help="Show statistics for a specific tag"),
    file_count: bool = typer.Option(False, "--file-count", help="Show files per tag distribution"),
    chart: bool = typer.Option(False, "--chart", help="Display statistics as ASCII charts")
):
    """Show tag statistics and analytics"""
    if chart:
        handle_stats_charts()
    else:
        handle_stats_command(tag=tag, file_count=file_count)


def main():
    """Main entry point for the TagManager CLI."""
    app()


if __name__ == "__main__":
    main()
