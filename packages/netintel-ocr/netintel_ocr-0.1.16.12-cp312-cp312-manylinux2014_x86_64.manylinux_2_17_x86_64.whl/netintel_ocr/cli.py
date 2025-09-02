import argparse
import sys
import os
import json
from pathlib import Path

from .processor import process_pdf
from .network_processor import process_pdf_network_diagrams
from .hybrid_processor import process_pdf_hybrid
try:
    from .__version__ import format_version_string, get_version_info, __version__
except ImportError:
    # Fallback if __version__.py doesn't exist yet
    __version__ = "0.1.16.12"
    def format_version_string(json_format=False):
        return f"NetIntel-OCR v{__version__}"
    def get_version_info():
        return {"version": __version__}

try:
    from .dedup_manager import DeduplicationManager
except ImportError:
    DeduplicationManager = None


def cli():
    parser = argparse.ArgumentParser(
        prog='netintel-ocr',
        description=f"NetIntel-OCR v{__version__}: Next-Generation Vector Intelligence Platform with Milvus. "
                    "20-60x faster search, 70% less memory usage. "
                    "NEW v0.1.15: Milvus vector database, Qwen3-8B embeddings, simplified deployment scales.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # DEFAULT: Automatic network diagram detection (hybrid mode)
  netintel-ocr document.pdf
  
  # Text-only mode (skip detection for speed)
  netintel-ocr document.pdf --text-only
  
  # Network diagrams only (skip text pages)
  netintel-ocr network-architecture.pdf --network-only
  
  # Adjust detection sensitivity (icons are on by default)
  netintel-ocr document.pdf --confidence 0.8
  
  # Disable icons if needed
  netintel-ocr document.pdf --no-icons
  
  # Process specific pages
  netintel-ocr large.pdf --start 10 --end 20
  
  # Use a different model
  netintel-ocr doc.pdf --model llava:latest
  
  # NEW v0.1.13: Initialize project with deployment scale options
  
  ## Personal/Testing (1 user, <10 PDFs/day):
  netintel-ocr --init --deployment-scale minimal
  # Creates: Single all-in-one container with SQLite queue and local storage
  # Start: docker-compose -f docker/docker-compose.minimal.yml up
  
  ## Small Team (2-5 users, 10-50 PDFs/day):
  netintel-ocr --init --deployment-scale small
  # Creates: API with embedded workers, Redis, MinIO
  # Start: cd docker && docker-compose up -d
  
  ## Department (5-20 users, 50-200 PDFs/day):
  netintel-ocr --init --deployment-scale medium
  # Creates: Multiple MCP instances, Nginx load balancer
  # Start: docker-compose -f docker/docker-compose.medium.yml up -d
  
  ## Enterprise (20+ users, 200+ PDFs/day):
  netintel-ocr --init --deployment-scale large --with-kubernetes
  # Creates: Full production setup with monitoring + Kubernetes charts
  # Docker: docker-compose -f docker/docker-compose.large.yml up -d
  # K8s: helm install netintel-ocr ./helm
  
  ## All Configurations (for evaluation):
  netintel-ocr --init --deployment-scale all --with-kubernetes
  # Creates all deployment options for testing different scales
  
  # Use configuration file
  netintel-ocr document.pdf --config config.yml
  
  # Query vector database (foundation mode)
  netintel-ocr --query "network topology"
        """
    )
    
    # Version information (v0.1.14)
    parser.add_argument(
        '--version',
        action='version',
        version=format_version_string(),
        help='Show version information and exit'
    )
    parser.add_argument(
        '--version-json',
        action='store_true',
        help='Output version information as JSON'
    )
    
    # Deduplication options (v0.1.14)
    dedup_group = parser.add_argument_group('Deduplication Options (v0.1.14)')
    dedup_group.add_argument(
        '--dedup-mode',
        type=str,
        choices=['exact', 'fuzzy', 'hybrid', 'full'],
        default=None,
        help='Deduplication mode: exact (MD5), fuzzy (SimHash), hybrid (MD5+SimHash), full (MD5+SimHash+CDC). Auto-detected if not specified.'
    )
    dedup_group.add_argument(
        '--simhash-bits',
        type=int,
        choices=[64, 128],
        default=64,
        help='SimHash fingerprint size in bits (default: 64)'
    )
    dedup_group.add_argument(
        '--hamming-threshold',
        type=int,
        default=5,
        help='Maximum Hamming distance for near-duplicate detection (default: 5)'
    )
    dedup_group.add_argument(
        '--cdc-min-length',
        type=int,
        default=128,
        help='Minimum chunk length for Content-Defined Chunking (default: 128)'
    )
    dedup_group.add_argument(
        '--faiss-index-type',
        type=str,
        choices=['hash', 'IVF', 'flat'],
        default='hash',
        help='Faiss index type for similarity search (default: hash)'
    )
    dedup_group.add_argument(
        '--no-dedup',
        action='store_true',
        help='Disable deduplication completely'
    )
    dedup_group.add_argument(
        '--find-duplicates',
        type=str,
        metavar='PDF_PATH',
        help='Find duplicates of the specified PDF document'
    )
    dedup_group.add_argument(
        '--dedup-stats',
        action='store_true',
        help='Show deduplication statistics'
    )
    
    # Server modes (v0.1.13)
    server_group = parser.add_argument_group('Server Modes (v0.1.13)')
    server_group.add_argument(
        "--api",
        action="store_true",
        help="Start REST API server for document processing and search (port 8000)",
    )
    server_group.add_argument(
        "--mcp",
        action="store_true",
        help="Start Model Context Protocol (MCP) server for LLM integration (port 8001)",
    )
    server_group.add_argument(
        "--all-in-one",
        action="store_true",
        help="Run API, MCP, and embedded workers in single process (minimal deployment)",
    )
    server_group.add_argument(
        "--embedded-workers",
        action="store_true",
        help="Run PDF processing workers in API process (for resource-limited environments)",
    )
    server_group.add_argument(
        "--max-workers",
        type=int,
        default=2,
        help="Maximum concurrent PDF workers when using embedded mode (default: 2)",
    )
    server_group.add_argument(
        "--api-host",
        type=str,
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)",
    )
    server_group.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="API server port (default: 8000)",
    )
    server_group.add_argument(
        "--mcp-host",
        type=str,
        default="0.0.0.0",
        help="MCP server host (default: 0.0.0.0)",
    )
    server_group.add_argument(
        "--mcp-port",
        type=int,
        default=8001,
        help="MCP server port (default: 8001)",
    )
    server_group.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode with hot reload and debug logging",
    )
    server_group.add_argument(
        "--local-storage",
        action="store_true",
        help="Use local filesystem instead of MinIO (for minimal deployments)",
    )
    server_group.add_argument(
        "--sqlite-queue",
        action="store_true",
        help="Use SQLite queue instead of Redis (for minimal deployments)",
    )
    
    # Special commands (v0.1.11-v0.1.12)
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new NetIntel-OCR project with Docker/Kubernetes deployment configurations. "
             "Use --deployment-scale to choose: minimal (1 user), small (2-5 users), medium (5-20 users), "
             "large (20+ users), or all. Add --with-kubernetes for Helm charts. "
             "Example: netintel-ocr --init --deployment-scale small",
    )
    parser.add_argument(
        "--query",
        type=str,
        metavar="QUERY",
        help="Query the vector database with full search capabilities (v0.1.12)",
    )
    parser.add_argument(
        "--merge-to-centralized",
        action="store_true",
        help="Merge per-document databases to centralized LanceDB with embeddings (v0.1.12)",
    )
    parser.add_argument(
        "--batch-ingest",
        action="store_true",
        help="Process multiple PDFs in parallel and merge to centralized DB (v0.1.12)",
    )
    parser.add_argument(
        "--db-stats",
        action="store_true",
        help="Show centralized database statistics (v0.1.12)",
    )
    parser.add_argument(
        "--db-optimize",
        action="store_true",
        help="Optimize centralized database with compaction and index rebuilding (v0.1.12)",
    )
    parser.add_argument(
        "--db-export",
        type=str,
        metavar="OUTPUT_FILE",
        help="Export centralized database to file (v0.1.12)",
    )
    
    parser.add_argument(
        "pdf_path",
        nargs="?",
        help="Path to the input PDF file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output",
        help="Base output directory (default: output). Each document will be stored in output/<md5_checksum>/",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="nanonets-ocr-s:latest",
        help="Ollama model to use (default: nanonets-ocr-s:latest)",
    )
    parser.add_argument(
        "--network-model",
        type=str,
        default=None,
        help="Ollama model to use specifically for network diagram processing. "
             "If not specified, uses the --model parameter for all tasks. "
             "Recommended: qwen2.5vl for diagrams, nanonets-ocr-s for text. "
             "Example: --model nanonets-ocr-s --network-model qwen2.5vl",
    )
    parser.add_argument(
        "--flow-model",
        default=None,
        help="Separate model for flow diagram processing. If not specified, uses --network-model or --model",
    )
    parser.add_argument(
        "--keep-images",
        "-k",
        action="store_true",
        default=False,
        help="Keep the intermediate image files (default: False)",
    )
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        default=0,
        help="Width of the resized images. Set to 0 to skip resizing (default: 0)",
    )
    parser.add_argument(
        "--start",
        "-s",
        type=int,
        default=0,
        help="Start page number (default: 0)",
    )
    parser.add_argument(
        "--end",
        "-e",
        type=int,
        default=0,
        help="End page number (default: 0)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=False,
        help="Enable debug output with detailed processing information",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Verbose output - show progress information (default is quiet)",
    )
    # Processing mode options
    mode_group = parser.add_argument_group('Processing Modes')
    mode_group.add_argument(
        "--text-only",
        "-t",
        action="store_true",
        default=False,
        help="Text-only mode: Skip network diagram detection for faster processing. "
             "Use this when you know the document contains only text.",
    )
    mode_group.add_argument(
        "--network-only",
        action="store_true",
        default=False,
        help="Process ONLY network diagrams, skip regular text pages (use when you know the document contains mainly diagrams).",
    )
    
    # Network diagram detection options (applies to default and network-only modes)
    network_group = parser.add_argument_group('Network Diagram Options')
    network_group.add_argument(
        "--confidence",
        "-c",
        type=float,
        default=0.7,
        help="Minimum confidence threshold for network diagram detection (0.0-1.0). "
             "Higher values = stricter detection. Default: 0.7",
    )
    network_group.add_argument(
        "--no-icons",
        action="store_true",
        default=False,
        help="Disable Font Awesome icons in Mermaid diagrams. "
             "By default, icons are added for better visual representation.",
    )
    network_group.add_argument(
        "--diagram-only",
        action="store_true",
        default=False,
        help="On pages with network diagrams, only extract the diagram without the text content. "
             "By default, both diagram and text are extracted.",
    )
    network_group.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each LLM operation (default: 60). "
             "Increase for complex diagrams, decrease for faster fallback to text.",
    )
    network_group.add_argument(
        "--fast-extraction",
        action="store_true",
        default=False,
        help="Use optimized fast extraction for network diagrams. "
             "Reduces extraction time from 30-60s to 10-20s per diagram.",
    )
    
    # Table extraction options
    table_group = parser.add_argument_group('Table Extraction Options')
    table_group.add_argument(
        "--extract-tables",
        action="store_true",
        default=True,
        help="Extract tables from PDF (default: enabled). "
             "Tables are detected and converted to structured JSON format.",
    )
    table_group.add_argument(
        "--no-tables",
        action="store_true",
        default=False,
        help="Disable table extraction for faster processing.",
    )
    table_group.add_argument(
        "--table-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence for table detection (0.0-1.0, default: 0.7).",
    )
    table_group.add_argument(
        "--table-method",
        choices=['llm'],
        default='llm',
        help="Table extraction method. 'llm' uses vision models for table extraction. Default: llm",
    )
    table_group.add_argument(
        "--save-table-json",
        action="store_true",
        default=False,
        help="Save extracted tables as separate JSON files in addition to markdown.",
    )
    network_group.add_argument(
        "--multi-diagram",
        action="store_true",
        default=False,
        help="Force multi-diagram extraction mode. "
             "Extracts each diagram on a page as a separate region for individual processing.",
    )
    network_group.add_argument(
        "--no-auto-detect",
        action="store_true",
        default=False,
        help="Disable automatic network diagram detection (deprecated, use --fast-mode instead).",
    )
    
    # Checkpoint/resume options
    checkpoint_group = parser.add_argument_group('Checkpoint Options')
    checkpoint_group.add_argument(
        "--resume",
        action="store_true",
        default=False,
        help="Resume processing from a checkpoint if one exists. "
             "Checkpoints are automatically saved during processing and "
             "allow you to continue from where a previous run was interrupted. "
             "The checkpoint is stored in output/<md5>/.checkpoint/",
    )
    
    # Vector generation options (v0.1.7 - enabled by default)
    vector_group = parser.add_argument_group('Vector Database Options (v0.1.7)')
    vector_group.add_argument(
        "--no-vector",
        action="store_true",
        default=False,
        help="DISABLE vector generation (v0.1.6 behavior). "
             "By default (v0.1.7+), NetIntel-OCR automatically generates: "
             "1) Vector-optimized markdown (document-vector.md), "
             "2) LanceDB-ready chunks (chunks.jsonl), "
             "3) Complete metadata and schema files. "
             "Use this flag to only generate human-friendly markdown.",
    )
    vector_group.add_argument(
        "--vector-only",
        action="store_true",
        default=False,
        help="Generate ONLY vector files (skip human-friendly markdown). "
             "Faster when you only need vector database output.",
    )
    vector_group.add_argument(
        "--vector-format",
        choices=['lancedb', 'pinecone', 'weaviate', 'qdrant', 'chroma'],
        default='lancedb',
        help="Target vector database format (default: lancedb). "
             "LanceDB format is optimized and includes pre-chunked JSONL.",
    )
    vector_group.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size in tokens for vector database (default: 1000). "
             "Optimal for most embedding models.",
    )
    vector_group.add_argument(
        "--chunk-overlap",
        type=int,
        default=100,
        help="Overlap between chunks in tokens (default: 100). "
             "Helps preserve context across chunk boundaries.",
    )
    vector_group.add_argument(
        "--chunk-strategy",
        choices=['semantic', 'fixed', 'sentence'],
        default='semantic',
        help="Chunking strategy (default: semantic). "
             "'semantic' respects document structure, "
             "'fixed' uses fixed-size chunks, "
             "'sentence' chunks at sentence boundaries.",
    )
    vector_group.add_argument(
        "--array-strategy",
        choices=['separate_rows', 'concatenate', 'serialize'],
        default='separate_rows',
        help="How to handle arrays in JSON flattening (default: separate_rows). "
             "'separate_rows' creates individual rows, "
             "'concatenate' joins with delimiter, "
             "'serialize' converts to JSON string.",
    )
    vector_group.add_argument(
        "--embedding-metadata",
        action="store_true",
        default=False,
        help="Include additional metadata for embedding generation. "
             "Adds entity extraction, technical term detection, and quality scores.",
    )
    vector_group.add_argument(
        "--legacy",
        action="store_true",
        default=False,
        help="Use v0.1.6 behavior (equivalent to --no-vector). "
             "Disables all vector generation features.",
    )
    vector_group.add_argument(
        "--vector-regenerate",
        action="store_true",
        default=False,
        help="Regenerate vector files from existing markdown output. "
             "Use this when you have already processed a PDF and want to "
             "regenerate vector files with different settings. "
             "Skips PDF processing and uses existing markdown files.",
    )
    vector_group.add_argument(
        "--embedding-model",
        type=str,
        default="qwen3-embedding:4b",
        help="Embedding model to use for vector generation. "
             "For Ollama: qwen3-embedding:4b (default), qwen3-embedding:8b, "
             "qwen3-embedding:0.6b, nomic-embed-text, mxbai-embed-large. "
             "For OpenAI: text-embedding-ada-002, text-embedding-3-small, etc.",
    )
    vector_group.add_argument(
        "--embedding-provider",
        choices=['ollama', 'openai'],
        default='ollama',
        help="Provider for embedding generation (default: ollama). "
             "Use 'ollama' for local embeddings with Ollama models, "
             "or 'openai' for OpenAI embeddings (requires API key).",
    )
    
    # Configuration and infrastructure options (v0.1.11)
    config_group = parser.add_argument_group('Project Initialization & Configuration (v0.1.13)')
    config_group.add_argument(
        "--config",
        type=str,
        metavar="CONFIG_FILE",
        help="Path to YAML configuration file. Overrides default settings and environment variables.",
    )
    config_group.add_argument(
        "--lancedb-path",
        type=str,
        help="Local path to LanceDB for query operations",
    )
    config_group.add_argument(
        "--lancedb-uri",
        type=str,
        help="Remote URI for LanceDB (S3/MinIO) for distributed deployments",
    )
    config_group.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing files during --init",
    )
    config_group.add_argument(
        "--base-dir",
        type=str,
        default="./netintel-ocr",
        help="Base directory for --init command (default: ./netintel-ocr)",
    )
    config_group.add_argument(
        "--deployment-scale",
        type=str,
        choices=["minimal", "small", "medium", "large", "all"],
        default="all",
        help="Deployment scale for --init command. Choose based on your needs:\n"
             "  • minimal: Single container, all-in-one (1-5 users, <10 PDFs/day, 2GB RAM)\n"
             "  • small: API + embedded workers (2-5 users, 10-50 PDFs/day, 4GB RAM)\n"
             "  • medium: Multiple services + load balancing (5-20 users, 50-200 PDFs/day, 8GB RAM)\n"
             "  • large: Enterprise with monitoring (20+ users, 200+ PDFs/day, 16GB+ RAM)\n"
             "  • all: Generate all configurations (default)\n"
             "Examples:\n"
             "  netintel-ocr --init --deployment-scale minimal  # Personal use\n"
             "  netintel-ocr --init --deployment-scale small    # Small team\n"
             "  netintel-ocr --init --deployment-scale large --with-kubernetes  # Enterprise",
    )
    config_group.add_argument(
        "--with-kubernetes",
        action="store_true",
        help="Include Kubernetes/Helm charts when using --init. Recommended for large deployments. "
             "Creates Helm charts with StatefulSet for API, Deployment+HPA for MCP, and KEDA autoscaling. "
             "Example: netintel-ocr --init --deployment-scale large --with-kubernetes",
    )
    
    # v0.1.12 Query options
    query_group = parser.add_argument_group('Query Options (v0.1.12)')
    query_group.add_argument(
        "--query-limit",
        type=int,
        default=10,
        help="Maximum number of query results (default: 10)",
    )
    query_group.add_argument(
        "--rerank",
        action="store_true",
        help="Apply reranking to query results for better relevance",
    )
    query_group.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.7,
        help="Minimum similarity score for query results (default: 0.7)",
    )
    query_group.add_argument(
        "--output-format",
        choices=['json', 'markdown', 'csv'],
        default='json',
        help="Output format for query results (default: json)",
    )
    
    # v0.1.12 Batch processing options
    batch_group = parser.add_argument_group('Batch Processing Options (v0.1.12)')
    batch_group.add_argument(
        "--input-pattern",
        type=str,
        help="Input pattern for batch processing (e.g., '*.pdf', 'docs/*.pdf')",
    )
    batch_group.add_argument(
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel workers for batch processing (default: 4)",
    )
    batch_group.add_argument(
        "--auto-merge",
        action="store_true",
        default=True,
        help="Automatically merge to centralized DB after batch processing",
    )
    batch_group.add_argument(
        "--compute-embeddings",
        action="store_true",
        help="Generate embeddings during merge operation",
    )
    batch_group.add_argument(
        "--dedupe",
        action="store_true",
        default=True,
        help="Skip duplicate documents during merge",
    )
    
    # Prompt management options (v0.1.16)
    prompt_group = parser.add_argument_group('Prompt Management Options (v0.1.16)')
    prompt_group.add_argument(
        "--prompts-export",
        nargs='?',
        const='prompts_export.json',
        metavar="OUTPUT_FILE",
        help="Export all default prompts to JSON file for review or customization. "
             "Default output: prompts_export.json. "
             "Example: netintel-ocr --prompts-export custom_prompts.json",
    )
    prompt_group.add_argument(
        "--prompts-import",
        type=str,
        metavar="INPUT_FILE",
        help="Import custom prompts from JSON file. "
             "Example: netintel-ocr document.pdf --prompts-import my_prompts.json",
    )
    prompt_group.add_argument(
        "--show-prompts",
        action="store_true",
        help="Display all active prompts (including any customizations)",
    )
    prompt_group.add_argument(
        "--show-prompt",
        type=str,
        metavar="PROMPT_KEY",
        help="Display a specific prompt. "
             "Keys: unified_extraction, diagram_detection, network_component_extraction, "
             "flow_element_extraction, network_mermaid_generation, flow_mermaid_generation, "
             "network_context, flow_context",
    )
    prompt_group.add_argument(
        "--override-prompt",
        action='append',
        nargs=2,
        metavar=('KEY', 'CONTENT'),
        help="Override a specific prompt with new content. Can be used multiple times. "
             "Example: --override-prompt network_detection 'Custom detection prompt'",
    )
    prompt_group.add_argument(
        "--list-prompt-templates",
        action="store_true",
        help="List available prompt templates (security-focused, compliance-audit, etc.)",
    )
    prompt_group.add_argument(
        "--prompt-template",
        type=str,
        choices=['security-focused', 'compliance-audit', 'cloud-architecture', 
                 'iot-networks', 'telecom', 'process-optimization', 'workflow-automation'],
        help="Load a predefined prompt template. "
             "Examples: security-focused (enhanced security analysis), "
             "process-optimization (process flow optimization)",
    )

    args = parser.parse_args()
    
    # Handle version JSON output (v0.1.14)
    if args.version_json:
        print(json.dumps(get_version_info(), indent=2))
        sys.exit(0)
    
    # Handle prompt management commands (v0.1.16)
    from .prompt_manager import prompt_manager
    
    if args.prompts_export:
        prompt_manager.export_prompts(args.prompts_export)
        sys.exit(0)
    
    if args.show_prompts:
        prompt_manager.show_prompts()
        sys.exit(0)
    
    if args.show_prompt:
        prompt_manager.show_prompts(args.show_prompt)
        sys.exit(0)
    
    if args.list_prompt_templates:
        prompt_manager.list_prompt_templates()
        sys.exit(0)
    
    # Load custom prompts if specified
    if args.prompts_import:
        if not prompt_manager.import_prompts(args.prompts_import):
            sys.exit(1)
    
    # Load prompt template if specified
    if args.prompt_template:
        if not prompt_manager.load_template(args.prompt_template):
            sys.exit(1)
    
    # Override specific prompts if specified
    if args.override_prompt:
        for key, content in args.override_prompt:
            prompt_manager.override_prompt(key, content)
    
    # Handle deduplication statistics (v0.1.14)
    if args.dedup_stats:
        if DeduplicationManager is None:
            print("Error: Deduplication features not available. Please install with C++ support.")
            sys.exit(1)
        
        from .dedup_utils import format_dedup_report
        dedup_manager = DeduplicationManager()
        stats = dedup_manager.get_statistics()
        print(format_dedup_report(stats))
        sys.exit(0)
    
    # Handle find duplicates (v0.1.14)
    if args.find_duplicates:
        pdf_path = Path(args.find_duplicates)
        if not pdf_path.exists():
            print(f"Error: PDF file not found: {pdf_path}")
            sys.exit(1)
        
        if DeduplicationManager is None:
            print("Error: Deduplication features not available. Please install with C++ support.")
            sys.exit(1)
        
        dedup_manager = DeduplicationManager(
            mode=args.dedup_mode,
            hamming_threshold=args.hamming_threshold,
            cdc_min_chunk=args.cdc_min_length
        )
        
        # Process the document for deduplication
        with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
            text_content = f.read()
        
        result = dedup_manager.process_document(pdf_path, text_content)
        
        print(f"MD5: {result.get('md5_checksum', 'N/A')}")
        if result.get('simhash'):
            print(f"SimHash: {result['simhash']}")
        
        if result.get('is_duplicate'):
            print(f"Duplicate of: {result['duplicate_of']}")
            print(f"Similarity: {result['similarity_score']:.2%}")
        else:
            print("No duplicates found")
        
        if result.get('hamming_neighbors'):
            print(f"Similar documents: {len(result['hamming_neighbors'])} found")
            for neighbor in result['hamming_neighbors'][:3]:
                print(f"  - {neighbor['document_id']}: {neighbor['similarity']:.2%}")
        
        sys.exit(0)
    
    # Handle v0.1.13 server modes first
    if args.api or args.mcp or args.all_in_one:
        import asyncio
        import uvicorn
        
        # Configure storage and queue backends
        if args.local_storage:
            os.environ["STORAGE_TYPE"] = "local"
        if args.sqlite_queue:
            os.environ["QUEUE_TYPE"] = "sqlite"
        if args.embedded_workers:
            os.environ["WORKER_MODE"] = "embedded"
            os.environ["MAX_WORKERS"] = str(args.max_workers)
        
        # Start servers based on mode
        if args.all_in_one:
            # Run both API and MCP servers in one process
            print("🚀 Starting NetIntel-OCR in all-in-one mode...")
            print(f"   API Server: http://{args.api_host}:{args.api_port}")
            print(f"   MCP Server: http://{args.mcp_host}:{args.mcp_port}")
            print(f"   Workers: Embedded (max {args.max_workers})")
            
            # Import and configure both servers
            from .api.main import create_app as create_api_app
            from .mcp.server import create_mcp_server
            
            # Run both servers concurrently
            async def run_all_servers():
                # Create API app
                api_app = create_api_app(embedded_workers=True, max_workers=args.max_workers)
                
                # Create MCP server
                mcp_server = create_mcp_server()
                
                # Run both servers
                api_config = uvicorn.Config(
                    api_app,
                    host=args.api_host,
                    port=args.api_port,
                    reload=args.dev,
                    log_level="debug" if args.dev else "info"
                )
                mcp_config = uvicorn.Config(
                    mcp_server.app,
                    host=args.mcp_host,
                    port=args.mcp_port,
                    reload=args.dev,
                    log_level="debug" if args.dev else "info"
                )
                
                api_server = uvicorn.Server(api_config)
                mcp_server_instance = uvicorn.Server(mcp_config)
                
                await asyncio.gather(
                    api_server.serve(),
                    mcp_server_instance.serve()
                )
            
            asyncio.run(run_all_servers())
            sys.exit(0)
            
        elif args.api:
            # Run API server only
            print("🚀 Starting NetIntel-OCR API Server...")
            print(f"   Host: {args.api_host}")
            print(f"   Port: {args.api_port}")
            print(f"   Docs: http://{args.api_host}:{args.api_port}/docs")
            if args.embedded_workers:
                print(f"   Workers: Embedded (max {args.max_workers})")
            else:
                print("   Workers: Kubernetes Jobs (external)")
            
            from .api.main import create_app
            
            app = create_app(
                embedded_workers=args.embedded_workers,
                max_workers=args.max_workers if args.embedded_workers else None
            )
            
            uvicorn.run(
                app,
                host=args.api_host,
                port=args.api_port,
                reload=args.dev,
                log_level="debug" if args.dev else "info"
            )
            sys.exit(0)
            
        elif args.mcp:
            # Run MCP server only
            print("🚀 Starting NetIntel-OCR MCP Server...")
            print(f"   Host: {args.mcp_host}")
            print(f"   Port: {args.mcp_port}")
            print("   Mode: Read-only (horizontally scalable)")
            
            from .mcp.server import create_mcp_server
            
            mcp_server = create_mcp_server()
            
            uvicorn.run(
                mcp_server.app,
                host=args.mcp_host,
                port=args.mcp_port,
                reload=args.dev,
                log_level="debug" if args.dev else "info"
            )
            sys.exit(0)
    
    # Handle v0.1.13 project initialization
    if args.init:
        from .project_initializer import ProjectInitializer
        initializer = ProjectInitializer(
            base_dir=args.base_dir,
            deployment_scale=args.deployment_scale,
            with_kubernetes=args.with_kubernetes
        )
        success = initializer.initialize_project(force=args.force)
        sys.exit(0 if success else 1)
    
    # Handle v0.1.12 query command
    if args.query:
        from .query_engine import QueryEngine, OutputFormat
        engine = QueryEngine(
            lancedb_path=args.lancedb_path,
            lancedb_uri=args.lancedb_uri,
            embedding_model=args.embedding_model if hasattr(args, 'embedding_model') else "nomic-embed-text"
        )
        result = engine.query(
            args.query,
            limit=args.query_limit,
            rerank=args.rerank,
            similarity_threshold=args.similarity_threshold
        )
        
        # Format output
        output_format = OutputFormat(args.output_format)
        formatted = engine.format_results(result, output_format)
        print(formatted)
        sys.exit(0)
    
    # Handle v0.1.12 merge command
    if args.merge_to_centralized:
        from .centralized_db import CentralizedDatabaseManager, MergeMode
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb"),
            compute_embeddings=args.compute_embeddings
        )
        result = manager.merge_to_centralized(
            source_dir=args.output,
            mode=MergeMode.APPEND,
            dedupe=args.dedupe
        )
        print(f"✅ Merged {result.documents_merged} documents")
        print(f"   Added {result.chunks_added} chunks")
        print(f"   Skipped {result.documents_skipped} duplicates")
        if result.errors:
            print(f"⚠️  {len(result.errors)} errors occurred")
        sys.exit(0)
    
    # Handle v0.1.12 batch ingestion
    if args.batch_ingest:
        from .batch_processor import BatchProcessor
        
        # Get input patterns
        patterns = []
        if args.input_pattern:
            patterns.append(args.input_pattern)
        elif args.pdf_path:
            patterns.append(args.pdf_path)
        else:
            parser.error("--batch-ingest requires --input-pattern or pdf_path")
        
        processor = BatchProcessor(
            output_dir=args.output,
            parallel_workers=args.parallel,
            auto_merge=args.auto_merge
        )
        
        result = processor.process_batch(
            input_patterns=patterns,
            dedupe=args.dedupe
        )
        
        print(f"✅ Batch processing complete")
        print(f"   Processed: {result.processed}/{result.total_files}")
        print(f"   Failed: {result.failed}")
        print(f"   Skipped: {result.skipped}")
        print(f"   Total chunks: {result.total_chunks}")
        print(f"   Time: {result.total_time:.2f}s")
        sys.exit(0)
    
    # Handle v0.1.12 database statistics
    if args.db_stats:
        from .centralized_db import CentralizedDatabaseManager
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb")
        )
        stats = manager.get_statistics()
        documents = manager.list_documents()
        
        print("📊 Database Statistics")
        print(f"   Documents: {stats.get('total_documents', 0)}")
        print(f"   Chunks: {stats.get('total_chunks', 0)}")
        print(f"   Size: {stats.get('database_size_bytes', 0) / 1024 / 1024:.2f} MB")
        print(f"   Last update: {stats.get('last_update', 'Never')}")
        
        if documents:
            print("\n📄 Recent Documents:")
            for doc in documents[:5]:
                print(f"   - {doc.source_file} ({doc.chunk_count} chunks)")
        sys.exit(0)
    
    # Handle v0.1.12 database optimization
    if args.db_optimize:
        from .centralized_db import CentralizedDatabaseManager
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb")
        )
        result = manager.optimize_database(compact=True, rebuild_indices=True)
        print("✅ Database optimization complete")
        for action in result.get('actions_performed', []):
            print(f"   - {action}")
        sys.exit(0)
    
    # Handle v0.1.12 database export
    if args.db_export:
        from .centralized_db import CentralizedDatabaseManager
        manager = CentralizedDatabaseManager(
            centralized_path=os.path.join(args.output, "lancedb")
        )
        
        # Export chunks to file
        import json
        chunks_file = Path(args.output) / "lancedb" / "chunks.jsonl"
        if chunks_file.exists():
            with open(args.db_export, 'w') as out:
                with open(chunks_file, 'r') as inp:
                    if args.db_export.endswith('.json'):
                        # Convert JSONL to JSON array
                        chunks = [json.loads(line) for line in inp if line.strip()]
                        json.dump(chunks, out, indent=2)
                    else:
                        # Copy as JSONL
                        out.write(inp.read())
            print(f"✅ Exported database to {args.db_export}")
        else:
            print("❌ No database to export")
        sys.exit(0)
    
    # Check if pdf_path is required but missing
    if not args.pdf_path:
        parser.error("pdf_path is required unless using --init, --query, or --merge-to-centralized")
    
    # Load configuration if provided
    config = None
    if args.config:
        from .config_manager import ConfigManager
        config = ConfigManager(args.config)
        config.merge_cli_args(args)
        # Validate configuration
        is_valid, errors = config.validate_config()
        if not is_valid:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
    
    # Set global debug flag
    # Default to quiet mode (minimal output) unless debug is explicitly requested
    if args.debug:
        os.environ["NETINTEL_OCR_DEBUG"] = "1"
        os.environ["NETINTEL_OCR_QUIET"] = "0"  # Debug overrides quiet
    else:
        os.environ["NETINTEL_OCR_DEBUG"] = "0"
        # Default is quiet mode - minimal output (unless verbose is specified)
        os.environ["NETINTEL_OCR_QUIET"] = "0" if args.verbose else "1"

    # Handle vector regeneration mode
    if args.vector_regenerate:
        # Import the vector regeneration function
        from .vector_regenerator import regenerate_vectors
        
        # Regenerate vectors from existing markdown
        regenerate_vectors(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            vector_format=args.vector_format,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            chunk_strategy=args.chunk_strategy,
            array_strategy=args.array_strategy,
            include_extended_metadata=args.embedding_metadata,
            embedding_model=args.embedding_model,
            embedding_provider=args.embedding_provider,
            debug=args.debug,
            quiet=not args.verbose
        )
        return
    
    # Determine processing mode
    if args.network_only:
        # Network-only mode: Process only network diagrams
        process_pdf_network_diagrams(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.network_model or args.model,  # Use network_model if specified
            keep_images=args.keep_images,
            width=args.width,
            start=args.start,
            end=args.end,
            confidence_threshold=args.confidence,
            use_icons=not args.no_icons,  # Icons enabled by default
        )
    elif args.text_only or args.no_auto_detect:
        # Text-only mode: Skip detection for speed
        process_pdf_hybrid(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            keep_images=args.keep_images,
            width=args.width,
            start=args.start,
            end=args.end,
            auto_detect=False,
            fast_mode=True,
            resume=args.resume,
            extract_tables=not args.no_tables,
            table_confidence=args.table_confidence,
            table_method=args.table_method,
            save_table_json=args.save_table_json,
        )
    else:
        # DEFAULT: Hybrid mode with automatic detection
        # Determine if vector generation should be enabled
        generate_vector = not (args.no_vector or args.legacy)
        
        process_pdf_hybrid(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            network_model=args.network_model,  # Pass network model if specified
            flow_model=args.flow_model,  # Pass flow model if specified
            keep_images=args.keep_images,
            width=args.width,
            start=args.start,
            end=args.end,
            auto_detect=True,
            confidence_threshold=args.confidence,
            use_icons=not args.no_icons,  # Icons enabled by default
            fast_mode=False,
            timeout_seconds=args.timeout,
            include_text_with_diagrams=not args.diagram_only,  # Include text by default
            fast_extraction=args.fast_extraction,  # Use fast extraction if requested
            force_multi_diagram=args.multi_diagram,  # Force multi-diagram extraction
            debug=args.debug,
            quiet=not args.verbose,  # Quiet by default unless verbose flag
            resume=args.resume,  # Pass resume flag for checkpoint support
            extract_tables=not args.no_tables,  # Table extraction enabled by default
            table_confidence=args.table_confidence,
            table_method=args.table_method,
            save_table_json=args.save_table_json,
            # Vector generation options (v0.1.7)
            generate_vector=generate_vector,
            vector_format=args.vector_format,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            chunk_strategy=args.chunk_strategy,
            array_strategy=args.array_strategy,
            embedding_metadata=args.embedding_metadata,
            embedding_model=args.embedding_model,
            embedding_provider=args.embedding_provider,
        )


if __name__ == "__main__":
    cli()
