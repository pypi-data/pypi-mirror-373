# GitHub Copilot Instructions - Phase 1: Basic Multi-VM Support

## Context Files to Read
Please analyze these specification files in the project root:
- `spec-report.md` - Current pylua_bioxen_vm_lib specification (v0.1.18)
- `xcp-ng-support.md` - Extended specification for XCP-ng integration MVP
- `xcp-ng-support-report.md` - Audit report comparing current codebase vs MVP requirements
- `xapi-summary.md` – Summary of the xAPI (Experience API) base standard and its relevance to XCP-ng integration, located in the `xapi-base-standard-documentation` folder.

## Phase 1 Objectives
Implement basic multi-VM support with placeholders only. Focus on:
1. Add `vm_type` parameter to existing `create_vm()` function
2. Create simple factory pattern supporting `vm_type="basic"` and `vm_type="xcpng"`
3. Maintain 100% backward compatibility
4. Add placeholder XCPngVM class structure

## Files to Modify

### 1. `pylua_bioxen_vm_lib/vm_manager.py`
**Task**: Extend VMManager to support vm_type parameter

**Requirements**:
- Add `vm_type="basic"` parameter to `create_vm()` method with default value
- Implement simple factory pattern (dictionary lookup is sufficient for MVP)
- Support `vm_type="basic"` (current functionality) and `vm_type="xcpng"` (placeholder)
- Ensure all existing code continues to work without changes
- Add basic validation for vm_type parameter

**Example Structure**:
```python
def create_vm(self, vm_id, vm_type="basic", networked=False, persistent=False, debug_mode=False, lua_executable="lua", config=None):
    # Factory pattern implementation
    vm_classes = {
        "basic": BasicLuaVM,  # Current implementation
        "xcpng": XCPngVM      # New placeholder
    }
    # Implementation details...
```

### 2. `pylua_bioxen_vm_lib/lua_process.py`
**Task**: Abstract VM communication to prepare for XCP-ng backend

**Requirements**:
- Refactor existing LuaProcess class into BasicLuaVM class
- Create abstract base class or interface for VM types
- Maintain all existing functionality in BasicLuaVM
- Prepare communication abstraction for future XCP-ng SSH support
- No breaking changes to public API

### 3. Create placeholder structure for XCPngVM
**Task**: Add minimal XCPngVM class structure

**Requirements**:
- Create placeholder XCPngVM class with same interface as BasicLuaVM
- Implement stub methods that raise NotImplementedError with helpful messages
- Document intended functionality in docstrings
- Include placeholders for: start(), stop(), execute(), install_package()

**Example Structure**:
```python
class XCPngVM:
    """Placeholder for XCP-ng VM integration via XAPI (Phase 2 implementation)"""
    
    def __init__(self, vm_id, config=None):
        self.vm_id = vm_id
        self.config = config or {}
        
    def execute_string(self, lua_code):
        raise NotImplementedError("XCP-ng VM support coming in Phase 2")
    
    # Additional placeholder methods...
```

## Testing Requirements for Phase 1
- Verify `create_vm()` with `vm_type="basic"` works identically to current implementation
- Verify `create_vm()` with `vm_type="xcpng"` creates XCPngVM placeholder
- Verify default behavior (no vm_type specified) creates BasicLuaVM
- Verify invalid vm_type raises appropriate error

## Documentation Updates for Phase 1
Update specification sections to document:
- New `vm_type` parameter in create_vm()
- Available VM types: "basic" (current), "xcpng" (coming soon)
- Backward compatibility guarantee
- Brief mention of XCP-ng integration roadmap

## Success Criteria for Phase 1
- [ ] All existing functionality works without changes
- [ ] `create_vm(vm_type="basic")` creates functional VM
- [ ] `create_vm(vm_type="xcpng")` creates placeholder that explains Phase 2 is needed
- [ ] Factory pattern is in place and extensible
- [ ] No breaking changes to public API
- [ ] Basic tests pass

## Implementation Notes
- Keep changes minimal and focused
- Use clear error messages for XCPngVM placeholders
- Document all changes in docstrings
- Maintain existing coding style and patterns
- Focus on proving the factory pattern works, not implementing XCP-ng functionality yet

## Next Steps After Phase 1
Phase 2 will implement actual XCP-ng integration in the placeholder XCPngVM class using XAPI client code.