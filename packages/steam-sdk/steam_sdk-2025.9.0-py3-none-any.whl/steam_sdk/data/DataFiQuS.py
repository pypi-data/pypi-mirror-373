from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional, Union, List

from steam_sdk.data.DataConductorFiQuS import Conductor as ConductorFiQuS
from steam_sdk.data.DataModelCommon import Circuit_Class
from steam_sdk.data.DataModelCommon import PowerSupplyClass
from steam_sdk.data.DataModelCommon import EnergyExtraction, CLIQ_Class, E_CLIQ_Class, ESC_Class
from steam_sdk.data.DataModelCommon import QuenchDetection

from steam_sdk.data.DataFiQuSCCT import CCT
from steam_sdk.data.DataFiQuSCWS import CWS
from steam_sdk.data.DataFiQuSConductorAC_Strand import CACStrand
from steam_sdk.data.DataFiQuSConductorAC_Rutherford import CACRutherford
from steam_sdk.data.DataFiQuSPancake3D import Pancake3D
from steam_sdk.data.DataFiQuSMultipole import Multipole


class RunFiQuS(BaseModel):
    """
    Class for FiQuS run
    """

    type: Optional[Literal[
        "start_from_yaml",
        "mesh_only",
        "geometry_only",
        "geometry_and_mesh",
        "pre_process_only",
        "mesh_and_solve_with_post_process_python",
        "solve_with_post_process_python",
        "solve_only",
        "post_process_getdp_only",
        "post_process_python_only",
        "post_process",
        "plot_python",
        "batch_post_process_python",
    ]] = Field(
        default="start_from_yaml",
        title="Run Type of FiQuS",
        description="FiQuS allows you to run the model in different ways. The run type can be specified here. For example, you can just create the geometry and mesh or just solve the model with previous mesh, etc.",
    )
    geometry: Optional[Union[str, int]] = Field(
        default=None,
        title="Geometry Folder Key",
        description="This key will be appended to the geometry folder.",
    )
    mesh: Optional[Union[str, int]] = Field(
        default=None,
        title="Mesh Folder Key",
        description="This key will be appended to the mesh folder.",
    )
    solution: Optional[Union[str, int]] = Field(
        default=None,
        title="Solution Folder Key",
        description="This key will be appended to the solution folder.",
    )
    launch_gui: Optional[bool] = Field(
        default=False,
        title="Launch GUI",
        description="If True, the GUI will be launched after the run.",
    )
    overwrite: Optional[bool] = Field(
        default=False,
        title="Overwrite",
        description="If True, the existing folders will be overwritten, otherwise new folders will be created.",
    )
    comments: str = Field(
        default="",
        title="Comments",
        description="Comments for the run. These comments will be saved in the run_log.csv file.",
    )
    verbosity_Gmsh: int = Field(
        default=5,
        title="verbosity_Gmsh",
        description="Level of information printed on the terminal and the message console (0: silent except for fatal errors, 1: +errors, 2: +warnings, 3: +direct, 4: +information, 5: +status, 99: +debug)",
    )
    verbosity_GetDP: int = Field(
        default=5,
        title="verbosity_GetDP",
        description="Level of information printed on the terminal and the message console. Higher number prints more, good options are 5 or 6.",
    )
    verbosity_FiQuS: bool = Field(
        default=True,
        title="verbosity_FiQuS",
        description="Level of information printed on the terminal and the message console by FiQuS. Only True of False for now.",
    )

class General(BaseModel):
    """
        Class for FiQuS general
    """
    magnet_name: Optional[str] = None

class QuenchHeaters(BaseModel):
    """
        Level 3: Class for FiQuS Multipole
    """
    N_strips: Optional[int] = None
    t_trigger: Optional[List[float]] = None
    U0: Optional[List[float]] = None
    C: Optional[List[float]] = None
    R_warm: Optional[List[float]] = None
    w: Optional[List[float]] = None
    h: Optional[List[float]] = None
    h_ins: List[List[float]] = []
    type_ins: List[List[str]] = []
    h_ground_ins: List[List[float]] = []
    type_ground_ins: List[List[str]] = []
    l: Optional[List[float]] = None
    l_copper: Optional[List[float]] = None
    l_stainless_steel: Optional[List[float]] = None
    ids: Optional[List[int]] = None
    turns: Optional[List[int]] = None
    turns_sides: Optional[List[str]] = None

class QuenchProtection(BaseModel):
    """
        Level 2: Class for FiQuS Multipole
    """
    energy_extraction:  EnergyExtraction = EnergyExtraction()
    quench_heaters: QuenchHeaters = QuenchHeaters()
    cliq: CLIQ_Class = CLIQ_Class()
    esc: ESC_Class = ESC_Class()
    e_cliq: E_CLIQ_Class = E_CLIQ_Class()

class DataFiQuS(BaseModel):
    """
        This is data structure of FiQuS Input file
    """
    general: General = General()
    run: RunFiQuS = RunFiQuS()
    magnet: Union[CCT, CWS, Multipole, Pancake3D, CACStrand, CACRutherford] = Field(
        default=Multipole(), discriminator="type"
    )
    circuit: Circuit_Class = Circuit_Class()
    power_supply: PowerSupplyClass = PowerSupplyClass()
    quench_protection: QuenchProtection = QuenchProtection()
    quench_detection: QuenchDetection = QuenchDetection()
    conductors: Dict[str, ConductorFiQuS] = {}
