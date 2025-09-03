from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

from steam_sdk.data.DataFiQuS import RunFiQuS

from steam_sdk.data.DataFiQuSCCT import CCTGeometryCWSInputs
from steam_sdk.data.DataFiQuSCCT import CCTGeometryAir
from steam_sdk.data.DataFiQuSCCT import CCTMesh
from steam_sdk.data.DataFiQuSCCT import CCTSolveWinding
from steam_sdk.data.DataFiQuSCCT import CCTSolveFormer
from steam_sdk.data.DataFiQuSCCT import CCTSolveAir

from steam_sdk.data.DataFiQuSCWS import CWSGeometry
from steam_sdk.data.DataFiQuSCWS import CWSMesh
from steam_sdk.data.DataFiQuSCWS import CWSSolve
from steam_sdk.data.DataFiQuSCWS import CWSSolveConductorsExcitation, CWSSolveConductors
from steam_sdk.data.DataFiQuSCWS import CWSPostproc

from steam_sdk.data.DataFiQuSMultipole import MultipoleGeometry
from steam_sdk.data.DataFiQuSMultipole import MultipoleMesh
from steam_sdk.data.DataFiQuSMultipole import MultipoleSolveElectromagnetics, MultipoleSolveThermal, MultipoleSolveWedge
from steam_sdk.data.DataFiQuSMultipole import MultipolePostProc

from steam_sdk.data.DataFiQuSPancake3D import Pancake3DGeometry
from steam_sdk.data.DataFiQuSPancake3D import Pancake3DMesh
from steam_sdk.data.DataFiQuSPancake3D import Pancake3DSolve
from steam_sdk.data.DataFiQuSPancake3D import Pancake3DPostprocess

from steam_sdk.data.DataFiQuSConductorAC_Strand import CACStrandGeometry
from steam_sdk.data.DataFiQuSConductorAC_Strand import CACStrandMesh
from steam_sdk.data.DataFiQuSConductorAC_Strand import CACStrandSolve
from steam_sdk.data.DataFiQuSConductorAC_Strand import CACStrandPostproc

from steam_sdk.data.DataFiQuSConductorAC_Rutherford import CACRutherfordGeometry
from steam_sdk.data.DataFiQuSConductorAC_Rutherford import CACRutherfordMesh
from steam_sdk.data.DataFiQuSConductorAC_Rutherford import CACRutherfordSolve
from steam_sdk.data.DataFiQuSConductorAC_Rutherford import CACRutherfordPostproc



class CCTGeometryCWSInputsOptions(CCTGeometryCWSInputs):
    pass


class CCTGeometryWindingOptions(BaseModel):  # Geometry related windings _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    r_wms: Optional[List[float]] = None  # radius of the middle of the winding
    ndpts: Optional[List[int]] = None  # number of divisions of turn, i.e. number of hexagonal elements for each turn
    ndpt_ins: Optional[List[int]] = None  # number of divisions of terminals in
    ndpt_outs: Optional[List[int]] = None  # number of divisions of terminals in
    lps: Optional[List[float]] = None  # layer pitch
    alphas: Optional[List[float]] = None  # tilt angle
    wwws: Optional[List[float]] = None  # winding wire widths (assuming rectangular)
    wwhs: Optional[List[float]] = None  # winding wire heights (assuming rectangular)


class CCTGeometryFormerOptions(BaseModel):  # Geometry related formers _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    z_mins: Optional[List[float]] = None  # extend of former  in negative z direction
    z_maxs: Optional[List[float]] = None  # extend of former in positive z direction
    rotates: Optional[List[float]] = None  # rotation of the former around its axis in degrees


class CCTGeometryAirOptions(CCTGeometryAir):  # Geometry related air_region _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    pass


class CCTGeometryOptions(BaseModel):
    """
        Level 2: Class for FiQuS CCT for FiQuS input
    """
    CWS_inputs: CCTGeometryCWSInputsOptions = CCTGeometryCWSInputsOptions()
    windings: CCTGeometryWindingOptions = CCTGeometryWindingOptions()
    formers: CCTGeometryFormerOptions = CCTGeometryFormerOptions()
    air: CCTGeometryAirOptions = CCTGeometryAirOptions()


class CCTMeshOptions(CCTMesh):
    pass


class CCTSolveWindingOptions(CCTSolveWinding):  # Solution time used windings _inputs (materials and BC)
    pass


class CCTSolveFormerOptions(CCTSolveFormer):  # Solution time used formers _inputs (materials and BC)
    pass


class CCTSolveAirOptions(CCTSolveAir):  # Solution time used air _inputs (materials and BC)
    pass


class CCTSolveOptions(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    windings: CCTSolveWindingOptions = CCTSolveWindingOptions()  # windings solution time _inputs
    formers: CCTSolveFormerOptions = CCTSolveFormerOptions()  # former solution time _inputs
    air: CCTSolveAirOptions = CCTSolveAirOptions()  # air solution time _inputs
    pro_template: Optional[str] = None  # file name of .pro template file
    variables: Optional[List[str]] = None  # Name of variable to post-process by GetDP, like B for magnetic flux density
    volumes: Optional[List[str]] = None  # Name of volume to post-process by GetDP, line Winding_1
    file_exts: Optional[List[str]] = None  # Name of file extensions to post-process by GetDP, like .pos


class CCTPostprocOptions(BaseModel):
    """
        Class for FiQuS CCT input file
    """
    additional_outputs: Optional[List[str]] = None  # Name of software specific input files to prepare, like :LEDET3D
    fqpcs_export_trim_tol: Optional[List[float]] = None  # this multiplier times winding extend gives 'z' coordinate above(below) which hexes are exported for LEDET, length of this list must match number of fqpls
    variables: Optional[List[str]] = None  # Name of variable to post-process by python Gmsh API, like B for magnetic flux density
    volumes: Optional[List[str]] = None  # Name of volume to post-process by python Gmsh API, line Winding_1
    file_exts: Optional[List[str]] = None  # Name of file extensions o post-process by python Gmsh API, like .pos


class CCT_MagnetOptions(BaseModel):
    """
        Class for FiQuS CCT
    """
    geometry: CCTGeometryOptions = CCTGeometryOptions()
    mesh: CCTMeshOptions = CCTMeshOptions()
    solve: CCTSolveOptions = CCTSolveOptions()
    postproc: CCTPostprocOptions = CCTPostprocOptions()


class MultipoleGeometryOptions(MultipoleGeometry):
    pass


class MultipoleMeshOptions(MultipoleMesh):
    pass


class MultipoleSolveOptions(BaseModel):

    """
    Level 2: Class for FiQuS Multipole
    """
    electromagnetics: Optional[MultipoleSolveElectromagnetics] = Field(
        default=MultipoleSolveElectromagnetics(),
        description="This dictionary contains the solver information for the electromagnetic solution.",
    )
    thermal: Optional[MultipoleSolveThermal] = Field(
        default=MultipoleSolveThermal(),
        description="This dictionary contains the solver information for the thermal solution.",
    )
    wedges: Optional[MultipoleSolveWedge] = Field(
        default=MultipoleSolveWedge(),
        description="This dictionary contains the material information of wedges.",
    )
    noOfMPITasks: Optional[Union[bool, int]] = Field(
        default=False,
        title="No. of tasks for MPI parallel run of GetDP",
        description=(
            "If integer, GetDP will be run in parallel using MPI. This is only valid"
            " if MPI is installed on the system and an MPI-enabled GetDP is used."
            " If False, GetDP will be run in serial without invoking mpiexec."
        ),
    )


class MultipolePostProcOptions(MultipolePostProc):
    pass


class Multipole_magnetOptions(BaseModel):
    geometry: MultipoleGeometryOptions = MultipoleGeometryOptions()
    mesh: MultipoleMeshOptions = MultipoleMeshOptions()
    solve: MultipoleSolveOptions = MultipoleSolveOptions()
    postproc: MultipolePostProcOptions = MultipolePostProcOptions()


class Pancake3DGeometryOptions(Pancake3DGeometry):
    pass


class Pancake3DMeshOptions(Pancake3DMesh):
    pass


class Pancake3DSolveOptions(Pancake3DSolve):
    pass


class Pancake3DPostprocessOptions(Pancake3DPostprocess):
    pass


class Pancake3D_magnetOptions(BaseModel):
    geometry: Pancake3DGeometryOptions = Pancake3DGeometryOptions()
    mesh: Pancake3DMeshOptions = Pancake3DMeshOptions()
    solve: Pancake3DSolveOptions = Pancake3DSolveOptions()
    postproc: Pancake3DPostprocessOptions = Pancake3DPostprocessOptions()


class RunFiQuS(RunFiQuS):
    pass

# ---- CAC Strand Options ----
class CACStrandGeometryOptions(CACStrandGeometry):
    pass


class CACStrandMeshOptions(CACStrandMesh):
    pass


class CACStrandSolveGeneralparameters(BaseModel):
    """
    Level 3: Class for CAC general parameters
    """

    superconductor_linear: Optional[bool] = Field(default=False, description="For debugging: replace LTS by normal conductor")
    noOfMPITasks: Optional[Union[bool, int]] = Field(
        default=False,
        title="No. of tasks for MPI parallel run of GetDP",
        description=(
            "If integer, GetDP will be run in parallel using MPI. This is only valid"
            " if MPI is installed on the system and an MPI-enabled GetDP is used."
            " If False, GetDP will be run in serial without invoking mpiexec."
        ),
    )

class CACStrandSolveOptions(CACStrandSolve):
    general_parameters: CACStrandSolveGeneralparameters = CACStrandSolveGeneralparameters()
    pass

class CACStrandPostprocOptions(CACStrandPostproc):
    pass


class CACStrand_MagnetOptions(BaseModel):
    """
        Class for FiQuS CWS
    """
    geometry: CACStrandGeometryOptions = CACStrandGeometryOptions()
    mesh: CACStrandMeshOptions = CACStrandMeshOptions()
    solve: CACStrandSolveOptions = CACStrandSolveOptions()
    postproc: CACStrandPostprocOptions = CACStrandPostprocOptions()

# ---- CAC Rutherford Options ----
class CACRutherfordGeometryOptions(CACRutherfordGeometry):
    pass


class CACRutherfordMeshOptions(CACRutherfordMesh):
    pass


class CACRutherfordSolveGeneralparameters(BaseModel):
    """
    Level 3: Class for CAC general parameters
    """
    superconductor_linear: Optional[bool] = Field(default=False, description="For debugging: replace LTS by normal conductor")
    crossing_coupling_resistance: Optional[float] = Field(default=1e-6, description="Crossing coupling resistance (Ohm).")

class CACRutherfordSolveOptions(CACRutherfordSolve):
    general_parameters: CACRutherfordSolveGeneralparameters = CACRutherfordSolveGeneralparameters()


class CACRutherfordPostprocOptions(CACRutherfordPostproc):
    pass


class CACRutherford_MagnetOptions(BaseModel):
    """
        Class for FiQuS CWS
    """
    geometry: CACRutherfordGeometryOptions = CACRutherfordGeometryOptions()
    mesh: CACRutherfordMeshOptions = CACRutherfordMeshOptions()
    solve: CACRutherfordSolveOptions = CACRutherfordSolveOptions()
    postproc: CACRutherfordPostprocOptions = CACRutherfordPostprocOptions()


class CWSGeometryOptions(CWSGeometry):
    pass


class CWSMeshOptions(CWSMesh):
    pass


class CWSSolveOptions(CWSSolve):
    pass


class CWSPostprocOptions(CWSPostproc):
    pass


class CWS_MagnetOptions(BaseModel):
    """
        Class for FiQuS CWS
    """
    geometry: CWSGeometryOptions = CWSGeometryOptions()
    mesh: CWSMeshOptions = CWSMeshOptions()
    solve: CWSSolveOptions = CWSSolveOptions()
    postproc: CWSPostprocOptions = CWSPostprocOptions()


class FiQuSOptions(BaseModel):
    """
        This is data structure of FiQuS Options in STEAM SDK
    """
    run: RunFiQuS = RunFiQuS()
    CACStrand: CACStrand_MagnetOptions = CACStrand_MagnetOptions()
    CACRutherford: CACRutherford_MagnetOptions = CACRutherford_MagnetOptions()
    cct: CCT_MagnetOptions = CCT_MagnetOptions()
    cws: CWS_MagnetOptions = CWS_MagnetOptions()
    multipole: Multipole_magnetOptions = Multipole_magnetOptions()
    Pancake3D: Pancake3D_magnetOptions = Pancake3D_magnetOptions()
