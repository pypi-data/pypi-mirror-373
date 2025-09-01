from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import MP4_EXTS

def get_mp4_files(dir):
    """Get a list of MP4 video files in a folder.

    Args:
        dir (str): The path to the folder containing the MP4 video files.

    Returns:
        list: A list of MP4 video file paths.
    """
    return get_files_by_extension(dir, MP4_EXTS)