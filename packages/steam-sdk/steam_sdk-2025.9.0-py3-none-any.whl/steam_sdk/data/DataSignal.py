from pydantic import BaseModel, PrivateAttr
from typing import Dict, List, Optional


############################
# Signals
class Signal(BaseModel):
    """
        Level 2: Class for Configuration options
        - Each Signal is either measured, simulated, or measured+simulated comparison.
        - Each signal is obtained by summing together existing original signals (for example: summing voltage taps to obtain voltages across coil sections)
        - Multipliers can be defined to modify the original signal (for example: changing polarity, applying a gain)
        - The Signal is obtained with the cross product of original signals and multipliers
          (for example: If meas_signals_to_add=[V1, V2] and  meas_multipliers: [+2, -0.001] the defined signal will be V1*2-0.001*V2)

        Note: Meas = Measurement and Sim = simulation

        unit: Physical units of the signal (the same for meas and sim)
        meas_label: Label of the measured signal
        meas_time_vector: Name of the time vector variable for the measurement signal
        meas_signals_to_add: List of original signals to sum together to define a signal
        meas_multipliers: List of multipliers for the measured signals
        sim_label: Label of the simulated signal
        sim_time_vector: Name of the time vector variable for the simulation signal
        sim_signals_to_add: List of original signals to sum together to define a signal
        sim_multipliers: List of multipliers for the simulated signals
    """
    # name: Optional[str] = None  # or name_suffix, or name_prefix, t.b.d.

    meas_label: Optional[str] = None
    meas_signals_to_add_x: List[str] = []
    meas_multipliers_x: List[float] = []
    meas_offsets_x: List[float] = []
    meas_signals_to_add_y: List[str] = []
    meas_multipliers_y: List[float] = []
    meas_offsets_y: List[float] = []

    sim_label: Optional[str] = None
    sim_signals_to_add_x: List[str] = []
    sim_multipliers_x: List[float] = []
    sim_offsets_x: List[float] = []
    sim_signals_to_add_y: List[str] = []
    sim_multipliers_y: List[float] = []
    sim_offsets_y: List[float] = []

    fig_title: Optional[str] = None
    fig_label_x: Optional[str] = None
    fig_label_y: Optional[str] = None
    fig_range_x: List[float] = []
    fig_range_y: List[float] = []
    fig_range_x_relative_to_t_PC_off: List[float] = []

############################
# Configuration
class Configuration(BaseModel):
    """
        Level 1: Class for Configuration options

        configuration_name: Name of the defined configuration (it will be called by the software)
        SignalList: List of defined signals (they could be measured, simulated, or measured+simulated comparison)

    """
    # SignalList: List[Signal] = [Signal(), Signal()]
    SignalList: Dict[str, Signal] = {None: Signal()}


############################
# Highest level
class DataSignal(BaseModel):
    '''
        **Class for the defining configuration of measured and simulated signals**

        This class contains the data structure of signals.

        :return: DataSignal object
    '''

    ConfigurationList: Dict[str, Configuration] = {None: Configuration()}
