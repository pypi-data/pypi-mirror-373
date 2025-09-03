import copy
import os
from pathlib import Path
from typing import Union

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.data.DataCoSim import NSTI
from steam_sdk.data.DataModelCosim import DataModelCosim
from steam_sdk.data.DataModelCosim import sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.utils.attribute_model import get_attribute_model, set_attribute_model
from steam_sdk.utils.sgetattr import rsetattr


def write_model_input_files(cosim_data: DataModelCosim,
                            model: Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE],
                            cosim_software: str,
                            data_settings: DataSettings,
                            extra_dicts_with_change: dict = None,
                            nsti: NSTI = None,
                            verbose: bool = False):
    '''
    Make all required input files for the selected model. Save them to the COSIM subfolder. Delete temporary files.
    This method does not depend on the software tool
    :param cosim_data TODO
    :param model: Object defining the model information
    :param cosim_software: Name of the software (supported: COSIM, PyCosim)
    :param data_settings: DataSettings object containing all settings, previously read from user specific settings.SYSTEM.yaml file or from a STEAM analysis permanent settings
    :param nsti: NSTI parameters. N=Simulation number, S=Simulation set, T=Time window, I=Iteration
    :type nsti: NSTI
    :param extra_dicts_with_change Additional parameters to change. These will be changed AFTER the parameter changes defined by model.variables_to_modify_pre_cosim, model.variables_to_modify_cosim, or model.variables_to_modify_post_cosim
    :param verbose: If True, display information while running
    :return:
    '''
    # Unpack input
    model_data_name = model.modelName
    case_model = model.modelCase
    software = model.type
    simulation_name = model.modelName
    # simulation_number = model.simulationNumber if hasattr(model, 'simulationNumber') else None  # PSPICE netlists don't have number
    n_time_windows = len(cosim_data.Options_COSIM.Settings.Time_Windows.t_0) if cosim_software == 'COSIM' else len(model.CoSim.variables_to_modify_for_each_time_window)

    # TODO variables_to_change, variables_values should be defined based on a new argmetn 1,2,3... defining whether it's pre-cosim, cosim, or post-cosim
    if nsti.t == 0:  # Before the first time
        variables_to_change = copy.deepcopy(list(model.PreCoSim.variables_to_modify_time_window.keys()))
        variables_values = copy.deepcopy(list(model.PreCoSim.variables_to_modify_time_window.values()))
    elif nsti.t > n_time_windows:  # Final simulation after the last time window
        variables_to_change = copy.deepcopy(list(model.PostCoSim.variables_to_modify_time_window.keys()))
        variables_values = copy.deepcopy(list(model.PostCoSim.variables_to_modify_time_window.values()))
    else:  # Co-simulation
        variables_to_change = copy.deepcopy(list(model.CoSim.variables_to_modify_iteration.keys()))    #TODO deal with variables_to_modify_time_window
        variables_values = copy.deepcopy(list(model.CoSim.variables_to_modify_iteration.values()))
    # Add extra variables to change
    if extra_dicts_with_change is not None:
        variables_to_change = variables_to_change + list(extra_dicts_with_change.keys())
        variables_values = variables_values + list(extra_dicts_with_change.values())

    # Apply replacements to string variables and list-of-strings variables
    variables_values_templated = []
    replacements = {
        'modelName': model.modelName,
        'n_s_t_i': nsti.n_s_t_i,
        'n': nsti.n,
        's': nsti.s,
        't': nsti.t,
        'i': nsti.i,
    }
    for var_value in variables_values:
        if isinstance(var_value, str):
            # If the variable is a string, apply replacements
            var_value = template_replace(var_value, replacements)
        elif isinstance(var_value, list):
            # If the variable is a list, go through all of its elements and apply replacements to all strings
            for v, var_value_in_list in enumerate(var_value):
                if isinstance(var_value_in_list, str):
                    var_value_in_list = template_replace(var_value_in_list, replacements)
                    var_value[v] = var_value_in_list
        variables_values_templated.append(var_value)
    variables_values = variables_values_templated

    cosim_name = cosim_data.GeneralParameters.cosim_name
    cosim_number = str(nsti.n)

    # Define folder paths
    if cosim_software == 'COSIM':
        local_cosim_folder = data_settings.local_COSIM_folder
        if software == 'FiQuS':
            raise ValueError(f'FiQuS does not support COSIM. Please use PyCoSim instead')
        elif software == 'LEDET':
            local_folder = os.path.join(local_cosim_folder, cosim_name, cosim_number, 'Input', model.name, 'LEDET')
        elif software == 'PSPICE':
            local_folder = os.path.join(local_cosim_folder, cosim_name, cosim_number, 'Input', model.name)
        if software == 'XYCE':
            local_folder = os.path.join(local_cosim_folder, cosim_name, cosim_number, 'Input', model.name)
    elif cosim_software == 'PyCoSim':
        local_cosim_folder = data_settings.local_PyCoSim_folder
        local_folder_prefix = os.path.join(local_cosim_folder, cosim_name, software)
        if software == 'FiQuS':
            local_folder = os.path.join(local_folder_prefix, model.modelName)  # use model set in the input folder name
        elif software == 'LEDET':
            local_folder = os.path.join(local_folder_prefix, str(nsti.n))
        elif software in ['PSPICE', 'XYCE']:
            local_folder = os.path.join(local_folder_prefix, str(nsti.n), str(nsti.n_s_t_i))  #TODO double check
    else:
         raise Exception(f'Co-simulation software {cosim_software} not supported.')

    # Always assume the STEAM models folder structure, which contains subfolders "circuits", "conductors", "cosims", "magnets"
    file_model_data = str(Path(os.path.join(data_settings.local_library_path, f'{case_model}s', model_data_name, 'input', f'modelData_{model_data_name}.yaml')).resolve())
    # Make BuilderModel object
    BM = BuilderModel(file_model_data=file_model_data, case_model=case_model, data_settings=data_settings, verbose=verbose)
    # Edit BuilderModel object with the variable changes set in the input file
    if not len(variables_to_change) == len(variables_values):
        raise Exception(f'Variables variables_to_change and variables_values must have the same length.')
    for v, (variable_to_change, value) in enumerate(zip(variables_to_change, variables_values)):
        if verbose:
            print(f'Modify variable {variable_to_change} to value {value}.')
        if 'Conductors[' in variable_to_change:  # Special case when the variable to change is the Conductors key
            idx_conductor = int(variable_to_change.split('Conductors[')[1].split(']')[0])
            conductor_variable_to_change = variable_to_change.split('].')[1]

            if verbose:
                print(f'Variable {variable_to_change} is treated as a Conductors key. Conductor index: #{idx_conductor}. Conductor variable to change: {conductor_variable_to_change}.')
                old_value = get_attribute_model(case_model, BM, conductor_variable_to_change, idx_conductor)
                print(f'Variable {conductor_variable_to_change} changed from {old_value} to {value}.')

            if case_model == 'conductor':
                rsetattr(BM.conductor_data.Conductors[idx_conductor], conductor_variable_to_change, value)
            elif case_model == 'magnet':
                rsetattr(BM.model_data.Conductors[idx_conductor], conductor_variable_to_change, value)
            else:
                raise Exception(f'The selected case {case_model} is incompatible with the variable to change {variable_to_change}.')
        # TODO deal with the case where the entry to change contains "Netlist["
        else:  # Standard case when the variable to change is not the Conductors key
            if verbose:
                old_value = get_attribute_model(case_model, BM, variable_to_change)
                print(f'Variable {variable_to_change} changed from {old_value} to {value}.')
            set_attribute_model(case_model, BM, variable_to_change, value)
    # Write output of the BuilderModel object
    if 'FiQuS' == software:
        if BM.model_data.Options_FiQuS.run.type in ['start_from_yaml', 'solve_with_post_process_python']:
            variable_to_change = 'Options_FiQuS.run.solution'
            value = nsti.n_s_t_i
            set_attribute_model(case_model, BM, variable_to_change, value)
        BM.buildFiQuS(sim_name=model.modelName, sim_number=f'{nsti.n_s_t_i}', output_path=local_folder,
                      flag_plot_all=False, verbose=False)  # flag_plot_all, verbose all hard-coded to False to avoid unwanted plots, and logging info
    elif 'LEDET' == software:
        sim_number = nsti.n if cosim_software == 'COSIM' else f'_{nsti.n_s_t_i}'
        # Write LEDET model
        local_model_folder = str(Path(Path(local_folder) / simulation_name / 'Input').resolve())
        field_maps_folder = Path(Path(local_folder) / '..' / 'Field maps' / simulation_name).resolve()  # The map2d files are written in a subfolder {simulation_name} inside a folder "Field maps" at the same level as the LEDET folder [this structure is hard-coded in STEAM-LEDET]
        BM.buildLEDET(sim_name=simulation_name, sim_number=sim_number,  # TODO edit nsti.n
                      output_path=local_model_folder, output_path_field_maps=field_maps_folder,
                      flag_json=False, flag_plot_all=False, verbose=False)  # flag_json, flag_plot_all, verbose all hard-coded to False to avoid unwanted files, plots, and logging info
    elif 'PSPICE' == software:
        # Write PSPICE model
        local_model_folder = str(Path(local_folder).resolve())
        BM.buildPSPICE(sim_name=simulation_name, sim_number='', output_path=local_model_folder, verbose=verbose)
    elif 'XYCE' == software:
        raise Exception(f'Writing of {software} models not yet supported within ParserCOSIM.')
    else:
        raise Exception(f'Writing of {software} models not yet supported within ParserCOSIM.')

    return BM


def template_replace(template_str, replacements):
    """
    Replaces placeholders in the format <<entry_name>> with entry_value in the template string.

    Args:
    template_str (str): The template string containing placeholders.
    replacements (dict): A dictionary where keys are the entry names and values are the entry values.

    Returns:
    str: The template string with placeholders replaced by their corresponding values.
    """
    for entry_name, entry_value in replacements.items():
        placeholder = f'<<{entry_name}>>'
        if template_str is not None:    # this is to deal with data model entries being None
            template_str = template_str.replace(placeholder, str(entry_value))
    try:
        template_str = int(template_str)    # To avoid pydantic validation errors convert back entries that are string representation of integer to integer
    except ValueError:
        pass
    return template_str
