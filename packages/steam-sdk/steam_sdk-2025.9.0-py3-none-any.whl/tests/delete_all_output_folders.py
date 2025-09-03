import os
import shutil

from steam_sdk.utils.find_delete_files import find_delete_files

if __name__ == "__main__":
    flag_delete = True

    # Delete all folders named "output" in the project
    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        for dirname in dirnames:
            if dirname == "output":
                output_path = os.path.join(dirpath, dirname)
                if os.path.isdir(output_path):
                    if flag_delete:
                        shutil.rmtree(output_path)
                    print(f"Deleted {output_path}")

    # Delete all LEDET diaries in selected folders
    print('Delete temporary files')
    list_folders = ['analyses', 'drivers']
    for folder in list_folders:
        target_extensions = ['.txt']  # Change this to the extensions you're targeting
        # if flag_delete:
        n_deleted = find_delete_files(folder, target_extensions, target_suffix='diaryLEDET_')