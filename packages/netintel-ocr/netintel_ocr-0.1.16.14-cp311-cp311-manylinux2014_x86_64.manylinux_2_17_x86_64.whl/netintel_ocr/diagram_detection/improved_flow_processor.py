"""Improved flow diagram processor that generates meaningful output."""

import re
from typing import Dict, Any, List, Optional, Tuple
from .improved_flow_extractor import ImprovedFlowExtractor
from .flow_mermaid_generator import FlowMermaidGenerator
from ..output_utils import debug_print


class ImprovedFlowProcessor:
    """Process flow diagrams to generate meaningful, non-repetitive output."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """Initialize the improved flow processor."""
        self.model = model
        self.extractor = ImprovedFlowExtractor(model)
        self.mermaid_generator = FlowMermaidGenerator(model)
    
    def process_flow_diagram(self, image_path: str, 
                            surrounding_text: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a flow diagram and generate structured output.
        
        Args:
            image_path: Path to the flow diagram image
            surrounding_text: Optional dict with 'before' and 'after' text
            
        Returns:
            Structured flow diagram analysis
        """
        # Extract flow elements
        extraction = self.extractor.extract(image_path)
        
        if not extraction.get('extraction_successful'):
            return {
                'success': False,
                'error': extraction.get('error', 'Extraction failed'),
                'output': self._generate_error_output()
            }
        
        # Generate Mermaid diagram
        mermaid_code = self.mermaid_generator.generate(extraction, use_llm=False)
        
        # Generate structured output
        output = self._generate_structured_output(extraction, mermaid_code, surrounding_text)
        
        return {
            'success': True,
            'extraction': extraction,
            'mermaid': mermaid_code,
            'output': output
        }
    
    def _generate_structured_output(self, extraction: Dict[str, Any], 
                                   mermaid_code: str,
                                   surrounding_text: Optional[Dict[str, str]] = None) -> str:
        """Generate structured, meaningful output from extraction."""
        output_parts = []
        
        # Add title if detected from surrounding text
        if surrounding_text:
            title = self._extract_title(surrounding_text.get('before', ''))
            if title:
                output_parts.append(f"## {title}\n")
        
        # Add process summary
        if extraction.get('process_summary'):
            output_parts.append(f"**Process Overview**: {extraction['process_summary']}\n")
        elif extraction.get('clean_summary'):
            output_parts.append(f"**Process Overview**:\n{extraction['clean_summary']}\n")
        
        # Add analysis section
        analysis = extraction.get('analysis', {})
        if analysis:
            output_parts.append(self._format_analysis(analysis))
        
        # Add flow structure
        output_parts.append(self._format_flow_structure(extraction))
        
        # Add Mermaid diagram
        output_parts.append("### Flow Diagram\n")
        output_parts.append("```mermaid")
        output_parts.append(mermaid_code)
        output_parts.append("```\n")
        
        # Add detailed elements if not too many
        if len(extraction.get('elements', [])) <= 15:
            output_parts.append(self._format_detailed_elements(extraction))
        
        # Add loop information if present
        if extraction.get('loops'):
            output_parts.append(self._format_loops(extraction.get('loops', [])))
        
        return '\n'.join(output_parts)
    
    def _extract_title(self, before_text: str) -> Optional[str]:
        """Extract potential title from preceding text."""
        lines = before_text.split('\n')
        for line in reversed(lines[-5:]):  # Check last 5 lines
            line = line.strip()
            if line and len(line) < 100:  # Reasonable title length
                # Check if it looks like a title (starts with number or capital)
                if re.match(r'^[\d\.]+\s+[A-Z]', line) or line[0].isupper():
                    return line
        return None
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis section."""
        parts = ["### Flow Analysis\n"]
        
        parts.append(f"- **Total Elements**: {analysis.get('total_elements', 0)}")
        parts.append(f"- **Process Steps**: {analysis.get('process_steps', 0)}")
        parts.append(f"- **Decision Points**: {analysis.get('decision_points', 0)}")
        parts.append(f"- **Complexity**: {analysis.get('complexity', 'unknown')}")
        
        if analysis.get('has_loops'):
            parts.append(f"- **Loops Detected**: {analysis.get('loop_count', 0)}")
        
        parts.append("")
        return '\n'.join(parts)
    
    def _format_flow_structure(self, extraction: Dict[str, Any]) -> str:
        """Format the flow structure in a readable way."""
        parts = ["### Process Flow\n"]
        
        elements = extraction.get('elements', [])
        flows = extraction.get('flows', [])
        
        # Create element lookup
        element_lookup = {e['id']: e for e in elements}
        
        # Find start points
        start_ids = set()
        end_ids = set()
        all_targets = set(f['to'] for f in flows)
        all_sources = set(f['from'] for f in flows)
        
        for e in elements:
            if e['type'] == 'start' or e['id'] not in all_targets:
                start_ids.add(e['id'])
            if e['type'] == 'end' or e['id'] not in all_sources:
                end_ids.add(e['id'])
        
        # Generate flow description
        if start_ids:
            start_labels = [element_lookup.get(sid, {}).get('label', sid) 
                          for sid in list(start_ids)[:3]]
            parts.append(f"**Starts with**: {', '.join(start_labels)}")
        
        # List main process steps (non-decision)
        process_steps = [e for e in elements if e['type'] == 'process'][:10]
        if process_steps:
            parts.append("\n**Main Process Steps**:")
            for i, step in enumerate(process_steps, 1):
                label = step.get('label', 'Unnamed step')
                # Truncate long labels
                if len(label) > 80:
                    label = label[:77] + "..."
                parts.append(f"{i}. {label}")
        
        # List key decisions
        decisions = [e for e in elements if e['type'] == 'decision'][:5]
        if decisions:
            parts.append("\n**Key Decision Points**:")
            for decision in decisions:
                label = decision.get('label', 'Unnamed decision')
                if len(label) > 80:
                    label = label[:77] + "..."
                parts.append(f"- {label}")
                
                # Show decision outcomes
                outcomes = [f for f in flows if f['from'] == decision['id']]
                if outcomes:
                    for outcome in outcomes[:2]:  # Limit to 2 outcomes
                        outcome_label = outcome.get('label', '')
                        target = element_lookup.get(outcome['to'], {})
                        target_label = target.get('label', outcome['to'])
                        if outcome_label:
                            parts.append(f"  → {outcome_label}: {target_label[:50]}")
                        else:
                            parts.append(f"  → {target_label[:50]}")
        
        if end_ids:
            end_labels = [element_lookup.get(eid, {}).get('label', eid) 
                         for eid in list(end_ids)[:3]]
            parts.append(f"\n**Ends with**: {', '.join(end_labels)}")
        
        parts.append("")
        return '\n'.join(parts)
    
    def _format_detailed_elements(self, extraction: Dict[str, Any]) -> str:
        """Format detailed element list."""
        parts = ["### Detailed Elements\n"]
        
        elements = extraction.get('elements', [])
        
        # Group by type
        by_type = {}
        for elem in elements:
            elem_type = elem.get('type', 'unknown')
            if elem_type not in by_type:
                by_type[elem_type] = []
            by_type[elem_type].append(elem)
        
        type_names = {
            'start': 'Start Points',
            'end': 'End Points',
            'process': 'Process Steps',
            'decision': 'Decision Points',
            'data': 'Data Elements'
        }
        
        for elem_type, type_elements in by_type.items():
            if type_elements:
                type_name = type_names.get(elem_type, elem_type.title())
                parts.append(f"**{type_name}**:")
                for elem in type_elements:
                    label = elem.get('label', 'Unnamed')
                    if len(label) > 100:
                        label = label[:97] + "..."
                    parts.append(f"- {label}")
                parts.append("")
        
        return '\n'.join(parts)
    
    def _format_loops(self, loops: List[Dict]) -> str:
        """Format loop information."""
        parts = ["### Detected Loops\n"]
        
        for i, loop in enumerate(loops, 1):
            parts.append(f"**Loop {i}**:")
            parts.append(f"- From: {loop.get('from', 'unknown')}")
            parts.append(f"- To: {loop.get('to', 'unknown')}")
            if loop.get('condition'):
                parts.append(f"- Condition: {loop.get('condition')}")
            if loop.get('path'):
                path_str = ' → '.join(loop['path'][:5])
                if len(loop['path']) > 5:
                    path_str += " → ..."
                parts.append(f"- Path: {path_str}")
            parts.append("")
        
        return '\n'.join(parts)
    
    def _generate_error_output(self) -> str:
        """Generate error output."""
        return """### Flow Diagram Extraction Failed

Unable to extract flow diagram elements from the image.

This could be due to:
- Image quality issues
- Complex or non-standard diagram format
- Text-based diagram that needs different processing

Please try:
- Improving image quality
- Using a clearer diagram
- Checking if this is actually a flow diagram
"""