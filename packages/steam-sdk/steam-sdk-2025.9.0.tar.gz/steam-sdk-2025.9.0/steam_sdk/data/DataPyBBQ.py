from pydantic import BaseModel

from typing import List, Optional

"""
    These classes define the four PyBBQ dataclasses, which contain the variables to write in the PyBBQ 
    input file.
"""

class DataPyBBQ(BaseModel):
    # Cable geometry and operating values:
    width: Optional[float] = None
    height: Optional[float] = None
    CuSC: Optional[float] = None
    non_void: Optional[float] = None
    shape: Optional[str] = None
    strands: Optional[int] = None # New
    strand_dmt: Optional[float] = None # New
    layers: Optional[int] = None
    insulation_thickness: Optional[float] = None
    busbar_length: Optional[float] = None
    T1: Optional[float] = None

    # Magnetic Field
    Calc_b_from_geometry: Optional[bool] = None
    Background_Bx: Optional[float] = None
    Background_By: Optional[float] = None
    Background_Bz: Optional[float] = None
    Self_Field: Optional[float] = None
    B0_dump: Optional[bool] = None

    # Materials:
    material: Optional[str] = None            # New
    tapetype: Optional[str] = None            # New
    RRR: Optional[float] = None               # New
    Jc_4K_5T_NbTi: Optional[float] = None     # New

    # Load
    Current: Optional[float] = None
    Inductance: Optional[float] = None
    DumpR: Optional[float] = None

    # Cooling
    c5: Optional[float] = None                # New
    c6: Optional[float] = None                # New
    p: Optional[float] = None                 # New
    Pmax: Optional[float] = None              # New
    Helium_cooling: Optional[bool] = None
    Helium_cooling_internal: Optional[bool] = None    # New
    wetted_p: Optional[float] = None          # New

    # Initialization of the hot-spot
    Power: Optional[float] = None  # New
    Heating_mode: Optional[str] = None
    Heating_nodes: Optional[List[int]] = None
    Heating_time: Optional[float] = None
    Heating_time_constant: Optional[float] = None

    # Protection and Detection
    Detection_Voltage: Optional[float] = None
    Protection_Delay: Optional[float] = None

    # Analysis
    Tref: Optional[float] = None              # New
    Posref: Optional[List[float]] = None      # New

    # Solver setting:
    output: Optional[bool] = None
    dt: Optional[float] = None
    t0: List[float] = []
    sections: Optional[int] = None # Moved
    print_every: Optional[int] = None
    store_every: Optional[int] = None
    plot_every: Optional[int] = None
    sim_name: Optional[str] = None
    uniquify_path: Optional[bool] = None


