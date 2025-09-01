"""Tests for novus_pytils.compression.zip module."""

import pytest
import zipfile
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from novus_pytils.compression.zip import (
    get_zip_files, extract_zip_file, create_zip_file, add_directory_to_zip,
    list_zip_contents, get_zip_info, extract_single_file, is_valid_zip,
    zip_directory, add_files_to_zip, remove_files_from_zip, extract_files_by_pattern,
    ZipFile
)


@pytest.fixture
def sample_zip_file(temp_dir):
    """Create a sample zip file for testing."""
    zip_path = temp_dir / "sample.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("file1.txt", "Content of file 1")
        zf.writestr("file2.txt", "Content of file 2")
        zf.writestr("folder/file3.txt", "Content of file 3")
    
    return str(zip_path)


@pytest.fixture
def test_files_for_zip(temp_dir):
    """Create test files for zipping."""
    file1 = temp_dir / "test1.txt"
    file2 = temp_dir / "test2.txt"
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    file3 = subdir / "test3.txt"
    
    file1.write_text("Content 1")
    file2.write_text("Content 2")
    file3.write_text("Content 3")
    
    return {
        "files": [str(file1), str(file2)],
        "dir": str(temp_dir),
        "subdir": str(subdir)
    }


class TestGetZipFiles:
    """Test the get_zip_files function."""
    
    def test_get_zip_files_basic(self, temp_dir):
        # Create zip files
        (temp_dir / "file1.zip").write_text("")
        (temp_dir / "file2.zip").write_text("")
        (temp_dir / "other.txt").write_text("")
        
        zip_files = get_zip_files(str(temp_dir))
        
        assert isinstance(zip_files, list)
        assert len(zip_files) == 2
        assert any("file1.zip" in f for f in zip_files)
        assert any("file2.zip" in f for f in zip_files)
    
    def test_get_zip_files_no_zip_files(self, temp_dir):
        (temp_dir / "file.txt").write_text("")
        
        zip_files = get_zip_files(str(temp_dir))
        assert zip_files == []
    
    def test_get_zip_files_nonexistent_directory(self):
        # get_files_by_extension returns empty list for nonexistent directory
        zip_files = get_zip_files("/nonexistent/directory")
        assert zip_files == []
    
    def test_get_zip_files_empty_directory(self, temp_dir):
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        zip_files = get_zip_files(str(empty_dir))
        assert zip_files == []


class TestExtractZipFile:
    """Test the extract_zip_file function."""
    
    def test_extract_zip_file_basic(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        extract_zip_file(sample_zip_file, str(extract_dir))
        
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "file2.txt").exists()
        assert (extract_dir / "folder" / "file3.txt").exists()
        
        assert (extract_dir / "file1.txt").read_text() == "Content of file 1"
    
    def test_extract_zip_file_nonexistent_zip(self, temp_dir):
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        with pytest.raises(FileNotFoundError):
            extract_zip_file("/nonexistent/file.zip", str(extract_dir))
    
    def test_extract_zip_file_invalid_zip(self, temp_dir):
        # Create invalid zip file
        invalid_zip = temp_dir / "invalid.zip"
        invalid_zip.write_text("not a zip file")
        
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()
        
        with pytest.raises(zipfile.BadZipFile):
            extract_zip_file(str(invalid_zip), str(extract_dir))
    
    def test_extract_zip_file_nonexistent_extract_dir(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "nonexistent"
        
        # Should create the directory
        extract_zip_file(sample_zip_file, str(extract_dir))
        
        assert extract_dir.exists()
        assert (extract_dir / "file1.txt").exists()


class TestCreateZipFile:
    """Test the create_zip_file function."""
    
    def test_create_zip_file_from_list(self, test_files_for_zip, temp_dir):
        zip_path = temp_dir / "created.zip"
        files = test_files_for_zip["files"]
        
        create_zip_file(str(zip_path), files)
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) == 2
            assert any("test1.txt" in name for name in names)
            assert any("test2.txt" in name for name in names)
    
    def test_create_zip_file_from_dict(self, test_files_for_zip, temp_dir):
        zip_path = temp_dir / "created.zip"
        
        # Check if files exist first
        file1_path = test_files_for_zip["files"][0]
        file2_path = test_files_for_zip["files"][1]
        
        from pathlib import Path
        assert Path(file1_path).exists(), f"File does not exist: {file1_path}"
        assert Path(file2_path).exists(), f"File does not exist: {file2_path}"
        
        files = {
            file1_path: "custom1.txt",
            file2_path: "custom2.txt"
        }
        
        create_zip_file(str(zip_path), files)
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "custom1.txt" in names
            assert "custom2.txt" in names
    
    def test_create_zip_file_overwrite(self, test_files_for_zip, temp_dir):
        zip_path = temp_dir / "overwrite.zip"
        
        # Create initial zip
        create_zip_file(str(zip_path), test_files_for_zip["files"][:1])
        
        # Overwrite with different files
        create_zip_file(str(zip_path), test_files_for_zip["files"][1:])
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) == 1
            assert any("test2.txt" in name for name in names)
    
    def test_create_zip_file_nonexistent_file(self, temp_dir):
        zip_path = temp_dir / "test.zip"
        files = ["/nonexistent/file.txt"]
        
        # Function silently skips nonexistent files
        create_zip_file(str(zip_path), files)
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) == 0  # No files added


class TestListZipContents:
    """Test the list_zip_contents function."""
    
    def test_list_zip_contents_basic(self, sample_zip_file):
        contents = list_zip_contents(sample_zip_file)
        
        assert isinstance(contents, list)
        assert len(contents) == 3
        assert "file1.txt" in contents
        assert "file2.txt" in contents
        assert "folder/file3.txt" in contents
    
    def test_list_zip_contents_empty_zip(self, temp_dir):
        zip_path = temp_dir / "empty.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            pass  # Create empty zip
        
        contents = list_zip_contents(str(zip_path))
        assert contents == []
    
    def test_list_zip_contents_nonexistent_zip(self):
        with pytest.raises(FileNotFoundError):
            list_zip_contents("/nonexistent/file.zip")
    
    def test_list_zip_contents_invalid_zip(self, temp_dir):
        invalid_zip = temp_dir / "invalid.zip"
        invalid_zip.write_text("not a zip file")
        
        with pytest.raises(zipfile.BadZipFile):
            list_zip_contents(str(invalid_zip))


class TestGetZipInfo:
    """Test the get_zip_info function."""
    
    def test_get_zip_info_basic(self, sample_zip_file):
        info = get_zip_info(sample_zip_file)
        
        assert isinstance(info, dict)
        assert "file_count" in info
        assert "total_size" in info
        assert "compressed_size" in info
        assert "compression_ratio" in info
        assert "files" in info
        
        assert info["file_count"] == 3
        assert isinstance(info["total_size"], int)
        assert isinstance(info["compressed_size"], int)
        assert isinstance(info["compression_ratio"], float)
    
    def test_get_zip_info_empty_zip(self, temp_dir):
        zip_path = temp_dir / "empty.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            pass
        
        info = get_zip_info(str(zip_path))
        assert info["file_count"] == 0
        assert info["total_size"] == 0
    
    def test_get_zip_info_nonexistent_zip(self):
        with pytest.raises(FileNotFoundError):
            get_zip_info("/nonexistent/file.zip")


class TestExtractSingleFile:
    """Test the extract_single_file function."""
    
    def test_extract_single_file_basic(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "single_extract"
        extract_dir.mkdir()
        
        extracted_path = extract_single_file(sample_zip_file, "file1.txt", str(extract_dir))
        
        assert Path(extracted_path).exists()
        assert Path(extracted_path).read_text() == "Content of file 1"
    
    def test_extract_single_file_nested(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "nested_extract"
        extract_dir.mkdir()
        
        extracted_path = extract_single_file(sample_zip_file, "folder/file3.txt", str(extract_dir))
        
        assert Path(extracted_path).exists()
        assert Path(extracted_path).read_text() == "Content of file 3"
    
    def test_extract_single_file_not_found(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "extract"
        extract_dir.mkdir()
        
        with pytest.raises(KeyError):
            extract_single_file(sample_zip_file, "nonexistent.txt", str(extract_dir))
    
    def test_extract_single_file_nonexistent_zip(self, temp_dir):
        extract_dir = temp_dir / "extract"
        extract_dir.mkdir()
        
        with pytest.raises(FileNotFoundError):
            extract_single_file("/nonexistent/file.zip", "file.txt", str(extract_dir))


class TestIsValidZip:
    """Test the is_valid_zip function."""
    
    def test_is_valid_zip_true(self, sample_zip_file):
        assert is_valid_zip(sample_zip_file) is True
    
    def test_is_valid_zip_false(self, temp_dir):
        invalid_zip = temp_dir / "invalid.zip"
        invalid_zip.write_text("not a zip file")
        
        assert is_valid_zip(str(invalid_zip)) is False
    
    def test_is_valid_zip_nonexistent(self):
        assert is_valid_zip("/nonexistent/file.zip") is False
    
    def test_is_valid_zip_empty_file(self, temp_dir):
        empty_file = temp_dir / "empty.zip"
        empty_file.write_text("")
        
        assert is_valid_zip(str(empty_file)) is False


class TestZipDirectory:
    """Test the zip_directory function."""
    
    def test_zip_directory_basic(self, test_files_for_zip, temp_dir):
        zip_path = temp_dir / "directory.zip"
        
        zip_directory(test_files_for_zip["dir"], str(zip_path))
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) > 0
            # Should contain the test files
            assert any("test1.txt" in name for name in names)
            assert any("test2.txt" in name for name in names)
    
    def test_zip_directory_with_subdirectories(self, test_files_for_zip, temp_dir):
        zip_path = temp_dir / "with_subdirs.zip"
        
        zip_directory(test_files_for_zip["dir"], str(zip_path), include_root=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            # Should include files from subdirectory
            assert any("subdir" in name for name in names)
            assert any("test3.txt" in name for name in names)
    
    def test_zip_directory_exclude_subdirectories(self, test_files_for_zip, temp_dir):
        zip_path = temp_dir / "no_subdirs.zip"
        
        zip_directory(test_files_for_zip["dir"], str(zip_path), include_root=False)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            # Should still include subdirectory files, just without root directory name
            assert any("subdir" in name or "test3.txt" in name for name in names)
    
    def test_zip_directory_nonexistent(self, temp_dir):
        zip_path = temp_dir / "test.zip"
        
        # Function silently creates empty zip for nonexistent directory
        zip_directory("/nonexistent/directory", str(zip_path))
        
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert len(names) == 0


class TestAddFilesToZip:
    """Test the add_files_to_zip function."""
    
    def test_add_files_to_zip_list(self, sample_zip_file, test_files_for_zip):
        # Get original file count
        original_count = len(list_zip_contents(sample_zip_file))
        
        add_files_to_zip(sample_zip_file, test_files_for_zip["files"][:1])
        
        # Check new file count
        new_contents = list_zip_contents(sample_zip_file)
        assert len(new_contents) == original_count + 1
        assert any("test1.txt" in name for name in new_contents)
    
    def test_add_files_to_zip_dict(self, sample_zip_file, test_files_for_zip):
        original_count = len(list_zip_contents(sample_zip_file))
        
        files_dict = {test_files_for_zip["files"][0]: "added_file.txt"}
        add_files_to_zip(sample_zip_file, files_dict)
        
        new_contents = list_zip_contents(sample_zip_file)
        assert len(new_contents) == original_count + 1
        assert "added_file.txt" in new_contents
    
    def test_add_files_to_zip_nonexistent_zip(self, test_files_for_zip):
        with pytest.raises(FileNotFoundError):
            add_files_to_zip("/nonexistent/file.zip", test_files_for_zip["files"])


class TestRemoveFilesFromZip:
    """Test the remove_files_from_zip function."""
    
    def test_remove_files_from_zip_basic(self, sample_zip_file):
        original_contents = list_zip_contents(sample_zip_file)
        assert "file1.txt" in original_contents
        
        remove_files_from_zip(sample_zip_file, ["file1.txt"])
        
        new_contents = list_zip_contents(sample_zip_file)
        assert "file1.txt" not in new_contents
        assert len(new_contents) == len(original_contents) - 1
    
    def test_remove_files_from_zip_multiple(self, sample_zip_file):
        original_contents = list_zip_contents(sample_zip_file)
        
        remove_files_from_zip(sample_zip_file, ["file1.txt", "file2.txt"])
        
        new_contents = list_zip_contents(sample_zip_file)
        assert "file1.txt" not in new_contents
        assert "file2.txt" not in new_contents
        assert len(new_contents) == len(original_contents) - 2
    
    def test_remove_files_from_zip_nonexistent_file(self, sample_zip_file):
        original_contents = list_zip_contents(sample_zip_file)
        
        # Should not raise error for nonexistent files
        remove_files_from_zip(sample_zip_file, ["nonexistent.txt"])
        
        # Contents should remain unchanged
        new_contents = list_zip_contents(sample_zip_file)
        assert len(new_contents) == len(original_contents)
    
    def test_remove_files_from_zip_nonexistent_zip(self):
        with pytest.raises(FileNotFoundError):
            remove_files_from_zip("/nonexistent/file.zip", ["file.txt"])


class TestExtractFilesByPattern:
    """Test the extract_files_by_pattern function."""
    
    def test_extract_files_by_pattern_basic(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "pattern_extract"
        extract_dir.mkdir()
        
        extracted = extract_files_by_pattern(sample_zip_file, "*.txt", str(extract_dir))
        
        assert isinstance(extracted, list)
        assert len(extracted) == 3  # All files match *.txt
        
        # Check files were actually extracted
        for file_path in extracted:
            assert Path(file_path).exists()
    
    def test_extract_files_by_pattern_specific(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "specific_extract"
        extract_dir.mkdir()
        
        extracted = extract_files_by_pattern(sample_zip_file, "file1*", str(extract_dir))
        
        assert len(extracted) == 1
        assert "file1.txt" in extracted[0]
    
    def test_extract_files_by_pattern_no_match(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "no_match"
        extract_dir.mkdir()
        
        extracted = extract_files_by_pattern(sample_zip_file, "*.xyz", str(extract_dir))
        
        assert extracted == []
    
    def test_extract_files_by_pattern_nested(self, sample_zip_file, temp_dir):
        extract_dir = temp_dir / "nested_extract"
        extract_dir.mkdir()
        
        extracted = extract_files_by_pattern(sample_zip_file, "folder/*", str(extract_dir))
        
        assert len(extracted) == 1
        assert "file3.txt" in extracted[0]


class TestZipFileClass:
    """Test the ZipFile class."""
    
    def test_zipfile_class_initialization(self, temp_dir):
        zip_path = temp_dir / "class_test.zip"
        
        zip_obj = ZipFile(str(zip_path))
        
        # Test that the object is created (implementation depends on actual class)
        assert zip_obj is not None
    
    def test_zipfile_class_with_existing_file(self, sample_zip_file):
        zip_obj = ZipFile(sample_zip_file)
        
        # Test basic functionality (implementation-specific)
        assert zip_obj is not None