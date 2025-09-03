import os

import numpy as np
import pandas as pd
import h5py


def getSignalMat(path_sim, simNumber, list_Signals):

    simulationSignalsToPlot = pd.DataFrame()

    for i in range(len(simNumber)):
        path_simulationSignals = os.path.join(path_sim + str(simNumber[i]) + '.mat')
        with h5py.File(path_simulationSignals, 'r') as simulationSignals:
            for n in range(len(list_Signals)):
                simulationSignal = np.array(simulationSignals[list_Signals[n]])
                simulationSignal = simulationSignal.flatten().tolist()
                simulationSignal.insert(0, list_Signals[n]+'_'+str(simNumber[i]))
                simulationSignal = [simulationSignal]
                temp_frame = pd.DataFrame(simulationSignal)
                temp_frame.set_index(0, inplace=True)
                simulationSignalsToPlot = simulationSignalsToPlot.append(temp_frame)
    return simulationSignalsToPlot



def get_signals_from_mat_OLD(full_name_file: str, list_signals):
    '''
    Reads a mat file and returns a dataframe with the selected signals

    Note: The selected signals can also be define with a special syntax that allows accessing one certain row or column (1-indexed).
          Example: U_CoilSections(:,2) allows reading the 2nd column of the variable named U_CoilSections
          Example: U_CoilSections(3,:) allows reading the 3rd row of the variable named U_CoilSections
          Multiple columns/rows selection not currently supported  #TODO it would be nice to add

    :param full_name_file: full path to the mat file
    :param list_signals: list of signals to read
    :return: dataframe with the selected signals
    '''

    with h5py.File(full_name_file, 'r') as simulationSignals:
        df_signals = pd.DataFrame()
        for label_signal in list_signals:
            if ('(' in label_signal) and (')' in label_signal):
                # Special case: Only certain columns will be read
                label_signal_split = label_signal.split('(')
                signal = label_signal_split[0]
                rows_columns = label_signal_split[1].rstrip(')').split(',')
                label_rows    = rows_columns[0]
                label_columns = rows_columns[1]

                # Find slice of selected rows
                if label_rows == ':':
                    rows = slice(0, simulationSignals[signal].shape[1] - 1)
                elif ':' in label_rows:
                    raise Exception('Multiple rows selection not currently supported.')
                    # label_rows_split = label_rows.split(':')
                    # rows = slice(int(label_rows_split[0]) - 1, int(label_rows_split[1]) - 1)
                else:
                    rows = int(label_rows)

                # Find slice of selected columns
                if label_columns == ':':
                    columns = slice(0, simulationSignals[signal].shape[0]-1)
                elif ':' in label_columns:
                    raise Exception('Multiple columns selection not currently supported.')
                    # label_columns_split = label_columns.split(':')
                    # columns = slice(int(label_columns_split[0])-1, int(label_columns_split[1])-1)
                else:
                    columns = int(label_columns)-1

                # Apply slices
                simulationSignal = np.array(simulationSignals[signal][rows][columns])
                # NOTE: h5py._hl.dataset.Dataset are subsetted by using [rows, columns] not [rows][columns]
                #   - by only using [rows] or [columns] only the row is being accessed
                # EXAMPLE: using 'Uground_half_turns(:,1)' as signal name
                # when reading simulationSignals[signal] with h5py: row represents halfturn and column represents timestep
                #   - the dimensions are: number_of_halfturns x number_of_time_steps
                # [rows] ':' means so many rows (= halfturns) are being used as there are timesteps, meaning it deletes halfturns if number_of_halfturns>number_of_time_steps
                #   - the dimensions are: number_of_time_steps x number_of_time_steps, data is still: halfturns x time
                # [columns] '1' means it takes only the first row
                #   - the dimensions are: 1 x number_of_time_steps, data is still: halfturns x time
                #   - the error was never spottet because for number_of_halfturns < number_of_time_steps no error is made
            else:
                # Regular case: One-column signal is read
                signal = label_signal
                simulationSignal = np.array(simulationSignals[signal])

            simulationSignal = simulationSignal.flatten().tolist()
            df = pd.DataFrame({label_signal: simulationSignal})
            df_signals = pd.concat([df_signals, df], axis=1)
    return df_signals

def get_signals_from_mat(full_name_file: str, list_signals, bool_transpose: bool = True):
    '''
    Reads a mat file and returns a dataframe with the selected signals

    Note: The selected signals can also be define with a special syntax that allows accessing one certain row or column (1-indexed).
          Example: U_CoilSections(:,2) allows reading the 2nd column of the variable named U_CoilSections
          Example: U_CoilSections(3,:) allows reading the 3rd row of the variable named U_CoilSections
          Multiple columns/rows selection not currently supported  #TODO it would be nice to add

    :param full_name_file: full path to the mat file
    :param list_signals: list of signals to read
    :return: dataframe with the selected signals
    '''

    with h5py.File(full_name_file, 'r') as simulationSignals:
        df_signals = pd.DataFrame()
        number_of_time_steps = len(simulationSignals['time_vector'])  #TODO it is bad to hard-code this logic!
        for label_signal in list_signals:
            if ('(' in label_signal) and (')' in label_signal):
                # Special case: Only certain columns will be read
                label_signal_split = label_signal.split('(')
                signal        = label_signal_split[0]
                rows_columns  = label_signal_split[1].rstrip(')').split(',')
                label_rows    = rows_columns[0]
                label_columns = rows_columns[1]


                # Find slice of selected rows
                if label_rows == ':':
                    rows = slice(0, simulationSignals[signal].shape[1])
                elif ':' in label_rows:
                    raise Exception('Multiple rows selection not currently supported.')
                    # label_rows_split = label_rows.split(':')
                    # rows = slice(int(label_rows_split[0]) - 1, int(label_rows_split[1]) - 1)
                else:
                    rows = int(label_rows)

                # Find slice of selected columns
                if label_columns == ':':
                    columns = slice(0, simulationSignals[signal].shape[0])
                elif ':' in label_columns:
                    raise Exception('Multiple columns selection not currently supported.')
                    # label_columns_split = label_columns.split(':')
                    # columns = slice(int(label_columns_split[0])-1, int(label_columns_split[1])-1)
                else:
                    columns = int(label_columns)-1

                # Apply slices
                if bool_transpose:
                    simulationSignal = np.array(simulationSignals[signal][columns, rows])
                else:
                    simulationSignal = np.array(simulationSignals[signal][rows, columns])
            else:
                # Regular case: One-column signal is read
                signal = label_signal
                simulationSignal = np.array(simulationSignals[signal])

            simulationSignal = simulationSignal.flatten()
            df = pd.DataFrame({label_signal: simulationSignal})
            df_signals = pd.concat([df_signals, df], axis=1)
    return df_signals


def get_signals_from_mat_to_dict(full_name_file: str, list_signals, bool_transpose: bool = True,
                                 dict_variable_types: dict = {}):
    '''
    Reads a mat file and returns a dataframe with the selected signals

    Note: The selected signals can also be define with a special syntax that allows accessing one certain row or column (1-indexed).
          Example: U_CoilSections(:,2) allows reading the 2nd column of the variable named U_CoilSections
          Example: U_CoilSections(3,:) allows reading the 3rd row of the variable named U_CoilSections
          Multiple columns/rows selection not currently supported  #TODO it would be nice to add

    :param full_name_file: full path to the mat file
    :param list_signals: list of signals to read
    :param dict_variable_types: Optional variable to define the type of variable to read from a .mat file (the values in the dictionary can be "0D", "1D", or "2D")
    :type dict_variable_types: dict
    :return: dict with the selected signals
    '''

    with h5py.File(full_name_file, 'r') as simulationSignals:
        dict_signals = {}
        number_of_time_steps = len(simulationSignals['time_vector'])  #TODO it is bad to hard-code this logic!
        for label_signal in list_signals:
            if ('(' in label_signal) and (')' in label_signal):
                # Special case: Only certain columns will be read
                label_signal_split = label_signal.split('(')
                signal        = label_signal_split[0]
                rows_columns  = label_signal_split[1].rstrip(')').split(',')
                label_rows    = rows_columns[0]
                label_columns = rows_columns[1]

                # Find slice of selected rows
                if label_rows == ':':
                    rows = slice(0, simulationSignals[signal].shape[1])
                elif ':' in label_rows:
                    raise Exception('Multiple rows selection not currently supported.')
                    # label_rows_split = label_rows.split(':')
                    # rows = slice(int(label_rows_split[0]) - 1, int(label_rows_split[1]) - 1)
                else:
                    rows = int(label_rows)

                # Find slice of selected columns
                if label_columns == ':':
                    columns = slice(0, simulationSignals[signal].shape[0])
                elif ':' in label_columns:
                    raise Exception('Multiple columns selection not currently supported.')
                    # label_columns_split = label_columns.split(':')
                    # columns = slice(int(label_columns_split[0])-1, int(label_columns_split[1])-1)
                else:
                    columns = int(label_columns)-1

                # Apply slices
                if bool_transpose:
                    simulationSignal = np.array(simulationSignals[signal][columns, rows])
                else:
                    simulationSignal = np.array(simulationSignals[signal][rows, columns])
            else:
                # Regular case: One-column signal is read
                if bool_transpose:
                    simulationSignal = np.array(simulationSignals[label_signal]).T
                else:
                    simulationSignal = np.array(simulationSignals[label_signal])

            dict_signals[label_signal] = simulationSignal

        # Optional: Adjust each variable to the correct type (0D, 1D, 2D)
        for signal, signal_type in dict_variable_types.items():
            if signal_type == '0D':
                dict_signals[signal] = dict_signals[signal][0, 0]
            elif signal_type == '1D':
                if dict_signals[signal].shape[0] == 1:
                    dict_signals[signal] = dict_signals[signal][0]  # get the first column
                elif dict_signals[signal].shape[1] == 1:
                    dict_signals[signal] = dict_signals[signal].T[0]  # transpose and get first column
            elif signal_type == '2D':
                dict_signals[signal] = np.array(dict_signals[signal])
    return dict_signals


def print_shapes_of_entries(simulationSignals):
    shapes_dict = {}
    for key, value in simulationSignals.items():
        # Check if the value is a dataset
        if isinstance(value, h5py.Dataset):
            # Check the shape of the dataset
            shape = value.shape
            # Add the shape and key to the dictionary
            if shape not in shapes_dict:
                shapes_dict[shape] = [key]
            else:
                shapes_dict[shape].append(key)
    # Print out the shapes and associated keys
    for shape, keys in shapes_dict.items():
        print(f"Shape {shape} found in datasets: {keys}")


class Parser_LEDET_Mat:
    def __init__(self, LEDET_folder, magnet_name, sim_number):
        mat_file_path = os.path.join(LEDET_folder, magnet_name, 'Output', 'Mat Files', f'SimulationResults_LEDET_{sim_number}.mat')
        print(f'Reading mat file: {mat_file_path}')
        self.data = h5py.File(mat_file_path, 'r')
        self.t = np.array(self.data.get('time_vector')).T[0]

    def data_0D(self, var_name):
        return np.array(self.data.get(var_name))[0, 0]

    def data_1D(self, var_name, op='max'):
        data = np.array(self.data.get(var_name))
        if data.dtype == object:
            # https://stackoverflow.com/questions/17316880/reading-v-7-3-mat-file-in-python
            list_of_pointers = [r and self.data.get(self.data[r].name, self.data[r].name) for r in data.flat][0]
            return np.array(list_of_pointers).T
        if data.shape[0] == 1:
            return data[0]          # get first column
        elif data.shape[1] == 1:
            return data.T[0]        # transpose and get first column
        elif data.shape[0] == self.t.shape[0]:
            if op == 'min':
                return data.min(axis=1)
            elif op == 'max':
                return data.max(axis=1)
        elif data.shape[1] == self.t.shape[0]:
            if op == 'min':
                return data.min(axis=0)
            elif op == 'max':
                return data.max(axis=0)
            elif type(op) is dict:
                if 'c' in op.keys():
                    return data[op['c']]
                elif 'cs' in op.keys():
                    HalfTurnToCoilSection = np.where(np.array(self.data.get('HalfTurnToCoilSection')).T[0]==op['cs'])
                    if op['op'] == 'max':
                        return data[HalfTurnToCoilSection].max(axis=0)
                    elif op['op'] == 'min':
                        return data[HalfTurnToCoilSection].min(axis=0)
        else:
            raise Exception('Can not get such data')

    def data_2D(self, var_name):
        return np.array(self.data.get(var_name))