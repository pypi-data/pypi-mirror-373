"""
NetIntel-OCR v0.1.14 Deduplication Utilities
Helper functions for deduplication operations
"""

import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def compute_file_hash(file_path: Path, algorithm: str = 'md5') -> str:
    """Compute hash of a file."""
    hash_func = getattr(hashlib, algorithm)()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def compute_text_hash(text: str, algorithm: str = 'md5') -> str:
    """Compute hash of text content."""
    hash_func = getattr(hashlib, algorithm)()
    hash_func.update(text.encode('utf-8'))
    return hash_func.hexdigest()


def format_dedup_report(stats: Dict[str, Any]) -> str:
    """Format deduplication statistics as a readable report."""
    lines = [
        "=" * 60,
        "NetIntel-OCR v0.1.14 Deduplication Report",
        "=" * 60,
        "",
        f"Deployment Mode: {stats.get('deployment_mode', 'unknown')}",
        f"C++ Core: {'Enabled' if stats.get('cpp_core_enabled') else 'Disabled (Python fallback)'}",
        f"Faiss: {'Enabled' if stats.get('faiss_enabled') else 'Disabled'}",
        "",
        "Processing Statistics:",
        f"  Documents Processed: {stats.get('documents_processed', 0)}",
        f"  Exact Duplicates: {stats.get('exact_duplicates', 0)} ({stats.get('exact_duplicate_rate', 0):.1%})",
        f"  Near Duplicates: {stats.get('near_duplicates', 0)} ({stats.get('near_duplicate_rate', 0):.1%})",
        f"  Average CDC Reduction: {stats.get('avg_cdc_reduction', 0):.1f}%",
        f"  Average Processing Time: {stats.get('avg_processing_time', 0):.3f}s",
        "",
        "=" * 60
    ]
    
    return "\n".join(lines)


def save_dedup_metadata(
    dedup_result: Dict[str, Any],
    output_path: Path,
    format: str = 'json'
) -> None:
    """Save deduplication metadata to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'json':
        with open(output_path, 'w') as f:
            json.dump(dedup_result, f, indent=2)
    elif format == 'txt':
        with open(output_path, 'w') as f:
            for key, value in dedup_result.items():
                f.write(f"{key}: {value}\n")
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Saved deduplication metadata to {output_path}")


def load_dedup_metadata(metadata_path: Path) -> Dict[str, Any]:
    """Load deduplication metadata from file."""
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    with open(metadata_path, 'r') as f:
        if metadata_path.suffix == '.json':
            return json.load(f)
        else:
            # Parse text format
            metadata = {}
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            return metadata


def batch_process_documents(
    documents: List[Path],
    dedup_manager: Any,
    batch_size: int = 100
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process documents in batches for deduplication."""
    results = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} documents)")
        
        for doc_path in batch:
            try:
                # Read document content (simplified - would use actual OCR)
                with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Process for deduplication
                result = dedup_manager.process_document(doc_path, content)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {doc_path}: {e}")
                results.append({
                    'pdf_path': str(doc_path),
                    'error': str(e)
                })
    
    # Get final statistics
    stats = dedup_manager.get_statistics()
    
    return results, stats


def find_duplicate_groups(
    dedup_results: List[Dict[str, Any]],
    similarity_threshold: float = 0.95
) -> List[List[str]]:
    """Group documents by duplication relationships."""
    groups = []
    processed = set()
    
    for result in dedup_results:
        doc_path = result['pdf_path']
        
        if doc_path in processed:
            continue
        
        if result.get('is_duplicate'):
            # Find or create group
            duplicate_of = result.get('duplicate_of')
            similarity = result.get('similarity_score', 0)
            
            if similarity >= similarity_threshold:
                # Find existing group or create new one
                group_found = False
                for group in groups:
                    if duplicate_of in group:
                        group.append(doc_path)
                        group_found = True
                        break
                
                if not group_found:
                    groups.append([duplicate_of, doc_path])
                
                processed.add(doc_path)
    
    return groups


def calculate_storage_savings(
    dedup_results: List[Dict[str, Any]],
    file_sizes: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """Calculate potential storage savings from deduplication."""
    total_size = 0
    duplicate_size = 0
    cdc_savings = 0
    
    for result in dedup_results:
        doc_path = result['pdf_path']
        
        # Get file size
        if file_sizes:
            size = file_sizes.get(doc_path, 0)
        else:
            try:
                size = Path(doc_path).stat().st_size
            except:
                size = 0
        
        total_size += size
        
        # Calculate savings
        if result.get('is_duplicate'):
            duplicate_size += size
        
        # CDC savings
        cdc_reduction = result.get('cdc_reduction_percent', 0) / 100
        cdc_savings += size * cdc_reduction
    
    return {
        'total_size_bytes': total_size,
        'total_size_mb': total_size / (1024 * 1024),
        'duplicate_size_bytes': duplicate_size,
        'duplicate_size_mb': duplicate_size / (1024 * 1024),
        'cdc_savings_bytes': int(cdc_savings),
        'cdc_savings_mb': cdc_savings / (1024 * 1024),
        'total_savings_bytes': duplicate_size + int(cdc_savings),
        'total_savings_mb': (duplicate_size + cdc_savings) / (1024 * 1024),
        'savings_percentage': ((duplicate_size + cdc_savings) / total_size * 100) if total_size > 0 else 0
    }