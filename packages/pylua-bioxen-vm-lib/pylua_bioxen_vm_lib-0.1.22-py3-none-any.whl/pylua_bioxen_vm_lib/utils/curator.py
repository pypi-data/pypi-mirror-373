"""
curator.py - Intelligent Package Management System for AGI Bootstrapping

A curator embodies the intelligence needed for AGI development:
- Discernment: Carefully selects which packages/knowledge to include
- Context awareness: Understands how different components work together  
- Quality control: Ensures only valuable, reliable additions make it in
- Long-term vision: Builds collections that grow more valuable over time
- Adaptive expertise: Learns what works and refines the selection process
"""

import os
import sys
import json
import subprocess
import shutil
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class Package:
    """Represents a curated package with metadata"""
    name: str
    version: str = "latest"
    category: str = "utility"
    description: str = ""
    dependencies: List[str] = None
    installed: bool = False
    install_date: Optional[datetime] = None
    source: str = "luarocks"  # luarocks, git, local
    priority: int = 5  # 1-10, higher = more important
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class Curator:
    """Intelligent package management system for Lua environment"""

    def __init__(self, lua_path: str = None, manifest_path: str = None,
                 packages_catalog: Dict[str, Package] = None, 
                 profiles_catalog: Dict[str, Dict] = None):
        """Initialize the curator with environment configuration and external catalogs
        
        Args:
            lua_path: Path to Lua executable
            manifest_path: Path to manifest file
            packages_catalog: External package definitions (defaults to empty dict)
            profiles_catalog: External profile definitions (defaults to empty dict)
        """
        # Set up logging FIRST
        self.logger = self._setup_logging()

        # Set up catalogs from external sources or use empty defaults
        self.catalog = packages_catalog or {}
        self.profiles_catalog = profiles_catalog or {}

        # NOW we can call methods that use the logger and catalog
        self.lua_path = lua_path or self._detect_lua_path()
        self.manifest_path = Path(manifest_path) if manifest_path else Path("manifest.json")

        # Load or create manifest (this needs self.catalog to exist)
        self.manifest = self._load_manifest()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup intelligent logging system"""
        logger = logging.getLogger("curator")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        log_file = log_dir / f"curator_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _detect_lua_path(self) -> str:
        """Intelligently detect Lua installation path"""
        common_paths = [
            "/usr/local/bin/lua",
            "/usr/bin/lua",
            "/opt/lua/bin/lua",
            shutil.which("lua"),
            shutil.which("lua5.4"),
            shutil.which("lua5.3"),
        ]
        
        for path in common_paths:
            if path and Path(path).exists():
                self.logger.info(f"Detected Lua at: {path}")
                return str(path)
        
        self.logger.warning("Lua not found in common locations")
        return "lua"  # Fallback to PATH
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load or create package manifest using external profiles"""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    manifest = json.load(f)
                self.logger.info(f"Loaded manifest: {len(manifest.get('packages', {}))} packages")
                return manifest
            except Exception as e:
                self.logger.error(f"Failed to load manifest: {e}")
        
        # Create new manifest using external profiles or empty defaults
        manifest = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "lua_version": self._get_lua_version(),
            "packages": {},
            "profiles": dict(self.profiles_catalog)  # Use external profiles
        }
        
        self._save_manifest(manifest)
        return manifest
    
    def _save_manifest(self, manifest: Dict[str, Any] = None):
        """Save manifest to disk"""
        manifest = manifest or self.manifest
        manifest["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2, default=str)
            self.logger.debug("Manifest saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save manifest: {e}")
    
    def _get_lua_version(self) -> str:
        """Get Lua version for compatibility checking"""
        try:
            result = subprocess.run([self.lua_path, "-v"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.strip() or result.stderr.strip()
                # Extract version number (e.g., "Lua 5.4.4" -> "5.4.4")
                match = re.search(r'Lua (\d+\.\d+(?:\.\d+)?)', version_line)
                if match:
                    return match.group(1)
            return "unknown"
        except Exception as e:
            self.logger.warning(f"Could not determine Lua version: {e}")
            return "unknown"
    
    def _check_luarocks(self) -> bool:
        """Check if LuaRocks is available and working"""
        try:
            result = subprocess.run(["luarocks", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.debug("LuaRocks is available")
                return True
        except Exception as e:
            self.logger.warning(f"LuaRocks check failed: {e}")
        
        return False
    
    def _parse_version_constraint(self, constraint: str) -> Tuple[str, str]:
        """Parse semantic version constraints"""
        if constraint in ["latest", ""]:
            return ">=", "0.0.0"
        
        # Parse constraints like ">=1.0.0", "~>2.1", "=1.2.3"
        patterns = [
            (r'^>=(.+)$', '>='),
            (r'^>(.+)$', '>'),
            (r'^<=(.+)$', '<='),
            (r'^<(.+)$', '<'),
            (r'^=(.+)$', '='),
            (r'^~>(.+)$', '~>'),  # Compatible version
            (r'^(.+)$', '='),     # Default to exact match
        ]
        
        for pattern, op in patterns:
            match = re.match(pattern, constraint.strip())
            if match:
                return op, match.group(1)
        
        return "=", constraint
    
    def is_package_installed(self, package_name: str, version: str = None) -> bool:
        """Check if a package is installed with optional version check"""
        try:
            result = subprocess.run(["luarocks", "show", package_name], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                if version and version != "latest":
                    # Check version in output
                    version_match = re.search(rf'{package_name}\s+(\d+\.\d+(?:\.\d+)?)', result.stdout)
                    if version_match:
                        installed_version = version_match.group(1)
                        op, target_version = self._parse_version_constraint(version)
                        # Simplified version comparison (would need proper semver library for production)
                        return self._compare_versions(installed_version, op, target_version)
                return True
                
        except Exception as e:
            self.logger.debug(f"Error checking package {package_name}: {e}")
        
        return False
    
    def _compare_versions(self, installed: str, op: str, target: str) -> bool:
        """Simple version comparison (simplified for demo)"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        
        try:
            installed_tuple = version_tuple(installed)
            target_tuple = version_tuple(target)
            
            if op == '>=':
                return installed_tuple >= target_tuple
            elif op == '>':
                return installed_tuple > target_tuple
            elif op == '<=':
                return installed_tuple <= target_tuple
            elif op == '<':
                return installed_tuple < target_tuple
            elif op == '=':
                return installed_tuple == target_tuple
            elif op == '~>':
                # Compatible version (same major.minor, newer patch)
                return (installed_tuple[:2] == target_tuple[:2] and 
                       installed_tuple >= target_tuple)
        except Exception:
            pass
        
        return False
    
    def install_package(self, package_name: str, version: str = "latest", 
                       force: bool = False) -> bool:
        """Intelligently install a package with dependency resolution"""
        
        if not self._check_luarocks():
            self.logger.error("LuaRocks is not available")
            return False
        
        # Get package info from catalog or create minimal package info
        package = self.catalog.get(package_name)
        if not package:
            package = Package(package_name, version)
            self.logger.info(f"Installing uncatalogued package: {package_name}")
        
        # Check if already installed
        if not force and self.is_package_installed(package_name, version):
            self.logger.info(f"Package {package_name} already installed")
            self._update_manifest_package(package_name, package, installed=True)
            return True
        
        # Install dependencies first
        for dep in package.dependencies:
            if not self.install_package(dep):
                self.logger.error(f"Failed to install dependency: {dep}")
                return False
        
        # Install main package
        self.logger.info(f"Installing {package_name} v{version}...")
        
        try:
            cmd = ["luarocks", "install", "--local", package_name]
            if version != "latest":
                cmd.append(version)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.logger.info(f"Successfully installed {package_name}")
                package.installed = True
                package.install_date = datetime.now()
                self._update_manifest_package(package_name, package, installed=True)
                return True
            else:
                self.logger.error(f"Installation failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Installation error: {e}")
            return False
    
    def remove_package(self, package_name: str) -> bool:
        """Remove a package and clean up"""
        if not self._check_luarocks():
            self.logger.error("LuaRocks is not available")
            return False
        
        if not self.is_package_installed(package_name):
            self.logger.info(f"Package {package_name} is not installed")
            return True
        
        self.logger.info(f"Removing {package_name}...")
        
        try:
            result = subprocess.run(["luarocks", "remove", "--local", package_name], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.logger.info(f"Successfully removed {package_name}")
                self._update_manifest_package(package_name, installed=False)
                return True
            else:
                self.logger.error(f"Removal failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Removal error: {e}")
            return False
    def get_lua_env(self) -> dict:
        """Return environment variables for Lua VM to find local packages"""
        home = os.path.expanduser('~')
        lua_env = {
            "LUA_PATH": f"{home}/.luarocks/share/lua/5.1/?.lua;{home}/.luarocks/share/lua/5.1/?/init.lua;{os.environ.get('LUA_PATH', '')}",
            "LUA_CPATH": f"{home}/.luarocks/lib/lua/5.1/?.so;{os.environ.get('LUA_CPATH', '')}"
        }
        return lua_env

    def verify_local_package_installation(self, package_name: str) -> bool:
        """Verify a package is installed locally and accessible"""
        local_rocks_path = os.path.expanduser("~/.luarocks/lib/luarocks/rocks-5.1")
        package_exists = os.path.isdir(os.path.join(local_rocks_path, package_name))
        # Optionally, test Lua import capability here
        return package_exists
    
    def list_installed_packages(self) -> List[Dict[str, Any]]:
        """List all installed packages with metadata"""
        installed = []
        
        try:
            result = subprocess.run(["luarocks", "list"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Parse luarocks list output
                    match = re.match(r'^(\S+)\s+(\S+)', line.strip())
                    if match:
                        name, version = match.groups()
                        package_info = {
                            "name": name,
                            "version": version,
                            "category": "unknown",
                            "installed": True
                        }
                        
                        # Add catalog info if available
                        if name in self.catalog:
                            catalog_pkg = self.catalog[name]
                            package_info.update({
                                "category": catalog_pkg.category,
                                "description": catalog_pkg.description,
                                "priority": catalog_pkg.priority
                            })
                        
                        installed.append(package_info)
        
        except Exception as e:
            self.logger.error(f"Failed to list packages: {e}")
        
        return installed
    
    def _update_manifest_package(self, package_name: str, package: Package = None, 
                                installed: bool = True):
        """Update package info in manifest"""
        if "packages" not in self.manifest:
            self.manifest["packages"] = {}
        
        if package:
            self.manifest["packages"][package_name] = asdict(package)
        elif package_name in self.manifest["packages"]:
            self.manifest["packages"][package_name]["installed"] = installed
            if not installed:
                self.manifest["packages"][package_name]["install_date"] = None
        
        self._save_manifest()
    
    def curate_environment(self, profile: str = "standard") -> bool:
        """Intelligently curate the environment based on profile"""
        # Check profiles in manifest first, then fall back to external profiles catalog
        available_profiles = self.manifest.get("profiles", {})
        if not available_profiles:
            available_profiles = self.profiles_catalog
            
        if profile not in available_profiles:
            self.logger.error(f"Unknown profile: {profile}. Available profiles: {list(available_profiles.keys())}")
            return False
        
        packages = available_profiles[profile]
        self.logger.info(f"Curating environment with profile '{profile}': {len(packages)} packages")
        
        success_count = 0
        for package_name in packages:
            if self.install_package(package_name):
                success_count += 1
        
        self.logger.info(f"Environment curation complete: {success_count}/{len(packages)} packages installed")
        return success_count == len(packages)
    
    def get_available_profiles(self) -> Dict[str, List[str]]:
        """Get all available profiles from manifest or external catalog"""
        profiles = self.manifest.get("profiles", {})
        if not profiles:
            profiles = self.profiles_catalog
        return profiles
    
    def cleanup_orphaned_packages(self) -> List[str]:
        """Clean up packages not in any profile (orphaned packages)"""
        installed = {pkg["name"] for pkg in self.list_installed_packages()}
        
        # Get all packages in all profiles
        all_profile_packages = set()
        available_profiles = self.get_available_profiles()
        for packages in available_profiles.values():
            all_profile_packages.update(packages)
        
        # Find orphaned packages
        orphaned = installed - all_profile_packages - set(self.catalog.keys())
        
        if orphaned:
            self.logger.info(f"Found {len(orphaned)} orphaned packages: {list(orphaned)}")
            # Note: In production, might want confirmation before removing
            # For now, just report them
        else:
            self.logger.info("No orphaned packages found")
        
        return list(orphaned)
    
    def get_recommendations(self, installed_packages: List[str] = None) -> List[Package]:
        """Get intelligent package recommendations based on current setup"""
        if installed_packages is None:
            installed_packages = [pkg["name"] for pkg in self.list_installed_packages()]
        
        recommendations = []
        
        # Only provide recommendations if we have a populated catalog
        if not self.catalog:
            self.logger.info("No package catalog available for recommendations")
            return recommendations
        
        # Recommend based on what's already installed
        if "lua-cjson" in installed_packages and "luasocket" not in installed_packages:
            luasocket_pkg = self.catalog.get("luasocket")
            if luasocket_pkg:
                recommendations.append(luasocket_pkg)
        
        if any(pkg in installed_packages for pkg in ["busted", "luassert"]) and "inspect" not in installed_packages:
            inspect_pkg = self.catalog.get("inspect")
            if inspect_pkg:
                recommendations.append(inspect_pkg)
        
        # Recommend high-priority packages not yet installed
        for package in self.catalog.values():
            if package.priority >= 7 and package.name not in installed_packages:
                recommendations.append(package)
        
        # Sort by priority and deduplicate
        recommendations = list(set(recommendations))
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health = {
            "luarocks_available": self._check_luarocks(),
            "lua_version": self._get_lua_version(),
            "installed_packages": len(self.list_installed_packages()),
            "manifest_valid": self.manifest_path.exists(),
            "catalog_size": len(self.catalog),
            "available_profiles": len(self.get_available_profiles()),
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for critical packages (only if catalog is available)
        if self.catalog:
            critical_packages = [pkg for pkg in self.catalog.values() if pkg.priority >= 8]
            critical_installed = sum(1 for pkg in critical_packages 
                                   if self.is_package_installed(pkg.name))
            health["critical_packages_ratio"] = f"{critical_installed}/{len(critical_packages)}"
        else:
            health["critical_packages_ratio"] = "N/A (no catalog)"
        
        return health


# Convenience functions for external use
def get_curator(lua_path: str = None, manifest_path: str = None,
                packages_catalog: Dict[str, Package] = None, 
                profiles_catalog: Dict[str, Dict] = None) -> Curator:
    """Get a configured curator instance with optional external catalogs
    
    Args:
        lua_path: Path to Lua executable
        manifest_path: Path to manifest file
        packages_catalog: External package definitions
        profiles_catalog: External profile definitions
    """
    return Curator(lua_path, manifest_path, packages_catalog, profiles_catalog)


def quick_install(packages: List[str], profile: str = None, 
                  packages_catalog: Dict[str, Package] = None, 
                  profiles_catalog: Dict[str, Dict] = None) -> bool:
    """Quick install packages or profile with optional external catalogs"""
    curator = get_curator(packages_catalog=packages_catalog, profiles_catalog=profiles_catalog)
    
    if profile:
        return curator.curate_environment(profile)
    
    success = True
    for package in packages:
        if not curator.install_package(package):
            success = False
    
    return success


def bootstrap_lua_environment(profile: str = "standard", 
                             packages_catalog: Dict[str, Package] = None, 
                             profiles_catalog: Dict[str, Dict] = None) -> bool:
    """Bootstrap a complete Lua environment with optional external catalogs"""
    curator = get_curator(packages_catalog=packages_catalog, profiles_catalog=profiles_catalog)
    
    # Health check first
    health = curator.health_check()
    curator.logger.info(f"Environment health: {health}")
    
    if not health["luarocks_available"]:
        curator.logger.error("Cannot bootstrap: LuaRocks not available")
        return False
    
    # Check if profile exists
    available_profiles = curator.get_available_profiles()
    if profile not in available_profiles:
        curator.logger.error(f"Profile '{profile}' not found. Available: {list(available_profiles.keys())}")
        return False
    
    # Curate environment
    success = curator.curate_environment(profile)
    
    if success:
        curator.logger.info("Environment bootstrap completed successfully")
        recommendations = curator.get_recommendations()
        if recommendations:
            curator.logger.info(f"Recommended additions: {[r.name for r in recommendations]}")
    
    return success


if __name__ == "__main__":
    # Demo usage - now works with empty catalogs
    curator = get_curator()
    
    print("=== Curator Health Check ===")
    health = curator.health_check()
    for key, value in health.items():
        print(f"{key}: {value}")
    
    print("\n=== Installed Packages ===")
    installed = curator.list_installed_packages()
    for pkg in installed:
        print(f"- {pkg['name']} v{pkg['version']} ({pkg['category']})")
    
    print("\n=== Recommendations ===")
    recommendations = curator.get_recommendations()
    if recommendations:
        for pkg in recommendations:
            print(f"- {pkg.name}: {pkg.description} (priority: {pkg.priority})")
    else:
        print("- No recommendations available (no package catalog loaded)")
    
    print("\n=== Available Profiles ===")
    available_profiles = curator.get_available_profiles()
    if available_profiles:
        for profile, packages in available_profiles.items():
            print(f"- {profile}: {len(packages)} packages")
    else:
        print("- No profiles available (no profiles catalog loaded)")