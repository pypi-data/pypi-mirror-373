"""
Markdown Optimizer for Vector Database Integration

Creates markdown optimized for vector database ingestion with
consistent structure, proper formatting, and embedded metadata.
"""

import re
from typing import Dict, List, Optional
import json


class MarkdownOptimizer:
    """Optimize markdown content for vector database ingestion."""
    
    def __init__(self):
        """Initialize markdown optimizer."""
        self.section_separator = "\n\n"
        self.metadata_separator = "---"
    
    def optimize_markdown(self, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Optimize markdown content for vector databases.
        
        Args:
            content: Raw markdown content
            metadata: Optional metadata to embed
            
        Returns:
            Optimized markdown content
        """
        # Start with metadata header if provided
        optimized = ""
        if metadata:
            optimized = self._create_metadata_header(metadata) + "\n\n"
        
        # Process content
        optimized += self._optimize_content(content)
        
        return optimized
    
    def _create_metadata_header(self, metadata: Dict) -> str:
        """Create YAML-style metadata header."""
        header = self.metadata_separator + "\n"
        
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                # Convert complex types to JSON string
                header += f"{key}: {json.dumps(value)}\n"
            else:
                header += f"{key}: {value}\n"
        
        header += self.metadata_separator
        return header
    
    def _optimize_content(self, content: str) -> str:
        """
        Optimize the main content for vector databases.
        
        Args:
            content: Raw content
            
        Returns:
            Optimized content
        """
        if not content:
            return ""
        
        # Normalize headers
        content = self._normalize_headers(content)
        
        # Optimize code blocks
        content = self._optimize_code_blocks(content)
        
        # Standardize lists
        content = self._standardize_lists(content)
        
        # Optimize tables
        content = self._optimize_tables(content)
        
        # Ensure consistent spacing
        content = self._normalize_spacing(content)
        
        return content
    
    def _normalize_headers(self, content: str) -> str:
        """Ensure consistent header formatting."""
        lines = content.split('\n')
        normalized = []
        
        for line in lines:
            # Ensure space after hash in headers
            if re.match(r'^#{1,6}[^#\s]', line):
                line = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', line)
            normalized.append(line)
        
        return '\n'.join(normalized)
    
    def _optimize_code_blocks(self, content: str) -> str:
        """Optimize code blocks for better chunking."""
        # Add language hints where missing
        content = re.sub(
            r'^```\n',
            '```text\n',
            content,
            flags=re.MULTILINE
        )
        
        # Ensure code blocks are properly separated
        content = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            lambda m: f"\n```{m.group(1) or 'text'}\n{m.group(2)}\n```\n",
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _standardize_lists(self, content: str) -> str:
        """Standardize list formatting."""
        # Convert various list markers to consistent format
        lines = content.split('\n')
        standardized = []
        
        for line in lines:
            # Standardize unordered lists to use '-'
            if re.match(r'^\s*[\*\+]\s+', line):
                line = re.sub(r'^(\s*)[\*\+]\s+', r'\1- ', line)
            standardized.append(line)
        
        return '\n'.join(standardized)
    
    def _optimize_tables(self, content: str) -> str:
        """Optimize markdown tables for vector databases."""
        # Find markdown tables
        table_pattern = r'(\|[^\n]+\|\n)+(\|[-:\s|]+\|\n)(\|[^\n]+\|\n)+'
        
        def optimize_table(match):
            table = match.group(0)
            # Add spacing around table for better chunking
            return f"\n{table}\n"
        
        content = re.sub(table_pattern, optimize_table, content)
        return content
    
    def _normalize_spacing(self, content: str) -> str:
        """Ensure consistent spacing throughout document."""
        # Remove trailing whitespace
        lines = [line.rstrip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        # Ensure single blank line between sections
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure blank line before headers (except first)
        content = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', content)
        
        return content.strip()
    
    def create_vector_markdown(self, 
                              text_content: str,
                              tables: Optional[List[Dict]] = None,
                              diagrams: Optional[List[Dict]] = None,
                              metadata: Optional[Dict] = None) -> str:
        """
        Create complete vector-optimized markdown document.
        
        Args:
            text_content: Main text content
            tables: List of table data dictionaries
            diagrams: List of network diagram dictionaries
            metadata: Document metadata
            
        Returns:
            Complete vector-optimized markdown
        """
        sections = []
        
        # Add metadata header
        if metadata:
            sections.append(self._create_metadata_header(metadata))
        
        # Add main text content
        if text_content:
            sections.append("## Text Content\n\n" + self._optimize_content(text_content))
        
        # Add flattened tables
        if tables:
            table_section = self._create_table_section(tables)
            if table_section:
                sections.append(table_section)
        
        # Add network diagrams
        if diagrams:
            diagram_section = self._create_diagram_section(diagrams)
            if diagram_section:
                sections.append(diagram_section)
        
        return "\n\n".join(sections)
    
    def _create_table_section(self, tables: List[Dict]) -> str:
        """Create optimized table section."""
        if not tables:
            return ""
        
        section = "## Tables\n\n"
        
        for i, table in enumerate(tables):
            section += f"### Table {i + 1}\n\n"
            
            # Add table metadata if available
            if 'metadata' in table:
                section += "**Metadata:**\n"
                for key, value in table['metadata'].items():
                    section += f"- {key}: {value}\n"
                section += "\n"
            
            # Add flattened table data
            if 'flattened_data' in table:
                section += "**Data (Flattened):**\n```json\n"
                section += json.dumps(table['flattened_data'], indent=2)
                section += "\n```\n\n"
            elif 'data' in table:
                section += "**Data:**\n```json\n"
                section += json.dumps(table['data'], indent=2)
                section += "\n```\n\n"
        
        return section.rstrip()
    
    def _create_diagram_section(self, diagrams: List[Dict]) -> str:
        """Create optimized network diagram section."""
        if not diagrams:
            return ""
        
        section = "## Network Diagrams\n\n"
        
        for i, diagram in enumerate(diagrams):
            section += f"### Diagram {i + 1}\n\n"
            
            # Add diagram metadata
            if 'type' in diagram:
                section += f"**Type:** {diagram['type']}\n"
            if 'component_count' in diagram:
                section += f"**Components:** {diagram['component_count']}\n"
            if 'connection_count' in diagram:
                section += f"**Connections:** {diagram['connection_count']}\n"
            section += "\n"
            
            # Add flattened diagram data
            if 'flattened_data' in diagram:
                section += "**Structure (Flattened):**\n```json\n"
                section += json.dumps(diagram['flattened_data'], indent=2)
                section += "\n```\n\n"
            
            # Add mermaid code if available (cleaned)
            if 'mermaid_code' in diagram:
                section += "**Diagram Code:**\n```mermaid\n"
                section += diagram['mermaid_code']
                section += "\n```\n\n"
        
        return section.rstrip()