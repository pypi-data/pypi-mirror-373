import wave
import struct
import numpy as np
from typing import Dict, Union
from pathlib import Path
from novus_pytils.files.core import get_files_by_extension
from novus_pytils.utils.hash import get_file_md5_hash
from novus_pytils.exceptions import WAVError
from novus_pytils.globals import WAVE_EXTS
from novus_pytils.audio.wav_parser import WAVParser
from novus_pytils.audio.wrappers import PydubWrapper

def get_wav_files(dir):
    """Get all WAV files in a directory.

    Args:
        dir (str): The directory to search for WAV files.

    Returns:
        list: A list of paths to WAV files in the directory.
    """
    return get_files_by_extension(dir, WAVE_EXTS, relative=True)

def read_wav_file(filename):
    """Reads a WAV file and returns the audio data and file metadata."""
    with wave.open(filename, 'rb') as wav_file:
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()
        duration = num_frames / frame_rate

        audio_data = np.frombuffer(wav_file.readframes(num_frames), dtype=np.int16)

        return audio_data, num_channels, sample_width, frame_rate, num_frames, duration

def get_wav_metadata(wav_filepath: str) -> dict:
    """Get metadata information from a WAV file."""
    with wave.open(wav_filepath, 'rb') as wav_file:
        return {
            "filepath": wav_filepath,
            "file_size": wav_file.getnframes() * wav_file.getnchannels() * wav_file.getsampwidth(),
            "num_channels": wav_file.getnchannels(),
            "sample_width": wav_file.getsampwidth(),
            "frame_rate": wav_file.getframerate(),
            "num_frames": wav_file.getnframes(),
            "duration": wav_file.getnframes() / wav_file.getframerate()
        }

def analyze_wav_file(wav_path, input_dir):
    """Analyze a WAV file and extract comprehensive information."""
    wav_path = Path(wav_path)
    file_info = {
        'filename': wav_path.name,
        'relative_path': str(wav_path.relative_to(input_dir)),
        'full_path': str(wav_path),
        'file_size_bytes': 0,
        'file_size_mb': 0.0,
        'sample_rate': 0,
        'num_channels': 0,
        'num_frames': 0,
        'sample_width_bytes': 0,
        'sample_width_bits': 0,
        'length_seconds': 0.0,
        'length_milliseconds': 0,
        'length_formatted': '00:00:00.000',
        'md5_hash': '',
        'compression_type': '',
        'compression_name': '',
        'status': 'Success',
        'error_message': ''
    }
    
    try:
        file_info['file_size_bytes'] = wav_path.stat().st_size
        file_info['file_size_mb'] = file_info['file_size_bytes'] / (1024 * 1024)
        
        with wave.open(str(wav_path), 'rb') as wav_file:
            file_info['num_channels'] = wav_file.getnchannels()
            file_info['sample_rate'] = wav_file.getframerate()
            file_info['num_frames'] = wav_file.getnframes()
            file_info['sample_width_bytes'] = wav_file.getsampwidth()
            file_info['sample_width_bits'] = file_info['sample_width_bytes'] * 8
            file_info['compression_type'] = wav_file.getcomptype()
            file_info['compression_name'] = wav_file.getcompname()
            
            if file_info['sample_rate'] > 0:
                file_info['length_seconds'] = file_info['num_frames'] / file_info['sample_rate']
                file_info['length_milliseconds'] = int(file_info['length_seconds'] * 1000)
                
                hours = int(file_info['length_seconds'] // 3600)
                minutes = int((file_info['length_seconds'] % 3600) // 60)
                seconds = file_info['length_seconds'] % 60
                file_info['length_formatted'] = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        
        file_info['md5_hash'] = get_file_md5_hash(wav_path)
        
    except wave.Error as e:
        file_info['status'] = 'WAV Error'
        file_info['error_message'] = str(e)
    except Exception as e:
        file_info['status'] = 'Error'
        file_info['error_message'] = str(e)
    
    return file_info

def write_wav_file(filename, audio_data, num_channels, sample_width, frame_rate):
    """Writes audio data to a WAV file with specified parameters."""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(audio_data.tobytes())

def parse_wav(file_path: Union[str, Path]) -> Dict:
    """Quick function to parse a WAV file and return information."""
    parser = WAVParser(file_path)
    return parser.parse()

def validate_wav(file_path: Union[str, Path]) -> bool:
    """Check if a file is a valid WAV file."""
    try:
        parse_wav(file_path)
        return True
    except (WAVError, FileNotFoundError, struct.error):
        return False
    
def wav_to_mp3(wav_file, mp3_file, bitrate="192k", channels=None):
    """Convert a WAV audio file to MP3 format.

    Args:
        wav_file (str): The path to the input WAV audio file.
        mp3_file (str): The path to the output MP3 audio file.
        bitrate (str): The bitrate for the output MP3 file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_mp3(mp3_file, bitrate, channels)
    
def wav_to_aac(wav_file, aac_file, bitrate="192k", channels=None):
    """Convert a WAV audio file to AAC format.

    Args:
        wav_file (str): The path to the input WAV audio file.
        aac_file (str): The path to the output AAC audio file.
        bitrate (str): The bitrate for the output AAC file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_aac(aac_file, bitrate, channels)
    
def wav_to_m4a(wav_file, m4a_file, bitrate="192k", channels=None):
    """Convert a WAV audio file to M4A format.

    Args:
        wav_file (str): The path to the input WAV audio file.
        m4a_file (str): The path to the output M4A audio file.
        bitrate (str): The bitrate for the output M4A file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_m4a(m4a_file, bitrate, channels)
    
def wav_to_flac(wav_file, flac_file, bitrate=None, channels=None):
    """Convert a WAV audio file to FLAC format.

    Args:
        wav_file (str): The path to the input WAV audio file.
        flac_file (str): The path to the output FLAC audio file.
        bitrate (str): The bitrate for the output file (not applicable for FLAC).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_flac(flac_file, channels)
    
def wav_to_ogg(wav_file, ogg_file, bitrate="192k", channels=None):
    """Convert a WAV audio file to OGG format.

    Args:
        wav_file (str): The path to the input WAV audio file.
        ogg_file (str): The path to the output OGG audio file.
        bitrate (str): The bitrate for the output OGG file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_ogg(ogg_file, bitrate, channels)

def wav_to_wma(wav_file, wma_file, bitrate="192k", channels=None):
    """Convert a WAV audio file to WMA format.

    Args:
        wav_file (str): The path to the input WAV audio file.
        wma_file (str): The path to the output WMA audio file.
        bitrate (str): The bitrate for the output WMA file (default is "192k").
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_wma(wma_file, bitrate, channels)
 
def wav_to_wav(wav_file, wav_file_out, bitrate=None, channels=None):
    """Convert a WAV audio file to another WAV audio file with specified parameters.

    Args:
        wav_file (str): The path to the input WAV audio file.
        wav_file_out (str): The path to the output WAV audio file.
        bitrate (str): The bitrate for the output file (not applicable for WAV).
        channels (int): The number of channels for the output file.

    Returns:
        None
    """
    wrapper = PydubWrapper(wav_file)
    wrapper.to_wav(wav_file_out, channels)