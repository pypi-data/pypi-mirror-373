import typer
from .service import generate_tree_view, generate_tag_cloud, generate_stats_charts


def handle_tree_view():
    """Handle tree view visualization."""
    typer.echo(generate_tree_view())


def handle_tag_cloud():
    """Handle tag cloud visualization."""
    typer.echo(generate_tag_cloud())


def handle_stats_charts():
    """Handle statistics charts visualization."""
    typer.echo(generate_stats_charts())
