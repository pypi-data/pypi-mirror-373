from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import PNG_EXTS
from novus_pytils.image.wrappers import PillowWrapper

def get_png_files(dir):
    """Get a list of PNG image files in a folder.

    Args:
        dir (str): The path to the folder containing the PNG image files.

    Returns:
        list: A list of PNG image file paths.
    """
    return get_files_by_extension(dir, PNG_EXTS)

def is_png_file(file):
    """Check if a file is a PNG image file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a PNG image file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in PNG_EXTS)

def filter_png_files(files):
    """Filter a list of files to include only PNG image files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of PNG image file paths.
    """
    return [file for file in files if is_png_file(file)]

def count_png_files(dir):
    """Count the number of PNG image files in a folder.

    Args:
        dir (str): The path to the folder containing the PNG image files.

    Returns:
        int: The number of PNG image files in the folder.
    """
    return len(get_png_files(dir))

def has_png_files(dir):
    """Check if a folder contains any PNG image files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any PNG image files, False otherwise.
    """
    return count_png_files(dir) > 0

def png_to_jpg(png_file, jpg_file, quality=95, optimize=True):
    """Convert a PNG image file to JPG/JPEG format.

    Args:
        png_file (str): The path to the input PNG image file.
        jpg_file (str): The path to the output JPG/JPEG image file.
        quality (int): JPEG quality (1-100, default: 95).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(png_file)
    wrapper.to_jpeg(jpg_file, quality, optimize)

def png_to_webp(png_file, webp_file, quality=90, optimize=True, lossless=False):
    """Convert a PNG image file to WebP format.

    Args:
        png_file (str): The path to the input PNG image file.
        webp_file (str): The path to the output WebP image file.
        quality (int): WebP quality (1-100, default: 90).
        optimize (bool): Whether to optimize the output file (default: True).
        lossless (bool): Whether to use lossless compression (default: False).

    Returns:
        None
    """
    wrapper = PillowWrapper(png_file)
    wrapper.to_webp(webp_file, quality, optimize, lossless)

def png_to_bmp(png_file, bmp_file):
    """Convert a PNG image file to BMP format.

    Args:
        png_file (str): The path to the input PNG image file.
        bmp_file (str): The path to the output BMP image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(png_file)
    wrapper.to_bmp(bmp_file)

def png_to_tiff(png_file, tiff_file, compression=None):
    """Convert a PNG image file to TIFF format.

    Args:
        png_file (str): The path to the input PNG image file.
        tiff_file (str): The path to the output TIFF image file.
        compression (str): Compression method ('lzw', 'jpeg', 'packbits', etc.).

    Returns:
        None
    """
    wrapper = PillowWrapper(png_file)
    wrapper.to_tiff(tiff_file, compression)

def png_to_gif(png_file, gif_file):
    """Convert a PNG image file to GIF format.

    Args:
        png_file (str): The path to the input PNG image file.
        gif_file (str): The path to the output GIF image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(png_file)
    wrapper.to_gif(gif_file)

def png_to_png(png_file, output_png_file, optimize=True):
    """Convert a PNG image file to another PNG file with specified parameters.

    Args:
        png_file (str): The path to the input PNG image file.
        output_png_file (str): The path to the output PNG image file.
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(png_file)
    wrapper.to_png(output_png_file, optimize)