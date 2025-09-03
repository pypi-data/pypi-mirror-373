from typing import Union

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.utils.rgetattr import rgetattr
from steam_sdk.utils.sgetattr import rsetattr
import re

def get_attribute_model(case_model: str, builder_model: object, name_variable: str, idx_conductor: int = None, name_simulation_set: str = None):
    """
    Helper function used to get an attribute from a key of the model data.
    Depending on the model type (circuit, magnet, conductor), the data structure to access is different.
    Also, there is a special case when the variable to read is a sub-key of the Conductors key. In such a case, an additional parameter idx_conductor must be defined (see below).
    :param case_model: Model type
    :param builder_model: BuilderModel or BuilderCosim object to access
    :param name_variable: Name of the variable to read
    :param idx_conductor: When defined (and if case_model is 'magnet' or 'conductor'), a sub-key form the Conductors key is read. The index of the conductor to read is defined by idx_conductor
    :param name_simulation_set: When defined (and if case_model is 'cosim'), a sub-key form the Simulations key is read. The dictionary key of the simulation set to read is defined by name_simulation_set
    :return: Value of the variable to get
    """

    if case_model == 'magnet':
        if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
            value = rgetattr(builder_model.model_data, name_variable)
        else:
            value = rgetattr(builder_model.model_data.Conductors[idx_conductor], name_variable)
    elif case_model == 'conductor':
        if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
            value = rgetattr(builder_model.conductor_data, name_variable)
        else:
            value = rgetattr(builder_model.conductor_data.Conductors[idx_conductor], name_variable)
    elif case_model == 'circuit':
        # If the attribute is a dict, and a certain key of this dict has been specified for change,
        # the following piece of code will be run:
        if "Netlist[" in name_variable and "]" in name_variable:  # Special case: this means an entry Netlist was defined.
            component_name = name_variable.split("Netlist[")[1].split(']')[0]
            component_attribute = name_variable.split("Netlist[")[1].split(']')[1].strip('.')
            value = getattr(builder_model.circuit_data.Netlist[component_name], component_attribute)
        elif "[" in name_variable and "]" in name_variable:  # this means an entry of a dict was defined.
            dict_name = name_variable.split("[")[0]
            dict_entries = rgetattr(builder_model.circuit_data, dict_name)
            dict_key = re.search(r"\[(.*?)\]", name_variable).group(1)
            dict_key = dict_key.strip('"').strip("'")  # remove any " or ' symbol from the dictionary key
            value = dict_entries[dict_key]
        else:
            value = rgetattr(builder_model.circuit_data, name_variable)
    elif case_model == 'cosim':
        if name_simulation_set is None:  # Standard case when the variable to change is not the Conductors key
            value = rgetattr(builder_model.cosim_data, name_variable)
        else:
            value = rgetattr(builder_model.cosim_data.Simulations[name_simulation_set], name_variable)
    else:
        raise Exception(f'Model type not supported: case_model={case_model}')
    return value


def set_attribute_model(case_model: str, builder_model: object, name_variable: str,
                        value_variable: Union[int, float, str], idx_conductor: int = None):
    """
    Helper function used to set a key of the model data to a certain value.
    Depending on the model type (circuit, magnet, conductor), the data structure to access is different.
    Also, there is a special case when the variable to change is a sub-key of the Conductors key. In such a case, an additional parameter idx_conductor must be defined (see below).
    :param case_model: Model type
    :param builder_model: BuilderModel or BuilderCosim object to access
    :param name_variable: Name of the variable to change
    :param value_variable: New value of the variable of the variable
    :param idx_conductor: When defined, a sub-key form the Conductors key is read. The index of the conductor to read is defined by idx_conductor
    :return: Value of the variable to get
    """

    if case_model == 'magnet':
        if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
            rsetattr(builder_model.model_data, name_variable, value_variable)
        else:
            rsetattr(builder_model.model_data.Conductors[idx_conductor], name_variable, value_variable)
    elif case_model == 'conductor':
        if idx_conductor is None:  # Standard case when the variable to change is not the Conductors key
            rsetattr(builder_model.conductor_data, name_variable, value_variable)
        else:
            rsetattr(builder_model.conductor_data.Conductors[idx_conductor], name_variable, value_variable)
    elif case_model == 'circuit':
        # If the attribute is a dict, and a certain key of this dict has been specified for change,
        # the following piece of code will be run:
        if "Netlist[" in name_variable and "]" in name_variable:  # Special case: this means an entry Netlist was defined.
            component_name = name_variable.split("Netlist[")[1].split(']')[0]
            component_attribute = name_variable.split("Netlist[")[1].split(']')[1].strip('.')
            setattr(builder_model.circuit_data.Netlist[component_name], component_attribute, value_variable)
            rsetattr(builder_model.circuit_data, 'Netlist', builder_model.circuit_data.Netlist)
        elif "[" in name_variable and "]" in name_variable:  # this means an entry of a dict was defined.
            dict_name = name_variable.split("[")[0]
            dict_key = re.search(r"\[(.*?)\]", name_variable).group(1)
            dict_entries = rgetattr(builder_model.circuit_data, dict_name)
            dict_key = dict_key.strip('"').strip("'")  # remove any " or ' symbol from the dictionary key
            dict_entries[dict_key] = value_variable
            rsetattr(builder_model.circuit_data, dict_name, dict_entries)
        else:
            rsetattr(builder_model.circuit_data, name_variable, value_variable)
    elif case_model == 'cosim':
        rsetattr(builder_model.cosim_data, name_variable, value_variable)
    else:
        raise Exception(f'Model type not supported: case_model={case_model}')
