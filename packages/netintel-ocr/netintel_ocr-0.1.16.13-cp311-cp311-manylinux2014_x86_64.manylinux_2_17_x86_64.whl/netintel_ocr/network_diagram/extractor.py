"""Component extraction from network diagrams."""

import json
import base64
import requests
from typing import Dict, Any, List, Optional
from ..constants import OLLAMA_BASE_URL
from .prompts import EXTRACTION_PROMPT
try:
    from .improved_prompts import IMPROVED_EXTRACTION_PROMPT
    USE_IMPROVED = True
except ImportError:
    USE_IMPROVED = False


class ComponentExtractor:
    """Extracts network components and relationships from diagrams."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest", use_improved_prompts: bool = True):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
        self.use_improved = use_improved_prompts and USE_IMPROVED
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        Extract network components and relationships from the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted components, connections, and zones
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Use improved prompt if available
            if self.use_improved and USE_IMPROVED:
                prompt = IMPROVED_EXTRACTION_PROMPT
            else:
                prompt = EXTRACTION_PROMPT
            
            # Prepare the request payload
            # Note: Some models may not support format="json", so we'll parse the response manually
            payload = {
                "model": self.model,
                "prompt": prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no markdown formatting or extra text.",
                "stream": False,
                "images": [image_data],
                "options": {
                    "temperature": 0.1,  # Low temperature for accuracy
                    "top_p": 0.95,
                    "num_predict": 2000  # Enough tokens for detailed extraction
                }
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
                    extraction_result = json.loads(response_text)
                    return self._validate_extraction(extraction_result)
                except json.JSONDecodeError as e:
                    # Try to find JSON object in the response
                    import re
                    json_match = re.search(r'\{[^}]*"components"[^}]*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            extraction_result = json.loads(json_match.group())
                            return self._validate_extraction(extraction_result)
                        except:
                            pass
                    return self._empty_extraction(f"Invalid JSON response from model: {str(e)}")
            else:
                return self._empty_extraction(f"API call failed: {response.status_code}")
                
        except Exception as e:
            return self._empty_extraction(str(e))
    
    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the extracted data.
        
        Args:
            data: Raw extraction data
            
        Returns:
            Validated extraction data
        """
        # Ensure required fields exist
        validated = {
            "components": data.get("components", []),
            "connections": data.get("connections", []),
            "zones": data.get("zones", []),
            "extraction_successful": True
        }
        
        # Validate components have required fields
        for component in validated["components"]:
            if "id" not in component:
                component["id"] = f"comp_{len(validated['components'])}"
            if "type" not in component:
                component["type"] = "unknown"
            else:
                # Clean up type field - if it has pipe characters, take the first type
                comp_type = component["type"]
                if "|" in comp_type:
                    # Take the first type if multiple are given
                    component["type"] = comp_type.split("|")[0].strip()
                # Also handle case where all types are listed
                elif "router" in comp_type and "switch" in comp_type and "firewall" in comp_type:
                    # This looks like all types were listed, default to first mentioned
                    if "router" in comp_type.lower():
                        component["type"] = "router"
                    elif "switch" in comp_type.lower():
                        component["type"] = "switch"
                    elif "firewall" in comp_type.lower():
                        component["type"] = "firewall"
                    else:
                        component["type"] = "unknown"
            if "label" not in component:
                component["label"] = component["id"]
        
        # Validate connections reference existing components
        component_ids = {c["id"] for c in validated["components"]}
        validated["connections"] = [
            conn for conn in validated["connections"]
            if conn.get("from") in component_ids and conn.get("to") in component_ids
        ]
        
        return validated
    
    def _empty_extraction(self, error: str = None) -> Dict[str, Any]:
        """
        Return empty extraction result.
        
        Args:
            error: Error message if any
            
        Returns:
            Empty extraction structure
        """
        result = {
            "components": [],
            "connections": [],
            "zones": [],
            "extraction_successful": False
        }
        if error:
            result["error"] = error
        return result
    
    def get_component_summary(self, extraction: Dict[str, Any]) -> str:
        """
        Generate a summary of extracted components.
        
        Args:
            extraction: Extraction results
            
        Returns:
            Human-readable summary
        """
        if not extraction.get("extraction_successful"):
            return "Extraction failed: " + extraction.get("error", "Unknown error")
        
        components = extraction.get("components", [])
        connections = extraction.get("connections", [])
        zones = extraction.get("zones", [])
        
        summary = []
        summary.append(f"Found {len(components)} components:")
        
        # Count by type
        type_counts = {}
        for comp in components:
            comp_type = comp.get("type", "unknown")
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        for comp_type, count in type_counts.items():
            summary.append(f"  - {count} {comp_type}(s)")
        
        summary.append(f"Found {len(connections)} connections")
        summary.append(f"Found {len(zones)} network zones")
        
        return "\n".join(summary)