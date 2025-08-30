import os
import requests
from pathlib import Path
from typing import Optional
import uuid
import zipfile

from blocks_cli.config.config import config
from blocks_cli.builds import api_client

def get_bundle_upload_url():
    response = api_client.put(f"{config.clients.client_url}/v1/bundles/upload")
    response.raise_for_status()
    return response.json()


def upload_bundle_zip(bundle_upload_url: str, base_path: Path, zip_file_path: Optional[Path] = None, delete_after_upload: bool = True):
    try:
        random_file_name = str(uuid.uuid4())
        zip_filename_only = f"{random_file_name}.zip"
        
        if zip_file_path:
            # Use provided directory path
            zip_directory = zip_file_path
            zip_directory.mkdir(parents=True, exist_ok=True)
            zip_filename = str(zip_directory / zip_filename_only)
        else:
            # Use current directory
            zip_filename = zip_filename_only

        if os.path.exists(zip_filename):
            os.remove(zip_filename)

        # Create the zip archive from the current directory contents, ignoring specified folders
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(base_path):
                # Skip specified directories
                dirs[:] = [d for d in dirs if d not in ['.git', '.env']]
                for file in files:
                    if file == zip_filename:
                        continue
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_path)
                    zipf.write(file_path, arcname)

        # Confirm the creation of the zip file
        if not os.path.exists(zip_filename):
            raise Exception(f"Failed to create {zip_filename}")

        # Upload the zip file to presigned S3 URL
        with open(zip_filename, "rb") as f:
            response = requests.put(bundle_upload_url, data=f, headers={"Content-Type": "application/zip"})
            response.raise_for_status() 

    except Exception:
        raise
    finally:
        # Remove the zip file only if delete_after_upload is True
        if delete_after_upload and os.path.exists(zip_filename):
            os.remove(zip_filename)

    return response.text
