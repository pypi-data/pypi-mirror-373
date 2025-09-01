from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import CSV_EXTS

def get_csv_files(dir):
    """Get a list of CSV text files in a folder.

    Args:
        dir (str): The path to the folder containing the CSV text files.

    Returns:
        list: A list of CSV text file paths.
    """
    return get_files_by_extension(dir, CSV_EXTS)