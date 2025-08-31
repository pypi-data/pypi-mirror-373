"""Tests for the CLI module."""

import unittest
from unittest.mock import patch, MagicMock
import json

from click.testing import CliRunner
from system_compat_checker.cli import cli


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_version(self):
        """Test the version command."""
        result = self.runner.invoke(cli, ['version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('System Compatibility Checker', result.output)
    
    @patch('system_compat_checker.cli.get_api_key')
    @patch('system_compat_checker.cli.store_api_key')
    def test_setup(self, mock_store_api_key, mock_get_api_key):
        """Test the setup command."""
        # Mock get_api_key to return None (no existing key)
        mock_get_api_key.return_value = None
        # Mock store_api_key to return True (success)
        mock_store_api_key.return_value = True
        
        # Call the command with input
        result = self.runner.invoke(cli, ['setup'], input='test_api_key\n')
        
        # Assertions
        self.assertEqual(result.exit_code, 0)
        mock_get_api_key.assert_called_once()
        mock_store_api_key.assert_called_once_with('test_api_key')
        self.assertIn('API key stored successfully', result.output)
    
    @patch('system_compat_checker.cli.get_system_info')
    def test_system_info(self, mock_get_system_info):
        """Test the system-info command."""
        # Mock get_system_info to return test data
        mock_get_system_info.return_value = {
            'cpu': {'model': 'Test CPU'},
            'memory': {'total': 8589934592},  # 8 GB
            'os': {'system': 'Windows', 'version': '10'}
        }
        
        # Call the command
        result = self.runner.invoke(cli, ['system-info'])
        
        # Assertions
        self.assertEqual(result.exit_code, 0)
        mock_get_system_info.assert_called_once()
    
    @patch('system_compat_checker.cli.get_system_info')
    def test_system_info_json(self, mock_get_system_info):
        """Test the system-info command with JSON output."""
        # Mock get_system_info to return test data
        test_data = {
            'cpu': {'model': 'Test CPU'},
            'memory': {'total': 8589934592},  # 8 GB
            'os': {'system': 'Windows', 'version': '10'}
        }
        mock_get_system_info.return_value = test_data
        
        # Call the command
        result = self.runner.invoke(cli, ['system-info', '--json'])
        
        # Assertions
        self.assertEqual(result.exit_code, 0)
        mock_get_system_info.assert_called_once()
        # Check that the output is valid JSON and matches the test data
        output_data = json.loads(result.output)
        self.assertEqual(output_data, test_data)
    
    @patch('system_compat_checker.cli.get_api_key')
    @patch('system_compat_checker.cli.delete_api_key')
    def test_reset(self, mock_delete_api_key, mock_get_api_key):
        """Test the reset command."""
        # Mock get_api_key to return a key
        mock_get_api_key.return_value = 'test_api_key'
        # Mock delete_api_key to return True (success)
        mock_delete_api_key.return_value = True
        
        # Call the command with confirmation
        result = self.runner.invoke(cli, ['reset'], input='y\n')
        
        # Assertions
        self.assertEqual(result.exit_code, 0)
        mock_delete_api_key.assert_called_once()
        self.assertIn('API key removed successfully', result.output)


if __name__ == '__main__':
    unittest.main()
