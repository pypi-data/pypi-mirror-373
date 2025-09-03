from pydantic import BaseModel

from typing import List, Dict, Optional


############################
# General parameters
class GeneralParametersClass(BaseModel):
    magnet_name: Optional[str] = None
    circuit_name: Optional[str] = None  # TODO currenty unused
    state: Optional[str] = None  # measured, deduced from short-samples, deduced from design  # TODO currenty unused

############################
# Magnet
class MagnetClass(BaseModel):
    coils: List[str] = []
    measured_inductance_versus_current: List[List[float]] = []   # TODO currenty unused

############################
# Coils
class IcMeasurement(BaseModel):
    """
        Level 1: Class for parameters of a critical current measurement to adjust Jc fit parameters
    """
    Ic: Optional[float] = None
    T_ref_Ic: Optional[float] = None
    B_ref_Ic: Optional[float] = None
    Cu_noCu_sample: Optional[float] = None


class StrandGeometry(BaseModel):
    """
        Level 2: Class for strand geometry
    """
    diameter: Optional[float] = None
    bare_width: Optional[float] = None
    bare_height: Optional[float] = None


class ConductorSample(BaseModel):
    ID: Optional[str] = None  # TODO currenty unused
    Ra: Optional[float] = None
    Rc: Optional[float] = None
    number_of_strands: Optional[int] = None
    bare_cable_width: Optional[float] = None
    bare_cable_height: Optional[float] = None
    strand_twist_pitch: Optional[float] = None
    filament_twist_pitch: Optional[float] = None
    RRR: Optional[float] = None
    Cu_noCu: Optional[float] = None
    # critical current measurement attributes
    Tc0: Optional[float] = None
    Bc20: Optional[float] = None
    f_rho_eff: Optional[float] = None
    Ic_measurements: List[IcMeasurement] = []
    strand_geometry: StrandGeometry = StrandGeometry()


class Coil(BaseModel):
    ID: Optional[str] = None  # TODO currently unused
    cable_ID: Optional[str] = None  # TODO currently unused
    # Resistance measurement attributes
    coil_resistance_room_T: Optional[float] = None
    Cu_noCu_resistance_meas: Optional[float] = None
    B_resistance_meas: Optional[float] = None
    T_ref_coil_resistance: Optional[float] = None
    T_ref_RRR_low: Optional[float] = None  # TODO do i have to write this in modelData? there would be such an entry
    T_ref_RRR_high: Optional[float] = None
    # list of conductor samples and weight factor
    conductorSamples: List[ConductorSample] = []
    weight_factors: List[float] = []


class DataParsimConductor(BaseModel):
    '''
        **Class for the STEAM conductor**

        This class contains the data structure of a Conductor parsim  analyzed with STEAM_SDK.

        :return: DataParsimConductor object
    '''

    GeneralParameters: GeneralParametersClass = GeneralParametersClass()
    Magnet: MagnetClass = MagnetClass()
    Coils: Dict[str, Coil] = {}  # Datastructure representing one row in the csv file
