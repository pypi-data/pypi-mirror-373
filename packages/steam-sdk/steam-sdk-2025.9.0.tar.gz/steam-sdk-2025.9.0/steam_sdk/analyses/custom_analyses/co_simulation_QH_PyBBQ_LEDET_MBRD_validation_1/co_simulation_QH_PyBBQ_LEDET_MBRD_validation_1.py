from pathlib import Path

import numpy as np
import os
import yaml
from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.parsers.ParserCsv import get_signals_from_csv
from steam_sdk.data.DataModelConductor import DataModelConductor
from typing import Dict
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.data.DataAnalysis import ModifyModelMultipleVariables
from steam_sdk.builders.BuilderModel import BuilderModel

from steam_sdk.analyses.custom_analyses.co_simulation_QH_PyBBQ_LEDET_MBRD_validation_1.utils.create_conductor_analysis_file import create_conductor_analysis_file
from steam_sdk.analyses.custom_analyses.co_simulation_QH_PyBBQ_LEDET_MBRD_validation_1.utils.create_magnet_analysis_file import create_magnet_analysis_file
from steam_sdk.analyses.custom_analyses.co_simulation_QH_PyBBQ_LEDET_MBRD_validation_1.utils.calculate_quench_propagation_velocity import _quenchPropagationVelocity

def co_simulation_QH_PyBBQ_LEDET_MBRD_validation_1(dict_inputs: Dict):  # pragma: no cover

    """
    Function to run a co-simulation for the MBRD short model magnet including PyBBQ and Ledet
    :param dict_inputs: Dictionary that contains all variable input variables
    :return:
    """

    # validation specific inputs
    maxVoltagePC = 5.0
    t_off = 0.02
    t_control_LUT = [-0.02, 0.02, 0.03]
    iStartQuench = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248]
    tStartQuench = [99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0, 99999.0]
    magnetic_length = 1.378
    half_turn_length = [1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378]
    RRR = 182.0
    U0 = [460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0, 460.0]
    R_warm = [1.125, 0.962, 1.125, 0.962, 1.125, 0.962, 1.125, 0.962, 2.613, 2.584, 2.46, 2.431, 1.125, 0.962, 1.125, 0.962]
    l= [1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378, 1.378]
    time_vector_params = [-0.1, 0.0001, -0.001, -0.0009, 0.0001, 0.175, 0.1755, 0.0005, 2.0]

    """
    Hard coded parameters for short model
    :param maxVoltagePC: limiting PC voltage to decrease discharge current during PC is still switched on
    :param t_off: PC was switched of 20 ms after the quench detection
    :param t_control_LUT: adapting pc to late switch off
    :param iStartQuench: deleting first turn to prevent quench propagating to aperture 1
    :param tStartQuench: deleting first turn to prevent quench propagating to aperture 1
    :param magnetic_length: implementing shorter length of the short model
    :param half_turn_length: implementing shorter length of the short model
    :param RRR: lower measured RRR for short model
    :param U0: higher measured voltage across the QH for short model
    :param R_warm: adapted R_warm to fit the measured QH current
    :param l: implementing shorter length of the short model
    :param time_vector_params: adapting time vector for lower currents
    :param file_path_empty_analysis: path to an empty analysis to initialize aSTEAM
    """

    # unpack inputs
    magnet_name = dict_inputs['magnet_name']
    conductor_name = dict_inputs['conductor_name']
    flag_save_MatFile = dict_inputs['flag_save_MatFile']
    trigger_time_QH = dict_inputs['trigger_time_QH']
    QH_strips_active = dict_inputs['QH_strips_active']
    turn_number_quench = dict_inputs['turn_number_quench']
    quench_time = dict_inputs['quench_time']
    start_adiabatic_calculation = dict_inputs['start_adiabatic_calculation']
    length_initial_hotSpot = dict_inputs['length_initial_hotSpot']
    scaling_vq_initial_hotSpot = dict_inputs['scaling_vq_initial_hotSpot']
    EE_trigger_time = dict_inputs['EE_trigger_time']
    file_name_analysis_cond = dict_inputs['file_name_analysis_cond']
    file_name_analysis_mag = dict_inputs['file_name_analysis_mag']
    viewer_path = dict_inputs['viewer_path']
    software = dict_inputs['software']
    flag_runPyBBQ = dict_inputs['flag_run_PyBBQ']
    flag_run_LEDET = dict_inputs['flag_run_LEDET']
    list_events = dict_inputs['list_events']
    metrics_to_calculate = dict_inputs['metrics_to_calculate']
    variables_to_analyze = dict_inputs['variables_to_analyze']
    current_level = dict_inputs['current_level']
    f_helium = dict_inputs['wetted_p']
    f_inner_voids = dict_inputs['f_inner_voids']
    f_outer_voids = dict_inputs['f_outer_voids']
    simulation_numbers = dict_inputs['simulation_numbers']

    """
    Adaptable parameters for short model
    :param magnet_name: Name of the analyzed magnet
    :param conductor_name: Name of the conductor of the analyzed magnet
    :param flag_save_MatFile: if set to 2 shorter mat file
    :param trigger_time_QH: time when the QH are triggered
    :param QH_strips_active: only containing the QH strips which are active, NUMBERING STARTS FROM 1
    :param turn_number_quench: number of the turn which should manually quench
    :param quench_time: time when the manually set quench should occur
    :param start_adiabatic_calculation: time when the adiabatic hot-spot temperature calculation should start
    :param length_initial_hotSpot: length of the initial hot-spot
    :param scaling_vq_initial_hotSpot: vq scaling of the initial quench hot-spot, usually 2
    :param EE_trigger_time: time when the energy extraction is triggered
    :param file_name_analysis_cond: name of the conductor analysis file saved in output
    :param file_name_analysis_mag: name of the magnet analysis file saved in output
    :param viewer_path: path where the csv.file for the viewer is saved
    :param software: used software
    :param flag_runPyBBQ: flag if PyBBQ should be run
    :param flag_run_LEDET: flag if LEDET should be run
    :param list_events: list of the events given in the viewer csv which should be plotted and used for metrics
    :param metrics_to_calculate: list of the metrics which should be conducted
    :param variables_to_analyze: signal names given in the viewer config file which should be used for the metrics
    :param current_level: current levels of the magnet
    :param f_helium: values of wetted_p for the PyBBQ simulation
    :param f_inner_voids: fraction of inner voids
    :param f_outer_voids: fraction of inner voids
    :param simulation_numbers: list of the simulation numbers
    """

    file_path_empty_analysis = 'Input\\analysis_empty.yaml'

    aSTEAM = AnalysisSTEAM(file_name_analysis=file_path_empty_analysis, verbose=True)
    """
    Initializing AnalysisSTEAM object for the conductor simulation
    """
    create_conductor_analysis_file(aSTEAM, conductor_name, flag_save_MatFile, software, current_level, simulation_numbers, f_helium)

    ######################## Write output files ########################
    # Write the STEAM analysis data to a yaml file
    aSTEAM.write_analysis_file(path_output_file=os.path.join(aSTEAM.output_path, file_name_analysis_cond))
    ######################## Run STEAM analysis ########################
    # Note: To make sure the automatically-generated STEAM analysis yaml file is a valid one, the analysis is run from the yaml file and not from the aSTEAM object
    bSTEAM = AnalysisSTEAM(file_name_analysis=os.path.join(aSTEAM.output_path, file_name_analysis_cond), verbose=True)

    if flag_runPyBBQ == 1:
        bSTEAM.run_analysis()
    """
    Running conductor simulation
    """

    # Read model_data_magnet file
    model_data_path = os.path.join(Path(aSTEAM.library_path).resolve(), 'magnets', magnet_name, 'input', f'modelData_{magnet_name}.yaml')
    # assert(model_data_path == model_data_path1)
    if os.path.isfile(model_data_path):
        # Load yaml keys into DataAnalysis dataclass
        with open(model_data_path, "r") as stream:
            dictionary_yaml = yaml.safe_load(stream)
            model_data = DataModelMagnet(**dictionary_yaml)
        all_data_dict_model = {**model_data.model_dump()}

    # Read geometry information
    # Load information from ROXIE input files using ROXIE parser
    # roxie_parser = ParserRoxie()
    # roxie_data = roxie_parser.getData(dir_data=Path(Path(aSTEAM.library_path).resolve(), 'magnets', magnet_name, 'input', f'{magnet_name}.data'), dir_cadata=Path(Path(aSTEAM.library_path).resolve(), 'magnets', 'roxie.cadata'), dir_iron=Path(Path(aSTEAM.library_path).resolve(), 'magnets', magnet_name, 'input', 'D2_INFN3_4.iron'))
    # builder_ledet = BuilderLEDET(path_input_file = Path(Path(aSTEAM.library_path).resolve(), 'magnets', magnet_name, 'input', f'modelData_{magnet_name}.yaml'), input_model_data = DataModelMagnet(), input_roxie_data=roxie_data, input_map2d = os.path.join(Path(aSTEAM.library_path).resolve(), 'magnets', magnet_name, 'input', f'{magnet_name}.map2d'), flag_build=True)
    # pl = ParserLEDET(builder_ledet)
    # iContactAlongWidth_From = pl.builder_ledet.Inputs.iContactAlongWidth_From

    path_geometry_information = os.path.join(aSTEAM.output_path, f'{magnet_name}.yaml')
    BuilderModel(file_model_data=model_data_path, software=['LEDET'], flag_build=True,
                      output_path=aSTEAM.output_path, verbose=False, flag_plot_all=False)

    # Read geometry information
    dict_LEDET = yaml_to_data(path_geometry_information)
    iContactAlongWidth_From = np.array(dict_LEDET['iContactAlongWidth_From'])
    iContactAlongWidth_To = np.array(dict_LEDET['iContactAlongWidth_To'])
    iContactAlongHeight_From = np.array(dict_LEDET['iContactAlongHeight_From'])
    iContactAlongHeight_To = np.array(dict_LEDET['iContactAlongHeight_To'])

    # Read model_data_conductor file
    model_data_conductor_path = os.path.join(Path(aSTEAM.library_path).resolve(), 'conductors', conductor_name, 'input', f'modelData_{conductor_name}.yaml')
    if os.path.isfile(model_data_conductor_path):
        # Load yaml keys into DataAnalysis dataclass
        with open(model_data_conductor_path, "r") as stream:
            dictionary_yaml = yaml.safe_load(stream)
            model_data_conductor = DataModelConductor(**dictionary_yaml)
        all_data_dict_model_conductor = {**model_data_conductor.model_dump()}

    # getting variables from model_data
    heater_length = l
    QH_strips_total = len(l)
    l_copper = all_data_dict_model['Quench_Protection']['Quench_Heaters']['l_copper']
    l_steel = all_data_dict_model['Quench_Protection']['Quench_Heaters']['l_stainless_steel']
    heater_turns = all_data_dict_model['Quench_Protection']['Quench_Heaters']['iQH_toHalfTurn_To']
    heater_number = all_data_dict_model['Quench_Protection']['Quench_Heaters']['iQH_toHalfTurn_From']
    T_bath = all_data_dict_model['GeneralParameters']['T_initial']
    fraction_cover = all_data_dict_model['Quench_Protection']['Quench_Heaters']['f_cover']

    """
    Loading magnet data
    """

    # getting cable data
    A_CableInsulated = (all_data_dict_model['Conductors'][0]['cable']['bare_cable_width']+all_data_dict_model['Conductors'][0]['cable']['th_insulation_along_width']) * (all_data_dict_model['Conductors'][0]['cable']['bare_cable_height_mean']+all_data_dict_model['Conductors'][0]['cable']['th_insulation_along_height'])
    f_SC = 1/(all_data_dict_model['Conductors'][0]['strand']['Cu_noCu_in_strand']+1)
    f_ST = 1-f_SC
    f_SC = f_SC * all_data_dict_model['Conductors'][0]['cable']['bare_cable_width'] * all_data_dict_model['Conductors'][0]['cable']['bare_cable_height_mean'] * (1-all_data_dict_model['Conductors'][0]['cable']['f_inner_voids']-all_data_dict_model['Conductors'][0]['cable']['f_outer_voids'])/A_CableInsulated
    f_ST = f_ST * all_data_dict_model['Conductors'][0]['cable']['bare_cable_width'] * all_data_dict_model['Conductors'][0]['cable']['bare_cable_height_mean'] * (1-all_data_dict_model['Conductors'][0]['cable']['f_inner_voids']-all_data_dict_model['Conductors'][0]['cable']['f_outer_voids'])/A_CableInsulated

    Tc0_NbTi = 0
    Bc20_NbTi = 0
    c1_Ic_NbTi = 0
    c2_Ic_NbTi = 0
    Jc_Nb3Sn0 = 0
    Tc0_Nb3Sn = 0
    Bc20_Nb3Sn = 0

    if all_data_dict_model['Conductors'][0]['strand']['material_superconductor'] == 'Nb-Ti':
        idxNbTi = 1
        idxNb3Sn = 0
        Tc0_NbTi = all_data_dict_model['Conductors'][0]['Jc_fit']['Tc0_CUDI1']
        Bc20_NbTi = all_data_dict_model['Conductors'][0]['Jc_fit']['Bc20_CUDI1']
        c1_Ic_NbTi = all_data_dict_model['Conductors'][0]['Jc_fit']['C1_CUDI1']
        c2_Ic_NbTi = all_data_dict_model['Conductors'][0]['Jc_fit']['C2_CUDI1']
    else:
        idxNbTi = 0
        idxNb3Sn = 1
        Jc_Nb3Sn0 = all_data_dict_model['Conductors'][0]['Jc_fit']['Jc0_Summers']
        Tc0_Nb3Sn = all_data_dict_model['Conductors'][0]['Jc_fit']['Tc0_Summers']
        Bc20_Nb3Sn = all_data_dict_model['Conductors'][0]['Jc_fit']['Bc20_Summers']

    aSTEAM = AnalysisSTEAM(file_name_analysis=file_path_empty_analysis, verbose=True)
    """
    Initializing AnalysisSTEAM object for the magnet simulation
    """
    create_magnet_analysis_file(aSTEAM, magnet_name, software, simulation_numbers, viewer_path, list_events, metrics_to_calculate, variables_to_analyze)

    for i in range(len(simulation_numbers)):

        """
        Calculation quench propagation scaling
        """

        # initializing scaling_vq, length_HotSpot and timeOfQuench
        scaling_vq = all_data_dict_model['Options_LEDET']['quench_initiation']['fScaling_vQ_iStartQuench']
        scaling_vq = np.ones(len(scaling_vq)-1)
        length_HotSpot = all_data_dict_model['Options_LEDET']['quench_initiation']['lengthHotSpot_iStartQuench']
        length_HotSpot = np.zeros(len(length_HotSpot)-1)
        time_of_quench = all_data_dict_model['Options_LEDET']['quench_initiation']['tStartQuench']

        # reading current from input and calculating magnetic field
        current = current_level[i]
        B = current * all_data_dict_model_conductor['Options_PyBBQ']['magnetic_field']['Self_Field']

        # initializing path for PyBBQ output
        simulation_number = simulation_numbers[i]
        input_folder = os.path.join(aSTEAM.data_analysis.PermanentSettings.local_PyBBQ_folder + conductor_name, str(simulation_number), 'Output', 'Results - 0.21', conductor_name, 'summary.csv')

        # reading vq from PyBBQ output
        vQ_PyBBQ = get_signals_from_csv(input_folder, 'NZPV [m/s]')
        vQ_PyBBQ = vQ_PyBBQ['NZPV[m/s]'].iloc[0]
        print('NZPV calculated by PyBBQ is %s' % vQ_PyBBQ)

        # calculating vq with analytic formula
        vQ_analytic = _quenchPropagationVelocity(current, B, T_bath, A_CableInsulated, f_SC, f_ST, idxNbTi, idxNb3Sn, Tc0_NbTi, Bc20_NbTi, c1_Ic_NbTi, c2_Ic_NbTi, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn)
        print('NZPV calculated with the analytic formula is %s' % vQ_analytic)

        # creating list of quench heater triggering time
        QH_trigger_time = list(np.ones(QH_strips_total) * 9999)

        # calculating scaling_vq depending on geometry of heater stations
        # calculating fraction of turns covered by heater
        # only active heaters are considered
        for n in range(len(QH_strips_active[i])):
            QH_trigger_time[QH_strips_active[i][n]-1] = trigger_time_QH[i]
            new_scale_vq = round(2 * vQ_PyBBQ / vQ_analytic * round(heater_length[QH_strips_active[i][n] - 1] / (l_copper[QH_strips_active[i][n] - 1] + l_steel[QH_strips_active[i][n] - 1]), 0), 2)
            new_length_HotSpot = heater_length[QH_strips_active[i][n] - 1] * fraction_cover[QH_strips_active[i][n] - 1]
            for j in range(len(heater_turns)):
                if QH_strips_active[i][n] == heater_number[j]:
                    scaling_vq[heater_turns[j] - 1] = new_scale_vq
                    length_HotSpot[heater_turns[j] - 1] = new_length_HotSpot
                    if len(np.where(iContactAlongWidth_From == heater_turns[j])[0]) > 0:
                        scaling_vq[iContactAlongWidth_To[
                                       int(np.where(iContactAlongWidth_From == heater_turns[j])[0])] - 1] = new_scale_vq
                        length_HotSpot[iContactAlongWidth_To[
                                           int(np.where(iContactAlongWidth_From == heater_turns[j])[
                                                   0])] - 1] = new_length_HotSpot
                        if len(np.where(iContactAlongWidth_From == iContactAlongWidth_To[
                            int(np.where(iContactAlongWidth_From == heater_turns[j])[0])])[0]) > 0:
                            scaling_vq[iContactAlongWidth_To[int(np.where(
                                iContactAlongWidth_From == iContactAlongWidth_To[
                                    int(np.where(iContactAlongWidth_From == heater_turns[j])[0])])[
                                                                     0])] - 1] = new_scale_vq
                            length_HotSpot[iContactAlongWidth_To[int(np.where(
                                iContactAlongWidth_From == iContactAlongWidth_To[
                                    int(np.where(iContactAlongWidth_From == heater_turns[j])[0])])[
                                                                         0])] - 1] = new_length_HotSpot
                    if len(np.where(iContactAlongWidth_To == heater_turns[j])[0]) > 0:
                        scaling_vq[iContactAlongWidth_From[
                                       int(np.where(iContactAlongWidth_To == heater_turns[j])[0])] - 1] = new_scale_vq
                        length_HotSpot[iContactAlongWidth_From[
                                           int(np.where(iContactAlongWidth_To == heater_turns[j])[
                                                   0])] - 1] = new_length_HotSpot
                        if len(np.where(iContactAlongWidth_To == iContactAlongWidth_From[
                            int(np.where(iContactAlongWidth_To == heater_turns[j])[0])])[0]) > 0:
                            scaling_vq[iContactAlongWidth_From[int(np.where(
                                iContactAlongWidth_To == iContactAlongWidth_From[
                                    int(np.where(iContactAlongWidth_To == heater_turns[j])[0])])[
                                                                       0])] - 1] = new_scale_vq
                            length_HotSpot[iContactAlongWidth_From[int(np.where(
                                iContactAlongWidth_To == iContactAlongWidth_From[
                                    int(np.where(iContactAlongWidth_To == heater_turns[j])[0])])[
                                                                           0])] - 1] = new_length_HotSpot

                    # setting the two turns which are physically in contact along the height to quench
                    # if len(np.where(iContactAlongHeight_From == heater_turns[j])[0]) > 0:
                    #     scaling_vq[iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, heater_turns[j]))[0]]-1] = new_scale_vq
                    #     length_HotSpot[iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, heater_turns[j]))[0]]-1] = new_length_HotSpot
                    #     if len(np.where(iContactAlongHeight_From == iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, heater_turns[j]))[0]])[0]) > 0:
                    #         scaling_vq[iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, heater_turns[j]))[0]]))[0]] - 1] = new_scale_vq
                    #         length_HotSpot[iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, iContactAlongHeight_To[np.where(np.in1d(iContactAlongHeight_From, heater_turns[j]))[0]]))[0]] - 1] = new_length_HotSpot
                    # if len(np.where(iContactAlongHeight_To == heater_turns[j])[0]) > 0:
                    #     scaling_vq[iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, heater_turns[j]))[0]]-1] = new_scale_vq
                    #     length_HotSpot[iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, heater_turns[j]))[0]]-1] = new_length_HotSpot
                    #     if len(np.where(iContactAlongHeight_To == iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, heater_turns[j]))[0]])[0]) > 0:
                    #         scaling_vq[iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, heater_turns[j]))[0]]))[0]] - 1] = new_scale_vq
                    #         length_HotSpot[iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, iContactAlongHeight_From[np.where(np.in1d(iContactAlongHeight_To, heater_turns[j]))[0]]))[0]] - 1] = new_length_HotSpot


        print('The new scaling factor is %s' % new_scale_vq)

        # making a list and changing type from float64 to float
        QH_trigger_time = list(QH_trigger_time)
        QH_trigger_time = [float(x) for x in QH_trigger_time]
        scaling_vq = list(scaling_vq)
        scaling_vq = [float(x) for x in scaling_vq]
        length_HotSpot = list(length_HotSpot)
        length_HotSpot = [float(x) for x in length_HotSpot]
        time_of_quench = list(time_of_quench)
        time_of_quench = [float(x) for x in time_of_quench]

        # setting a turn to quench
        time_of_quench[turn_number_quench-1] = quench_time
        length_HotSpot[turn_number_quench-1] = length_initial_hotSpot
        scaling_vq[turn_number_quench-1] = scaling_vq_initial_hotSpot

        # Add as many steps as current levels and simulation numbers
        current_step = 'modifyModel_' + str(i + 1)
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step] = ModifyModelMultipleVariables(
            type='ModifyModelMultipleVariables')
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].model_name = 'BM'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_to_change = [
            'Options_LEDET.post_processing.flag_saveMatFile',
            'Power_Supply.I_initial',
            'Power_Supply.I_control_LUT',
            'Quench_Protection.Quench_Heaters.t_trigger',
            'Options_LEDET.post_processing.tQuench',
            'Options_LEDET.quench_initiation.lengthHotSpot_iStartQuench',
            'Options_LEDET.quench_initiation.fScaling_vQ_iStartQuench',
            'Options_LEDET.quench_initiation.tStartQuench',
            "Conductors[0].cable.f_inner_voids",
            "Conductors[0].cable.f_outer_voids",
            'Options_LEDET.physics.maxVoltagePC',
            'Power_Supply.t_off',
            'Power_Supply.t_control_LUT',
            'Options_LEDET.quench_initiation.iStartQuench',
            'Options_LEDET.quench_initiation.tStartQuench',
            'GeneralParameters.magnetic_length',
            'CoilWindings.half_turn_length',
            "Conductors[0].strand.RRR",
            'Quench_Protection.Quench_Heaters.U0',
            'Quench_Protection.Quench_Heaters.R_warm',
            'Quench_Protection.Quench_Heaters.l',
            'Options_LEDET.time_vector.time_vector_params',
            'Quench_Protection.Energy_Extraction.t_trigger'
        ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_value = [
            [flag_save_MatFile],
            [current_level[i]],
            [[current_level[i], current_level[i], 0]],
            [QH_trigger_time],
            [start_adiabatic_calculation],
            [length_HotSpot],
            [scaling_vq],
            [time_of_quench],
            [f_inner_voids[i]],
            [f_outer_voids[i]],
            [maxVoltagePC],
            [t_off],
            [t_control_LUT],
            [iStartQuench],
            [tStartQuench],
            [magnetic_length],
            [half_turn_length],
            [RRR],
            [U0],
            [R_warm],
            [l],
            [time_vector_params],
            [EE_trigger_time[i]]
            ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_numbers = [simulation_numbers[i]]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_name = f'{magnet_name}'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].software = [software[1]]
        if flag_run_LEDET == 1:
            aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)

    # appending simulations to run as last step
    if flag_run_LEDET == 1:
        step_run_simulation = f'RunSimList_{software[1]}'
        aSTEAM.data_analysis.AnalysisStepSequence.append(step_run_simulation)
    # appending simulations to run as last step
    step_run_simulation = 'run_viewer'
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_run_simulation)
    # appending simulations to run as last step
    step_run_simulation = 'calculate_metrics'
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_run_simulation)

    ######################## Write output files ########################
    # Write the STEAM analysis data to a yaml file
    aSTEAM.write_analysis_file(path_output_file=os.path.join(aSTEAM.output_path, file_name_analysis_mag))

    ######################## Run STEAM analysis ########################
    # Note: To make sure the automatically-generated STEAM analysis yaml file is a valid one, the analysis is run from the yaml file and not from the aSTEAM object
    bSTEAM = AnalysisSTEAM(file_name_analysis=os.path.join(aSTEAM.output_path, file_name_analysis_mag), verbose=True)

    """
    run magnet simulation
    """

    bSTEAM.run_analysis()
