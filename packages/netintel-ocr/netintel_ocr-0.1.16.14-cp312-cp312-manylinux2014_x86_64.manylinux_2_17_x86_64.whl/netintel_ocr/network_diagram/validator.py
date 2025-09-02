"""Mermaid diagram validation module."""

import re
from typing import Dict, Any, List, Tuple


class MermaidValidator:
    """Validates Mermaid diagram syntax and structure."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, mermaid_code: str) -> Dict[str, Any]:
        """
        Validate Mermaid diagram syntax.
        
        Args:
            mermaid_code: Mermaid diagram code
            
        Returns:
            Validation results
        """
        self.errors = []
        self.warnings = []
        
        lines = mermaid_code.strip().split("\n")
        
        # Check basic structure
        if not lines:
            self.errors.append("Empty diagram")
            return self._get_results(False)
        
        # Check graph declaration
        if not self._validate_graph_declaration(lines[0]):
            self.errors.append("Invalid graph declaration. Should start with 'graph' followed by direction (TB, LR, etc.)")
        
        # Track nodes and connections
        nodes = set()
        connections = []
        subgraph_depth = 0
        
        for i, line in enumerate(lines[1:], start=2):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("%%"):
                continue
            
            # Check subgraph syntax
            if "subgraph" in line:
                if line.strip().startswith("subgraph"):
                    subgraph_depth += 1
                    if not self._validate_subgraph(line):
                        self.errors.append(f"Line {i}: Invalid subgraph declaration")
                elif line.strip() == "end":
                    subgraph_depth -= 1
                    if subgraph_depth < 0:
                        self.errors.append(f"Line {i}: Unexpected 'end' without matching subgraph")
            
            # Check node definitions
            elif self._is_node_definition(line):
                node_id = self._extract_node_id(line)
                if node_id:
                    nodes.add(node_id)
            
            # Check connections
            elif self._is_connection(line):
                conn = self._extract_connection(line)
                if conn:
                    connections.append(conn)
            
            # Check style definitions
            elif line.startswith("classDef") or line.startswith("class "):
                if not self._validate_style(line):
                    self.warnings.append(f"Line {i}: Potentially invalid style definition")
        
        # Check for unmatched subgraphs
        if subgraph_depth != 0:
            self.errors.append(f"Unmatched subgraph declarations (depth: {subgraph_depth})")
        
        # Validate connections reference existing nodes
        for conn in connections:
            if conn[0] not in nodes:
                self.warnings.append(f"Connection references undefined node: {conn[0]}")
            if conn[1] not in nodes:
                self.warnings.append(f"Connection references undefined node: {conn[1]}")
        
        # Check for isolated nodes
        connected_nodes = set()
        for conn in connections:
            connected_nodes.add(conn[0])
            connected_nodes.add(conn[1])
        
        isolated = nodes - connected_nodes
        if isolated and len(nodes) > 1:
            self.warnings.append(f"Isolated nodes found: {', '.join(isolated)}")
        
        return self._get_results(len(self.errors) == 0)
    
    def _validate_graph_declaration(self, line: str) -> bool:
        """Validate graph declaration line."""
        pattern = r'^graph\s+(TB|BT|LR|RL|TD)(\s|$)'
        return bool(re.match(pattern, line.strip()))
    
    def _validate_subgraph(self, line: str) -> bool:
        """Validate subgraph declaration."""
        pattern = r'^subgraph\s+\w+(\[.*\])?$'
        return bool(re.match(pattern, line.strip()))
    
    def _is_node_definition(self, line: str) -> bool:
        """Check if line defines a node."""
        # Look for patterns like: ID[label], ID(label), ID{label}, etc.
        patterns = [
            r'^\w+\[.*\]',      # Rectangle
            r'^\w+\(.*\)',      # Round edges
            r'^\w+\{.*\}',      # Rhombus
            r'^\w+\[\(.*\)\]',  # Stadium
            r'^\w+\[\[.*\]\]',  # Subroutine
            r'^\w+\[\(.*\)\]',  # Cylindrical
            r'^\w+\(\(.*\)\)',  # Circle
            r'^\w+\>.*\]',      # Asymmetric
            r'^\w+\{.*\}',      # Rhombus
            r'^\w+\[\/.*\/\]',  # Parallelogram
            r'^\w+\[\\.*\\\]',  # Parallelogram alt
            r'^\w+\(\(\(.*\)\)\)',  # Double circle
        ]
        return any(re.match(pattern, line.strip()) for pattern in patterns)
    
    def _extract_node_id(self, line: str) -> str:
        """Extract node ID from definition."""
        match = re.match(r'^(\w+)', line.strip())
        return match.group(1) if match else None
    
    def _is_connection(self, line: str) -> bool:
        """Check if line defines a connection."""
        # Look for connection patterns: -->, ---, -.-, ==>, ===
        patterns = [
            r'\s+(-->|---|==>|===|-.->|-.-|--o|--x|o--|x--)',
            r'\s+(-..-|<-->|<==)',
        ]
        return any(re.search(pattern, line) for pattern in patterns)
    
    def _extract_connection(self, line: str) -> Tuple[str, str]:
        """Extract source and destination from connection."""
        # Match various connection patterns
        pattern = r'^(\w+)\s+(?:-->|---|==>|===|-.->|-.-|--o|--x|o--|x--|-..-|<-->|<==)(?:\|.*\|)?\s+(\w+)'
        match = re.match(pattern, line.strip())
        if match:
            return (match.group(1), match.group(2))
        return None
    
    def _validate_style(self, line: str) -> bool:
        """Validate style definition."""
        if line.startswith("classDef"):
            return bool(re.match(r'^classDef\s+\w+\s+.+', line))
        elif line.startswith("class "):
            return bool(re.match(r'^class\s+[\w,]+\s+\w+', line))
        return False
    
    def _get_results(self, is_valid: bool) -> Dict[str, Any]:
        """Get validation results."""
        return {
            "valid": is_valid,
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
    
    def fix_common_issues(self, mermaid_code: str) -> str:
        """
        Attempt to fix common Mermaid syntax issues.
        
        Args:
            mermaid_code: Mermaid diagram code
            
        Returns:
            Fixed Mermaid code
        """
        lines = mermaid_code.strip().split("\n")
        fixed_lines = []
        in_comment_block = False
        node_id_mapping = {}  # Track node ID replacements
        node_counter = {}  # Track duplicate node names
        
        for line in lines:
            # Remove C-style comments
            if "//" in line:
                # Check if it's actually a comment or part of a URL/label
                comment_idx = line.find("//")
                # If it's at the start or after whitespace, it's likely a comment
                if comment_idx == 0 or (comment_idx > 0 and line[comment_idx-1].isspace()):
                    line = line[:comment_idx].rstrip()
                    if not line:
                        continue
            
            # Remove curly braces on graph declaration
            if line.strip().startswith("graph") and "{" in line:
                line = line.replace("{", "").strip()
            
            # Skip standalone curly braces
            if line.strip() in ["{", "}"]:
                continue
            
            # Fix missing graph declaration
            if not fixed_lines and not line.strip().startswith("graph"):
                fixed_lines.append("graph TB")
            
            # Fix subgraph syntax (subgraph_NAME should be subgraph NAME)
            if line.strip().startswith("subgraph_"):
                line = line.replace("subgraph_", "subgraph ")
            
            # Fix node definitions with spaces in IDs
            # Match patterns like: NodeName With Spaces[label] or NodeName With Spaces([label])
            node_def_pattern = r'^\s*([A-Za-z][A-Za-z0-9\s\-]+)(\[|\(|\{|\[\[|\(\(|\>)'
            match = re.match(node_def_pattern, line)
            if match and not line.strip().startswith(('subgraph', 'graph', 'class', 'classDef', '%%')):
                original_id = match.group(1).strip()
                if ' ' in original_id or '-' in original_id:
                    # Create a valid node ID
                    safe_id = re.sub(r'[\s\-]+', '_', original_id)
                    safe_id = re.sub(r'[^A-Za-z0-9_]', '', safe_id)
                    
                    # Handle duplicates by adding counter
                    base_id = safe_id
                    if safe_id in node_counter:
                        node_counter[safe_id] += 1
                        safe_id = f"{base_id}{node_counter[safe_id]}"
                    else:
                        node_counter[safe_id] = 1
                    
                    # Store mapping for fixing connections later
                    node_id_mapping[original_id] = safe_id
                    
                    # Replace in line
                    line = line.replace(original_id, safe_id, 1)
            
            # Fix parentheses in node labels - they need to be quoted
            # Handle different node shapes with parentheses in labels
            
            # Pattern 1: Round edges - NodeID([Label with (parentheses)])
            round_pattern = r'(\w+)\(\[([^\[\]]+)\]\)'
            match = re.search(round_pattern, line)
            if match:
                node_id = match.group(1)
                label = match.group(2)
                # If label has parentheses, quote it
                if '(' in label and ')' in label and not (label.startswith('"') or label.startswith("'")):
                    line = re.sub(round_pattern, f'{node_id}(["{label}"])', line, count=1)
            
            # Pattern 2: Rectangle - NodeID[Label with (parentheses)]
            elif '[' in line and ']' in line and '(' in line:
                rect_pattern = r'(\w+)\[([^\[\]]+)\]'
                match = re.search(rect_pattern, line)
                if match:
                    node_id = match.group(1)
                    label = match.group(2)
                    # If label has parentheses and isn't quoted, quote it
                    if '(' in label and not (label.startswith('"') or label.startswith("'")):
                        line = re.sub(rect_pattern, f'{node_id}["{label}"]', line, count=1)
            
            # Fix missing quotes in labels with special characters
            line = re.sub(r'\[([^"\[\]]+:[^"\[\]]+)\]', r'["\1"]', line)
            
            # Fix connections with spaces in node IDs
            for original_id, safe_id in node_id_mapping.items():
                # Fix in connections (-->|, ---|, etc.)
                if '-->' in line or '---' in line or '==>' in line or '-.-' in line:
                    # Replace at start of connection
                    line = re.sub(rf'^\s*{re.escape(original_id)}\s*(-->|---|==>|===|-.-)', rf'    {safe_id} \1', line)
                    # Replace at end of connection  
                    line = re.sub(rf'(-->|---|==>|===|-.-)\s*{re.escape(original_id)}\s*$', rf'\1 {safe_id}', line)
                    # Replace in middle with label
                    line = re.sub(rf'(-->|---|==>|===|-.-)\|([^|]+)\|\s*{re.escape(original_id)}', rf'\1|\2| {safe_id}', line)
                
                # Fix in class applications
                if line.strip().startswith('class '):
                    line = line.replace(f' {original_id} ', f' {safe_id} ')
                    line = line.replace(f' {original_id},', f' {safe_id},')
                    line = line.replace(f',{original_id} ', f',{safe_id} ')
                    line = line.replace(f',{original_id},', f',{safe_id},')
                    # Handle at end of line
                    if line.endswith(f' {original_id}'):
                        line = line[:-len(original_id)] + safe_id
            
            # Only add non-empty lines
            if line.strip():
                fixed_lines.append(line)
        
        # If only graph declaration remains, create a simple diagram
        if len(fixed_lines) == 1 and fixed_lines[0].startswith("graph"):
            fixed_lines.append("    Note[Diagram could not be properly extracted]")
        
        return "\n".join(fixed_lines)