from pydantic import BaseModel
from typing import List, Literal, Optional

class CCTGeometryCWSInputs(BaseModel):
    """
        Level 3: Class for controlling if and where the conductor files and brep files are written for the CWS (conductor with step) workflow
    """
    write: bool = False             # if true only conductor and brep files are written, everything else is skipped.
    output_folder: Optional[str] = None       # this is relative path to the input file location


class CCTGeometryWinding(BaseModel):  # Geometry related windings _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    r_wms: Optional[List[float]] = None  # radius of the middle of the winding
    n_turnss: Optional[List[float]] = None  # number of turns
    ndpts: Optional[List[int]] = None  # number of divisions of turn, i.e. number of hexagonal elements for each turn
    ndpt_ins: Optional[List[int]] = None  # number of divisions of terminals ins
    ndpt_outs: Optional[List[int]] = None  # number of divisions of terminals outs
    lps: Optional[List[float]] = None  # layer pitch
    alphas: Optional[List[float]] = None  # tilt angle
    wwws: Optional[List[float]] = None  # winding wire widths (assuming rectangular)
    wwhs: Optional[List[float]] = None  # winding wire heights (assuming rectangular)


class CCTGeometryFQPCs(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    names: List[str] = []  # name to use in gmsh and getdp
    fndpls: Optional[List[int]] = None  # fqpl number of divisions per length
    fwws: Optional[List[float]] = None  # fqpl wire widths (assuming rectangular) for theta = 0 this is x dimension
    fwhs: Optional[List[float]] = None  # fqpl wire heights (assuming rectangular) for theta = 0 this is y dimension
    r_ins: Optional[List[float]] = None  # radiuses for inner diameter for fqpl (radial (or x direction for theta=0) for placing the fqpl
    r_bs: Optional[List[float]] = None  # radiuses for bending the fqpl by 180 degrees
    n_sbs: Optional[List[int]] = None  # number of 'bending segmetns' for the 180 degrees turn
    thetas: Optional[List[float]] = None  # rotation in deg from x+ axis towards y+ axis about z axis.
    z_starts: Optional[List[str]] = None  # which air boundary to start at. These is string with either: z_min or z_max key from the Air region.
    z_ends: Optional[List[float]] = None  # z coordinate of loop end


class CCTGeometryFormer(BaseModel):  # Geometry related formers _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    names: Optional[List[str]] = None  # name to use in gmsh and getdp
    r_ins: Optional[List[float]] = None  # inner radius
    r_outs: Optional[List[float]] = None  # outer radius
    z_mins: Optional[List[float]] = None  # extend of former  in negative z direction
    z_maxs: Optional[List[float]] = None  # extend of former in positive z direction
    rotates: Optional[List[float]] = None  # rotation of the former around its axis in degrees


class CCTGeometryAir(BaseModel):  # Geometry related air_region _inputs
    """
        Level 2: Class for FiQuS CCT
    """
    name: Optional[str] = None  # name to use in gmsh and getdp
    sh_type: Optional[str] = None  # cylinder or cuboid are possible
    ar: Optional[float] = None  # if box type is cuboid a is taken as a dimension, if cylinder then r is taken
    z_min: Optional[float] = None  # extend of air region in negative z direction
    z_max: Optional[float] = None  # extend of air region in positive z direction


class CCTGeometry(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    CWS_inputs: CCTGeometryCWSInputs = CCTGeometryCWSInputs()
    windings: CCTGeometryWinding = CCTGeometryWinding()
    fqpcs: CCTGeometryFQPCs = CCTGeometryFQPCs()
    formers: CCTGeometryFormer = CCTGeometryFormer()
    air: CCTGeometryAir = CCTGeometryAir()


class CCTMesh(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    MaxAspectWindings: Optional[float] = None  # used in transfinite mesh_generators settings to define mesh_generators size along two longer lines of hex elements of windings
    ThresholdSizeMin: Optional[float] = None  # sets field control of Threshold SizeMin
    ThresholdSizeMax: Optional[float] = None  # sets field control of Threshold SizeMax
    ThresholdDistMin: Optional[float] = None  # sets field control of Threshold DistMin
    ThresholdDistMax: Optional[float] = None  # sets field control of Threshold DistMax


class CCTSolveWinding(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: Optional[List[float]] = None  # current in the wire
    sigmas: Optional[List[float]] = None  # electrical conductivity
    mu_rs: Optional[List[float]] = None  # relative permeability


class CCTSolveFormer(BaseModel):  # Solution time used formers _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigmas: Optional[List[float]] = None  # electrical conductivity
    mu_rs: Optional[List[float]] = None  # relative permeability


class CCTSolveFQPCs(BaseModel):  # Solution time used windings _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    currents: List[float] = []  # current in the wire
    sigmas: List[float] = []  # electrical conductivity
    mu_rs: List[float] = []  # relative permeability


class CCTSolveAir(BaseModel):  # Solution time used air _inputs (materials and BC)
    """
        Level 2: Class for FiQuS CCT
    """
    sigma: Optional[float] = None  # electrical conductivity
    mu_r: Optional[float] = None  # relative permeability


class CCTSolve(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    windings: CCTSolveWinding = CCTSolveWinding()  # windings solution time _inputs
    formers: CCTSolveFormer = CCTSolveFormer()  # former solution time _inputs
    fqpcs: CCTSolveFQPCs = CCTSolveFQPCs()  # fqpls solution time _inputs
    air: CCTSolveAir = CCTSolveAir()  # air solution time _inputs
    pro_template: Optional[str] = None  # file name of .pro template file
    variables: Optional[List[str]] = None  # Name of variable to post-process by GetDP, like B for magnetic flux density
    volumes: Optional[List[str]] = None  # Name of volume to post-process by GetDP, line Winding_1
    file_exts: Optional[List[str]] = None  # Name of file extensions to post-process by GetDP, like .pos


class CCTPostproc(BaseModel):
    """
        Level 2: Class for  FiQuS CCT
    """
    windings_wwns: Optional[List[int]] = None  # wires in width direction numbers
    windings_whns: Optional[List[int]] = None  # wires in height direction numbers
    additional_outputs: Optional[List[str]] = None  # Name of software specific input files to prepare, like :LEDET3D
    winding_order: Optional[List[int]] = None
    fqpcs_export_trim_tol: Optional[List[float]] = None  # this multiplier times winding extend gives 'z' coordinate above(below) which hexes are exported for LEDET, length of this list must match number of fqpls
    variables: Optional[List[str]] = None  # Name of variable to post-process by python Gmsh API, like B for magnetic flux density
    volumes: Optional[List[str]] = None  # Name of volume to post-process by python Gmsh API, line Winding_1
    file_exts: Optional[List[str]] = None  # Name of file extensions o post-process by python Gmsh API, like .pos


class CCT(BaseModel):
    """
        Level 2: Class for FiQuS CCT
    """
    type: Literal['CCT_straight']
    geometry: CCTGeometry = CCTGeometry()
    mesh: CCTMesh = CCTMesh()
    solve: CCTSolve = CCTSolve()
    postproc: CCTPostproc = CCTPostproc()
