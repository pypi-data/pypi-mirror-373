from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import LOG_EXTS

def get_log_files(dir):
    """Get a list of LOG text files in a folder.

    Args:
        dir (str): The path to the folder containing the LOG text files.

    Returns:
        list: A list of LOG text file paths.
    """
    return get_files_by_extension(dir, LOG_EXTS)