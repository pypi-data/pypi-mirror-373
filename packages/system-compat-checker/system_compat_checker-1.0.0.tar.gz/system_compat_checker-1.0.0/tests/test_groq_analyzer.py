"""Tests for the groq_analyzer module."""

import unittest
from unittest.mock import patch, MagicMock
import json

from system_compat_checker.groq_analyzer import GroqCompatibilityAnalyzer


class TestGroqAnalyzer(unittest.TestCase):
    """Test cases for the groq_analyzer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = 'test_api_key'
        self.analyzer = GroqCompatibilityAnalyzer(self.api_key)
        self.system_info = {
            'cpu': {'model': 'Test CPU'},
            'memory': {'total': 8589934592},  # 8 GB
            'os': {'system': 'Windows', 'version': '10'}
        }
        self.app_name = 'Test App'
    
    def test_init(self):
        """Test initialization of the analyzer."""
        self.assertEqual(self.analyzer.api_key, self.api_key)
        self.assertEqual(self.analyzer.headers['Authorization'], f'Bearer {self.api_key}')
        self.assertEqual(self.analyzer.headers['Content-Type'], 'application/json')
    
    @patch('system_compat_checker.groq_analyzer.requests.post')
    def test_analyze_compatibility_success(self, mock_post):
        """Test analyzing compatibility successfully."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"compatible": true, "confidence": 90, "recommendations": ["Test recommendation"]}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Call the function
        result = self.analyzer.analyze_compatibility(self.system_info, self.app_name)
        
        # Assertions
        mock_post.assert_called_once()
        self.assertTrue(result['compatible'])
        self.assertEqual(result['confidence'], 90)
        self.assertEqual(result['recommendations'], ['Test recommendation'])
    
    @patch('system_compat_checker.groq_analyzer.requests.post')
    def test_analyze_compatibility_api_error(self, mock_post):
        """Test analyzing compatibility with an API error."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        mock_post.return_value = mock_response
        
        # Call the function
        result = self.analyzer.analyze_compatibility(self.system_info, self.app_name)
        
        # Assertions
        mock_post.assert_called_once()
        self.assertFalse(result['compatible'])
        self.assertEqual(result['confidence'], 0)
        self.assertIn('Failed to analyze compatibility due to an error', result['recommendations'][0])
    
    @patch('system_compat_checker.groq_analyzer.requests.post')
    def test_analyze_compatibility_parse_error(self, mock_post):
        """Test analyzing compatibility with a parsing error."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Invalid JSON'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Call the function
        result = self.analyzer.analyze_compatibility(self.system_info, self.app_name)
        
        # Assertions
        mock_post.assert_called_once()
        self.assertFalse(result['compatible'])
        self.assertEqual(result['confidence'], 0)
        self.assertIn('Failed to analyze compatibility due to an error', result['recommendations'][0])


if __name__ == '__main__':
    unittest.main()
