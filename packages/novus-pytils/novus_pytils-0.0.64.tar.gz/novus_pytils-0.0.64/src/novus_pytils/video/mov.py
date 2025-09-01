from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import MOV_EXTS

def get_mov_files(dir):
    """Get a list of MOV video files in a folder.

    Args:
        dir (str): The path to the folder containing the MOV video files.

    Returns:
        list: A list of MOV video file paths.
    """
    return get_files_by_extension(dir, MOV_EXTS)