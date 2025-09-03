import copy
import numpy as np
import statistics
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from steam_sdk.data import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.parsers.ParserRoxie import RoxieList
from steam_sdk.utils.misc import displayWaitAndClose, find_indices
from steam_sdk.plotters import PlotterRoxie


class PlotterModel:
    def __init__(self, roxie_data: RoxieData = None):
        if roxie_data:
            RL = RoxieList(roxie_data)
            self.x_insulated = RL.x_insulated
            self.y_insulated = RL.y_insulated
            self.x_bare = RL.x_bare
            self.y_bare = RL.y_bare
            self.i_conductor = RL.i_conductor
            self.x_strand = RL.x_strand
            self.y_strand = RL.y_strand
            self.i_strand = RL.i_strand
            self.strandToHalfTurn = RL.strand_to_halfTurn

    def plotterModel(self, data, titles, labels, types, texts, size, legends, style, window, scale,
                     order: [] = ['Default']):
        """
            Default plotter for most standard and simple cases
            - data [{'x': [x_data], 'y': [y_data], 'z': [colormap_data]},{...},...]: each entry of the dict contains the data of one plot
                - 'z' contains the colormap data that is going to be used for the colormap in a scatter plot
                - optional flag: 'flag_yscale': int, if added multiple y-axis for this plot will be plotted; int of 'flag_yscale' shows the order of the y-scale (start: 0, max. 4)
            - titles ['Title1','Title2',...]: each entry of the list shows the title of the plot
            - labels [{'x': 'text_x_axis', 'y': 'text_y_axis', 'z': 'text_colorbar'},...]: prints the text of the axis of each plot
            - types ['type1','type2',...]: will pass it to plotterModel_plot_type; 'scatter' and normal 'plot' available so far
            - texts [{'x': [0,2,4,...], 'y': [0,3,5,...], 't': [text1,text2,text3,...]}, {...}, ...]: contains text of each plot that is going to be printed
                - x and y lists contain the data where the associated text i t is going to be located; if t is empty, no text will be printed
            - legends ['Legend1','Legend2',... ]: legend of each plot
            - style [{'color': 'red', 'cmap': None, 'psize': 20, 'pstyle': '|'},{...},...]: style of each plot in dict
                - color: not mapped color is used; cmap has to be None then
                - cmap: just for scatter plots; contains used colormap like 'jet', data['z'] is used to get the sequence of n numbers to be mapped to colors using cmap
                - psize: point or marker size
                - pstyle: style of lines and/or markers; 3 entries in '': first for makers, second and third for line (like fmt in line and marker style: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html)
            - window [1,2,1,3,...]: subplot in which plot is shown; if same window is used multiple times: multiple plots in same subplot
            - scale ['axis_scale1', 'axis_scale2',...]: scale of axis x and y: 'equal' or 'auto' (https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html)
            - size [height, width] of whole figure
            - order [rows, columns]: How subplots are ordered in the whole figure; if not provided 'Default'-setting: one row is going to be uesed

            Examples:
                - test_plotterModel in test_PlotterDefault
                - test_plot_TDMS in test_ParserTDMs
                - test_plot_meas in test_ViewerMeas
        """

        # Define style
        selectedFont = self._define_plot_style()

        if order[0] == 'Default':
            num_windows = len(np.unique(window))
            fig, axs = plt.subplots(nrows=1, ncols=num_windows, figsize=size)
        else:
            fig, axs = plt.subplots(nrows=order[0], ncols=order[1], figsize=size)

        if len(data) == 1 or order == [1,1]:
            axs = [axs]
        for ty, d, ti, l, te, le, st, wi, sc in zip(types, data, titles, labels, texts, legends, style, window, scale):
            ax = axs[wi - 1]
            if 'flag_yscale' in d:
                if d['flag_yscale'] == 0:
                    ax.set_xlabel(l["x"], **selectedFont)
                    self.plot_multi_yaxis_options(ax, st, l, le, selectedFont)
                    plot = self.plotterModel_plot_type(ty, d, le, st, ax)
                elif d['flag_yscale'] == 1:
                    ax1 = axs[wi - 1].twinx()
                    self.plot_multi_yaxis_options(ax1, st, l, le, selectedFont)
                    plot = self.plotterModel_plot_type(ty, d, le, st, ax1)
                elif d['flag_yscale'] == 2:
                    ax2 = axs[wi - 1].twinx()
                    self.plot_multi_yaxis_options(ax2, st, l, le, selectedFont)
                    ax2.spines.right.set_position(("axes", 1.35))
                    plot = self.plotterModel_plot_type(ty, d, le, st, ax2)
                elif d['flag_yscale'] == 3:
                    ax3 = axs[wi - 1].twinx()
                    self.plot_multi_yaxis_options(ax3, st, l, le, selectedFont)
                    ax3.spines['left'].set_position(("axes", -0.35))
                    ax3.yaxis.set_label_position('left')
                    ax3.yaxis.set_ticks_position('left')
                    plot = self.plotterModel_plot_type(ty, d, le, st, ax3)
                else:
                    print('ERROR: Too many y-scales!!')
            else:
                plot = self.plotterModel_plot_type(ty, d, le, st, ax)
                ax.set_xlabel(l["x"], **selectedFont)
                ax.set_ylabel(l["y"], **selectedFont)
            if len(te["t"]) != 0:
                for x, y, z in zip(te["x"], te["y"], te["t"]):
                    ax.text(x, y, z)
            ax.set_title(f'{ti}', **selectedFont)
            ax.figure.autofmt_xdate()
            ax.set_aspect(sc)
            if le is not None:
                ax.legend()
            if st['cmap'] is not None:
                cax = make_axes_locatable(ax).append_axes('right', size='5%', pad=0.05)
                cbar = fig.colorbar(plot, cax=cax, orientation='vertical')
            if len(l["z"]) != 0:
                cbar.set_label(l["z"], **selectedFont)
        # plt.axis('equal')
        plt.tight_layout()
        displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5, flag_show_text=False)  # Show plots in Pycharm, wait a certain time, alert time is up, and close the window

    def plotterModel_plot_type(self, ty, d, le, st, ax):
        """
            defines and uses the different type of plots, like scatter, plot, ...
        """
        if ty == 'scatter':
            if st['cmap'] is not None:
                st['color'] = d['z']
            plot = ax.scatter(d['x'], d['y'], label=le, s=st['psize'], c=st['color'], cmap=st['cmap'],
                              marker=st['pstyle'])  # =cm.get_cmap('jet'))
        elif ty == 'plot':
            plot = ax.plot(d['x'], d['y'], st['pstyle'], label=le, ms=st['psize'], c=st['color'], )
        elif ty == 'semitransparent':
            plot = ax.plot(d['x'], d['y'], st['pstyle'], label=le, ms=st['psize'], c=st['color'], alpha=0.25)
            pass
        return plot

    def plot_multi_yaxis_options(self, ax, st, l, le, selectedFont):
        ax.yaxis.label.set_color(st['color'])
        ax.tick_params(axis='y', colors=st['color'])
        ax.set_ylabel(l["y"], **selectedFont)

    # def plot_field(model_data: DataModelMagnet):
    #     """
    #     Plot magnetic field components of a coil
    #     """
    #     data = [{'x': model_data.x, 'y': model_data.y, 'z': model_data.I},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.Bx},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.By},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.B}]
    #     titles = ['Current [A]', 'Br [T]', 'Bz [T]', 'Bmod [T]']
    #     labels = [{'x': "r (m)", 'y': "z (m)", 'z': ""}] * len(data)
    #     types = ['scatter'] * len(data)
    #     texts = [model_data.text] * len(data)
    #     plotterModel(data, titles, labels, types, texts, (15, 5))
    #
    #
    # def plot_strands_groups_layers(model_data: DataModelMagnet):
    #     types = ['scatter'] * 4
    #     data = [{'x': model_data.x, 'y': model_data.y, 'z': model_data.strandToHalfTurn},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.strandToGroup},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.halfTurnToTurn},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.nS}]
    #     titles = ['strandToHalfTurn', 'strandToGroup', 'halfTurnToTurn', 'Number of strands per half-turn']
    #     labels = [{'x': "r (m)", 'y': "z (m)", 'z': "Half-turn [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Group [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Turn [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Number of  strands per cable [-]"}]
    #     t_ht = copy.deepcopy(model_data.text)
    #     for ht in range(model_data.nHalfTurns):
    #         t_ht['x'].append(model_data.x_ave[ht])
    #         t_ht['y'].append(model_data.y_ave[ht])
    #         t_ht['t'].append('{}'.format(ht + 1))
    #     t_ng = copy.deepcopy(model_data.text)
    #     for g in range(model_data.nGroups):
    #         t_ng['x'].append(model_data.x_ave_group[g])
    #         t_ng['y'].append(model_data.y_ave_group[g])
    #         t_ng['t'].append('{}'.format(g + 1))
    #     texts = [t_ht, t_ng, model_data.text, model_data.text]
    #     plotterModel(data, titles, labels, types, texts, (15, 5))
    #
    #
    # def plot_polarities(model_data: DataModelMagnet):
    #     polarities_inStrand = np.zeros((1, model_data.nStrands), dtype=int)
    #     polarities_inStrand = polarities_inStrand[0]
    #     for g in range(1, model_data.nGroupsDefined + 1):
    #         polarities_inStrand[np.where(model_data.strandToGroup == g)] = model_data.polarities_inGroup[g - 1]
    #     data = [{'x': model_data.x, 'y': model_data.y, 'z': polarities_inStrand}]
    #     titles = ['Current polarities']
    #     labels = [{'x': "r (m)", 'y': "z (m)", 'z': "Polarity [-]"}]
    #     types = ['scatter'] * len(data)
    #     texts = [model_data.text] * len(data)
    #     plotterModel(data, titles, labels, types, texts, (5, 5))
    #
    #
    # def plot_half_turns(model_data: DataModelMagnet):
    #     data = [{'x': model_data.x_ave, 'y': model_data.y_ave, 'z': model_data.HalfTurnToGroup},
    #             {'x': model_data.x_ave, 'y': model_data.y_ave, 'z': model_data.HalfTurnToCoilSection},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.strandToGroup},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.strandToCoilSection}]
    #     titles = ['HalfTurnToGroup', 'HalfTurnToCoilSection', 'StrandToGroup', 'StrandToCoilSection']
    #     labels = [{'x': "r (m)", 'y': "z (m)", 'z': "Group [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Coil section [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Group [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Coil Section [-]"}]
    #     types = ['scatter'] * len(data)
    #     texts = [model_data.text] * len(data)
    #     plotterModel(data, titles, labels, types, texts, (15, 5))

    # def plot_half_turns_NEW(model_data: DataModelMagnet, roxie_data: APIdata):
    #     x_ave, y_ave =  _get_conductor_centers(roxie_data)
    #     data = [{'x': x_ave, 'y': model_data.y_ave, 'z': model_data.HalfTurnToGroup},
    #             {'x': x_ave, 'y': model_data.y_ave, 'z': model_data.HalfTurnToCoilSection},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.strandToGroup},
    #             {'x': model_data.x, 'y': model_data.y, 'z': model_data.strandToCoilSection}]
    #     titles = ['HalfTurnToGroup', 'HalfTurnToCoilSection', 'StrandToGroup', 'StrandToCoilSection']
    #     labels = [{'x': "r (m)", 'y': "z (m)", 'z': "Group [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Coil section [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Group [-]"},
    #               {'x': "r (m)", 'y': "z (m)", 'z': "Coil Section [-]"}]
    #     types = ['scatter'] * len(data)
    #     texts = [model_data.text] * len(data)
    #     plotterModel(data, titles, labels, types, texts, (15, 5))
    #
    #
    # def plot_nonlin_induct(model_data: DataModelMagnet):
    #     f = plt.figure(figsize=(7.5, 5))
    #     plt.plot(model_data.fL_I, model_data.fL_L, 'ro-')
    #     plt.xlabel('Current [A]', **selectedFont)
    #     plt.ylabel('Factor scaling nominal inductance [-]', **selectedFont)
    #     plt.title('Differential inductance versus current', **selectedFont)
    #     plt.xlim([0, model_data.I00 * 2])
    #     plt.grid(True)
    #     plt.rcParams.update({'font.size': 12})
    #     displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)

    def plot_psu_and_trig(self, model_data: DataModelMagnet):
        selectedFont = self._define_plot_style()

        ps = model_data.Power_Supply
        ee = model_data.Quench_Protection.Energy_Extraction
        qh = model_data.Quench_Protection.Quench_Heaters
        cl = model_data.Quench_Protection.CLIQ

        # Plot
        f = plt.figure(figsize=(5, 5))
        plt.plot([ps.t_off, ps.t_off], [0, 1], 'k--', linewidth=4.0, label='t_PC')
        plt.plot([ee.t_trigger, ee.t_trigger], [0, 1], 'r--', linewidth=4.0, label='t_EE')
        plt.plot([cl.t_trigger, cl.t_trigger], [0, 1], 'g--', linewidth=4.0, label='t_CLIQ')
        plt.plot([np.min(qh.t_trigger), np.min(qh.t_trigger)], [0, 1], 'b:', linewidth=2.0, label='t_QH')
        plt.xlabel('Time [s]', **selectedFont)
        plt.ylabel('Trigger [-]', **selectedFont)
        plt.xlim([1E-4, model_data.Options_LEDET.time_vector.time_vector_params[-1]])
        plt.title('Power suppply and quench protection triggers', **selectedFont)
        plt.grid(True)
        plt.rcParams.update({'font.size': 12})
        plt.legend(loc='best')
        plt.tight_layout()
        displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)

    # def plot_quench_prop_and_resist(model_data: DataModelMagnet):
    #     f = plt.figure(figsize=(16, 6))
    #     plt.subplot(1, 4, 1)
    #     # fig, ax = plt.subplots()
    #     plt.scatter(model_data.x_ave * 1000, model_data.y_ave * 1000, s=2, c=model_data.vQ_iStartQuench)
    #     plt.xlabel('x [mm]', **selectedFont)
    #     plt.ylabel('y [mm]', **selectedFont)
    #     plt.title('2D cross-section Quench propagation velocity', **selectedFont)
    #     plt.set_cmap('jet')
    #     plt.grid('minor', alpha=0.5)
    #     cbar = plt.colorbar()
    #     cbar.set_label('Quench velocity [m/s]', **selectedFont)
    #     plt.rcParams.update({'font.size': 12})
    #     # plt.axis('equal')
    #
    #     plt.subplot(1, 4, 2)
    #     plt.scatter(model_data.x_ave * 1000, model_data.y_ave * 1000, s=2, c=model_data.rho_ht_10K)
    #     plt.xlabel('x [mm]', **selectedFont)
    #     plt.ylabel('y [mm]', **selectedFont)
    #     plt.title('Resistivity', **selectedFont)
    #     plt.set_cmap('jet')
    #     plt.grid('minor', alpha=0.5)
    #     cbar = plt.colorbar()
    #     cbar.set_label('Resistivity [$\Omega$*m]', **selectedFont)
    #     plt.rcParams.update({'font.size': 12})
    #     # plt.axis('equal')
    #
    #     plt.subplot(1, 4, 3)
    #     plt.scatter(model_data.x_ave * 1000, model_data.y_ave * 1000, s=2, c=model_data.r_el_ht_10K)
    #     plt.xlabel('x [mm]', **selectedFont)
    #     plt.ylabel('y [mm]', **selectedFont)
    #     plt.title('Resistance per unit length', **selectedFont)
    #     plt.set_cmap('jet')
    #     plt.grid('minor', alpha=0.5)
    #     cbar = plt.colorbar()
    #     cbar.set_label('Resistance per unit length [$\Omega$/m]', **selectedFont)
    #     plt.rcParams.update({'font.size': 12})
    #     # plt.axis('equal')
    #
    #     plt.subplot(1, 4, 4)
    #     plt.scatter(model_data.x_ave * 1000, model_data.y_ave * 1000, s=2, c=model_data.tQuenchDetection * 1e3)
    #     plt.xlabel('x [mm]', **selectedFont)
    #     plt.ylabel('y [mm]', **selectedFont)
    #     plt.title('Approximate quench detection time', **selectedFont)
    #     plt.set_cmap('jet')
    #     plt.grid('minor', alpha=0.5)
    #     cbar = plt.colorbar()
    #     cbar.set_label('Time [ms]', **selectedFont)
    #     plt.rcParams.update({'font.size': 12})
    #     # plt.axis('equal')
    #     displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)
    #
    #
    # def plot_q_prop_v(model_data: DataModelMagnet):
    #     f = plt.figure(figsize=(16, 6))
    #     plt.subplot(1, 2, 1)
    #     plt.plot(model_data.mean_B_ht, model_data.vQ_iStartQuench, 'ko')
    #     plt.xlabel('Average magnetic field in the half-turn [T]', **selectedFont)
    #     plt.ylabel('Quench propagation velocity [m/s]', **selectedFont)
    #     plt.title('Quench propagation velocity', **selectedFont)
    #     plt.set_cmap('jet')
    #     plt.grid('minor', alpha=0.5)
    #     plt.rcParams.update({'font.size': 12})
    #     plt.subplot(1, 2, 2)
    #     plt.plot(model_data.mean_B_ht, model_data.tQuenchDetection * 1e3, 'ko')
    #     plt.xlabel('Average magnetic field in the half-turn [T]', **selectedFont)
    #     plt.ylabel('Approximate quench detection time [ms]', **selectedFont)
    #     plt.title('Approximate quench detection time', **selectedFont)
    #     plt.set_cmap('jet')
    #     plt.grid('minor', alpha=0.5)
    #     plt.rcParams.update({'font.size': 12})
    #     displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)
    #
    #
    def plot_electrical_order(self, el_order_half_turns, elPairs_GroupTogether, strandToGroup,
                              x_strand_from_map2d: np.array, y_strand_from_map2d: np.array,
                              strandToHalfTurn_map2d: np.array, model_data):
        selectedFont = self._define_plot_style()

        # Load useful variables
        x_ave, y_ave = self._get_conductor_centers()
        x_ave_group, y_ave_group = self._get_group_centers(strandToGroup)

        # Transform to arrays
        el_order_half_turns_Array = np.array(el_order_half_turns)
        elPairs_GroupTogether_Array = np.array(elPairs_GroupTogether)
        x_ave, y_ave = np.array(x_ave), np.array(y_ave)
        x_ave_group, y_ave_group = np.array(x_ave_group), np.array(y_ave_group)

        if model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable != 1:
            plt.figure(figsize=(16, 8))
            plt.subplot(1, 3, 1)
            plt.scatter(x_ave, y_ave, s=2, c=np.argsort(el_order_half_turns_Array))
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Electrical order of the half-turns', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Electrical order [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            #   Plot
            plt.subplot(1, 3, 2)
            plt.plot(x_ave[el_order_half_turns_Array - 1], y_ave[el_order_half_turns_Array - 1], 'k')
            plt.scatter(x_ave[el_order_half_turns_Array[0] - 1],
                        y_ave[el_order_half_turns_Array[0] - 1], s=50, c='r',
                        label='Positive lead')
            plt.scatter(x_ave[el_order_half_turns_Array[-1] - 1],
                        y_ave[el_order_half_turns_Array[-1] - 1], s=50, c='b',
                        label='Negative lead')
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Electrical order of the half-turns', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            plt.legend(loc='lower left')
            # Plot
            plt.subplot(1, 3, 3)
            plt.plot(x_ave_group[elPairs_GroupTogether_Array[:, 0] - 1],
                     y_ave_group[elPairs_GroupTogether_Array[:, 0] - 1], 'b')
            plt.scatter(x_ave_group[elPairs_GroupTogether_Array[:, 0] - 1],
                        y_ave_group[elPairs_GroupTogether_Array[:, 0] - 1], s=10,
                        c='b')
            plt.scatter(self.x_strand, self.y_strand, s=2, c='k')
            plt.scatter(x_ave_group, y_ave_group, s=10, c='r')
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Electrical order of the groups (only go-lines)', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            displayWaitAndClose(waitTimeBeforeMessage=1, waitTimeAfterMessage=0.5)
        else:
            nGroups = int(np.max(strandToGroup))
            nHalfTurns = int(np.max(strandToHalfTurn_map2d))
            # Average half-turn positions map2d
            x_ave_map2d = []
            y_ave_map2d = []
            for ht in range(1, nHalfTurns + 1):
                x_ave_map2d = np.hstack(
                    [x_ave_map2d, np.mean(x_strand_from_map2d[np.where(strandToHalfTurn_map2d == ht)])])
                y_ave_map2d = np.hstack(
                    [y_ave_map2d, np.mean(y_strand_from_map2d[np.where(strandToHalfTurn_map2d == ht)])])

            # Average group positions map2d
            x_ave_group_map2d = []
            y_ave_group_map2d = []
            for g in range(1, nGroups + 1):
                x_ave_group_map2d = np.hstack(
                    [x_ave_group_map2d, np.mean(x_strand_from_map2d[np.where(strandToGroup == g)])])
                y_ave_group_map2d = np.hstack(
                    [y_ave_group_map2d, np.mean(y_strand_from_map2d[np.where(strandToGroup == g)])])

            plt.figure(figsize=(16, 8))
            plt.subplot(1, 3, 1)
            plt.scatter(x_ave_map2d, y_ave_map2d, s=2, c=np.argsort(el_order_half_turns_Array))
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Electrical order of the half-turns', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Electrical order [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            #   Plot
            plt.subplot(1, 3, 2)
            plt.plot(x_ave_map2d[el_order_half_turns_Array - 1], y_ave_map2d[el_order_half_turns_Array - 1], 'k')
            plt.scatter(x_ave_map2d[el_order_half_turns_Array[0] - 1],
                        y_ave_map2d[el_order_half_turns_Array[0] - 1], s=50, c='r',
                        label='Positive lead')
            plt.scatter(x_ave_map2d[el_order_half_turns_Array[-1] - 1],
                        y_ave_map2d[el_order_half_turns_Array[-1] - 1], s=50, c='b',
                        label='Negative lead')
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Electrical order of the half-turns', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            plt.legend(loc='lower left')
            # Plot
            plt.subplot(1, 3, 3)
            plt.plot(x_ave_group_map2d[elPairs_GroupTogether_Array[:, 0] - 1],
                     y_ave_group_map2d[elPairs_GroupTogether_Array[:, 0] - 1],
                     'b')
            plt.scatter(x_ave_group_map2d[elPairs_GroupTogether_Array[:, 0] - 1],
                        y_ave_group_map2d[elPairs_GroupTogether_Array[:, 0] - 1], s=10,
                        c='b')
            plt.scatter(x_strand_from_map2d, y_strand_from_map2d, s=2, c='k')
            plt.scatter(x_ave_group_map2d, y_ave_group_map2d, s=10, c='r')
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Electrical order of the groups (only go-lines)', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            displayWaitAndClose(waitTimeBeforeMessage=1, waitTimeAfterMessage=0.5)

    def plot_conductor_numbering(self, model_data, strandToGroup: np.array,
                                 strandToHalfTurn_map2d: np.array, polarities_inGroup: np.array,
                                 x_strand_from_map2d: np.array, y_strand_from_map2d: np.array):
        selectedFont = self._define_plot_style()

        # Load useful variables
        x_ave, y_ave = self._get_conductor_centers()
        x_ave_group, y_ave_group = self._get_group_centers(strandToGroup)

        # Transform to arrays
        x_ave, y_ave = np.array(x_ave), np.array(y_ave)
        x_ave_group, y_ave_group = np.array(x_ave_group), np.array(y_ave_group)
        nGroups = int(np.max(strandToGroup))
        nHalfTurns = int(np.max(self.strandToHalfTurn))

        polarities_inStrand = np.zeros((1, len(self.strandToHalfTurn)), dtype=int)
        polarities_inStrand = polarities_inStrand[0]
        for g in range(1, nGroups + 1):
            polarities_inStrand[np.where(strandToGroup == g)] = polarities_inGroup[g - 1]

        if model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable != 1:
            plt.figure(figsize=(16, 8))
            # Plot group positions
            plt.subplot(1, 3, 1)
            plt.scatter(self.x_strand, self.y_strand, s=1, c=strandToGroup)
            for g in range(nGroups):
                plt.text(x_ave_group[g], y_ave_group[g], '{}'.format(g + 1))
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Index showing to which group each strand belongs', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Group [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            # Plot strand positions
            plt.subplot(1, 3, 2)
            plt.scatter(self.x_strand, self.y_strand, s=1, c=self.strandToHalfTurn)
            for g in range(nHalfTurns):
                plt.text(x_ave[g], y_ave[g], '{}'.format(g + 1))
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Index showing to which half-turn each strand belongs', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Half-turn [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            # Plot polarities
            plt.subplot(1, 3, 3)
            plt.scatter(self.x_strand, self.y_strand, s=1, c=polarities_inStrand)
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Defined polarities', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Polarity [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            displayWaitAndClose(waitTimeBeforeMessage=1, waitTimeAfterMessage=0.5)
        else:
            nHalfTurns = int(np.max(strandToHalfTurn_map2d))
            # Average half-turn positions map2d
            x_ave_map2d = []
            y_ave_map2d = []
            for ht in range(1, nHalfTurns + 1):
                x_ave_map2d = np.hstack(
                    [x_ave_map2d, np.mean(x_strand_from_map2d[np.where(strandToHalfTurn_map2d == ht)])])
                y_ave_map2d = np.hstack(
                    [y_ave_map2d, np.mean(y_strand_from_map2d[np.where(strandToHalfTurn_map2d == ht)])])

            # Average group positions map2d
            x_ave_group_map2d = []
            y_ave_group_map2d = []
            for g in range(1, nGroups + 1):
                x_ave_group_map2d = np.hstack(
                    [x_ave_group_map2d, np.mean(x_strand_from_map2d[np.where(strandToGroup == g)])])
                y_ave_group_map2d = np.hstack(
                    [y_ave_group_map2d, np.mean(y_strand_from_map2d[np.where(strandToGroup == g)])])

            plt.figure(figsize=(16, 8))
            # Plot group positions
            plt.subplot(1, 3, 1)
            plt.scatter(x_strand_from_map2d, y_strand_from_map2d, s=1, c=strandToGroup)
            for g in range(nGroups):
                plt.text(x_ave_group_map2d[g], y_ave_group_map2d[g], '{}'.format(g + 1))
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Index showing to which group each strand belongs', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Group [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            # Plot strand positions
            plt.subplot(1, 3, 2)
            plt.scatter(x_strand_from_map2d, y_strand_from_map2d, s=1, c=self.strandToHalfTurn)
            for g in range(nHalfTurns):
                plt.text(x_ave_map2d[g], y_ave_map2d[g], '{}'.format(g + 1))
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Index showing to which half-turn each strand belongs', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Half-turn [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            # Plot polarities
            plt.subplot(1, 3, 3)
            plt.scatter(x_strand_from_map2d, y_strand_from_map2d, s=1, c=polarities_inStrand)
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Defined polarities', **selectedFont)
            plt.set_cmap('jet')
            cbar = plt.colorbar()
            cbar.set_label('Polarity [-]', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            displayWaitAndClose(waitTimeBeforeMessage=1, waitTimeAfterMessage=0.5)

    def plot_heat_connections(self, iContactAlongHeight_From, iContactAlongHeight_To,
                              iContactAlongWidth_From, iContactAlongWidth_To, x_strand_from_map2d: np.array,
                              y_strand_from_map2d: np.array, strandToHalfTurn_map2d: np.array, model_data):
        selectedFont = self._define_plot_style()

        # Load useful variables
        x_ave, y_ave = self._get_conductor_centers()
        # Transform to arrays
        x_ave, y_ave = np.array(x_ave), np.array(y_ave)
        iContactAlongHeight_From_Array = np.int_(iContactAlongHeight_From)
        iContactAlongHeight_To_Array = np.int_(iContactAlongHeight_To)
        iContactAlongWidth_From_Array = np.int_(iContactAlongWidth_From)
        iContactAlongWidth_To_Array = np.int_(iContactAlongWidth_To)

        if model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable != 1:
            plt.figure(figsize=(16, 8))
            # plot conductors
            for c, (cXPos, cYPos) in enumerate(zip(self.x_insulated, self.y_insulated)):
                pt1, pt2, pt3, pt4 = (cXPos[0], cYPos[0]), (cXPos[1], cYPos[1]), (cXPos[2], cYPos[2]), (
                cXPos[3], cYPos[3])
                polygon = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='r', edgecolor='k',
                                   alpha=.25)
                plt.gca().add_patch(polygon)
            # plot average conductor positions
            plt.scatter(x_ave, y_ave, s=10, c='r')
            # plot heat exchange links along the cable narrow side
            for i in range(len(iContactAlongHeight_From)):
                plt.plot([x_ave[iContactAlongHeight_From_Array[i] - 1], x_ave[iContactAlongHeight_To_Array[i] - 1]],
                         [y_ave[iContactAlongHeight_From_Array[i] - 1], y_ave[iContactAlongHeight_To_Array[i] - 1]],
                         'k')
            # plot heat exchange links along the cable wide side
            for i in range(len(iContactAlongWidth_From)):
                plt.plot([x_ave[iContactAlongWidth_From_Array[i] - 1], x_ave[iContactAlongWidth_To_Array[i] - 1]],
                         [y_ave[iContactAlongWidth_From_Array[i] - 1], y_ave[iContactAlongWidth_To_Array[i] - 1]], 'r')
            # plot strands belonging to different conductor groups and closer to each other than max_distance
            # for p in pairs_close:
            #     if not strandToGroup[p[0]] == strandToGroup[p[1]]:
            #         plt.plot([X[p[0], 0], X[p[1], 0]], [X[p[0], 1], X[p[1], 1]], c='g')
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Heat exchange order of the half-turns', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            displayWaitAndClose(waitTimeBeforeMessage=1, waitTimeAfterMessage=0.5)
        else:
            nHalfTurns = int(np.max(strandToHalfTurn_map2d))
            # Average half-turn positions map2d
            x_ave_map2d = []
            y_ave_map2d = []
            for ht in range(1, nHalfTurns + 1):
                x_ave_map2d = np.hstack(
                    [x_ave_map2d, np.mean(x_strand_from_map2d[np.where(strandToHalfTurn_map2d == ht)])])
                y_ave_map2d = np.hstack(
                    [y_ave_map2d, np.mean(y_strand_from_map2d[np.where(strandToHalfTurn_map2d == ht)])])

            plt.figure(figsize=(16, 8))
            # plot conductors
            for c, (cXPos, cYPos) in enumerate(zip(self.x_insulated, self.y_insulated)):
                pt1, pt2, pt3, pt4 = (cXPos[0], cYPos[0]), (cXPos[1], cYPos[1]), (cXPos[2], cYPos[2]), (
                cXPos[3], cYPos[3])
                line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='r', edgecolor='k',
                                   alpha=.25)
                plt.gca().add_line(line)
            # plot average conductor positions
            plt.scatter(x_ave_map2d, y_ave_map2d, s=10, c='r')
            # plot heat exchange links along the cable narrow side
            for i in range(len(iContactAlongHeight_From)):
                plt.plot([x_ave_map2d[iContactAlongHeight_From_Array[i] - 1],
                          x_ave_map2d[iContactAlongHeight_To_Array[i] - 1]],
                         [y_ave_map2d[iContactAlongHeight_From_Array[i] - 1],
                          y_ave_map2d[iContactAlongHeight_To_Array[i] - 1]], 'k')
            # plot heat exchange links along the cable wide side
            for i in range(len(iContactAlongWidth_From)):
                plt.plot([x_ave_map2d[iContactAlongWidth_From_Array[i] - 1],
                          x_ave_map2d[iContactAlongWidth_To_Array[i] - 1]],
                         [y_ave_map2d[iContactAlongWidth_From_Array[i] - 1],
                          y_ave_map2d[iContactAlongWidth_To_Array[i] - 1]], 'r')
            # plot strands belonging to different conductor groups and closer to each other than max_distance
            # for p in pairs_close:
            #     if not strandToGroup[p[0]] == strandToGroup[p[1]]:
            #         plt.plot([X[p[0], 0], X[p[1], 0]], [X[p[0], 1], X[p[1], 1]], c='g')
            plt.xlabel('x [m]', **selectedFont)
            plt.ylabel('y [m]', **selectedFont)
            plt.title('Heat exchange order of the half-turns', **selectedFont)
            plt.rcParams.update({'font.size': 12})
            plt.axis('equal')
            displayWaitAndClose(waitTimeBeforeMessage=1, waitTimeAfterMessage=0.5)

    def plot_power_supl_contr(self, model_data: DataModelMagnet):
        selectedFont = self._define_plot_style()

        ps = model_data.Power_Supply

        plt.figure(figsize=(5, 5))
        plt.plot([ps.t_off, ps.t_off], [np.min(ps.I_control_LUT), np.max(ps.I_control_LUT)], 'k--', linewidth=4.0,
                 label='t_PC')
        plt.plot(ps.t_control_LUT, ps.I_control_LUT, 'ro-', label='LUT')
        plt.xlabel('Time [s]', selectedFont)
        plt.ylabel('Current [A]', selectedFont)
        plt.title('Look-up table controlling power supply', selectedFont)
        plt.grid(True)
        plt.rcParams.update({'font.size': 12})
        displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)

    def plot_all(self, model_data: DataModelMagnet):
        """
            Plot all default plots
        """
        # # plot_field(model_data)
        # plot_polarities(model_data, roxie_data)
        # plot_strands_groups_layers(model_data)
        # plot_electrical_order(model_data)
        # plot_q_prop_v(model_data)
        # # plot_quench_prop_and_resist(model_data)
        self.plot_psu_and_trig(model_data)
        # plot_half_turns(model_data, roxie_data)
        # plot_heat_exchange_order(model_data)
        # plot_nonlin_induct(model_data)
        self.plot_power_supl_contr(model_data)

    ############## Helper functions
    def _define_plot_style(self):
        """
        Define default style for plots
        """
        selectedFont = {'fontname': 'DejaVu Sans', 'size': 14}  # Define style for plots
        return selectedFont

    def _get_conductor_centers(self):
        """
            Find center locations of each half-turn
        """
        nHalfTurns = len(self.x_insulated)
        x_ave, y_ave = [], []
        for ht in range(nHalfTurns):
            x_ave.append(statistics.mean(self.x_insulated[ht]))
            y_ave.append(statistics.mean(self.y_insulated[ht]))

        return x_ave, y_ave

    def _get_group_centers(self, strandToGroup):
        """
            Find center locations of each group of half-turns (i.e. coil blocks)
        """
        nGroups = int(np.max(strandToGroup))
        # Average group positions
        x_ave_group = []
        y_ave_group = []
        for g in range(1, nGroups + 1):
            idx_g = find_indices(strandToGroup, lambda s: s == g)  # indices of the strands belonging to group g
            list_x = [self.x_strand[i] for i in idx_g]  # list of all x positions of strands belonging to group g
            list_y = [self.y_strand[i] for i in idx_g]  # list of all y positions of strands belonging to group g

            x_ave_group.append(statistics.mean(list_x))
            y_ave_group.append(statistics.mean(list_y))

        return x_ave_group, y_ave_group
