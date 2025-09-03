import math
import os
import re
import csv
from typing import List, Dict
import pandas as pd
import yaml
from pathlib import Path

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.data.DataAnalysis import DefaultParsimEventKeys
from steam_sdk.parsers.ParserTdms import ParserTdms
from steam_sdk.data.DataEventMagnet import DataEventMagnet, QuenchHeaterCircuit
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.sgetattr import rsetattr, rgetattr


class ParsimEventMagnet:
    """
    This class is used to:
     - read_from_input: reads the data of magnet events from a table (where rows represent a event and columns define the variable names)
     - write_event_file: writes the data to csv, that can be interpreted from ParimSweeper step (this step creates simulation input files for all magnet events)
     - set_up_viewer: creates a SetUpViewer csv file with all the magnet events to visually compare measurement and corresponding simulation
    """

    def __init__(self, ref_model: BuilderModel = None, verbose: bool = True):
        """
        :param ref_model: Reference model to populate empty fields with default values. Defaults to None.
        :param verbose: if True, additional information will be displayed. Defaults to True.
        """
        # Unpack and create arguments
        self.ref_model = ref_model
        self.verbose: bool = verbose
        self.list_events: List[DataEventMagnet] = []
        self.dict_AnalysisStepDefinition = {}
        self.list_AnalysisStepSequence = []

    def read_from_input(self, path_input_file: str, flag_append: bool, rel_quench_heater_trip_threshold: float):
        '''
        Read a list of events from an input csv file and assign its content to a list of DataEventMagnet() objects.

        Values that can be directly read as a column are parsed via event_column_names.yaml - if a new type of input csv
        is used, the code does not have to be changed, just add the new column names to this yaml file

        :param path_input_file: Path to the input csv file to read
        :param flag_append: If True, merge the content of the file to the current list of events. If False, overwrite it.
        :param rel_quench_heater_trip_threshold: relative threshold value for QH voltage for measurement of QH trigger time
        :return: no return value
        :raises Exception: If the input file has an unsupported extension or an incorrect format
        '''

        # Read the input file
        if path_input_file.endswith('.csv'):
            df_events = pd.read_csv(path_input_file)
        elif path_input_file.endswith('.xlsx'):
            df_events = pd.read_excel(path_input_file)
        else:
            raise Exception(f'The extension of the file {path_input_file} is not supported.')
        df_events = df_events.dropna(axis=1, how='all')

        # validate dataframe - if csv file has a headline or empty rows on the top, skip row until there all columnnames have values
        skip_rows = 0
        while any(['Unnamed: ' in s for s in df_events.columns]): # pandas assigns the columname 'Unnamed: i' when no name can be found
            skip_rows += 1
            if path_input_file.endswith('.csv'):
                df_events = pd.read_csv(path_input_file, skiprows=skip_rows)
            elif path_input_file.endswith('.xlsx'):
                df_events = pd.read_excel(path_input_file, skiprows=skip_rows)
            df_events = df_events.dropna(axis=1, how='all')
            if skip_rows == 2:  # check only for the first 2 rows
                raise Exception(f"The input file {path_input_file} has an incorrect format. Some columns have no name, or one of the column names starts with 'Unnamed: '.")

        # read dictionary for reading columns into local dataclass when directly possible
        # to add new column names the code does not have to be changed, just add the new colunm names to this yaml file
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translation_dicts", "event_column_names.yaml")
        with open(yaml_path, 'r') as file:
            # this dict now holds the attribute names as keys and a list of possible column names as values
            dict_attribute_to_column = yaml.safe_load(file)

        # Assign the content to a dataclass structure
        list_events = []
        parsed_columns = []  # list containing the column names that were parsed
        for index, event_info in df_events.iterrows():
            new_event = DataEventMagnet()

            # methods alter corresponding fields of new_event and return the column names that were parsed
            parsed_columns += self.__read_general_parameters(event_info, new_event, dict_attribute_to_column['GeneralParameters'])
            parsed_columns += self.__read_powering(event_info, new_event, dict_attribute_to_column['Powering'])
            parsed_columns += self.__read_QH(event_info, new_event, rel_quench_heater_trip_threshold)
            parsed_columns += self.__read_CLIQ(event_info, new_event, dict_attribute_to_column['CLIQ'])

            list_events.append(new_event)

        # print out all the names of the ignored columns
        ignored_column_names = list(set(df_events.columns) - set(parsed_columns))
        if self.verbose: print(f'Names of ignored columns: {ignored_column_names}')

        # Update attribute
        if flag_append:
            self.list_events += list_events
        else:
            self.list_events = list_events


    def write_event_file(self, simulation_numbers: List[int], t_PC_off: float, path_outputfile_event_csv: str,
                         simulation_name: str, current_polarities_CLIQ: List[int], dict_QH_circuits_to_QH_strips: Dict[str, List[int]]):
        '''
        Write the event information to a csv file, that can be used to run a ParsimSweep Step.

        :param simulation_numbers: List of simulation numbers (length has to correspond to number of events)
        :param t_PC_off: power converter off time
        :param path_outputfile_event_csv: Path to the output csv file for ParsimSweep
        :param simulation_name: Simulation name
        :param current_polarities_CLIQ: List of CLIQ polarities
        :param dict_QH_circuits_to_QH_strips: Mapping of Quench Heater (QH) circuits to QH strips

        :raises Exception: If the length of input simulation numbers differs from length of events found in the input file
        '''
        # check inputs
        if len(simulation_numbers) != len(self.list_events):
            raise Exception(f'length of input simulation numbers ({len(simulation_numbers)}) differs from length of events found in the input file ({len(self.list_events)})')

        # Make target folder if it is missing
        make_folder_if_not_existing(os.path.dirname(path_outputfile_event_csv))

        # make dict for every row and store it in a list of dicts - loop trough each element of self.list_events and write parameters to csv
        row_dicts = []
        for i, event in enumerate(self.list_events):
            new_row = {'simulation_name': simulation_name, 'simulation_number': simulation_numbers[i]}
            new_row.update(self.__write_analysis_powering(event, t_PC_off))
            new_row.update(self.__write_analysis_CLIQ(event, current_polarities_CLIQ))
            new_row.update(self.__write_analysis_QH(event, dict_QH_circuits_to_QH_strips))
            new_row.update(self.__write_analysis_general_parameters(event))
            row_dicts.append(new_row)

        # write csv file
        with open(path_outputfile_event_csv, 'w', newline='') as csv_file:
            fieldnames = list(set(key for d in row_dicts for key in d))  # TODO what happens when value is missing in dict
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in row_dicts: writer.writerow(row)

    def set_up_viewer(self, path_output_viewer_csv: str, default_keys: DefaultParsimEventKeys,
                      simulation_numbers: List[int], simulation_name: str, software: str):
        '''
        Writes a csv file that can be used to run a STEAM Viewer step

        :param path_output_viewer_csv: The path to the output csv file for the Viewer.
        :param default_keys: The default keys for the ParsimEvent step.
        :param simulation_numbers: list of simulation numbers to be included in the analysis.
        :param simulation_name: The name of the simulation.
        :param software: The software used for the simulation.
        '''
        # Unpack input dictionary with default key values
        path_config_file              = default_keys.path_config_file
        default_configs               = default_keys.default_configs
        path_tdms_files               = default_keys.path_tdms_files
        path_output_measurement_files = default_keys.path_output_measurement_files
        path_output                   = default_keys.path_output

        # Read the signal names needed for the different configurations to later check which configuration can be used
        dict_configs_with_signals = self.__read_signals_of_configs(default_configs, path_config_file)

        # Identify software-specific folder and file names
        if software == 'LEDET':
            local_LEDET_folder = default_keys.local_LEDET_folder
            # Identify simulation folder based on the software
            path_simulation_folder = f'{local_LEDET_folder}\{simulation_name}\Output\Mat Files'  # TODO read local_LEDET_folder from settings as well?
            # Identify simulation file names based on the software
            list_simulation_names = []
            for sim in simulation_numbers:
                list_simulation_names.append(f'SimulationResults_LEDET_{sim}.mat')
        else:
            raise Exception(f'The required software ({software}) is not supported.')

        # Check if the measurement files exist, and either find the file names or set different configuration settings (without measurement data)
        df = pd.DataFrame(columns=["Event label", "Configuration file", "Configuration", "Measurement folder", "Test campaign",
                                   "Test name", "flag_convert_meas_csv", "path_output_measurement_files", "Simulation folder",
                                   "Simulation file", "path_output_figures", "path_output_simulation_files", "Comments"])
        for i, event in enumerate(self.list_events):
            new_row = {
                "Event label": event.GeneralParameters.name,
                "Configuration file": path_config_file,
                "Measurement folder": path_tdms_files,
                "path_output_measurement_files": path_output_measurement_files,
                "Simulation folder": path_simulation_folder,
                "Simulation file": list_simulation_names[i],
                "path_output_figures": path_output,
                "path_output_simulation_files": "not_used",
                "Comments": "no comments"
            }

            # Find longest sequences of integers in the name string (this is supposed to be the timestamp at which the measurement was taken)
            digit_sequences = re.findall(r'\d+', event.GeneralParameters.name)  # Find all groups of consecutive digits
            n_integers = max(len(seq) for seq in digit_sequences)  # Find longest group of consecutive digits
            list_integer_sequences = re.findall(fr'\d{{{n_integers}}}', event.GeneralParameters.name)
            if len(list_integer_sequences) == 0:
                raise Exception(f'Timestamp in Event {event.GeneralParameters.name} could not be clearly identified. A sequence of 10 integers should be present to define a unique timestamp.')
            elif len(list_integer_sequences) == 1:
                timestamp = list_integer_sequences[0]
            else:
                raise Exception(f'More than one timestamp ({list_integer_sequences}) could be found in Event {event.GeneralParameters.name}. A sequence of 10 integers should be present to define a unique timestamp.')


            # Look into the tdms test campaign folders and search for files containing timestamp
            campaign_name_tdms, name_file_found_tdms = search_file_in_subfolders(timestamp, path_tdms_files, '.tdms')

            # if a tdms file could be found, append remaining values to dataframe - this event is finished
            if campaign_name_tdms and name_file_found_tdms:
                new_row["Test name"] = name_file_found_tdms
                new_row["Test campaign"] = campaign_name_tdms
                new_row["Configuration"] = self.__get_config_tdms(path_tdms_files, campaign_name_tdms, name_file_found_tdms,
                                                           dict_configs_with_signals, self.verbose)
                new_row["flag_convert_meas_csv"] = '1'  # csv will be generated by viewer if not present
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)  # Append the new row to the DataFrame
                continue


            # if no tdms file present, search for csv file containing the timestamp
            campaign_name_csv, name_file_found_csv = search_file_in_subfolders(timestamp, path_output_measurement_files,'.csv')

            # if a csv file could be found, append remaining values to dataframe - this event is finished
            if campaign_name_csv and name_file_found_csv:
                new_row["Test name"] = name_file_found_csv
                new_row["Test campaign"] = campaign_name_csv
                new_row["Configuration"] = self.__get_config_csv(path_output_measurement_files, campaign_name_csv,
                                                          name_file_found_csv, dict_configs_with_signals, self.verbose)
                new_row["flag_convert_meas_csv"] = '0'  # Viewer will not try to convert data
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)  # Append the new row to the DataFrame
                continue


            # if neither tdms nor csv is found, no measurement data is attached - Viewer shows only simulation results
            new_row["Test name"] = ''
            new_row["Test campaign"] = ''
            new_row["Configuration"] = default_configs[-1]
            new_row["flag_convert_meas_csv"] = ''
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)  # Append the new row to the DataFrame
            if self.verbose: print(f'NOTE: No measurement data for event {event.GeneralParameters.name} found.')

        # If the parent folder is not present, make it and save the dataframe as the viewer setup csv
        make_folder_if_not_existing(os.path.dirname(path_output_viewer_csv))
        df.to_csv(path_output_viewer_csv, index=False)



    ### Helper functions ###
    def __write_analysis_general_parameters(self, event: DataEventMagnet):
        '''
        Extracts and writes the general parameters information for an event.

        :param event: The data event object to read the data from
        :return: A dictionary containing the general parameters variable names (dict:key) and values (dict:value)
        '''
        event_dict = dict()
        # populate steps in list of steps
        dict_param = {  # key is attribute name in DataEventMagnet, value is attribute name in modelData
            'GeneralParameters.initial_temperature': 'GeneralParameters.T_initial',
        }
        for old_name, new_name in dict_param.items():
            if rgetattr(event, old_name) and not math.isnan(rgetattr(event, old_name)):
                event_dict[new_name] = rgetattr(event, old_name)
            if not new_name in event_dict:
                event_dict[new_name] = ''

        return event_dict

    def __write_analysis_powering(self, event: DataEventMagnet, t_PC_off: float, t_LUT_start: float = -10.0):
        '''
        Extracts and writes the power supply related information for an event.

        :param event: The data event object to read the data from
        :param t_PC_off: Power supply switch-off time
        :param t_LUT_start: starting time for the LUT time vector
        :return: A dictionary containing the power supply variable names (dict:key) and values (dict:value)
        '''
        event_dict = dict()

        # loop
        dict_param = {  # key is attribute name in DataEventMagnet, value is attribute name in modelData
            'Powering.PowerSupply.I_initial': 'Power_Supply.I_initial',
            'Powering.PowerSupply.t_off': 'Power_Supply.t_off',
            'Powering.PowerSupply.R_crowbar': 'Power_Supply.R_crowbar',
            'Powering.PowerSupply.Ud_crowbar': 'Power_Supply.Ud_crowbar',
        }
        for old_name, new_name in dict_param.items():
            if rgetattr(event, old_name) and not math.isnan(rgetattr(event, old_name)):
                event_dict[new_name] = rgetattr(event, old_name)
            if not new_name in event_dict:
                event_dict[new_name] = ''

        # Set power supply switch-off time
        event_dict['Power_Supply.t_off'] = t_PC_off

        # Calculate LUT vectors for power supply
        if not math.isnan(rgetattr(event, 'Powering.PowerSupply.I_initial')):
            I_initial = rgetattr(event, 'Powering.PowerSupply.I_initial')
        else:
            raise Exception(f'Powering.PowerSupply.I_initial must be provided in the event {rgetattr(event, "GeneralParameters.name")}')
        if not math.isnan(rgetattr(event, 'Powering.max_dI_dt')):
            dI_dt = rgetattr(event, 'Powering.max_dI_dt')
        else:
            if self.verbose:
                print(f'Powering.max_dI_dt not provided and set to 0 A/s.')
            dI_dt = 0

        event_dict['Power_Supply.t_control_LUT'] = [t_LUT_start, t_PC_off, t_PC_off + 0.01]
        event_dict['Power_Supply.I_control_LUT'] = [I_initial - (t_PC_off-t_LUT_start) * dI_dt, I_initial, 0]

        return event_dict

    def __write_analysis_CLIQ(self, event: DataEventMagnet, current_polarities_CLIQ: List[int]):
        '''
        Extracts and writes the CLIQ parameters for an event.

        :param event: The event from which the CLIQ parameters can be read
        :param current_polarities_CLIQ: The current polarities of the CLIQ event
        :return: A dictionary containing the CLIQ variable names (dict:key) and values (dict:value)
        '''
        event_dict = dict()

        dict_param = {
            'QuenchProtection.CLIQ.t_trigger': 'Quench_Protection.CLIQ.t_trigger',
            'QuenchProtection.CLIQ.U0': 'Quench_Protection.CLIQ.U0',
            'QuenchProtection.CLIQ.C': 'Quench_Protection.CLIQ.C',
            'QuenchProtection.CLIQ.R': 'Quench_Protection.CLIQ.R',
            'QuenchProtection.CLIQ.L': 'Quench_Protection.CLIQ.L',
        }
        for old_name, new_name in dict_param.items():
            if rgetattr(event, old_name) and not math.isnan(rgetattr(event, old_name)):
                event_dict[new_name] = rgetattr(event, old_name)
            if not new_name in event_dict:
                event_dict[new_name] = ''

        # add current_polarities_CLIQ if provided
        if current_polarities_CLIQ:  event_dict['Quench_Protection.CLIQ.current_direction'] = current_polarities_CLIQ

        return event_dict

    def __write_analysis_QH(self, event: DataEventMagnet, dict_QH_circuits_to_QH_strips: Dict[str, List[int]],
                            t_before_QH_start: float = 0.05, t_earliest_starting_time: float = -2):
        """
        Extracts and writes the Quench Heater (QH) parameters for an event.

        Parameters:
        event: The event from which the Quench Heater parameters can be read.
        dict_QH_circuits_to_QH_strips: specifies to which groups the QH are attached to
        t_before_QH_start: Simulation time will be set to the earliest QH trigger minus this number [seconds].
        t_earliest_starting_time: Lower limit for the simulation start time, if QH trigger is earlier than that, this time will be used as simulation start time [seconds].

        Returns:
        event_dict: A dictionary containing the Quench Heater variable names (dict:key) and values (dict:value).
        """
        event_dict = dict()
        # if there are no Quench Heaters specified in .yaml file, ignore Quench Heater entries
        if len(dict_QH_circuits_to_QH_strips) == 0:
            if self.verbose: print('No values for dict_QH_circuits_to_QH_strips provided in ParsimEvent step definition. Ignoring Quench Heater Data.')
            return {}

        # Unpack QH data from event data
        dict_QH = event.QuenchProtection.Quench_Heaters

        # Initialize lists of QH-strip parameters that will be assigned to the STEAM model
        n_QH_strips = len(self.ref_model.model_data.Quench_Protection.Quench_Heaters.t_trigger)  # number of QH strips in the original STEAM model
        new_list_t_trigger = [None for i in range(n_QH_strips)]
        new_list_U0 = [None for i in range(n_QH_strips)]  # DOES NOT WORK: self.ref_model.model_data.Quench_Protection.Quench_Heaters.U0  # initialize to the values from the original STEAM model in case some strips are not set in this event
        new_list_C = [None for i in range(n_QH_strips)]
        new_list_R_warm = [None for i in range(n_QH_strips)]
        new_list_R_cold = self.__calculate_QH_R_cold()  # calculated using parameters from the original STEAM model

        # Assign values to the key "strip_per_circuit" that defines which strips are connected to which circuit
        for qh, qh_info in dict_QH.items():
            # Note: qh_info is a QuenchHeaterCircuit object containing information about one QH circuit
            list_QH_strips_connected_to_this_unit = dict_QH_circuits_to_QH_strips[qh]  # Note: this works correctly because the QH names (i.e. qh) are the same in the dict_QH and dict_QH_circuits_to_QH_strips dictionaries
            rsetattr(dict_QH[qh], 'strip_per_circuit', list_QH_strips_connected_to_this_unit)  # this is redundant and not needed, however it is done for consistency

            # Assign values to QH strips that are used in this event
            n_strips_current_unit = len(list_QH_strips_connected_to_this_unit)
            for j in list_QH_strips_connected_to_this_unit:
                R_cold = new_list_R_cold[j - 1]  # the resistance of the cold part of the QH strip is calculated for each strip from the reference BuilderModel
                new_list_t_trigger[j - 1] = qh_info.t_trigger
                new_list_U0[j - 1] = qh_info.U0 / n_strips_current_unit  # NOTE: assumption: the voltage is distributed equally across the strips
                new_list_C[j - 1] = qh_info.C * n_strips_current_unit  # NOTE: assumption: the voltage is distributed equally across the strips
                new_list_R_warm[j - 1] = qh_info.R_total / n_strips_current_unit - R_cold

        # Assign very high value (1E9 s) to QH trigger time for the QH strips that are NOT used in this event (this will effectively avoid triggering them in the simulation)
        event_dict['Quench_Protection.Quench_Heaters.t_trigger'] = [t if t != None else 1e9 for t in new_list_t_trigger]
        event_dict['Quench_Protection.Quench_Heaters.U0'] = [x if x != None else self.ref_model.model_data.Quench_Protection.Quench_Heaters.U0[i] for i, x in enumerate(new_list_U0)]
        event_dict['Quench_Protection.Quench_Heaters.C'] = [x if x != None else self.ref_model.model_data.Quench_Protection.Quench_Heaters.C[i] for i, x in enumerate(new_list_C)]
        event_dict['Quench_Protection.Quench_Heaters.R_warm'] = [x if x != None else self.ref_model.model_data.Quench_Protection.Quench_Heaters.R_warm[i] for i, x in enumerate(new_list_R_warm)]

        # make sure that the simulation time starts at least t_before_QH_start seconds before the start time of the first Quench Heater
        new_start_time = min(event_dict['Quench_Protection.Quench_Heaters.t_trigger']) - t_before_QH_start  # time of earliest QH trigger
        original_time_vector = self.ref_model.model_data.Options_LEDET.time_vector.time_vector_params
        if new_start_time < t_earliest_starting_time:  # if smaller than lower limit, use lower limit
            if self.verbose: print(f'Earliest QH triggers earlier than lower time limit for simulation time. Simulation start time will be set to lower limit {t_earliest_starting_time}.')
            new_start_time = t_earliest_starting_time
        if new_start_time > original_time_vector[2]: new_start_time = None  # do not change simulation start time when desired time is after the end of the first time interval
        if new_start_time:
            if self.verbose: print(f'Simulation start time adjusted to earliest QH trigger. Simulation will start at {new_start_time} instead of {original_time_vector[0]}')
            new_time_vector = [new_start_time] + original_time_vector[1:]  # just change first entry
            event_dict['Options_LEDET.time_vector.time_vector_params'] = new_time_vector
        else:
            if self.verbose: print('No start time for Quench Heaters found in csv file. Using default simulation time.')

        return event_dict

    def __calculate_QH_R_cold(self):  # TODO: put it in BuilderModel?
        f_SS = self.ref_model.model_data.Options_LEDET.physics.fScaling_RhoSS
        w_QH = self.ref_model.model_data.Quench_Protection.Quench_Heaters.w
        h_QH = self.ref_model.model_data.Quench_Protection.Quench_Heaters.h
        l_QH = self.ref_model.model_data.Quench_Protection.Quench_Heaters.l
        f_QH = self.ref_model.model_data.Quench_Protection.Quench_Heaters.f_cover
        rhoSS = 5.00E-07 * f_SS  # in [Ohm m]  # TODO use cfun?
        return [rhoSS / (w_QH[qh] * h_QH[qh]) * l_QH[qh] * f_QH[qh] for qh in range(len(w_QH))]


    def __read_general_parameters(self, event_info: pd.Series, new_event: DataEventMagnet, dict_attribute_to_column: Dict):
        '''
        Function to set GeneralParameters keys from data series into local DataEventMagnet class

        :param event_info: Series containing data of a read event
        :param new_event: DataEventMagnet object to update
        :param dict_attribute_to_column: dict with attribute name as key and list of possible column names as value
        :return: list of read columns
        '''

        for attr_name, list_col_names in dict_attribute_to_column.items():
            # check if only one column for the attribute can be found
            used_column_names = [entry for entry in list_col_names if entry in event_info]
            if len(used_column_names) == 1:
                # set attribute if only one column for this attribute can be found
                rsetattr(new_event, 'GeneralParameters.'+attr_name, event_info[used_column_names[0]])
            elif len(used_column_names) == 0:
                if self.verbose: print(f'No column for attribute "GeneralParameters.{attr_name}" found. Trying to parse list values.')
            else:
                raise ValueError(f"More than one column for the attribute 'GeneralParameters.{attr_name}' found: {used_column_names}.")

        # raise exception if no name column can be found in the input file
        if not new_event.GeneralParameters.name:
            raise Exception(f'No file name for the test could be found in the csv file. A column with one of the following keys should have a valid name: {dict_attribute_to_column["name"]}.')

        return list(dict_attribute_to_column.keys())

    def __read_powering(self, event_info: pd.Series, new_event: DataEventMagnet, dict_attribute_to_column: Dict):
        '''
        Function to set Powering keys from data series into local DataEventMagnet class

        :param event_info: Series containing data of a read event
        :param new_event: DataEventMagnet object to update
        :param dict_attribute_to_column: dict with attribute name as key and list of possible column names as value
        :return: list of read columns
        '''

        for attr_name, list_col_names in dict_attribute_to_column.items():
            # check if only one column for the attribute can be found
            used_column_names = [entry for entry in list_col_names if entry in event_info]
            if len(used_column_names) == 1:
                # set attribute if only one column for this attribute can be found
                rsetattr(new_event, 'Powering.'+attr_name, event_info[used_column_names[0]])
            elif len(used_column_names) == 0:
                if self.verbose: print(f'No column for attribute "Powering.{attr_name}" found. Trying to parse list values.')
            else:
                raise ValueError(f"More than one column for the attribute 'Powering.{attr_name}' found: {used_column_names}.")

        return list(dict_attribute_to_column.keys())

    def __read_CLIQ(self, event_info: pd.Series, new_event: DataEventMagnet, dict_attribute_to_column: Dict):
        '''
        Function to set CLIQ keys from data series into local DataEventMagnet class

        :param event_info: Series containing data of a read event
        :param new_event: DataEventMagnet object to update
        :param dict_attribute_to_column: dict with attribute name as key and list of possible column names as value
        :return: list of read columns
        '''

        for attr_name, list_col_names in dict_attribute_to_column.items():
            # check if only one column for the attribute can be found
            used_column_names = [entry for entry in list_col_names if entry in event_info]
            if len(used_column_names) == 1:
                # set attribute if only one column for this attribute can be found
                rsetattr(new_event, attr_name, event_info[used_column_names[0]])
            elif len(used_column_names) == 0:
                if self.verbose: print(f'No column for attribute "{attr_name}" found. Trying to parse list values afterwards.')
            else:
                raise ValueError(f"More than one column for the attribute '{attr_name}' found: {used_column_names}.")

        # If these scalars are not set, try alternative reading method based on a list
        dict_list_params = {'CLIQ event Time [s]': 'QuenchProtection.CLIQ.t_trigger',  #TODO better handling of multiple values in one column: e.g. user could say the pairs of name-value columns and we read them correctely, in event_column_names.yaml we could then use the variable name found in the table entry
                          'CLIQ event Value': 'QuenchProtection.CLIQ.U0'}

        for key, dest_attr in dict_list_params.items():
            if not rgetattr(new_event, dest_attr):
                if key in event_info:
                    if event_info[key] == event_info[key]:
                        # Take the first value of the selected column (hard-coded behavior)
                        rsetattr(new_event, dest_attr, [float(num_as_str.strip(' ')) for num_as_str in event_info[key].split(';')][0])

        return list(dict_attribute_to_column.keys()) + list(dict_list_params.keys())


    def __read_QH(self, event_info: pd.Series, new_event: DataEventMagnet, rel_quench_heater_trip_threshold: float):
        '''
        Function to set Quench Heater (QH) parameters from data series into local DataEventMagnet class

        :param event_info: Series containing data of a read event
        :param new_event: DataEventMagnet object to update.
        :param rel_quench_heater_trip_threshold: Threshold value for QH voltage, expressed as a fraction of the initial charging voltage QH.U0
        :return: list of read columns
        '''

        # Check that the QH key exists in the input file
        key_QH_names = 'QH Name'
        if not key_QH_names in event_info:
            print(f'The key "{key_QH_names}" was not found in the input file. Quench heaters will not be set.')
            return []
        elif (type(event_info[key_QH_names]) == float) and (math.isnan(event_info[key_QH_names])):
            print(f'The key "{key_QH_names}" is empty. Quench heaters will not be set for this event.')
            return []
        else:
            list_QH_circuits = [num_as_str.strip(' ') for num_as_str in event_info[key_QH_names].split(';')]  # list of QH circuits

        # This is the dictionary of all the keys that can be parsed
        dict_params = {
            'QH Start time [s]'  : 't_trigger',
            'QH Voltage [V]'     : 'U0',
            'QH Capacitance [F]' : 'C',
            'QH Resistance [Ohm]': 'R_total',
            }

        column_names = list(dict_params.keys())

        # Remove the keys that are not present in the event information input file
        dict_params = {key: value for key, value in dict_params.items() if key in event_info}

        # Remove the keys that are present in the event information input file, but have empty value
        dict_params = {key: value for key, value in dict_params.items() if event_info[key] == event_info[key]}

        # Make QH circuit dictionary. Each key is a QH circuit
        dict_QH = {key: QuenchHeaterCircuit() for key in list_QH_circuits}

        # Add values to QH circuit parameters
        for param in dict_params:
            if (type(event_info[param]) == float) or (type(event_info[param]) == int):
                list_values = [event_info[param]]
            else:
                list_values = [float(num_as_str.strip(' ')) for num_as_str in event_info[param].split(';')]
            if len(list_QH_circuits) != len(list_values):
                raise Exception(f'The key "{key_QH_names}" has {len(list_QH_circuits)} values, while the key "{param}" has {len(list_values)} values.')
            for qh, qh_unit in enumerate(list_QH_circuits):
                rsetattr(dict_QH[qh_unit], dict_params[param], list_values[qh])

        # correct the measured trigger time by interpolating the discharge curve (U(t) = U * e^(-(t+T)/tau)) back in time
        # to measure the start time, a threshold is used. The real trigger time is therefore earlier.
        if rel_quench_heater_trip_threshold is not None:
            for QH_name, QH in dict_QH.items():
                # Calculate the time constant for the discharge
                tau = QH.C * QH.R_total
                # Calculate the corrected voltage based on the relative trip threshold
                U_corrected = QH.U0 / rel_quench_heater_trip_threshold
                # calculate time difference: U_meas(t_meas)/U_correct(t_corrected) = rel_quench_heater_trip_threshold
                delta_t = math.log(U_corrected / QH.U0) * tau  # delta_t = t_meas-t_corrected
                # Update the voltage of the quench heater and the trigger time with the corrected values
                if self.verbose: print(f'Corrected QuenchHeater trigger time from {QH.t_trigger} to {QH.t_trigger - delta_t} and U0 from {QH.U0} to {U_corrected}.')
                QH.t_trigger = QH.t_trigger - delta_t
                QH.U0 = U_corrected
            del U_corrected, delta_t, QH_name, QH

        # Add QH circuit dictionary to the event data
        rsetattr(new_event, 'QuenchProtection.Quench_Heaters', dict_QH)

        return column_names + ['QH Name']


    def __read_signals_of_configs(self, default_configs, path_config_file: str):
        '''
            Reads signal data from a YAML configuration file and returns a dictionary of the unique signals for each specified configuration.

            Args:
                default_configs (str or list): Names of the configurations to retrieve signal data for.
                path_config_file (str): Path to the YAML configuration file.

            Returns:
                dict: A dictionary containing the unique signal data for each specified configuration.
                      The keys of the dictionary are the names of the configurations, and the values are lists of unique signals.
        '''
        # Open the YAML file and read its contents into a string variable
        with open(path_config_file, "r") as f:
            yaml_string = f.read()
        # Parse the YAML string into a Python dictionary using the load() method from the PyYAML library
        dict_configs = yaml.load(yaml_string, Loader=yaml.FullLoader)

        # Initialize a dictionary, keys are the names of the specified configurations
        dict_configs_with_signals = {config: [] for config in default_configs}

        # Loop through the specified configurations
        for config in default_configs:
            # check if specified config name is valid
            if config not in dict_configs['ConfigurationList'].keys():
                raise Exception(f'The configuration {config} is not defined in the configurations file {path_config_file}.')
            # Loop through each signal in the 'SignalList' for the configuration
            for signal in dict_configs['ConfigurationList'][config]['SignalList'].values():
                # both 'meas_signals_to_add_x' and 'meas_signals_to_add_y' have to be present in the measurement file
                if 'meas_signals_to_add_x' in signal:
                    dict_configs_with_signals[config].extend(signal['meas_signals_to_add_x'])
                if 'meas_signals_to_add_y' in signal:
                    dict_configs_with_signals[config].extend(signal['meas_signals_to_add_y'])
            # only store the unique values
            dict_configs_with_signals[config] = list(set(dict_configs_with_signals[config]))
        del yaml_string, dict_configs

        # check if config has been read correctly (at least one configuration has a list of measurement names)
        if all(value == [] for value in dict_configs_with_signals.values()):
            raise Exception(f'No valid configuration found in configurations file {path_config_file}')

        return dict_configs_with_signals
    


    def __get_config_tdms(self, path_tdms_files, campaign_name, file_name, dict_configs_with_signals, verbose):
        """
        Read the TDMS file specified by the `path_tdms_files`, `campaign_name` and `file_name` arguments
        using the ParserTdms class to make a list of all the measurement signal names present in the TDMS file.
        The function returns the most advanced configuration by using the get_most_advanced_viewer_config function.

        :param path_tdms_files: A string representing the path to the TDMS folder.
        :param campaign_name: A string representing the name of the campaign.
        :param file_name: A string representing the name of the TDMS file to be found.
        :param dict_configs_with_signals: A dictionary holding all configurations (keys) and their needed signals (values).
        :param verbose: A boolean indicating whether to print verbose output.
        :return: name of the most advanced viewer configuration.
        """
        # define full path
        full_path = Path(os.path.join(path_tdms_files, campaign_name, file_name + '.tdms')).resolve()

        # init list
        list_meas_signals = []

        # for each group (LF, MF, HF) there can be different signals, dict keys are groups and values respective signals
        dict_meas_signals_with_groups = ParserTdms(Path(full_path)).getNames()[2]

        # loop through the dict
        for group, signal_list in dict_meas_signals_with_groups.items():
            # append the group name with the signal name and a . in between, as in the tdms files
            for signal in signal_list:
                list_meas_signals.append(group + '.' + signal)
            # the time is not in signal list from the .getNames() function and has to be added here
            list_meas_signals.append(group + '.Time [s]')

        return self.__get_most_advanced_viewer_config(dict_configs_with_signals, list_meas_signals, file_name, verbose=verbose)

    def __get_config_csv(self, path_parent_dir, campaign_name, file_name, dict_configs_with_signals, verbose):
        """
        Read all the signals present in a csv measurement file and return the most advanced configuration
        by using the get_most_advanced_viewer_config function.

        :param path_parent_dir: A string representing the path to the folder with all the campaigns in it.
        :param campaign_name: A string representing the name of the campaign to look for csv files.
        :param file_name: A string representing the name of the csv file.
        :param dict_configs_with_signals: A dictionary containing the configurations with signals.
        :param verbose: A boolean indicating whether to print verbose output.
        :return: name of the most advanced viewer configuration.
        """
        # Initialization of list to store measurement signals
        list_meas_signals = []

        # Loop over campaign names and file names to get full path of csv file and extract signal names
        for suffix in ["MF", "HF", "LF"]:
            full_path = Path(os.path.join(path_parent_dir, campaign_name, file_name + '_' + suffix + '.csv')).resolve()
            if os.path.isfile(full_path):
                # read all the names of the columns (=names of the present signals)
                csv_header = pd.read_csv(full_path, nrows=1).columns.tolist()

                # Append the suffix to the header names
                csv_header = [suffix + '.' + header_name for header_name in csv_header]

                # Append the signal names to the list
                list_meas_signals = list_meas_signals + csv_header

        # Call the function to get the most advanced configuration
        return self.__get_most_advanced_viewer_config(dict_configs_with_signals, list_meas_signals, file_name, verbose=verbose)


    def __get_most_advanced_viewer_config(self, dict_configs_with_signals, list_meas_signals, filename, verbose):
        """
        Return the configuration name of the first dict where all signal names in its list of values are present in `list_meas_signals`.

        :param dict_configs_with_signals: A dictionary with configuration names as keys and lists of signal names as values - Ordered from most advanced to least advanced.
        :param list_meas_signals: A list of signal names found in tdms/csv measurement files.
        :param filename: A string representing the name of the measurement file.
        :param verbose: A boolean indicating whether to print verbose output.
        :return: A string representing the most advanced viewer configuration.
        """
        #
        if dict_configs_with_signals == {}: raise Exception(f'No configurations specified.')

        # check for the configurations if all the needed signals are present and return the most advanced one
        for config_name, signal_list in dict_configs_with_signals.items():
            # check whether all the signal names in the configuration's list are present in the measurement signal list
            if set(signal_list).issubset(set(list_meas_signals)):
                # if all the signal names are present, return the configuration name
                if verbose: print(f'{filename}: configuration {config_name} is used.')
                return config_name
            else:
                # print missing signals and skip to the next configuration
                missing_signals = set(signal_list).difference(set(list_meas_signals))
                if verbose: print(f'{filename}: configuration {config_name} skipped. Could not find {missing_signals}')

        # if no valid configuration could be found, raise an exception with an error message indicating the missing signals for the simplest configuration
        if config_name and missing_signals:
            raise Exception(f'No valid configuration could be found for measurement {filename}.\n'
                            f'Missing signals for simplest configuration {config_name}: {missing_signals}')
        else:
            raise Exception(f'No valid configuration could be found for measurement {filename}.')


def remove_frequency_suffix(name_file_found_csv):
    """
    Removes a frequency suffix ("_MF", "_HF", "_LF") from the end of a file name if existing
    """
    for suffix in ["_MF", "_HF", "_LF"]:
        if name_file_found_csv.endswith(suffix):
            name_file_found_csv = name_file_found_csv[:-len(suffix)]
    return name_file_found_csv


def search_file_in_subfolders(timestamp, path_to_parent_dir, datatype):
    """
    Search for a file in subfolders of a given directory.

    :param timestamp: A string of integer sequences (timestamp) to search for in the file names.
    :param path_to_parent_dir: The path to the parent directory.
    :param datatype: The file extension to search for.

    :return: A tuple containing the names of the subfolders the file was found in, and the name of the file without the extension.
             If the file is not found, both elements will be empty.
    """
    # if no path for the folder to search in is provided, don't search and return None
    if path_to_parent_dir == '':
        return None, None

    # check for datatypes
    supported_filetypes = ['.tdms', '.csv']
    if datatype not in supported_filetypes:
        raise Exception(f'Datatype {datatype} not supported for measurement files.')

    # initialize lists to store subfolder names and file names
    list_campaign_names, list_file_names = [], []

    # get the names of all subfolders
    subfolders = [os.path.basename(f.path) for f in os.scandir(path_to_parent_dir) if f.is_dir()]

    # loop through all subfolders and search for file with given integer sequences and datatype
    for subfolder in subfolders:
        # list with all filesnames in the subfolder
        list_files = os.listdir(os.path.join(path_to_parent_dir, subfolder))
        for file in list_files:
            # check for every file if it has given datatype and contains the integer sequences in its name
            if file.endswith(datatype) and timestamp in file:
                list_campaign_names.append(subfolder)  # add subfolder name to list of subfolders where file was found
                list_file_names.append(
                    file.split(datatype)[0])  # add file name without extension to list of file names found

    # evaluate names of files that have been found
    campaign_name, name_file_found = None, None
    # for tdms files only one file should be found
    if datatype == supported_filetypes[0]:
        if len(list_campaign_names) == 1:
            campaign_name, name_file_found = list_campaign_names[0], list_file_names[0]
        elif len(list_campaign_names) > 1:
            raise Exception(f'More than one tdms file with the specified timestamp found: {list_file_names}')
    # for csv files a timestamp can be found multiple times (e.g. meas2210051743_MF.csv and meas2210051743_HF.csv)
    elif datatype == supported_filetypes[1]:
        list_file_names = [remove_frequency_suffix(name) for name in list_file_names]
        if len(list_campaign_names) == 1:
            campaign_name, name_file_found = list_campaign_names[0], list_file_names[0]
        elif len(list_campaign_names) > 1:
            # check if names without the frequency suffix are the same
            if all(element == list_file_names[0] for element in list_file_names):
                campaign_name, name_file_found = list_campaign_names[0], list_file_names[0]
            else:
                raise Exception(
                    f'More than one csv file with the specified timestamp found: {list_file_names}')

    # return tuple with lists of subfolder and file names
    return campaign_name, name_file_found
