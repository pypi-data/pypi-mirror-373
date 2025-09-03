from pydantic import BaseModel, create_model, Field
from typing import Any, Dict, List, Optional, Union
from steam_sdk.data.DataTFM import Wedge, CB, CPS, AlRing, BS, Shorts, Capacitances


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
    circuit_name: Optional[str] = None
    model: Model = Model()
    additional_files: List[str] = Field(default=[], description="These files will be physically copied to the output folder.")


############################
# Auxiliary files
class Auxiliary_Files(BaseModel):
    """
        Level 1: Class for general information on the case study
        Note: These entries will be written in the netlist, but no further action will be taken (see General.additional_files)
    """
    files_to_include: List[str] = Field(default=[], description="These entries will be written in the netlist, but no further action will be taken (to physically copy files, see General.additional_files).")


############################
# Stimuli
class StimuliClass(BaseModel):
    """
        Level 1: Stimulus files
    """
    flag_check_existence_stimulus_files: Optional[bool] = Field(default=None, description="If True, the code will make sure that the bias-point file is of \".IC\" type, i.e. that it can be used to set initial conditions.")
    stimulus_files: List[str] = []


############################
# Libraries
class LibrariesClass(BaseModel):
    """
        Level 1: Component libraries
    """
    component_libraries: List[str] = []


############################
# TFM Couplings
class TFM_Couplings(BaseModel):
    M_AlRing_Wedge: Optional[float] = None
    M_AlRing_CPS: Optional[float] = None
    M_AlRing_CB: Optional[float] = None
    M_AlRing_BS: Optional[float] = None
    M_CPS_Wedge: Optional[float] = None
    M_CPS_CB: Optional[float] = None
    M_CPS_BS: Optional[float] = None
    M_CB_Wedge: Optional[float] = None
    M_CB_BS: Optional[float] = None
    M_Wedge_BS: Optional[float] = None

############################
class Magnet_TFM(BaseModel):
    circuit_name: Optional[str] = None
    name: Optional[str] = None
    n_apertures: Optional[int] = None
    multipole_type: Optional[str] = None
    C_ground: Optional[float] = None
    turn_to_section: Optional[list] = None
    section_to_aperture: Optional[list] = None
    magnet_Couplings: Optional[TFM_Couplings] = None
    magnet_Wedge: Optional[Wedge] = None
    magnet_CB: Optional[CB] = None
    magnet_CPS: Optional[CPS] = None
    magnet_AlRing: Optional[AlRing] = None
    magnet_BS: Optional[BS] = None
    magnet_Shorts: Optional[Shorts] = None
    magnet_Capacitances: Optional[Capacitances] = None
    class Config:
        arbitrary_types_allowed = True

class TFMClass(BaseModel):
    flag_BS: Optional[bool] = None
    flag_Wedge: Optional[bool] = None
    flag_CB: Optional[bool] = None
    flag_CPS: Optional[bool] = None
    flag_AlRing: Optional[bool] = None
    flag_ISCC: Optional[bool] = None
    flag_ED: Optional[bool] = None
    flag_IFCC: Optional[bool] = None
    flag_PC: Optional[bool] = None
    flag_debug: Optional[bool] = None
    flag_LumpedC: Optional[bool] = True
    skip_TFM: Optional[bool] = None
    temperature: Optional[float] = None
    current: Optional[float] = None
    B_nom_center: Optional[float] = None
    magnets_TFM: Dict[str, Magnet_TFM] = {}


############################
# Global parameters
class Global_Parameters(BaseModel):
    """
        Level 1: Global circuit parameters
    """
    global_parameters: Optional[dict] = None


############################
# Initial conditions
class InitialConditionsClass(BaseModel):
    """
        Level 1: Initial conditions parameters
    """
    initial_conditions: Optional[dict] = None


############################
# Netlist, defined as a list of Component objects
# class NetlistClass(BaseModel):
#     """
#         Level 1: Netlist
#     """
#     def __setattr__(self, key, value):
#         return object.__setattr__(self, key, value)

class Component(BaseModel):
    """
        Level 2: Circuit component
    """
    type: Optional[str] = None
    nodes: List[Union[str, int]] = []
    value: Optional[str] = None
    parameters: Optional[dict] = dict()


############################
# Simulation options
class OptionsClass(BaseModel):
    """
        Level 1: Simulation options
    """
    options_simulation: Optional[dict] = None
    options_autoconverge: Optional[dict] = None
    flag_inCOSIM: Optional[bool] = None


############################
# Analysis settings
class SimulationTime(BaseModel):
    """
        Level 2: Simulation time settings
    """
    time_start: Optional[float] = None
    time_end: Optional[float] = None
    min_time_step: Optional[float] = None
    time_schedule: Optional[dict] = {}


class SimulationFrequency(BaseModel):
    """
        Level 2: Simulation frequency settings
    """
    frequency_step: Optional[str] = None
    frequency_points: Optional[float] = None
    frequency_start: Optional[str] = None
    frequency_end: Optional[str] = None


class AnalysisClass(BaseModel):
    """
        Level 1: Analysis settings
    """
    analysis_type: Optional[str] = None
    simulation_time: Optional[SimulationTime] = SimulationTime()
    simulation_frequency: Optional[SimulationFrequency] = SimulationFrequency()


############################
# Bias settings
class Settings_LoadBias(BaseModel):
    """
        Level 2: Load bias points (load currents and voltages) settings
    """
    file_path: Optional[str] = Field(default=None, description="Path of the file from which the bias points will be read at the beginning of the simulation. The expected extension is .bsp. This option will make the software load initial voltages and currents from the file.")
    flag_check_load_bias_files: Optional[bool] = Field(default=None, description="If True, the code will check whether each stimulus file included in the netlist exists. If it doesn't exist, it'll generate such a file with a dummy entry. This action will prevent PSPICE from returning error during runtime.")

class Settings_SaveBias(BaseModel):
    """
        Level 2: Save bias points (save currents and voltages) settings
    """
    file_path: Optional[str] = Field(default=None, description="Path of the file where the bias points will be written at the end of the simulation. The expected extension is .bsp. This option will make the software save final voltages and currents to the file.")
    analysis_type: Optional[str] = Field(default=None, description="Type of analysis to run. Default is \"transient\".")
    save_bias_time: Optional[float] = Field(default=None, description="Simulation time at which the bias points will be written. This usually should be defined as the end of the simulation.")

class BiasClass(BaseModel):
    """
        Level 1: Bias (load/save currents and voltages) settings
    """
    load_bias_points: Settings_LoadBias = Settings_LoadBias()
    save_bias_points: Settings_SaveBias = Settings_SaveBias()


############################
# Post-processing settings
class Settings_Probe(BaseModel):
    """
        Level 2: Probe settings
    """
    probe_type: Optional[str] = None
    variables: List[str] = []

class PostProcessClass(BaseModel):
    """
        Level 1: Post-processing settings
    """
    probe: Settings_Probe = Settings_Probe()


############################
# Highest level
class DataModelCircuit(BaseModel):
    '''
        **Class for the circuit netlist inputs**

        This class contains the data structure of circuit netlist model inputs.

        :param N: test 1
        :type N: int
        :param n: test 2
        :type n: int

        :return: DataModelCircuit object
    '''

    GeneralParameters: General = General()
    AuxiliaryFiles: Auxiliary_Files = Auxiliary_Files()
    Stimuli: StimuliClass = StimuliClass()
    Libraries: LibrariesClass = LibrariesClass()
    GlobalParameters: Global_Parameters = Global_Parameters()
    InitialConditions: InitialConditionsClass = InitialConditionsClass()
    Netlist: Dict[str, Component] = {}
    Options: OptionsClass = OptionsClass()
    Analysis: AnalysisClass = AnalysisClass()
    BiasPoints: BiasClass = BiasClass()
    PostProcess: PostProcessClass = PostProcessClass()
    TFM: Optional[TFMClass] = None
