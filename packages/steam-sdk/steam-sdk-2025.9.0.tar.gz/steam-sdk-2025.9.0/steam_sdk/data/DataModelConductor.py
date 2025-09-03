from pydantic import BaseModel
from typing import List, Optional

from steam_sdk.data.DataConductor import Conductor
from steam_sdk.data.DataModelMagnet import Circuit_Class, PowerSupplyClass, QuenchProtection, LEDETOptions


############################
# Source files
class SourceFiles(BaseModel):
    """
        Level 1: Class for the source files
    """
    magnetic_field_fromROXIE: Optional[str] = None  # ROXIE .map2d file


############################
# General parameters
class Model(BaseModel):
    """
        Level 2: Class for information on the model
    """
    name: Optional[str] = None  # magnetIdentifier (ProteCCT)
    version: Optional[str] = None
    case: Optional[str] = None
    state: Optional[str] = None


class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    conductor_name: Optional[str] = None
    model: Model = Model()
    material_database_path: Optional[str] = None
    T_initial: Optional[float] = None
    length_busbar: Optional[float] = None

############################
# Conductor geometry


############################
# BBQ options
class GeometryBBQ(BaseModel):
    """
        Level 2: Class for geometry options in BBQ
    """
    thInsul: Optional[float] = None


class SimulationBBQ(BaseModel):
    """
        Level 2: Class for simulation options in BBQ
    """
    meshSize: Optional[float] = None


class PhysicsBBQ(BaseModel):
    """
        Level 2: Class for physics options in BBQ
    """
    adiabaticZoneLength: Optional[float] = None
    aFilmBoilingHeliumII: Optional[float] = None
    aKap: Optional[float] = None
    BBackground: Optional[float] = None
    BPerI: Optional[float] = None
    IDesign: Optional[float] = None
    jointLength: Optional[float] = None
    jointResistancePerMeter: Optional[float] = None
    muTInit: Optional[float] = None
    nKap: Optional[float] = None
    QKapLimit: Optional[float] = None
    Rjoint: Optional[float] = None
    symmetryFactor: Optional[float] = None
    tauDecay: Optional[float] = None
    TInitMax: Optional[float] = None
    TInitOp: Optional[float] = None
    TLimit: Optional[float] = None
    tValidation: Optional[float] = None
    TVQRef: Optional[float] = None
    VThreshold: Optional[float] = None
    withCoolingToBath: Optional[float] = None


class QuenchInitializationBBQ(BaseModel):
    """
        Level 2: Class for quench initialization parameters in BBQ
    """
    sigmaTInit: Optional[float] = None


class BBQ(BaseModel):
    """
        Level 1: Class for BBQ options
    """
    geometry: GeometryBBQ = GeometryBBQ()
    simulation: SimulationBBQ = SimulationBBQ()
    physics: PhysicsBBQ = PhysicsBBQ()
    quench_initialization: QuenchInitializationBBQ = QuenchInitializationBBQ()


############################
# PyBBQ options
class GeometryPyBBQ(BaseModel):
    """
        Level 2: Class for geometry options in PyBBQ
    """
    thInsul: Optional[float] = None
    tapetype: Optional[str] = None


class MagneticFieldPyBBQ(BaseModel):
    """
        Level 1: Class for magnetic-field options in PyBBQ
    """
    Calc_b_from_geometry: Optional[bool] = None
    Background_Bx: Optional[float] = None
    Background_By: Optional[float] = None
    Background_Bz: Optional[float] = None
    Self_Field: Optional[float] = None
    B0_dump: Optional[bool] = None


class SimulationPyBBQ(BaseModel):
    """
        Level 2: Class for simulation options in PyBBQ
    """
    meshSize: Optional[float] = None
    layers: Optional[int] = None
    output: Optional[bool] = None
    dt: Optional[float] = None
    t0: List[float] = []
    posref: List[float] = []
    print_every: Optional[int] = None
    store_every: Optional[int] = None
    plot_every: Optional[int] = None
    uniquify_path: Optional[bool] = None

class PhysicsPyBBQ(BaseModel):
    """
        Level 2: Class for physics options in PyBBQ
    """
    adiabaticZoneLength: Optional[float] = None
    aFilmBoilingHeliumII: Optional[float] = None
    aKap: Optional[float] = None
    BBackground: Optional[float] = None
    BPerI: Optional[float] = None
    Heating_mode: Optional[str] = None
    Heating_nodes: Optional[List[int]] = None
    Heating_time: Optional[float] = None
    Heating_time_constant: Optional[float] = None
    IDesign: Optional[float] = None
    Jc_4K_5T_NbTi: Optional[float] = None
    jointLength: Optional[float] = None
    jointResistancePerMeter: Optional[float] = None
    muTInit: Optional[float] = None
    nKap: Optional[float] = None
    Power: Optional[float] = None
    QKapLimit: Optional[float] = None
    Rjoint: Optional[float] = None
    symmetryFactor: Optional[float] = None
    tauDecay: Optional[float] = None
    TInitMax: Optional[float] = None
    TLimit: Optional[float] = None
    tValidation: Optional[float] = None
    TVQRef: Optional[float] = None
    VThreshold: Optional[float] = None
    wetted_p: Optional[float] = None
    withCoolingToBath: Optional[bool] = None
    withCoolingInternal: Optional[bool] = None


class QuenchInitializationPyBBQ(BaseModel):
    """
        Level 2: Class for quench initialization parameters in PyBBQ
    """
    sigmaTInit: Optional[float] = None

class PyBBQ(BaseModel):
    """
        Level 1: Class for PyBBQ options
    """
    geometry: GeometryPyBBQ = GeometryPyBBQ()
    magnetic_field: MagneticFieldPyBBQ = MagneticFieldPyBBQ()
    simulation: SimulationPyBBQ = SimulationPyBBQ()
    physics: PhysicsPyBBQ = PhysicsPyBBQ()
    quench_initialization: QuenchInitializationPyBBQ = QuenchInitializationPyBBQ()



############################
# Highest level
class DataModelConductor(BaseModel):
    '''
        **Class for the STEAM inputs**

        This class contains the data structure of STEAM model inputs.

        :param N: test 1
        :type N: int
        :param n: test 2
        :type n: int

        :return: DataModelMagnet object
    '''

    Sources: SourceFiles = SourceFiles()
    GeneralParameters: General = General()
    Conductors: List[Conductor] = [Conductor(cable={'type': 'Rutherford'}, strand={'type': 'Round'}, Jc_fit={'type': 'CUDI1'})]
    Circuit: Circuit_Class = Circuit_Class()
    Power_Supply: PowerSupplyClass = PowerSupplyClass()
    Quench_Protection: QuenchProtection = QuenchProtection()
    Options_BBQ: BBQ = BBQ()
    Options_LEDET: LEDETOptions = LEDETOptions()
    Options_PyBBQ: PyBBQ = PyBBQ()
