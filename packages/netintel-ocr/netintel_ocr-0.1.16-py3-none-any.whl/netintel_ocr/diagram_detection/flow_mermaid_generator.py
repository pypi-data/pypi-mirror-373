"""Flow diagram Mermaid generator."""

import json
from typing import Dict, Any, List, Optional
from ..ollama import transcribe_image
from ..output_utils import debug_print


class FlowMermaidGenerator:
    """Generates Mermaid.js code for flow diagrams."""
    
    def __init__(self, model: str = "NetIntelOCR-7B-0925"):
        """
        Initialize the flow Mermaid generator.
        
        Args:
            model: The model to use for generation
        """
        self.model = model
    
    def generate(self, extraction: Dict[str, Any], use_llm: bool = True, 
                custom_prompt: Optional[str] = None) -> str:
        """
        Generate Mermaid code for flow diagram.
        
        Args:
            extraction: Extracted flow elements
            use_llm: Whether to use LLM for generation
            custom_prompt: Optional custom prompt
            
        Returns:
            Mermaid.js flowchart code
        """
        if not extraction.get('extraction_successful'):
            return self._generate_error_diagram()
        
        if use_llm and extraction.get('elements'):
            # Try LLM generation first
            try:
                return self._generate_with_llm(extraction, custom_prompt)
            except Exception as e:
                debug_print(f"LLM generation failed, using rule-based: {e}")
        
        # Fallback to rule-based generation
        return self._generate_with_rules(extraction)
    
    def _generate_with_llm(self, extraction: Dict[str, Any], 
                          custom_prompt: Optional[str] = None) -> str:
        """Generate Mermaid using LLM."""
        prompt = custom_prompt or self._get_generation_prompt(extraction)
        
        # Create a simplified version of extraction for the prompt
        simplified = {
            'elements': extraction.get('elements', []),
            'flows': extraction.get('flows', []),
            'swim_lanes': extraction.get('swim_lanes', [])
        }
        
        full_prompt = f"{prompt}\n\nExtracted elements:\n{json.dumps(simplified, indent=2)}"
        
        # Note: This would need actual image path in real implementation
        response = self._call_llm_for_generation(full_prompt)
        
        # Extract Mermaid code from response
        if '```mermaid' in response:
            mermaid = response.split('```mermaid')[1].split('```')[0].strip()
        elif 'flowchart' in response.lower():
            # Try to extract flowchart definition
            lines = response.split('\n')
            mermaid_lines = []
            in_diagram = False
            
            for line in lines:
                if 'flowchart' in line.lower():
                    in_diagram = True
                if in_diagram:
                    mermaid_lines.append(line)
            
            mermaid = '\n'.join(mermaid_lines)
        else:
            mermaid = response
        
        return mermaid
    
    def _generate_with_rules(self, extraction: Dict[str, Any]) -> str:
        """Generate Mermaid using rules."""
        elements = extraction.get('elements', [])
        flows = extraction.get('flows', [])
        swim_lanes = extraction.get('swim_lanes', [])
        
        if not elements:
            return self._generate_error_diagram()
        
        # Start flowchart
        mermaid_lines = ["flowchart TD"]
        
        # Add swim lanes if present
        if swim_lanes:
            mermaid_lines.append("    %% Swim lanes present but not rendered in basic Mermaid")
            for lane in swim_lanes:
                mermaid_lines.append(f"    %% Lane: {lane.get('label', 'Unknown')}")
        
        # Add elements
        for element in elements:
            elem_id = self._sanitize_id(element.get('id', f"elem_{elements.index(element)}"))
            label = element.get('label', 'Unnamed')
            elem_type = element.get('type', 'process')
            
            # Format based on type
            if elem_type == 'start' or elem_type == 'end':
                line = f"    {elem_id}([{label}])"
            elif elem_type == 'decision':
                line = f"    {elem_id}{{{label}}}"
            elif elem_type == 'data':
                line = f"    {elem_id}[({label})]"
            elif elem_type == 'process':
                line = f"    {elem_id}[{label}]"
            else:
                line = f"    {elem_id}[{label}]"
            
            mermaid_lines.append(line)
        
        # Add flows
        for flow in flows:
            from_id = self._sanitize_id(flow.get('from', 'unknown'))
            to_id = self._sanitize_id(flow.get('to', 'unknown'))
            label = flow.get('label', '')
            
            if label:
                line = f"    {from_id} -->|{label}| {to_id}"
            else:
                line = f"    {from_id} --> {to_id}"
            
            mermaid_lines.append(line)
        
        return '\n'.join(mermaid_lines)
    
    def _get_generation_prompt(self, extraction: Dict[str, Any]) -> str:
        """Get the prompt for LLM generation."""
        return """Convert these flow diagram elements into valid Mermaid.js flowchart syntax.
        
        Rules:
        1. Use 'flowchart TD' or 'flowchart LR' as appropriate
        2. Element shapes:
           - Start/End: Use circles ([Start])
           - Process: Use rectangles [Process]
           - Decision: Use diamonds {Decision}
           - Data: Use parallelograms [(Database)]
           - Document: Use special shape [/Document/]
        3. Connections:
           - Use --> for flow arrows
           - Use -->|label| for labeled flows
           - Decision outcomes should be labeled (Yes/No, True/False)
        4. Keep IDs simple and valid (alphanumeric, no spaces)
        5. Make the diagram readable and well-organized
        
        Generate clean, valid Mermaid code that accurately represents the flow."""
    
    def _sanitize_id(self, id_str: str) -> str:
        """Sanitize ID for Mermaid compatibility."""
        # Remove special characters and spaces
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in str(id_str))
        
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'id_' + sanitized
        
        return sanitized or 'unknown'
    
    def _generate_error_diagram(self) -> str:
        """Generate error diagram."""
        return """flowchart TD
    Error[Unable to extract flow elements]
    style Error fill:#f99,stroke:#f66,stroke-width:2px"""
    
    def _call_llm_for_generation(self, prompt: str) -> str:
        """Call LLM for Mermaid generation (placeholder)."""
        # In real implementation, this would call the actual LLM
        # For now, return a simple response
        return """flowchart TD
    Start([Start]) --> Process[Process]
    Process --> End([End])"""
    
    def optimize_layout(self, mermaid_code: str) -> str:
        """
        Optimize the layout of the generated Mermaid diagram.
        
        Args:
            mermaid_code: Initial Mermaid code
            
        Returns:
            Optimized Mermaid code
        """
        lines = mermaid_code.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Add styling for better visibility
            if 'flowchart' in line.lower():
                optimized_lines.append(line)
                # Add default styles
                optimized_lines.append("    %%{init: {'theme':'default'}}%%")
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)