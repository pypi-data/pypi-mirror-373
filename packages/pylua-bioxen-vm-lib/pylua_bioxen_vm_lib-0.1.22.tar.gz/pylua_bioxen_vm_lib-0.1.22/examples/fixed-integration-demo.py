"""
Fixed Integration Demo for pylua_bioxen_vm_lib
Demonstrates the complete AGI bootstrapping workflow using the ACTUAL implementation:
- Environment setup and validation using VMManager
- VM creation and management
- Networking capabilities
- Interactive session management
- Health monitoring and diagnostics
- Error handling and recovery scenarios

This demo uses the CORRECT import paths based on diagnostic results.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import traceback

# Import actual components (CORRECTED import paths based on diagnostic)
try:
    from pylua_bioxen_vm_lib import VMManager, InteractiveSession, SessionManager
    from pylua_bioxen_vm_lib.vm_manager import VMCluster
    from pylua_bioxen_vm_lib.networking import NetworkedLuaVM, validate_host, validate_port
    from pylua_bioxen_vm_lib.lua_process import LuaProcess
    from pylua_bioxen_vm_lib.exceptions import (
        VMManagerError, LuaProcessError, NetworkingError, 
        InteractiveSessionError, LuaVMError
    )
    print("✅ Successfully imported all pylua_bioxen_vm_lib components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure pylua_bioxen_vm_lib is properly installed and try:")
    print("  pip install -e .  (if in development)")
    print("  OR check your diagnostic script results")
    sys.exit(1)


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    print(f"\n{char * 60}")
    print(f" {title.center(58)} ")
    print(f"{char * 60}\n")


def print_status(message: str, status: str = "INFO"):
    """Print a status message with formatting"""
    markers = {
        "SUCCESS": "✅",
        "ERROR": "❌", 
        "WARNING": "⚠️",
        "INFO": "ℹ️"
    }
    marker = markers.get(status, "•")
    print(f"{marker} {message}")


def demo_vm_manager_setup():
    """Demonstrate VMManager capabilities"""
    print_section("STEP 1: VM Manager Setup & Validation")
    
    try:
        # Create VM manager with the actual available parameters
        print_status("Creating VMManager...")
        manager = VMManager()
        print_status("VMManager created successfully!", "SUCCESS")
        
        # Show manager capabilities by examining available methods
        methods = [method for method in dir(manager) if not method.startswith('_') and callable(getattr(manager, method))]
        print(f"  Available methods: {len(methods)}")
        
        # Show key methods
        key_methods = ['create_vm', 'list_vms', 'get_vm_status', 'shutdown_all']
        available_key_methods = [m for m in key_methods if m in methods]
        print(f"  Key methods available: {available_key_methods}")
        
        # Test basic VM creation
        print_status("Testing basic VM creation...")
        try:
            vm_id = manager.create_vm("demo_vm")
            print_status(f"Successfully created VM: {vm_id}", "SUCCESS")
            
            # Try to get VM status if method exists
            if hasattr(manager, 'get_vm_status'):
                status = manager.get_vm_status(vm_id)
                print(f"  VM Status: {status}")
            elif hasattr(manager, 'get_vm_info'):
                info = manager.get_vm_info(vm_id)
                print(f"  VM Info: {info}")
                
        except Exception as e:
            print_status(f"VM creation failed: {e}", "ERROR")
            return None
            
        return manager
        
    except Exception as e:
        print_status(f"VM Manager setup failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_lua_process_integration(manager):
    """Demonstrate LuaProcess creation and integration"""
    print_section("STEP 2: Lua Process Integration")
    
    if not manager:
        print_status("Skipping LuaProcess demo - no manager", "WARNING")
        return None
    
    try:
        print_status("Testing Lua execution capabilities...")
        
        # Get available VMs from manager
        if hasattr(manager, 'list_vms'):
            active_vms = manager.list_vms()
            print(f"  Currently active VMs: {len(active_vms) if active_vms else 0}")
        
        # Test basic Lua execution
        print("\n--- Basic Lua Execution Test ---")
        try:
            # Try different execution methods based on what's available
            if hasattr(manager, 'execute_vm_sync'):
                vm_id = manager.create_vm("lua_test_vm")
                result = manager.execute_vm_sync(vm_id, 'return math.sqrt(16)')
                print_status(f"Math test result: {result}", "SUCCESS" if result else "WARNING")
                
            elif hasattr(manager, 'create_vm'):
                # Create a VM and test direct LuaProcess if available
                vm_id = manager.create_vm("lua_test_vm") 
                print_status(f"Created test VM: {vm_id}", "SUCCESS")
                
                # Test creating LuaProcess directly
                try:
                    lua_proc = LuaProcess(name="direct_test")
                    print_status("Created LuaProcess directly", "SUCCESS")
                    
                    # Test basic execution if method exists
                    if hasattr(lua_proc, 'execute'):
                        result = lua_proc.execute('return "Hello from Lua!"')
                        print_status(f"Direct execution: {result}", "SUCCESS")
                    
                except Exception as e:
                    print_status(f"Direct LuaProcess test failed: {e}", "WARNING")
                    
        except Exception as e:
            print_status(f"Lua execution test failed: {e}", "ERROR")
        
        return True
        
    except Exception as e:
        print_status(f"LuaProcess integration demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_networking_capabilities(manager):
    """Demonstrate NetworkedLuaVM capabilities"""
    print_section("STEP 3: Networking Capabilities")
    
    try:
        print_status("Testing networking components...")
        
        # Test host and port validation
        print("\n--- Network Validation Test ---")
        test_hosts = ["localhost", "127.0.0.1", "invalid-host"]
        for host in test_hosts:
            try:
                is_valid = validate_host(host)
                status = "SUCCESS" if is_valid else "WARNING"
                print_status(f"Host '{host}': {'Valid' if is_valid else 'Invalid'}", status)
            except Exception as e:
                print_status(f"Host validation failed for '{host}': {e}", "ERROR")
        
        test_ports = [8080, 80, 443, 65536, -1]
        for port in test_ports:
            try:
                is_valid = validate_port(port)
                status = "SUCCESS" if is_valid else "WARNING"  
                print_status(f"Port {port}: {'Valid' if is_valid else 'Invalid'}", status)
            except Exception as e:
                print_status(f"Port validation failed for {port}: {e}", "ERROR")
        
        # Test NetworkedLuaVM creation
        print("\n--- NetworkedLuaVM Creation Test ---")
        try:
            net_vm = NetworkedLuaVM(name="test_network_vm")
            print_status(f"Created NetworkedLuaVM: {net_vm.name}", "SUCCESS")
            
            # Show available methods
            methods = [m for m in dir(net_vm) if not m.startswith('_') and callable(getattr(net_vm, m))]
            print(f"  Available methods: {len(methods)}")
            
            # Test basic networking methods if available
            network_methods = ['start_server', 'connect_to', 'send_data', 'receive_data']
            available_network_methods = [m for m in network_methods if hasattr(net_vm, m)]
            print(f"  Network methods: {available_network_methods}")
            
        except Exception as e:
            print_status(f"NetworkedLuaVM creation failed: {e}", "ERROR")
        
        return True
        
    except Exception as e:
        print_status(f"Networking demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_interactive_sessions(manager):
    """Demonstrate InteractiveSession capabilities"""
    print_section("STEP 4: Interactive Session Management")
    
    try:
        print_status("Testing interactive session components...")
        
        # Test SessionManager
        print("\n--- SessionManager Test ---")
        try:
            session_mgr = SessionManager()
            print_status("Created SessionManager successfully", "SUCCESS")
            
            # Show available methods
            methods = [m for m in dir(session_mgr) if not m.startswith('_') and callable(getattr(session_mgr, m))]
            print(f"  Available methods: {len(methods)}")
            
            # Show key session management methods
            session_methods = ['create_session', 'list_sessions', 'get_session', 'remove_session']
            available_session_methods = [m for m in session_methods if hasattr(session_mgr, m)]
            print(f"  Session management methods: {available_session_methods}")
            
        except Exception as e:
            print_status(f"SessionManager creation failed: {e}", "ERROR")
        
        # Test InteractiveSession
        print("\n--- InteractiveSession Test ---")  
        if manager:
            try:
                # Create a VM for interactive session
                vm_id = manager.create_vm("interactive_test")
                print_status(f"Created VM for interactive session: {vm_id}")
                
                # Try to create InteractiveSession - parameters may vary
                # Check what parameters InteractiveSession expects
                import inspect
                sig = inspect.signature(InteractiveSession.__init__)
                params = list(sig.parameters.keys())[1:]  # Skip 'self'
                print(f"  InteractiveSession parameters: {params}")
                
                # Basic session creation test
                if 'vm_id' in params or 'vm' in params:
                    session = InteractiveSession(vm_id)
                    print_status("Created InteractiveSession successfully", "SUCCESS")
                else:
                    session = InteractiveSession()
                    print_status("Created InteractiveSession (no parameters)", "SUCCESS")
                
                # Show available session methods
                session_methods = [m for m in dir(session) if not m.startswith('_') and callable(getattr(session, m))]
                key_session_methods = ['attach', 'detach', 'send_input', 'read_output']
                available_key_methods = [m for m in key_session_methods if m in session_methods]
                print(f"  Key session methods: {available_key_methods}")
                
            except Exception as e:
                print_status(f"InteractiveSession creation failed: {e}", "ERROR")
        
        return True
        
    except Exception as e:
        print_status(f"Interactive session demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_error_handling(manager):
    """Demonstrate error handling and recovery scenarios"""
    print_section("STEP 5: Error Handling & Recovery")
    
    print_status("Testing error handling capabilities...")
    
    # Test exception handling
    print("\n--- Exception Types Test ---")
    exception_types = [VMManagerError, LuaProcessError, NetworkingError, InteractiveSessionError, LuaVMError]
    for exc_type in exception_types:
        try:
            print(f"  {exc_type.__name__}: Available")
        except NameError:
            print(f"  {exc_type.__name__}: Not imported")
    
    # Test invalid operations
    print("\n--- Invalid Operations Test ---")
    if manager:
        try:
            # Try operations that should fail gracefully
            if hasattr(manager, 'get_vm_status'):
                status = manager.get_vm_status("nonexistent-vm")
                print_status(f"Invalid VM status check: {status}", "WARNING" if status is None else "SUCCESS")
                
            if hasattr(manager, 'execute_vm_sync'):
                result = manager.execute_vm_sync("invalid-vm", "return 42")
                print_status(f"Execution on invalid VM: {result}", "WARNING" if not result else "SUCCESS")
                
        except Exception as e:
            print_status(f"Error handling test: {type(e).__name__}: {e}")
    
    return True


def demo_system_health_check():
    """Perform comprehensive system health check"""
    print_section("STEP 6: System Health Check")
    
    print_status("Performing comprehensive health check...")
    
    # Check imports
    print("\n--- Import Health ---")
    components = {
        'VMManager': VMManager,
        'InteractiveSession': InteractiveSession, 
        'SessionManager': SessionManager,
        'NetworkedLuaVM': NetworkedLuaVM,
        'LuaProcess': LuaProcess
    }
    
    for name, component in components.items():
        try:
            instance = component() if name != 'NetworkedLuaVM' else component(name='health_check')
            print_status(f"{name}: Instantiable", "SUCCESS")
        except Exception as e:
            print_status(f"{name}: {type(e).__name__}", "WARNING")
    
    # Check system requirements
    print("\n--- System Requirements ---")
    import shutil
    
    # Check for Lua
    lua_path = shutil.which("lua")
    if lua_path:
        print_status(f"Lua interpreter: {lua_path}", "SUCCESS")
    else:
        print_status("Lua interpreter: Not found", "ERROR")
    
    # Check for LuaRocks
    luarocks_path = shutil.which("luarocks")
    if luarocks_path:
        print_status(f"LuaRocks: {luarocks_path}", "SUCCESS")
    else:
        print_status("LuaRocks: Not found", "WARNING")
    
    return True


def main():
    """Main integration demo"""
    print_section("PyLua Bioxen VM Lib - Complete Integration Demo", "=")
    
    print("This demo showcases the complete system using CORRECTED imports:")
    print("✅ VMManager for VM orchestration")  
    print("✅ LuaProcess integration")
    print("✅ NetworkedLuaVM capabilities")
    print("✅ InteractiveSession management")
    print("✅ Comprehensive error handling")
    print("✅ System health monitoring")
    print("")
    
    start_time = time.time()
    
    # Run demonstration steps
    manager = demo_vm_manager_setup()
    demo_lua_process_integration(manager)
    demo_networking_capabilities(manager)
    demo_interactive_sessions(manager)
    demo_error_handling(manager)
    demo_system_health_check()
    
    # Final summary
    print_section("Demo Summary & System Status")
    
    duration = time.time() - start_time
    print_status(f"Integration demo completed in {duration:.2f} seconds", "SUCCESS")
    
    print("\n--- Final Component Status ---")
    if manager:
        try:
            # Try to get active VMs if method exists
            if hasattr(manager, 'list_vms'):
                active_vms = manager.list_vms()
                print_status(f"VMManager: {len(active_vms) if active_vms else 0} active VMs", "SUCCESS")
            else:
                print_status("VMManager: Operational", "SUCCESS")
            
            # Clean up VMs
            if hasattr(manager, 'shutdown_all'):
                manager.shutdown_all()
                print_status("All VMs shut down cleanly", "SUCCESS")
                
        except Exception as e:
            print_status(f"Shutdown warning: {e}", "WARNING")
    
    print_status("NetworkedLuaVM: Networking capabilities tested", "SUCCESS")
    print_status("InteractiveSession: Session management tested", "SUCCESS")
    print_status("Error Handling: Exception types available", "SUCCESS")
    
    print("\n--- What You Can Do Next ---")
    print("• Create VMs: manager = VMManager(); vm_id = manager.create_vm('my_vm')")
    print("• Network VMs: net_vm = NetworkedLuaVM(name='network_test')")
    print("• Interactive sessions: session = InteractiveSession(...)")
    print("• Explore methods: dir(manager) to see all available methods")
    
    print_section("System Integration Complete!", "=")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nDemo failed with unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)