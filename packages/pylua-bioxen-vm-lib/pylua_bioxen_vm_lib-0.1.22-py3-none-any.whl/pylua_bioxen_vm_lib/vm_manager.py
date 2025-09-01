"""
High-level VM manager for orchestrating multiple Lua VMs.

This module provides the main interface for creating, managing, and coordinating
multiple networked Lua VMs.
"""

import threading
import time
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from pylua_bioxen_vm_lib.lua_process import LuaProcess
from pylua_bioxen_vm_lib.networking import NetworkedLuaVM

"""
High-level VM manager for orchestrating multiple Lua VMs with interactive terminal support.
"""

import threading
import time
import fnmatch
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future

from .lua_process import LuaProcess
from .networking import NetworkedLuaVM
from pylua_bioxen_vm_lib.interactive_session import InteractiveSession, SessionManager
from pylua_bioxen_vm_lib.logger import VMLogger
from pylua_bioxen_vm_lib.exceptions import (
    VMManagerError, 
    ProcessRegistryError,
    InteractiveSessionError,
    SessionNotFoundError,
    SessionAlreadyExistsError
)


class VMManager:
    """
    High-level manager for multiple Lua VMs.
    
    Handles creation, lifecycle management, and coordination of Lua VMs
    with support for both basic and networked VMs, plus full interactive
    terminal capabilities similar to a hypervisor.
    """
    
    def __init__(self, max_workers: int = 10, lua_executable: str = "lua", debug_mode: bool = False):
        """
        Initialize the VM manager.
        
        Args:
            max_workers: Maximum number of concurrent VM executions
            lua_executable: Path to Lua interpreter
            debug_mode: Enable debug logging
        """
        self.max_workers = max_workers
        self.lua_executable = lua_executable
        self.debug_mode = debug_mode
        self.logger = VMLogger(debug_mode=debug_mode, component="VMManager")
        
        # VM and execution tracking
        self.vms: Dict[str, LuaProcess] = {}
        self.futures: Dict[str, Future] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Interactive session management
        self.session_manager = SessionManager(debug_mode=debug_mode)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Process registry for persistent VMs
        self._persistent_vms: Dict[str, Dict[str, Any]] = {}
        
        self.logger.debug(f"VMManager initialized with max_workers={max_workers}, debug_mode={debug_mode}")

    # ==================== CORE VM MANAGEMENT ====================
    def create_vm(self, vm_id: str, vm_type: str = "basic", networked: bool = False, 
                  persistent: bool = False, debug_mode: bool = None, 
                  lua_executable: str = None, config: dict = None) -> LuaProcess:
        """
        Create a new Lua VM with multi-VM type support (Phase 1).
        
        Args:
            vm_id: Unique identifier for the VM
            vm_type: Type of VM to create ("basic" or "xcpng")
            networked: Whether to create a networked VM with socket support
            persistent: Whether this VM should be registered for interactive sessions
            debug_mode: Override debug mode for this VM (uses manager default if None)
            lua_executable: Override Lua executable for this VM (uses manager default if None)
            config: Configuration dictionary for VM-specific settings (required for xcpng)
        Returns:
            The created VM instance (BasicLuaVM, NetworkedLuaVM, or XCPngVM)
        """
        if vm_id in self.vms:
            raise ValueError(f"VM with ID '{vm_id}' already exists")
        
        # Use manager defaults if not specified
        vm_debug_mode = debug_mode if debug_mode is not None else self.debug_mode
        vm_lua_executable = lua_executable if lua_executable is not None else self.lua_executable
        
        with self._lock:
            # Factory pattern implementation
            vm_classes = {
                "basic": self._create_basic_vm,
                "xcpng": self._create_xcpng_vm
            }
            
            if vm_type not in vm_classes:
                raise ValueError(f"Unknown VM type: {vm_type}. Supported types: {list(vm_classes.keys())}")
            
            # Create VM using factory method
            vm = vm_classes[vm_type](vm_id, networked, vm_debug_mode, vm_lua_executable, config)
            self.vms[vm_id] = vm
            
            # Register for interactive sessions if persistent
            if persistent:
                self._register_persistent_vm(vm_id, vm_type, networked)
                
            self.logger.debug(f"Created VM '{vm_id}' (type={vm_type}, networked={networked}, persistent={persistent})")
            return vm

    def _create_basic_vm(self, vm_id: str, networked: bool, debug_mode: bool, 
                        lua_executable: str, config: dict = None) -> LuaProcess:
        """Create a basic VM (current implementation)"""
        if networked:
            return NetworkedLuaVM(name=vm_id, lua_executable=lua_executable, debug_mode=debug_mode)
        else:
            return LuaProcess(name=vm_id, lua_executable=lua_executable, debug_mode=debug_mode)
    
    def _create_xcpng_vm(self, vm_id: str, networked: bool, debug_mode: bool, 
                        lua_executable: str, config: dict = None):
        """Create an XCP-ng VM (Phase 2 implementation)"""
        from .xcp_ng_integration import XCPngVM
        if config is None:
            raise ValueError("XCP-ng VM requires configuration dictionary with XCP-ng connection details.")
        return XCPngVM(vm_id, config)
    
    def _create_xcpng_session_wrapper(self, vm_id: str, vm):
        """Create a session wrapper for XCP-ng VMs that manages their own sessions"""
        # For XCP-ng VMs, we create a simple wrapper that delegates to the VM's methods
        class XCPngSessionWrapper:
            def __init__(self, vm_id, vm):
                self.vm_id = vm_id
                self.vm = vm
                
            def is_attached(self):
                return self.vm.session_active
                
            def is_running(self):
                return self.vm.session_active
                
            def send_command(self, command):
                return self.vm.send_input(command)
                
            def read_output(self, timeout=0.1):
                return self.vm.read_output(timeout)
                
            def terminate(self):
                self.vm.stop()
        
        wrapper = XCPngSessionWrapper(vm_id, vm)
        # Register it with session manager for compatibility
        self.session_manager.sessions[vm_id] = wrapper
        return wrapper

    def get_vm(self, vm_id: str) -> Optional[LuaProcess]:
        """Get a VM by ID."""
        return self.vms.get(vm_id)

    def list_vms(self) -> List[str]:
        """Get list of all VM IDs."""
        return list(self.vms.keys())

    def remove_vm(self, vm_id: str) -> bool:
        """
        Remove a VM and clean up its resources.
        """
        with self._lock:
            # Detach any active interactive sessions
            try:
                self.detach_from_vm(vm_id)
            except:
                pass
            # Remove from session manager
            self.session_manager.remove_session(vm_id)
            # Remove from persistent registry
            self._persistent_vms.pop(vm_id, None)
            # Clean up VM
            vm = self.vms.pop(vm_id, None)
            if vm:
                vm.cleanup()
                # Cancel any running futures for this VM
                future = self.futures.pop(vm_id, None)
                if future and not future.done():
                    future.cancel()
                self.logger.debug(f"Removed VM '{vm_id}' and cleaned up resources")
                return True
            return False

    # ==================== PERSISTENT VM REGISTRY ====================
    def _register_persistent_vm(self, vm_id: str, vm_type: str, networked: bool) -> None:
        """Register a VM in the persistent registry with vm_type support."""
        vm = self.vms.get(vm_id)
        self._persistent_vms[vm_id] = {
            'created_at': time.time(),
            'vm_type': vm_type,
            'networked': networked,
            'interactive_capable': True,
            'session_active': False,
            'vm_class': vm.__class__.__name__ if vm else 'unknown'
        }
        self.logger.debug(f"Registered persistent VM '{vm_id}' (type={vm_type}, networked={networked})")

    def list_persistent_vms(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all persistent VMs.
        """
        with self._lock:
            result = {}
            for vm_id, metadata in self._persistent_vms.items():
                session = self.session_manager.get_session(vm_id)
                result[vm_id] = {
                    **metadata,
                    'session_attached': session.is_attached() if session else False,
                    'process_running': session.is_running() if session else False,
                    'vm_exists': vm_id in self.vms
                }
            return result

    def get_vm_info(self, vm_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific VM.
        """
        if vm_id not in self.vms:
            return None
        vm = self.vms[vm_id]
        session = self.session_manager.get_session(vm_id)
        persistent_info = self._persistent_vms.get(vm_id, {})
        
        # Determine VM type based on class
        from .xcp_ng_integration import XCPngVM
        if isinstance(vm, XCPngVM):
            vm_type = 'xcpng'
        elif isinstance(vm, NetworkedLuaVM):
            vm_type = 'networked'
        else:
            vm_type = 'basic'
            
        return {
            'vm_id': vm_id,
            'vm_name': vm.name,
            'vm_type': vm_type,
            'persistent': vm_id in self._persistent_vms,
            'session_exists': session is not None,
            'session_attached': session.is_attached() if session else False,
            'process_running': session.is_running() if session else False,
            'interactive_capable': vm_id in self._persistent_vms,
            **persistent_info
        }

    # ==================== INTERACTIVE SESSION MANAGEMENT ====================
    def attach_to_vm(self, vm_id: str, output_callback: Optional[Callable[[str], None]] = None) -> InteractiveSession:
        """
        Attach to a VM's interactive session (hypervisor-like interface).
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise SessionNotFoundError(f"VM '{vm_id}' not found")
        with self._lock:
            # Get or create session
            session = self.session_manager.get_session(vm_id)
            if not session:
                session = self.session_manager.create_session(vm_id, vm)
            # Attach to session
            session.attach(output_callback)
            # Update persistent registry
            if vm_id in self._persistent_vms:
                self._persistent_vms[vm_id]['session_active'] = True
            self.logger.debug(f"Attached to VM '{vm_id}' interactive session")
            return session

    def detach_from_vm(self, vm_id: str) -> None:
        """
        Detach from a VM's interactive session (keeps VM running).
        """
        session = self.session_manager.get_session(vm_id)
        if session:
            session.detach()
            # Update persistent registry
            if vm_id in self._persistent_vms:
                self._persistent_vms[vm_id]['session_active'] = False
            self.logger.debug(f"Detached from VM '{vm_id}' interactive session")

    def send_input(self, vm_id: str, input_str: str) -> None:
        """
        Send input to a VM's interactive session (works for both basic and xcpng VMs).
        """
        # Check if this is an XCP-ng VM with direct session support
        vm = self.get_vm(vm_id)
        if vm and hasattr(vm, 'send_input') and hasattr(vm, 'session_active'):
            # XCP-ng VM with direct session support
            if not vm.session_active:
                raise SessionNotFoundError(f"XCP-ng VM '{vm_id}' has no active session")
            vm.send_input(input_str)
        else:
            # Basic VM using session manager
            session = self.session_manager.get_session(vm_id)
            if not session:
                raise SessionNotFoundError(f"No interactive session for VM '{vm_id}'")
            session.send_command(input_str)
        
        self.logger.debug(f"Sent input to VM '{vm_id}': {input_str!r}")

    def read_output(self, vm_id: str, timeout: Optional[float] = 0.1) -> str:
        """
        Read output from a VM's interactive session (works for both basic and xcpng VMs).
        """
        # Check if this is an XCP-ng VM with direct session support
        vm = self.get_vm(vm_id)
        if vm and hasattr(vm, 'read_output') and hasattr(vm, 'session_active'):
            # XCP-ng VM with direct session support
            if not vm.session_active:
                raise SessionNotFoundError(f"XCP-ng VM '{vm_id}' has no active session")
            output = vm.read_output(timeout)
        else:
            # Basic VM using session manager
            session = self.session_manager.get_session(vm_id)
            if not session:
                raise SessionNotFoundError(f"No interactive session for VM '{vm_id}'")
            output = session.read_output(timeout=timeout)
        
        self.logger.debug(f"Read output from VM '{vm_id}': {output!r}")
        return output

    def execute_interactive_command(self, vm_id: str, command: str, timeout: float = 5.0) -> str:
        """
        Execute a command in an interactive session and wait for output.
        """
        session = self.session_manager.get_session(vm_id)
        if not session:
            raise SessionNotFoundError(f"No interactive session for VM '{vm_id}'")
        result = session.execute_and_wait(command, timeout=timeout)
        self.logger.debug(f"Executed interactive command on VM '{vm_id}': {command!r} -> {result!r}")
        return result

    def list_interactive_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all active interactive sessions.
        """
        return self.session_manager.list_sessions()

    def terminate_vm_session(self, vm_id: str) -> None:
        """
        Terminate a VM's interactive session and stop the process (works for both basic and xcpng VMs).
        """
        # Check if this is an XCP-ng VM with direct session support
        vm = self.get_vm(vm_id)
        if vm and hasattr(vm, 'stop') and hasattr(vm, 'session_active'):
            # XCP-ng VM - stop the VM and cleanup
            vm.stop()
        else:
            # Basic VM using session manager
            session = self.session_manager.get_session(vm_id)
            if session:
                session.terminate()
                self.session_manager.remove_session(vm_id)
        
        # Update persistent registry
        if vm_id in self._persistent_vms:
            self._persistent_vms[vm_id]['session_active'] = False
        self.logger.debug(f"Terminated VM '{vm_id}' session")

    # ==================== HYPERVISOR-LIKE OPERATIONS ====================
    def create_interactive_vm(self, vm_id: str, vm_type: str = "basic", config: dict = None, 
                             networked: bool = False, auto_attach: bool = True) -> InteractiveSession:
        """
        Create a VM specifically for interactive use (hypervisor-like) with multi-VM type support.
        
        Args:
            vm_id: Unique identifier for the VM
            vm_type: Type of VM to create ("basic" or "xcpng")
            config: Configuration dictionary (required for xcpng VMs)
            networked: Whether to create networked VM (for basic VMs)
            auto_attach: Whether to automatically attach to the session
            
        Returns:
            InteractiveSession for the created VM
        """
        # Create VM as persistent with vm_type support
        vm = self.create_vm(vm_id, vm_type=vm_type, config=config, networked=networked, persistent=True)
        
        # For XCP-ng VMs, we need to start them since they manage their own sessions
        if vm_type == "xcpng":
            vm.start()  # This will create the VM and establish SSH session
            # Create a wrapper session that delegates to the VM's SSH session
            session = self._create_xcpng_session_wrapper(vm_id, vm)
        else:
            # For basic VMs, use existing session manager
            if auto_attach:
                session = self.attach_to_vm(vm_id)
            else:
                session = self.session_manager.create_session(vm_id, vm)
        
        self.logger.debug(f"Created interactive VM '{vm_id}' (type={vm_type}, auto_attach={auto_attach})")
        return session

    def clone_vm_session(self, source_vm_id: str, target_vm_id: str) -> InteractiveSession:
        """
        Clone a VM's configuration to create a new interactive session.
        """
        source_vm = self.get_vm(source_vm_id)
        if not source_vm:
            raise SessionNotFoundError(f"Source VM '{source_vm_id}' not found")
        # Determine if source is networked
        networked = isinstance(source_vm, NetworkedLuaVM)
        session = self.create_interactive_vm(target_vm_id, networked=networked, auto_attach=True)
        self.logger.debug(f"Cloned VM session from '{source_vm_id}' to '{target_vm_id}'")
        return session

    def bulk_create_interactive_cluster(self, cluster_id: str, vm_count: int, 
                                      networked: bool = True) -> Dict[str, InteractiveSession]:
        """
        Create a cluster of interactive VMs.
        """
        sessions = {}
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            session = self.create_interactive_vm(vm_id, networked=networked, auto_attach=False)
            sessions[vm_id] = session
        self.logger.debug(f"Created interactive cluster '{cluster_id}' with {vm_count} VMs")
        return sessions

    def broadcast_to_interactive_sessions(self, vm_pattern: str, command: str) -> Dict[str, str]:
        """
        Broadcast a command to all interactive sessions matching a pattern.
        """
        matching_sessions = {}
        all_sessions = self.session_manager.list_sessions()
        for vm_id in all_sessions:
            if fnmatch.fnmatch(vm_id, vm_pattern):
                session = self.session_manager.get_session(vm_id)
                if session and session.is_attached():
                    matching_sessions[vm_id] = session
        if not matching_sessions:
            raise ValueError(f"No attached sessions found matching pattern: {vm_pattern}")
        results = {}
        for vm_id, session in matching_sessions.items():
            try:
                output = session.execute_and_wait(command, timeout=5.0)
                results[vm_id] = output
            except Exception as e:
                results[vm_id] = f"Error: {e}"
        self.logger.debug(f"Broadcast command to {len(matching_sessions)} sessions matching '{vm_pattern}'")
        return results

    # ==================== BACKWARD COMPATIBLE METHODS ====================
    def execute_vm_async(self, vm_id: str, lua_code: str, 
                        timeout: Optional[float] = None) -> Future:
        """
        Execute Lua code on a VM asynchronously (backward compatible).
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise ValueError(f"VM '{vm_id}' not found")
        def execute():
            return vm.execute_string(lua_code, timeout=timeout)
        future = self.executor.submit(execute)
        self.futures[vm_id] = future
        self.logger.debug(f"Started async execution on VM '{vm_id}'")
        return future

    def execute_vm_sync(self, vm_id: str, lua_code: str, 
                       timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute Lua code on a VM synchronously (backward compatible).
        """
        vm = self.get_vm(vm_id)
        if not vm:
            raise ValueError(f"VM '{vm_id}' not found")
        result = vm.execute_string(lua_code, timeout=timeout)
        self.logger.debug(f"Executed sync code on VM '{vm_id}', success={result.get('success', False)}")
        return result

    def start_server_vm(self, vm_id: str, port: int, 
                       timeout: Optional[float] = None) -> Future:
        """Start a VM as a socket server asynchronously."""
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        def start_server():
            return vm.start_server(port, timeout=timeout)
        future = self.executor.submit(start_server)
        self.futures[vm_id] = future
        self.logger.debug(f"Started server VM '{vm_id}' on port {port}")
        return future

    def start_client_vm(self, vm_id: str, host: str, port: int, 
                       message: str = "Hello from client!", 
                       timeout: Optional[float] = None) -> Future:
        """Start a VM as a socket client asynchronously."""
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        def start_client():
            return vm.start_client(host, port, message, timeout=timeout)
        future = self.executor.submit(start_client)
        self.futures[vm_id] = future
        self.logger.debug(f"Started client VM '{vm_id}' connecting to {host}:{port}")
        return future

    def start_p2p_vm(self, vm_id: str, local_port: int,
                     peer_host: Optional[str] = None, peer_port: Optional[int] = None,
                     run_duration: int = 30, timeout: Optional[float] = None) -> Future:
        """Start a VM in P2P mode asynchronously."""
        vm = self.get_vm(vm_id)
        if not vm or not isinstance(vm, NetworkedLuaVM):
            raise ValueError(f"Networked VM '{vm_id}' not found")
        def start_p2p():
            return vm.start_p2p(local_port, peer_host, peer_port, run_duration, timeout=timeout)
        future = self.executor.submit(start_p2p)
        self.futures[vm_id] = future
        self.logger.debug(f"Started P2P VM '{vm_id}' on port {local_port}")
        return future

    # ==================== UTILITY AND MANAGEMENT METHODS ====================
    def wait_for_vm(self, vm_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for an asynchronous VM operation to complete."""
        future = self.futures.get(vm_id)
        if not future:
            raise ValueError(f"No running operation found for VM '{vm_id}'")
        result = future.result(timeout=timeout)
        self.logger.debug(f"VM '{vm_id}' operation completed")
        return result

    def cancel_vm(self, vm_id: str) -> bool:
        """Cancel a running VM operation."""
        future = self.futures.get(vm_id)
        if future and not future.done():
            cancelled = future.cancel()
            if cancelled:
                self.logger.debug(f"Cancelled VM '{vm_id}' operation")
            return cancelled
        return False

    def get_vm_status(self, vm_id: str) -> Optional[str]:
        """Get the status of a VM's current operation."""
        future = self.futures.get(vm_id)
        if not future:
            return None
        if future.cancelled():
            return 'cancelled'
        elif future.done():
            return 'done'
        else:
            return 'running'

    def create_vm_cluster(self, cluster_id: str, vm_count: int, 
                         networked: bool = True) -> List[str]:
        """Create a cluster of VMs with consistent naming."""
        vm_ids = []
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            self.create_vm(vm_id, networked=networked)
            vm_ids.append(vm_id)
        self.logger.debug(f"Created VM cluster '{cluster_id}' with {vm_count} VMs")
        return vm_ids

    def setup_p2p_cluster(self, cluster_id: str, vm_count: int, 
                         base_port: int = 8080, run_duration: int = 60) -> List[Future]:
        """Set up a P2P cluster where each VM connects to the next one in a ring."""
        if vm_count < 2:
            raise ValueError("P2P cluster requires at least 2 VMs")
        # Create VMs if they don't exist
        vm_ids = []
        for i in range(vm_count):
            vm_id = f"{cluster_id}_{i:03d}"
            if vm_id not in self.vms:
                self.create_vm(vm_id, networked=True)
            vm_ids.append(vm_id)
        # Start P2P VMs in a ring topology
        futures = []
        for i, vm_id in enumerate(vm_ids):
            local_port = base_port + i
            # Connect to the next VM in the ring
            next_i = (i + 1) % vm_count
            peer_port = base_port + next_i
            future = self.start_p2p_vm(
                vm_id, 
                local_port, 
                peer_host="localhost", 
                peer_port=peer_port,
                run_duration=run_duration
            )
            futures.append(future)
        self.logger.debug(f"Set up P2P cluster '{cluster_id}' with {vm_count} VMs in ring topology")
        return futures

    def broadcast_to_cluster(self, cluster_pattern: str, lua_code: str,
                           timeout: Optional[float] = None) -> Dict[str, Future]:
        """Broadcast Lua code execution to all VMs matching a pattern."""
        matching_vms = [vm_id for vm_id in self.vms.keys() 
                       if fnmatch.fnmatch(vm_id, cluster_pattern)]
        if not matching_vms:
            raise ValueError(f"No VMs found matching pattern: {cluster_pattern}")
        futures = {}
        for vm_id in matching_vms:
            future = self.execute_vm_async(vm_id, lua_code, timeout=timeout)
            futures[vm_id] = future
        self.logger.debug(f"Broadcast to {len(matching_vms)} VMs matching '{cluster_pattern}'")
        return futures

    def wait_for_cluster(self, futures: Dict[str, Future], 
                        timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Wait for multiple VM operations to complete."""
        results = {}
        for vm_id, future in futures.items():
            try:
                results[vm_id] = future.result(timeout=timeout)
            except Exception as e:
                results[vm_id] = {
                    'error': str(e),
                    'success': False,
                    'stdout': '',
                    'stderr': str(e),
                    'return_code': -1
                }
        self.logger.debug(f"Completed cluster operation for {len(futures)} VMs")
        return results

    def get_cluster_status(self, cluster_pattern: str) -> Dict[str, str]:
        """Get status of all VMs matching a pattern."""
        status = {}
        for vm_id in self.vms.keys():
            if fnmatch.fnmatch(vm_id, cluster_pattern):
                status[vm_id] = self.get_vm_status(vm_id) or 'idle'
        return status

    def cleanup_cluster(self, cluster_pattern: str) -> int:
        """Remove all VMs matching a pattern."""
        matching_vms = [vm_id for vm_id in self.vms.keys() 
                       if fnmatch.fnmatch(vm_id, cluster_pattern)]
        removed_count = 0
        for vm_id in matching_vms:
            if self.remove_vm(vm_id):
                removed_count += 1
        self.logger.debug(f"Cleaned up cluster '{cluster_pattern}': removed {removed_count} VMs")
        return removed_count

    def shutdown_all(self) -> None:
        """Shutdown all VMs and clean up resources."""
        # Cancel all running futures
        cancelled_count = 0
        for future in self.futures.values():
            if not future.done():
                if future.cancel():
                    cancelled_count += 1
        # Clean up all interactive sessions
        self.session_manager.cleanup_all()
        # Clean up all VMs
        vm_count = len(self.vms)
        for vm in self.vms.values():
            vm.cleanup()
        # Clear collections
        self.vms.clear()
        self.futures.clear()
        self._persistent_vms.clear()
        # Shutdown executor
        self.executor.shutdown(wait=True)
        self.logger.debug(f"Shutdown complete: cleaned up {vm_count} VMs, cancelled {cancelled_count} futures")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the VM manager state."""
        running_count = sum(1 for status in [self.get_vm_status(vm_id) for vm_id in self.vms.keys()]
                          if status == 'running')
        networked_count = sum(1 for vm in self.vms.values() 
                            if isinstance(vm, NetworkedLuaVM))
        session_stats = self.session_manager.list_sessions()
        attached_sessions = sum(1 for info in session_stats.values() if info.get('attached', False))
        return {
            'total_vms': len(self.vms),
            'networked_vms': networked_count,
            'basic_vms': len(self.vms) - networked_count,
            'persistent_vms': len(self._persistent_vms),
            'interactive_sessions': len(session_stats),
            'attached_sessions': attached_sessions,
            'running_operations': running_count,
            'completed_operations': len([f for f in self.futures.values() if f.done()]),
            'max_workers': self.max_workers,
            'lua_executable': self.lua_executable
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.shutdown_all()

    def __repr__(self):
        return (f"VMManager(vms={len(self.vms)}, "
                f"interactive_sessions={len(self.session_manager.list_sessions())}, "
                f"max_workers={self.max_workers})")


# Keep the existing VMCluster class for backward compatibility
class VMCluster:
    """
    Helper class for managing a group of related VMs.
    
    Provides a higher-level interface for common cluster operations.
    """
    def __init__(self, manager: VMManager, cluster_id: str, vm_ids: List[str]):
        self.manager = manager
        self.cluster_id = cluster_id
        self.vm_ids = vm_ids

    def broadcast(self, lua_code: str, timeout: Optional[float] = None) -> Dict[str, Future]:
        """Broadcast code execution to all VMs in cluster."""
        futures = {}
        for vm_id in self.vm_ids:
            future = self.manager.execute_vm_async(vm_id, lua_code, timeout=timeout)
            futures[vm_id] = future
        return futures

    def wait_all(self, futures: Dict[str, Future], 
                timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Wait for all cluster operations to complete."""
        return self.manager.wait_for_cluster(futures, timeout=timeout)

    def get_status(self) -> Dict[str, str]:
        """Get status of all VMs in cluster."""
        return {vm_id: self.manager.get_vm_status(vm_id) or 'idle' 
                for vm_id in self.vm_ids}

    def cleanup(self) -> int:
        """Remove all VMs in this cluster."""
        removed = 0
        for vm_id in self.vm_ids:
            if self.manager.remove_vm(vm_id):
                removed += 1
        return removed

    def __len__(self):
        return len(self.vm_ids)

    def __repr__(self):
        return f"VMCluster(id='{self.cluster_id}', vms={len(self.vm_ids)})"