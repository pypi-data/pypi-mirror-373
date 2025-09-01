"""Tests for novus_pytils.image.core module."""

import pytest
from unittest.mock import patch, MagicMock

from novus_pytils.image.core import count_image_files, get_image_files


class TestCountImageFiles:
    """Test the count_image_files function."""
    
    @patch('novus_pytils.image.core.get_files_by_extension')
    def test_count_image_files_basic(self, mock_get_files):
        mock_get_files.return_value = ["photo1.jpg", "image.png", "graphic.gif"]
        
        result = count_image_files("/test/path")
        
        assert result == 3
        mock_get_files.assert_called_once()
    
    @patch('novus_pytils.image.core.get_files_by_extension')
    def test_count_image_files_no_files(self, mock_get_files):
        mock_get_files.return_value = []
        
        result = count_image_files("/empty/path")
        
        assert result == 0
    
    @patch('novus_pytils.image.core.get_files_by_extension')
    def test_count_image_files_uses_supported_extensions(self, mock_get_files):
        mock_get_files.return_value = ["image.jpg"]
        
        count_image_files("/test/path")
        
        # Verify it's called with SUPPORTED_IMAGE_EXTENSIONS
        args, kwargs = mock_get_files.call_args
        assert args[0] == "/test/path"


class TestGetImageFiles:
    """Test the get_image_files function."""
    
    @patch('novus_pytils.image.core.get_files_by_extension')
    @patch('novus_pytils.image.core.SUPPORTED_IMAGE_EXTENSIONS', ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg'])
    def test_get_image_files_basic(self, mock_get_files):
        expected_files = ["photo.jpg", "image.png", "graphic.gif"]
        mock_get_files.return_value = expected_files
        
        result = get_image_files("/test/dir")
        
        assert result == expected_files
        mock_get_files.assert_called_once_with("/test/dir", ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg'], relative=True)
    
    @patch('novus_pytils.image.core.get_files_by_extension')
    def test_get_image_files_with_custom_extensions(self, mock_get_files):
        custom_extensions = [".jpg", ".png"]
        mock_get_files.return_value = ["photo.jpg", "image.png"]
        
        result = get_image_files("/test/dir", file_extensions=custom_extensions)
        
        assert result == ["photo.jpg", "image.png"]
        mock_get_files.assert_called_once_with("/test/dir", custom_extensions, relative=True)
    
    @patch('novus_pytils.image.core.get_files_by_extension')
    def test_get_image_files_empty_directory(self, mock_get_files):
        mock_get_files.return_value = []
        
        result = get_image_files("/empty/dir")
        
        assert result == []