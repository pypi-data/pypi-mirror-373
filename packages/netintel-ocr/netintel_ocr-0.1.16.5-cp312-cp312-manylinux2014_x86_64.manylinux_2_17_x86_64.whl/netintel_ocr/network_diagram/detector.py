"""Network diagram detection module."""

import json
import base64
import requests
from typing import Dict, Any, Optional
from ..constants import OLLAMA_BASE_URL
from .prompts import DETECTION_PROMPT


class NetworkDiagramDetector:
    """Detects if an image contains a network diagram."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest"):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
    
    def detect(self, image_path: str) -> Dict[str, Any]:
        """
        Detect if the image contains a network diagram.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detection results including confidence score
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Prepare the request payload
            # Note: Some models may not support format="json", so we'll parse the response manually
            payload = {
                "model": self.model,
                "prompt": DETECTION_PROMPT + "\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting or extra text.",
                "stream": False,
                "images": [image_data]
            }
            
            # Make the API call
            response = requests.post(f"{self.base_url}/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Try to extract JSON from the response
                # Sometimes the model returns markdown-wrapped JSON
                if "```json" in response_text:
                    # Extract JSON from markdown code block
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    if end > start:
                        response_text = response_text[start:end].strip()
                elif "```" in response_text:
                    # Extract from generic code block
                    start = response_text.find("```") + 3
                    if response_text[start] == "\n":
                        start += 1
                    end = response_text.find("```", start)
                    if end > start:
                        response_text = response_text[start:end].strip()
                
                try:
                    # Parse the JSON response
                    detection_result = json.loads(response_text)
                    return detection_result
                except json.JSONDecodeError as e:
                    # Try to extract JSON object from text
                    import re
                    json_match = re.search(r'\{[^}]*"is_network_diagram"[^}]*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            detection_result = json.loads(json_match.group())
                            return detection_result
                        except:
                            pass
                    
                    # Fallback if response isn't valid JSON
                    return {
                        "is_network_diagram": False,
                        "confidence": 0.0,
                        "error": f"Invalid JSON response from model: {str(e)}"
                    }
            else:
                return {
                    "is_network_diagram": False,
                    "confidence": 0.0,
                    "error": f"API call failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "is_network_diagram": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def is_network_diagram(self, image_path: str, confidence_threshold: float = 0.7) -> bool:
        """
        Simple boolean check if image is a network diagram.
        
        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence to consider as network diagram
            
        Returns:
            True if network diagram detected with sufficient confidence
        """
        result = self.detect(image_path)
        return (
            result.get("is_network_diagram", False) and 
            result.get("confidence", 0.0) >= confidence_threshold
        )