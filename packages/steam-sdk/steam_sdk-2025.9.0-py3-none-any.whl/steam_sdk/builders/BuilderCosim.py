import datetime
import os
from pathlib import Path
from typing import Union

from steam_sdk.data.DataModelCosim import DataModelCosim
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserCOSIM import ParserCOSIM
from steam_sdk.parsers.ParserPyCoSim import ParserPyCoSim
from steam_sdk.parsers.ParserYAML import yaml_to_data


class BuilderCosim:
    """
        Class to generate co-operative simulation models, which can be later on run with various co-simulation tools
    """

    def __init__(self,
                 file_model_data: str,
                 data_settings: DataSettings,
                 verbose: bool = False
                 ):
        """
            Builder object to generate models from STEAM simulation tools specified by user

            file_model_data: path to folder with input data (roxie files, geometry, modelData.yaml = config from user input)
            :param data_settings: DataSettings object containing all settings, previously read from user specific settings.SYSTEM.yaml file or from a STEAM analysis permanent settings
            verbose: to display internal processes (output of status & error messages) for troubleshooting
        """

        # Unpack arguments
        self.file_model_data: str = file_model_data
        self.settings_dict = data_settings
        self.verbose: bool = verbose

        # Set case_model to "cosim". At the moment this is the only option, so it is hard-coded, but in the future there might be different model cases to support (in this case, an additional argument will be needed)
        self.case_model = 'cosim'

        if verbose:
            print('Settings:')
            [print(attr, getattr(self.settings_dict, attr)) for attr in
             self.settings_dict.__dict__.keys()]  # Print all settings

        # Initialize
        self.cosim_data: DataModelCosim = DataModelCosim()

        # Load model data from the input .yaml file
        self.loadModelCosim()

        # Set paths of input files
        self.set_input_paths()

        # Display time stamp
        if self.verbose:
            print(f'BuilderModel ended. Time stamp: {datetime.datetime.now()}')

    def set_input_paths(self):
        """
            Sets input paths from created DataModelCosim and displays related information
        """
        # TODO: Add test for this method

        # Find folder where the input file is located, which will be used as the "anchor" for all input files
        self.path_input_file = Path(self.file_model_data).parent
        if self.verbose:
            print('These paths were set:')
            print(f'path_input_file:   {self.path_input_file}')

    def loadModelCosim(self):
        """
            Loads model data from yaml file to model data object
        """
        if self.verbose:
            print('Loading .yaml file to cosim model data object.')

        # Load yaml keys into DataModelCosim dataclass
        self.cosim_data = yaml_to_data(self.file_model_data, DataModelCosim)

    def buildCOSIM(self, sim_name: str, sim_number: int, output_path: str, verbose: bool = None):
        """
            Build a COSIM model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number that will be used to write the output file  #TODO Note this parser only supports int as sim_number
            :param output_path: Output folder
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        # sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number

        # Make COSIM model
        pCOSIM = ParserCOSIM(cosim_data=self.cosim_data, data_settings=self.settings_dict)
        pCOSIM.write_cosim_model(sim_name=sim_name, sim_number=sim_number, output_path_COSIM_folder=output_path, verbose=verbose)

    def buildPyCoSim(self, sim_name: str, sim_number: Union[int, str], output_path: str, verbose: bool = None):
        """
            Build a PyCoSim input file (this is a shortened version of the generic cosim model data yaml file)
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number

        # Make PyCoSim input file
        path_output_file = os.path.join(output_path, f'{sim_name}{sim_suffix}.yaml')
        pPyCoSim = ParserPyCoSim(cosim_data=self.cosim_data)
        pPyCoSim.write_cosim_model(full_path_file_name=path_output_file, verbose=verbose)
