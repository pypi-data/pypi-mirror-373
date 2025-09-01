from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import INI_EXTS

def get_ini_files(dir):
    """Get a list of INI text files in a folder.

    Args:
        dir (str): The path to the folder containing the INI text files.

    Returns:
        list: A list of INI text file paths.
    """
    return get_files_by_extension(dir, INI_EXTS)