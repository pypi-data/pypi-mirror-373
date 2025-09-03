import os
from pathlib import Path
from typing import Union, Dict

import numpy as np
import pandas as pd

from nptdms import TdmsFile

from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class ParserTdms:
    """
        Class with methods to read .tdms files and convert them to .csv files
    """

    def __init__(self, path_tdms: str):
        """
            Initialization using the path to the .tdms file to read
            Reminder: .tdms files are arranged in groups of signals. The parser will maintain this structure.
            It is assumed here that different groups have different time vectors, but different signals in the same group have the same time vector.
        """
        # Reads .tdms file
        self.TDMSFile = TdmsFile.read(path_tdms)
        self.signal_data = np.array([[]])
        self.dict_groups_signals = {}  # This is a dictionary of data frames. Each dictionary refers to a group, and each data frame includes all of its signals (i.e. channels)


    def get_signal(self, group_name: str, signal_name: str):
        """
            This function gets a specific signal (channel) from a group of a .tdms file.

            - groups: A group is an instance of the TdmsGroup class, and can contain multiple channels of data
            - channel: Channels are instances of the TdmsChannel class and act like arrays - in this case: signals of the measurement

            :return np.array
        """

        # get signal data
        signal_output = self.TDMSFile[group_name][signal_name][:]
        return signal_output

    def get_all_signals(self, group_names:[], signal_names:[]):
        """
            This function gets specific signals (channel) from a group of a .tdms file.

            - groups: A group is an instance of the TdmsGroup class, and can contain multiple channels of data
            - channel: Channels are instances of the TdmsChannel class and act like arrays - in this case: signals of the measurement
        """
        signal_output = []
        for i in range(len(signal_names)):
            # get signal data
            signal_output_temp = self.TDMSFile[group_names[i]][signal_names[i]][:]
            signal_output.append(signal_output_temp)
        return signal_output

    def appendColumnToSignalData(self, dictionary: Dict):
        """
            Appending the values of the specified signals in ascending order to signal_data without the name of the group or the signal
             -> row by row: so each array represents each row with one value of each desired signal
            Input: dictionary: {group_name_1: [signal_name1, signal_name2,...], group_name_2: [signal_name3, signal_name4,...],...}
        """
        for group in dictionary.keys():
            for channel in dictionary[group]:
                if self.signal_data.size == 0:
                    self.signal_data = np.atleast_2d(self.TDMSFile[group][channel][:]).T
                else:
                    self.signal_data = np.column_stack((self.signal_data, self.TDMSFile[group][channel][:]))

    def printTDMSproperties(self):
        """
            This function prints the general properties of a .tdms file.
        """

        # Iterate over all items in the file properties and print them
        print("#### GENERAL PROPERTIES ####")
        for name, value in self.TDMSFile.properties.items():
            print("{0}: {1}".format(name, value))

    def printTDMSgroups(self, flag_channel_prop: bool = False):
        """
            This function prints the general properties of a .tdms file, like    the general properties
                                                                                group names and their properties
                                                                                channel names and if wished their properties
        """

        count = 1
        print("#### GROUP PROPERTIES ####")
        print(self.TDMSFile.properties)
        for g in self.TDMSFile.groups():
            print("@@@GROUP", count)
            print("{}".format(g))
            for name, value in g.properties.items():
                print("{0}: {1}".format(name, value))
                print("# CHANNELS OF GROUP {}#".format(count))
                for c in g.channels():
                    print("# CHANNEL #")
                    print("{}".format(c))
                    print(c.name)
                    if flag_channel_prop:
                        print("# CHANNEL PROPERTIES #")
                        for name, value in c.properties.items():
                            print("{0}: {1}".format(name, value))
            count = count + 1

    def getNames(self):
        """
        This function gets all group and signal names from a .tdms file
        """

        dict_groups = {}
        group_names = []
        signal_names = [[]]
        for g in self.TDMSFile.groups():
            dict_groups[g.name] = []
            group_names.append(g.name)
            signal_names_group = []
            for c in g.channels():
                signal_names_group.append(c.name)
                dict_groups[g.name].append(c.name)
            signal_names.append(signal_names_group)
        signal_names.pop(0)
        return group_names, signal_names, dict_groups

    def writeTdmsToCsv(self, path_output: str, dictionary: Dict):
        """
            This function writes the signals of the signal_data dictionary of this class of a .tdms file to a specific csv file.
            dictionary for header with names of the groups and signal that are used in the .tdms file
            header: Groupname_signalname, ....
        """
        make_folder_if_not_existing(os.path.dirname(path_output), verbose=False)

        # Get signal
        # signal_output = getspecificSignal(path_tdms, group_name, signal_name)
        # np.savetxt(path_output, signal_output, delimiter=",")
        # headers, units,...
        header = []
        for group in dictionary.keys():
            for channel in dictionary[group]:
                header.append(group + '_' + channel)

        tdms_df = pd.DataFrame(self.signal_data)
        tdms_df.to_csv(path_output, header=header, index=False)

    def get_timeVector(self, group_name: str, signal_name: str):
        """
            This function reconstructs the time_vector of a signal of a .tdms file using the following properties:
                wf_increment, wf_samples, wf_samples
            If any of these properties are not present in the signal, the function returns an empty np.array
            If wf_increment or wf_samples are 0 , the function returns an empty np.array
        """
        # Read the three required properties, and return NaN if any of them is missing
        properties = self.TDMSFile[group_name][signal_name].properties
        if 'wf_increment' in properties:
            inc = properties['wf_increment']
        else:
            return np.empty((0, 0))
        if 'wf_samples' in properties:
            samples = properties['wf_samples']
        else:
            return np.empty((0, 0))
        if 'wf_start_offset' in properties:
            offset = properties['wf_start_offset']
        else:
            return np.empty((0, 0))

        if (inc == 0) or (samples == 0):
            return np.empty((0, 0))

        time_vector = np.arange(offset, offset + inc*samples, inc)

        return time_vector

    def convertTdmsToDict(self, selected_groups: list = []):
        '''
        Convert the signals of one or more groups of a .tdms file into a dictionary
        Each dictionary key will contain the signals (i.e. channels) of one group

        :param selected_groups: List of groups to convert. If left empty, all groups will be converted
        :return: dict
        '''

        # Initialize dictionary
        dict_groups_signals = {}

        # Read all signals groups and signals names
        _, _, dict_groups = self.getNames()

        # If selected_groups is empty, select all signals groups
        if len(selected_groups) == 0:
            selected_groups = list(dict_groups.keys())

        # Write groups and names in a dictionary
        for group in selected_groups:
            # Acquire time vector of the current group and assign it to a temporary dictionary
            temp_dict = {}
            time_vector = self.get_timeVector(group, dict_groups[group][0])
            if len(time_vector) > 0:  # only add the time vector if it was calculated properly
                temp_dict['Time [s]'] = pd.Series(time_vector)
            # Acquire all signals of the current group in the dictionary
            for signal in dict_groups[group]:
                temp_dict[signal] = pd.Series(self.TDMSFile[group][signal].data)

            # Convert dictionary to dataframe
            dict_groups_signals[group] = pd.DataFrame(temp_dict)

        return dict_groups_signals

    def convertTdmsToCsv(self, path_output: Union[str, Path], selected_groups: list = [], flag_overwrite: bool = True):
        '''
        Convert the signals of one or more groups of a .tdms file into a .csv file
        Each signal group will be converted to a different .csv file

        :param path_output: Full path of the output file(s), as a string or Path. Note: for each group, a different suffix will be added to the file name
        :param selected_groups: List of groups to convert. If left empty, all groups will be converted
        :param flag_overwrite: Flag indicating whether output files must be over-written or not. If set to False and an output file already exists, issue a message .
        :return:
        '''

        # If path_output is given as a string, resolve its path
        if type(path_output) == str:
            path_output = Path(path_output).resolve()

        # If the output folder does not exist, make it now
        make_folder_if_not_existing(os.path.dirname(path_output))

        # Acquire data (all signals) and assign them to the object dictionary
        self.dict_groups_signals = self.convertTdmsToDict(selected_groups=[])

        # If selected_groups is empty, select all signals groups
        if len(selected_groups) == 0:
            _, _, dict_groups = self.getNames()  # Read all signals groups and signals names
            selected_groups = list(dict_groups.keys())

        # Write groups and names in a dictionary
        for group in selected_groups:
            # Define current file name
            suffix_group = f'_{group}'
            full_path_file_group = str(path_output).split('.csv')[0] + suffix_group + '.csv'

            # Write file
            if (flag_overwrite == False) and (os.path.isfile(full_path_file_group) == True):
                print(f'File {full_path_file_group} already exists and flag_overwrite={flag_overwrite}: File not overwritten.')
            else:
                self.dict_groups_signals[group].to_csv(full_path_file_group, index=False, sep=',')  # , float_format='%.7f')  # Write file
                print(f'File {full_path_file_group} written.')


#### HELPER functions ####

def getAllTDMSfiles(path_folder):
    """
        Gets all .tdms files in a specific folder and returns a list of the names of the .tdms files
    """
    # TODO: Not tested
    list_all_files = os.listdir(path_folder)
    list_tdms_files = []
    for file in list_all_files:
        if file.endswith(".tdms"):
            list_tdms_files.append(file)

    return list_tdms_files
