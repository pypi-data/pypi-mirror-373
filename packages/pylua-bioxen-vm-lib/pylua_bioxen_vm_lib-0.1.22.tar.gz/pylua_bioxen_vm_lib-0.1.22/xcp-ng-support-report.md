# Audit Report: pylua_bioxen_vm_lib vs XCP-ng Support MVP

## Summary
This audit compares the current codebase against the requirements in `xcp-ng-support.md` for a minimum viable prototype (MVP) of XCP-ng integration. The goal is to add basic XCPngVM support using XCP-ng's XAPI (native management API), while maintaining backward compatibility and focusing on rapid prototyping.

## Key MVP Requirements
- Multi-VM class foundation (BasicLuaVM, XCPngVM)
- XCPngVM: XAPI integration, template-based deployment, SSH-based Lua execution, basic resource management
- LLM-generated middleware for XAPI client, config mapping, response parsing, error handling
- Factory pattern for VM creation (basic + xcpng)
- Networking, environment, and package management for XCP-ng VMs
- New module: `xcp_ng_integration.py`
- Basic tests and documentation updates

## Audit Findings
### Core Library
- `vm_manager.py`: Needs extension for XCPngVM, XCP-ng config, and XAPI middleware integration.
- `lua_process.py`: Should abstract VM communication and add XCP-ng backend support (SSH execution).
- `networking.py`: Needs XCP-ng network config support via XAPI.
- `env.py` & `curator.py`: Should support SSH-based package management for XCP-ng VMs.
- `cli.py`/`cli.py2`: Should allow selection and management of XCPngVM type.
- **Missing:** `xcp_ng_integration.py` (required for XCPngVM, XAPI client, and config mapping).

### Factory Pattern
- VM factory should support XCPngVM creation and configuration.

### Tests
- **Missing:** `tests/test_xcpng_vm.py`, `tests/test_xcpng_integration.py`, `tests/test_xcpng_networking.py`.
- Existing tests need extension for XCP-ng VM scenarios and cross-VM compatibility.

### Examples
- Example scripts should demonstrate XCP-ng VM creation, execution, and package installation.

### Documentation
- **Missing:** XCP-ng setup guide, VM type selection, XCP-ng config reference, troubleshooting.
- Existing docs need updates for new VM type and integration steps.

## Files Requiring Updates or Creation
- `pylua_bioxen_vm_lib/vm_manager.py`
- `pylua_bioxen_vm_lib/lua_process.py`
- `pylua_bioxen_vm_lib/networking.py`
- `pylua_bioxen_vm_lib/env.py`
- `pylua_bioxen_vm_lib/utils/curator.py` (and/or `curator.py2`)
- `pylua_bioxen_vm_lib/cli.py` and/or `cli.py2`
- `pylua_bioxen_vm_lib/xcp_ng_integration.py` (new, with XAPI client)
- `tests/test_xcpng_vm.py` (new)
- `tests/test_xcpng_integration.py` (new)
- `tests/test_xcpng_networking.py` (new)
- `examples/basic_usage.py`, `examples/distributed_compute.py`, `examples/integration_demo.py`, `examples/fixed-integration-demo.py`, `examples/p2p_messaging.py`
- `docs/api.md`, `docs/examples.md`, `docs/installation.md` (plus new XCP-ng-specific docs)

## Strategic Gaps
- No current support for XCPngVM or XAPI middleware.
- No XCP-ng-specific networking, environment, or package management.
- No LLM-generated middleware for XAPI/config translation.
- No XCP-ng-related tests or documentation.

## Recommendations
1. Implement `xcp_ng_integration.py` with XCPngVM and XAPI client.
2. Extend VMManager, LuaVMFactory, and related modules for XCP-ng support.
3. Add XCP-ng-specific networking, environment, and package management logic.
4. Develop new tests and documentation for XCP-ng integration.
5. Maintain backward compatibility and MVP focus.


## xAPI Integration with XCP-ng Support
xAPI (Experience API) can be integrated with XCP-ng VM management in pylua_bioxen_vm_lib to enable standardized tracking and reporting of VM-based activities. Each VM operation (creation, execution, package installation) can generate xAPI statements describing the activity, agent, and results, which are sent to a Learning Record Store (LRS). This enables:
- Persistent tracking of VM lifecycle events and user actions
- Standardized reporting and analytics for biological compute workflows
- Interoperability with external learning and research platforms

To implement this:
- Add xAPI client functionality to pylua_bioxen_vm_lib
- Map VM activities and results to xAPI statements
- Transmit statements to an LRS at key workflow steps
- Support authentication and secure communication with the LRS

Integrating xAPI will enhance auditability, reproducibility, and compliance for scientific workflows managed by XCP-ng VMs.

## Conclusion
Significant updates are required to meet the XCP-ng support MVP. The codebase should prioritize modular, incremental changes to enable XCPngVM and XAPI integration, with supporting tests and documentation.
