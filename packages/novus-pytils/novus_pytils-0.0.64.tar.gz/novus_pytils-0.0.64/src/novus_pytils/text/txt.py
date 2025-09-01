from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import TXT_EXTS

def get_txt_files(dir):
    """Get a list of TXT text files in a folder.

    Args:
        dir (str): The path to the folder containing the TXT text files.

    Returns:
        list: A list of TXT text file paths.
    """
    return get_files_by_extension(dir, TXT_EXTS)