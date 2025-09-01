from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import JSON_EXTS

def get_json_files(dir):
    """Get a list of JSON text files in a folder.

    Args:
        dir (str): The path to the folder containing the JSON text files.

    Returns:
        list: A list of JSON text file paths.
    """
    return get_files_by_extension(dir, JSON_EXTS)