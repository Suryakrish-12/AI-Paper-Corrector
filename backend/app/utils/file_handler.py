import zipfile
import os
import shutil
from typing import List

class FileHandler:
    @staticmethod
    def save_upload(file_data, filename: str, dest_dir: str) -> str:
        """
        Saves raw uploaded bytes or file stream into local workspace storage.
        """
        os.makedirs(dest_dir, exist_ok=True)
        # Standardize folder structures
        clean_filename = os.path.basename(filename).replace(" ", "_")
        file_path = os.path.join(dest_dir, clean_filename)
        
        with open(file_path, "wb") as buffer:
            if hasattr(file_data, "read"):
                buffer.write(file_data.read())
            else:
                buffer.write(file_data)
        return file_path

    @staticmethod
    def extract_zip(zip_path: str, dest_dir: str) -> List[str]:
        """
        Decompresses answer script ZIP packages and returns all valid image/PDF paths.
        """
        os.makedirs(dest_dir, exist_ok=True)
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
            
        for root, _, files in os.walk(dest_dir):
            for file in files:
                # Exclude macOS OS-level indexing directories
                if not file.startswith('__MACOSX') and not file.startswith('.'):
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in ['.pdf', '.png', '.jpg', '.jpeg']:
                        extracted_files.append(os.path.join(root, file))
                        
        return extracted_files
