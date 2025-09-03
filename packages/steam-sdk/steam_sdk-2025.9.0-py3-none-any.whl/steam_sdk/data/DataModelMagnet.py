from typing import List, Optional

from pydantic import BaseModel, Field

from steam_sdk.data.DataAPDLCTOptions import APDLCTOptions
from steam_sdk.data.DataConductor import Conductor
from steam_sdk.data.DataFiQuSOptions import FiQuSOptions
from steam_sdk.data.DataLEDETOptions import LEDETOptions
from steam_sdk.data.DataModelCommon import Circuit_Class
from steam_sdk.data.DataModelCommon import PowerSupplyClass
from steam_sdk.data.DataModelCommon import QuenchProtection
from steam_sdk.data.DataProteCCTOptions import PROTECCTOptions
from steam_sdk.data.DataPySIGMAOptions import PySIGMAOptions


############################
# Source files
class SourceFiles(BaseModel):
    """
        Level 1: Class for the source files
    """
    coil_fromROXIE: Optional[str] = Field(
        default=None,
        title='Name of the file',
        description='.data file',
    )
    conductor_fromROXIE: Optional[str] = None  # ROXIE .cadata file
    iron_fromROXIE: Optional[str] = None    # ROXIE .iron file
    BH_fromROXIE: Optional[str] = None      # ROXIE .bhdata file (BH-curves)
    magnetic_field_fromROXIE: Optional[str] = None  # ROXIE .map2d file
    sm_inductance: Optional[str] = None


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
    magnet_name: Optional[str] = None
    circuit_name: Optional[str] = None
    model: Model = Model()
    magnet_type: Optional[str] = None
    T_initial: Optional[float] = None               # T00 (LEDET), Top (SIGMA)
    magnetic_length: Optional[float] = None   # l_magnet (LEDET), magLength (SIGMA), magneticLength (ProteCCT)


############################
# Coil Windings
class CoilWindingsElectricalOrder(BaseModel):
    """
        Level 2: Class for the order of the electrical pairs
    """
    group_together: List[List[int]] = []   # elPairs_GroupTogether
    reversed: List[int] = []         # elPairs_RevElOrder
    overwrite_electrical_order: List[int] = []


class MultipoleWedge(BaseModel):
    """
        Level 3: Class for multi-pole coil data
    """
    material: Optional[str] = None
    RRR: Optional[float] = None
    T_ref_RRR_high: Optional[float] = None


class CoilWindingsMultipole(BaseModel):
    """
        Level 2: Class for multi-pole coil data
    """
    wedges: MultipoleWedge = MultipoleWedge()


class SolenoidCoil(BaseModel):
    """
        Level 3: Class for Solenoid windings
    """
    name: Optional[str] = None            # -             solenoid name
    a1: Optional[float] = None            # m             smaller radial dimension of solenoid
    a2: Optional[float] = None            # m             larger radial dimension of solenoid
    b1: Optional[float] = None            # m             smaller axial dimension of solenoid
    b2: Optional[float] = None            # m             larger axial dimension of solenoid
    conductor_name: Optional[str] = None  # -             wire name - name must correspond to existing conductor name in the same yaml file
    ntpl: Optional[int] = None            # -             number of turns per layer
    nl: Optional[int] = None              # -             number of layers
    pre_preg: Optional[float] = None     # m              Pre-preg thicknes (radial) i.e. in LEDET in width direction
    section: Optional[int] = None         # Section in ledet for the block

class CoilWindingsSolenoid(BaseModel):
    """
        Level 2: Class for Solenoid windings
    """
    coils: List[SolenoidCoil] = [SolenoidCoil()]

class CoilWindingsPancake(BaseModel):
    """
        Level 2: Class for Pancake windings
    """
    tbc: Optional[str] = None

class CoilWindingsCCT_straight(BaseModel):
    """
        Level 2: Class for straight CCT windings
    """
    winding_order: Optional[List[int]] = None
    winding_numberTurnsFormers: Optional[List[int]] = None            # total number of channel turns, ProteCCT: numTurnsPerStrandTotal, FiQuS: n_turnss
    winding_numRowStrands: Optional[List[int]] = None                 # number of rows of strands in channel, ProteCCT: numRowStrands, FiQuS: windings_wwns
    winding_numColumnStrands: Optional[List[int]] = None              # number of columns of strands in channel, ProteCCT: numColumnStrands, FiQuS: windings_whns
    winding_chws: Optional[List[float]] = None                        # width of winding slots, ProteCTT: used to calc. wStrandSlot=winding_chws/numRowStrands, FiQuS: wwws
    winding_chhs: Optional[List[float]] = None                        # width of winding slots, ProteCTT: used to calc. wStrandSlot=winding_chhs/numColumnStrands, FiQuS: wwhs
    former_inner_radiuses: List[float] = []                  # innerRadiusFormers (ProteCCT)
    former_outer_radiuses: List[float] = []                  # innerRadiusFormers (ProteCCT)
    former_RRRs: List[float] = []                   # RRRFormer (ProteCCT)
    #former_thickness_underneath_coil: Optional[float] = None          # formerThicknessUnderneathCoil. Thickness of the former underneath the slot holding the strands in [m] (ProteCCT)
    cylinder_inner_radiuses: List[float] = []              # innerRadiusOuterCylinder (ProteCCT)
    cylinder_outer_radiuses: List[float] = []                  # ProteCCT: thicknessOuterCylinder = cylinder_outer_radiuses - cylinder_inner_radiuses
    cylinder_RRRs: List[float] = []                         # ProteCCT: RRROuterCylinder


class CoilWindingsCCT_curved(BaseModel):
    """
        Level 2: Class for curved CCT windings
    """
    tbc: Optional[str] = None


class Coil_Windings(BaseModel):
    """
        Level 1: Class for winding information
    """
    conductor_to_group: List[int] = []  # This key assigns to each group a conductor of one of the types defined with Conductor.name
    group_to_coil_section: List[int] = []  # This key assigns groups of half-turns to coil sections
    polarities_in_group: List[int] = []  # This key assigns the polarity of the current in each group # TODO: Consider if it is convenient to remove this (and check DictionaryLEDET when you do)
    n_half_turn_in_group: List[int] = []
    half_turn_length: List[float] = []
    electrical_pairs: CoilWindingsElectricalOrder = CoilWindingsElectricalOrder()  # Variables used to calculate half-turn electrical order
    multipole: CoilWindingsMultipole = CoilWindingsMultipole()
    pancake: CoilWindingsPancake = CoilWindingsPancake()
    solenoid: CoilWindingsSolenoid = CoilWindingsSolenoid()
    CCT_straight: CoilWindingsCCT_straight = CoilWindingsCCT_straight()
    CCT_curved: CoilWindingsCCT_curved = CoilWindingsCCT_curved()


class QuenchDetection(BaseModel):
    """
    Level 2: Class for FiQuS
    """

    voltage_thresholds: Optional[List[float]] = Field(
        default=None,
        title="List of quench detection voltage thresholds",
        description="Voltage thresholds for quench detection. The quench detection will be triggered when the voltage exceeds these thresholds continuously for a time larger than the discrimination time.",
    )

    discrimination_times: Optional[List[float]] = Field(
        default=None,
        title="List of quench detection discrimination times",
        description="Discrimination times for quench detection. The quench detection will be triggered when the voltage exceeds the thresholds continuously for a time larger than these discrimination times.",
    )

    voltage_tap_pairs: Optional[List[List[int]]] = Field(
        default=None,
        title="List of quench detection voltage tap pairs",
        description="Voltage tap pairs for quench detection. The voltage difference between these pairs will be used for quench detection.",
    )

############################
# Highest level
class DataModelMagnet(BaseModel):
    """
        **Class for the STEAM inputs**

        This class contains the data structure of STEAM model inputs.

        :return: DataModelMagnet object
    """

    Sources: SourceFiles = SourceFiles()
    GeneralParameters: General = General()
    CoilWindings: Coil_Windings = Coil_Windings()
    Conductors: List[Conductor] = [Conductor(cable={'type': 'Rutherford'}, strand={'type': 'Round'}, Jc_fit={'type': 'CUDI1'})]
    Circuit: Circuit_Class = Circuit_Class()
    Power_Supply: PowerSupplyClass = PowerSupplyClass()
    Quench_Protection: QuenchProtection = QuenchProtection()
    Quench_Detection: QuenchDetection = QuenchDetection()
    Options_APDL_CT: APDLCTOptions = APDLCTOptions()
    Options_FiQuS: FiQuSOptions = FiQuSOptions()
    Options_LEDET: LEDETOptions = LEDETOptions()
    Options_ProteCCT: PROTECCTOptions = PROTECCTOptions()
    Options_SIGMA: PySIGMAOptions = PySIGMAOptions()
