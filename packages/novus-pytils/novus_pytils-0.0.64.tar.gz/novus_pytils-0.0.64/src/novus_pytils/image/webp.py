from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import WEBP_EXTS
from novus_pytils.image.wrappers import PillowWrapper

def get_webp_files(dir):
    """Get a list of WEBP image files in a folder.

    Args:
        dir (str): The path to the folder containing the WEBP image files.

    Returns:
        list: A list of WEBP image file paths.
    """
    return get_files_by_extension(dir, WEBP_EXTS)

def is_webp_file(file):
    """Check if a file is a WEBP image file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a WEBP image file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in WEBP_EXTS)

def filter_webp_files(files):
    """Filter a list of files to include only WEBP image files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of WEBP image file paths.
    """
    return [file for file in files if is_webp_file(file)]

def count_webp_files(dir):
    """Count the number of WEBP image files in a folder.

    Args:
        dir (str): The path to the folder containing the WEBP image files.

    Returns:
        int: The number of WEBP image files in the folder.
    """
    return len(get_webp_files(dir))

def has_webp_files(dir):
    """Check if a folder contains any WEBP image files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any WEBP image files, False otherwise.
    """
    return count_webp_files(dir) > 0

def webp_to_jpg(webp_file, jpg_file, quality=95, optimize=True):
    """Convert a WEBP image file to JPG/JPEG format.

    Args:
        webp_file (str): The path to the input WEBP image file.
        jpg_file (str): The path to the output JPG/JPEG image file.
        quality (int): JPEG quality (1-100, default: 95).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(webp_file)
    wrapper.to_jpeg(jpg_file, quality, optimize)

def webp_to_png(webp_file, png_file, optimize=True):
    """Convert a WEBP image file to PNG format.

    Args:
        webp_file (str): The path to the input WEBP image file.
        png_file (str): The path to the output PNG image file.
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(webp_file)
    wrapper.to_png(png_file, optimize)

def webp_to_bmp(webp_file, bmp_file):
    """Convert a WEBP image file to BMP format.

    Args:
        webp_file (str): The path to the input WEBP image file.
        bmp_file (str): The path to the output BMP image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(webp_file)
    wrapper.to_bmp(bmp_file)

def webp_to_tiff(webp_file, tiff_file, compression=None):
    """Convert a WEBP image file to TIFF format.

    Args:
        webp_file (str): The path to the input WEBP image file.
        tiff_file (str): The path to the output TIFF image file.
        compression (str): Compression method ('lzw', 'jpeg', 'packbits', etc.).

    Returns:
        None
    """
    wrapper = PillowWrapper(webp_file)
    wrapper.to_tiff(tiff_file, compression)

def webp_to_gif(webp_file, gif_file):
    """Convert a WEBP image file to GIF format.

    Args:
        webp_file (str): The path to the input WEBP image file.
        gif_file (str): The path to the output GIF image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(webp_file)
    wrapper.to_gif(gif_file)

def webp_to_webp(webp_file, output_webp_file, quality=90, optimize=True, lossless=False):
    """Convert a WEBP image file to another WEBP file with specified parameters.

    Args:
        webp_file (str): The path to the input WEBP image file.
        output_webp_file (str): The path to the output WEBP image file.
        quality (int): WebP quality (1-100, default: 90).
        optimize (bool): Whether to optimize the output file (default: True).
        lossless (bool): Whether to use lossless compression (default: False).

    Returns:
        None
    """
    wrapper = PillowWrapper(webp_file)
    wrapper.to_webp(output_webp_file, quality, optimize, lossless)