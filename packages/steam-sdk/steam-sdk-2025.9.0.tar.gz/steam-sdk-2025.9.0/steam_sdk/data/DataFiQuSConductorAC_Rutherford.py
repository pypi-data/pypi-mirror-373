from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class CACRutherfordIOsettingsLoad(BaseModel):
    """
    Level 3: Class for Input/Output settings for the cable geometry
    """

    load_from_yaml: Optional[bool] = Field(
        default=None,
        description="True to load cable geometry from yaml-file, false to create the geometry.",
    )
    filename: Optional[str] = Field(
        default=None,
        description="Name of the file from which to load the cable geometry.",
    )


class CACRutherfordIOsettingsSave(BaseModel):
    """
    Level 3: Class for Input/Output settings for the cable geometry
    """

    save_to_yaml: Optional[bool] = Field(
        default=None,
        description="True to save cable geometry to yaml-file, false to not save the geometry.",
    )
    filename: Optional[str] = Field(
        default=None,
        description="Name of the file to which to save the cable geometry.",
    )


class CACRutherfordIOsettings(BaseModel):
    """
    Level 2: Class for Input/Output settings for the cable geometry
    """

    load: CACRutherfordIOsettingsLoad = (
        CACRutherfordIOsettingsLoad()
    )
    save: CACRutherfordIOsettingsSave = (
        CACRutherfordIOsettingsSave()
    )

# ============= GEOMETRY ============= #


class CACRutherfordGeometry(BaseModel):
    """
    Level 2: Class for cable geometry parameters
    """
    io_settings: CACRutherfordIOsettings = CACRutherfordIOsettings()

    point_snap_tolerance_relative_to_strand_diameter: Optional[float] = Field(
        default=None,
        description="The maximum distance between two points, relative to the strand diameter, where the points are considered equal (i.e. they 'snap' together).",
    )
    min_roundness_factor: Optional[float] = Field(
        default=None,
        description="Minimum roundness is the ratio between the min -and max radius for the corner circle-arcs.",
    )
    air_radius: Optional[float] = Field(
        default=None, description="Radius of the air region (m)."
    )
    coating_corner_arc_radius: Optional[float] = Field(
        default=0, description="Radius of the corner arcs of the coating (m)."
    )
    coating_thickness: Optional[float] = Field(
        default=0, description="Thickness of the coating (m)."
    )
    keep_strand_area: Optional[bool] = Field(
        default=True, description="If True, the area of the strands are determined by the area of the strand described in 'conductors'. If False, the area of the strands are determined based on the cable geometry inputs."
    )


# ============= MESH ============= #




class CACRutherfordMesh(BaseModel):
    """
    Level 2: Class for FiQuS ConductorAC
    """

    scaling_global: Optional[float] = Field(default=1, description="Global scaling factor for mesh size.")

    strand_mesh_size_ratio: Optional[float] = Field(1, description="Mesh size ratio for the strand, relative to the strand diameter.")
    coating_mesh_size_ratio: Optional[float] = Field(1, description="Mesh size ratio for the coating, relative to the strand diameter.")
    air_boundary_mesh_size_ratio: Optional[float] = Field(1, description="Mesh size ratio for the air boundary, relative to the strand diameter.")

# ============= SOLVE ============= #
# -- General parameters -- #
class CACRutherfordSolveGeneralparameters(BaseModel):
    """
    Level 3: Class for general parameters
    """
    temperature: float = Field(default=1.9, description="Temperature (K) of the strand.")
    superconductor_linear: Optional[bool] = Field(default=False, description="For debugging: replace LTS by normal conductor.")

    crossing_coupling_resistance: Optional[float] = Field(default=1e-6, description="Crossing coupling resistance (Ohm).")

class CACRutherfordSolveInitialConditions(BaseModel):
    """
    Level 3: Class for initial conditions
    """

    init_from_pos_file: bool = Field(
        default=False, description="Do we initialize the solution at a non-zero field."
    )
    pos_file_to_init_from: Optional[str] = Field(
        default=None,
        description="Name of .pos file for magnetic field (A/m) from which the solution should be initialized."
        " Should be in the Geometry_xxx/Mesh_xxx/ folder in which the Solution_xxx will be saved.",
    )


# -- Source parameters -- #
class CACRutherfordSolveSourceparametersSineSuperimposedDC(BaseModel):
    """
    Level 5: Class for superimposed DC field or current parameters for the sine source
    """
    field_magnitude: Optional[float] = Field(default=0.0, description="DC field magnitude (T) (direction along y-axis). Solution must be initialized with a non-zero field solution stored in a .pos file if non-zero DC field is used.")
    current_magnitude: Optional[float] = Field(default=0.0, description="DC current magnitude (A). Solution must be initialized with a non-zero field solution stored in a .pos file if non-zero DC current is used.")

class CACRutherfordSolveSourceparametersSine(BaseModel):
    """
    Level 4: Class for Sine source parameters
    """
    frequency: Optional[float] = Field(default=None, description="Frequency of the sine source (Hz).")
    field_amplitude: Optional[float] = Field(default=None, description="Amplitude of the sine field (T).")
    current_amplitude: Optional[float] = Field(default=None, description="Amplitude of the sine current (A).")
    field_angle: Optional[float] = Field(default=90, description="Angle of the sine field direction, with respect to the x-axis (degrees).")
    superimposed_DC: CACRutherfordSolveSourceparametersSineSuperimposedDC = CACRutherfordSolveSourceparametersSineSuperimposedDC()

class CACRutherfordSolveSourceparametersPiecewise(BaseModel):
    """
    Level 4: Class for piecewise (linear) source parameters
    """
    source_csv_file: Optional[str] = Field(default=None, description="File name for the from_file source type defining the time evolution of current and field (in-phase). Multipliers are used for each of them. The file should contain two columns: 'time' (s) and 'value' (field/current (T/A)), with these headers. If this field is set, times, applied_fields_relative and transport_currents_relative are ignored.")
    times: Optional[List[float]] = Field(default=None, description="Time instants (s) defining the piecewise linear sources. Used only if source_csv_file is not set. Can be scaled by time_multiplier.")
    applied_fields_relative: Optional[List[float]] = Field(default=None, description="Applied fields relative to multiplier applied_field_multiplier at the time instants 'times'. Used only if source_csv_file is not set.")
    transport_currents_relative: Optional[List[float]] = Field(default=None, description="Transport currents relative to multiplier transport_current_multiplier at the time instants 'times'. Used only if source_csv_file is not set.")
    time_multiplier: Optional[float] = Field(default=None, description="Multiplier for the time values in times (scales the time values). Also used for the time values in the source_csv_file.")
    applied_field_multiplier: Optional[float] = Field(default=None, description="Multiplier for the applied fields in applied_fields_relative. Also used for the values in the source_csv_file.")
    transport_current_multiplier: Optional[float] = Field(default=None, description="Multiplier for the transport currents in transport_currents_relative. Also used for the values in the source_csv_file.")

class CACRutherfordSolveSourceparameters(BaseModel):
    """
    Level 3: Class for material properties
    """

    source_type: Literal['sine', 'piecewise'] = Field(
        default='sine',
        description="Time evolution of applied current and magnetic field. Supported options are: sine, sine_with_DC, piecewise_linear, from_list.",
    )
    boundary_condition_type: str = Field(
        default="Natural",
        description="Boundary condition type. Supported options are: Natural, Essential. Do not use essential boundary condition with induced currents.",
    )
    sine: CACRutherfordSolveSourceparametersSine = CACRutherfordSolveSourceparametersSine()
    piecewise: CACRutherfordSolveSourceparametersPiecewise = CACRutherfordSolveSourceparametersPiecewise()


# -- Numerical parameters -- #
class CACRutherfordSolveNumericalparametersSine(BaseModel):
    """ 
    Level 4: Numerical parameters corresponding to the sine source
    """
    timesteps_per_period: Optional[float] = Field(default=None, description="Initial value for number of time steps (-) per period for the sine source. Determines the initial time step size.")
    number_of_periods_to_simulate: Optional[float] = Field(default=None, description="Number of periods (-) to simulate for the sine source.")

class CACRutherfordSolveNumericalparametersPiecewise(BaseModel):
    """
    Level 4: Numerical parameters corresponding to the piecewise source
    """
    time_to_simulate: Optional[float] = Field(default=None, description="Total time to simulate (s). Used for the piecewise source.")
    timesteps_per_time_to_simulate: Optional[float] = Field(default=None, description="If variable_max_timestep is False. Number of time steps (-) per period for the piecewise source.")
    force_stepping_at_times_piecewise_linear: bool = Field(default=False, description="If True, time-stepping will contain exactly the time instants that are in the times_source_piecewise_linear list (to avoid truncation maximum applied field/current values).")

    variable_max_timestep: bool = Field(default=False, description="If False, the maximum time step is kept constant through the simulation. If True, it varies according to the piecewise definition.")
    times_max_timestep_piecewise_linear: Optional[List[float]] = Field(default=None, description="Time instants (s) defining the piecewise linear maximum time step.")
    max_timestep_piecewise_linear: Optional[List[float]] = Field(default=None, description="Maximum time steps (s) at the times_max_timestep_piecewise_linear. Above the limits, linear extrapolation of the last two values.")

class CACRutherfordSolveNumericalparameters(BaseModel):
    """
    Level 3: Class for numerical parameters
    """

    sine: CACRutherfordSolveNumericalparametersSine = CACRutherfordSolveNumericalparametersSine()
    piecewise: CACRutherfordSolveNumericalparametersPiecewise = CACRutherfordSolveNumericalparametersPiecewise()


class CACRutherfordSolveFormulationparameters(BaseModel):
    """
    Level 3: Class for finite element formulation parameters
    """

    formulation: Optional[str] = Field(
        default=None, description="Only possible option is linked_flux for the moment"
    )
    dynamic_correction: Optional[bool] = Field(
        default=None,
        description="In the voltage_based case, do we activate the dynamic correction?",
    )
    compute_temperature: bool = Field(
        default=False, description="Do we compute the temperature?"
    )

    two_ell_periodicity : bool = Field(
        default=True, description="True to integrate over twice the shortest periodicity length."
    )


class CACRutherfordSolveFrequencydomainsolverFrequencysweep(BaseModel):
    """
    Level 4: Class for frequency sweep settings
    """
    run_sweep: bool = Field(
        default=False, description="Set True to run a frequency sweep (logarithmic)."
    )
    start_frequency: float = Field(
        default=1, description="Start frequency (Hz) of the sweep."
    )
    end_frequency: float = Field(
        default=100, description="End frequency (Hz) of the sweep."
    )
    number_of_frequencies: int = Field(
        default=10, description="Number of frequencies in the sweep."
    )


    
class CACRutherfordSolveFrequencydomainsolver(BaseModel):
    """
    Level 3: Class for frequency domain solver settings
    """
    enable: bool = Field(
        default=False, description="Set True to enable the frequency domain solver."
    )
    frequency_sweep: CACRutherfordSolveFrequencydomainsolverFrequencysweep = (
        CACRutherfordSolveFrequencydomainsolverFrequencysweep()
    )
    


class CACRutherfordSolve(BaseModel):
    """
    Level 2: Class for FiQuS ConductorAC
    """

    pro_template: Optional[str] = Field(
        default=None, description="Name of the .pro template file."
    )
    conductor_name: Optional[str] = Field(
        default=None, description="Name of the conductor."
    )
    formulation_parameters: CACRutherfordSolveFormulationparameters = (
        CACRutherfordSolveFormulationparameters()
    )
    general_parameters: CACRutherfordSolveGeneralparameters = (
        CACRutherfordSolveGeneralparameters()
    )
    initial_conditions: CACRutherfordSolveInitialConditions = (
        CACRutherfordSolveInitialConditions()
    )
    frequency_domain_solver: CACRutherfordSolveFrequencydomainsolver = (
        CACRutherfordSolveFrequencydomainsolver()
    )
    source_parameters: CACRutherfordSolveSourceparameters = (
        CACRutherfordSolveSourceparameters()
    )
    numerical_parameters: CACRutherfordSolveNumericalparameters = (
        CACRutherfordSolveNumericalparameters()
    )


# ============= POSTPROC ============= #
class CACRutherfordPostprocBatchpostprocLossMapCrossSection(BaseModel):
    """
    Level 5: Class with settings for plotting a cross-section of the loss map.
    """
    plot_cross_section: bool = Field(
        default=False, description="Set True to plot a cross-section of the loss map."
    )
    save_plot: bool = Field(default=False, description="Set True to save the plot.")
    filename: str = Field(default="cross_section", description="Name of the plot file.")
    axis_to_cut: str = Field(
        default="x", description="Axis to cut for the cross-section."
    )
    cut_value: float = Field(
        default=0, description="Value of the axis to cut for the cross-section."
    )

    ylabel: str = Field(default="Loss", description="Label of the y-axis.")
    title: Optional[str] = Field(
        default=None,
        description="Title of the plot. The placeholder <<cut_value>> can be used to indicate the value of the cut axis.",
    )


class CACRutherfordPostprocBatchpostprocLossMapCrossSectionSweep(BaseModel):
    """
    Level 5: Class with settings for animating a cross-section sweep of the loss map along one axis.
    """
    animate_cross_section_sweep: bool = Field(
        default=False,
        description="Set True to animate a cross-section sweep of the loss map along one axis.",
    )
    save_plot: bool = Field(
        default=False, description="Set True to save the animation."
    )
    filename: str = Field(
        default="crossSectionSweep", description="Name of the animation file."
    )
    axis_to_sweep: str = Field(
        default="x", description="Axis to sweep for the animation."
    )
    ylabel: str = Field(default="Loss", description="Label of the y-axis.")
    title: Optional[str] = Field(
        default=None,
        description="Title of the plot. Use <<sweep_value>> to indicate the value of the sweep axis.",
    )


class CACRutherfordPostprocBatchpostprocLossMap(BaseModel):
    """
    Level 4: Class with settings for generating loss maps
    """
    produce_loss_map: bool = Field(
        default=False, description="Set True to produce a loss map."
    )
    save_plot: bool = Field(default=False, description="Set True to save the plot.")
    filename: str = Field(default="loss_map", description="Name of the plot file.")
    x_val: Optional[str] = Field(
        default=None, description="Parameter to be plotted on the x-axis. This field corresponds to a parameter in the input YAML-file. E.g. 'solve.source_parameters.sine.frequency' will plot the loss map for different frequencies."
    )
    y_val: Optional[str] = Field(
        default=None, description="Parameter to be plotted on the y-axis. This field corresponds to a parameter in the input YAML-file. E.g. 'solve.source_parameters.sine.field_amplitude' will plot the loss map for different applied field amplitudes."
    )
    x_steps: int = Field(default=20, description="Number of steps on the x-axis.")
    y_steps: int = Field(default=20, description="Number of steps on the y-axis.")
    loss_type: Literal['TotalLoss', 'FilamentLoss', 'CouplingLoss', 'EddyLoss'] = Field(
        default='TotalLoss',
        description="Type of loss to be plotted. Supported options are: TotalLoss, FilamentLoss, CouplingLoss, EddyLoss."
    )
    x_log: bool = Field(
        default=True, description="Set True to plot x-axis in log-scale."
    )
    y_log: bool = Field(
        default=True, description="Set True to plot y-axis in log-scale."
    )
    loss_log: bool = Field(
        default=True, description="Set True to plot loss in log-scale."
    )
    x_norm: float = Field(default=1, description="Normalization factor for x-axis.")
    y_norm: float = Field(default=1, description="Normalization factor for y-axis.")
    loss_norm: float = Field(default=1, description="Normalization factor for the AC-loss.")
    show_datapoints: bool = Field(
        default=True, description="Set True to show markers for all the datapoints in the loss map."
    )

    title: Optional[str] = Field(default=None, description="Title for the plot.")
    xlabel: Optional[str] = Field(default=None, description="Label for the x-axis.")
    ylabel: Optional[str] = Field(default=None, description="Label for the y-axis.")


    show_loss_type_dominance_contour: bool = Field(
        default=False,
        description="Set True to plot a contour curve separating regions where different loss types dominate. ",
    )

    cross_section: CACRutherfordPostprocBatchpostprocLossMapCrossSection = (
        CACRutherfordPostprocBatchpostprocLossMapCrossSection()
    )
    cross_section_sweep: CACRutherfordPostprocBatchpostprocLossMapCrossSectionSweep = (
        CACRutherfordPostprocBatchpostprocLossMapCrossSectionSweep()
    )


class CACRutherfordPostprocBatchpostprocPlot2d(BaseModel):
    """
    Level 4: Class for 2D plot settings
    """
    produce_plot2d: bool = Field(
        default=False, description="Set True to produce a 2D plot."
    )
    combined_plot: bool = Field(
        default=False,
        description="Set True to produce a combined plot for all simulations. If False, a separate plot is produced for each simulation.",
    )
    save_plot: bool = Field(default=False, description="Set True to save the plot.")
    filename: str = Field(default="plot2d", description="Name of the plot file.")
    x_val: Optional[str] = Field(
        default=None, description="Value to be plotted on the x-axis. Parameters in the input YAML-file and class-variables from the plotter 'SimulationData' class can be accessed trough the notation << . >>. E.g. '<<solve.source_parameters.sine.frequency>>' will create a 2D plot with frequency on the x-axis. '<<time>>' will create a plot with time on the x-axis."
    )
    y_vals: Optional[List[str]] = Field(
        default=None, description=" List of values to be plotted on the y-axis. Parameters in the input YAML-file and class-variables from the plotter 'SimulationData' class can be accessed trough the notation << . >>. E.g. total AC-loss per cycle can be accessed as ['<<total_power_per_cycle['TotalLoss_dyn']>>']."
    )
    labels: Optional[List[str]] = Field(
        default=None,
        description="List of labels for the plot. Each label corresponding to a value in y_val.",
    )
    linestyle: Optional[str] = Field(
        default=None, description="Linestyle for the plot."
    )

    title: Optional[str] = Field(default=None, description="Title for the plot.")
    xlabel: Optional[str] = Field(default=None, description="Label for the x-axis.")
    ylabel: Optional[str] = Field(default=None, description="Label for the y-axis.")
    x_log: bool = Field(default=False, description="Set True to plot x-axis in log-scale.")
    y_log: bool = Field(default=False, description="Set True to plot y-axis in log-scale.")
    legend: bool = Field(default=True, description="Set True to show legend.")


class CACRutherfordPostprocBatchpostprocFilter(BaseModel):
    """
    Level 4: Field for filtering simulations based on simulation parameters for batch post-processing
    """
    apply_filter: bool = Field(
        default=False,
        description="Set True to filter simulations by parameters from the input YAML-file.",
    )
    filter_criterion: Optional[str] = Field(
        default=None,
        description="Criterion used to filter simulations based on simulation parameters. For example will '<<solve.source_parameters.sine.frequency>> > 100' disregard simulations done with frequencies lower than 100Hz.",
    )


class CACRutherfordPostprocBatchpostprocSort(BaseModel):
    """
    Level 4: Field for sorting simulations based on simulation parameters for batch post-processing
    """
    apply_sort: bool = Field(default=False, description="Set True to sort simulations.")
    sort_key: Optional[str] = Field(
        default=None,
        description="Criterion used to sort simulations based on simulation parameters. For example will 'sd.total_power_per_cycle['TotalLoss'] sort simulations based on the total loss.",
    )


class CACRutherfordPostprocBatchpostproc(BaseModel):
    """
    Level 3: Class for batch post-processing settings
    """
    postProc_csv: Optional[str] = Field(
        default=None,
        description="Name of the .csv file for post-processing (without file extension). This file specifies the simulations to be post-processed. The file is structured into three columns, specifying the folder names to access the simulation results: 'input.run.geometry', 'input.run.mesh' and 'input.run.solve'. Each row corresponds to a simulation to be post-processed.",
    )
    output_folder: Optional[str] = Field(
        default=None,
        description="Batch post-processing creates a folder with the given name in the output directory, where all the plots are saved.",
    )
    filter: CACRutherfordPostprocBatchpostprocFilter = CACRutherfordPostprocBatchpostprocFilter()
    sort: CACRutherfordPostprocBatchpostprocSort = CACRutherfordPostprocBatchpostprocSort()
    loss_map: CACRutherfordPostprocBatchpostprocLossMap = CACRutherfordPostprocBatchpostprocLossMap()
    plot2d: CACRutherfordPostprocBatchpostprocPlot2d = CACRutherfordPostprocBatchpostprocPlot2d()


class CACRutherfordPostprocPlotInstPower(BaseModel):
    """
    Level 3: Class with settings for generating plots of instantaneous power
    """
    show: bool = Field(default=False, description="Creates a plot for the calculated instantaneous AC loss (W/m) as a function of time (s).")
    title: str = Field(default="Instantaneous Power", description="Title for the plot.")
    save: bool = Field(default=False, description="Set True to save the plot.")
    save_file_name: str = Field(
        default="instantaneous_power", description="Name of the plot file."
    )


class CACRutherfordPostprocCleanup(BaseModel):
    """
    Level 3: Class for cleanup settings
    """
    remove_pre_file: bool = Field(
        default=False,
        description="Set True to remove the .pre-file after post-processing, to save disk space.",
    )
    remove_res_file: bool = Field(
        default=False,
        description="Set True to remove the .res-file after post-processing, to save disk space.",
    )
    remove_msh_file: bool = Field(
        default=False,
        description="Set True to remove the .msh-file after post-processing, to save disk space.",
    )


class CACRutherfordPostproc(BaseModel):
    """
    Level 2: Class for FiQuS ConductorAC
    """

    generate_pos_files: bool = Field(
        default=True,
        description="Set True to generate .pos-files during post-processing",
    )
    plot_instantaneous_power: CACRutherfordPostprocPlotInstPower = (
        CACRutherfordPostprocPlotInstPower()
    )
    compute_current_per_filament: bool = Field(
        default=False,
        description="Computes current in every filament, with decomposition into magnetization and transport current.",
    )
    save_last_current_density: Optional[str] = Field(
        default=None,
        description="Saves the last current density field solution (out-of-plane) in the file given as a string."
        " The '.pos' extension will be appended to it. Nothing is done if None."
        " This can be for using the current density as an initial condition (but not implemented yet).",
    )
    save_last_magnetic_field: Optional[str] = Field(
        default=None,
        description="Saves the last magnetic field solution (in-plane) in the file given as a string."
        " The '.pos' extension will be appended to it. Nothing is done if None."
        " This is for using the magnetic field as an initial condition for another resolution.",
    )
    cleanup: CACRutherfordPostprocCleanup = CACRutherfordPostprocCleanup()
    batch_postproc: CACRutherfordPostprocBatchpostproc = CACRutherfordPostprocBatchpostproc()


# ============= BASE ============= #
class CACRutherford(BaseModel):
    """
    Level 1: Class for FiQuS ConductorAC
    """

    type: Literal["CACRutherford"]
    geometry: CACRutherfordGeometry = CACRutherfordGeometry()
    mesh: CACRutherfordMesh = CACRutherfordMesh()
    solve: CACRutherfordSolve = CACRutherfordSolve()
    postproc: CACRutherfordPostproc = CACRutherfordPostproc()
