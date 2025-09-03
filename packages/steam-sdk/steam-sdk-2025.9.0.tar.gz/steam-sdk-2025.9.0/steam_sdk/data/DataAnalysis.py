from typing import List, Union, Literal, Dict, Tuple, Optional

from pydantic import BaseModel, Field, ConfigDict

from steam_sdk.data.DataSettings import DataSettings


############################
# General parameters
class ModelClass(BaseModel):
    """
        Level 2: Class for information on the model
    """
    name: Optional[Union[str, float, int]] = None
    version: Optional[Union[str, float, int]] = None
    case: Optional[Union[str, float, int]] = None
    state: Optional[Union[str, float, int]] = None


class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    analysis_name: Optional[str] = None
    flag_permanent_settings: Optional[bool] = None
    relative_path_settings: Optional[str] = Field(default=None,
                                              title="Relative path to settings file",
                                              description="Relative path to settings.user.yaml file. It is relative to folder with analysis.yaml file",
                                              examples=[r"../builders/model_library", r"C:\STEAM\model_library"])
    # relative_path_settings: Optional[str] = Field(default=None, description="This key is only used if flag_permanent_settings=False. It defines the relative path to the folder where the settings file is contained. This file is named settings.{user}.yaml, where {user} is the current user name.")
    model: ModelClass = ModelClass()

class StrandCriticalCurrentMeasurement(BaseModel):
    """
        Level 1: Class for essential parameters for a critical current measurement to adjust Jc fit parameters
    """
    column_name_I_critical: Optional[str] = None
    reference_mag_field: Optional[float] = None
    reference_temperature: Optional[float] = None
    column_name_CuNoCu_short_sample: Optional[str] = None
    coil_names: List[str] = []


############################
# Analysis step definition
class MakeModel(BaseModel):
    """
        Level 2: Analysis step to generate a model using BuilderModel
    """
    type: Literal["MakeModel"]
    model_name: Optional[str] = None
    file_model_data: Optional[str] = None  # it would be nice if it could be read as parameters from other keys (anchors)
    case_model: Optional[str] = None
    software: Optional[str] = None
    simulation_name: Optional[str] = None
    simulation_number: Optional[Union[int, str]] = None
    flag_json: Optional[bool] = None
    flag_plot_all: Optional[bool] = None
    verbose: Optional[bool] = None
    model_config = ConfigDict(protected_namespaces=())


class ModifyModel(BaseModel):
    """
        Level 2: Analysis step to modify an existing BuilderModel object by changing one variable
    """
    type: Literal['ModifyModel']
    model_name: Optional[str] = None
    variable_to_change: Optional[str] = None
    variable_value: list = []
    new_model_name: List[str] = []  # if not empty, new copies of the model object will be built
    simulation_numbers: List[Union[int, str]] = []  # if not empty, simulation files will be built
    simulation_name: Optional[str] = None
    software: Optional[str] = None
    flag_json: Optional[bool] = None
    flag_plot_all: Optional[bool] = None
    verbose: Optional[bool] = None
    model_config = ConfigDict(protected_namespaces=())



class ModifyModelMultipleVariables(BaseModel):
    """
        Level 2: Analysis step to modify an existing BuilderModel object by changing a list of variables
    """
    type: Literal['ModifyModelMultipleVariables']
    model_name: Optional[str] = None
    variables_to_change: List[str] = []
    variables_value: List[Union[List, str, float, int]] = []
    new_model_name: List[str] = []  # if not empty, new copies of the model object will be built
    simulation_numbers: List[Union[int, str]] = []  # if not empty, simulation files will be built
    simulation_name: Optional[str] = None
    software: Optional[str] = None
    flag_json: Optional[bool] = None
    flag_plot_all: Optional[bool] = None
    verbose: Optional[bool] = None
    model_config = ConfigDict(protected_namespaces=())


class SetUpFolder(BaseModel):
    """
        Level 2: Analysis step to set up the folder structure for the required simulation software
    """
    type: Literal['SetUpFolder']
    simulation_name: Optional[str] = None
    software: Optional[str] = None


class AddAuxiliaryFile(BaseModel):
    """
        Level 2: Analysis step to add/change an auxiliary file
    """
    type: Literal['AddAuxiliaryFile']
    software: Optional[str] = None
    simulation_name: Optional[str] = None
    simulation_numbers: List[Union[int, str]] = []  # if not empty, simulation files will be built
    full_path_aux_file: Optional[str] = None
    new_file_name: Optional[str] = None  # if empty, file is not renamed


class CopyFile(BaseModel):
    """
        Level 2: Analysis step to copy one file from a location to another
    """
    type: Literal['CopyFile']
    full_path_file_to_copy: Optional[str] = None
    full_path_file_target: Optional[str] = None


class CopyFileRelativeEntries(BaseModel):
    local_tool_folders: List[str] = []
    simulation_names: List[str] = []
    remainder_paths:  List[str] = []


class CopyFileRelative(BaseModel):
    """
        Level 2: Analysis step to copy one file from a location to another
    """
    type: Literal['CopyFileRelative']
    copy_from: CopyFileRelativeEntries = CopyFileRelativeEntries()
    copy_to: CopyFileRelativeEntries = CopyFileRelativeEntries()


class RunSimulation(BaseModel):
    """
        Level 2: Analysis step to run a simulation file
    """
    type: Literal['RunSimulation']
    software: Optional[str] = None
    simulation_name: Optional[str] = None
    simulation_numbers: List[Union[int, str]] = []
    simFileType: Optional[str] = None
    timeout_s: Optional[int] = None
    concurrency: Optional[Union[int, Literal["htcondor"]]] = Field(
        default=1,                           
        title="concurrency setting",
        description="Concurrency setting. If it is an integer, it defines the number of parallel workers. If it is 'htcondor', it will use the HTCondor cluster.",
        examples=[1, 7, "htcondor"]
    )


class PostProcessCompare(BaseModel):
    """
        Level 2: Analysis step to run a simulation file
    """
    type: Literal['PostProcessCompare']
    physical_quantity: Optional[str] = None
    simulation_numbers: Optional[Union[Literal['ParametricSweep'], Tuple[int, int], Tuple[str, str], int, str]] = None  # first is considered reference. If only an int is provided, the other results are taken from ROXIE. If ParametricSweep is used, the first of the csv is taken as reference
    time_steps: Optional[Union[str, List[Tuple[float, float, float]]]] = None  # If ParametricSweep is used for simulation_numbers, the time steps of each compared data set are used
    simulation_name: Optional[str] = None
    path_to_saved_files: Optional[str] = None


class PostProcess(BaseModel):
    """
        Level 2: Analysis step to run a simulation file
    """
    type: Literal['PostProcess']
    software: Optional[str] = None
    simulation_name: Optional[str] = None
    simulation_number: Union[int, str] = None


class RunCustomPyFunction(BaseModel):
    """
        Level 2: Analysis step to run a custom Python function
    """
    type: Literal['RunCustomPyFunction']
    flag_enable: Optional[bool] = None
    function_name: Optional[str] = None
    function_arguments: Dict = {}
    path_module: Optional[str] = None  # optional


class RunViewer(BaseModel):
    """
        Level 2: Analysis step to make a steam_sdk.viewers.Viewer.Viewer() object and run its analysis
    """
    type: Literal['RunViewer']
    viewer_name: Optional[str] = None
    file_name_transients: Optional[str] = None
    list_events: List[int] = []
    flag_analyze: Optional[bool] = None
    flag_display: Optional[bool] = None
    flag_save_figures: Optional[bool] = None
    path_output_html_report: Optional[str] = None
    path_output_pdf_report: Optional[str] = None
    figure_types: Union[List[str], str] = []
    verbose: Optional[bool] = None


class CalculateMetrics(BaseModel):
    """
        Level 2: Analysis step to calculate metrics (usually to compare two or more measured and/or simulated signals)
    """
    type: Literal['CalculateMetrics']
    viewer_name: Optional[str] = None
    metrics_name: Optional[str] = None
    metrics_to_calculate: List[str] = []
    variables_to_analyze: List[List[str]] = [[]]
    metrics_output_filepath: Optional[str] = None


class LoadCircuitParameters(BaseModel):
    """
        Level 2: Analysis step to load global circuit parameters from a .csv file
    """
    type: Literal['LoadCircuitParameters']
    model_name: Optional[str] = None
    path_file_circuit_parameters: Optional[str] = None
    selected_circuit_name: Optional[str] = None
    model_config = ConfigDict(protected_namespaces=())


class WriteStimulusFile(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from coil resistance csv file
    """
    type: Literal['WriteStimulusFile']
    output_file: Optional[str] = None
    path_interpolation_file: Union[str, List[str]] = None
    n_total_magnets: Optional[int] = None
    n_apertures: Optional[int] = None
    current_level: List[float] = []
    magnets: List[int] = []
    t_offset: List[float] = []
    interpolation_type: Optional[str] = None  # 'Linear' or 'Spline'
    type_file_writing: Optional[str] = None  # 'w' or 'a'
    n_sampling: Optional[int] = None
    magnet_types: List[int] = []
    software: Optional[str] = None


class DefaultParsimEventKeys(BaseModel):
    """
        Level 3: Class for default keys of ParsimEventMagnet
    """
    local_LEDET_folder: Optional[str] = None
    path_config_file: Optional[str] = None
    default_configs: List[str] = []
    path_tdms_files: Optional[str] = None
    path_output_measurement_files: Optional[str] = None
    path_output: Optional[str] = None


class ParsimEvent(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from coil resistance csv file
    """
    type: Literal['ParsimEvent']
    input_file: Optional[str] = None
    path_output_event_csv: Optional[str] = None
    path_output_viewer_csv: Optional[str] = None  # This used to be a list, but now it is a string (March 2024)
    simulation_numbers: List[Union[int, str]] = []
    model_name: Optional[str] = None
    case_model: Optional[str] = None
    simulation_name: Optional[str] = None
    software: Optional[str] = None
    t_PC_off: Optional[float] = None  # TODO: consider making list of floats
    rel_quench_heater_trip_threshold: Optional[float] = None
    current_polarities_CLIQ: List[int] = []  # TODO: consider making list of lists
    dict_QH_circuits_to_QH_strips: Dict[str, List[int]] = {}
    default_keys: DefaultParsimEventKeys = DefaultParsimEventKeys()
    path_postmortem_offline_data_folder: Optional[str] = None
    path_to_configurations_folder: Optional[str] = None
    filepath_to_temp_viewer_csv: Optional[str] = None
    model_config = ConfigDict(protected_namespaces=())


class ParametricSweep(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from sweep input csv file
    """
    type: Literal['ParametricSweep']
    input_sweep_file: Optional[str] = None
    model_name: Optional[str] = None
    case_model: Optional[str] = None
    software: Optional[str] = None
    verbose: Optional[bool] = None
    model_config = ConfigDict(protected_namespaces=())

class ParsimConductor(BaseModel):
    """
        Level 2: Analysis step to write stimulus file from coil csv file
    """
    type: Literal['ParsimConductor']
    model_name: Optional[str] = None
    case_model: Optional[str] = None
    input_file: Optional[str] = None
    magnet_name: Optional[str] = None
    software: Optional[str] = None
    simulation_number: Optional[Union[int, str]] = None
    strand_critical_current_measurements: List[StrandCriticalCurrentMeasurement] = []
    groups_to_coils: Dict[str, List[int]] = {}
    length_to_coil: Dict[str, float] = {}
    path_output_sweeper_csv: Optional[str] = None
    model_config = ConfigDict(protected_namespaces=())

# class AnalysisStep(BaseModel):
#     """
#         Level 1: Class for information on the analysis step
#         Objects of this class will be defined in AnalysisStepDefinition
#     """
#     step: Union[MakeModel, ModifyModel, ModifyModelMultipleVariables, SetUpFolder, ChangeAuxiliaryFile, RunSimulation, PostProcess] = {}

############################
# Highest level
class DataAnalysis(BaseModel):
    '''
        **Class for the STEAM analysis inputs**

        This class contains the data structure of an analysis performed with STEAM_SDK.

        :param N: test 1
        :type N: int
        :param n: test 2
        :type n: int

        :return: DataModelCircuit object
    '''

    GeneralParameters: General = General()
    PermanentSettings: DataSettings = DataSettings()
    AnalysisStepDefinition: Dict[str, Union[MakeModel, ModifyModel, ModifyModelMultipleVariables, SetUpFolder,
                                            AddAuxiliaryFile, CopyFile, CopyFileRelative, RunSimulation, PostProcessCompare, PostProcess, RunCustomPyFunction,
                                            RunViewer, CalculateMetrics, LoadCircuitParameters, WriteStimulusFile,
                                            ParsimEvent, ParametricSweep, ParsimConductor]] = {}
    AnalysisStepSequence: List[str] = []  # Here the analysis steps are defined, in execution order. Names must be defined in AnalysisStepDefinition. Repetitions ARE allowed.
