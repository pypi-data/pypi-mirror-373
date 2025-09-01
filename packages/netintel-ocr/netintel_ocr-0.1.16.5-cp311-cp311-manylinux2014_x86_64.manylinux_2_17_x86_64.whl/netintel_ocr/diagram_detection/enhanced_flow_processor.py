"""Enhanced flow chart processor using vision model for proper extraction."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from ..ollama import transcribe_image
from ..output_utils import debug_print
from ..network_diagram.mermaid_syntax_fixer import MermaidSyntaxFixer


class EnhancedFlowProcessor:
    """Complete flow chart processor using vision model for extraction, Mermaid generation, and context."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """Initialize the enhanced flow processor."""
        self.model = model
        self.mermaid_fixer = MermaidSyntaxFixer()
        self.detected_elements = {}
        self.element_counter = 0
        
    def detect_flow_diagram(self, image_path: str) -> Tuple[bool, float, str]:
        """
        Detect if the image contains a flow diagram using vision model.
        
        Returns:
            (is_flow_diagram, confidence, diagram_type)
        """
        prompt = """Analyze this image and determine if it contains a flow diagram.
        
        Look for:
        - Process boxes (rectangles with text)
        - Decision diamonds
        - Start/end ovals or circles
        - Arrows connecting elements
        - Swim lanes or process phases
        - Flow direction indicators
        
        Common flow diagram types:
        - Process flow diagrams
        - Workflow diagrams
        - Decision trees
        - Business process models (BPMN)
        - Data flow diagrams
        - Sequence diagrams
        - Activity diagrams
        
        Return JSON:
        {
            "is_flow_diagram": true/false,
            "confidence": 0.0-1.0,
            "diagram_type": "process_flow|workflow|decision_tree|data_flow|sequence|activity|other",
            "reasoning": "why this is/isn't a flow diagram"
        }"""
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            result = self._parse_json_response(response)
            
            return (
                result.get('is_flow_diagram', False),
                result.get('confidence', 0.0),
                result.get('diagram_type', 'unknown')
            )
        except Exception as e:
            debug_print(f"Flow detection failed: {e}")
            return False, 0.0, 'unknown'
    
    def extract_flow_elements(self, image_path: str) -> Dict[str, Any]:
        """
        Extract flow chart elements using vision model.
        
        Returns:
            Structured extraction of flow elements
        """
        prompt = """Analyze this flow diagram image and extract ALL elements and connections.
        
        CRITICAL: List each element ONLY ONCE. Do not repeat elements even if there are loops.
        
        Extract:
        1. PROCESS ELEMENTS (rectangles):
           - Each process step or activity
           - Give each a unique identifier (P1, P2, etc.)
           - Include the exact text inside
           
        2. DECISION POINTS (diamonds):
           - Each decision or condition
           - Give each a unique identifier (D1, D2, etc.)
           - Include the question or condition text
           
        3. START/END POINTS (ovals/circles):
           - Start points (where flow begins)
           - End points (where flow terminates)
           - Give identifiers (S1 for start, E1 for end)
           
        4. DATA ELEMENTS (parallelograms, cylinders):
           - Data inputs/outputs
           - Databases or files
           - Give identifiers (DATA1, DATA2, etc.)
           
        5. CONNECTIONS (arrows):
           - From which element to which element
           - Label on the arrow (especially for decision branches like Yes/No)
           - Direction of flow
           
        6. SWIM LANES (if present):
           - Lane names/roles
           - Which elements are in which lane
           
        Return JSON:
        {
            "extraction_successful": true,
            "elements": [
                {
                    "id": "unique_id",
                    "type": "process|decision|start|end|data",
                    "shape": "rectangle|diamond|oval|parallelogram",
                    "text": "exact text in element",
                    "position": "top|middle|bottom, left|center|right",
                    "lane": "lane name if in swim lane"
                }
            ],
            "connections": [
                {
                    "from": "element_id",
                    "to": "element_id",
                    "label": "text on arrow (e.g., Yes, No)",
                    "type": "normal|conditional"
                }
            ],
            "swim_lanes": [
                {
                    "name": "lane name",
                    "elements": ["element_ids in this lane"]
                }
            ],
            "flow_direction": "top-to-bottom|left-to-right|complex"
        }
        
        IMPORTANT: Each element appears ONCE. Loops are represented as connections, not duplicate elements."""
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            result = self._parse_json_response(response)
            
            # Clean and validate extraction
            cleaned = self._clean_extraction(result)
            return cleaned
            
        except Exception as e:
            debug_print(f"Flow element extraction failed: {e}")
            return self._error_extraction(str(e))
    
    def generate_mermaid(self, extraction: Dict[str, Any]) -> str:
        """
        Generate Mermaid diagram from extracted flow elements.
        
        Args:
            extraction: Extracted flow elements
            
        Returns:
            Valid Mermaid flowchart code
        """
        if not extraction.get('extraction_successful'):
            return self._error_mermaid()
        
        elements = extraction.get('elements', [])
        connections = extraction.get('connections', [])
        swim_lanes = extraction.get('swim_lanes', [])
        direction = extraction.get('flow_direction', 'top-to-bottom')
        
        # Determine flow direction
        mermaid_dir = 'TD'  # Top Down default
        if 'left' in direction.lower():
            mermaid_dir = 'LR'
        elif 'bottom' in direction.lower():
            mermaid_dir = 'BT'
        elif 'right' in direction.lower():
            mermaid_dir = 'RL'
        
        # Start building Mermaid
        lines = [f"flowchart {mermaid_dir}"]
        
        # Add swim lanes as subgraphs if present
        if swim_lanes:
            for lane in swim_lanes:
                lane_name = self._sanitize_id(lane.get('name', 'Lane'))
                lines.append(f"    subgraph {lane_name}[\"{lane.get('name', 'Lane')}\"]")
                
                # Add elements in this lane
                for elem_id in lane.get('elements', []):
                    elem = next((e for e in elements if e['id'] == elem_id), None)
                    if elem:
                        lines.append(f"        {self._format_mermaid_element(elem)}")
                
                lines.append("    end")
        
        # Add elements not in swim lanes
        if swim_lanes:
            lane_elements = set()
            for lane in swim_lanes:
                lane_elements.update(lane.get('elements', []))
            
            for elem in elements:
                if elem['id'] not in lane_elements:
                    lines.append(f"    {self._format_mermaid_element(elem)}")
        else:
            # No swim lanes, add all elements
            for elem in elements:
                lines.append(f"    {self._format_mermaid_element(elem)}")
        
        # Add connections
        for conn in connections:
            lines.append(f"    {self._format_mermaid_connection(conn)}")
        
        # Join and fix syntax
        mermaid_code = '\n'.join(lines)
        
        # Apply syntax fixes
        is_valid, fixed_code, errors = self.mermaid_fixer.fix(mermaid_code)
        
        if is_valid:
            return fixed_code
        else:
            debug_print(f"Mermaid syntax issues: {errors}")
            return mermaid_code  # Return original if fixing failed
    
    def extract_context(self, image_path: str, mermaid_code: str, 
                       extraction: Dict[str, Any],
                       surrounding_text: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Extract context and meaning from the flow diagram.
        
        Args:
            image_path: Path to flow diagram image
            mermaid_code: Generated Mermaid code
            extraction: Extracted elements
            surrounding_text: Optional surrounding document text
            
        Returns:
            Context analysis of the flow diagram
        """
        # Build context prompt
        before_text = surrounding_text.get('before', '') if surrounding_text else ''
        after_text = surrounding_text.get('after', '') if surrounding_text else ''
        
        prompt = f"""Analyze this flow diagram and provide comprehensive context.
        
        Document context before diagram: {before_text[:500]}
        Document context after diagram: {after_text[:500]}
        
        Extracted elements: {json.dumps(extraction.get('elements', []), indent=2)}
        Connections: {json.dumps(extraction.get('connections', []), indent=2)}
        
        Analyze and provide:
        1. PURPOSE: What is the main purpose of this flow/process?
        2. SCOPE: What system/department/area does this cover?
        3. KEY STEPS: What are the critical process steps?
        4. DECISION POINTS: What are the key decisions and their criteria?
        5. INPUTS/OUTPUTS: What goes in and what comes out?
        6. BOTTLENECKS: Identify potential bottlenecks or delays
        7. OPTIMIZATION: Suggest improvements or optimizations
        8. COMPLIANCE: Any regulatory or compliance checkpoints?
        9. INTEGRATION: How does this integrate with other processes?
        10. METRICS: What metrics could measure this process?
        
        Return JSON:
        {{
            "purpose": "main purpose of the flow",
            "scope": "what area/system this covers",
            "key_steps": ["critical step 1", "critical step 2"],
            "decision_criteria": {{"decision1": "criteria", "decision2": "criteria"}},
            "inputs": ["input1", "input2"],
            "outputs": ["output1", "output2"],
            "bottlenecks": ["potential bottleneck 1"],
            "optimizations": ["suggestion 1", "suggestion 2"],
            "compliance_points": ["checkpoint1"],
            "integrations": ["system1", "system2"],
            "metrics": ["metric1", "metric2"],
            "summary": "comprehensive summary of the flow"
        }}"""
        
        try:
            response = transcribe_image(image_path, self.model, prompt)
            context = self._parse_json_response(response)
            
            # Add analysis of flow complexity
            context['complexity_analysis'] = self._analyze_complexity(extraction)
            
            return context
            
        except Exception as e:
            debug_print(f"Context extraction failed: {e}")
            return self._basic_context_analysis(extraction)
    
    def process_complete(self, image_path: str, 
                        surrounding_text: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Complete flow diagram processing pipeline.
        
        Args:
            image_path: Path to flow diagram image
            surrounding_text: Optional surrounding document text
            
        Returns:
            Complete processing result with detection, extraction, Mermaid, and context
        """
        # Step 1: Detect flow diagram
        is_flow, confidence, diagram_type = self.detect_flow_diagram(image_path)
        
        if not is_flow or confidence < 0.5:
            return {
                'is_flow_diagram': False,
                'confidence': confidence,
                'message': 'Not detected as flow diagram'
            }
        
        # Step 2: Extract elements
        extraction = self.extract_flow_elements(image_path)
        
        # Step 3: Generate Mermaid
        mermaid_code = self.generate_mermaid(extraction)
        
        # Step 4: Extract context
        context = self.extract_context(image_path, mermaid_code, extraction, surrounding_text)
        
        # Step 5: Format output
        formatted_output = self._format_output(
            diagram_type, extraction, mermaid_code, context
        )
        
        return {
            'is_flow_diagram': True,
            'confidence': confidence,
            'diagram_type': diagram_type,
            'extraction': extraction,
            'mermaid': mermaid_code,
            'context': context,
            'formatted_output': formatted_output
        }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from model response."""
        try:
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '{' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]
            else:
                return {}
            
            return json.loads(json_str)
        except Exception as e:
            debug_print(f"JSON parsing failed: {e}")
            return {}
    
    def _clean_extraction(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and deduplicate extraction."""
        if not extraction.get('extraction_successful'):
            return extraction
        
        # Deduplicate elements
        seen_texts = set()
        unique_elements = []
        id_mapping = {}
        
        for elem in extraction.get('elements', []):
            elem_text = elem.get('text', '').strip()
            elem_type = elem.get('type', '')
            
            # Create unique key
            elem_key = f"{elem_type}:{elem_text}"
            
            if elem_key not in seen_texts:
                seen_texts.add(elem_key)
                # Ensure unique ID
                if not elem.get('id'):
                    elem['id'] = f"{elem_type[:1].upper()}{self.element_counter}"
                    self.element_counter += 1
                unique_elements.append(elem)
                id_mapping[elem.get('id')] = elem['id']
        
        extraction['elements'] = unique_elements
        
        # Update connections with new IDs
        for conn in extraction.get('connections', []):
            if conn.get('from') in id_mapping:
                conn['from'] = id_mapping[conn['from']]
            if conn.get('to') in id_mapping:
                conn['to'] = id_mapping[conn['to']]
        
        return extraction
    
    def _sanitize_id(self, text: str) -> str:
        """Sanitize text for use as Mermaid ID."""
        # Remove special characters
        sanitized = re.sub(r'[^A-Za-z0-9_]', '_', str(text))
        sanitized = re.sub(r'_+', '_', sanitized).strip('_')
        
        # Ensure starts with letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'ID_' + sanitized
        
        return sanitized or 'Unknown'
    
    def _format_mermaid_element(self, elem: Dict[str, Any]) -> str:
        """Format element for Mermaid."""
        elem_id = self._sanitize_id(elem.get('id', 'unknown'))
        text = elem.get('text', 'Unknown').replace('"', "'")
        elem_type = elem.get('type', 'process')
        
        # Format based on type
        if elem_type == 'start' or elem_type == 'end':
            return f'{elem_id}(["{text}"])'
        elif elem_type == 'decision':
            return f'{elem_id}{{"{text}"}}'
        elif elem_type == 'data':
            return f'{elem_id}[\\"{text}"\\]'
        else:  # process
            return f'{elem_id}["{text}"]'
    
    def _format_mermaid_connection(self, conn: Dict[str, Any]) -> str:
        """Format connection for Mermaid."""
        from_id = self._sanitize_id(conn.get('from', 'unknown'))
        to_id = self._sanitize_id(conn.get('to', 'unknown'))
        label = conn.get('label', '')
        
        if label:
            return f'{from_id} -->|{label}| {to_id}'
        else:
            return f'{from_id} --> {to_id}'
    
    def _analyze_complexity(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze flow complexity."""
        elements = extraction.get('elements', [])
        connections = extraction.get('connections', [])
        
        # Count element types
        type_counts = {}
        for elem in elements:
            elem_type = elem.get('type', 'unknown')
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        # Detect loops (connections that go backwards)
        loops = []
        elem_positions = {e['id']: i for i, e in enumerate(elements)}
        
        for conn in connections:
            from_pos = elem_positions.get(conn['from'], -1)
            to_pos = elem_positions.get(conn['to'], -1)
            if to_pos < from_pos and to_pos >= 0:
                loops.append(conn)
        
        # Calculate complexity score
        decision_count = type_counts.get('decision', 0)
        total_elements = len(elements)
        loop_count = len(loops)
        
        complexity_score = decision_count * 2 + total_elements + loop_count * 3
        
        if complexity_score > 30:
            complexity = 'high'
        elif complexity_score > 15:
            complexity = 'medium'
        else:
            complexity = 'low'
        
        return {
            'complexity_level': complexity,
            'complexity_score': complexity_score,
            'element_counts': type_counts,
            'total_elements': total_elements,
            'total_connections': len(connections),
            'decision_points': decision_count,
            'detected_loops': loop_count,
            'has_swim_lanes': len(extraction.get('swim_lanes', [])) > 0
        }
    
    def _basic_context_analysis(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic context analysis as fallback."""
        elements = extraction.get('elements', [])
        connections = extraction.get('connections', [])
        
        # Extract key information
        starts = [e for e in elements if e.get('type') == 'start']
        ends = [e for e in elements if e.get('type') == 'end']
        decisions = [e for e in elements if e.get('type') == 'decision']
        processes = [e for e in elements if e.get('type') == 'process']
        
        return {
            'purpose': 'Process flow diagram',
            'key_steps': [p.get('text', '') for p in processes[:5]],
            'decision_criteria': {d.get('text', ''): 'Decision point' for d in decisions},
            'inputs': [s.get('text', 'Start') for s in starts],
            'outputs': [e.get('text', 'End') for e in ends],
            'summary': f"Flow with {len(processes)} process steps and {len(decisions)} decision points"
        }
    
    def _format_output(self, diagram_type: str, extraction: Dict[str, Any],
                      mermaid_code: str, context: Dict[str, Any]) -> str:
        """Format the complete output."""
        output = []
        
        # Title
        output.append(f"## {diagram_type.replace('_', ' ').title()} Diagram\n")
        
        # Purpose and summary
        if context.get('summary'):
            output.append(f"**Summary**: {context['summary']}\n")
        
        # Key information
        if context.get('key_steps'):
            output.append("### Key Process Steps")
            for i, step in enumerate(context['key_steps'][:10], 1):
                output.append(f"{i}. {step}")
            output.append("")
        
        # Decision points
        if context.get('decision_criteria'):
            output.append("### Decision Points")
            for decision, criteria in list(context['decision_criteria'].items())[:5]:
                output.append(f"- **{decision}**: {criteria}")
            output.append("")
        
        # Mermaid diagram
        output.append("### Flow Diagram")
        output.append("```mermaid")
        output.append(mermaid_code)
        output.append("```\n")
        
        # Analysis
        if 'complexity_analysis' in context:
            analysis = context['complexity_analysis']
            output.append("### Complexity Analysis")
            output.append(f"- **Complexity Level**: {analysis['complexity_level']}")
            output.append(f"- **Total Elements**: {analysis['total_elements']}")
            output.append(f"- **Decision Points**: {analysis['decision_points']}")
            if analysis['detected_loops'] > 0:
                output.append(f"- **Loops Detected**: {analysis['detected_loops']}")
            output.append("")
        
        # Optimizations
        if context.get('optimizations'):
            output.append("### Optimization Opportunities")
            for opt in context['optimizations'][:3]:
                output.append(f"- {opt}")
            output.append("")
        
        return '\n'.join(output)
    
    def _error_extraction(self, error: str) -> Dict[str, Any]:
        """Create error extraction response."""
        return {
            'extraction_successful': False,
            'error': error,
            'elements': [],
            'connections': [],
            'swim_lanes': []
        }
    
    def _error_mermaid(self) -> str:
        """Generate error Mermaid diagram."""
        return """flowchart TD
    Error[Flow Extraction Failed]
    style Error fill:#f99,stroke:#f00,stroke-width:2px"""