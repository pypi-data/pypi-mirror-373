from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import M4V_EXTS

def get_m4v_files(dir):
    """Get a list of M4V video files in a folder.

    Args:
        dir (str): The path to the folder containing the M4V video files.

    Returns:
        list: A list of M4V video file paths.
    """
    return get_files_by_extension(dir, M4V_EXTS)