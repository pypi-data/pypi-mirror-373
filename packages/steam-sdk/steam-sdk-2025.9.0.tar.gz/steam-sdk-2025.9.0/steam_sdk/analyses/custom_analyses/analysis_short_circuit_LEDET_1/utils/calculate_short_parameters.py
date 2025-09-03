import h5py
import numpy as np
import pandas as pd

from steam_sdk.data.DataAnalysis import ModifyModelMultipleVariables
from steam_sdk.utils.tic_toc import toc
from steam_sdk.utils.unique import unique


########################################################################################################################
# Helper functions

def calculate_short_parameters(start_index, pair, short_position_name,
                               idx_contact_from, idx_contact_to,
                               M, length_short_circuit,
                               dict_LEDET, magnet_name, list_software,
                               path_file_model_geometry, aSTEAM, df_M12, verbose):  # pragma: no cover
    # Function to calculate all possible internal short-circuit locations based on the half-turn physical proximity
    # The function also updates the dataframe df_M12 with relevant information
    # Note 1: In this function when suffix "_reordered" is included in a variable's name it signifies the variable follows the electrical order
    # Note 2: The variable "pair" is indexed starting from 1, not 0
    # Note 3: The variables "idx_contact_from" and "idx_contact_to" are modified versions of iContactAlongWidth_From/iContactAlongWidth_To/iContactAlongHeight_From/iContactAlongHeight_To (without high indices), but the latter are also needed and will be read from dict_LEDET
    # Note 4: The variable "short_position_name" defines the name of the short-circuit position

    # Define global variables
    label_suffix = 'modify_model_short_location_'  # Known maintainance issue: This variable needs to have the same value in the function set_simulations_to_prepare_run
    original_pair_idx = pair       # used to access the indexed pair from the variables idx_contact_from and idx_contact_to
    pair = pair + start_index - 1  # used to keep track of increasing simulation number when this function is called repeatedly

    # Unpack variables
    nT = dict_LEDET['nT']
    polarities_inGroup = dict_LEDET['polarities_inGroup']
    l_mag_inGroup = dict_LEDET['l_mag_inGroup']
    el_order_half_turns = np.array(dict_LEDET['el_order_half_turns'])
    iContactAlongWidth_From = dict_LEDET['iContactAlongWidth_From']
    iContactAlongWidth_To = dict_LEDET['iContactAlongWidth_To']
    iContactAlongHeight_From = dict_LEDET['iContactAlongHeight_From']
    iContactAlongHeight_To = dict_LEDET['iContactAlongHeight_To']

    # Calculate electrical order of the turns (for each consecutive pair of half-turns, take the one with smaller index)
    el_order_turns = []
    for ht in range(int(len(el_order_half_turns) / 2)):
        el_order_turns.append(min(el_order_half_turns[ht * 2], el_order_half_turns[ht * 2 + 1]))
    # n_turns = len(el_order_turns)

    # Read model geometry from .mat file
    with h5py.File(path_file_model_geometry, 'r') as simulationSignals:
        sAvePositions     = np.array(simulationSignals['model_geometry']['sAvePositions'])
        ds_mesh           = np.array(simulationSignals['model_geometry']['ds'])
        nodeToHalfTurn    = np.array(simulationSignals['model_geometry']['nodeToHalfTurn'])
        total_coil_length = np.array(simulationSignals['model_geometry']['L'])


    ####################################################################################################################
    # Calculate useful indices
    n_turns = len(el_order_turns)

    # Current pair of half-turns that are in physical contact (first element has index 1)
    idx_from_reordered = np.where(el_order_half_turns == idx_contact_from[original_pair_idx])[0] + 1
    idx_to_reordered = np.where(el_order_half_turns == idx_contact_to[original_pair_idx])[0] + 1

    # Find half-turns that would be shorted if a short-circuit occurred between the two selected half-turns (first element has index 1)
    # Note: the last half-turn is not by-passed by the short; for example, if the short is between turns 1 and 2 only turn 1 is shorted
    idx_shorted_reordered = np.arange(min(idx_from_reordered, idx_to_reordered), max(idx_from_reordered, idx_to_reordered))
    idx_shorted = el_order_half_turns[idx_shorted_reordered - 1]

    # Since each consecutive pair of half-turns forms a turn, the turn indices can be found by deleting indices with value higher than half of the number of turns, i.e. the half-turns defining return paths (first element has index 1)
    idx_turn_shorted = idx_shorted[idx_shorted <= n_turns]
    idx_turn_not_shorted = np.setdiff1d(el_order_turns, idx_turn_shorted)  # found by removing the values "idx_turn_shorted" from "el_order_turns"
    idx_turn_shorted_reordered = np.where(np.in1d(el_order_turns, idx_turn_shorted))[0] + 1
    n_turns_shorted = len(idx_turn_shorted)

    if verbose:
        print(f'Pair #{pair + 1}: From half-turn {idx_contact_from[original_pair_idx]} to {idx_contact_to[original_pair_idx]}, in electrical positions {idx_from_reordered} and {idx_to_reordered}. Shorted turn in el position: {idx_turn_shorted_reordered}. Shorted half-turns: {idx_shorted} in el positions: {idx_shorted_reordered}')


    ####################################################################################################################
    # Calculate new conductor groups and parameters. The goal of this code section is to assign shorted turns to separate groups, which will be assigned to Coil Section #2
    n_groups = len(polarities_inGroup)
    conductor_to_group, group_to_coil_section, polarities_in_group, n_half_turn_in_group, half_turn_length = [], [], [], [], []
    current_ht    = 0  # index of the current half-turn, starting from 0
    if verbose: print(f'idx_shorted={idx_shorted}')
    for group in range(n_groups):
        idx_ht_in_group = np.r_[current_ht+1:current_ht+nT[group]+1]  # first index is 1
        idx_ht_shorted_in_group = np.where(np.in1d(idx_ht_in_group, idx_shorted))[0]  # first index is 1
        if len(idx_ht_shorted_in_group) == 0:
            # the current group does not contain any shorted half-turns, so there is no need to split it
            if verbose: print(f'group {group + 1} does not contain any shorted half-turn.')
            conductor_to_group.append(1)  # hard-coded, only one conductor is supported
            group_to_coil_section.append(1)  # not-shorted turns/groups assigned to Coil Section #1
            polarities_in_group.append(polarities_inGroup[group])
            n_half_turn_in_group.append(nT[group])
            half_turn_length.append(l_mag_inGroup[group])
        elif len(idx_ht_shorted_in_group) == nT[group]:
            # the current group contains only shorted half-turns, so there is no need to split it
            if verbose: print(f'group {group + 1} contains only shorted half-turns.')
            conductor_to_group.append(1)  # hard-coded, only one conductor is supported
            group_to_coil_section.append(2)  # shorted turns/groups assigned to Coil Section #2
            polarities_in_group.append(polarities_inGroup[group])
            n_half_turn_in_group.append(nT[group])
            half_turn_length.append(l_mag_inGroup[group])
        else:
            # the current group contains shorted and not-shorted turns, so it must be split in multiple groups
            if verbose: print(f'group {group+1} contains shorted and not-shorted turns. idx_ht_shorted_in_group: {idx_ht_shorted_in_group}')

            for i in idx_ht_in_group:
                if (i == idx_ht_in_group[0]) or ((i in idx_shorted) != (i-1 in idx_shorted)):
                    if verbose: print(f'half-turn {i} beginning of a new group')
                    conductor_to_group.append(1)  # hard-coded, only one conductor is supported
                    group_to_coil_section.append(2) if (i in idx_shorted) else group_to_coil_section.append(1)  # shorted turns/groups assigned to Coil Section #2
                    polarities_in_group.append(polarities_inGroup[group])
                    n_half_turn_in_group.append(1)  # this value might be increased if more half-turns are added to this group later
                    half_turn_length.append(l_mag_inGroup[group])
                else:
                    n_half_turn_in_group[-1] = n_half_turn_in_group[-1] + 1  # add one more half-turn to this group. This value might be increased again if more half-turns are added to this group later
                if verbose: print(f'n_half_turn_in_group[-1]={n_half_turn_in_group[-1]}')

        current_ht = current_ht + nT[group]


    ####################################################################################################################
    # Calculate new self-mutual inductance matrix
    # Reminder: The turns in matrices M and M_new are ordered following the ROXIE/STEAM order, and not the electrical order
    M_new = np.empty((2, 2))
    M_new[0, 0] = np.sum(M[idx_turn_not_shorted[:, None]-1, idx_turn_not_shorted-1])
    M_new[1, 1] = np.sum(M[idx_turn_shorted[:, None]-1, idx_turn_shorted-1])
    M_new[0, 1] = M_new[1, 0] = np.sum(M[idx_turn_not_shorted[:, None]-1, idx_turn_shorted-1])
    if verbose: print(f'M_new: {M_new}')


    ####################################################################################################################
    # Identify indices of the two half-turns where the short-circuit power is dissipated
    sim3D_idxFinerMeshHalfTurn = [int(idx_contact_from[original_pair_idx]), int(idx_contact_to[original_pair_idx])]

    # Identify the half-turns that are physically adjacent to the above-mentioned half-turns, to which finer mesh will be applied as well - contact along width
    for i in np.where(iContactAlongWidth_From == idx_contact_from[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongWidth_To[i])  # add half-turns touching the 1st half-turn along its width
    for i in np.where(iContactAlongWidth_To == idx_contact_from[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongWidth_From[i])  # add half-turns touching the 1st half-turn along its width (repeated in case the index is in "to" and not "from")
    for i in np.where(iContactAlongWidth_From == idx_contact_to[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongWidth_To[i])  # add half-turns touching the 2nd half-turn along its width
    for i in np.where(iContactAlongWidth_To == idx_contact_to[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongWidth_From[i])  # add half-turns touching the 2nd half-turn along its width (repeated in case the index is in "to" and not "from")

    # Identify the half-turns that are physically adjacent to the above-mentioned half-turns, to which finer mesh will be applied as well - contact along height
    for i in np.where(iContactAlongHeight_From == idx_contact_from[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongHeight_To[i])  # add half-turns touching the 1st half-turn along its height
    for i in np.where(iContactAlongHeight_To == idx_contact_from[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongHeight_From[i])  # add half-turns touching the 1st half-turn along its height (repeated in case the index is in "to" and not "from")
    for i in np.where(iContactAlongHeight_From == idx_contact_to[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongHeight_To[i])  # add half-turns touching the 2nd half-turn along its height
    for i in np.where(iContactAlongHeight_To == idx_contact_to[original_pair_idx])[0]:
        sim3D_idxFinerMeshHalfTurn.append(iContactAlongHeight_From[i])  # add half-turns touching the 2nd half-turn along its height (repeated in case the index is in "to" and not "from")

    # Remove duplicates
    sim3D_idxFinerMeshHalfTurn = unique(sim3D_idxFinerMeshHalfTurn)
    # Convert elements to int
    sim3D_idxFinerMeshHalfTurn = [int(i) for i in sim3D_idxFinerMeshHalfTurn]

    # Calculate short-circuit location along the coil, in the first half-turn where the short occurs (assumtion: short occurs at the middle point along the length)
    # Note: The nodeToHalfTurn variable orders the nodes following their electrical order. This is why in this code section the variables "idx_from_reordered" and "idx_to_reordered" are used
    cumulative_length_all_half_turns = np.append(0, np.cumsum(ds_mesh))
    idx_nodes_shorted_half_turn_1st = np.where(nodeToHalfTurn == idx_from_reordered)[0]
    start_location_half_turn_1st = cumulative_length_all_half_turns[idx_nodes_shorted_half_turn_1st[0]]
    cumulative_length_half_turn_1st = np.cumsum(ds_mesh[idx_nodes_shorted_half_turn_1st])
    middle_point_half_turn_1st = start_location_half_turn_1st + cumulative_length_half_turn_1st[-1] / 2

    # Calculate short-circuit location along the coil, in the second half-turn where the short occurs (assumtion: short occurs at the middle point along the length)
    idx_nodes_shorted_half_turn_2nd = np.where(nodeToHalfTurn == idx_to_reordered)[0]
    start_location_half_turn_2nd = cumulative_length_all_half_turns[idx_nodes_shorted_half_turn_2nd[0]]
    middle_point_half_turn_2nd = start_location_half_turn_2nd + cumulative_length_half_turn_1st[-1] / 2
    # Note: using the same variable (cumulative_length_half_turn_1st[-1]/2) as the previous half-turn to make the locations match. This is supposed to reproduce how LEDET will calculate the nodes where the short-circuit power is deposited

    sim3D_shortCircuitPosition = [
        [float(middle_point_half_turn_1st - length_short_circuit / 2), float(middle_point_half_turn_1st + length_short_circuit / 2)],
        [float(middle_point_half_turn_2nd - length_short_circuit / 2), float(middle_point_half_turn_2nd + length_short_circuit / 2)],
    ]

    # Calculate most likely quench position, i.e. the position where the short-circuit occurs (this will help displaying the temperature evolution in the LEDET pdf report)
    sim3D_Tpulse_sPosition = float(np.mean(sim3D_shortCircuitPosition[0]))  # Average of the start/end positions of the short-circuit in the first half-turn

    #TODO: half-turns receiving the power: double-check

    #TODO: field map in LEDET? add new keys?


    # Add calculated values to analysis step
    current_step = f'{label_suffix}{pair+1}'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step] = ModifyModelMultipleVariables(type='ModifyModelMultipleVariables')
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].model_name = 'BM'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_to_change = [
        'CoilWindings.conductor_to_group',
        'CoilWindings.group_to_coil_section',
        'CoilWindings.polarities_in_group',
        'CoilWindings.n_half_turn_in_group',
        'CoilWindings.half_turn_length',
        'Options_LEDET.magnet_inductance.flag_calculate_inductance',
        'Options_LEDET.magnet_inductance.overwrite_inductance_coil_sections',
        'Options_LEDET.simulation_3D.sim3D_idxFinerMeshHalfTurn',
        'Options_LEDET.simulation_3D.sim3D_Tpulse_sPosition',
        'Options_LEDET.simulation_3D.sim3D_shortCircuitPosition',
    ]
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_value = [
        [conductor_to_group],
        [group_to_coil_section],
        [polarities_in_group],
        [n_half_turn_in_group],
        [half_turn_length],
        [False],
        [M_new.tolist()],
        [sim3D_idxFinerMeshHalfTurn],
        [sim3D_Tpulse_sPosition],
        [sim3D_shortCircuitPosition],
    ]
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_name = f'{magnet_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].software = list_software
    aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)


    # Add row to dataframe
    entry = pd.DataFrame(
        {
            # 'pair ': f'{label_suffix}{original_pair_idx + 1}',  # not needed
            'short circuit position [-]': short_position_name,
            'idx_ht_from (STEAM order)': idx_contact_from[original_pair_idx],
            'idx_ht_to (STEAM order)': idx_contact_to[original_pair_idx],
            'idx_turns_shorted (el order)': str(idx_turn_shorted_reordered), # TODO: improve formatting
            'n_turns_shorted': n_turns_shorted,
            'M11': M_new[0, 0],
            'M22': M_new[1, 1],
            'M12': M_new[0, 1]
        },
            index=[pair + 1])
    df_M12 = pd.concat([df_M12, entry], axis=0)


    if verbose: toc()

    return M_new, df_M12

