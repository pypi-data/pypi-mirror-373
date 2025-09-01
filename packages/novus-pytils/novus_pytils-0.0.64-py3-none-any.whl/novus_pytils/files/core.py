# src/novus_pytils/files/core.py   
import os
import shutil
import requests
from datetime import datetime
from typing import List

def read_file_bytes(file_path) -> bytes:
    """Read the contents of a file and return it as bytes.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        bytes: The contents of the file as bytes.
    """
    with open(file_path, 'rb') as file:
        return file.read()
    
def read_file_text(file_path, encoding='utf-8') -> str:
    """Read the contents of a text file and return it as a string.

    Args:
        file_path (str): The path to the text file to be read.
        encoding (str, optional): The encoding of the text file. Defaults to 'utf-8'.

    Returns:
        str: The contents of the text file as a string.
    """
    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()

def get_file_size(file_path) -> int:
    """Get the size of a file in bytes.

    Args:
        file_path (str): The path to the file.

    Returns:
        int: The size of the file in bytes.
    """
    return os.path.getsize(file_path)

def download_file(url: str, save_to: str):
    """
    Downloads a file from the specified URL and saves it to the given path.

    Args:
        url (str): The URL of the file to be downloaded.
        save_to (str): The local file path where the downloaded file will be saved.
    """
    response = requests.get(url)
    with open(save_to, 'wb') as f:
        f.write(response.content)

def file_exists(file_path):
    """
    Checks if a file exists at the specified path.

    Args:
        file_path (str): The path to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)

def delete_file(file_path):
    """
    Deletes the specified file.

    Args:
        file_path (str): The path to the file to be deleted.

    Notes:
        This function does not raise an error if the file does not exist.
    """
    if os.path.exists(file_path):
        os.remove(file_path)

def get_file_extension(file_path):
    """
    Retrieves the file extension from the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file extension, in lowercase.
    """
    return os.path.splitext(file_path)[1].lower()

def get_file_name(file_path):
    """
    Retrieves the file name (without extension) from the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file name without extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def get_file_directory(file_path):
    """
    Retrieves the directory path from the given file path.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The directory path containing the file.
    """
    return os.path.dirname(file_path)

def copy_file(src_file_path, dest_file_path):
    """
    Copies a file from the source path to the destination path.

    Args:
        src_file_path (str): The path to the source file.
        dest_file_path (str): The path where the file should be copied to.

    Notes:
        This function preserves the file's metadata, such as modification and access times.
    """
    shutil.copy2(src_file_path, dest_file_path)

def copy_files(src_paths, dest_dir, enumerate_dups=True):
    """
    Copies files from the source paths to the destination directory.

    Args:
        src_paths (list): A list of paths to the source files.
        dest_dir (str): The path to the destination directory.
        enumerate_dups (bool, optional): If True, appends a number to the file name if a file with the same name already exists in the destination directory. Defaults to True.

    Notes:
        This function preserves the file's metadata, such as modification and access times.
    """
    for src_path in src_paths:
        filename = os.path.basename(src_path)
        dest_path = os.path.join(dest_dir, filename)

        if enumerate_dups:
            counter = 1
            while os.path.exists(dest_path):
                filename, extension = os.path.splitext(filename)
                filename = f"{filename}_{counter}{extension}"
                dest_path = os.path.join(dest_dir, filename)
                counter += 1

        shutil.copy2(src_path, dest_path)

def move_file(src_file_path, dest_file_path):
    """
    Moves a file from the source path to the destination path.

    Args:
        src_file_path (str): The path to the source file.
        dest_file_path (str): The path where the file should be moved to.

    Notes:
        This function preserves the file's metadata, such as modification and access times.
    """
    shutil.move(src_file_path, dest_file_path)

def create_file_from_content(file_path: str, content: str) -> None:
    """
    Create a file with the specified content.

    Args:
        file_path (str): The path to the file to create.
        content (str): The content to write to the file.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_file_content(file_path: str) -> str:
    """
    Read the content of a file.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        str: The content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def append_to_file(file_path: str, content: str) -> None:
    """
    Append content to a file.

    Args:
        file_path (str): The path to the file.
        content (str): The content to append.
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)

def get_file_creation_time(file_path: str) -> float:
    """
    Get the creation time of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        float: The creation time of the file as a timestamp.
    """
    return os.path.getctime(file_path)

def get_file_modification_time(file_path: str) -> float:
    """
    Get the modification time of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        float: The modification time of the file as a timestamp.
    """
    return os.path.getmtime(file_path)

def is_file_empty(file_path: str) -> bool:
    """
    Check if a file is empty.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file is empty, False otherwise.
    """
    return os.path.getsize(file_path) == 0

def filter_files_by_size(files: List[str], min_size: int = 0, max_size: int = None) -> List[str]:
    """
    Filter files by size.

    Args:
        files (List[str]): List of file paths.
        min_size (int): Minimum file size in bytes.
        max_size (int): Maximum file size in bytes (None for no limit).

    Returns:
        List[str]: Filtered list of file paths.
    """
    filtered_files = []
    for file_path in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size >= min_size and (max_size is None or size <= max_size):
                filtered_files.append(file_path)
    return filtered_files

def filter_files_by_date(files: List[str], start_date: datetime = None, end_date: datetime = None, 
                        after: datetime = None, before: datetime = None) -> List[str]:
    """
    Filter files by modification date.

    Args:
        files (List[str]): List of file paths.
        start_date (datetime): Start date filter (deprecated, use after).
        end_date (datetime): End date filter (deprecated, use before).
        after (datetime): Filter files modified after this date.
        before (datetime): Filter files modified before this date.

    Returns:
        List[str]: Filtered list of file paths.
    """
    # Support both old and new parameter names for backward compatibility
    if after is not None:
        start_date = after
    if before is not None:
        end_date = before
        
    filtered_files = []
    for file_path in files:
        if os.path.exists(file_path):
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (start_date is None or mod_time >= start_date) and (end_date is None or mod_time <= end_date):
                filtered_files.append(file_path)
    return filtered_files

def rename_file(old_path: str, new_path: str) -> None:
    """
    Rename a file.

    Args:
        old_path (str): The current path of the file.
        new_path (str): The new path for the file.
    """
    os.rename(old_path, new_path)

def get_file_permissions(file_path: str) -> str:
    """
    Get the permissions of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file permissions in octal format.
    """
    return oct(os.stat(file_path).st_mode)[-3:]

def set_file_permissions(file_path: str, permissions: int) -> None:
    """
    Set the permissions of a file.

    Args:
        file_path (str): The path to the file.
        permissions (int): The permissions to set (e.g., 0o644).
    """
    os.chmod(file_path, permissions)

def create_backup(file_path: str, backup_location: str = None) -> str:
    """
    Create a backup of a file.

    Args:
        file_path (str): The path to the file to backup.
        backup_location (str): The directory to place the backup, or suffix if it doesn't exist as a directory.

    Returns:
        str: The path to the backup file.
    """
    if backup_location and os.path.isdir(backup_location):
        # backup_location is a directory
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_location, filename + '.bak')
    elif backup_location:
        # backup_location is a suffix
        backup_path = file_path + backup_location
    else:
        # Default suffix
        backup_path = file_path + '.bak'
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def restore_backup(backup_path: str, original_path: str = None) -> None:
    """
    Restore a file from its backup.

    Args:
        backup_path (str): The path to the backup file.
        original_path (str): The path to restore to (defaults to backup path without suffix).
    """
    if original_path is None:
        if backup_path.endswith('.bak'):
            original_path = backup_path[:-4]
        else:
            original_path = backup_path.replace('.backup', '')
    
    shutil.copy2(backup_path, original_path)

def get_file_list(directory):
    """
    Walks the given directory and returns a list of files.

    Args:
        directory (str): The directory to walk.

    Returns:
        list: A list of file paths.
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def get_dir_list(directory, relative=False):
    """
    Generates a list of directories within the specified directory.

    Args:
        directory (str): The directory to walk.
        relative (bool, optional): If True, returns directory paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of directory paths.
    """
    dir_list = []
    for root, dirs, _ in os.walk(directory):
        for dir in dirs:
            if relative:
                relative_root = root.replace(directory, '')
                dir_list.append(os.path.join(relative_root, dir))
            else:
                dir_list.append(os.path.join(root, dir))
    return dir_list

def get_files_by_extension(directory, extensions, relative=False, recursive=False):
    """
    Retrieves a list of files with specified extensions from a directory.

    Args:
        directory (str): The directory to search for files.
        extensions (list): A list of file extensions to filter by.
        relative (bool, optional): If True, returns file paths relative to the input directory. Defaults to False.
        recursive (bool, optional): If True, searches subdirectories recursively. Defaults to False.

    Returns:
        list: A list of file paths with the specified extensions.
    """
    file_list = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()

                for ext in extensions:
                    if ext.casefold() == file_ext.casefold():
                        if relative:
                            relative_root = root.replace(os.path.join(directory, ''), '')
                            file_list.append(os.path.join(relative_root, file))
                        else:
                            file_list.append(os.path.join(root, file))
    else:
        # Only search the root directory
        if os.path.exists(directory):
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    for ext in extensions:
                        if ext.casefold() == file_ext.casefold():
                            if relative:
                                file_list.append(file)
                            else:
                                file_list.append(file_path)

    return file_list

def get_files_containing_string(directory, string, relative=False):
    """
    Retrieves a list of files in a directory and its subdirectories that contain a specified string.

    Args:
        directory (str): The directory to search for files.
        string (str): The string to search for in the files.
        relative (bool, optional): If True, returns file paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of file paths that contain the specified string.
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if string.casefold() in file.casefold():
                if relative:
                    relative_root = root.replace(directory, '')
                    file_list.append(os.path.join(relative_root, file))
                else:
                    file_list.append(os.path.join(root, file))

    return file_list

def get_dirs_containing_string(directory, string, relative=False):
    """
    Retrieves a list of directories in a specified directory and its subdirectories that contain a specified string.

    Args:
        directory (str): The directory to search for directories.
        string (str): The string to search for in the directory names.
        relative (bool, optional): If True, returns directory paths relative to the input directory. Defaults to False.

    Returns:
        list: A list of directory paths that contain the specified string.
    """
    dir_list = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if string.casefold() in dir.casefold():
                if relative:
                    relative_root = root.replace(directory, '')
                    dir_list.append(os.path.join(relative_root, dir))
                else:
                    dir_list.append(os.path.join(root, dir))

    return dir_list

def directory_contains_directory(directory, subdirectory):
    """
    Checks if a directory contains a specified subdirectory.

    Args:
        directory (str): The directory to search in.
        subdirectory (str): The subdirectory to search for.

    Returns:
        bool: True if the subdirectory is found, False otherwise.
    """
    for _, dirs, _ in os.walk(directory):
        for dir in dirs:
            if subdirectory.casefold() in dir.casefold():
                return True
    return False

def directory_contains_file(directory, filename):
    """
    Checks if a directory contains a specified file.

    Args:
        directory (str): The directory to search in.
        filename (str): The file to search for.

    Returns:
        bool: True if the file is found, False otherwise.
    """
    for _, _, files in os.walk(directory):
        for file in files:
            if filename.casefold() in file.casefold():
                return True
    return False

def directory_contains_file_with_extension(directory, extension):
    """
    Checks if a directory contains at least one file with a specified file extension.

    Args:
        directory (str): The directory to search in.
        extension (str): The file extension to search for, including the leading period (e.g. '.txt').

    Returns:
        bool: True if a file with the specified extension is found, False otherwise.
    """
    for _, _, files in os.walk(directory):
        for file in files:
            if extension.casefold() in os.path.splitext(file)[1].casefold():
                return True
    return False

def create_directory(directory_path):
    """
    Creates a directory at the specified path.

    Args:
        directory_path (str): The path where the directory should be created.

    Notes:
        If the directory already exists, this function does nothing.
    """
    os.makedirs(directory_path, exist_ok=True)

def create_subdirectory(parent_dir, subdirectory_name):
    """
    Creates a subdirectory inside the given parent directory.

    Args:
        parent_dir (str): The path of the parent directory.
        subdirectory_name (str): The name of the subdirectory to create.

    Notes:
        If the subdirectory already exists, this function does nothing.
    """
    subdirectory_path = os.path.join(parent_dir, subdirectory_name)
    os.makedirs(subdirectory_path, exist_ok=True)

def directory_exists(directory_path):
    """
    Checks if a directory exists at the specified path.

    Args:
        directory_path (str): The path to check.

    Returns:
        bool: True if the directory exists, False otherwise.
    """
    return os.path.exists(directory_path) and os.path.isdir(directory_path)

def delete_directory(directory_path):
    """
    Deletes the specified directory and all its contents.

    Args:
        directory_path (str): The path to the directory to delete.

    Notes:
        This function does not raise an error if the directory does not exist.
    """
    if os.path.exists(directory_path):
        if os.path.isdir(directory_path):
            shutil.rmtree(directory_path)

def recreate_directory(directory_path):
    """
    Deletes and then creates a directory at the specified path.

    Args:
        directory_path (str): The path to the directory to be recreated.

    Notes:
        If the directory does not exist, it will be created.
    """
    delete_directory(directory_path)
    create_directory(directory_path)

def copy_directory(src_dir, dest_dir):
    """
    Copies a directory from the source directory to the destination directory.

    Args:
        src_dir (str): The path to the source directory.
        dest_dir (str): The path to the destination directory.

    Notes:
        If the destination directory does not exist, it will be created. If it does exist, its contents will be overwritten.
    """
    shutil.copytree(src_dir, dest_dir)

def get_directory_size(directory_path: str) -> int:
    """
    Get the total size of a directory in bytes.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        int: The total size of the directory in bytes.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def count_files_in_directory(directory_path: str, recursive: bool = False) -> int:
    """
    Count the number of files in a directory.

    Args:
        directory_path (str): The path to the directory.
        recursive (bool): If True, count files recursively in subdirectories. Defaults to False.

    Returns:
        int: The number of files in the directory.
    """
    if recursive:
        count = 0
        for _, _, files in os.walk(directory_path):
            count += len(files)
        return count
    else:
        # Count only files in the root directory
        if not os.path.exists(directory_path):
            return 0
        count = 0
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                count += 1
        return count

def get_subdirectories(directory_path: str) -> List[str]:
    """
    Get a list of subdirectories in a directory.

    Args:
        directory_path (str): The path to the directory.

    Returns:
        List[str]: A list of subdirectory paths.
    """
    subdirs = []
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            subdirs.append(item_path)
    return subdirs

def get_files_recursively(directory_path: str, extensions: List[str] = None) -> List[str]:
    """
    Get all files in a directory recursively.

    Args:
        directory_path (str): The path to the directory.
        extensions (List[str], optional): List of file extensions to filter by.

    Returns:
        List[str]: A list of file paths.
    """
    files = []
    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if extensions:
                file_ext = os.path.splitext(filename)[1].lower()
                if any(ext.lower() == file_ext for ext in extensions):
                    files.append(file_path)
            else:
                files.append(file_path)
    return files

def sync_directories(src_dir: str, dest_dir: str) -> None:
    """
    Synchronize two directories.

    Args:
        src_dir (str): The source directory.
        dest_dir (str): The destination directory.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for root, dirs, files in os.walk(src_dir):
        # Create directories
        for dir_name in dirs:
            src_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(src_path, src_dir)
            dest_path = os.path.join(dest_dir, rel_path)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
        
        # Copy files
        for file_name in files:
            src_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(src_path, src_dir)
            dest_path = os.path.join(dest_dir, rel_path)
            
            # Copy if file doesn't exist or is newer
            if not os.path.exists(dest_path) or os.path.getmtime(src_path) > os.path.getmtime(dest_path):
                shutil.copy2(src_path, dest_path)