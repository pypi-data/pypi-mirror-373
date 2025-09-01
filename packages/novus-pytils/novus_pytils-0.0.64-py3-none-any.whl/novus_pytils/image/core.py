from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import SUPPORTED_IMAGE_EXTENSIONS

def count_image_files(image_folder_path):
    """Count the number of image files in a folder.

    Args:
        image_folder_path (str): The path to the folder containing the image files.

    Returns:
        int: The number of image files in the folder.
    """
    files = get_files_by_extension(image_folder_path, SUPPORTED_IMAGE_EXTENSIONS)
    return len(files)


def get_image_files(dir, file_extensions=SUPPORTED_IMAGE_EXTENSIONS):
    """Get a list of image files in a folder.

    Args:
        dir (str): The path to the folder containing the image files.
        file_extensions (list, optional): A list of file extensions to consider as image files.

    Returns:
        list: A list of image file paths.
    """
    files = get_files_by_extension(dir, file_extensions, relative=True)
    return files