import cloudinary
import cloudinary.uploader
from typing import Dict, Any, Optional, BinaryIO
import os
from dotenv import load_dotenv

class CloudinaryService:
    def __init__(self):
        load_dotenv()
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )

    def upload_file_stream(self, file_stream: BinaryIO, filename: str, folder: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Prepare upload options
            options = {"resource_type": "raw"}
            if folder:
                options["folder"] = folder
            
            # Add original filename (with extension) as public_id
            options["public_id"] = filename
            
            # Upload the file stream directly
            response = cloudinary.uploader.upload(file_stream, **options)
            return response
        except Exception as e:
            raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")
