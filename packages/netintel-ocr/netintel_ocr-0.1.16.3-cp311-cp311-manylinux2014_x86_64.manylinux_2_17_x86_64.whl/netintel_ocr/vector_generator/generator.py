"""
Main Vector Generator for NetIntel-OCR v0.1.7

Orchestrates vector database optimization by coordinating all
sub-components to create LanceDB-ready output by default.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .content_filter import ContentFilter
from .json_flattener import JSONFlattener
from .markdown_optimizer import MarkdownOptimizer
from .metadata_enricher import MetadataEnricher
from .chunker import Chunker
from .schema_generator import SchemaGenerator


class VectorGenerator:
    """Generate vector database optimized output from extracted content."""
    
    def __init__(self,
                 output_dir: str,
                 vector_format: str = "lancedb",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 100,
                 chunk_strategy: str = "semantic",
                 array_strategy: str = "separate_rows",
                 create_chunks: bool = True,
                 include_extended_metadata: bool = False,
                 embedding_model: str = "qwen3-embedding:4b",
                 embedding_provider: str = "ollama"):
        """
        Initialize Vector Generator.
        
        Args:
            output_dir: Base output directory for vector files
            vector_format: Target vector database format
            chunk_size: Chunk size in tokens
            chunk_overlap: Overlap between chunks
            chunk_strategy: Chunking strategy
            array_strategy: How to handle arrays in JSON
            create_chunks: Whether to create chunks.jsonl
            include_extended_metadata: Include extended metadata (reduces content space)
            embedding_model: Embedding model to use (default: qwen3-embedding:4b)
            embedding_provider: Provider for embeddings (default: ollama)
        """
        self.output_dir = Path(output_dir)
        self.vector_format = vector_format
        self.create_chunks = create_chunks
        self.embedding_model = embedding_model
        self.embedding_provider = embedding_provider
        
        # Initialize components
        self.content_filter = ContentFilter()
        self.json_flattener = JSONFlattener(array_strategy=array_strategy)
        self.markdown_optimizer = MarkdownOptimizer()
        self.metadata_enricher = MetadataEnricher()
        self.chunker = Chunker(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            strategy=chunk_strategy,
            include_extended_metadata=include_extended_metadata
        )
        self.schema_generator = SchemaGenerator(
            vector_format=vector_format,
            embedding_model=embedding_model,
            embedding_provider=embedding_provider
        )
        
        # Create necessary directories
        self._setup_directories()
    
    def _setup_directories(self):
        """Create vector output directories."""
        # Create main directories
        (self.output_dir / "markdown").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "lancedb").mkdir(parents=True, exist_ok=True)
        (self.output_dir / ".vector_cache").mkdir(parents=True, exist_ok=True)
    
    def process_merged_document(self,
                               merged_markdown_path: str,
                               source_file: str,
                               page_count: int,
                               tables: Optional[List[Dict]] = None,
                               diagrams: Optional[List[Dict]] = None) -> Dict:
        """
        Process merged document to create vector-optimized output.
        
        This is the main entry point called after all pages are processed
        and merged into document.md. It creates document-vector.md and
        all LanceDB-ready files.
        
        Args:
            merged_markdown_path: Path to merged document.md
            source_file: Original PDF filename
            page_count: Total pages in document
            tables: List of extracted tables from all pages
            diagrams: List of extracted network diagrams from all pages
            
        Returns:
            Dictionary with paths to generated files
        """
        print(f"🔄 Generating vector files for {source_file}...")
        
        # Read merged document
        with open(merged_markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Step 1: Filter content to remove artifacts
        filtered_content, extracted_metadata = self.content_filter.extract_metadata(content)
        
        # Step 2: Process tables if present
        flattened_tables = None
        if tables:
            flattened_tables = self._process_tables(tables)
        
        # Step 3: Process diagrams if present
        flattened_diagrams = None
        if diagrams:
            flattened_diagrams = self._process_diagrams(diagrams)
        
        # Step 4: Create vector-optimized markdown
        vector_markdown = self._create_vector_markdown(
            filtered_content,
            flattened_tables,
            flattened_diagrams,
            source_file,
            page_count,
            extracted_metadata
        )
        
        # Step 5: Save vector markdown
        vector_markdown_path = self.output_dir / "markdown" / "document-vector.md"
        with open(vector_markdown_path, 'w', encoding='utf-8') as f:
            f.write(vector_markdown)
        
        # Step 6: Generate chunks if enabled
        chunks_path = None
        chunk_count = 0
        if self.create_chunks:
            chunks_path, chunk_count = self._create_chunks(
                vector_markdown,
                source_file,
                page_count
            )
        
        # Step 7: Generate metadata files
        metadata_files = self._generate_metadata_files(
            source_file,
            page_count,
            chunk_count,
            flattened_tables is not None,
            flattened_diagrams is not None
        )
        
        # Step 8: Save flattened tables if present
        if flattened_tables:
            self._save_flattened_tables(flattened_tables)
        
        print(f"✅ Vector files generated successfully")
        
        return {
            "vector_markdown": str(vector_markdown_path),
            "chunks": chunks_path,
            "metadata": metadata_files,
            "tables": flattened_tables is not None
        }
    
    def _process_tables(self, tables: List[Dict]) -> List[Dict]:
        """Process and flatten tables."""
        flattened_tables = []
        
        for table in tables:
            # Filter non-source content
            filtered_table = self.content_filter.filter_table_json(table)
            
            # Flatten structure
            if 'data' in filtered_table:
                flattened = self.json_flattener.flatten_table(filtered_table['data'])
            else:
                flattened = self.json_flattener.flatten_table(filtered_table)
            
            flattened_tables.append({
                'original': filtered_table,
                'flattened_data': flattened,
                'metadata': table.get('metadata', {})
            })
        
        return flattened_tables
    
    def _process_diagrams(self, diagrams: List[Dict]) -> List[Dict]:
        """Process and flatten network diagrams."""
        flattened_diagrams = []
        
        for diagram in diagrams:
            # Filter Mermaid code if present
            if 'mermaid_code' in diagram:
                diagram['mermaid_code'] = self.content_filter.filter_mermaid_diagram(
                    diagram['mermaid_code']
                )
            
            # Flatten structure
            if 'data' in diagram:
                flattened = self.json_flattener.flatten_network_diagram(diagram['data'])
            else:
                flattened = self.json_flattener.flatten_network_diagram(diagram)
            
            flattened_diagrams.append({
                'type': diagram.get('type', 'network_topology'),
                'flattened_data': flattened,
                'mermaid_code': diagram.get('mermaid_code', ''),
                'component_count': diagram.get('component_count', 0),
                'connection_count': diagram.get('connection_count', 0)
            })
        
        return flattened_diagrams
    
    def _create_vector_markdown(self,
                                filtered_content: str,
                                flattened_tables: Optional[List[Dict]],
                                flattened_diagrams: Optional[List[Dict]],
                                source_file: str,
                                page_count: int,
                                extracted_metadata: Dict) -> str:
        """Create vector-optimized markdown document."""
        # Enrich with document metadata
        document_metadata = self.metadata_enricher.enrich_document(
            filtered_content,
            source_file,
            page_count,
            additional_metadata=extracted_metadata
        )
        
        # Create optimized markdown
        vector_markdown = self.markdown_optimizer.create_vector_markdown(
            text_content=filtered_content,
            tables=flattened_tables,
            diagrams=flattened_diagrams,
            metadata=document_metadata
        )
        
        return vector_markdown
    
    def _create_chunks(self,
                      vector_markdown: str,
                      source_file: str,
                      page_count: int) -> Tuple[str, int]:
        """Create chunks for vector database with comprehensive metadata.
        
        Returns:
            Tuple of (chunks_path, chunk_count)
        """
        import hashlib
        from pathlib import Path
        
        # Generate document ID
        document_id = self.metadata_enricher._generate_document_id(source_file)
        
        # Calculate MD5 of source file for integrity
        source_path = Path(source_file)
        md5_hash = hashlib.md5()
        if source_path.exists():
            with open(source_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            md5_checksum = md5_hash.hexdigest()
            file_size = source_path.stat().st_size
        else:
            md5_checksum = document_id  # Use document ID if file not found
            file_size = 0
        
        # Create comprehensive document metadata for source-of-truth tracking
        doc_metadata = {
            'source_file': source_file,
            'source_path': str(source_path.absolute()) if source_path.exists() else source_file,
            'md5_checksum': md5_checksum,
            'file_size': file_size,
            'page_count': page_count,
            'extraction_timestamp': datetime.utcnow().isoformat() + 'Z',
            'models_used': {
                'text_extraction': 'nanonets-ocr-s:latest',  # TODO: Pass from processor
                'network_detection': 'qwen2.5vl:latest',  # TODO: Pass from processor
            }
        }
        
        # Generate chunks
        chunks = self.chunker.chunk_document(
            vector_markdown,
            document_id,
            doc_metadata
        )
        
        # Enrich chunk metadata
        for i, chunk in enumerate(chunks):
            chunk_text = chunk['content']
            # Use index from enumerate, not from chunk dict
            chunk_metadata = self.metadata_enricher.enrich_chunk(
                chunk_text,
                i,
                document_id
            )
            # Only update metadata if it exists in chunk
            if 'metadata' in chunk:
                chunk['metadata'].update(chunk_metadata)
            else:
                chunk['metadata'] = chunk_metadata
        
        # Save chunks as JSONL
        chunks_path = self.output_dir / "lancedb" / "chunks.jsonl"
        jsonl_content = self.chunker.create_chunks_jsonl(chunks)
        
        with open(chunks_path, 'w', encoding='utf-8') as f:
            f.write(jsonl_content)
        
        # Save chunk mapping for reference
        chunk_map = {
            'document_id': document_id,
            'total_chunks': len(chunks),
            'chunk_indices': list(range(len(chunks)))
        }
        
        map_path = self.output_dir / ".vector_cache" / "chunks_map.json"
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(chunk_map, f, indent=2)
        
        return str(chunks_path), len(chunks)
    
    def _generate_metadata_files(self,
                                 source_file: str,
                                 page_count: int,
                                 chunk_count: int,
                                 has_tables: bool,
                                 has_diagrams: bool) -> Dict[str, str]:
        """Generate all metadata files for vector database."""
        metadata_files = {}
        
        # Generate main metadata
        metadata = {
            'source_file': source_file,
            'page_count': page_count,
            'chunk_count': chunk_count,
            'has_tables': has_tables,
            'has_diagrams': has_diagrams,
            'extraction_timestamp': datetime.utcnow().isoformat() + 'Z',
            'vector_format': self.vector_format,
            'chunk_config': {
                'size': self.chunker.chunk_size,
                'overlap': self.chunker.chunk_overlap,
                'strategy': self.chunker.strategy
            }
        }
        
        metadata_path = self.output_dir / "lancedb" / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        metadata_files['metadata'] = str(metadata_path)
        
        # Generate schema
        schema = self.schema_generator.generate_schema()
        schema_path = self.output_dir / "lancedb" / "schema.json"
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
        metadata_files['schema'] = str(schema_path)
        
        # Generate embeddings config
        embeddings_config = self.schema_generator.generate_embeddings_config()
        embed_path = self.output_dir / "lancedb" / "embeddings_config.json"
        with open(embed_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_config, f, indent=2)
        metadata_files['embeddings_config'] = str(embed_path)
        
        # Generate index config
        index_config = self.schema_generator.generate_index_config()
        index_path = self.output_dir / "lancedb" / "index_config.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_config, f, indent=2)
        metadata_files['index_config'] = str(index_path)
        
        return metadata_files
    
    def _save_flattened_tables(self, flattened_tables: List[Dict]):
        """Save flattened tables for vector database."""
        tables_dir = self.output_dir / "tables"
        tables_dir.mkdir(exist_ok=True)
        
        # Save as JSONL for easy ingestion
        tables_path = tables_dir / "tables_flat.jsonl"
        
        with open(tables_path, 'w', encoding='utf-8') as f:
            for table in flattened_tables:
                if isinstance(table['flattened_data'], list):
                    # Multiple rows
                    for row in table['flattened_data']:
                        f.write(json.dumps(row, ensure_ascii=False) + '\n')
                else:
                    # Single flattened structure
                    f.write(json.dumps(table['flattened_data'], ensure_ascii=False) + '\n')
        
        # Generate table schema
        sample_data = []
        for table in flattened_tables:
            if isinstance(table['flattened_data'], list):
                sample_data.extend(table['flattened_data'][:5])
            else:
                sample_data.append(table['flattened_data'])
        
        if sample_data:
            table_schema = self.schema_generator.generate_table_schema(sample_data)
            schema_path = tables_dir / "schema.json"
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(table_schema, f, indent=2)
    
    def generate_processing_metrics(self, 
                                   start_time: datetime,
                                   end_time: datetime,
                                   pages_processed: int,
                                   chunks_created: int) -> Dict:
        """Generate processing metrics for monitoring."""
        duration = (end_time - start_time).total_seconds()
        
        metrics = {
            'processing_metrics': {
                'pages_processed': pages_processed,
                'vector_files_created': 1,
                'total_chunks_generated': chunks_created,
                'processing_time_seconds': duration,
                'pages_per_second': pages_processed / duration if duration > 0 else 0
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        metrics_path = self.output_dir / ".vector_cache" / "processing_metrics.json"
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics