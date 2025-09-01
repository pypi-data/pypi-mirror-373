"""
Unit tests for EnvironmentManager in PyLua VM
Covers profile management, Lua/LuaRocks detection, config validation, system info, path resolution, and error handling.
"""
import unittest
from pylua_vm.env import EnvironmentManager
from pylua_vm.logger import VMLogger

class TestEnvironmentManager(unittest.TestCase):
    def setUp(self):
        self.logger = VMLogger()

    def test_profile_management(self):
        profiles = ['minimal', 'standard', 'full', 'development', 'production', 'networking']
        for profile in profiles:
            env = EnvironmentManager(profile=profile, logger=self.logger)
            self.assertEqual(env.profile, profile)

    def test_lua_detection(self):
        env = EnvironmentManager(profile='standard', logger=self.logger)
        lua_exec = env.detect_lua()
        self.logger.info(f"Detected Lua executable: {lua_exec}")
        self.assertTrue(lua_exec)

    def test_luarocks_detection(self):
        env = EnvironmentManager(profile='standard', logger=self.logger)
        luarocks_exec = env.detect_luarocks()
        self.logger.info(f"Detected LuaRocks executable: {luarocks_exec}")
        self.assertTrue(luarocks_exec)

    def test_config_validation(self):
        env = EnvironmentManager(profile='standard', logger=self.logger)
        valid = env.validate_config()
        self.logger.info(f"Config validation result: {valid}")
        self.assertTrue(valid)

    def test_system_info(self):
        env = EnvironmentManager(profile='standard', logger=self.logger)
        info = env.get_system_info()
        self.logger.info(f"System info: {info}")
        self.assertIsInstance(info, dict)
        self.assertIn('platform', info)

    def test_path_resolution(self):
        env = EnvironmentManager(profile='standard', logger=self.logger)
        lua_path = env.resolve_lua_path()
        self.logger.info(f"Resolved Lua path: {lua_path}")
        self.assertTrue(lua_path)

    def test_error_handling_invalid_profile(self):
        env = EnvironmentManager(profile='invalid_profile', logger=self.logger)
        errors = env.validate()
        self.logger.info(f"Errors for invalid profile: {errors}")
        self.assertTrue(errors)

if __name__ == '__main__':
    unittest.main()
