# pylua_bioxen_vm_lib Specification

## Overview

The **pylua_bioxen_vm_lib** (version 0.1.18) is a Python library for managing Lua virtual machines (VMs) within the BioXen framework. It's designed for biological computation and genomic data virtualization.

**Key Features:**
- Synchronous and asynchronous Lua code execution
- Interactive session management  
- Library-agnostic package management
- Isolated Lua environments
- Perfect for lightweight, sandboxed Lua VMs in biological workflows

This specification was updated on August 26, 2025, and aligns with the development branch codebase.

---

## Quick Start

**Getting Started in 30 Seconds:**
This library lets you run Lua code from Python. Create a VM, send it some Lua code, get results back!

```python
from pylua_bioxen_vm_lib import create_vm

# Create and use a VM
vm = create_vm("my_vm")
result = vm.execute_string('return 2 + 2')
print(result['stdout'])  # Output: 4
```

---

## VM Creation

**Purpose:** Creates isolated Lua environments that run as separate processes

### Main Function

```python
create_vm(vm_id="default", networked=False, persistent=False, debug_mode=False, lua_executable="lua")
```

**Parameters:**
- `vm_id` - Unique identifier for your VM (default: "default")
- `networked` - Enable experimental networking features (default: False)
- `persistent` - Keep VM alive between sessions (default: False) 
- `debug_mode` - Show detailed logs for troubleshooting (default: False)
- `lua_executable` - Path to Lua on your system (default: "lua")

**Returns:** A `LuaProcess` object for running Lua code

### Basic Example

```python
from pylua_bioxen_vm_lib import create_vm

# Create a simple VM
vm = create_vm("test_vm", debug_mode=True)

# Run some Lua code
result = vm.execute_string('print("Hello, BioXen!")')

# See the output
print(result['stdout'])  # Output: Hello, BioXen!
```

---

## VM Manager

**Purpose:** Manages multiple Lua VMs and their sessions with lifecycle control

### Main Class: `VMManager`

Handles creating, executing, and managing multiple VMs at once.

### Key Methods

**VM Management:**
- `create_vm(vm_id, networked=False, persistent=False)` - Creates a managed VM
- `execute_vm_sync(vm_id, code)` - Runs Lua code and waits for result
- `execute_vm_async(vm_id, code)` - Runs Lua code without waiting
- `terminate_vm_session(vm_id)` - Shuts down a VM

**Interactive Sessions:**
- `create_interactive_vm(vm_id)` - Creates a persistent session
- `attach_to_vm(vm_id)` - Connects to existing session
- `detach_from_vm(vm_id)` - Disconnects from session
- `send_input(vm_id, input)` - Sends Lua code to session
- `read_output(vm_id)` - Gets output from session
- `list_sessions()` - Shows all active sessions

### Basic Example

```python
from pylua_bioxen_vm_lib import VMManager

# Use context manager for automatic cleanup
with VMManager(debug_mode=True) as manager:
    # Create a VM
    vm = manager.create_vm("managed_vm")
    
    # Run some code
    result = manager.execute_vm_sync("managed_vm", 'print("Result:", 2 + 2)')
    print(result['stdout'])  # Output: Result: 4
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

### Pattern 1: Basic VM Execution

Execute Lua code in a simple, standalone VM:

```python
from pylua_bioxen_vm_lib import create_vm

vm = create_vm("simple_vm", debug_mode=True)
result = vm.execute_string('print("Hello!")')
print(result['stdout'])  # Output: Hello!
```

### Pattern 2: Managed VMs

Use context managers for automatic resource cleanup:

```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    vm = manager.create_vm("managed_vm")
    result = manager.execute_vm_sync("managed_vm", 'return 2 + 2')
    print(result['stdout'])  # Output: 4
```

### Pattern 3: Interactive Sessions

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

### Pattern 4: Package Management

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

- **BioXen Integration:** Designed specifically for biological computing and genomic data virtualization
- **Experimental Networking:** The `networked=True` option is experimental and requires LuaSocket
- **Library-Agnostic:** Package management uses external catalogs, not hardcoded dictionaries
- **Interactive Features:** Package loading and REPL work through `send_input()` and `read_output()`
- **API Access:** For additional features, visit [xAI API](https://xai.com)

---

*This specification aligns with version 0.1.18 of pylua_bioxen_vm_lib and addresses compliance findings from the August 26, 2025 development branch.*