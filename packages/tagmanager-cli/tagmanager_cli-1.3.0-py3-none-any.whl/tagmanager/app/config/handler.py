"""
Configuration Management CLI Handler

Provides command-line interface for configuration operations.
"""

import json
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .service import (
    get_configuration_value,
    set_configuration_value,
    delete_configuration_value,
    list_configuration_values,
    reset_configuration,
    validate_configuration_key,
    get_configuration_info,
    export_configuration,
    import_configuration,
    _get_configuration_categories,
)

console = Console()


def handle_config_get(key: str) -> None:
    """Handle getting a configuration value"""
    if not validate_configuration_key(key):
        console.print(f"[red]Error: Unknown configuration key '{key}'[/red]")
        console.print("[yellow]Use 'tm config list' to see available keys[/yellow]")
        return
    
    value, is_default = get_configuration_value(key)
    
    if value is None:
        console.print(f"[yellow]Configuration key '{key}' is not set[/yellow]")
        return
    
    # Create a nice display
    status = "[dim](default)[/dim]" if is_default else "[green](user-set)[/green]"
    console.print(f"[bold]{key}[/bold] {status}")
    console.print(f"Value: [cyan]{value}[/cyan]")
    console.print(f"Type: [dim]{type(value).__name__}[/dim]")


def handle_config_set(key: str, value: str) -> None:
    """Handle setting a configuration value"""
    if not validate_configuration_key(key):
        console.print(f"[red]Error: Unknown configuration key '{key}'[/red]")
        console.print("[yellow]Use 'tm config list' to see available keys[/yellow]")
        return
    
    if set_configuration_value(key, value):
        console.print(f"[green]✓[/green] Set [bold]{key}[/bold] = [cyan]{value}[/cyan]")
    else:
        console.print(f"[red]✗[/red] Failed to set configuration value")


def handle_config_delete(key: str) -> None:
    """Handle deleting a configuration value"""
    if not validate_configuration_key(key):
        console.print(f"[red]Error: Unknown configuration key '{key}'[/red]")
        return
    
    if delete_configuration_value(key):
        console.print(f"[green]✓[/green] Deleted configuration key [bold]{key}[/bold]")
        console.print("[dim]Value will now use default[/dim]")
    else:
        console.print(f"[yellow]Configuration key '{key}' was not set[/yellow]")


def handle_config_list(
    category: Optional[str] = None,
    show_defaults: bool = False,
    output_format: str = "table"
) -> None:
    """Handle listing configuration values"""
    
    # Determine prefix based on category
    prefix = f"{category}." if category else ""
    
    # Validate category if provided
    if category and category not in _get_configuration_categories():
        console.print(f"[red]Error: Unknown category '{category}'[/red]")
        console.print(f"[yellow]Available categories: {', '.join(_get_configuration_categories())}[/yellow]")
        return
    
    config_data = list_configuration_values(prefix, show_defaults)
    
    if not config_data:
        if category:
            console.print(f"[yellow]No configuration values found in category '{category}'[/yellow]")
        else:
            console.print("[yellow]No configuration values set[/yellow]")
        
        if not show_defaults:
            console.print("[dim]Use --show-defaults to see default values[/dim]")
        return
    
    if output_format == "json":
        console.print(json.dumps(config_data, indent=2))
        return
    
    # Create table display
    table = Table(title="Configuration Settings" + (f" - {category.title()}" if category else ""))
    table.add_column("Key", style="bold")
    table.add_column("Value", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Description", style="dim", max_width=40)
    
    # Sort by key for consistent display
    for key in sorted(config_data.keys()):
        data = config_data[key]
        
        # Format value for display
        value_str = str(data['value'])
        if len(value_str) > 30:
            value_str = value_str[:27] + "..."
        
        # Status indicator
        status = "🔧 Default" if data['is_default'] else "✓ Set"
        
        table.add_row(
            key,
            value_str,
            data['type'],
            status,
            data['description']
        )
    
    console.print(table)
    
    # Show summary
    total_count = len(config_data)
    user_set_count = sum(1 for d in config_data.values() if not d['is_default'])
    default_count = total_count - user_set_count
    
    summary_text = f"Total: {total_count}"
    if show_defaults:
        summary_text += f" (User-set: {user_set_count}, Defaults: {default_count})"
    
    console.print(f"\n[dim]{summary_text}[/dim]")


def handle_config_reset(key: Optional[str] = None, confirm: bool = False) -> None:
    """Handle resetting configuration"""
    if key:
        # Reset specific key
        if not validate_configuration_key(key):
            console.print(f"[red]Error: Unknown configuration key '{key}'[/red]")
            return
        
        if not confirm:
            console.print(f"[yellow]This will reset '{key}' to its default value.[/yellow]")
            if not typer.confirm("Continue?"):
                console.print("Cancelled.")
                return
        
        if reset_configuration(key):
            console.print(f"[green]✓[/green] Reset [bold]{key}[/bold] to default value")
        else:
            console.print(f"[red]✗[/red] Failed to reset configuration key")
    
    else:
        # Reset all configuration
        if not confirm:
            console.print("[red]⚠️  This will reset ALL configuration to defaults![/red]")
            console.print("[yellow]All your custom settings will be lost.[/yellow]")
            if not typer.confirm("Are you sure?"):
                console.print("Cancelled.")
                return
        
        if reset_configuration():
            console.print("[green]✓[/green] Reset all configuration to defaults")
        else:
            console.print("[red]✗[/red] Failed to reset configuration")


def handle_config_info() -> None:
    """Handle showing configuration system information"""
    info = get_configuration_info()
    
    # Create info panel
    info_text = f"""
[bold]Configuration Directory:[/bold] {info['config_dir']}
[bold]Configuration File:[/bold] {info['config_file']}
[bold]File Exists:[/bold] {'✓ Yes' if info['config_exists'] else '✗ No'}
[bold]Settings Count:[/bold] {info['total_settings']}
[bold]Available Keys:[/bold] {info['available_keys']}
[bold]Categories:[/bold] {', '.join(info['config_categories'])}
    """.strip()
    
    panel = Panel(
        info_text,
        title="Configuration System Information",
        border_style="blue"
    )
    
    console.print(panel)


def handle_config_export(file_path: Optional[str] = None) -> None:
    """Handle exporting configuration"""
    try:
        exported_path = export_configuration(file_path)
        console.print(f"[green]✓[/green] Configuration exported to: [cyan]{exported_path}[/cyan]")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to export configuration: {e}")


def handle_config_import(file_path: str, merge: bool = True) -> None:
    """Handle importing configuration"""
    try:
        if import_configuration(file_path, merge):
            action = "merged" if merge else "replaced"
            console.print(f"[green]✓[/green] Configuration {action} from: [cyan]{file_path}[/cyan]")
        else:
            console.print(f"[red]✗[/red] Failed to import configuration")
    except FileNotFoundError:
        console.print(f"[red]✗[/red] Configuration file not found: {file_path}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to import configuration: {e}")


def handle_config_categories() -> None:
    """Handle showing configuration categories"""
    categories = _get_configuration_categories()
    
    console.print("[bold]Configuration Categories:[/bold]")
    for category in categories:
        console.print(f"  • [cyan]{category}[/cyan]")
    
    console.print(f"\n[dim]Use 'tm config list --category <name>' to see category settings[/dim]")


def handle_config_validate() -> None:
    """Handle validating current configuration"""
    config_data = list_configuration_values(show_defaults=False)
    
    if not config_data:
        console.print("[green]✓[/green] No user configuration to validate")
        return
    
    console.print("[bold]Validating configuration...[/bold]")
    
    valid_count = 0
    invalid_count = 0
    
    for key, data in config_data.items():
        try:
            # Re-validate the current value
            from ...config_manager import get_config_manager
            config_manager = get_config_manager()
            config_manager._validate_value(key, data['value'])
            
            console.print(f"[green]✓[/green] {key}")
            valid_count += 1
            
        except Exception as e:
            console.print(f"[red]✗[/red] {key}: {e}")
            invalid_count += 1
    
    # Summary
    console.print(f"\n[bold]Validation Summary:[/bold]")
    console.print(f"Valid: [green]{valid_count}[/green]")
    console.print(f"Invalid: [red]{invalid_count}[/red]")
    
    if invalid_count > 0:
        console.print(f"\n[yellow]Use 'tm config reset <key>' to fix invalid values[/yellow]")
