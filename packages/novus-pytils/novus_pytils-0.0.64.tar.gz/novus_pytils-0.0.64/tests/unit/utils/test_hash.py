"""Tests for novus_pytils.utils.hash module."""

import pytest
import tempfile
from pathlib import Path

from novus_pytils.utils.hash import (
    get_file_md5_hash, get_file_sha256_hash, get_string_md5_hash, get_string_sha256_hash
)


class TestGetFileMd5Hash:
    """Test the get_file_md5_hash function."""
    
    def test_file_md5_hash(self, sample_text_file):
        hash_value = get_file_md5_hash(sample_text_file)
        assert isinstance(hash_value, str)
        assert len(hash_value) == 32  # MD5 hash length
        assert hash_value.isalnum()
    
    def test_same_file_same_hash(self, sample_text_file):
        hash1 = get_file_md5_hash(sample_text_file)
        hash2 = get_file_md5_hash(sample_text_file)
        assert hash1 == hash2
    
    def test_different_files_different_hash(self, temp_dir):
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        hash1 = get_file_md5_hash(str(file1))
        hash2 = get_file_md5_hash(str(file2))
        assert hash1 != hash2
    
    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            get_file_md5_hash("/nonexistent/file.txt")
    
    def test_empty_file(self, temp_dir):
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        
        hash_value = get_file_md5_hash(str(empty_file))
        # MD5 hash of empty file
        assert hash_value == "d41d8cd98f00b204e9800998ecf8427e"


class TestGetFileSha256Hash:
    """Test the get_file_sha256_hash function."""
    
    def test_file_sha256_hash(self, sample_text_file):
        hash_value = get_file_sha256_hash(sample_text_file)
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hash length
        assert hash_value.isalnum()
    
    def test_same_file_same_hash(self, sample_text_file):
        hash1 = get_file_sha256_hash(sample_text_file)
        hash2 = get_file_sha256_hash(sample_text_file)
        assert hash1 == hash2
    
    def test_different_files_different_hash(self, temp_dir):
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        hash1 = get_file_sha256_hash(str(file1))
        hash2 = get_file_sha256_hash(str(file2))
        assert hash1 != hash2
    
    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            get_file_sha256_hash("/nonexistent/file.txt")
    
    def test_empty_file(self, temp_dir):
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        
        hash_value = get_file_sha256_hash(str(empty_file))
        # SHA256 hash of empty file
        assert hash_value == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TestGetStringMd5Hash:
    """Test the get_string_md5_hash function."""
    
    def test_string_md5_hash(self):
        hash_value = get_string_md5_hash("Hello, World!")
        assert isinstance(hash_value, str)
        assert len(hash_value) == 32
        assert hash_value.isalnum()
    
    def test_same_string_same_hash(self):
        text = "test string"
        hash1 = get_string_md5_hash(text)
        hash2 = get_string_md5_hash(text)
        assert hash1 == hash2
    
    def test_different_strings_different_hash(self):
        hash1 = get_string_md5_hash("string1")
        hash2 = get_string_md5_hash("string2")
        assert hash1 != hash2
    
    def test_empty_string(self):
        hash_value = get_string_md5_hash("")
        # MD5 hash of empty string
        assert hash_value == "d41d8cd98f00b204e9800998ecf8427e"
    
    def test_unicode_string(self):
        hash_value = get_string_md5_hash("Hello, 世界!")
        assert isinstance(hash_value, str)
        assert len(hash_value) == 32
    
    def test_known_hash_value(self):
        # Known MD5 hash for "hello"
        assert get_string_md5_hash("hello") == "5d41402abc4b2a76b9719d911017c592"


class TestGetStringSha256Hash:
    """Test the get_string_sha256_hash function."""
    
    def test_string_sha256_hash(self):
        hash_value = get_string_sha256_hash("Hello, World!")
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64
        assert hash_value.isalnum()
    
    def test_same_string_same_hash(self):
        text = "test string"
        hash1 = get_string_sha256_hash(text)
        hash2 = get_string_sha256_hash(text)
        assert hash1 == hash2
    
    def test_different_strings_different_hash(self):
        hash1 = get_string_sha256_hash("string1")
        hash2 = get_string_sha256_hash("string2")
        assert hash1 != hash2
    
    def test_empty_string(self):
        hash_value = get_string_sha256_hash("")
        # SHA256 hash of empty string
        assert hash_value == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    def test_unicode_string(self):
        hash_value = get_string_sha256_hash("Hello, 世界!")
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64
    
    def test_known_hash_value(self):
        # Known SHA256 hash for "hello"
        assert get_string_sha256_hash("hello") == "2cf24dba4f21d4288094c58e4c66b4c0c2d95b95bb2726b5"