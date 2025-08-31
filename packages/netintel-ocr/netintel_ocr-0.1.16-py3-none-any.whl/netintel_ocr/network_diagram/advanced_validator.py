"""Advanced Mermaid diagram validation and fixing."""

import re
from typing import Dict, List, Tuple, Set


class AdvancedMermaidFixer:
    """Advanced fixing for complex Mermaid syntax issues."""
    
    def fix_complex_diagram(self, mermaid_code: str) -> str:
        """
        Fix complex Mermaid diagrams with multiple issues.
        
        Args:
            mermaid_code: Original Mermaid code
            
        Returns:
            Fixed Mermaid code
        """
        lines = mermaid_code.strip().split("\n")
        fixed_lines = []
        
        # Track node mappings and state
        node_id_map = {}  # Original ID -> Safe ID
        defined_nodes = set()  # Track defined safe IDs
        node_counts = {}  # Track duplicates
        in_subgraph = False
        
        for line in lines:
            original_line = line
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # Handle comments
            if line.strip().startswith("%%"):
                fixed_lines.append(line)
                continue
            
            # Remove C-style comments
            if "//" in line:
                comment_idx = line.find("//")
                if comment_idx == 0 or (comment_idx > 0 and line[comment_idx-1].isspace()):
                    line = line[:comment_idx].rstrip()
                    if not line:
                        continue
            
            # Fix graph declaration
            if line.strip().startswith("graph") and "{" in line:
                line = line.replace("{", "").strip()
            
            # Skip standalone braces
            if line.strip() in ["{", "}"]:
                continue
            
            # Fix subgraph syntax
            if "subgraph" in line:
                # Fix subgraph_NAME to subgraph NAME
                line = re.sub(r'subgraph_(\w+)', r'subgraph \1', line)
                if line.strip().startswith("subgraph"):
                    in_subgraph = True
                fixed_lines.append(line)
                continue
            
            # Handle end statement
            if line.strip() == "end":
                in_subgraph = False
                fixed_lines.append(line)
                continue
            
            # Process node definitions
            if self._is_node_definition(line):
                line, node_map = self._fix_node_definition(line, node_counts)
                node_id_map.update(node_map)
                for safe_id in node_map.values():
                    defined_nodes.add(safe_id)
                fixed_lines.append(line)
                continue
            
            # Process connections
            if self._is_connection(line):
                line = self._fix_connection(line, node_id_map)
                fixed_lines.append(line)
                continue
            
            # Process class definitions
            if line.strip().startswith("classDef"):
                fixed_lines.append(line)
                continue
            
            # Process class applications
            if line.strip().startswith("class "):
                line = self._fix_class_application(line, node_id_map)
                fixed_lines.append(line)
                continue
            
            # Default: add the line
            fixed_lines.append(line)
        
        return "\n".join(fixed_lines)
    
    def _is_node_definition(self, line: str) -> bool:
        """Check if line defines a node."""
        # Skip if it's a connection
        if any(arrow in line for arrow in ["-->", "---", "==>", "-.-", "===", "-.->", "--o", "--x"]):
            return False
        
        # Skip class and subgraph lines
        if any(line.strip().startswith(kw) for kw in ["class ", "classDef", "subgraph", "graph", "%%", "end"]):
            return False
        
        # Check for node patterns
        patterns = [
            r'^\s*[\w\s\-]+\[',      # Rectangle
            r'^\s*[\w\s\-]+\(',      # Round/Stadium  
            r'^\s*[\w\s\-]+\{',      # Rhombus
            r'^\s*[\w\s\-]+\>',      # Asymmetric
            r'^\s*[\w\s\-]+\[\[',    # Subroutine
            r'^\s*[\w\s\-]+\(\(',    # Circle
        ]
        
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _is_connection(self, line: str) -> bool:
        """Check if line defines a connection."""
        arrows = ["-->", "---", "==>", "-.-", "===", "-.->", "--o", "--x", "o--", "x--"]
        return any(arrow in line for arrow in arrows)
    
    def _fix_node_definition(self, line: str, node_counts: Dict[str, int]) -> Tuple[str, Dict[str, str]]:
        """
        Fix node definition with problematic IDs.
        
        Returns:
            Fixed line and mapping of original to safe IDs
        """
        node_map = {}
        
        # Extract node ID and the rest
        match = re.match(r'^(\s*)([\w\s\-]+)([\[\(\{\>\<].*)', line)
        if not match:
            return line, node_map
        
        indent = match.group(1)
        original_id = match.group(2).strip()
        rest = match.group(3)
        
        # Create safe ID
        safe_id = self._make_safe_id(original_id, node_counts)
        
        # Store mapping
        node_map[original_id] = safe_id
        
        # Fix parentheses in labels if needed
        if '[' in rest and ']' in rest and '(' in rest:
            # Extract label
            label_match = re.search(r'\[([^\[\]]+)\]', rest)
            if label_match:
                label = label_match.group(1)
                if '(' in label and ')' in label and not (label.startswith('"') or label.startswith("'")):
                    rest = rest.replace(f'[{label}]', f'["{label}"]')
        
        # For round parentheses nodes
        if rest.startswith('([') and '])' in rest:
            label_match = re.search(r'\(\[([^\[\]]+)\]\)', rest)
            if label_match:
                label = label_match.group(1)
                if '(' in label and ')' in label and not (label.startswith('"') or label.startswith("'")):
                    rest = rest.replace(f'([{label}])', f'(["{label}"])')
        
        return f"{indent}{safe_id}{rest}", node_map
    
    def _make_safe_id(self, original_id: str, node_counts: Dict[str, int]) -> str:
        """Create a safe node ID from original."""
        # Remove special characters and replace with underscores
        safe_id = re.sub(r'[^A-Za-z0-9]', '_', original_id)
        # Remove multiple underscores
        safe_id = re.sub(r'_+', '_', safe_id)
        # Remove leading/trailing underscores
        safe_id = safe_id.strip('_')
        
        # Handle empty result
        if not safe_id:
            safe_id = "node"
        
        # Handle duplicates
        base_id = safe_id
        if base_id in node_counts:
            node_counts[base_id] += 1
            safe_id = f"{base_id}{node_counts[base_id]}"
        else:
            node_counts[base_id] = 1
        
        return safe_id
    
    def _fix_connection(self, line: str, node_map: Dict[str, str]) -> str:
        """Fix connections with mapped node IDs."""
        fixed_line = line
        
        # Replace node IDs in connections
        for original_id, safe_id in node_map.items():
            # Escape special regex characters in original ID
            escaped_id = re.escape(original_id)
            
            # Match at start of line (source node)
            fixed_line = re.sub(
                rf'^\s*{escaped_id}\s*(-->|---|==>|===|-.-|-.->|--o|--x)',
                rf'    {safe_id} \1',
                fixed_line
            )
            
            # Match at end of line (target node)
            fixed_line = re.sub(
                rf'(-->|---|==>|===|-.-|-.->|--o|--x|o--|x--)\s*{escaped_id}\s*$',
                rf'\1 {safe_id}',
                fixed_line
            )
            
            # Match with label in middle
            fixed_line = re.sub(
                rf'(-->|---|==>|===|-.-|-.->)\|([^|]*)\|\s*{escaped_id}',
                rf'\1|\2| {safe_id}',
                fixed_line
            )
        
        return fixed_line
    
    def _fix_class_application(self, line: str, node_map: Dict[str, str]) -> str:
        """Fix class application with mapped node IDs."""
        fixed_line = line
        
        for original_id, safe_id in node_map.items():
            # Simple replacements for class applications
            fixed_line = fixed_line.replace(f' {original_id} ', f' {safe_id} ')
            fixed_line = fixed_line.replace(f' {original_id},', f' {safe_id},')
            fixed_line = fixed_line.replace(f',{original_id} ', f',{safe_id} ')
            fixed_line = fixed_line.replace(f',{original_id},', f',{safe_id},')
            
            # Handle at end of line
            if fixed_line.endswith(f' {original_id}'):
                fixed_line = fixed_line[:-len(original_id)] + safe_id
        
        return fixed_line