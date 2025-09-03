import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
from matplotlib.collections import PatchCollection
from steam_sdk.data.DataRoxieParser import CoilData
from steam_sdk.data.DataPlot import DataPlot
from steam_sdk.parsers.ParserYAML import yaml_to_data


class PlotterGriddedData:
    """
    Class for 2D plots of pairwise and gridded FiQuS Multipole data
    """

    def __init__(
            self,
            parsed_results_path: Path,
            simulation_name: str,
            coil_data: CoilData = None,
            ffmpeg_exe_path: Path = None,
            verbose: bool = True
    ):
        """
        :param parsed_results_path: full paths to FiQuS Solution folders
        :param simulation_name: physical quantities to manipulate per solution
        """
        self.parsed_results_path = parsed_results_path
        self.simulation_name = simulation_name

        plt.rcParams['animation.ffmpeg_path'] = ffmpeg_exe_path
        self.plot_settings: DataPlot =\
            yaml_to_data(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      '../../tests/plotters/plotData_settings.yaml'), DataPlot)

        self.conductors_corners_coordinates = {'iH': [], 'iL': [], 'oH': [], 'oL': []}
        for po in coil_data.physical_order:
            block = coil_data.coils[po.coil].poles[po.pole].layers[po.layer].windings[po.winding].blocks[po.block]
            for halfTurn_nr, halfTurn in block.half_turns.items():
                self.conductors_corners_coordinates['iH'].append([halfTurn.corners.bare.iH.x, halfTurn.corners.bare.iH.y])
                self.conductors_corners_coordinates['iL'].append([halfTurn.corners.bare.iL.x, halfTurn.corners.bare.iL.y])
                self.conductors_corners_coordinates['oH'].append([halfTurn.corners.bare.oH.x, halfTurn.corners.bare.oH.y])
                self.conductors_corners_coordinates['oL'].append([halfTurn.corners.bare.oL.x, halfTurn.corners.bare.oL.y])

        self.physical_quantities = ('temperature', 'magnetic_flux_density')
        # self.data_frames = {solution: {} for solution in self.solution_folders_paths}

        # # Check if all solution folder paths exist
        # for path in self.solution_folders_paths.values():
        #     if not os.path.exists(path):
        #         raise Exception(f"Solution folder '{path}' does not exist.")
        #
        # if physical_quantity_to_initialize_per_solution:
        #     # Check if the keys of both input dicts match
        #     for solution_key in physical_quantity_to_initialize_per_solution.keys():
        #         if solution_key not in solution_folders_paths:
        #             raise Exception(f"Solution name '{solution_key}' is not present among the solution names provided with the associated paths.")
        #
        #     for solution_key, physical_quantity in physical_quantity_to_initialize_per_solution.items():
        #         self.data_frames[solution_key][physical_quantity] = pd.DataFrame()
        #         getattr(self, f'parse_{physical_quantity}_results')(solution_key)
        # else:
        #     for physical_quantity in self.physical_quantities:
        #         for solution_key in self.solution_folders_paths.keys():
        #             self.data_frames[solution_key][physical_quantity] = pd.DataFrame()
        #             getattr(self, f'parse_{physical_quantity}_results')(solution_key)

    def plot_conductors_temperatures_over_time(self, file_name: str, data_type: str = 'physical_quantity'):
        """
        Plots temperature related results
        :return: Nothing, only does file and folder operation
        :rtype: None
        """
        crns = self.conductors_corners_coordinates

        def update(frame):
            collection.set_facecolor(cmap(norm(data_frame.iloc[frame, 1:])))
            ax.set_title(f"Time: {data_frame['Time'][frame]:.3f}s")
            return ax

        data_frame = pd.read_csv(os.path.join(self.parsed_results_path, file_name))
        fig = plt.figure(1)
        ax = plt.axes()
        ax.set_xlabel('x [cm]', size=self.plot_settings.FontSizes.labels)  # adjust other plots to cm
        ax.set_ylabel('y [cm]', size=self.plot_settings.FontSizes.labels)
        ax.tick_params(axis='x', labelsize=self.plot_settings.FontSizes.ticks)
        ax.tick_params(axis='y', labelsize=self.plot_settings.FontSizes.ticks)

        min_value = data_frame.iloc[:, 1:].min().min()
        max_value = data_frame.iloc[:, 1:].max().max()
        ht_polygons = [patches.Polygon(np.array([(crns['iH'][i][0], crns['iH'][i][1]), (crns['iL'][i][0], crns['iL'][i][1]),
                                                 (crns['oL'][i][0], crns['oL'][i][1]), (crns['oH'][i][0], crns['oH'][i][1])]) * 1e2,
                                       closed=True) for i in range(len(crns['iH']))]
        collection = PatchCollection(ht_polygons)
        ax.add_collection(collection)
        cmap = plt.get_cmap('plasma')
        norm = plt.Normalize(vmin=min_value, vmax=max_value)
        cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax)
        if data_type == 'absolute_error': cbar.set_label('Absolute Error [K]')
        elif data_type == 'relative_error': cbar.set_label('Relative Error [%]')
        else: cbar.set_label('Temperature [K]')
        cbar.ax.yaxis.label.set_fontsize(self.plot_settings.FontSizes.labels)
        cbar.ax.tick_params(labelsize=self.plot_settings.FontSizes.ticks)
        ax.autoscale_view()

        ani = animation.FuncAnimation(fig, update, frames=data_frame['Time'].size, repeat=False)
        # plt.show()
        ani.save(os.path.join(self.parsed_results_path, f"{self.simulation_name}_{file_name[:-4]}.mp4"), writer='ffmpeg', dpi=300)
        fig.savefig(os.path.join(self.parsed_results_path, f"{self.simulation_name}_{file_name[:-4]}.pdf"), bbox_inches='tight')

        plt.clf()

    def plot_time_figure(self, solution: str, physical_quantity: str, half_turns: List[int], save: bool = False):
        """
        Plots physical quantity evolution over time
        :return: Nothing, only does file and folder operation
        :rtype: None
        """
        pass  # todo: move to PlotterPairwiseData
        # plot_objects = {str(half_turn): None for half_turn in half_turns}
        # fig_width, fig_height = 8.5, 6.5
        # font_sizes = {'axis_label': 14, 'axis_ticks': 12}
        # font_weights = {'axis_label': 'regular', 'axis_ticks': 'regular'}
        # line_styles = {'Ref': 'solid', 'TSA': 'dashed', 'QH': 'dashed'}
        # marker_frequency = {'Ref': 0.2, 'TSA': 0.23, 'QH': 0}
        # plt.figure(1)
        # plt.figure(1).set_figwidth(fig_width)
        # plt.figure(1).set_figheight(fig_height)
        # markers = ['o', 's', 'D', '^']
        # fig_cond_T = plt.axes()
        # fig_cond_T.set_xlabel('Time [s]', size=self.plot_settings.FontSizes.labels, weight=font_weights['axis_label'])
        # fig_cond_T.set_ylabel('Temperature [K]', size=self.plot_settings.FontSizes.labels, weight=font_weights['axis_label'])
        # fig_cond_T.tick_params(axis='x', labelsize=self.plot_settings.FontSizes.ticks)
        # fig_cond_T.tick_params(axis='y', labelsize=self.plot_settings.FontSizes.ticks)
        # color_database = {'intense_blue': [0, 115, 181],
        #                   'morning_orange': [242, 151, 43],
        #                   'october': [205, 93, 4],
        #                   'dark_red': [170, 0, 0]}
        # color_data = {color_name: [i / 255 for i in color] for color_name, color in color_database.items()}
        # colors = {'Ref': color_data['intense_blue'], 'TSA': color_data['morning_orange'], 'Pow': [0, 0, 0],
        #           'Cur': color_data['dark_red']}
        #
        # for half_turn in half_turns:
        #     half_turn_label = f'HT{half_turn}'
        #     plot_objects[str(half_turn)] =\
        #         fig_cond_T.plot(self.data_frames[solution][physical_quantity]['Time'], self.data_frames[solution][physical_quantity][half_turn_label],
        #                         color=colors['TSA'], linestyle=line_styles['TSA'], linewidth=2, marker=markers[0],
        #                         markevery=marker_frequency['TSA'], label=half_turn_label)[0]
        #
        # plt.show()
