"""
File: AnalysisEvent.py
Date: 2024-10-11

Description:
    This file contains helper functions for specific analyses within the steam-models-dev framework.
    These functions are designed to be static, as they do not require an instance of any particular class.
    Unlike the more general-purpose functions found in AnalysisSTEAM.py, the functions in this file serve
    more specialized use-cases and are intended for narrower applications within the analysis of STEAM models.
"""

import csv
import os
import re
import warnings
import ruamel.yaml
import pandas as pd
from steam_sdk.parsers.ParserPSPICE import ParserPSPICE
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing

def find_n_magnets_in_circuit(
        filename: str,
        circuit_name: str
) -> None:
    '''
        **Find the number of magnets present in the current circuit by reading the value from a CSV file.**

        :param filename: Path to the input CSV file.
        :param circuit_name: Name of the circuit to look for.
        :return: String indicating the number of magnets in the circuit.
    '''
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['circuit'] == circuit_name:
                return row['NumberOfMagnets']
        return None


def find_IPQ_circuit_type_from_IPQ_parameters_table(
        filename: str,
        circuit_name: str
) -> str:
    '''
    **Return the circuit type (e.g., IPQ_RQ4_4_2xRPHH_4xMQY) for a specific IPQ circuit name (e.g., RQ4.L8) from a table.**

    :param filename: Path to the IPQ_circuit_parameters.csv file.
    :param circuit_name: Name of the circuit to look up in the table.
    :return: String representing the circuit type.
    TODO: In the future probably not needed anymore since
    '''
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['circuit'] == circuit_name:
                return row['circuit_type']
    raise ValueError(f"Error in find_IPQ_circuit_type_from_IPQ_parameters_table function: "
                     f"Circuit '{circuit_name}' not found in the table. "
                     f"Maybe check if the circuit_name is misspelled ?")

def get_circuit_name_from_eventfile(
        event_file: str
) -> str:
    '''
    **Return the circuit name for a given event file by reading the entry "Circuit Name."**

    :param event_file: Path to the event file for which the circuit name is to be obtained.
    :return: String indicating the circuit name.
    '''
    with open(event_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            first_entry = row.get("Circuit Name")
            if first_entry:
                return first_entry
    raise ValueError(f"Error in get_circuit_name_from_eventfile function: "
                     f"Circuit Name entry could not be found in file {event_file}. "
                     f"Maybe check if the file is properly formatted?")
def get_circuit_family_from_circuit_name(
        circuit_name: str,
        library_path: str
) -> str:
    '''
       **Return the circuit family corresponding to a certain circuit name using a lookup table stored in the steam_models library.**

       :param circuit_name: Name of the circuit to look up.
       :param library_path: Path to the steam_models library where the lookup table is located.
       :return: String representing the circuit family.
    '''
    # Load the file from library_path into a DataFrame
    df = pd.read_csv(os.path.join(library_path,'circuits','circuit_parameters', 'Table_CircuitName_CircuitFamily_CircuitType.csv'))

    # Find the row where 'circuit_name' matches the 'circuit_name' column
    row = df.loc[df['circuit_name'] == circuit_name]
    # If the row is found, get the corresponding 'circuit_types' entry
    if not row.empty:
        circuit_family_entry = row['circuit_family'].values[0]
        return circuit_family_entry
    raise ValueError(f"Error in get_circuit_family_from_circuit_name function: "
                     f"Circuit '{circuit_name}' not found in the table. "
                     f"Maybe check if the circuit_name is misspelled ?")

def create_two_csvs_from_odd_and_even_rows(
        input_file_name: str,
        output_odd_file_name: str = 'output_odd.csv',
        output_even_file_name:str = 'output_even.csv'
) -> [str, str]:
    '''
    **Create two CSV files from the odd and even rows of a given CSV file and return the filenames of the created files.**

    :param input_file_name: Path of the input CSV file.
    :param output_odd_file_name: Filepath of the CSV file created from the odd rows.
    :param output_even_file_name: Filepath of the CSV file created from the even rows.
    :return: List of strings containing the filenames of the created odd and even CSV files.
    '''
    # Create empty lists to hold the odd and even rows
    odd_rows = []
    even_rows = []

    # Open the input CSV file and read in the rows
    with open(input_file_name, 'r') as input_file:
        reader = csv.reader(input_file)

        # Save the header row
        header = next(reader)

        # Loop over the remaining rows and append them to the odd or even list
        for i, row in enumerate(reader):
            if i % 2 == 0:
                even_rows.append(row)
            else:
                odd_rows.append(row)

    # Write the odd and even rows to separate output files'
    with open(output_odd_file_name, 'w', newline='') as output_odd_file:
        writer_odd = csv.writer(output_odd_file)
        writer_odd.writerow(header)
        writer_odd.writerows(odd_rows)

    with open(output_even_file_name, 'w', newline='') as output_even_file:
        writer_even = csv.writer(output_even_file)
        writer_even.writerow(header)
        writer_even.writerows(even_rows)

    # Return a list of the output file names
    return [output_even_file_name, output_odd_file_name]

def get_number_of_apertures_from_circuit_family_name(
        circuit_family_name: str
) -> int:
    '''
    **Return the number of apertures for a given circuit family name.**

    :param circuit_family_name: Name of the circuit family for which the number of apertures is determined.
    :return: Integer indicating the number of apertures.
    '''
    #circuit_family_name = get_circuit_family_from_circuit_name(circuit_name)
    if circuit_family_name in ["IPQ", "RB"]:
        return 2
    else:
        return 1

def get_number_of_quenching_magnets_from_layoutdetails(
        position: str,
        circuit_family_name: str,
        library_path: str
) -> str:
    '''
    **Return the electrical position (#Electric_circuit value) of a magnet based on its location within the circuit.**
    :param position: Position of the magnet within the circuit.
    :param circuit_family_name: Family of the circuit.
    :param library_path: Absolute path to the steam_models library.
    :return: String indicating the electrical position of the magnet.
    '''
    df = pd.read_csv(
        os.path.join(library_path, 'circuits', 'circuit_parameters', f"{circuit_family_name}_LayoutDetails.csv"))
    mask = df['Magnet'].str.split('.').str[1] == position
    result = df.loc[mask, '#Electric_circuit'].iloc[0]
    return result

def get_magnet_types_list(
        number_of_magnets: int,
        simulation_name: str
) -> list:
    """
    **Generate a list representing types of magnets based on simulation parameters.**

    :param number_of_magnets: The total number of magnets in the circuit.
    :param simulation_name: The name of the simulation.

    Explanation:
        - If the simulation involves 4 magnets and starts with "RQX", the list will be [1, 2, 2, 1].
        - If the simulation starts with "IPQ" and involves 2 magnets, the list will be [1, 2].
        - If the simulation starts with "RB", all magnets will be of type 1.
        - If the simulation name is not "RQX", "IPQ", or "RB", for specific numbers of magnets
          (154, 13, 8, 77, 6, 12, 11, 10, 9, 4, 2), the list will consist of one type 1 magnet
          followed by (number_of_magnets - 1) type 2 magnets.
        - For all other cases, the default magnet type is 1 for all magnets.

    :return: List of integers representing magnet types, where each element indicates the type
             of the corresponding magnet in the simulation.
    """
    if number_of_magnets == 4 and simulation_name.startswith("RQX"): #to be improved
        return [1, 2, 2, 1]
    elif simulation_name.startswith("IPQ") and number_of_magnets == 2:
        return [1, 2]
    elif simulation_name.startswith("RB"):
        return [1] * number_of_magnets
    elif number_of_magnets in [154, 13, 8, 77, 6, 12, 11, 10, 9, 4, 2]:
        return [1] + [2] * (number_of_magnets - 1)
    else:
        return [1] * number_of_magnets

def get_number_of_magnets(
        circuit_name: str,
        simulation_name: str,
        circuit_type: str,
        circuit_family_name: str
) -> int:
    """
    **Determine the number of magnets in a specific circuit based on circuit name, type, and simulation name.**

    :param circuit_name: Name of the circuit.
    :param simulation_name: Name of the simulation.
    :param circuit_type: Type of the circuit.
    :param circuit_family_name: Family the circuit belongs to.

    Algorithm:
        - If the circuit type is "RCS" or "RB", return 154.
        - If the circuit type is "RCD" or "RCO", return 77.
        - If the circuit name starts with "RQ6." and has a length of 8, return 6.
        - If the circuit name starts with "RQS.R", "RQS.L", or "RQTL9", return 2.
        - If the circuit name starts with "RQS.A", "RSS", or "RQX", return 4.
        - If the circuit name starts with "RQTD" or "RQTF", return 8.
        - If the circuit family name is "60A", "IPD", "80-120A", or "600A", return 1.
        - If the circuit type is "RQ_47magnets", return 47.
        - If the circuit type is "RQ_51magnets", return 51.
        - If the circuit family name is "IPQ", calculate the number of magnets based on the simulation name.

    Note:
        - For "IPQ" circuits, the function extracts a numeric value from the simulation name and divides it by 2
          to determine the number of magnets.

    :return: Integer representing the number of magnets in the circuit.
    """
    if circuit_type in ["RCS", "RB"]:
        return 154
    elif circuit_type in ["RCD", "RCO"]:
        return 77
    elif circuit_name.startswith("RQ6.") and len(circuit_name) == 8:
        return 6
    elif circuit_name.startswith(("RQS.R", "RQS.L", "RQTL9")):
        return 2
    elif circuit_name.startswith(("RQS.A", "RSS", "RQX")):
        return 4
    elif circuit_name.startswith(("RQTD", "RQTF")):
        return 8
    elif circuit_family_name in ["60A", "IPD", "80-120A", "600A"]:
        return 1
    elif circuit_type == "RQ_47magnets":
        return 47
    elif circuit_type == "RQ_51magnets":
        return 51
    elif circuit_family_name == "IPQ":
        return int(int(re.search(r'_(\d+)_', simulation_name).group(1))/2)
    #TODO: Get rid of this confusing logic. And add the relevant quantity to the table of all circuit names.

def get_magnet_name(
        circuit_name: str,
        simulation_name: str,
        circuit_type: str
) -> str:
    """
    **Determine the magnet name(s) based on the provided circuit name, simulation name, and circuit type.**

    :param circuit_name: Name of the circuit.
    :param simulation_name: Name of the simulation.
    :param circuit_type: Type of the circuit.

    :return: A string representing the magnet name or a list of magnet names if multiple names are possible.
    """
    if circuit_type == "IPD":
        if circuit_name in ["RD1.L2","RD1.L8","RD1.R2","RD1.R8"]:
           return "MBX"
        if circuit_name in ["RD2.L1", "RD2.L2", "RD2.L5", "RD2.L8", "RD2.R1", "RD2.R2", "RD2.R5", "RD2.R8"]:
            return "MBRC"
        if circuit_name in ["RD3.L4", "RD3.R4"]:
            return "MBRS"
        if circuit_name in ["RD4.L4","RD4.R4"]:
            return "MBRB"
    if circuit_name.startswith("RCBH") or circuit_name.startswith("RCBV"):
        return "MCBH"
    elif circuit_name.startswith("RD"):
        #circuit_type = self.__get_circuit_type(circuit_name, self.library_path)
        magnet_dict = {"RD1": "MBX", "RD2": "MBRC", "RD3": "MBRS", "RD4": "MBRB"}
        return magnet_dict.get(circuit_type, "")
    elif circuit_name.startswith("RQX"):
        return ["MQXA", "MQXB"]
    elif circuit_name.startswith(("RQ4", "RQ5", "RQ7", "RQ8", "RQ9", "RQ10")) or (circuit_name.startswith("RQ6.") and
                                                                                  len(circuit_name) == 6):
        magnet_dict = {"IPQ_RQ4_2_2xRPHH_2xMQY": "MQY", "IPQ_RQ4_4_2xRPHH_4xMQY": ["MQY", "MQY"],
                       "IPQ_RQ5_2_2xRPHGB_2xMQML": "MQML", "IPQ_RQ5_2_2xRPHH_2xMQY": "MQY", "IPQ_RQ5_4_2xRPHGB_4xMQM":
                           ["MQM", "MQM"], "IPQ_RQ5_4_2xRPHH_4xMQY": ["MQY", "MQY"], "IPQ_RQ6_2_2xRPHGB_2xMQML": "MQML",
                       "IPQ_RQ6_2_2xRPHGB_2xMQY": "MQY", "IPQ_RQ6_4_2xRPHGB_2xMQM_2xMQML": ["MQM", "MQML"],
                       "IPQ_RQ7_2_2xRPHGA_2xMQM": "MQM", "IPQ_RQ7_4_2xRPHGA_4xMQM": ["MQM", "MQM"],
                       "IPQ_RQ8_2_2xRPHGA_2xMQML": "MQML", "IPQ_RQ9_4_2xRPHGA_2xMQM_2xMQMC": ["MQM", "MQMC"],
                       "IPQ_RQ10_2_2xRPHGA_2xMQML": "MQML"}
        return magnet_dict.get(simulation_name, "")
    elif circuit_name.startswith("RQ6.") and len(circuit_name) == 8:
        return ["MQTLH", "MQTLH_quenchback"]
    elif circuit_name.startswith(("RQTL7", "RQTL8", "RQTL10", "RQTL11")):
        return "MQTLI"
    elif circuit_name.startswith("RQTL9"):
        return ["MQTLI", "MQTLI_quenchback"]
    elif circuit_name.startswith("RQSX3"):
        return "MQSX"
    elif circuit_name.startswith("RQS"):
        return ["MQS", "MQS_quenchback"]
    elif circuit_name.startswith(("RQT12", "RQT13")):
        return "MQT"
    elif circuit_name.startswith(("RQTD", "RQTF")):
        return ["MQT", "MQT_quenchback"]
    elif circuit_name.startswith("RQ"):
        return "MQ"
    elif circuit_name.startswith("RCBY"):
        return "MCBYH"
    elif circuit_name.startswith("RCBC"):
        return "MCBCH"
    elif circuit_name.startswith("RCS"):
        return ["MCS", "MCS_quenchback"]
    elif circuit_name.startswith("RB"):
        return "MB"
    elif circuit_name.startswith("RCBX"):
        return ["MCBXH", "MCBXV"]
    elif circuit_name.startswith("RSS"):
        return ["MSS", "MSS_quenchback"]
    elif circuit_name.startswith(("ROD", "ROF")):
        return ["MO", "MO_quenchback"]
    elif circuit_name.startswith(("RSD", "RSF")):
        return ["MS", "MS_quenchback"]
    elif simulation_name == "RCD":
        return ["MCD", "MCD_quenchback"]
    elif simulation_name == "RCO":
        return ["MCO", "MCO_quenchback"]

def get_t_PC_off_from_PSPICE_netlist_data(
        path_to_circuit_file: str,
        verbose: bool = False
) -> float:
    """
    **Extract the t_PC_off value from a PSPICE netlist file and return it.**

    :param path_to_circuit_file: File path to the PSPICE netlist file.
    :param verbose: If True, prints debug information. Default is False.

    :return: Float representing the extracted t_PC_off value.
    """
    pp = ParserPSPICE(None)
    if verbose:
        print(f"Getting t_PC_off from netlist data at {path_to_circuit_file}")
    netlist_data = pp.read_netlist(path_to_circuit_file, flag_acquire_auxiliary_files=False, verbose=False)
    dictionary_global_parameters = netlist_data.GlobalParameters.global_parameters
    t_PC_off_dict = {}
    for key, value in dictionary_global_parameters.items():
        if "t_PC_off" in key:
            t_PC_off_dict[key] = value
    if verbose:
        print(f"The following values of t_PC_off were extracted from the netlist file: {t_PC_off_dict}")
    if not len(set(t_PC_off_dict.values())) == 1:
        warnings.warn('t_PC_off values are not identical in netlist!')
    else:
        return float(t_PC_off_dict[next(iter(t_PC_off_dict))])


def generate_unique_event_identifier_from_eventfile(
        file_name,
        verbose: bool = False
) -> str:
    """
    **Generate a unique identifier for an event based on the event file.**

    :param file_name: Name of the event file, including the file extension.
    :param verbose: If True, prints debug information. Default is False.

    :return: String representing a unique event identifier.
    """
    pattern = r'(.*?)(\d{4}-\d{2}-\d{2}-\d{2}h\d{2}-\d{4}-\d{2}-\d{2}-\d{2}h\d{2})(?:_(\w+))?\..*'

    match = re.search(pattern, file_name)

    if verbose:
        print("-" * 50)
        print("File Name:", file_name)

    if match:
        output = match.group(1) + match.group(2)
        if verbose:
            print("Unique identifier is:", output)
    else:
        output = None
        if verbose:
            warnings.warn("Unique identifier is None")

    return output

def get_signal_keys_from_configurations_file(
        full_config_file_path: str,
        configuration: str
) -> list:
    """
    **Retrieve all signal keys specified in a configuration file to include them in the .csdf output file of a simulation.**

    :param full_config_file_path: Absolute path to the configuration file.
    :param configuration: Name of the specific configuration (defined inside the configuration file) to use.

    :return: List of strings representing all simulation signals needed to create the plots defined in the configuration file.
    """
    with open(full_config_file_path, 'r') as yaml_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        yaml_data = yaml.load(yaml_file)

    signal_keys = []

    for config_key, config_value in yaml_data['ConfigurationList'].items():
        if config_key == configuration:
            for signal_key, signal_value in config_value['SignalList'].items():
                if signal_key.endswith('_zoom'):
                   continue
                signal_keys.append(signal_value['sim_signals_to_add_y'][0].replace("'", ""))
    return list(set(signal_keys))

def determine_config_path_and_configuration(
        directory_config_files,
        steam_circuit_type
) -> tuple[str, str]:
    """
    **Determine the full path to the configuration file and the configuration to use based on the provided circuit type.**

    :param directory_config_files: Absolute path to a directory containing different config files for various circuit types,
                                   or an absolute path to a single config file.
    :param steam_circuit_type: Type of the circuit to determine the corresponding configuration.

    :return: Tuple of strings containing the configuration file path and the configuration to be used.
    """
    if os.path.isdir(directory_config_files):
        config_filepath = os.path.join(directory_config_files,f"config_{steam_circuit_type}.yaml")
        configuration =  f"{steam_circuit_type}_1"
    elif os.path.isfile(directory_config_files): # Full path to SIGMON specific config file was defined
        config_filepath = directory_config_files
        #Here cases for different configurations may be included
        if os.path.basename(config_filepath).startswith("config_SIGMON"):

            IPQ_list = ["IPQ_RQ4_2_2xRPHH_2xMQY", "IPQ_RQ4_4_2xRPHH_4xMQY","IPQ_RQ5_2_2xRPHGB_2xMQML"
            "IPQ_RQ5_2_2xRPHGB_2xMQML",
            "IPQ_RQ5_4_2xRPHH_4xMQY",
            "IPQ_RQ5_2_2xRPHH_2xMQY",
            "IPQ_RQ5_4_2xRPHGB_4xMQM",
            "IPQ_RQ5_2_2xRPHGB_2xMQML",
            "IPQ_RQ6_2_2xRPHGB_2xMQML",
            "IPQ_RQ6_4_2xRPHGB_2xMQM_2xMQML",
            "IPQ_RQ6_2_2xRPHGB_2xMQY",
            "IPQ_RQ7_4_2xRPHGA_4xMQM",
            "IPQ_RQ7_2_2xRPHGA_2xMQM",
            "IPQ_RQ8_2_2xRPHGA_2xMQML",
            "IPQ_RQ9_4_2xRPHGA_2xMQM_2xMQMC",
            "IPQ_RQ10_2_2xRPHGA_2xMQML"]


            # For RCD and RCO the right signals are already included
            default_circuits_with_EE = ["RCS", "RQ6","RQS","RQT","RQTL9","RSD_11magnets","RSF_10magnets","RU",
                                        "RO_13magnets","RO_8magnets", "RCD", "RQ_47magnets","RQ_51magnets", "RQS_AxxBx",
                                        "RSD_12magnets", "RSF_9magnets"]
            default_circuits_without_EE = ["RCB", "RCBC", "RCBY", "RQT_12_13", "RQTL_7_8_10_11", "RQT","RSS", "RCBX",
                                           "RCO", "RQSX3", "IPD", "RQX","RQS_R_LxBx"]

            circuits_80_120A = ["RCBC", "RCBY"]

            if steam_circuit_type == "RQX":
                configuration = "SIGMON_RQX"
            elif steam_circuit_type in circuits_80_120A:
                configuration = "SIGMON_80-120A"
            elif steam_circuit_type in IPQ_list:
                configuration = "SIGMON_IPQ"
            elif steam_circuit_type.startswith("RB"):
                configuration = "SIGMON_RB"
            elif steam_circuit_type in default_circuits_with_EE:
                configuration = "SIGMON_default_with_EE"
            elif steam_circuit_type in default_circuits_without_EE:
                configuration = "SIGMON_default_without_EE"
    else:
        print(f"{directory_config_files} does not exist or is not a valid path.")
        warnings.warn("!Invalid config file path!")
        config_filepath = None
    return config_filepath, configuration


def get_circuit_type_from_circuit_name(
        circuit_name: str,
        library_path: str,
        simulation_name = None
)-> str:
    """
    **Reads the 'Table_CircuitName_CircuitFamily_CircuitTypes.csv' file located in steam-models/circuits/circuit_parameters
    and returns a string containing the circuit type.**

    :param circuit_name: The name of the circuit for which the circuit type is to be determined.
    :param library_path: The path to the library where the 'Table_CircuitName_CircuitFamily_CircuitTypes.csv' file is located.
    :param simulation_name: (Optional) The name of the simulation.

    :return: A string representing the circuit type.
    """

    #This line is needed for RCD_RCO events
    if simulation_name == "RCD":  # improvement pending
        return "RCD"
    elif simulation_name == "RCO":  # improvement pending
        return "RCO"
    else:
            #If not a RCD_RCO event, we
            # Load the file from library_path into a DataFrame
            df = pd.read_csv(os.path.join(library_path, 'circuits', 'circuit_parameters', 'Table_CircuitName_CircuitFamily_CircuitType.csv'))

            # Find the row where 'circuit_name' matches the 'circuit_name' column
            row = df.loc[df['circuit_name'] == circuit_name]
            # If the row is found, get the corresponding 'circuit_types' entry
            if not row.empty:
                circuit_type_entry = row['circuit_type'].values[0]
                return circuit_type_entry
            else:
                return None  # Circuit name not found in the file

def get_circuit_information_of_circuit_types(
        circuit_type: str,
        circuit_name: str,
        circuit_family: str,
        simulation_numbers: list
) -> tuple [list, list, list] :
    """
    **Handles special cases of double circuits, such as RCD_AND_RCO.**

    For double circuit types (e.g., RCD_AND_RCO), two simulations are carried out. The setup may vary: for RCD_AND_RCO circuits,
    two distinct Analysis STEAM objects are called, whereas for RXBC circuits, both simulations use the same Analysis STEAM object.
    This function retrieves the simulation numbers, circuit types, and circuit names used in these different cases.
    This function is e.g. necessary to find the path to the simulation folder.

    TODO: In future work, double circuits should be implemented more consistently in STEAM so this function is not needed anymore.

    :param circuit_type: The type of the circuit.
    :param circuit_name: The name of the circuit.
    :param circuit_family: The family to which the circuit belongs.
    :param simulation_numbers: The numbers associated with the simulations.

    :return: A tuple containing:
        - A list of circuit types used for the simulations.
        - A list of circuit names used for the simulations.
        - A list of simulation numbers.
    """
    postprocess_circuittypes = []
    postprocess_simulation_numbers = []
    postprocess_circuitnames = []

    if circuit_type in ["RCD_AND_RCO", "RCD", "RCO"]:  # For RQ circuits we have to do two queries: one for RQD and one for RQF
        # since this is a double Circuit
        postprocess_circuittypes.append("RCD")
        postprocess_circuittypes.append("RCO")
        postprocess_simulation_numbers.append(simulation_numbers[0])
        postprocess_simulation_numbers.append(simulation_numbers[0])
        postprocess_circuitnames.append("RCD." + circuit_name.split(".")[-1])
        postprocess_circuitnames.append("RCO." + circuit_name.split(".")[-1])
    elif circuit_type == "RCBX":
        postprocess_circuittypes.append(circuit_type)
        postprocess_circuittypes.append(circuit_type)
        postprocess_simulation_numbers.append(simulation_numbers[0])
        postprocess_simulation_numbers.append(simulation_numbers[0] + 1)
        postprocess_circuitnames.append(circuit_name.replace("RCBX", "RCBXH"))
        postprocess_circuitnames.append(circuit_name.replace("RCBX", "RCBXV"))
    elif circuit_family == "RQ":
        postprocess_circuittypes.append(circuit_type)
        postprocess_circuittypes.append(circuit_type)
        postprocess_simulation_numbers.append(simulation_numbers[0])
        postprocess_simulation_numbers.append(simulation_numbers[0] + 1)
        postprocess_circuitnames.append("RQD." + circuit_name.split(".")[-1])
        postprocess_circuitnames.append("RQF." + circuit_name.split(".")[-1])
    else:
        postprocess_circuittypes.append(circuit_type)
        postprocess_simulation_numbers.append(simulation_numbers[0])
        postprocess_circuitnames.append(circuit_name)

    return postprocess_circuittypes, postprocess_simulation_numbers, postprocess_circuitnames


def write_config_file_for_viewer(
        circuit_type,
        simulation_numbers,
        circuit_name,
        circuit_family,
        t_PC_off,
        path_to_configurations_folder,
        temp_working_directory,
        path_postmortem_offline_data_folder,
        unique_identifier,
filepath_to_temp_viewer_csv
        ) -> None:
    """
    **Function which writes the initialization file for the viewer in the corresponding simulation folder**

    :param circuit_type: type of the circuit
    :param simulation_numbers: simulation number
    :param circuit_name: name of the circuit
    :param circuit_family: family the circuit belongs to
    :param t_PC_off: time at which the power converter is switched of
    :param path_to_configurations_folder: path to a configuration file or a directory with circuit type specific configuration files
    :param temp_working_directory: temporary working directory for the viewer
    :param path_postmortem_offline_data_folder: path to the measurement data folder
    :param unique_identifier: unique identifier of the event
    :param filepath_to_temp_viewer_csv: path to which the viewer initilization file is to be written.

        :return: None
    """
    postprocess_circuittypes, postprocess_simulation_numbers, postprocess_circuitnames =\
        get_circuit_information_of_circuit_types(circuit_type,circuit_name,circuit_family, simulation_numbers)

    # iterate over all cases
    for file_counter, circuit_type, circuit_name in zip(postprocess_simulation_numbers,
                                                        postprocess_circuittypes, postprocess_circuitnames):

        hard_coded_filename_addition = f"__UID_{unique_identifier}__CN_{circuit_name}"


        path_to_simulation_folder = os.path.join(temp_working_directory, circuit_type, str(file_counter))

        filepath_to_temp_viewer_csv = os.path.join(path_to_simulation_folder, f'temp_viewer{hard_coded_filename_addition}.csv')

        full_config_file_path, configuration = determine_config_path_and_configuration(
            directory_config_files=path_to_configurations_folder, steam_circuit_type=circuit_type)

        path_measurement_data = os.path.join(path_postmortem_offline_data_folder, f"pm-{unique_identifier}", f"{circuit_name}.feather")

        output_folder_viewer = path_to_simulation_folder  # we will just put it in the simulation folder

        # generate some metadata for the viewer csv file
        path_output_measurement_files = os.path.dirname(os.path.dirname(path_measurement_data))
        test_campaign = os.path.basename(os.path.dirname(path_measurement_data))
        test_name = os.path.splitext(os.path.basename(path_measurement_data))[0]

        configurations_viewer = {
            'Event label': unique_identifier,
            'Configuration file': full_config_file_path,
            'Configuration': configuration,
            'Measurement folder': 'dummy_entry',
            'Test campaign': test_campaign,
            'Test name': test_name,
            'flag_convert_meas_csv': False,
            'path_output_measurement_files': path_output_measurement_files,
            'Simulation folder': path_to_simulation_folder,
            'Simulation file': f'{circuit_type}.csd',
            'path_output_figures': output_folder_viewer,
            'path_output_simulation_files': 'not_used',
            't_PC_off': t_PC_off
        }

        # write the temp_viewer file
        fieldnames = configurations_viewer.keys()

        make_folder_if_not_existing(os.path.dirname(filepath_to_temp_viewer_csv))

        with open(filepath_to_temp_viewer_csv, 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Write the header row
            csv_writer.writeheader()
            # Write configurations to the CSV file
            csv_writer.writerow(configurations_viewer)

def get_hard_coded_filename_postfix(
        unique_identifier: str,
        circuit_name: str
) -> str:
    """
    **Generates a hard-coded filename postfix based on the circuit name and unique identifier.**

    Since only the combination of circuit name and unique identifier is truly unique (especially for double circuits),
    unique identifiers must be complemented with a postfix to obtain filenames that cannot be confused with other events or circuits.

    :param unique_identifier: The unique identifier of the event.
    :param circuit_name: The name of the circuit.

    :return: A string representing the hard-coded filename postfix.
    """
    hard_coded_filename_postfix = f"__UID_{unique_identifier}__CN_{circuit_name}"
    return hard_coded_filename_postfix

def extract_signal_touples_from_config(
        config_path: str,
        target_configuration: str
) -> list:
    """
    **Extracts pairs of simulation signals and corresponding measurement signals from a configuration file.**

    :param config_path: The absolute path to the configuration file.
    :param target_configuration: Defines which of the configurations in the config file to use.

    :return: A list of lists, where each sublist contains a unique pair of simulation and corresponding measurement signals.
    """
    with open(config_path, 'r') as file:
        config = ruamel.yaml.YAML().load(file)
    labels_set = set()
    # Extract signal tuples for the target configuration
    if target_configuration in config['ConfigurationList']:
        signals = config['ConfigurationList'][target_configuration]['SignalList']
        for key, value in signals.items():
            if 'meas_label' in value and 'sim_label' in value:
                meas_label = value['meas_label']
                sim_label = value['sim_label']
                labels_set.add((sim_label, meas_label))
    # Convert the set to a list of lists
    labels_list = [list(pair) for pair in labels_set]
    return labels_list
