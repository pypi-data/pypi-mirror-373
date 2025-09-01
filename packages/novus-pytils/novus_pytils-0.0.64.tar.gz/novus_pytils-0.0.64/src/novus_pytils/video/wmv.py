from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import WMV_EXTS

def get_wmv_files(dir):
    """Get a list of WMV video files in a folder.

    Args:
        dir (str): The path to the folder containing the WMV video files.

    Returns:
        list: A list of WMV video file paths.
    """
    return get_files_by_extension(dir, WMV_EXTS)