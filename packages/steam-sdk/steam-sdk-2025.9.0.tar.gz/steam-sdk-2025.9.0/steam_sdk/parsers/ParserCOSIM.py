import json
import os
from typing import Union

from steam_sdk.data.DataCoSim import NSTI
from steam_sdk.data.DataModelCosim import DataModelCosim, sim_PSPICE
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.utils_ParserCosims import write_model_input_files
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class ParserCOSIM:
    """
        Class with methods to read/write COSIM information from/to other programs
    """

    def __init__(self, cosim_data: DataModelCosim, data_settings: DataSettings = None):
        '''
        :param cosim_data: DataModelCosim object containing co-simulation parameter structure
        :param data_settings: DataSettings object containing all settings, previously read from user specific settings.SYSTEM.yaml file or from a STEAM analysis permanent settings
        '''

        # Load co-simulation data from the BuilderModel object
        self.cosim_data = cosim_data
        self.data_settings = data_settings

    def write_cosim_model(self, sim_name: str, sim_number: int, output_path_COSIM_folder: str, verbose: bool = None):
        '''
        :param sim_name: Simulation name that will be used to write the output file
        :param sim_number: Simulation number that will be used to write the output file
        :param output_path_COSIM_folder: Output folder
        :param verbose: If True, display logging information
        :return:
        '''
        # Assign variable to self to guarantee consistency between the methods
        self.local_COSIM_folder = output_path_COSIM_folder
        self.cosim_name = sim_name
        self.sim_number = sim_number
        # self.sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number
        make_folder_if_not_existing(output_path_COSIM_folder, verbose=verbose)

        # Write COSIM configuration file
        self.write_config_file(verbose=verbose)

        # Write COSIM submodels
        for model_name, model in self.cosim_data.Simulations.items():
            if verbose: (f'{model_name}, {model}')
            if model.type == 'FiQuS':
                self.write_model_FiQuS()
            elif model.type == 'LEDET':
                self.write_model_LEDET(model=model, verbose=verbose)
            elif model.type == 'PSPICE':
                self.write_model_PSPICE(model=model, verbose=verbose)
            elif model.type == 'XYCE':
                self.write_model_XYCE()

    def write_config_file(self, output_file_name: str = 'COSIMConfig.json', verbose: bool = False):
        '''
        ** Write COSIM configuration file **
        '''
        # Calculate variables
        coSimulationDir = self.reformat_path(os.path.join(self.local_COSIM_folder, self.cosim_name, str(self.sim_number), 'Output')) + '\\'
        t_0 = self.cosim_data.Options_COSIM.Settings.Time_Windows.t_0
        t_end = self.cosim_data.Options_COSIM.Settings.Time_Windows.t_end
        executionOrder = self.cosim_data.Options_COSIM.Settings.Options_run.executionOrder
        executeCleanRun = self.cosim_data.Options_COSIM.Settings.Options_run.executeCleanRun
        coSimulationModelSolvers, coSimulationModelDirs, coSimulationModelConfigs, coSimulationPortDefinitions = [], [], [], []
        convergenceVariables, relTolerance, absTolerance, t_step_max = [], [], [], []
        for model_name, model in self.cosim_data.Simulations.items():
            coSimulationModelSolvers.append(model.type)
            coSimulationModelDirs.append(self.reformat_path(os.path.join(self.local_COSIM_folder, self.cosim_name, str(self.sim_number), 'Input', model_name)) + '\\')
            coSimulationModelConfigs.append(f'{model_name}_config.json')
            coSimulationPortDefinitions.append(f'{model_name}_InputOutputPortDefinition.json')
            convergenceVariables.append(self.cosim_data.Options_COSIM.Settings.Convergence.convergenceVariables[model_name])
            relTolerance.append(self.cosim_data.Options_COSIM.Settings.Convergence.relTolerance[model_name])
            absTolerance.append(self.cosim_data.Options_COSIM.Settings.Convergence.absTolerance[model_name])
            t_step_max.append(self.cosim_data.Options_COSIM.Settings.Time_Windows.t_step_max[model_name])

        # Dictionary to write
        dict_cosim_config = {
                "coSimulationDir": coSimulationDir,
                "coSimulationModelSolvers": coSimulationModelSolvers,
                "coSimulationModelDirs": coSimulationModelDirs,
                "coSimulationModelConfigs": coSimulationModelConfigs,
                "coSimulationPortDefinitions": coSimulationPortDefinitions,
                "convergenceVariables": convergenceVariables,
                "t_0": t_0,
                "t_end": t_end,
                "t_step_max": t_step_max,
                "relTolerance": relTolerance,
                "absTolerance": absTolerance,
                "executionOrder": executionOrder,
                "executeCleanRun": executeCleanRun
        }

        # Serializing json
        json_cosim_config = json.dumps(dict_cosim_config, indent=4)

        # Writing to .json file
        path_output_file = os.path.join(self.local_COSIM_folder, self.cosim_name, str(self.sim_number), 'Input', output_file_name)
        make_folder_if_not_existing(os.path.dirname(path_output_file), verbose=verbose)
        with open(path_output_file, "w") as outfile:
            outfile.write(json_cosim_config)
        if verbose:
            print(f'File {path_output_file} written.')

    def write_model_FiQuS(self):
        '''
        ** COSIM does not support FiQuS at the moment **
        '''
        raise Exception('ParserCOSIM does not support FiQuS model generation.')

    def write_model_LEDET(self, model, verbose: bool = False):
        '''
        ** Write selected LEDET model **
        '''
        # Unpack input
        magnet_name = model.modelName

        # Make subfolders
        path_submodel_folder = os.path.join(self.local_COSIM_folder, self.cosim_name, str(self.sim_number), 'Input', model.name)
        make_folder_if_not_existing(path_submodel_folder, verbose=verbose)
        make_folder_if_not_existing(os.path.join(path_submodel_folder, 'LEDET', magnet_name, 'Input'), verbose=verbose)
        make_folder_if_not_existing(os.path.join(path_submodel_folder, 'LEDET', magnet_name, 'Input', 'Control current input'), verbose=verbose)
        make_folder_if_not_existing(os.path.join(path_submodel_folder, 'LEDET', magnet_name, 'Input', 'Initialize variables'), verbose=verbose)
        make_folder_if_not_existing(os.path.join(path_submodel_folder, 'LEDET', magnet_name, 'Input', 'InitializationFiles'), verbose=verbose)
        make_folder_if_not_existing(os.path.join(path_submodel_folder, 'Field maps', magnet_name), verbose=verbose)
        # Make configuration file
        path_config_file = os.path.join(path_submodel_folder, f'{model.name}_config.json')
        self.write_config_file_ledet(output_file=path_config_file,
                                     LEDET_path=self.reformat_path(self.cosim_data.Options_COSIM.solverPaths[model.name]),
                                     magnet_name=magnet_name, sim_set_number=str(self.sim_number))
        # Make input/output port definition file
        path_ports_file = os.path.join(path_submodel_folder, f'{model.name}_InputOutputPortDefinition.json')
        self.write_ports_file(output_file=path_ports_file, model_name=model.name)
        # Make input files, self-mutual inductance files, magnetic field map files. Save them to the COSIM subfolder
        write_model_input_files(cosim_data=self.cosim_data, model=model, cosim_software='COSIM',
                                data_settings=self.data_settings, nsti=NSTI(self.sim_number, None, 0, None),
                                verbose=verbose)

    def write_model_PSPICE(self, model, verbose: bool = False):
        '''
        ** Write selected PSPICE model **
        '''
        # Make subfolders
        path_submodel_folder = os.path.join(self.local_COSIM_folder, self.cosim_name, str(self.sim_number), 'Input', model.name)
        make_folder_if_not_existing(path_submodel_folder, verbose=verbose)
        # Make configuration file
        path_config_file = os.path.join(path_submodel_folder, f'{model.name}_config.json')
        self.write_config_file_pspice(output_file=path_config_file, model=model, solver_path=
        self.cosim_data.Options_COSIM.solverPaths[model.name])
        # Make input/output port definition file
        path_ports_file = os.path.join(path_submodel_folder, f'{model.name}_InputOutputPortDefinition.json')
        self.write_ports_file(output_file=path_ports_file, model_name=model.name)
        # Make input netlist files, auxiliary files. Save them to the COSIM subfolder. Delete temporary files.
        write_model_input_files(cosim_data=self.cosim_data, model=model, cosim_software='COSIM',
                                data_settings=self.data_settings, nsti=NSTI(self.sim_number, None, 0, None),
                                verbose=verbose)

    def write_model_XYCE(self):
        '''
        ** COSIM does not support XYCE at the moment **
        '''
        raise Exception('ParserCOSIM does not support XYCE model generation.')


    @staticmethod
    def reformat_path(path: str):
        '''
        Reformat a string defining a path so that all delimiters are double slashes
        :param path: string defining the original path
        :return: str
        '''

        return os.path.normpath(path).replace(os.sep, '\\')

    @staticmethod
    def write_config_file_ledet(output_file: str, LEDET_path: str, magnet_name: str, sim_set_number: int):
        '''
        Write the LEDET configuration .json file
        :param output_file: Target file
        :param LEDET_path: Path to PSPICE executable
        :param sim_set_number: Number of the simulation set, i.e. number of the LEDET simulation used in the COSIM model
        :return: None
        '''

        # Dictionary to write
        dict_ledet_config = {
            "solverPath": f"{LEDET_path}",
            "modelFolder": "LEDET",
            "modelName": f"{magnet_name}",
            "simulationNumber": f"{sim_set_number}"
        }

        # Serializing json
        json_ledet_config = json.dumps(dict_ledet_config, indent=4)

        # Writing to .json file
        with open(output_file, "w") as outfile:
            outfile.write(json_ledet_config)

    @staticmethod
    def write_config_file_pspice(output_file: str, model: sim_PSPICE, solver_path: str):
        '''
        Write the PSPICE configuration .json file
        :param output_file: Target file
        :param model: sim_PSPICE object containing the information about this model
        :param solver_path: path to the solver to be used in the simulation
        :return: None
        '''
        # Unpack inputs
        solver_path = ParserCOSIM.reformat_path(solver_path)
        modelName = model.modelName
        configurationFileName = model.configurationFileName
        externalStimulusFileName = model.externalStimulusFileName
        initial_conditions = model.initialConditions
        skipBiasPointCalculation = model.skipBiasPointCalculation

        # Write a list of initial conditions
        string_initial_conditions = [f'{ic_name}={ic}' for ic_name, ic in initial_conditions.items()]

        # Dictionary to write
        dict_pspice_config = {
            "solverPath": solver_path,
            "modelName": f'{modelName}.cir',
            "configurationFileName": configurationFileName,
            "externalStimulusFileName": externalStimulusFileName,
            "initialConditions": string_initial_conditions,
            "skipBiasPointCalculation": skipBiasPointCalculation,
        }

        # Serializing json
        json_pspice_config = json.dumps(dict_pspice_config, indent=4)

        # Writing to .json file
        with open(output_file, "w") as outfile:
            outfile.write(json_pspice_config)

    def write_ports_file(self, output_file: str, model_name: str):
        '''
            Write the input/output port configuration .json file
            This method does not depend on the software tool
            :param output_file: Target file
            :return: None
        '''

        list_of_dict_ports = []
        for port_name, port in self.cosim_data.Options_COSIM.PortDefinition.items():
            if model_name in port.Models:
                port_info = port.Models[model_name]

                # Dictionary to write
                dict_ports = {
                    "name": port_name,
                    "components": port_info.components,
                    "inputs": [],
                    "outputs": [],
                }
                for input_name, input in port_info.inputs.items():
                    dict_ports["inputs"].append({
                        "couplingParameter": input.variable_coupling_parameter,
                        "labels": input.variable_names,
                        "types": input.variable_types})
                for output_name, output in port_info.outputs.items():
                    dict_ports["outputs"].append({
                        "couplingParameter": output.variable_coupling_parameter,
                        "labels": output.variable_names,
                        "types": output.variable_types})
                list_of_dict_ports.append(dict_ports)

        # Writing to .json file
        with open(output_file, "w") as outfile:
            # Serializing json
            for dict_ports in list_of_dict_ports:
                json_ports = json.dumps(dict_ports, indent=4)
                outfile.write(json_ports)
                outfile.write('\n')
