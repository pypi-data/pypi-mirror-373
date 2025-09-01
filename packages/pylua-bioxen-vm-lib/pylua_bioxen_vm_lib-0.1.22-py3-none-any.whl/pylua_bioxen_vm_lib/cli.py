"""
PyLua VM Curator CLI
Provides interactive and command-line tools for environment setup, package management, and diagnostics.
Embodies the curator philosophy of intelligent, discerning package management.

Updated to work with external package and profile catalogs from pkgdict folder.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import subprocess

# Import external catalogs from the consuming application
try:
    from pkgdict.bioxen_packages import ALL_PACKAGES
    from pkgdict.bioxen_profiles import ALL_PROFILES
    CATALOGS_AVAILABLE = True
except ImportError:
    print("Warning: External package catalogs not found. Using empty catalogs.")
    ALL_PACKAGES = {}
    ALL_PROFILES = {}
    CATALOGS_AVAILABLE = False

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

from pylua_bioxen_vm_lib.utils.curator import Curator, get_curator, bootstrap_lua_environment, quick_install


def setup_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Lua Package Curator - Intelligent package management for Lua environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s health                          # Check system health
  %(prog)s list                            # List installed packages  
  %(prog)s install lua-cjson               # Install specific package
  %(prog)s install --profile standard      # Install profile
  %(prog)s bootstrap --profile full        # Bootstrap complete environment
  %(prog)s profiles                        # List available profiles
  %(prog)s recommendations                 # Get package recommendations
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check system health')
    health_parser.add_argument('--verbose', '-v', action='store_true', 
                              help='Show detailed health information')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List installed packages')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--priority', type=int, help='Filter by minimum priority')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install packages')
    install_group = install_parser.add_mutually_exclusive_group(required=True)
    install_group.add_argument('packages', nargs='*', help='Package names to install')
    install_group.add_argument('--profile', help='Profile to install')
    install_parser.add_argument('--force', action='store_true', help='Force reinstallation')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove packages')
    remove_parser.add_argument('packages', nargs='+', help='Package names to remove')
    
    # Bootstrap command
    bootstrap_parser = subparsers.add_parser('bootstrap', help='Bootstrap Lua environment')
    bootstrap_parser.add_argument('--profile', default='standard', 
                                 help='Profile to bootstrap (default: standard)')
    
    # Profiles command
    profiles_parser = subparsers.add_parser('profiles', help='List available profiles')
    profiles_parser.add_argument('--detail', action='store_true', 
                                help='Show packages in each profile')
    
    # Recommendations command
    recommendations_parser = subparsers.add_parser('recommendations', 
                                                  help='Get package recommendations')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up orphaned packages')
    cleanup_parser.add_argument('--dry-run', action='store_true', 
                               help='Show what would be cleaned up without doing it')
    
    # Global options
    parser.add_argument('--lua-path', help='Path to Lua executable')
    parser.add_argument('--manifest', help='Path to manifest file')
    parser.add_argument('--no-catalogs', action='store_true',
                       help='Run without external package/profile catalogs')
    
    return parser


def get_curator_with_catalogs(args) -> Curator:
    """Create curator instance with appropriate catalogs based on args"""
    if args.no_catalogs or not CATALOGS_AVAILABLE:
        return get_curator(lua_path=args.lua_path, manifest_path=args.manifest)
    else:
        return get_curator(
            lua_path=args.lua_path, 
            manifest_path=args.manifest,
            packages_catalog=ALL_PACKAGES,
            profiles_catalog=ALL_PROFILES
        )


def cmd_health(args) -> int:
    """Handle health check command"""
    curator = get_curator_with_catalogs(args)
    health = curator.health_check()
    
    print("=== System Health Check ===")
    
    # Basic health info
    status_items = [
        ("LuaRocks Available", "✓" if health["luarocks_available"] else "✗"),
        ("Lua Version", health["lua_version"]),
        ("Installed Packages", health["installed_packages"]),
        ("Manifest Valid", "✓" if health["manifest_valid"] else "✗"),
        ("Package Catalog Size", health["catalog_size"]),
        ("Available Profiles", health["available_profiles"]),
        ("Critical Packages", health.get("critical_packages_ratio", "N/A")),
    ]
    
    for label, value in status_items:
        print(f"{label:20}: {value}")
    
    if args.verbose:
        print(f"\nTimestamp: {health['timestamp']}")
        if not CATALOGS_AVAILABLE:
            print("Warning: Running without external catalogs")
    
    # Return exit code based on health
    if not health["luarocks_available"]:
        return 1
    
    return 0


def cmd_list(args) -> int:
    """Handle list packages command"""
    curator = get_curator_with_catalogs(args)
    installed = curator.list_installed_packages()
    
    if not installed:
        print("No packages installed.")
        return 0
    
    # Apply filters
    if args.category:
        installed = [pkg for pkg in installed if pkg.get("category") == args.category]
    
    if args.priority:
        installed = [pkg for pkg in installed if pkg.get("priority", 0) >= args.priority]
    
    print(f"=== Installed Packages ({len(installed)}) ===")
    for pkg in installed:
        priority_str = f" (priority: {pkg.get('priority', 'N/A