import os
from pathlib import Path

from steam_sdk.data.DataModelParsimDakota import DataModelParsimDakota
from steam_sdk.data.DataAnalysis import DataAnalysis
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.drivers.DriverDakota import DriverDakota
from steam_sdk.parsers.ParserDakota import ParserDakota
from steam_sdk.parsers.ParserYAML import yaml_to_data, model_data_to_yaml
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing

class ParsimDakota:
    """
    Main class for running parametric simulations with Dakota
    """

    def __init__(self, input_DAKOTA_yaml: str = None, verbose: bool = True):
        """
        This is paramat
        If verbose is set to True, additional information will be displayed
        """
        # Read dakota yaml and analysis yaml
        data_model_dakota: DataModelParsimDakota = yaml_to_data(input_DAKOTA_yaml, DataModelParsimDakota)

        if Path(data_model_dakota.relative_path_analysis_file).is_absolute():
            analysis_file_path = data_model_dakota.relative_path_analysis_file
        else:
            analysis_file_path = str(Path(os.path.join(os.path.dirname(input_DAKOTA_yaml), data_model_dakota.relative_path_analysis_file)).resolve())
        data_model_analysis: DataAnalysis = yaml_to_data(analysis_file_path, DataAnalysis)

        # deal with settings cases for either from analysis or from setting file

        self.settings = DataSettings()  # object containing the settings acquired during initialization
        if data_model_analysis.GeneralParameters.flag_permanent_settings: # use settings from analysis file and
            data_settings: DataSettings = DataSettings(**data_model_analysis.PermanentSettings.model_dump())
            absolute_path_library = str(Path(os.path.join(analysis_file_path, data_model_analysis.PermanentSettings.local_library_path)).resolve())
        else:
            full_path_file_settings = os.path.join(Path(os.path.dirname(analysis_file_path), Path(data_model_analysis.GeneralParameters.relative_path_settings)).resolve(), f"settings.{os.getlogin()}.yaml")  # use settings file from the tests folder of the SDK
            if not os.path.isfile(full_path_file_settings):
                raise Exception(f'Local setting file {full_path_file_settings} not found. This file must be provided when flag_permanent_settings is set to False.')
            data_settings: DataSettings = yaml_to_data(full_path_file_settings, DataSettings)
            data_model_analysis.GeneralParameters.relative_path_settings = os.path.dirname(full_path_file_settings)
            absolute_path_library = str(Path(os.path.join(os.path.dirname(analysis_file_path), data_settings.local_library_path)).resolve())

        dakota_working_folder = str(Path(os.path.join(os.path.dirname(input_DAKOTA_yaml), data_settings.local_Dakota_folder, data_model_dakota.parsim_name)).resolve())
        for field_name, field_value in data_settings.model_dump().items():
            if field_value:
                if not os.path.isabs(field_value):
                    tool = field_name.split('_')[-2]
                    if tool == 'Dakota':
                        field_value = dakota_working_folder
                    elif tool == 'library':
                        field_value = absolute_path_library
                    elif tool not in ['library', 'Dakota']:
                        field_value = os.path.join(dakota_working_folder, tool)
                setattr(self.settings, field_name, field_value)

        data_model_analysis.PermanentSettings = self.settings
        data_model_analysis.GeneralParameters.flag_permanent_settings = True

        # update the library path to absolute as the analysis file is going to be saved locally:
        make_folder_if_not_existing(dakota_working_folder)
        written_analysis_file = os.path.join(dakota_working_folder, os.path.basename(analysis_file_path))
        #written_analysis_file = os.path.join(settings.local_PyCoSim_folder, os.path.basename(analysis_file_path))
        model_data_to_yaml(data_model_analysis, written_analysis_file)
        # write dakota input file (.in) from yaml Dakota parametric study definition
        ParserDakota().assemble_in_file(data_model_dakota=data_model_dakota, dakota_working_folder=dakota_working_folder)

        # run analysis with pre iterable steps and iterables steps via dakota and its input file
        DriverDakota(analysis_yaml_path=written_analysis_file, data_model_dakota=data_model_dakota, settings=data_settings)


