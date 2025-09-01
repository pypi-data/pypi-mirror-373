#!/usr/bin/env python3
"""
Module Structure Diagnostic for pylua_bioxen_vm_lib
This script will determine the actual structure and available imports
"""

import sys
import os
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title.center(58)} ")
    print(f"{'='*60}\n")

def check_directory_structure():
    """Check the actual directory structure"""
    print_section("Directory Structure Analysis")
    
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Look for pylua_vm directory
    pylua_dir = current_dir / "pylua_vm"
    if pylua_dir.exists():
        print(f"✅ Found pylua_vm directory: {pylua_dir}")
        
        # List all Python files
        python_files = list(pylua_dir.glob("*.py"))
        print(f"\nPython files in pylua_vm ({len(python_files)}):")
        for py_file in python_files:
            print(f"  📄 {py_file.name}")
            
        # Check for __init__.py
        init_file = pylua_dir / "__init__.py"
        if init_file.exists():
            print(f"\n✅ __init__.py exists ({init_file.stat().st_size} bytes)")
            try:
                content = init_file.read_text()[:500]  # First 500 chars
                print(f"Init file content preview:\n{content}")
            except Exception as e:
                print(f"❌ Could not read __init__.py: {e}")
        else:
            print(f"\n❌ __init__.py missing!")
            
    else:
        print(f"❌ pylua_vm directory not found at {pylua_dir}")
        
        # Look for alternatives
        alternatives = ["pylua_bioxen_vm_lib", "bioxen_vm", "lua_vm"]
        for alt in alternatives:
            alt_path = current_dir / alt
            if alt_path.exists():
                print(f"🔍 Found alternative: {alt_path}")

def check_python_path():
    """Check Python import path"""
    print_section("Python Path Analysis")
    
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    print(f"\nPython sys.path ({len(sys.path)} entries):")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")
        
    # Check if current directory is in path
    cwd = str(Path.cwd())
    if cwd in sys.path:
        print(f"\n✅ Current directory is in Python path (index: {sys.path.index(cwd)})")
    else:
        print(f"\n⚠️ Current directory NOT in Python path")

def try_imports():
    """Try various import combinations"""
    print_section("Import Attempts")
    
    # Test basic import
    print("1. Testing basic pylua_vm import...")
    try:
        import pylua_vm
        print(f"✅ pylua_vm imported successfully")
        print(f"   Module file: {getattr(pylua_vm, '__file__', 'Unknown')}")
        print(f"   Module path: {getattr(pylua_vm, '__path__', 'Unknown')}")
        
        # Show what's in the module
        contents = [item for item in dir(pylua_vm) if not item.startswith('_')]
        print(f"   Contents: {contents}")
        
    except Exception as e:
        print(f"❌ pylua_vm import failed: {e}")
    
    # Test submodule imports
    submodules = ['curator', 'vm_manager', 'networking', 'interactive_session']
    
    for submodule in submodules:
        print(f"\n2. Testing pylua_vm.{submodule} import...")
        try:
            module = __import__(f'pylua_vm.{submodule}', fromlist=[submodule])
            print(f"✅ pylua_vm.{submodule} imported successfully")
            
            # Show available classes/functions
            contents = [item for item in dir(module) if not item.startswith('_')]
            print(f"   Available items: {contents[:10]}...")  # Show first 10
            
        except Exception as e:
            print(f"❌ pylua_vm.{submodule} import failed: {e}")

def check_specific_files():
    """Check specific files we know should exist"""
    print_section("Specific File Analysis")
    
    expected_files = [
        ("pylua_vm/__init__.py", "Package initialization"),
        ("pylua_vm/curator.py", "Curator module"),
        ("pylua_vm/vm_manager.py", "VM Manager"),
        ("pylua_vm/networking.py", "Networking"),
        ("pylua_vm/interactive_session.py", "Interactive sessions")
    ]
    
    for file_path, description in expected_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path} - {description} ({size} bytes)")
            
            # Try to read first few lines
            try:
                with open(path, 'r') as f:
                    first_lines = [f.readline().strip() for _ in range(3)]
                print(f"   First lines: {first_lines}")
            except Exception as e:
                print(f"   Could not read: {e}")
                
        else:
            print(f"❌ {file_path} - {description} (NOT FOUND)")

def suggest_fixes():
    """Suggest potential fixes based on findings"""
    print_section("Suggested Fixes")
    
    cwd = Path.cwd()
    
    # Check if we're in the right directory
    if (cwd / "setup.py").exists() and (cwd / "pylua_vm").exists():
        print("🔧 You appear to be in the project root directory")
        print("   Try: pip install -e .")
        print("   This will properly install the package for imports")
        
    # Check if __init__.py is missing
    init_file = cwd / "pylua_vm" / "__init__.py"
    if not init_file.exists():
        print("🔧 Missing pylua_vm/__init__.py file")
        print("   Create an empty __init__.py file:")
        print("   touch pylua_vm/__init__.py")
        
    # Check if we need to add to Python path
    if str(cwd) not in sys.path:
        print("🔧 Add project to Python path:")
        print("   export PYTHONPATH=$PYTHONPATH:$(pwd)")
        print("   OR add sys.path.insert(0, '.') to your script")

def main():
    """Run all diagnostics"""
    print("🔍 Module Structure Diagnostic for pylua_bioxen_vm_lib")
    
    check_directory_structure()
    check_python_path()
    check_specific_files()
    try_imports()
    suggest_fixes()
    
    print_section("Diagnostic Complete")
    print("Run the suggested fixes above, then try your imports again!")

if __name__ == "__main__":
    main()