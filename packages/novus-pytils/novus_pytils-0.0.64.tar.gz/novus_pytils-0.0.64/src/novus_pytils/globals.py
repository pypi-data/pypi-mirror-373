"""Global constants and configuration values.

This module defines constants used throughout the novus_pytils package.
"""

# TODO Maybe? These extensions might be better as a dictionary "extension: filetype" leaving this for now

# Audio Extensions
WAVE_EXTS = ['.wav']
OGG_EXTS = ['.ogg']
FLAC_EXTS = ['.flac']
MP3_EXTS = ['.mp3']
AAC_EXTS = ['.aac']
WMA_EXTS = ['.wma']
M4A_EXTS = ['.m4a']

SUPPORTED_AUDIO_EXTENSIONS = WAVE_EXTS + OGG_EXTS + FLAC_EXTS + MP3_EXTS + AAC_EXTS + WMA_EXTS + M4A_EXTS

# Text Extensions
TXT_EXTS = ['.txt']
MD_EXTS = ['.md', '.markdown', '.mdown', '.mkd', '.mdwn', '.mdtxt', '.mdtext', '.mdx']
CSV_EXTS = ['.csv']
JSON_EXTS = ['.json']
XML_EXTS = ['.xml']
LOG_EXTS = ['.log']
INI_EXTS = ['.ini']
CFG_EXTS = ['.cfg', '.conf', '.config']
YAML_EXTS = ['.yaml', '.yml']

SUPPORTED_TEXT_EXTENSIONS = TXT_EXTS + MD_EXTS + CSV_EXTS + JSON_EXTS + XML_EXTS + LOG_EXTS + INI_EXTS + CFG_EXTS + YAML_EXTS

# Video Extensions
AVI_EXTS = ['.avi']
MKV_EXTS = ['.mkv']
MP4_EXTS = ['.mp4']
MOV_EXTS = ['.mov']
WMV_EXTS = ['.wmv'] 
FLV_EXTS = ['.flv']
WEBM_EXTS = ['.webm']
M4V_EXTS = ['.m4v']

SUPPORTED_VIDEO_EXTENSIONS = AVI_EXTS + MKV_EXTS + MP4_EXTS + MOV_EXTS + WMV_EXTS + FLV_EXTS + WEBM_EXTS + M4V_EXTS

# Image Extensions
JPG_EXTS = ['.jpg', '.jpeg']
PNG_EXTS = ['.png']
GIF_EXTS = ['.gif']
BMP_EXTS = ['.bmp']
TIFF_EXTS = ['.tiff', '.tif']
WEBP_EXTS = ['.webp']
SVG_EXTS = ['.svg']

SUPPORTED_IMAGE_EXTENSIONS = JPG_EXTS + PNG_EXTS + GIF_EXTS + BMP_EXTS + TIFF_EXTS + WEBP_EXTS + SVG_EXTS

# Compression Extensions
ZIP_EXTS = ['.zip'] # TODO Add more archive types later

SUPPORTED_COMPRESSION_EXTENSIONS = ZIP_EXTS

# TODO Update conversion maps when conversion modules are refactored
AUDIO_CONVERSION_MAP = {
    '.wav': ['.mp3', '.ogg', '.flac', '.aac'],
    '.mp3': ['.wav', '.ogg', '.flac', '.aac'],
    '.ogg': ['.wav', '.mp3', '.flac', '.aac'],
    '.flac': ['.wav', '.mp3', '.ogg', '.aac'],
    '.aac': ['.wav', '.mp3', '.ogg', '.flac']
}

VIDEO_CONVERSION_MAP = {
    '.mp4': ['.avi', '.mkv', '.mov', '.webm'],
    '.avi': ['.mp4', '.mkv', '.mov', '.webm'],
    '.mkv': ['.mp4', '.avi', '.mov', '.webm'],
    '.mov': ['.mp4', '.avi', '.mkv', '.webm'],
    '.webm': ['.mp4', '.avi', '.mkv', '.mov']
}

IMAGE_CONVERSION_MAP = {
    '.jpg': ['.png', '.gif', '.bmp', '.tiff', '.webp'],
    '.jpeg': ['.png', '.gif', '.bmp', '.tiff', '.webp'],
    '.png': ['.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'],
    '.gif': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
    '.bmp': ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp'],
    '.tiff': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    '.webp': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
}

TEXT_CONVERSION_MAP = {
    '.txt': ['.md', '.csv', '.json', '.xml', '.yaml'],
    '.md': ['.txt', '.html', '.pdf'],
    '.csv': ['.json', '.xml', '.txt'],
    '.json': ['.xml', '.yaml', '.csv', '.txt'],
    '.xml': ['.json', '.yaml', '.csv', '.txt'],
    '.yaml': ['.json', '.xml', '.txt']
}

def get_all_supported_extensions():
    """
    Get all supported file extensions.

    Returns:
        list: A list of all supported file extensions.
    """
    return (SUPPORTED_AUDIO_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS + 
            SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_TEXT_EXTENSIONS + SUPPORTED_COMPRESSION_EXTENSIONS)

def is_supported_extension(extension: str) -> bool:
    """
    Check if a file extension is supported.

    Args:
        extension (str): The file extension to check.

    Returns:
        bool: True if the extension is supported, False otherwise.
    """
    return extension.lower() in get_all_supported_extensions()

def get_file_type_by_extension(extension: str) -> str:
    """
    Get the file type based on its extension.

    Args:
        extension (str): The file extension.

    Returns:
        str: The file type ('audio', 'video', 'image', 'text', or 'unknown').
    """
    ext = extension.lower()
    if ext in SUPPORTED_AUDIO_EXTENSIONS:
        return 'audio'
    elif ext in SUPPORTED_VIDEO_EXTENSIONS:
        return 'video'
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in SUPPORTED_TEXT_EXTENSIONS:
        return 'text'
    else:
        return 'unknown'

def validate_file_type(file_path: str) -> bool:
    """
    Validate if a file type is supported.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file type is supported, False otherwise.
    """
    import os
    extension = os.path.splitext(file_path)[1].lower()
    return is_supported_extension(extension)