import numpy as np
import pandas as pd

from steam_sdk.data.DataAnalysis import SetUpFolder, MakeModel, ModifyModelMultipleVariables
from steam_sdk.utils.tic_toc import toc


def set_common_parameters(aSTEAM, magnet_name, magnet_name_short_circuit, list_software, dict_LEDET, verbose):  # pragma: no cover
    # Function to set up all parameters needed for a short-circuit analysis that are not dependent on the magnet nor on the short-circuit position

    # Unpack variables
    nT                       = dict_LEDET['nT']
    el_order_half_turns      = dict_LEDET['el_order_half_turns']
    iContactAlongWidth_From  = dict_LEDET['iContactAlongWidth_From']
    iContactAlongWidth_To    = dict_LEDET['iContactAlongWidth_To']
    iContactAlongHeight_From = dict_LEDET['iContactAlongHeight_From']
    iContactAlongHeight_To   = dict_LEDET['iContactAlongHeight_To']

    # Add step to set up LEDET folder model
    step_setup_folder = 'setup_folder'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder] = SetUpFolder(type='SetUpFolder')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder].simulation_name = f'{magnet_name_short_circuit}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder].software = list_software
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_setup_folder)

    if verbose:
        print(f'Step "{step_setup_folder}" added to the STEAM analysis')
        toc()


    # Add step to import reference model
    step_ref_model = 'make_reference_model'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model] = MakeModel(type='MakeModel')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].model_name = 'BM'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].file_model_data = f'{magnet_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].case_model = 'magnet'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].software = []
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].simulation_name = None
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].simulation_number = None
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_build = True  # important to keep True since it calculates the edited map2d file
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].verbose = True
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_plot_all = False
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_json = False
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_ref_model)

    if verbose:
        print(f'Step "{step_ref_model}" added to the STEAM analysis')
        toc()


    # Setting the thermal links, i.e. the pairs of half-turns that are physically adjacent
    # Note 1: Setting Sources.magnetic_field_fromROXIE to None will cause STEAM_SDK to ignore the map2d file
    # Note 2: Since thermal links along the conductor long side (i.e. along its width) are calculated automatically only between half-turns within the same group, and since the groups are re-calculated depending on the short-cicuit location, the thermal links will be read from the reference LEDET file and imposed
    # Note 3: Since with STEAM_SDK current version [0.0.114], thermal links along the conductor short side (i.e. along its height) are calculated using strand x and y positions from the map2d file, they will be read from the reference LEDET file and imposed
    iContactAlongWidth_pairs_to_add = []
    for ht in range(len(iContactAlongWidth_From)):
        iContactAlongWidth_pairs_to_add.append([iContactAlongWidth_From[ht], iContactAlongWidth_To[ht]])
    iContactAlongHeight_pairs_to_add = []
    for ht in range(len(iContactAlongHeight_From)):
        iContactAlongHeight_pairs_to_add.append([iContactAlongHeight_From[ht], iContactAlongHeight_To[ht]])

    # Add parameter values to analysis step
    current_step = 'set_common_parameters'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step] = ModifyModelMultipleVariables(type='ModifyModelMultipleVariables')
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].model_name = 'BM'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_to_change = [
        'Sources.magnetic_field_fromROXIE',
        'GeneralParameters.magnet_name',
        'GeneralParameters.model.case',
        'GeneralParameters.model.state',
        'CoilWindings.n_half_turn_in_group',
        'CoilWindings.electrical_pairs.overwrite_electrical_order',
        'Quench_Protection.CLIQ.current_direction',
        'Options_LEDET.heat_exchange.iContactAlongWidth_pairs_to_add',
        'Options_LEDET.heat_exchange.iContactAlongHeight_pairs_to_add',
        'Options_LEDET.heat_exchange.iContactAlongHeight_pairs_to_remove',  # to remove pair [1, 1]
        'Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable',
        'Options_LEDET.field_map_files.flag_calculateMagneticField',  # set to =1 to calculate the magnetic-field map at the beginning of each simulation (avoids having to write field maps)
        'Options_LEDET.physics.flag_ScaleDownSuperposedMagneticField',  # set to =2 to scale the calculated magnetic-field maps
        'Options_LEDET.post_processing.flag_saveMatFile',
        'Options_LEDET.post_processing.tQuench',
        'Options_LEDET.post_processing.initialQuenchTemp',
        'Options_LEDET.simulation_3D.flag_3D',
        'Options_LEDET.simulation_3D.flag_adaptiveTimeStepping',
        'Options_LEDET.simulation_3D.sim3D_uThreshold',
        'Options_LEDET.simulation_3D.sim3D_Tpulse_peakT',
        'Options_LEDET.simulation_3D.sim3D_Tpulse_width',
        'Options_LEDET.simulation_3D.sim3D_tShortCircuit',
        'Options_LEDET.simulation_3D.sim3D_coilSectionsShortCircuit',
    ]
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_value = [
        [None],  # to avoid reading conductor parameters from map2d file
        [f'{magnet_name_short_circuit}'],
        ['short_circuit'],
        ['ongoing'],
        [nT],
        [el_order_half_turns],
        [[1, -1]],
        [iContactAlongWidth_pairs_to_add],
        [iContactAlongHeight_pairs_to_add],
        [[[1, 1]]],
        [1],  # to check
        [1],
        [2],
        [2],
        [[0.0, 0.0]],
        [[10.0, 10.0]],
        [1],
        [1],
        [99999999.0],
        [1.900001],
        [0.05],
        [0.0],
        [[1, -1]],
    ]
    aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)


    if verbose:
        print(f'Step "{current_step}" added to the STEAM analysis')
        toc()

    return
