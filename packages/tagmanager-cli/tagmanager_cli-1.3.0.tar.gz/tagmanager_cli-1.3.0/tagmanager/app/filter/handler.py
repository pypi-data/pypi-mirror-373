from typing import Optional
import typer

from .service import (
    find_duplicate_tags,
    find_orphaned_files,
    find_similar_files,
    find_tag_clusters,
    find_isolated_files,
    format_duplicates_result,
    format_orphans_result,
    format_similar_result
)


def handle_filter_duplicates():
    """Handle filter duplicates command."""
    result = find_duplicate_tags()
    typer.echo(format_duplicates_result(result))


def handle_filter_orphans():
    """Handle filter orphans command."""
    result = find_orphaned_files()
    typer.echo(format_orphans_result(result))


def handle_filter_similar(file_path: str, threshold: float = 0.3):
    """Handle filter similar command."""
    if threshold < 0 or threshold > 1:
        typer.echo("❌ Similarity threshold must be between 0.0 and 1.0")
        return
    
    result = find_similar_files(file_path, threshold)
    typer.echo(format_similar_result(result))


def handle_filter_clusters(min_size: int = 2):
    """Handle filter clusters command."""
    if min_size < 2:
        typer.echo("❌ Minimum cluster size must be at least 2")
        return
    
    result = find_tag_clusters(min_size)
    
    output = []
    output.append("🎯 Tag Clusters Analysis")
    output.append("=" * 50)
    output.append("")
    
    if not result['success']:
        output.append(f"❌ {result['message']}")
        typer.echo("\n".join(output))
        return
    
    if not result['clusters']:
        output.append("❌ No tag clusters found!")
        output.append(f"📊 Try reducing minimum cluster size (current: {min_size})")
        typer.echo("\n".join(output))
        return
    
    output.append(f"📊 Analysis Summary:")
    output.append(f"   Total files: {result['total_files']}")
    output.append(f"   Tag clusters found: {len(result['clusters'])}")
    output.append(f"   Minimum cluster size: {min_size}")
    output.append("")
    
    output.append("🎯 Tag Clusters:")
    for i, (tag, info) in enumerate(result['clusters'].items(), 1):
        output.append(f"   {i}. '{tag}' - {info['file_count']} files ({info['percentage']:.1f}%)")
        
        # Show first few files
        for j, file_path in enumerate(info['files'][:5], 1):
            import os
            filename = os.path.basename(file_path)
            output.append(f"      {j}. {filename}")
        
        if len(info['files']) > 5:
            remaining = len(info['files']) - 5
            output.append(f"      ... and {remaining} more files")
        output.append("")
        
        if i >= 10:  # Limit display
            remaining = len(result['clusters']) - 10
            output.append(f"   ... and {remaining} more clusters")
            break
    
    typer.echo("\n".join(output))


def handle_filter_isolated(max_shared: int = 1):
    """Handle filter isolated command."""
    if max_shared < 0:
        typer.echo("❌ Maximum shared tags must be 0 or greater")
        return
    
    result = find_isolated_files(max_shared)
    
    output = []
    output.append("🏝️  Isolated Files Analysis")
    output.append("=" * 50)
    output.append("")
    
    if not result['success']:
        output.append(f"❌ {result['message']}")
        typer.echo("\n".join(output))
        return
    
    if not result['isolated_files']:
        output.append("✅ No isolated files found!")
        output.append(f"📊 All files share more than {max_shared} tag(s) with others")
        typer.echo("\n".join(output))
        return
    
    output.append(f"📊 Analysis Summary:")
    output.append(f"   Total files: {result['total_files']}")
    output.append(f"   Isolated files: {len(result['isolated_files'])}")
    output.append(f"   Max shared tags threshold: {max_shared}")
    output.append("")
    
    output.append("🏝️  Isolated Files:")
    for i, isolated in enumerate(result['isolated_files'], 1):
        import os
        filename = os.path.basename(isolated['file_path'])
        output.append(f"   {i}. {filename}")
        output.append(f"      🏷️  Tags: {', '.join(isolated['tags'])}")
        output.append(f"      🔗 Max shared: {isolated['max_shared_tags']} tags")
        
        if isolated['most_similar_file']:
            similar_name = os.path.basename(isolated['most_similar_file'])
            output.append(f"      👥 Most similar: {similar_name}")
        output.append("")
        
        if i >= 10:  # Limit display
            remaining = len(result['isolated_files']) - 10
            output.append(f"   ... and {remaining} more files")
            break
    
    typer.echo("\n".join(output))
