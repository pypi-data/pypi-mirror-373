from pathlib import Path

import yaml


from steam_sdk.data.DataModelCircuit import DataModelCircuit, Component
from steam_sdk.parsers.ParserYAML import yaml_to_data

def read_circuit_data_from_model_data(full_path_file_name: str, verbose: bool = False):
    if isinstance(full_path_file_name, Path):
        full_path_file_name = str(full_path_file_name)
    # Load yaml keys into DataModelCircuit dataclass
    with open(full_path_file_name, "r") as stream:
        dictionary_yaml = yaml.safe_load(stream)
        circuit_data = DataModelCircuit(**dictionary_yaml)
        for key in dictionary_yaml['Netlist'].keys():
            new_Component = Component(**dictionary_yaml['Netlist'][key])
            circuit_data.Netlist[key] = new_Component
    if verbose:
        print('File ' + full_path_file_name + ' read.')
    return circuit_data
    #return yaml_to_data(full_path_file_name, DataModelCircuit)