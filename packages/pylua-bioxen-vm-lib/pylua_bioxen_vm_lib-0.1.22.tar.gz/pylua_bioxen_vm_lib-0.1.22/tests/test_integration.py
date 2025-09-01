"""
Integration tests for PyLua VM system
Covers environment manager, LuaProcess curator integration, NetworkedLuaVM setup, and cross-component compatibility.
Mock testing for missing Lua/LuaRocks is excluded.
"""
import unittest
from pylua_bioxen_vm_lib.env import EnvironmentManager
from pylua_bioxen_vm_lib.lua_process import LuaProcess
from pylua_bioxen_vm_lib.networking import NetworkedLuaVM
from pylua_bioxen_vm_lib.logger import VMLogger

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.logger = VMLogger()

    def test_environment_profiles(self):
        for profile in ['minimal', 'standard', 'full', 'development', 'production', 'networking']:
            env = EnvironmentManager(profile=profile, logger=self.logger)
            errors = env.validate()
            self.logger.info(f"Profile '{profile}' validation errors: {errors}")
            self.assertTrue(isinstance(errors, list))

    def test_lua_process_curator_methods(self):
        env = EnvironmentManager(profile='standard', logger=self.logger)
        vm = LuaProcess(env_manager=env, logger=self.logger)
        setup_result = vm.setup_packages(profile='standard')
        self.logger.info(f"Packages installed: {setup_result}")
        self.assertIsNotNone(setup_result)
        recommendations = vm.get_package_recommendations()
        self.logger.info(f"Package recommendations: {recommendations}")
        self.assertIsInstance(recommendations, list)
        health = vm.check_environment_health()
        self.logger.info(f"Environment health: {health}")
        self.assertIsInstance(health, dict)

    def test_networked_lua_vm_setup(self):
        env = EnvironmentManager(profile='networking', logger=self.logger)
        net_vm = NetworkedLuaVM(env_manager=env, logger=self.logger)
        net_result = net_vm.setup_networking_packages(include_advanced=True)
        self.logger.info(f"Networking setup result: {net_result}")
        self.assertIsInstance(net_result, dict)
        health = net_vm.check_networking_health()
        self.logger.info(f"Networking health: {health}")
        self.assertIsInstance(health, dict)
        recommendations = net_vm.get_networking_recommendations()
        self.logger.info(f"Networking recommendations: {recommendations}")
        self.assertIsInstance(recommendations, list)

    def test_profile_switching_and_compatibility(self):
        env = EnvironmentManager(profile='minimal', logger=self.logger)
        vm = LuaProcess(env_manager=env, logger=self.logger)
        vm.setup_packages(profile='minimal')
        env.profile = 'full'
        vm.setup_packages(profile='full')
        self.logger.info(f"Profile switched to 'full'.")
        health = vm.check_environment_health()
        self.logger.info(f"Health after profile switch: {health}")
        self.assertIsInstance(health, dict)

    def test_error_handling(self):
        env = EnvironmentManager(profile='invalid_profile', logger=self.logger)
        errors = env.validate()
        self.logger.info(f"Invalid profile errors: {errors}")
        self.assertTrue(errors)

if __name__ == '__main__':
    unittest.main()
