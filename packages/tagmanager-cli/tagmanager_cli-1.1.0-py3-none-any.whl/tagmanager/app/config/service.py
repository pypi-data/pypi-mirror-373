"""
Configuration Management Service

Provides business logic for configuration operations.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ...config_manager import get_config_manager, ConfigManager


def get_configuration_value(key: str) -> Tuple[Any, bool]:
    """
    Get a configuration value.
    
    Returns:
        Tuple of (value, is_default) where is_default indicates if using default value
    """
    config_manager = get_config_manager()
    
    # Check if key exists in user config
    user_config = config_manager.list_all()
    is_default = key not in user_config
    
    value = config_manager.get(key)
    return value, is_default


def set_configuration_value(key: str, value: str) -> bool:
    """
    Set a configuration value.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        config_manager = get_config_manager()
        config_manager.set(key, value)
        return True
    except Exception as e:
        print(f"Error setting configuration: {e}")
        return False


def delete_configuration_value(key: str) -> bool:
    """
    Delete a configuration value.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        config_manager = get_config_manager()
        return config_manager.delete(key)
    except Exception as e:
        print(f"Error deleting configuration: {e}")
        return False


def list_configuration_values(prefix: str = "", show_defaults: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    List configuration values with metadata.
    
    Returns:
        Dictionary with configuration data including values, defaults, and descriptions
    """
    config_manager = get_config_manager()
    
    # Get user configuration
    user_config = config_manager.list_all(prefix)
    
    # Get all possible configuration keys with defaults
    all_keys = _get_all_configuration_keys()
    
    result = {}
    
    # Process user-set values
    for key, value in user_config.items():
        if not prefix or key.startswith(prefix):
            result[key] = {
                'value': value,
                'is_default': False,
                'type': type(value).__name__,
                'description': _get_key_description(key),
            }
    
    # Add defaults if requested
    if show_defaults:
        for key in all_keys:
            if not prefix or key.startswith(prefix):
                if key not in result:
                    default_value = config_manager._get_default_value(key)
                    if default_value is not None:
                        result[key] = {
                            'value': default_value,
                            'is_default': True,
                            'type': type(default_value).__name__,
                            'description': _get_key_description(key),
                        }
    
    return result


def reset_configuration(key: Optional[str] = None) -> bool:
    """
    Reset configuration to defaults.
    
    Args:
        key: Specific key to reset, or None to reset all
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_manager = get_config_manager()
        config_manager.reset(key)
        return True
    except Exception as e:
        print(f"Error resetting configuration: {e}")
        return False


def validate_configuration_key(key: str) -> bool:
    """
    Validate if a configuration key is valid.
    
    Returns:
        True if valid, False otherwise
    """
    valid_keys = _get_all_configuration_keys()
    return key in valid_keys


def get_configuration_info() -> Dict[str, Any]:
    """
    Get information about the configuration system.
    
    Returns:
        Dictionary with configuration system information
    """
    config_manager = get_config_manager()
    info = config_manager.get_config_info()
    
    # Add additional information
    info.update({
        'available_keys': len(_get_all_configuration_keys()),
        'config_categories': _get_configuration_categories(),
    })
    
    return info


def export_configuration(file_path: Optional[str] = None) -> str:
    """
    Export configuration to a file.
    
    Args:
        file_path: Optional path to export file
        
    Returns:
        Path to exported file
    """
    config_manager = get_config_manager()
    export_path = Path(file_path) if file_path else None
    return config_manager.export_config(export_path)


def import_configuration(file_path: str, merge: bool = True) -> bool:
    """
    Import configuration from a file.
    
    Args:
        file_path: Path to configuration file
        merge: Whether to merge with existing config or replace
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config_manager = get_config_manager()
        config_manager.import_config(Path(file_path), merge)
        return True
    except Exception as e:
        print(f"Error importing configuration: {e}")
        return False


def _get_all_configuration_keys() -> List[str]:
    """Get all valid configuration keys"""
    return [
        # Display settings
        'display.emojis',
        'display.colors',
        'display.tree_icons',
        'display.max_items',
        
        # Search settings
        'search.fuzzy_threshold',
        'search.case_sensitive',
        'search.exact_match_default',
        
        # Tag settings
        'tags.max_per_file',
        'tags.separator',
        'tags.auto_create',
        'tags.validation',
        
        # File settings
        'files.follow_symlinks',
        'files.include_hidden',
        'files.max_size_mb',
        
        # Output settings
        'output.format',
        'output.date_format',
        'output.timezone',
        
        # Performance settings
        'performance.cache_enabled',
        'performance.cache_ttl',
        'performance.batch_size',
        
        # Backup settings
        'backup.auto_backup',
        'backup.count',
        'backup.on_bulk_operations',
        
        # Advanced settings
        'advanced.debug_mode',
        'advanced.log_level',
        'advanced.plugin_directory',
    ]


def _get_configuration_categories() -> List[str]:
    """Get configuration categories"""
    return [
        'display',
        'search', 
        'tags',
        'files',
        'output',
        'performance',
        'backup',
        'advanced'
    ]


def _get_key_description(key: str) -> str:
    """Get description for a configuration key"""
    descriptions = {
        # Display settings
        'display.emojis': 'Enable emoji icons in output',
        'display.colors': 'Enable colored output',
        'display.tree_icons': 'Show tree icons in tree view',
        'display.max_items': 'Maximum number of items to display',
        
        # Search settings
        'search.fuzzy_threshold': 'Fuzzy search similarity threshold (0.0-1.0)',
        'search.case_sensitive': 'Enable case-sensitive search by default',
        'search.exact_match_default': 'Use exact matching by default',
        
        # Tag settings
        'tags.max_per_file': 'Maximum number of tags per file',
        'tags.separator': 'Separator character for multiple tags',
        'tags.auto_create': 'Automatically create new tags',
        'tags.validation': 'Enable tag name validation',
        
        # File settings
        'files.follow_symlinks': 'Follow symbolic links when processing files',
        'files.include_hidden': 'Include hidden files in operations',
        'files.max_size_mb': 'Maximum file size to process (MB)',
        
        # Output settings
        'output.format': 'Default output format (table, json, csv, tree)',
        'output.date_format': 'Date format string',
        'output.timezone': 'Timezone for date display',
        
        # Performance settings
        'performance.cache_enabled': 'Enable caching for better performance',
        'performance.cache_ttl': 'Cache time-to-live in seconds',
        'performance.batch_size': 'Batch size for bulk operations',
        
        # Backup settings
        'backup.auto_backup': 'Automatically backup tag database',
        'backup.count': 'Number of backup files to keep',
        'backup.on_bulk_operations': 'Create backup before bulk operations',
        
        # Advanced settings
        'advanced.debug_mode': 'Enable debug mode with verbose output',
        'advanced.log_level': 'Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)',
        'advanced.plugin_directory': 'Directory for TagManager plugins',
    }
    
    return descriptions.get(key, 'No description available')
