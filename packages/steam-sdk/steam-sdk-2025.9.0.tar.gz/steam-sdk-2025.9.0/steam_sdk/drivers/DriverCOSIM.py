import json
import os
from pathlib import Path
from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.drivers.DriverLEDET import DriverLEDET
from steam_sdk.parsers.ParserLEDET import ParserLEDET
from subprocess import call
from typing import Union


class DriverCOSIM:
    '''
        Class to run COSIM models in Windows.
        This class was written with the help of G. Vallone (LBNL).
    '''

    def __init__(self, COSIM_path: str, path_folder_COSIM: str, verbose: bool = False):
        '''
        Initialize class to run COSIM models.

        :param COSIM_path: Path to COSIM executable, for example: \\eosproject-smb\eos\project\s\steam\download\cosim\steam-cosim_v0.5.exe
        :param path_folder_COSIM: Path to COSIM library folder
        :param verbose: If True, print some logging information
        '''

        # Unpack arguments
        self.COSIM_path = COSIM_path
        self.path_folder_COSIM = path_folder_COSIM
        self.verbose = verbose
        if verbose:
            print(f'COSIM_path: {COSIM_path}')
            print(f'path_folder_COSIM: {path_folder_COSIM}')
            print(f'verbose: {verbose}')

    def run(self, simulation_name: str, sim_number: Union[str, int], verbose: bool = None, flag_report_LEDET: bool = True):
        '''
        Run the COSIM model
        :param simulation_name: Name of the co-simulation model to run
        :param sim_number: String or number identifying the simulation to run
        :param verbose: If True, print some logging information
        :param flag_report_LEDET: If True, re-run LEDET simulations at the end of the co-simulation to obtain the .pdf reports
        :return: null
        '''
        if verbose == None:
            verbose = self.verbose
        # Define string to run
        callString = self._make_callString(model_name=simulation_name, sim_number=sim_number)
        if verbose:
            print(f'DriverCOSIM - Call string:\n{callString}')

        # Run
        call(callString, shell=False)
        if verbose:
            print(f'DriverCOSIM - Run finished for the called string:\n{callString}')

        # Optional post-processing
        if flag_report_LEDET:
            # Read the COSIM configuration file
            path_config_file = os.path.join(self.path_folder_COSIM, simulation_name, str(sim_number), 'Output', 'COSIMConfig.json')
            with open(path_config_file, 'r') as file:
                dict_config_cosim = json.load(file)

            # Loop through all models of the co-simulation and re-run the LEDET simulations to obtain the .pdf reports
            path_cosim_output_folder = dict_config_cosim['coSimulationDir']
            for item in os.listdir(path_cosim_output_folder):
                item_path = os.path.join(path_cosim_output_folder, item)

                # Check if it's a folder and ends with "_LEDET"
                if os.path.isdir(item_path) and item.endswith('_LEDET'):
                    if verbose:
                        print(f"Found folder with suffix '_LEDET': {item_path}")
                    # Find LEDET configuration file
                    for filename in os.listdir(os.path.join(item_path, 'Model')):
                        if filename.endswith('_config.json'):
                            path_config_ledet = os.path.join(item_path, 'Model', filename)
                            with open(path_config_ledet, 'r') as file:
                                dict_config_ledet = json.load(file)
                            if verbose:
                                print(f"Found LEDET configuration file: {path_config_ledet}")

                    # Read LEDET file from the COSIM output folder
                    path_ledet_folder = os.path.join(item_path, 'Model', 'LEDET')
                    path_ledet_input_file = os.path.join(path_ledet_folder, dict_config_ledet['modelName'], 'Input', f"{dict_config_ledet['modelName']}_{dict_config_ledet['simulationNumber']}.xlsx")
                    path_ledet_output_pdf_report = os.path.join(path_ledet_folder, dict_config_ledet['modelName'], 'Output', 'Reports', f"reportLEDET_{dict_config_ledet['modelName']}_{dict_config_ledet['simulationNumber']}.pdf")
                    bLEDET = BuilderLEDET(flag_build=False)
                    pLEDET = ParserLEDET(bLEDET)
                    pLEDET.readFromExcel(path_ledet_input_file, verbose=verbose)
                    # Enable flags to generate .pdf report and .mat file, and disable flags to show/save figures
                    setattr(pLEDET.builder_ledet.Options, 'flag_generateReport', 1)
                    # setattr(pLEDET.builder_ledet.Options, 'flag_saveMatFile', 1)
                    setattr(pLEDET.builder_ledet.Options, 'flag_showFigures', 0)
                    setattr(pLEDET.builder_ledet.Options, 'flag_saveFigures', 0)
                    # Re-save the LEDET file
                    pLEDET.writeLedet2Excel(path_ledet_input_file, verbose=False)
                    # Run LEDET model
                    if verbose:
                        print(f'LEDET input file {path_ledet_input_file} was edited. Simulation will be re-run from the updated file.')
                    dLEDET = DriverLEDET(path_exe=dict_config_ledet['solverPath'], path_folder_LEDET=path_ledet_folder, verbose=verbose)
                    dLEDET.run_LEDET(dict_config_ledet['modelName'], str(dict_config_ledet['simulationNumber']), simFileType='.xlsx')
                    if verbose:
                        print(f'LEDET pdf report expected to be generated at {path_ledet_output_pdf_report}')
                        print(f'DriverCOSIM - LEDET post-processing finished.')


    def _make_callString(self, model_name: str, sim_number: Union[str, int], ):
        '''
        Write the sring that will be used to call COSIM
        :param model_name: Name of the co-simulation model to run
        :param sim_number: String or number identifying the simulation to run
        :return: null
        '''
        config_file_name = Path(os.path.join(self.path_folder_COSIM, model_name, str(sim_number), 'Input', 'COSIMConfig.json')).resolve()
        callString = (f'java -jar {self.COSIM_path} {config_file_name}')
        return callString
