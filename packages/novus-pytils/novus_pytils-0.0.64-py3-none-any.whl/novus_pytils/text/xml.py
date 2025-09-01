from novus_pytils.files.core import get_files_by_extension
from novus_pytils.globals import XML_EXTS

def get_xml_files(dir):
    """Get a list of XML text files in a folder.

    Args:
        dir (str): The path to the folder containing the XML text files.

    Returns:
        list: A list of XML text file paths.
    """
    return get_files_by_extension(dir, XML_EXTS)