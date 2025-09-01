"""
Environment management for PyLua VM Curator system.

This module handles environment profiles, configuration validation, cross-platform paths,
development/production profiles, and integration with the curator system for AGI bootstrapping.
"""

import os
import json
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pylua_bioxen_vm_lib.logger import VMLogger
from pylua_bioxen_vm_lib.exceptions import LuaNotFoundError


class EnvironmentManager:
    """
    Manages PyLua VM environments with curator integration.
    
    Handles configuration profiles, cross-platform compatibility, Lua version detection,
    development vs production settings, and environment validation for AGI systems.
    """
    
    # Environment profiles with their characteristics
    PROFILES = {
        'minimal': {
            'description': 'Minimal environment with core Lua only',
            'packages': [],
            'luarocks_required': False,
            'development_tools': False,
            'networking': False
        },
        'standard': {
            'description': 'Standard environment with curated essential packages',
            'packages': ['lua-cjson', 'luafilesystem', 'inspect'],
            'luarocks_required': True,
            'development_tools': True,
            'networking': False
        },
        'full': {
            'description': 'Full environment with all curated packages',
            'packages': ['lua-cjson', 'luafilesystem', 'penlight', 'inspect', 'luasocket', 'lpeg'],
            'luarocks_required': True,
            'development_tools': True,
            'networking': True
        },
        'development': {
            'description': 'Development environment with testing and debugging tools',
            'packages': ['lua-cjson', 'luafilesystem', 'penlight', 'inspect', 'busted', 'luassert'],
            'luarocks_required': True,
            'development_tools': True,
            'networking': False
        },
        'production': {
            'description': 'Production environment with optimized, stable packages',
            'packages': ['lua-cjson', 'luafilesystem', 'penlight'],
            'luarocks_required': True,
            'development_tools': False,
            'networking': False
        },
        'networking': {
            'description': 'Network-focused environment for distributed systems',
            'packages': ['lua-cjson', 'luasocket', 'http', 'penlight'],
            'luarocks_required': True,
            'development_tools': False,
            'networking': True
        }
    }
    
    def __init__(self, profile: str = 'standard', config_path: Optional[Union[str, Path]] = None, 
                 debug_mode: bool = False):
        """
        Initialize environment manager.
        
        Args:
            profile: Environment profile name
            config_path: Optional path to configuration file
            debug_mode: Enable debug logging
        """
        # Initialize basic attributes first
        self.profile = profile
        self.debug_mode = debug_mode
        
        # System information
        self.system = platform.system()
        self.machine = platform.machine()
        self.python_version = platform.python_version()
        
        # Initialize logger
        self.logger = VMLogger(debug_mode=debug_mode, component="EnvironmentManager")
        
        # Validate profile early
        if profile not in self.PROFILES:
            available = ', '.join(self.PROFILES.keys())
            raise ValueError(f"Unknown profile '{profile}'. Available profiles: {available}")
        
        # Configuration path
        self.config_path = Path(config_path) if config_path else self._default_config_path()
        
        # Lua detection
        self.lua_executable = self._find_lua_executable()
        self.lua_version = self._detect_lua_version()
        self.luarocks_version = self._detect_luarocks_version()
        
        # Load configuration
        self.config = self._load_config()
        
        self.logger.debug(f"Environment manager initialized: profile='{profile}', system='{self.system}'")
    
    def _default_config_path(self) -> Path:
        """Get default configuration path based on operating system."""
        if self.system == 'Windows':
            config_dir = Path.home() / 'AppData' / 'Local' / 'PyLuaVM'
        elif self.system == 'Darwin':  # macOS
            config_dir = Path.home() / 'Library' / 'Application Support' / 'PyLuaVM'
        else:  # Linux and others
            config_dir = Path.home() / '.config' / 'pylua_vm'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'environment.json'
    
    def _find_lua_executable(self) -> Optional[str]:
        """Find Lua executable in PATH."""
        self.logger.debug("Searching for Lua executable")
        
        # Try common Lua executable names
        lua_names = ['lua', 'lua5.4', 'lua5.3', 'lua5.2', 'lua5.1']
        
        for lua_name in lua_names:
            if shutil.which(lua_name):
                self.logger.debug(f"Found Lua executable: {lua_name}")
                return lua_name
        
        self.logger.debug("No Lua executable found in PATH")
        return None
    
    def _detect_lua_version(self) -> Optional[str]:
        """Detect Lua version."""
        if not self.lua_executable:
            return None
        
        try:
            self.logger.debug(f"Detecting Lua version for executable: {self.lua_executable}")
            result = subprocess.run(
                [self.lua_executable, '-v'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            version_info = result.stdout.strip() or result.stderr.strip()
            self.logger.debug(f"Lua version detected: {version_info}")
            return version_info
        except Exception as e:
            self.logger.debug(f"Failed to detect Lua version: {e}")
            return None
    
    def _detect_luarocks_version(self) -> Optional[str]:
        """Detect LuaRocks version."""
        try:
            self.logger.debug("Detecting LuaRocks version")
            result = subprocess.run(
                ['luarocks', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                version_info = result.stdout.strip().split('\n')[0]
                self.logger.debug(f"LuaRocks version detected: {version_info}")
                return version_info
        except Exception as e:
            self.logger.debug(f"Failed to detect LuaRocks: {e}")
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        self.logger.debug(f"Loading configuration from: {self.config_path}")
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.debug(f"Configuration loaded successfully")
                return config
            except Exception as e:
                self.logger.debug(f"Failed to load configuration: {e}")
                return {}
        else:
            self.logger.debug("Configuration file does not exist, using defaults")
            return {}
    
    def validate_environment(self) -> List[str]:
        """
        Validate the current environment configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        self.logger.debug("Validating environment")
        errors = []
        
        # Check Lua installation
        if not self.lua_executable:
            errors.append("Lua interpreter not found in PATH. Please install Lua.")
        elif not self.lua_version:
            errors.append(f"Lua executable '{self.lua_executable}' found but version detection failed.")
        
        # Check LuaRocks if required by profile
        profile_info = self.PROFILES.get(self.profile, {})
        if profile_info.get('luarocks_required', False) and not self.luarocks_version:
            errors.append("LuaRocks not found but required for this profile. Please install LuaRocks.")
        
        # Check system compatibility
        if self.system not in ['Windows', 'Linux', 'Darwin']:
            errors.append(f"Unsupported operating system: {self.system}")
        
        # Validate profile-specific requirements
        if self.profile not in self.PROFILES:
            errors.append(f"Invalid profile: {self.profile}")
        
        # Check write permissions for config directory
        try:
            test_file = self.config_path.parent / '.test_write'
            test_file.write_text('test')
            test_file.unlink()
        except Exception:
            errors.append(f"No write permission for config directory: {self.config_path.parent}")
        
        self.logger.debug(f"Environment validation completed: {len(errors)} errors found")
        return errors
    
    def get_profile_info(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a profile.
        
        Args:
            profile_name: Profile to get info for (current profile if None)
            
        Returns:
            Profile information dictionary
        """
        profile = profile_name or self.profile
        if profile not in self.PROFILES:
            raise ValueError(f"Unknown profile: {profile}")
        
        profile_info = self.PROFILES[profile].copy()
        profile_info['name'] = profile
        profile_info['is_current'] = (profile == self.profile)
        
        return profile_info
    
    def list_available_profiles(self) -> List[Dict[str, Any]]:
        """
        Get list of all available environment profiles.
        
        Returns:
            List of profile information dictionaries
        """
        profiles = []
        for name, info in self.PROFILES.items():
            profile_dict = info.copy()
            profile_dict['name'] = name
            profile_dict['is_current'] = (name == self.profile)
            profiles.append(profile_dict)
        
        return profiles
    
    def set_profile(self, profile: str, save_config: bool = True) -> None:
        """
        Change the current environment profile.
        
        Args:
            profile: New profile name
            save_config: Whether to save the change to config file
        """
        if profile not in self.PROFILES:
            available = ', '.join(self.PROFILES.keys())
            raise ValueError(f"Unknown profile '{profile}'. Available profiles: {available}")
        
        old_profile = self.profile
        self.profile = profile
        
        if save_config:
            self.config['profile'] = profile
            self.save_config()
        
        self.logger.debug(f"Profile changed from '{old_profile}' to '{profile}'")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get comprehensive system information.
        
        Returns:
            Dictionary with system details
        """
        return {
            'platform': {
                'system': self.system,
                'machine': self.machine,
                'python_version': self.python_version
            },
            'lua': {
                'executable': self.lua_executable,
                'version': self.lua_version,
                'available': self.lua_executable is not None
            },
            'luarocks': {
                'version': self.luarocks_version,
                'available': self.luarocks_version is not None
            },
            'environment': {
                'profile': self.profile,
                'config_path': str(self.config_path),
                'config_exists': self.config_path.exists()
            },
            'validation': {
                'errors': self.validate_environment(),
                'is_valid': len(self.validate_environment()) == 0
            }
        }
    
    def get_cross_platform_path(self, path: Union[str, Path]) -> str:
        """
        Convert path to cross-platform format.
        
        Args:
            path: Path to convert
            
        Returns:
            Resolved cross-platform path string
        """
        return str(Path(path).resolve())
    
    def get_lua_paths(self) -> Dict[str, Optional[str]]:
        """
        Get Lua-related paths for the current environment.
        
        Returns:
            Dictionary with Lua paths
        """
        paths = {
            'lua_executable': self.lua_executable,
            'luarocks_executable': shutil.which('luarocks'),
            'lua_path': os.environ.get('LUA_PATH'),
            'lua_cpath': os.environ.get('LUA_CPATH')
        }
        
        # Try to detect common Lua installation directories
        if self.system == 'Linux':
            paths['lua_modules'] = '/usr/local/share/lua/5.4'
            paths['lua_lib'] = '/usr/local/lib/lua/5.4'
        elif self.system == 'Darwin':
            paths['lua_modules'] = '/opt/homebrew/share/lua/5.4'
            paths['lua_lib'] = '/opt/homebrew/lib/lua/5.4'
        elif self.system == 'Windows':
            paths['lua_modules'] = 'C:\\lua\\share\\lua\\5.4'
            paths['lua_lib'] = 'C:\\lua\\lib\\lua\\5.4'
        
        return paths
    
    def is_development_mode(self) -> bool:
        """Check if current profile is development-oriented."""
        profile_info = self.PROFILES.get(self.profile, {})
        return profile_info.get('development_tools', False) or self.profile == 'development'
    
    def is_production_mode(self) -> bool:
        """Check if current profile is production-oriented."""
        return self.profile == 'production'
    
    def is_networking_enabled(self) -> bool:
        """Check if current profile has networking capabilities."""
        profile_info = self.PROFILES.get(self.profile, {})
        return profile_info.get('networking', False)
    
    def get_recommended_packages(self) -> List[str]:
        """
        Get recommended packages for the current profile.
        
        Returns:
            List of package names
        """
        profile_info = self.PROFILES.get(self.profile, {})
        return profile_info.get('packages', [])
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        self.logger.debug(f"Saving configuration to: {self.config_path}")
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update config with current settings
        self.config.update({
            'profile': self.profile,
            'last_updated': platform.node(),  # hostname as identifier
            'system_info': {
                'system': self.system,
                'machine': self.machine,
                'lua_version': self.lua_version,
                'luarocks_version': self.luarocks_version
            }
        })
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)
            self.logger.debug("Configuration saved successfully")
        except Exception as e:
            self.logger.debug(f"Failed to save configuration: {e}")
            raise
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        self.logger.debug("Resetting configuration to defaults")
        self.config = {}
        self.save_config()
    
    def create_env_summary(self) -> Dict[str, Any]:
        """
        Create a comprehensive environment summary for debugging and reporting.
        
        Returns:
            Complete environment summary
        """
        return {
            'environment_manager': {
                'profile': self.profile,
                'debug_mode': self.debug_mode
            },
            'system_info': self.get_system_info(),
            'profile_info': self.get_profile_info(),
            'lua_paths': self.get_lua_paths(),
            'capabilities': {
                'development_mode': self.is_development_mode(),
                'production_mode': self.is_production_mode(),
                'networking_enabled': self.is_networking_enabled()
            },
            'recommended_packages': self.get_recommended_packages(),
            'validation_errors': self.validate_environment()
        }
    
    def install_profile_packages(self) -> Dict[str, bool]:
        """
        Install packages recommended for the current profile using LuaRocks.
        
        Returns:
            Dictionary mapping package names to installation success status
        """
        if not self.luarocks_version:
            raise LuaNotFoundError("LuaRocks not available for package installation")
        
        packages = self.get_recommended_packages()
        results = {}
        
        self.logger.debug(f"Installing {len(packages)} packages for profile '{self.profile}'")
        
        for package in packages:
            try:
                self.logger.debug(f"Installing package: {package}")
                result = subprocess.run(
                    ['luarocks', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                success = result.returncode == 0
                results[package] = success
                
                if success:
                    self.logger.debug(f"Successfully installed: {package}")
                else:
                    self.logger.debug(f"Failed to install {package}: {result.stderr}")
                    
            except Exception as e:
                self.logger.debug(f"Exception installing {package}: {e}")
                results[package] = False
        
        return results
    
    def check_package_availability(self, packages: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Check if packages are available/installed.
        
        Args:
            packages: List of packages to check (current profile packages if None)
            
        Returns:
            Dictionary mapping package names to availability status
        """
        packages = packages or self.get_recommended_packages()
        results = {}
        
        for package in packages:
            try:
                # Try to check if package is installed via luarocks list
                result = subprocess.run(
                    ['luarocks', 'list', package],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                # Package is available if luarocks list shows it
                results[package] = package in result.stdout
            except Exception:
                # If we can't check, assume not available
                results[package] = False
        
        return results
    
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get recommended environment variables for the current profile.
        
        Returns:
            Dictionary of environment variable names to values
        """
        env_vars = {}
        
        # Basic Lua paths
        lua_paths = self.get_lua_paths()
        if lua_paths['lua_modules']:
            env_vars['LUA_PATH'] = f"{lua_paths['lua_modules']}/?.lua;;"
        if lua_paths['lua_lib']:
            env_vars['LUA_CPATH'] = f"{lua_paths['lua_lib']}/?.so;;"
        
        # Profile-specific variables
        if self.is_development_mode():
            env_vars['LUA_DEV_MODE'] = '1'
            env_vars['LUA_DEBUG'] = '1'
        
        if self.is_production_mode():
            env_vars['LUA_PRODUCTION'] = '1'
        
        if self.is_networking_enabled():
            env_vars['LUA_NETWORKING'] = '1'
        
        return env_vars
    
    def setup_environment_variables(self) -> None:
        """Set up environment variables for the current session."""
        env_vars = self.get_environment_variables()
        for name, value in env_vars.items():
            os.environ[name] = value
            self.logger.debug(f"Set environment variable: {name}={value}")
    
    def __repr__(self) -> str:
        return f"EnvironmentManager(profile='{self.profile}', system='{self.system}', lua='{self.lua_version or 'not found'}')"