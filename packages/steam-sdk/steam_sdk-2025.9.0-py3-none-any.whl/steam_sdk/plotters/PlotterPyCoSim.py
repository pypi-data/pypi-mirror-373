import os
import glob
import shutil
from pathlib import Path
from typing import Union, List

import matplotlib.pyplot as plt
from matplotlib import cm, colors, font_manager

import numpy as np
from scipy.interpolate import interp1d

from steam_sdk.data.DataCoSim import NSTI
from steam_sdk.data.DataFiQuS import DataFiQuS
from steam_sdk.data.DataModelCircuit import DataModelCircuit
from steam_sdk.data.DataModelConductor import DataModelConductor
from steam_sdk.data.DataModelCosim import sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE, sim_Generic, FileToCopy, VariableToCopy
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataPyCoSim import DataPyCoSim
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.drivers.DriverFiQuS import DriverFiQuS
from steam_sdk.drivers.DriverLEDET import DriverLEDET
from steam_sdk.drivers.DriverPSPICE import DriverPSPICE
from steam_sdk.drivers.DriverXYCE import DriverXYCE
from steam_sdk.parsers.ParserFile import get_signals_from_file
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.read_settings_file import read_settings_file
from steam_sdk.parsers.utils_ParserCosims import write_model_input_files
from steam_sdk.parsers.utils_ParserCosims import template_replace
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.rgetattr import rgetattr

from steam_sdk.cosims.CosimPyCoSim import CosimPyCoSim

from steam_sdk.configs.StylesPlots import styles_plots


class PlotterPyCoSim:

    def __init__(self,
                 file_model_data: str,
                 sim_number: int,
                 data_settings: DataSettings = None,
                 verbose: bool = False
                 ):
        """

        """
        # Load data from input file
        self.cosim_data: DataPyCoSim = yaml_to_data(file_model_data, DataPyCoSim)
        self.local_PyCoSim_folder = Path(data_settings.local_PyCoSim_folder).resolve()
        self.sim_number = sim_number
        self.data_settings = data_settings
        self.verbose = verbose

    def plot_convergence_variable_at_iterations(self, style):

        plot_style = styles_plots[style]  # chosen style
        dict_check_lengths = {}

        for model in self.cosim_data.Simulations.values():
            if model.CoSim.flag_run:
                dict_check_lengths[model.name] = len(model.CoSim.variables_to_modify_for_each_time_window)
                self.n_time_windows = len(model.CoSim.variables_to_modify_for_each_time_window)

        out_dir = os.path.join(self.data_settings.local_PyCoSim_folder, model.modelName, 'Plots')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for model_set, model in enumerate(self.cosim_data.Simulations.values()):
            if model.CoSim.flag_run and len(model.CoSim.convergence) > 0:

                base_folder = os.path.join(self.data_settings.local_PyCoSim_folder, model.modelName, model.type, str(self.sim_number), model.modelName)

                for convergence_dict in model.CoSim.convergence:
                    fig_all_time_windows, (ax_all_time_windows) = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(plot_style['plot_width'], plot_style['plot_height']))
                    fig_each_time_window, (ax_each_time_window) = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(plot_style['plot_width'], plot_style['plot_height']))

                    for tw in range(self.n_time_windows):

                        print(f'Making convergence plot for: {model.name} for time window {tw}')

                        self.nsti = NSTI(self.sim_number, model_set, tw + 1, 0)

                        replacements = {
                            'modelName': model.modelName,
                            'n_s_t_i': f'{self.nsti.n}_{self.nsti.s}_{self.nsti.t}_*',
                            'n': self.nsti.n,
                            's': self.nsti.s,
                            't': self.nsti.t,
                            'i': '*',
                        }
                        convergence_file_rel_path = template_replace(convergence_dict.file_name_relative_path, replacements=replacements)
                        convergence_file_path = Path(os.path.join(base_folder, convergence_file_rel_path)).resolve()
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
                    ax_all_time_windows.set_xlabel(convergence_dict.time_var_name)
                    ax_all_time_windows.set_ylabel(convergence_dict.var_name)
                    ax_each_time_window.set_title(f'n={self.nsti.n}, s={self.nsti.s}')

                    ax_all_time_windows.set_yscale('log')
                    ax_all_time_windows.set_ylim([0.1, 400])
                    ax_all_time_windows.set_xlim([0, 7])
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


if __name__ == "__main__":
    model_name = 'Fusillo_sub'
    sim_number = 2200066
    verbose = True

    data_settings = read_settings_file(absolute_path_settings_folder=os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'tests'), verbose=verbose)
    data_settings.local_PyCoSim_folder = r"D:\tempPyCoSim"

    file_model_data = os.path.join(data_settings.local_PyCoSim_folder, model_name, 'input', f"{model_name}_{sim_number}.yaml")

    ppcs = PlotterPyCoSim(file_model_data=file_model_data, sim_number=sim_number, data_settings=data_settings, verbose=verbose)
    ppcs.plot_convergence_variable_at_iterations(style='poster')
