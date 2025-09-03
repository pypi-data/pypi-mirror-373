from pydantic import BaseModel
from typing import (List, Dict, Optional)

from steam_sdk.data.DataModelCommon import Circuit_Class, PowerSupplyClass, EnergyExtraction


############################
# General parameters
class General(BaseModel):
    """
        Level 1: Class for general information on the case study
    """
    name: Optional[str] = None  # TODO: unused so far
    place: Optional[str] = None  # TODO: unused so far
    date: Optional[str] = None  # TODO: unused so far
    time: Optional[str] = None  # TODO: unused so far (&correct that it is a str?)
    type: Optional[str] = None  # natural quench, provoked discharge, powering cycle
    type_trigger: Optional[str] = None  # TODO: unused so far! & is there a difference between type_trigger and type?
    circuit: Optional[str] = None  # TODO: unused so far
    magnet: Optional[str] = None  # TODO: unused so far
    conductor: Optional[str] = None  # TODO: unused so far
    item: Optional[str] = None  # another measured item that is not circuit, magnet, or conductor   # TODO: unused so far
    state: Optional[str] = None  # occurred, predicted  # TODO: unused so far
    initial_temperature: Optional[str] = None

############################
# Powering
class PoweringClass(BaseModel):
    """
        Level 1: Class for information on the power supply and its current profile
    """
    # initial_current: Optional[str] = None
    current_at_discharge: Optional[str] = None  # TODO: unused so far
    max_dI_dt: Optional[str] = None
    max_dI_dt2: Optional[str] = None
    # custom_powering_cycle: List[List[float]] = [[]]  # optional
    PowerSupply: PowerSupplyClass = PowerSupplyClass()  # TODO t_off, t_control_LUT, I_control_LUT are unused because writing function directly assigns value to sweeper.csv


############################
# Quench Heaters
class QuenchHeaterCircuit(BaseModel):
    """
        Level 2: Class for information on the quench heater circuit
    """
    # N_circuits: Optional[int] = None
    strip_per_circuit: List[int] = []  # TODO unused, writing function takes the argument
    t_trigger: Optional[float] = None
    U0: Optional[float] = None
    C: Optional[float] = None
    R_warm: Optional[float] = None
    R_cold: Optional[float] = None  # TODO unused, writing function calculates it an only assigns it to sweeper.csv
    R_total: Optional[float] = None  # TODO unused, writing function calculates it an only assigns it to sweeper.csv
    L: Optional[float] = None  # TODO totally unused


############################
# CLIQ
class CLIQClass(BaseModel):
    """
        Level 2: Class for information on the CLIQ protection system
    """
    t_trigger: Optional[float] = None
    U0: Optional[float] = None
    C: Optional[float] = None
    R: Optional[float] = None
    L: Optional[float] = None


############################
# Quench protection
class QuenchProtectionClass(BaseModel):
    """
        Level 1: Class for information on the quench protection system
    """
    Energy_Extraction: EnergyExtraction = EnergyExtraction()  # TODO unused so far
    Quench_Heaters: Dict[str, QuenchHeaterCircuit] = {}
    CLIQ: CLIQClass = CLIQClass()
    # FQPLs: FQPLs = FQPLs()


############################
# Quench
class QuenchClass(BaseModel):
    """
        Level 1: Class for information on the quench location
    """
    t_quench: Optional[str] = None
    location_coil: Optional[str] = None
    location_block: Optional[str] = None
    location_turn: Optional[str] = None
    location_half_turn: Optional[str] = None


############################
# Highest level
class DataEventMagnet(BaseModel):
    '''
    **Class for the STEAM magnet event**

    This class contains the data structure of a magnet event analyzed with STEAM_SDK.

    :param GeneralParameters: General information on the case study such as name, date, time, etc.
    :param Circuit: Electrical circuit information for the magnet.
    :param Powering: Information on the power supply and its current profile for the magnet.
    :param QuenchProtection: Information on the quench protection system, including energy extraction, quench heaters, and CLIQ.
    :param Quench: Information on the quench location, including time and location details.
    '''

    GeneralParameters: General = General()
    Circuit: Circuit_Class = Circuit_Class()
    Powering: PoweringClass = PoweringClass()
    QuenchProtection: QuenchProtectionClass = QuenchProtectionClass()
    Quench: QuenchClass = QuenchClass()  # TODO unused so far
