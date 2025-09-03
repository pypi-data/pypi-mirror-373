from steam_sdk.data.DataAnalysis import SetUpFolder, MakeModel, RunSimulation

def create_magnet_analysis_file(aSTEAM, magnet_name, software, simulation_numbers):  # pragma: no cover

    """
    Function to fill the before created analysis file for the magnet simulation
    :param aSTEAM: Dictionary that contains all variable input variables
    :param magnet_name: Name of the magnet of the analyzed magnet
    :param software: used software
    :param simulation_numbers: list of simulation numbers
    :return:
    """

    aSTEAM.data_analysis.GeneralParameters.model.name = magnet_name

    # Add step to set up LEDET folder model
    step_setup_folder = 'setup_folder'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder] = SetUpFolder(type='SetUpFolder')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder].simulation_name = f'{magnet_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_setup_folder].software = [software[1]]
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_setup_folder)

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
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].verbose = False
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_plot_all = False
    aSTEAM.data_analysis.AnalysisStepDefinition[step_ref_model].flag_json = False
    aSTEAM.data_analysis.AnalysisStepSequence.append(step_ref_model)

    # prepare step run_simulation
    step_run_simulation = f'RunSimList_{software[1]}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation] = RunSimulation(type='RunSimulation')
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].software = software[1]
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simulation_name = f'{magnet_name}'
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simulation_numbers = simulation_numbers
    aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simFileType = None