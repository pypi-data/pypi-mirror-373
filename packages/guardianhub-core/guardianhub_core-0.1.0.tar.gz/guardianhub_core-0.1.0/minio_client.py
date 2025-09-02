# core/guardianhub_core/storage.py
from minio import Minio
from typing import Optional
import os


def get_minio_client(
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: bool = False
) -> Minio:
    """
    Create and return a MinIO client instance.

    Args:
        endpoint: MinIO server endpoint (host:port)
        access_key: Access key for MinIO
        secret_key: Secret key for MinIO
        secure: Whether to use HTTPS

    Returns:
        Minio: Configured MinIO client instance
    """
    endpoint = endpoint or os.getenv('MINIO_ENDPOINT', 'minio:9000')
    access_key = access_key or os.getenv('MINIO_ACCESS_KEY', 'minio')
    secret_key = secret_key or os.getenv('MINIO_SECRET_KEY', 'minio123')

    return Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )