from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import SUPPORTED_AUDIO_EXTENSIONS

def count_audio_files(audio_folder_path):
    """Count the number of audio files in a folder.

    Args:
        audio_folder_path (str): The path to the folder containing the audio files.

    Returns:
        int: The number of audio files in the folder.
    """
    files = get_files_by_extension(audio_folder_path, SUPPORTED_AUDIO_EXTENSIONS)
    return len(files)

def get_audio_files(dir, file_extensions=SUPPORTED_AUDIO_EXTENSIONS):
    """Get a list of audio files in a folder.

    Args:
        dir (str): The path to the folder containing the audio files.
        file_extensions (list, optional): A list of file extensions to consider as audio files.

    Returns:
        list: A list of audio file paths.
    """
    files = get_files_by_extension(dir, file_extensions, relative=True)
    return files