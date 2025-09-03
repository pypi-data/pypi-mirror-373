import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm, colors, font_manager
import seaborn as sns
from scipy.optimize import curve_fit

from steam_sdk.parsers.ParserMat import Parser_LEDET_Mat

sns.set(context='notebook', style='ticks', palette='deep', font='Times New Roman', font_scale=1.3,
        color_codes=False, rc={'figure.figsize': (5.2, 2.6), "axes.linewidth": 0.7, 'xtick.major.width': 0.7, 'xtick.major.size': 3.0, 'ytick.major.width': 0.7, 'ytick.major.size': 3.0})

plt.rcParams["font.family"] = "Times New Roman"

class PlotterParametric:
    def __init__(self, base_path, base_magnet_name, magnet_labels_list, sim_nr_list_of_lists, style, value, save=False, print_only=False):
        self.base_path = base_path
        self.base_magnet_name = base_magnet_name
        if len(magnet_labels_list) != len(sim_nr_list_of_lists):
            raise ValueError(f'magnet_labels_list is {len(magnet_labels_list)} long and does not match sim_nr_list_of_lists that is {len(sim_nr_list_of_lists)} long')
        self.magnet_labels_list = magnet_labels_list
        self.sim_nr_list_of_lists = sim_nr_list_of_lists
        self.save = save
        self.print_only = print_only
        self.time_label = 'Time'
        self.value = value
        self.values_dict = {
            'Time': {'mat_label': 'time_vector', 'min': 0.0, 'max': 0.8, 'unit': 's'},
            'T max': {'mat_label': 'T_ht', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'K'},
            'I mag': {'mat_label': 'I_CoilSections', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'A'},
            'U max': {'mat_label': 'Uground_half_turns', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'V'},
            'U min': {'mat_label': 'Uground_half_turns', 'op': 'min', 'min': 0, 'max': 200, 'unit': 'V'},
            'R mag': {'mat_label': 'R_CoilSections', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'Ohm'}
        }
        styles_dict = {
            'poster': {'plot_width': 1.9*8.9/2.54, 'plot_height': 3.2*6.2/2.54, 'font_size': 24},
            'publication': {'plot_width': 8.9/2.54, 'plot_height': 4/2.54, 'font_size': 5}
        }
        self.colormaps = ['Greens', 'Blues', 'Oranges', 'Purples', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']

        self.cs = styles_dict[style]    # chosen style


        self.cvd = self.values_dict[self.value]    # chosen value dict
        self.td = self.values_dict[self.time_label]  # time dict
        self.magnet_dict = {}
        self.time_dict = {}
        self.sim_nr_dict = {}
        self.peak_T_dict = {}
        self.I_mag_dict = {}
        for magnet_label, sim_nr_list in zip(self.magnet_labels_list, self.sim_nr_list_of_lists):
            self.sim_nr_dict[magnet_label] = sim_nr_list
            self.peak_T_dict[magnet_label] = []
            self.I_mag_dict[magnet_label] = []
            SampleData = []
            for sim_seq, sim_nr in enumerate(sim_nr_list):
                mat_file_obj = Parser_LEDET_Mat(self.base_path, self.base_magnet_name, sim_nr)
                t = mat_file_obj.t - np.min(mat_file_obj.t)
                if sim_seq == 0:  # take interpolation time vector from the first simulation
                    t_for_interp = t
                    self.time_dict[magnet_label] = t_for_interp
                y = mat_file_obj.data_1D(self.cvd['mat_label'], op=self.cvd['op'])
                y_i = np.interp(t_for_interp, t, y)
                self.peak_T_dict[magnet_label].append(np.max(mat_file_obj.data_1D('T_ht', op='max')))
                self.I_mag_dict[magnet_label].append(np.max(mat_file_obj.data_1D('I_CoilSections', op='max')))
                SampleData.append(y_i)
            self.magnet_dict[magnet_label] = np.array(SampleData).T

    def plt_T_vs_I(self, hex_color_list):

        def func(x, c3, c2, c1, offset):
            return c3 * x ** 3 + c2 * x ** 2 + c1 * x + offset

        fig, (ax1) = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(self.cs['plot_width'], self.cs['plot_height']))
        #ax_map = [ax1,ax1,ax1,ax1,ax2,ax2,ax2,ax2,ax3,ax3,ax3,ax3]
        ax_map = [ax1, ax1, ax1, ax1, ax1, ax1, ax1, ax1, ax1, ax1, ax1, ax1]
        markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
        for i, magnet_label in enumerate(self.magnet_dict.keys()):
            I_mag = np.array(self.I_mag_dict[magnet_label])
            T_peak = np.array(self.peak_T_dict[magnet_label])
            ax_map[i].scatter(I_mag, T_peak, color=hex_color_list[i], label=magnet_label, s=10, marker=markers[i])

            # these are the same as the scipy defaults
            initialParameters = np.array([1e-6, -1.5e-3, 5e-1, -3.0])
            # curve fit the test data
            fittedParameters, pcov = curve_fit(func, I_mag, T_peak, initialParameters)
            modelPredictions = func(I_mag, *fittedParameters)
            absError = modelPredictions - T_peak
            SE = np.square(absError)  # squared errors
            MSE = np.mean(SE)  # mean squared errors
            RMSE = np.sqrt(MSE)  # Root Mean Squared Error, RMSE
            Rsquared = 1.0 - (np.var(absError) / np.var(T_peak))
            print('Parameters:', fittedParameters)
            print('RMSE:', RMSE)
            print('R-squared:', Rsquared)
            xModel = np.linspace(150, 460)
            yModel = func(xModel, *fittedParameters)
            # now the model as a line plot
            ax_map[i].plot(xModel, yModel, color=hex_color_list[i], linestyle='dashed', linewidth=0.75)

        for ax in [ax1]:
            ax.tick_params(labelsize=self.cs['font_size'])

            ax.set_ylabel(f"T max (K)", size=self.cs['font_size'])  # .set_fontproperties(font)

            legend = ax.legend(loc="best",ncol=3, prop={'size': self.cs['font_size']})
            frame = legend.get_frame()  # sets up for color, edge, and transparency
            frame.set_edgecolor('black')  # edge color of legend
            frame.set_alpha(0)  # deals with transparency
            #ax.invert_xaxis()
            ax.set_xlim(460, 160)
            ax.set_xticks(np.arange(150, 500, 50))
            ax.set_ylim(30, 600)
            ax.set_yticks(np.arange(0, 650, 50))
        ax1.set_xlabel(f"I mag initial (A)", size=self.cs['font_size'])  # .set_fontproperties(font)

        fig.tight_layout()
        plt.subplots_adjust(bottom=0.13, right=0.92, top=0.97, left=0.17)
        # x0, x1, y0, y1 = plt.axis()
        # margin_x = 0.1 * (x1 - x0)
        # margin_y = 0.1 * (y1 - y0)
        # plt.axis((x0 - margin_x,
        #           x1 + margin_x,
        #           y0 - margin_y,
        #           y1 + margin_y))
        if not self.print_only:
            if self.save:
                out_dir = os.path.join(self.base_path, 'results-vs-time')
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{style}_Tmax_vs_I.svg'), dpi=300)
                # fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.png'), dpi=300)
            else:
                plt.show()
        plt.close()

    def plot_data_vs_time(self, plot_types):
        fig, (ax1) = plt.subplots(nrows=1, ncols=1, sharex=True,figsize=(self.cs['plot_width'], self.cs['plot_height']))
        # custom_font = {'fontname': "Times New Roman", 'size': self.cs['font_size']}
        # fontPath = r"C:\Windows\Fonts\times.ttf"
        # font = font_manager.FontProperties(fname=fontPath, size=6)

        for magnet_label, SampleData in self.magnet_dict.items():
            colormap = cm.get_cmap(self.colormaps[self.magnet_labels_list.index(magnet_label)])
            for plot_type in plot_types:
                if plot_type == 'percentiles':
                    n = 11  # change this value for the number of iterations/percentiles
                    percentiles = np.linspace(0, 100, n)
                    percentiles = np.array([2.5, 25, 50, 75, 97.5])     # or override percentiles like this
                    #percentiles = np.array([25, 50, 75])        # or like this
                    n = percentiles.shape[0]
                    d_p, nn_r = SampleData.shape
                    SDist = np.zeros((d_p, n))
                    for i in range(n):
                        for t in range(d_p):
                            SDist[t, i] = np.percentile(SampleData[t, :], percentiles[i])
                    half = int((n - 1) / 2)
                    for i in range(half):
                        label = f'{magnet_label} {(percentiles[-(i + 1)] - percentiles[i]):.0f} % CI'
                        #label = f'{magnet_label}'
                        color_rgba = colors.to_rgba(colormap(i / half + 1/half))
                        color_rgba_transp = (color_rgba[0], color_rgba[1], color_rgba[2], 0.5)
                        ax1.fill_between(self.time_dict[magnet_label], SDist[:, i], SDist[:, -(i + 1)], edgecolor=color_rgba_transp,
                                         color=color_rgba_transp, linewidth=0,
                                         label=label)
                        print(f'{magnet_label} percentile {i} temperature is: {np.max(SDist[:, i])} K')
                        print(f'{magnet_label} percentile {i+1} temperature is: {np.max(SDist[:, -(i + 1)])} K')
                    ax1.plot(self.time_dict[magnet_label], SDist[:, half], color='black', linewidth=0.6)

                    print(f'{magnet_label} median temperature is: {np.max(SDist[:, half])} K')
                elif plot_type == 'all_sim':
                    n_sim = SampleData.shape[1]
                    for i in range(n_sim):
                        print(f'Adding sim number: {self.sim_nr_dict[magnet_label][i]} to the plot')
                        if i == n_sim:
                            ax1.plot(self.time_dict[magnet_label], SampleData[:, i], color=colors.to_rgba(colormap((0.5*i) / n_sim+0.5)), label=f'{magnet_label}')
                        else:
                            ax1.plot(self.time_dict[magnet_label], SampleData[:, i], color=colors.to_rgba(colormap((0.5*i) / n_sim+0.5)))
                else:
                    raise ValueError(f'Plot plot_type: {plot_type} is not supported!')
        if self.print_only:
            for i in range(len(percentiles)):
                print(f'{magnet_label} percentile: {percentiles[i]} is: {SDist[-1, i]}')
        ax1.tick_params(labelsize=self.cs['font_size'])
        ax1.set_xlabel(f"{self.time_label} ({self.td['unit']})", size=self.cs['font_size'])#.set_fontproperties(font)
        ax1.set_ylabel(f"{value} ({self.cvd['unit']})", size=self.cs['font_size'])#.set_fontproperties(font)
        ymin, ymax = ax1.get_ylim()
        if self.cvd['op'] == 'min':
            ax1.set_ylim(ymin=ymin, ymax=0)  # set y limit to zero
        elif self.cvd['op'] == 'max':
            ax1.set_ylim(ymin=0, ymax=ymax)  # set y limit to zero
        ax1.set_xlim(self.td['min'], self.td['max'])
        legend = plt.legend(loc="best", prop={'size': self.cs['font_size']})
        frame = legend.get_frame()  # sets up for color, edge, and transparency
        frame.set_edgecolor('black')  # edge color of legend
        frame.set_alpha(0)  # deals with transparency
        #plt.legend.set_fontproperties(font)
        fig.tight_layout()
        if not self.print_only:
            if self.save:
                out_dir = os.path.join(self.base_path, 'results-vs-time')
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.svg'), dpi=300)
                #fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.png'), dpi=300)
            else:
                plt.show()
        plt.close()

    def plot_selected_vs_time(self):
        fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True,figsize=(self.cs['plot_width'], self.cs['plot_height']))
        for ax_i, (magnet_label, SampleData) in enumerate(self.magnet_dict.items()):
            colormap = cm.get_cmap(self.colormaps[self.magnet_labels_list.index(magnet_label)])
            ax = axs[ax_i]
            n_sim = SampleData.shape[1]
            for i in range(n_sim):
                print(f'Adding sim number: {self.sim_nr_dict[magnet_label][i]} to the plot')

                ax.plot(self.time_dict[magnet_label], SampleData[:, i], label=f'{magnet_label}')


            ax.tick_params(labelsize=self.cs['font_size'])
            ax.set_xlabel(f"{self.time_label} ({self.td['unit']})", size=self.cs['font_size'])#.set_fontproperties(font)
            ax.set_ylabel(f"{value} ({self.cvd['unit']})", size=self.cs['font_size'])#.set_fontproperties(font)
            ymin, ymax = ax.get_ylim()
            if self.cvd['op'] == 'min':
                ax.set_ylim(ymin=ymin, ymax=0)  # set y limit to zero
            elif self.cvd['op'] == 'max':
                ax.set_ylim(ymin=0, ymax=ymax)  # set y limit to zero
            ax.set_xlim(self.td['min'], self.td['max'])
        legend = plt.legend(loc="best", prop={'size': self.cs['font_size']})
        frame = legend.get_frame()  # sets up for color, edge, and transparency
        frame.set_edgecolor('black')  # edge color of legend
        frame.set_alpha(0)  # deals with transparency
        #plt.legend.set_fontproperties(font)
        fig.tight_layout()

        if self.save:
            out_dir = os.path.join(self.base_path, 'results-vs-time')
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.svg'), dpi=300)
            #fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.png'), dpi=300)
        else:
            plt.show()
        plt.close()

    def plot_b_and_w(self, hex_color_list):
        fig, axs = plt.subplots(ncols=3)

        data = []
        magnet_labels = []
        magnet_names =[]
        for magnet_label, SampleData in self.magnet_dict.items():
            if self.cvd['op']=='max':
                d = np.max(SampleData[:-1], axis=0).tolist()
            elif self.cvd['op']=='min':
                d = np.min(SampleData[:-1], axis=0).tolist()
            data.extend(d)
            FQPC_type = magnet_label.split(' ')[1]  # keep only the string after space
            magnet_type = magnet_label.split(' ')[0]  # keep only the string after space
            magnet_labels.extend([FQPC_type for _ in d])
            magnet_names.extend([magnet_type for _ in d])
            #magnet_labels.extend([magnet_label for _ in d])
        #u_magnet_names = np.unique(magnet_names).tolist()
        indexes = np.unique(magnet_names, return_index=True)[1]
        u_magnet_names= [magnet_names[index] for index in sorted(indexes)]
        # Set your custom color palette
        for i, u_mag_name in enumerate(u_magnet_names):
            sns.set_palette(sns.color_palette(hex_color_list))
            trim_mask = np.where(np.array(magnet_names) == u_mag_name)[0]
            data_trimmed = np.array(data)[trim_mask]
            magnet_labels_trimmed = np.array(magnet_labels)[trim_mask]
            df = pd.DataFrame.from_dict({self.value: data_trimmed, 'magnet': magnet_labels_trimmed})
            flierprops = dict(markerfacecolor='0.75', markersize=1, linestyle='none')
            #plt.axhline(y=0, color='lightblue', linestyle='-', linewidth=0.5)
            for _, hex_color in zip(magnet_labels, hex_color_list):
                a = sns.boxplot(x='magnet', y=self.value, data=df, ax=axs[i], flierprops=flierprops, linewidth=0.5, showfliers=False, whis=[2.5, 97.5])  # , palette="Set3")
                a.set_xlabel('', fontsize=6)
                a.set_ylabel(self.value, fontsize=6)
                a.tick_params(labelsize=6)
            axs[i].set_xlabel(u_mag_name, fontweight='normal', fontsize=6)
            axs[i].yaxis.label.set_visible(i==0)
        fig.tight_layout()
        if self.save:
            out_dir = os.path.join(self.base_path, 'b&w_multi')
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            #plt.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_b&w.png'), dpi=300)
            plt.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_b&w.svg'), dpi=300)
        else:
            plt.show()
        plt.close()


if __name__ == "__main__":
    base_path = r"D:\FQPC_LEDET_folder\LEDET"   # path to ledet folder
    base_magnet_name = 'MCBRD'
    styles = ["poster", 'publication']
    styles = ['publication']
    plot_types = ['percentiles', 'all_sim']
    plot_types = ['percentiles']

    # m30 = ['M30 0']
    # s30 = [list(range(30001, 30009, 1))]

    m30 = ['M30 0', 'M30 1O', 'M30 1A', 'M30 2A']
    s30 = [list(range(30001, 30049, 1)), list(range(30101, 30149, 1)), list(range(30201, 30249, 1)), list(range(30401, 30449, 1))]

    # m30_curr = ['M30 0',
    #             'M30 1O',
    #             'M30 1A',
    #             'M30 2A']
    # s30_curr = [[31001, 32001, 33001, 34001, 35001, 36001, 37001, 38001, 39001],
    #             [31101, 32101, 33101, 34101, 35101, 36101, 37101, 38101, 39101],
    #             [31201, 32201, 33201, 34201, 35201, 36201, 37201, 38201, 39201],
    #             [31401, 32401, 33401, 34401, 35401, 36401, 37401, 38401, 39401]]
    #
    # m30_curr = ['M30 0',
    #             'M30 1O',
    #             'M30 1A',
    #             'M30 2A']
    # s30_curr = [[31001, 32001, 33001, 34001, 35001, 36001],
    #             [31101, 32101, 33101, 34101, 35101, 36101],
    #             [31201, 32201, 33201, 34201, 35201, 36201],
    #             [31401, 32401, 33401, 34401, 35401, 36401]]
    #
    # m100_curr = ['M100 0',
    #             'M100 1O',
    #             'M100 1A',
    #             'M100 2A']
    # s100_curr = [[101001, 102001, 103001, 104001, 105001, 106001, 107001, 108001, 109001],
    #             [101101, 102101, 103101, 104101, 105101, 106101, 107101, 108101, 109101],
    #             [101201, 102201, 103201, 104201, 105201, 106201, 107201, 108201, 109201],
    #             [101401, 102401, 103401, 104401, 105401, 106401, 107401, 108401, 109401]]
    #
    # m100_curr = ['M100 0',
    #             'M100 1O',
    #             'M100 1A',
    #             'M100 2A']
    # s100_curr = [[101001, 102001, 103001, 104001, 105001, 106001, 107001],
    #             [101101, 102101, 103101, 104101, 105101, 106101, 107101],
    #             [101201, 102201, 103201, 104201, 105201, 106201, 107201],
    #             [101401, 102401, 103401, 104401, 105401, 106401, 107401]]
    #
    # m200_curr = ['M200 0',
    #              'M200 1O',
    #              'M200 1A',
    #              'M200 2A']
    # s200_curr = [[201001, 202001, 203001, 204001, 205001, 206001, 207001, 208001, 209001],
    #             [201101, 202101, 203101, 204101, 205101, 206101, 207101, 208101, 209101],
    #             [201201, 202201, 203201, 204201, 205201, 206201, 207201, 208201, 209201],
    #             [201401, 202401, 203401, 204401, 205401, 206401, 207401, 208401, 209401]]
    #
    # m200_curr = ['M200 0',
    #              'M200 1O',
    #              'M200 1A',
    #              'M200 2A']
    # s200_curr = [[201001, 202001, 203001, 204001, 205001, 206001, 207001],
    #             [201101, 202101, 203101, 204101, 205101, 206101, 207101],
    #             [201201, 202201, 203201, 204201, 205201, 206201, 207201],
    #             [201401, 202401, 203401, 204401, 205401, 206401, 207401]]

    m30 = ['M30 0', 'M30 1O', 'M30 1A', 'M30 2A']
    s30 = [list(range(30001, 30049, 1)), list(range(30101, 30149, 1)), list(range(30201, 30249, 1)), list(range(30401, 30449, 1))]

    # to_remove = [30416, 30421, 30426, 30431, 30436, 30439, 30444]
    #
    # for m_list in s30:
    #     for r in to_remove:
    #         try:
    #             m_list.remove(r)
    #         except ValueError:
    #             pass

    m100 = ['M100 0', 'M100 1O', 'M100 1A', 'M100 2A']
    s100 = [list(range(100001, 100049, 1)), list(range(100101, 100149, 1)), list(range(100201, 100249, 1)), list(range(100401, 100449, 1))]

    m200 = ['M200 0', 'M200 1O', 'M200 1A', 'M200 2A']
    s200 = [list(range(200001, 200049, 1)), list(range(200101, 200149, 1)), list(range(200201, 200249, 1)), list(range(200401, 200449, 1))]

    #m200 = ['M200 0', 'M200 2A']
    #s200 = [list(range(200001, 200049, 1)), list(range(200401, 200449, 1))]

    hex_color_list = ['#80A28D', '#8498B5', '#BF9382', '#9F80BE', '#80A28D', '#8498B5', '#BF9382', '#9F80BE', '#80A28D', '#8498B5', '#BF9382', '#9F80BE']
    #hex_color_list = ['#80A28D', '#80A28D','#80A28D','#80A28D', '#8498B5', '#8498B5', '#8498B5', '#8498B5', '#BF9382', '#BF9382', '#BF9382', '#BF9382']
    magnet_labels_list = m30 + m100 + m200
    sim_nr_list_of_lists = s30 + s100 + s200

    #magnet_labels_list = ['M200 0', 'M200 2A']
    #sim_nr_list_of_lists = [[200018], [200418]]
    # magnet_labels_list =[m30[0], m100[1], m200[2]]
    # sim_nr_list_of_lists = [s30[0], s100[1], s200[2]]
    #magnet_labels_list = m30
    #sim_nr_list_of_lists = s30
    # magnet_labels_list = m100
    # sim_nr_list_of_lists = s100
    #magnet_labels_list = m200
    #sim_nr_list_of_lists = s200
    #
    #
    # magnet_labels_list = m30_curr
    # sim_nr_list_of_lists = s30_curr
    # # magnet_labels_list = m100_curr
    # # sim_nr_list_of_lists = s100_curr
    # # magnet_labels_list = m200_curr
    # # sim_nr_list_of_lists = s200_curr
    # magnet_labels_list = m30_curr+m100_curr+m200_curr
    # sim_nr_list_of_lists = s30_curr+s100_curr+s200_curr

    values = ['T max', 'I mag', 'U max', 'U min']
    #values = ['T max', 'U max', 'U min']
    values = ['I mag', 'T max']
    values = ['U max', 'U min']
    #values = ['T max', 'R mag', 'I mag']
    values = ['T max']

    for style in styles:
        for value in values:
            pp = PlotterParametric(base_path, base_magnet_name, magnet_labels_list, sim_nr_list_of_lists, style, value, save=True, print_only=False)
            pass
            #pp.plot_data_vs_time(plot_types=plot_types)
            #pp.plot_selected_vs_time()
            pp.plot_b_and_w(hex_color_list)
            #pp.plt_T_vs_I(hex_color_list)
