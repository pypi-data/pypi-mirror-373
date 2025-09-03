import os
from pathlib import Path


def make_folder_if_not_existing(folder: str, verbose: bool = False) -> None:
    """
    Helper function for creating a folder by specifying a path. If the folder exists nothing is created.
    :param folder: full path to folder to be made
    :type folder: str
    :param verbose: If true more text is printed to the console
    :type verbose: bool
    :return: Nothing, just creates folder on disk if not existing already.
    :rtype: None
    """
    if not os.path.isdir(folder):
        Path(folder).mkdir(parents=True, exist_ok=True)
        if verbose:
            print("Folder {} does not exist. Making it now".format(folder))
