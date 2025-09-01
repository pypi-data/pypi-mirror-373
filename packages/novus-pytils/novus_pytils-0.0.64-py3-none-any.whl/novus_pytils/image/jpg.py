from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import JPG_EXTS
from novus_pytils.image.wrappers import PillowWrapper

def get_jpg_files(dir):
    """Get a list of JPG/JPEG image files in a folder.

    Args:
        dir (str): The path to the folder containing the JPG/JPEG image files.

    Returns:
        list: A list of JPG/JPEG image file paths.
    """
    return get_files_by_extension(dir, JPG_EXTS)

def is_jpg_file(file):
    """Check if a file is a JPG/JPEG image file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a JPG/JPEG image file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in JPG_EXTS)

def filter_jpg_files(files):
    """Filter a list of files to include only JPG/JPEG image files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of JPG/JPEG image file paths.
    """
    return [file for file in files if is_jpg_file(file)]

def count_jpg_files(dir):
    """Count the number of JPG/JPEG image files in a folder.

    Args:
        dir (str): The path to the folder containing the JPG/JPEG image files.

    Returns:
        int: The number of JPG/JPEG image files in the folder.
    """
    return len(get_jpg_files(dir))

def has_jpg_files(dir):
    """Check if a folder contains any JPG/JPEG image files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any JPG/JPEG image files, False otherwise.
    """
    return count_jpg_files(dir) > 0

def jpg_to_png(jpg_file, png_file, optimize=True):
    """Convert a JPG/JPEG image file to PNG format.

    Args:
        jpg_file (str): The path to the input JPG/JPEG image file.
        png_file (str): The path to the output PNG image file.
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(jpg_file)
    wrapper.to_png(png_file, optimize)

def jpg_to_webp(jpg_file, webp_file, quality=90, optimize=True):
    """Convert a JPG/JPEG image file to WebP format.

    Args:
        jpg_file (str): The path to the input JPG/JPEG image file.
        webp_file (str): The path to the output WebP image file.
        quality (int): WebP quality (1-100, default: 90).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(jpg_file)
    wrapper.to_webp(webp_file, quality, optimize)

def jpg_to_bmp(jpg_file, bmp_file):
    """Convert a JPG/JPEG image file to BMP format.

    Args:
        jpg_file (str): The path to the input JPG/JPEG image file.
        bmp_file (str): The path to the output BMP image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(jpg_file)
    wrapper.to_bmp(bmp_file)

def jpg_to_tiff(jpg_file, tiff_file, compression=None):
    """Convert a JPG/JPEG image file to TIFF format.

    Args:
        jpg_file (str): The path to the input JPG/JPEG image file.
        tiff_file (str): The path to the output TIFF image file.
        compression (str): Compression method ('lzw', 'jpeg', 'packbits', etc.).

    Returns:
        None
    """
    wrapper = PillowWrapper(jpg_file)
    wrapper.to_tiff(tiff_file, compression)

def jpg_to_gif(jpg_file, gif_file):
    """Convert a JPG/JPEG image file to GIF format.

    Args:
        jpg_file (str): The path to the input JPG/JPEG image file.
        gif_file (str): The path to the output GIF image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(jpg_file)
    wrapper.to_gif(gif_file)

def jpg_to_jpg(jpg_file, output_jpg_file, quality=95, optimize=True):
    """Convert a JPG/JPEG image file to another JPG/JPEG file with specified quality.

    Args:
        jpg_file (str): The path to the input JPG/JPEG image file.
        output_jpg_file (str): The path to the output JPG/JPEG image file.
        quality (int): JPEG quality (1-100, default: 95).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(jpg_file)
    wrapper.to_jpeg(output_jpg_file, quality, optimize)