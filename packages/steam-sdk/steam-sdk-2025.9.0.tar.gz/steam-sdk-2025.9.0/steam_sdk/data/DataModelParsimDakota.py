from pydantic import BaseModel, Field

from typing import Dict, List, Union, Literal, Optional

class Bound(BaseModel):
    """
        Class for FiQuS multipole
    """
    min: Optional[float] = None
    max: Optional[float] = None


class SamplingVar(BaseModel):
    """
        Class for FiQuS multipole
    """
    bounds: Bound = Bound()


class MultiDimParStudyVar(BaseModel):
    """
        Class for FiQuS multipole
    """
    data_points: Optional[int] = None
    bounds: Bound = Bound()

class VariablesWithInitialBounds(BaseModel):
    """
        Dataclass for variables that need initial bounds, e.g. for local optimization
    """
    initial_point: float = Field(default=None, description="First design point the algorithm chooses for a variable")
    bounds: Bound = Bound()
    scale_type: Optional[str] = None
    #descriptors: str = Field(default=None, description="Smart sentence from dakota manual")

class Sampling(BaseModel):
    """
        Class for FiQuS multipole
    """
    type: Literal['sampling']
    samples: Optional[int] = None
    seed: Optional[int] = None
    response_levels: Optional[float] = None
    variables: Dict[str, SamplingVar] = {}


class MultiDimParStudy(BaseModel):
    """
        Class for FiQuS multipole
    """
    type: Literal['multidim_parameter_study']
    variables: Dict[str, MultiDimParStudyVar] = {}

class OptppQNewton(BaseModel):
    """
        Data class of the coliny_pattern_search algorithm OptppQNewton
    """
    type: Literal['optpp_q_newton']
    convergence_tolerance: float = Field(default=None, description="Smart sentence from dakota manual")
    gradient_tolerance: float = Field(default=None, description="Threshold value on the L2 norm of the objective function"
                                                                "gradient that indicates convergence to a stationary point.")
    variables: Dict[str, VariablesWithInitialBounds] = {}
    #samples: Optional[int] = None
    #seed: Optional[int] = None

    #response_levels: Optional[float] = None

class coliny_pattern_search(BaseModel):
    """
        Data class of the coliny_pattern_search algorithm
    """
    type: Literal['coliny_pattern_search']
    initial_delta: float = Field(default=None, description="Difference between two initial steps")
    solution_target: float = Field(default=None, description="Stopping criteria based on objective function value ")
    contraction_factor: float = Field(default=None, description="Amount by which step length is rescaled ")
    max_iterations: int = Field(default=None, description="Number of iterations allowed for optimizers and adaptive UQ methods")
    max_function_evaluations: int = Field(default=None, description="Number of function evaluations allowed for optimizers")
    variable_tolerance: float = Field(default=None, description="Step length-based stopping criteria for derivative-free optimizers")
    variables: Dict[str, VariablesWithInitialBounds] = {}
    #samples: Optional[int] = None
    #seed: Optional[int] = None

    #response_levels: Optional[float] = None




class Response(BaseModel):
    """
        Class for FiQuS multipole
    """
    response: Optional[str] = None  # Union[ResponseFunction, ObjectiveFunction] = {'type': 'response_functions'}
    descriptors: Optional[List[str]] = None


# First Level
class DataModelParsimDakota(BaseModel):
    parsim_name: str = Field(default=None, description="Name of the study. This is folder name in which the files will be saved in the local_Dakota_folder")
    sim_number_offset: int = Field(default=None, description="This number is added to the simulation numbers used by the tool and Dakota. THis is to enable not overwriting simulations in the tool folder")
    evaluation_concurrency: int = Field(default=None, description="Number of concurrent executions. ")
    study: Union[MultiDimParStudy, Sampling, OptppQNewton,coliny_pattern_search] = {'Type of study (algorithm) selected for the optimization/parameter study.'}
    responses: Response = Response()
    relative_path_analysis_file: str = Field(default=None, description="Relative path (in relation to dakota input yaml) to analysis file, including the file name and extension")
    initial_steps_list: List[str] = Field(default=None, description="List of initial steps to be performed before Dakota is running (looping)")
    iterable_steps_list: List[str] = Field(default=None, description="List of steps to repeat in the analysis when Dakota is running (looping)")
    python_path_dakota: str = Field(default="python.exe", description="Path to the python.exe, that Dakota should use for running driver_link.py")

# from steam_sdk.data.DataAnalysis import WorkingFolders
# from steam_sdk.data.DataSettings import DataSettings

### SUB-SUB-LEVEL
# class interface(BaseModel):
#     analysis_drivers: str = ''
#     fork: Optional[str] = None
#     interface_arguments: Dict = {}
#
#
# class responses(BaseModel):
#     response_functions: int = 0
#     descriptors: Optional[List[str]] = None
#     objective_functions: int = 0
#     nonlinear_inequality_constraints: int = 0
#     calibration_terms: int = 0
#     type_gradients: str = ''
#     numerical_gradients: Dict = {}
#     analytical_gradients: Dict = {}
#     no_gradients: bool = False
#     no_hessians: bool = False
#
#
# class variables(BaseModel):
#     type_variable: str = ''
#     variable_arguments: Dict = {}
#
#
# class model(BaseModel):
#     type_model: str = ''
#
#
# class method(BaseModel):
#     type_method: str = ''
#     method_argument: Dict = {}
#
#
# class environment(BaseModel):
#     graphics: bool = False
#     type_tabular_data: str = ''
#     tabular_data_argument: Dict = {}
#
#
# # SUB-LEVEL
# class DAKOTA_analysis(BaseModel):
#     interface: interface = interface()
#     responses: responses = responses()
#     variables: variables = variables()
#     method: method = method()
#     model: model = model()
#     environment: environment = environment()





# Second Level: Responses
# class ObjectiveFunction(BaseModel):
#     """
#         Class for FiQuS multipole
#     """
#     #type: Literal['objective_functions']
#
#
# class ResponseFunction(BaseModel):
#     """
#         Class for FiQuS multipole
#     """
#     #type: Literal['response_functions']




