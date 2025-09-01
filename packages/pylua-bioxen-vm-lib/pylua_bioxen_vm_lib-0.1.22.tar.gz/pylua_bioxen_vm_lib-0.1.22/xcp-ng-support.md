# Extended pylua_bioxen_vm_lib Specification: XCP-ng XAPI Integration (MVP)

## Objective: MINIMUM VIABLE PROTOTYPE
Build a minimal working prototype to extend pylua_bioxen_vm_lib (v0.1.18) with basic XCP-ng integration via XAPI. Focus on proving the concept works through XCP-ng's native management API, not building a complete solution.

**MVP Scope**: Add XCPngVM support to existing BasicLuaVM functionality. Leverage XCP-ng's XAPI for all virtualization management instead of direct hypervisor integration.

## Core Architecture Extensions

### 1. Multi-VM Class Foundation (MVP Scope)
Implement minimal multi-VM architecture with these VM types:
- **BasicLuaVM**: Current implementation (backward compatible)
- **XCPngVM**: NEW - XCP-ng integration via REST APIs

Future VM types deferred until after MVP validation.

### 2. XCP-ng XAPI Integration Strategy
**Philosophy**: Leverage XCP-ng's complete virtualization management platform through its native XAPI instead of direct Xen integration. Use XAPI for all VM lifecycle operations.

**Integration Approach**:
- Use XCP-ng XAPI for all hypervisor operations
- Interface with XCP-ng through XAPI protocol (HTTP-based)
- Leverage existing XCP-ng template and networking systems
- Maintain seamless user experience with zero manual VM configuration
- Build upon proven XCP-ng infrastructure rather than custom Xen tooling

### 3. LLM-Generated Middleware Architecture (MVP Only)
LLMs will generate minimal middleware code for:
- **XAPI Client Code**: HTTP client for XCP-ng XAPI communication
- **Configuration Mapping**: Maps BioXen VM specs to XAPI parameters
- **Response Parsing**: Converts XAPI responses to Python objects
- **Error Handling**: Maps XAPI errors to appropriate Python exceptions

**MVP Limitation**: Advanced workflow orchestration deferred until prototype validation.

Note: LLMs generate the middleware code once - they do not serve as runtime components.

## Implementation Requirements

### Core Library Updates

#### vm_manager.py
- Extend VMManager to support XCPngVM type
- Add XCP-ng connection configuration handling
- Integrate middleware code for XCP-ng API communication
- Support XCP-ng template-based VM deployment
- Maintain backward compatibility with existing create_vm() interface

#### lua_process.py  
- Abstract VM communication to support XCP-ng backend
- Add XCP-ng VM communication via SSH (primary method for MVP)
- Support both process-based and XCP-ng VM-based Lua execution

#### New: xcp_ng_integration.py
- XCPngVM class implementation
- XAPI client (LLM-generated middleware code)
- Configuration mapping utilities
- Template and deployment management
- XAPI session management

#### networking.py
- Extend networking to support XCP-ng network configurations
- Interface with XCP-ng network management APIs
- Support biological workflow networking requirements

#### env.py & curator.py
- Support package installation in XCP-ng VMs
- Handle SSH-based package management for XCP-ng VMs
- Environment isolation for XCP-ng VMs

### Factory Pattern Implementation

```python
class LuaVMFactory:
    @staticmethod
    def create_vm(vm_type, vm_id, config=None):
        # MVP: Only basic and xcp-ng types supported
        vm_classes = {
            "basic": BasicLuaVM,
            "xcpng": XCPngVM  # NEW - MVP implementation only
        }
        if vm_type not in vm_classes:
            raise ValueError(f"Unknown VM type: {vm_type}. MVP supports: {list(vm_classes.keys())}")
        return vm_classes[vm_type](vm_id, config)
```

### XCPngVM Class Requirements (MVP Scope)

#### Minimal Core Interface (inherits from BaseLuaVM)
- `start()`: Create and start XCP-ng VM using REST API
- `stop()`: Gracefully shutdown XCP-ng VM via API
- `execute(lua_code)`: Execute Lua code in VM via SSH
- `install_package(package)`: Install Lua packages using curator over SSH

#### MVP XCP-ng Features (Basic Implementation Only)
- Template-based VM deployment using XCP-ng templates
- Basic resource management (memory, CPU) via API parameters
- SSH communication only for code execution
- Basic HTTP error handling and logging
- Simple VM lifecycle management

#### LLM-Generated Middleware Integration Points (MVP)
- HTTP client code for XCP-ng REST API
- JSON configuration mapping (BioXen specs → XCP-ng API calls)
- Response parsing (XCP-ng JSON → Python objects)
- HTTP error translation (API errors → Python exceptions)

## Dependencies and Integration

### System Dependencies (handled by BioXen-luavm)
```bash
# XCP-ng connection tools
sudo apt-get install curl jq ssh-client
# Python development
sudo apt-get install python-dev python3-dev
```

### Python Dependencies
```python
# Add to requirements.txt
requests>=2.31.0
paramiko>=3.0.0  # For SSH communication
urllib3>=1.26.0
```

### BioXen-luavm Integration
- BioXen-luavm handles XCP-ng connection configuration
- Configures XCP-ng pool access credentials
- Sets up SSH key management for VM access
- Provides XCP-ng connectivity validation tools

## Usage Patterns

### Pattern 5: XCP-ng VM Execution (MVP)
```python
from pylua_bioxen_vm_lib import VMManager

with VMManager(debug_mode=True) as manager:
    # Create XCP-ng VM from template
    vm = manager.create_vm("xcpng_vm", vm_type="xcpng", 
                          config={
                              "template": "lua-bio-template",
                              "xcpng_host": "192.168.1.100",
                              "memory": "2GB",
                              "vcpus": 2
                          })
    
    # Execute biological computation
    result = manager.execute_vm_sync("xcpng_vm", '''
        require("bio_compute")
        sequence = "ATCGTAGCTACG"
        analysis = bio_compute.analyze_dna(sequence)
        print("Analysis:", analysis)
    ''')
    
    print(result['stdout'])
```

### Pattern 6: Basic Package Installation
```python
# Curator installs via SSH in XCP-ng VM
installer = PackageInstaller()
installer.install_package_in_vm("bio_sequence_analysis", 
                                vm_id="xcpng_vm", 
                                vm_type="xcpng")
```

## Testing Requirements

### XCP-ng-Specific Tests (MVP)
- `tests/test_xcpng_vm.py`: XCPngVM class basic functionality
- `tests/test_xcpng_integration.py`: XCP-ng API communication
- `tests/test_xcpng_networking.py`: Basic networking validation

### Integration Tests (MVP)
- Basic cross-VM type compatibility testing
- Package management for XCP-ng VMs
- Simple performance validation

## Documentation Updates

### New Documentation Sections (MVP)
- **XCP-ng Setup Guide**: Integration with BioXen-luavm for XCP-ng connection
- **VM Type Selection Guide**: When to use basic vs xcpng
- **XCP-ng Configuration Reference**: Connection and template parameters
- **Troubleshooting XCP-ng Integration**: Common connection and API issues

## Implementation Strategy (MVP Focus)

### Phase 1: Foundation (MVP Priority)
1. Implement BaseLuaVM abstract class
2. Refactor existing code into BasicLuaVM
3. Create minimal VM factory pattern (basic + xcpng only)
4. Update VMManager to use factory

### Phase 2: XCP-ng MVP Integration
1. Create `xcp_ng_integration.py` module (LLM-generated middleware code)
2. Implement basic XCPngVM class with REST API client
3. Add minimal XCP-ng API communication
4. Implement SSH-based Lua execution
5. Update curator for basic XCP-ng package management

### Phase 3: MVP Validation
1. Basic functionality testing against XCP-ng instance
2. Simple XCP-ng VM creation and Lua execution
3. Package installation verification
4. Integration with BioXen-luavm setup

### Phase 4: Future Enhancement Planning
1. Advanced XCP-ng features (snapshots, migration)
2. Enhanced error handling and retry logic
3. Performance optimization
4. Comprehensive testing and documentation

## Success Criteria (MVP)
- BasicLuaVM maintains existing functionality (zero regression)
- XCPngVM can create and start a basic XCP-ng VM
- Lua code execution works in XCP-ng VM via SSH
- Basic package installation works in XCP-ng VM
- LLM-generated middleware code successfully translates core Python API calls to XCP-ng operations
- Integration with BioXen-luavm setup process
- One biological computing workflow successfully runs on XCP-ng VM

**MVP Success Definition**: Can create an XCP-ng VM, execute simple Lua code, and install one package. Advanced features deferred.

## Notes
- Focus on XCP-ng REST API integration rather than direct Xen management
- Leverage XCP-ng's existing VM lifecycle, networking, and storage management
- Keep Python API consistent between BasicLuaVM and XCPngVM
- Use XCP-ng templates for rapid VM deployment
- Maintain library focus on biological computation and genomic data virtualization
- Validate architecture with minimal working prototype before expanding features