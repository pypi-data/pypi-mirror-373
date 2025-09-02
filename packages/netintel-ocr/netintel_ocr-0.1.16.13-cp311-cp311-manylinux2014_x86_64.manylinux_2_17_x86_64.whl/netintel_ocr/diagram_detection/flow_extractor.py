"""Flow diagram element extractor."""

import json
from typing import Dict, Any, List, Optional
from ..ollama import transcribe_image
from ..output_utils import debug_print


class FlowElementExtractor:
    """Extracts elements from flow diagrams (process flows, workflows, etc.)."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """
        Initialize the flow element extractor.
        
        Args:
            model: The vision model to use for extraction
        """
        self.model = model
    
    def extract(self, image_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract flow diagram elements from the image.
        
        Args:
            image_path: Path to the image file
            custom_prompt: Optional custom prompt to override default
            
        Returns:
            Extracted flow elements and connections
        """
        prompt = custom_prompt or self._get_extraction_prompt()
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            return self._parse_response(response)
        except Exception as e:
            debug_print(f"Flow element extraction failed: {e}")
            return {
                'extraction_successful': False,
                'elements': [],
                'flows': [],
                'swim_lanes': [],
                'start_end_points': [],
                'error': str(e)
            }
    
    def _get_extraction_prompt(self) -> str:
        """Get the default flow extraction prompt."""
        return """Extract all flow diagram elements from this image.
        
        Identify and categorize:
        1. PROCESS ELEMENTS:
           - Process boxes (rectangles)
           - Sub-processes
           - Manual processes
           
        2. DECISION POINTS:
           - Decision diamonds
           - Conditional branches
           - Switch/case structures
           
        3. DATA ELEMENTS:
           - Data stores (databases, files)
           - Input/output elements
           - Documents
           
        4. FLOW CONTROL:
           - Start points (ovals, circles)
           - End points (ovals, circles)
           - Connectors
           - Loop backs
           
        5. ORGANIZATIONAL:
           - Swim lanes (if present)
           - Phases or stages
           - Roles/responsibilities
        
        6. CONNECTIONS:
           - Flow arrows with labels
           - Decision outcomes (Yes/No, True/False)
           - Data flows
        
        Return a JSON response with:
        {
            "extraction_successful": boolean,
            "elements": [
                {
                    "id": unique identifier,
                    "type": "process" | "decision" | "data" | "start" | "end" | "connector",
                    "label": text label on element,
                    "description": what this element does,
                    "position": approximate position in flow
                }
            ],
            "flows": [
                {
                    "from": element id,
                    "to": element id,
                    "label": flow label or condition,
                    "type": "sequence" | "conditional" | "data" | "loop"
                }
            ],
            "swim_lanes": [
                {
                    "id": lane identifier,
                    "label": lane name/role,
                    "elements": [list of element ids in this lane]
                }
            ],
            "start_end_points": {
                "starts": [list of start element ids],
                "ends": [list of end element ids]
            },
            "process_summary": brief description of overall process
        }"""
    
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
                    return self._create_error_response("Could not extract JSON from response")
                
                result = json.loads(json_str)
            else:
                result = response
            
            # Validate and ensure required fields
            return {
                'extraction_successful': result.get('extraction_successful', False),
                'elements': result.get('elements', []),
                'flows': result.get('flows', []),
                'swim_lanes': result.get('swim_lanes', []),
                'start_end_points': result.get('start_end_points', {'starts': [], 'ends': []}),
                'process_summary': result.get('process_summary', '')
            }
            
        except Exception as e:
            debug_print(f"Failed to parse flow extraction response: {e}")
            return self._create_error_response(str(e))
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            'extraction_successful': False,
            'elements': [],
            'flows': [],
            'swim_lanes': [],
            'start_end_points': {'starts': [], 'ends': []},
            'error': error_msg
        }
    
    def enhance_extraction(self, basic_extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance basic extraction with additional analysis.
        
        Args:
            basic_extraction: Initial extraction results
            
        Returns:
            Enhanced extraction with additional metadata
        """
        if not basic_extraction.get('extraction_successful'):
            return basic_extraction
        
        enhanced = basic_extraction.copy()
        
        # Analyze critical path
        enhanced['critical_path'] = self._find_critical_path(
            basic_extraction['elements'],
            basic_extraction['flows'],
            basic_extraction.get('start_end_points', {})
        )
        
        # Identify decision complexity
        enhanced['decision_complexity'] = self._analyze_decisions(
            basic_extraction['elements']
        )
        
        # Find loops and cycles
        enhanced['loops'] = self._find_loops(
            basic_extraction['flows']
        )
        
        return enhanced
    
    def _find_critical_path(self, elements: List[Dict], flows: List[Dict], 
                           start_end: Dict) -> List[str]:
        """Find the critical path through the flow."""
        # Simplified critical path - longest path from start to end
        starts = start_end.get('starts', [])
        ends = start_end.get('ends', [])
        
        if not starts or not ends:
            return []
        
        # For now, return main path (would need graph traversal for real implementation)
        path = []
        current = starts[0] if starts else None
        visited = set()
        
        while current and current not in ends:
            if current in visited:
                break  # Avoid infinite loops
            
            path.append(current)
            visited.add(current)
            
            # Find next element
            next_elements = [f['to'] for f in flows if f['from'] == current]
            current = next_elements[0] if next_elements else None
        
        if current in ends:
            path.append(current)
        
        return path
    
    def _analyze_decisions(self, elements: List[Dict]) -> Dict[str, Any]:
        """Analyze decision point complexity."""
        decisions = [e for e in elements if e.get('type') == 'decision']
        
        return {
            'total_decisions': len(decisions),
            'decision_points': [d.get('label', d.get('id')) for d in decisions],
            'complexity_level': 'high' if len(decisions) > 5 else 'medium' if len(decisions) > 2 else 'low'
        }
    
    def _find_loops(self, flows: List[Dict]) -> List[Dict]:
        """Find loops in the flow."""
        loops = []
        
        # Simple loop detection - flows that go backwards
        for flow in flows:
            if flow.get('type') == 'loop':
                loops.append({
                    'from': flow['from'],
                    'to': flow['to'],
                    'condition': flow.get('label', 'unspecified')
                })
        
        return loops


class UnifiedDiagramExtractor:
    """Unified extractor that handles both network and flow diagrams."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """Initialize the unified extractor."""
        self.model = model
        self.flow_extractor = FlowElementExtractor(model)
        # Import network extractor when available
        self.network_extractor = None  # Will be set to ComponentExtractor
    
    def extract(self, image_path: str, diagram_category: str) -> Dict[str, Any]:
        """
        Extract elements based on diagram category.
        
        Args:
            image_path: Path to the image file
            diagram_category: 'network', 'flow', or 'hybrid'
            
        Returns:
            Extracted elements appropriate for diagram type
        """
        if diagram_category == 'flow':
            return self.flow_extractor.extract(image_path)
        elif diagram_category == 'network':
            if self.network_extractor:
                return self.network_extractor.extract(image_path)
            else:
                # Fallback if network extractor not available
                return {'extraction_successful': False, 'error': 'Network extractor not available'}
        elif diagram_category == 'hybrid':
            # Extract both types and merge
            flow_data = self.flow_extractor.extract(image_path)
            network_data = self.network_extractor.extract(image_path) if self.network_extractor else {}
            
            return self._merge_extractions(flow_data, network_data)
        else:
            return {'extraction_successful': False, 'error': f'Unknown diagram category: {diagram_category}'}
    
    def _merge_extractions(self, flow_data: Dict, network_data: Dict) -> Dict[str, Any]:
        """Merge flow and network extraction results."""
        return {
            'extraction_successful': flow_data.get('extraction_successful', False) or 
                                    network_data.get('extraction_successful', False),
            'flow_elements': flow_data.get('elements', []),
            'network_components': network_data.get('components', []),
            'flows': flow_data.get('flows', []),
            'network_connections': network_data.get('connections', []),
            'swim_lanes': flow_data.get('swim_lanes', []),
            'security_zones': network_data.get('security_zones', []),
            'diagram_type': 'hybrid'
        }