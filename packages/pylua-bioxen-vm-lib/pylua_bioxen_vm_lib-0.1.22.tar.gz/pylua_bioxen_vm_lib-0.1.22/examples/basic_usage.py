"""
Basic usage example for PyLua VM Curator system.
Demonstrates the Phase 3 multi-VM support with basic and XCP-ng VMs.
Phase 3: Complete CLI integration and unified VM management.
"""
import json
import time
from pylua_bioxen_vm_lib import create_vm, VMManager

print("🧬 PyLua BioXen VM Library - Basic Usage Examples")
print("=" * 60)

# Phase 3: Core VM Factory Pattern Examples
print("\n1. Basic VM Creation and Execution")
print("-" * 40)

try:
    # Create a basic VM (local process)
    basic_vm = create_vm("demo_basic", vm_type="basic")
    print("✅ Basic VM created successfully")
    
    # Execute simple Lua code
    result = basic_vm.execute_string('print("Hello from Basic VM!")')
    print("✅ Execution result:", result.get('stdout', '').strip())
    
    # Execute biological computation example
    bio_code = '''
    function calculate_gc_content(sequence)
        local gc_count = 0
        local total = #sequence
        
        for i = 1, total do
            local nucleotide = sequence:sub(i, i):upper()
            if nucleotide == "G" or nucleotide == "C" then
                gc_count = gc_count + 1
            end
        end
        
        return (gc_count / total) * 100
    end
    
    -- Test with sample DNA sequence
    local dna = "ATCGATCGTAGCTAGCGGCGAATC"
    local gc_percentage = calculate_gc_content(dna)
    print("DNA Sequence: " .. dna)
    print("GC Content: " .. string.format("%.1f%%", gc_percentage))
    '''
    
    result = basic_vm.execute_string(bio_code)
    print("✅ Biological computation result:")
    if result.get('stdout'):
        print("   " + result['stdout'].strip().replace('\n', '\n   '))
    
except Exception as e:
    print(f"❌ Basic VM error: {e}")

print("\n2. XCP-ng VM Creation (API Demonstration)")
print("-" * 50)

# XCP-ng VM configuration example
xcpng_config = {
    "xapi_url": "https://demo-xcpng.example.com",
    "username": "root",
    "password": "demo_password",
    "template": "lua-bio-template",
    "vm_name": "demo-lua-vm",
    "memory": "2GB",
    "vcpus": 2,
    "verify_ssl": False
}

try:
    # Note: This will show expected error without actual XCP-ng infrastructure
    xcpng_vm = create_vm("demo_xcpng", vm_type="xcpng", config=xcpng_config)
    print("✅ XCP-ng VM object created successfully")
    
    # This would work with real XCP-ng infrastructure
    # xcpng_vm.start()
    # result = xcpng_vm.execute_string(bio_code)
    # xcpng_vm.stop()
    
except Exception as e:
    print(f"❌ XCP-ng VM demo (expected without infrastructure): {str(e)[:80]}...")
    print("💡 This demonstrates the API - real usage requires XCP-ng host")

print("\n3. VMManager Multi-VM Orchestration")
print("-" * 40)

try:
    with VMManager(debug_mode=False) as manager:
        print("✅ VMManager initialized")
        
        # Create basic VM through manager
        basic_session = manager.create_interactive_vm("managed_basic", vm_type="basic")
        print("✅ Interactive basic VM created through VMManager")
        
        # Send commands to VM
        manager.send_input("managed_basic", "vm_name = 'Managed Basic VM'")
        manager.send_input("managed_basic", "print('Running in:', vm_name)")
        
        # Read output
        time.sleep(0.2)  # Allow processing
        output = manager.read_output("managed_basic")
        if output:
            print("✅ VM response:", output.strip().split('\n')[-2] if '\n' in output else output.strip())
        
        # List active sessions
        sessions = manager.session_manager.list_sessions()
        print(f"✅ Active sessions: {list(sessions.keys())}")
        
        # Try XCP-ng VM through manager (will show expected error)
        try:
            xcpng_session = manager.create_interactive_vm("managed_xcpng", vm_type="xcpng", config=xcpng_config)
            print("✅ XCP-ng VM session created through VMManager")
        except Exception as e:
            print(f"❌ XCP-ng VM creation (expected): {str(e)[:60]}...")
        
except Exception as e:
    print(f"❌ VMManager error: {e}")

print("\n4. Configuration File Management")
print("-" * 35)

try:
    # Create example configuration file
    config_file = "demo_xcpng_config.json"
    with open(config_file, 'w') as f:
        json.dump(xcpng_config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_file}")
    
    # Load and validate config
    with open(config_file) as f:
        loaded_config = json.load(f)
    
    print("✅ Configuration loaded and validated:")
    print(f"   Host: {loaded_config.get('xapi_url')}")
    print(f"   Template: {loaded_config.get('template')}")
    print(f"   Memory: {loaded_config.get('memory')}")
    print(f"   vCPUs: {loaded_config.get('vcpus')}")
    
except Exception as e:
    print(f"❌ Configuration management error: {e}")

print("\n5. Biological Sequence Analysis Workflow")
print("-" * 45)

# Multiple DNA sequences for analysis
sequences = {
    "sample_1": "ATCGATCGTAGCTAGCGGCGAATC",
    "sample_2": "GGCCTTAAGCCGATCGTAGCCCGG", 
    "sample_3": "AATTGGCCTTAAGCCGATCGTAGC",
    "sample_4": "CCGGAATTCCGGAATTCCGGAATT"
}

try:
    # Analyze sequences using basic VM
    analysis_vm = create_vm("sequence_analyzer", vm_type="basic")
    
    # Define analysis function
    analysis_function = '''
    function analyze_dna_sequence(sequence, name)
        local length = #sequence
        local gc_count = 0
        local at_count = 0
        
        for i = 1, length do
            local nucleotide = sequence:sub(i, i):upper()
            if nucleotide == "G" or nucleotide == "C" then
                gc_count = gc_count + 1
            elseif nucleotide == "A" or nucleotide == "T" then
                at_count = at_count + 1
            end
        end
        
        local gc_content = (gc_count / length) * 100
        local at_content = (at_count / length) * 100
        
        print(string.format("%s: Len=%d, GC=%.1f%%, AT=%.1f%%", 
              name, length, gc_content, at_content))
    end
    '''
    
    analysis_vm.execute_string(analysis_function)
    print("✅ DNA analysis function loaded")
    
    # Analyze each sequence
    for sample_name, sequence in sequences.items():
        analysis_code = f'''analyze_dna_sequence("{sequence}", "{sample_name}")'''
        result = analysis_vm.execute_string(analysis_code)
        if result.get('stdout'):
            print(f"   {result['stdout'].strip()}")
    
except Exception as e:
    print(f"❌ Biological analysis error: {e}")

print("\n" + "=" * 60)
print("🎉 Phase 3 Basic Usage Examples Complete!")
print("=" * 60)
print("✅ Basic VM: Local Lua process execution")
print("✅ XCP-ng VM: Remote VM API demonstration") 
print("✅ VMManager: Multi-VM session management")
print("✅ Configuration: File-based setup management")
print("✅ Biological: DNA sequence analysis workflows")
print("\n💡 Next steps:")
print("   • Use interactive CLI: python interactive-bioxen-lua.py")
print("   • Set up XCP-ng infrastructure for remote VMs")
print("   • Scale biological computations across multiple VMs")
print("   • Explore advanced multi-VM orchestration patterns")
