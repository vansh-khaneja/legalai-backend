from typing import BinaryIO, Dict, Any, Optional
import os
import mimetypes
from dotenv import load_dotenv
from supabase import create_client


class S3Service:
    def __init__(self):
        # Load environment variables if .env is used locally
        load_dotenv()

        # Reuse existing env var names; allow BUCKET_NAME override for Supabase convention
        self.bucket = os.getenv("BUCKET_NAME") or os.getenv("S3_BUCKET_NAME")
        supabase_url = os.getenv("SUPABASE_URL")
        # Prefer service role for server-side uploads; fallback to anon if explicitly desired
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

        if not self.bucket:
            raise ValueError("Bucket name missing. Set BUCKET_NAME or S3_BUCKET_NAME in env.")
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials missing. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY).")

        self.supabase = create_client(supabase_url, supabase_key)

    def upload_file_stream(
        self,
        file_stream: BinaryIO,
        filename: str,
        folder: Optional[str] = None,
    ) -> Dict[str, Any]:

        key = f"{folder.strip('/')}/{filename}" if folder else filename

        # Ensure stream is at start
        try:
            file_stream.seek(0)
        except Exception:
            pass

        # Read data in chunks to handle large files better
        data = file_stream.read()

        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"

        # Perform upload to Supabase Storage with proper error handling
        try:
            result = self.supabase.storage.from_(self.bucket).upload(
                key,
                data,
                file_options={"contentType": content_type},
            )

            # Handle different response formats from supabase-py
            if hasattr(result, 'status_code') and result.status_code != 200:
                raise Exception(f"Upload failed with status {result.status_code}")

        except Exception as e:
            raise Exception(f"Upload error: {str(e)}")

        # Get public URL (requires bucket to be public in Supabase settings)
        try:
            public_url = self.supabase.storage.from_(self.bucket).get_public_url(key)
            # Handle different possible return formats
            if isinstance(public_url, dict):
                public_url = (
                    public_url.get("publicURL") or
                    public_url.get("publicUrl") or
                    public_url.get("public_url")
                )
        except Exception:
            # If public URL fails, return None and let caller handle it
            public_url = None

        return {"bucket": self.bucket, "key": key, "url": public_url}
