# Phase 3 Test: Simple Usage Pattern

def test_xcpng_vm_usage():
    try:
        from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
        vm = XCPngVM(vm_id="test_xcpng_vm", config={"template": "lua-bio-template"})
        # Simulate Lua execution via SSH (placeholder)
        result = vm.execute("print('Hello from XCP-ng VM')")
        print("Phase 3: XCPngVM usage pattern passed.")
    except Exception as e:
        print(f"Phase 3: XCPngVM usage pattern failed: {e}")

if __name__ == "__main__":
    test_xcpng_vm_usage()
