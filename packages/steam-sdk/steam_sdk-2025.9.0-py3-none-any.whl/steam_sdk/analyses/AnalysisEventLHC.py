"""
File: AnalysisEventLHC.py
Date: 2024-10-11

Description:
    This script contains several functions to create an analysis of a superconducting magnet circuit with STEAM.
    It creates and runs an AnalysisSteam object and fills in all necessary attributes of the object to run a full
    simulation of the respective circuit, while only relying on a path to the user settings file and a dictionary of
    input parameters.
"""

# Imports
import shutil
from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.analyses.AnalysisEvent import find_IPQ_circuit_type_from_IPQ_parameters_table, \
    get_circuit_name_from_eventfile, generate_unique_event_identifier_from_eventfile, \
    get_signal_keys_from_configurations_file, determine_config_path_and_configuration, \
    get_circuit_type_from_circuit_name, extract_signal_touples_from_config, get_hard_coded_filename_postfix, \
    get_circuit_information_of_circuit_types, get_circuit_family_from_circuit_name
from steam_sdk.data.DataAnalysis import ModifyModelMultipleVariables, MakeModel, ParsimEvent, \
    DefaultParsimEventKeys, RunSimulation, RunViewer, CalculateMetrics
from steam_sdk.parsers.ParserYAML import yaml_to_data
import warnings
from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional
import os

def steam_analyze_lhc_event(
        path_settings_file: str,
        input_parameter_dictionary: dict
) -> None:
    """
    **Analyzes an LHC event based on the provided settings and parameters.**

    :param path_settings_file: Absolute path to the settings file (e.g., `settings.username.yaml`).

    :param input_parameter_dictionary: Dictionary specifying the parameters needed for the function call. The parameters
     are validated using a Pydantic data model. It should contain the following keys:
        **path_meas_data_folder** (`str`): Absolute path to the folder containing the measurement data.
        **config_file_or_dir** (`str`): Absolute path to the configuration file or directory for the viewer.
        **metrics_to_calculate** (`Optional[List[str]]`): List of error metrics to calculate for all signals specified
         in the configuration file. Defaults to an empty list if not provided.
        **timeout_s** (`int`): Timeout in seconds after which a frozen simulation will be aborted.
        **flag_run_software** (`bool`): Flag indicating whether to execute the simulation software or only create
        simulation files without running them.
        **input_csv_file** (`str`): Absolute path to the FPA event file to be simulated.
        **software** (`str`): Circuit solver software to use (either `PSPICE` or `XYCE`).
        **file_counter** (`int`): Number of the simulation folder in the output directory.

    :return: None
    """

    # Define the Pydantic data model to validate the passed function parameters:
    class InputParameterModel(BaseModel):
        path_meas_data_folder: str
        config_file_or_dir: str
        metrics_to_calculate: Optional[List[str]] = []
        timeout_s: int
        flag_run_software: bool
        input_csv_file: str
        software: str
        file_counter: int
        class Config:
            extra = 'forbid'  # Disallows extra keys
    try:
        # Validate the input dictionary using the Pydantic model
        validated_params = InputParameterModel(**input_parameter_dictionary)

        # Retrieve necessary local variables
        settings_data_object = yaml_to_data(path_settings_file)
        library_path = settings_data_object["local_library_path"]
        input_csv_file = validated_params.input_csv_file
        circuit_name = get_circuit_name_from_eventfile(event_file=input_csv_file)
        circuit_type = get_circuit_type_from_circuit_name(circuit_name, library_path)
        circuit_family = get_circuit_family_from_circuit_name(circuit_name, library_path)

        if circuit_type == "RCD_AND_RCO":
            # RCD and RCO is a "double circuit". For this kind of events, two simulations of both circuit parts have to
            # be run
            _analyze_circuit_event(
                path_settings_file=path_settings_file,
                input_parameter_dictionary=validated_params.dict(),
                circuit_type="RCD",
                circuit_name="RCD." + circuit_name.split(".")[-1],
                circuit_family = circuit_family
            )
            _analyze_circuit_event(
                path_settings_file=path_settings_file,
                input_parameter_dictionary=validated_params.dict(),
                circuit_type="RCO",
                circuit_name="RCO." + circuit_name.split(".")[-1],
                circuit_family = circuit_family
            )
        else:
            # All other circuits and double circuits like RQs and RCBX can be run with this function as this is how
            # it is implemented in AnalysisSteam:
            # TODO: Other double circuits like RCBXH/V follow a different approach than for RCD/RCO circuits.
            #  For these circuits, the logic to run both simulations is directly implemented in the AnalysisSteam class,
            #  which makes the code unnessary complex and difficult to understand. In future work, the case of
            #  all double circuits could therefore be treated like for the above case of RCD, RCO circuits, by just running
            #  two seperate analyses.
            _analyze_circuit_event(
                path_settings_file=path_settings_file,
                input_parameter_dictionary=validated_params.dict(),
                circuit_type= circuit_type,
                circuit_name = circuit_name,
                circuit_family=circuit_family
            )

    except ValidationError as e:
        # Catch and print validation errors
        print("Validation Error in input parameter dictionary:")
        print(e)

def _analyze_circuit_event(
    path_settings_file: str,
    input_parameter_dictionary: dict,
    circuit_type: str,
    circuit_name: str,
    circuit_family : str
) -> None:
    """
    **Private function that assembles an Analysis STEAM object based on the circuit type to be simulated.
    This function is intended for internal use only and is called by `steam_analyze_lhc_event`.**

    :param  path_settings_file: Absolute path to the settings file (e.g., `settings.username.yaml`).
    :param input_parameter_dictionary: Dictionary specifying the parameters needed for the function call. The parameters
     are validated using a Pydantic data model. It should contain the following keys:
        **path_meas_data_folder** (`str`): Absolute path to the folder containing the measurement data.
        **config_file_or_dir** (`str`): Absolute path to the configuration file or directory for the viewer.
        **metrics_to_calculate** (`Optional[List[str]]`): List of error metrics to calculate for all signals specified
         in the configuration file. Defaults to an empty list if not provided.
        **timeout_s** (`int`): Timeout in seconds after which a frozen simulation will be aborted.
        **flag_run_software** (`bool`): Flag indicating whether to execute the simulation software or only create
        simulation files without running them.
        **input_csv_file** (`str`): Absolute path to the FPA event file to be simulated.
        **software** (`str`): Circuit solver software to use (either `PSPICE` or `XYCE`).
        **file_counter** (`int`): Number of the simulation folder in the output directory.
    :param circuit_type: The type of circuit to be simulated. Determines which model from `steam_models` is
     used for the simulation.
    :param circuit_name: The name of the circuit. While circuits of the same type may share similar names, they are
     distinct entities (e.g., `RB.A26` and `RB.A56` both belong to the `RB` circuit type).

     :return: None
    """

    aSTEAM = AnalysisSTEAM()
    aSTEAM.data_analysis.GeneralParameters.relative_path_settings = os.path.relpath(os.path.dirname(path_settings_file),
                                                                                    os.path.dirname(os.getcwd()))
    aSTEAM.path_analysis_file = os.getcwd()
    aSTEAM._resolve_settings()
    timeout_s = input_parameter_dictionary["timeout_s"]

    input_csv_file = input_parameter_dictionary["input_csv_file"]
    flag_run_software = input_parameter_dictionary["flag_run_software"]
    software = input_parameter_dictionary["software"]
    file_counter = input_parameter_dictionary["file_counter"]
    local_software_folder = getattr(aSTEAM.settings, f"local_{software}_folder")

    unique_identifier_event = generate_unique_event_identifier_from_eventfile(
        file_name=os.path.basename(input_csv_file))

    output_directory_yaml_files =  os.path.join(os.getcwd(), 'output', 'yaml_files')
    output_directory_parsim_sweep_files = os.path.join(os.getcwd(), 'output', 'parsim_sweep_files')

    output_directory_initialization_file_viewer = os.path.join(os.getcwd(), 'output', 'initialization_files_viewer')

    yaml_file_name = f'infile_{unique_identifier_event}.yaml'
    parsim_sweep_file_name = f'parsim_sweep_{software}_{circuit_type}_{unique_identifier_event}_{file_counter}.csv'

    path_output_yaml_file = os.path.join(output_directory_yaml_files,yaml_file_name)
    path_output_parsim_sweep_csv = os.path.join(output_directory_parsim_sweep_files,parsim_sweep_file_name)

    # get all signals that are defined in the config file to later include them in the model using a
    # ModifyModelMultipleVariables step
    signals_to_include = ['']
    if input_parameter_dictionary['config_file_or_dir'] != None:
        full_config_file_path , configuration = (
            determine_config_path_and_configuration(
                directory_config_files =input_parameter_dictionary['config_file_or_dir'],
                steam_circuit_type=circuit_type))
        signals_to_include = get_signal_keys_from_configurations_file(full_config_file_path,
                                                                      configuration = configuration)

        variables_to_analyze = extract_signal_touples_from_config(full_config_file_path, configuration)
    else:
        warnings.warn("no signals from the config file will be included in the model, variables entry will be empty in"
                      " the cir file, causing all signals to be calculated")

    aSTEAM.data_analysis.AnalysisStepDefinition = {
        'makeModel_ref': MakeModel(type='MakeModel', model_name='BM', file_model_data=circuit_type,
                                   case_model='circuit', software=software, simulation_name=None,
                                   simulation_number=None, flag_build=True, verbose=False,
                                   flag_plot_all=False, flag_json=False),
        'modifyModel_probe1': ModifyModelMultipleVariables(type='ModifyModelMultipleVariables', model_name='BM',
                                       variables_to_change=['PostProcess.probe.probe_type'],
                                       variables_value=[['CSDF']], software=software, simulation_name=None,
                                       simulation_numbers=[]),
        'modifyModel_include_config_signals': ModifyModelMultipleVariables(type='ModifyModelMultipleVariables',
                                                                           model_name='BM',
                                                          variables_to_change=['PostProcess.probe.variables'],
                                                          variables_value=[[signals_to_include]], software=software,
                                                          simulation_name=None,
                                                          simulation_numbers=[]),
        'runParsimEvent': ParsimEvent(type='ParsimEvent',
                                      input_file=input_csv_file,
                                      path_output_event_csv=path_output_parsim_sweep_csv,
                                      path_output_viewer_csv=output_directory_initialization_file_viewer,
                                      simulation_numbers=[file_counter], model_name='BM', case_model='circuit',
                                      simulation_name=circuit_type, software=software, t_PC_off=None,
                                      rel_quench_heater_trip_threshold=None, current_polarities_CLIQ=[],
                                      dict_QH_circuits_to_QH_strips={},
                                      default_keys=DefaultParsimEventKeys(local_LEDET_folder=None,
                                                                          path_config_file=None, default_configs=[],
                                                                          path_tdms_files=None,
                                                                          path_output_measurement_files=None,
                                                                          path_output=local_software_folder),
                                      path_postmortem_offline_data_folder=input_parameter_dictionary
                                      ['path_meas_data_folder'],
                                      path_to_configurations_folder = input_parameter_dictionary['config_file_or_dir'],
                                      filepath_to_temp_viewer_csv = None
                                      ),
        'run_simulation': RunSimulation(type='RunSimulation', software=software, simulation_name="from_ParsimEvent_step"
                                        , simulation_numbers=[file_counter],
        timeout_s = timeout_s )
    }
    aSTEAM.output_path = local_software_folder

    AnalysisStepSequence = ['makeModel_ref', 'modifyModel_probe1', 'modifyModel_include_config_signals',
                            'runParsimEvent']
    if flag_run_software == True: AnalysisStepSequence.append('run_simulation')

    if circuit_type in ["RCD", "RCO"]:
        postprocess_circuittypes, postprocess_simulation_numbers, postprocess_circuitnames = [circuit_type], [file_counter], [circuit_name]
    else:
        postprocess_circuittypes, postprocess_simulation_numbers, postprocess_circuitnames = (
                get_circuit_information_of_circuit_types(circuit_type = circuit_type,
                                                     circuit_name = circuit_name,
                                                     simulation_numbers= [file_counter],
                                                     circuit_family= circuit_family))


    for i, (circuit_type, circuit_name, file_counter) in enumerate(zip(postprocess_circuittypes, postprocess_circuitnames,postprocess_simulation_numbers)):

        hard_coded_filename_postfix = get_hard_coded_filename_postfix(unique_identifier_event, circuit_name)

        filepath_to_temp_viewer_csv = os.path.join(
            local_software_folder, circuit_type, str(file_counter), f"temp_viewer{hard_coded_filename_postfix}.csv"
        )

        path_output_pdf_report = os.path.join(
            local_software_folder, circuit_type, str(file_counter), f"report{hard_coded_filename_postfix}.pdf"
        )

        aSTEAM.data_analysis.AnalysisStepDefinition[f"RunViewer{i}"] =  RunViewer(type="RunViewer",
                                file_name_transients=filepath_to_temp_viewer_csv,
                                flag_analyze=True,
                                verbose=True,
                                flag_save_figures=True, viewer_name=f"viewer_{i}",
                                path_output_pdf_report=path_output_pdf_report)

        aSTEAM.data_analysis.AnalysisStepDefinition[f"CalculateMetrics{i}"] = CalculateMetrics(type="CalculateMetrics",
                                              viewer_name=f"viewer_{i}",
                                              metrics_name="metrics",
                                              metrics_to_calculate=input_parameter_dictionary[
                                                  'metrics_to_calculate'],
                                              variables_to_analyze=variables_to_analyze,
                                              metrics_output_filepath=os.path.join(local_software_folder,
                                                                                   circuit_type,
                                                                                   str(file_counter),
                                                                                   "output_metrics.yaml")
                                              )

    if len(input_parameter_dictionary['metrics_to_calculate']) > 0:
        for i,_ in enumerate(postprocess_circuittypes):
            AnalysisStepSequence.extend([f"RunViewer{i}"])
        for i,_ in enumerate(postprocess_circuittypes):
            AnalysisStepSequence.extend([f"CalculateMetrics{i}"])

    aSTEAM.data_analysis.AnalysisStepSequence = AnalysisStepSequence
    aSTEAM.write_analysis_file(path_output_file=path_output_yaml_file)
    aSTEAM.run_analysis(verbose=True)

    # Copy eventfile into the simulation folder
    shutil.copyfile(input_csv_file,os.path.join(local_software_folder, f'{circuit_type}', f'{file_counter}',
                                                f'Eventfile_{unique_identifier_event}.csv'))

    # print summary entry if possible:
    if len(input_parameter_dictionary['metrics_to_calculate']) > 0:
        average_metrics = aSTEAM.summary
        print("======================== Metrics ========================")
        print(f"The average metrics for this event are {average_metrics}")
