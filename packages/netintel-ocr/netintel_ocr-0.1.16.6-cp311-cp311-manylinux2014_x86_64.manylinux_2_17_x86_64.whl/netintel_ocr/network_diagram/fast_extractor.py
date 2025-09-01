"""Fast component extraction from network diagrams."""

import json
import base64
import requests
from typing import Dict, Any, List, Optional
from ..constants import OLLAMA_BASE_URL
try:
    from .improved_prompts import IMPROVED_FAST_PROMPT, IMPROVED_EXTRACTION_PROMPT
    USE_IMPROVED_PROMPTS = True
except ImportError:
    USE_IMPROVED_PROMPTS = False

# Original prompt for fallback
ORIGINAL_FAST_PROMPT = """Quickly identify network components and connections in this diagram.

List components with format:
- ID: type (label)
Example: R1: router (Main Router)

List connections with format:
- from -> to
Example: R1 -> SW1

Return as JSON:
{
  "components": [
    {"id": "R1", "type": "router", "label": "Main Router"}
  ],
  "connections": [
    {"from": "R1", "to": "SW1"}
  ]
}

Be concise. Focus only on visible components and connections."""

# Use improved prompt if available, otherwise fallback
if USE_IMPROVED_PROMPTS:
    FAST_EXTRACTION_PROMPT = IMPROVED_FAST_PROMPT
else:
    FAST_EXTRACTION_PROMPT = ORIGINAL_FAST_PROMPT


class FastExtractor:
    """Fast extraction of network components with minimal processing."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest", timeout: int = 30, use_improved_prompts: bool = True):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
        self.timeout = timeout
        self.use_improved = use_improved_prompts and USE_IMPROVED_PROMPTS
    
    def extract_fast(self, image_path: str) -> Dict[str, Any]:
        """
        Fast extraction with simplified prompt.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted components and connections
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Use appropriate prompt based on settings
            if self.use_improved and USE_IMPROVED_PROMPTS:
                prompt = IMPROVED_EXTRACTION_PROMPT + "\n\nReturn ONLY valid JSON."
                num_predict = 1500  # More tokens for detailed extraction
            else:
                prompt = FAST_EXTRACTION_PROMPT
                num_predict = 500  # Original limit
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "images": [image_data],
                "options": {
                    "temperature": 0.1,  # Lower temperature for more deterministic output
                    "top_p": 0.9,
                    "num_predict": num_predict
                }
            }
            
            # Make the API call
            response = requests.post(f"{self.base_url}/generate", json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Extract JSON from response
                extraction_result = self._parse_response(response_text)
                return self._process_fast_extraction(extraction_result)
            else:
                return self._fallback_extraction(image_path)
                
        except Exception:
            return self._fallback_extraction(image_path)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from response text."""
        # Try direct JSON parse first
        try:
            return json.loads(response_text)
        except:
            pass
        
        # Try to extract from markdown
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end > start:
                try:
                    return json.loads(response_text[start:end].strip())
                except:
                    pass
        
        # Try to extract from code block
        if "```" in response_text:
            start = response_text.find("```") + 3
            if response_text[start] == "\n":
                start += 1
            end = response_text.find("```", start)
            if end > start:
                try:
                    return json.loads(response_text[start:end].strip())
                except:
                    pass
        
        # Try to find JSON object
        import re
        json_match = re.search(r'\{[^}]*"components"[^}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {"components": [], "connections": []}
    
    def extract(self, image_path: str) -> Dict[str, Any]:
        """
        Extract components (alias for extract_fast for compatibility).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted components and connections
        """
        return self.extract_fast(image_path)
    
    def _process_fast_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process fast extraction results."""
        components = data.get("components", [])
        connections = data.get("connections", [])
        
        # Ensure components have required fields
        for i, comp in enumerate(components):
            if "id" not in comp:
                comp["id"] = f"comp{i+1}"
            if "type" not in comp:
                comp["type"] = "unknown"
            if "label" not in comp:
                comp["label"] = comp["id"]
            
            # Clean up type field
            comp_type = comp["type"].lower()
            if "|" in comp_type:
                comp["type"] = comp_type.split("|")[0].strip()
            elif comp_type not in ["router", "switch", "firewall", "server", "database", 
                                   "load_balancer", "cloud_service", "workstation", "wireless_ap"]:
                # Try to match partial
                if "rout" in comp_type:
                    comp["type"] = "router"
                elif "switch" in comp_type:
                    comp["type"] = "switch"
                elif "fire" in comp_type:
                    comp["type"] = "firewall"
                elif "serv" in comp_type:
                    comp["type"] = "server"
                elif "data" in comp_type or "db" in comp_type:
                    comp["type"] = "database"
                elif "load" in comp_type or "lb" in comp_type:
                    comp["type"] = "load_balancer"
                elif "cloud" in comp_type:
                    comp["type"] = "cloud_service"
                else:
                    comp["type"] = "unknown"
        
        # Process connections
        for conn in connections:
            if "type" not in conn:
                conn["type"] = "ethernet"
            if "bidirectional" not in conn:
                conn["bidirectional"] = True
        
        return {
            "components": components,
            "connections": connections,
            "zones": [],
            "extraction_successful": True,
            "method": "fast"
        }
    
    def _fallback_extraction(self, image_path: str) -> Dict[str, Any]:
        """Ultra-fast fallback with basic components."""
        # Return empty extraction on timeout
        return {
            "components": [],
            "connections": [],
            "zones": [],
            "extraction_successful": True,
            "method": "fallback",
            "note": "Fast fallback extraction"
        }


def extract_with_optimization(image_path: str, model: str = "nanonets-ocr-s:latest", 
                              use_fast: bool = True) -> Dict[str, Any]:
    """
    Extract components with optimization options.
    
    Args:
        image_path: Path to the image
        model: Model to use
        use_fast: Whether to use fast extraction
        
    Returns:
        Extraction results
    """
    if use_fast:
        extractor = FastExtractor(model)
        return extractor.extract_fast(image_path)
    else:
        # Fall back to regular extraction
        from .extractor import ComponentExtractor
        extractor = ComponentExtractor(model)
        return extractor.extract(image_path)