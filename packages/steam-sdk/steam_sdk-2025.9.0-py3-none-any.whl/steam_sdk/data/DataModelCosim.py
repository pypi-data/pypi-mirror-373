from typing import List, Union, Dict, Literal, Optional, Any

from pydantic import BaseModel, Field, validator, ConfigDict


############################
# General parameters
class Model(BaseModel):
    """
        Level 2: Class for information on the model
    """
    name: Optional[str] = None
    version: Optional[str] = None
    case: Optional[str] = None
    state: Optional[str] = None


class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    cosim_name: Optional[str] = None
    model: Model = Model()


############################
# Simulation configurations - one for simulation tool

class ConvergenceChecks(BaseModel):
    """
        Level 2: Class to define convergence checks to perform
    """
    file_name_relative_path: Optional[str] = Field(default=None, description="Name of the file with variable from which the convergence should be read."
                                                                             "It is possible to use here inside <<>> special names replaced during run time with variables. These names include:"
                                                                             "<<modelName>> replace by current model name"
                                                                             "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                             "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                             "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                             "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                             "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name")
    var_name: Optional[str] = Field(default=None, description="Name of the convergence variable")
    time_var_name: Optional[str] = Field(default=None, description="Name of the variable defining the time vector. If defined, the variable values will be interpolated over the time vector before being compared.")
    relative_tolerance: Optional[float] = Field(default=None, description="Relative tolerance applied to the convergence check (either relative_tolerance or absolute_tolerance must be fulfilled to pass the convergence check)")
    absolute_tolerance: Optional[float] = Field(default=None, description="Absolute tolerance applied to the convergence check (either relative_tolerance or absolute_tolerance must be fulfilled to pass the convergence check)")


class FileToCopy(BaseModel):
    source_file_name_relative_path: Optional[str] = Field(default=None, description="Name of the file to copy"
                                                                                 "It is possible to use here inside <<>> special names replaced during run time with variables. These names include:"
                                                                                 "<<modelName>> replace by current model name"
                                                                                 "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                                 "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                                 "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                                 "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                                 "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name")
    target_model: Optional[str] = Field(default=None, description="Name of the simulation model")
    target_file_name_relative_path: Optional[str] = Field(default=None, description="New name of the file to copy. If null, don't change the name"
                                                                                 "It is possible to use here inside <<>> special names replaced during run time with variables. These names include:"
                                                                                 "<<modelName>> replace by current model name"
                                                                                 "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                                 "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                                 "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                                 "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                                 "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name")
    dict_translate_variables: Dict = Field(default={}, description="Dictionary defining the names of the variables to read from the source file and write to the target file with different names.")
    list_time_shifts: List[float] = Field(default=[], description="List defining the time shift to apply at each time window when copying the file. This list must contain either zero elements or as many elements as time windows. It cannot be used in PreCoSim or PostCoSim.")


class VariableToCopy(BaseModel):
    source_file_name_relative_path: Optional[str] = Field(default=None, description="Path of the file that contains the variable to copy (supported formats: .csd, .csv, .mat)"
                                                                             "It is possible to use here inside <<>> special names replaced during run time with variables. These names include:"
                                                                             "<<modelName>> replace by current model name"
                                                                             "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                             "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                             "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                             "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                             "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name")
    var_name: Optional[str] = Field(default=None, description="Name of the variable to copy (header name is a .csv or .csd file, or variable name in a .mat file")
    target_model: Optional[str] = Field(default=None, description="Name of the simulation model")
    model_var_name: Optional[str] = Field(default=None, description="Name of the BuilderModel key to which the variable value will be assigned")
    model_config = ConfigDict(protected_namespaces=())


class SimulationSimParameters(BaseModel):
    """
        Level 2: Class to define parameters such as flag to run, variables to modify, and files and variables to pass between simulations.
        This class is re-used by PreCoSim(), CoSim(), and PostCoSim() classes.
    """
    flag_run: Optional[bool] = Field(default=None, description="Flag to enable (True) or disable (False) running this simulation")
    files_to_copy_after_time_window: List[FileToCopy] = Field(default=[], description="Files to copy after current model solved and to the next time window of the target model")
    variables_to_copy_after_time_window: List[VariableToCopy] = Field(default=[], description="Variables to copy after the simulation to the new time window of target model")

class PreCoSimParameters(SimulationSimParameters):
    """
        Level 2: Class of Pre-CoSimulation
    """
    variables_to_modify_time_window: Dict[str, Any] = Field(default={}, description="Dictionary with keys of model data and values that are modified in the simulation"
                                                                                    "It is possible to a special <<name>> with the name that is replaced during run time with run-time variable."
                                                                                    "Valid names are:"
                                                                                    "<<modelName>> replace by current model name"
                                                                                    "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                                    "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                                    "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                                    "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                                    "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name"
                                                                                    "The above names are used and updated with variable for source or target models")


class CoSimParameters(SimulationSimParameters):
    """
        Level 2: Class of Pre-CoSimulation
    """
    files_to_copy_after_iteration: List[FileToCopy] = Field(default=[], description="Files to copy after current model solved and to the next iteration of the target model")
    variables_to_copy_after_iteration: List[VariableToCopy] = Field(default=[], description="Variables to copy after the simulation to the new iteration of target model")
    variables_to_modify_iteration: Dict[str, Any] = Field(default={}, description="Dictionary with keys of model data and values that are modified in the simulation"
                                                           "It is possible to a special <<name>> with the name that is replaced during run time with run-time variable."
                                                           "Valid names are:"
                                                           "<<modelName>> replace by current model name"
                                                           "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                           "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                           "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                           "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                           "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name"
                                                           "The above names are used and updated with variable for source or target models")
    variables_to_modify_for_each_time_window: List[Dict[str, Any]] = Field(default=[{}], description="List of dictionaries with keys of model data and values that are modified in co-simulation"
                                                                                       "Each defining a list of parameters to change at one time window. This list must have as many elements as the number of time windows."
                                                                                       "It is possible to a special <<name>> with the name that is replaced during run time with run-time variable."
                                                                                       "Valid names are:"
                                                                                       "<<modelName>> replace by current model name"
                                                                                       "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                                       "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                                       "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                                       "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                                       "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name"
                                                                                       "The above names are used and updated with variable for source or target models")
    convergence: List[ConvergenceChecks] = Field(default=[], description="List of convergence checks to perform during each time window (all variable checks must be fulfilled to pass the convergence check). If not defined, convergence for this model will be always assumed true.")

class PostCoSimParameters(SimulationSimParameters):
    """
        Level 2: Class of Pre-CoSimulation
    """
    variables_to_modify_time_window: Dict[str, Any] = Field(default={}, description="Dictionary with keys of model data and values that are modified in the simulation"
                                                                                    "It is possible to a special <<name>> with the name that is replaced during run time with run-time variable."
                                                                                    "Valid names are:"
                                                                                    "<<modelName>> replace by current model name"
                                                                                    "<<n_s_t_i>> replace by current model n_s_t_i. Remember to put _ in front e.g. typically _<<n_s_t_i>> is used in file name"
                                                                                    "<<n>> replace by current model simulation number n. Remember to put _ in front e.g. typically _<<n>> is used in file name"
                                                                                    "<<s>> replace by current model set s. Remember to put _ in front e.g. typically _<<s>> is used in file name"
                                                                                    "<<t>> replace by current model time window number t. Remember to put _ in front e.g. typically _<<t>> is used in file name"
                                                                                    "<<i>> replace by current model iteration i. Remember to put _ in front e.g. typically _<<i>> is used in file name"
                                                                                    "The above names are used and updated with variable for source or target models")


class sim_Generic(BaseModel):
    """
        Level 1: Class of FiQuS simulation configuration
    """
    name: Optional[str] = None
    modelName: Optional[str] = None
    modelCase: Optional[str] = None
    PreCoSim: PreCoSimParameters = Field(default=PreCoSimParameters(), description="Pre-co-simulation: Section to define flag to run, variables to modify, and files and variables to pass between simulations.")
    CoSim: CoSimParameters = Field(default=CoSimParameters(), description="Co-simulation: Section to define flag to run, variables to modify, and files and variables to pass between simulations.")
    PostCoSim: PostCoSimParameters = Field(default=PostCoSimParameters(), description="Post-co-simulation: Section to define flag to run, variables to modify, and files and variables to pass between simulations.")


class sim_FiQuS(sim_Generic):
    """
        Level 1: Class of FiQuS simulation configuration
    """
    type: Literal['FiQuS']


class sim_LEDET(sim_Generic):
    """
        Level 1: Class of LEDET simulation configuration
    """
    type: Literal['LEDET']


class sim_PSPICE(sim_Generic):
    """
        Level 1: Class of PSPICE simulation configuration
    """
    type: Literal['PSPICE']
    configurationFileName: Optional[str] = None
    externalStimulusFileName: Optional[str] = None
    initialConditions: Dict[str, Union[float, int]] = {}
    skipBiasPointCalculation: Optional[bool] = None


class sim_XYCE(sim_Generic):
    """
        Level 1: Class of XYCE simulation configuration
    """
    type: Literal['XYCE']
    configurationFileName: Optional[str] = None
    externalStimulusFileName: Optional[str] = None
    initialConditions: Dict[str, Union[float, int]] = {}
    skipBiasPointCalculation: Optional[bool] = None


############################
# Co-simulation port
# class CosimPortModel(BaseModel):
#     input_model: Optional[str] = None
#     input_variable_component: Optional[str] = None
#     input_variable_name: Optional[str] = None
#     input_variable_coupling_parameter: Optional[str] = None
#     input_variable_type: Optional[str] = None
#     output_model: Optional[str] = None
#     output_variable_component: Optional[str] = None
#     output_variable_name: Optional[str] = None
#     output_variable_coupling_parameter: Optional[str] = None
#     output_variable_type: Optional[str] = None

class CosimPortVariable(BaseModel):
    variable_names: List[str] = []
    variable_coupling_parameter: Optional[str] = None
    variable_types: List[str] = []


class CosimPortModel(BaseModel):
    components: List[str] = []
    inputs: Dict[str, CosimPortVariable] = {}
    outputs: Dict[str, CosimPortVariable] = {}


class CosimPort(BaseModel):
    """
    Class for co-simulation port to be used within PortDefinition
    """
    Models: Dict[str, CosimPortModel] = {}


############################
# Co-simulation settings
class ConvergenceClass(BaseModel):
    """
        Level 2: Class for convergence options
    """
    convergenceVariables: Dict[str, Union[str, None]] = {}
    relTolerance: Dict[str, Union[float, int, None]] = {}
    absTolerance: Dict[str, Union[float, int, None]] = {}


class Time_WindowsClass(BaseModel):
    """
        Level 2: Class for time window options
    """
    t_0: Optional[List[Union[float, int]]] = []
    t_end: Optional[List[Union[float, int]]] = []
    t_step_max: Optional[Dict[str, List[Union[float, int]]]] = {}


class Options_runClass(BaseModel):
    """
        Level 2: Class for co-simulation run options
    """
    executionOrder: Optional[List[int]] = []
    executeCleanRun: Optional[List[bool]] = []


class CosimulationSettings(BaseModel):
    """
        Level 1: Class for co-simulation settings
    """
    Convergence: ConvergenceClass = ConvergenceClass()
    Time_Windows: Time_WindowsClass = Time_WindowsClass()
    Options_run: Options_runClass = Options_runClass()


class CosimulationSettings(BaseModel):
    """
        Level 1: Class for co-simulation settings
    """
    Convergence: ConvergenceClass = ConvergenceClass()
    Time_Windows: Time_WindowsClass = Time_WindowsClass()
    Options_run: Options_runClass = Options_runClass()


############################
# COSIM options
class Options_COSIMClass(BaseModel):
    """
        Level 1: Class for co-simulation settings
    """
    solverPaths: Dict[str, str] = Field(default={}, description="Dictionary containing the paths to the solvers used by each simulation defined in the 'Simulations' key. The keys of this dictionary must match the keys of the 'Simulations' dictionary.")
    PortDefinition: Dict[str, CosimPort] = {}
    Settings: CosimulationSettings = CosimulationSettings()

# pyCOSIM options
class PlotsPyCoSim(BaseModel):
    """
        Defines options for plotting of PyCoSim
    """
    Convergence: Optional[bool] = Field(default=None, description="If true a plot of convergence  variables for all models and variables is made. If false no plot is made")
    DuringCoSim: Optional[bool] = Field(default=None, description="If true plotting is done during run time. If falls no plotting is done during run time")
    Style: Optional[str] = Field(default='default', description="This defines a plot style to use. If a string defined does not exist in the sdk defined styles, a default style is used.")

############################
# pyCOSIM PostProcess entries
class PostProcessPyCoSim(BaseModel):
    """
        Defines options for postprocessing of PyCoSim
    """
    Plots: PlotsPyCoSim = PlotsPyCoSim()

class Options_PyCoSimClass(BaseModel):
    """
        Level 1: Class for co-simulation settings
    """
    Start_from_s_t_i: Optional[str] = Field(default=None, description="Allows setting s_t_i to start from. The n of the full n_s_t_i is taken from the current simulation number."
                                                                      "Only CoSim s_t_i can be chosen (i.e. no Pre or Post Cosim s_t_i are coded). This skips the PreCosim stages."
                                                                      "The s_t_i to give is typically to last last set, time window and last iteration that failed to solve"
                                                                      "The entry needs to be put in quotation marks, e.g. '1_1_1'")
    PostProcess: PostProcessPyCoSim = PostProcessPyCoSim()

############################
# Highest level
class DataModelCosim(BaseModel):
    """
        **Class for the STEAM inputs**

        This class contains the data structure of STEAM model inputs for cooperative simulations (co-simulations).

        :return: DataCosim object
    """

    GeneralParameters: General = General()
    Simulations: Dict[str, Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE]] = {}
    Options_PyCoSim: Options_PyCoSimClass = Options_PyCoSimClass()
    Options_COSIM: Options_COSIMClass = Options_COSIMClass()


    @validator('Simulations')
    def validate_Simulations(cls, Simulations):
        for key, value in Simulations.items():
            value.name = key
        return Simulations

    # def __init__(self, **data):
    #     super().__init__(**data)
    #     for key, value in self.Simulations.items():
    #         value.name = key
    #     print('aa')
