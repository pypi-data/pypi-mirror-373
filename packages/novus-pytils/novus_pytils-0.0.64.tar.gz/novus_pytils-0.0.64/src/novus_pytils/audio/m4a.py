from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import M4A_EXTS
from novus_pytils.audio.wrappers import PydubWrapper

def get_m4a_files(dir):
    """Get a list of M4A audio files in a folder.

    Args:
        dir (str): The path to the folder containing the M4A audio files.

    Returns:
        list: A list of M4A audio file paths.
    """
    return get_files_by_extension(dir, M4A_EXTS)

def is_m4a_file(file):
    """Check if a file is an M4A audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is an M4A audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in M4A_EXTS)

def filter_m4a_files(files):
    """Filter a list of files to include only M4A audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of M4A audio file paths.
    """
    return [file for file in files if is_m4a_file(file)]

def count_m4a_files(dir):
    """Count the number of M4A audio files in a folder.

    Args:
        dir (str): The path to the folder containing the M4A audio files.

    Returns:
        int: The number of M4A audio files in the folder.
    """
    return len(get_m4a_files(dir))

def has_m4a_files(dir):
    """Check if a folder contains any M4A audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any M4A audio files, False otherwise.
    """
    return count_m4a_files(dir) > 0

def m4a_to_wav(m4a_file, wav_file, bitrate=None, channels=None):
    """Convert an M4A audio file to WAV format.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        wav_file (str): The path to save the converted WAV audio file.
        bitrate (str): The bitrate for the output file (not applicable for WAV).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_wav(wav_file, channels)
    
def m4a_to_mp3(m4a_file, mp3_file, bitrate="192k", channels=None):
    """Convert an M4A audio file to MP3 format.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        mp3_file (str): The path to save the converted MP3 audio file.
        bitrate (str): The bitrate for the output MP3 file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_mp3(mp3_file, bitrate, channels)
    
def m4a_to_aac(m4a_file, aac_file, bitrate="192k", channels=None):
    """Convert an M4A audio file to AAC format.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        aac_file (str): The path to save the converted AAC audio file.
        bitrate (str): The bitrate for the output AAC file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_aac(aac_file, bitrate, channels)
    
def m4a_to_flac(m4a_file, flac_file, bitrate=None, channels=None):
    """Convert an M4A audio file to FLAC format.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        flac_file (str): The path to save the converted FLAC audio file.
        bitrate (str): The bitrate for the output file (not applicable for FLAC).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_flac(flac_file, channels)
    
def m4a_to_wma(m4a_file, wma_file, bitrate="192k", channels=None):
    """Convert an M4A audio file to WMA format.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        wma_file (str): The path to save the converted WMA audio file.
        bitrate (str): The bitrate for the output WMA file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_wma(wma_file, bitrate, channels)
    
def m4a_to_ogg(m4a_file, ogg_file, bitrate="192k", channels=None):
    """Convert an M4A audio file to OGG format.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        ogg_file (str): The path to save the converted OGG audio file.
        bitrate (str): The bitrate for the output OGG file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_ogg(ogg_file, bitrate, channels)
    
def m4a_to_m4a(m4a_file, m4a_out_file, bitrate="192k", channels=None):
    """Convert an M4A audio file to another M4A file with specified bitrate.

    Args:
        m4a_file (str): The path to the M4A audio file to convert.
        m4a_out_file (str): The path to save the converted M4A audio file.
        bitrate (str): The bitrate for the output M4A file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(m4a_file)
    wrapper.to_m4a(m4a_out_file, bitrate, channels)