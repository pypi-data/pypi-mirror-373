"""
Storage Service - MinIO/S3 connection management
"""

import os
from typing import Optional
import aioboto3
import boto3
from botocore.exceptions import ClientError

_s3_client = None
_bucket_name = None

async def init_storage():
    """Initialize S3/MinIO storage connection"""
    global _s3_client, _bucket_name
    
    # Get configuration from environment
    endpoint_url = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
    _bucket_name = os.getenv("S3_BUCKET_NAME", "netintel-ocr")
    
    # Create S3 client
    session = aioboto3.Session()
    _s3_client = await session.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    ).__aenter__()
    
    # Ensure bucket exists
    try:
        await _s3_client.head_bucket(Bucket=_bucket_name)
    except ClientError:
        await _s3_client.create_bucket(Bucket=_bucket_name)
    
    print(f"Connected to S3/MinIO at {endpoint_url}, bucket: {_bucket_name}")

async def check_storage_connection() -> bool:
    """Check if storage is connected"""
    if not _s3_client:
        return False
    
    try:
        await _s3_client.head_bucket(Bucket=_bucket_name)
        return True
    except:
        return False

def get_storage():
    """Get storage client"""
    if not _s3_client:
        raise RuntimeError("Storage not initialized")
    return _s3_client, _bucket_name