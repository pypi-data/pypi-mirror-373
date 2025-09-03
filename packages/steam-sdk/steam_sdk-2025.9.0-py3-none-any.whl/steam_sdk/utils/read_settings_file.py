import os

from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserYAML import yaml_to_data


# def read_settings_file(relative_path_settings: str = None, verbose: bool = False):
#     user_name = os.getlogin()
#     if verbose:
#         print('user_name:   {}'.format(user_name))
#     if not relative_path_settings:
#         relative_path_settings = '../'
#     path_settings_folder = Path(os.getcwd() / Path(relative_path_settings)).resolve()
#     settings_file = Path.joinpath(path_settings_folder, f"settings.{user_name}.yaml")
#     if not Path.exists(settings_file):
#         raise Exception(f'Settings file not found at: {settings_file}')
#     data_settings: DataSettings = yaml_to_data(settings_file, DataSettings)
#
#     if verbose:
#         print(f'path_settings: {path_settings_folder}')
#         print(f'path to settings file: {settings_file}')
#
#     return data_settings

def read_settings_file(absolute_path_settings_folder: str = None, verbose: bool = False):
    user_name = os.getlogin()
    if verbose:
        print('user_name:   {}'.format(user_name))
    settings_file = os.path.join(absolute_path_settings_folder, f"settings.{user_name}.yaml")
    if not os.path.exists(settings_file):
        raise Exception(f'Settings file not found at: {settings_file}')
    data_settings: DataSettings = yaml_to_data(settings_file, DataSettings)

    if verbose:
        print(f'path_settings: {absolute_path_settings_folder}')
        print(f'path to settings file: {settings_file}')

    return data_settings
