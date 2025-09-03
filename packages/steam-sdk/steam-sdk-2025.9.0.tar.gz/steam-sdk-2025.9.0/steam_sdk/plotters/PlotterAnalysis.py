import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from steam_sdk.parsers.ParserMat import Parser_LEDET_Mat
from matplotlib.ticker import FuncFormatter

class PlotterAnalysis:
    def __init__(self, base_path):
        self.base_path = base_path

        self.__values_dict = {
            #'Time': {'mat_label': 'time_vector', 'op': None, 'min': -0.05, 'max': 0.2, 'unit': 's'},
            'Time': {'mat_label': 'time_vector', 'op': None, 'min': -0.01, 'max': 3.5, 'unit': 's'},
            'Time adb': {'mat_label': 'time_vector_hs', 'op': None, 'min': -0.05, 'max': 3.5, 'unit': 's'},
            '$T_{max}$': {'mat_label': 'T_ht', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'K'},
            '$T_{max adb}$': {'mat_label': 'T_hs', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'K'},
            '$I_{A}$': {'mat_label': 'Ia', 'op': None, 'min': 0, 'max': 200, 'unit': 'A'},
            '$I_{B}$': {'mat_label': 'Ib', 'op': None, 'min': 0, 'max': 200, 'unit': 'A'},
            '$I_{CLIQ}$': {'mat_label': 'Ic', 'op': None, 'min': 0, 'max': 200, 'unit': 'A'},
            '$U_{max}$': {'mat_label': 'Uground_half_turns', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'V'},
            '$U_{min}$': {'mat_label': 'Uground_half_turns', 'op': 'min', 'min': 0, 'max': 200, 'unit': 'V'},
            '$R_{mag}$': {'mat_label': 'R_CoilSections', 'op': 'max', 'min': 0, 'max': 200, 'unit': 'Ohm'},
            '$U_{GND MAX}$': {'mat_label': 'Uturn_half_turns', 'op': None, 'min': 0, 'max': 200, 'unit': 'V'},
        }

    def set_plot_style(self, style):

        styles_dict = {
            'poster': {'plot_width': 1.9*8.9/2.54, 'plot_height': 3.2*6.2/2.54, 'font_size': 24},
            'publication': {'plot_width': 8.9/2.54, 'plot_height': 4/2.54, 'font_size': 5},
            'presentation': {'plot_width': 7 / 2.54, 'plot_height': 8 / 2.54, 'font_size': 10}
        }
        self.cs = styles_dict[style]

    def read_sweep(self, input_sweep_file, case, x_var_name, y_var_name):
        df = pd.read_csv(input_sweep_file)
        case_values = df.loc[df['comments'] == case]
        self.sim_numbers = case_values['simulation_number'].tolist()
        self.x_var_vals = case_values[x_var_name].tolist()
        self.y_var_vals = case_values[y_var_name].tolist()

    def plot_sweep_2d(self, model_name, x_var_name, y_var_name, z_var_name):
        plt.style.use('_mpl-gallery-nogrid')



        if x_var_name == 'Power_Supply.I_initial':
            x_label = 'Magnet Initial Current (kA)'
            x_multip = 0.001
        else:
            x_label = x_var_name
            x_multip = 1
        if y_var_name == 'Quench_Protection.CLIQ.C':
            y_label = 'CLIQ Unit Capacitance (mF)'
            y_multip = 1000
        else:
            y_label = y_var_name
            y_multip = 1

        if z_var_name == '$I_{CLIQ}$':
            z_label = z_var_name + ' (kA)'
            z_multip = 0.001
            format_str = '{:.2f}'
        elif z_var_name == '$U_{max}$':
            z_label = z_var_name + ' (kV)'
            z_multip = 0.001
            format_str = '{:.2f}'
        elif z_var_name == '$T_{max adb}$':
            z_label = z_var_name + ' (K)'
            z_multip = 1
            format_str = '{:.0f}'
        else:
            z_label = z_var_name
            z_multip = 1

        x = np.array(self.x_var_vals) * x_multip
        y = np.array(self.y_var_vals) * y_multip
        z = []

        for sim_nr in self.sim_numbers:
            self.cvd = self.__values_dict[z_var_name]
            mat_file_obj = Parser_LEDET_Mat(self.base_path, model_name, sim_nr)
            #self.time_data[magnet_label][self.time_name][sim_nr] = mat_file_obj.data_1D(self.td['mat_label'], op=None)
            data = mat_file_obj.data_1D(self.cvd['mat_label'], op=self.cvd['op'])
            # - uncomment this commented out block of code to limit data
            max_data = np.max(data)
            manual_z_max = False
            if manual_z_max:
                if max_data >300:
                    max_data = 300
                z.append(max_data)
            else:
                z.append(max_data)
        z = np.array(z) * z_multip
        #vmax = z.max()
        #levels = np.linspace(z.min(), vmax, 12)


        if model_name == 'robust_12T_50_mm_MQXF_cable_5_blocks_V2':
            model_label = '50mm,5b'
            x_max_lim = 18
        elif model_name == 'robust_12T_50_mm_MQXF_cable_6_blocks_V2':
            model_label = '50mm,6b'
            x_max_lim = 18
        elif model_name == 'robust_12T_56_mm_MQXF_cable_6_blocks_V2':
            model_label = '56mm,6b'
            x_max_lim = 17



        xm = np.ma.masked_where(x_max_lim < x , x)
        x = x[~xm.mask].copy()
        y = y[~xm.mask].copy()
        z = z[~xm.mask].copy()

        y_min_lim = 5

        ym = np.ma.masked_where(y_min_lim> y, y)
        x = x[~ym.mask].copy()
        y = y[~ym.mask].copy()
        z = z[~ym.mask].copy()

        levels = np.linspace(z.min(), z.max(), 12)
        # plot:
        fig, ax = plt.subplots(figsize=(self.cs['plot_width'], self.cs['plot_height']))

        ax.plot(x, y, 'o', markersize=2, color='grey')
        sc = ax.tricontourf(x, y, z, levels=levels, vmin=z.min(), vmax=z.max())
        #sc = ax.contourf(x, y, z, levels=levels, vmin=z.min(), vmax=vmax)

        offset = 0.1
        x_offset = offset * x.min()
        y_offset = offset * y.min()
        manual_y_lim = False
        if manual_y_lim:
            y_min = 0.004
        else:
            y_min = y.min()-y_offset



        ax.set(xlim=(x.min()-x_offset, x.max()+x_offset), ylim=(y_min, y.max()+y_offset))


        fmt = lambda x, pos: format_str.format(x)
        cbar = fig.colorbar(sc, format=FuncFormatter(fmt))
        #cbar = fig.colorbar(sc)

        cbar.set_label(f'{z_label} max = {z.max():.2f}')

        plt.xlabel(x_label)
        plt.ylabel(y_label)


        plt.title(label=model_label,
                 fontweight=10,
                 pad='2.0')

        fig.tight_layout()
        fig.savefig(os.path.join(r'E:\Python\m12t_r\plots', f'{model_label}_{z_label}.svg'), dpi=300)
        plt.show()

    def read_data(self, model_names, model_labels, sim_nr_list_of_lists, values, el_order_lookup=None):
        self.names = ''
        self.numbers = ''
        self.data = {}
        self.time_data = {}
        self.plot_x_el_order = {}
        self.values = values
        for magnet_name, magnet_label, sim_nr_list in zip(model_names, model_labels, sim_nr_list_of_lists):
            self.data[magnet_label] = {}
            self.plot_x_el_order[magnet_label] = {}
            self.names += f'{magnet_name},'
            for value in values:
                if value == '$T_{max adb}$':
                    self.time_name = 'Time adb'
                else:
                    self.time_name = 'Time'
                self.td = self.__values_dict[self.time_name]
                self.cvd = self.__values_dict[value]
                self.time_data[magnet_label] = {self.time_name: {}}
                self.data[magnet_label][value] = {}
                self.plot_x_el_order[magnet_label]['plot_x'] = {}
                for sim_nr in sim_nr_list:
                    self.numbers += f'{sim_nr},'
                    mat_file_obj = Parser_LEDET_Mat(self.base_path, magnet_name, sim_nr)
                    self.time_data[magnet_label][self.time_name][sim_nr] = mat_file_obj.data_1D(self.td['mat_label'], op=None)
                    if value == '$U_{GND MAX}$':
                        dict_order = el_order_lookup[magnet_name]
                        self.data[magnet_label][value][sim_nr] = {}
                        self.plot_x_el_order[magnet_label]['plot_x'][sim_nr] = {}
                        for order_label, order_list in dict_order.items():
                            plot_x, Umax_gnd_half_turns = self._U_gnd_turns(mat_file_obj, order_list)
                            self.data[magnet_label][value][sim_nr][order_label] = Umax_gnd_half_turns
                            self.plot_x_el_order[magnet_label]['plot_x'][sim_nr][order_label] = plot_x
                    else:
                        self.data[magnet_label][value][sim_nr] = mat_file_obj.data_1D(self.cvd['mat_label'], op=self.cvd['op'])

    def _U_gnd_turns(self, mat_file_obj, order_list):
        Uturn_half_turns = mat_file_obj.data_2D('Uturn_half_turns').T
        #el_order_half_turns = mat_file_obj.data_1D('el_order_half_turns').astype(int) - 1
        order_list = np.array(order_list, dtype='int')-1
        Uturn_half_turns_reordered = Uturn_half_turns[:, order_list]
        Uground_half_turns = np.fliplr(np.cumsum(np.fliplr(Uturn_half_turns_reordered), axis=1))
        #Umax_gnd_half_turns = Uground_half_turns.min(axis=0)
        Umax_gnd_half_turns = np.amax(np.abs(Uground_half_turns), axis=0)
        plot_x = []
        for i, v in enumerate(order_list):
            plot_x.append(i)
        plot_x = np.array(plot_x)
        return plot_x, Umax_gnd_half_turns

    def plot_selected_vs_el_order(self, use_markers=False, save=False):
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(self.cs['plot_width'], self.cs['plot_height']))
        markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
        i = 0
        sim_names = {
            1: 'oQH', 2: 'iQH', 3: 'CLIQu', 13: 'CLIQi', 4: 'iQH&CLIQu', 14: 'iQH&CLIQi', 5: 'i&oQH', 6: 'oQH&CLIQu', 16: 'oQH&CLIQi', 7: 'o&iQH&CLIQu', 17: 'o&iQH&CLIQi',
            101: 'oQH', 102: 'iQH', 103: 'CLIQu', 113: 'CLIQi', 104: 'iQH&CLIQu', 114: 'iQH&CLIQi', 105: 'i&oQH', 106: 'oQH&CLIQu', 116: 'oQH&CLIQi', 107: 'o&iQH&CLIQu', 117: 'o&iQH&CLIQi'}

        out_dir = os.path.join(self.base_path, 'PlotterAnalysis')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        csv_file_path = os.path.join(out_dir, f'summary.csv')
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            #writer.writerow(['magnet_label', 'sim_nr', 'el_order', 'max V'])
            for magnet_label, magnet_data in self.data.items():
                for value, value_dict in magnet_data.items():
                    for sim_nr, sim_data in value_dict.items():
                        if sim_nr>100:
                            leng = 'L_'
                        else:
                            leng = 'S_'
                        if use_markers:     # user
                            marker = markers[i]
                        else:
                            marker = 'None'
                        if len(self.values) == 3:
                            label = f'{magnet_label},{value}:{leng + sim_names[sim_nr]}'
                        else:
                            #label = f'{magnet_label}:{leng + sim_names[sim_nr]}'
                            label = f'{sim_nr}'
                        offset = 0
                        ls=['-','--','-.',':']
                        for key, plot_x in self.plot_x_el_order[magnet_label]['plot_x'][sim_nr].items():
                            max_v = round(np.max(self.data[magnet_label][value][sim_nr][key]), 0)
                            ax.plot(plot_x, self.data[magnet_label][value][sim_nr][key], label=f'{key}-{max_v}', linestyle=ls[offset], marker=marker, markevery=5)
                            offset +=1
                            data = [magnet_label, sim_nr, key, max_v]
                            writer.writerow(data)
                        i += 1
                        data = [magnet_label, sim_nr, ]
        ax.tick_params(labelsize=self.cs['font_size'])
        ax.set_xlabel(f"Half-turn number in el. order", size=self.cs['font_size'])#.set_fontproperties(font)
        if len(self.values) == 3:   # CLIQ currents plot
            value = '$I_{A}, I_{B}, I_{CLIQ}$'
        ax.set_ylabel(f"{value} ({self.cvd['unit']})", size=self.cs['font_size'])#.set_fontproperties(font)
        ymin, ymax = ax.get_ylim()
        if self.cvd['op'] == 'min':
            ax.set_ylim(ymin=ymin, ymax=0)  # set y limit to zero
        elif self.cvd['op'] == 'max':
            ax.set_ylim(ymin=0, ymax=ymax)  # set y limit to zero
        #ax.set_xlim(self.td['min'], self.td['max'])
        legend = plt.legend(loc="best", prop={'size': self.cs['font_size']})
        frame = legend.get_frame()  # sets up for color, edge, and transparency
        frame.set_edgecolor('black')  # edge color of legend
        frame.set_alpha(0)  # deals with transparency
        #plt.legend.set_fontproperties(font)
        fig.tight_layout()
        if save:
            fig.savefig(os.path.join(out_dir, f'{self.names}_{self.numbers}_{value}.png'), dpi=300)
            #fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.png'), dpi=300)
        else:
            plt.show()
        plt.close()


    def plot_selected_vs_time(self, use_markers=False, save=False, print_only=False):
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(self.cs['plot_width'], self.cs['plot_height']))
        markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
        i = 0
        sim_names = {
            1: 'oQH', 2: 'iQH', 3: 'CLIQu', 13: 'CLIQi', 4: 'iQH&CLIQu', 14: 'iQH&CLIQi', 5: 'i&oQH', 6: 'oQH&CLIQu', 16: 'oQH&CLIQi', 7: 'o&iQH&CLIQu', 17: 'o&iQH&CLIQi',
            101: 'oQH', 102: 'iQH', 103: 'CLIQu', 113: 'CLIQi', 104: 'iQH&CLIQu', 114: 'iQH&CLIQi', 105: 'i&oQH', 106: 'oQH&CLIQu', 116: 'oQH&CLIQi', 107: 'o&iQH&CLIQu', 117: 'o&iQH&CLIQi'}

        for magnet_label, magnet_data in self.data.items():
            for value, value_dict in magnet_data.items():
                for sim_nr, sim_data in value_dict.items():
                    if sim_nr>100:
                        leng = 'L_'
                    else:
                        leng = 'S_'
                    if use_markers:     # user
                        marker = markers[i]
                    else:
                        marker = 'None'
                    if len(self.values) == 3:
                        label = f'{magnet_label},{value}:{leng + sim_names[sim_nr]}'
                    else:
                        #label = f'{magnet_label}:{leng + sim_names[sim_nr]}'
                        label = f'{sim_nr}'
                    ax.plot(self.time_data[magnet_label][self.time_name][sim_nr], self.data[magnet_label][value][sim_nr],
                            markevery=20, marker=marker, label=label)
                    i += 1
        ax.tick_params(labelsize=self.cs['font_size'])
        ax.set_xlabel(f"Time (s)", size=self.cs['font_size'])#.set_fontproperties(font)
        if len(self.values) == 3:   # CLIQ currents plot
            value = '$I_{A}, I_{B}, I_{CLIQ}$'
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
        if save:
            out_dir = os.path.join(self.base_path, 'PlotterAnalysis')
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            fig.savefig(os.path.join(out_dir, f'{self.names}_{self.numbers}_{value}.svg'), dpi=300)
            #fig.savefig(os.path.join(out_dir, f'{"+".join(self.magnet_labels_list)}_{value}_{style}_{plot_type}.png'), dpi=300)
        else:
            plt.show()
        plt.close()

    def print_data(self):
        print(self.data)

if __name__ == "__main__":
    base_path = r"D:\tempLEDET\LEDET"   # path to ledet folder
    # model_names_list = [['robust_12T_50_mm_MQXF_cable_5_blocks_V2'], ['robust_12T_50_mm_MQXF_cable_6_blocks_V2'], ['robust_12T_56_mm_MQXF_cable_6_blocks_V2']]
    # model_labels_list = [['50mm,5b'], ['50mm,6b'], ['56mm,6b']]

    el_order_lookup = {
        'robust_12T_50_mm_MQXF_cable_5_blocks_V2': {
            '#1': [1, 75, 2, 76, 3, 77, 4, 78, 5, 79, 6, 80, 7, 81, 8, 82, 9, 83, 10, 84, 11, 85, 12, 86, 13, 87, 14, 88, 15, 89, 16, 90, 17, 91, 18, 92, 19, 93, 20, 94, 21, 95, 22, 96, 37, 111, 36, 110, 35, 109, 34, 108, 33, 107, 32, 106, 31, 105, 30, 104, 29, 103, 28, 102, 27, 101, 26, 100, 25, 99, 24, 98, 23, 97, 112, 38, 113, 39, 114, 40, 115, 41, 116, 42, 117, 43, 118, 44, 119, 45, 120, 46, 121, 47, 122, 48, 123, 49, 124, 50, 125, 51, 126, 52, 127, 53, 128, 54, 129, 55, 130, 56, 131, 57, 132, 58, 133, 59, 148, 74, 147, 73, 146, 72, 145, 71, 144, 70, 143, 69, 142, 68, 141, 67, 140, 66, 139, 65, 138, 64, 137, 63, 136, 62, 135, 61, 134, 60],
            '#2': [23, 97, 24, 98, 25, 99, 26, 100, 27, 101, 28, 102, 29, 103, 30, 104, 31, 105, 32, 106, 33, 107, 34, 108, 35, 109, 36, 110, 37, 111, 22, 96, 21, 95, 20, 94, 19, 93, 18, 92, 17, 91, 16, 90, 15, 89, 14, 88, 13, 87, 12, 86, 11, 85, 10, 84, 9, 83, 8, 82, 7, 81, 6, 80, 5, 79, 4, 78, 3, 77, 2, 76, 1, 75, 134, 60, 135, 61, 136, 62, 137, 63, 138, 64, 139, 65, 140, 66, 141, 67, 142, 68, 143, 69, 144, 70, 145, 71, 146, 72, 147, 73, 148, 74, 133, 59, 132, 58, 131, 57, 130, 56, 129, 55, 128, 54, 127, 53, 126, 52, 125, 51, 124, 50, 123, 49, 122, 48, 121, 47, 120, 46, 119, 45, 118, 44, 117, 43, 116, 42, 115, 41, 114, 40, 113, 39, 112, 38],
            '#3': [1, 75, 2, 76, 3, 77, 4, 78, 5, 79, 6, 80, 7, 81, 8, 82, 9, 83, 10, 84, 11, 85, 12, 86, 13, 87, 14, 88, 15, 89, 16, 90, 17, 91, 18, 92, 19, 93, 20, 94, 21, 95, 22, 96, 37, 111, 36, 110, 35, 109, 34, 108, 33, 107, 32, 106, 31, 105, 30, 104, 29, 103, 28, 102, 27, 101, 26, 100, 25, 99, 24, 98, 23, 97, 134, 60, 135, 61, 136, 62, 137, 63, 138, 64, 139, 65, 140, 66, 141, 67, 142, 68, 143, 69, 144, 70, 145, 71, 146, 72, 147, 73, 148, 74, 133, 59, 132, 58, 131, 57, 130, 56, 129, 55, 128, 54, 127, 53, 126, 52, 125, 51, 124, 50, 123, 49, 122, 48, 121, 47, 120, 46, 119, 45, 118, 44, 117, 43, 116, 42, 115, 41, 114, 40, 113, 39, 112, 38],
            '#4': [23, 97, 24, 98, 25, 99, 26, 100, 27, 101, 28, 102, 29, 103, 30, 104, 31, 105, 32, 106, 33, 107, 34, 108, 35, 109, 36, 110, 37, 111, 22, 96, 21, 95, 20, 94, 19, 93, 18, 92, 17, 91, 16, 90, 15, 89, 14, 88, 13, 87, 12, 86, 11, 85, 10, 84, 9, 83, 8, 82, 7, 81, 6, 80, 5, 79, 4, 78, 3, 77, 2, 76, 1, 75, 112, 38, 113, 39, 114, 40, 115, 41, 116, 42, 117, 43, 118, 44, 119, 45, 120, 46, 121, 47, 122, 48, 123, 49, 124, 50, 125, 51, 126, 52, 127, 53, 128, 54, 129, 55, 130, 56, 131, 57, 132, 58, 133, 59, 148, 74, 147, 73, 146, 72, 145, 71, 144, 70, 143, 69, 142, 68, 141, 67, 140, 66, 139, 65, 138, 64, 137, 63, 136, 62, 135, 61, 134, 60]
        },
        'robust_12T_50_mm_MQXF_cable_6_blocks_V2': {
            '#1': [1, 75, 2, 76, 3, 77, 4, 78, 5, 79, 6, 80, 7, 81, 8, 82, 9, 83, 10, 84, 11, 85, 12, 86, 13, 87, 14, 88, 15, 89, 16, 90, 17, 91, 18, 92, 19, 93, 20, 94, 21, 95, 22, 96, 37, 111, 36, 110, 35, 109, 34, 108, 33, 107, 32, 106, 31, 105, 30, 104, 29, 103, 28, 102, 27, 101, 26, 100, 25, 99, 24, 98, 23, 97, 112, 38, 113, 39, 114, 40, 115, 41, 116, 42, 117, 43, 118, 44, 119, 45, 120, 46, 121, 47, 122, 48, 123, 49, 124, 50, 125, 51, 126, 52, 127, 53, 128, 54, 129, 55, 130, 56, 131, 57, 132, 58, 133, 59, 148, 74, 147, 73, 146, 72, 145, 71, 144, 70, 143, 69, 142, 68, 141, 67, 140, 66, 139, 65, 138, 64, 137, 63, 136, 62, 135, 61, 134, 60],
            '#2': [23, 97, 24, 98, 25, 99, 26, 100, 27, 101, 28, 102, 29, 103, 30, 104, 31, 105, 32, 106, 33, 107, 34, 108, 35, 109, 36, 110, 37, 111, 22, 96, 21, 95, 20, 94, 19, 93, 18, 92, 17, 91, 16, 90, 15, 89, 14, 88, 13, 87, 12, 86, 11, 85, 10, 84, 9, 83, 8, 82, 7, 81, 6, 80, 5, 79, 4, 78, 3, 77, 2, 76, 1, 75, 134, 60, 135, 61, 136, 62, 137, 63, 138, 64, 139, 65, 140, 66, 141, 67, 142, 68, 143, 69, 144, 70, 145, 71, 146, 72, 147, 73, 148, 74, 133, 59, 132, 58, 131, 57, 130, 56, 129, 55, 128, 54, 127, 53, 126, 52, 125, 51, 124, 50, 123, 49, 122, 48, 121, 47, 120, 46, 119, 45, 118, 44, 117, 43, 116, 42, 115, 41, 114, 40, 113, 39, 112, 38],
            '#3': [1, 75, 2, 76, 3, 77, 4, 78, 5, 79, 6, 80, 7, 81, 8, 82, 9, 83, 10, 84, 11, 85, 12, 86, 13, 87, 14, 88, 15, 89, 16, 90, 17, 91, 18, 92, 19, 93, 20, 94, 21, 95, 22, 96, 37, 111, 36, 110, 35, 109, 34, 108, 33, 107, 32, 106, 31, 105, 30, 104, 29, 103, 28, 102, 27, 101, 26, 100, 25, 99, 24, 98, 23, 97, 134, 60, 135, 61, 136, 62, 137, 63, 138, 64, 139, 65, 140, 66, 141, 67, 142, 68, 143, 69, 144, 70, 145, 71, 146, 72, 147, 73, 148, 74, 133, 59, 132, 58, 131, 57, 130, 56, 129, 55, 128, 54, 127, 53, 126, 52, 125, 51, 124, 50, 123, 49, 122, 48, 121, 47, 120, 46, 119, 45, 118, 44, 117, 43, 116, 42, 115, 41, 114, 40, 113, 39, 112, 38],
            '#4': [23, 97, 24, 98, 25, 99, 26, 100, 27, 101, 28, 102, 29, 103, 30, 104, 31, 105, 32, 106, 33, 107, 34, 108, 35, 109, 36, 110, 37, 111, 22, 96, 21, 95, 20, 94, 19, 93, 18, 92, 17, 91, 16, 90, 15, 89, 14, 88, 13, 87, 12, 86, 11, 85, 10, 84, 9, 83, 8, 82, 7, 81, 6, 80, 5, 79, 4, 78, 3, 77, 2, 76, 1, 75, 112, 38, 113, 39, 114, 40, 115, 41, 116, 42, 117, 43, 118, 44, 119, 45, 120, 46, 121, 47, 122, 48, 123, 49, 124, 50, 125, 51, 126, 52, 127, 53, 128, 54, 129, 55, 130, 56, 131, 57, 132, 58, 133, 59, 148, 74, 147, 73, 146, 72, 145, 71, 144, 70, 143, 69, 142, 68, 141, 67, 140, 66, 139, 65, 138, 64, 137, 63, 136, 62, 135, 61, 134, 60]
        },
        'robust_12T_56_mm_MQXF_cable_6_blocks_V2': {
            '#1': [1, 83, 2, 84, 3, 85, 4, 86, 5, 87, 6, 88, 7, 89, 8, 90, 9, 91, 10, 92, 11, 93, 12, 94, 13, 95, 14, 96, 15, 97, 16, 98, 17, 99, 18, 100, 19, 101, 20, 102, 21, 103, 22, 104, 23, 105, 24, 106, 41, 123, 40, 122, 39, 121, 38, 120, 37, 119, 36, 118, 35, 117, 34, 116, 33, 115, 32, 114,
                   31, 113, 30, 112, 29, 111, 28, 110, 27, 109, 26, 108, 25, 107, 124, 42, 125, 43, 126, 44, 127, 45, 128, 46, 129, 47, 130, 48, 131, 49, 132, 50, 133, 51, 134, 52, 135, 53, 136, 54, 137, 55, 138, 56, 139, 57, 140, 58, 141, 59, 142, 60, 143, 61, 144, 62, 145, 63, 146, 64, 147, 65,
                   164, 82, 163, 81, 162, 80, 161, 79, 160, 78, 159, 77, 158, 76, 157, 75, 156, 74, 155, 73, 154, 72, 153, 71, 152, 70, 151, 69, 150, 68, 149, 67, 148, 66],
            '#2': [25, 107, 26, 108, 27, 109, 28, 110, 29, 111, 30, 112, 31, 113, 32, 114, 33, 115, 34, 116, 35, 117, 36, 118, 37, 119, 38, 120, 39, 121, 40, 122, 41, 123, 24, 106, 23, 105, 22, 104, 21, 103, 20, 102, 19, 101, 18, 100, 17, 99, 16, 98, 15, 97, 14, 96, 13, 95, 12, 94, 11, 93, 10, 92,
                   9, 91, 8, 90, 7, 89, 6, 88, 5, 87, 4, 86, 3, 85, 2, 84, 1, 83, 148, 66, 149, 67, 150, 68, 151, 69, 152, 70, 153, 71, 154, 72, 155, 73, 156, 74, 157, 75, 158, 76, 159, 77, 160, 78, 161, 79, 162, 80, 163, 81, 164, 82, 147, 65, 146, 64, 145, 63, 144, 62, 143, 61, 142, 60, 141, 59,
                   140, 58, 139, 57, 138, 56, 137, 55, 136, 54, 135, 53, 134, 52, 133, 51, 132, 50, 131, 49, 130, 48, 129, 47, 128, 46, 127, 45, 126, 44, 125, 43, 124, 42],
            '#3': [1, 83, 2, 84, 3, 85, 4, 86, 5, 87, 6, 88, 7, 89, 8, 90, 9, 91, 10, 92, 11, 93, 12, 94, 13, 95, 14, 96, 15, 97, 16, 98, 17, 99, 18, 100, 19, 101, 20, 102, 21, 103, 22, 104, 23, 105, 24, 106, 41, 123, 40, 122, 39, 121, 38, 120, 37, 119, 36, 118, 35, 117, 34, 116, 33, 115, 32, 114,
                   31, 113, 30, 112, 29, 111, 28, 110, 27, 109, 26, 108, 25, 107, 148, 66, 149, 67, 150, 68, 151, 69, 152, 70, 153, 71, 154, 72, 155, 73, 156, 74, 157, 75, 158, 76, 159, 77, 160, 78, 161, 79, 162, 80, 163, 81, 164, 82, 147, 65, 146, 64, 145, 63, 144, 62, 143, 61, 142, 60, 141, 59,
                   140, 58, 139, 57, 138, 56, 137, 55, 136, 54, 135, 53, 134, 52, 133, 51, 132, 50, 131, 49, 130, 48, 129, 47, 128, 46, 127, 45, 126, 44, 125, 43, 124, 42],
            '#4': [25, 107, 26, 108, 27, 109, 28, 110, 29, 111, 30, 112, 31, 113, 32, 114, 33, 115, 34, 116, 35, 117, 36, 118, 37, 119, 38, 120, 39, 121, 40, 122, 41, 123, 24, 106, 23, 105, 22, 104, 21, 103, 20, 102, 19, 101, 18, 100, 17, 99, 16, 98, 15, 97, 14, 96, 13, 95, 12, 94, 11, 93, 10, 92,
                   9, 91, 8, 90, 7, 89, 6, 88, 5, 87, 4, 86, 3, 85, 2, 84, 1, 83, 124, 42, 125, 43, 126, 44, 127, 45, 128, 46, 129, 47, 130, 48, 131, 49, 132, 50, 133, 51, 134, 52, 135, 53, 136, 54, 137, 55, 138, 56, 139, 57, 140, 58, 141, 59, 142, 60, 143, 61, 144, 62, 145, 63, 146, 64, 147, 65,
                   164, 82, 163, 81, 162, 80, 161, 79, 160, 78, 159, 77, 158, 76, 157, 75, 156, 74, 155, 73, 154, 72, 153, 71, 152, 70, 151, 69, 150, 68, 149, 67, 148, 66]
        }
    }

    model_names_list = [['robust_12T_50_mm_MQXF_cable_5_blocks_V2']]
    model_labels_list = [['50mm,5b']]

    # model_names = ['robust_12T_50_mm_MQXF_cable_5_blocks_V2']
    # model_labels = ['50mm,5b']
    # model_names = ['robust_12T_50_mm_MQXF_cable_6_blocks_V2']
    # model_labels = ['50mm,6b']
    model_names = ['robust_12T_56_mm_MQXF_cable_6_blocks_V2']
    model_labels = ['56mm,6b']
    model_names_list=[]
    model_labels_list=[]
    for _ in range(3*7+1):
        model_names_list.append(model_names)
        model_labels_list.append(model_labels)
    # model_names = ['robust_12T_50_mm_MQXF_cable_6_blocks_V2']
    # model_labels = ['50mm,6b']
    # model_names = ['robust_12T_56_mm_MQXF_cable_6_blocks_V2']
    # model_labels = ['56mm,6b']
    # sim_nr_list_of_lists = [[13, 113], [13, 113], [13, 113]]
    # #sim_nr_list_of_lists = [[3, 103], [3, 103], [3, 103]]
    # sim_nr_list_of_lists = [[3], [3], [3]]
    # sim_nr_list_of_lists = [[3]]
    #sim_nr_list_of_lists = [[3, 13], [3, 13], [3, 13]]
    #sim_nr_list_of_lists = [[13], [13], [13]]

    #sim_nr_list_of_lists = [[1, 2, 3, 13, 4, 14, 5, 6, 16, 7, 17]]
    sim_nr_list_of_lists = [
        #list(range(13001, 13019)),
        #list(range(13101, 13119)),
        #list(range(13201, 13219)),
        #list(range(13301, 13319)),
        #list(range(13401, 13419)),
        #list(range(13501, 13519)),
        # list(range(13601, 13619)),
        # list(range(13701, 13719)),
        # list(range(13801, 13819)),
        # list(range(13901, 13919)),
        # list(range(14001, 14019)),
        # list(range(14101, 14119)),
        # list(range(14201, 14219)),
        # list(range(14301, 14319)),
        # list(range(14401, 14419)),
        # list(range(14501, 14519)),
        # list(range(14601, 14619)),
        # list(range(14701, 14719)),
        # list(range(14801, 14819)),
        # (range(14901, 14919)),
        [50001]
        ]
    #sim_nr_list_of_lists = [[101, 102, 103, 113, 104, 114, 105, 106, 116, 107, 117]]

    sim_nr_list_of_lists = [  ]
    ranges = [(40001,40008), (40011,40018), (40021,40028)]
    for r in ranges:
        for i in range(*r):
            sim_nr_list_of_lists.append([i])


    #sim_nr_list_of_lists = [[3, 13, 4, 14, 6, 16, 7, 17]]
    #sim_nr_list_of_lists = [[103, 113, 104, 114, 106, 116, 107, 117]]
    #values = ['$I_{A}$', '$I_{B}$', '$I_{CLIQ}$']

    #values = ['$T_{max}$']
    values = ['$T_{max adb}$']
    #values = ['$U_{max}$']
    #values = ['$U_{min}$']
    #values = ['$R_{mag}$']
    #values = ['$I_{A}$']
    #values = ['$I_{CLIQ}$']
    values = ['$U_{GND MAX}$']
    style = 'presentation'


    path_to_sweep_file = r'E:\Python\m12t_r\model_long.csv'
    # path_to_sweep_file = r'E:\Python\m12t_r\model_long_HF.csv'
    # path_to_sweep_file = r'E:\Python\m12t_r\model_long_HF_CLIQ.csv'
    #case = 'CLIQ only'
    #case = 'Inner QH  & CLIQ'
    case = 'Outer QH  & CLIQ'
    #case = 'Outer & Inner QH'
    #case = 'Outer & Inner QH & CLIQ'

    magnet_name = 'robust_12T_50_mm_MQXF_cable_5_blocks_V2'
    magnet_name = 'robust_12T_50_mm_MQXF_cable_6_blocks_V2'
    magnet_name = 'robust_12T_56_mm_MQXF_cable_6_blocks_V2'

    x_var_name = 'Power_Supply.I_initial'
    y_var_name = 'Quench_Protection.CLIQ.C'
    z_var_name = '$T_{max adb}$'
    #z_var_name = '$I_{A}$'
   # z_var_name = '$U_{max}$'
    #z_var_name = '$I_{CLIQ}$'


    pa = PlotterAnalysis(base_path)
    pa.set_plot_style(style)
    #
    # for model_names, model_labels, sim_nr_list in zip(model_names_list, model_labels_list, sim_nr_list_of_lists):
    #     pa.read_data(model_names, model_labels, [sim_nr_list], values, el_order_lookup)
    #     #pa.plot_selected_vs_time(use_markers=0, save=0)
    #     pa.plot_selected_vs_el_order(use_markers=0, save=1)


    pa.read_sweep(path_to_sweep_file, case, x_var_name, y_var_name)
    pa.plot_sweep_2d(magnet_name, x_var_name, y_var_name, z_var_name)
