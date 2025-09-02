"""
Vector Regenerator for NetIntel-OCR

Regenerates vector database files from existing markdown output
without re-processing the PDF.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
import glob

from .vector_generator import VectorGenerator


def find_markdown_output(pdf_path: str, output_dir: str) -> Optional[Path]:
    """
    Find the existing markdown output for a given PDF.
    
    Args:
        pdf_path: Path to the original PDF file
        output_dir: Base output directory
        
    Returns:
        Path to the merged markdown file if found, None otherwise
    """
    # Calculate MD5 of the PDF
    md5_hash = hashlib.md5()
    
    try:
        with open(pdf_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        md5_checksum = md5_hash.hexdigest()
    except FileNotFoundError:
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return None
    
    # Look for the markdown in the MD5-based directory
    output_path = Path(output_dir) / md5_checksum
    
    # Look for the merged markdown file
    markdown_dir = output_path / "markdown"
    if not markdown_dir.exists():
        # Try legacy location (direct in output folder)
        legacy_markdown = output_path / "document.md"
        if legacy_markdown.exists():
            return legacy_markdown
        
        # Try to find any .md file that matches the PDF name
        pdf_name = Path(pdf_path).stem
        potential_files = [
            output_path / f"{pdf_name}.md",
            output_path / "merged.md",
            output_path / "document.md"
        ]
        
        for file in potential_files:
            if file.exists():
                return file
        
        return None
    
    # Look for merged file in markdown directory
    merged_files = list(markdown_dir.glob("*.md"))
    
    # Filter out document-vector.md if it exists
    merged_files = [f for f in merged_files if not f.name.endswith("-vector.md")]
    
    if merged_files:
        # Prefer file matching PDF name
        pdf_name = Path(pdf_path).stem
        for file in merged_files:
            if file.stem == pdf_name:
                return file
        
        # Otherwise return the first markdown file
        return merged_files[0]
    
    return None


def find_table_json_files(output_path: Path) -> List[Dict]:
    """
    Find and load any extracted table JSON files.
    
    Args:
        output_path: Path to the document output directory
        
    Returns:
        List of table dictionaries
    """
    tables = []
    
    # Check for tables directory
    tables_dir = output_path / "tables"
    if tables_dir.exists():
        # Load all JSON files in tables directory
        for json_file in tables_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    table_data = json.load(f)
                    
                    # Handle both single table and list of tables
                    if isinstance(table_data, list):
                        tables.extend(table_data)
                    else:
                        tables.append(table_data)
            except Exception as e:
                print(f"⚠️  Warning: Could not load table file {json_file}: {e}")
    
    return tables


def find_diagram_json_files(output_path: Path) -> List[Dict]:
    """
    Find and load any extracted network diagram JSON files.
    
    Args:
        output_path: Path to the document output directory
        
    Returns:
        List of diagram dictionaries
    """
    diagrams = []
    
    # Check for diagrams directory
    diagrams_dir = output_path / "diagrams"
    if diagrams_dir.exists():
        # Load all JSON files in diagrams directory
        for json_file in diagrams_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    diagram_data = json.load(f)
                    
                    # Handle both single diagram and list of diagrams
                    if isinstance(diagram_data, list):
                        diagrams.extend(diagram_data)
                    else:
                        diagrams.append(diagram_data)
            except Exception as e:
                print(f"⚠️  Warning: Could not load diagram file {json_file}: {e}")
    
    return diagrams


def regenerate_vectors(
    pdf_path: str,
    output_dir: str = "output",
    vector_format: str = "lancedb",
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    chunk_strategy: str = "semantic",
    array_strategy: str = "separate_rows",
    include_extended_metadata: bool = False,
    embedding_model: str = "qwen3-embedding:4b",
    embedding_provider: str = "ollama",
    debug: bool = False,
    quiet: bool = True
) -> bool:
    """
    Regenerate vector files from existing markdown output.
    
    Args:
        pdf_path: Path to the original PDF file
        output_dir: Base output directory
        vector_format: Target vector database format
        chunk_size: Chunk size in tokens
        chunk_overlap: Overlap between chunks
        chunk_strategy: Chunking strategy
        array_strategy: How to handle arrays in JSON
        include_extended_metadata: Include extended metadata
        debug: Enable debug output
        quiet: Suppress output
        
    Returns:
        True if successful, False otherwise
    """
    if not quiet:
        print(f"🔄 Regenerating vector files for: {pdf_path}")
    
    # Find the existing markdown output
    markdown_path = find_markdown_output(pdf_path, output_dir)
    
    if not markdown_path:
        print(f"❌ Error: No existing markdown output found for {pdf_path}")
        print(f"   Searched in: {output_dir}")
        print(f"   Please process the PDF first using: netintel-ocr \"{pdf_path}\"")
        return False
    
    if not quiet:
        print(f"✅ Found existing markdown: {markdown_path}")
    
    # Get the output directory for this document
    output_path = markdown_path.parent.parent if markdown_path.parent.name == "markdown" else markdown_path.parent
    
    # Load any existing tables and diagrams
    tables = find_table_json_files(output_path)
    diagrams = find_diagram_json_files(output_path)
    
    if not quiet:
        if tables:
            print(f"📊 Found {len(tables)} extracted tables")
        if diagrams:
            print(f"🎨 Found {len(diagrams)} extracted diagrams")
    
    # Get page count from the markdown (look for footer or metadata)
    page_count = 0
    try:
        with open(markdown_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Try to extract page count from footer
            if "Total Pages:" in content:
                import re
                match = re.search(r"Total Pages:\s*(\d+)", content)
                if match:
                    page_count = int(match.group(1))
            
            # If not found, count page markers
            if page_count == 0:
                page_count = content.count("<!-- Page")
                
            # If still 0, default to 1
            if page_count == 0:
                page_count = 1
    except Exception as e:
        print(f"⚠️  Warning: Could not determine page count: {e}")
        page_count = 1
    
    # Initialize vector generator
    try:
        vector_gen = VectorGenerator(
            output_dir=str(output_path),
            vector_format=vector_format,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_strategy=chunk_strategy,
            array_strategy=array_strategy,
            create_chunks=True,
            include_extended_metadata=include_extended_metadata,
            embedding_model=embedding_model,
            embedding_provider=embedding_provider
        )
        
        # Process the merged document
        result = vector_gen.process_merged_document(
            merged_markdown_path=str(markdown_path),
            source_file=pdf_path,
            page_count=page_count,
            tables=tables if tables else None,
            diagrams=diagrams if diagrams else None
        )
        
        if not quiet:
            print(f"✅ Vector files regenerated successfully!")
            print(f"📁 Output location: {output_path}")
            
            if result.get('vector_markdown'):
                print(f"   - Vector markdown: {Path(result['vector_markdown']).name}")
            if result.get('chunks'):
                print(f"   - Chunks file: {Path(result['chunks']).name}")
            if result.get('metadata'):
                print(f"   - Metadata files created: {len(result['metadata'])} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating vectors: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False


def cli():
    """Command-line interface for standalone vector regeneration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Regenerate vector files from existing NetIntel-OCR markdown output"
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the original PDF file"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Base output directory (default: output)"
    )
    
    parser.add_argument(
        "--vector-format",
        choices=['lancedb', 'pinecone', 'weaviate', 'qdrant', 'chroma'],
        default='lancedb',
        help="Target vector database format (default: lancedb)"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in tokens (default: 1000)"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Overlap between chunks in tokens (default: 100)"
    )
    
    parser.add_argument(
        "--chunk-strategy",
        choices=['semantic', 'fixed', 'sentence'],
        default='semantic',
        help="Chunking strategy (default: semantic)"
    )
    
    parser.add_argument(
        "--array-strategy",
        choices=['separate_rows', 'concatenate', 'serialize'],
        default='separate_rows',
        help="How to handle arrays in JSON flattening (default: separate_rows)"
    )
    
    parser.add_argument(
        "--embedding-metadata",
        action="store_true",
        help="Include extended metadata for embedding generation"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug output"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    success = regenerate_vectors(
        pdf_path=args.pdf_path,
        output_dir=args.output,
        vector_format=args.vector_format,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        chunk_strategy=args.chunk_strategy,
        array_strategy=args.array_strategy,
        include_extended_metadata=args.embedding_metadata,
        debug=args.debug,
        quiet=not args.verbose
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(cli())