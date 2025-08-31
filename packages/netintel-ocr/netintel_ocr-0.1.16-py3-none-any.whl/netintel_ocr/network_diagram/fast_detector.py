"""Fast network diagram detection."""

import json
import base64
import requests
from typing import Dict, Any
from ..constants import OLLAMA_BASE_URL

# Simplified detection prompt
FAST_DETECTION_PROMPT = """Is this a network diagram? Look for routers, switches, servers, or network connections.

Answer with JSON:
{
  "is_network_diagram": true/false,
  "confidence": 0.0-1.0
}

Be quick and decisive."""


class FastDetector:
    """Fast network diagram detection with minimal processing."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest"):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
    
    def detect_fast(self, image_path: str) -> Dict[str, Any]:
        """
        Fast detection with simplified prompt.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detection result
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Use simplified prompt with constrained output
            payload = {
                "model": self.model,
                "prompt": FAST_DETECTION_PROMPT,
                "stream": False,
                "images": [image_data],
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent detection
                    "top_p": 0.9,
                    "num_predict": 100  # Very short response needed
                }
            }
            
            # Make the API call with short timeout
            response = requests.post(f"{self.base_url}/generate", json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Parse the response
                detection = self._parse_detection(response_text)
                
                # Add default fields if missing
                if "diagram_type" not in detection:
                    detection["diagram_type"] = "architecture" if detection.get("is_network_diagram") else "none"
                
                return detection
            else:
                return {"is_network_diagram": False, "confidence": 0.0, "error": "API failed"}
                
        except Exception as e:
            return {"is_network_diagram": False, "confidence": 0.0, "error": str(e)[:100]}
    
    def _parse_detection(self, response_text: str) -> Dict[str, Any]:
        """Parse detection result from response."""
        # Try direct JSON parse
        try:
            result = json.loads(response_text)
            if isinstance(result, dict) and "is_network_diagram" in result:
                return result
        except:
            pass
        
        # Try to extract from markdown
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end > start:
                try:
                    result = json.loads(response_text[start:end].strip())
                    if isinstance(result, dict) and "is_network_diagram" in result:
                        return result
                except:
                    pass
        
        # Try to find JSON object
        import re
        json_match = re.search(r'\{[^}]*"is_network_diagram"[^}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                if isinstance(result, dict):
                    return result
            except:
                pass
        
        # Check for keywords in response
        response_lower = response_text.lower()
        if any(word in response_lower for word in ["yes", "true", "network diagram", "network topology"]):
            return {"is_network_diagram": True, "confidence": 0.7}
        elif any(word in response_lower for word in ["no", "false", "not a network", "text"]):
            return {"is_network_diagram": False, "confidence": 0.8}
        
        # Default to not a network diagram
        return {"is_network_diagram": False, "confidence": 0.5}