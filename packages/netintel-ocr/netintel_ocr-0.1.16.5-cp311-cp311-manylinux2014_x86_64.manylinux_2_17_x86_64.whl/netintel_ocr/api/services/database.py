"""
Database Service - LanceDB connection management
"""

import os
import lancedb
from typing import Optional
import asyncio

_db_connection: Optional[lancedb.DBConnection] = None

async def init_database():
    """Initialize LanceDB connection"""
    global _db_connection
    
    storage_path = os.getenv("LANCEDB_STORAGE_PATH", "/data/lancedb")
    
    # Create storage directory if it doesn't exist
    os.makedirs(storage_path, exist_ok=True)
    
    # Connect to LanceDB
    _db_connection = await asyncio.to_thread(lancedb.connect, storage_path)
    
    print(f"Connected to LanceDB at {storage_path}")

async def close_database():
    """Close database connection"""
    global _db_connection
    if _db_connection:
        _db_connection = None
        print("Database connection closed")

async def check_database_connection() -> bool:
    """Check if database is connected"""
    return _db_connection is not None

def get_db() -> lancedb.DBConnection:
    """Get database connection"""
    if not _db_connection:
        raise RuntimeError("Database not initialized")
    return _db_connection