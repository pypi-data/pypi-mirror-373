"""Multi-diagram extractor for pages with multiple network diagrams."""

import json
import base64
import requests
from typing import Dict, Any, List, Optional
from ..constants import OLLAMA_BASE_URL

# Prompt for detecting multiple diagrams
MULTI_DIAGRAM_DETECTION_PROMPT = """Analyze this image and identify ALL network diagrams present.

Some pages may contain multiple separate network diagrams (e.g., "Before" and "After" scenarios, or multiple architecture views).

For EACH distinct network diagram found, provide:
1. Diagram number/position
2. Diagram title or context (if labeled)
3. Brief description
4. Approximate location (top, bottom, left, right, center)

Response format (JSON):
{
  "diagram_count": 2,
  "diagrams": [
    {
      "id": 1,
      "title": "Current Architecture",
      "description": "Shows existing network setup",
      "location": "top",
      "is_network_diagram": true
    },
    {
      "id": 2,
      "title": "Proposed Architecture",
      "description": "Shows new SD-WAN setup",
      "location": "bottom",
      "is_network_diagram": true
    }
  ]
}

If only one diagram, return diagram_count: 1.
If no network diagrams, return diagram_count: 0."""

# Prompt for extracting from specific diagram region
FOCUSED_EXTRACTION_PROMPT = """Focus on the {location} diagram titled "{title}" and extract its components.

{base_prompt}

IMPORTANT: Only extract components from the {location} diagram, ignore other diagrams on the page."""


class MultiDiagramExtractor:
    """Extract multiple network diagrams from a single page."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest"):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
    
    def detect_multiple_diagrams(self, image_path: str) -> Dict[str, Any]:
        """
        Detect if page contains multiple network diagrams.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detection result with diagram count and locations
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            payload = {
                "model": self.model,
                "prompt": MULTI_DIAGRAM_DETECTION_PROMPT,
                "stream": False,
                "images": [image_data],
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            }
            
            response = requests.post(f"{self.base_url}/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Parse JSON response
                detection = self._parse_json_response(response_text)
                
                # Validate and clean
                if not isinstance(detection, dict):
                    detection = {"diagram_count": 1, "diagrams": []}
                
                if "diagram_count" not in detection:
                    detection["diagram_count"] = len(detection.get("diagrams", []))
                
                return detection
            else:
                return {"diagram_count": 1, "diagrams": [], "error": "Detection failed"}
                
        except Exception as e:
            return {"diagram_count": 1, "diagrams": [], "error": str(e)}
    
    def extract_all_diagrams(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract all network diagrams from the page.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of extraction results, one per diagram
        """
        # First detect how many diagrams
        detection = self.detect_multiple_diagrams(image_path)
        
        if detection.get("diagram_count", 0) <= 1:
            # Fall back to single extraction
            from .extractor import ComponentExtractor
            extractor = ComponentExtractor(self.model)
            single_result = extractor.extract(image_path)
            return [single_result]
        
        # Multiple diagrams detected
        extractions = []
        
        for diagram_info in detection.get("diagrams", []):
            if not diagram_info.get("is_network_diagram", True):
                continue
            
            # Extract this specific diagram
            extraction = self._extract_specific_diagram(
                image_path,
                diagram_info.get("location", ""),
                diagram_info.get("title", f"Diagram {diagram_info.get('id', 1)}")
            )
            
            # Add metadata
            extraction["diagram_info"] = diagram_info
            extractions.append(extraction)
        
        return extractions if extractions else [self._empty_extraction()]
    
    def _extract_specific_diagram(self, image_path: str, location: str, title: str) -> Dict[str, Any]:
        """
        Extract components from a specific diagram on the page.
        
        Args:
            image_path: Path to the image
            location: Location of the diagram (top, bottom, etc.)
            title: Title or identifier of the diagram
            
        Returns:
            Extraction result for this specific diagram
        """
        try:
            from .extractor import ComponentExtractor
            from .prompts import EXTRACTION_PROMPT
            
            # Create focused prompt
            focused_prompt = FOCUSED_EXTRACTION_PROMPT.format(
                location=location if location else "specified",
                title=title,
                base_prompt=EXTRACTION_PROMPT
            )
            
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            payload = {
                "model": self.model,
                "prompt": focused_prompt + "\n\nReturn ONLY valid JSON.",
                "stream": False,
                "images": [image_data]
            }
            
            response = requests.post(f"{self.base_url}/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Parse and validate
                extraction = self._parse_json_response(response_text)
                
                if isinstance(extraction, dict):
                    extraction["extraction_successful"] = True
                    extraction["diagram_title"] = title
                    extraction["diagram_location"] = location
                    return self._validate_extraction(extraction)
                else:
                    return self._empty_extraction(f"Failed to extract {title}")
            else:
                return self._empty_extraction(f"API call failed for {title}")
                
        except Exception as e:
            return self._empty_extraction(str(e))
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON from LLM response."""
        # Try direct parse
        try:
            return json.loads(response_text)
        except:
            pass
        
        # Try extracting from markdown
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end > start:
                try:
                    return json.loads(response_text[start:end].strip())
                except:
                    pass
        
        # Try finding JSON object
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {}
    
    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extraction data."""
        validated = {
            "components": data.get("components", []),
            "connections": data.get("connections", []),
            "zones": data.get("zones", []),
            "extraction_successful": data.get("extraction_successful", True),
            "diagram_title": data.get("diagram_title", ""),
            "diagram_location": data.get("diagram_location", "")
        }
        
        # Ensure components have IDs
        for i, comp in enumerate(validated["components"]):
            if "id" not in comp:
                comp["id"] = f"comp{i+1}"
            if "type" not in comp:
                comp["type"] = "unknown"
            if "label" not in comp:
                comp["label"] = comp["id"]
        
        return validated
    
    def _empty_extraction(self, error: str = None) -> Dict[str, Any]:
        """Return empty extraction result."""
        result = {
            "components": [],
            "connections": [],
            "zones": [],
            "extraction_successful": False
        }
        if error:
            result["error"] = error
        return result