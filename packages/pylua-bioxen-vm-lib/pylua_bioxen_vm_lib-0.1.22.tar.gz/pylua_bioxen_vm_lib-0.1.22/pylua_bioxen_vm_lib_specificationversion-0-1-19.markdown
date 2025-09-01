# pylua_bioxen_vm_lib Specification

## Overview

The **pylua_bioxen_vm_lib** (version 0.1.19!) is a Python library for managing Lua virtual machines (VMs) within the BioXen framework. It's designed for biological computation and genomic data virtualization with multi-VM support.

**Key Features:**
- **Multi-VM Architecture**: Support for different VM types via factory pattern
- **XCP-ng Integration**: Placeholder support for XCP-ng VMs (Phase 2 implementation coming)
- Synchronous and asynchronous Lua code execution
- Interactive session management  
- Library-agnostic package management
- Isolated Lua environments
- Perfect for lightweight, sandboxed Lua VMs in biological workflows

This specification was updated on September 1, 2025, and reflects the Phase 1 multi-VM implementation.

---

## Quick Start

**Getting Started in 30 Seconds:**
This library lets you run Lua code from Python. Create a VM, send it some Lua code, get results back!

```python
from pylua_bioxen_vm_lib import create_vm

# Create and use a basic VM (backward compatible)
vm = create_vm("my_vm")
result = vm.execute_string('return 2 + 2')
print(result['stdout'])  # Output: 4

# Or explicitly specify VM type
vm = create_vm("my_vm", vm_type="basic")
result = vm.execute_string('return 2 + 2')
print(result['stdout'])  # Output: 4
```

---

## VM Creation


**Purpose:** Creates isolated Lua environments that run as separate processes. Now supports multiple VM types via a factory pattern.

### Main Function

```python
create_vm(vm_id="default", vm_type="basic", networked=False, persistent=False, debug_mode=False, lua_executable="lua", config=None)
```

**Parameters:**
- `vm_id` - Unique identifier for your VM (default: "default")
- `vm_type` - Type of VM to create ("basic" for current implementation, "xcpng" for XCP-ng placeholder; default: "basic")
- `networked` - Enable experimental networking features (default: False)
- `persistent` - Keep VM alive between sessions (default: False) 
- `debug_mode` - Show detailed logs for troubleshooting (default: False)
- `lua_executable` - Path to Lua on your system (default: "lua")
- `config` - Optional configuration dictionary for advanced VM types

**Returns:** A VM object (BasicLuaVM or XCPngVM placeholder)

### Factory Pattern Example

```python
from pylua_bioxen_vm_lib import create_vm

# Create a basic VM (current functionality)
vm_basic = create_vm("test_vm", vm_type="basic", debug_mode=True)

# Create an XCP-ng VM (Phase 1 placeholder)
config = {
    "xcpng_host": "192.168.1.100",
    "username": "root",
    "password": "secret",
    "template": "lua-bio-template"
}
vm_xcpng = create_vm("xcpng_vm", vm_type="xcpng", config=config)

# Default behavior (backward compatible)
vm_default = create_vm("my_vm")  # Creates basic VM
```

**Note:**
- If `vm_type` is not specified, defaults to "basic" for backward compatibility.
- If `vm_type` is "xcpng", a placeholder VM is created. Actual XCP-ng functionality will be implemented in Phase 2.
- Invalid `vm_type` values will raise an error.

### Placeholder XCPngVM Class (Phase 1)

```python
import requests
import paramiko

class XCPngVM:
    """Placeholder for XCP-ng VM integration via XAPI (Phase 2 implementation)"""
    def __init__(self, vm_id, config=None):
        self.vm_id = vm_id
        self.config = config or {}
        # Validates required config keys for Phase 2
    def start(self):
        """Start VM using XAPI (stub)"""
        raise NotImplementedError("XCP-ng VM start() functionality coming in Phase 2")
    def stop(self):
        """Stop VM using XAPI (stub)"""
        raise NotImplementedError("XCP-ng VM stop() functionality coming in Phase 2")
    def execute_string(self, lua_code):
        """Execute Lua code in VM via SSH (stub)"""
        raise NotImplementedError("XCP-ng VM execute_string() functionality coming in Phase 2")
    def install_package(self, package_name):
        """Install Lua package via SSH (stub)"""
        raise NotImplementedError("XCP-ng VM install_package() functionality coming in Phase 2")
    def get_status(self):
        """Get VM status information (placeholder)"""
        return {"vm_id": self.vm_id, "status": "placeholder", "type": "xcpng_placeholder"}
    # Additional methods for template-based creation, XAPI client, etc.
```

### Testing and Success Criteria
- Creating a VM with `vm_type="basic"` works as before.
- Creating a VM with `vm_type="xcpng"` returns a placeholder object with clear error messages.
- Default behavior (no `vm_type`) creates a BasicLuaVM.
- Invalid `vm_type` raises an appropriate error.

### Documentation Updates
- The specification now documents the new `vm_type` parameter, available VM types, and the roadmap for XCP-ng integration.
- Backward compatibility is guaranteed for all existing code and usage patterns.

---

## VM Manager

**Purpose:** Manages multiple Lua VMs and their sessions with lifecycle control

### Main Class: `VMManager`

Handles creating, executing, and managing multiple VMs at once.

### Key Methods

**VM Management:**
- `create_vm(vm_id, vm_type="basic", networked=False, persistent=False)` - Creates a managed VM with multi-VM type support
- `execute_vm_sync(vm_id, code)` - Runs Lua code and waits for result
- `execute_vm_async(vm_id, code)` - Runs Lua code without waiting
- `terminate_vm_session(vm_id)` - Shuts down a VM
- `get_vm_info(vm_id)` - Gets detailed VM information including type

**Interactive Sessions:**
- `create_interactive_vm(vm_id)` - Creates a persistent session
- `attach_to_vm(vm_id)` - Connects to existing session
- `detach_from_vm(vm_id)` - Disconnects from session
- `send_input(vm_id, input)` - Sends Lua code to session
- `read_output(vm_id)` - Gets output from session
- `list_sessions()` - Shows all active sessions

### Multi-VM Management Example

```python
from pylua_bioxen_vm_lib import VMManager

# Use context manager for automatic cleanup
with VMManager(debug_mode=True) as manager:
    # Create a basic VM
    basic_vm = manager.create_vm("basic_vm", vm_type="basic")
    
    # Create an XCP-ng VM (placeholder)
    config = {
        "xcpng_host": "192.168.1.100",
        "username": "root",
        "password": "secret",
        "template": "lua-bio-template"
    }
    xcpng_vm = manager.create_vm("xcpng_vm", vm_type="xcpng", config=config)
    
    # Run code on basic VM
    result = manager.execute_vm_sync("basic_vm", 'print("Hello from basic VM")')
    print(result['stdout'])
    
    # Get VM information
    info = manager.get_vm_info("xcpng_vm")
    print(f"VM Type: {info['vm_type']}")  # Output: xcpng
```

---

## Interactive Sessions

**Purpose:** Real-time interaction with Lua VMs for dynamic scripting

### Main Class: `InteractiveSession`

Allows back-and-forth communication with a Lua VM, like a chat conversation.

### Key Methods

- `send_input(input)` - Sends Lua code to the session
- `read_output()` - Gets output from the session  
- `set_environment(env_name)` - Sets the Lua environment

**Note:** Package loading and REPL functionality work through `send_input()` and `read_output()`. There are no separate `load_package()` or `interactive_loop()` methods.

### Interactive Example

```python
from pylua_bioxen_vm_lib import VMManager
import time

# Create an interactive session
manager = VMManager(debug_mode=True)
session = manager.create_interactive_vm("interactive_vm")

# Send some Lua code
manager.send_input("interactive_vm", "x = 42\nprint('Value:', x)\n")

# Wait a moment for processing
time.sleep(0.5)

# Read the result
print(manager.read_output("interactive_vm"))  # Output: Value: 42
```

---

## Session Manager

**Purpose:** Manages the lifecycle of interactive sessions

### Main Class: `SessionManager`

Access this through `VMManager.session_manager` to control sessions.

### Key Methods

- `list_sessions()` - Returns dictionary of active sessions and details
- `terminate_session(vm_id)` - Terminates a specific session

### Session Management Example

```python
from pylua_bioxen_vm_lib import VMManager

manager = VMManager(debug_mode=True)
session_manager = manager.session_manager

# Create a session
session = manager.create_interactive_vm("test_session")

# List active sessions
sessions = session_manager.list_sessions()
print(sessions)  # Output: {'test_session': <session_details>}

# Clean up
session_manager.terminate_session("test_session")
```

---

## Package Management

**Purpose:** Manages Lua packages and isolated environments using external catalogs

### Key Modules

- `pylua_bioxen_vm_lib.utils.curator` - Package metadata and repositories
- `pylua_bioxen_vm_lib.env` - Environment management
- `pylua_bioxen_vm_lib.package_manager` - Package operations

### Key Classes & Functions

- `Curator` and `get_curator()` - Manages package metadata
- `PackageInstaller` - Installs, updates, and removes packages
- `EnvironmentManager` - Manages isolated Lua environments
- `PackageManager` - Orchestrates package operations
- `RepositoryManager` - Manages package repositories
- `search_packages(query)` - Searches available packages
- `bootstrap_lua_environment(env_name)` - Sets up Lua environment

**Important:** Package management uses external catalogs, not hardcoded dictionaries. Load packages by sending `require` statements via `send_input()`.

### Package Example

```python
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller, search_packages

# Search and install a package
installer = PackageInstaller()
packages = search_packages("bio_compute")
installer.install_package("bio_compute")
```

---

## Exception Handling

**Purpose:** Provides specific exceptions for robust error handling

### Key Exceptions

**Session Errors:**
- `InteractiveSessionError` - General session management errors
- `AttachError` - Problems attaching to sessions
- `DetachError` - Problems detaching from sessions  
- `SessionNotFoundError` - Invalid session ID
- `SessionAlreadyExistsError` - Duplicate session creation

**VM Errors:**
- `VMManagerError` - VM manager operation errors
- `LuaVMError` - Lua code execution errors

### Error Handling Example

```python
from pylua_bioxen_vm_lib import VMManager
from pylua_bioxen_vm_lib.exceptions import SessionNotFoundError

try:
    VMManager().attach_to_vm("nonexistent")
except SessionNotFoundError:
    print("Session not found")
```

---

## Logging

**Purpose:** Configurable logging for debugging and monitoring

### Main Class: `VMLogger`

**Parameters:**
- `debug_mode` - Enable verbose logging (True/False)
- `component` - Specify logging component name

### Logging Example

```python
from pylua_bioxen_vm_lib.logger import VMLogger

logger = VMLogger(debug_mode=True, component="MyApp")
logger.debug("Debug message")
```

---

## Usage Patterns

### Pattern 1: Basic VM Execution (Backward Compatible)

Execute Lua code in a simple, standalone VM:

```python
from pylua_bioxen_vm_lib import create_vm

# Default behavior (backward compatible)
vm = create_vm("simple_vm", debug_mode=True)
result = vm.execute_string('print("Hello!")')
print(result['stdout'])  # Output: Hello!

# Explicit basic VM creation
vm_basic = create_vm("basic_vm", vm_type="basic", debug_mode=True)
result = vm_basic.execute_string('print("Hello from basic VM!")')
print(result['stdout'])  # Output: Hello from basic VM!
```

### Pattern 2: Multi-VM Factory Pattern (Phase 1)

Create different types of VMs using the factory pattern:

```python
from pylua_bioxen_vm_lib import create_vm

# Create a basic VM
basic_vm = create_vm("basic_test", vm_type="basic")

# Create an XCP-ng VM (Phase 1 placeholder)
config = {
    "xcpng_host": "192.168.1.100",
    "username": "root",
    "password": "secret",
    "template": "lua-bio-template"
}
xcpng_vm = create_vm("xcpng_test", vm_type="xcpng", config=config)

# Basic VM works normally
result = basic_vm.execute_string('return "Hello from Basic VM"')
print(result['stdout'])

# XCP-ng VM shows placeholder behavior
try:
    xcpng_vm.execute_string('return "Hello from XCP-ng"')
except NotImplementedError as e:
    print(f"Expected: {e}")  # Shows Phase 2 message
```

### Pattern 3: Managed Multi-VM Environment

Use VMManager for coordinated multi-VM operations:

```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Create multiple VM types
    basic_vm = manager.create_vm("basic_worker", vm_type="basic")
    xcpng_vm = manager.create_vm("xcpng_worker", vm_type="xcpng", config=config)
    
    # Execute on basic VM
    result = manager.execute_vm_sync("basic_worker", 'return 2 + 2')
    print(f"Basic VM result: {result['stdout']}")
    
    # Get VM information
    basic_info = manager.get_vm_info("basic_worker")
    xcpng_info = manager.get_vm_info("xcpng_worker")
    
    print(f"Basic VM type: {basic_info['vm_type']}")  # "basic"
    print(f"XCP-ng VM type: {xcpng_info['vm_type']}")  # "xcpng"
```

### Pattern 4: Interactive Sessions

Manage persistent sessions for back-and-forth coding:

```python
from pylua_bioxen_vm_lib import VMManager
import time

manager = VMManager(debug_mode=True)

# Create interactive session
session = manager.create_interactive_vm("interactive_vm")

# Send code
manager.send_input("interactive_vm", "x = 10\nprint('Value:', x)\n")
time.sleep(0.5)

# Read result
print(manager.read_output("interactive_vm"))  # Output: Value: 10

# Clean up
manager.detach_from_vm("interactive_vm")
manager.terminate_vm_session("interactive_vm")
```

### Pattern 5: Package Management

Install and use Lua packages in your VMs:

```python
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller
from pylua_bioxen_vm_lib import VMManager
import time

# Install package
installer = PackageInstaller()
installer.install_package("bio_compute")

# Use package in VM
with VMManager() as manager:
    session = manager.create_interactive_vm("package_vm")
    
    # Load and use package
    manager.send_input("package_vm", 'require("bio_compute")\nprint(bio_compute.compute(10))')
    time.sleep(0.5)
    print(manager.read_output("package_vm"))
```

---

## Best Practices

### Resource Management
- **Always use context managers:** Use `VMManager` with `with` statements for automatic cleanup
- **Clean up sessions:** Always detach and terminate sessions to free resources

### Error Handling  
- **Catch specific exceptions:** Use `SessionNotFoundError`, etc. instead of generic exceptions
- **Validate inputs:** Check session IDs to avoid `SessionAlreadyExistsError`

### Debugging
- **Enable debug mode:** Set `debug_mode=True` or use environment variable:
  ```bash
  export PYLUA_DEBUG=true
  ```

### Package Management
- **Use isolated environments:** Create separate environments with `EnvironmentManager`
- **Load packages properly:** Use `require` statements via `send_input()` - there's no direct `load_package()` method

---

## Complete Example

Here's a full example integrating VMs with package management for biological computation:

```python
import os
import time
from pylua_bioxen_vm_lib import VMManager, VMLogger
from pylua_bioxen_vm_lib.utils.curator import PackageInstaller

# Set up logging
logger = VMLogger(
    debug_mode=os.getenv('PYLUA_DEBUG', 'false').lower() == 'true', 
    component="BioApp"
)

# Install required package
installer = PackageInstaller()
installer.install_package("bio_compute")

# Use the package in a VM
with VMManager(debug_mode=True) as manager:
    # Create interactive session
    session = manager.create_interactive_vm("bio_vm")
    
    # Load package and analyze sequence
    manager.send_input("bio_vm", '''
        require("bio_compute")
        result = bio_compute.analyze_sequence("ATCG")
        print("Analysis result:", result)
    ''')
    
    # Get results
    time.sleep(0.5)
    print(manager.read_output("bio_vm"))
    
    # Clean up
    manager.terminate_vm_session("bio_vm")
```

---

## Installation & Dependencies

### System Requirements
- **Python 3.7+**
- **Lua interpreter** (installed on your system)
- **LuaSocket** (for networking features)

### Installation Steps

```bash
# Install the Python library
pip install pylua_bioxen_vm_lib

# Install Lua dependencies
luarocks install luasocket
```

---

## Additional Notes

- **Multi-VM Architecture:** Phase 1 implementation provides factory pattern for different VM types
- **XCP-ng Integration:** Phase 1 includes placeholder support; full implementation coming in Phase 2
- **Backward Compatibility:** All existing code works unchanged with new multi-VM features
- **BioXen Integration:** Designed specifically for biological computing and genomic data virtualization
- **Experimental Networking:** The `networked=True` option is experimental and requires LuaSocket
- **Library-Agnostic:** Package management uses external catalogs, not hardcoded dictionaries
- **Interactive Features:** Package loading and REPL work through `send_input()` and `read_output()`

---

## Phase 1 Implementation Status

### ✅ Completed Features (Phase 1)
- **Multi-VM Factory Pattern**: Added `vm_type` parameter supporting "basic" and "xcpng"
- **XCPngVM Placeholder**: Complete placeholder class with Phase 2 implementation roadmap
- **Enhanced VMManager**: Factory pattern and VM type tracking
- **Backward Compatibility**: All existing code works unchanged
- **Comprehensive Testing**: Phase 1 test suite validates all functionality

### 🚧 Upcoming Features (Phase 2)
- **XCP-ng XAPI Integration**: Real XCP-ng VM management via XAPI REST API
- **Template-based Deployment**: VM creation from XCP-ng templates
- **SSH-based Execution**: Remote Lua execution in XCP-ng VMs
- **Package Management**: Curator-based package installation over SSH
- **Enhanced Error Handling**: XCP-ng-specific error mapping and retry logic

### 📋 Implementation Roadmap

**Phase 1 (✅ Complete)**: Basic multi-VM support with placeholders  
**Phase 2 (Next)**: XCP-ng integration with XAPI client and SSH execution  
**Phase 3 (Future)**: Advanced features, xAPI tracking, performance optimization

### 🔧 Phase 1 Usage Examples

```python
# Backward compatible - works exactly as before
vm = create_vm("my_vm")

# New multi-VM API
basic_vm = create_vm("basic", vm_type="basic")
xcpng_vm = create_vm("xcpng", vm_type="xcpng", config={
    "xcpng_host": "host", "username": "user", 
    "password": "pass", "template": "template"
})

# VMManager with multi-VM support
with VMManager() as manager:
    basic = manager.create_vm("basic_worker", vm_type="basic")
    xcpng = manager.create_vm("xcpng_worker", vm_type="xcpng", config=config)
    info = manager.get_vm_info("xcpng_worker")
    print(info["vm_type"])  # "xcpng"
```

---

*This specification reflects version 0.1.19 of pylua_bioxen_vm_lib with Phase 1 multi-VM implementation completed on September 1, 2025.*