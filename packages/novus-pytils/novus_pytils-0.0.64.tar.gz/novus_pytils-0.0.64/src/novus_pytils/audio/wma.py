from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import WMA_EXTS
from novus_pytils.audio.wrappers import PydubWrapper

def get_wma_files(dir):
    """Get a list of WMA audio files in a folder.

    Args:
        dir (str): The path to the folder containing the WMA audio files.

    Returns:
        list: A list of WMA audio file paths.
    """
    return get_files_by_extension(dir, WMA_EXTS)

def is_wma_file(file):
    """Check if a file is a WMA audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a WMA audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in WMA_EXTS)

def filter_wma_files(files):
    """Filter a list of files to include only WMA audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of WMA audio file paths.
    """
    return [file for file in files if is_wma_file(file)]

def count_wma_files(dir):
    """Count the number of WMA audio files in a folder.

    Args:
        dir (str): The path to the folder containing the WMA audio files.

    Returns:
        int: The number of WMA audio files in the folder.
    """
    return len(get_wma_files(dir))

def has_wma_files(dir):
    """Check if a folder contains any WMA audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any WMA audio files, False otherwise.
    """
    return count_wma_files(dir) > 0

def wma_to_wav(wma_file, wav_file, bitrate=None, channels=None):
    """Convert a WMA audio file to WAV format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        wav_file (str): The path to the output WAV audio file.
        bitrate (str): The bitrate for the output file (not applicable for WAV).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_wav(wav_file, channels)
    
def wma_to_mp3(wma_file, mp3_file, bitrate="192k", channels=None):
    """Convert a WMA audio file to MP3 format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        mp3_file (str): The path to the output MP3 audio file.
        bitrate (str): The bitrate for the output MP3 file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_mp3(mp3_file, bitrate, channels)
    
def wma_to_aac(wma_file, aac_file, bitrate="192k", channels=None):
    """Convert a WMA audio file to AAC format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        aac_file (str): The path to the output AAC audio file.
        bitrate (str): The bitrate for the output AAC file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_aac(aac_file, bitrate, channels)
    
def wma_to_m4a(wma_file, m4a_file, bitrate="192k", channels=None):
    """Convert a WMA audio file to M4A format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        m4a_file (str): The path to the output M4A audio file.
        bitrate (str): The bitrate for the output M4A file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_m4a(m4a_file, bitrate, channels)
    
def wma_to_flac(wma_file, flac_file, bitrate=None, channels=None):
    """Convert a WMA audio file to FLAC format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        flac_file (str): The path to the output FLAC audio file.
        bitrate (str): The bitrate for the output file (not applicable for FLAC).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_flac(flac_file, channels)
    
def wma_to_ogg(wma_file, ogg_file, bitrate="192k", channels=None):
    """Convert a WMA audio file to OGG format.

    Args:
        wma_file (str): The path to the input WMA audio file.
        ogg_file (str): The path to the output OGG audio file.
        bitrate (str): The bitrate for the output OGG file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_ogg(ogg_file, bitrate, channels)
    
def wma_to_wma(wma_file, wma_out_file, bitrate="192k", channels=None):
    """Convert a WMA audio file to another WMA file with specified bitrate.

    Args:
        wma_file (str): The path to the input WMA audio file.
        wma_out_file (str): The path to the output WMA audio file.
        bitrate (str): The bitrate for the output WMA file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wma_file)
    wrapper.to_wma(wma_out_file, bitrate, channels)
