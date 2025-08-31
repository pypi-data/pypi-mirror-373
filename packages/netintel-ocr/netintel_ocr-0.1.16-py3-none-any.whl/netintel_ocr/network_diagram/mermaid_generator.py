"""Mermaid diagram generation from network components."""

import json
import requests
from typing import Dict, Any, List, Optional
from ..constants import OLLAMA_BASE_URL
from .prompts import MERMAID_GENERATION_PROMPT
from .icons import COMPONENT_ICONS, CONNECTION_STYLES, MERMAID_STYLES


class MermaidGenerator:
    """Generates Mermaid diagrams from extracted network components."""
    
    def __init__(self, model: str = "nanonets-ocr-s:latest", use_icons: bool = False):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
        self.use_icons = use_icons
    
    def generate(self, extraction: Dict[str, Any], use_llm: bool = True) -> str:
        """
        Generate Mermaid diagram from extracted components.
        
        Args:
            extraction: Extracted components and connections
            use_llm: Whether to use LLM for generation (vs rule-based)
            
        Returns:
            Mermaid diagram code
        """
        if not extraction.get("extraction_successful"):
            return self._generate_error_diagram(extraction.get("error", "Extraction failed"))
        
        if use_llm:
            return self._generate_with_llm(extraction)
        else:
            return self._generate_rule_based(extraction)
    
    def _generate_with_llm(self, extraction: Dict[str, Any]) -> str:
        """
        Generate Mermaid diagram using LLM.
        
        Args:
            extraction: Extracted components and connections
            
        Returns:
            Mermaid diagram code
        """
        try:
            # Format the prompt with extraction data
            prompt = MERMAID_GENERATION_PROMPT.format(
                components=json.dumps(extraction.get("components", [])),
                connections=json.dumps(extraction.get("connections", [])),
                zones=json.dumps(extraction.get("zones", []))
            )
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            # Make the API call
            response = requests.post(f"{self.base_url}/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                mermaid_code = result.get("response", "")
                
                # Clean up the response - remove markdown formatting
                mermaid_code = mermaid_code.strip()
                
                # Remove markdown code blocks if present
                if "```mermaid" in mermaid_code:
                    # Extract from mermaid code block
                    start = mermaid_code.find("```mermaid") + 10
                    end = mermaid_code.find("```", start)
                    if end > start:
                        mermaid_code = mermaid_code[start:end].strip()
                elif "```" in mermaid_code:
                    # Extract from generic code block
                    lines = mermaid_code.split("\n")
                    in_code = False
                    code_lines = []
                    for line in lines:
                        if line.strip().startswith("```"):
                            in_code = not in_code
                            continue
                        if in_code:
                            code_lines.append(line)
                    if code_lines:
                        mermaid_code = "\n".join(code_lines)
                
                # Clean up invalid syntax
                mermaid_code = self._clean_mermaid_syntax(mermaid_code)
                
                # Ensure it starts with graph directive
                if not mermaid_code.strip().startswith(("graph", "flowchart", "stateDiagram")):
                    # Try to find the start of the diagram
                    for line in mermaid_code.split("\n"):
                        if line.strip().startswith(("graph", "flowchart", "stateDiagram")):
                            idx = mermaid_code.find(line)
                            mermaid_code = mermaid_code[idx:]
                            break
                
                return mermaid_code
            else:
                return self._generate_rule_based(extraction)
                
        except Exception as e:
            return self._generate_rule_based(extraction)
    
    def _generate_rule_based(self, extraction: Dict[str, Any]) -> str:
        """
        Generate Mermaid diagram using rule-based approach.
        
        Args:
            extraction: Extracted components and connections
            
        Returns:
            Mermaid diagram code
        """
        lines = []
        lines.append("graph TB")
        lines.append("    %% Network Diagram")
        
        components = extraction.get("components", [])
        connections = extraction.get("connections", [])
        zones = extraction.get("zones", [])
        
        # Group components by zone
        zones_dict = {}
        for comp in components:
            zone = comp.get("zone", "default")
            if zone not in zones_dict:
                zones_dict[zone] = []
            zones_dict[zone].append(comp)
        
        # Generate subgraphs for zones
        if len(zones_dict) > 1 or (len(zones_dict) == 1 and "default" not in zones_dict):
            for zone_name, zone_components in zones_dict.items():
                zone_info = next((z for z in zones if z.get("name") == zone_name), {})
                zone_label = zone_name
                if zone_info.get("subnet"):
                    zone_label += f" - {zone_info['subnet']}"
                
                lines.append(f'    subgraph {zone_name}["{zone_label}"]')
                for comp in zone_components:
                    lines.append(f"        {self._generate_node(comp)}")
                lines.append("    end")
        else:
            # No zones, just add components
            for comp in components:
                lines.append(f"    {self._generate_node(comp)}")
        
        # Add connections
        if connections:
            lines.append("    ")
            lines.append("    %% Connections")
            for conn in connections:
                lines.append(f"    {self._generate_connection(conn)}")
        
        # Add styling
        lines.append("    ")
        lines.append("    %% Styling")
        lines.extend(MERMAID_STYLES.strip().split("\n"))
        
        # Apply style classes
        if components:
            lines.append("    ")
            lines.append("    %% Apply styles")
            style_map = {}
            for comp in components:
                comp_type = comp.get("type", "unknown")
                if comp_type in COMPONENT_ICONS:
                    style_class = COMPONENT_ICONS[comp_type]["style_class"]
                    if style_class not in style_map:
                        style_map[style_class] = []
                    style_map[style_class].append(comp["id"])
            
            for style_class, comp_ids in style_map.items():
                lines.append(f"    class {','.join(comp_ids)} {style_class}")
        
        return "\n".join(lines)
    
    def _generate_node(self, component: Dict[str, Any]) -> str:
        """
        Generate node definition for a component.
        
        Args:
            component: Component data
            
        Returns:
            Mermaid node definition
        """
        comp_id = component.get("id", "unknown")
        comp_type = component.get("type", "unknown")
        label = component.get("label", comp_id)
        
        # Add IP info to label if available
        if component.get("ip_info"):
            label += f"<br/>{component['ip_info']}"
        
        # Add icon if enabled
        if self.use_icons and comp_type in COMPONENT_ICONS:
            icon = COMPONENT_ICONS[comp_type]["icon"]
            label = f"{icon} {label}"
        
        # Get shape based on component type
        if comp_type in COMPONENT_ICONS:
            shape = COMPONENT_ICONS[comp_type]["mermaid_shape"]
            node = shape.format(label=label)
        else:
            node = f"[{label}]"  # Default rectangle
        
        return f"{comp_id}{node}"
    
    def _generate_connection(self, connection: Dict[str, Any]) -> str:
        """
        Generate connection definition.
        
        Args:
            connection: Connection data
            
        Returns:
            Mermaid connection definition
        """
        from_id = connection.get("from", "unknown")
        to_id = connection.get("to", "unknown")
        conn_type = connection.get("type", "ethernet")
        label = connection.get("label", "")
        bidirectional = connection.get("bidirectional", True)
        
        # Get connection style
        if conn_type in CONNECTION_STYLES:
            style = CONNECTION_STYLES[conn_type]["syntax"]
            if label:
                label_format = CONNECTION_STYLES[conn_type]["label_format"]
                label = label_format.format(label=label)
        else:
            style = "---"  # Default solid line
            if label:
                label = f"|{label}|"
        
        # Handle directionality
        if not bidirectional and conn_type == "data_flow":
            style = "-->"
        
        if label:
            return f"{from_id} {style}{label} {to_id}"
        else:
            return f"{from_id} {style} {to_id}"
    
    def _generate_error_diagram(self, error: str) -> str:
        """
        Generate an error diagram.
        
        Args:
            error: Error message
            
        Returns:
            Mermaid diagram showing error
        """
        return f"""graph TB
    Error[Network Diagram Extraction Failed]
    Reason["{error}"]
    Error --> Reason
    
    classDef error fill:#ff9999,stroke:#ff0000,stroke-width:2px
    class Error,Reason error"""
    
    def _clean_mermaid_syntax(self, mermaid_code: str) -> str:
        """
        Clean up invalid Mermaid syntax from LLM output.
        
        Args:
            mermaid_code: Raw Mermaid code from LLM
            
        Returns:
            Cleaned Mermaid code
        """
        lines = mermaid_code.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Skip C-style comments
            if line.strip().startswith("//"):
                continue
            
            # Remove inline comments
            if "//" in line:
                line = line[:line.index("//")].rstrip()
            
            # Skip lines with only curly braces
            if line.strip() in ["{", "}"]:
                continue
            
            # Fix graph declaration with curly braces
            if line.strip().startswith("graph") and "{" in line:
                line = line.replace("{", "").strip()
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Convert comment-style definitions to actual Mermaid syntax
            # Example: // NodeA (type) -> NodeB (type) [connection]
            if "->" in line or "--" in line:
                # Extract node and connection info
                parts = line.strip()
                if parts:
                    cleaned_lines.append(parts)
            elif line.strip():
                cleaned_lines.append(line)
        
        # If we removed everything except the graph declaration, use rule-based generation
        if len(cleaned_lines) <= 1:
            return "graph TB\n    %% Invalid syntax detected, using fallback"
        
        return "\n".join(cleaned_lines)
    
    def wrap_in_markdown(self, mermaid_code: str) -> str:
        """
        Wrap Mermaid code in markdown code block.
        
        Args:
            mermaid_code: Mermaid diagram code
            
        Returns:
            Markdown-wrapped Mermaid code
        """
        return f"```mermaid\n{mermaid_code}\n```"