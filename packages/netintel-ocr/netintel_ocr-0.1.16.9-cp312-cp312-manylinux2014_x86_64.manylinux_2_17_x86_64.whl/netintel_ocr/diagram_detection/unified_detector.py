"""Unified diagram detector for network, flow, and hybrid diagrams."""

import json
from typing import Dict, Any, Optional
from ..ollama import transcribe_image
from ..output_utils import debug_print


class UnifiedDiagramDetector:
    """Detects and classifies diagrams as network, flow, or hybrid."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925", confidence_threshold: float = 0.7):
        """
        Initialize the unified diagram detector.
        
        Args:
            model: The vision model to use for detection
            confidence_threshold: Minimum confidence to consider a diagram detected
        """
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.failed_attempts = 0
        self.max_failures = 3
    
    def detect(self, image_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect if the image contains a diagram and classify its type.
        
        Args:
            image_path: Path to the image file
            custom_prompt: Optional custom prompt to override default
            
        Returns:
            Detection results with diagram category and type
        """
        # Stop processing if model has failed too many times
        if self.failed_attempts >= self.max_failures:
            raise Exception(f"Stopping: Diagram detection model has failed {self.max_failures} times")
        
        prompt = custom_prompt or self._get_detection_prompt()
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            result = self._parse_response(response)
            # Reset failure count on successful parse
            if result.get('error') is None:
                self.failed_attempts = 0
            return result
        except Exception as e:
            self.failed_attempts += 1
            error_msg = str(e)
            
            # Show verbose error messages
            if "GGML_ASSERT" in error_msg or "status code 500" in error_msg:
                debug_print(f"Diagram detection failed: {error_msg} (attempt {self.failed_attempts}/{self.max_failures})")
            elif "status code 404" in error_msg:
                debug_print(f"Model not found: {error_msg} (attempt {self.failed_attempts}/{self.max_failures})")
            else:
                debug_print(f"Diagram detection failed: {error_msg} (attempt {self.failed_attempts}/{self.max_failures})")
            
            # Stop processing after max failures
            if self.failed_attempts >= self.max_failures:
                raise Exception(f"Stopping: Model failed {self.max_failures} times. Last error: {error_msg}")
            
            # Return a safe default response
            return {
                'is_diagram': False,
                'diagram_category': 'none',
                'diagram_type': 'unknown',
                'confidence': 0.0,
                'description': '',
                'key_elements': [],
                'error': f"Model error (attempt {self.failed_attempts}/{self.max_failures})"
            }
    
    def _get_detection_prompt(self) -> str:
        """Get the default detection prompt."""
        return """Analyze this image and determine if it contains a diagram.
        
        Classify the diagram into one of these categories:
        1. NETWORK: Network topology, security architecture, infrastructure diagrams
           - Look for: routers, switches, firewalls, servers, cloud resources, network connections
           
        2. FLOW: Process flows, workflows, decision trees, sequence diagrams, data flows
           - Look for: process boxes, decision diamonds, start/end points, flow arrows, swim lanes
           
        3. HYBRID: Contains both network and flow elements
           - Look for: combination of network devices AND process/flow elements
           
        4. NONE: Not a diagram or unrecognizable diagram type
        
        Return a JSON response with:
        {
            "is_diagram": boolean,
            "diagram_category": "network" | "flow" | "hybrid" | "none",
            "diagram_type": specific type (e.g., "network_topology", "process_flow", "workflow"),
            "confidence": float (0.0 to 1.0),
            "description": brief description of what the diagram shows,
            "key_elements": list of identified elements
        }
        
        Focus on accuracy. Only classify as a diagram if you're confident."""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the model response into structured data."""
        try:
            # Try to extract JSON from response
            if isinstance(response, str):
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '{' in response and '}' in response:
                    start = response.index('{')
                    end = response.rindex('}') + 1
                    json_str = response[start:end]
                else:
                    # Fallback parsing
                    return self._fallback_parse(response)
                
                result = json.loads(json_str)
            else:
                result = response
            
            # Validate and ensure required fields
            is_diagram = result.get('is_diagram', False)
            confidence = result.get('confidence', 0.0)
            
            # Apply confidence threshold
            if confidence < self.confidence_threshold:
                is_diagram = False
            
            return {
                'is_diagram': is_diagram,
                'diagram_category': result.get('diagram_category', 'none'),
                'diagram_type': result.get('diagram_type', 'unknown'),
                'confidence': confidence,
                'description': result.get('description', ''),
                'key_elements': result.get('key_elements', []),
                'error': None
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            # Show full error for debugging
            debug_print(f"Failed to parse detection response: {e}")
            return self._fallback_parse(response)
        except Exception as e:
            debug_print(f"Unexpected error parsing response: {e}")
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails."""
        response_lower = response.lower()
        
        # Simple heuristic detection
        is_network = any(word in response_lower for word in 
                         ['router', 'switch', 'firewall', 'network', 'topology'])
        is_flow = any(word in response_lower for word in 
                      ['process', 'workflow', 'decision', 'flow', 'sequence'])
        
        if is_network and is_flow:
            category = 'hybrid'
        elif is_network:
            category = 'network'
        elif is_flow:
            category = 'flow'
        else:
            category = 'none'
        
        return {
            'is_diagram': category != 'none',
            'diagram_category': category,
            'diagram_type': 'unknown',
            'confidence': 0.5 if category != 'none' else 0.0,
            'description': response[:200] if len(response) > 200 else response,
            'key_elements': [],
            'error': None
        }


class NetworkDiagramDetector(UnifiedDiagramDetector):
    """Legacy compatibility class - redirects to unified detector."""
    
    def detect(self, image_path: str) -> Dict[str, Any]:
        """Detect network diagrams (legacy compatibility)."""
        result = super().detect(image_path)
        
        # Convert to legacy format
        is_network = result['diagram_category'] in ['network', 'hybrid']
        
        return {
            'is_network_diagram': is_network,
            'confidence': result['confidence'],
            'diagram_type': result.get('diagram_type', 'network_topology'),
            'description': result.get('description', '')
        }