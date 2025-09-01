"""
Chunker for Vector Database Integration

Creates optimized chunks for vector databases, especially LanceDB,
with configurable size, overlap, and chunking strategies.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    content: str
    index: int
    start_char: int
    end_char: int
    page_numbers: List[int]
    metadata: Dict


class Chunker:
    """Create optimized chunks for vector databases."""
    
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 100,
                 strategy: str = "semantic",
                 include_extended_metadata: bool = False):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size in tokens (approximate)
            chunk_overlap: Overlap between chunks in tokens
            strategy: Chunking strategy - "semantic", "fixed", "sentence"
            include_extended_metadata: Include comprehensive metadata (reduces content space)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self.include_extended_metadata = include_extended_metadata
        
        # Approximate tokens per character (rough estimate)
        self.chars_per_token = 4
    
    def chunk_document(self, 
                      content: str,
                      document_id: str,
                      metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Chunk a document into vector-ready chunks.
        
        Args:
            content: Document content to chunk
            document_id: Unique document identifier
            metadata: Document-level metadata
            
        Returns:
            List of chunk dictionaries ready for vector database
        """
        if self.strategy == "semantic":
            chunks = self._semantic_chunking(content)
        elif self.strategy == "sentence":
            chunks = self._sentence_chunking(content)
        else:
            chunks = self._fixed_chunking(content)
        
        # Format chunks for vector database
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_dict = self._format_chunk(
                chunk=chunk,
                index=i,
                document_id=document_id,
                document_metadata=metadata
            )
            formatted_chunks.append(chunk_dict)
        
        return formatted_chunks
    
    def _semantic_chunking(self, content: str) -> List[Chunk]:
        """
        Chunk based on semantic boundaries (paragraphs, sections).
        
        Args:
            content: Content to chunk
            
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        # Split by major sections (headers)
        sections = self._split_by_headers(content)
        
        current_pos = 0
        for section in sections:
            section_start = content.find(section, current_pos)
            if section_start == -1:
                continue
            
            # If section is too large, split further
            if self._estimate_tokens(section) > self.chunk_size:
                # Split by paragraphs
                sub_chunks = self._split_large_section(section, section_start)
                chunks.extend(sub_chunks)
            else:
                # Check if we can combine with previous chunk
                if chunks and self._can_combine(chunks[-1], section):
                    # Extend previous chunk
                    chunks[-1].content += "\n\n" + section
                    chunks[-1].end_char = section_start + len(section)
                else:
                    # Create new chunk
                    chunk = Chunk(
                        content=section,
                        index=len(chunks),
                        start_char=section_start,
                        end_char=section_start + len(section),
                        page_numbers=[],  # Will be filled later
                        metadata={}
                    )
                    chunks.append(chunk)
            
            current_pos = section_start + len(section)
        
        # Add overlap between chunks
        chunks = self._add_overlap(chunks, content)
        
        return chunks
    
    def _sentence_chunking(self, content: str) -> List[Chunk]:
        """
        Chunk based on sentence boundaries.
        
        Args:
            content: Content to chunk
            
        Returns:
            List of Chunk objects
        """
        chunks = []
        sentences = self._split_into_sentences(content)
        
        current_chunk = []
        current_size = 0
        chunk_start = 0
        
        for sent_idx, sentence in enumerate(sentences):
            sent_tokens = self._estimate_tokens(sentence)
            
            if current_size + sent_tokens > self.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_content = ' '.join(current_chunk)
                chunk = Chunk(
                    content=chunk_content,
                    index=len(chunks),
                    start_char=chunk_start,
                    end_char=chunk_start + len(chunk_content),
                    page_numbers=[],
                    metadata={}
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_size = sum(self._estimate_tokens(s) for s in current_chunk)
                chunk_start = content.find(overlap_sentences[0] if overlap_sentences else sentence, 
                                         chunk_start)
            else:
                current_chunk.append(sentence)
                current_size += sent_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk = Chunk(
                content=chunk_content,
                index=len(chunks),
                start_char=chunk_start,
                end_char=chunk_start + len(chunk_content),
                page_numbers=[],
                metadata={}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _fixed_chunking(self, content: str) -> List[Chunk]:
        """
        Fixed-size chunking with overlap.
        
        Args:
            content: Content to chunk
            
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        chunk_size_chars = self.chunk_size * self.chars_per_token
        overlap_chars = self.chunk_overlap * self.chars_per_token
        
        start = 0
        while start < len(content):
            end = min(start + chunk_size_chars, len(content))
            
            # Try to break at word boundary
            if end < len(content):
                last_space = content.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_content = content[start:end]
            
            chunk = Chunk(
                content=chunk_content,
                index=len(chunks),
                start_char=start,
                end_char=end,
                page_numbers=[],
                metadata={}
            )
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap_chars if end < len(content) else end
        
        return chunks
    
    def _split_by_headers(self, content: str) -> List[str]:
        """Split content by markdown headers."""
        # Pattern to match markdown headers
        header_pattern = r'^#{1,6}\s+.*$'
        
        sections = []
        current_section = []
        lines = content.split('\n')
        
        for line in lines:
            if re.match(header_pattern, line):
                # Save previous section
                if current_section:
                    sections.append('\n'.join(current_section))
                # Start new section with header
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _split_large_section(self, section: str, start_pos: int) -> List[Chunk]:
        """Split a large section into smaller chunks."""
        chunks = []
        
        # Split by paragraphs (double newline)
        paragraphs = section.split('\n\n')
        
        current_chunk = []
        current_size = 0
        chunk_start = start_pos
        
        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)
            
            if current_size + para_tokens > self.chunk_size and current_chunk:
                # Create chunk
                chunk_content = '\n\n'.join(current_chunk)
                chunk = Chunk(
                    content=chunk_content,
                    index=len(chunks),
                    start_char=chunk_start,
                    end_char=chunk_start + len(chunk_content),
                    page_numbers=[],
                    metadata={}
                )
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk = [para]
                current_size = para_tokens
                chunk_start += len(chunk_content) + 2  # +2 for \n\n
            else:
                current_chunk.append(para)
                current_size += para_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunk = Chunk(
                content=chunk_content,
                index=len(chunks),
                start_char=chunk_start,
                end_char=chunk_start + len(chunk_content),
                page_numbers=[],
                metadata={}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // self.chars_per_token
    
    def _can_combine(self, chunk: Chunk, new_content: str) -> bool:
        """Check if new content can be combined with existing chunk."""
        combined_tokens = self._estimate_tokens(chunk.content + new_content)
        return combined_tokens <= self.chunk_size * 1.2  # Allow 20% overflow
    
    def _add_overlap(self, chunks: List[Chunk], full_content: str) -> List[Chunk]:
        """Add overlap between chunks."""
        if self.chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks
        
        for i in range(1, len(chunks)):
            # Get overlap from previous chunk
            prev_chunk = chunks[i - 1]
            overlap_text = self._get_overlap_text(prev_chunk.content, self.chunk_overlap)
            
            if overlap_text:
                # Prepend overlap to current chunk
                chunks[i].content = overlap_text + "\n\n" + chunks[i].content
        
        return chunks
    
    def _get_overlap_text(self, content: str, overlap_tokens: int) -> str:
        """Get overlap text from end of content."""
        overlap_chars = overlap_tokens * self.chars_per_token
        
        if len(content) <= overlap_chars:
            return content
        
        # Try to break at sentence boundary
        overlap_start = len(content) - overlap_chars
        next_sentence = content.find('. ', overlap_start)
        
        if next_sentence != -1 and next_sentence < len(content) - 1:
            return content[next_sentence + 2:]
        
        return content[-overlap_chars:]
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap."""
        if not sentences:
            return []
        
        overlap_size = 0
        overlap_sentences = []
        
        # Take sentences from end until we reach overlap size
        for sent in reversed(sentences):
            overlap_size += self._estimate_tokens(sent)
            overlap_sentences.insert(0, sent)
            
            if overlap_size >= self.chunk_overlap:
                break
        
        return overlap_sentences
    
    def _format_chunk(self, 
                     chunk: Chunk,
                     index: int,
                     document_id: str,
                     document_metadata: Optional[Dict] = None) -> Dict:
        """
        Format chunk for vector database ingestion with MINIMAL metadata.
        
        Optimized to maximize content space while preserving essential metadata
        for source-of-truth tracking and filtering.
        
        Args:
            chunk: Chunk object
            index: Chunk index
            document_id: Document identifier
            document_metadata: Document-level metadata
            
        Returns:
            Formatted chunk dictionary with minimal essential metadata
        """
        # ULTRA-MINIMAL structure - only source filename, page numbers, and date indexed
        chunk_dict = {
            'id': f"{document_id}_chunk_{index:04d}",
            'content': chunk.content,  # MAXIMIZE space for actual content
            'source_file': document_metadata.get('source_file') if document_metadata else None,
            'page_numbers': chunk.page_numbers if chunk.page_numbers else [],  # Essential for source location
            'indexed_at': document_metadata.get('extraction_timestamp') if document_metadata else None,
        }
        
        # Only add extended metadata if explicitly requested
        if self.include_extended_metadata:
            chunk_dict['document_id'] = document_id
            chunk_dict['chunk_index'] = index
            chunk_dict['metadata'] = {
                'start_char': chunk.start_char,
                'end_char': chunk.end_char,
            }
        
        # Placeholder for embeddings (required by vector DBs)
        chunk_dict['embedding'] = None
        
        return chunk_dict
    
    def create_chunks_jsonl(self, chunks: List[Dict]) -> str:
        """
        Create JSONL format for chunks (one JSON object per line).
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            JSONL string
        """
        lines = []
        for chunk in chunks:
            lines.append(json.dumps(chunk, ensure_ascii=False))
        
        return '\n'.join(lines)