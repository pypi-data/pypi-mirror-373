"""
JSON generation module for table data output.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class TableJSONGenerator:
    """Generate JSON output for extracted tables."""
    
    def __init__(self):
        """Initialize the JSON generator."""
        self.json_indent = 2
    
    def generate_json(
        self, 
        tables: List[Dict[str, Any]], 
        page_num: int,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Generate JSON structure for extracted tables.
        
        Args:
            tables: List of extracted tables
            page_num: Page number
            include_metadata: Whether to include metadata
            
        Returns:
            Complete JSON structure
        """
        output = {
            'page': page_num,
            'table_count': len(tables),
            'extraction_timestamp': datetime.now().isoformat(),
            'tables': []
        }
        
        for idx, table in enumerate(tables):
            table_json = self._format_table(table, idx, include_metadata)
            output['tables'].append(table_json)
        
        return output
    
    def _format_table(
        self, 
        table: Dict[str, Any], 
        index: int,
        include_metadata: bool
    ) -> Dict[str, Any]:
        """
        Format a single table for JSON output.
        
        Args:
            table: Table data
            index: Table index on page
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted table JSON
        """
        table_type = table.get('type', 'unknown')
        
        # Base structure
        formatted = {
            'table_index': index,
            'type': table_type
        }
        
        # Add type-specific formatting
        if table_type == 'simple':
            formatted.update(self._format_simple_table(table))
        elif table_type == 'complex':
            formatted.update(self._format_complex_table(table))
        elif table_type == 'multi_row':
            formatted.update(self._format_multi_row_table(table))
        else:
            # Generic format
            formatted['data'] = table.get('data', [])
        
        # Add metadata if requested
        if include_metadata:
            formatted['metadata'] = self._format_metadata(table)
        
        return formatted
    
    def _format_simple_table(self, table: Dict) -> Dict[str, Any]:
        """Format a simple table."""
        return {
            'headers': table.get('headers', []),
            'data': table.get('data', []),
            'confidence': table.get('metadata', {}).get('confidence', 0)
        }
    
    def _format_complex_table(self, table: Dict) -> Dict[str, Any]:
        """Format a complex table with structure."""
        return {
            'structure': table.get('structure', {}),
            'data': table.get('data', []),
            'confidence': table.get('metadata', {}).get('confidence', 0)
        }
    
    def _format_multi_row_table(self, table: Dict) -> Dict[str, Any]:
        """Format a multi-row field table."""
        return {
            'fields': table.get('fields', {}),
            'confidence': table.get('metadata', {}).get('confidence', 0)
        }
    
    def _format_metadata(self, table: Dict) -> Dict[str, Any]:
        """Format metadata for a table."""
        metadata = table.get('metadata', {})
        
        return {
            'rows': metadata.get('rows', 0),
            'columns': metadata.get('columns', 0),
            'extraction_method': table.get('extraction_method', 'unknown'),
            'confidence': metadata.get('confidence', 0),
            'has_headers': metadata.get('has_headers', False),
            'has_merged_cells': metadata.get('has_merged_cells', False),
            'processing_time': metadata.get('processing_time', 'N/A'),
            'inferred_types': table.get('inferred_types', {})
        }
    
    def save_to_file(
        self, 
        json_data: Dict[str, Any], 
        output_path: Path,
        filename: str = None
    ) -> Path:
        """
        Save JSON data to file.
        
        Args:
            json_data: JSON data to save
            output_path: Output directory path
            filename: Optional filename (defaults to table_pageXXX.json)
            
        Returns:
            Path to saved file
        """
        try:
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename if not provided
            if not filename:
                page_num = json_data.get('page', 0)
                filename = f"table_page_{page_num:03d}.json"
            
            # Full file path
            file_path = output_path / filename
            
            # Write JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=self.json_indent, ensure_ascii=False)
            
            logger.info(f"Saved table JSON to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
            raise
    
    def generate_markdown_table(self, table: Dict[str, Any]) -> str:
        """
        Generate markdown representation of a table.
        
        Args:
            table: Table data
            
        Returns:
            Markdown formatted table string
        """
        table_type = table.get('type', 'unknown')
        
        if table_type == 'simple':
            return self._simple_table_to_markdown(table)
        elif table_type == 'complex':
            return self._complex_table_to_markdown(table)
        elif table_type == 'multi_row':
            return self._multi_row_to_markdown(table)
        else:
            return "```json\n" + json.dumps(table.get('data', {}), indent=2) + "\n```"
    
    def _simple_table_to_markdown(self, table: Dict) -> str:
        """Convert simple table to markdown."""
        headers = table.get('headers', [])
        data = table.get('data', [])
        
        if not headers or not data:
            return "*Empty table*"
        
        # Build markdown table
        lines = []
        
        # Header row
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        
        # Separator row
        lines.append("|" + "|".join(["-" * (len(str(h)) + 2) for h in headers]) + "|")
        
        # Data rows
        for row in data:
            if isinstance(row, dict):
                values = [str(row.get(h, '')) for h in headers]
            else:
                values = [str(v) for v in row[:len(headers)]]
            lines.append("| " + " | ".join(values) + " |")
        
        return "\n".join(lines)
    
    def _complex_table_to_markdown(self, table: Dict) -> str:
        """Convert complex table to markdown."""
        # For complex tables, show structure and sample data
        lines = ["#### Complex Table Structure"]
        
        structure = table.get('structure', {})
        if structure:
            lines.append("\n**Header Levels:**")
            lines.append("```json")
            lines.append(json.dumps(structure.get('headers', {}), indent=2))
            lines.append("```")
            
            if structure.get('merged_cells'):
                lines.append("\n**Merged Cells:**")
                lines.append("```json")
                lines.append(json.dumps(structure.get('merged_cells', []), indent=2))
                lines.append("```")
        
        # Show data
        data = table.get('data', [])
        if data:
            lines.append("\n**Data (first 5 rows):**")
            lines.append("```json")
            lines.append(json.dumps(data[:5], indent=2))
            lines.append("```")
        
        return "\n".join(lines)
    
    def _multi_row_to_markdown(self, table: Dict) -> str:
        """Convert multi-row field table to markdown."""
        fields = table.get('fields', {})
        
        if not fields:
            return "*No fields found*"
        
        lines = ["#### Field Values"]
        
        for group_name, group_fields in fields.items():
            lines.append(f"\n**{group_name}:**")
            
            if isinstance(group_fields, dict):
                for key, value in group_fields.items():
                    if isinstance(value, list):
                        value_str = ", ".join(str(v) for v in value)
                    else:
                        value_str = str(value)
                    lines.append(f"- **{key}**: {value_str}")
            else:
                lines.append(f"- {group_fields}")
        
        return "\n".join(lines)
    
    def combine_with_page_content(
        self,
        page_content: str,
        tables: List[Dict[str, Any]],
        page_num: int
    ) -> str:
        """
        Combine tables with existing page content in markdown.
        
        Args:
            page_content: Existing page text content
            tables: List of extracted tables
            page_num: Page number
            
        Returns:
            Combined markdown content
        """
        lines = []
        
        # Add page header
        if tables:
            lines.append(f"# Page {page_num} - With Tables\n")
        else:
            lines.append(f"# Page {page_num}\n")
        
        # Add detected tables section if any
        if tables:
            lines.append("## Detected Tables\n")
            
            for idx, table in enumerate(tables):
                table_type = table.get('type', 'unknown')
                confidence = table.get('metadata', {}).get('confidence', 0)
                method = table.get('extraction_method', 'unknown')
                
                lines.append(f"### Table {idx + 1}: {table_type.title()} Table")
                lines.append(f"**Confidence**: {confidence:.2f}")
                lines.append(f"**Extraction Method**: {method}")
                
                # Add metadata
                metadata = table.get('metadata', {})
                if metadata.get('rows'):
                    lines.append(f"**Rows**: {metadata['rows']} | **Columns**: {metadata.get('columns', 'N/A')}")
                
                lines.append("")
                
                # Add rendered view
                lines.append("#### Rendered View")
                lines.append(self.generate_markdown_table(table))
                lines.append("")
                
                # Add JSON view
                lines.append("#### Structured Data (JSON)")
                lines.append("```json")
                formatted_table = self._format_table(table, idx, False)
                lines.append(json.dumps(formatted_table, indent=2))
                lines.append("```")
                lines.append("")
        
        # Add original page text
        if page_content:
            lines.append("## Page Text Content\n")
            lines.append(page_content)
        
        return "\n".join(lines)