# GitHub Copilot Instructions - Phase 3: Simple Usage Pattern & CLI Integration

## Context Files to Read
Please analyze these specification files in the project root:
- `spec-report.md` - Current pylua_bioxen_vm_lib specification (v0.1.18)
- `xcp-ng-support.md` - Extended specification for XCP-ng integration MVP
- `xcp-ng-support-report.md` - Audit report with implementation requirements

## Important Context: Existing BioXen-luavm CLI
The current `interactive-bioxen-lua.py` shows the CLI frontend structure. Phase 3 should integrate XCP-ng support into this existing CLI pattern, maintaining the current user experience while adding VM type selection.

## Phase 3 Objectives
Complete the MVP by:
1. **Updating BioXen-luavm CLI** to support XCP-ng VM type selection
2. **Adding XCP-ng examples** to existing example scripts
3. **Creating documentation** that covers both library API and CLI integration
4. **Adding configuration management** for XCP-ng settings

## Prerequisites
Phase 1 and 2 must be complete with:
- Working factory pattern with BasicLuaVM and XCPngVM
- XCPngVM class implemented with XAPI client and SSH execution
- Backward compatibility maintained

## Files to Update

### 1. Update `interactive-bioxen-lua.py` (BioXen-luavm CLI)
**Task**: Add XCP-ng VM type selection to existing CLI

**Key Changes Needed**:

#### Update `create_lua_vm()` method
```python
def create_lua_vm(self):
    vm_id = questionary.text(
        "Enter VM ID (unique identifier):",
        validate=lambda x: x and x not in self.vm_status or "VM ID already exists or empty"
    ).ask()
    if not vm_id:
        return

    # NEW: VM Type Selection
    vm_type = questionary.select(
        "Select VM type:",
        choices=[
            Choice("🖥️  Local Process VM (basic)", "basic"),
            Choice("☁️  XCP-ng Virtual Machine (xcpng)", "xcpng"),
        ],
        default="basic"
    ).ask()

    if not vm_type:
        return

    # Handle XCP-ng configuration
    config = {}
    if vm_type == "xcpng":
        config = self._get_xcpng_config()
        if not config:
            print("❌ XCP-ng configuration required")
            return

    profile_name = questionary.text(
        "Enter profile name for this VM:",
        default="standard"
    ).ask()

    try:
        print(f"🔄 Creating {vm_type} VM '{vm_id}' with profile '{profile_name}'...")
        
        # Create VM with type and config
        session = self.vm_manager.create_interactive_vm(vm_id, vm_type=vm_type, config=config)
        
        # Rest of existing logic...
```

#### Add XCP-ng Configuration Helper
```python
def _get_xcpng_config(self) -> Optional[Dict[str, Any]]:
    """Get XCP-ng configuration from user or config file"""
    
    config_choice = questionary.select(
        "XCP-ng configuration:",
        choices=[
            Choice("Load from config file", "file"),
            Choice("Enter manually", "manual"),
            Choice("Cancel", "cancel")
        ]
    ).ask()
    
    if config_choice == "cancel":
        return None
    
    if config_choice == "file":
        config_path = questionary.path(
            "Path to XCP-ng config file (JSON):",
            default="xcpng_config.json"
        ).ask()
        
        try:
            with open(config_path) as f:
                import json
                return json.load(f)
        except Exception as e:
            print(f"❌ Could not load config file: {e}")
            return None
    
    elif config_choice == "manual":
        # Manual configuration entry
        host = questionary.text("XCP-ng host IP/hostname:").ask()
        username = questionary.text("Username:", default="root").ask()
        password = questionary.password("Password:").ask()
        template = questionary.text("VM template name:", default="lua-bio-template").ask()
        
        if not all([host, username, password, template]):
            print("❌ All fields required for XCP-ng configuration")
            return None
            
        return {
            "xcpng_host": host,
            "xcpng_username": username,
            "xcpng_password": password,
            "template": template,
            "memory": "2GB",
            "vcpus": 2,
            "verify_ssl": False
        }
    
    return None
```

#### Update VMStatus class
```python
class VMStatus:
    def __init__(self, profile, vm_type="basic"):
        self.profile = profile
        self.vm_type = vm_type  # NEW: Track VM type
        self.running = False
        self.attached = False
        self.pid = None
        self.created_at = datetime.now()
        self.packages_installed = 0
```

#### Update `list_vms()` method
```python
def list_vms(self):
    if not self.vm_status:
        print("📭 No VMs created")
        return

    print("\n🖥️  VM List:")
    print("-" * 80)
    
    for vm_id, status in self.vm_status.items():
        state_indicators = []
        if status.running:
            state_indicators.append("🟢 Running")
        else:
            state_indicators.append("🔴 Stopped")
        
        if status.attached:
            state_indicators.append("🔗 Attached")
        
        # NEW: Show VM type
        vm_type_icon = "🖥️" if status.vm_type == "basic" else "☁️"
        
        print(f"VM ID: {vm_id}")
        print(f"  Type: {vm_type_icon} {status.vm_type}")
        print(f"  Profile: {status.profile}")
        print(f"  Status: {' '.join(state_indicators)}")
        print(f"  Created: {status.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Uptime: {status.get_uptime()}")
        print()
```

### 2. Create `xcpng_config.json` (NEW FILE - Example Configuration)
**Task**: Provide example XCP-ng configuration file

**Content**:
```json
{
    "xcpng_host": "192.168.1.100",
    "xcpng_username": "root",
    "xcpng_password": "your_secure_password",
    "template": "lua-bio-template",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": false,
    "ssh_timeout": 30,
    "vm_network": "Pool-wide network associated with eth0"
}
```

### 3. Update `examples/basic_usage.py`
**Task**: Add XCP-ng VM usage for library developers

**Requirements**:
- Keep all existing BasicLuaVM examples intact
- Add XCP-ng VM example with error handling
- Show both VM types working with same API

### 4. Update `examples/integration_demo.py`
**Task**: Add XCP-ng integration to existing VMManager demo

**Requirements**:
- Show both BasicLuaVM and XCPngVM in same workflow
- Demonstrate cross-VM type compatibility
- Include biological computation examples

### 5. `docs/api.md`
**Task**: Document updated API and CLI integration

**Sections to Add/Update**:

#### VMManager Updates
```markdown
### create_interactive_vm() - Updated
```python
create_interactive_vm(vm_id, vm_type="basic", config=None)
```

**Parameters:**
- `vm_id` - Unique VM identifier
- `vm_type` - VM type: "basic" (local process) or "xcpng" (XCP-ng VM)
- `config` - Configuration dictionary (required for xcpng)

#### XCP-ng Integration
Document the XAPI client, SSH execution, and configuration requirements.

#### CLI Integration
```markdown
### BioXen-luavm CLI Integration
The BioXen-luavm CLI integrates XCP-ng support through:

1. **VM Type Selection**: Choose between local and XCP-ng VMs during creation
2. **Configuration Management**: Load XCP-ng settings from JSON files or manual entry
3. **Unified Interface**: Same commands work for both VM types
4. **Status Tracking**: CLI shows VM type in status displays

#### CLI Usage
```bash
python3 interactive-bioxen-lua.py
# Select "Create new Lua VM"
# Choose VM type: basic or xcpng
# For xcpng: provide configuration file or enter manually
```
```

### 6. `docs/installation.md`
**Task**: Add complete XCP-ng setup instructions

**Sections to Add**:

#### BioXen-luavm CLI with XCP-ng Support
```markdown
### BioXen-luavm CLI Installation
```bash
# Install BioXen-luavm dependencies
pip install -r requirements.txt

# For XCP-ng support, ensure additional dependencies
pip install requests>=2.31.0 paramiko>=3.0.0
```

#### XCP-ng Host Preparation
```markdown
### XCP-ng Template Setup
Create a Lua-ready template in XCP-ng:

1. **Create base VM** with Ubuntu/Debian
2. **Install Lua runtime**:
   ```bash
   apt-get update
   apt-get install -y lua5.3 luarocks openssh-server git
   systemctl enable ssh
   ```
3. **Configure SSH access** (root or dedicated user)
4. **Convert to template** in XCP-ng management interface
5. **Test template** creates working VMs

#### Configuration File Setup
Create `xcpng_config.json` in BioXen-luavm directory:
```json
{
    "xcpng_host": "your-xcpng-host.local",
    "xcpng_username": "root",
    "xcpng_password": "your_password",
    "template": "lua-bio-template"
}
```
```

### 7. `docs/cli_integration.md` (NEW FILE)
**Task**: Specific CLI integration guide

**Content**:
```markdown
# BioXen-luavm CLI: XCP-ng Integration Guide

## Overview
This guide explains XCP-ng VM support in the BioXen-luavm CLI, added in pylua_bioxen_vm_lib MVP.

## Using XCP-ng VMs in CLI

### 1. VM Creation with Type Selection
When creating a new VM:
1. Select "🚀 Create new Lua VM"
2. Choose VM type:
   - "🖥️ Local Process VM (basic)" - Current functionality
   - "☁️ XCP-ng Virtual Machine (xcpng)" - New XCP-ng support
3. For XCP-ng: Provide configuration (file or manual entry)

### 2. Configuration Options
- **Config File**: Load from `xcpng_config.json`
- **Manual Entry**: Enter host, credentials, template interactively

### 3. Unified VM Management
Once created, XCP-ng VMs work identically to basic VMs:
- Same attach/detach commands
- Same interactive terminal experience
- Same package installation process
- Same monitoring and status displays

## Configuration Management

### Example xcpng_config.json
```json
{
    "xcpng_host": "192.168.1.100",
    "xcpng_username": "root",
    "xcpng_password": "password",
    "template": "lua-bio-template",
    "memory": "2GB",
    "vcpus": 2
}
```

### Security Notes
- Store config files securely (passwords in plain text)
- Consider SSH key authentication for production
- Use network isolation for XCP-ng hosts

## Troubleshooting
- **"Connection failed"**: Check XCP-ng host connectivity
- **"Template not found"**: Verify template exists in XCP-ng
- **"SSH timeout"**: Check VM network configuration and SSH service
```

## Testing Strategy for Phase 3

### CLI Integration Testing
- Test VM type selection in CLI menu
- Verify configuration file loading
- Test manual configuration entry
- Validate error handling for missing XCP-ng infrastructure

### Example Script Testing
- Ensure all Python examples run without syntax errors
- Test with mock XCP-ng responses
- Verify biological computation examples are correct

## Success Criteria for Phase 3
- [ ] CLI supports VM type selection (basic/xcpng)
- [ ] XCP-ng configuration loading works (file and manual)
- [ ] VM status displays show VM type correctly
- [ ] All existing CLI functionality preserved
- [ ] Examples demonstrate both VM types
- [ ] Documentation covers CLI usage patterns
- [ ] Configuration examples are provided
- [ ] Troubleshooting guide covers common issues

## MVP Validation: Complete Workflow Test
Create this validation checklist for the complete MVP:

### Library API Validation
```python
# Test: Direct library API with both VM types
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Basic VM (existing)
    basic_vm = manager.create_interactive_vm("test_basic", vm_type="basic")
    
    # XCP-ng VM (new)
    xcpng_vm = manager.create_interactive_vm("test_xcpng", vm_type="xcpng", config={
        "xcpng_host": "test-host",
        "template": "lua-bio-template"
    })
    
    # Same API for both types
    manager.send_input("test_basic", "print('Basic VM works')")
    manager.send_input("test_xcpng", "print('XCP-ng VM works')")
```

### CLI Integration Validation
```bash
# Test: CLI supports both VM types
python3 interactive-bioxen-lua.py
# 1. Create basic VM - should work as before
# 2. Create xcpng VM - should prompt for configuration
# 3. List VMs - should show both types with icons
# 4. Attach to both - should work identically
```

### Configuration Validation
```bash
# Test: Configuration file loading
echo '{"xcpng_host":"test","template":"lua-template"}' > xcpng_config.json
# CLI should load this file when creating xcpng VM
```

## Implementation Notes for CLI Integration

### Maintaining Existing UX
- Keep all existing menu options and flows
- VM type selection should feel natural, not disruptive
- Error messages should be helpful and actionable
- Preserve the emoji-rich CLI style

### Configuration Strategy
- Support both file-based and manual configuration
- Validate configuration before VM creation attempts
- Provide clear error messages for configuration issues
- Cache configuration for repeated use

### Error Handling in CLI
```python
# Pattern for XCP-ng errors in CLI
try:
    session = self.vm_manager.create_interactive_vm(vm_id, vm_type="xcpng", config=config)
except VMManagerError as e:
    print(f"❌ XCP-ng VM creation failed: {e}")
    print("💡 Check XCP-ng host connectivity and configuration")
    return
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    return
```

### Status Display Updates
- Show VM type icons (🖥️ for basic, ☁️ for xcpng)
- Include XCP-ng host information in detailed status
- Differentiate between local and remote VM states

## Documentation Strategy

### Focus Areas
1. **CLI User Guide**: How to use XCP-ng VMs through BioXen-luavm
2. **Library Developer Guide**: Direct API usage for extending functionality
3. **Setup Guide**: Complete XCP-ng infrastructure setup
4. **Troubleshooting**: Common issues and solutions

### Documentation Tone
- Match the existing practical, example-focused style
- Include complete, runnable examples
- Provide troubleshooting for real-world scenarios
- Maintain focus on biological computation use cases

## Phase 3 Completion Criteria

### For CLI Users (Primary Audience)
- Can select XCP-ng VM type in BioXen-luavm CLI
- Can configure XCP-ng connection (file or manual)
- Can create and use XCP-ng VMs identically to basic VMs
- Can troubleshoot common configuration issues

### For Library Developers
- Can use new VM factory pattern in Python code
- Can extend XCP-ng functionality if needed
- Have complete API documentation and examples

### For System Administrators
- Can set up XCP-ng templates for Lua computation
- Can configure networking and security properly
- Can troubleshoot connectivity and template issues

## MVP Success Definition
After Phase 3, the complete workflow should work:
1. **Setup**: Install BioXen-luavm and configure XCP-ng template
2. **CLI Usage**: Create XCP-ng VM through CLI menu selection
3. **Execution**: Run biological Lua computations in XCP-ng VM
4. **Management**: Attach/detach/monitor XCP-ng VMs like basic VMs
5. **Cleanup**: Stop and cleanup XCP-ng VMs properly

This completes the MVP for XCP-ng integration in both the library and CLI frontend.