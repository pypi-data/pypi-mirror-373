from ..helpers import load_tags
from ...configReader import config
import os

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box

def truncate(string, length):
    if length < 4:
        return string[:length]
    return (string[:length - 3] + '...') if len(string) > length else string

def print_list_tags_all_table():
    console = Console()
    display_file_as = config["LIST_ALL"]["DISPLAY_FILE_AS"]
    max_len_config = int(config["LIST_ALL"]["MAX_PATH_LENGTH"])
    tags = load_tags()

    if not tags:
        console.print(
            Panel.fit(
                "[bold yellow]No tagged files found![/bold yellow]\n\n"
                "Use [bold green]tm add <file> --tags <tag1> <tag2>[/bold green] to start tagging your files.",
                title="🏷️ TagManager",
                border_style="magenta"
            )
        )
        return

    # Dynamically determine max file and tag lengths for better fit
    file_lengths = [
        len(file) if display_file_as == "PATH" else len(os.path.split(file)[1])
        for file in tags
    ]
    max_file_len = min(max(file_lengths, default=10), max_len_config)
    tag_lengths = [len(tag) for file in tags for tag in tags[file]]
    max_tag_len = max(tag_lengths, default=10)
    max_tag_len = min(max_tag_len, 30)

    # Table style: use a more stylish box and row highlighting
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
        highlight=True,
        title="[bold blue]All Tagged Files[/bold blue]",
        caption="[dim]Tip: Use [green]tm tags[/green] to see all tags[/dim]"
    )
    table.add_column("File", style="bold cyan", no_wrap=True, max_width=max_file_len)
    table.add_column("Tags", style="bold green", overflow="fold")

    for file, file_tags in tags.items():
        truncated_tags = [
            f"[bold]{truncate(tag, max_tag_len)}[/bold]" if len(tag) == max_tag_len else tag
            for tag in file_tags
        ]
        display_file = file if display_file_as == "PATH" else os.path.split(file)[1]
        display_file = truncate(display_file, max_file_len)
        tags_str = ', '.join(truncated_tags) if truncated_tags else "[dim]No tags[/dim]"
        table.add_row(display_file, tags_str)

    console.print(table)
