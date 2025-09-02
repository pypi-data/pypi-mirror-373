"""Improved flow diagram extractor with loop detection and deduplication."""

import json
import re
from typing import Dict, Any, List, Optional, Set, Tuple
from ..ollama import transcribe_image
from ..output_utils import debug_print
import hashlib


class ImprovedFlowExtractor:
    """Enhanced flow diagram extractor with anti-repetition and loop detection."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """Initialize the improved flow extractor."""
        self.model = model
        self.seen_elements = set()
        self.seen_flows = set()
        self.element_hashes = {}
        
    def extract(self, image_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract flow diagram elements with deduplication and loop detection.
        
        Args:
            image_path: Path to the image file
            custom_prompt: Optional custom prompt
            
        Returns:
            Extracted and deduplicated flow elements
        """
        # Reset tracking sets
        self.seen_elements = set()
        self.seen_flows = set()
        self.element_hashes = {}
        
        prompt = custom_prompt or self._get_improved_prompt()
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            extracted = self._parse_response(response)
            
            # Post-process to remove duplicates and detect loops
            cleaned = self._clean_extraction(extracted)
            
            # Enhance with flow analysis
            enhanced = self._enhance_extraction(cleaned)
            
            return enhanced
            
        except Exception as e:
            debug_print(f"Flow extraction failed: {e}")
            return self._create_error_response(str(e))
    
    def _get_improved_prompt(self) -> str:
        """Get improved extraction prompt that prevents repetition."""
        return """Analyze this flow diagram and extract its elements ONCE. Do not repeat elements.
        
        IMPORTANT: Each element should be listed ONLY ONCE. If you see loops or repeated patterns,
        describe them as connections, not duplicate elements.
        
        Extract:
        1. UNIQUE PROCESS STEPS (list each step only once):
           - Process boxes, activities, tasks
           - Give each a unique ID
           
        2. DECISION POINTS (list each decision only once):
           - Decision diamonds with their conditions
           - Include all possible outcomes (Yes/No, True/False, etc.)
           
        3. DATA ELEMENTS:
           - Databases, files, data stores
           - Input/output elements
           
        4. FLOW CONTROL:
           - Start and end points
           - Loop back connections (describe as connections, not new elements)
           
        5. CONNECTIONS:
           - Sequential flows
           - Conditional branches
           - Loop backs (identify cycles)
           
        Return JSON with NO DUPLICATE elements:
        {
            "extraction_successful": true,
            "elements": [
                {
                    "id": "unique_id",
                    "type": "process|decision|data|start|end",
                    "label": "element text",
                    "description": "what it does"
                }
            ],
            "flows": [
                {
                    "from": "element_id",
                    "to": "element_id",
                    "label": "condition or description",
                    "type": "sequence|conditional|loop"
                }
            ],
            "loops": [
                {
                    "from": "element_id",
                    "to": "element_id",
                    "condition": "loop condition"
                }
            ],
            "process_summary": "Overall process description"
        }
        
        CRITICAL: Do not repeat the same element multiple times. If there's a loop,
        describe it in the 'flows' or 'loops' section, not by duplicating elements."""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the model response."""
        try:
            # Extract JSON from response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '{' in response and '}' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]
            else:
                # Try to extract structured information from text
                return self._extract_from_text(response)
            
            result = json.loads(json_str)
            return result
            
        except Exception as e:
            debug_print(f"Failed to parse JSON, attempting text extraction: {e}")
            return self._extract_from_text(response)
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract flow elements from unstructured text."""
        elements = []
        flows = []
        
        # Split into lines and process
        lines = text.split('\n')
        current_id = 0
        element_map = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip repetitive patterns
            line_hash = hashlib.md5(line.encode()).hexdigest()
            if line_hash in self.seen_elements:
                continue
            self.seen_elements.add(line_hash)
            
            # Detect element types
            if any(keyword in line.lower() for keyword in ['start', 'begin', 'initiate']):
                elem_type = 'start'
            elif any(keyword in line.lower() for keyword in ['end', 'complete', 'finish']):
                elem_type = 'end'
            elif '?' in line or any(keyword in line.lower() for keyword in ['if', 'does', 'check', 'verify']):
                elem_type = 'decision'
            elif any(keyword in line.lower() for keyword in ['data', 'database', 'file', 'store']):
                elem_type = 'data'
            else:
                elem_type = 'process'
            
            # Create element
            elem_id = f"elem_{current_id}"
            element = {
                'id': elem_id,
                'type': elem_type,
                'label': line[:100],  # Truncate long labels
                'description': line
            }
            
            elements.append(element)
            element_map[line] = elem_id
            current_id += 1
        
        # Create sequential flows
        for i in range(len(elements) - 1):
            flow = {
                'from': elements[i]['id'],
                'to': elements[i + 1]['id'],
                'type': 'sequence'
            }
            flows.append(flow)
        
        return {
            'extraction_successful': True,
            'elements': elements,
            'flows': flows,
            'loops': [],
            'process_summary': 'Flow extracted from text'
        }
    
    def _clean_extraction(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate elements and flows."""
        if not extraction.get('extraction_successful'):
            return extraction
        
        # Deduplicate elements
        unique_elements = []
        seen_labels = {}
        
        for elem in extraction.get('elements', []):
            label = elem.get('label', '')
            elem_type = elem.get('type', '')
            
            # Create a hash of the element content
            elem_hash = hashlib.md5(f"{label}{elem_type}".encode()).hexdigest()
            
            if elem_hash not in self.element_hashes:
                self.element_hashes[elem_hash] = elem
                unique_elements.append(elem)
                seen_labels[label] = elem['id']
            else:
                # Map duplicate to original ID for flow updates
                original_id = self.element_hashes[elem_hash]['id']
                if elem.get('id'):
                    self._update_flow_references(extraction.get('flows', []), 
                                               elem['id'], original_id)
        
        # Deduplicate flows
        unique_flows = []
        seen_connections = set()
        
        for flow in extraction.get('flows', []):
            conn_key = (flow.get('from'), flow.get('to'), flow.get('label', ''))
            if conn_key not in seen_connections:
                seen_connections.add(conn_key)
                unique_flows.append(flow)
        
        # Detect loops
        loops = self._detect_loops(unique_flows)
        
        extraction['elements'] = unique_elements
        extraction['flows'] = unique_flows
        extraction['loops'] = loops
        
        return extraction
    
    def _update_flow_references(self, flows: List[Dict], old_id: str, new_id: str):
        """Update flow references when deduplicating elements."""
        for flow in flows:
            if flow.get('from') == old_id:
                flow['from'] = new_id
            if flow.get('to') == old_id:
                flow['to'] = new_id
    
    def _detect_loops(self, flows: List[Dict]) -> List[Dict]:
        """Detect loops in the flow."""
        loops = []
        
        # Build adjacency list
        graph = {}
        for flow in flows:
            from_id = flow.get('from')
            to_id = flow.get('to')
            
            if from_id not in graph:
                graph[from_id] = []
            graph[from_id].append(to_id)
        
        # Find back edges (loops)
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        dfs(neighbor, path[:])
                    elif neighbor in rec_stack:
                        # Found a loop
                        loop_start = path.index(neighbor)
                        loop_path = path[loop_start:] + [neighbor]
                        loops.append({
                            'path': loop_path,
                            'from': node,
                            'to': neighbor,
                            'condition': 'Loop detected'
                        })
            
            rec_stack.remove(node)
        
        # Run DFS from each unvisited node
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return loops
    
    def _enhance_extraction(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance extraction with additional analysis."""
        if not extraction.get('extraction_successful'):
            return extraction
        
        elements = extraction.get('elements', [])
        flows = extraction.get('flows', [])
        loops = extraction.get('loops', [])
        
        # Add flow analysis
        extraction['analysis'] = {
            'total_elements': len(elements),
            'total_flows': len(flows),
            'has_loops': len(loops) > 0,
            'loop_count': len(loops),
            'decision_points': sum(1 for e in elements if e.get('type') == 'decision'),
            'process_steps': sum(1 for e in elements if e.get('type') == 'process'),
            'complexity': self._calculate_complexity(elements, flows, loops)
        }
        
        # Generate clean summary
        extraction['clean_summary'] = self._generate_clean_summary(extraction)
        
        return extraction
    
    def _calculate_complexity(self, elements: List[Dict], flows: List[Dict], 
                             loops: List[Dict]) -> str:
        """Calculate flow complexity."""
        decision_count = sum(1 for e in elements if e.get('type') == 'decision')
        loop_count = len(loops)
        
        if decision_count > 5 or loop_count > 2:
            return 'high'
        elif decision_count > 2 or loop_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_clean_summary(self, extraction: Dict[str, Any]) -> str:
        """Generate a clean, non-repetitive summary of the flow."""
        elements = extraction.get('elements', [])
        flows = extraction.get('flows', [])
        loops = extraction.get('loops', [])
        
        summary_parts = []
        
        # Find start points
        start_elements = [e for e in elements if e.get('type') == 'start']
        if start_elements:
            summary_parts.append(f"Process starts with: {start_elements[0].get('label', 'Start')}")
        
        # List key process steps
        process_steps = [e for e in elements if e.get('type') == 'process']
        if process_steps:
            step_labels = [s.get('label', '') for s in process_steps[:5]]  # Limit to first 5
            summary_parts.append(f"Key steps: {', '.join(step_labels)}")
            if len(process_steps) > 5:
                summary_parts.append(f"... and {len(process_steps) - 5} more steps")
        
        # List decision points
        decisions = [e for e in elements if e.get('type') == 'decision']
        if decisions:
            decision_labels = [d.get('label', '') for d in decisions[:3]]  # Limit to first 3
            summary_parts.append(f"Decision points: {', '.join(decision_labels)}")
        
        # Mention loops
        if loops:
            summary_parts.append(f"Contains {len(loops)} loop(s)")
        
        # Find end points
        end_elements = [e for e in elements if e.get('type') == 'end']
        if end_elements:
            summary_parts.append(f"Process ends with: {end_elements[0].get('label', 'End')}")
        
        return '\n'.join(summary_parts)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            'extraction_successful': False,
            'elements': [],
            'flows': [],
            'loops': [],
            'error': error_msg,
            'analysis': {},
            'clean_summary': f"Failed to extract flow: {error_msg}"
        }