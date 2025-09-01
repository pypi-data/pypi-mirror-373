# GitHub Copilot Instructions - Phase 2: XCP-ng Integration with Interactive Session Support

## Context Files to Read
Please analyze these specification files in the project root:
- `spec-report.md` - Current pylua_bioxen_vm_lib specification (v0.1.18)
- `xcp-ng-support.md` - Extended specification for XCP-ng integration MVP
- `xcp-ng-support-report.md` - Audit report with implementation requirements

## Phase 2 Objectives
Implement XCP-ng integration via XAPI with focus on **interactive session support**. The BioXen-luavm CLI uses persistent sessions (create_interactive_vm, send_input, read_output), not one-shot execution. XCPngVM must support:
1. Create and manage XCP-ng VMs using XAPI REST calls
2. Maintain persistent SSH connections for interactive sessions
3. Handle session-based Lua execution (send_input/read_output pattern)
4. Support attach/detach workflow over SSH
5. Install packages in XCP-ng VMs using existing curator over SSH

## Prerequisites
Phase 1 must be complete with:
- Factory pattern working with BasicLuaVM and XCPngVM placeholder
- `vm_type` parameter in create_interactive_vm() method
- Backward compatibility maintained

## Files to Create/Modify

### 1. Create `pylua_bioxen_vm_lib/xcp_ng_integration.py` (NEW FILE)
**Task**: Implement XCPngVM class with interactive session support

**Core Components Needed**:

#### XAPIClient Class
```python
class XAPIClient:
    """HTTP client for XCP-ng XAPI communication"""
    
    def __init__(self, host, username, password, verify_ssl=False):
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session_token = None
        self.base_url = f"https://{host}"
    
    def authenticate(self):
        """Authenticate with XCP-ng and get session token"""
        # POST to XAPI session endpoint
        # Store session token for subsequent calls
        # Handle authentication errors
    
    def create_vm_from_template(self, template_name, vm_name, config):
        """Create VM from template with specified configuration"""
        # POST to create VM from template
        # Handle memory, vcpu, network configuration
        # Return VM UUID for management
    
    def start_vm(self, vm_uuid):
        """Start the VM and wait for boot completion"""
        # POST to start VM
        # Poll until VM is running
        # Return success/failure
    
    def get_vm_network_info(self, vm_uuid):
        """Get VM IP address for SSH connection"""
        # GET VM network interfaces
        # Extract IP address for SSH access
        # Handle multiple interfaces
    
    def stop_vm(self, vm_uuid):
        """Gracefully shutdown VM"""
        # POST to shutdown VM
        # Wait for clean shutdown
    
    def destroy_vm(self, vm_uuid):
        """Completely remove VM"""
        # DELETE VM and associated resources
```

#### SSHSessionManager Class
```python
class SSHSessionManager:
    """Manages persistent SSH connection for interactive Lua sessions"""
    
    def __init__(self, host, username, password=None, key_filename=None, timeout=30):
        self.host = host
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        self.ssh_client = None
        self.shell_channel = None
        self.connected = False
    
    def connect(self):
        """Establish SSH connection and interactive shell"""
        # Create paramiko SSH client
        # Connect with credentials
        # Open interactive shell channel
        # Start Lua interpreter in shell
    
    def send_input(self, lua_code):
        """Send Lua code to interactive session"""
        # Send code through shell channel
        # Handle line endings and buffering
        # Return success/failure
    
    def read_output(self, timeout=1.0):
        """Read output from interactive session"""
        # Read available output from shell channel
        # Handle partial reads and buffering
        # Return combined stdout/stderr
    
    def disconnect(self):
        """Close SSH connection cleanly"""
        # Close shell channel
        # Close SSH connection
        # Reset connection state
```

#### XCPngVM Class - Interactive Session Implementation
```python
class XCPngVM:
    """XCP-ng VM implementation with interactive session support"""
    
    def __init__(self, vm_id, config=None):
        self.vm_id = vm_id
        self.config = config or {}
        self.vm_uuid = None
        self.vm_ip = None
        self.xapi_client = None
        self.ssh_session = None
        self.running = False
        self.session_active = False
        
        # Initialize XAPI client
        self._init_xapi_client()
    
    def _init_xapi_client(self):
        """Initialize XAPI client from configuration"""
        required_fields = ["xcpng_host", "xcpng_username", "xcpng_password"]
        for field in required_fields:
            if field not in self.config:
                raise VMManagerError(f"Missing required XCP-ng config: {field}")
        
        self.xapi_client = XAPIClient(
            host=self.config["xcpng_host"],
            username=self.config["xcpng_username"],
            password=self.config["xcpng_password"],
            verify_ssl=self.config.get("verify_ssl", False)
        )
    
    def start(self):
        """Create and start XCP-ng VM, establish SSH session"""
        try:
            # Authenticate with XCP-ng
            self.xapi_client.authenticate()
            
            # Create VM from template
            template = self.config.get("template", "lua-bio-template")
            self.vm_uuid = self.xapi_client.create_vm_from_template(
                template, f"lua-vm-{self.vm_id}", self.config
            )
            
            # Start VM
            self.xapi_client.start_vm(self.vm_uuid)
            
            # Get VM IP for SSH
            self.vm_ip = self.xapi_client.get_vm_network_info(self.vm_uuid)
            
            # Establish SSH session
            self.ssh_session = SSHSessionManager(
                host=self.vm_ip,
                username="root",  # Or from config
                password=self.config.get("ssh_password"),
                timeout=self.config.get("ssh_timeout", 30)
            )
            self.ssh_session.connect()
            
            self.running = True
            self.session_active = True
            
        except Exception as e:
            self._cleanup_on_error()
            raise VMManagerError(f"Failed to start XCP-ng VM: {e}")
    
    def stop(self):
        """Stop VM and cleanup resources"""
        try:
            if self.ssh_session:
                self.ssh_session.disconnect()
                self.session_active = False
            
            if self.vm_uuid and self.xapi_client:
                self.xapi_client.stop_vm(self.vm_uuid)
                self.xapi_client.destroy_vm(self.vm_uuid)
            
            self.running = False
            
        except Exception as e:
            raise VMManagerError(f"Failed to stop XCP-ng VM: {e}")
    
    # Interactive Session Methods (Key for CLI integration)
    def send_input(self, input_text):
        """Send input to interactive Lua session"""
        if not self.session_active:
            raise InteractiveSessionError("No active session")
        
        try:
            return self.ssh_session.send_input(input_text)
        except Exception as e:
            raise InteractiveSessionError(f"Failed to send input: {e}")
    
    def read_output(self):
        """Read output from interactive Lua session"""
        if not self.session_active:
            raise InteractiveSessionError("No active session")
        
        try:
            return self.ssh_session.read_output()
        except Exception as e:
            raise InteractiveSessionError(f"Failed to read output: {e}")
    
    def execute_string(self, lua_code):
        """Execute Lua code and return result (for compatibility)"""
        if not self.session_active:
            self.start()
        
        self.send_input(lua_code + "\n")
        time.sleep(0.1)  # Brief wait for execution
        output = self.read_output()
        
        return {"stdout": output, "stderr": ""}
    
    def install_package(self, package_name):
        """Install package using curator over SSH"""
        # Use existing curator logic but execute over SSH
        # Send luarocks install commands via SSH session
        install_cmd = f"luarocks install {package_name}"
        self.send_input(f"os.execute('{install_cmd}')")
```

### 2. Update `pylua_bioxen_vm_lib/vm_manager.py`
**Task**: Support interactive sessions with vm_type parameter

**Key Method Updates**:

#### create_interactive_vm() method
```python
def create_interactive_vm(self, vm_id, vm_type="basic", config=None):
    """Create interactive VM session with specified type"""
    
    # Use factory pattern from Phase 1
    vm = self._create_vm_instance(vm_id, vm_type, config)
    
    # Start the VM (different for basic vs xcpng)
    vm.start()
    
    # Register session
    self.sessions[vm_id] = vm
    
    return vm

def _create_vm_instance(self, vm_id, vm_type, config):
    """Factory method for VM creation"""
    vm_classes = {
        "basic": BasicLuaVM,
        "xcpng": XCPngVM
    }
    
    if vm_type not in vm_classes:
        raise VMManagerError(f"Unknown VM type: {vm_type}")
    
    return vm_classes[vm_type](vm_id, config)
```

#### Session management methods
```python
def send_input(self, vm_id, input_text):
    """Send input to VM session (works for both basic and xcpng)"""
    if vm_id not in self.sessions:
        raise SessionNotFoundError(f"No session found: {vm_id}")
    
    vm = self.sessions[vm_id]
    return vm.send_input(input_text)

def read_output(self, vm_id):
    """Read output from VM session (works for both basic and xcpng)"""
    if vm_id not in self.sessions:
        raise SessionNotFoundError(f"No session found: {vm_id}")
    
    vm = self.sessions[vm_id]
    return vm.read_output()
```

### 3. Update `pylua_bioxen_vm_lib/lua_process.py`
**Task**: Ensure BasicLuaVM supports the interactive session interface

**Requirements**:
- Refactor existing LuaProcess into BasicLuaVM
- Ensure BasicLuaVM has send_input() and read_output() methods
- Maintain existing functionality while supporting new interface
- Create common interface that both BasicLuaVM and XCPngVM implement

**Common Interface Methods Required**:
- `start()` - Initialize VM/process
- `stop()` - Cleanup VM/process  
- `send_input(text)` - Send input to session
- `read_output()` - Read output from session
- `execute_string(code)` - Execute code and return result

## Critical Implementation Requirements

### Interactive Session Support
The CLI expects these methods to work identically for both VM types:
- `create_interactive_vm(vm_id, vm_type, config)`
- `send_input(vm_id, input_text)`
- `read_output(vm_id)`
- `attach_to_vm(vm_id)` / `detach_from_vm(vm_id)`
- `terminate_vm_session(vm_id)`

### SSH Session Management for XCP-ng
- Maintain persistent SSH connection throughout session
- Handle SSH reconnection if connection drops
- Buffer input/output appropriately for interactive use
- Start Lua interpreter in SSH shell and keep it running

### Error Handling Mapping
Map XCP-ng/SSH errors to existing exception types that CLI expects:
- XAPI authentication failures → VMManagerError
- SSH connection failures → InteractiveSessionError  
- VM creation failures → VMManagerError
- Session management issues → SessionNotFoundError, etc.

## Testing Strategy for Phase 2

### Interactive Session Testing
- Test create_interactive_vm() with both vm_types
- Verify send_input/read_output work over SSH for XCP-ng
- Test session persistence and reconnection
- Validate attach/detach functionality

### CLI Compatibility Testing
- Mock test with BioXen-luavm CLI expectations
- Verify exception types match what CLI handles
- Test configuration validation and error reporting

## Success Criteria for Phase 2
- [ ] XCPngVM supports full interactive session interface
- [ ] SSH connection remains persistent for session duration
- [ ] send_input() and read_output() work reliably over SSH
- [ ] XAPI client can create, start, and manage VMs
- [ ] Error handling maps correctly to existing exception types
- [ ] Package installation works over SSH using existing curator
- [ ] All existing BasicLuaVM functionality preserved
- [ ] CLI can create both basic and xcpng interactive sessions

## Key Difference from Original Phase 2 Plan
**Focus on Interactive Sessions**: The implementation must support the CLI's session-based workflow where:
1. VM is created and started once
2. User sends multiple Lua commands over time
3. Each command gets executed and output returned
4. Session persists until explicitly terminated

This is different from simple execute_string() calls - it requires maintaining state and persistent connections for the duration of the interactive session.

## Implementation Priority Order
1. **XAPI Client** - Basic VM lifecycle management
2. **SSH Session Manager** - Persistent interactive connection  
3. **XCPngVM Class** - Integration of XAPI + SSH for sessions
4. **VMManager Integration** - Factory pattern and session management
5. **Error Handling** - Map to existing exception hierarchy

## Phase 2 Validation Test
```python
# Test interactive session workflow
with VMManager(debug_mode=True) as manager:
    # Create XCP-ng interactive session
    session = manager.create_interactive_vm("test_xcpng", vm_type="xcpng", config=config)
    
    # Test interactive workflow (like CLI does)
    manager.send_input("test_xcpng", "x = 42")
    manager.send_input("test_xcpng", "print('Value:', x)")
    output = manager.read_output("test_xcpng")
    
    # Should output: Value: 42
    assert "Value: 42" in output
    
    # Test package installation
    manager.send_input("test_xcpng", "os.execute('luarocks install luasocket')")
    manager.send_input("test_xcpng", "socket = require('socket')")
    
    # Cleanup
    manager.terminate_vm_session("test_xcpng")
```

This validates the interactive session pattern that the CLI depends on.