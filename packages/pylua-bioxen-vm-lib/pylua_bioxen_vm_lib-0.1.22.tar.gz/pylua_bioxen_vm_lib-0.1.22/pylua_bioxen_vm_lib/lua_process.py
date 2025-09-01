"""
Core Lua process management for individual VM instances.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from pylua_bioxen_vm_lib.exceptions import (
    LuaProcessError, 
    LuaNotFoundError, 
    ScriptGenerationError
)
from pylua_bioxen_vm_lib.interactive_session import InteractiveSession
from pylua_bioxen_vm_lib.logger import VMLogger
from pylua_bioxen_vm_lib.utils.curator import Curator


class LuaProcess:
    """
    Manages a single Lua interpreter subprocess with intelligent package curation.
    
    This class handles the execution of Lua code through subprocess calls,
    supporting both string execution and script file execution, enhanced with
    curator-based package management for AGI bootstrapping.
    """
    
    def __init__(self, name: str = "LuaVM", lua_executable: str = "lua", debug_mode: bool = False):
        """
        Initialize a Lua process manager.
        
        Args:
            name: Human-readable name for this VM instance
            lua_executable: Path to Lua interpreter (default: "lua")
            debug_mode: Enable debug logging output
        """
        self.name = name
        self.lua_executable = lua_executable
        self.debug_mode = debug_mode
        self.logger = VMLogger(debug_mode=debug_mode, component="LuaProcess")
        self._temp_scripts = []  # Track temporary script files for cleanup
        self._interactive_session: Optional[InteractiveSession] = None
        
        # Initialize curator for intelligent package management
        self._curator: Optional[Curator] = None
        self._packages_setup = False
        
        self.logger.debug(f"Initializing LuaProcess: name='{name}', executable='{lua_executable}'")
        
        # Verify Lua is available
        self._verify_lua_available()
        
    # --- Curator Integration Methods ---
    
    def setup_packages(self, profile: str = 'standard') -> Dict[str, Any]:
        """
        Setup packages using curator with specified profile.
        
        Args:
            profile: Environment profile ('minimal', 'standard', 'full')
            
        Returns:
            Dict with setup results and package information
        """
        self.logger.debug(f"Setting up packages with profile: '{profile}'")
        
        try:
            # Initialize curator if not already done
            if self._curator is None:
                self._curator = Curator()
                self.logger.debug("Curator initialized")
            
            # Curate the environment
            result = self._curator.curate_environment(profile)
            self._packages_setup = True
            
            setup_info = {
                'success': result.get('success', False),
                'profile': profile,
                'packages_installed': result.get('installed_packages', []),
                'failed_packages': result.get('failed_packages', []),
                'total_packages': len(result.get('installed_packages', []) + result.get('failed_packages', [])),
                'curator_recommendations': self._curator.get_recommendations() if result.get('success') else []
            }
            
            if setup_info['success']:
                self.logger.debug(f"Package setup completed successfully: {len(setup_info['packages_installed'])} packages installed")
            else:
                self.logger.debug(f"Package setup had issues: {len(setup_info['failed_packages'])} packages failed")
                
            return setup_info
            
        except Exception as e:
            self.logger.debug(f"Package setup failed with exception: {e}")
            error_result = {
                'success': False,
                'profile': profile,
                'error': str(e),
                'packages_installed': [],
                'failed_packages': [],
                'total_packages': 0
            }
            return error_result
    
    def install_package(self, package_name: str, version: str = 'latest') -> Dict[str, Any]:
        """
        Install a specific package via curator.
        
        Args:
            package_name: Name of the package to install
            version: Version constraint (default: 'latest')
            
        Returns:
            Dict with installation results
        """
        self.logger.debug(f"Installing package: '{package_name}' (version: {version})")
        
        try:
            # Initialize curator if not already done
            if self._curator is None:
                self._curator = Curator()
                self.logger.debug("Curator initialized for package installation")
            
            # Install the package
            result = self._curator.install_package(package_name, version)
            
            install_info = {
                'success': result.get('success', False),
                'package': package_name,
                'version': version,
                'installed_version': result.get('installed_version'),
                'dependencies': result.get('dependencies', []),
                'error': result.get('error') if not result.get('success') else None
            }
            
            if install_info['success']:
                self.logger.debug(f"Package '{package_name}' installed successfully")
            else:
                self.logger.debug(f"Package '{package_name}' installation failed: {install_info['error']}")
                
            return install_info
            
        except Exception as e:
            self.logger.debug(f"Package installation failed with exception: {e}")
            return {
                'success': False,
                'package': package_name,
                'version': version,
                'error': str(e)
            }
    
    def get_package_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get curator recommendations for packages to install.
        
        Returns:
            List of recommendation dictionaries with package info and rationale
        """
        self.logger.debug("Getting package recommendations from curator")
        
        try:
            # Initialize curator if not already done
            if self._curator is None:
                self._curator = Curator()
                self.logger.debug("Curator initialized for recommendations")
            
            recommendations = self._curator.get_recommendations()
            self.logger.debug(f"Retrieved {len(recommendations)} recommendations")
            
            return recommendations
            
        except Exception as e:
            self.logger.debug(f"Failed to get recommendations: {e}")
            return []
    
    def check_environment_health(self) -> Dict[str, Any]:
        """
        Check system health via curator.
        
        Returns:
            Dict with health check results and diagnostics
        """
        self.logger.debug("Performing environment health check via curator")
        
        try:
            # Initialize curator if not already done
            if self._curator is None:
                self._curator = Curator()
                self.logger.debug("Curator initialized for health check")
            
            health_result = self._curator.health_check()
            
            # Add VM-specific health information
            health_result['vm_info'] = {
                'name': self.name,
                'lua_executable': self.lua_executable,
                'packages_setup': self._packages_setup,
                'interactive_session_running': self.is_interactive_running(),
                'temp_scripts_count': len(self._temp_scripts)
            }
            
            self.logger.debug(f"Health check completed: overall_health={health_result.get('overall_health', 'unknown')}")
            
            return health_result
            
        except Exception as e:
            self.logger.debug(f"Health check failed with exception: {e}")
            return {
                'overall_health': 'error',
                'error': str(e),
                'vm_info': {
                    'name': self.name,
                    'lua_executable': self.lua_executable,
                    'packages_setup': self._packages_setup,
                    'interactive_session_running': self.is_interactive_running(),
                    'temp_scripts_count': len(self._temp_scripts)
                }
            }
    
    def get_installed_packages(self) -> List[str]:
        """
        Get list of currently installed packages.
        
        Returns:
            List of installed package names
        """
        self.logger.debug("Getting list of installed packages")
        
        try:
            if self._curator is None:
                self.logger.debug("Curator not initialized, returning empty package list")
                return []
            
            packages = self._curator.get_installed_packages()
            self.logger.debug(f"Found {len(packages)} installed packages")
            
            return packages
            
        except Exception as e:
            self.logger.debug(f"Failed to get installed packages: {e}")
            return []
    
    def get_curator_manifest(self) -> Dict[str, Any]:
        """
        Get the current curator manifest for reproducible environments.
        
        Returns:
            Manifest dictionary with environment configuration
        """
        self.logger.debug("Getting curator manifest")
        
        try:
            if self._curator is None:
                self.logger.debug("Curator not initialized, returning empty manifest")
                return {}
            
            manifest = self._curator.get_manifest()
            self.logger.debug("Retrieved curator manifest")
            
            return manifest
            
        except Exception as e:
            self.logger.debug(f"Failed to get curator manifest: {e}")
            return {}

    # --- Interactive Session Methods ---
    def start_interactive_session(self):
        """Start a persistent interactive Lua interpreter session."""
        self.logger.debug("Starting interactive session")
        if self._interactive_session and self._interactive_session.is_running():
            raise LuaProcessError("Interactive session already running")
        self._interactive_session = InteractiveSession(
            lua_executable=self.lua_executable, 
            name=self.name,
            debug_mode=self.debug_mode
        )
        self._interactive_session.start()
        self.logger.debug("Interactive session started successfully")

    def stop_interactive_session(self):
        """Stop the interactive Lua interpreter session."""
        self.logger.debug("Stopping interactive session")
        if self._interactive_session:
            self._interactive_session.stop()
            self._interactive_session = None
            self.logger.debug("Interactive session stopped")

    def send_input(self, input_str: str):
        """Send input to the interactive Lua interpreter session."""
        self.logger.debug(f"Sending input to interactive session: '{input_str[:50]}{'...' if len(input_str) > 50 else ''}'")
        if not self._interactive_session or not self._interactive_session.is_running():
            raise LuaProcessError("Interactive session not running")
        self._interactive_session.send_input(input_str)

    def read_output(self, timeout: float = 0.1) -> Optional[str]:
        """Read output from the interactive Lua interpreter session."""
        self.logger.debug(f"Reading output from interactive session (timeout={timeout})")
        if not self._interactive_session or not self._interactive_session.is_running():
            raise LuaProcessError("Interactive session not running")
        output = self._interactive_session.read_output(timeout=timeout)
        if output:
            self.logger.debug(f"Read output: '{output[:100]}{'...' if len(output) > 100 else ''}'")
        return output

    def is_interactive_running(self) -> bool:
        """Check if the interactive session is running."""
        is_running = self._interactive_session is not None and self._interactive_session.is_running()
        self.logger.debug(f"Interactive session running status: {is_running}")
        return is_running
    
    def _verify_lua_available(self) -> None:
        """Check if Lua interpreter is available in PATH."""
        self.logger.debug(f"Verifying Lua executable availability: '{self.lua_executable}'")
        try:
            result = subprocess.run(
                [self.lua_executable, "-v"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode != 0:
                self.logger.debug(f"Lua verification failed with return code {result.returncode}: {result.stderr}")
                raise LuaNotFoundError(f"Lua interpreter check failed: {result.stderr}")
            self.logger.debug(f"Lua verification successful: {result.stdout.strip()}")
        except FileNotFoundError:
            self.logger.debug(f"Lua executable not found in PATH: '{self.lua_executable}'")
            raise LuaNotFoundError(f"Lua executable '{self.lua_executable}' not found in PATH")
        except subprocess.TimeoutExpired:
            self.logger.debug(f"Lua executable verification timed out: '{self.lua_executable}'")
            raise LuaNotFoundError(f"Lua executable '{self.lua_executable}' did not respond")
    
    def execute_string(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a Lua code string.
        
        Args:
            lua_code: Lua code to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        if not lua_code.strip():
            raise ValueError("Lua code cannot be empty")
        
        self.logger.debug(f"Executing Lua string (timeout={timeout}): '{lua_code[:100]}{'...' if len(lua_code) > 100 else ''}'")
        
        command = [self.lua_executable, "-e", lua_code]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            
            execution_result = {
                'stdout': result.stdout.strip() if result.stdout else "",
                'stderr': result.stderr.strip() if result.stderr else "",
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
            
            self.logger.debug(f"String execution completed: success={execution_result['success']}, return_code={result.returncode}")
            if execution_result['stderr']:
                self.logger.debug(f"String execution stderr: {execution_result['stderr']}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            self.logger.debug(f"String execution timed out after {timeout} seconds")
            raise LuaProcessError(f"Lua execution timed out after {timeout} seconds")
        except Exception as e:
            self.logger.debug(f"String execution failed with exception: {e}")
            raise LuaProcessError(f"Failed to execute Lua code: {e}")
    
    def execute_file(self, script_path: Union[str, Path], timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a Lua script file.
        
        Args:
            script_path: Path to Lua script file
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        script_path = Path(script_path)
        
        self.logger.debug(f"Executing Lua file (timeout={timeout}): '{script_path}'")
        
        if not script_path.exists():
            self.logger.debug(f"Script file not found: {script_path}")
            raise FileNotFoundError(f"Lua script not found: {script_path}")
        
        if not script_path.is_file():
            self.logger.debug(f"Path is not a file: {script_path}")
            raise ValueError(f"Path is not a file: {script_path}")
        
        command = [self.lua_executable, str(script_path)]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            
            execution_result = {
                'stdout': result.stdout.strip() if result.stdout else "",
                'stderr': result.stderr.strip() if result.stderr else "",
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
            
            self.logger.debug(f"File execution completed: success={execution_result['success']}, return_code={result.returncode}")
            if execution_result['stderr']:
                self.logger.debug(f"File execution stderr: {execution_result['stderr']}")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            self.logger.debug(f"File execution timed out after {timeout} seconds")
            raise LuaProcessError(f"Lua script execution timed out after {timeout} seconds")
        except Exception as e:
            self.logger.debug(f"File execution failed with exception: {e}")
            raise LuaProcessError(f"Failed to execute Lua script: {e}")
    
    def execute_temp_script(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a temporary Lua script and execute it.
        
        Useful for complex multi-line Lua code that's easier to manage as a file.
        
        Args:
            lua_code: Lua code to write to temporary script
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with keys: 'stdout', 'stderr', 'return_code', 'success'
        """
        self.logger.debug(f"Creating and executing temporary script (timeout={timeout})")
        
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.lua',
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(lua_code)
                temp_script_path = Path(temp_file.name)
            
            self.logger.debug(f"Created temporary script: {temp_script_path}")
            
            # Track for cleanup
            self._temp_scripts.append(temp_script_path)
            
            # Execute the temporary script
            result = self.execute_file(temp_script_path, timeout=timeout)
            
            # Clean up immediately after execution
            self._cleanup_temp_script(temp_script_path)
            
            self.logger.debug("Temporary script execution completed")
            return result
            
        except Exception as e:
            self.logger.debug(f"Temporary script creation/execution failed: {e}")
            raise ScriptGenerationError(f"Failed to create/execute temporary script: {e}")
    
    def _cleanup_temp_script(self, script_path: Path) -> None:
        """Clean up a specific temporary script file."""
        self.logger.debug(f"Cleaning up temporary script: {script_path}")
        try:
            if script_path.exists():
                script_path.unlink()
                self.logger.debug(f"Successfully removed temporary script: {script_path}")
            if script_path in self._temp_scripts:
                self._temp_scripts.remove(script_path)
        except Exception as e:
            self.logger.debug(f"Warning: Could not remove temporary script {script_path}: {e}")
    
    def cleanup(self) -> None:
        """Clean up all temporary script files and curator resources."""
        self.logger.debug(f"Cleaning up {len(self._temp_scripts)} temporary scripts and stopping interactive session")
        for script_path in self._temp_scripts[:]:  # Copy list to avoid modification during iteration
            self._cleanup_temp_script(script_path)
        if self._interactive_session:
            self._interactive_session.stop()
            self._interactive_session = None
        
        # Clean up curator resources if needed
        if self._curator:
            self.logger.debug("Cleaning up curator resources")
            # Note: Curator cleanup would be implemented here if needed
            
        self.logger.debug("Cleanup completed")
    
    def start(self):
        """Start the Lua VM (for compatibility with XCP-ng interface)"""
        # For basic VMs, starting means ensuring interactive session is ready
        if not self._interactive_session:
            self.start_interactive_session()
    
    def stop(self):
        """Stop the Lua VM (for compatibility with XCP-ng interface)"""
        # For basic VMs, stopping means cleanup
        self.cleanup()
    
    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()
    
    def __repr__(self):
        return f"LuaProcess(name='{self.name}', lua_executable='{self.lua_executable}', debug_mode={self.debug_mode}, packages_setup={self._packages_setup})"