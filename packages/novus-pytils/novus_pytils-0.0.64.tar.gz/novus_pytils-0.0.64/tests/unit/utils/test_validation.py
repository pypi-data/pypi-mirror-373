"""Tests for novus_pytils.utils.validation module."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from novus_pytils.utils.validation import (
    ValidationResult, validate_file_path, validate_file_type, validate_image_dimensions,
    validate_crop_box, validate_audio_parameters, validate_video_parameters,
    validate_time_format, validate_file_size, validate_quality_parameter,
    has_path_traversal, contains_dangerous_chars, get_type_from_mime, sanitize_filename,
    validate_batch_operation, validate_file_extension, validate_color_format,
    validate_url, validate_email, validate_json_structure, is_safe_path, check_disk_space
)


class TestValidationResult:
    """Test the ValidationResult class."""
    
    def test_valid_result(self):
        result = ValidationResult(True, "Success")
        assert result.is_valid is True
        assert result.message == "Success"
    
    def test_invalid_result(self):
        result = ValidationResult(False, "Error message")
        assert result.is_valid is False
        assert result.message == "Error message"


class TestValidateFilePath:
    """Test the validate_file_path function."""
    
    def test_existing_file(self, sample_text_file):
        result = validate_file_path(sample_text_file, must_exist=True)
        assert result.is_valid is True
    
    def test_non_existing_file_must_exist(self):
        result = validate_file_path("/nonexistent/file.txt", must_exist=True)
        assert result.is_valid is False
        assert "does not exist" in result.message.lower()
    
    def test_non_existing_file_optional(self):
        result = validate_file_path("/nonexistent/file.txt", must_exist=False)
        assert result.is_valid is True
    
    def test_empty_path(self):
        result = validate_file_path("", must_exist=False)
        assert result.is_valid is False
        assert "empty" in result.message.lower()
    
    def test_none_path(self):
        result = validate_file_path(None, must_exist=False)
        assert result.is_valid is False
    
    def test_check_permissions(self, sample_text_file):
        result = validate_file_path(sample_text_file, check_permissions=True)
        assert result.is_valid is True


class TestValidateFileType:
    """Test the validate_file_type function."""
    
    def test_valid_extension_match(self):
        result = validate_file_type("test.txt", expected_types=["txt", "md"])
        assert result == "txt"
    
    def test_case_insensitive_extension(self):
        result = validate_file_type("test.TXT", expected_types=["txt"])
        assert result == "txt"
    
    def test_extension_not_in_expected(self):
        with pytest.raises(ValueError):
            validate_file_type("test.pdf", expected_types=["txt", "md"])
    
    def test_no_extension(self):
        with pytest.raises(ValueError):
            validate_file_type("test", expected_types=["txt"])
    
    def test_empty_expected_types(self):
        result = validate_file_type("test.txt", expected_types=[])
        assert result == "txt"


class TestValidateImageDimensions:
    """Test the validate_image_dimensions function."""
    
    def test_valid_dimensions(self):
        result = validate_image_dimensions(800, 600)
        assert result.is_valid is True
    
    def test_zero_dimensions(self):
        result = validate_image_dimensions(0, 600)
        assert result.is_valid is False
        assert "width" in result.message.lower()
    
    def test_negative_dimensions(self):
        result = validate_image_dimensions(800, -100)
        assert result.is_valid is False
        assert "height" in result.message.lower()
    
    def test_exceeds_max_width(self):
        result = validate_image_dimensions(15000, 600, max_width=10000)
        assert result.is_valid is False
        assert "width exceeds" in result.message.lower()
    
    def test_exceeds_max_height(self):
        result = validate_image_dimensions(800, 15000, max_height=10000)
        assert result.is_valid is False
        assert "height exceeds" in result.message.lower()


class TestValidateCropBox:
    """Test the validate_crop_box function."""
    
    def test_valid_crop_box(self):
        result = validate_crop_box((10, 20, 100, 200), 1000, 1000)
        assert result is True
    
    def test_invalid_coordinates(self):
        result = validate_crop_box((100, 200, 50, 300), 1000, 1000)
        assert result is False
    
    def test_exceeds_image_bounds(self):
        result = validate_crop_box((10, 20, 1100, 200), 1000, 1000)
        assert result is False
    
    def test_no_image_dimensions(self):
        result = validate_crop_box((10, 20, 100, 200))
        assert result is True


class TestValidateAudioParameters:
    """Test the validate_audio_parameters function."""
    
    def test_valid_parameters(self):
        result = validate_audio_parameters(sample_rate=44100, channels=2, bitrate="192k", duration=120.5)
        assert result.is_valid is True
    
    def test_invalid_sample_rate(self):
        result = validate_audio_parameters(sample_rate=0)
        assert result.is_valid is False
        assert "sample rate" in result.message.lower()
    
    def test_invalid_channels(self):
        result = validate_audio_parameters(channels=0)
        assert result.is_valid is False
        assert "channels" in result.message.lower()
    
    def test_invalid_bitrate_format(self):
        result = validate_audio_parameters(bitrate="invalid")
        assert result.is_valid is False
        assert "bitrate" in result.message.lower()
    
    def test_negative_duration(self):
        result = validate_audio_parameters(duration=-10)
        assert result.is_valid is False
        assert "duration" in result.message.lower()


class TestValidateVideoParameters:
    """Test the validate_video_parameters function."""
    
    def test_valid_parameters(self):
        result = validate_video_parameters(fps=30.0, resolution="1920x1080", bitrate="2M", duration=300.0)
        assert result.is_valid is True
    
    def test_invalid_fps(self):
        result = validate_video_parameters(fps=0)
        assert result.is_valid is False
        assert "fps" in result.message.lower()
    
    def test_invalid_resolution_format(self):
        result = validate_video_parameters(resolution="invalid")
        assert result.is_valid is False
        assert "resolution" in result.message.lower()
    
    def test_valid_resolution_formats(self):
        valid_resolutions = ["1920x1080", "1280x720", "3840x2160"]
        for res in valid_resolutions:
            result = validate_video_parameters(resolution=res)
            assert result.is_valid is True


class TestValidateTimeFormat:
    """Test the validate_time_format function."""
    
    def test_valid_time_formats(self):
        valid_times = ["00:30", "1:23:45", "120", "45.5"]
        for time_str in valid_times:
            assert validate_time_format(time_str) is True
    
    def test_invalid_time_formats(self):
        invalid_times = ["invalid", "25:00", "1:70:30", "-10"]
        for time_str in invalid_times:
            assert validate_time_format(time_str) is False
    
    def test_empty_string(self):
        assert validate_time_format("") is False


class TestValidateFileSize:
    """Test the validate_file_size function."""
    
    def test_valid_file_size(self, sample_text_file):
        result = validate_file_size(sample_text_file, max_size_mb=1.0)
        assert result.is_valid is True
    
    def test_file_too_large(self, temp_dir):
        # Create a file larger than the limit
        large_file = temp_dir / "large.txt"
        large_file.write_text("x" * 1000)  # 1KB file
        
        result = validate_file_size(str(large_file), max_size_mb=0.0001)  # 0.1KB limit
        assert result.is_valid is False
        assert "exceeds" in result.message.lower()
    
    def test_file_too_small(self, sample_text_file):
        result = validate_file_size(sample_text_file, min_size_mb=10.0)
        assert result.is_valid is False
        assert "smaller" in result.message.lower()
    
    def test_nonexistent_file(self):
        result = validate_file_size("/nonexistent/file.txt")
        assert result.is_valid is False


class TestValidateQualityParameter:
    """Test the validate_quality_parameter function."""
    
    def test_valid_quality(self):
        for quality in [1, 50, 95, 100]:
            result = validate_quality_parameter(quality)
            assert result.is_valid is True
    
    def test_invalid_quality_too_low(self):
        result = validate_quality_parameter(0)
        assert result.is_valid is False
        assert "range" in result.message.lower()
    
    def test_invalid_quality_too_high(self):
        result = validate_quality_parameter(101)
        assert result.is_valid is False
        assert "range" in result.message.lower()


class TestHasPathTraversal:
    """Test the has_path_traversal function."""
    
    def test_safe_paths(self):
        safe_paths = ["file.txt", "folder/file.txt", "./file.txt", "folder\\file.txt"]
        for path in safe_paths:
            assert has_path_traversal(path) is False
    
    def test_dangerous_paths(self):
        dangerous_paths = ["../file.txt", "../../etc/passwd", "..\\windows\\system32"]
        for path in dangerous_paths:
            assert has_path_traversal(path) is True


class TestContainsDangerousChars:
    """Test the contains_dangerous_chars function."""
    
    def test_safe_paths(self):
        safe_paths = ["file.txt", "folder/file.txt", "my-file_123.txt"]
        for path in safe_paths:
            assert contains_dangerous_chars(path) is False
    
    def test_dangerous_paths(self):
        dangerous_paths = ["file<script>.txt", "file|cmd.txt", "file\"quote.txt"]
        for path in dangerous_paths:
            assert contains_dangerous_chars(path) is True


class TestGetTypeFromMime:
    """Test the get_type_from_mime function."""
    
    def test_image_mime_types(self):
        assert get_type_from_mime("image/jpeg") == "image"
        assert get_type_from_mime("image/png") == "image"
    
    def test_audio_mime_types(self):
        assert get_type_from_mime("audio/mpeg") == "audio"
        assert get_type_from_mime("audio/wav") == "audio"
    
    def test_video_mime_types(self):
        assert get_type_from_mime("video/mp4") == "video"
        assert get_type_from_mime("video/avi") == "video"
    
    def test_text_mime_types(self):
        assert get_type_from_mime("text/plain") == "text"
        assert get_type_from_mime("application/json") == "text"
    
    def test_unknown_mime_type(self):
        assert get_type_from_mime("application/unknown") == "unknown"


class TestSanitizeFilename:
    """Test the sanitize_filename function."""
    
    def test_clean_filename(self):
        assert sanitize_filename("clean_file.txt") == "clean_file.txt"
    
    def test_filename_with_illegal_chars(self):
        result = sanitize_filename("file<>:\"|?*.txt")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
    
    def test_filename_with_path_traversal(self):
        result = sanitize_filename("../../../etc/passwd")
        assert ".." not in result
    
    def test_reserved_windows_names(self):
        reserved = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        for name in reserved:
            result = sanitize_filename(f"{name}.txt")
            assert result != f"{name}.txt"


class TestValidateFileExtension:
    """Test the validate_file_extension function."""
    
    def test_valid_extension(self):
        result = validate_file_extension("test.txt", ["txt", "md"])
        assert result.is_valid is True
    
    def test_invalid_extension(self):
        result = validate_file_extension("test.pdf", ["txt", "md"])
        assert result.is_valid is False
        assert "not allowed" in result.message.lower()
    
    def test_case_insensitive(self):
        result = validate_file_extension("test.TXT", ["txt"])
        assert result.is_valid is True


class TestValidateColorFormat:
    """Test the validate_color_format function."""
    
    def test_valid_hex_colors(self):
        valid_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000"]
        for color in valid_colors:
            result = validate_color_format(color)
            assert result.is_valid is True
    
    def test_valid_rgb_colors(self):
        valid_colors = ["rgb(255,0,0)", "rgb(0, 255, 0)", "rgb(0,0,255)"]
        for color in valid_colors:
            result = validate_color_format(color)
            assert result.is_valid is True
    
    def test_invalid_colors(self):
        invalid_colors = ["#ZZ0000", "rgb(256,0,0)", "invalid", "#FF00"]
        for color in invalid_colors:
            result = validate_color_format(color)
            assert result.is_valid is False


class TestValidateUrl:
    """Test the validate_url function."""
    
    def test_valid_urls(self):
        valid_urls = [
            "https://example.com",
            "http://test.org/path",
            "https://sub.domain.com:8080/path?query=value"
        ]
        for url in valid_urls:
            result = validate_url(url)
            assert result.is_valid is True
    
    def test_invalid_urls(self):
        invalid_urls = ["not-a-url", "ftp://example.com", "https://", ""]
        for url in invalid_urls:
            result = validate_url(url)
            assert result.is_valid is False


class TestValidateEmail:
    """Test the validate_email function."""
    
    def test_valid_emails(self):
        valid_emails = ["test@example.com", "user.name@domain.org", "user+tag@domain.co.uk"]
        for email in valid_emails:
            result = validate_email(email)
            assert result.is_valid is True
    
    def test_invalid_emails(self):
        invalid_emails = ["invalid", "@domain.com", "user@", "user@domain", ""]
        for email in invalid_emails:
            result = validate_email(email)
            assert result.is_valid is False


class TestValidateJsonStructure:
    """Test the validate_json_structure function."""
    
    def test_valid_structure_with_required_fields(self):
        data = {"name": "test", "value": 42}
        result = validate_json_structure(data, required_fields=["name", "value"])
        assert result.is_valid is True
    
    def test_missing_required_field(self):
        data = {"name": "test"}
        result = validate_json_structure(data, required_fields=["name", "value"])
        assert result.is_valid is False
        assert "missing" in result.message.lower()
    
    def test_field_type_validation(self):
        data = {"name": "test", "value": 42}
        field_types = {"name": str, "value": int}
        result = validate_json_structure(data, field_types=field_types)
        assert result.is_valid is True
    
    def test_wrong_field_type(self):
        data = {"name": "test", "value": "not_int"}
        field_types = {"name": str, "value": int}
        result = validate_json_structure(data, field_types=field_types)
        assert result.is_valid is False


class TestIsSafePath:
    """Test the is_safe_path function."""
    
    def test_safe_relative_path(self):
        assert is_safe_path("file.txt") is True
        assert is_safe_path("folder/file.txt") is True
    
    def test_unsafe_path_traversal(self):
        assert is_safe_path("../file.txt") is False
        assert is_safe_path("../../etc/passwd") is False
    
    def test_safe_path_within_base(self, temp_dir):
        safe_path = str(temp_dir / "file.txt")
        assert is_safe_path(safe_path, str(temp_dir)) is True
    
    def test_unsafe_path_outside_base(self, temp_dir):
        unsafe_path = str(temp_dir.parent / "file.txt")
        assert is_safe_path(unsafe_path, str(temp_dir)) is False


class TestCheckDiskSpace:
    """Test the check_disk_space function."""
    
    @patch('shutil.disk_usage')
    def test_sufficient_disk_space(self, mock_disk_usage, temp_dir):
        # Mock disk usage: total, used, free (in bytes)
        mock_disk_usage.return_value = (1000 * 1024 * 1024, 500 * 1024 * 1024, 500 * 1024 * 1024)
        
        result = check_disk_space(str(temp_dir), required_mb=100)
        assert result.is_valid is True
    
    @patch('shutil.disk_usage')
    def test_insufficient_disk_space(self, mock_disk_usage, temp_dir):
        # Mock disk usage with limited free space
        mock_disk_usage.return_value = (1000 * 1024 * 1024, 999 * 1024 * 1024, 1 * 1024 * 1024)
        
        result = check_disk_space(str(temp_dir), required_mb=100)
        assert result.is_valid is False
        assert "insufficient" in result.message.lower()
    
    def test_invalid_path(self):
        result = check_disk_space("/nonexistent/path", required_mb=100)
        assert result.is_valid is False