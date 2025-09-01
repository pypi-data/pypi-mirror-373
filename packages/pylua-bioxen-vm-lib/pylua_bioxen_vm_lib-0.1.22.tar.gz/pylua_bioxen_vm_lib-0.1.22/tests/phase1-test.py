#!/usr/bin/env python3
"""
Phase 1 Test: Basic Multi-VM Support

Tests the implementation of Phase 1 requirements:
1. vm_type parameter support in create_vm()
2. Factory pattern for basic and xcpng VM types
3. Backward compatibility with existing code
4. Placeholder XCPngVM class functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pylua_bioxen_vm_lib import create_vm, VMManager
from pylua_bioxen_vm_lib.xcp_ng_integration import XCPngVM
from pylua_bioxen_vm_lib.lua_process import LuaProcess
from pylua_bioxen_vm_lib.networking import NetworkedLuaVM


def test_create_vm_basic():
    """Test create_vm() with vm_type='basic' (maintains backward compatibility)"""
    print("\n1. Testing create_vm() with vm_type='basic'")
    
    # Test basic VM creation
    vm = create_vm("test_basic", vm_type="basic")
    assert isinstance(vm, LuaProcess)
    assert vm.name == "test_basic"
    print("✅ Basic VM creation works")
    
    # Test networked basic VM
    vm_net = create_vm("test_basic_net", vm_type="basic", networked=True)
    assert isinstance(vm_net, NetworkedLuaVM)
    print("✅ Networked basic VM creation works")


def test_create_vm_xcpng():
    """Test create_vm() with vm_type='xcpng' (placeholder)"""
    print("\n2. Testing create_vm() with vm_type='xcpng'")
    
    config = {
        "xcpng_host": "192.168.1.100",
        "username": "root", 
        "password": "test",
        "template": "lua-bio-template"
    }
    
    vm = create_vm("test_xcpng", vm_type="xcpng", config=config)
    assert isinstance(vm, XCPngVM)
    assert vm.vm_id == "test_xcpng"
    assert vm.config == config
    print("✅ XCP-ng VM creation works")


def test_create_vm_invalid_type():
    """Test create_vm() with invalid vm_type raises error"""
    print("\n3. Testing create_vm() with invalid vm_type")
    
    try:
        create_vm("test_invalid", vm_type="invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown VM type" in str(e)
        print("✅ Invalid VM type properly rejected")


def test_backward_compatibility():
    """Test that existing code still works (backward compatibility)"""
    print("\n4. Testing backward compatibility")
    
    # Test default behavior (should create basic VM)
    vm_default = create_vm("test_default")
    assert isinstance(vm_default, LuaProcess)
    print("✅ Default create_vm() still works")
    
    # Test old-style parameters
    vm_old = create_vm("test_old", networked=True, debug_mode=True)
    assert isinstance(vm_old, NetworkedLuaVM)
    print("✅ Old-style parameters still work")


def test_vm_manager_factory():
    """Test VMManager with vm_type parameter"""
    print("\n5. Testing VMManager factory pattern")
    
    manager = VMManager(debug_mode=True)
    
    # Test basic VM via manager
    vm_basic = manager.create_vm("manager_basic", vm_type="basic")
    assert isinstance(vm_basic, LuaProcess)
    print("✅ VMManager basic VM creation works")
    
    # Test XCP-ng VM via manager
    config = {
        "xcpng_host": "test.example.com",
        "username": "admin",
        "password": "secret", 
        "template": "test-template"
    }
    vm_xcpng = manager.create_vm("manager_xcpng", vm_type="xcpng", config=config)
    assert isinstance(vm_xcpng, XCPngVM)
    print("✅ VMManager XCP-ng VM creation works")
    
    # Test VM info tracking
    info = manager.get_vm_info("manager_xcpng")
    assert info["vm_type"] == "xcpng"
    print("✅ VM type tracking works")


def test_xcpng_placeholder_methods():
    """Test that XCPngVM placeholder methods raise NotImplementedError"""
    print("\n6. Testing XCPngVM placeholder functionality")
    
    config = {
        "xcpng_host": "test.local",
        "username": "user",
        "password": "pass",
        "template": "template"
    }
    
    vm = XCPngVM("test_placeholder", config)
    
    # Test status method (should work)
    status = vm.get_status()
    assert status["type"] == "xcpng_placeholder"
    assert status["phase"] == "1_placeholder"
    print("✅ XCPngVM status method works")
    
    # Test placeholder methods raise NotImplementedError
    methods_to_test = ["start", "stop", "execute_string", "execute_file", "install_package", "terminate"]
    
    for method_name in methods_to_test:
        try:
            method = getattr(vm, method_name)
            if method_name in ["execute_string", "execute_file"]:
                method("test_code")
            elif method_name == "install_package":
                method("test_package")
            else:
                method()
            assert False, f"{method_name} should raise NotImplementedError"
        except NotImplementedError as e:
            assert "Phase 2" in str(e)
            
    print("✅ All placeholder methods properly raise NotImplementedError with Phase 2 message")


def test_config_validation():
    """Test XCP-ng VM config validation"""
    print("\n7. Testing XCP-ng VM config validation")
    
    # Test missing config
    try:
        XCPngVM("test_no_config")
        assert False, "Should require config"
    except ValueError as e:
        assert "requires configuration" in str(e)
        print("✅ Missing config properly rejected")
    
    # Test incomplete config
    incomplete_config = {"xcpng_host": "test.com"}
    try:
        XCPngVM("test_incomplete", incomplete_config)
        assert False, "Should require complete config"
    except ValueError as e:
        assert "missing required keys" in str(e)
        print("✅ Incomplete config properly rejected")


def run_all_tests():
    """Run all Phase 1 tests"""
    print("=" * 60)
    print("PHASE 1 TESTS: Basic Multi-VM Support")
    print("=" * 60)
    
    try:
        test_create_vm_basic()
        test_create_vm_xcpng()
        test_create_vm_invalid_type()
        test_backward_compatibility()
        test_vm_manager_factory()
        test_xcpng_placeholder_methods()
        test_config_validation()
        
        print("\n" + "=" * 60)
        print("🎉 ALL PHASE 1 TESTS PASSED!")
        print("✅ vm_type parameter support implemented")
        print("✅ Factory pattern working for basic and xcpng")
        print("✅ Backward compatibility maintained")
        print("✅ XCPngVM placeholder class functional")
        print("✅ Ready for Phase 2 implementation")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ PHASE 1 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
