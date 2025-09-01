You're absolutely right. Here's a streamlined MVP plan:

## Minimal MVP Update Plan

### Phase 1: Basic Multi-VM Support (Placeholders Only)
1. **Add VM Types Section**
   - Document `vm_type` parameter in `create_vm()`
   - Show basic factory pattern: `vm_type="basic"` (current) and `vm_type="xcpng"` (placeholder)
   - Backward compatibility note

2. **Add XCPngVM Placeholder Section**
   - Basic class structure
   - SSH execution method
   - XAPI connection concept

### Phase 2: XCP-ng Integration Basics
1. **New XCP-ng Integration Module**
   - Document `xcp_ng_integration.py` placeholder
   - Basic XAPI client structure
   - Template-based VM creation

2. **Update Dependencies**
   - Add `requests` and `paramiko` 
   - XCP-ng connection requirements

### Phase 3: Simple Usage Pattern
1. **Add Pattern 5: Basic XCP-ng Usage**
   - Simple VM creation with XCP-ng
   - Basic Lua execution via SSH
   - Minimal configuration example

That's it. Three phases, focus on proving XCP-ng VMs can run Lua code. No complex xAPI tracking, no advanced features - just the absolute minimum to validate the concept works.

Ready for your next direction?