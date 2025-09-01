from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import SVG_EXTS

def get_svg_files(dir):
    """Get a list of SVG image files in a folder.

    Args:
        dir (str): The path to the folder containing the SVG image files.

    Returns:
        list: A list of SVG image file paths.
    """
    return get_files_by_extension(dir, SVG_EXTS)