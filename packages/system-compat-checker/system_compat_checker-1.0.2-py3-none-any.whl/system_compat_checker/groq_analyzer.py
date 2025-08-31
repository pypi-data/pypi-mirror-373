"""Groq API integration for system compatibility analysis.

This module provides functionality to analyze system compatibility using the Groq API.
"""

import json
from typing import Dict, Any, Optional

import requests


class GroqCompatibilityAnalyzer:
    """Groq API integration for system compatibility analysis."""
    
    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    RECOMMENDED_MODEL = "llama3-70b-8192"
    
    def __init__(self, api_key: str):
        """Initialize the Groq compatibility analyzer.
        
        Args:
            api_key: The Groq API key.
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_compatibility(self, system_info: Dict[str, Any], app_name: str, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze system compatibility for a specific application.
        
        Args:
            system_info: The system information collected.
            app_name: The name of the application to check compatibility for.
            requirements: Optional specific requirements for the application.
            
        Returns:
            Dict[str, Any]: The compatibility analysis result.
        """
        # Build the prompt
        prompt = self._build_prompt(system_info, app_name, requirements)
        
        # Call the Groq API
        try:
            response = self._call_api(prompt)
            return self._parse_response(response)
        except Exception as e:
            return {
                "error": str(e),
                "compatible": False,
                "confidence": 0,
                "recommendations": ["Failed to analyze compatibility due to an error."]
            }
    
    def _build_prompt(self, system_info: Dict[str, Any], app_name: str, requirements: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for the Groq API.
        
        Args:
            system_info: The system information collected.
            app_name: The name of the application to check compatibility for.
            requirements: Optional specific requirements for the application.
            
        Returns:
            str: The prompt for the Groq API.
        """
        # Convert system_info to a formatted string
        system_info_str = json.dumps(system_info, indent=2)
        
        # Build the requirements string
        requirements_str = "No specific requirements provided."
        if requirements:
            requirements_str = json.dumps(requirements, indent=2)
        
        # Build the prompt
        prompt = f"""You are a system compatibility expert. Analyze the following system information and determine if it's compatible with {app_name}.

System Information:
```json
{system_info_str}
```

Application: {app_name}

Requirements (if any):
```json
{requirements_str}
```

Provide a detailed analysis of the compatibility, including:
1. Is the system compatible with {app_name}? (Yes/No/Partial)
2. Confidence level (0-100%)
3. Specific compatibility issues (if any)
4. Recommendations for improving compatibility

Format your response as a JSON object with the following structure:
```json
{{
  "compatible": true/false,
  "confidence": 85,
  "issues": [
    "Issue 1",
    "Issue 2"
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "detailed_analysis": "A detailed explanation of the compatibility analysis."
}}
```
"""
        
        return prompt
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Call the Groq API with the given prompt.
        
        Args:
            prompt: The prompt to send to the Groq API.
            
        Returns:
            Dict[str, Any]: The API response.
            
        Raises:
            Exception: If the API call fails.
        """
        payload = {
            "model": self.RECOMMENDED_MODEL,
            "messages": [
                {"role": "system", "content": "You are a system compatibility expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,  # Lower temperature for more deterministic responses
            "max_tokens": 1000
        }
        
        response = requests.post(self.BASE_URL, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
        
        return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the Groq API response.
        
        Args:
            response: The API response.
            
        Returns:
            Dict[str, Any]: The parsed compatibility analysis.
            
        Raises:
            Exception: If the response cannot be parsed.
        """
        try:
            # Extract the content from the response
            content = response["choices"][0]["message"]["content"]
            
            # Extract the JSON part from the content
            json_start = content.find("{")
            json_end = content.rfind("}")
            
            if json_start == -1 or json_end == -1:
                raise Exception("No JSON found in the response")
            
            json_str = content[json_start:json_end + 1]
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["compatible", "confidence", "recommendations"]
            for field in required_fields:
                if field not in result:
                    result[field] = None if field == "compatible" else [] if field == "recommendations" else 0
            
            return result
        
        except Exception as e:
            raise Exception(f"Failed to parse API response: {str(e)}")