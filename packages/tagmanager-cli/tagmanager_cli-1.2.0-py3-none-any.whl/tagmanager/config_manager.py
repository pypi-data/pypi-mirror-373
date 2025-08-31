#!/usr/bin/env python3
"""
TagManager Configuration Management System

Provides centralized configuration management with validation, defaults,
and easy CLI access to settings.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import configparser


@dataclass
class ConfigDefaults:
    """Default configuration values with descriptions"""
    
    # Display settings
    display_emojis: bool = True
    display_colors: bool = True
    display_tree_icons: bool = True
    max_display_items: int = 100
    
    # Search settings
    fuzzy_search_threshold: float = 0.6
    case_sensitive_search: bool = False
    exact_match_default: bool = False
    
    # Tag settings
    max_tags_per_file: int = 50
    tag_separator: str = " "
    auto_create_tags: bool = True
    tag_validation: bool = True
    
    # File settings
    follow_symlinks: bool = False
    include_hidden_files: bool = False
    max_file_size_mb: int = 100
    
    # Output settings
    output_format: str = "table"  # table, json, csv, tree
    date_format: str = "%Y-%m-%d %H:%M:%S"
    timezone: str = "local"
    
    # Performance settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    batch_size: int = 1000
    
    # Backup settings
    auto_backup: bool = True
    backup_count: int = 5
    backup_on_bulk_operations: bool = True
    
    # Storage settings
    tag_file_path: str = "~/file_tags.json"
    
    # Advanced settings
    debug_mode: bool = False
    log_level: str = "INFO"
    plugin_directory: str = ""


class ConfigManager:
    """Manages TagManager configuration with validation and persistence"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.legacy_config_file = self.config_dir / "config.ini"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._config = self._load_config()
        self._defaults = ConfigDefaults()
        
        # Migrate from legacy config if needed
        self._migrate_legacy_config()
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory"""
        if sys.platform.startswith('win'):
            config_dir = Path.home() / "AppData" / "Local" / "TagManager"
        else:
            config_dir = Path.home() / ".config" / "tagmanager"
        return config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                return {}
        return {}
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, sort_keys=True)
        except IOError as e:
            print(f"Error: Could not save config file: {e}")
    
    def _migrate_legacy_config(self) -> None:
        """Migrate from legacy INI config format"""
        if not self.legacy_config_file.exists():
            return
            
        try:
            legacy_config = configparser.ConfigParser()
            legacy_config.read(self.legacy_config_file)
            
            # Migrate known settings
            if 'DEFAULT' in legacy_config:
                section = legacy_config['DEFAULT']
                
                # Map legacy settings to new format
                legacy_mappings = {
                    'TAG_FILE': 'storage.tag_file',
                    'MAX_DISPLAY_ITEMS': 'display.max_display_items',
                    'FUZZY_THRESHOLD': 'search.fuzzy_search_threshold',
                }
                
                for legacy_key, new_key in legacy_mappings.items():
                    if legacy_key in section:
                        self.set(new_key, section[legacy_key])
            
            print(f"Migrated configuration from {self.legacy_config_file}")
            
        except Exception as e:
            print(f"Warning: Could not migrate legacy config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Try to get from defaults
            if default is None:
                default = self._get_default_value(key)
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Validate and convert value
        validated_value = self._validate_value(key, value)
        config[keys[-1]] = validated_value
        
        # Save configuration
        self._save_config()
    
    def delete(self, key: str) -> bool:
        """Delete configuration value"""
        keys = key.split('.')
        config = self._config
        
        try:
            # Navigate to parent
            for k in keys[:-1]:
                config = config[k]
            
            # Delete the key
            if keys[-1] in config:
                del config[keys[-1]]
                self._save_config()
                return True
            return False
        except (KeyError, TypeError):
            return False
    
    def list_all(self, prefix: str = "") -> Dict[str, Any]:
        """List all configuration values with optional prefix filter"""
        def flatten_dict(d: Dict, parent_key: str = "") -> Dict[str, Any]:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        flattened = flatten_dict(self._config)
        
        if prefix:
            return {k: v for k, v in flattened.items() if k.startswith(prefix)}
        return flattened
    
    def reset(self, key: Optional[str] = None) -> None:
        """Reset configuration to defaults"""
        if key is None:
            # Reset all configuration
            self._config = {}
            self._save_config()
        else:
            # Reset specific key
            default_value = self._get_default_value(key)
            if default_value is not None:
                self.set(key, default_value)
            else:
                self.delete(key)
    
    def _get_default_value(self, key: str) -> Any:
        """Get default value for a configuration key"""
        # Map configuration keys to default values
        key_mappings = {
            'display.emojis': self._defaults.display_emojis,
            'display.colors': self._defaults.display_colors,
            'display.tree_icons': self._defaults.display_tree_icons,
            'display.max_items': self._defaults.max_display_items,
            
            'search.fuzzy_threshold': self._defaults.fuzzy_search_threshold,
            'search.case_sensitive': self._defaults.case_sensitive_search,
            'search.exact_match_default': self._defaults.exact_match_default,
            
            'tags.max_per_file': self._defaults.max_tags_per_file,
            'tags.separator': self._defaults.tag_separator,
            'tags.auto_create': self._defaults.auto_create_tags,
            'tags.validation': self._defaults.tag_validation,
            
            'files.follow_symlinks': self._defaults.follow_symlinks,
            'files.include_hidden': self._defaults.include_hidden_files,
            'files.max_size_mb': self._defaults.max_file_size_mb,
            
            'output.format': self._defaults.output_format,
            'output.date_format': self._defaults.date_format,
            'output.timezone': self._defaults.timezone,
            
            'performance.cache_enabled': self._defaults.cache_enabled,
            'performance.cache_ttl': self._defaults.cache_ttl_seconds,
            'performance.batch_size': self._defaults.batch_size,
            
            'backup.auto_backup': self._defaults.auto_backup,
            'backup.count': self._defaults.backup_count,
            'backup.on_bulk_operations': self._defaults.backup_on_bulk_operations,
            
            'storage.tag_file_path': self._defaults.tag_file_path,
            
            'advanced.debug_mode': self._defaults.debug_mode,
            'advanced.log_level': self._defaults.log_level,
            'advanced.plugin_directory': self._defaults.plugin_directory,
        }
        
        return key_mappings.get(key)
    
    def _validate_value(self, key: str, value: Any) -> Any:
        """Validate and convert configuration value"""
        # Type validation based on key
        validations = {
            'display.emojis': bool,
            'display.colors': bool,
            'display.tree_icons': bool,
            'display.max_items': int,
            
            'search.fuzzy_threshold': float,
            'search.case_sensitive': bool,
            'search.exact_match_default': bool,
            
            'tags.max_per_file': int,
            'tags.separator': str,
            'tags.auto_create': bool,
            'tags.validation': bool,
            
            'files.follow_symlinks': bool,
            'files.include_hidden': bool,
            'files.max_size_mb': int,
            
            'output.format': str,
            'output.date_format': str,
            'output.timezone': str,
            
            'performance.cache_enabled': bool,
            'performance.cache_ttl': int,
            'performance.batch_size': int,
            
            'backup.auto_backup': bool,
            'backup.count': int,
            'backup.on_bulk_operations': bool,
            
            'storage.tag_file_path': str,
            
            'advanced.debug_mode': bool,
            'advanced.log_level': str,
            'advanced.plugin_directory': str,
        }
        
        expected_type = validations.get(key)
        if expected_type:
            try:
                # Convert string representations of booleans
                if expected_type == bool and isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
                
                # Convert to expected type
                return expected_type(value)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for {key}: expected {expected_type.__name__}, got {type(value).__name__}")
        
        # Additional validations
        if key == 'search.fuzzy_threshold':
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError("Fuzzy search threshold must be between 0.0 and 1.0")
        
        elif key == 'output.format':
            valid_formats = ['table', 'json', 'csv', 'tree', 'yaml']
            if value not in valid_formats:
                raise ValueError(f"Output format must be one of: {', '.join(valid_formats)}")
        
        elif key == 'advanced.log_level':
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if value.upper() not in valid_levels:
                raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        
        return value
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get information about the configuration system"""
        return {
            'config_dir': str(self.config_dir),
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists(),
            'total_settings': len(self.list_all()),
            'defaults_available': len([k for k in dir(self._defaults) if not k.startswith('_')]),
        }
    
    def export_config(self, file_path: Optional[Path] = None) -> str:
        """Export configuration to a file"""
        if file_path is None:
            file_path = self.config_dir / f"config_export_{int(time.time())}.json"
        
        export_data = {
            'version': '1.0',
            'exported_at': time.time(),
            'config': self._config,
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, sort_keys=True)
        
        return str(file_path)
    
    def import_config(self, file_path: Path, merge: bool = True) -> None:
        """Import configuration from a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        if 'config' not in import_data:
            raise ValueError("Invalid configuration file format")
        
        imported_config = import_data['config']
        
        if merge:
            # Merge with existing configuration
            def deep_merge(base: Dict, update: Dict) -> Dict:
                for key, value in update.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
                return base
            
            deep_merge(self._config, imported_config)
        else:
            # Replace entire configuration
            self._config = imported_config
        
        self._save_config()


# Global configuration instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config(key: str, default: Any = None) -> Any:
    """Convenience function to get configuration value"""
    return get_config_manager().get(key, default)

def set_config(key: str, value: Any) -> None:
    """Convenience function to set configuration value"""
    get_config_manager().set(key, value)
