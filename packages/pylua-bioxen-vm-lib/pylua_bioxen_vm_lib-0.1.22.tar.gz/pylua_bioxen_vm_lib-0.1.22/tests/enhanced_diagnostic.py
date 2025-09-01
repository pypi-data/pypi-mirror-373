#!/usr/bin/env python3
"""
Enhanced Module Structure Diagnostic for pylua_bioxen_vm_lib
This script will determine the actual structure and available imports,
plus check for specific requirements of the pylua_bioxen_vm_lib project.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title.center(58)} ")
    print(f"{'='*60}\n")

def check_system_requirements():
    """Check system requirements for pylua_bioxen_vm_lib"""
    print_section("System Requirements Check")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version >= (3, 7):
        print("✅ Python 3.7+ requirement met")
    else:
        print("❌ Python 3.7+ required")
    
    # Check for Lua interpreter
    lua_path = shutil.which("lua")
    if lua_path:
        print(f"✅ Lua interpreter found: {lua_path}")
        try:
            result = subprocess.run(["lua", "-v"], capture_output=True, text=True, timeout=5)
            print(f"   Version info: {result.stderr.strip() or result.stdout.strip()}")
        except Exception as e:
            print(f"   Could not get Lua version: {e}")
    else:
        print("❌ Lua interpreter not found in PATH")
        print("   Install Lua: https://www.lua.org/download.html")
    
    # Check for LuaSocket (luarocks install luasocket)
    print("\n🔍 Checking for LuaSocket...")
    try:
        result = subprocess.run(
            ["lua", "-e", "require('socket'); print('LuaSocket available')"], 
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("✅ LuaSocket library available")
        else:
            print("❌ LuaSocket library not found")
            print("   Install with: luarocks install luasocket")
    except Exception as e:
        print(f"   Could not check LuaSocket: {e}")
    
    # Check for luarocks
    luarocks_path = shutil.which("luarocks")
    if luarocks_path:
        print(f"✅ LuaRocks found: {luarocks_path}")
    else:
        print("⚠️ LuaRocks not found (needed for installing LuaSocket)")

def check_directory_structure():
    """Check the actual directory structure"""
    print_section("Directory Structure Analysis")
    
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Look for the package directory
    package_dirs = ["pylua_bioxen_vm_lib", "pylua_vm", "src/pylua_bioxen_vm_lib"]
    found_package = None
    
    for pkg_dir in package_dirs:
        pkg_path = current_dir / pkg_dir
        if pkg_path.exists():
            found_package = pkg_path
            print(f"✅ Found package directory: {pkg_path}")
            break
    
    if not found_package:
        print(f"❌ No package directory found. Looking for: {package_dirs}")
        return None
        
    # List all Python files
    python_files = list(found_package.glob("*.py"))
    print(f"\nPython files in {found_package.name} ({len(python_files)}):")
    for py_file in python_files:
        size = py_file.stat().st_size
        print(f"  📄 {py_file.name} ({size} bytes)")
        
    # Check for __init__.py
    init_file = found_package / "__init__.py"
    if init_file.exists():
        print(f"\n✅ __init__.py exists ({init_file.stat().st_size} bytes)")
        try:
            content = init_file.read_text()[:500]  # First 500 chars
            print(f"Init file content preview:\n{content}")
        except Exception as e:
            print(f"❌ Could not read __init__.py: {e}")
    else:
        print(f"\n❌ __init__.py missing!")
    
    # Check for specific expected files based on repository
    expected_files = [
        "vm_manager.py", "curator.py", "networking.py", "interactive_session.py"
    ]
    
    print(f"\nExpected module files:")
    for expected in expected_files:
        expected_path = found_package / expected
        if expected_path.exists():
            size = expected_path.stat().st_size
            print(f"  ✅ {expected} ({size} bytes)")
        else:
            print(f"  ❌ {expected} (missing)")
    
    return found_package

def check_python_path():
    """Check Python import path"""
    print_section("Python Path Analysis")
    
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    print(f"\nPython sys.path ({len(sys.path)} entries):")
    for i, path in enumerate(sys.path):
        marker = " 🎯" if str(Path.cwd()) in path else ""
        print(f"  {i}: {path}{marker}")
        
    # Check if current directory is in path
    cwd = str(Path.cwd())
    if cwd in sys.path:
        print(f"\n✅ Current directory is in Python path (index: {sys.path.index(cwd)})")
    else:
        print(f"\n⚠️ Current directory NOT in Python path")

def try_imports():
    """Try various import combinations"""
    print_section("Import Attempts")
    
    # Test different package names
    package_names = ["pylua_bioxen_vm_lib", "pylua_vm"]
    
    for pkg_name in package_names:
        print(f"1. Testing {pkg_name} import...")
        try:
            module = __import__(pkg_name)
            print(f"✅ {pkg_name} imported successfully")
            print(f"   Module file: {getattr(module, '__file__', 'Unknown')}")
            print(f"   Module path: {getattr(module, '__path__', 'Unknown')}")
            
            # Show what's in the module
            contents = [item for item in dir(module) if not item.startswith('_')]
            print(f"   Contents: {contents}")
            
            # Try to import main classes
            main_classes = ['VMManager', 'InteractiveSession']
            for cls_name in main_classes:
                try:
                    cls = getattr(module, cls_name, None)
                    if cls:
                        print(f"   ✅ {cls_name} class available")
                    else:
                        print(f"   ⚠️ {cls_name} class not found in module")
                except Exception as e:
                    print(f"   ❌ Error accessing {cls_name}: {e}")
            
            break  # If successful, don't try other package names
            
        except Exception as e:
            print(f"❌ {pkg_name} import failed: {e}")
    
    # Test submodule imports
    submodules = ['vm_manager', 'curator', 'networking', 'interactive_session']
    
    for submodule in submodules:
        print(f"\n2. Testing {pkg_name}.{submodule} import...")
        try:
            module = __import__(f'{pkg_name}.{submodule}', fromlist=[submodule])
            print(f"✅ {pkg_name}.{submodule} imported successfully")
            
            # Show available classes/functions
            contents = [item for item in dir(module) if not item.startswith('_')]
            print(f"   Available items: {contents[:10]}...")  # Show first 10
            
        except Exception as e:
            print(f"❌ {pkg_name}.{submodule} import failed: {e}")

def check_installation_status():
    """Check if the package is properly installed"""
    print_section("Installation Status Check")
    
    # Check if package is pip installed
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True)
        if "pylua-bioxen-vm" in result.stdout or "pylua_bioxen_vm_lib" in result.stdout:
            print("✅ Package appears to be pip installed")
            
            # Get specific info
            info_result = subprocess.run([sys.executable, "-m", "pip", "show", "pylua-bioxen-vm"], 
                                       capture_output=True, text=True)
            if info_result.returncode == 0:
                print("Package info:")
                print(info_result.stdout)
        else:
            print("❌ Package not found in pip list")
            
    except Exception as e:
        print(f"❌ Could not check pip status: {e}")
    
    # Check for setup.py or pyproject.toml
    setup_py = Path("setup.py")
    pyproject_toml = Path("pyproject.toml")
    
    if setup_py.exists():
        print(f"✅ setup.py found ({setup_py.stat().st_size} bytes)")
    elif pyproject_toml.exists():
        print(f"✅ pyproject.toml found ({pyproject_toml.stat().st_size} bytes)")
    else:
        print("❌ No setup.py or pyproject.toml found")

def suggest_fixes():
    """Suggest potential fixes based on findings"""
    print_section("Suggested Fixes")
    
    cwd = Path.cwd()
    
    # Check if we're in the right directory
    has_setup = (cwd / "setup.py").exists() or (cwd / "pyproject.toml").exists()
    has_package = any((cwd / pkg).exists() for pkg in ["pylua_bioxen_vm_lib", "pylua_vm"])
    
    if has_setup and has_package:
        print("🔧 You appear to be in the project root directory")
        print("   Option 1: Install in development mode:")
        print("     pip install -e .")
        print("   Option 2: Install from PyPI:")
        print("     pip install pylua-bioxen-vm-lib")
        
    # Check if __init__.py is missing
    for pkg_dir in ["pylua_bioxen_vm_lib", "pylua_vm"]:
        pkg_path = cwd / pkg_dir
        if pkg_path.exists():
            init_file = pkg_path / "__init__.py"
            if not init_file.exists():
                print(f"🔧 Missing {pkg_dir}/__init__.py file")
                print(f"   Create an empty __init__.py file:")
                print(f"     touch {pkg_dir}/__init__.py")
    
    # Check if we need to add to Python path
    if str(cwd) not in sys.path:
        print("🔧 Add project to Python path:")
        print("   export PYTHONPATH=$PYTHONPATH:$(pwd)")
        print("   OR add sys.path.insert(0, '.') to your script")
    
    # System requirements
    if not shutil.which("lua"):
        print("🔧 Install Lua interpreter:")
        print("   Ubuntu/Debian: sudo apt-get install lua5.3")
        print("   macOS: brew install lua")
        print("   Windows: Download from https://www.lua.org/download.html")
    
    if shutil.which("lua") and not shutil.which("luarocks"):
        print("🔧 Install LuaRocks:")
        print("   Ubuntu/Debian: sudo apt-get install luarocks")
        print("   macOS: brew install luarocks")
        print("   Then install LuaSocket: luarocks install luasocket")

def run_basic_functionality_test():
    """Try to run a basic functionality test if possible"""
    print_section("Basic Functionality Test")
    
    try:
        # Try to import and create a basic VM manager
        import pylua_bioxen_vm_lib
        from pylua_bioxen_vm_lib import VMManager
        
        print("✅ Successfully imported pylua_bioxen_vm_lib and VMManager")
        
        # Try to create a VM manager (but don't actually create VMs)
        print("🔬 Testing VMManager instantiation...")
        manager = VMManager()
        print("✅ VMManager created successfully")
        
        # Check available methods
        methods = [m for m in dir(manager) if not m.startswith('_') and callable(getattr(manager, m))]
        print(f"   Available methods: {methods}")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")

def main():
    """Run all diagnostics"""
    print("🔍 Enhanced Module Structure Diagnostic for pylua_bioxen_vm_lib")
    print("   Repository: https://github.com/aptitudetechnology/pylua_bioxen_vm_lib")
    
    check_system_requirements()
    check_directory_structure()
    check_python_path()
    check_installation_status()
    try_imports()
    run_basic_functionality_test()
    suggest_fixes()
    
    print_section("Diagnostic Complete")
    print("Follow the suggested fixes above, then try your imports again!")
    print("\nFor more help, check:")
    print("- Repository README: https://github.com/aptitudetechnology/pylua_bioxen_vm_lib")
    print("- PyPI package: pip install pylua-bioxen-vm-lib")

if __name__ == "__main__":
    main()