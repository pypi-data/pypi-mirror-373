#!/usr/bin/env python3
"""
Python Import Diagnostics Script for pylua_bioxen_vm_lib
This script helps diagnose why the pylua_vm module cannot be imported.
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util
import json
from typing import Dict, List, Any, Optional


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
        "INFO": "ℹ",
        "FOUND": "🔍"
    }
    marker = markers.get(status, "•")
    print(f"{marker} {message}")


def get_current_directory_info() -> Dict[str, Any]:
    """Get information about the current directory structure"""
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    
    info = {
        "current_dir": str(current_dir),
        "parent_dir": str(parent_dir),
        "current_contents": [],
        "parent_contents": [],
        "python_packages": [],
        "setup_files": []
    }
    
    # Check current directory contents
    try:
        for item in current_dir.iterdir():
            if item.is_dir():
                info["current_contents"].append(f"📁 {item.name}/")
                # Check if it looks like a Python package
                if (item / "__init__.py").exists():
                    info["python_packages"].append(str(item))
            else:
                info["current_contents"].append(f"📄 {item.name}")
                if item.name in ["setup.py", "pyproject.toml", "setup.cfg"]:
                    info["setup_files"].append(str(item))
    except PermissionError:
        info["current_contents"] = ["Permission denied"]
    
    # Check parent directory contents
    try:
        for item in parent_dir.iterdir():
            if item.is_dir():
                info["parent_contents"].append(f"📁 {item.name}/")
                # Check if it looks like a Python package
                if (item / "__init__.py").exists():
                    info["python_packages"].append(str(item))
            else:
                info["parent_contents"].append(f"📄 {item.name}")
                if item.name in ["setup.py", "pyproject.toml", "setup.cfg"]:
                    info["setup_files"].append(str(item))
    except PermissionError:
        info["parent_contents"] = ["Permission denied"]
    
    return info


def find_python_packages(search_dir: Path, max_depth: int = 3) -> List[Dict[str, str]]:
    """Recursively find Python packages in a directory"""
    packages = []
    
    def _find_packages(current_dir: Path, current_depth: int):
        if current_depth > max_depth:
            return
        
        try:
            for item in current_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if it's a Python package
                    init_file = item / "__init__.py"
                    if init_file.exists():
                        packages.append({
                            "name": item.name,
                            "path": str(item),
                            "relative_path": str(item.relative_to(search_dir)),
                            "has_init": True,
                            "depth": current_depth
                        })
                    
                    # Continue searching subdirectories
                    _find_packages(item, current_depth + 1)
        except PermissionError:
            pass
    
    _find_packages(search_dir, 0)
    return packages


def check_python_path():
    """Check Python path and installed packages"""
    info = {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "python_path": sys.path.copy(),
        "installed_packages": []
    }
    
    # Try to get installed packages
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            info["installed_packages"] = json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        # Fallback to basic pip list
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                info["pip_list_output"] = result.stdout
        except:
            info["pip_error"] = "Could not run pip list"
    
    return info


def try_import_variations() -> Dict[str, Any]:
    """Try importing various module name variations"""
    variations = [
        "pylua_vm",
        "pylua_bioxen_vm_lib", 
        "bioxen_vm",
        "lua_vm",
        "pylua_vm_lib",
        "pylua.vm",
        "bioxen.vm"
    ]
    
    results = {}
    
    for variation in variations:
        try:
            spec = importlib.util.find_spec(variation)
            if spec is not None:
                results[variation] = {
                    "status": "FOUND",
                    "origin": spec.origin,
                    "submodule_search_locations": spec.submodule_search_locations
                }
                
                # Try to actually import it
                try:
                    module = importlib.import_module(variation)
                    results[variation]["imported"] = True
                    results[variation]["module_file"] = getattr(module, "__file__", "Unknown")
                    results[variation]["module_path"] = getattr(module, "__path__", [])
                except Exception as e:
                    results[variation]["imported"] = False
                    results[variation]["import_error"] = str(e)
            else:
                results[variation] = {"status": "NOT_FOUND"}
        except Exception as e:
            results[variation] = {"status": "ERROR", "error": str(e)}
    
    return results


def check_setup_files(directory: Path) -> Dict[str, Any]:
    """Check setup files for package information"""
    setup_info = {}
    
    # Check setup.py
    setup_py = directory / "setup.py"
    if setup_py.exists():
        setup_info["setup.py"] = {"exists": True, "size": setup_py.stat().st_size}
        try:
            content = setup_py.read_text(encoding='utf-8')[:1000]  # First 1000 chars
            setup_info["setup.py"]["preview"] = content
            
            # Look for package name
            import re
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                setup_info["setup.py"]["package_name"] = name_match.group(1)
        except Exception as e:
            setup_info["setup.py"]["error"] = str(e)
    
    # Check pyproject.toml
    pyproject = directory / "pyproject.toml"
    if pyproject.exists():
        setup_info["pyproject.toml"] = {"exists": True, "size": pyproject.stat().st_size}
        try:
            content = pyproject.read_text(encoding='utf-8')
            setup_info["pyproject.toml"]["content"] = content[:1000]  # First 1000 chars
        except Exception as e:
            setup_info["pyproject.toml"]["error"] = str(e)
    
    # Check setup.cfg
    setup_cfg = directory / "setup.cfg"
    if setup_cfg.exists():
        setup_info["setup.cfg"] = {"exists": True, "size": setup_cfg.stat().st_size}
    
    return setup_info


def suggest_solutions(diagnostics: Dict[str, Any]) -> List[str]:
    """Suggest solutions based on diagnostic results"""
    solutions = []
    
    # Check if we found any Python packages
    if diagnostics.get("python_packages"):
        solutions.append("🔧 Found Python packages in the directory. Try installing in development mode:")
        solutions.append("   cd /path/to/project && pip install -e .")
    
    # Check if setup files exist
    setup_files = diagnostics.get("setup_files", {})
    if setup_files.get("setup.py", {}).get("exists"):
        solutions.append("🔧 Found setup.py. Install the package with:")
        solutions.append("   pip install -e .")
    
    if setup_files.get("pyproject.toml", {}).get("exists"):
        solutions.append("🔧 Found pyproject.toml. Install with:")
        solutions.append("   pip install -e .")
    
    # Check for import variations that worked
    successful_imports = [name for name, result in diagnostics.get("import_attempts", {}).items() 
                         if result.get("status") == "FOUND"]
    
    if successful_imports:
        solutions.append(f"🔧 Found working import names: {', '.join(successful_imports)}")
        solutions.append("   Update your import statements to use these names.")
    
    # Check if package is already installed
    installed_packages = diagnostics.get("python_info", {}).get("installed_packages", [])
    relevant_packages = [pkg for pkg in installed_packages 
                        if any(keyword in pkg.get("name", "").lower() 
                              for keyword in ["pylua", "bioxen", "lua"])]
    
    if relevant_packages:
        solutions.append("🔧 Found potentially relevant installed packages:")
        for pkg in relevant_packages:
            solutions.append(f"   {pkg.get('name')} v{pkg.get('version')}")
    
    # Generic solutions
    solutions.extend([
        "🔧 Add project directory to Python path:",
        "   import sys; sys.path.insert(0, '/path/to/project')",
        "🔧 Check if you're in the right directory:",
        "   cd /path/to/pylua_bioxen_vm_lib",
        "🔧 Verify Python environment:",
        "   which python3 && python3 --version"
    ])
    
    return solutions


def main():
    """Main diagnostic function"""
    print_section("Python Import Diagnostics for pylua_bioxen_vm_lib")
    
    print("Diagnosing why 'from pylua_vm.env import EnvironmentManager' fails...\n")
    
    # Collect all diagnostic information
    diagnostics = {}
    
    # 1. Current directory analysis
    print_section("Step 1: Directory Structure Analysis")
    dir_info = get_current_directory_info()
    diagnostics["directory_info"] = dir_info
    
    print_status(f"Current directory: {dir_info['current_dir']}")
    print_status(f"Parent directory: {dir_info['parent_dir']}")
    
    print(f"\nCurrent directory contents ({len(dir_info['current_contents'])} items):")
    for item in dir_info['current_contents'][:10]:  # Show first 10
        print(f"  {item}")
    if len(dir_info['current_contents']) > 10:
        print(f"  ... and {len(dir_info['current_contents']) - 10} more items")
    
    if dir_info['python_packages']:
        print_status("Found Python packages:", "FOUND")
        for pkg in dir_info['python_packages']:
            print(f"  📦 {pkg}")
    else:
        print_status("No Python packages found in current or parent directory", "WARNING")
    
    # 2. Find Python packages recursively
    print_section("Step 2: Recursive Package Search")
    current_dir = Path.cwd()
    packages = find_python_packages(current_dir)
    diagnostics["found_packages"] = packages
    
    if packages:
        print_status(f"Found {len(packages)} Python packages:", "FOUND")
        for pkg in packages:
            print(f"  📦 {pkg['name']} at {pkg['relative_path']} (depth: {pkg['depth']})")
    else:
        print_status("No Python packages found recursively", "WARNING")
    
    # 3. Python environment analysis
    print_section("Step 3: Python Environment Analysis")
    python_info = check_python_path()
    diagnostics["python_info"] = python_info
    
    print_status(f"Python executable: {python_info['python_executable']}")
    print_status(f"Python version: {python_info['python_version'].split()[0]}")
    
    print(f"\nPython path ({len(python_info['python_path'])} entries):")
    for i, path in enumerate(python_info['python_path'][:5]):  # Show first 5
        print(f"  {i}: {path}")
    if len(python_info['python_path']) > 5:
        print(f"  ... and {len(python_info['python_path']) - 5} more paths")
    
    # Check for relevant installed packages
    if python_info.get("installed_packages"):
        relevant = [pkg for pkg in python_info["installed_packages"] 
                   if any(keyword in pkg.get("name", "").lower() 
                         for keyword in ["pylua", "bioxen", "lua", "vm"])]
        if relevant:
            print_status(f"Found {len(relevant)} potentially relevant packages:", "FOUND")
            for pkg in relevant:
                print(f"  📦 {pkg.get('name')} v{pkg.get('version', 'unknown')}")
    
    # 4. Import attempts
    print_section("Step 4: Import Attempts")
    import_results = try_import_variations()
    diagnostics["import_attempts"] = import_results
    
    successful = []
    failed = []
    
    for module_name, result in import_results.items():
        if result["status"] == "FOUND":
            successful.append((module_name, result))
            print_status(f"✅ {module_name} - FOUND at {result.get('origin', 'unknown')}", "SUCCESS")
        else:
            failed.append((module_name, result))
            print_status(f"❌ {module_name} - {result['status']}")
    
    if successful:
        print_status(f"\n🎉 Found {len(successful)} working imports!", "SUCCESS")
        for name, result in successful:
            if result.get("imported"):
                print(f"  ✅ {name} imports successfully")
                if result.get("module_path"):
                    print(f"     Subpackages: {result['module_path']}")
            else:
                print(f"  ⚠️ {name} found but import failed: {result.get('import_error', 'Unknown')}")
    
    # 5. Setup file analysis
    print_section("Step 5: Setup File Analysis")
    setup_info = check_setup_files(current_dir)
    diagnostics["setup_files"] = setup_info
    
    if setup_info:
        for filename, info in setup_info.items():
            if info.get("exists"):
                print_status(f"Found {filename} ({info['size']} bytes)", "FOUND")
                
                if "package_name" in info:
                    print(f"  Package name: {info['package_name']}")
                
                if "preview" in info and len(info["preview"]) > 50:
                    print(f"  Preview: {info['preview'][:100]}...")
            else:
                print_status(f"{filename} not found")
    else:
        print_status("No setup files found", "WARNING")
    
    # 6. Generate solutions
    print_section("Step 6: Recommended Solutions")
    solutions = suggest_solutions(diagnostics)
    
    if solutions:
        for solution in solutions:
            print(solution)
    else:
        print_status("No specific solutions identified. Check the analysis above.", "WARNING")
    
    # 7. Summary
    print_section("Diagnostic Summary")
    
    print("📊 Analysis Results:")
    print(f"  • Python packages found: {len(diagnostics.get('found_packages', []))}")
    print(f"  • Working imports: {len([r for r in import_results.values() if r.get('status') == 'FOUND'])}")
    print(f"  • Setup files: {len([f for f, info in setup_info.items() if info.get('exists')])}")
    
    if successful:
        print_status(f"\n🎯 Quick fix: Try importing '{successful[0][0]}' instead of 'pylua_vm'", "SUCCESS")
    elif packages:
        print_status(f"\n🎯 Quick fix: Run 'pip install -e .' in the project directory", "SUCCESS")
    else:
        print_status(f"\n🔍 No obvious quick fix found. Review the analysis above.", "WARNING")
    
    return diagnostics


if __name__ == "__main__":
    try:
        result = main()
        print(f"\n✅ Diagnostic complete. Run with --json flag to output raw data.")
        
        # Offer to save diagnostics
        save = input("\nSave diagnostic results to file? (y/N): ").lower().strip()
        if save in ['y', 'yes']:
            output_file = Path("import_diagnostics.json")
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📁 Diagnostics saved to {output_file}")
            
    except KeyboardInterrupt:
        print("\n\n⛔ Diagnostic interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)