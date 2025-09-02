"""
Content Filter for Vector Generation

Removes non-source artifacts and model-infused content to ensure
vector embeddings represent only the actual document content.
"""

import re
from typing import Dict, List, Tuple


class ContentFilter:
    """Filter out non-source content and artifacts from extracted text."""
    
    def __init__(self):
        """Initialize content filter with patterns to remove."""
        # Patterns for content to remove
        self.removal_patterns = [
            # Processing artifacts
            r'^#+ Page \d+.*$',  # Page headers
            r'^Generated: \d{4}-\d{2}-\d{2}.*$',  # Generation timestamps
            r'^Model: .*$',  # Model information
            r'^Processing time: .*$',  # Processing metrics
            r'^Confidence: [\d.]+$',  # Confidence scores
            r'^\[.*extraction failed.*\]',  # Failure messages
            r'^\[.*timeout.*\]',  # Timeout messages
            r'^Error:.*$',  # Error messages
            r'^Warning:.*$',  # Warning messages
            r'^✓ Complete.*$',  # Completion markers
            r'^Detection Confidence: .*$',  # Detection metrics
            r'^Components: \d+ detected.*$',  # Component counts
            r'^Connections: \d+ detected.*$',  # Connection counts
            r'^Models Used:.*$',  # Model usage info
            r'^Extraction Method:.*$',  # Method indicators
            
            # Footer metrics (from merged documents)
            r'^## 📊 Processing Metrics.*',  # Start of metrics section
            r'^### Document Information.*',
            r'^### Processing Details.*',
            r'^### Quality Report.*',
            r'^### Processing Configuration.*',
            r'^- \*\*Source File\*\*:.*',
            r'^- \*\*File Size\*\*:.*',
            r'^- \*\*MD5 Checksum\*\*:.*',
            r'^- \*\*Total Pages.*\*\*:.*',
            r'^- \*\*Extraction Date\*\*:.*',
            r'^- \*\*Processing Time\*\*:.*',
            r'^- \*\*Processing Mode\*\*:.*',
            
            # System messages
            r'^\s*---+\s*$',  # Horizontal rules (keep only if part of source)
            r'^NetIntel-OCR v[\d.]+.*$',  # Tool version
            r'^Processed with.*$',  # Processing notes
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.MULTILINE | re.IGNORECASE) 
                                 for pattern in self.removal_patterns]
    
    def filter_content(self, text: str) -> str:
        """
        Remove non-source artifacts from text content.
        
        Args:
            text: Raw extracted text with potential artifacts
            
        Returns:
            Filtered text containing only source-truthful content
        """
        if not text:
            return ""
        
        filtered = text
        
        # Remove matching patterns
        for pattern in self.compiled_patterns:
            filtered = pattern.sub('', filtered)
        
        # Remove metadata headers if they exist
        filtered = self._remove_metadata_headers(filtered)
        
        # Clean up excessive whitespace
        filtered = self._normalize_whitespace(filtered)
        
        # Remove empty sections
        filtered = self._remove_empty_sections(filtered)
        
        return filtered.strip()
    
    def _remove_metadata_headers(self, text: str) -> str:
        """Remove YAML-style metadata headers."""
        # Remove YAML front matter
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                # Return content after front matter
                return parts[2]
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace while preserving structure."""
        # Replace multiple blank lines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        return '\n'.join(lines)
    
    def _remove_empty_sections(self, text: str) -> str:
        """Remove empty markdown sections."""
        # Pattern for empty sections (header followed by nothing or another header)
        empty_section_pattern = r'^(#{1,6}[^#\n]+)\n+(?=#{1,6}|$)'
        text = re.sub(empty_section_pattern, '', text, flags=re.MULTILINE)
        
        return text
    
    def extract_metadata(self, text: str) -> Tuple[str, Dict]:
        """
        Extract metadata from content while filtering.
        
        Args:
            text: Raw text with embedded metadata
            
        Returns:
            Tuple of (filtered_content, extracted_metadata)
        """
        metadata = {}
        
        # Extract confidence scores before removing them
        confidence_match = re.search(r'Confidence:\s*([\d.]+)', text, re.IGNORECASE)
        if confidence_match:
            metadata['confidence'] = float(confidence_match.group(1))
        
        # Extract model information
        model_match = re.search(r'Model:\s*([^\n]+)', text, re.IGNORECASE)
        if model_match:
            metadata['extraction_model'] = model_match.group(1).strip()
        
        # Extract component counts for network diagrams
        components_match = re.search(r'Components:\s*(\d+)', text, re.IGNORECASE)
        if components_match:
            metadata['component_count'] = int(components_match.group(1))
        
        connections_match = re.search(r'Connections:\s*(\d+)', text, re.IGNORECASE)
        if connections_match:
            metadata['connection_count'] = int(connections_match.group(1))
        
        # Extract diagram type
        type_match = re.search(r'Type:\s*([^\n]+)', text, re.IGNORECASE)
        if type_match:
            metadata['diagram_type'] = type_match.group(1).strip()
        
        # Now filter the content
        filtered_content = self.filter_content(text)
        
        return filtered_content, metadata
    
    def filter_mermaid_diagram(self, diagram: str) -> str:
        """
        Filter Mermaid diagram content specifically.
        
        Args:
            diagram: Mermaid diagram code
            
        Returns:
            Cleaned Mermaid diagram
        """
        if not diagram:
            return ""
        
        lines = diagram.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip comment lines with metadata
            if line.strip().startswith('%%'):
                # Keep structural comments but remove metadata comments
                if any(x in line.lower() for x in ['generated', 'confidence', 'model', 'timestamp']):
                    continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def filter_table_json(self, table_data: Dict) -> Dict:
        """
        Filter table JSON to remove non-source fields.
        
        Args:
            table_data: Table data dictionary
            
        Returns:
            Filtered table data
        """
        # Fields to remove from table data
        remove_fields = [
            'extraction_method',
            'extraction_timestamp', 
            'confidence_score',
            'processing_time',
            'model_used',
            'retry_count',
            'error_messages'
        ]
        
        filtered = {k: v for k, v in table_data.items() 
                   if k not in remove_fields}
        
        return filtered