"""
Query Engine for NetIntel-OCR v0.1.12
Implements vector similarity search with filtering, reranking, and multiple output formats.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)


class SimilarityMetric(Enum):
    """Similarity metrics for vector search."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"


class OutputFormat(Enum):
    """Output formats for query results."""
    JSON = "json"
    MARKDOWN = "markdown"
    CSV = "csv"


@dataclass
class QueryChunk:
    """Represents a chunk returned from query."""
    id: str
    content: str
    similarity_score: float
    document_id: str
    source_file: str
    page_numbers: List[int]
    metadata: Dict[str, Any]
    

@dataclass
class QueryResult:
    """Result of a query operation."""
    query: str
    chunks: List[QueryChunk]
    total_results: int
    query_time_ms: float
    filters_applied: Dict[str, Any]
    reranked: bool


class QueryEngine:
    """Query engine for vector similarity search."""
    
    def __init__(self,
                 lancedb_path: Optional[str] = None,
                 lancedb_uri: Optional[str] = None,
                 embedding_model: str = "nomic-embed-text",
                 cache_enabled: bool = True):
        """
        Initialize query engine.
        
        Args:
            lancedb_path: Local path to LanceDB
            lancedb_uri: Remote URI for LanceDB (S3/MinIO)
            embedding_model: Model to use for query embeddings
            cache_enabled: Enable query result caching
        """
        self.lancedb_path = Path(lancedb_path) if lancedb_path else None
        self.lancedb_uri = lancedb_uri
        self.embedding_model = embedding_model
        self.cache_enabled = cache_enabled
        self.query_cache = {}
        
        # Load chunks if local path provided
        self.chunks = []
        if self.lancedb_path:
            self._load_chunks()
    
    def _load_chunks(self):
        """Load chunks from local database."""
        chunks_file = self._get_chunks_file()
        if chunks_file and chunks_file.exists():
            self.chunks = []
            with open(chunks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.chunks.append(json.loads(line))
            logger.info(f"Loaded {len(self.chunks)} chunks from {chunks_file}")
    
    def _get_chunks_file(self) -> Optional[Path]:
        """Get path to chunks file."""
        if not self.lancedb_path:
            return None
        
        # Check if it's a centralized database
        chunks_file = self.lancedb_path / "chunks.jsonl"
        if chunks_file.exists():
            return chunks_file
        
        # Check if it's a per-document database
        chunks_file = self.lancedb_path / "lancedb" / "chunks.jsonl"
        if chunks_file.exists():
            return chunks_file
        
        return None
    
    def query(self,
              query_text: str,
              limit: int = 10,
              filters: Optional[Dict[str, Any]] = None,
              rerank: bool = False,
              include_metadata: bool = True,
              similarity_metric: SimilarityMetric = SimilarityMetric.COSINE,
              similarity_threshold: float = 0.0) -> QueryResult:
        """
        Execute vector similarity search.
        
        Args:
            query_text: Natural language query
            limit: Maximum results to return
            filters: Metadata filters
            rerank: Apply reranking for better relevance
            include_metadata: Include chunk metadata in results
            similarity_metric: Similarity metric to use
            similarity_threshold: Minimum similarity score
            
        Returns:
            QueryResult with chunks, scores, and metadata
        """
        start_time = datetime.now()
        
        # Check cache
        cache_key = self._get_cache_key(query_text, limit, filters)
        if self.cache_enabled and cache_key in self.query_cache:
            logger.info(f"Cache hit for query: {query_text[:50]}...")
            cached_result = self.query_cache[cache_key]
            cached_result.query_time_ms = 0  # Indicate cache hit
            return cached_result
        
        # Generate query embedding
        query_embedding = self._generate_query_embedding(query_text)
        
        # Execute vector search
        candidates = self._vector_search(
            query_embedding,
            self.chunks,
            similarity_metric,
            limit * 3 if rerank else limit  # Get more candidates for reranking
        )
        
        # Apply filters
        if filters:
            candidates = self._apply_filters(candidates, filters)
        
        # Apply similarity threshold
        candidates = [c for c in candidates if c['score'] >= similarity_threshold]
        
        # Rerank if requested
        if rerank and candidates:
            candidates = self._rerank_results(query_text, candidates)
        
        # Limit results
        candidates = candidates[:limit]
        
        # Convert to QueryChunk objects
        chunks = []
        for candidate in candidates:
            chunk_data = candidate.get('chunk', {})
            chunks.append(QueryChunk(
                id=chunk_data.get('id', ''),
                content=chunk_data.get('content', ''),
                similarity_score=candidate.get('score', 0.0),
                document_id=chunk_data.get('document_id', ''),
                source_file=chunk_data.get('source_file', ''),
                page_numbers=chunk_data.get('page_numbers', []),
                metadata=chunk_data.get('metadata', {}) if include_metadata else {}
            ))
        
        # Calculate query time
        query_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Create result
        result = QueryResult(
            query=query_text,
            chunks=chunks,
            total_results=len(chunks),
            query_time_ms=query_time_ms,
            filters_applied=filters or {},
            reranked=rerank
        )
        
        # Cache result
        if self.cache_enabled:
            self.query_cache[cache_key] = result
        
        return result
    
    def _generate_query_embedding(self, query_text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for query text.
        
        Args:
            query_text: Query text
            
        Returns:
            Query embedding or None
        """
        # For now, return None - will be implemented with embedding_manager
        # In production, this would call the embedding manager
        logger.info(f"Generating embedding for query: {query_text[:50]}...")
        return None
    
    def _vector_search(self,
                      query_embedding: Optional[np.ndarray],
                      chunks: List[Dict],
                      similarity_metric: SimilarityMetric,
                      limit: int) -> List[Dict]:
        """
        Perform vector similarity search.
        
        Args:
            query_embedding: Query embedding
            chunks: Chunks to search
            similarity_metric: Similarity metric
            limit: Number of results
            
        Returns:
            List of candidates with scores
        """
        if query_embedding is None:
            # Fallback to keyword search if no embedding
            return self._keyword_search(chunks, limit)
        
        candidates = []
        
        for chunk in chunks:
            chunk_embedding = chunk.get('embedding')
            if chunk_embedding is None:
                continue
            
            # Calculate similarity
            score = self._calculate_similarity(
                query_embedding,
                np.array(chunk_embedding),
                similarity_metric
            )
            
            candidates.append({
                'chunk': chunk,
                'score': score
            })
        
        # Sort by score (descending)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates[:limit]
    
    def _keyword_search(self, chunks: List[Dict], limit: int) -> List[Dict]:
        """
        Fallback keyword search when embeddings not available.
        
        Args:
            chunks: Chunks to search
            limit: Number of results
            
        Returns:
            List of candidates with scores
        """
        # For demonstration, return random chunks
        # In production, this would implement actual keyword search
        import random
        sample_size = min(limit, len(chunks))
        sample_chunks = random.sample(chunks, sample_size) if chunks else []
        
        candidates = []
        for chunk in sample_chunks:
            candidates.append({
                'chunk': chunk,
                'score': random.random()  # Random score for demonstration
            })
        
        return candidates
    
    def _calculate_similarity(self,
                            vec1: np.ndarray,
                            vec2: np.ndarray,
                            metric: SimilarityMetric) -> float:
        """
        Calculate similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            metric: Similarity metric
            
        Returns:
            Similarity score
        """
        if metric == SimilarityMetric.COSINE:
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot_product / (norm1 * norm2))
        
        elif metric == SimilarityMetric.EUCLIDEAN:
            # Negative euclidean distance (closer = higher score)
            return float(-np.linalg.norm(vec1 - vec2))
        
        elif metric == SimilarityMetric.DOT:
            # Dot product
            return float(np.dot(vec1, vec2))
        
        return 0.0
    
    def _apply_filters(self,
                      candidates: List[Dict],
                      filters: Dict[str, Any]) -> List[Dict]:
        """
        Apply metadata filters to candidates.
        
        Args:
            candidates: Candidate chunks
            filters: Filter criteria
            
        Returns:
            Filtered candidates
        """
        filtered = []
        
        for candidate in candidates:
            chunk = candidate.get('chunk', {})
            metadata = chunk.get('metadata', {})
            
            # Check all filters
            passes_filters = True
            
            for key, value in filters.items():
                # Handle special filter operators
                if isinstance(value, dict):
                    if '$in' in value:
                        # Check if metadata value is in list
                        if metadata.get(key) not in value['$in']:
                            passes_filters = False
                            break
                    elif '$gte' in value:
                        # Greater than or equal
                        if metadata.get(key) < value['$gte']:
                            passes_filters = False
                            break
                    elif '$lte' in value:
                        # Less than or equal
                        if metadata.get(key) > value['$lte']:
                            passes_filters = False
                            break
                    elif '$contains' in value:
                        # Contains substring or element
                        metadata_value = metadata.get(key, '')
                        if isinstance(metadata_value, str):
                            if value['$contains'] not in metadata_value:
                                passes_filters = False
                                break
                        elif isinstance(metadata_value, list):
                            if value['$contains'] not in metadata_value:
                                passes_filters = False
                                break
                else:
                    # Exact match
                    if metadata.get(key) != value:
                        passes_filters = False
                        break
            
            if passes_filters:
                filtered.append(candidate)
        
        return filtered
    
    def _rerank_results(self,
                       query_text: str,
                       candidates: List[Dict]) -> List[Dict]:
        """
        Rerank results for better relevance.
        
        Args:
            query_text: Original query
            candidates: Candidate chunks
            
        Returns:
            Reranked candidates
        """
        # Simple keyword boost reranking
        query_terms = query_text.lower().split()
        
        for candidate in candidates:
            chunk_content = candidate.get('chunk', {}).get('content', '').lower()
            
            # Count query term occurrences
            term_count = sum(1 for term in query_terms if term in chunk_content)
            
            # Boost score based on term matches
            boost = 1.0 + (term_count * 0.1)
            candidate['score'] *= boost
        
        # Re-sort by boosted scores
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return candidates
    
    def _get_cache_key(self,
                      query_text: str,
                      limit: int,
                      filters: Optional[Dict]) -> str:
        """Generate cache key for query."""
        filter_str = json.dumps(filters, sort_keys=True) if filters else ""
        return f"{query_text}:{limit}:{filter_str}"
    
    def hybrid_query(self,
                    query_text: str,
                    keyword_query: Optional[str] = None,
                    vector_weight: float = 0.7,
                    keyword_weight: float = 0.3,
                    limit: int = 10) -> QueryResult:
        """
        Hybrid search combining vector and keyword search.
        
        Args:
            query_text: Vector search query
            keyword_query: Keyword search query (uses query_text if None)
            vector_weight: Weight for vector results
            keyword_weight: Weight for keyword results
            limit: Number of results
            
        Returns:
            Combined query results
        """
        keyword_query = keyword_query or query_text
        
        # Get vector results
        vector_results = self.query(query_text, limit=limit * 2)
        
        # Get keyword results
        keyword_results = self._keyword_only_search(keyword_query, limit * 2)
        
        # Combine and reweight scores
        combined_scores = {}
        
        for chunk in vector_results.chunks:
            combined_scores[chunk.id] = {
                'chunk': chunk,
                'score': chunk.similarity_score * vector_weight
            }
        
        for chunk in keyword_results:
            chunk_id = chunk.get('id')
            if chunk_id in combined_scores:
                combined_scores[chunk_id]['score'] += chunk.get('score', 0) * keyword_weight
            else:
                combined_scores[chunk_id] = {
                    'chunk': self._dict_to_chunk(chunk),
                    'score': chunk.get('score', 0) * keyword_weight
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:limit]
        
        # Create result
        chunks = [r['chunk'] for r in sorted_results]
        
        return QueryResult(
            query=f"hybrid: {query_text}",
            chunks=chunks,
            total_results=len(chunks),
            query_time_ms=0,
            filters_applied={},
            reranked=False
        )
    
    def _keyword_only_search(self, query_text: str, limit: int) -> List[Dict]:
        """
        Keyword-only search.
        
        Args:
            query_text: Search query
            limit: Number of results
            
        Returns:
            Matching chunks
        """
        query_terms = query_text.lower().split()
        results = []
        
        for chunk in self.chunks:
            content = chunk.get('content', '').lower()
            
            # Score based on term matches
            score = sum(1 for term in query_terms if term in content) / len(query_terms)
            
            if score > 0:
                results.append({
                    'id': chunk.get('id'),
                    'content': chunk.get('content'),
                    'score': score,
                    'source_file': chunk.get('source_file'),
                    'page_numbers': chunk.get('page_numbers', []),
                    'metadata': chunk.get('metadata', {})
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:limit]
    
    def _dict_to_chunk(self, chunk_dict: Dict) -> QueryChunk:
        """Convert dictionary to QueryChunk."""
        return QueryChunk(
            id=chunk_dict.get('id', ''),
            content=chunk_dict.get('content', ''),
            similarity_score=chunk_dict.get('score', 0.0),
            document_id=chunk_dict.get('metadata', {}).get('document_id', ''),
            source_file=chunk_dict.get('source_file', ''),
            page_numbers=chunk_dict.get('page_numbers', []),
            metadata=chunk_dict.get('metadata', {})
        )
    
    def multi_query(self,
                   queries: List[str],
                   aggregation: str = "reciprocal_rank_fusion",
                   limit: int = 10) -> QueryResult:
        """
        Execute multiple queries and aggregate results.
        
        Args:
            queries: List of queries
            aggregation: Aggregation method
            limit: Number of results
            
        Returns:
            Aggregated query results
        """
        all_results = []
        
        # Execute all queries
        for query in queries:
            result = self.query(query, limit=limit * 2)
            all_results.append(result)
        
        # Aggregate results
        if aggregation == "reciprocal_rank_fusion":
            aggregated = self._reciprocal_rank_fusion(all_results, limit)
        else:
            # Default to first query results
            aggregated = all_results[0].chunks[:limit] if all_results else []
        
        return QueryResult(
            query=f"multi: {', '.join(queries)}",
            chunks=aggregated,
            total_results=len(aggregated),
            query_time_ms=sum(r.query_time_ms for r in all_results),
            filters_applied={},
            reranked=False
        )
    
    def _reciprocal_rank_fusion(self,
                               results: List[QueryResult],
                               limit: int) -> List[QueryChunk]:
        """
        Reciprocal rank fusion aggregation.
        
        Args:
            results: Query results to aggregate
            limit: Number of results
            
        Returns:
            Aggregated chunks
        """
        scores = {}
        
        for result in results:
            for rank, chunk in enumerate(result.chunks):
                chunk_id = chunk.id
                if chunk_id not in scores:
                    scores[chunk_id] = {'chunk': chunk, 'score': 0}
                
                # Reciprocal rank scoring
                scores[chunk_id]['score'] += 1.0 / (rank + 1)
        
        # Sort by aggregated score
        sorted_chunks = sorted(
            scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:limit]
        
        return [item['chunk'] for item in sorted_chunks]
    
    def find_similar(self,
                    document_id: str,
                    limit: int = 10,
                    min_similarity: float = 0.0) -> QueryResult:
        """
        Find documents similar to a reference document.
        
        Args:
            document_id: Reference document ID
            limit: Number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            Similar documents
        """
        # Find reference document chunks
        ref_chunks = [c for c in self.chunks 
                     if c.get('metadata', {}).get('document_id') == document_id]
        
        if not ref_chunks:
            return QueryResult(
                query=f"similar to: {document_id}",
                chunks=[],
                total_results=0,
                query_time_ms=0,
                filters_applied={},
                reranked=False
            )
        
        # Use first chunk content as query
        ref_content = ref_chunks[0].get('content', '')
        
        # Query for similar content
        return self.query(
            ref_content,
            limit=limit,
            filters={'document_id': {'$ne': document_id}},  # Exclude reference doc
            similarity_threshold=min_similarity
        )
    
    def format_results(self,
                      result: QueryResult,
                      format: OutputFormat) -> str:
        """
        Format query results.
        
        Args:
            result: Query results
            format: Output format
            
        Returns:
            Formatted results
        """
        if format == OutputFormat.JSON:
            return json.dumps({
                'query': result.query,
                'total_results': result.total_results,
                'query_time_ms': result.query_time_ms,
                'results': [asdict(chunk) for chunk in result.chunks]
            }, indent=2)
        
        elif format == OutputFormat.MARKDOWN:
            md = f"# Query Results\n\n"
            md += f"**Query**: {result.query}\n"
            md += f"**Results**: {result.total_results}\n"
            md += f"**Time**: {result.query_time_ms:.2f}ms\n\n"
            
            for i, chunk in enumerate(result.chunks, 1):
                md += f"## Result {i} (Score: {chunk.similarity_score:.3f})\n"
                md += f"**Source**: {chunk.source_file}"
                if chunk.page_numbers:
                    md += f" (Pages: {', '.join(map(str, chunk.page_numbers))})"
                md += f"\n\n{chunk.content}\n\n---\n\n"
            
            return md
        
        elif format == OutputFormat.CSV:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['chunk_id', 'score', 'source_file', 'pages', 'content_preview'])
            
            # Data
            for chunk in result.chunks:
                content_preview = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
                pages = ','.join(map(str, chunk.page_numbers))
                writer.writerow([
                    chunk.id,
                    f"{chunk.similarity_score:.3f}",
                    chunk.source_file,
                    pages,
                    content_preview
                ])
            
            return output.getvalue()
        
        return str(result)