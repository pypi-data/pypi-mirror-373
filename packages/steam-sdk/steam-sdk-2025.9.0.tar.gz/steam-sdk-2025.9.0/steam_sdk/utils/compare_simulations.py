import os
import re
import pandas as pd
from datetime import datetime
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.parsers.CSD_Reader import CSD_read
from steam_sdk.parsers.ParserCsd import get_signals_from_csd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from steam_sdk.utils.reformat_figure import reformat_figure


def get_t_PC_off_value(file_path: str):
    # Open the file and read its contents line by line
    t_PC_off_value = 0
    with open(file_path, 'r') as file:
        for line in file:
            # Check if the line contains '.PARAM' and 't_PC_off'
            if 't_PC_off' in line:
                # Split the line by '=' and get the second part (the value)
                print("Found t_PC_off")
                parts = line.split('=')
                if len(parts) == 2:
                    t_PC_off_value = parts[1].strip()
                    t_PC_off_value = re.search(r'\d+\.\d+', t_PC_off_value).group(0)
                    t_PC_off_value = float(t_PC_off_value)  # Convert to float
                    break  # Exit the loop once we've found the value

    return t_PC_off_value

def compare_PSPICE_XYCE_simulations(circuit_type: str, event_name: str, path_folder_model_PSPICE: str, path_folder_model_XYCE: str):
    XYCE_csd_file = os.path.join(path_folder_model_XYCE, f"{circuit_type}.csd")
    PSPICE_CSD_file = os.path.join(path_folder_model_PSPICE, f"{circuit_type}.csd")
    list_signals_XYCE = CSD_read(XYCE_csd_file).signal_names
    list_signals_PSPICE = CSD_read(PSPICE_CSD_file).signal_names
    verbose = True
    path_output_csv = os.path.join(os.getcwd(), 'output', 'csv', f'{circuit_type}.csv')
    output_folder_figs = os.path.join(os.getcwd(), 'output', 'figures')
    make_folder_if_not_existing(os.path.dirname(path_output_csv))
    make_folder_if_not_existing(output_folder_figs)

    # # Plotting options
    # default_figsize = (20 / 2.54, 15 / 2.54)  # 20 cm by 15 cm
    # label_font = {'fontname': 'DejaVu Sans', 'size': 16}
    # title_font = {'fontname': 'DejaVu Sans', 'size': 16}
    # legend_font = {'fontname': 'DejaVu Sans', 'size': 14}
    # tick_font = {'fontname': 'DejaVu Sans', 'size': 12}
    # figure_types = ['png']  # supported: ['png', 'svg', 'pdf']
    # Align the data using interpolation
    pdf_pages = PdfPages(os.path.join(output_folder_figs, f'{event_name}_compare_pspice_xyce_plots.pdf'))
    # Load PSPICE simulation results
    df_PSPICE = get_signals_from_csd(full_name_file=os.path.join(path_folder_model_PSPICE, f'{circuit_type}.csd'),
                                     list_signals=['time'] + list_signals_PSPICE)
    df_XYCE = get_signals_from_csd(full_name_file=os.path.join(path_folder_model_XYCE, f'{circuit_type}.csd'),
                                   list_signals=['time'] + list_signals_XYCE)
    time_P = df_PSPICE['time']
    time_X = df_XYCE['time']
    if verbose: print(f'PSPICE and XYCE simulation output file read.')

    t_PC_off = get_t_PC_off_value(os.path.join(path_folder_model_PSPICE, f'{circuit_type}.cir'))
    zoom_time = t_PC_off
    zoom_window = 0.1

    # PSPICE and XYCE plots comparison
    for signal_PSPICE, signal_XYCE in zip(list_signals_PSPICE, list_signals_XYCE):
        # Create a figure with subplots
        fig, axes = plt.subplots(3, 1, figsize=(8, 12))

        # Plot the original signal
        axes[0].plot(time_X, df_XYCE[signal_XYCE], 'b', label=f'{signal_XYCE}')
        axes[0].plot(time_P, df_PSPICE[signal_PSPICE], 'r', label=f'{signal_PSPICE}')
        axes[0].set_ylabel('Voltage[V] or Current[A]')
        axes[0].set_title(f'{event_name}')
        axes[0].legend(loc='best')
        axes[0].grid()

        # Zoomed-in plot around time 0
        axes[1].plot(time_X, df_XYCE[signal_XYCE], 'b', label=f'{signal_XYCE}')
        axes[1].plot(time_P, df_PSPICE[signal_PSPICE], 'r', label=f'{signal_PSPICE}')
        axes[1].set_xlim(-zoom_window, zoom_window)
        axes[1].set_ylabel('Voltage[V] or Current[A]')
        axes[1].set_title(f'{event_name} (Zoomed around Time 0)')
        axes[1].legend(loc='best')
        axes[1].grid()

        # Zoomed-in plot around t_PC_off
        axes[2].plot(time_X, df_XYCE[signal_XYCE], 'b', label=f'{signal_XYCE}')
        axes[2].plot(time_P, df_PSPICE[signal_PSPICE], 'r', label=f'{signal_PSPICE}')
        axes[2].set_xlim(t_PC_off - zoom_window, t_PC_off + zoom_window)
        axes[2].set_xlabel('Time [s]')
        axes[2].set_ylabel('Voltage[V] or Current[A]')
        axes[2].set_title(f'{event_name} (Zoomed around t_PC_off)')
        axes[2].legend(loc='best')
        axes[2].grid()

        # Save the current set of plots in the PDF file
        pdf_pages.savefig()

        # Close the current figure to start a new one in the next iteration
        plt.close()

    # Close the PDF file
    pdf_pages.close()

    # for signal_PSPICE, signal_XYCE in zip(list_signals_PSPICE, list_signals_XYCE):
    #     plt.figure()
    #     plt.plot(time_X, df_XYCE[signal_XYCE], 'b', label=f'{signal_XYCE}')
    #     plt.plot(time_P, df_PSPICE[signal_PSPICE], 'r', label=f'{signal_PSPICE}')
    #     #plt.scatter(time_P, df_PSPICE[signal_PSPICE], s=5, label=f'{signal_PSPICE}')
    #     #plt.xlim(zoom_time - zoom_window, zoom_time + zoom_window)
    #
    #     #plt.scatter(time_X, df_XYCE[signal_XYCE], s=5, label=f'{signal_XYCE}')
    #     plt.xlabel('Time [s]')
    #     plt.ylabel('Voltage[V] or Current[A]')
    #     plt.title(f'{circuit_type}')
    #     plt.legend(loc='best')
    #     plt.grid()
    #     #reformat_figure(figsize=default_figsize, label_font=label_font, title_font=title_font, legend_font=legend_font, tick_font=tick_font)
    #     #[plt.savefig(os.path.join(output_folder_figs, f'{circuit_type}_{signal_PSPICE}.{d_type}'), format=d_type) for d_type in figure_types]
    #     pdf_pages.savefig()
    #     plt.close()

def compare_simulation_with_measured_signal(circuit_type: str, event_file: str, path_folder_model_software: str, software: str):
        from lhcsmapi.Time import Time
        from lhcsmapi.metadata import signal_metadata
        from lhcsmapi.api import query, resolver, processing

        output_folder_figs = os.path.join(os.getcwd(), 'output', 'figures')
        make_folder_if_not_existing(output_folder_figs)

        df = pd.read_csv(os.path.join("input", event_file))
        if circuit_type == "RQX":
            ts = df[['Date (FGC_RQX)', 'Time (FGC_RQX)', 'Circuit Name']].dropna() #FGC_RQX for RQX
            ts['Timestamp Epoch before'] = ts['Date (FGC_RQX)'] + ' ' + ts['Time (FGC_RQX)']   #FGC_RQX for RQX
            if software == 'PSPICE':
                signal_names_sim_current = ['I(x_RQX.v1_ph)', 'I(x_RTQX1.v1_ph)', 'I(x_RTQX2.v1_ph)']
                signal_names_sim_voltage = ['V(104,101)', 'V(102,101)', 'V(103,102)']
            elif software == 'XYCE':
                signal_names_sim_current = ['I(X_RQX:V1_PH)', 'I(X_RTQX1:V1_PH)', 'I(X_RTQX2:V1_PH)']
                signal_names_sim_voltage = ['V(104,101)', 'V(102,101)', 'V(103,102)']
        elif circuit_type.startswith("IPQ"):
            ts = df[['Date (FGC_Bn)', 'Time (FGC_Bn)', 'Circuit Name']].dropna() #FGC_Bn for IPQ
            ts['Timestamp Epoch before'] = ts['Date (FGC_Bn)'] + ' ' + ts['Time (FGC_Bn)']   #FGC_Bn for IPQ
            if software == 'PSPICE':
                signal_names_sim_current = ['I(R_Warm_1)', 'I(R_Warm_2)']
                signal_names_sim_voltage = ['V(2,1)', 'V(0A,7)']
            elif software == 'XYCE':
                signal_names_sim_current = ['I(R_Warm_1)', 'I(R_Warm_2)']
                signal_names_sim_voltage = ['V(2,1)', 'V(0A,7)']
        else:
            ts = df[['Date (FGC)', 'Time (FGC)', 'Circuit Name']].dropna() #FGC for the rest
            ts['Timestamp Epoch before'] = ts['Date (FGC)'] + ' ' + ts['Time (FGC)']   #FGC for the rest
            if software == 'PSPICE':
                signal_names_sim_current = ['I(x_PC.V_monitor_out)']
                signal_names_sim_voltage = ['V(2,1)']
            elif software == 'XYCE':
                signal_names_sim_current = ['I(X_PC:V_MONITOR_OUT)']
                signal_names_sim_voltage = ['V(2,1)']
        timestamp = datetime.strptime(ts['Timestamp Epoch before'][0].replace('-', '/'), "%Y/%m/%d %H:%M:%S.%f")
        timestamp = Time.to_unix_timestamp(timestamp)

        signal_names_meas_current = ['I_A'] #TODO signal list to be extended ["I_REF", "I_MEAS", "V_REF", "V_MEAS", "I_EARTH", "I_EARTH_PCNT", "I_A", "I_B"]
        signal_names_meas_voltage = ['V_MEAS']

        circuit_name = ts['Circuit Name'][0]
        #circuit_type = get_circuit_family_name(circuit_name)
        params = resolver.get_params_for_pm_events(circuit_type, circuit_name, 'PC', timestamp, duration=100000000000)
        for i in range(len(signal_names_sim_current)):
            data_current = query.query_pm_signals(params.triplets[i].system, params.triplets[i].class_, params.triplets[i].source, signal_names_meas_current, timestamp)
            data_processed_current = processing.SignalProcessing(data_current).synchronize_time(timestamp).convert_index_to_sec().get_dataframes()

            data_voltage = query.query_pm_signals(params.triplets[i].system, params.triplets[i].class_, params.triplets[i].source, signal_names_meas_voltage, timestamp)
            data_processed_voltage = processing.SignalProcessing(data_voltage).synchronize_time(timestamp).convert_index_to_sec().get_dataframes()

            # Plotting options
            default_figsize = (20 / 2.54, 15 / 2.54)  # 20 cm by 15 cm
            label_font = {'fontname': 'DejaVu Sans', 'size': 16}
            title_font = {'fontname': 'DejaVu Sans', 'size': 16}
            legend_font = {'fontname': 'DejaVu Sans', 'size': 14}
            tick_font = {'fontname': 'DejaVu Sans', 'size': 12}
            figure_types = ['png']  # supported: ['png', 'svg', 'pdf']

            df_software_current = get_signals_from_csd(full_name_file=os.path.join(path_folder_model_software, f'{circuit_type}.csd'), list_signals=['time']+signal_names_sim_current)
            df_software_voltage = get_signals_from_csd(full_name_file=os.path.join(path_folder_model_software, f'{circuit_type}.csd'), list_signals=['time']+signal_names_sim_voltage)

            time_sim_current = df_software_current['time']
            time_sim_voltage = df_software_voltage['time']
            t_PC_off= get_t_PC_off_value(os.path.join(path_folder_model_software, f'{circuit_type}.cir'))
            zoom_time = t_PC_off
            zoom_window = 0.5
            for signal_sim_current, signal_meas_current in zip([signal_names_sim_current[i]], signal_names_meas_current):
                plt.figure()
                plt.plot(time_sim_current, df_software_current[signal_sim_current], 'r--', label=f'{signal_sim_current}')
                plt.plot(data_processed_current[signal_meas_current].keys() + t_PC_off, data_processed_current[signal_meas_current].values, 'b-', label=f'{signal_meas_current}')
                plt.xlim(zoom_time - zoom_window, zoom_time + zoom_window)
                plt.legend(loc='best')
                plt.grid()
                reformat_figure(figsize=default_figsize, label_font=label_font, title_font=title_font, legend_font=legend_font, tick_font=tick_font)
                signal_sim_current = signal_sim_current.replace(':','.')
                [plt.savefig(os.path.join(output_folder_figs, f'{circuit_type}_{signal_sim_current}.{d_type}'), format=d_type) for d_type in figure_types]
                plt.close()

            for signal_sim_voltage, signal_meas_voltage in zip([signal_names_sim_voltage[i]], signal_names_meas_voltage):
                plt.figure()
                plt.plot(time_sim_voltage, df_software_voltage[signal_sim_voltage], 'r--', label=f'{signal_sim_voltage}')
                plt.plot(data_processed_voltage[signal_meas_voltage].keys() + t_PC_off, data_processed_voltage[signal_meas_voltage].values, 'b-', label=f'{signal_meas_voltage}')
                plt.xlim(zoom_time - zoom_window, zoom_time + zoom_window)
                plt.legend(loc='best')
                plt.grid()
                reformat_figure(figsize=default_figsize, label_font=label_font, title_font=title_font, legend_font=legend_font, tick_font=tick_font)
                signal_sim_voltage = signal_sim_voltage.replace(':','.')
                [plt.savefig(os.path.join(output_folder_figs, f'{circuit_type}_{signal_sim_voltage}.{d_type}'), format=d_type) for d_type in figure_types]
                plt.close()
