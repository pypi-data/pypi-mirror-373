from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import FLV_EXTS

def get_flv_files(dir):
    """Get a list of FLV video files in a folder.

    Args:
        dir (str): The path to the folder containing the FLV video files.

    Returns:
        list: A list of FLV video file paths.
    """
    return get_files_by_extension(dir, FLV_EXTS)