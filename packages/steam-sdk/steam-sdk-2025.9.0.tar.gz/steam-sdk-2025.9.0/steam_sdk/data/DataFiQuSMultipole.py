from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Union, Optional, Tuple
from steam_sdk.data.DataRoxieParser import RoxieData

## different to FiQuS
class MultipoleRoxieGeometry(BaseModel):
    """
        Class for FiQuS multipole Roxie data (.geom)
    """
    Roxie_Data: RoxieData = RoxieData()

## same as in FiQuS
class MultipoleGeoElement(BaseModel):
    """
    Level 5: Class for FiQuS Multipole
    """
    lines: Optional[int] = Field(
        default=3,
        description="It specifies the number of Gaussian points for lines.",
    )
    triangles: Optional[Literal[1, 3, 4, 6, 7, 12, 13, 16]] = Field(
        default=3,
        description="It specifies the number of Gaussian points for triangles.",
    )
    quadrangles: Optional[Literal[1, 3, 4, 7]] = Field(
        default=4,
        description="It specifies the number of Gaussian points for quadrangles.",
    )


class MultipoleSolveConvectionBoundaryCondition(BaseModel):
    """
    Level 5: Class for FiQuS Multipole
    """
    boundaries: Optional[List[str]] = Field(
        default=[],
        description="It specifies the list of boundaries where the condition is applied."
                    "Each boundary is identified by a string of the form <half-turn/wedge reference number><side>,"
                    "where the accepted sides are i, o, l, h which correspond respectively to inner, outer, lower (angle), higher (angle): e.g., 1o",
    )
    heat_transfer_coefficient: Optional[Union[float, str]] = Field(
        default=None,
        description="It specifies the value or function name of the heat transfer coefficient for this boundary condition.",
    )


class MultipoleSolveHeatFluxBoundaryCondition(BaseModel):
    """
    Level 5: Class for FiQuS Multipole
    """
    boundaries: Optional[List[str]] = Field(
        default=[],
        description="It specifies the list of boundaries where the condition is applied."
                    "Each boundary is identified by a string of the form <half-turn/wedge reference number><side>,"
                    "where the accepted sides are i, o, l, h which correspond respectively to inner, outer, lower (angle), higher (angle): e.g., 1o",
    )
    const_heat_flux: Optional[float] = Field(
        default=None,
        description="It specifies the value of the heat flux for this boundary condition.",
    )
    # function_heat_flux: Optional[str] = None


class MultipoleSolveTemperatureBoundaryCondition(BaseModel):
    """
    Level 5: Class for FiQuS Multipole
    """
    boundaries: Optional[List[str]] = Field(
        default=[],
        description="It specifies the list of boundaries where the condition is applied."
                    "Each boundary is identified by a string of the form <half-turn/wedge reference number><side>,"
                    "where the accepted sides are i, o, l, h which correspond respectively to inner, outer, lower (angle), higher (angle): e.g., 1o",
    )
    const_temperature: Optional[float] = Field(
        default=None,
        description="It specifies the value of the temperature for this boundary condition.",
    )
    # function_temperature: Optional[str] = None


class MultipoleSolveQuenchInitiation(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    """
    turns: Optional[List[int]] = Field(
        default=[],
        description="It specifies the list of reference numbers of half-turns whose critical currents are set to zero.",
    )
    t_trigger: Optional[List[float]] = Field(
        default=[],
        description="It specifies the list of time instants at which the critical current is set to zero.",
    )


class MultipoleSolveBoundaryConditionsThermal(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    """
    temperature: Optional[Dict[str, MultipoleSolveTemperatureBoundaryCondition]] = Field(
        default={},
        description="This dictionary contains the information about the Dirichlet boundary conditions."
                    "The keys are chosen names for each boundary condition.",
    )
    heat_flux: Optional[Dict[str, MultipoleSolveHeatFluxBoundaryCondition]] = Field(
        default={},
        description="This dictionary contains the information about the Neumann boundary conditions."
                    "The keys are chosen names for each boundary condition.",
    )
    cooling: Optional[Dict[str, MultipoleSolveConvectionBoundaryCondition]] = Field(
        default={},
        description="This dictionary contains the information about the Robin boundary conditions."
                    "The keys are chosen names for each boundary condition.",
    )


# class MultipoleSolveTransientElectromagnetics(BaseModel):
#     """
#     Level 4: Class for FiQuS Multipole
#     """
#     time_stepping: Optional[Literal["adaptive", "fixed"]] = Field(
#         default="adaptive",
#         description="It specifies the type of time stepping.",
#     )
#     initial_time: Optional[float] = Field(
#         default=0.,
#         description="It specifies the initial time of the simulation.",
#     )
#     final_time: Optional[float] = Field(
#         default=None,
#         description="It specifies the final time of the simulation.",
#     )
#     fixed: MultipoleSolveTimeParametersFixed = Field(
#         default=MultipoleSolveTimeParametersFixed(),
#         description="This dictionary contains the information about the time parameters of the fixed time stepping.",
#     )
#     adaptive: MultipoleSolveTimeParametersAdaptive = Field(
#         default=MultipoleSolveTimeParametersAdaptive(),
#         description="This dictionary contains the information about the time parameters of the adaptive time stepping.",
#     )


class MultipoleSolveHeCooling(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    """
    enabled: Optional[bool] = Field(
        default=False,
        description="It determines whether the helium cooling is enabled or not (adiabatic conditions).",
    )
    sides: Optional[Literal["external", "inner", "outer", "inner_outer"]] = Field(
        default="outer",
        description="It specifies the general grouping of the boundaries where to apply cooling:"
                    "'adiabatic': no cooling; 'external': all external boundaries; 'inner': only inner boundaries; 'outer': only outer boundaries; 'inner_outer': inner and outer boundaries.",
    )
    heat_transfer_coefficient: Optional[Union[float, str]] = Field(
        default=None,
        description="It specifies the value or name of the function of the constant heat transfer coefficient.",
    )

class MultipoleSolveNonLinearSolver(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    """
    rel_tolerance: Optional[float] = Field(
        default=1E-4,
        description="It specifies the relative tolerance.",
    )
    abs_tolerance: Optional[float] = Field(
        default=0.1,
        description="It specifies the absolute tolerance.",
    )
    relaxation_factor: Optional[float] = Field(
        default=0.7,
        description="It specifies the relaxation factor.",
    )
    max_iterations: Optional[int] = Field(
        default=20,
        description="It specifies the maximum number of iterations if no convergence is reached.",
    )
    norm_type: Optional[Literal["L1Norm", "MeanL1Norm", "L2Norm", "MeanL2Norm", "LinfNorm"]] = Field(
        default='LinfNorm',
        description="It specifies the type of norm to be calculated for convergence assessment.",
    )


class MultipoleSolveTransientThermal(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    """
    initial_time: Optional[float] = Field(
        default=0.,
        description="It specifies the initial time of the simulation.",
    )
    final_time: Optional[float] = Field(
        default=None,
        description="It specifies the final time of the simulation.",
    )
    initial_time_step: Optional[float] = Field(
        default=1E-10,
        description="It specifies the initial time step used at the beginning of the transient simulation.",
    )
    min_time_step: Optional[float] = Field(
        default=1E-12,
        description="It specifies the minimum possible value of the time step.",
    )
    max_time_step: Optional[float] = Field(
        default=10,
        description="It specifies the maximum possible value of the time step.",
    )
    breakpoints: Optional[List[float]] = Field(
        default=[],
        description="It forces the transient simulation to hit the time instants contained in this list.",
    )
    integration_method: Optional[Union[None, Literal[
       "Euler", "Gear_2", "Gear_3", "Gear_4", "Gear_5", "Gear_6"
    ]]] = Field(
        default="Euler",
        title="Integration Method",
        description="It specifies the type of integration method to be used.",
    )
    rel_tol_time: Optional[float] = Field(
        default=1E-4,
        description="It specifies the relative tolerance.",
    )
    abs_tol_time: Optional[float] = Field(
        default=1e-4,
        description="It specifies the absolute tolerance.",
    )
    norm_type: Optional[Literal["L1Norm", "MeanL1Norm", "L2Norm", "MeanL2Norm", "LinfNorm"]] = Field(
        default='LinfNorm',
        description="It specifies the type of norm to be calculated for convergence assessment.",
    )
    stop_temperature: Optional[float] = Field(
        default=300,
        description="If one half turn reaches this temperature, the simulation is stopped.",
    )


class MultipoleSolveInsulationBlockToBlock(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    It contains the information about the materials and thicknesses of the inner insulation regions (between blocks) modeled via thin-shell approximation.
    """
    material: Optional[str] = Field(
        default=None,
        description="It specifies the default material of the insulation regions between the blocks insulation regions.",
    )
    # the order of blocks should be: [inner, outer] for mid-layer couples or [lower, higher] for mid-pole and mid-winding couples
    blocks_connection_overwrite: Optional[List[Tuple[str, str]]] = Field(
        default=[],
        description="It specifies the blocks couples adjacent to the insulation region."
                    "The blocks must be ordered from inner to outer block for mid-layer insulation regions and from lower to higher angle block for mid-pole and mid-winding insulation regions.",
    )
    materials_overwrite: Optional[List[List[str]]] = Field(
        default=[],
        description="It specifies the list of materials making up the layered insulation region to be placed between the specified blocks."
                    "The materials must be ordered from inner to outer layers and lower to higher angle layers.",
    )
    thicknesses_overwrite: Optional[List[List[Optional[float]]]] = Field(
        default=[],
        description="It specifies the list of thicknesses of the specified insulation layers. The order must match the one of the materials list.",
    )


class MultipoleSolveInsulationExterior(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    It contains the information about the materials and thicknesses of the outer insulation regions (exterior boundaries) modeled via thin-shell approximation.
    """
    blocks: Optional[List[str]] = Field(
        default=[],
        description="It specifies the reference numbers of the blocks adjacent to the exterior insulation regions to modify.",
    )
    materials_append: Optional[List[List[str]]] = Field(
        default=[],
        description="It specifies the list of materials making up the layered insulation region to be appended to the block insulation."
                    "The materials must be ordered from the block outward.",
    )
    thicknesses_append: Optional[List[List[float]]] = Field(
        default=[],
        description="It specifies the list of thicknesses of the specified insulation layers. The order must match the one of the materials list.",
    )


class MultipoleSolveWedge(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    material: Optional[str] = Field(
        default=None,
        description="It specifies the material of the wedge regions.",
    )
    RRR: Optional[float] = Field(
        default=None,
        description="It specifies the RRR of the wedge regions.",
    )
    T_ref_RRR_high: Optional[float] = Field(
        default=None,
        description="It specifies the reference temperature associated with the RRR.",
    )


class MultipoleSolveInsulationTSA(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    block_to_block: MultipoleSolveInsulationBlockToBlock = Field(
        default=MultipoleSolveInsulationBlockToBlock(),
        description="This dictionary contains the information about the materials and thicknesses of the inner insulation regions (between blocks) modeled via thin-shell approximation.",
    )
    exterior: Optional[MultipoleSolveInsulationExterior] = Field(
        default=MultipoleSolveInsulationExterior(),
        description="This dictionary contains the information about the materials and thicknesses of the outer insulation regions (exterior boundaries) modeled via thin-shell approximation.",
    )


class MultipoleSolveThermal(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    solve_type: Optional[Literal[None, "transient"]] = Field(
        default=None,
        description="It determines whether the thermal transient problem is solved ('transient') or not ('null').",
    )
    insulation_TSA: Optional[MultipoleSolveInsulationTSA] = Field(
        default=MultipoleSolveInsulationTSA(),
        description="This dictionary contains the information about the materials and thicknesses of the insulation regions modeled via thin-shell approximation.",
    )
    He_cooling: Optional[MultipoleSolveHeCooling] = Field(
        default=MultipoleSolveHeCooling(),
        description="This dictionary contains the information about the Robin boundary condition for generic groups of boundaries.",
    )
    overwrite_boundary_conditions: Optional[MultipoleSolveBoundaryConditionsThermal] = Field(
        default=MultipoleSolveBoundaryConditionsThermal(),
        description="This dictionary contains the information about boundary conditions for explicitly specified boundaries.",
    )
    non_linear_solver: Optional[MultipoleSolveNonLinearSolver] = Field(
        default=MultipoleSolveNonLinearSolver(),
        description="This dictionary contains the information about the parameters for the non-linear solver.",
    )
    time_stepping: Optional[MultipoleSolveTransientThermal] = Field(
        default=MultipoleSolveTransientThermal(),
        description="This dictionary contains the information about the parameters for the transient solver.",
    )
    jc_degradation_to_zero: Optional[MultipoleSolveQuenchInitiation] = Field(
        default=MultipoleSolveQuenchInitiation(),
        description="This dictionary contains the information about half turns with zero critical current.",
    )
    init_temperature: Optional[float] = Field(
        default=1.9,
        description="It specifies the initial temperature of the simulation.",
    )
    enforce_init_temperature_as_minimum: Optional[bool] = Field(
        default=False,
        description="It determines whether the initial temperature is enforced as the minimum temperature of the simulation.",
    )

class MultipoleSolveElectromagnetics(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    solve_type: Optional[Literal[None, "stationary"]] = Field(
        default=None,
        description="It determines whether the magneto-static problem is solved ('stationary') or not ('null').",
    )

    non_linear_solver: Optional[MultipoleSolveNonLinearSolver] = Field(
        default=MultipoleSolveNonLinearSolver(),
        description="This dictionary contains the information about the parameters for the non-linear solver.",
    )
    # currently not needed since stationary only, we will be able to reuse it from the thermal solver
    # time_stepping_parameters: MultipoleSolveTransientElectromagnetics = Field(
    #     default=MultipoleSolveTransientElectromagnetics(),
    #     description="This dictionary contains the information about the parameters for the transient solver.",
    # )


class MultipoleMeshThinShellApproximationParameters(BaseModel):
    """
    Level 4: Class for FiQuS Multipole
    """
    minimum_discretizations: Optional[int] = Field(
        default=1,
        description="It specifies the number of minimum spacial discretizations across a thin-shell.",
    )
    global_size_QH: Optional[float] = Field(
        default=1e-4,
        description="The thickness of the quench heater region is divided by this parameter to determine the number of spacial discretizations across the thin-shell.",
    )
    minimum_discretizations_QH: Optional[int] = Field(
        default=1,
        description="It specifies the number of minimum spacial discretizations across a thin-shell.",
    )


class MultipoleMeshThreshold(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    enabled: Optional[bool] = Field(
        default=False,
        description="It determines whether the gmsh Field is enabled or not.",
    )
    SizeMin: Optional[float] = Field(
        default=None,
        description="It sets gmsh Mesh.MeshSizeMin.",
    )
    SizeMax: Optional[float] = Field(
        default=None,
        description="It sets gmsh Mesh.MeshSizeMax.",
    )
    DistMin: Optional[float] = Field(
        default=None,
        description="It sets gmsh Mesh.MeshDistMin.",
    )
    DistMax: Optional[float] = Field(
        default=None,
        description="It sets gmsh Mesh.MeshDistMax.",
    )

class MultipoleMeshTransfinite(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    enabled_for: Literal[None, "curves", "curves_and_surfaces"] = Field(
        default=None,
        description="It determines on what entities the transfinite algorithm is applied.",
    )
    curve_target_size_height: Optional[float] = Field(
        default=None,
        description="The height of the region (short side) is divided by this parameter to determine the number of elements to apply via transfinite curves.",
    )
    curve_target_size_width: Optional[float] = Field(
        default=None,
        description="The width of the region (long side) is divided by this parameter to determine the number of elements to apply via transfinite curves.",
    )
class MultipoleMeshTransfiniteOrField(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    transfinite: Optional[MultipoleMeshTransfinite] = Field(
        default=MultipoleMeshTransfinite(),
        description="This dictionary contains the mesh information for transfinite curves.",
    )
    field: Optional[MultipoleMeshThreshold] = Field(
        default=MultipoleMeshThreshold(),
        description="This dictionary contains the gmsh Field information.",
    )

class MultipolePostProcThermal(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    output_time_steps_pos: Optional[Union[bool, int]] = Field(
        default=True,
        description="It determines whether the solution for the .pos file is saved for all time steps (True), none (False), or equidistant time steps (int).",
    )
    output_time_steps_txt: Optional[Union[bool, int]] = Field(
        default=True,
        description="It determines whether the solution for the .txt file is saved for all time steps (True), none (False), or equidistant time steps (int).",
    )
    save_pos_at_the_end: Optional[bool] = Field(
        default=True,
        description="It determines whether the solution for the .pos file is saved at the end of the simulation or during run time.",
    )
    save_txt_at_the_end: Optional[bool] = Field(
        default=False,
        description="It determines whether the solution for the .txt file is saved at the end of the simulation or during run time.",
    )
    take_average_conductor_temperature: Optional[bool] = Field(
        default=True,
        description="It determines whether the output files are based on the average conductor temperature or not (map2d).",
    )
    plot_all: Optional[Union[bool, None]] = Field(
        default=False,
        description="It determines whether the figures are generated and shown (true), generated only (null), or not generated (false). Useful for tests.",
    )
    variables: Optional[List[Literal["T", "jOverJc", "rho"]]] = Field(
        default=["T"],
        description="It specifies the physical quantity to be output.",
    )
    volumes: Optional[List[
        Literal["omega", "powered", "induced", "iron", "conducting", "insulator"]]] = Field(
        default=["powered"],
        description="It specifies the regions associated with the physical quantity to be output.",
    )


class MultipolePostProcElectromagnetics(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    output_time_steps_pos: Optional[Union[bool, int]] = Field(
        default=True,
        description="It determines whether the solution for the .pos file is saved for all time steps (True), none (False), or equidistant time steps (int).",
    )
    output_time_steps_txt: Optional[Union[bool, int]] = Field(
        default=True,
        description="It determines whether the solution for the .txt file is saved for all time steps (True), none (False), or equidistant time steps (int).",
    )
    save_pos_at_the_end: Optional[bool] = Field(
        default=True,
        description="It determines whether the solution for the .pos file is saved at the end of the simulation or during run time.",
    )
    save_txt_at_the_end: Optional[bool] = Field(
        default=False,
        description="It determines whether the solution for the .txt file is saved at the end of the simulation or during run time.",
    )
    compare_to_ROXIE: Optional[str] = Field(
        default=None,
        description="It contains the absolute path to a reference ROXIE map2d file. If provided, comparative plots with respect to the reference are generated.",
    )
    plot_all: Optional[Union[bool, None]] = Field(
        default=False,
        description="It determines whether the figures are generated and shown (true), generated only (null), or not generated (false). Useful for tests.",
    )
    variables: Optional[List[Literal["a", "az", "b", "h", "js"]]] = Field(
        default=["b"],
        description="It specifies the physical quantity to be output.",
    )
    volumes: Optional[List[
        Literal["omega", "powered", "induced", "air", "air_far_field", "iron", "conducting", "insulator"]]] = Field(
        default=["powered"],
        description="It specifies the regions associated with the physical quantity to be output.",
    )


class MultipolePostProc(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    electromagnetics: Optional[MultipolePostProcElectromagnetics] = Field(
        default=MultipolePostProcElectromagnetics(),
        description="This dictionary contains the post-processing information for the electromagnetic solution.",
    )
    thermal: Optional[MultipolePostProcThermal] = Field(
        default=MultipolePostProcThermal(),
        description="This dictionary contains the post-processing information for the thermal solution.",
    )

class MultipoleSolveCoilWindingsElectricalOrder(BaseModel):
    """
    Level 2: Class for the order of the electrical pairs
    """
    group_together: Optional[List[List[int]]] = []  # elPairs_GroupTogether
    reversed: Optional[List[int]] = []  # elPairs_RevElOrder
    overwrite_electrical_order: Optional[List[int]] = []

class MultipoleSolveCoilWindings(BaseModel):
    """
        Level 1: Class for winding information
    """
    conductor_to_group: Optional[List[int]] = []  # This key assigns to each group a conductor of one of the types defined with Conductor.name
    group_to_coil_section: Optional[List[int]] = []  # This key assigns groups of half-turns to coil sections
    polarities_in_group: Optional[List[int]] = []  # This key assigns the polarity of the current in each group #
    half_turn_length: Optional[List[float]] = []
    electrical_pairs: MultipoleSolveCoilWindingsElectricalOrder = MultipoleSolveCoilWindingsElectricalOrder()  # Variables used to calculate half-turn electrical order

class MultipoleSolve(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    coil_windings: MultipoleSolveCoilWindings = MultipoleSolveCoilWindings()
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

class MultipoleThermalInsulationMesh(BaseModel):
    """
    Level 3: Class for FiQuS Multipole
    """
    global_size: Optional[float] = Field(
        default=1e-4,
        description="It specifies the global size of the mesh for the insulation regions. It is enforced as a constant mesh field for surface insulation and by fixing the number of TSA layers for thin-shell approximation.",
    )
    TSA: Optional[MultipoleMeshThinShellApproximationParameters] = Field(
        default=MultipoleMeshThinShellApproximationParameters(),
        description="This dictionary contains the mesh information for thin-shells.",
    )
    
class MultipoleMeshThermal(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    create: Optional[bool] = Field(
        default=True,
        description="It determines whether the thermal mesh is built or not.",
    )
    conductors: Optional[MultipoleMeshTransfiniteOrField] = Field(
        default=MultipoleMeshTransfiniteOrField(),
        description="This dictionary contains the mesh information for the conductor regions.",
    )
    wedges: Optional[MultipoleMeshTransfiniteOrField] = Field(
        default=MultipoleMeshTransfiniteOrField(),
        description="This dictionary contains the mesh information for the wedge regions.",
    )
    iron_field: Optional[MultipoleMeshThreshold] = Field(
        default=MultipoleMeshThreshold(),
        description="This dictionary contains the gmsh Field information for the iron yoke region.",
    )
    insulation: Optional[MultipoleThermalInsulationMesh] = Field(
        default=MultipoleThermalInsulationMesh(),
        description="This dictionary contains the mesh information for the insulation regions.",
    )
   
    iron_field: Optional[MultipoleMeshThreshold] = Field(
        default=MultipoleMeshThreshold(),
        description="This dictionary contains the gmsh Field information for the iron yoke region.",
    )

    isothermal_conductors: Optional[bool] = Field(
        default=False,
        description="It determines whether the conductors are considered isothermal or not using getDP constraints.",
    )
    isothermal_wedges: Optional[bool] = Field(
        default=False,
        description="It determines whether the wedges are considered isothermal or not using getDP Link constraints.",
    )

class MultipoleMeshElectromagnetics(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    create: Optional[bool] = Field(
        default=True,
        description="It determines whether the electromagnetic mesh is built or not.",
    )
    conductors: Optional[MultipoleMeshTransfiniteOrField] = Field(
        default=MultipoleMeshTransfiniteOrField(),
        description="This dictionary contains the mesh information for the conductor regions.",
    )
    wedges: Optional[MultipoleMeshTransfiniteOrField] = Field(
        default=MultipoleMeshTransfiniteOrField(),
        description="This dictionary contains the mesh information for the wedge regions.",
    )
    iron_field: Optional[MultipoleMeshThreshold] = Field(
        default=MultipoleMeshThreshold(),
        description="This dictionary contains the gmsh Field information for the iron yoke region.",
    )
    bore_field: Optional[MultipoleMeshThreshold] = Field(
        default=MultipoleMeshThreshold(),
        description="This dictionary contains the gmsh Field information for the bore region.",
    )

class MultipoleMesh(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    electromagnetics: Optional[MultipoleMeshElectromagnetics] = Field(
        default=MultipoleMeshElectromagnetics(),
        description="This dictionary contains the mesh information for the electromagnetic solution.",
    )
    thermal: Optional[MultipoleMeshThermal] = Field(
        default=MultipoleMeshThermal(),
        description="This dictionary contains the mesh information for the thermal solution.",
    )


class MultipoleGeometryThermal(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    create: Optional[bool] = Field(
        default=True,
        description="It determines whether the thermal geometry is built or not.",
    )
    with_iron_yoke: Optional[bool] = Field(
        default=False,
        description="It determines whether the iron yoke region is built or not.",
    )
    with_wedges: Optional[bool] = Field(
        default=True,
        description="It determines whether the wedge regions are built or not.",
    )
    use_TSA: Optional[bool] = Field(
        default=False,
        description="It determines whether the insulation regions are explicitly built or modeled via thin-shell approximation.",
    )
    correct_block_coil_tsa_checkered_scheme: Optional[bool] = Field(
        default=False,
        description="There is a bug in the TSA naming scheme for block coils, this flag activates a simple (not clean) bug fix that will be replaced in a future version.",
    )

class MultipoleGeometryElectromagnetics(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    create: Optional[bool] = Field(
        default=True,
        description="It determines whether the electromagnetic geometry is built or not.",
    )
    with_iron_yoke: Optional[bool] = Field(
        default=True,
        description="It determines whether the iron yoke region is built or not.",
    )
    with_wedges: Optional[bool] = Field(
        default=True,
        description="It determines whether the wedge regions are built or not.",
    )
    symmetry: Optional[Literal["none", "xy", "x", "y"]] = Field(
        default='none',
        description="It determines the model regions to build according to the specified axis/axes.",
    )


class MultipoleGeometry(BaseModel):
    """
    Level 2: Class for FiQuS Multipole
    """
    geom_file_path: Optional[str] = Field(
        default=None,
        description="It contains the path to a .geom file. If null, the default .geom file produced by steam-sdk BuilderFiQuS will be used.",
    )
    plot_preview: Optional[bool] = Field(
        default=False,
        description="If true, it displays matplotlib figures of the magnet geometry with relevant information (e.g., conductor and block numbers).",
    )
    electromagnetics: Optional[MultipoleGeometryElectromagnetics] = Field(
        default=MultipoleGeometryElectromagnetics(),
        description="This dictionary contains the geometry information for the electromagnetic solution.",
    )
    thermal: Optional[MultipoleGeometryThermal] = Field(
        default=MultipoleGeometryThermal(),
        description="This dictionary contains the geometry information for the thermal solution.",
    )


class Multipole(BaseModel):
    """
    Level 1: Class for FiQuS Multipole
    """
    type: Literal["multipole"] = "multipole"
    geometry: MultipoleGeometry = Field(
        default=MultipoleGeometry(),
        description="This dictionary contains the geometry information.",
    )
    mesh: Optional[MultipoleMesh] = Field(
        default=MultipoleMesh(),
        description="This dictionary contains the mesh information.",
    )
    solve: Optional[MultipoleSolve] = Field(
        default=MultipoleSolve(),
        description="This dictionary contains the solution information.",
    )
    postproc: Optional[MultipolePostProc] = Field(
        default=MultipolePostProc(),
        description="This dictionary contains the post-process information.",
    )
