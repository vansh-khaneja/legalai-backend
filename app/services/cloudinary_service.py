"""
Deprecated: CloudinaryService shim.

This module now re-exports the S3-based implementation to avoid breaking imports.
Prefer importing `S3Service` from `services.s3_service` directly.
"""

from app.services.s3_service import S3Service as CloudinaryService
