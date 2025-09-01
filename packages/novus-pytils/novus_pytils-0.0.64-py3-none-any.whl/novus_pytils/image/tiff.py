from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import TIFF_EXTS
from novus_pytils.image.wrappers import PillowWrapper

def get_tiff_files(dir):
    """Get a list of TIFF image files in a folder.

    Args:
        dir (str): The path to the folder containing the TIFF image files.

    Returns:
        list: A list of TIFF image file paths.
    """
    return get_files_by_extension(dir, TIFF_EXTS)

def is_tiff_file(file):
    """Check if a file is a TIFF image file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a TIFF image file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in TIFF_EXTS)

def filter_tiff_files(files):
    """Filter a list of files to include only TIFF image files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of TIFF image file paths.
    """
    return [file for file in files if is_tiff_file(file)]

def count_tiff_files(dir):
    """Count the number of TIFF image files in a folder.

    Args:
        dir (str): The path to the folder containing the TIFF image files.

    Returns:
        int: The number of TIFF image files in the folder.
    """
    return len(get_tiff_files(dir))

def has_tiff_files(dir):
    """Check if a folder contains any TIFF image files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any TIFF image files, False otherwise.
    """
    return count_tiff_files(dir) > 0

def tiff_to_jpg(tiff_file, jpg_file, quality=95, optimize=True):
    """Convert a TIFF image file to JPG/JPEG format.

    Args:
        tiff_file (str): The path to the input TIFF image file.
        jpg_file (str): The path to the output JPG/JPEG image file.
        quality (int): JPEG quality (1-100, default: 95).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(tiff_file)
    wrapper.to_jpeg(jpg_file, quality, optimize)

def tiff_to_png(tiff_file, png_file, optimize=True):
    """Convert a TIFF image file to PNG format.

    Args:
        tiff_file (str): The path to the input TIFF image file.
        png_file (str): The path to the output PNG image file.
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(tiff_file)
    wrapper.to_png(png_file, optimize)

def tiff_to_webp(tiff_file, webp_file, quality=90, optimize=True):
    """Convert a TIFF image file to WebP format.

    Args:
        tiff_file (str): The path to the input TIFF image file.
        webp_file (str): The path to the output WebP image file.
        quality (int): WebP quality (1-100, default: 90).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(tiff_file)
    wrapper.to_webp(webp_file, quality, optimize)

def tiff_to_bmp(tiff_file, bmp_file):
    """Convert a TIFF image file to BMP format.

    Args:
        tiff_file (str): The path to the input TIFF image file.
        bmp_file (str): The path to the output BMP image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(tiff_file)
    wrapper.to_bmp(bmp_file)

def tiff_to_gif(tiff_file, gif_file):
    """Convert a TIFF image file to GIF format.

    Args:
        tiff_file (str): The path to the input TIFF image file.
        gif_file (str): The path to the output GIF image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(tiff_file)
    wrapper.to_gif(gif_file)

def tiff_to_tiff(tiff_file, output_tiff_file, compression=None):
    """Convert a TIFF image file to another TIFF file with specified compression.

    Args:
        tiff_file (str): The path to the input TIFF image file.
        output_tiff_file (str): The path to the output TIFF image file.
        compression (str): Compression method ('lzw', 'jpeg', 'packbits', etc.).

    Returns:
        None
    """
    wrapper = PillowWrapper(tiff_file)
    wrapper.to_tiff(output_tiff_file, compression)