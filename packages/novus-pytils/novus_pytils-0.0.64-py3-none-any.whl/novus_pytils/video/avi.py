from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import AVI_EXTS

def get_avi_files(dir):
    """Get a list of AVI video files in a folder.

    Args:
        dir (str): The path to the folder containing the AVI video files.

    Returns:
        list: A list of AVI video file paths.
    """
    return get_files_by_extension(dir, AVI_EXTS)