import os
import unittest
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.parsers.ParserMap2d import ParserMap2dFile
from steam_sdk.plotters.PlotterModel import PlotterModel
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.read_settings_file import read_settings_file


class TestPlotterDefault(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output'), verbose=True)

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

        # Close all figures
        plt.close('all')


    def test_plotterModel(self, magnet_name: str = 'MBRD', flag_save_png: int = 0):
        """
            Example of plotting the group each strand belongs to, the half - turn each strand belongs to and the electrical order
            of a desired magnet (in this case MBRD), but can be used with test_plotter_model_save_plots for the whole
            magnet library; the style should be the same as the according specific plots in PlotterModel
        """

        # Paths
        magnet_folder = Path(Path('..') / Path(os.path.join('builders', 'model_library', 'magnets', magnet_name,))).resolve()
        file_model_data = Path(magnet_folder, 'input', 'modelData_' + magnet_name + '.yaml')
        nameFileSMIC = os.path.join(magnet_folder, 'output', magnet_name + '_selfMutualInductanceMatrix.csv')
        output_path = os.path.join('output')

        #Builders
        BM = BuilderModel(file_model_data=file_model_data, data_settings=self.settings, verbose=False)
        BM.buildLEDET(sim_name=magnet_name, sim_number='_string_added_to_file', output_path=output_path, flag_json=False, flag_plot_all=False, verbose=False)

        BL = BuilderLEDET(path_input_file=file_model_data, input_model_data=BM.model_data,
                          input_roxie_data=BM.roxie_data, input_map2d=BM.map2d_file_modified,
                          smic_write_path=nameFileSMIC, flag_build=True, flag_plot_all=False,
                          verbose=BM.verbose)

        #Data
        if BM.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == 1:  #Ribbon

            _, _, _, strandToHalfTurn, strandToGroup, x_strand, y_strand, _ = ParserMap2dFile(map2dFile=Path(BM.map2d_file_modified)).getParametersFromMap2d()
            nGroups = int(np.max(strandToGroup))
            nHalfTurns = int(np.max(strandToHalfTurn))

            # Average half-turn positions map2d
            x_ave = []
            y_ave = []
            for ht in range(1, nHalfTurns + 1):
                x_ave = np.hstack([x_ave, np.mean(x_strand[np.where(strandToHalfTurn == ht)[0][0]])])
                y_ave = np.hstack([y_ave, np.mean(y_strand[np.where(strandToHalfTurn == ht)[0][0]])])

            # Average group positions map2d
            x_ave_group = []
            y_ave_group = []
            for g in range(1, nGroups + 1):
                x_ave_group = np.hstack([x_ave_group, np.mean(x_strand[np.where(strandToGroup == g)])])
                y_ave_group = np.hstack([y_ave_group, np.mean(y_strand[np.where(strandToGroup == g)])])

            # texts
            x_text_grp, y_text_grp, t_text_grp = [], [], []
            for g in range(nGroups):
                x_text_grp.append(x_ave_group[g])
                y_text_grp.append(y_ave_group[g])
                t_text_grp.append('{}'.format(g + 1))

            x_text_hT, y_text_hT, t_text_hT = [], [], []
            for g in range(nHalfTurns):
                x_text_hT.append(x_ave[g])
                y_text_hT.append(y_ave[g])
                t_text_hT.append('{}'.format(g + 1))

        else:
            _, _, _, strandToHalfTurn, strandToGroup, x_strand, y_strand, _, _, _ = ParserMap2dFile(map2dFile=Path(BM.path_map2d)).getParametersFromMap2d()
            nGroups = int(np.max(strandToGroup))
            nHalfTurns = int(np.max(strandToHalfTurn))

            PM = PlotterModel(BM.roxie_data)
            x_ave, y_ave = PM._get_conductor_centers()
            x_ave, y_ave = np.array(x_ave), np.array(y_ave)
            x_ave_group, y_ave_group = PM._get_group_centers(strandToGroup)
            x_ave_group, y_ave_group = np.array(x_ave_group), np.array(y_ave_group)

            # texts
            x_text_grp, y_text_grp, t_text_grp = [], [], []
            for g in range(nGroups):
                x_text_grp.append(x_ave_group[g])
                y_text_grp.append(y_ave_group[g])
                t_text_grp.append('{}'.format(g + 1))

            x_text_hT, y_text_hT, t_text_hT = [], [], []
            for g in range(nHalfTurns):
                x_text_hT.append(x_ave[g])
                y_text_hT.append(y_ave[g])
                t_text_hT.append('{}'.format(g + 1))

        el_order_sort = np.argsort(BL.Inputs.el_order_half_turns)

        ## PLOTS ##
        data = [{'x': x_strand, 'y': y_strand, 'z': strandToGroup},
                {'x': x_strand, 'y': y_strand, 'z': strandToHalfTurn},
                {'x': x_ave, 'y': y_ave, 'z': el_order_sort}, ]
        len_data = len(data)
        titles = ['Index showing to which group each strand belongs',
                  'Index showing to which half - turn each strand belongs',
                  'Electrical order of the half-turns']
        labels = [{'x': 'x [m]', 'y': 'y [m]', 'z': 'Group [-]'},
                  {'x': 'x [m]', 'y': 'y [m]', 'z': 'Half-turn [-]'},
                  {'x': 'x [m]', 'y': 'y [m]', 'z': 'Electrical order [-]'},
                  ]
        types = ['scatter'] * len_data
        texts = [{'x': x_text_grp, 'y': y_text_grp, 't': t_text_grp},
                 {'x': x_text_hT, 'y': y_text_hT, 't': t_text_hT},
                 {'x': [], 'y': [], 't': []}]
        legends = [None] * len_data
        style = [{'color': None, 'cmap': 'jet', 'psize': 1, 'pstyle': '.'},
                 {'color': None, 'cmap': 'jet', 'psize': 1, 'pstyle': '.'},
                 {'color': None, 'cmap': 'jet', 'psize': 2, 'pstyle': '.'}]
        window = [1,2,3]
        axis = ['equal']*len_data
        size = [16, 8]
        order = [3, 1]

        PM = PlotterModel()
        #PM.plotterModel(data, titles, labels, types, texts, size, legends, style, window, axis, order=order)

        # If you want to save the magnet pictures uncomment this:
        # plt.savefig(Path(output_path, magnet_name + '.png'), format='png')

    # def test_plotter_model_save_plots(self):
    #     """
    #           This method plots and saves all of the magnets from the magnet_library with the test_plotterModel method.
    #     """
    #
    #     magnet_names = ['MBRB', 'MQXF_V2', 'MQSX', 'MBRD', 'MBXF', 'MB_2COILS',
    #                         'MED_C_COMB', 'MQMC_2in1', 'MQM_2in1', 'MQML_2in1', 'MQ_1AP', 'MO_1AP', 'MO',
    #                         'MQXB', 'MQY_2in1', 'MS_1AP', 'MCO', 'MCDO', 'MQT_1AP', 'MBH_1in1',
    #                         'MSS_1AP', 'MQTLH_1AP', 'MQTLI_1AP', 'MQS_1AP', 'MBRC',
    #                         'ERMC_V1', 'HEPDipo_4COILS', 'MCD', 'RMM_V1', 'MCBYH_1AP', 'MCS', 'MBX', 'MQXA',
    #                         'MBRS', 'MCBX_HV', 'MCBXH', 'MCBXV', 'CFD_600A'
    #                             ]
    #
    #     test = TestPlotterDefault()
    #
    #     for name in magnet_names:
    #         TestPlotterDefault.test_plotterModel(test, magnet_name=name)






