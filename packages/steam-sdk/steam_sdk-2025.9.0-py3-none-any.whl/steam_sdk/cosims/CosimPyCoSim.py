import os
import glob
import shutil
from pathlib import Path
from typing import Union, List

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.configs.StylesPlots import styles_plots
from steam_sdk.data.DataCoSim import NSTI
from steam_sdk.data.DataFiQuS import DataFiQuS
from steam_sdk.data.DataModelCircuit import DataModelCircuit
from steam_sdk.data.DataModelConductor import DataModelConductor
from steam_sdk.data.DataModelCosim import sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE, sim_Generic, FileToCopy, VariableToCopy
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataModelCosim import DataModelCosim
from steam_sdk.data.DataPyCoSim import DataPyCoSim
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.drivers.DriverFiQuS import DriverFiQuS
from steam_sdk.drivers.DriverLEDET import DriverLEDET
from steam_sdk.drivers.DriverPSPICE import DriverPSPICE
from steam_sdk.drivers.DriverXYCE import DriverXYCE
from steam_sdk.parsers.ParserCsv import write_signals_to_csv
from steam_sdk.parsers.ParserFile import get_signals_from_file
from steam_sdk.parsers.ParserPSPICE import write_time_stimulus_file
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.parsers.utils_ParserCosims import write_model_input_files
from steam_sdk.parsers.utils_ParserCosims import template_replace
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.rgetattr import rgetattr


class CosimPyCoSim:
    """
        Class to run a co-operative simulation
    """

    def __init__(self,
                 file_model_data: str,
                 sim_number: int,
                 data_settings: DataSettings = None,
                 verbose: bool = False
                 ):
        """
            Builder object to generate models from STEAM simulation tools specified by user

            file_model_data: path to folder with input data (DataModelCosim yaml input file)
            sim_number: number of the simulation
            :param data_settings: DataSettings object containing all settings, previously read from user specific settings.SYSTEM.yaml file or from a STEAM analysis permanent settings
            verbose: to display internal processes (output of status & error messages) for troubleshooting

            Notes:
            The PyCoSim folder structure will be as follows:
            - local_PyCoSim is the main folder
              - COSIM_NAME
                - SOFTWARE_FOLDER
                  - SIMULATION_NAME
                    - {COSIM_NUMBER}_{SIMULATION_NUMBER}_{TIME_WINDOW_NUMBER}_{ITERATION_NUMBER}

            Example 1:
            - C:\local_PyCoSim
              - RQX
                - LEDET
                  - MQXA
                    - Field Maps
                    - 55_1_1_1\LEDET\Input
                  - MQXA
                    - 55_2_1_1
                  - MQXB
                    - 55_1_1_1
                  - MQXB
                    - 55_2_1_1

            Example 1:
            - C:\local_PyCoSim
              - RQX
                - FiQuS
                  - MQXA
                    - G1
                      - M1
                        - 55_1_1_1
                - LEDET
                  - MQXB
                    - Field Maps
                    - 55
                     - 1_1_1\LEDET\Input
                - PSPICE
                  - RQX_cosim
                    - 55_1_1_1

            D:\library_mesh

        """
        # Load data from input file
        self.verbose = verbose
        if self.verbose:
            print(f'PyCoSim initialized with input file {file_model_data}.')

        self.cosim_data: DataModelCosim = yaml_to_data(file_model_data, DataPyCoSim)
        self.local_PyCoSim_folder = Path(data_settings.local_PyCoSim_folder).resolve()
        if self.verbose:
            print(f'Local PyCoSim folder is {self.local_PyCoSim_folder}')
        self.sim_number = sim_number
        if self.verbose:
            print(f'PyCoSimulation number {self.sim_number}')
        self.data_settings = data_settings

        self.diary = {}  # This will be populated with small information about the simulation runs
        self.summary = {}  # This will be populated with a summary of simulation results (mainly used for DAKOTA)

        # Initialize the dictionary that will be used to pass variable values from an output file to a model data object
        self._reset_variables_to_pass()

        # Initialize the dictionary that will be used to check convergence at each time window
        self.dict_convergence_variables = {key: {} for key in self.cosim_data.Simulations}  # Assign empty list to all models

        # Check that the variables variables_to_modify.cosim_for_each_time_window have all the same length, if their run.cosim is True

        self._get_n_time_windows()

        if self.verbose:
            print(f'Number of windows: {self.n_time_windows}')

    def run(self):
        """
        This runs PyCoSimulation with all the PreCoSim, CoSim and PostCoSim stages
        """

        if self.verbose: print(f'Co-simulation {self.cosim_data.GeneralParameters.cosim_name} {self.sim_number} started.')
        self.nsti = NSTI(self.sim_number, 0, 0, 0)

        # PreCoSim
        if self.cosim_data.Start_from_s_t_i:    # skip PreCoSim as Start_from_s_t_i is set
            print(f'PreCoSim skipped as Options_PyCoSim.Start_from_s_t_i is set to {self.cosim_data.Start_from_s_t_i}')
        else:
            for model_set, model in enumerate(self.cosim_data.Simulations.values()):
                self.nsti.update(self.sim_number, model_set, 0, 0)  # Initial time window and iteration  # cosim_nsti --> N=Simulation number. S=Simulation set. T=Time window. I=Iteration.
                print(f'-------------- {model.name} PreCoSim -----{self.nsti.n_s_t_i}-----------------------------------------------------------')
                if model.PreCoSim.flag_run:
                    if self.verbose: print(f'Model {model.name}. Simulation set {self.nsti.s}. Pre-cosim simulation.')

                    BM: BuilderModel = write_model_input_files(cosim_data=self.cosim_data, model=model,
                                                               cosim_software='PyCoSim', data_settings=self.data_settings,
                                                               extra_dicts_with_change=self.dict_to_pass[model.name]['variables_to_modify']['pre_cosim'],
                                                               nsti=self.nsti, verbose=self.verbose)
                    self._run_sim(model=model)
                    # TODO add some basic check that the simulation run without errors
                    self._copy_variables(model=model, mode='time_window')
                    self._copy_files(model=model, BM=BM, mode='time_window')

        # CoSim
        # Loop through time windows
        Start_from_s_t_i_injected = False
        for tw in range(self.n_time_windows):
            if self.cosim_data.Start_from_s_t_i:  # skip PreCoSim as Start_from_s_t_i is set
                print(f'CoSim starts form Options_PyCoSim.Start_from_s_t_i set to {self.cosim_data.Start_from_s_t_i}')
                parsed_values = self.cosim_data.Start_from_s_t_i.split('_')
                if len(parsed_values) ==3:
                    start_from_s, start_from_tw, start_from_i = parsed_values      # note this overwrites teh tw of the top loop
                else:
                    raise Exception(f'Options_PyCoSim.Start_from_s_t_i is not valid. It needs to be a string with three integers separated by underscore.'
                                    f'For example: 1_2_3, but {self.cosim_data.Start_from_s_t_i} was given!')
            # Reset convergence variables
            flag_converge, current_iteration = False, 0
            # Reset the dictionary that is used to pass variable values from an output file to a model data object
            self._reset_variables_to_pass()
            # Loop until convergence is found
            while flag_converge == False:
                list_flag_converge, list_files_copied_at_this_iteration = [], []  # Re-initialize with each new iteration
                skip_converge_check_due_to_injection = False
                for model_set, model in enumerate(self.cosim_data.Simulations.values()):
                    if self.cosim_data.Start_from_s_t_i and not Start_from_s_t_i_injected:
                        model_set = int(start_from_s)
                        current_iteration = int(start_from_i)
                        for _ in range(current_iteration):
                            list_flag_converge.append(False)
                        tw = int(start_from_tw)-1
                        Start_from_s_t_i_injected = True
                        skip_converge_check_due_to_injection = True
                    self.nsti.update(self.sim_number, model_set, tw + 1, current_iteration)
                    print(f'-------------- {model.name} CoSim -----{self.nsti.n_s_t_i}-----------------------------------------------------------')
                    # Make model
                    if model.CoSim.flag_run:
                        if self.verbose: print(f'Model {model.name}. Simulation number {self.nsti.n}. Simulation set {self.nsti.s}. Time window {self.nsti.t}. Iteration {self.nsti.i}.')
                        # Add to the list of variables to change also the variables defined with the key "variables_to_modify.cosim_for_each_time_window"
                        for new_var_name, new_var_value in model.CoSim.variables_to_modify_for_each_time_window[tw].items():
                            self.dict_to_pass[model.name]['variables_to_modify']['cosim'][new_var_name] = new_var_value
                        BM: BuilderModel = write_model_input_files(cosim_data=self.cosim_data, model=model,
                                                                   cosim_software='PyCoSim', data_settings=self.data_settings,
                                                                   extra_dicts_with_change=self.dict_to_pass[model.name]['variables_to_modify']['cosim'],
                                                                   nsti=self.nsti, verbose=self.verbose)
                        self._run_sim(model=model)
                        list_newly_copied_files = self._copy_files(model=model, BM=BM, mode='iteration')
                        list_files_copied_at_this_iteration = list_files_copied_at_this_iteration + list_newly_copied_files
                        self._copy_variables(model=model, mode='iteration')

                        self._copy_variables(model=model, mode='time_window') #TODO this is ugly here, of course, but it's wrong to only call the method for the last model (if called only after convergence is reached)
                        self._copy_files(model=model, BM=BM, mode='time_window') #TODO this is ugly here, of course, but it's wrong to only call the method for the last model (if called only after convergence is reached)

                        # Copy the "time_window" files and variables from the previous time window to the next iteration of the current time window. Note that for the first time window the files will be taken from the PreCoSim "time_window" files
                        self._copy_files(model=model, BM=BM, mode='next_iteration')
                        #TODO do the same for variables
                        # TODO add some basic check that the simulation run without errors
                        list_flag_converge.append(self._check_convergence(model=model, skip_converge_check_due_to_injection=skip_converge_check_due_to_injection))
                flag_converge = all(list_flag_converge)
                print(f'NSTI: {self.nsti.n_s_t_i} list_flag_converge = {list_flag_converge}')
                if not flag_converge:
                    current_iteration = current_iteration + 1
            print(f'-------------- Cosimulation converged! -----{self.nsti.n_s_t_i}-----------------------------------------------------------')
            # Copy files and variables to the first iteration of the next time window
            self._copy_variables(model=model, mode='time_window')
            self._copy_files(model=model, BM=BM, mode='time_window')

            # Delete the folders of the latest iteration of the current time window
            for model_set, model in enumerate(self.cosim_data.Simulations.values()):
                if model.CoSim.flag_run:
                    for file in list_files_copied_at_this_iteration:
                        if os.path.isfile(file):
                            print(f'NSTI: {self.nsti.n_s_t_i} Delete folder {os.path.dirname(file)}')
                            # delete_if_existing(os.path.dirname(file))  #TODO problem: list_files_copied_at_this_iteration is not correct

        # PostCoSim
        for model_set, model in enumerate(self.cosim_data.Simulations.values()):
            self.nsti.update(self.sim_number, model_set, self.n_time_windows + 1, 0)
            print(f'-------------- {model.name} PostCoSim -----{self.nsti.n_s_t_i}-----------------------------------------------------------')
            if model.PostCoSim.flag_run:
                if self.verbose: print(f'Model {model.name}. Simulation set {self.nsti.s}. Post-cosim simulation.')
                # Make model
                BM: BuilderModel = write_model_input_files(cosim_data=self.cosim_data, model=model,
                                                           cosim_software='PyCoSim', data_settings=self.data_settings,
                                                           extra_dicts_with_change=self.dict_to_pass[model.name]['variables_to_modify']['post_cosim'],
                                                           nsti=self.nsti, verbose=self.verbose)
                # Run model
                self._run_sim(model=model)
                # TODO add some basic check that the simulation run without errors
                self._copy_variables(model=model, mode='time_window')
                self._copy_files(model=model, BM=BM, mode='time_window')

        if self.verbose: print(f'Co-simulation {self.cosim_data.GeneralParameters.cosim_name} {self.sim_number} finished.')

    def plot(self):

        plot_style = styles_plots[self.cosim_data.PostProcess.Plots.Style]  # chosen style

        for model_set, model in enumerate(self.cosim_data.Simulations.values()):
            out_dir = os.path.join(self.data_settings.local_PyCoSim_folder, model.modelName, 'Plots')
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            if model.CoSim.flag_run and len(model.CoSim.convergence) > 0:

                self.nsti = NSTI(self.sim_number, 0, 0, 0)
                for convergence_dict in model.CoSim.convergence:
                    fig_all_time_windows, (ax_all_time_windows) = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(plot_style['plot_width'], plot_style['plot_height']))
                    fig_each_time_window, (ax_each_time_window) = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(plot_style['plot_width'], plot_style['plot_height']))

                    for tw in range(self.n_time_windows):

                        print(f'NSTI: {self.nsti.n_s_t_i} Making convergence plot for: {model.name} for time window {tw}')

                        self.nsti.update(self.sim_number, model_set, tw + 1, 0)
                        local_folder = self.__find_local_source_folder(model=model)
                        replacements = {
                            'modelName': model.modelName,
                            'n_s_t_i': f'{self.nsti.n}_{self.nsti.s}_{self.nsti.t}_*',
                            'n': self.nsti.n,
                            's': self.nsti.s,
                            't': self.nsti.t,
                            'i': '*',
                        }
                        convergence_file_rel_path = template_replace(convergence_dict.file_name_relative_path, replacements=replacements)
                        convergence_file_path = Path(os.path.join(local_folder, convergence_file_rel_path)).resolve()
                        conv_files_folder = str(convergence_file_path.parent)
                        conv_file_pattern = str(convergence_file_path.name)
                        search_pattern = os.path.join(conv_files_folder, conv_file_pattern)
                        matching_files = glob.glob(search_pattern)

                        for i, conv_file in enumerate(matching_files):

                            conv_file = template_replace(conv_file, replacements={'*': i})
                            if self.verbose:
                                print(f'Adding to the convergence plot: {conv_file}')
                            var_value = get_signals_from_file(full_name_file=conv_file, list_signals=convergence_dict.var_name, dict_variable_types={})[convergence_dict.var_name.strip()]
                            time_var_value = get_signals_from_file(full_name_file=conv_file, list_signals=convergence_dict.time_var_name, dict_variable_types={})[convergence_dict.time_var_name.strip()]

                            ax_each_time_window.plot(time_var_value, var_value, label=f'i={i}')
                            ax_all_time_windows.plot(time_var_value, var_value, label=f't={self.nsti.t}, i={i}')

                        ax_each_time_window.tick_params(labelsize=plot_style['font_size'])
                        ax_each_time_window.set_xlabel(convergence_dict.var_name)
                        ax_each_time_window.set_ylabel(convergence_dict.time_var_name)
                        ax_each_time_window.set_title(f'n={self.nsti.n}, s={self.nsti.s}, t={self.nsti.t}')

                        legend = ax_each_time_window.legend(loc="best", prop={'size': plot_style['font_size']})
                        frame = legend.get_frame()  # sets up for color, edge, and transparency
                        frame.set_edgecolor('black')  # edge color of legend
                        frame.set_alpha(0)  # deals with transparency

                        fig_each_time_window.tight_layout()
                        file_name_each_time_window = f"Convergence {convergence_dict.var_name.strip()} vs {convergence_dict.time_var_name} {self.nsti.n}_{self.nsti.s}_{self.nsti.t}.{plot_style['file_ext']}"
                        full_path_each_time_window = os.path.join(out_dir, file_name_each_time_window)
                        fig_each_time_window.savefig(full_path_each_time_window, dpi=300)
                        if self.verbose:
                            print(f'Saved : {full_path_each_time_window}')
                        fig_each_time_window.clear()

                    ax_all_time_windows.tick_params(labelsize=plot_style['font_size'])
                    ax_all_time_windows.set_xlabel(convergence_dict.var_name)
                    ax_all_time_windows.set_ylabel(convergence_dict.time_var_name)
                    ax_each_time_window.set_title(f'n={self.nsti.n}, s={self.nsti.s}')

                    legend = ax_all_time_windows.legend(loc="best", prop={'size': plot_style['font_size']})
                    frame = legend.get_frame()  # sets up for color, edge, and transparency
                    frame.set_edgecolor('black')  # edge color of legend
                    frame.set_alpha(0)  # deals with transparency
                    fig_all_time_windows.tight_layout()
                    file_all_time_windows = f"Convergence {convergence_dict.var_name.strip()} vs {convergence_dict.time_var_name} {self.nsti.n}_{self.nsti.s}.{plot_style['file_ext']}"
                    full_path_each_time_window = os.path.join(out_dir, file_all_time_windows)
                    fig_all_time_windows.savefig(full_path_each_time_window, dpi=300)
                    if self.verbose:
                        print(f'Saved : {full_path_each_time_window}')
                    fig_all_time_windows.clear()

        plt.close(fig_each_time_window)
        plt.close(fig_all_time_windows)

    def _run_sim(self, model: Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE]):
        """
        Run selected simulation.
        The function applies a different logic for each simulation software.
        """

        # Define local folder
        local_folder = self.__find_local_target_folder(model=model, nsti=self.nsti)

        # Run simulation
        if model.type == 'FiQuS':
            dFiQuS = DriverFiQuS(path_folder_FiQuS_input=local_folder, path_folder_FiQuS_output=local_folder,
                                 FiQuS_path=self.data_settings.FiQuS_path, GetDP_path=self.data_settings.GetDP_path, verbose=self.verbose)
            self.summary[model.name] = dFiQuS.run_FiQuS(sim_file_name=f'{model.modelName}_{self.nsti.n_s_t_i}_FiQuS')
        elif model.type == 'LEDET':
            dLEDET = DriverLEDET(path_exe=self.data_settings.LEDET_path, path_folder_LEDET=os.path.dirname(local_folder), verbose=self.verbose)  # Note: os.path.dirname() needed because DriverLEDET will add nameMagnet to the simulation path already
            sim_result = dLEDET.run_LEDET(nameMagnet=model.modelName, simsToRun=self.nsti.n_s_t_i, simFileType='.xlsx')  # simFileType is hard-coded .yaml
            # if sim_result == 0:
            #     raise Exception(f'Error when running LEDET! Executable: {self.data_settings.LEDET_path}. LEDET local folder {local_folder}. ')
        elif model.type == 'PSPICE':
            dPSPICE = DriverPSPICE(path_exe=self.data_settings.PSPICE_path, path_folder_PSPICE=local_folder, verbose=self.verbose)
            dPSPICE.run_PSPICE(nameCircuit=model.modelName, suffix='')
        elif model.type == 'XYCE':
            dXYCE = DriverXYCE(path_exe=self.data_settings.XYCE_path, path_folder_XYCE=local_folder, verbose=self.verbose)
            dXYCE.run_XYCE(nameCircuit=model.modelName, suffix='')
        else:
            raise Exception(f'Software {model.type} not supported for automated running.')

    def _copy_files(self, model: Union[sim_Generic, sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE], BM: BuilderModel = None, mode='iteration'):
        '''
        This function copies files across from the output of one model to another.
        :param model: Current simulation model
        :param BM: BuilderModel object used to access some model parameters
        :param mode: this is mode of operation, only three options are allowed: 'iteration' to copy files to the next iteration, 'time_window' to copy files to the next time window, 'next_iteration' to copy the file from the same time window but next iteration
        :return: list of written files
        '''
        supported_modes = ['iteration', 'time_window', 'next_iteration']
        if mode not in supported_modes:
            raise Exception(f'This method does not support mode: {mode}. Supported modes: {supported_modes}')

        # Get list of files to copy, which depends on the current co-simulation state
        if mode == 'iteration':
            files_to_copy: List[FileToCopy] = model.CoSim.files_to_copy_after_iteration
        elif mode == 'time_window':
            if self.nsti.t == 0:
                files_to_copy: List[FileToCopy] = model.PreCoSim.files_to_copy_after_time_window
            elif self.nsti.t > self.n_time_windows:
                files_to_copy: List[FileToCopy] = model.PostCoSim.files_to_copy_after_time_window
            else:
                files_to_copy: List[FileToCopy] = model.CoSim.files_to_copy_after_time_window
        elif mode == 'next_iteration':
            if self.nsti.t == 1:  # For the first time window the files will be taken from the PreCoSim "time_window" files
                files_to_copy: List[FileToCopy] = model.PreCoSim.files_to_copy_after_time_window
            elif self.nsti.t > self.n_time_windows:
                raise Exception(f'NSTI: {self.nsti.n_s_t_i}. Mode {mode} cannot be used during PostCoSimulation. This case is never supposed to happen.')
            else:
                files_to_copy: List[FileToCopy] = model.CoSim.files_to_copy_after_time_window

        # Initialize output list of written files
        list_copied_files = []

        if len(files_to_copy) > 0:
            # Define local folder
            local_folder = self.__find_local_source_folder(model=model)

            # Copy files
            for file_to_copy in files_to_copy:
                # Check whether to add an NSTI suffix between the base name and the extension of the old file name. NSTI: N=simulation number. S=simulation set. T=time window. I=Iteration number
                # source_file_name_relative_path = self._add_nsti_to_file_name(file_to_copy.source_file_name_relative_path, nsti=self.nsti) if file_to_copy.flag_add_nsti_to_source_file_name else file_to_copy.source_file_name_relative_path
                target_set = list(self.cosim_data.Simulations.keys()).index(file_to_copy.target_model)
                if mode == 'iteration':
                    target_time_window = self.nsti.t        # same time window
                    if target_set > self.nsti.s:            # the set is the subsequent one so stay with the same iteration number
                        target_iteration = self.nsti.i      # current iteration
                    else:                                   # the set is the previous one, so this is meant for the next iteration
                        target_iteration = self.nsti.i + 1  # next iteration
                elif mode == 'time_window':
                    if self.nsti.t == 0:
                        target_time_window = self.nsti.t + 1    # PreCoSim - pass the file to the first time window of the CoSim
                    elif self.nsti.t > self.n_time_windows:  #TODO check whether this should be replaced by self.nsti.t >= self.n_time_windows
                        target_time_window = self.nsti.t        # PostCoSim - do not increase as this was done to flag that it is now PostCoSim
                    else:
                        target_time_window = self.nsti.t + 1    # CoSim    - this means that copy files was called at after convergence, next time window is + 1
                    target_iteration = 0                        # always the zeroth iteration in the time window
                elif mode == 'next_iteration':
                    # This mode is only used in CoSim. It will copy the file from the same time window but to the next iteration
                    target_time_window = self.nsti.t
                    target_iteration = self.nsti.i + 1
                target_nsti = NSTI(self.sim_number, target_set, target_time_window, target_iteration)

                # If not defined, don't change the file name
                if not file_to_copy.target_file_name_relative_path:
                    file_to_copy.target_file_name_relative_path = file_to_copy.source_file_name_relative_path

                # Source files
                source_replacements = {
                    'modelName': model.modelName,
                    'n_s_t_i': self.nsti.n_s_t_i,
                    'n': self.nsti.n,
                    's': self.nsti.s,
                    't': self.nsti.t,
                    'i': self.nsti.i,
                }

                # Target files
                target_replacements = {
                    'modelName': self.cosim_data.Simulations[file_to_copy.target_model].modelName,
                    'n_s_t_i': target_nsti.n_s_t_i,
                    'n': target_nsti.n,
                    's': target_nsti.s,
                    't': target_nsti.t,
                    'i': target_nsti.i,
                }

                source_file_name_relative_path = template_replace(file_to_copy.source_file_name_relative_path, source_replacements)
                target_file_name_relative_path = template_replace(file_to_copy.target_file_name_relative_path, target_replacements)

                # TODO make it better (move code around, fix the placeholder, add logic to get last_iteration_from_previous_time_window)
                if mode == 'next_iteration' and model.type in ['PSPICE', 'XYCE']:    # TODO: This swap of target to source does not work for FiQuS or LEDET. This is temporary fix until better ideas are in place
                    last_iteration_from_previous_time_window = 1  #TODO THIS IS AN HARD-CODED PLACE HOLDER. FIX THIS
                    source_replacements = {
                        'modelName': model.modelName,
                        'n_s_t_i': self.nsti.n_s_t_i,
                        'n': self.nsti.n,
                        's': self.nsti.s,
                        't': self.nsti.t - 1,
                        'i': last_iteration_from_previous_time_window,
                    }
                    source_file_name_relative_path = template_replace(file_to_copy.target_file_name_relative_path, source_replacements)

                # Figure out paths
                source_file = Path(Path(local_folder), source_file_name_relative_path).resolve()
                target_local_folder = self.__find_local_target_folder(model=self.cosim_data.Simulations[file_to_copy.target_model], nsti=target_nsti)
                target_file = Path(Path(target_local_folder), target_file_name_relative_path).resolve()
                list_copied_files.append(target_file)

                # Make sure the target folder exists, if not make it
                make_folder_if_not_existing(os.path.dirname(target_file), verbose=self.verbose)

                # Read a subset of signals, if the dictionary file_to_copy.dict_translate_variables is defined
                if len(file_to_copy.dict_translate_variables) > 0:
                    # Read source file
                    temp_dict_signals = get_signals_from_file(full_name_file=source_file, list_signals=file_to_copy.dict_translate_variables.keys())

                    # Get name of the time vector, which depends on a different logic for the different programs
                    if model.type == 'FiQuS':
                        name_time_signal = 't [s]'
                    elif model.type == 'LEDET':
                        name_time_signal = 'time_vector'
                    elif model.type in ['PSPICE', 'XYCE']:
                        name_time_signal = 'time'

                    # Apply a time shift to all time signals
                    if len(file_to_copy.list_time_shifts) == 0:
                        time_shift = 0
                    elif self.nsti.t == 0 or self.nsti.t > self.n_time_windows:
                        raise Exception(f'The variable list_time_shifts must contain either zero elements when used in PreCoSim or PostCoSim.')
                    elif len(file_to_copy.list_time_shifts) == self.n_time_windows:
                        time_shift = file_to_copy.list_time_shifts[self.nsti.t-1]  # Remember that the time windows are 1-indexed, i.e. the first time window is numbered 1 and not 0 (hence the "-1")
                    else:
                        raise Exception(f'The variable list_time_shifts must contain either zero elements or as many elements as time windows. Instead, list_time_shifts={file_to_copy.list_time_shifts} while there are {self.n_time_windows} time windows.')

                    # If mode='iteration', interpolate the time vector using the time vector of the target model
                    if mode == 'iteration':
                        if self.cosim_data.Simulations[file_to_copy.target_model].type in ['FiQuS']:
                            pass  #TODO add this logic
                        elif self.cosim_data.Simulations[file_to_copy.target_model].type in ['LEDET']:
                            time_vector_params = self.cosim_data.Simulations[file_to_copy.target_model].variables_to_modify_for_each_time_window[self.nsti.t-1]['Options_LEDET.time_vector.time_vector_params']  # Remember that the time windows are 1-indexed, i.e. the first time window is numbered 1 and not 0 (hence the "-1")
                            target_time_vector = []
                            for v in range(len(time_vector_params) // 3):
                                start = time_vector_params[0 + 3 * v]
                                step = time_vector_params[1 + 3 * v]
                                stop = time_vector_params[2 + 3 * v]
                                target_time_vector.extend(np.arange(start, stop + step, step))
                            target_time_vector = np.array(sorted(target_time_vector))  # Convert to np array and avoid repeated values
                        elif self.cosim_data.Simulations[file_to_copy.target_model].type in ['PSPICE', 'XYCE']:
                            time_start = self.cosim_data.Simulations[file_to_copy.target_model].variables_to_modify_for_each_time_window[self.nsti.t-1]['Analysis.simulation_time.time_start']
                            min_time_step = self.cosim_data.Simulations[file_to_copy.target_model].variables_to_modify_for_each_time_window[self.nsti.t-1]['Analysis.simulation_time.min_time_step']
                            time_end = self.cosim_data.Simulations[file_to_copy.target_model].variables_to_modify_for_each_time_window[self.nsti.t-1]['Analysis.simulation_time.time_end']
                            time_schedule: dict = self.cosim_data.Simulations[file_to_copy.target_model].variables_to_modify_for_each_time_window[self.nsti.t-1]['Analysis.simulation_time.time_schedule']  # Remember that the time windows are 1-indexed, i.e. the first time window is numbered 1 and not 0 (hence the "-1")
                            time_vector_params = []
                            t_start = [float(t) for t in time_schedule.keys()]
                            t_step = list(time_schedule.values())
                            target_time_vector = []
                            target_time_vector.extend(np.arange(time_start, time_end + min_time_step, min_time_step))
                            for t in range(len(t_start)):
                                if t < len(time_schedule):
                                    target_time_vector.extend(np.arange(t_start[t], t_start[t+1] + t_step[t], t_step[t]))  # points are added here since afterwards the vector will be sorted
                                else:
                                    target_time_vector.extend(np.arange(t_start[t], time_end + t_step[t], t_step[t]))  # points are added here since afterwards the vector will be sorted
                            target_time_vector = np.array(sorted(target_time_vector))  # Convert to np array, sort the time points, and avoid repeated values
                        else:
                            raise Exception(f'Error while generating file {target_file}: Target model is of type {self.cosim_data.Simulations[file_to_copy.target_model].type}. '
                                        f'For this case, there is no defined way to caltulate the time vector for the software {self.cosim_data.Simulations[file_to_copy.target_model].type}. Please contact steam-team@cern.ch')

                    # # If this is within CoSim (not PreCoSim nor PostCoSim), apply a time shift to all time signals
                    # if self.nsti.t > 0 and self.nsti.t <= self.n_time_windows and mode == 'iteration': # TODO remove PreCoSim/PostCoSim condition
                    #     if model.modelCase == 'circuit' and not BM.circuit_data.Analysis.simulation_time.time_shift:
                    #         BM.circuit_data.Analysis.simulation_time.time_shift = 0
                    #
                    #     if model.type in ['PSPICE', 'XYCE'] and self.cosim_data.Simulations[file_to_copy.target_model].type in ['FiQuS', 'LEDET']:
                    #         time_shift = BM.circuit_data.Analysis.simulation_time.time_shift # + BM.circuit_data.Analysis.simulation_time.time_end
                    #     elif model.type in ['FiQuS', 'LEDET'] and self.cosim_data.Simulations[file_to_copy.target_model].type in ['PSPICE', 'XYCE']:
                    #         # TODO get time_shift from previous time window... or better define a new key?
                    #         time_shift = -self.cosim_data.Simulations[file_to_copy.target_model].CoSim.variables_to_modify_for_each_time_window[self.nsti.t-1]['Analysis.simulation_time.time_shift']  #TODO testing this... maybe a more robust method is needed
                    #         # time_shift = 0  # TODO substitute this
                    #     else:
                    #         time_shift = 0
                    # elif mode == 'time_window' and model.type in ['PSPICE', 'XYCE'] and 'ExternalStimulus' in source_file_name_relative_path:  # TODO horrible hard-coded logic, will change
                    #     if model.modelCase == 'circuit' and not BM.circuit_data.Analysis.simulation_time.time_shift:
                    #         BM.circuit_data.Analysis.simulation_time.time_shift = 0
                    #
                    #     time_shift = BM.circuit_data.Analysis.simulation_time.time_shift  # TODO horrible hard-coded logic, will change
                    # else:
                    #     time_shift = 0
                    # Apply the time shift and interpolate over the target time vector
                    if self.cosim_data.Simulations[file_to_copy.target_model].type in ['FiQuS', 'LEDET']:
                        temp_dict_signals[name_time_signal] = temp_dict_signals[name_time_signal] + time_shift
                        if mode == 'iteration':
                            # Interpolate all signals over the target time vector
                            temp_dict_signals[name_time_signal] = target_time_vector
                            for key, value in temp_dict_signals.items():
                                temp_dict_signals[key] = interp1d(target_time_vector, temp_dict_signals[key])(temp_dict_signals[name_time_signal])
                    elif self.cosim_data.Simulations[file_to_copy.target_model].type in ['PSPICE']:
                        # Note: The function write_time_stimulus_file() will take care of applying the time shift
                        # Interpolate all signals over the target time vector
                        if mode == 'iteration':
                            if target_file.endswith('.stl'):
                                for key, value in temp_dict_signals.items():  # Each value is a dict with hard-coded keys "time" and "value"
                                    temp_dict_signals[key]['time'] = target_time_vector
                                    temp_dict_signals[key] = interp1d(target_time_vector, temp_dict_signals[key]['value'])(temp_dict_signals[key]['time'])
                            else:
                                temp_dict_signals[name_time_signal] = target_time_vector
                                for key, value in temp_dict_signals.items():
                                    temp_dict_signals[key] = interp1d(target_time_vector, temp_dict_signals[key])(temp_dict_signals[name_time_signal])
                    elif self.cosim_data.Simulations[file_to_copy.target_model].type == 'XYCE':
                        pass  # TODO Possibly it'll be included in the previous case, when ParserXYCE supports this option
                    else:
                        raise Exception(f'Error while generating file {target_file}: Target model is of type {self.cosim_data.Simulations[file_to_copy.target_model].type}. '
                                        f'For this case, there is no defined name of the time vector for the software {model.type}. Please contact steam-team@cern.ch')

                    print(f'NSTI: {self.nsti.n_s_t_i}. Model={model.name}. mode={mode}. time_shift={time_shift} s. Source file {source_file}. Target file {target_file}.')
                    # Deal with special hard-coded cases that require editing the files in a specific format
                    if self.cosim_data.Simulations[file_to_copy.target_model].type == 'FiQuS' and model.type in ['FiQuS', 'LEDET', 'PSPICE', 'XYCE']:
                        write_signals_to_csv(full_name_file=target_file, dict_signals=temp_dict_signals, list_signals=[], dict_translate_signal_names=file_to_copy.dict_translate_variables, delimiter=',')
                    elif self.cosim_data.Simulations[file_to_copy.target_model].type == 'LEDET' and model.type in ['FiQuS', 'LEDET', 'PSPICE', 'XYCE']:
                        write_signals_to_csv(full_name_file=target_file, dict_signals=temp_dict_signals, list_signals=[], dict_translate_signal_names=file_to_copy.dict_translate_variables, delimiter=' ')
                    elif self.cosim_data.Simulations[file_to_copy.target_model].type == 'PSPICE':
                        mode_write_stimulus_file = 'one_time_vector'
                        if model.type == 'PSPICE':
                            # In the case of .stl file, solve the special format of the read dictionary
                            _, source_file_type = os.path.splitext(source_file)
                            if source_file_type == '.stl':
                                mode_write_stimulus_file = 'individual_time_vectors'
                        elif model.type == 'XYCE':
                            pass  # TODO possibly time_shift will need updating as done for PSPICE
                        write_time_stimulus_file(path_file=target_file, dict_signals=temp_dict_signals,
                                                 name_time_signal=name_time_signal,
                                                 dict_translate_signal_names=file_to_copy.dict_translate_variables,
                                                 time_shift=time_shift,
                                                 mode=mode_write_stimulus_file,
                                                 name_value_signal='value')
                    # elif self.cosim_data.Simulations[file_to_copy.target_model].type == 'XYCE':  # TODO
                    else:
                        # Standard case where the files are copied without changes
                        print(f'NSTI: {self.nsti.n_s_t_i}. Model={model.name}. mode={mode}. Source file {source_file} copied to file {target_file} without changes.')
                        shutil.copyfile(source_file, target_file)
                    del temp_dict_signals  # To make sure that the variable is not used by mistake for another file
                else:
                    # Standard case where the files are copied without changes
                    print(f'NSTI: {self.nsti.n_s_t_i}. Model={model.name}. mode={mode}. Source file {source_file} copied to file {target_file} without changes.')
                    shutil.copyfile(source_file, target_file)

        return list_copied_files


    def _copy_variables(self, model: Union[sim_Generic, sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE], mode='iteration'):
        '''
        This function copies variables across from the output files of one model to the BuilderModel object of another.
        :param model:
        :return:
        '''

        if mode not in ['iteration', 'time_window']:
            raise Exception(f'This method does not support mode: {mode}')

        # Get list of variables to copy, which depends on the current co-simulation state
        if mode == 'iteration':
            vars_to_copy: List[VariableToCopy] = model.CoSim.variables_to_copy_after_iteration
            dict_key = 'cosim'
        elif mode == 'time_window':
            if self.nsti.t == 0:
                if len(model.PreCoSim.variables_to_copy_after_time_window)==0:
                    vars_to_copy = []
                else:
                    vars_to_copy: List[VariableToCopy] = model.PreCoSim.variables_to_copy_after_time_window
                dict_key = 'pre_cosim'
            elif self.nsti.t > self.n_time_windows:
                vars_to_copy: List[VariableToCopy] = model.PostCoSim.variables_to_copy_after_time_window
                dict_key = 'post_cosim'
            else:
                vars_to_copy: List[VariableToCopy] = model.CoSim.variables_to_copy_after_time_window
                dict_key = 'cosim'


        if len(vars_to_copy) > 0:
            # Define local folder
            local_folder = self.__find_local_source_folder(model=model)

            # Copy files
            for var_to_copy in vars_to_copy:
                # Check whether to add an NSTI suffix between the base name and the extension of the old file name. NSTI: N=simulation number. S=simulation set. T=time window. I=Iteration number
                file_name_relative_path = var_to_copy.source_file_name_relative_path

                # Define dict_variable_types, which determines the expected shape of the variable (used by the function get_signals_from_file() )
                if self.cosim_data.Simulations[model.name].modelCase == 'magnet':
                    empty_data_model = DataModelMagnet()
                elif self.cosim_data.Simulations[model.name].modelCase == 'conductor':
                    empty_data_model = DataModelConductor()
                elif self.cosim_data.Simulations[model.name].modelCase == 'circuit':
                    empty_data_model = DataModelCircuit()
                empty_attr = rgetattr(empty_data_model, var_to_copy.model_var_name)
                if isinstance(empty_attr, list) and len(empty_attr) == 1:
                    dict_variable_types = {var_to_copy.model_var_name: '2D'}
                elif isinstance(empty_attr, list):
                    dict_variable_types = {var_to_copy.model_var_name: '1D'}
                else:
                    dict_variable_types = {var_to_copy.model_var_name: '2D'}

                # Get variable value from the source file. Supported formats: .csd, .csv, .mat
                source_file = Path(Path(local_folder), file_name_relative_path).resolve()
                var_value = get_signals_from_file(full_name_file=source_file, list_signals=var_to_copy.var_name,
                                                  dict_variable_types=dict_variable_types)  # Note: get_signals_from_file() returns a dict
                # If the get_signals_from_file() function returned a dictionary, select the appropriate key
                if isinstance(var_value, dict):
                    var_value = var_value[var_to_copy.var_name]
                # If a numpy array, make it a list
                if isinstance(var_value, np.ndarray):
                    var_value = var_value.tolist()

                # Assign variable values to the self variable that is used to pass their values to future model generation within the co-simulation
                self.dict_to_pass[var_to_copy.target_model]['variables_to_modify'][dict_key][var_to_copy.model_var_name] = var_value  # TODO deal with after time window

    def __find_local_source_folder(self, model: Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE]):
        '''
        Function to find the path to the local folder, which has a different logic for each simulation tool
        :param model: Current simulation model
        :return: Path to the local folder of the current simulation model
        '''
        local_folder_prefix = os.path.join(self.local_PyCoSim_folder,
                                           self.cosim_data.GeneralParameters.cosim_name,
                                           model.type)
        if model.type == 'FiQuS':
            fiqus_input_file_path = os.path.join(local_folder_prefix, model.modelName, f'{model.modelName}_{self.nsti.n_s_t_i}_FiQuS.yaml')
            fiqus_data: DataFiQuS = yaml_to_data(fiqus_input_file_path, DataFiQuS)
            if fiqus_data.run.type in ['geometry_only']:
                return os.path.join(local_folder_prefix, model.modelName, f'Geometry_{fiqus_data.run.geometry}')
            elif fiqus_data.run.type in ['start_from_yaml', 'solve_with_post_process_python', 'post_process_python_only']:
                return os.path.join(local_folder_prefix, model.modelName, f'Geometry_{fiqus_data.run.geometry}', f'Mesh_{fiqus_data.run.mesh}', f'Solution_{fiqus_data.run.solution}')
        elif model.type == 'LEDET':
            return os.path.join(local_folder_prefix, str(self.nsti.n), model.modelName)
        elif model.type in ['PSPICE', 'XYCE']:
            return os.path.join(local_folder_prefix, self.nsti.n, self.nsti.n_s_t_i)
        else:
            raise Exception(f'Software {model.type} not supported for automated running.')

    def __find_local_target_folder(self, model: Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE], nsti: NSTI):
        """
        Function to find the path to the local folder, which has a different logic for each simulation tool.
        This function is used to find an input folder for each tool but also target folder used in copy files to target model (that is the input folder of target model)
        :param model: Current simulation model
        :type model: Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE]
        :param nsti: target nsti object
        :type nsti: NSTI
        :return: Path to the local folder of the current simulation model
        """

        # Define local folder
        local_folder_prefix = os.path.join(self.local_PyCoSim_folder,
                                           self.cosim_data.GeneralParameters.cosim_name,
                                           model.type)
        if model.type == 'FiQuS':
            local_folder = os.path.join(local_folder_prefix, model.modelName)
        elif model.type == 'LEDET':
            local_folder = os.path.join(local_folder_prefix, str(nsti.n), model.modelName)
        elif model.type in ['PSPICE', 'XYCE']:
            local_folder = os.path.join(local_folder_prefix, nsti.n, nsti.n_s_t_i)
        local_folder = str(Path.resolve(Path(local_folder)))
        return local_folder

    @staticmethod
    def _add_nsti_to_file_name(file_name: str, nsti: NSTI):
        """
        Function to add the NSTI suffix between the base file name and its extension
        :param file_name: Name of the file to edit
        :param nsti: NSTI object. NSTI: N=simulation number. S=simulation set. T=time window. I=Iteration number
        :return: Name of the edited file
        """

        base_name, extension = os.path.splitext(file_name)
        return f"{base_name}_{nsti.n_s_t_i}{extension}"

    def _reset_variables_to_pass(self):
        """
        Initialize or reset the dictionary that will be used to pass variable values from an output file to a model data object
        :return:
        """

        self.dict_to_pass = {key: {
            'variables_to_modify': {
                'pre_cosim': {},
                'cosim': {},
                'post_cosim': {}
            }
        } for key in self.cosim_data.Simulations}  # Assign blank_entry to all models

    def _check_convergence(self, model: Union[sim_Generic, sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE], skip_converge_check_due_to_injection):
        """
        # all variable checks must be fulfilled to pass convergence check
        # either relative_tolerance or absolute_tolerance must be fulfilled to pass convergence check
        :param model: Current simulation model
        :type model: object
        :return: True if convergence has been achieved, False if no convergence
        :rtype: bool
        """

        # TODO allow checking convergence on a scalar variable, not just on a vector
        # TODO allow checking convergence on max/min/avg values rather than on a vector

        # If no variable checks are defined for this model, return True (=convergence check passed)
        if len(model.CoSim.convergence) == 0:
            if self.verbose: print(f'NSTI: {self.nsti.n_s_t_i}. Convergence check for model {model.name} passed since no variable checks were set.')
            return True

        # Define local folder
        local_folder = self.__find_local_source_folder(model=model)
        if not self.nsti.t in self.dict_convergence_variables[model.name]:
            self.dict_convergence_variables[model.name][self.nsti.t] = {}
        self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i] = {}
        # Perform the converge checks
        for check_to_perform in model.CoSim.convergence:
            if self.verbose: print(f'NSTI: {self.nsti.n_s_t_i}. Performing convergence check for model {model.name} on variable {check_to_perform.var_name}.')

            # Check whether to add an NSTI suffix between the base name and the extension of the old file name. NSTI: N=simulation number. S=simulation set. T=time window. I=Iteration number
            file_name_relative_path = check_to_perform.file_name_relative_path
            # Get variable value from the source file. Supported formats: .csd, .csv, .mat
            source_file = str(Path(Path(local_folder), file_name_relative_path).resolve())

            replacements = {
                'modelName': model.modelName,
                'n_s_t_i': self.nsti.n_s_t_i,
                'n': self.nsti.n,
                's': self.nsti.s,
                't': self.nsti.t,
                'i': self.nsti.i,
            }
            source_file = template_replace(source_file, replacements)

            var_value = get_signals_from_file(full_name_file=source_file, list_signals=check_to_perform.var_name, dict_variable_types={})[check_to_perform.var_name.strip()]

            # Add convergence variable values to self.self.dict_convergence_variables
            self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i][check_to_perform.var_name] = var_value
            if check_to_perform.time_var_name:
                # Add time vector of the convergence variable values to self.self.dict_convergence_variables
                time_var_value = get_signals_from_file(full_name_file=source_file, list_signals=check_to_perform.time_var_name, dict_variable_types={})[check_to_perform.time_var_name.strip()]
                self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i][check_to_perform.time_var_name] = time_var_value

            # At the first iteration, always return False (no convergence reached yet)
            if self.nsti.i == 0:
                if self.verbose: print(f'Model {model.name}. Simulation set {self.nsti.s}. Time window {self.nsti.t}.')
                return False
            else:
                if skip_converge_check_due_to_injection: # because PyCoSim was started with Start_from_s_t_i the previous iteration (self.nsti.i - 1) are not there. Assigning zeros to them
                    self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i - 1] = {}
                    self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i - 1][check_to_perform.var_name] = np.random.randint(var_value.shape[0])
                    self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i - 1][check_to_perform.time_var_name] = time_var_value
                old_var_value = self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i - 1][check_to_perform.var_name]
                if check_to_perform.time_var_name:
                    # Interpolate the variable over the time vector (use the time vector of the previous iteration)
                    old_time_var_value = self.dict_convergence_variables[model.name][self.nsti.t][self.nsti.i - 1][check_to_perform.time_var_name]
                    new_var_value_interpolated = interp1d(time_var_value, var_value)(old_time_var_value)
                    var_value = new_var_value_interpolated  # Use the interpolated values

                # Perform relative-tolerance check
                rel_error = abs(var_value - old_var_value) / abs(old_var_value)
                # Perform absolute-tolerance check
                abs_error = abs(var_value - old_var_value)
                # Check whether converge criteria are met (the multiple if statements display slightly different information if only rel or abs convergence, or both, were reached
                if np.all(rel_error < check_to_perform.relative_tolerance) and np.all(abs_error <= check_to_perform.absolute_tolerance):
                    flag_converged = True
                    print(f'NSTI: {self.nsti.n_s_t_i}. Model {model.name}. Simulation set {self.nsti.s}. Time window {self.nsti.t}. Convergence reached at iteration {self.nsti.i}. Absolute tolerance: {abs_error} <= {check_to_perform.absolute_tolerance}. Relative tolerance: {rel_error} <= {check_to_perform.relative_tolerance}.')
                elif np.all(rel_error < check_to_perform.relative_tolerance):
                    flag_converged = True
                    print(f'NSTI: {self.nsti.n_s_t_i}. Model {model.name}. Simulation set {self.nsti.s}. Time window {self.nsti.t}. Convergence reached at iteration {self.nsti.i}. Absolute tolerance: {abs_error} > {check_to_perform.absolute_tolerance}. Relative tolerance: {rel_error} <= {check_to_perform.relative_tolerance}.')
                elif np.all(abs_error <= check_to_perform.absolute_tolerance):
                    flag_converged = True
                    print(f'NSTI: {self.nsti.n_s_t_i}. Model {model.name}. Simulation set {self.nsti.s}. Time window {self.nsti.t}. Convergence reached at iteration {self.nsti.i}. Absolute tolerance: {abs_error} <= {check_to_perform.absolute_tolerance}. Relative tolerance: {rel_error} > {check_to_perform.relative_tolerance}.')
                else:
                    flag_converged = False
                    print(f'NSTI: {self.nsti.n_s_t_i}. Model {model.name}. Simulation set {self.nsti.s}. Time window {self.nsti.t}. Convergence not yet reached at iteration {self.nsti.i}. Absolute tolerance: {abs_error}. Relative tolerance: {rel_error}.')
                return flag_converged

    def _get_n_time_windows(self):
        """
        Helper method to calculate number of time windows
        :return: None, just populate self.n_time_windows
        :rtype: None
        """
        dict_check_lengths = {}
        for model in self.cosim_data.Simulations.values():
            if model.CoSim.flag_run:
                dict_check_lengths[model.name] = len(model.CoSim.variables_to_modify_for_each_time_window)
                self.n_time_windows = len(model.CoSim.variables_to_modify_for_each_time_window)
            else:
                self.n_time_windows = 0
        if len(set(list(dict_check_lengths.values()))) > 1:
            raise Exception(f'The variable variables_to_modify.cosim_for_each_time_window must have the same length in all models that have run.cosim=True. {dict_check_lengths}')

    def _update_diary(self, action: str):
        """
        Helper method to add an entry to the co-simulation diary
        :param action: String defining the action to report in the diary. Supported: "run".
        :return: None, just populate self.diary
        :rtype: None
        """

        # Check input
        supported_actions = ['run']
        if not action in supported_actions:
            raise Exception(f'Action {action} is not supported. Supported actions: {supported_actions}.')

        # Initialize the diary key for the current NSTI, if not already present
        if not self.nsti.n_s_t_i in self.diary:
            self.diary[self.nsti.n_s_t_i] = {'run': None}

        # Add a note that the current NSTI simulation was run
        if action == 'run':
            self.diary[self.nsti.n_s_t_i]['run'] = True
