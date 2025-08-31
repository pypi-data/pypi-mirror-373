"""Tests for the storage module."""

import unittest
from unittest.mock import patch, MagicMock

from system_compat_checker.storage import store_api_key, get_api_key, delete_api_key, SERVICE_NAME, USERNAME


class TestStorage(unittest.TestCase):
    """Test cases for the storage module."""
    
    @patch('system_compat_checker.storage.keyring')
    def test_store_api_key_success(self, mock_keyring):
        """Test storing an API key successfully."""
        # Mock keyring.set_password
        mock_keyring.set_password.return_value = None
        
        # Call the function
        result = store_api_key('test_api_key')
        
        # Assertions
        mock_keyring.set_password.assert_called_once_with(SERVICE_NAME, USERNAME, 'test_api_key')
        self.assertTrue(result)
    
    @patch('system_compat_checker.storage.keyring')
    def test_store_api_key_failure(self, mock_keyring):
        """Test storing an API key with an error."""
        # Mock keyring.set_password to raise an exception
        mock_keyring.set_password.side_effect = Exception('Test error')
        
        # Call the function
        result = store_api_key('test_api_key')
        
        # Assertions
        mock_keyring.set_password.assert_called_once_with(SERVICE_NAME, USERNAME, 'test_api_key')
        self.assertFalse(result)
    
    @patch('system_compat_checker.storage.keyring')
    def test_get_api_key_success(self, mock_keyring):
        """Test retrieving an API key successfully."""
        # Mock keyring.get_password
        mock_keyring.get_password.return_value = 'test_api_key'
        
        # Call the function
        result = get_api_key()
        
        # Assertions
        mock_keyring.get_password.assert_called_once_with(SERVICE_NAME, USERNAME)
        self.assertEqual(result, 'test_api_key')
    
    @patch('system_compat_checker.storage.keyring')
    def test_get_api_key_failure(self, mock_keyring):
        """Test retrieving an API key with an error."""
        # Mock keyring.get_password to raise an exception
        mock_keyring.get_password.side_effect = Exception('Test error')
        
        # Call the function
        result = get_api_key()
        
        # Assertions
        mock_keyring.get_password.assert_called_once_with(SERVICE_NAME, USERNAME)
        self.assertIsNone(result)
    
    @patch('system_compat_checker.storage.keyring')
    def test_delete_api_key_success(self, mock_keyring):
        """Test deleting an API key successfully."""
        # Mock keyring.delete_password
        mock_keyring.delete_password.return_value = None
        
        # Call the function
        result = delete_api_key()
        
        # Assertions
        mock_keyring.delete_password.assert_called_once_with(SERVICE_NAME, USERNAME)
        self.assertTrue(result)
    
    @patch('system_compat_checker.storage.keyring')
    def test_delete_api_key_failure(self, mock_keyring):
        """Test deleting an API key with an error."""
        # Mock keyring.delete_password to raise an exception
        mock_keyring.delete_password.side_effect = Exception('Test error')
        
        # Call the function
        result = delete_api_key()
        
        # Assertions
        mock_keyring.delete_password.assert_called_once_with(SERVICE_NAME, USERNAME)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
