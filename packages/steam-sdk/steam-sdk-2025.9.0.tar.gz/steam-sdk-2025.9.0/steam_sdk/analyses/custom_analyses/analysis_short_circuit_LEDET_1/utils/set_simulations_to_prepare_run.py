from steam_sdk.data.DataAnalysis import RunSimulation
from steam_sdk.utils.tic_toc import toc


########################################################################################################################
# Helper functions

def set_simulations_to_prepare_run(aSTEAM, list_simulations_to_prepare, list_simulations_to_run,
                                   magnet_name_short_circuit, list_software, verbose):  # pragma: no cover
    # function to edit the AnalysisSTEAM object to define simulations to write and run

    # Global parameters
    label_suffix = 'modify_model_short_location_'  # Known maintainance issue: This variable needs to have the same value in the function calculate_short_parameters


    # Edit the steps generating selected models to make sure they generate a simulation model (for example, a LEDET input file)
    # Note: The model objects will still be present when the analysis is run, but no output simulation files will be generated unless they are in this list
    for sim in list_simulations_to_prepare:
        current_step = f'{label_suffix}{sim}'
        if current_step in aSTEAM.data_analysis.AnalysisStepDefinition:
            aSTEAM.data_analysis.AnalysisStepDefinition[current_step].simulation_numbers = [sim]
        else:
            print(f'WARNING: The model #{sim} was not generated, so its subkey "simulation_numbers" cannot be changed.')


    # Add a step to run simulations and assign it the list of simulations to run
    for software in list_software:
        step_run_simulation = f'run_simulation_list_{software}'
        aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation] = RunSimulation(type='RunSimulation')
        aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].software = software
        aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simulation_name = magnet_name_short_circuit
        aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simulation_numbers = list_simulations_to_run
        aSTEAM.data_analysis.AnalysisStepDefinition[step_run_simulation].simFileType = '.yaml'  # hard-coded
        aSTEAM.data_analysis.AnalysisStepSequence.append(step_run_simulation)


    if verbose:
        print('Step to set the simulations to write and run edited.')
        toc()

    return
