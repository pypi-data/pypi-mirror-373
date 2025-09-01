from novus_pytils.files import get_files_by_extension
from novus_pytils.globals import SUPPORTED_TEXT_EXTENSIONS

def count_text_files(text_folder_path):
    """Count the number of text files in a folder.

    Args:
        text_folder_path (str): The path to the folder containing the text files.

    Returns:
        int: The number of text files in the folder.
    """
    files = get_files_by_extension(text_folder_path, SUPPORTED_TEXT_EXTENSIONS)
    return len(files)


def get_text_files(dir, file_extensions=SUPPORTED_TEXT_EXTENSIONS):
    """Get a list of text files in a folder.

    Args:
        dir (str): The path to the folder containing the text files.
        file_extensions (list, optional): A list of file extensions to consider as text files.

    Returns:
        list: A list of text file paths.
    """
    files = get_files_by_extension(dir, file_extensions, relative=True)
    return files