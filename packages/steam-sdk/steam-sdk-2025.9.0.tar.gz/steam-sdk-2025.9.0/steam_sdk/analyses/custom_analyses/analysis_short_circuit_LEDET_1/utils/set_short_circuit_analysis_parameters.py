import numpy as np
import pandas as pd

from steam_sdk.data.DataAnalysis import ModifyModelMultipleVariables
from steam_sdk.utils.tic_toc import toc


def set_short_circuit_analysis_parameters(aSTEAM, dict_LEDET, RRR, Jc_fit_C1_CUDI1, Jc_fit_C2_CUDI1, scale_cooling_to_heat_sink, scale_heat_diffusion_between_turns, R_short_circuit, verbose):  # pragma: no cover
    # Function to set up the unknown parameters that directly affect the short-circuit analysis (typically changed in a parametric sweep)
    # TODO: Known issue: The conductor parameters are not updated properly in case more than one conductor is used in the magnet

    # Apply scaling factor to all elements of these variables
    sim3D_f_cooling_down  = [x * scale_cooling_to_heat_sink for x in dict_LEDET['sim3D_f_cooling_down']]
    sim3D_f_cooling_up    = [x * scale_cooling_to_heat_sink for x in dict_LEDET['sim3D_f_cooling_up']]
    sim3D_f_cooling_left  = [x * scale_cooling_to_heat_sink for x in dict_LEDET['sim3D_f_cooling_left']]
    sim3D_f_cooling_right = [x * scale_cooling_to_heat_sink for x in dict_LEDET['sim3D_f_cooling_right']]

    # Add parameter values to analysis step
    current_step = 'set_short_circuit_analysis_parameters'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step] = ModifyModelMultipleVariables(type='ModifyModelMultipleVariables')
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].model_name = 'BM'
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_to_change = [
        'Conductors[0].strand.RRR',
        'Conductors[0].Jc_fit.C1_CUDI1',
        'Conductors[0].Jc_fit.C2_CUDI1',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_down',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_up',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_left',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_right',
        'Options_LEDET.simulation_3D.sim3D_fExUD',
        'Options_LEDET.simulation_3D.sim3D_fExLR',
        'Options_LEDET.simulation_3D.sim3D_R_shortCircuit',
    ]
    aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_value = [
        [RRR],
        [Jc_fit_C1_CUDI1],
        [Jc_fit_C2_CUDI1],
        [sim3D_f_cooling_down],
        [sim3D_f_cooling_up],
        [sim3D_f_cooling_left],
        [sim3D_f_cooling_right],
        [scale_heat_diffusion_between_turns],
        [scale_heat_diffusion_between_turns],
        [R_short_circuit],
    ]
    aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)


    if verbose:
        print(f'Step "{current_step}" added to the STEAM analysis')
        toc()

    return
