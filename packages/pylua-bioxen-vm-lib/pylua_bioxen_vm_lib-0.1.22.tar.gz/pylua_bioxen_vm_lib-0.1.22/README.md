# pylua_bioxen_vm_lib

A Python library for orchestrating networked Lua virtual machines through subprocess management and socket communication with multi-VM support.

## Overview

pylua_bioxen_vm_lib provides a unique approach to running multiple Lua interpreters as isolated processes, managed from Python with built-in networking capabilities. **Version 0.1.19** introduces **Phase 1 multi-VM support** with factory pattern for different VM types including XCP-ng integration placeholders.

## Key Features

- **Multi-VM Architecture** - Factory pattern supporting different VM types (basic, xcpng)
- **Process-isolated Lua VMs** - Each VM runs in its own subprocess for fault tolerance
- **XCP-ng Integration** - Phase 1 placeholder support for XCP-ng VMs (full implementation in Phase 2)
- **Built-in networking** - Socket-based communication using LuaSocket
- **Multiple communication patterns** - Server, client, and P2P messaging modes
- **Dynamic VM management** - Spawn and terminate VMs as needed
- **Language-agnostic architecture** - Could be extended to other interpreters
- **Python orchestration** - Full lifecycle management from Python
- **Interactive sessions** - Attach/detach to running VMs for real-time interaction
- **Backward compatibility** - All existing code works unchanged
## Interactive Terminal Support

pylua_bioxen_vm_lib now supports interactive session management, allowing you to attach to running Lua VMs and interact with them in real-time.

### Interactive Session Management
- Attach/detach to running Lua VMs
- Send input and receive output in real-time
- Session lifecycle management
- Multiple concurrent sessions per VM

### Example Usage
```python
from pylua_bioxen_vm_lib import VMManager, InteractiveSession

manager = VMManager()
vm = manager.create_vm("interactive_vm")

# Start an interactive session
session = InteractiveSession(vm)
session.attach()

# Send commands and get responses
session.send_input("x = 42")
session.send_input("print(x)")
output = session.read_output()

# Detach when done
session.detach()
```

### Multi-VM Support (Phase 1)
```python
from pylua_bioxen_vm_lib import create_vm, VMManager

# Create different types of VMs
basic_vm = create_vm("basic_worker", vm_type="basic")
xcpng_vm = create_vm("xcpng_worker", vm_type="xcpng", config={
    "xcpng_host": "192.168.1.100",
    "username": "root", 
    "password": "secret",
    "template": "lua-bio-template"
})

# Use VMManager for coordinated operations
with VMManager() as manager:
    basic = manager.create_vm("basic", vm_type="basic")
    xcpng = manager.create_vm("xcpng", vm_type="xcpng", config=config)
    
    # Get VM info
    info = manager.get_vm_info("xcpng")
    print(f"VM Type: {info['vm_type']}")  # xcpng
```

## Architecture

```
Python Process
├── VM Manager
│   ├── Lua Process 1 (subprocess)
│   ├── Lua Process 2 (subprocess)
│   └── Lua Process N (subprocess)
└── Networking Layer
    ├── Socket Server
    ├── Socket Client
    └── P2P Communication
```

## Installation

```bash
pip install pylua_bioxen_vm_lib
```

### Prerequisites

- Python 3.7+
- Lua interpreter installed on system
- LuaSocket library (`luarocks install luasocket`)

## Quick Start

```python
from pylua_bioxen_vm_lib import VMManager

# Create a VM manager
manager = VMManager()

# Spawn Lua VMs
vm1 = manager.create_vm("vm1")
vm2 = manager.create_vm("vm2")

# Execute Lua code
result = vm1.execute("return math.sqrt(16)")
print(result)  # 4.0

# Enable networking
vm1.start_server(port=8080)
vm2.connect_to("localhost", 8080)

# Send messages between VMs
vm2.send_message("Hello from VM2!")
message = vm1.receive_message()

# Cleanup
manager.shutdown_all()
```

## Use Cases

- **Distributed computing** - Parallel Lua script execution
- **Game servers** - Isolated game logic processes
- **Microservices** - Lightweight Lua-based services
- **Sandboxed scripting** - Safe execution of untrusted Lua code
- **Load balancing** - Multiple worker processes
- **Protocol testing** - Network protocol simulation

## Communication Patterns

### Server Mode
```python
vm.start_server(port=8080)
vm.accept_connections()
```

### Client Mode  
```python
vm.connect_to("hostname", port)
vm.send_data("message")
```

### P2P Mode
```python
vm1.establish_p2p_with(vm2)
vm1.broadcast("Hello network!")
```

example usage


```python
from pylua_bioxen_vm_lib import VMManager

with VMManager() as manager:
    # Server VM
    server_vm = manager.create_vm("server", networked=True)
    server_future = manager.start_server_vm("server", port=8080)
    
    # Client VM  
    client_vm = manager.create_vm("client", networked=True)
    client_future = manager.start_client_vm("client", "localhost", 8080, "Hello!")
    
    # P2P VM
    p2p_vm = manager.create_vm("p2p", networked=True)
    p2p_future = manager.start_p2p_vm("p2p", 8081, "localhost", 8080)
```

## Examples

See the `examples/` directory for:
- Basic VM management (`basic_usage.py`)
- Distributed computation (`distributed_compute.py`) 
- P2P messaging (`p2p_messaging.py`)

## Documentation

- [API Reference](docs/api.md)
- [Examples](docs/examples.md)
- [Installation Guide](docs/installation.md)

## Development

```bash
git clone https://github.com/yourusername/pylua_bioxen_vm_lib.git
cd pylua_bioxen_vm_lib
pip install -e .
python -m pytest tests/
```

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details.

## Why pylua_bioxen_vm_lib?

Existing Python-Lua integrations focus on embedding Lua within Python processes. pylua_bioxen_vm_lib takes a different approach by managing separate Lua processes, providing:

- **True isolation** - One VM crash doesn't affect others
- **Horizontal scaling** - Easy to distribute across cores/machines  
- **Network-first design** - Built for distributed systems
- **Fault tolerance** - Automatic recovery and reconnection
- **Resource management** - Independent memory and CPU usage per VM

Perfect for applications requiring robust, scalable Lua script execution with network communication capabilities.
