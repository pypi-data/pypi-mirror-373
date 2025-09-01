"""
pylua_bioxen_vm_lib: A Python library for orchestrating networked Lua virtual machines.
This library provides process-isolated Lua VMs managed from Python with built-in
networking capabilities using LuaSocket and full interactive terminal support.
Perfect for distributed computing, microservices, game servers, and sandboxed scripting.
"""
from pylua_bioxen_vm_lib.lua_process import LuaProcess
from pylua_bioxen_vm_lib.vm_manager import VMManager, VMCluster
from pylua_bioxen_vm_lib.interactive_session import InteractiveSession, SessionManager
from pylua_bioxen_vm_lib.networking import NetworkedLuaVM, LuaScriptTemplate, validate_port, validate_host
# XCPngVM imported dynamically in create_vm() to avoid circular imports
from pylua_bioxen_vm_lib.exceptions import (
    LuaVMError,
    LuaProcessError,
    NetworkingError,
    LuaNotFoundError,
    LuaSocketNotFoundError,
    VMConnectionError,
    VMTimeoutError,
    ScriptGenerationError,
    InteractiveSessionError,
    AttachError,
    DetachError,
    PTYError,
    SessionNotFoundError,
    SessionAlreadyExistsError,
    SessionStateError,
    IOThreadError,
    ProcessRegistryError,
    VMManagerError
)

__version__ = "0.1.22"
__author__ = "pylua_bioxen_vm_lib contributors"
__email__ = ""
__description__ = "Process-isolated networked Lua VMs with interactive terminal support"
__url__ = "https://github.com/yourusername/pylua_bioxen_vm_lib"

__all__ = [
    "LuaProcess",
    "NetworkedLuaVM",
    "VMManager",
    "VMCluster",
    "InteractiveSession",
    "SessionManager",
    "LuaScriptTemplate",
    "validate_port",
    "validate_host",
    "LuaVMError",
    "LuaProcessError",
    "NetworkingError",
    "LuaNotFoundError",
    "LuaSocketNotFoundError",
    "VMConnectionError",
    "VMTimeoutError",
    "ScriptGenerationError",
    "InteractiveSessionError",
    "AttachError",
    "DetachError",
    "PTYError",
    "SessionNotFoundError",
    "SessionAlreadyExistsError",
    "SessionStateError",
    "IOThreadError",
    "ProcessRegistryError",
    "VMManagerError",
    "__version__",
    "create_vm",
    "create_manager",
    "create_interactive_manager",
    "create_interactive_session"
]


def create_vm(vm_id: str = "default", vm_type: str = "basic", networked: bool = False, 
              persistent: bool = False, debug_mode: bool = False, 
              lua_executable: str = "lua", config: dict = None):
    """
    Create a Lua VM instance with multi-VM type support (Phase 1).
    
    Args:
        vm_id: Unique identifier for the VM instance
        vm_type: Type of VM to create ("basic" or "xcpng")
        networked: Whether to enable networking capabilities via LuaSocket
        persistent: Whether this VM should be registered for interactive sessions
        debug_mode: Enable debug logging output (default: False)
        lua_executable: Path to Lua interpreter (default: "lua")
        config: Configuration dictionary for VM-specific settings
        
    Returns:
        BasicLuaVM, NetworkedLuaVM, or XCPngVM instance based on vm_type
        
    Raises:
        ValueError: If vm_type is not supported
    """
    # Factory pattern for VM creation
    if vm_type == "basic":
        # Create basic VM (current implementation, maintains backward compatibility)
        if networked:
            return NetworkedLuaVM(name=vm_id, lua_executable=lua_executable, debug_mode=debug_mode)
        else:
            return LuaProcess(name=vm_id, lua_executable=lua_executable, debug_mode=debug_mode)
    
    elif vm_type == "xcpng":
        # Create XCP-ng VM (Phase 1 placeholder, Phase 2 implementation)
        from .xcp_ng_integration import XCPngVM
        return XCPngVM(vm_id, config)
    
    else:
        raise ValueError(f"Unknown VM type: {vm_type}. Supported types: basic, xcpng")


def create_manager(max_workers: int = 10, lua_executable: str = "lua", debug_mode: bool = False) -> VMManager:
    """
    Create a VM Manager for orchestrating multiple Lua VMs.
    
    Args:
        max_workers: Maximum number of worker threads for async operations
        lua_executable: Path to Lua interpreter (default: "lua")
        debug_mode: Enable debug logging output (default: False)
        
    Returns:
        VMManager instance
    """
    return VMManager(max_workers=max_workers, lua_executable=lua_executable, debug_mode=debug_mode)


def create_interactive_manager(max_workers: int = 10, lua_executable: str = "lua", debug_mode: bool = False) -> VMManager:
    """
    Create a VM Manager specifically optimized for interactive sessions.
    
    Args:
        max_workers: Maximum number of worker threads for async operations
        lua_executable: Path to Lua interpreter (default: "lua")
        debug_mode: Enable debug logging output (default: False)
        
    Returns:
        VMManager instance configured for interactive use
    """
    return VMManager(max_workers=max_workers, lua_executable=lua_executable, debug_mode=debug_mode)


def create_interactive_session(vm_id: str = "interactive", networked: bool = False,
                             lua_executable: str = "lua", auto_attach: bool = True, debug_mode: bool = False) -> InteractiveSession:
    """
    Create and optionally attach to an interactive Lua session.
    
    Args:
        vm_id: Unique identifier for the interactive session
        networked: Whether to enable networking capabilities via LuaSocket
        lua_executable: Path to Lua interpreter (default: "lua")
        auto_attach: Whether to automatically attach to the session after creation
        debug_mode: Enable debug logging output (default: False)
        
    Returns:
        InteractiveSession instance
    """
    manager = VMManager(lua_executable=lua_executable, debug_mode=debug_mode)
    return manager.create_interactive_vm(vm_id, networked=networked, auto_attach=auto_attach)