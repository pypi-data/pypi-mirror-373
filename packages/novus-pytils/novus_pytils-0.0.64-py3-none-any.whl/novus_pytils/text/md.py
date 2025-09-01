from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import MD_EXTS

def get_md_files(dir):
    """Get a list of Markdown text files in a folder.

    Args:
        dir (str): The path to the folder containing the Markdown text files.

    Returns:
        list: A list of Markdown text file paths.
    """
    return get_files_by_extension(dir, MD_EXTS)