"""Comprehensive Mermaid syntax fixer for LLM-generated diagrams."""

import re
from typing import Dict, List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)


class MermaidSyntaxFixer:
    """Complete Mermaid syntax fixer that handles all common LLM errors."""
    
    def __init__(self):
        self.node_registry = {}
        self.safe_id_map = {}
        self.errors = []
        self.warnings = []
        
    def fix(self, mermaid_code: str) -> Tuple[bool, str, List[str]]:
        """
        Fix Mermaid code with comprehensive error handling.
        
        Returns:
            (is_valid, fixed_code, errors)
        """
        # Reset state
        self.node_registry = {}
        self.safe_id_map = {}
        self.errors = []
        self.warnings = []
        
        # Apply fixes
        fixed = self._apply_comprehensive_fixes(mermaid_code)
        
        # Validate
        is_valid = self._validate(fixed)
        
        return is_valid, fixed, self.errors
    
    def _apply_comprehensive_fixes(self, code: str) -> str:
        """Apply all fixes in the correct order."""
        
        # Step 1: Clean up basic issues
        code = self._clean_basic_issues(code)
        
        # Step 2: Parse and fix structure
        lines = code.split('\n')
        graph_line, content_lines = self._extract_graph_declaration(lines)
        
        # Step 3: Process nodes and connections
        nodes = []
        connections = []
        subgraphs = []
        other = []
        
        current_subgraph = None
        for line in content_lines:
            stripped = line.strip()
            
            if not stripped or stripped.startswith('%%'):
                other.append(line)
            elif stripped.startswith('subgraph'):
                current_subgraph = self._fix_subgraph_declaration(stripped)
                subgraphs.append((current_subgraph, []))
            elif stripped == 'end':
                if subgraphs:
                    current_subgraph = None
            elif self._is_connection(stripped):
                connections.append((stripped, current_subgraph))
            elif stripped.startswith(('classDef', 'class')):
                other.append(line)
            else:
                # It's a node definition
                node_def = self._fix_node_definition(stripped)
                if current_subgraph and subgraphs:
                    subgraphs[-1][1].append(node_def)
                else:
                    nodes.append(node_def)
        
        # Step 4: Fix connections with registered nodes
        fixed_connections = []
        for conn, subgraph in connections:
            fixed_conn = self._fix_connection(conn)
            fixed_connections.append(fixed_conn)
        
        # Step 5: Rebuild the diagram
        result = [graph_line]
        
        # Add standalone nodes
        for node in nodes:
            result.append(f"    {node}")
        
        # Add subgraphs
        for subgraph_name, subgraph_nodes in subgraphs:
            if subgraph_name:
                result.append(f"    subgraph {subgraph_name}")
                for node in subgraph_nodes:
                    result.append(f"        {node}")
                result.append("    end")
        
        # Add connections
        for conn in fixed_connections:
            result.append(f"    {conn}")
        
        # Add other elements (styles, comments)
        for item in other:
            if item.strip():
                result.append(f"    {item.strip()}")
        
        return '\n'.join(result)
    
    def _clean_basic_issues(self, code: str) -> str:
        """Clean up basic syntax issues."""
        # Remove C-style comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Remove curly braces
        code = code.replace('{', '').replace('}', '')
        
        # Fix graph declaration
        code = re.sub(r'graph\s+(\w+)\s*\{', r'graph \\1', code)
        
        # Remove empty lines
        lines = [line for line in code.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    def _extract_graph_declaration(self, lines: List[str]) -> Tuple[str, List[str]]:
        """Extract and fix graph declaration."""
        graph_line = "graph TB"  # Default
        content_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('graph'):
                # Extract direction
                match = re.match(r'graph\s+(\w+)', stripped)
                if match:
                    direction = match.group(1)
                    if direction in ['TB', 'TD', 'BT', 'RL', 'LR']:
                        graph_line = f"graph {direction}"
                    else:
                        graph_line = "graph TB"
            else:
                content_lines.append(line)
        
        return graph_line, content_lines
    
    def _fix_subgraph_declaration(self, line: str) -> str:
        """Fix subgraph declaration."""
        match = re.match(r'subgraph\s+(.+)', line.strip())
        if match:
            name = match.group(1).strip()
            # Remove quotes if present
            name = name.strip('"').strip("'")
            # Make safe ID
            safe_name = re.sub(r'[^A-Za-z0-9_]', '_', name)
            safe_name = re.sub(r'_+', '_', safe_name).strip('_')
            if not safe_name:
                safe_name = 'Subgraph'
            return safe_name
        return 'Subgraph'
    
    def _is_connection(self, line: str) -> bool:
        """Check if line is a connection."""
        connections = ['-->', '---', '-.->',  '-.-', '==>', '===', '--x', '--o']
        return any(conn in line for conn in connections)
    
    def _fix_node_definition(self, line: str) -> str:
        """Fix node definition and register it."""
        # Extract node ID and shape/label
        patterns = [
            (r'^([A-Za-z0-9_\-\s#]+)\s*\[([^\]]*)\]', '[', ']'),
            (r'^([A-Za-z0-9_\-\s#]+)\s*\(([^\)]*)\)', '(', ')'),
            (r'^([A-Za-z0-9_\-\s#]+)\s*\{([^\}]*)\}', '{', '}'),
            (r'^([A-Za-z0-9_\-\s#]+)\s*\(\(([^\)]*)\)\)', '((', '))'),
            (r'^([A-Za-z0-9_\-\s#]+)\s*\[\[([^\]]*)\]\]', '[[', ']]'),
            (r'^([A-Za-z0-9_\-\s#]+)\s*\(\[([^\]]*)\]\)', '([', '])'),
        ]
        
        for pattern, shape_start, shape_end in patterns:
            match = re.match(pattern, line.strip())
            if match:
                raw_id = match.group(1).strip()
                label = match.group(2).strip() if len(match.groups()) > 1 else raw_id
                
                # Create safe ID
                safe_id = self._make_safe_id(raw_id)
                
                # Store mapping
                self.safe_id_map[raw_id] = safe_id
                self.node_registry[safe_id] = label
                
                # Fix label if it contains special characters
                if any(char in label for char in ['(', ')', '#', '/', '\\']):
                    if not (label.startswith('"') and label.endswith('"')):
                        label = f'"{label}"'
                
                return f"{safe_id}{shape_start}{label}{shape_end}"
        
        # No shape found, treat as simple node
        raw_id = line.strip()
        safe_id = self._make_safe_id(raw_id)
        self.safe_id_map[raw_id] = safe_id
        self.node_registry[safe_id] = raw_id
        return f"{safe_id}[{raw_id}]"
    
    def _make_safe_id(self, raw_id: str) -> str:
        """Create a safe node ID."""
        # Replace all problematic characters
        safe = re.sub(r'[^A-Za-z0-9]', '_', raw_id)
        safe = re.sub(r'_+', '_', safe)
        safe = safe.strip('_')
        
        # Ensure starts with letter
        if safe and not safe[0].isalpha():
            safe = 'Node_' + safe
        
        if not safe:
            safe = 'Node'
        
        # Handle duplicates
        base = safe
        counter = 1
        while safe in self.node_registry:
            safe = f"{base}_{counter}"
            counter += 1
        
        return safe
    
    def _fix_connection(self, line: str) -> str:
        """Fix connection syntax."""
        # Fix malformed connections
        line = line.strip()
        
        # Fix triple dash with label
        line = re.sub(r'---\|([^|]+)\|---', r'---|\\1|', line)
        
        # Fix LINK token
        line = re.sub(r'\bLINK\b', '---', line)
        
        # Fix spaced arrows
        line = re.sub(r'--\s+>', '-->', line)
        line = re.sub(r'--\s+--', '---', line)
        line = re.sub(r'-\s+-', '---', line)
        
        # Find connection type
        conn_match = None
        conn_type = None
        for conn in ['-->', '---', '-.->',  '-.-', '==>', '===', '--x', '--o']:
            if conn in line:
                conn_type = conn
                # Split on first occurrence
                parts = line.split(conn, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    # Extract label if present
                    label = ''
                    if '|' in right:
                        label_match = re.match(r'\|([^|]*)\|\s*(.+)', right)
                        if label_match:
                            label = label_match.group(1)
                            right = label_match.group(2).strip()
                    
                    # Map node IDs
                    left = self._map_to_safe_id(left)
                    right = self._map_to_safe_id(right)
                    
                    # Rebuild connection
                    if label:
                        return f"{left} {conn_type}|{label}| {right}"
                    else:
                        return f"{left} {conn_type} {right}"
        
        # If no valid connection found, return as-is
        return line
    
    def _map_to_safe_id(self, node_ref: str) -> str:
        """Map a node reference to its safe ID."""
        node_ref = node_ref.strip()
        
        # Check direct mapping
        if node_ref in self.safe_id_map:
            return self.safe_id_map[node_ref]
        
        # Check if it's already a safe ID
        if node_ref in self.node_registry:
            return node_ref
        
        # Create new safe ID for unregistered node
        safe_id = self._make_safe_id(node_ref)
        self.safe_id_map[node_ref] = safe_id
        self.node_registry[safe_id] = node_ref
        
        return safe_id
    
    def _validate(self, code: str) -> bool:
        """Validate the fixed Mermaid code."""
        lines = code.split('\n')
        
        # Check for graph declaration
        if not any(line.strip().startswith('graph') for line in lines):
            self.errors.append("Missing graph declaration")
            return False
        
        # Check subgraph balance
        subgraph_count = sum(1 for line in lines if 'subgraph' in line)
        end_count = sum(1 for line in lines if line.strip() == 'end')
        
        if subgraph_count != end_count:
            self.errors.append(f"Unbalanced subgraphs: {subgraph_count} subgraphs, {end_count} ends")
            return False
        
        return True