import csv
import math
import os
import warnings
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import steammaterials
import yaml
from scipy.optimize import fsolve
from steammaterials.STEAM_materials import STEAM_materials

from steam_sdk.data.DataAnalysis import StrandCriticalCurrentMeasurement
from steam_sdk.data.DataConductor import Conductor
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataParsimConductor import ConductorSample
from steam_sdk.data.DataParsimConductor import DataParsimConductor, IcMeasurement, Coil, StrandGeometry
from steam_sdk.parsers.ParserMap2d import ParserMap2dFile
from steam_sdk.utils.correct_RRR_NIST import correct_RRR_NIST
from steam_sdk.utils.get_attribute_type import get_attribute_type
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.parse_str_to_list import parse_str_to_list
from steam_sdk.utils.rhasattr import rhasattr
from steam_sdk.utils.sgetattr import rsetattr, rgetattr


class ParsimConductor:
    """
    class to assist running a ParsimConductor step

    This class is used to:
     - read_from_input: reading input table where every row represents one coil of a magent
     - write_conductor_parameter_file: calculates all conductor parameters to change and writes them in a csv file for a ParsimSweeper step
    """

    def __init__(self, path_input_dir: Path, model_data: DataModelMagnet, groups_to_coils: Dict[str, List[int]],
                 length_to_coil: Dict[str, float], dict_coilName_to_conductorIndex: Dict[str, int],
                 verbose: bool = True):
        '''
        Initializes the ParsimConductor with the required input data and configurations.

        :param path_input_dir: The path of the magnet directory in steam_models
        :param model_data: The original model data of the magnet
        :param groups_to_coils: A dictionary mapping coil name (key) to their respective groups (values).
        :param length_to_coil: A dictionary mapping coil names to their lengths (if None or empty, length will be optimized - if coil length is known, fraction of copper will be optimized)
        :param dict_coilName_to_conductorIndex: A dictionary mapping coil names to their respective conductor indices in BuilderModel
        :param verbose: A boolean indicating whether to display additional information (default is True).
        '''
        # Unpack arguments
        self.verbose: bool = verbose
        self.model_data = model_data
        self.path_input_dir = path_input_dir
        self.dict_coilName_to_conductorIndex = dict_coilName_to_conductorIndex
        self.groups_to_coils = groups_to_coils
        self.number_of_groups = max([max(values) for values in self.groups_to_coils.values()])

        # length_to_coil is either empty/None (coil_length will be optimized) or filled with {coilname: length} (fCu will be optimized)
        if length_to_coil is None: length_to_coil = {}  # optimize coillength if not specified by the user
        if not isinstance(length_to_coil, dict):
            raise Exception(
                f'length_to_coil parameter of ParsimConductor step has to be a dict! Leave it empty if you dont know the values, otherwise specify the length for every coil.')
        if length_to_coil != {}:
            if not set(groups_to_coils.keys()) == set(length_to_coil.keys()):
                raise Exception(
                    f'Coils of input dictionaries dont have the same names.\ngroups_to_coils= {groups_to_coils.keys()}\nlength_to_coil= {length_to_coil.keys()}')
        self.length_to_coil = length_to_coil

        # check input: coil names in the input dicts have to be the same
        if not set(groups_to_coils.keys()) == set(dict_coilName_to_conductorIndex.keys()):
            raise Exception(
                f'Coils of input dictionaries dont have the same names.\ngroups_to_coils= {groups_to_coils.keys()}\ndict_coilName_to_conductorIndex= {dict_coilName_to_conductorIndex.keys()}')

        # DataParsimConductor object that will hold all the information from the input csv file when reading it
        self.data_parsim_conductor = DataParsimConductor()

    def read_from_input(self, path_input_file: str, magnet_name: str,
                        strand_critical_current_measurements: List[StrandCriticalCurrentMeasurement]):
        '''
        Reads a .csv or .xlsx file containing magnet and coil data, and assigns its content to an instance of DataParsimConductor.

        :param path_input_file: The path to the .csv or .xlsx file to read.
        :param magnet_name: The name of the magnet for which data should be processed.
        :param strand_critical_current_measurements: A dictionary containing the critical current measurements details specified by the user.
        '''
        def converter_func(val):
            # When there is one string in a column, empty elements are read as '' by read_csv, whereas read_excel reads them as NA values
            if val == '': return pd.NA
            # When there is one string in a column, float elements are read as '190' by read_csv, whereas read_excel reads them as floats
            try: return float(val)
            except ValueError: return val

        # read table into pandas dataframe
        if path_input_file.endswith('.csv'):
            # read_csv does not read a table the same way read_excel does. The main difference is that read_csv reads every
            # value in a column with the same data type, whereas read_excel uses different data types for different values.
            # To ensure that the datatypes are identical for later processing, a converter_func for read_csv is introduced.
            converters = {col: converter_func for col in pd.read_csv(path_input_file, nrows=0).columns.tolist()}
            df_coils = pd.read_csv(path_input_file, converters=converters)
        elif path_input_file.endswith('.xlsx'):
            df_coils = pd.read_excel(path_input_file)
        else:
            raise Exception(f'The extension of the file {path_input_file} is not supported. Use either csv or xlsx.')
        df_coils = df_coils.dropna(axis=1, how='all')

        # read dict for reading columns into local dataclass
        # to add new column names the code does not have to be changed, just add the new colunm names to this yaml file
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translation_dicts",
                                 "conductor_column_names.yaml")
        with open(yaml_path, 'r') as file:
            # this dict now holds the attribute names as keys and a list of possible column names as values
            dict_attribute_to_column = yaml.safe_load(file)

        # set magnet name to local model
        rsetattr(self.data_parsim_conductor, 'GeneralParameters.magnet_name', magnet_name)

        # get column name of coil and magnet
        parsed_columns = []  # list containing the column names that were parsed
        column_name_magnets, column_name_coils = self.__read_and_check_main_column_names(df_coils, parsed_columns,
                                                                                         dict_attribute_to_column[
                                                                                             'MainColumnNames'])

        # delete all rows of dataframe that don't belong to the magnet
        mask = df_coils[
                   column_name_magnets] != magnet_name  # create a boolean mask for the rows that do not have the value in the column
        df_coils = df_coils.drop(df_coils[mask].index)  # drop the rows that do not have the value in the column

        # Assign the content to a dataclass structure - loop over all the coils of the magnet in the database
        for _, row in df_coils.iterrows():
            # in case coilname is only a number, convert it to str
            if isinstance(row[column_name_coils], (int, float)): row[column_name_coils] = str(row[column_name_coils])
            # if the coil name is not present in the userinput dictionary, don't read it
            if row[column_name_coils] not in self.dict_coilName_to_conductorIndex.keys():
                warnings.warn(
                    f'The coil {row[column_name_coils]} is present in the conductor database but is not used.')
                continue
            self.__read_magnet(row, column_name_coils, parsed_columns)
            self.__read_coils(row, column_name_coils, parsed_columns, dict_attribute_to_column['Coil'])
            self.__read_conductors(row, column_name_coils, parsed_columns, strand_critical_current_measurements,
                                   dict_attribute_to_column['ConductorSample'])

        # check if all needed coils could be found in the conductor database
        for need_coil_name in self.dict_coilName_to_conductorIndex.keys():
            if need_coil_name not in self.data_parsim_conductor.Coils.keys():
                raise Exception(
                    f'The coil {need_coil_name} for the magnet {magnet_name} could not be found in the conductor database. Please check the input dictionaries.')

        # show the user all the columns that where ignored by the code
        ignored_column_names = list(set(df_coils.columns) - set(parsed_columns))
        if self.verbose: print(f'Names of ignored columns: {ignored_column_names}')

    def write_conductor_parameter_file(self, path_output_file: str, simulation_name: str, simulation_number: int,
                                       rel_warning_limit: float = 0.1):
        """
        Calculates and writes the conductor parameters to change from the DataParsimConductor instance to a csv file
        for running a ParsimSweep step.

        :param path_output_file: The path to the output file
        :param simulation_name: The name of the simulation
        :param simulation_number: The number of the simulation
        :param rel_warning_limit: function raises warning in console when values are changed for more/less then this relative value
        """

        # Make target folder if it is missing
        make_folder_if_not_existing(os.path.dirname(path_output_file))

        # save all conductor parameters in a dict
        dict_sweeper = dict()
        dict_sweeper['simulation_name'] = simulation_name
        dict_sweeper['simulation_number'] = int(simulation_number)

        # write all the ConductorSample data to
        if self.length_to_coil != {}:
            # if groups_to_coil_length is specified, optimize the fraction of superconductor
            self.__write_parsweep_conductors(dict_sweeper, flag_optimize_fCu=True, rel_warning_limit=rel_warning_limit)
        else:
            # if no groups_to_coil_length is specified, optimize the length of the magnet
            self.__write_parsweep_conductors(dict_sweeper, flag_optimize_fCu=False, rel_warning_limit=rel_warning_limit)
            self.__write_parsweep_optimized_ht_length(dict_sweeper)

        # open file in writing mode and write the dict of the parameters as a row in the sweeper csv file
        with open(path_output_file, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=dict_sweeper.keys())
            writer.writeheader()
            writer.writerow(dict_sweeper)

    ################ HELPERS

    def __read_and_check_main_column_names(self, df_coils: pd.DataFrame, parsed_columns: List[str],
                                           dict_attr_to_colname: Dict[str, List[str]]):
        '''
        function checking the main columns "magnet name" and "coil name" and returning their column name

        :param df_coils: dataframe where every row represents one coil
        :param parsed_columns: A list of column names that have already been parsed (parsed columns are added)
        :param dict_attr_to_colname: A dictionary mapping attribute names of the coil (key) to possible column names (values)
        '''
        # allowed names for the magnet
        csv_column_names_for_magnet_name = dict_attr_to_colname['magnet_name']
        csv_column_names_for_coil_name = dict_attr_to_colname['coil_name']

        # find out what name is being used for the magnet and coil column
        column_name_magnets, column_name_coils = None, None
        for col_name_magnet in csv_column_names_for_magnet_name:
            if col_name_magnet in df_coils.keys():
                column_name_magnets = col_name_magnet
        for col_name_coil in csv_column_names_for_coil_name:
            if col_name_coil in df_coils.keys():
                column_name_coils = col_name_coil

        # check if there is a column for magnet and coil
        if not column_name_magnets:
            raise Exception(
                f'No column for the magnet name could be found in the input table. Make sure this column is present.\nAllowed values :{csv_column_names_for_magnet_name}')
        if not column_name_coils:
            raise Exception(
                f'No column for the coil names could be found in the input table. Make sure this columns are present.\nAllowed values:{csv_column_names_for_coil_name}')

        # check if magnet name is present in the xlsx file
        if not any(df_coils[column_name_magnets] == self.data_parsim_conductor.GeneralParameters.magnet_name):
            raise Exception(
                f'The magnet "{self.data_parsim_conductor.GeneralParameters.magnet_name}" is not present in the conductor database. Please change the GeneralParameters.model.name in the analysis input file.')

        # mark columns as parsed
        parsed_columns.append(column_name_magnets)
        parsed_columns.append(column_name_coils)

        return column_name_magnets, column_name_coils

    def __read_magnet(self, row: pd.Series, column_name_coils: str, parsed_columns: List[str]):
        '''
        Adds the coil name from the given row to the Magnet's list of coils in the DataParsimConductor instance.

        :param row: A pandas Series object representing a row in the input table where a row is a coil of the magnet
        :param column_name_coils: The name of the column containing the coil names in the input table
        :param parsed_columns: A list of column names that have already been parsed (parsed columns are added)
        '''
        # add coil name to Coils list
        self.data_parsim_conductor.Magnet.coils.append(row[column_name_coils])

    def __read_coils(self, row: pd.Series, column_name_coils: str, parsed_columns: List[str],
                     dict_attr_to_colname: Dict[str, List[str]]):
        '''
        Reads coil related data for a row in the table into a new Coil instance, and adds it to the DataParsimConductor instance

        :param row: A pandas Series object representing a row in the input table where a row is a coil of the magnet
        :param column_name_coils: The name of the column containing the coil names in the input table
        :param parsed_columns: A list of column names that have already been parsed (parsed columns are added)
        :param dict_attr_to_colname: A dictionary mapping attribute names of the coil (key) to possible column names (values)
        '''
        # create new coil instance
        coil_name = row[column_name_coils]
        new_Coil = Coil()

        # change parameters of coil instance according to yaml translation file
        for attribute_name, column_names in dict_attr_to_colname.items():
            # check if only one column for the attribute can be found
            used_column_names = [entry for entry in column_names if entry in row]
            if len(used_column_names) == 1:
                used_column_name = used_column_names[0]
            elif len(used_column_names) == 0:
                warnings.warn(f'No column for Coil attribute "{attribute_name}" found.')
                continue
            else:
                raise ValueError(f"More then one column for the ConductorSample attribute '{attribute_name}' found.")

            # extract unit of the value from the column name - unit is given in squared brackets (e.g. "voltage [V]")
            dim = used_column_name[
                  used_column_name.find('[') + 1:used_column_name.find(']')] if '[' in used_column_name else ''
            # check if value is set in csv file
            if not pd.isna(row[used_column_name]):
                # if input is a float list in string format, parse it into a float list
                if get_attribute_type(new_Coil, attribute_name) == List[float]:
                    if isinstance(row[used_column_name], str):
                        float_list = parse_str_to_list(row[used_column_name], only_float_list=True)
                    else:
                        float_list = [row[used_column_name]]
                    rsetattr(new_Coil, attribute_name, [make_value_SI(val, dim) for val in float_list])
                else:
                    # change parameter and convert number into SI unit
                    rsetattr(new_Coil, attribute_name, make_value_SI(row[used_column_name], dim))
                # mark column as parsed
                if used_column_name not in parsed_columns: parsed_columns.append(used_column_name)

        # normalize weight factors if not normalized
        if new_Coil.weight_factors and sum(new_Coil.weight_factors) != 1.0:
            weight_sum = sum(new_Coil.weight_factors)
            new_Coil.weight_factors = [w / weight_sum for w in new_Coil.weight_factors]

        # add new coil to local DataParsimConductor dataclass
        self.data_parsim_conductor.Coils[coil_name] = new_Coil

    def __read_conductors(self, row: pd.Series, column_name_coils: str, parsed_columns: List[str],
                          strand_critical_current_measurements: List[StrandCriticalCurrentMeasurement],
                          dict_attr_to_colname: Dict[str, List[str]]):
        '''
        Reads conductor related data for a row in the table into ConductorSample instances and adds them to the corresponding Coil instance.

        :param row: A pandas Series object representing a row in the input table where a row is a coil of the magnet
        :param column_name_coils: The name of the column containing the coil names in the input table
        :param parsed_columns: A list of column names that have already been parsed (parsed columns are added)
        :param strand_critical_current_measurements: A dictionary of critical current measurements provided by the user
        :param dict_attr_to_colname: A dictionary mapping attribute names of the conductor samples (key) to possible column names (values)
        '''
        coil_name = row[column_name_coils]

        # read how many conductor samples there are in the database for this coil
        n_conductor_samples_found = []
        all_col_names = [string for string_list in dict_attr_to_colname.values() for string in string_list]
        # add column names for Ic measurements
        for meas in strand_critical_current_measurements:
            if coil_name in meas.coil_names:
                all_col_names.append(meas.column_name_I_critical)
                all_col_names.append(meas.column_name_CuNoCu_short_sample)
        for col_name in all_col_names:
            if col_name in row and not pd.isna(row[col_name]) and isinstance(row[col_name], str):
                float_list = parse_str_to_list(row[col_name], only_float_list=True)
                n_conductor_samples_found.append(len(float_list))
        if all(element == n_conductor_samples_found[0] for element in n_conductor_samples_found):
            if len(n_conductor_samples_found) == 0:
                n_conductor_samples = 1
            else:
                n_conductor_samples = n_conductor_samples_found[0]
        else:
            raise Exception(f'Different number of Conductor Samples found for Coil "{coil_name}".')

        # check length of weight factors
        if self.data_parsim_conductor.Coils[coil_name].weight_factors:
            if len(self.data_parsim_conductor.Coils[coil_name].weight_factors) != n_conductor_samples:
                raise Exception(
                    f'Length of weight factor for coil {coil_name} is not similar to number of Conductor samples. Please correct the length to {n_conductor_samples} or delete entry (the average of the values will then be calculated)')

        # create ConductorSample instances for every conductor sample
        new_Conductors = [ConductorSample() for _ in range(n_conductor_samples)]

        # read the critical current measurements into instances of the local conductor sample dataclasses
        for meas in strand_critical_current_measurements:
            # raise error when col name of IcMeasurement is in translation dictionary (meaning it is already used)
            for attr_name, col_names in dict_attr_to_colname.items():
                if meas.column_name_I_critical in col_names:
                    raise Exception(
                        f'Invalid column name for I_critical. "{meas.column_name_I_critical}" already used for the attribute "{attr_name}". Please change.')
                if meas.column_name_CuNoCu_short_sample in col_names:
                    raise Exception(
                        f'Invalid column name for I_critical. "{meas.column_name_CuNoCu_short_sample}" already used for the attribute "{attr_name}". Please change.')

            if coil_name in meas.coil_names:
                # create new IcMeasurement instances, add all values and append it to the measurement list of the conductor
                new_Ic_measurements = [IcMeasurement() for _ in range(n_conductor_samples)]
                # add temperature and magnetic flux of the measurements (directly given in step definition)
                for Ic_meas in new_Ic_measurements:
                    rsetattr(Ic_meas, 'B_ref_Ic', meas.reference_mag_field)
                    rsetattr(Ic_meas, 'T_ref_Ic', meas.reference_temperature)
                # read critical current form csv file
                if meas.column_name_I_critical in row and not pd.isna(row[meas.column_name_I_critical]):
                    setattr_to_list(new_Ic_measurements, row, meas.column_name_I_critical, 'Ic')
                else:
                    raise Exception(
                        f'Provided column name for Ic measurement "{meas.column_name_I_critical}" was not found in the conductor database or is empty for coil {coil_name}.')
                # read CuNoCu ratio of the short sample measurement
                if meas.column_name_CuNoCu_short_sample in row and not pd.isna(
                        row[meas.column_name_CuNoCu_short_sample]):
                    setattr_to_list(new_Ic_measurements, row, meas.column_name_CuNoCu_short_sample, 'Cu_noCu_sample')
                else:
                    raise Exception(
                        f'Provided coulumn name for Ic measurement "{meas.column_name_CuNoCu_short_sample}" was not found in the conductor database or is empty.')
                # append the new Ic measurements to a conductor sample
                for cond, Ic_meas in zip(new_Conductors, new_Ic_measurements):
                    cond.Ic_measurements.append(Ic_meas)

        # change parameters of conductors instance according to yaml translation file
        for attribute_name, column_names in dict_attr_to_colname.items():
            # check if only one column for the attribute can be found
            used_column_names = [entry for entry in column_names if entry in row]
            if len(used_column_names) == 1:
                used_column_name = used_column_names[0]
            elif len(used_column_names) == 0:
                warnings.warn(f'No column for ConductorSample attribute "{attribute_name}" found.')
                continue
            else:
                raise ValueError(f"More then one column for the ConductorSample attribute '{attribute_name}' found.")

            # check if value is set in csv file and set it to all the conductor instances
            if not pd.isna(row[used_column_name]):
                setattr_to_list(new_Conductors, row, used_column_name, attribute_name)
            # mark column as parsed
            if used_column_name not in parsed_columns: parsed_columns.append(used_column_name)

        # check if only either diameter or bare w/h is set and check if original conductor type is the right one
        original_conductor_type = self.model_data.Conductors[
            self.dict_coilName_to_conductorIndex[coil_name]].strand.type
        if not original_conductor_type: raise Exception(
            f'Strand type of conductor for coil {coil_name} is not specified in modelData.')
        for cond in new_Conductors:
            if original_conductor_type == 'Round':
                if cond.strand_geometry.bare_width or cond.strand_geometry.bare_height:
                    raise Exception(f'Tried to change bare with/height of Round conductor in coil {coil_name}')
            elif original_conductor_type == 'Rectangular':
                if cond.strand_geometry.diameter:
                    raise Exception(f'Tried to change diameter of Rectangular conductor in coil {coil_name}')
            else:
                raise Exception(f'Unknown conductor type {original_conductor_type} for coil {coil_name}.')

        # append new conductor instance to Conductors dictionary of ParsimConductor
        self.data_parsim_conductor.Coils[coil_name].conductorSamples = new_Conductors

    def __write_parsweep_optimized_ht_length(self, dict_sweeper: Dict[str, Any]):
        """
        Optimizes the half-turn length for each conductor sample in each coil and calculates the average for each group.

        :param dict_sweeper: The dictionary where the optimized half-turn length will be stored, in the format {attributeNameDataModelMagnet: newValue}
        """
        ht_len = [0.0 for _ in range(self.number_of_groups)]

        # looping through the coils
        for coil_name, coil in self.data_parsim_conductor.Coils.items():
            if not coil.coil_resistance_room_T:
                warnings.warn(
                    f'No room temperature resistance measurement for coil "{coil_name}" was found in database. Using default value for half_turn_length from modelData.')
                continue
            original_conductor = self.model_data.Conductors[self.dict_coilName_to_conductorIndex[coil_name]]
            # calculate the optimized coil length for every group in the conductor sample separately
            for sample in coil.conductorSamples:
                # optimize the length for this coil with one conductor
                L = self.__calculate_coil_length_with_resistance_meas(sample, coil_name, original_conductor, coil)
                # for every conductorSamples add the optimized lengths together (to later make the average)
                for group_number in self.groups_to_coils[coil_name]:
                    ht_len[group_number - 1] = ht_len[group_number - 1] + L
            # divide the sum of all the length with the number of conductorSamples do get the average value
            for index in self.groups_to_coils[coil_name]:
                ht_len[index - 1] = ht_len[index - 1] / len(coil.conductorSamples)

        # if half_turn_length from modelData has correct length, and some values in ht_len were calculated, combine the 2
        ht_len_modelData = self.model_data.CoilWindings.half_turn_length
        if ht_len_modelData and len(ht_len_modelData) == self.number_of_groups and any(l != 0.0 for l in ht_len):
            # use the values from modelData if no value could be calculated
            ht_len = [ht_len_modelData[i] if ht_len[i] == 0.0 else ht_len[i] for i in range(len(ht_len))]

        # if some values could not be calculated or been taken from modeldata, inform the user that calculation was skipped
        if any(l in [None, 0.0] for l in ht_len):
            warnings.warn(
                f'Length optimization was skipped. Not all ht lengths could be calculated from measurements or read from modelData.')
        else:
            # add the list to the sweeper dict as a string
            dict_sweeper[f'CoilWindings.half_turn_length'] = '[' + ', '.join(str(x) for x in ht_len) + ']'

    def __calculate_coil_length_with_resistance_meas(self, conductor_sample: ConductorSample, coil_name: str,
                                                     original_conductor: Conductor, coil: Coil):
        """
        Optimizes the coil length using the room temperature resistance measurements using the formula:
        R_RT = rho * L / (fCu * A_cond) * f_twist_pitch -> solving for length L

        :param conductor_sample: A ConductorSample object containing sample data for the conductor
        :param coil_name: The name of the coil
        :param original_conductor: The original conductor object, needed for getting parameters if they are not beeing changed, meaning not present in conductor_sample
        :param coil: The Coil object to get the RT resistance measurement values
        """

        # calculate correction factor strand twist-pitch with bare cable width and strand twist pitch
        bare_cable_width = conductor_sample.bare_cable_width
        if not bare_cable_width: bare_cable_width = original_conductor.cable.bare_cable_width
        if not bare_cable_width: raise Exception('Could not find bare cable width in conductor database and in original conductor.')
        if original_conductor.cable.type == 'Ribbon':
            f_twist_pitch = 1.0
        else:
            strand_twist_pitch = conductor_sample.strand_twist_pitch
            if not strand_twist_pitch: strand_twist_pitch = original_conductor.cable.strand_twist_pitch
            if not strand_twist_pitch: raise Exception('Could not find strand twist pitch in conductor database and in original conductor.')
            f_twist_pitch = np.sqrt(bare_cable_width ** 2 + (strand_twist_pitch / 2) ** 2) / (strand_twist_pitch / 2)

        # get number of half turns from map2d file if present, else check in modelData
        number_of_hts = self.__read_num_ht_per_group()
        number_of_ht = sum([number_of_hts[i - 1] for i in
                            self.groups_to_coils[coil_name]])  # add all the halfturns for the coil together

        # define needed parameters - check if they are present in sample and if not use default values form in modelData
        R_RT = coil.coil_resistance_room_T
        if not R_RT: raise Exception(f'No room temperature measurement provided for coil {coil_name}')
        Cu_noCu = coil.Cu_noCu_resistance_meas
        if not Cu_noCu: Cu_noCu = conductor_sample.Cu_noCu
        if not Cu_noCu: Cu_noCu = original_conductor.strand.Cu_noCu_in_strand
        if not Cu_noCu: raise Exception('Could not find copper-non-copper-ratio in conductor database (nor general nor measurement specific) and in original conductor.')
        fCu = Cu_noCu / (1 + Cu_noCu)
        A_strand = calc_strand_area(conductor_sample.strand_geometry, original_conductor)
        n_strands = conductor_sample.number_of_strands
        if not n_strands: n_strands = original_conductor.cable.n_strands
        if not n_strands: Exception('Could not find number of strands in conductor database and in original conductor.')
        A_cond = A_strand * n_strands

        # Calculate rho with C function
        temperature = coil.T_ref_coil_resistance
        if not temperature: temperature = 293.0
        mag_field = coil.B_resistance_meas
        if not mag_field: mag_field = 0.0
        RRR = conductor_sample.RRR
        if not RRR: RRR = original_conductor.strand.RRR
        if not RRR: raise Exception('Could not find RRR in conductor database and in original conductor.')
        # Define temperatures at which the RRR is defined (if not assigned, assign default values)
        T_ref_RRR_high = coil.T_ref_RRR_high
        if not T_ref_RRR_high: T_ref_RRR_high = original_conductor.strand.T_ref_RRR_high
        if not T_ref_RRR_high: T_ref_RRR_high = 293.0
        T_ref_RRR_low = coil.T_ref_RRR_low
        if not T_ref_RRR_low: T_ref_RRR_low = original_conductor.strand.T_ref_RRR_low
        if not T_ref_RRR_low: T_ref_RRR_low = 4.0
        # Find correction factor for the RRR to use in the NIST fit of copper electrical resistivity
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_RRR_high, T_ref_low=T_ref_RRR_low)
        # Calculate copper electrical resistivity
        rho_param = np.vstack((temperature, mag_field, corrected_RRR))  # create parameter v stack for c function
        CFUN_rhoCuNIST = STEAM_materials('CFUN_rhoCu_NIST_v1', rho_param.shape[0], rho_param.shape[1])
        rho = CFUN_rhoCuNIST.evaluate(rho_param)[0]  # evaluate rho function with the parameters

        # calculate the coil length to match the measured room-temperature resistance, and divided it by the number of half-turns
        L = R_RT * fCu * A_cond / (rho * f_twist_pitch)
        L_ht = L / number_of_ht
        return L_ht

    def __read_num_ht_per_group(self):
        """
        Reads the number of half-turns per group either from the map2d file or from the model_data's CoilWindings attribute.
        If neither is available, raises an exception.

        :return: A list containing the number of half-turns for each group.
        """
        if self.model_data.Sources.magnetic_field_fromROXIE:
            path_map2d = Path(self.path_input_dir, self.model_data.Sources.magnetic_field_fromROXIE).resolve()
            # number_of_ht has as many elements as groups. Each element defines the number of half-turns in that group
            number_of_hts, _, _, _, _, _, _, _, _, _ = ParserMap2dFile(map2dFile=path_map2d).getParametersFromMap2d()  # TODO number_of_hts is block number for HOC magnets
            if len(number_of_hts) != self.number_of_groups: raise Exception(f'The number of groups given to ParsimConductor ({self.number_of_groups}) is different then the number of groups specified in the map2d file "{path_map2d}" ({len(number_of_hts)})')
        else:
            number_of_hts = self.model_data.CoilWindings.n_half_turn_in_group
            if not number_of_hts: raise Exception('Number of half turns per group could not be specified. CoilWindings.n_half_turn_in_group is empty in modelData.')
            if len(number_of_hts) != self.number_of_groups: raise Exception('The number of groups given to ParsimConductor is different then the length of CoilWindings.n_half_turn_in_group in modelData.')
        return number_of_hts

    def __write_parsweep_conductors(self, dict_sweeper: Dict[str, Any], flag_optimize_fCu: bool,
                                    rel_warning_limit: float):
        """
        Writes the Conductor parameters for a sweeper CSV file to a dictionary.

        :param dict_sweeper: The input dictionary where the sweeper entries will be stored in the format {attributeNameDataModelMagnet: newValue}.
        :param flag_optimize_fCu: If set to True, fCu will be optimized with the coil resistance measurement at room temperature.
        :param rel_warning_limit: function raises warning in console when values are changed for more/less then this relative value
        """
        # parameter dict for creating the column names of sweeper csv file
        dict_param = {
            # format {attribute_name_of_ConductorSample_object: attribute_name_of_Conductor_from_DataModelMagnet_object}
            'bare_cable_width': 'cable.bare_cable_width',
            'bare_cable_height': 'cable.bare_cable_height',
            'number_of_strands': 'cable.n_strands',
            'strand_twist_pitch': 'cable.strand_twist_pitch',
            'Ra': 'cable.Ra',
            'Rc': 'cable.Rc',
            'strand_geometry.diameter': 'strand.diameter',
            'strand_geometry.bare_width': 'strand.bare_width',
            'strand_geometry.bare_height': 'strand.bare_height',
            'Cu_noCu': 'strand.Cu_noCu_in_strand',
            'RRR': 'strand.RRR',
            'f_rho_eff': 'strand.f_Rho_effective',
            'filament_twist_pitch': 'strand.fil_twist_pitch',
            'Bc20': 'Jc_fit.Tc0_CUDI1',
            'Tc0': 'Jc_fit.Bc20_CUDI1',
        }

        # looping through the coil list
        for coil_name, coil in self.data_parsim_conductor.Coils.items():
            idx = self.dict_coilName_to_conductorIndex[coil_name]
            sweeper_cond_name = f'Conductors[{idx}].'

            # parse data from DataParsimConductor to strings for sweeper csv and store them in dict_sweeper
            for sample_attribute_name, conductor_attribute_name in dict_param.items():
                val = getattr_from_list(coil.conductorSamples, sample_attribute_name, coil.weight_factors)
                if val:
                    # check if the original conductor has the attribute that will be changed to avoid errors when running parsim sweeper
                    if not rhasattr(self.model_data.Conductors[idx], conductor_attribute_name):
                        raise Exception(f'Tried to change conductor attribute "{conductor_attribute_name}" that is not specified for the conductor of coil {coil_name}.')
                    # append value to sweeper dict
                    dict_sweeper[sweeper_cond_name + conductor_attribute_name] = val

            # insert Jc fit value(s) depending on their fitting function (usual Bottura, CUDI1, CUDI3 for NbTi and Summers, Bordini for Nb3Sn)
            Jc_dict_list = []
            for conductor_sample in coil.conductorSamples:
                # calculate the parameters for Jc fit for every conductor sample of this coil
                Jc_dict = self.__calculate_Jc_fit_params(original_conductor=self.model_data.Conductors[idx],
                                                         coil_name=coil_name,
                                                         strand_geometry=conductor_sample.strand_geometry,
                                                         Bc20=conductor_sample.Bc20,
                                                         Ic_measurements=conductor_sample.Ic_measurements,
                                                         Tc0=conductor_sample.Tc0,
                                                         n_strand=conductor_sample.number_of_strands,
                                                         Cu_nCu=conductor_sample.Cu_noCu)
                Jc_dict_list.append(Jc_dict)
            # Calculate the average of values for each key across all dictionaries in the list
            Jc_avg_dict = average_dicts(Jc_dict_list)
            for name, val in Jc_avg_dict.items():
                dict_sweeper[sweeper_cond_name + 'Jc_fit.' + name] = val

            # optimize the fraction of copper with the resistance measurement at room temperature
            if flag_optimize_fCu:
                # check if RT measurement is defined
                if not coil.coil_resistance_room_T:
                    warnings.warn(f'No room temperature resistance measurement for coil "{coil_name}" was found in database. Not optimizing fraction of copper.')
                    continue
                # calculate Cu_noCu for every conductor sample and use mean value
                list_optimized_Cu_noCu = []
                for sample in coil.conductorSamples:
                    list_optimized_Cu_noCu.append(self.__calculate_fCu_with_resistance_meas(sample, coil_name,
                                                                                            self.model_data.Conductors[
                                                                                                idx], coil))
                # if the Cu no Cu ratio could be parsed directly from a column, overwrite it with optimized value
                dict_sweeper[sweeper_cond_name + 'strand.Cu_noCu_in_strand'] = np.mean(list_optimized_Cu_noCu)

    def __calculate_fCu_with_resistance_meas(self, conductor_sample: ConductorSample, coil_name: str,
                                             original_conductor: Conductor, coil: Coil):
        """
        Optimizes the fraction of copper (fCu) using the room temperature resistance measurements using the formula:
        R_RT = rho * L / (fCu * A_cond) * f_twist_pitch -> solving for fCu

        :param conductor_sample: A ConductorSample object containing sample data for the conductor
        :param coil_name: The name of the coil
        :param original_conductor: The original conductor object, needed for getting parameters if they are not being changed, meaning not present in conductor_sample
        :param coil: The Coil object to get the RT resistance measurement values
        """

        # calculate correction factor strand twist-pitch with bare cable width and strand twist pitch
        bare_cable_width = conductor_sample.bare_cable_width
        if not bare_cable_width: bare_cable_width = original_conductor.cable.bare_cable_width
        if not bare_cable_width: raise Exception('Could not find bare cable width in conductor database and in original conductor.')
        if original_conductor.cable.type == 'Ribbon':
            f_twist_pitch = 1.0
        else:
            strand_twist_pitch = conductor_sample.strand_twist_pitch
            if not strand_twist_pitch: strand_twist_pitch = original_conductor.cable.strand_twist_pitch
            if not strand_twist_pitch: raise Exception('Could not find strand twist pitch in conductor database and in original conductor.')
            f_twist_pitch = np.sqrt(bare_cable_width ** 2 + (strand_twist_pitch / 2) ** 2) / (strand_twist_pitch / 2)

        # define needed parameters - check if they are present in sample and if not use default values form in modelData
        L_coil = self.length_to_coil[coil_name]
        R_RT = coil.coil_resistance_room_T
        if not R_RT: raise Exception(f'No room temperature measurement provided for coil {coil_name}')
        A_strand = calc_strand_area(conductor_sample.strand_geometry, original_conductor)
        n_strands = conductor_sample.number_of_strands
        if not n_strands: n_strands = original_conductor.cable.n_strands
        if not n_strands: raise Exception('Could not find number of strands in conductor database and in original conductor.')
        A_cond = A_strand * n_strands

        # Calculate rho with C function
        temperature = coil.T_ref_coil_resistance
        if not temperature: temperature = 293.0
        mag_field = coil.B_resistance_meas
        if not mag_field: mag_field = 0.0
        RRR = conductor_sample.RRR
        if not RRR: RRR = original_conductor.strand.RRR
        if not RRR: raise Exception('Could not find RRR in conductor database and in original conductor.')
        # Define temperatures at which the RRR is defined (if not assigned, assign default values)
        T_ref_RRR_high = coil.T_ref_RRR_high
        if not T_ref_RRR_high: T_ref_RRR_high = original_conductor.strand.T_ref_RRR_high
        if not T_ref_RRR_high: T_ref_RRR_high = 293.0
        T_ref_RRR_low = coil.T_ref_RRR_low
        if not T_ref_RRR_low: T_ref_RRR_low = original_conductor.strand.T_ref_RRR_low
        if not T_ref_RRR_low: T_ref_RRR_low = 4.0
        # Find correction factor for the RRR to use in the NIST fit of copper electrical resistivity
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_RRR_high, T_ref_low=T_ref_RRR_low)
        # Calculate copper electrical resistivity
        rho_param = np.vstack((temperature, mag_field, corrected_RRR))  # create parameter v stack for c function
        CFUN_rhoCuNIST = STEAM_materials('CFUN_rhoCu_NIST_v1', rho_param.shape[0], rho_param.shape[1])
        rho = CFUN_rhoCuNIST.evaluate(rho_param)[0]  # evaluate rho function with the parameters

        # calculte fCu
        fCu = L_coil * rho * f_twist_pitch / (R_RT * A_cond)
        Cu_noCu_new = fCu / (1 - fCu)

        # compare new value with old one
        Cu_noCu_old = coil.Cu_noCu_resistance_meas
        if not Cu_noCu_old: Cu_noCu_old = conductor_sample.Cu_noCu
        if not Cu_noCu_old: Cu_noCu_old = original_conductor.strand.Cu_noCu_in_strand
        if self.verbose: print(f'Copper-non-Copper-ratio optimized form {Cu_noCu_old} to {Cu_noCu_new}.')

        # calculate fCu
        return Cu_noCu_new

    def __calculate_Jc_fit_params(self, original_conductor: Conductor, strand_geometry: StrandGeometry, n_strand: int,
                                  Cu_nCu: float, Tc0: float, Bc20: float, Ic_measurements: List[IcMeasurement],
                                  coil_name: str):
        """
        Calculate Jc fit parameters for a coil based using the variables to change, the original conductor's properties
        and the provided critical current measurements.

        :param original_conductor: The original conductor object, needed for getting parameters if they are not being changed, meaning not present in conductor_sample
        :param strand_geometry: geometry of the conductor sample
        :param n_strand: number of strands
        :param Cu_nCu: copper non copper ratio
        :param Tc0: Tc0 parameter for Jc fitting function
        :param Bc20: Bc20 parameter for Jc fitting function
        :param Ic_measurements: list of critical current measurements for this conductorSample
        :param coil_name: name of the coil

        returns: dictionary containing the calculated Jc fit parameters in format {attributeNameJcInDataModelMagnet: value}
        """
        Jc_dict = {}
        # TODO: use C-python-wrapper functions(see steam-materials-library) when implemented
        if original_conductor.Jc_fit.type == 'Summers':
            # check inputs
            if not original_conductor.strand.type: raise Exception(
                f'Strand type of conductor in coil {coil_name} is not specified in modelData.')
            if len(Ic_measurements) > 1:
                raise Exception(
                    f'More then one Measurement for Summers fit provided for coil {coil_name}. Please only provide 1 or 0.')
            elif len(Ic_measurements) < 1:
                warnings.warn(
                    f'No Measurement for Summers fit provided for coil {coil_name}. Calculation of new Summers parameters will be skipped.')
                return {}
            else:
                Ic_measurement = Ic_measurements[0]
                if not Ic_measurement.Ic: raise Exception(
                    f'No measured critical current (Ic) for Summers fit could be found in conductor database for coil {coil_name}. Please check column name in step definition.')
                if not Ic_measurement.B_ref_Ic: raise Exception(
                    f'No reference magnetic field of critical current measurement for Summers fit provided for coil {coil_name}.')
                if not Ic_measurement.T_ref_Ic: raise Exception(
                    f'No reference temperature of critical current measurement for Summers fit provided for coil {coil_name}.')
                if not Ic_measurement.Cu_noCu_sample: raise Exception(
                    f'No Cu-nCu-ratio of critical current measurement for Summers fit could be found in conductor database for coil {coil_name}. Please check column name in step definition.')

            # use parameters of modelData if they are not changed with the conductor database
            if Tc0:
                Jc_dict['Tc0_Summers'] = Tc0
            else:
                Tc0 = original_conductor.Jc_fit.Tc0_Summers
            if not Tc0: raise Exception(
                f'No Tc0 specified in modelData or the conductor database for coil {coil_name}.')
            if Bc20:
                Jc_dict['Bc20_Summers'] = Bc20
            else:
                Bc20 = original_conductor.Jc_fit.Bc20_Summers
            if not Bc20: raise Exception(
                f'No Bc20 specified in modelData or the conductor database for coil {coil_name}.')

            # calculate critical current density from critical current by using the area of
            fCu = Ic_measurement.Cu_noCu_sample / (Ic_measurement.Cu_noCu_sample + 1)
            A = calc_strand_area(strand_geometry, original_conductor)
            A_noCu = A * (1 - fCu)
            Jc_Tref_Bref = Ic_measurement.Ic / A_noCu

            # search for the best C0  # TODO use CFUN when available
            tol = 1e-6  # hardcoded
            if original_conductor.Jc_fit.Jc0_Summers:
                val_range = [original_conductor.Jc_fit.Jc0_Summers / 1000, original_conductor.Jc_fit.Jc0_Summers * 1000]
            else:
                val_range = [1e6, 1e14]
            n_iterations = math.ceil(np.log((val_range[1] - val_range[0]) / tol) / np.log(
                10))  # from formula: width/(10**n_iterations) = tol
            C0 = None
            for _ in range(n_iterations):
                try_CO_Summers = np.linspace(val_range[0], val_range[1], 10)
                tryJc_Summers = np.zeros(len(try_CO_Summers))
                # calculate Jc for every selected C0 value
                for j in range(len(try_CO_Summers)):
                    tryJc_Summers[j] = Jc_Nb3Sn_Summer_new(Ic_measurement.T_ref_Ic, Ic_measurement.B_ref_Ic,
                                                           try_CO_Summers[j], Tc0, Bc20)
                # find indices of the list values that are higher than Jc_Tref_Bref
                tempIdx = np.where(np.array(tryJc_Summers) >= Jc_Tref_Bref)[0]
                if len(tempIdx) == 0: raise Exception(
                    'No C0 for Jc Summers fit could be found in specified value range.')
                # set new value range for net iteration
                val_range = [try_CO_Summers[tempIdx[0] - 1], try_CO_Summers[tempIdx[0]]]
                C0 = try_CO_Summers[tempIdx[0] - 1]

            Jc_dict['Jc0_Summers'] = C0

            return Jc_dict
        # elif original_conductor.Jc_fit.type == 'Bordini':
        #     # TODO use C-function when wrapper is available
        #     Jc_dict['C0_Bordini'] = 0
        #     Jc_dict['alpha_Bordini'] = 0
        #     Jc_dict['Tc0_Bordini'] = 0
        #     Jc_dict['Bc20_Bordini'] = 0
        #     return Jc_dict
        elif original_conductor.Jc_fit.type == 'CUDI1':
            # general equation for CUDI1: Ic = (C1 + C2*B) * (1 - T/Tc0*(1-B/Bc20)^-.59)

            # use parameters of modelData if they are not changed with the conductor database
            if Tc0:
                Jc_dict['Tc0_CUDI1'] = Tc0
            else:
                Tc0 = original_conductor.Jc_fit.Tc0_CUDI1
            if Bc20:
                Jc_dict['Bc20_CUDI1'] = Bc20
            else:
                Bc20 = original_conductor.Jc_fit.Bc20_CUDI1
            if not n_strand: n_strand = original_conductor.cable.n_strands
            if not n_strand: raise Exception(
                f'Number of strands for coil {coil_name} unknown. CUDI parameter calculation not possible.')

            # depending on the number of critical current measurements, use different ways to calculate C1 and C2 parameter
            if len(Ic_measurements) == 2:
                # if two measurements are specified, we have 2 equations and 2 unknowns -> system can be solved

                # check inputs
                for Ic_measurement in Ic_measurements:
                    if not Ic_measurement.Ic: raise Exception(
                        f'No measured critical current (Ic) for CUDI1 fit could be found in conductor database for coil {coil_name}. Please check column name in step definition.')
                    if not Ic_measurement.B_ref_Ic: raise Exception(
                        f'No reference magnetic field of critical current measurement for CUDI1 fit provided for coil {coil_name}.')
                    if not Ic_measurement.T_ref_Ic: raise Exception(
                        f'No reference temperature of critical current measurement for CUDI1 fit provided for coil {coil_name}.')
                if not Tc0: raise Exception(
                    f'No Tc0 specified in modelData or the conductor database for coil {coil_name}.')
                if not Bc20: raise Exception(
                    f'No Bc02 specified in modelData or the conductor database for coil {coil_name}.')

                # solve system of linear equations: A*x = b
                A = np.array([[1, Ic_measurements[0].B_ref_Ic], [1, Ic_measurements[1].B_ref_Ic]])
                b_1 = Ic_measurements[0].Ic / (
                            1 - Ic_measurements[0].T_ref_Ic / Tc0 * (1 - Ic_measurements[0].B_ref_Ic / Bc20) ** -0.59)
                b_2 = Ic_measurements[1].Ic / (
                            1 - Ic_measurements[1].T_ref_Ic / Tc0 * (1 - Ic_measurements[1].B_ref_Ic / Bc20) ** -0.59)
                b = np.array([b_1, b_2])
                x = np.linalg.solve(A, b)
                C1_str, C2_str = x
            elif len(Ic_measurements) == 1:
                # if only one measurement is provided use one equation and the ratio of C1 and C2 according to modelData and warn the user
                warnings.warn(
                    f'Only one Measurement for CUDI1 fit provided for coil {coil_name}. Ratio of C1 and C2 from modelData is used as a second equation.')

                # check inputs and use parameters of modelData if they are not changed with the conductor database
                if not Ic_measurements[0].Ic: raise Exception(
                    f'No measured critical current (Ic) for CUDI1 fit could be found in conductor database for coil {coil_name}. Please check column name in step definition.')
                if not Ic_measurements[0].B_ref_Ic: raise Exception(
                    f'No reference magnetic field of critical current measurement for CUDI1 fit provided for coil {coil_name}.')
                if not Ic_measurements[0].T_ref_Ic: raise Exception(
                    f'No reference temperature of critical current measurement for CUDI1 fit provided for coil {coil_name}.')
                if not Tc0: raise Exception(
                    f'No Tc0 specified in modelData or the conductor database for coil {coil_name}.')
                if not Bc20: raise Exception(
                    f'No Bc02 specified in modelData or the conductor database for coil {coil_name}.')

                # try to read C1 over C2 ratio from modelData - if not existing use usual ratio for NbTi superconductors
                if not original_conductor.Jc_fit.C1_CUDI1 or not original_conductor.Jc_fit.C2_CUDI1:
                    print(
                        f'No C1 or C2 parameter defined in modelData for coil {coil_name}. Using usual ratio for NbTi superconductors.')
                    # 787.327 and -63.073 are hardcoded values come from magnet "MB inner layer" in csv file "Strand and cable characteristics"
                    # saving signed angle instead of ratio to keep track of signs - tan(angle_C1_C2) = C1/C2
                    angle_C1_C2 = math.atan2(3448.573,
                                             -257.289)  # atan2 is a tangens calcualtion that also saves the sign of the angle depending on the quadrant
                    initial_guess = [3448.573, -257.289]
                else:
                    angle_C1_C2 = math.atan2(original_conductor.Jc_fit.C1_CUDI1, original_conductor.Jc_fit.C2_CUDI1)
                    initial_guess = [original_conductor.Jc_fit.C1_CUDI1, original_conductor.Jc_fit.C2_CUDI1]

                def CUDI1_equation_fixed_ratio(C, *args):
                    # function defining the equation system to solve
                    C1, C2 = C
                    Ic, T, Tc0, B, Bc20, angle_C1_C2 = args

                    return [Ic - (C1 + C2 * B) * (1 - T / (Tc0 * (1 - B / Bc20) ** 0.59)),
                            C1 - C2 * math.tan(angle_C1_C2)]

                # Solve the equation system
                args = (
                Ic_measurements[0].Ic, Ic_measurements[0].T_ref_Ic, Tc0, Ic_measurements[0].B_ref_Ic, Bc20, angle_C1_C2)
                C = fsolve(func=CUDI1_equation_fixed_ratio, x0=initial_guess, args=args)
                C1_str = C[0]
                C2_str = C[1]

                # old approach with analytical solution (not used because of problem with sign of C1&C2)
                # # Ic = (C1 + C2*B) * (1 - T/Tc0*(1-B/Bc20)^-.59) where only C1 and C2 are unknown - second equation: tan(angle_C1_C2) = C1/C2
                # C2 = Ic_measurements[0].Ic / (1 - Ic_measurements[0].T_ref_Ic / (Tc0 * (1 - Ic_measurements[0].B_ref_Ic / Bc20) ** 0.59)) / (Ic_measurements[0].B_ref_Ic + math.tan(angle_C1_C2))
                # C1 = C2 * math.tan(angle_C1_C2)
            elif len(Ic_measurements) == 0:
                # if no measurement is provided use the usual ratio for NbTi superconductors and scale that value by cross section of superconductor and warn the user
                warnings.warn(
                    f'No Measurement for CUDI1 fit provided for coil {coil_name}. Usual ratio for NbTi superconductors of C1 and C2 is used and scaled by cross section of superconductor. Copper-non-copper ratio of magnet model will be used.')

                # get Copper to non Copper ratio
                if not Cu_nCu: Cu_nCu = original_conductor.strand.Cu_noCu_in_strand
                if not Cu_nCu: raise Exception(
                    f'No Copper-to-non-copper ratio could be found in conductor database or modeldata for coil {coil_name}.')

                # hardcoded values come from magnet "MB inner layer" in csv file "Strand and cable characteristics"
                # NOTE: cab...cable, str...strand, C1_cab = C1_str * nStrands  and  C1_str = C1_str_MB / A_MB * A_thisMagnet
                C1_per_square_meter_of_NbTi = 3448.573 / 3.362E-07  # C1_cab/(Cable Section NbTi) #  = strandArea * nStrands * (1-fCu) # MB inner layer
                C2_per_square_meter_of_NbTi = -257.289 / 3.362E-07  # C2_cab/(Cable Section NbTi) #  = strandArea * nStrands * (1-fCu) # MB inner layer

                # scale it with the cross-section of superconductor
                strand_cross_section = calc_strand_area(strand_geometry, original_conductor)
                fraction_of_superconductor = 1 / (Cu_nCu + 1)
                strand_NbTi_area = fraction_of_superconductor * strand_cross_section
                C1_str = C1_per_square_meter_of_NbTi * strand_NbTi_area
                C2_str = C2_per_square_meter_of_NbTi * strand_NbTi_area
            else:
                raise Exception(
                    f'More then two measurements for CUDI1 fit provided in coil {coil_name}. Please only provide 2, 1 or 0 measurements.')

            # calculate cable parameters by multiplying with number of strands
            if original_conductor.cable.type == 'Ribbon':
                Jc_dict['C1_CUDI1'] = C1_str
                Jc_dict['C2_CUDI1'] = C2_str
            else:
                Jc_dict['C1_CUDI1'] = C1_str * n_strand
                Jc_dict['C2_CUDI1'] = C2_str * n_strand

            # check if values are real and not imaginary (e.g. when Bc20 is bigger than B_ref_Ic)
            if np.iscomplex(complex(Jc_dict['C2_CUDI1'])) or np.iscomplex(complex(Jc_dict['C1_CUDI1'])):
                raise Exception(
                    f'When calculating CUDI1 parameters (C1, C2) the values turned out to have an imaginary part. Please check the inputs for coil {coil_name}.')

            return Jc_dict
        else:
            raise Exception(
                f'No implementation for fit type "{original_conductor.Jc_fit.type}" defined in ParsimConductor.')


def calc_strand_area(strand_geometry, original_conductor):
    # check inputs
    if not original_conductor.strand.type: raise Exception(f'Strand type is not specified in modelData.')

    if original_conductor.strand.type == 'Round':

        # if diameter is not changed in conductor database, use the one form modeldata
        if not strand_geometry.diameter:
            diameter = original_conductor.strand.diameter
        else:
            diameter = strand_geometry.diameter

        # calculate area of circle
        A = np.pi * diameter ** 2 / 4
    elif original_conductor.strand.type == 'Rectangular':

        # if height/width is not changed in conductor database, use the one from modeldata
        if not strand_geometry.bare_height:
            h = original_conductor.strand.bare_height
        else:
            h = strand_geometry.bare_height
        if not strand_geometry.bare_width:
            w = original_conductor.strand.bare_width
        else:
            w = strand_geometry.bare_width

        # calculate area of circle
        A = w * h
    else:
        raise Exception(f'Unknown type of conductor strand: {original_conductor.strand.type}!')
    return A


def Jc_Nb3Sn_Summer_new(T, B, C, Tc0, Bc20):
    if T == 0: T = 0.001
    if B == 0: B = 0.001
    frac_T = T / Tc0
    if frac_T > 1: frac_T = 1
    Bc2 = Bc20 * (1 - frac_T ** 2) * (1 - 0.31 * frac_T ** 2 * (1 - 1.77 * np.log(frac_T)))
    frac_B = B / Bc2
    if frac_B > 1: frac_B = 1
    Jc = C / np.sqrt(B) * (1 - frac_B) ** 2 * (1 - frac_T ** 2) ** 2
    return Jc


def make_value_SI(val: float, dim: str):
    if dim in ['mm', 'mOhm', 'mV']:
        return val / 1000
    elif dim in ['m', 'T', 'K', 'Ohm', 'V', '', ' ', '-']:
        return val
    elif dim in ['kA', 'kV', 'km']:
        return val * 1000
    elif dim in ['degC']:
        return val + 273.15
    else:
        raise Exception(f'unknown physical unit "{dim}".')


def setattr_to_list(list_instances: List[Any], row: pd.Series, col_name: str, attr_name: str):
    """
    Sets an attribute of a list of instances to a value derived from a specified column in a CSV row.

    :param list_instances: a list of instances to modify
    :param row: a row of data from a CSV file
    :param col_name: the name of the CSV column to get values from
    :param attr_name: the name of the attribute to set on each instance
    """
    # get dimension from csv column name
    dim = col_name[col_name.find('[') + 1:col_name.find(']')] if '[' in col_name else ''

    # parse str into list or make single float to
    if isinstance(row[col_name], str):
        val_list = parse_str_to_list(row[col_name], only_float_list=True)
    elif type(row[col_name]) in [float, int]:
        val_list = [row[col_name] for _ in range(len(list_instances))]
    else:
        raise Exception(f'Unknown datatype in column "{col_name}".')

    for val, instance in zip(val_list, list_instances):
        rsetattr(instance, attr_name, make_value_SI(val, dim))


def getattr_from_list(list_instances: List[Any], attribute_name: str, weight_factors: List[float]):
    """
    returns the weighted attribute value from a list of instances

    :param list_instances: list of instances to get the attribute value from
    :param attribute_name: attribute name
    :param weight_factors: list of weight factors
    """
    # check if attribute is either set in all of the instances (return weighted values) or in none (return None)
    attr_present = []
    for instance in list_instances:
        if rgetattr(instance, attribute_name):
            attr_present.append(True)
        else:
            attr_present.append(False)
    if True in attr_present and False in attr_present:
        raise Exception(f'The attribute "{attribute_name}" is only set in a few instances of the ConductorSample list.')
    if not all(attr_present):
        return None

    # read the values for the specific attribute for all the instances and store them in a list
    val_list = []
    for instance in list_instances:
        val_list.append(rgetattr(instance, attribute_name))

    # if there is no weight_factors specified, weight them equally (average)
    if not weight_factors:
        weight_factors = [1.0 / len(list_instances) for _ in range(len(list_instances))]

    # check if length is the same
    if len(weight_factors) != len(val_list):
        raise Exception(
            f'The length of the weight factors {len(weight_factors)} is not the same as the number of conductor samples {len(val_list)}.')

    # check if weight factors is normalized
    if sum(weight_factors) != 1.0:
        weight_factors = [w / sum(weight_factors) for w in weight_factors]

    # calculate weighting
    return sum([v * w for v, w in zip(val_list, weight_factors)])


def average_dicts(dict_list: List[Dict[str, Any]]):
    """
    Returns a dictionary with the same keys as the list of input dicts, and makes the average for all the values in the list

    :param dict_list: a list of dictionaries (with the same keys)
    """
    if not dict_list or dict_list == {}:
        return {}

    # check if all dicts have the same keys
    first_dict_keys = set(dict_list[0].keys())
    for d in dict_list[1:]:
        if set(d.keys()) != first_dict_keys:
            raise Exception('Input dictionaries do not have the same keys.')

    avg_dict = {}
    num_dicts = len(dict_list)

    # Sum the values for each key
    for d in dict_list:
        for key, value in d.items():
            # init dict value if not existing
            if key not in avg_dict: avg_dict[key] = 0
            if value is None or avg_dict[key] is None:
                avg_dict[key] = None
            else:
                avg_dict[key] += value

    # Divide the summed values by the number of dictionaries
    for key in avg_dict:
        avg_dict[key] /= num_dicts

    return avg_dict
