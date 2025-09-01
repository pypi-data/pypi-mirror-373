from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import MKV_EXTS

def get_mkv_files(dir):
    """Get a list of MKV video files in a folder.

    Args:
        dir (str): The path to the folder containing the MKV video files.

    Returns:
        list: A list of MKV video file paths.
    """
    return get_files_by_extension(dir, MKV_EXTS)