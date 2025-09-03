import os
import shutil


def delete_if_existing(folder, verbose: bool = True):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        if verbose: print(f'Folder {folder} already existed. It was removed.')
