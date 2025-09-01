"""Pytest configuration and fixtures for novus-pytils tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
import os


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("Hello, World!\nThis is a test file.\n")
    return str(file_path)


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    file_path = temp_dir / "sample.json"
    file_path.write_text('{"name": "test", "value": 42}')
    return str(file_path)


@pytest.fixture
def sample_yaml_file(temp_dir):
    """Create a sample YAML file for testing."""
    file_path = temp_dir / "sample.yaml"
    file_path.write_text("name: test\nvalue: 42\nitems:\n  - a\n  - b\n  - c")
    return str(file_path)


@pytest.fixture
def sample_csv_file(temp_dir):
    """Create a sample CSV file for testing."""
    file_path = temp_dir / "sample.csv"
    file_path.write_text("name,age,city\nJohn,30,NYC\nJane,25,LA")
    return str(file_path)


@pytest.fixture
def empty_zip_file(temp_dir):
    """Create an empty zip file for testing."""
    import zipfile
    file_path = temp_dir / "empty.zip"
    with zipfile.ZipFile(file_path, 'w') as zf:
        pass
    return str(file_path)


@pytest.fixture
def fixtures_dir():
    """Return the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_files_dir(temp_dir):
    """Create directory with various test files."""
    test_dir = temp_dir / "test_files"
    test_dir.mkdir()
    
    # Create text files
    (test_dir / "file1.txt").write_text("Content 1")
    (test_dir / "file2.txt").write_text("Content 2")
    (test_dir / "readme.md").write_text("# Test README")
    
    # Create subdirectory with files
    sub_dir = test_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "file3.txt").write_text("Content 3")
    
    return str(test_dir)