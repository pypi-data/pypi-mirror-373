from pydantic import BaseModel
from typing import Union, Literal, Optional

# This dataclass is used both by DataModelConductor and DataModelMagnet

class Ic_A_NbTi(BaseModel):
    """
    Level 3: Class for setting IcNbTi fit
    """
    type: Literal["Ic_A_NbTi"]
    Jc_5T_4_2K: Optional[float] = None  # [A/m^2]

class ConstantJc(BaseModel):
    """
        Level 3: Class for setting constant Jc
    """
    type: Literal['Constant Jc']
    Jc_constant: Optional[float] = None  # [A/m^2]


class Bottura(BaseModel):
    """
        Level 3: Class for setting Bottura fit
    """
    type: Literal['Bottura']
    Tc0_Bottura: Optional[float] = None  # [K]
    Bc20_Bottura: Optional[float] = None  # [T]
    Jc_ref_Bottura: Optional[float] = None  # [A/m^2]
    C0_Bottura: Optional[float] = None  # [-]
    alpha_Bottura: Optional[float] = None  # [-]
    beta_Bottura: Optional[float] = None  # [-]
    gamma_Bottura: Optional[float] = None  # [-]


class CUDI1(BaseModel):
    """
        Level 3: Class for Nb-Ti fit based on "Fit 1" in CUDI manual
    """
    type: Literal['CUDI1']
    Tc0_CUDI1: Optional[float] = None  # [K]
    Bc20_CUDI1: Optional[float] = None  # [T]
    C1_CUDI1: Optional[float] = None  # [A]
    C2_CUDI1: Optional[float] = None  # [A/T]


class CUDI3(BaseModel):
    """
        Level 3: Class for Nb-Ti fit based on "Fit 3" in CUDI manual
    """
    type: Literal['CUDI3']
    Tc0_CUDI3: Optional[float] = None  # [K]
    Bc20_CUDI3: Optional[float] = None  # [T]
    c1_CUDI3: Optional[float] = None  # [-]
    c2_CUDI3: Optional[float] = None  # [-]
    c3_CUDI3: Optional[float] = None  # [-]
    c4_CUDI3: Optional[float] = None  # [-]
    c5_CUDI3: Optional[float] = None  # [-]
    c6_CUDI3: Optional[float] = None  # [-]


class Summers(BaseModel):
    """
        Level 3: Class for cable Summer's Nb3Sn fit
    """
    type: Literal['Summers']
    Tc0_Summers: Optional[float] = None  # [K]
    Bc20_Summers: Optional[float] = None  # [T]
    Jc0_Summers: Optional[float] = None  # [A*T^0.5/m^2]


class Bordini(BaseModel):
    """
        Level 3: Class for cable Bordini's Nb3Sn fit
    """
    type: Literal['Bordini']
    Tc0_Bordini: Optional[float] = None  # [K]
    Bc20_Bordini: Optional[float] = None  # [T]
    C0_Bordini: Optional[float] = None  # [A*T/m^2]
    alpha_Bordini: Optional[float] = None  # [-]


class BSCCO_2212_LBNL(BaseModel):
    """
        Level 3: Class for cable Bi-2212 fit developed in LBNL
    """
    # only ad-hoc fit [T. Shen, D. Davis, E. Ravaioli with LBNL, Berkeley, CA]
    type: Literal['BSCCO_2212_LBNL']
    f_scaling_Jc_BSCCO2212: Optional[float] = None  # [-] used for the ad-hoc fit


# ------------------- Cable types ---------------------------#
class Mono(BaseModel):
    """
        Mono cable type: This is basically type of cable consisting of one strand - not really a cable
    """
    type: Literal['Mono']
    bare_cable_width: Optional[float] = None
    bare_cable_height_low: Optional[float] = None
    bare_cable_height_high: Optional[float] = None
    bare_cable_height_mean: Optional[float] = None
    th_insulation_along_width: Optional[float] = None
    th_insulation_along_height: Optional[float] = None
    # Fractions given with respect to the insulated conductor
    f_superconductor: Optional[float] = None
    f_stabilizer: Optional[float] = None  # (related to CuFraction in ProteCCT)
    f_insulation: Optional[float] = None
    f_inner_voids: Optional[float] = None
    f_outer_voids: Optional[float] = None
    # Available materials depend on the component and on the selected program
    material_insulation: Optional[str] = None
    material_inner_voids: Optional[str] = None
    material_outer_voids: Optional[str] = None


class Rutherford(BaseModel):
    """
        Rutherford cable type: for example LHC MB magnet cable
    """
    type: Literal['Rutherford']
    n_strands: Optional[int] = None
    n_strand_layers: Optional[int] = None
    n_strands_per_layers: Optional[int] = None
    bare_cable_width: Optional[float] = None
    bare_cable_height_low: Optional[float] = None
    bare_cable_height_high: Optional[float] = None
    bare_cable_height_mean: Optional[float] = None
    th_insulation_along_width: Optional[float] = None
    th_insulation_along_height: Optional[float] = None
    width_core: Optional[float] = None
    height_core: Optional[float] = None
    strand_twist_pitch: Optional[float] = None
    strand_twist_pitch_angle: Optional[float] = None
    Rc: Optional[float] = None
    Ra: Optional[float] = None
    # Fractions given with respect to the insulated conductor
    f_superconductor: Optional[float] = None
    f_stabilizer: Optional[float] = None  # (related to CuFraction in ProteCCT)
    f_insulation: Optional[float] = None
    f_inner_voids: Optional[float] = None
    f_outer_voids: Optional[float] = None
    f_core: Optional[float] = None
    # Available materials depend on the component and on the selected program
    material_insulation: Optional[str] = None
    material_inner_voids: Optional[str] = None
    material_outer_voids: Optional[str] = None
    material_core: Optional[str] = None


class Ribbon(BaseModel):
    """
        Ribbon cable type: This is basically type of cable consisting of one strand - not really a cable # TODO copy error, this is not MONO
    """
    type: Literal['Ribbon']
    n_strands: Optional[int] = None  # This defines the number of "strands" in the ribbon cable, which are physically glued but electrically in series
    bare_cable_width: Optional[float] = None  # refers to the strand width (rectangular) or diameter (round)
    bare_cable_height_low: Optional[float] = None
    bare_cable_height_high: Optional[float] = None
    bare_cable_height_mean: Optional[float] = None
    th_insulation_along_width: Optional[float] = None  # This defines the thickness of the insulation around each strand (DIFFERENT FROM ROXIE CADATA FILE)
    th_insulation_along_height: Optional[float] = None  # This defines the thickness of the insulation around each strand (DIFFERENT FROM ROXIE CADATA FILE)
    # Fractions given with respect to the insulated conductor
    f_superconductor: Optional[float] = None
    f_stabilizer: Optional[float] = None  # (related to CuFraction in ProteCCT)
    f_insulation: Optional[float] = None
    f_inner_voids: Optional[float] = None
    f_outer_voids: Optional[float] = None
    f_core: Optional[float] = None
    # Available materials depend on the component and on the selected program
    material_insulation: Optional[str] = None
    material_inner_voids: Optional[str] = None
    material_outer_voids: Optional[str] = None
    material_core: Optional[str] = None


# ------------------- Conductors ---------------------------#

class Round(BaseModel):
    """
        Level 2: Class for strand parameters
    """
    type: Literal['Round']
    diameter: Optional[float] = None  # ds_inGroup (LEDET), DConductor (BBQ), DStrand (ProteCCT)
    diameter_core:  Optional[float] = None  # dcore_inGroup (LEDET)
    diameter_filamentary:  Optional[float] = None  # dfilamentary_inGroup (LEDET)
    Cu_noCu_in_strand: Optional[float] = None
    RRR: Optional[float] = None  # RRR_Cu_inGroup (LEDET), RRRStrand (ProteCCT)
    T_ref_RRR_high: Optional[float] = None  # TupRRR (SIGMA), Reference temperature for RRR measurements
    T_ref_RRR_low: Optional[float] = None  # CURRENTLY NOT USED
    fil_twist_pitch: Optional[float] = None
    f_Rho_effective: Optional[float] = None
    material_superconductor: Optional[str] = None
    n_value_superconductor: Optional[float] = None
    ec_superconductor: Optional[float] = None
    material_stabilizer: Optional[str] = None
    rho_material_stabilizer: Optional[Union[str, float]] = None # Material function for resistivity of the stabilizer. Constant resistivity can be given as float.
    filament_diameter: Optional[float] = None  # df_inGroup (LEDET)
    number_of_filaments: Optional[int] = None

class Rectangular(BaseModel):
    """
        Level 2: Class for strand parameters
    """
    type: Literal['Rectangular']
    bare_width: Optional[float] = None
    bare_height: Optional[float] = None
    Cu_noCu_in_strand: Optional[float] = None
    RRR: Optional[float] = None  # RRR_Cu_inGroup (LEDET), RRRStrand (ProteCCT)
    T_ref_RRR_high: Optional[float] = None  # TupRRR (SIGMA), Reference temperature for RRR measurements
    T_ref_RRR_low: Optional[float] = None  # CURRENTLY NOT USED
    fil_twist_pitch: Optional[float] = None
    f_Rho_effective: Optional[float] = None
    bare_corner_radius: Optional[float] = None
    material_superconductor: Optional[str] = None
    n_value_superconductor: Optional[float] = None
    ec_superconductor: Optional[float] = None
    material_stabilizer: Optional[str] = None
    filament_diameter: Optional[float] = None  # df_inGroup (LEDET)

# ------------------- Conductors ---------------------------#

class Conductor(BaseModel):
    """
        Level 1: Class for conductor parameters
    """
    name: Optional[str] = None  # conductor name
    version: Optional[str] = None
    case: Optional[str] = None
    state: Optional[str] = None
    # For the below 3 parts see: https://gitlab.cern.ch/steam/steam_sdk/-/blob/master/docs/STEAM_SDK_Conductor_structure.svg
    cable: Union[Rutherford, Mono, Ribbon] = {'type': 'Rutherford'}     # TODO: Busbar, Rope, Roebel, CORC, TSTC, CICC
    strand: Union[Round, Rectangular] = {'type': 'Round'}       # TODO: Tape, WIC
    Jc_fit: Union[ConstantJc, Bottura, CUDI1, CUDI3, Summers, Bordini, BSCCO_2212_LBNL, Ic_A_NbTi] = {'type': 'CUDI1'}   # TODO: CUDI other numbers? , Roxie?


