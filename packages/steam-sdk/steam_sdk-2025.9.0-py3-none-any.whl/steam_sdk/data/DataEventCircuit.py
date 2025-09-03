from typing import List, Dict, Optional

from pydantic import BaseModel

############################
# General parameters
class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    name: Optional[str] = None
    place: Optional[str] = None
    date: Optional[str] = None
    period: Optional[str] = None  # for example: "HWC 2021"
    time: Optional[str] = None  # TODO: correct that it is a str?
    state: Optional[str] = None  # occurred, predicted
    circuit_type: Optional[str] = None
    initial_temperature: Optional[str] = None

############################
# Powering
class Powering(BaseModel):
    """
        Level 1: Class for information on the circuit powering
    """
    circuit_name: Optional[str] = None
    circuit_type: Optional[str] = None
    delta_t_FGC_PIC: List[float] = [] # time delay between PIC signal and power supply switching-off signal (FGC)
    current_at_discharge: List[float] = []
    dI_dt_at_discharge: List[float] = []
    plateau_duration: List[float] = []
    cause_FPA: Optional[str] = None


############################
# Energy extraction
class EnergyExtraction(BaseModel):
    delta_t_EE_PIC: Optional[float] = None  # time delay between PIC signal and energy-extraction triggering
    U_EE_max: Optional[float] = None


############################
# Quench event
class QuenchEvent(BaseModel):
    """
        Level 1: Class for information on the quench event occurred in the circuit
        The name of the keys in the QuenchEvent dictionary is the name of the quenched magnet
    """
    quench_cause: Optional[str] = None
    magnet_name: Optional[str] = None  # for example: magnet #23 or magnet Q1
    magnet_electrical_position: Optional[int] = None
    quench_order: Optional[int] = None  # defining in which order multiple quenches occurred
    current_at_quench: List[float] = []
    delta_t_iQPS_PIC: Optional[float] = None  # time delay between PIC signal and "initial" quench detection system (iQPS)
    delta_t_nQPS_PIC: Optional[float] = None  # time delay between PIC signal and "new" quench detection system (nQPS)
    quench_location: Optional[str] = None  # for example: in which aperture the quench occurred
    QDS_trigger_cause: Optional[str] = None
    QDS_trigger_origin: Optional[str] = None
    dU_iQPS_dt: Optional[float] = None
    V_symm_max: Optional[float] = None
    dV_symm_dt: Optional[float] = None


############################
# Highest level
class DataEventCircuit(BaseModel):
    '''
        **Class for the STEAM magnet event**

        This class contains the data structure of a magnet event analyzed with STEAM_SDK.

        :return: DataModelCircuit object
    '''

    GeneralParameters: General = General()
    PoweredCircuits: Dict[str, Powering] = {}
    EnergyExtractionSystem: Dict[str, EnergyExtraction] = {}
    QuenchEvents: Dict[str, QuenchEvent] = {}
