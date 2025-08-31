"""Robust Mermaid validator and fixer using comprehensive rules."""

import re
from typing import Dict, List, Set, Tuple, Optional
import hashlib


class RobustMermaidValidator:
    """Comprehensive Mermaid diagram validator and fixer."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.node_registry = {}
        self.safe_id_map = {}
        
    def validate_and_fix(self, mermaid_code: str) -> Tuple[bool, str, List[str]]:
        """
        Validate and fix Mermaid code.
        
        Returns:
            (is_valid, fixed_code, errors)
        """
        self.errors = []
        self.warnings = []
        self.node_registry = {}
        self.safe_id_map = {}
        
        fixed_code = self._comprehensive_fix(mermaid_code)
        is_valid = self._validate_syntax(fixed_code)
        
        return is_valid, fixed_code, self.errors
    
    def _comprehensive_fix(self, code: str) -> str:
        """Apply comprehensive fixes to Mermaid code."""
        lines = code.strip().split('\n')
        fixed_lines = []
        
        # Phase 1: Clean up basic issues
        cleaned_lines = self._phase1_cleanup(lines)
        
        # Phase 2: Fix node IDs and build registry
        node_fixed_lines = self._phase2_fix_nodes(cleaned_lines)
        
        # Phase 3: Fix connections using registry
        connection_fixed_lines = self._phase3_fix_connections(node_fixed_lines)
        
        # Phase 4: Fix class applications
        final_lines = self._phase4_fix_classes(connection_fixed_lines)
        
        return '\n'.join(final_lines)
    
    def _phase1_cleanup(self, lines: List[str]) -> List[str]:
        """Phase 1: Basic cleanup."""
        cleaned = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Keep comments as-is
            if line.strip().startswith('%%'):
                cleaned.append(line)
                continue
            
            # Remove C-style comments
            if '//' in line:
                idx = line.find('//')
                if idx == 0 or (idx > 0 and line[idx-1].isspace()):
                    line = line[:idx].rstrip()
                    if not line:
                        continue
            
            # Fix graph declaration
            if line.strip().startswith('graph') and '{' in line:
                line = line.replace('{', '').strip()
            
            # Skip standalone braces
            if line.strip() in ['{', '}']:
                continue
            
            # Fix subgraph syntax
            line = re.sub(r'subgraph_(\w+)', r'subgraph \1', line)
            
            cleaned.append(line)
        
        return cleaned
    
    def _phase2_fix_nodes(self, lines: List[str]) -> List[str]:
        """Phase 2: Fix node definitions and build registry."""
        fixed = []
        node_counter = {}
        
        for line in lines:
            # Skip non-node lines
            if (line.strip().startswith(('%%', 'graph', 'subgraph', 'end', 'class', 'classDef')) or
                any(arrow in line for arrow in ['-->', '---', '==>', '-.-', '==='])):
                fixed.append(line)
                continue
            
            # Check if this is a node definition
            node_match = self._extract_node_definition(line)
            if node_match:
                original_id, shape_start, label, shape_end = node_match
                
                # Create safe ID
                safe_id = self._create_safe_id(original_id, node_counter)
                self.safe_id_map[original_id] = safe_id
                self.node_registry[safe_id] = {
                    'original': original_id,
                    'label': label,
                    'shape': (shape_start, shape_end)
                }
                
                # Fix label if it has parentheses
                if label and '(' in label and ')' in label:
                    if not (label.startswith('"') or label.startswith("'")):
                        label = f'"{label}"'
                
                # Reconstruct node definition
                indent = len(line) - len(line.lstrip())
                fixed_line = ' ' * indent + safe_id + shape_start + label + shape_end
                fixed.append(fixed_line)
            else:
                fixed.append(line)
        
        return fixed
    
    def _extract_node_definition(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Extract node definition components.
        
        Returns:
            (node_id, shape_start, label, shape_end) or None
        """
        # Pattern for various node shapes
        patterns = [
            (r'^(\s*)([\w\s\-]+)\[([^\[\]]*)\]', '[', ']'),  # Rectangle
            (r'^(\s*)([\w\s\-]+)\(\[([^\[\]]*)\]\)', '([', '])'),  # Round
            (r'^(\s*)([\w\s\-]+)\(\(([^\(\)]*)\)\)', '((', '))'),  # Circle
            (r'^(\s*)([\w\s\-]+)\{\{([^\{\}]*)\}\}', '{{', '}}'),  # Rhombus
            (r'^(\s*)([\w\s\-]+)\[\(([^\(\)]*)\)\]', '[(', ')]'),  # Stadium
            (r'^(\s*)([\w\s\-]+)\[\[([^\[\]]*)\]\]', '[[', ']]'),  # Subroutine
            (r'^(\s*)([\w\s\-]+)\>([^\<\>]*)\]', '>', ']'),  # Asymmetric
        ]
        
        for pattern, shape_start, shape_end in patterns:
            match = re.match(pattern, line)
            if match:
                indent = match.group(1)
                node_id = match.group(2).strip()
                label = match.group(3) if len(match.groups()) > 2 else ''
                return (node_id, shape_start, label, shape_end)
        
        return None
    
    def _create_safe_id(self, original: str, counter: Dict[str, int]) -> str:
        """Create a safe node ID."""
        # Replace all non-alphanumeric with underscore
        safe = re.sub(r'[^A-Za-z0-9]', '_', original)
        # Remove multiple underscores
        safe = re.sub(r'_+', '_', safe)
        # Remove leading/trailing underscores
        safe = safe.strip('_')
        
        # Ensure it starts with a letter
        if safe and not safe[0].isalpha():
            safe = 'N' + safe
        
        # Handle empty
        if not safe:
            safe = 'Node'
        
        # Handle duplicates
        base = safe
        if base in counter:
            counter[base] += 1
            safe = f"{base}{counter[base]}"
        else:
            counter[base] = 1
        
        return safe
    
    def _phase3_fix_connections(self, lines: List[str]) -> List[str]:
        """Phase 3: Fix connections using the node registry."""
        fixed = []
        
        for line in lines:
            if not any(arrow in line for arrow in ['-->', '---', '==>', '-.-', '===']):
                fixed.append(line)
                continue
            
            fixed_line = line
            
            # Replace all original IDs with safe IDs in connections
            for original, safe in self.safe_id_map.items():
                # Escape special characters in original ID
                escaped = re.escape(original)
                
                # Replace at start (source)
                fixed_line = re.sub(
                    rf'^\s*{escaped}\s*(-->|---|==>|===|-.-)',
                    f'    {safe} \\1',
                    fixed_line
                )
                
                # Replace at end (target)
                fixed_line = re.sub(
                    rf'(-->|---|==>|===|-.-)\s*{escaped}\s*$',
                    f'\\1 {safe}',
                    fixed_line
                )
                
                # Replace with label
                fixed_line = re.sub(
                    rf'(-->|---|==>|===|-.-)\|([^|]*)\|\s*{escaped}',
                    f'\\1|\\2| {safe}',
                    fixed_line
                )
            
            fixed.append(fixed_line)
        
        return fixed
    
    def _phase4_fix_classes(self, lines: List[str]) -> List[str]:
        """Phase 4: Fix class applications."""
        fixed = []
        
        for line in lines:
            if not line.strip().startswith('class '):
                fixed.append(line)
                continue
            
            fixed_line = line
            
            # Replace original IDs with safe IDs in class applications
            for original, safe in self.safe_id_map.items():
                # Various positions where node ID can appear
                fixed_line = re.sub(rf'\b{re.escape(original)}\b', safe, fixed_line)
            
            fixed.append(fixed_line)
        
        return fixed
    
    def _validate_syntax(self, code: str) -> bool:
        """Validate the fixed Mermaid syntax."""
        lines = code.strip().split('\n')
        
        # Check for graph declaration
        if not any(line.strip().startswith('graph') for line in lines):
            self.errors.append("Missing graph declaration")
            return False
        
        # Check subgraph balance
        subgraph_count = sum(1 for line in lines if line.strip().startswith('subgraph'))
        end_count = sum(1 for line in lines if line.strip() == 'end')
        
        if subgraph_count != end_count:
            self.errors.append(f"Unbalanced subgraphs: {subgraph_count} subgraphs, {end_count} ends")
            return False
        
        # Check for invalid characters in node IDs (after fixing)
        for line in lines:
            if any(arrow in line for arrow in ['-->', '---', '==>', '-.-']):
                # Extract node IDs from connections
                parts = re.split(r'-->|---|==>|===|-.-', line)
                for part in parts:
                    node_id = part.split('|')[0].strip() if '|' in part else part.strip()
                    if node_id and ' ' in node_id:
                        self.errors.append(f"Invalid node ID with spaces: {node_id}")
                        return False
        
        return len(self.errors) == 0