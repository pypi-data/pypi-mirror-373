from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import CFG_EXTS

def get_cfg_files(dir):
    """Get a list of configuration text files in a folder.

    Args:
        dir (str): The path to the folder containing the configuration text files.

    Returns:
        list: A list of configuration text file paths.
    """
    return get_files_by_extension(dir, CFG_EXTS)