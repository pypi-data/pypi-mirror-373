# Implementation Plan: pylua_bioxen_vm_lib Specification Version Update (MVP)

## Overview
This plan outlines the steps and files requiring update or creation to implement the minimal MVP for XCP-ng VM support in pylua_bioxen_vm_lib, based on the current codebase.

## Phase 1: Basic Multi-VM Support (Placeholders Only)
- Update `vm_manager.py` to document and support the `vm_type` parameter in `create_vm()`.
- Add/extend factory pattern logic in `vm_manager.py` or a dedicated factory module.
- Add placeholder for `XCPngVM` in `vm_manager.py` or a new file (see below).
- Ensure backward compatibility with existing VM creation.

## Phase 2: XCP-ng Integration Basics
- Create new module: `xcp_ng_integration.py` (add to `pylua_bioxen_vm_lib/`).
  - Implement placeholder `XCPngVM` class structure.
  - Add basic XAPI client structure (can use requests for HTTP, paramiko for SSH).
  - Document template-based VM creation logic.
- Update dependencies in `requirements.txt` to include `requests` and `paramiko`.
- Update `networking.py` to support XCP-ng network configuration (placeholder logic).
- Update `env.py` and `curator.py` to support SSH-based package management for XCP-ng VMs (minimal changes).

## Phase 3: Simple Usage Pattern
- Update or create example scripts:
  - `examples/basic_usage.py`: Add usage for XCPngVM creation and Lua execution via SSH.
  - `examples/integration_demo.py`, `examples/fixed-integration-demo.py`: Add minimal XCP-ng VM usage patterns.
- Update documentation:
  - `docs/api.md`: Document new VM type and API changes.
  - `docs/examples.md`: Add XCP-ng usage examples.
  - `docs/installation.md`: Add XCP-ng dependency and setup instructions.

## Files Requiring Update or Creation
- `pylua_bioxen_vm_lib/vm_manager.py`
- `pylua_bioxen_vm_lib/xcp_ng_integration.py` (new)
- `pylua_bioxen_vm_lib/networking.py`
- `pylua_bioxen_vm_lib/env.py`
- `pylua_bioxen_vm_lib/utils/curator.py` (and/or `curator.py2`)
- `requirements.txt`
- `examples/basic_usage.py`, `examples/integration_demo.py`, `examples/fixed-integration-demo.py`
- `docs/api.md`, `docs/examples.md`, `docs/installation.md`

## Optional/Testing
- Add minimal test(s) for XCPngVM creation and Lua execution:
  - `tests/test_vm_manager.py`
  - `tests/test_lua_process.py`
  - `tests/test_networking.py`

## Notes
- Focus on placeholders and minimal working logic for MVP.
- Advanced features, xAPI tracking, and full error handling are deferred until after MVP validation.
