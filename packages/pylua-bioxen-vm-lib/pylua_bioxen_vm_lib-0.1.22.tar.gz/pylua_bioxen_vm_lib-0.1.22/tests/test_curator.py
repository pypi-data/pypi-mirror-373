"""
Unit tests for Curator system in PyLua VM
Covers package recommendations, version management, dependency resolution, manifest, health monitoring, and error handling.
"""
import unittest
from pylua_vm.env import EnvironmentManager
from pylua_vm.utils.curator import Curator
from pylua_vm.logger import VMLogger

class TestCurator(unittest.TestCase):
    def setUp(self):
        self.logger = VMLogger()
        self.env = EnvironmentManager(profile='standard', logger=self.logger)
        self.curator = Curator(env_manager=self.env, logger=self.logger)

    def test_recommend_packages(self):
        recommendations = self.curator.recommend_packages()
        self.logger.info(f"Curator recommendations: {recommendations}")
        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)

    def test_install_package(self):
        package = self.curator.recommend_packages()[0]
        result = self.curator.install_package(package)
        self.logger.info(f"Install result for {package}: {result}")
        self.assertTrue(result)

    def test_version_pinning(self):
        package = self.curator.recommend_packages()[0]
        result = self.curator.install_package(package, version='1.0.0')
        self.logger.info(f"Install with version pinning: {result}")
        self.assertTrue(result)

    def test_dependency_resolution(self):
        deps = self.curator.resolve_dependencies('luasocket')
        self.logger.info(f"Dependencies for luasocket: {deps}")
        self.assertIsInstance(deps, list)

    def test_manifest_generation(self):
        manifest = self.curator.generate_manifest()
        self.logger.info(f"Curator manifest: {manifest}")
        self.assertIsInstance(manifest, dict)
        self.assertIn('packages', manifest)

    def test_health_monitoring(self):
        health = self.curator.health_check()
        self.logger.info(f"Curator health: {health}")
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)

    def test_error_handling_invalid_package(self):
        result = self.curator.install_package('nonexistent_package')
        self.logger.info(f"Install result for invalid package: {result}")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
