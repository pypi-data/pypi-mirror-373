from pydantic import BaseModel, Field

from typing import List, Union, Optional, Literal


############################
# Circuit
class Circuit_Class(BaseModel):
    """
        Level 1: Class for the circuit parameters
    """
    R_circuit: Optional[float] = None             # R_circuit
    L_circuit: Optional[float] = None             # Lcir (SIGMA)
    R_parallel: Optional[float] = None

 
############################
# Power Supply (aka Power Converter)
class PowerSupplyClass(BaseModel):
    """
        Level 1: Class for the power supply (aka power converter)
    """
    I_initial: Optional[float] = Field(
        default=None,
        description="Initial current in the magnet. Propagated differently in various tools and obsolete # I00 (LEDET), I_0 (SIGMA), I0 (BBQ)")
    t_off: Optional[float] = Field(
        default=None,
        description="Time of switching off the switch next to current controlled source. t_PC (LEDET)")
    t_control_LUT: List[float] = Field(
        default=[],
        description="List of time values [s] for linear piece wise time function of current controlled source. t_PC_LUT (LEDET)")
    I_control_LUT: List[float] = Field(
        default=[],
        description="List of current values [A] for linear piece wise time function of current controlled source. I_PC_LUT (LEDET)")
    R_crowbar: Optional[float] = Field(
        default=None,
        description="Crowbar resistance in forward direction [Ohm]. Rcrow (SIGMA), RCrowbar (ProteCCT)")
    L_crowbar: Optional[float] = Field(
        default=None,
        description="Crowbar inductance in forward direction [H].")
    Ud_crowbar: Optional[float] = Field(
        default=None,
        description="Crowbar diode voltage in forward direction [V].")
    R_c_r: Optional[float] = Field(
        default=None,
        description="Crowbar resistance in reverse direction [Ohm].")
    L_c_r: Optional[float] = Field(
        default=None,
        description="Crowbar inductance in reverse direction [H].")
    Ud_c_r: Optional[float] = Field(
        default=None,
        description="Crowbar diode voltage in reverse direction [V].")
    R_1: Optional[float] = Field(
        default=None,
        description="Resistance R1 [Ohm].")
    L_1: Optional[float] = Field(
        default=None,
        description="Inductance L1 [H].")
    R_2: Optional[float] = Field(
        default=None,
        description="Resistance R2 [Ohm].")
    L_2: Optional[float] = Field(
        default=None,
        description="Inductance L2 [H].")
    C: Optional[float] = Field(
        default=None,
        description="Capacitance C [F].")
    R_3: Optional[float] = Field(
        default=None,
        description="Resistance R3 [Ohm].")
    L_3: Optional[float] = Field(
        default=None,
        description="Inductance L3 [H].")

############################
# Quench Protection
class EnergyExtraction(BaseModel):
    """
        Level 2: Class for the energy extraction parameters
    """
    t_trigger: Optional[float] = Field(
        default=None,
        description="Trigger time on the positive lead [s]. tEE (LEDET), tSwitchDelay (ProteCCT)")
    R_EE: Optional[Union[float, list]] = Field(
        default=None,
        description="When it is a scalar: Resistance of the energy-extraction system, or constant in the varistor equation [Ohm]. When it is a list: Parameters of the polynomial fit used to calculate the resistance. The equivalent EE resistance depends on the integrated energy deposited in the EE and will be calculated as: R_EE(t)=f(min(R_EE_initial_energy+integral(R_EE(t)*Ia(t)^2,dt),R_EE_max_energy)*abs(Ia(t))^R_EE_power, where f is a polynomial function with parameters R_EE (ordered from lowest to highest order), R_EE_initial_energy is the initial energy in the EE element (from previous tests) and R_EE_max_energy is the maximum value of dissipated energy considered in the fit (to bound the polynomial fit).")
    power_R_EE: Optional[float] = Field(
        default=None,
        description="Varistor power component. If different from 0, energy-extraction system will be based on a varistor with equivalent resistance R_EE(t)=R_EE*abs(Ia_t)^R_EE_power [-]. Note: If the variable R_EE is defined as a list, read the R_EE description to see how R_EE(t) is calculated.")
    initial_energy: Optional[float] = Field(
        default=None,
        description="If the variable R_EE is defined as a vector, read the R_EE description to see how R_EE(t) is calculated. If the variable R_EE is defined as a vector, this variable is ignored.")
    max_energy: Optional[float] = Field(
        default=None,
        description="If the variable R_EE is defined as a vector, read the R_EE description to see how R_EE(t) is calculated. If the variable R_EE is defined as a vector, this variable is ignored.")
    L: Optional[float] = Field(
        default=None,
        description="Inductance in series with resistor on the positive lead [H].")
    C: Optional[float] = Field(
        default=None,
        description="Snubber capacitance in parallel to the EE switch on the positive lead [F].")
    L_c: Optional[float] = Field(
        default=None,
        description="Inductance in the snubber capacitance branch in parallel to the EE switch on the positive lead [H].")
    R_c: Optional[float] = Field(
        default=None,
        description="Resistance in the snubber capacitance branch in parallel to the EE switch on the positive lead [Ohm].")
    Ud_snubber: Optional[float] = Field(
        default=None,
        description="Forward voltage of diode in the snubber capacitance branch in parallel to the EE switch on the positive lead [V].")
    L_s: Optional[float] = Field(
        default=None,
        description="Inductance in the EE switch branch on the positive lead [H].")
    R_s: Optional[float] = Field(
        default=None,
        description="Resistance in the EE switch branch on the positive lead [Ohm].")
    Ud_switch: Optional[float] = Field(
        default=None,
        description="Forward voltage of diode in the EE switch branch on the positive lead [V].")

    t_trigger_n: Optional[float] = Field(
        default=None,
        description="Trigger time on the negative lead [s]. tEE (LEDET), tSwitchDelay (ProteCCT)")
    R_EE_n: Optional[float] = Field(
        default=None,
        description="Energy extraction resistance on the negative lead [Ohm]. R_EE_triggered (ProteCCT)")
    power_R_EE_n: Optional[float] = Field(
        default=None,
        description="Varistor power component, R(I) = R_EE*abs(I)^power_R_EE on the negative lead [-]. RDumpPower (ProteCCT)")
    L_n: Optional[float] = Field(
        default=None,
        description="Inductance in series with resistor on the negative lead [H].")
    C_n: Optional[float] = Field(
        default=None,
        description="Snubber capacitance in parallel to the EE switch on the negative lead [F].")
    L_c_n: Optional[float] = Field(
        default=None,
        description="Inductance in the snubber capacitance branch in parallel to the EE switch on the negative lead [H].")
    R_c_n: Optional[float] = Field(
        default=None,
        description="Resistance in the snubber capacitance branch in parallel to the EE switch on the negative lead [Ohm].")
    Ud_snubber_n: Optional[float] = Field(
        default=None,
        description="Forward voltage of diode in the snubber capacitance branch in parallel to the EE switch on the negative lead [V].")
    L_s_n: Optional[float] = Field(
        default=None,
        description="Inductance in the EE switch branch on the negative lead [H].")
    R_s_n: Optional[float] = Field(
        default=None,
        description="Resistance in the EE switch branch on the negative lead [Ohm].")
    Ud_switch_n: Optional[float] = Field(
        default=None,
        description="Forward voltage of diode in the EE switch branch on the negative lead [V].")


class QuenchHeater(BaseModel):
    """
        Level 2: Class for the quench heater parameters
    """
    N_strips: Optional[int] = Field(
        default=None,
        description="Number of quench heater traces (typically 2 traces make one pad)")
    t_trigger: List[float] = Field(
        default=[],
        description="Trigger times list of of quench heaters [s]")
    U0: List[float] = Field(
        default=[],
        description="Initial charging voltages list of capacitor for the trance (not full pad!) [V]")
    C: List[float] = Field(
        default=[],
        description="Capacitances list of quench heater power supply for the trance (not full pad!) [H]")
    R_warm: List[float] = Field(
        default=[],
        description="Internal resistances list of quench heater power supply and/or additional resistance added to limit the heater current for the trance (not full pad!) [Ohm]")
    w: List[float] = Field(
        default=[],
        description="Widths list of quench heater trance stainless steel part [m]")
    h: List[float] = Field(
        default=[],
        description="Thickness list of quench heater trance stainless steel part [m]")
    s_ins: Union[List[float], List[List[float]]] = Field(
        default=[],
        description="Thickness list of quench heater insulation between the stainless steel part and conductor insulation [m]"
                    "This could be a list of list to specify multiple material thicknesses")
    type_ins: Union[List[str], List[List[str]]] = Field(
        default=[],
        description="Material names list of quench heater insulation between the stainless steel part and conductor insulation [-]"
                    "This could be a list of list to specify multiple material names")
    s_ins_He: Union[List[float], List[List[float]]] = Field(
        default=[],
        description="Material names list of quench heater insulation between the stainless steel part and helium bath [-]"
                    "This could be a list of list to specify multiple material thicknesses")
    type_ins_He: Union[List[str], List[List[str]]] = Field(
        default=[],
        description="Material names list of quench heater insulation between the stainless steel part and helium bath [-]"
                    "This could be a list of list to specify multiple material names")
    l: List[float] = Field(
        default=[],
        description="Lengths list of quench heaters [m]. Typically equal to magnet length.")
    l_copper: List[float] = Field(
        default=[],
        description="Lengths list of copper laminations of quench heaters [m].")
    l_stainless_steel: List[float] = Field(
        default=[],
        description="Lengths list of stainless steel only sections of quench heaters [m].")
    f_cover: List[float] = Field(
        default=[],
        description="List of fraction of stainless steel cover. This is l_stainless_steel/(l_stainless_steel+l_copper). Marked as obsolete, but still specified in some models [-].")
    iQH_toHalfTurn_From: List[int] = Field(
        default=[],
        description="List of heater numbers (1 based) equal to the length of turns that are covered by (i.e. thermally connected to) quench heaters.")
    iQH_toHalfTurn_To: List[int] = Field(
        default=[],
        description="List of turn numbers (1 based) that are covered by (i.e. thermally connected to) quench heaters.")
    turns_sides: List[str] = Field(
        default=[],
        description="List of letters specifying side of turn where quench heater is placed. Only used in FiQuS Multipole module."
                    "Possible sides are: 'o' - outer, 'i' - inner, 'l' - lower angle, 'h' - higher angle.")


class CLIQ_Class(BaseModel):
    """
        Level 2: Class for the CLIQ parameters
    """
    t_trigger: Optional[float] = Field(
        default=None,
        description="Trigger time of CLIQ unit [s].")
    current_direction: List[int] = Field(
        default=[],
        description="Polarity of current in groups specified as a list with length equal to the number of groups [-].")
    sym_factor: Optional[float] = Field(
        default=None,
        description="Obsolete.")
    N_units: Optional[int] = Field(
        default=None,
        description="Obsolete.")
    U0: Optional[float] = Field(
        default=None,
        description="Initial charging voltage of CLIQ unit [V].")
    C: Optional[float] = Field(
        default=None,
        description="Capacitance of CLIQ unit [F].")
    R: Optional[float] = Field(
        default=None,
        description="Resistance of CLIQ unit [Ohm].")
    L: Optional[float] = Field(
        default=None,
        description="Inductance of CLIQ unit [H].")
    I0: Optional[float] = Field(
        default=None,
        description="Obsolete.")


class ESC_Class(BaseModel):
    """
        Level 2: Class for the ESC parameters
    """
    t_trigger: List[float] = Field(
        default=[],
        description="Trigger time of ESC units [s] given as a list with length corresponding to the number of ESC units.")
    U0: List[float] = Field(
        default=[],
        description="Initial charging voltage of ESC units [V] given as a list with length corresponding to the number of ESC units."
                    "The unit is grounded in the middle, so the voltage to ground is half of this value")
    C: List[float] = Field(
        default=[],
        description="Capacitance of ESC units [F] given as a list with length corresponding to the number of ESC units."
                    "The unit is grounded in the middle, with two capacitors in series with value of 2C")
    L: List[float] = Field(
        default=[],
        description="Parasitic inductance of ESC units [H] given as a list with length corresponding to the number of ESC units."
                    "The unit is grounded in the middle, with two capacitors in series with value of 2C")
    R_unit: List[float] = Field(
        default=[],
        description="Internal resistance of ESC units [Ohm] given as a list with length corresponding to the number of ESC units.")
    R_leads: List[float] = Field(
        default=[],
        description="Resistance of leads from ESC coil to ESC diode connections [Ohm] given as a list with length corresponding to the number of ESC units.")
    Ud_Diode: List[float] = Field(
        default=[],
        description="Forward diodes voltage across ESC coils [V] given as a list with length corresponding to the number of ESC units.")
    L_Diode: List[float] = Field(
        default=[],
        description="Inductance in series with diodes across ESC coils [V] given as a list with length corresponding to the number of ESC units.")


class FQPCs_Class(BaseModel):
    """
        Level 2: Class for the FQPLs parameters for protection
    """
    enabled: Optional[List[bool]] = Field(
        default=None,
        description="List of booleans specifying which FQPC is enabled.")
    names: Optional[List[str]] = Field(
        default=None,
        description="List of names to use in gmsh and getdp. Any unique ASCII strings would work")
    fndpls: Optional[List[int]] = Field(
        default=None,
        description="List of FQPC number of divisions per length at geometry level [-]")
    fwws: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC wire widths (assuming rectangular). For theta = 0 this is x dimension. Works at geometry level [-]")
    fwhs: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC wire heights (assuming rectangular). For theta = 0 this is y dimension. Works at geometry level [-]")
    r_ins: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC inner diameter of (e.g. for CCT magnet). For theta = 0 this is x dimension. Works at geometry level [-]")
    r_bs: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC radiuses for bending the fqpl by 180 degrees at the end of the magnet to go backward. Works at geometry level [-]")
    n_sbs: Optional[List[int]] = Field(
        default=None,
        description="List of FQPC number of 'bending segments' for the 180 degrees turn. Works at geometry level [-]")
    thetas: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC rotation in deg from x+ axis towards y+ axis about z axis. Works at geometry level [-]")
    z_starts: Optional[List[str]] = Field(
        default=None,
        description="List of z coordinates for the air boundary to start at. These are string with either: z_min or z_max key from the Air region. Works at geometry level [-]")
    z_ends: Optional[List[float]] = Field(
        default=None,
        description="List of z coordinates for the air boundary to end at. These are string with either: z_min or z_max key from the Air region. Works at geometry level [-]")
    currents: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC currents for a magnetostatic solution. Works at solve level [-]")
    sigmas: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC electrical conductivity for a magnetostatic solution. Works at solve level [-]")
    mu_rs: Optional[List[float]] = Field(
        default=None,
        description="List of FQPC magnetic permeability  for a magnetostatic solution. Works at solve level [-]")
    th_conns_def: Optional[List[List]] = Field(
        default=None,
        description="List of lists specifying thermal connections for LEDET to connect the FQPCs to the other turns of the magnet")

class SourceSine(BaseModel):
    """
    Level 3: Class for Sine source parameters for E-CLIQ
    """
    frequency: Optional[float] = Field(default=None, description="Frequency of the sine source (Hz).")
    current_amplitude: Optional[float] = Field(default=None, description="Amplitude of the sine current (A).")
    number_of_periods: Optional[float] = Field(default=None, description="Amplitude of the sine current (A).")

class SourcePiecewise(BaseModel):
    """
    Level 3 Class for piecewise (linear) source parameters for E-CLIQ
    """
    csv_file: Optional[str] = Field(default=None, description="File name for the from_file source type defining the time evolution of current. Multipliers are used for each of them. The file should contain two columns: 'time' (s) and 'current' (A), with these headers. If this field is set, times and currents are ignored.")
    times: Optional[List[float]] = Field(default=None, description="Time instants (s) defining the piecewise linear sources. Used only if source_csv_file is not set. Can be scaled by time_multiplier.")
    currents: Optional[List[float]] = Field(default=None, description="E-CLIQ coil currents relative to current_multiplier at the time instants 'times'. Used only if source_csv_file is not set.")
    time_multiplier: Optional[float] = Field(default=None, description="Multiplier for the time values in times (scales the time values). Also used for the time values in the source_csv_file.")
    current_multiplier: Optional[float] = Field(default=None, description="Multiplier for the E-CLIQ coil currents in currents. Also used for the values in the source_csv_file.")

class E_CLIQ_Class(BaseModel):
    """
        Level 2: Class for the E-CLIQ parameters for protection
    """
    t_trigger: Optional[List[float]] = Field(
        default=None,
        description="Trigger time of E-CLIQ current sources [s] given as a list with length corresponding to the number of E-CLIQ units.")
    R_leads: Optional[List[float]] = Field(
        default=None,
        description="List of E-CLIQ unit lead resistances [Ohm]. List length corresponding to the number of E-CLIQ units.")
    L_leads: Optional[List[float]] = Field(
        default=None,
        description="List of E-CLIQ unit lead inductances [H]. List length corresponding to the number of E-CLIQ units.")
    source_type: Literal['sine', 'piecewise', None] = Field(
        default=None,
        description="Time evolution of applied current. Supported options are: sine, piecewise.")
    sine: SourceSine = Field(
        default=SourceSine(),
        description="Definition of sine current source parameters.")
    piecewise: SourcePiecewise = Field(
        default=SourcePiecewise(),
        description="Definition of piecewise current source parameters.")

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

class QuenchProtection(BaseModel):
    """
        Level 1: Class for quench protection
    """
    Energy_Extraction: EnergyExtraction = EnergyExtraction()
    Quench_Heaters: QuenchHeater = QuenchHeater()
    CLIQ: CLIQ_Class = CLIQ_Class()
    ESC: ESC_Class = ESC_Class()
    FQPCs: FQPCs_Class = FQPCs_Class()
    E_CLIQ: E_CLIQ_Class = E_CLIQ_Class()
