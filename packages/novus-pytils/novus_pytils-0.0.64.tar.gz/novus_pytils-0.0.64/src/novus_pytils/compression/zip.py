import os
import zipfile
from typing import List, Optional, Union, Dict, Any
import shutil
from novus_pytils.globals import ZIP_EXTS
from novus_pytils.files.core import get_files_by_extension

def get_zip_files(dir_path : str) -> list:
    """
    Get all zip files in a directory.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        list: A list of paths to zip files in the directory.
    """
    return get_files_by_extension(dir_path, ZIP_EXTS)

def extract_zip_file(zip_file: str, extract_to: str) -> None:
    """
    Extracts the contents of a ZIP file to a specified directory.

    Args:
        zip_file (str): The path to the ZIP file to be extracted.
        extract_to (str): The directory where the contents will be extracted. 
                          If the directory does not exist, it will be created.
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        os.makedirs(extract_to, exist_ok=True)
        zip_ref.extractall(extract_to)

def create_zip_file(zip_path: str, files: Union[List[str], Dict[str, str]], 
                   compression: int = zipfile.ZIP_DEFLATED) -> None:
    """
    Creates a ZIP file from a list of files or a dictionary mapping file paths to archive names.

    Args:
        zip_path (str): Path where the ZIP file will be created.
        files (Union[List[str], Dict[str, str]]): Either a list of file paths to add,
                                                 or a dict mapping file paths to archive names.
        compression (int): Compression method (default: ZIP_DEFLATED).
    """
    os.makedirs(os.path.dirname(zip_path) or '.', exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', compression=compression) as zip_ref:
        if isinstance(files, dict):
            for file_path, archive_name in files.items():
                if os.path.isfile(file_path):
                    zip_ref.write(file_path, archive_name)
                elif os.path.isdir(file_path):
                    add_directory_to_zip(zip_ref, file_path, archive_name)
        else:
            for file_path in files:
                if os.path.isfile(file_path):
                    zip_ref.write(file_path, os.path.basename(file_path))
                elif os.path.isdir(file_path):
                    add_directory_to_zip(zip_ref, file_path, os.path.basename(file_path))

def add_directory_to_zip(zip_ref: zipfile.ZipFile, dir_path: str, archive_dir: str = "") -> None:
    """
    Recursively adds a directory and its contents to a ZIP file.

    Args:
        zip_ref (zipfile.ZipFile): Open ZIP file reference.
        dir_path (str): Path to the directory to add.
        archive_dir (str): Directory name in the archive (default: empty).
    """
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Calculate the archive path
            rel_path = os.path.relpath(file_path, dir_path)
            archive_path = os.path.join(archive_dir, rel_path) if archive_dir else rel_path
            zip_ref.write(file_path, archive_path.replace(os.sep, '/'))

def list_zip_contents(zip_path: str) -> List[str]:
    """
    Lists all files in a ZIP archive.

    Args:
        zip_path (str): Path to the ZIP file.

    Returns:
        List[str]: List of file names in the ZIP archive.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        return zip_ref.namelist()

def get_zip_info(zip_path: str) -> Dict[str, Any]:
    """
    Gets detailed information about a ZIP file.

    Args:
        zip_path (str): Path to the ZIP file.

    Returns:
        Dict[str, Any]: Dictionary containing ZIP file information.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        info_list = zip_ref.infolist()
        
        total_size = sum(info.file_size for info in info_list)
        compressed_size = sum(info.compress_size for info in info_list)
        
        return {
            'filename': os.path.basename(zip_path),
            'file_count': len(info_list),
            'total_size': total_size,
            'compressed_size': compressed_size,
            'compression_ratio': (1 - compressed_size / total_size) * 100 if total_size > 0 else 0,
            'files': [info.filename for info in info_list],
            'file_details': [
                {
                    'filename': info.filename,
                    'file_size': info.file_size,
                    'compress_size': info.compress_size,
                    'date_time': info.date_time,
                    'is_dir': info.is_dir()
                }
                for info in info_list
            ]
        }

def extract_single_file(zip_path: str, file_name: str, extract_to: str) -> str:
    """
    Extracts a single file from a ZIP archive.

    Args:
        zip_path (str): Path to the ZIP file.
        file_name (str): Name of the file to extract.
        extract_to (str): Directory where the file will be extracted.

    Returns:
        str: Path to the extracted file.

    Raises:
        KeyError: If the file is not found in the archive.
    """
    os.makedirs(extract_to, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        if file_name not in zip_ref.namelist():
            raise KeyError(f"File '{file_name}' not found in ZIP archive")
        
        zip_ref.extract(file_name, extract_to)
        return os.path.join(extract_to, file_name)

def is_valid_zip(zip_path: str) -> bool:
    """
    Checks if a file is a valid ZIP archive.

    Args:
        zip_path (str): Path to the file to check.

    Returns:
        bool: True if the file is a valid ZIP archive, False otherwise.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.testzip()
        return True
    except (zipfile.BadZipFile, FileNotFoundError, OSError):
        return False

def zip_directory(directory_path: str, zip_path: str, 
                 include_root: bool = False,
                 compression: int = zipfile.ZIP_DEFLATED) -> None:
    """
    Creates a ZIP file from an entire directory.

    Args:
        directory_path (str): Path to the directory to zip.
        zip_path (str): Path where the ZIP file will be created.
        include_root (bool): Whether to include the root directory in the archive.
        compression (int): Compression method (default: ZIP_DEFLATED).
    """
    os.makedirs(os.path.dirname(zip_path) or '.', exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', compression=compression) as zip_ref:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                if include_root:
                    archive_path = os.path.relpath(file_path, os.path.dirname(directory_path))
                else:
                    archive_path = os.path.relpath(file_path, directory_path)
                
                zip_ref.write(file_path, archive_path.replace(os.sep, '/'))

def add_files_to_zip(zip_path: str, files: Union[List[str], Dict[str, str]]) -> None:
    """
    Adds files to an existing ZIP archive.

    Args:
        zip_path (str): Path to the existing ZIP file.
        files (Union[List[str], Dict[str, str]]): Files to add to the archive.
    """
    # Create a temporary ZIP file
    temp_zip = zip_path + '.tmp'
    
    with zipfile.ZipFile(zip_path, 'r') as old_zip:
        with zipfile.ZipFile(temp_zip, 'w') as new_zip:
            # Copy existing files
            for item in old_zip.infolist():
                data = old_zip.read(item.filename)
                new_zip.writestr(item, data)
            
            # Add new files
            if isinstance(files, dict):
                for file_path, archive_name in files.items():
                    if os.path.isfile(file_path):
                        new_zip.write(file_path, archive_name)
            else:
                for file_path in files:
                    if os.path.isfile(file_path):
                        new_zip.write(file_path, os.path.basename(file_path))
    
    # Replace the original file
    shutil.move(temp_zip, zip_path)

def remove_files_from_zip(zip_path: str, files_to_remove: List[str]) -> None:
    """
    Removes files from an existing ZIP archive.

    Args:
        zip_path (str): Path to the ZIP file.
        files_to_remove (List[str]): List of file names to remove from the archive.
    """
    temp_zip = zip_path + '.tmp'
    
    with zipfile.ZipFile(zip_path, 'r') as old_zip:
        with zipfile.ZipFile(temp_zip, 'w') as new_zip:
            for item in old_zip.infolist():
                if item.filename not in files_to_remove:
                    data = old_zip.read(item.filename)
                    new_zip.writestr(item, data)
    
    shutil.move(temp_zip, zip_path)

def extract_files_by_pattern(zip_path: str, pattern: str, extract_to: str) -> List[str]:
    """
    Extracts files from a ZIP archive that match a pattern.

    Args:
        zip_path (str): Path to the ZIP file.
        pattern (str): Pattern to match file names (supports * and ? wildcards).
        extract_to (str): Directory where files will be extracted.

    Returns:
        List[str]: List of extracted file paths.
    """
    import fnmatch
    
    os.makedirs(extract_to, exist_ok=True)
    extracted_files = []
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if fnmatch.fnmatch(file_name, pattern):
                zip_ref.extract(file_name, extract_to)
                extracted_files.append(os.path.join(extract_to, file_name))
    
    return extracted_files

# TODO Update ZipFile context manager to include more functionality to match functional api
class ZipFile:
    """Context manager for working with ZIP files."""
    
    def __init__(self, zip_path: str, mode: str = 'r', compression: int = zipfile.ZIP_DEFLATED):
        """
        Initialize ZipFile.

        Args:
            zip_path (str): Path to the ZIP file.
            mode (str): File mode ('r', 'w', 'a').
            compression (int): Compression method for write/append modes.
        """
        self.zip_path = zip_path
        self.mode = mode
        self.compression = compression
        self.zip_ref = None
    
    def __enter__(self) -> zipfile.ZipFile:
        """Enter the context manager."""
        if self.mode in ('w', 'a'):
            os.makedirs(os.path.dirname(self.zip_path) or '.', exist_ok=True)
        
        self.zip_ref = zipfile.ZipFile(self.zip_path, self.mode, compression=self.compression)
        return self.zip_ref
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        if self.zip_ref:
            self.zip_ref.close()
    
    def add_file(self, file_path: str, archive_name: Optional[str] = None) -> None:
        """
        Add a file to the ZIP archive.

        Args:
            file_path (str): Path to the file to add.
            archive_name (str, optional): Name in the archive. Defaults to basename.
        """
        if self.zip_ref and self.mode in ('w', 'a'):
            archive_name = archive_name or os.path.basename(file_path)
            self.zip_ref.write(file_path, archive_name)
    
    def add_string(self, content: str, filename: str) -> None:
        """
        Add string content as a file to the ZIP archive.

        Args:
            content (str): String content to add.
            filename (str): Filename in the archive.
        """
        if self.zip_ref and self.mode in ('w', 'a'):
            self.zip_ref.writestr(filename, content)
    
    def extract_all(self, extract_to: str) -> None:
        """
        Extract all files from the ZIP archive.

        Args:
            extract_to (str): Directory to extract files to.
        """
        if self.zip_ref and self.mode == 'r':
            os.makedirs(extract_to, exist_ok=True)
            self.zip_ref.extractall(extract_to)
    
    def list_files(self) -> List[str]:
        """
        List all files in the ZIP archive.

        Returns:
            List[str]: List of file names in the archive.
        """
        if self.zip_ref:
            return self.zip_ref.namelist()
        return []