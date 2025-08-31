"""
Metadata Enricher for Vector Database Integration

Enriches content with comprehensive metadata for improved
search, filtering, and retrieval in vector databases.
"""

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class MetadataEnricher:
    """Enrich content with metadata for vector databases."""
    
    def __init__(self):
        """Initialize metadata enricher."""
        self.entity_patterns = {
            'ip_addresses': r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b',
            'urls': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'dates': r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b',
            'mac_addresses': r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b',
            'ports': r'\b(?:port|Port)\s*(\d{1,5})\b',
            'protocols': r'\b(?:TCP|UDP|HTTP|HTTPS|SSH|FTP|SMTP|DNS|DHCP|ICMP|BGP|OSPF)\b',
            'vlans': r'\b(?:VLAN|vlan)\s*(\d{1,4})\b',
        }
    
    def enrich_document(self, 
                        content: str,
                        source_file: str,
                        page_count: int,
                        extraction_timestamp: Optional[str] = None,
                        additional_metadata: Optional[Dict] = None) -> Dict:
        """
        Enrich document with comprehensive metadata.
        
        Args:
            content: Document content
            source_file: Source PDF filename
            page_count: Total pages in document
            extraction_timestamp: When extraction occurred
            additional_metadata: Any additional metadata to include
            
        Returns:
            Complete metadata dictionary
        """
        metadata = {
            'source_file': source_file,
            'page_count': page_count,
            'extraction_timestamp': extraction_timestamp or datetime.utcnow().isoformat() + 'Z',
            'document_id': self._generate_document_id(source_file),
            'char_count': len(content),
            'word_count': len(content.split()),
            'line_count': content.count('\n') + 1,
        }
        
        # Extract entities
        entities = self.extract_entities(content)
        if entities:
            metadata['entities'] = entities
        
        # Detect content types
        content_types = self.detect_content_types(content)
        if content_types:
            metadata['content_types'] = content_types
        
        # Calculate quality metrics
        quality = self.calculate_quality_metrics(content)
        if quality:
            metadata['quality_metrics'] = quality
        
        # Add technical depth score
        metadata['technical_depth'] = self._calculate_technical_depth(content)
        
        # Merge additional metadata if provided
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return metadata
    
    def enrich_chunk(self,
                    chunk: str,
                    chunk_index: int,
                    document_id: str,
                    page_numbers: Optional[List[int]] = None,
                    chunk_metadata: Optional[Dict] = None) -> Dict:
        """
        Enrich a text chunk with metadata.
        
        Args:
            chunk: Chunk text content
            chunk_index: Index of chunk in document
            document_id: Parent document ID
            page_numbers: Page numbers this chunk spans
            chunk_metadata: Additional chunk-specific metadata
            
        Returns:
            Chunk metadata dictionary
        """
        metadata = {
            'chunk_id': f"{document_id}_chunk_{chunk_index:04d}",
            'chunk_index': chunk_index,
            'document_id': document_id,
            'char_count': len(chunk),
            'word_count': len(chunk.split()),
            'token_count': self._estimate_tokens(chunk),
        }
        
        if page_numbers:
            metadata['page_numbers'] = page_numbers
            metadata['page_span'] = len(page_numbers)
        
        # Extract chunk-specific entities
        entities = self.extract_entities(chunk)
        if entities:
            # Only include non-empty entity lists
            metadata['entities'] = {k: v for k, v in entities.items() if v}
        
        # Detect chunk content type
        content_type = self._detect_chunk_content_type(chunk)
        if content_type:
            metadata['content_type'] = content_type
        
        # Information density
        metadata['information_density'] = self._calculate_information_density(chunk)
        
        # Merge additional metadata
        if chunk_metadata:
            metadata.update(chunk_metadata)
        
        return metadata
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to extract entities from
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Deduplicate while preserving order
                unique_matches = []
                seen = set()
                for match in matches:
                    if match not in seen:
                        seen.add(match)
                        unique_matches.append(match)
                entities[entity_type] = unique_matches[:50]  # Limit to 50 per type
        
        # Extract technical terms
        technical_terms = self._extract_technical_terms(text)
        if technical_terms:
            entities['technical_terms'] = technical_terms[:50]
        
        return entities
    
    def detect_content_types(self, content: str) -> List[str]:
        """
        Detect types of content present in document.
        
        Args:
            content: Document content
            
        Returns:
            List of detected content types
        """
        types = []
        
        # Check for tables
        if '|' in content and re.search(r'\|.*\|.*\|', content):
            types.append('table')
        
        # Check for network diagrams (Mermaid)
        if '```mermaid' in content.lower() or 'graph ' in content:
            types.append('network_diagram')
        
        # Check for code blocks
        if '```' in content:
            types.append('code')
        
        # Check for lists
        if re.search(r'^\s*[-*+]\s+', content, re.MULTILINE):
            types.append('list')
        
        # Check for JSON data
        if re.search(r'\{[^}]*"[^"]*":[^}]*\}', content):
            types.append('json')
        
        # Check for configuration data
        if re.search(r'^\s*\w+\s*=\s*[\w"\']+', content, re.MULTILINE):
            types.append('configuration')
        
        # Always has text
        types.append('text')
        
        return list(set(types))  # Deduplicate
    
    def calculate_quality_metrics(self, content: str) -> Dict[str, float]:
        """
        Calculate content quality metrics.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary of quality metrics
        """
        metrics = {}
        
        # Completeness (based on sentence structure)
        complete_sentences = len(re.findall(r'[.!?]\s+[A-Z]', content))
        total_sentences = max(1, content.count('.') + content.count('!') + content.count('?'))
        metrics['completeness'] = min(1.0, complete_sentences / total_sentences)
        
        # Information density (unique words / total words)
        words = content.lower().split()
        if words:
            metrics['information_density'] = len(set(words)) / len(words)
        else:
            metrics['information_density'] = 0.0
        
        # Structure score (headers, lists, etc.)
        structure_elements = (
            content.count('#') +  # Headers
            content.count('- ') +  # Lists
            content.count('1. ') +  # Numbered lists
            content.count('```')  # Code blocks
        )
        metrics['structure_score'] = min(1.0, structure_elements / 100)
        
        # Readability (average sentence length)
        if complete_sentences > 0:
            avg_sentence_length = len(words) / complete_sentences
            # Optimal is around 15-20 words per sentence
            metrics['readability'] = max(0, min(1.0, 1.0 - abs(avg_sentence_length - 17.5) / 50))
        else:
            metrics['readability'] = 0.5
        
        return metrics
    
    def _generate_document_id(self, source_file: str) -> str:
        """Generate unique document ID."""
        # Use MD5 hash of filename + timestamp
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{source_file}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: ~4 characters per token
        return len(text) // 4
    
    def _detect_chunk_content_type(self, chunk: str) -> str:
        """Detect primary content type of a chunk."""
        if '```mermaid' in chunk.lower():
            return 'network_diagram'
        elif '```' in chunk:
            return 'code'
        elif re.search(r'\|.*\|.*\|', chunk):
            return 'table'
        elif re.search(r'\{[^}]*"[^"]*":[^}]*\}', chunk):
            return 'json'
        else:
            return 'text'
    
    def _calculate_information_density(self, text: str) -> float:
        """Calculate information density of text."""
        if not text:
            return 0.0
        
        words = text.lower().split()
        if not words:
            return 0.0
        
        # Ratio of unique words to total words
        unique_ratio = len(set(words)) / len(words)
        
        # Adjust for technical content (higher is better)
        technical_boost = min(0.2, len(self._extract_technical_terms(text)) * 0.01)
        
        return min(1.0, unique_ratio + technical_boost)
    
    def _calculate_technical_depth(self, content: str) -> float:
        """Calculate technical depth score."""
        technical_indicators = [
            r'\b\d+\.\d+\.\d+\.\d+\b',  # IP addresses
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+::\w+\b',  # Namespace notation
            r'\b0x[0-9A-Fa-f]+\b',  # Hex values
            r'\b\w+\(\)',  # Function calls
            r'[A-Z][a-z]+[A-Z]\w*',  # CamelCase
        ]
        
        score = 0
        for pattern in technical_indicators:
            matches = len(re.findall(pattern, content))
            score += min(matches, 10) * 0.1  # Cap contribution per pattern
        
        return min(1.0, score)
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text."""
        # Common technical terms and patterns
        technical_patterns = [
            r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b',  # Acronyms
            r'\b\w+[A-Z]\w+\b',  # CamelCase
            r'\b\w+_\w+\b',  # Snake_case
            r'\b\w+-\w+\b',  # Hyphenated terms
        ]
        
        terms = set()
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            terms.update(matches)
        
        # Filter out common words
        common_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        terms = [t for t in terms if t.lower() not in common_words and len(t) > 2]
        
        return list(terms)[:50]  # Limit to top 50