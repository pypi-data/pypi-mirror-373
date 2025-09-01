from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import GIF_EXTS
from novus_pytils.image.wrappers import PillowWrapper

def get_gif_files(dir):
    """Get a list of GIF image files in a folder.

    Args:
        dir (str): The path to the folder containing the GIF image files.

    Returns:
        list: A list of GIF image file paths.
    """
    return get_files_by_extension(dir, GIF_EXTS)

def is_gif_file(file):
    """Check if a file is a GIF image file.

    Args:
        file (str): The path to the file to check.

    Returns:
        bool: True if the file is a GIF image file, False otherwise.
    """
    return any(file.lower().endswith(ext) for ext in GIF_EXTS)

def filter_gif_files(files):
    """Filter a list of files to include only GIF image files.

    Args:
        files (list): A list of file paths to filter.

    Returns:
        list: A list of GIF image file paths.
    """
    return [file for file in files if is_gif_file(file)]

def count_gif_files(dir):
    """Count the number of GIF image files in a folder.

    Args:
        dir (str): The path to the folder containing the GIF image files.

    Returns:
        int: The number of GIF image files in the folder.
    """
    return len(get_gif_files(dir))

def has_gif_files(dir):
    """Check if a folder contains any GIF image files.

    Args:
        dir (str): The path to the folder to check.

    Returns:
        bool: True if the folder contains any GIF image files, False otherwise.
    """
    return count_gif_files(dir) > 0

def gif_to_jpg(gif_file, jpg_file, quality=95, optimize=True):
    """Convert a GIF image file to JPG/JPEG format.

    Args:
        gif_file (str): The path to the input GIF image file.
        jpg_file (str): The path to the output JPG/JPEG image file.
        quality (int): JPEG quality (1-100, default: 95).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(gif_file)
    wrapper.to_jpeg(jpg_file, quality, optimize)

def gif_to_png(gif_file, png_file, optimize=True):
    """Convert a GIF image file to PNG format.

    Args:
        gif_file (str): The path to the input GIF image file.
        png_file (str): The path to the output PNG image file.
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(gif_file)
    wrapper.to_png(png_file, optimize)

def gif_to_webp(gif_file, webp_file, quality=90, optimize=True):
    """Convert a GIF image file to WebP format.

    Args:
        gif_file (str): The path to the input GIF image file.
        webp_file (str): The path to the output WebP image file.
        quality (int): WebP quality (1-100, default: 90).
        optimize (bool): Whether to optimize the output file (default: True).

    Returns:
        None
    """
    wrapper = PillowWrapper(gif_file)
    wrapper.to_webp(webp_file, quality, optimize)

def gif_to_bmp(gif_file, bmp_file):
    """Convert a GIF image file to BMP format.

    Args:
        gif_file (str): The path to the input GIF image file.
        bmp_file (str): The path to the output BMP image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(gif_file)
    wrapper.to_bmp(bmp_file)

def gif_to_tiff(gif_file, tiff_file, compression=None):
    """Convert a GIF image file to TIFF format.

    Args:
        gif_file (str): The path to the input GIF image file.
        tiff_file (str): The path to the output TIFF image file.
        compression (str): Compression method ('lzw', 'jpeg', 'packbits', etc.).

    Returns:
        None
    """
    wrapper = PillowWrapper(gif_file)
    wrapper.to_tiff(tiff_file, compression)

def gif_to_gif(gif_file, output_gif_file):
    """Convert a GIF image file to another GIF file.

    Args:
        gif_file (str): The path to the input GIF image file.
        output_gif_file (str): The path to the output GIF image file.

    Returns:
        None
    """
    wrapper = PillowWrapper(gif_file)
    wrapper.to_gif(output_gif_file)