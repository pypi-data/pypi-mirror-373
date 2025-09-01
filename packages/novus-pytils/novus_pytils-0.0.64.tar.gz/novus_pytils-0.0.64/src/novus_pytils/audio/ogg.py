from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import OGG_EXTS
from novus_pytils.audio.wrappers import PydubWrapper

def get_ogg_files(dir):
    """Get a list of OGG audio files in a folder.

    Args:
        dir (str): The path to the folder containing the OGG audio files.

    Returns:
        list: A list of OGG audio file paths.
    """
    return get_files_by_extension(dir, OGG_EXTS)


def is_ogg_file(file):
    """Check if a file is an OGG audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is an OGG audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in OGG_EXTS)

def filter_ogg_files(files):
    """Filter a list of files to include only OGG audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of OGG audio file paths.
    """
    return [file for file in files if is_ogg_file(file)]

def count_ogg_files(dir):
    """Count the number of OGG audio files in a folder.

    Args:
        dir (str): The path to the folder containing the OGG audio files.

    Returns:
        int: The number of OGG audio files in the folder.
    """
    return len(get_ogg_files(dir))

def has_ogg_files(dir):
    """Check if a folder contains any OGG audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any OGG audio files, False otherwise.
    """
    return count_ogg_files(dir) > 0


def ogg_to_wav(ogg_file, wav_file, bitrate=None, channels=None):
    """Convert an OGG audio file to WAV format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        wav_file (str): The path to the output WAV audio file.
        bitrate (str): The bitrate for the output file (not applicable for WAV).
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_wav(wav_file, channels)
    
def ogg_to_mp3(ogg_file, mp3_file, bitrate="192k", channels=None):
    """Convert an OGG audio file to MP3 format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        mp3_file (str): The path to the output MP3 audio file.
        bitrate (str): The bitrate for the output MP3 file (default is "192k").
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_mp3(mp3_file, bitrate, channels)
    
def ogg_to_aac(ogg_file, aac_file, bitrate="192k", channels=None):
    """Convert an OGG audio file to AAC format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        aac_file (str): The path to the output AAC audio file.
        bitrate (str): The bitrate for the output AAC file (default is "192k").
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_aac(aac_file, bitrate, channels)
    
def ogg_to_m4a(ogg_file, m4a_file, bitrate="192k", channels=None):
    """Convert an OGG audio file to M4A format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        m4a_file (str): The path to the output M4A audio file.
        bitrate (str): The bitrate for the output M4A file (default is "192k").
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_m4a(m4a_file, bitrate, channels)
    
def ogg_to_flac(ogg_file, flac_file, bitrate=None, channels=None):
    """Convert an OGG audio file to FLAC format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        flac_file (str): The path to the output FLAC audio file.
        bitrate (str): The bitrate for the output file (not applicable for FLAC).
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_flac(flac_file, channels)
    
def ogg_to_wma(ogg_file, wma_file, bitrate="192k", channels=None):
    """Convert an OGG audio file to WMA format.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        wma_file (str): The path to the output WMA audio file.
        bitrate (str): The bitrate for the output WMA file (default is "192k").
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_wma(wma_file, bitrate, channels)
    
def ogg_to_ogg(ogg_file, ogg_out_file, bitrate="192k", channels=None):
    """Convert an OGG audio file to another OGG file with specified bitrate.

    Args:
        ogg_file (str): The path to the input OGG audio file.
        ogg_out_file (str): The path to the output OGG audio file.
        bitrate (str): The bitrate for the output OGG file (default is "192k").
        channels (int): The number of channels for the output file.
    """
    wrapper = PydubWrapper(ogg_file)
    wrapper.to_ogg(ogg_out_file, bitrate, channels)