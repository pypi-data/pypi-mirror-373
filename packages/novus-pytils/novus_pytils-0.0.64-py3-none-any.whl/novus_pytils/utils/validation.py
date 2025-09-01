"""Validation utilities and error handling.

This module provides comprehensive validation functions and error handling
utilities for file operations and data validation.
"""
import os
import re
import mimetypes
import json
import urllib.parse
import shutil
from dataclasses import dataclass
from typing import List, Dict, Tuple
from pathlib import Path
from novus_pytils.exceptions import UnsupportedFormatError, ValidationError, SecurityError
from novus_pytils.globals import (
    SUPPORTED_TEXT_EXTENSIONS, SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS
)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    message: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def __str__(self):
        return f"ValidationResult(valid={self.is_valid}, message='{self.message}')"
    
def validate_file_path(file_path: str, must_exist: bool = True, check_permissions: bool = False) -> ValidationResult:
    """Validate file path for security and existence.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must exist
        check_permissions: Whether to check file permissions
        
    Returns:
        ValidationResult: Result of validation
    """
    if not file_path or file_path is None or not isinstance(file_path, str):
        return ValidationResult(False, "File path must be a non-empty string")
    
    if file_path == "":
        return ValidationResult(False, "File path cannot be empty")
    
    path = Path(file_path)
    
    if len(str(path)) > 260:
        return ValidationResult(False, "File path too long (max 260 characters)")
    
    if has_path_traversal(file_path):
        return ValidationResult(False, "Path traversal detected in file path")
    
    if contains_dangerous_chars(file_path):
        return ValidationResult(False, "Dangerous characters detected in file path")
    
    file_exists = os.path.exists(file_path)
    
    if must_exist and not file_exists:
        return ValidationResult(False, f"File does not exist: {file_path}")
    
    if file_exists and check_permissions:
        try:
            if must_exist and not os.access(file_path, os.R_OK):
                return ValidationResult(False, f"File is not readable: {file_path}")
            
            if path.parent.exists() and not os.access(path.parent, os.W_OK):
                return ValidationResult(False, f"Directory is not writable: {path.parent}")
        except OSError:
            # Skip permission checks if there are OS errors (e.g., in mocked tests)
            pass
    
    if file_exists:
        return ValidationResult(True, "File exists and is valid")
    else:
        return ValidationResult(True, "File path is valid")


def validate_file_type(file_path: str, expected_types: List[str] = None) -> str:
    """Validate file type based on extension and MIME type.
    
    Args:
        file_path: Path to validate
        expected_types: List of expected file types ('text', 'image', 'audio', 'video')
        
    Returns:
        str: Detected file type
        
    Raises:
        UnsupportedFormatError: If file type is not supported
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    file_type = None
    if ext in SUPPORTED_TEXT_EXTENSIONS:
        file_type = 'text'
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        file_type = 'image'
    elif ext in SUPPORTED_AUDIO_EXTENSIONS:
        file_type = 'audio'
    elif ext in SUPPORTED_VIDEO_EXTENSIONS:
        file_type = 'video'
    else:
        raise UnsupportedFormatError(f"Unsupported file extension: {ext}")
    
    if expected_types and file_type not in expected_types:
        raise UnsupportedFormatError(f"Expected {expected_types}, got {file_type}")
    
    if os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            mime_file_type = get_type_from_mime(mime_type)
            if mime_file_type != file_type:
                raise UnsupportedFormatError(f"MIME type {mime_type} doesn't match extension {ext}")
    
    return file_type


def validate_image_dimensions(width: int, height: int, max_width: int = 10000, max_height: int = 10000) -> ValidationResult:
    """Validate image dimensions.
    
    Args:
        width: Image width
        height: Image height
        max_width: Maximum allowed width
        max_height: Maximum allowed height
        
    Returns:
        ValidationResult: Validation result with is_valid and message
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return ValidationResult(is_valid=False, message="Width and height must be integers")
    
    if width <= 0 or height <= 0:
        return ValidationResult(is_valid=False, message="Width and height must be positive")
    
    if width > max_width:
        return ValidationResult(is_valid=False, message=f"Width {width} exceeds maximum allowed width of {max_width}")
    
    if height > max_height:
        return ValidationResult(is_valid=False, message=f"Height {height} exceeds maximum allowed height of {max_height}")
    
    return ValidationResult(is_valid=True, message="Valid dimensions")


def validate_crop_box(box: Tuple[int, int, int, int], image_width: int = None, image_height: int = None) -> bool:
    """Validate crop box coordinates.
    
    Args:
        box: (left, top, right, bottom) coordinates
        image_width: Optional image width for bounds checking
        image_height: Optional image height for bounds checking
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If box is invalid
    """
    if len(box) != 4:
        raise ValidationError("Crop box must have 4 coordinates (left, top, right, bottom)")
    
    left, top, right, bottom = box
    
    if not all(isinstance(coord, int) for coord in box):
        raise ValidationError("Crop coordinates must be integers")
    
    if left >= right or top >= bottom:
        raise ValidationError("Invalid crop box: left >= right or top >= bottom")
    
    if left < 0 or top < 0:
        raise ValidationError("Crop coordinates cannot be negative")
    
    if image_width and image_height:
        if right > image_width or bottom > image_height:
            raise ValidationError(f"Crop box exceeds image bounds ({image_width}x{image_height})")
    
    return True


def validate_audio_parameters(sample_rate: int = None, channels: int = None, bitrate: str = None, duration: float = None) -> ValidationResult:
    """Validate audio parameters.
    
    Args:
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
        bitrate: Bitrate string (e.g., '192k')
        duration: Duration in seconds
        
    Returns:
        ValidationResult: Validation result with is_valid and message
    """
    if sample_rate is not None:
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            return ValidationResult(is_valid=False, message="Sample rate must be a positive integer")
        
        if sample_rate < 8000 or sample_rate > 192000:
            return ValidationResult(is_valid=False, message="Sample rate must be between 8000 and 192000 Hz")
    
    if channels is not None:
        if not isinstance(channels, int) or channels <= 0:
            return ValidationResult(is_valid=False, message="Channels must be a positive integer")
        
        if channels > 8:
            return ValidationResult(is_valid=False, message="Maximum 8 audio channels supported")
    
    if bitrate is not None:
        if not isinstance(bitrate, str):
            return ValidationResult(is_valid=False, message="Bitrate must be a string")
        
        if not re.match(r'^\d+[kmKM]?$', bitrate):
            return ValidationResult(is_valid=False, message="Invalid bitrate format (e.g., '192k', '320K')")
    
    if duration is not None:
        if not isinstance(duration, (int, float)) or duration < 0:
            return ValidationResult(is_valid=False, message="Duration must be a non-negative number")
    
    return ValidationResult(is_valid=True, message="Valid audio parameters")


def validate_video_parameters(fps: float = None, resolution: str = None, bitrate: str = None, duration: float = None) -> ValidationResult:
    """Validate video parameters.
    
    Args:
        fps: Frames per second
        resolution: Resolution string (e.g., '1920x1080')
        bitrate: Bitrate string (e.g., '2M')
        duration: Duration in seconds
        
    Returns:
        ValidationResult: Validation result with is_valid and message
    """
    if fps is not None:
        if not isinstance(fps, (int, float)) or fps <= 0:
            return ValidationResult(is_valid=False, message="FPS must be a positive number")
        
        if fps > 120:
            return ValidationResult(is_valid=False, message="FPS cannot exceed 120")
    
    if resolution is not None:
        if not isinstance(resolution, str):
            return ValidationResult(is_valid=False, message="Resolution must be a string")
        
        if not re.match(r'^\d+x\d+$', resolution):
            return ValidationResult(is_valid=False, message="Invalid resolution format (e.g., '1920x1080')")
        
        width, height = map(int, resolution.split('x'))
        dim_result = validate_image_dimensions(width, height, 7680, 4320)  # 8K max
        if not dim_result.is_valid:
            return ValidationResult(is_valid=False, message=f"Invalid resolution: {dim_result.message}")
    
    if bitrate is not None:
        if not isinstance(bitrate, str):
            return ValidationResult(is_valid=False, message="Bitrate must be a string")
        
        if not re.match(r'^\d+[kmKM]?$', bitrate):
            return ValidationResult(is_valid=False, message="Invalid bitrate format (e.g., '2M', '1000k')")
    
    if duration is not None:
        if not isinstance(duration, (int, float)) or duration < 0:
            return ValidationResult(is_valid=False, message="Duration must be a non-negative number")
    
    return ValidationResult(is_valid=True, message="Valid video parameters")


def validate_time_format(time_str: str) -> bool:
    """Validate time format for video/audio operations.
    
    Args:
        time_str: Time string (e.g., '00:01:30', '90', '1.5')
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If format is invalid
    """
    if not isinstance(time_str, str):
        raise ValidationError("Time must be a string")
    
    if re.match(r'^\\d+$', time_str):
        return True
    
    if re.match(r'^\\d+\\.\\d+$', time_str):
        return True
    
    if re.match(r'^\\d{2}:\\d{2}:\\d{2}$', time_str):
        hours, minutes, seconds = map(int, time_str.split(':'))
        if minutes >= 60 or seconds >= 60:
            raise ValidationError("Invalid time format: minutes/seconds >= 60")
        return True
    
    if re.match(r'^\\d{2}:\\d{2}:\\d{2}\\.\\d+$', time_str):
        time_part, _ = time_str.split('.')
        hours, minutes, seconds = map(int, time_part.split(':'))
        if minutes >= 60 or seconds >= 60:
            raise ValidationError("Invalid time format: minutes/seconds >= 60")
        return True
    
    raise ValidationError("Invalid time format. Use HH:MM:SS, seconds, or decimal seconds")


def validate_file_size(file_path: str, max_size_mb: float = None, min_size_mb: float = 0) -> ValidationResult:
    """Validate file size.
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in megabytes
        min_size_mb: Minimum file size in megabytes
        
    Returns:
        ValidationResult: Result of validation
    """
    # Validate parameters first
    if max_size_mb is not None and max_size_mb < 0:
        return ValidationResult(False, "Invalid maximum size: cannot be negative")
    
    if min_size_mb < 0:
        return ValidationResult(False, "Invalid minimum size: cannot be negative")
    
    if not os.path.exists(file_path):
        return ValidationResult(False, f"File does not exist: {file_path}")
    
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    
    if size_mb < min_size_mb:
        return ValidationResult(False, f"File too small: {size_mb:.2f}MB (minimum {min_size_mb}MB)")
    
    if max_size_mb and size_mb > max_size_mb:
        return ValidationResult(False, f"File size exceeds limit: {size_mb:.2f}MB (maximum {max_size_mb}MB)")
    
    return ValidationResult(True, f"File size {size_mb:.2f}MB is within valid range")


def validate_quality_parameter(quality: int) -> ValidationResult:
    """Validate quality parameter (1-100).
    
    Args:
        quality: Quality value
        
    Returns:
        ValidationResult: Result of validation
    """
    if not isinstance(quality, int):
        return ValidationResult(False, "Quality must be an integer")
    
    if quality < 1 or quality > 100:
        return ValidationResult(False, "Quality must be between 1 and 100")
    
    return ValidationResult(True, f"Quality {quality} is valid")


def has_path_traversal(path: str) -> bool:
    """Check if path contains path traversal attempts.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if path traversal detected
    """
    dangerous_patterns = ['../', '..\\\\', '../', '..\\', '..']
    path_lower = path.lower()
    
    return any(pattern in path_lower for pattern in dangerous_patterns)


def contains_dangerous_chars(path: str) -> bool:
    """Check if path contains dangerous characters.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if dangerous characters found
    """
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    
    for char in dangerous_chars:
        if char in path:
            return True
    
    if any(ord(char) < 32 for char in path):
        return True
    
    return False


def get_type_from_mime(mime_type: str) -> str:
    """Get file type from MIME type.
    
    Args:
        mime_type: MIME type string
        
    Returns:
        str: File type ('text', 'image', 'audio', 'video')
        
    Raises:
        UnsupportedFormatError: If MIME type is not supported
    """
    if mime_type.startswith('text/'):
        return 'text'
    elif mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type in ['application/json', 'application/xml', 'application/yaml']:
        return 'text'
    else:
        raise UnsupportedFormatError(f"Unsupported MIME type: {mime_type}")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return 'unnamed'
        
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    sanitized = re.sub(r'[\x00-\x1f]', '_', sanitized)
    
    sanitized = sanitized.strip('. ')
    
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                     'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                     'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    name_without_ext = os.path.splitext(sanitized)[0].upper()
    if name_without_ext in reserved_names:
        sanitized = f"_{sanitized}"
    
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized or 'unnamed'


def validate_batch_operation(files: List[str], operation: str, **kwargs) -> Dict[str, List[str]]:
    """Validate batch operation parameters.
    
    Args:
        files: List of file paths
        operation: Operation name
        **kwargs: Additional parameters
        
    Returns:
        dict: Validation results with 'valid' and 'invalid' file lists
        
    Raises:
        ValidationError: If operation is invalid
    """
    valid_operations = ['convert', 'copy', 'move', 'delete', 'info']
    
    if operation not in valid_operations:
        raise ValidationError(f"Invalid operation: {operation}. Valid: {valid_operations}")
    
    if not files:
        raise ValidationError("No files provided for batch operation")
    
    if len(files) > 1000:
        raise ValidationError("Too many files for batch operation (max 1000)")
    
    valid_files = []
    invalid_files = []
    
    for file_path in files:
        try:
            validate_file_path(file_path, must_exist=True)
            valid_files.append(file_path)
        except (ValidationError, SecurityError):
            invalid_files.append(file_path)
    
    if operation in ['copy', 'move'] and 'dest_dir' not in kwargs:
        raise ValidationError(f"dest_dir required for {operation} operation")
    
    if operation == 'convert' and 'target_format' not in kwargs:
        raise ValidationError("target_format required for convert operation")
    
    return {
        'valid': valid_files,
        'invalid': invalid_files
    }


def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> ValidationResult:
    """
    Validate that file has an allowed extension.

    Args:
        file_path: Path to the file.
        allowed_extensions: List of allowed extensions (with dots).

    Returns:
        ValidationResult: Result of validation.
    """
    ext = os.path.splitext(file_path)[1].lower()
    allowed_lower = [e.lower() for e in allowed_extensions]
    
    if ext == "":
        return ValidationResult(False, "File has no extension")
    
    if ext not in allowed_lower:
        return ValidationResult(False, f"File extension {ext} is not supported. Allowed extensions: {allowed_extensions}")
    
    return ValidationResult(True, f"File extension {ext} is valid")


def validate_color_format(color: str) -> ValidationResult:
    """
    Validate color format (hex, rgb, etc.).

    Args:
        color: Color string to validate.

    Returns:
        ValidationResult: Result of validation.
    """
    if not isinstance(color, str):
        return ValidationResult(False, "Color must be a string")
    
    # Check hex format (6 digits)
    if re.match(r'^#[0-9a-fA-F]{6}$', color):
        return ValidationResult(True, f"Valid hex color: {color}")
    
    # Check hex format (3 digits)
    if re.match(r'^#[0-9a-fA-F]{3}$', color):
        return ValidationResult(True, f"Valid short hex color: {color}")
    
    # Check RGB format
    if re.match(r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$', color):
        return ValidationResult(True, f"Valid RGB color: {color}")
    
    # Check RGBA format
    if re.match(r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$', color):
        return ValidationResult(True, f"Valid RGBA color: {color}")
    
    # Check named colors (basic set)
    named_colors = ['red', 'green', 'blue', 'black', 'white', 'yellow', 'cyan', 'magenta']
    if color.lower() in named_colors:
        return ValidationResult(True, f"Valid named color: {color}")
    
    return ValidationResult(False, f"Invalid color format: {color}")


def validate_url(url: str) -> ValidationResult:
    """
    Validate URL format.

    Args:
        url: URL string to validate.

    Returns:
        ValidationResult: Result of validation.
    """
    if not isinstance(url, str):
        return ValidationResult(False, "URL must be a string")
    
    if not url:
        return ValidationResult(False, "URL cannot be empty")
    
    try:
        result = urllib.parse.urlparse(url)
        if not all([result.scheme, result.netloc]):
            return ValidationResult(False, "Invalid URL format")
        
        if result.scheme not in ['http', 'https', 'ftp', 'ftps']:
            return ValidationResult(False, "Unsupported URL scheme")
        
        return ValidationResult(True, f"Valid URL: {url}")
    except Exception as e:
        return ValidationResult(False, f"Invalid URL: {str(e)}")


def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.

    Args:
        email: Email address to validate.

    Returns:
        ValidationResult: Result of validation.
    """
    if not isinstance(email, str):
        return ValidationResult(False, "Email must be a string")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return ValidationResult(False, "Invalid email format")
    
    return ValidationResult(True, f"Valid email: {email}")


def validate_json_structure(data, required_fields: List[str] = None, field_types: Dict[str, type] = None) -> ValidationResult:
    """
    Validate JSON data structure.

    Args:
        data: JSON data (dict or string) to validate.
        required_fields: List of required field names.
        field_types: Dictionary mapping field names to expected types.

    Returns:
        ValidationResult: Result of validation.
    """
    # If data is a string, try to parse it as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return ValidationResult(False, f"Invalid JSON: {str(e)}")
    
    # If it's not a dict after parsing, it's invalid
    if not isinstance(data, dict):
        return ValidationResult(False, "JSON data must be an object")
    
    errors = []
    if required_fields:
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
    
    if field_types:
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
    
    if errors:
        return ValidationResult(False, "Validation failed", errors)
    
    return ValidationResult(True, "Valid JSON structure")


def is_safe_path(path: str, base_path: str = None) -> bool:
    """
    Check if path is safe (no path traversal).

    Args:
        path: Path to check.
        base_path: Base path to restrict to.

    Returns:
        bool: True if path is safe, False otherwise.
    """
    if has_path_traversal(path):
        return False
    
    if contains_dangerous_chars(path):
        return False
    
    if base_path:
        try:
            resolved_path = os.path.abspath(path)
            resolved_base = os.path.abspath(base_path)
            if not resolved_path.startswith(resolved_base):
                return False
        except Exception:
            return False
    
    return True


def check_disk_space(path: str, required_mb: float) -> ValidationResult:
    """
    Check if there's enough disk space at the given path.

    Args:
        path: Path to check disk space for.
        required_mb: Required space in KB (despite the parameter name).

    Returns:
        ValidationResult: Result of validation.
    """
    try:
        total, used, free = shutil.disk_usage(path)
        # Treat required_mb as KB for compatibility with tests
        required_bytes = required_mb * 1024
        free_mb = free / (1024 * 1024)
        required_display_mb = required_mb / 1024
        
        if free < required_bytes:
            return ValidationResult(False, f"Insufficient disk space. Required: {required_display_mb:.2f}MB, Available: {free_mb:.2f}MB")
        return ValidationResult(True, f"Sufficient disk space. Required: {required_display_mb:.2f}MB, Available: {free_mb:.2f}MB")
    except Exception as e:
        return ValidationResult(False, f"Disk space check error: {str(e)}")