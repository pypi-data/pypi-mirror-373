"""Tests for novus_pytils.audio.core module."""

import pytest
from unittest.mock import patch, MagicMock

from novus_pytils.audio.core import count_audio_files, get_audio_files


class TestCountAudioFiles:
    """Test the count_audio_files function."""
    
    @patch('novus_pytils.audio.core.get_files_by_extension')
    def test_count_audio_files_basic(self, mock_get_files):
        mock_get_files.return_value = ["file1.mp3", "file2.wav", "file3.flac"]
        
        result = count_audio_files("/test/path")
        
        assert result == 3
        mock_get_files.assert_called_once()
    
    @patch('novus_pytils.audio.core.get_files_by_extension')
    def test_count_audio_files_no_files(self, mock_get_files):
        mock_get_files.return_value = []
        
        result = count_audio_files("/empty/path")
        
        assert result == 0
    
    @patch('novus_pytils.audio.core.get_files_by_extension')
    def test_count_audio_files_uses_supported_extensions(self, mock_get_files):
        mock_get_files.return_value = ["file1.mp3"]
        
        count_audio_files("/test/path")
        
        # Verify it's called with SUPPORTED_AUDIO_EXTENSIONS
        args, kwargs = mock_get_files.call_args
        assert args[0] == "/test/path"
        # Second argument should be the supported extensions


class TestGetAudioFiles:
    """Test the get_audio_files function."""
    
    @patch('novus_pytils.audio.core.get_files_by_extension')
    @patch('novus_pytils.audio.core.SUPPORTED_AUDIO_EXTENSIONS', ['.wav', '.ogg', '.flac', '.mp3', '.aac', '.wma', '.m4a'])
    def test_get_audio_files_basic(self, mock_get_files):
        expected_files = ["music.mp3", "sound.wav", "audio.flac"]
        mock_get_files.return_value = expected_files
        
        result = get_audio_files("/test/dir")
        
        assert result == expected_files
        mock_get_files.assert_called_once_with("/test/dir", ['.wav', '.ogg', '.flac', '.mp3', '.aac', '.wma', '.m4a'], relative=True)
    
    @patch('novus_pytils.audio.core.get_files_by_extension')
    def test_get_audio_files_with_custom_extensions(self, mock_get_files):
        custom_extensions = [".mp3", ".wav"]
        mock_get_files.return_value = ["file.mp3", "file.wav"]
        
        result = get_audio_files("/test/dir", file_extensions=custom_extensions)
        
        assert result == ["file.mp3", "file.wav"]
        mock_get_files.assert_called_once_with("/test/dir", custom_extensions, relative=True)
    
    @patch('novus_pytils.audio.core.get_files_by_extension')
    def test_get_audio_files_empty_directory(self, mock_get_files):
        mock_get_files.return_value = []
        
        result = get_audio_files("/empty/dir")
        
        assert result == []