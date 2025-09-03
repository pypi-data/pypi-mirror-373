from steam_sdk.data.DataAnalysis import SetUpFolder, MakeModel, ModifyModelMultipleVariables, RunSimulation

def create_conductor_analysis_file(aSTEAM, conductor_name, flag_save_MatFile, software, current_level, simulation_numbers, f_helium):  # pragma: no cover

    """
    Function to fill the before created analysis file for the magnet simulation
    :param aSTEAM: Dictionary that contains all variable input variables
    :param conductor_name: Name of the conductor of the analyzed magnet
    :param software: used software
    :param simulation_numbers: list of simulation numbers
    :param flag_save_MatFile: if set to 2 shorter mat file
    :param current_level: current levels of the magnet
    :param f_helium: values of wetted_p for the PyBBQ simulation
    :param RRR: changed RRR in PyBBQ for short model magnet
    :return:
    """

    # validation specific inputs
    RRR = 196.6


    aSTEAM.data_analysis.GeneralParameters.model.name = conductor_name

    # Add step to set up LEDET folder model
    step_setup_folder = 'setup_folder'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder] = SetUpFolder(type='SetUpFolder')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder].simulation_name = f'{conductor_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder].software = [software[1]]
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_setup_folder)

    # Add step to import reference model
    step_ref_model = 'make_reference_model'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model] = MakeModel(type='MakeModel')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].model_name = 'BM'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].file_model_data = f'{conductor_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].case_model = 'conductor'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].software = []
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].simulation_name = None
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].simulation_number = None
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_build = True  # important to keep True since it calculates the edited map2d file
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].verbose = False
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_plot_all = False
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_json = False
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_ref_model)

    # Add as many steps as current levels and simulation numbers
    for i in range(len(simulation_numbers)):
        current_step = 'modifyModel_' + str(i + 1)
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step] = ModifyModelMultipleVariables(
            type='ModifyModelMultipleVariables')
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].model_name = 'BM'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_to_change = [
            'Options_LEDET.post_processing.flag_saveMatFile',
            'Power_Supply.I_initial',
            'Power_Supply.I_control_LUT',
            'Options_PyBBQ.physics.wetted_p',
            'Conductors[0].strand.RRR'
        ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].variables_value = [
            [flag_save_MatFile],
            [current_level[i]],
            [[current_level[i], current_level[i], current_level[i]]],
            [f_helium[i]],
            [RRR]
        ]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_numbers = [simulation_numbers[i]]
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_name = f'{conductor_name}'
        aSTEAM.data_analysis.AnalysisStepDefinition[current_step].software = [software[0]]
        aSTEAM.data_analysis.AnalysisStepSequence.append(current_step)

    # prepare step run_simulation
    step_run_simulation = f'RunSimList_{software[0]}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation] = RunSimulation(type='RunSimulation')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].software = software[0]
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simulation_name = f'{conductor_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simulation_numbers = simulation_numbers
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_run_simulation)