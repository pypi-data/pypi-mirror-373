from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import SUPPORTED_VIDEO_EXTENSIONS

def count_video_files(video_folder_path):
    """Count the number of video files in a folder.

    Args:
        video_folder_path (str): The path to the folder containing the video files.

    Returns:
        int: The number of video files in the folder.
    """
    files = get_files_by_extension(video_folder_path, SUPPORTED_VIDEO_EXTENSIONS)
    return len(files)


def get_video_files(dir, file_extensions=SUPPORTED_VIDEO_EXTENSIONS):
    """Get a list of video files in a folder.

    Args:
        dir (str): The path to the folder containing the video files.
        file_extensions (list, optional): A list of file extensions to consider as video files.

    Returns:
        list: A list of video file paths.
    """
    files = get_files_by_extension(dir, file_extensions, relative=True)
    return files