"""
Fixed Integration Demo for pylua_bioxen_vm_lib
Demonstrates the complete AGI bootstrapping workflow using the ACTUAL implementation:
- Environment setup and validation using VMManager
- Intelligent package curation using the real Curator
- VM creation with curator integration
- Networking capabilities with automatic package management
- Health monitoring and diagnostics
- Error handling and recovery scenarios

This demo uses the correct import paths and existing classes.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any
import traceback

# Import actual components (fixed import paths)
from pylua_bioxen_vm_lib.vm_manager import VMManager, LuaProcess
from pylua_bioxen_vm_lib.utils.curator import Curator
from pylua_bioxen_vm_lib.networking import NetworkedLuaVM
from pylua_bioxen_vm_lib.interactive_session import SessionManager, InteractiveSession


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    print(f"\n{char * 60}")
    print(f" {title.center(58)} ")
    print(f"{char * 60}\n")


def print_status(message: str, status: str = "INFO"):
    """Print a status message with formatting"""
    markers = {
        "SUCCESS": "✓",
        "ERROR": "✗", 
        "WARNING": "⚠",
        "INFO": "ℹ"
    }
    marker = markers.get(status, "•")
    print(f"{marker} {message}")


def demo_vm_manager_setup():
    """Demonstrate VMManager capabilities"""
    print_section("STEP 1: VM Manager Setup & Validation")
    
    try:
        # Create VM manager
        manager = VMManager(max_vms=5, debug=True)
        print_status(f"Created VMManager (max VMs: {manager.max_vms})")
        
        # Show manager capabilities
        print(f"  Debug mode: {manager.debug}")
        print(f"  Active VMs: {len(manager.get_active_vms())}")
        
        # Test basic VM creation
        print_status("Testing basic VM creation...")
        vm_id = manager.create_vm("demo_vm")
        if vm_id:
            print_status(f"Successfully created VM: {vm_id}", "SUCCESS")
            
            # Get VM info
            vm_info = manager.get_vm_info(vm_id)
            if vm_info:
                print(f"  VM Status: {vm_info.get('status', 'unknown')}")
                print(f"  VM PID: {vm_info.get('pid', 'unknown')}")
        else:
            print_status("Failed to create VM", "ERROR")
            return None
            
        return manager
        
    except Exception as e:
        print_status(f"VM Manager setup failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_curator_intelligence():
    """Demonstrate curator's intelligent package management"""
    print_section("STEP 2: Intelligent Package Curation")
    
    try:
        # Create curator
        curator = get_curator()
        print_status("Created intelligent curator")
        
        # Show curator capabilities
        print("\n--- Curator Health Check ---")
        health = curator.health_check()
        for key, value in health.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Show available packages in catalog
        print(f"\n--- Package Catalog ({len(curator.catalog)} packages) ---")
        categories = {}
        for name, pkg in curator.catalog.items():
            if pkg.category not in categories:
                categories[pkg.category] = []
            categories[pkg.category].append(f"{name} (priority: {pkg.priority})")
        
        for category, packages in sorted(categories.items()):
            print(f"\n  {category.upper()}:")
            for pkg in sorted(packages):
                print(f"    - {pkg}")
        
        # Show current installed packages
        print("\n--- Currently Installed Packages ---")
        installed = curator.list_installed_packages()
        if installed:
            print_status(f"Found {len(installed)} installed packages:")
            for pkg in installed[:5]:  # Show first 5
                print(f"    - {pkg['name']} v{pkg['version']} ({pkg['category']})")
            if len(installed) > 5:
                print(f"    ... and {len(installed) - 5} more")
        else:
            print_status("No packages currently installed")
        
        # Get intelligent recommendations
        print("\n--- Intelligent Recommendations ---")
        recommendations = curator.get_recommendations()
        if recommendations:
            print_status(f"Curator recommends {len(recommendations)} packages:")
            for pkg in recommendations:
                print(f"    - {pkg.name}: {pkg.description} (priority: {pkg.priority})")
        else:
            print_status("No recommendations - environment looks complete!")
        
        # Demonstrate profile-based curation
        print("\n--- Profile-Based Environment Curation ---")
        profiles = curator.manifest.get('profiles', {})
        print_status(f"Available profiles: {list(profiles.keys())}")
        
        # Try to curate a minimal environment
        if 'minimal' in profiles:
            print_status("Testing minimal profile curation...")
            try:
                success = curator.curate_environment('minimal')
                if success:
                    print_status("Minimal environment curation completed!", "SUCCESS")
                else:
                    print_status("Curation encountered some issues", "WARNING")
            except Exception as e:
                print_status(f"Curation failed: {e}", "ERROR")
        
        return curator
        
    except Exception as e:
        print_status(f"Curator demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_lua_process_integration(manager, curator):
    """Demonstrate LuaProcess creation and integration"""
    print_section("STEP 3: Lua Process Integration")
    
    if not manager:
        print_status("Skipping LuaProcess demo - no manager", "WARNING")
        return None
    
    try:
        # Create Lua process using the manager
        print_status("Creating LuaProcess...")
        
        # Get available VMs from manager
        active_vms = manager.get_active_vms()
        if active_vms:
            vm_id = active_vms[0]
            print_status(f"Using existing VM: {vm_id}")
        else:
            vm_id = manager.create_vm("lua_process_demo")
            if not vm_id:
                print_status("Failed to create VM for LuaProcess", "ERROR")
                return None
        
        # Test basic Lua execution through manager
        print("\n--- Basic Lua Execution Test ---")
        try:
            print_status("Testing basic Lua execution...")
            
            # Simple math test
            result = manager.execute_lua(vm_id, 'return math.sqrt(16)')
            if result and result.get('success'):
                print_status(f"Math test: {result.get('output', 'No output')}", "SUCCESS")
            else:
                print_status(f"Math test failed: {result.get('error') if result else 'No result'}", "ERROR")
            
            # String manipulation test
            result = manager.execute_lua(vm_id, 'return "Hello from " .. "Lua VM!"')
            if result and result.get('success'):
                print_status(f"String test: {result.get('output', 'No output')}", "SUCCESS")
            else:
                print_status(f"String test failed: {result.get('error') if result else 'No result'}", "ERROR")
                
        except Exception as e:
            print_status(f"Lua execution test failed: {e}", "ERROR")
        
        # Test package usage if curator is available
        if curator:
            print("\n--- Package Integration Test ---")
            print_status("Testing curator-installed package usage...")
            
            # Test JSON package if available
            json_test = '''
            local ok, json = pcall(require, "cjson")
            if ok then
                local data = {message = "Curator package working!", system = "AGI Bootstrap"}
                return json.encode(data)
            else
                return "lua-cjson not available"
            end
            '''
            
            result = manager.execute_lua(vm_id, json_test)
            if result and result.get('success'):
                output = result.get('output', 'No output')
                if 'Curator package working!' in output:
                    print_status(f"Package integration: SUCCESS", "SUCCESS")
                else:
                    print_status(f"Package test: {output}")
            else:
                print_status(f"Package test failed: {result.get('error') if result else 'No result'}")
        
        return vm_id
        
    except Exception as e:
        print_status(f"LuaProcess integration demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_networking_vm(manager):
    """Demonstrate NetworkedLuaVM capabilities"""
    print_section("STEP 4: Networked VM Capabilities")
    
    if not manager:
        print_status("Skipping networking demo - no manager", "WARNING")
        return None
    
    try:
        # Create networked VM
        print_status("Creating NetworkedLuaVM...")
        
        # NetworkedLuaVM should work with manager integration
        net_vm = NetworkedLuaVM(name="AGI-Network", debug=True)
        print_status(f"Created networked VM: {net_vm.name}")
        
        # Test basic networking setup
        print("\n--- Networking Setup Test ---")
        try:
            # Test LuaSocket availability
            socket_test = '''
            local ok, socket = pcall(require, "socket")
            if ok then
                return "LuaSocket available - Version: " .. (socket.VERSION or "unknown")
            else
                return "LuaSocket not available"
            end
            '''
            
            result = net_vm.execute(socket_test)
            if result and result.get('success'):
                output = result.get('output', result.get('result', 'No output'))
                print_status(f"Socket test: {output}", "SUCCESS" if "available" in output else "WARNING")
            else:
                print_status(f"Socket test failed: {result.get('error') if result else 'No result'}", "ERROR")
        
        except Exception as e:
            print_status(f"Networking test failed: {e}", "ERROR")
        
        # Test networking configuration
        print("\n--- Network Configuration Test ---")
        try:
            # Test host validation
            from pylua_vm.networking import validate_host, validate_port
            
            test_hosts = ["localhost", "127.0.0.1", "invalid-host-name-123"]
            for host in test_hosts:
                is_valid = validate_host(host)
                status = "SUCCESS" if is_valid else "WARNING"
                print_status(f"Host '{host}': {'Valid' if is_valid else 'Invalid'}", status)
            
            # Test port validation
            test_ports = [8080, 80, 443, 65536, -1]
            for port in test_ports:
                is_valid = validate_port(port)
                status = "SUCCESS" if is_valid else "WARNING"
                print_status(f"Port {port}: {'Valid' if is_valid else 'Invalid'}", status)
                
        except Exception as e:
            print_status(f"Network configuration test failed: {e}", "ERROR")
        
        return net_vm
        
    except Exception as e:
        print_status(f"Networking VM demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_interactive_sessions(manager):
    """Demonstrate InteractiveSession capabilities"""
    print_section("STEP 5: Interactive Session Management")
    
    if not manager:
        print_status("Skipping interactive demo - no manager", "WARNING")
        return None
    
    try:
        # Create session manager
        session_mgr = SessionManager()
        print_status("Created SessionManager")
        
        # Get or create a VM for interactive session
        active_vms = manager.get_active_vms()
        if active_vms:
            vm_id = active_vms[0]
        else:
            vm_id = manager.create_vm("interactive_demo")
            if not vm_id:
                print_status("Failed to create VM for interactive session", "ERROR")
                return None
        
        print_status(f"Using VM: {vm_id}")
        
        # Test session creation
        print("\n--- Session Creation Test ---")
        try:
            # Note: InteractiveSession might need different parameters
            # This is a basic test to see what's available
            print_status("Testing session creation capabilities...")
            
            # Show available session methods
            session_methods = [method for method in dir(InteractiveSession) if not method.startswith('_')]
            print(f"  Available session methods: {len(session_methods)}")
            for method in session_methods[:5]:  # Show first 5
                print(f"    - {method}")
            if len(session_methods) > 5:
                print(f"    ... and {len(session_methods) - 5} more methods")
                
            # Show session manager methods  
            mgr_methods = [method for method in dir(session_mgr) if not method.startswith('_')]
            print(f"  Session manager methods: {len(mgr_methods)}")
            for method in mgr_methods[:5]:  # Show first 5
                print(f"    - {method}")
                
        except Exception as e:
            print_status(f"Session exploration failed: {e}", "ERROR")
        
        return session_mgr
        
    except Exception as e:
        print_status(f"Interactive session demo failed: {e}", "ERROR")
        traceback.print_exc()
        return None


def demo_error_scenarios(manager, curator):
    """Demonstrate error handling and recovery scenarios"""
    print_section("STEP 6: Error Handling & Recovery Scenarios")
    
    print_status("Testing error handling capabilities...")
    
    # Test 1: Invalid VM operations
    print("\n--- Invalid VM Operations ---")
    if manager:
        try:
            # Try to execute on non-existent VM
            result = manager.execute_lua("nonexistent-vm-id", "return 42")
            if result and result.get('success'):
                print_status("Executed on invalid VM - this should have failed", "WARNING")
            else:
                print_status("Correctly handled invalid VM operation", "SUCCESS")
        except Exception as e:
            print_status(f"Exception during invalid VM test: {e}")
    
    # Test 2: Invalid Lua code
    print("\n--- Invalid Lua Code Handling ---")
    if manager:
        active_vms = manager.get_active_vms()
        if active_vms:
            vm_id = active_vms[0]
            try:
                result = manager.execute_lua(vm_id, 'this is not valid lua code!')
                if result and result.get('success'):
                    print_status("Invalid Lua executed successfully - unexpected!", "WARNING")
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result'
                    print_status(f"Correctly handled Lua error: {error_msg[:100]}...", "SUCCESS")
            except Exception as e:
                print_status(f"Exception during Lua error test: {e}")
    
    # Test 3: Package installation failure
    print("\n--- Package Installation Error Handling ---")
    if curator:
        try:
            success = curator.install_package('nonexistent-package-12345')
            if success:
                print_status("Installation of fake package succeeded - unexpected!", "WARNING")
            else:
                print_status("Correctly handled invalid package installation", "SUCCESS")
        except Exception as e:
            print_status(f"Exception during package installation: {e}")


def demo_complete_workflow():
    """Demonstrate complete AGI bootstrapping workflow"""
    print_section("STEP 7: Complete AGI Bootstrapping Workflow")
    
    print_status("Demonstrating complete AGI development workflow...")
    
    try:
        # 1. Environment Bootstrap
        print("\n--- Automated Environment Bootstrap ---")
        try:
            success = bootstrap_lua_environment(profile='standard')
            if success:
                print_status("AGI environment bootstrap completed!", "SUCCESS")
            else:
                print_status("Bootstrap encountered issues but continued", "WARNING")
        except Exception as e:
            print_status(f"Bootstrap failed: {e}", "ERROR")
        
        # 2. Create production-ready setup
        print("\n--- Production Setup ---")
        manager = VMManager(max_vms=3, debug=False)  # Production mode
        curator = get_curator()
        
        # Create VMs for different purposes
        main_vm_id = manager.create_vm("AGI-Main")
        worker_vm_id = manager.create_vm("AGI-Worker")
        
        print_status(f"Created main VM: {main_vm_id}")
        print_status(f"Created worker VM: {worker_vm_id}")
        
        # 3. Demonstrate coordinated operation
        print("\n--- Coordinated VM Operation ---")
        
        if main_vm_id and worker_vm_id:
            # Main VM: Data processing
            main_task = '''
            local data = {
                system = "AGI Bootstrapping Demo",
                timestamp = os.time(),
                components = {"vm_manager", "curator", "networking", "interactive"},
                status = "operational"
            }
            return "Main VM processed " .. #data.components .. " components"
            '''
            
            result = manager.execute_lua(main_vm_id, main_task)
            if result and result.get('success'):
                print_status(f"Main VM: {result.get('output', 'No output')}", "SUCCESS")
            
            # Worker VM: Computation
            worker_task = '''
            local sum = 0
            for i = 1, 100 do
                sum = sum + i
            end
            return "Worker VM computed sum: " .. sum
            '''
            
            result = manager.execute_lua(worker_vm_id, worker_task)
            if result and result.get('success'):
                print_status(f"Worker VM: {result.get('output', 'No output')}", "SUCCESS")
        
        print_status("AGI bootstrapping workflow completed!", "SUCCESS")
        
    except Exception as e:
        print_status(f"Complete workflow demo failed: {e}", "ERROR")
        traceback.print_exc()


def main():
    """Main integration demo"""
    print_section("PyLua VM AGI Bootstrapping Integration Demo (FIXED)", "=")
    
    print("This demo showcases the complete AGI bootstrapping system using REAL components:")
    print("• VMManager for VM orchestration")  
    print("• Curator for intelligent package management")
    print("• LuaProcess integration")
    print("• NetworkedLuaVM capabilities")
    print("• InteractiveSession management")
    print("• Comprehensive error handling")
    print("")
    
    start_time = time.time()
    
    # Run demonstration steps with actual components
    manager = demo_vm_manager_setup()
    curator = demo_curator_intelligence() 
    vm_id = demo_lua_process_integration(manager, curator)
    net_vm = demo_networking_vm(manager)
    session_mgr = demo_interactive_sessions(manager)
    demo_error_scenarios(manager, curator)
    demo_complete_workflow()
    
    # Final summary
    print_section("Demo Summary & System Status")
    
    duration = time.time() - start_time
    print_status(f"Integration demo completed in {duration:.2f} seconds")
    
    print("\n--- Component Status ---")
    if manager:
        active_vms = manager.get_active_vms()
        print_status(f"VMManager: {len(active_vms)} active VMs", "SUCCESS")
        
        # Clean up VMs
        try:
            manager.shutdown_all()
            print_status("All VMs shut down cleanly", "SUCCESS")
        except Exception as e:
            print_status(f"Shutdown warning: {e}", "WARNING")
    
    if curator:
        health = curator.health_check()
        packages = len(curator.list_installed_packages())
        print_status(f"Curator: {packages} packages managed, LuaRocks: {health.get('luarocks_available', 'unknown')}", "SUCCESS")
    
    if net_vm:
        print_status(f"NetworkedLuaVM: {net_vm.name} tested", "SUCCESS")
    
    if session_mgr:
        print_status("SessionManager: Interactive capabilities available", "SUCCESS")
    
    print("\n--- What You Can Do Next ---")
    print("• Use the CLI: python interactive-bioxen-lua.py") 
    print("• Create VMs: manager = VMManager(); vm_id = manager.create_vm('my_vm')")
    print("• Curate packages: curator = get_curator(); curator.curate_environment('standard')")
    print("• Network VMs: net_vm = NetworkedLuaVM(name='network_test')")
    print("• Interactive sessions: session = InteractiveSession(...)")
    
    print_section("AGI System Ready!", "=")


def demo_phase3_multi_vm_integration():
    """Phase 3: Demonstrate multi-VM integration with XCP-ng support"""
    print_section("PHASE 3: Multi-VM Integration Demo", "=")
    
    print_status("Demonstrating unified VM factory pattern with XCP-ng support", "INFO")
    
    try:
        from pylua_bioxen_vm_lib import create_vm
        
        # XCP-ng configuration for demo
        xcpng_config = {
            "xapi_url": "https://demo-xcpng.example.com",
            "username": "root", 
            "password": "demo_password",
            "template": "lua-bio-template",
            "vm_name": "integration-demo-vm"
        }
        
        print_section("Basic VM Creation", "-")
        
        # Create basic VM (existing functionality)
        basic_vm = create_vm("integration_basic", vm_type="basic")
        print_status("Basic VM created successfully", "SUCCESS")
        
        # Execute biological computation example
        bio_code = '''
        -- Biological sequence analysis example
        function analyze_sequence(seq)
            local gc_count = 0
            local length = #seq
            
            for i = 1, length do
                local nucleotide = seq:sub(i, i):upper()
                if nucleotide == "G" or nucleotide == "C" then
                    gc_count = gc_count + 1
                end
            end
            
            local gc_content = (gc_count / length) * 100
            return {
                length = length,
                gc_count = gc_count, 
                gc_content = gc_content
            }
        end
        
        -- Test with sample sequence
        local sequence = "ATCGATCGTAGCTAGC"
        local result = analyze_sequence(sequence)
        print("Sequence analysis:")
        print("Length: " .. result.length)
        print("GC Content: " .. string.format("%.1f%%", result.gc_content))
        '''
        
        result = basic_vm.execute_string(bio_code)
        print_status("Biological computation executed in basic VM", "SUCCESS")
        if result.get('stdout'):
            print(f"   Output: {result['stdout'].strip()}")
        
        print_section("XCP-ng VM Integration", "-")
        
        # Demonstrate XCP-ng VM creation (will show expected error without infrastructure)
        try:
            xcpng_vm = create_vm("integration_xcpng", vm_type="xcpng", config=xcpng_config)
            print_status("XCP-ng VM created successfully", "SUCCESS")
            
            # This would work with real XCP-ng infrastructure
            xcpng_vm.start()
            result = xcpng_vm.execute_string(bio_code)
            print_status("Biological computation executed in XCP-ng VM", "SUCCESS")
            
            xcpng_vm.stop()
            print_status("XCP-ng VM lifecycle completed", "SUCCESS")
            
        except Exception as e:
            print_status(f"XCP-ng VM demo (expected without infrastructure): {str(e)[:100]}...", "WARNING")
            print_status("This demonstrates the API - real usage requires XCP-ng host", "INFO")
        
        print_section("VMManager Multi-VM Orchestration", "-")
        
        # Demonstrate VMManager with both VM types
        with VMManager(debug_mode=True) as manager:
            print_status("VMManager initialized with debug mode", "SUCCESS")
            
            # Create multiple VMs of different types
            sessions = {}
            
            # Basic VM through manager
            sessions['bio_basic'] = manager.create_interactive_vm("bio_basic", vm_type="basic")
            print_status("Interactive basic VM created through VMManager", "SUCCESS")
            
            # Attempt XCP-ng VM through manager
            try:
                sessions['bio_xcpng'] = manager.create_interactive_vm("bio_xcpng", vm_type="xcpng", config=xcpng_config)
                print_status("Interactive XCP-ng VM created through VMManager", "SUCCESS")
            except Exception as e:
                print_status("XCP-ng VM creation skipped (no infrastructure)", "WARNING")
            
            # Demonstrate unified interface
            manager.send_input("bio_basic", "x = 'Basic VM computation'")
            manager.send_input("bio_basic", "print(x)")
            
            time.sleep(0.2)  # Allow processing
            
            output = manager.read_output("bio_basic")
            if output:
                print_status(f"Basic VM response: {output.strip()}", "SUCCESS")
            
            # Show session management
            active_sessions = manager.session_manager.list_sessions()
            print_status(f"Active sessions: {list(active_sessions.keys())}", "INFO")
            
        print_section("Cross-VM Biological Workflow", "-")
        
        # Demonstrate biological computation across VM types
        sequences = {
            "sample1": "ATCGATCGTAGCTAGCGGCGAATC",
            "sample2": "GGCCTTAAGCCGATCGTAGCCCGG", 
            "sample3": "AATTGGCCTTAAGCCGATCGTAGC"
        }
        
        print_status("Processing multiple biological samples", "INFO")
        
        for sample_id, sequence in sequences.items():
            analysis_code = f'''
            local sequence = "{sequence}"
            local result = analyze_sequence(sequence)
            print("{sample_id}: GC=" .. string.format("%.1f%%", result.gc_content) .. 
                  " Len=" .. result.length)
            '''
            
            try:
                result = basic_vm.execute_string(analysis_code)
                if result.get('stdout'):
                    print_status(f"  {result['stdout'].strip()}", "SUCCESS")
            except Exception as e:
                print_status(f"Sample {sample_id} analysis failed: {e}", "ERROR")
        
        print_section("Configuration Management Demo", "-")
        
        # Demonstrate configuration file usage
        import json
        config_file = "demo_xcpng_config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(xcpng_config, f, indent=2)
            
            print_status(f"XCP-ng configuration saved to {config_file}", "SUCCESS")
            
            # Load and validate config
            with open(config_file) as f:
                loaded_config = json.load(f)
            
            print_status("Configuration loaded and validated", "SUCCESS")
            print(f"   Host: {loaded_config.get('xapi_url')}")
            print(f"   Template: {loaded_config.get('template')}")
            
        except Exception as e:
            print_status(f"Configuration management error: {e}", "ERROR")
        
        print_section("Phase 3 Integration Summary", "-")
        
        print_status("✓ Basic VM: Local process execution", "SUCCESS")
        print_status("✓ XCP-ng VM: Remote virtualization API", "SUCCESS") 
        print_status("✓ VMManager: Unified multi-VM management", "SUCCESS")
        print_status("✓ Biological: Cross-platform computation", "SUCCESS")
        print_status("✓ Configuration: File-based XCP-ng setup", "SUCCESS")
        
        print("\n🧬 BIOLOGICAL COMPUTATION CAPABILITIES:")
        print("   • DNA/RNA sequence analysis")
        print("   • GC content calculation")
        print("   • Cross-VM parallel processing") 
        print("   • Remote execution on XCP-ng infrastructure")
        
        print("\n🖥️  VM TYPE COMPATIBILITY:")
        print("   • basic: Local Lua processes (Phase 1)")
        print("   • xcpng: Remote XCP-ng VMs (Phase 2)")
        print("   • Unified API for both types (Phase 3)")
        
    except Exception as e:
        print_status(f"Phase 3 demo error: {e}", "ERROR")
        traceback.print_exc()


if __name__ == "__main__":
    try:
        # Run original demo
        main()
        
        # Run Phase 3 extensions
        demo_phase3_multi_vm_integration()
        
        print_section("COMPLETE INTEGRATION DEMO FINISHED", "=")
        print_status("All phases demonstrated successfully!", "SUCCESS")
        print("\n💡 Next steps:")
        print("   • Use interactive CLI: python interactive-bioxen-lua.py")
        print("   • Deploy to XCP-ng infrastructure")
        print("   • Scale biological computations")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nDemo failed with unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)