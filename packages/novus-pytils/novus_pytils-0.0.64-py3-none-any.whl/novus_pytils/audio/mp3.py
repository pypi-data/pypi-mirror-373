from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import MP3_EXTS
from novus_pytils.audio.wrappers import PydubWrapper

def get_mp3_files(dir):
    """Get a list of MP3 audio files in a folder.

    Args:
        dir (str): The path to the folder containing the MP3 audio files.

    Returns:
        list: A list of MP3 audio file paths.
    """
    return get_files_by_extension(dir, MP3_EXTS)

def is_mp3_file(file):
    """Check if a file is an MP3 audio file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is an MP3 audio file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in MP3_EXTS)

def filter_mp3_files(files):
    """Filter a list of files to include only MP3 audio files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of MP3 audio file paths.
    """
    return [file for file in files if is_mp3_file(file)]

def count_mp3_files(dir):
    """Count the number of MP3 audio files in a folder.

    Args:
        dir (str): The path to the folder containing the MP3 audio files.

    Returns:
        int: The number of MP3 audio files in the folder.
    """
    return len(get_mp3_files(dir))

def has_mp3_files(dir):
    """Check if a folder contains any MP3 audio files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any MP3 audio files, False otherwise.
    """
    return count_mp3_files(dir) > 0

def mp3_to_wav(mp3_file, wav_file, bitrate=None, channels=None):
    """Convert an MP3 audio file to WAV format.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        wav_file (str): The path to the output WAV audio file.
        bitrate (str): The bitrate for the output file (not applicable for WAV).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_wav(wav_file, channels)
    
def mp3_to_aac(mp3_file, aac_file, bitrate="192k", channels=None):
    """Convert an MP3 audio file to AAC format.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        aac_file (str): The path to the output AAC audio file.
        bitrate (str): The bitrate for the output AAC file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_aac(aac_file, bitrate, channels)
    
def mp3_to_m4a(mp3_file, m4a_file, bitrate="192k", channels=None):
    """Convert an MP3 audio file to M4A format.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        m4a_file (str): The path to the output M4A audio file.
        bitrate (str): The bitrate for the output M4A file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_m4a(m4a_file, bitrate, channels)
    
def mp3_to_flac(mp3_file, flac_file, bitrate=None, channels=None):
    """Convert an MP3 audio file to FLAC format.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        flac_file (str): The path to the output FLAC audio file.
        bitrate (str): The bitrate for the output file (not applicable for FLAC).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_flac(flac_file, channels)
    
def mp3_to_wma(mp3_file, wma_file, bitrate="192k", channels=None):
    """Convert an MP3 audio file to WMA format.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        wma_file (str): The path to the output WMA audio file.
        bitrate (str): The bitrate for the output WMA file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_wma(wma_file, bitrate, channels)
    
def mp3_to_ogg(mp3_file, ogg_file, bitrate="192k", channels=None):
    """Convert an MP3 audio file to OGG format.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        ogg_file (str): The path to the output OGG audio file.
        bitrate (str): The bitrate for the output OGG file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_ogg(ogg_file, bitrate, channels)
    
def mp3_to_mp3(mp3_file, output_mp3_file, bitrate="192k", channels=None):
    """Convert an MP3 audio file to another MP3 file with a specified bitrate.

    Args:
        mp3_file (str): The path to the input MP3 audio file.
        output_mp3_file (str): The path to the output MP3 audio file.
        bitrate (str): The bitrate for the output MP3 file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(mp3_file)
    wrapper.to_mp3(output_mp3_file, bitrate, channels)