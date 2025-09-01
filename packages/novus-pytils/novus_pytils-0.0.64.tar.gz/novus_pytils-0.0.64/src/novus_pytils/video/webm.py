from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import WEBM_EXTS

def get_webm_files(dir):
    """Get a list of WEBM video files in a folder.

    Args:
        dir (str): The path to the folder containing the WEBM video files.

    Returns:
        list: A list of WEBM video file paths.
    """
    return get_files_by_extension(dir, WEBM_EXTS)