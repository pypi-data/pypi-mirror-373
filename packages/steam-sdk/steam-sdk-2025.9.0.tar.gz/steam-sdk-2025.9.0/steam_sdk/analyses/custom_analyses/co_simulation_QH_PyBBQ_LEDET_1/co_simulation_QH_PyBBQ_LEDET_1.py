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

from steam_sdk.analyses.custom_analyses.co_simulation_QH_PyBBQ_LEDET_1.utils.create_conductor_analysis_file import create_conductor_analysis_file
from steam_sdk.analyses.custom_analyses.co_simulation_QH_PyBBQ_LEDET_1.utils.create_magnet_analysis_file import create_magnet_analysis_file
from steam_sdk.analyses.custom_analyses.co_simulation_QH_PyBBQ_LEDET_1.utils.calculate_quench_propagation_velocity import _quenchPropagationVelocity

def co_simulation_QH_PyBBQ_LEDET_1(dict_inputs: Dict):

    """
    Function to run a co-simulation for a QH protected magnet including PyBBQ and LEDET
    :param dict_inputs: Dictionary that contains all variable input variables
    :return:
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
    software = dict_inputs['software']
    flag_runPyBBQ = dict_inputs['flag_run_PyBBQ']
    flag_run_LEDET = dict_inputs['flag_run_LEDET']
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
    :param software: used software
    :param flag_runPyBBQ: flag if PyBBQ should be run
    :param flag_run_LEDET: flag if LEDET should be run
    :param current_level: current levels of the magnet
    :param f_helium: values of wetted_p for the PyBBQ simulation
    :param f_inner_voids: fraction of inner voids
    :param f_outer_voids: fraction of inner voids
    :param simulation_numbers: list of the simulation numbers
    :param file_path_empty_analysis: path to an empty analysis to initialize aSTEAM (hard coded)
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
    heater_length = all_data_dict_model['Quench_Protection']['Quench_Heaters']['l']
    QH_strips_total = len(heater_length)
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
    create_magnet_analysis_file(aSTEAM, magnet_name, software, simulation_numbers)

    for i in range(len(simulation_numbers)):

        """
        Calculation quench propagation scaling
        """

        # initializing scaling_vq, length_HotSpot and timeOfQuench
        scaling_vq = all_data_dict_model['Options_LEDET']['quench_initiation']['fScaling_vQ_iStartQuench']
        scaling_vq = np.ones(len(scaling_vq))
        length_HotSpot = all_data_dict_model['Options_LEDET']['quench_initiation']['lengthHotSpot_iStartQuench']
        length_HotSpot = np.zeros(len(length_HotSpot))
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
                    x = len(np.where(iContactAlongWidth_From == heater_turns[j])[0])
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
                    # should only used when sure that the quench arrives fast in the next layer
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
            [EE_trigger_time[i]]
            ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_numbers = [simulation_numbers[i]]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_name = f'{magnet_name}'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].software = [software[1]]
        aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)

    # appending simulations to run as last step
    step_run_simulation = f'RunSimList_{software[1]}'
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

    if flag_run_LEDET == 1:
        bSTEAM.run_analysis()
