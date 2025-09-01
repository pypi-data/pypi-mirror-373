"""Enhanced Mermaid diagram fixer that handles complex syntax issues."""

import re
from typing import Dict, List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)


class EnhancedMermaidFixer:
    """Advanced Mermaid syntax fixer that handles LLM-generated issues."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.node_registry = {}
        self.safe_id_map = {}
        self.connection_patterns = [
            '-->',  # Directed arrow
            '---',  # Simple line
            '-.->',  # Dotted arrow
            '-.-',  # Dotted line
            '==>',  # Thick arrow
            '===',  # Thick line
            '--x',  # Cross ending
            '--o',  # Circle ending
        ]
        
    def fix_mermaid(self, mermaid_code: str) -> Tuple[bool, str, List[str]]:
        """
        Fix complex Mermaid syntax issues from LLM output.
        
        Returns:
            (is_valid, fixed_code, errors)
        """
        self.errors = []
        self.warnings = []
        self.node_registry = {}
        self.safe_id_map = {}
        
        # Apply comprehensive fixes in phases
        fixed_code = self._apply_all_fixes(mermaid_code)
        
        # Validate the result
        is_valid = self._validate_final_syntax(fixed_code)
        
        return is_valid, fixed_code, self.errors
    
    def _apply_all_fixes(self, code: str) -> str:
        """Apply all fixing phases."""
        
        # Phase 1: Pre-processing and cleanup
        code = self._preprocess_code(code)
        
        # Phase 2: Fix malformed connections
        code = self._fix_malformed_connections(code)
        
        # Phase 3: Fix node definitions
        code = self._fix_node_definitions(code)
        
        # Phase 4: Fix labels and quotes
        code = self._fix_labels_and_quotes(code)
        
        # Phase 5: Fix subgraphs and structure
        code = self._fix_structure(code)
        
        # Phase 6: Final cleanup
        code = self._final_cleanup(code)
        
        return code
    
    def _preprocess_code(self, code: str) -> str:
        """Pre-process and clean the code."""
        lines = []
        
        for line in code.split('\n'):
            # Remove C-style comments
            if '//' in line:
                comment_idx = line.find('//')
                line = line[:comment_idx].rstrip()
            
            # Skip empty lines and standalone braces
            if not line.strip() or line.strip() in ['{', '}']:
                continue
            
            # Fix graph declaration with braces
            if line.strip().startswith('graph') and '{' in line:
                line = line.replace('{', '').strip()
            
            # Fix incorrect spacing in graph declaration
            line = re.sub(r'graph\s+(\w+)\s+', r'graph \1\n    ', line)
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _fix_malformed_connections(self, code: str) -> str:
        """Fix malformed connection syntax."""
        lines = []
        
        for line in code.split('\n'):
            # Fix triple dash issues (e.g., "---|Logical|---")
            line = re.sub(r'---\|([^|]+)\|---', r'---|\\1|', line)
            
            # Fix incorrect LINK tokens
            line = re.sub(r'\s+LINK\s+', ' --- ', line)
            
            # Fix malformed arrow syntax with labels
            line = re.sub(r'--\s*\|([^|]+)\|\s*-->', r'--|\\1|-->', line)
            line = re.sub(r'--\s*\|([^|]+)\|\s*---', r'---|\\1|', line)
            
            # Fix incorrect double dash patterns
            line = re.sub(r'--\s+--\s+', '---', line)
            line = re.sub(r'--\s+--', '---', line)
            line = re.sub(r'--\s+>\s+', '-->', line)
            line = re.sub(r'--\s+>', '-->', line)
            line = re.sub(r'--\s+', '---', line)
            
            # Fix missing spaces in connections (but preserve labels)
            for pattern in self.connection_patterns:
                # Only add spaces if not already present and not part of a label
                if '|' not in line or pattern not in line:
                    continue
                # Ensure spaces around connections
                line = re.sub(rf'(\S){re.escape(pattern)}(\S)', rf'\1 {pattern} \2', line)
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _fix_node_definitions(self, code: str) -> str:
        """Fix node definition issues."""
        lines = []
        defined_nodes = set()
        
        for line in code.split('\n'):
            # Skip non-node lines
            if any(arrow in line for arrow in self.connection_patterns):
                lines.append(line)
                continue
            
            if line.strip().startswith(('graph', 'subgraph', 'end', 'class', 'classDef', '%%')):
                lines.append(line)
                continue
            
            # Fix node definitions with problematic characters
            node_match = self._extract_node_pattern(line)
            if node_match:
                node_id, label_with_shape = node_match
                
                # Create safe node ID
                safe_id = self._make_safe_id(node_id)
                self.safe_id_map[node_id] = safe_id
                
                # Fix label issues
                label_with_shape = self._fix_node_label(label_with_shape)
                
                # Register node
                defined_nodes.add(safe_id)
                
                # Reconstruct line
                indent = len(line) - len(line.lstrip())
                line = ' ' * indent + safe_id + label_with_shape
            
            lines.append(line)
        
        # Update connections with safe IDs
        fixed_lines = []
        for line in lines:
            if any(arrow in line for arrow in self.connection_patterns):
                line = self._update_connection_ids(line, self.safe_id_map)
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _extract_node_pattern(self, line: str) -> Optional[Tuple[str, str]]:
        """Extract node ID and label/shape from a line."""
        # First check for nodes with spaces in their IDs (common LLM mistake)
        space_patterns = [
            r'^(\s*)([A-Za-z0-9_\- ]+)\s*(\[.*\])',
            r'^(\s*)([A-Za-z0-9_\- ]+)\s*(\(.*\))',
            r'^(\s*)([A-Za-z0-9_\- ]+)\s*(\{.*\})',
            r'^(\s*)([A-Za-z0-9_\- ]+)\s*(\[\[.*\]\])',
            r'^(\s*)([A-Za-z0-9_\- ]+)\s*(\(\[.*\]\))',
            r'^(\s*)([A-Za-z0-9_\- ]+)\s*(\(\(.*\)\))',
        ]
        
        for pattern in space_patterns:
            match = re.match(pattern, line)
            if match:
                node_id = match.group(2).strip()
                label_shape = match.group(3) if len(match.groups()) >= 3 else ''
                return (node_id, label_shape)
        
        # Check for node without explicit shape
        match = re.match(r'^(\s*)([A-Za-z0-9_\- ]+)\s*$', line.strip())
        if match and not any(kw in line for kw in ['graph', 'subgraph', 'end', 'class', 'classDef']):
            return (match.group(2).strip(), '')
        
        return None
    
    def _make_safe_id(self, node_id: str) -> str:
        """Create a safe node ID."""
        # Remove spaces and special characters
        safe_id = re.sub(r'[^A-Za-z0-9_]', '_', node_id)
        
        # Remove multiple underscores
        safe_id = re.sub(r'_+', '_', safe_id)
        
        # Remove leading/trailing underscores
        safe_id = safe_id.strip('_')
        
        # Ensure it starts with a letter
        if safe_id and not safe_id[0].isalpha():
            safe_id = 'Node_' + safe_id
        
        # Handle empty case
        if not safe_id:
            safe_id = 'Node'
        
        # Make unique if needed
        base_id = safe_id
        counter = 1
        while safe_id in self.node_registry:
            safe_id = f"{base_id}_{counter}"
            counter += 1
        
        self.node_registry[safe_id] = True
        return safe_id
    
    def _fix_node_label(self, label_with_shape: str) -> str:
        """Fix issues in node labels."""
        if not label_with_shape:
            return '[Node]'
        
        # Extract shape markers and content
        shape_pairs = [
            ('[[', ']]'),
            ('([', '])'),
            ('((', '))'),
            ('{{', '}}'),
            ('[(', ')]'),
            ('[', ']'),
            ('(', ')'),
            ('{', '}'),
        ]
        
        for start, end in shape_pairs:
            if label_with_shape.startswith(start) and label_with_shape.endswith(end):
                content = label_with_shape[len(start):-len(end)]
                
                # Fix quotes in content
                if content and not (content.startswith('"') and content.endswith('"')):
                    # Check if content needs quotes (has special characters)
                    if any(char in content for char in ['(', ')', '#', '/', '\\', '|']):
                        content = f'"{content}"'
                
                return start + content + end
        
        # Default to rectangle if no valid shape found
        return f'[{label_with_shape}]'
    
    def _update_connection_ids(self, line: str, id_map: Dict[str, str]) -> str:
        """Update connection line with safe node IDs."""
        # Find the arrow pattern
        arrow_pattern = None
        for pattern in self.connection_patterns:
            if pattern in line:
                arrow_pattern = pattern
                break
        
        if not arrow_pattern:
            return line
        
        # Split by arrow, handling labels
        parts = line.split(arrow_pattern, 1)
        if len(parts) != 2:
            return line
        
        left_part = parts[0].strip()
        right_part = parts[1].strip()
        
        # Extract label if present
        label = ''
        if '|' in arrow_pattern or '|' in right_part:
            # Handle labeled connections
            if '|' in right_part:
                label_match = re.match(r'^[|\s]*([^|]*)[|\s]*(.*)$', right_part)
                if label_match:
                    label = label_match.group(1)
                    right_part = label_match.group(2).strip()
        
        # Update node IDs
        for original, safe in id_map.items():
            if left_part == original:
                left_part = safe
            if right_part == original:
                right_part = safe
        
        # Reconstruct line
        indent = '    '
        if label:
            return f"{indent}{left_part} {arrow_pattern}|{label}| {right_part}"
        else:
            return f"{indent}{left_part} {arrow_pattern} {right_part}"
    
    def _fix_labels_and_quotes(self, code: str) -> str:
        """Fix label and quote issues."""
        lines = []
        
        for line in code.split('\n'):
            # Fix STR token issues (e.g., 'Internal' being treated as STR)
            line = re.sub(r'\bSTR\b', '', line)
            
            # Fix unquoted labels with special characters in connections
            if any(arrow in line for arrow in self.connection_patterns):
                # Fix labels between pipes
                line = re.sub(r'\|([^|"]+)\|', lambda m: f'|{m.group(1).strip()}|', line)
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _fix_structure(self, code: str) -> str:
        """Fix structural issues like subgraphs."""
        lines = []
        indent_level = 0
        in_subgraph = False
        
        for line in code.split('\n'):
            stripped = line.strip()
            
            # Handle graph declaration
            if stripped.startswith('graph '):
                lines.append(stripped)
                indent_level = 1
                continue
            
            # Handle subgraph - fix spaces in subgraph names
            if 'subgraph' in stripped:
                # Fix subgraph with spaces in name
                match = re.match(r'^subgraph\s+(.+)$', stripped)
                if match:
                    subgraph_name = match.group(1)
                    # Replace spaces with underscores in subgraph name
                    safe_name = re.sub(r'[^A-Za-z0-9_]', '_', subgraph_name)
                    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
                    if not safe_name:
                        safe_name = 'Subgraph'
                    lines.append('    ' * indent_level + f'subgraph {safe_name}')
                    indent_level += 1
                    in_subgraph = True
                else:
                    lines.append('    ' * indent_level + stripped)
                    if 'subgraph' == stripped[:8]:
                        indent_level += 1
                        in_subgraph = True
                continue
            
            # Handle end
            if stripped == 'end':
                indent_level = max(1, indent_level - 1)
                lines.append('    ' * indent_level + 'end')
                in_subgraph = indent_level > 1
                continue
            
            # Handle other lines
            if stripped:
                if stripped.startswith(('%%', 'classDef', 'class')):
                    lines.append('    ' + stripped)
                else:
                    lines.append('    ' * max(1, indent_level) + stripped)
        
        # Ensure proper subgraph balance
        subgraph_count = sum(1 for line in lines if 'subgraph' in line)
        end_count = sum(1 for line in lines if line.strip() == 'end')
        
        # Add missing 'end' statements
        while end_count < subgraph_count:
            lines.append('    end')
            end_count += 1
        
        return '\n'.join(lines)
    
    def _final_cleanup(self, code: str) -> str:
        """Final cleanup pass."""
        lines = []
        
        for line in code.split('\n'):
            # Remove duplicate spaces
            line = re.sub(r'\s+', ' ', line)
            
            # Fix indentation
            if line.strip():
                if line.strip().startswith('graph'):
                    lines.append(line.strip())
                elif line.strip().startswith('%%'):
                    lines.append('    ' + line.strip())
                elif not line.startswith(' '):
                    lines.append('    ' + line.strip())
                else:
                    lines.append(line.rstrip())
        
        # Ensure proper structure
        result = '\n'.join(lines)
        
        # Make sure we have a valid graph declaration
        if not result.strip().startswith('graph'):
            result = 'graph TB\n' + result
        
        return result
    
    def _validate_final_syntax(self, code: str) -> bool:
        """Validate the final Mermaid syntax."""
        lines = code.strip().split('\n')
        
        # Must have graph declaration
        if not any(line.strip().startswith('graph') for line in lines):
            self.errors.append("Missing graph declaration")
            return False
        
        # Check subgraph balance
        subgraph_count = sum(1 for line in lines if 'subgraph' in line)
        end_count = sum(1 for line in lines if line.strip() == 'end')
        
        if subgraph_count != end_count:
            self.errors.append(f"Unbalanced subgraphs: {subgraph_count} subgraphs, {end_count} ends")
        
        # Check for invalid node IDs in connections
        for line in lines:
            if any(arrow in line for arrow in self.connection_patterns):
                # Basic check for spaces in node IDs
                parts = re.split(r'-->|---|-.->|-.-|==>|===|--x|--o', line)
                for part in parts:
                    # Remove label if present
                    if '|' in part:
                        part = part.split('|')[0]
                    part = part.strip()
                    
                    # Check for spaces (invalid in node IDs)
                    if part and ' ' in part and not part.startswith('"'):
                        self.warnings.append(f"Possible invalid node ID: {part}")
        
        return len(self.errors) == 0