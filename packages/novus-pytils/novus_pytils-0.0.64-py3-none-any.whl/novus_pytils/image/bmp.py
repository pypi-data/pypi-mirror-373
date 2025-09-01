from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import BMP_EXTS
from novus_pytils.image.wrappers import PillowWrapper

def get_bmp_files(dir):
    """Get a list of BMP image files in a folder.

    Args:
        dir (str): The path to the folder containing the BMP image files.

    Returns:
        list: A list of BMP image file paths.
    """
    return get_files_by_extension(dir, BMP_EXTS)

def is_bmp_file(file):
    """Check if a file is a BMP image file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a BMP image file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in BMP_EXTS)

def filter_bmp_files(files):
    """Filter a list of files to include only BMP image files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of BMP image file paths.
    """
    return [file for file in files if is_bmp_file(file)]

def count_bmp_files(dir):
    """Count the number of BMP image files in a folder.

    Args:
        dir (str): The path to the folder containing the BMP image files.

    Returns:
        int: The number of BMP image files in the folder.
    """
    return len(get_bmp_files(dir))

def has_bmp_files(dir):
    """Check if a folder contains any BMP image files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any BMP image files, False otherwise.
    """
    return count_bmp_files(dir) > 0

def bmp_to_jpg(bmp_file, jpg_file, quality=95, optimize=True):
    """Convert a BMP image file to JPG/JPEG format.

    Args:
        bmp_file (str): The path to the input BMP image file.
        jpg_file (str): The path to the output JPG/JPEG image file.
        quality (int): JPEG quality (1-100, default: 95).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(bmp_file)
    wrapper.to_jpeg(jpg_file, quality, optimize)

def bmp_to_png(bmp_file, png_file, optimize=True):
    """Convert a BMP image file to PNG format.

    Args:
        bmp_file (str): The path to the input BMP image file.
        png_file (str): The path to the output PNG image file.
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(bmp_file)
    wrapper.to_png(png_file, optimize)

def bmp_to_webp(bmp_file, webp_file, quality=90, optimize=True):
    """Convert a BMP image file to WebP format.

    Args:
        bmp_file (str): The path to the input BMP image file.
        webp_file (str): The path to the output WebP image file.
        quality (int): WebP quality (1-100, default: 90).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(bmp_file)
    wrapper.to_webp(webp_file, quality, optimize)

def bmp_to_tiff(bmp_file, tiff_file, compression=None):
    """Convert a BMP image file to TIFF format.

    Args:
        bmp_file (str): The path to the input BMP image file.
        tiff_file (str): The path to the output TIFF image file.
        compression (str): Compression method ('lzw', 'jpeg', 'packbits', etc.).

    Returns:
        None
    """
    wrapper = PillowWrapper(bmp_file)
    wrapper.to_tiff(tiff_file, compression)

def bmp_to_gif(bmp_file, gif_file):
    """Convert a BMP image file to GIF format.

    Args:
        bmp_file (str): The path to the input BMP image file.
        gif_file (str): The path to the output GIF image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(bmp_file)
    wrapper.to_gif(gif_file)

def bmp_to_bmp(bmp_file, output_bmp_file):
    """Convert a BMP image file to another BMP file.

    Args:
        bmp_file (str): The path to the input BMP image file.
        output_bmp_file (str): The path to the output BMP image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(bmp_file)
    wrapper.to_bmp(output_bmp_file)