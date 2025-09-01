"""
Unit tests for NetworkedLuaVM in PyLua VM
Covers networking package setup, recommendations, health checks, categorization, and error handling.
"""
import unittest
from pylua_vm.env import EnvironmentManager
from pylua_vm.networking import NetworkedLuaVM
from pylua_vm.logger import VMLogger

class TestNetworkedLuaVM(unittest.TestCase):
    def setUp(self):
        self.logger = VMLogger()
        self.env = EnvironmentManager(profile='networking', logger=self.logger)
        self.net_vm = NetworkedLuaVM(env_manager=self.env, logger=self.logger)

    def test_networking_package_setup(self):
        result = self.net_vm.setup_networking_packages(include_advanced=True)
        self.logger.info(f"Networking package setup result: {result}")
        self.assertIsInstance(result, dict)
        self.assertIn('networking_ready', result)

    def test_networking_recommendations(self):
        recommendations = self.net_vm.get_networking_recommendations()
        self.logger.info(f"Networking recommendations: {recommendations}")
        self.assertIsInstance(recommendations, list)
        for rec in recommendations:
            self.assertIn('networking_category', rec)
            self.assertIn('package', rec)

    def test_networking_health_check(self):
        health = self.net_vm.check_networking_health()
        self.logger.info(f"Networking health: {health}")
        self.assertIsInstance(health, dict)
        self.assertIn('networking', health)
        self.assertIn('networking_readiness_percentage', health['networking'])

    def test_luasocket_verification(self):
        verified = self.net_vm.verify_luasocket()
        self.logger.info(f"LuaSocket verification: {verified}")
        self.assertTrue(isinstance(verified, bool))

    def test_http_client_template(self):
        client = self.net_vm.get_http_client_template()
        self.logger.info(f"HTTP client template: {client}")
        self.assertTrue(client)

    def test_error_handling_invalid_category(self):
        recommendations = self.net_vm.get_networking_recommendations(category='invalid')
        self.logger.info(f"Recommendations for invalid category: {recommendations}")
        self.assertIsInstance(recommendations, list)

if __name__ == '__main__':
    unittest.main()
