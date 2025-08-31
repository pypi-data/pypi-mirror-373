"""
MCP Server Implementation using FastMCP with HTTP-SSE
"""

from fastmcp import FastMCP
from fastmcp.server import Server
from typing import List, Dict, Any, Optional
import os
import lancedb
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("netintel-ocr-mcp")
mcp.description = "NetIntel-OCR Model Context Protocol Server - Read-only access to document data"

# Database connection
_db_connection = None

def get_db():
    """Get database connection"""
    global _db_connection
    if not _db_connection:
        storage_path = os.getenv("LANCEDB_STORAGE_PATH", "/data/lancedb")
        _db_connection = lancedb.connect(storage_path)
    return _db_connection

# Tool: Search Documents
@mcp.tool()
async def search_documents(
    query: str,
    limit: int = 10,
    document_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search documents by content or metadata
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 10)
        document_type: Filter by document type (optional)
    
    Returns:
        List of matching documents with metadata
    """
    db = get_db()
    
    if "documents" not in db.table_names():
        return []
    
    table = db.open_table("documents")
    
    # TODO: Implement actual search logic
    results = table.search().limit(limit).to_list()
    
    return results

# Tool: Get Document Content
@mcp.tool()
async def get_document_content(
    document_id: str,
    page: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get extracted text content from a document
    
    Args:
        document_id: Document identifier
        page: Specific page number (optional)
    
    Returns:
        Document content with text and metadata
    """
    db = get_db()
    
    if "content" not in db.table_names():
        return {"error": "Content not found"}
    
    table = db.open_table("content")
    
    if page is not None:
        results = table.search().where(
            f"document_id = '{document_id}' AND page_number = {page}"
        ).to_list()
    else:
        results = table.search().where(
            f"document_id = '{document_id}'"
        ).to_list()
    
    return {
        "document_id": document_id,
        "pages": results,
        "total_pages": len(results)
    }

# Tool: Get Network Diagrams
@mcp.tool()
async def get_network_diagrams(
    document_id: Optional[str] = None,
    device_type: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get extracted network diagrams
    
    Args:
        document_id: Filter by document ID (optional)
        device_type: Filter by device type (optional)
        limit: Maximum number of results
    
    Returns:
        List of network diagrams with devices and connections
    """
    db = get_db()
    
    if "diagrams" not in db.table_names():
        return []
    
    table = db.open_table("diagrams")
    query = table.search()
    
    if document_id:
        query = query.where(f"document_id = '{document_id}'")
    
    # TODO: Add device_type filtering
    
    results = query.limit(limit).to_list()
    
    return results

# Tool: Get Tables
@mcp.tool()
async def get_tables(
    document_id: Optional[str] = None,
    column_name: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get extracted tables from documents
    
    Args:
        document_id: Filter by document ID (optional)
        column_name: Filter by column name (optional)
        limit: Maximum number of results
    
    Returns:
        List of extracted tables with headers and data
    """
    db = get_db()
    
    if "tables" not in db.table_names():
        return []
    
    table = db.open_table("tables")
    query = table.search()
    
    if document_id:
        query = query.where(f"document_id = '{document_id}'")
    
    # TODO: Add column_name filtering
    
    results = query.limit(limit).to_list()
    
    return results

# Tool: Vector Search
@mcp.tool()
async def vector_search(
    query: str,
    collection: str = "content",
    limit: int = 10,
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search
    
    Args:
        query: Search query text
        collection: Collection to search in
        limit: Maximum number of results
        threshold: Similarity threshold (0-1)
    
    Returns:
        List of similar documents/content with scores
    """
    db = get_db()
    
    if collection not in db.table_names():
        return []
    
    table = db.open_table(collection)
    
    # TODO: Implement actual vector search
    # This requires embedding generation and similarity calculation
    
    return []

# Tool: Get Document Metadata
@mcp.tool()
async def get_document_metadata(
    document_id: str
) -> Dict[str, Any]:
    """
    Get metadata for a specific document
    
    Args:
        document_id: Document identifier
    
    Returns:
        Document metadata including status, dates, and properties
    """
    db = get_db()
    
    if "documents" not in db.table_names():
        return {"error": "Document not found"}
    
    table = db.open_table("documents")
    results = table.search().where(f"document_id = '{document_id}'").limit(1).to_list()
    
    if not results:
        return {"error": "Document not found"}
    
    return results[0]

# Tool: List Documents
@mcp.tool()
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all documents with pagination
    
    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        status: Filter by document status
    
    Returns:
        Paginated list of documents
    """
    db = get_db()
    
    if "documents" not in db.table_names():
        return {"documents": [], "total": 0}
    
    table = db.open_table("documents")
    query = table.search()
    
    if status:
        query = query.where(f"status = '{status}'")
    
    results = query.limit(limit).offset(skip).to_list()
    
    return {
        "documents": results,
        "total": len(results),
        "skip": skip,
        "limit": limit
    }

# Tool: Get Statistics
@mcp.tool()
async def get_statistics() -> Dict[str, Any]:
    """
    Get database statistics and metrics
    
    Returns:
        Statistics about documents, processing, and storage
    """
    db = get_db()
    
    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "collections": {}
    }
    
    for table_name in db.table_names():
        table = db.open_table(table_name)
        stats["collections"][table_name] = {
            "count": len(table)
        }
    
    return stats

# Resource: Document Collection
@mcp.resource("documents://list")
async def list_documents_resource() -> str:
    """List all available documents"""
    result = await list_documents(limit=100)
    return f"Total documents: {result['total']}\\n" + \
           "\\n".join([f"- {d['document_id']}: {d.get('filename', 'Unknown')}" 
                     for d in result['documents']])

# Resource: Network Diagrams
@mcp.resource("diagrams://list")
async def list_diagrams_resource() -> str:
    """List all network diagrams"""
    diagrams = await get_network_diagrams(limit=100)
    return f"Total diagrams: {len(diagrams)}\\n" + \
           "\\n".join([f"- Diagram {d['diagram_id']} (Page {d.get('page_number', 'N/A')})" 
                     for d in diagrams])

# Resource: Tables
@mcp.resource("tables://list")
async def list_tables_resource() -> str:
    """List all extracted tables"""
    tables = await get_tables(limit=100)
    return f"Total tables: {len(tables)}\\n" + \
           "\\n".join([f"- Table {t['table_id']} (Page {t.get('page_number', 'N/A')})" 
                     for t in tables])

# Prompt: Network Analysis
@mcp.prompt()
async def network_analysis_prompt(document_id: str) -> str:
    """
    Generate a prompt for network infrastructure analysis
    
    Args:
        document_id: Document to analyze
    
    Returns:
        Analysis prompt with context
    """
    content = await get_document_content(document_id)
    diagrams = await get_network_diagrams(document_id)
    tables = await get_tables(document_id)
    
    prompt = f"""Analyze the network infrastructure documentation:

Document ID: {document_id}
Pages: {content.get('total_pages', 0)}
Diagrams: {len(diagrams)}
Tables: {len(tables)}

Please provide:
1. Network topology overview
2. Key components and their relationships
3. Security considerations
4. Potential improvements
"""
    
    return prompt

# Prompt: Table Summary
@mcp.prompt()
async def table_summary_prompt(document_id: str) -> str:
    """
    Generate a prompt for table data summarization
    
    Args:
        document_id: Document containing tables
    
    Returns:
        Summary prompt with table context
    """
    tables = await get_tables(document_id)
    
    prompt = f"""Summarize the following {len(tables)} tables:

"""
    
    for table in tables[:5]:  # Limit to first 5 tables
        prompt += f"Table {table['table_id']}:\\n"
        prompt += f"Headers: {', '.join(table.get('headers', []))}\\n"
        prompt += f"Rows: {len(table.get('rows', []))}\\n\\n"
    
    prompt += """
Please provide:
1. Key data patterns
2. Important relationships
3. Notable findings
"""
    
    return prompt

def create_app():
    """Create FastMCP application"""
    return mcp.get_app()

if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8001"))
    
    # Run server
    uvicorn.run(
        create_app(),
        host=host,
        port=port,
        log_level="info"
    )