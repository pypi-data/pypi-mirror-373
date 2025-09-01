"""Hash utility functions for file integrity checking.

This module provides functions for calculating MD5 and SHA-256 hashes of files.
"""
import hashlib

def get_file_md5_hash(file_path):
    """
    Calculate the MD5 hash of a file.

    Args:
        file_path (str): The path to the file for which the MD5 hash is to be calculated.

    Returns:
        str: The MD5 hash of the file in hexadecimal format.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_sha256_hash(file_path):
    """
    Calculate the SHA-256 hash of a file.

    Args:
        file_path (str): The path to the file for which the SHA-256 hash is to be calculated.

    Returns:
        str: The SHA-256 hash of the file in hexadecimal format.
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_string_md5_hash(text: str) -> str:
    """
    Calculate the MD5 hash of a string.

    Args:
        text (str): The string for which the MD5 hash is to be calculated.

    Returns:
        str: The MD5 hash of the string in hexadecimal format.
    """
    hash_md5 = hashlib.md5()
    hash_md5.update(text.encode('utf-8'))
    return hash_md5.hexdigest()

def get_string_sha256_hash(text: str) -> str:
    """
    Calculate the SHA-256 hash of a string.

    Args:
        text (str): The string for which the SHA-256 hash is to be calculated.

    Returns:
        str: The SHA-256 hash of the string in hexadecimal format.
    """
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(text.encode('utf-8'))
    return hash_sha256.hexdigest()