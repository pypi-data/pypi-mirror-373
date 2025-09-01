"""Tests for novus_pytils.files.core module."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from novus_pytils.files.core import (
    read_file_bytes, read_file_text, get_file_size, download_file, file_exists,
    delete_file, get_file_extension, get_file_name, get_file_directory,
    copy_file, copy_files, move_file, create_file_from_content, read_file_content,
    append_to_file, get_file_creation_time, get_file_modification_time, is_file_empty,
    filter_files_by_size, filter_files_by_date, rename_file, get_file_permissions,
    set_file_permissions, create_backup, restore_backup, get_file_list, get_dir_list,
    get_files_by_extension, get_files_containing_string, get_dirs_containing_string,
    directory_contains_directory, directory_contains_file, directory_contains_file_with_extension,
    create_directory, create_subdirectory, directory_exists, delete_directory,
    recreate_directory, copy_directory, get_directory_size, count_files_in_directory,
    get_subdirectories, get_files_recursively, sync_directories
)


class TestReadFileBytes:
    """Test the read_file_bytes function."""
    
    def test_read_file_bytes_basic(self, temp_dir):
        content = b"Hello, World!\x00\x01\x02"
        file_path = temp_dir / "binary.bin"
        file_path.write_bytes(content)
        
        result = read_file_bytes(str(file_path))
        assert result == content
        assert isinstance(result, bytes)
    
    def test_read_file_bytes_empty(self, temp_dir):
        file_path = temp_dir / "empty.bin"
        file_path.write_bytes(b"")
        
        result = read_file_bytes(str(file_path))
        assert result == b""
    
    def test_read_file_bytes_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            read_file_bytes("/nonexistent/file.bin")
    
    def test_read_file_bytes_large_file(self, temp_dir):
        large_content = b"x" * 10000
        file_path = temp_dir / "large.bin"
        file_path.write_bytes(large_content)
        
        result = read_file_bytes(str(file_path))
        assert len(result) == 10000
        assert result == large_content


class TestReadFileText:
    """Test the read_file_text function."""
    
    def test_read_file_text_basic(self, sample_text_file):
        result = read_file_text(sample_text_file)
        assert isinstance(result, str)
        assert "Hello, World!" in result
    
    def test_read_file_text_custom_encoding(self, temp_dir):
        content = "Hëllö, Wörld!"
        file_path = temp_dir / "utf8.txt"
        file_path.write_text(content, encoding="utf-8")
        
        result = read_file_text(str(file_path), encoding="utf-8")
        assert result == content
    
    def test_read_file_text_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            read_file_text("/nonexistent/file.txt")
    
    def test_read_file_text_encoding_error(self, temp_dir):
        # Write binary data that's not valid UTF-8
        file_path = temp_dir / "binary.txt"
        file_path.write_bytes(b"\xff\xfe\x00\x01")
        
        with pytest.raises(UnicodeDecodeError):
            read_file_text(str(file_path), encoding="utf-8")


class TestGetFileSize:
    """Test the get_file_size function."""
    
    def test_get_file_size_basic(self, sample_text_file):
        size = get_file_size(sample_text_file)
        assert isinstance(size, int)
        assert size > 0
    
    def test_get_file_size_empty(self, temp_dir):
        file_path = temp_dir / "empty.txt"
        file_path.write_text("")
        
        size = get_file_size(str(file_path))
        assert size == 0
    
    def test_get_file_size_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            get_file_size("/nonexistent/file.txt")
    
    def test_get_file_size_large_file(self, temp_dir):
        content = "x" * 10000
        file_path = temp_dir / "large.txt"
        file_path.write_text(content)
        
        size = get_file_size(str(file_path))
        assert size == 10000


class TestDownloadFile:
    """Test the download_file function."""
    
    @patch('requests.get')
    def test_download_file_success(self, mock_get, temp_dir):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.content = b"downloaded content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        save_path = temp_dir / "downloaded.txt"
        download_file("https://example.com/file.txt", str(save_path))
        
        assert save_path.exists()
        assert save_path.read_bytes() == b"downloaded content"
        mock_get.assert_called_once_with("https://example.com/file.txt")
    
    @patch('requests.get')
    def test_download_file_http_error(self, mock_get, temp_dir):
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response
        
        save_path = temp_dir / "failed.txt"
        with pytest.raises(Exception):
            download_file("https://example.com/file.txt", str(save_path))
    
    @patch('requests.get')
    def test_download_file_connection_error(self, mock_get, temp_dir):
        # Mock connection error
        mock_get.side_effect = Exception("Connection Error")
        
        save_path = temp_dir / "failed.txt"
        with pytest.raises(Exception):
            download_file("https://example.com/file.txt", str(save_path))


class TestFileExists:
    """Test the file_exists function."""
    
    def test_file_exists_true(self, sample_text_file):
        assert file_exists(sample_text_file) is True
    
    def test_file_exists_false(self):
        assert file_exists("/nonexistent/file.txt") is False
    
    def test_file_exists_directory(self, temp_dir):
        # Should return False for directories
        assert file_exists(str(temp_dir)) is False
    
    def test_file_exists_empty_path(self):
        assert file_exists("") is False
        # The function doesn't handle None gracefully, so this would raise TypeError
        with pytest.raises(TypeError):
            file_exists(None)


class TestDeleteFile:
    """Test the delete_file function."""
    
    def test_delete_file_success(self, temp_dir):
        file_path = temp_dir / "to_delete.txt"
        file_path.write_text("content")
        
        assert file_path.exists()
        delete_file(str(file_path))
        assert not file_path.exists()
    
    def test_delete_file_nonexistent(self):
        # Should not raise error for nonexistent file
        delete_file("/nonexistent/file.txt")
    
    def test_delete_file_directory(self, temp_dir):
        # Should not delete directories
        with pytest.raises((OSError, IsADirectoryError)):
            delete_file(str(temp_dir))


class TestGetFileExtension:
    """Test the get_file_extension function."""
    
    def test_get_file_extension_basic(self):
        assert get_file_extension("file.txt") == ".txt"
        assert get_file_extension("/path/to/file.pdf") == ".pdf"
        assert get_file_extension("document.docx") == ".docx"
    
    def test_get_file_extension_no_extension(self):
        assert get_file_extension("filename") == ""
        assert get_file_extension("/path/to/filename") == ""
    
    def test_get_file_extension_multiple_dots(self):
        assert get_file_extension("file.tar.gz") == ".gz"
        assert get_file_extension("backup.2023.01.01.sql") == ".sql"
    
    def test_get_file_extension_hidden_file(self):
        assert get_file_extension(".gitignore") == ""
        assert get_file_extension(".bashrc") == ""
    
    def test_get_file_extension_case_sensitive(self):
        # Function converts to lowercase
        assert get_file_extension("file.TXT") == ".txt"
        assert get_file_extension("image.JPEG") == ".jpeg"


class TestGetFileName:
    """Test the get_file_name function."""
    
    def test_get_file_name_basic(self):
        # Function returns filename WITHOUT extension
        assert get_file_name("file.txt") == "file"
        assert get_file_name("/path/to/file.txt") == "file"
        assert get_file_name("C:\\Windows\\file.txt") == "file"
    
    def test_get_file_name_no_extension(self):
        assert get_file_name("filename") == "filename"
        assert get_file_name("/path/to/filename") == "filename"
    
    def test_get_file_name_hidden_file(self):
        # Hidden files without extension return the full name
        assert get_file_name(".gitignore") == ".gitignore"
        assert get_file_name("/path/to/.bashrc") == ".bashrc"
    
    def test_get_file_name_current_directory(self):
        assert get_file_name("./file.txt") == "file"
        assert get_file_name("../file.txt") == "file"


class TestGetFileDirectory:
    """Test the get_file_directory function."""
    
    def test_get_file_directory_basic(self):
        result = get_file_directory("/path/to/file.txt")
        assert result == "/path/to"
    
    def test_get_file_directory_current_dir(self):
        result = get_file_directory("file.txt")
        assert result in [".", ""]
    
    def test_get_file_directory_root(self):
        result = get_file_directory("/file.txt")
        assert result == "/"
    
    def test_get_file_directory_relative(self):
        result = get_file_directory("./subdir/file.txt")
        assert "subdir" in result or result == "./subdir"


class TestCopyFile:
    """Test the copy_file function."""
    
    def test_copy_file_success(self, temp_dir):
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        content = "test content"
        source.write_text(content)
        
        copy_file(str(source), str(dest))
        
        assert dest.exists()
        assert dest.read_text() == content
        assert source.exists()  # Original should still exist
    
    def test_copy_file_nonexistent_source(self, temp_dir):
        dest = temp_dir / "dest.txt"
        with pytest.raises(FileNotFoundError):
            copy_file("/nonexistent/file.txt", str(dest))
    
    def test_copy_file_overwrite_existing(self, temp_dir):
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("new content")
        dest.write_text("old content")
        
        copy_file(str(source), str(dest))
        
        assert dest.read_text() == "new content"
    
    def test_copy_file_to_nonexistent_directory(self, temp_dir):
        source = temp_dir / "source.txt"
        source.write_text("content")
        dest = temp_dir / "nonexistent" / "dest.txt"
        
        with pytest.raises((FileNotFoundError, OSError)):
            copy_file(str(source), str(dest))


class TestMoveFile:
    """Test the move_file function."""
    
    def test_move_file_success(self, temp_dir):
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        content = "test content"
        source.write_text(content)
        
        move_file(str(source), str(dest))
        
        assert dest.exists()
        assert not source.exists()
        assert dest.read_text() == content
    
    def test_move_file_nonexistent_source(self, temp_dir):
        dest = temp_dir / "dest.txt"
        with pytest.raises(FileNotFoundError):
            move_file("/nonexistent/file.txt", str(dest))
    
    def test_move_file_overwrite_existing(self, temp_dir):
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("new content")
        dest.write_text("old content")
        
        move_file(str(source), str(dest))
        
        assert dest.read_text() == "new content"
        assert not source.exists()


class TestCreateFileFromContent:
    """Test the create_file_from_content function."""
    
    def test_create_file_from_content_basic(self, temp_dir):
        file_path = temp_dir / "new_file.txt"
        content = "Hello, World!"
        
        create_file_from_content(str(file_path), content)
        
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_create_file_from_content_overwrite(self, temp_dir):
        file_path = temp_dir / "existing.txt"
        file_path.write_text("old content")
        
        create_file_from_content(str(file_path), "new content")
        
        assert file_path.read_text() == "new content"
    
    def test_create_file_from_content_empty(self, temp_dir):
        file_path = temp_dir / "empty.txt"
        
        create_file_from_content(str(file_path), "")
        
        assert file_path.exists()
        assert file_path.read_text() == ""


class TestReadFileContent:
    """Test the read_file_content function."""
    
    def test_read_file_content_basic(self, sample_text_file):
        content = read_file_content(sample_text_file)
        assert isinstance(content, str)
        assert len(content) > 0
    
    def test_read_file_content_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            read_file_content("/nonexistent/file.txt")


class TestAppendToFile:
    """Test the append_to_file function."""
    
    def test_append_to_file_existing(self, temp_dir):
        file_path = temp_dir / "append.txt"
        file_path.write_text("initial content")
        
        append_to_file(str(file_path), " appended content")
        
        assert file_path.read_text() == "initial content appended content"
    
    def test_append_to_file_nonexistent(self, temp_dir):
        file_path = temp_dir / "new_append.txt"
        
        append_to_file(str(file_path), "new content")
        
        assert file_path.exists()
        assert file_path.read_text() == "new content"


class TestGetFileCreationTime:
    """Test the get_file_creation_time function."""
    
    def test_get_file_creation_time(self, sample_text_file):
        creation_time = get_file_creation_time(sample_text_file)
        assert isinstance(creation_time, float)
        assert creation_time > 0
    
    def test_get_file_creation_time_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            get_file_creation_time("/nonexistent/file.txt")


class TestGetFileModificationTime:
    """Test the get_file_modification_time function."""
    
    def test_get_file_modification_time(self, sample_text_file):
        mod_time = get_file_modification_time(sample_text_file)
        assert isinstance(mod_time, float)
        assert mod_time > 0
    
    def test_get_file_modification_time_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            get_file_modification_time("/nonexistent/file.txt")


class TestIsFileEmpty:
    """Test the is_file_empty function."""
    
    def test_is_file_empty_true(self, temp_dir):
        file_path = temp_dir / "empty.txt"
        file_path.write_text("")
        
        assert is_file_empty(str(file_path)) is True
    
    def test_is_file_empty_false(self, sample_text_file):
        assert is_file_empty(sample_text_file) is False
    
    def test_is_file_empty_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            is_file_empty("/nonexistent/file.txt")


class TestDirectoryOperations:
    """Test directory-related functions."""
    
    def test_create_directory(self, temp_dir):
        new_dir = temp_dir / "new_directory"
        
        create_directory(str(new_dir))
        
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_create_directory_existing(self, temp_dir):
        # Should not raise error for existing directory
        create_directory(str(temp_dir))
        assert temp_dir.exists()
    
    def test_directory_exists_true(self, temp_dir):
        assert directory_exists(str(temp_dir)) is True
    
    def test_directory_exists_false(self):
        assert directory_exists("/nonexistent/directory") is False
    
    def test_delete_directory(self, temp_dir):
        test_dir = temp_dir / "to_delete"
        test_dir.mkdir()
        
        delete_directory(str(test_dir))
        
        assert not test_dir.exists()
    
    def test_delete_directory_with_contents(self, temp_dir):
        test_dir = temp_dir / "with_contents"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")
        
        delete_directory(str(test_dir))
        
        assert not test_dir.exists()


class TestGetFileList:
    """Test the get_file_list function."""
    
    def test_get_file_list_basic(self, test_files_dir):
        files = get_file_list(test_files_dir)
        assert isinstance(files, list)
        assert len(files) > 0
        # Should contain files but not directories
        filenames = [os.path.basename(f) for f in files]
        assert "file1.txt" in filenames
        assert "file2.txt" in filenames
    
    def test_get_file_list_empty_directory(self, temp_dir):
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        files = get_file_list(str(empty_dir))
        assert files == []
    
    def test_get_file_list_nonexistent_directory(self):
        # The function likely returns empty list for nonexistent directory
        result = get_file_list("/nonexistent/directory")
        assert result == []


class TestGetFilesByExtension:
    """Test the get_files_by_extension function."""
    
    def test_get_files_by_extension_single(self, test_files_dir):
        txt_files = get_files_by_extension(test_files_dir, [".txt"])
        assert isinstance(txt_files, list)
        assert len(txt_files) >= 2  # file1.txt, file2.txt
        assert all(f.endswith('.txt') for f in txt_files)
    
    def test_get_files_by_extension_multiple(self, test_files_dir):
        files = get_files_by_extension(test_files_dir, [".txt", ".md"])
        assert isinstance(files, list)
        assert len(files) >= 3  # txt files + readme.md
    
    def test_get_files_by_extension_recursive(self, test_files_dir):
        files = get_files_by_extension(test_files_dir, [".txt"], recursive=True)
        assert isinstance(files, list)
        # Should include file3.txt from subdir
        assert len(files) >= 3
    
    def test_get_files_by_extension_not_found(self, test_files_dir):
        files = get_files_by_extension(test_files_dir, [".xyz"])
        assert files == []


class TestFilterFilesBySize:
    """Test the filter_files_by_size function."""
    
    def test_filter_files_by_size_basic(self, temp_dir):
        # Create files of different sizes
        small_file = temp_dir / "small.txt"
        large_file = temp_dir / "large.txt"
        small_file.write_text("x")  # 1 byte
        large_file.write_text("x" * 1000)  # 1000 bytes
        
        files = [str(small_file), str(large_file)]
        
        # Filter for files larger than 500 bytes
        result = filter_files_by_size(files, min_size=500)
        assert str(large_file) in result
        assert str(small_file) not in result
    
    def test_filter_files_by_size_max_size(self, temp_dir):
        small_file = temp_dir / "small.txt"
        large_file = temp_dir / "large.txt"
        small_file.write_text("x")
        large_file.write_text("x" * 1000)
        
        files = [str(small_file), str(large_file)]
        
        # Filter for files smaller than 500 bytes
        result = filter_files_by_size(files, max_size=500)
        assert str(small_file) in result
        assert str(large_file) not in result


class TestCountFilesInDirectory:
    """Test the count_files_in_directory function."""
    
    def test_count_files_basic(self, test_files_dir):
        count = count_files_in_directory(test_files_dir)
        assert isinstance(count, int)
        assert count >= 3  # At least file1.txt, file2.txt, readme.md
    
    def test_count_files_recursive(self, test_files_dir):
        count_non_recursive = count_files_in_directory(test_files_dir, recursive=False)
        count_recursive = count_files_in_directory(test_files_dir, recursive=True)
        
        # Recursive count should be higher (includes subdir files)
        assert count_recursive > count_non_recursive
    
    def test_count_files_empty_directory(self, temp_dir):
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        count = count_files_in_directory(str(empty_dir))
        assert count == 0