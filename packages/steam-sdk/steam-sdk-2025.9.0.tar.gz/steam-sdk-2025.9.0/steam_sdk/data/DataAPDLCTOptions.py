from typing import List, Dict, Optional

from pydantic import BaseModel


class APDLCTModelParameters(BaseModel):
    """
        Level 2: Class for model parameters
    """
    T_reference: Optional[float] = None
    t_ilay: Optional[float] = None
    t_icoil: Optional[float] = None
    fillerth: Optional[float] = None
    r0: Optional[float] = None
    t_yoke: Optional[float] = None
    threshold_phi_angle_rounded_to_zero: Optional[float] = None


class APDLCTFrictionParameters(BaseModel):
    """
        Level 2: Class for friction parameters
    """
    dict_mu: Dict[str, float] = {}


class APDLCTMeshParameters(BaseModel):
    """
        Level 2: Class for mesh parameters
    """
    f_scaling_mesh: Optional[float] = None  # this will scale all the others
    mesh_size_coil_azimuthal: Optional[float] = None
    mesh_size_coil_radial: Optional[float] = None
    mesh_size_aperture: Optional[float] = None
    mesh_size_filler: Optional[float] = None
    mesh_size_yoke: Optional[float] = None


class APDLCTContacts(BaseModel):
    """
        Level 2: Class for contacts definition
    """
    dict_contacts: Dict[str, int] = {}


class APDLCTOptions(BaseModel):
    """
        Level 1: Class for options for an APDL model of a cos-theta magnet (LBNL model)
    """
    groups_to_sections: List[int] = []
    Model_Parameters: APDLCTModelParameters = APDLCTModelParameters()
    Contacts: APDLCTContacts = APDLCTContacts()
    flags_CoilWedgeSwitch: List[int] = []
    Friction_Parameters: APDLCTFrictionParameters = APDLCTFrictionParameters()
    Mesh_Parameters: APDLCTMeshParameters = APDLCTMeshParameters()
