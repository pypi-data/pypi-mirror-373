"""Tests for the system_info module."""

import unittest
from unittest.mock import patch, MagicMock
import platform
import json

from system_compat_checker.system_info import get_system_info


class TestSystemInfo(unittest.TestCase):
    """Test cases for the system_info module."""
    
    @patch('system_compat_checker.system_info.platform.system')
    @patch('system_compat_checker.system_info.WindowsInfoCollector')
    def test_get_system_info_windows(self, mock_windows_collector, mock_platform_system):
        """Test get_system_info on Windows."""
        # Mock platform.system to return 'Windows'
        mock_platform_system.return_value = 'Windows'
        
        # Mock the WindowsInfoCollector.collect method
        mock_collector_instance = MagicMock()
        mock_windows_collector.return_value = mock_collector_instance
        mock_collector_instance.collect.return_value = {'test': 'data'}
        
        # Call the function
        result = get_system_info()
        
        # Assertions
        mock_platform_system.assert_called_once()
        mock_windows_collector.assert_called_once()
        mock_collector_instance.collect.assert_called_once()
        self.assertEqual(result, {'test': 'data'})
    
    @patch('system_compat_checker.system_info.platform.system')
    @patch('system_compat_checker.system_info.PosixInfoCollector')
    def test_get_system_info_posix(self, mock_posix_collector, mock_platform_system):
        """Test get_system_info on POSIX systems."""
        # Mock platform.system to return 'Linux'
        mock_platform_system.return_value = 'Linux'
        
        # Mock the PosixInfoCollector.collect method
        mock_collector_instance = MagicMock()
        mock_posix_collector.return_value = mock_collector_instance
        mock_collector_instance.collect.return_value = {'test': 'data'}
        
        # Call the function
        result = get_system_info()
        
        # Assertions
        mock_platform_system.assert_called_once()
        mock_posix_collector.assert_called_once()
        mock_collector_instance.collect.assert_called_once()
        self.assertEqual(result, {'test': 'data'})


if __name__ == '__main__':
    unittest.main()
