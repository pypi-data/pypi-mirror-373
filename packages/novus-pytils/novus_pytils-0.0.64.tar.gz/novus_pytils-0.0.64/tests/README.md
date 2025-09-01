# Novus PyTils Test Suite

This directory contains comprehensive test cases for all modules in the novus-pytils library.

## Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests
│   ├── audio/              # Audio module tests
│   ├── compression/        # Compression module tests  
│   ├── files/              # File operations tests
│   ├── image/              # Image module tests
│   ├── text/               # Text processing tests
│   ├── types/              # Data types tests
│   ├── utils/              # Utilities tests
│   └── video/              # Video module tests
└── fixtures/               # Test data and fixtures
    ├── audio/              # Sample audio files
    ├── image/              # Sample image files
    ├── text/               # Sample text files
    └── video/              # Sample video files
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests for a specific module
```bash
pytest tests/unit/utils/
pytest tests/unit/files/
pytest tests/unit/audio/
```

### Run tests with coverage
```bash
pytest --cov=novus_pytils
```

### Run tests by marker
```bash
pytest -m "not slow"        # Skip slow tests
pytest -m "unit"            # Run only unit tests
pytest -m "audio"           # Run only audio-related tests
```

### Run specific test files
```bash
pytest tests/unit/utils/test_validation.py
pytest tests/unit/types/test_lists.py
```

### Run with verbose output
```bash
pytest -v
```

## Test Categories

- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test module interactions (when applicable)
- **Slow Tests**: Tests that take longer to run (e.g., file I/O, network operations)

## Fixtures

The test suite includes shared fixtures in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_text_file`: Sample text file for testing
- `sample_json_file`: Sample JSON file for testing  
- `sample_yaml_file`: Sample YAML file for testing
- `sample_csv_file`: Sample CSV file for testing
- `test_files_dir`: Directory with various test files

## Coverage

The test suite aims for comprehensive coverage of all public APIs:

- ✅ Utils module (validation, hash, console)
- ✅ Types module (lists, pandas helpers)
- ✅ Files module (core file operations)
- ✅ Compression module (zip operations)
- ✅ Text module (YAML processing)
- ✅ Audio module (core functions)
- ✅ Image module (core functions)  
- ✅ Video module (core functions)

## Writing New Tests

When adding new functionality:

1. Create test files in the appropriate `tests/unit/` subdirectory
2. Use descriptive test class and method names
3. Include both positive and negative test cases
4. Use appropriate fixtures from `conftest.py`
5. Mock external dependencies (file system, network, etc.)
6. Add appropriate pytest markers

Example test structure:
```python
class TestMyFunction:
    """Test the my_function."""
    
    def test_my_function_basic_case(self):
        # Test basic functionality
        pass
        
    def test_my_function_edge_case(self):
        # Test edge cases
        pass
        
    def test_my_function_error_handling(self):
        # Test error conditions
        pass
```