import numpy as np
from pathlib import Path

from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData

from steam_sdk.data.DataPySIGMA import DataPySIGMA, MultipoleRoxieGeometry, MultipoleSettings, MultipoleConductor


class BuilderPySIGMA:
    """
        Class to generate FiQuS models
    """

    def __init__(self, model_data: DataModelMagnet = None, roxie_data=None, path_model_folder=None):
        """
        Object is initialized by defining FiQuS variable structure and file template.
        :param model_data: DataModelMagnet object
        :param roxie_data: RoxieData object
        :param path_model_folder: full path to model folder
        """

        # Data structure
        self.path_model_folder = path_model_folder
        self.data_SIGMA = DataPySIGMA(magnet={'type': model_data.GeneralParameters.magnet_type})
        self.data_SIGMA_geo = MultipoleRoxieGeometry()
        self.data_SIGMA_geo.Roxie_Data = RoxieData(**roxie_data.model_dump())
        self.data_SIGMA_set = MultipoleSettings()
        self.model_data=model_data

        # set file
        self.data_SIGMA_set.Model_Data_GS.general_parameters.I_ref = \
            [model_data.Options_LEDET.field_map_files.Iref] * len(self.data_SIGMA_geo.Roxie_Data.coil.coils)
        for cond in model_data.Conductors:
            self.data_SIGMA_set.Model_Data_GS.conductors[cond.name] = MultipoleConductor(
                cable={'type': cond.cable.type})
            conductor = self.data_SIGMA_set.Model_Data_GS.conductors[cond.name]
            conductor.cable.bare_cable_width = cond.cable.bare_cable_width
            conductor.cable.bare_cable_height_mean = cond.cable.bare_cable_height_mean
            conductor.cable.th_insulation_along_height = cond.cable.th_insulation_along_height
            conductor.cable.th_insulation_along_width = cond.cable.th_insulation_along_width
            if cond.cable.type == "Mono":
                conductor.cable.n_strands = 1
            elif cond.cable.type != "Mono" and cond.cable.n_strands is None :
                print("WARNING! n_strands is set to null. It will be set to a default value of 1 to run SIGMA."
                      " Update model_data.yaml in steam-models to what is found in ROXIE.")
                cond.cable.n_strands = 1
            else:
                conductor.cable.n_strands = cond.cable.n_strands

            # These must be non-zero if we solve for transient
            try:
                conductor.cable.n_strand_layers = cond.cable.n_strand_layers
            except:
                conductor.cable.n_strand_layers = 1

            try:
                conductor.cable.n_strands_per_layers = cond.cable.n_strands_per_layers
            except:
                conductor.cable.n_strands_per_layers = int(conductor.cable.n_strands/conductor.cable.n_strand_layers)



            if cond.cable.type == "Rutherford":
                conductor.cable.Rc = cond.cable.Rc
                conductor.cable.Ra = cond.cable.Ra

                conductor.cable.strand_twist_pitch = cond.cable.strand_twist_pitch
                conductor.cable.width_core = cond.cable.width_core
                conductor.cable.height_core = cond.cable.height_core
                conductor.cable.strand_twist_pitch_angle = cond.cable.strand_twist_pitch_angle

            conductor.cable.bare_cable_height_low = cond.cable.bare_cable_height_low
            conductor.cable.bare_cable_height_high = cond.cable.bare_cable_height_high
            conductor.cable.th_insulation_along_height = cond.cable.th_insulation_along_height
            conductor.cable.th_insulation_along_width = cond.cable.th_insulation_along_width

            conductor.cable.f_inner_voids = cond.cable.f_inner_voids
            conductor.cable.f_outer_voids = cond.cable.f_outer_voids
            conductor.strand.filament_diameter = cond.strand.filament_diameter
            # Diameter is not always present
            try: conductor.strand.diameter = cond.strand.diameter
            except:
                print("WARNING! Diameter not present for this coil. Calculating equivalent diameter using bare_width and bare_height.")
                equivalent_diameter = float(2*np.sqrt(cond.strand.bare_width*cond.strand.bare_height/np.pi))
                conductor.strand.diameter = equivalent_diameter
            conductor.strand.RRR = cond.strand.RRR
            conductor.strand.f_Rho_effective = cond.strand.f_Rho_effective
            conductor.strand.T_ref_RRR_high = cond.strand.T_ref_RRR_high
            conductor.strand.Cu_noCu_in_strand = cond.strand.Cu_noCu_in_strand
            conductor.strand.fil_twist_pitch = cond.strand.fil_twist_pitch
            conductor.Jc_fit.type = cond.Jc_fit.type
            if cond.Jc_fit.type[:4] == 'CUDI':
                conductor.Jc_fit.C1_CUDI1 = cond.Jc_fit.C1_CUDI1
                conductor.Jc_fit.C2_CUDI1 = cond.Jc_fit.C2_CUDI1
            else:
                conductor.Jc_fit.C1_CUDI1 = 0.0
                conductor.Jc_fit.C2_CUDI1 = 0.0


        # --------- sources  ----------
        self.data_SIGMA.Sources.bh_curve_source = str(Path(self.path_model_folder, model_data.Sources.BH_fromROXIE).resolve())

        # --------- general params  ----------
        self.data_SIGMA.GeneralParameters.magnet_name = model_data.GeneralParameters.magnet_name
        self.data_SIGMA.GeneralParameters.T_initial = model_data.GeneralParameters.T_initial
        self.data_SIGMA.GeneralParameters.magnetic_length = model_data.GeneralParameters.magnetic_length

        # --------- power supply  ----------
        self.data_SIGMA.Power_Supply.I_initial = model_data.Power_Supply.I_initial

        # --------- cliq  ----------
        self.data_SIGMA.Quench_Protection.CLIQ.C = model_data.Quench_Protection.CLIQ.C
        self.data_SIGMA.Quench_Protection.CLIQ.L = model_data.Quench_Protection.CLIQ.L
        self.data_SIGMA.Quench_Protection.CLIQ.I0 = model_data.Quench_Protection.CLIQ.I0
        self.data_SIGMA.Quench_Protection.CLIQ.U0 = model_data.Quench_Protection.CLIQ.U0
        self.data_SIGMA.Quench_Protection.CLIQ.t_trigger = model_data.Quench_Protection.CLIQ.t_trigger


        # --------- circuit  ----------

        self.data_SIGMA.Circuit.R_circuit = model_data.Circuit.R_circuit
        self.data_SIGMA.Circuit.L_circuit = model_data.Circuit.L_circuit
        self.data_SIGMA.Circuit.R_parallel = model_data.Circuit.R_parallel

        # --------- quench protection  ----------

        self.data_SIGMA.Quench_Protection.Quench_Heaters.N_strips = model_data.Quench_Protection.Quench_Heaters.N_strips
        self.data_SIGMA.Quench_Protection.Quench_Heaters.t_trigger = model_data.Quench_Protection.Quench_Heaters.t_trigger
        self.data_SIGMA.Quench_Protection.Quench_Heaters.U0 = model_data.Quench_Protection.Quench_Heaters.U0
        self.data_SIGMA.Quench_Protection.Quench_Heaters.C = model_data.Quench_Protection.Quench_Heaters.C
        self.data_SIGMA.Quench_Protection.Quench_Heaters.R_warm = model_data.Quench_Protection.Quench_Heaters.R_warm
        self.data_SIGMA.Quench_Protection.Quench_Heaters.w = model_data.Quench_Protection.Quench_Heaters.w
        self.data_SIGMA.Quench_Protection.Quench_Heaters.h = model_data.Quench_Protection.Quench_Heaters.h
        self.data_SIGMA.Quench_Protection.Quench_Heaters.s_ins = model_data.Quench_Protection.Quench_Heaters.s_ins
        self.data_SIGMA.Quench_Protection.Quench_Heaters.type_ins = model_data.Quench_Protection.Quench_Heaters.type_ins
        self.data_SIGMA.Quench_Protection.Quench_Heaters.s_ins_He = model_data.Quench_Protection.Quench_Heaters.s_ins_He
        self.data_SIGMA.Quench_Protection.Quench_Heaters.type_ins_He = model_data.Quench_Protection.Quench_Heaters.type_ins_He
        self.data_SIGMA.Quench_Protection.Quench_Heaters.l = model_data.Quench_Protection.Quench_Heaters.l
        self.data_SIGMA.Quench_Protection.Quench_Heaters.l_copper = model_data.Quench_Protection.Quench_Heaters.l_copper
        self.data_SIGMA.Quench_Protection.Quench_Heaters.l_stainless_steel = model_data.Quench_Protection.Quench_Heaters.l_stainless_steel
        self.data_SIGMA.Quench_Protection.Quench_Heaters.f_cover = model_data.Quench_Protection.Quench_Heaters.f_cover

        # --------- options sigma  ----------

        self.data_SIGMA.Options_SIGMA.time_vector_solution.time_step = model_data.Options_SIGMA.time_vector_solution.time_step

        self.data_SIGMA.Options_SIGMA.simulation.generate_study = model_data.Options_SIGMA.simulation.generate_study
        self.data_SIGMA.Options_SIGMA.simulation.study_type = model_data.Options_SIGMA.simulation.study_type
        self.data_SIGMA.Options_SIGMA.simulation.make_batch_mode_executable = model_data.Options_SIGMA.simulation.make_batch_mode_executable
        self.data_SIGMA.Options_SIGMA.simulation.nbr_elements_mesh_width = model_data.Options_SIGMA.simulation.nbr_elements_mesh_width
        self.data_SIGMA.Options_SIGMA.simulation.nbr_elements_mesh_height = model_data.Options_SIGMA.simulation.nbr_elements_mesh_height

        self.data_SIGMA.Options_SIGMA.physics.FLAG_M_pers = model_data.Options_SIGMA.physics.FLAG_M_pers
        self.data_SIGMA.Options_SIGMA.physics.FLAG_ifcc = model_data.Options_SIGMA.physics.FLAG_ifcc
        self.data_SIGMA.Options_SIGMA.physics.FLAG_iscc_crossover = model_data.Options_SIGMA.physics.FLAG_iscc_crossover
        self.data_SIGMA.Options_SIGMA.physics.FLAG_iscc_adjw = model_data.Options_SIGMA.physics.FLAG_iscc_adjw
        self.data_SIGMA.Options_SIGMA.physics.FLAG_iscc_adjn = model_data.Options_SIGMA.physics.FLAG_iscc_adjn
        self.data_SIGMA.Options_SIGMA.physics.tauCC_PE = model_data.Options_SIGMA.physics.tauCC_PE

        self.data_SIGMA.Options_SIGMA.quench_initialization.PARAM_time_quench = model_data.Options_SIGMA.quench_initialization.PARAM_time_quench
        self.data_SIGMA.Options_SIGMA.quench_initialization.FLAG_quench_all = model_data.Options_SIGMA.quench_initialization.FLAG_quench_all
        self.data_SIGMA.Options_SIGMA.quench_initialization.FLAG_quench_off = model_data.Options_SIGMA.quench_initialization.FLAG_quench_off
        self.data_SIGMA.Options_SIGMA.quench_initialization.num_qh_div = model_data.Options_SIGMA.quench_initialization.num_qh_div
        self.data_SIGMA.Options_SIGMA.quench_initialization.quench_init_heat = model_data.Options_SIGMA.quench_initialization.quench_init_heat
        self.data_SIGMA.Options_SIGMA.quench_initialization.quench_init_HT = model_data.Options_SIGMA.quench_initialization.quench_init_HT
        self.data_SIGMA.Options_SIGMA.quench_initialization.quench_stop_temp = model_data.Options_SIGMA.quench_initialization.quench_stop_temp

        self.data_SIGMA.Options_SIGMA.postprocessing.out_2D_at_points.coordinate_source = model_data.Options_SIGMA.postprocessing.out_2D_at_points.coordinate_source
        self.data_SIGMA.Options_SIGMA.postprocessing.out_2D_at_points.variables = model_data.Options_SIGMA.postprocessing.out_2D_at_points.variables
        self.data_SIGMA.Options_SIGMA.postprocessing.out_2D_at_points.time = model_data.Options_SIGMA.postprocessing.out_2D_at_points.time
        self.data_SIGMA.Options_SIGMA.postprocessing.out_2D_at_points.map2d = model_data.Sources.magnetic_field_fromROXIE

        self.data_SIGMA.Options_SIGMA.postprocessing.out_2D_at_points.coordinate_source = model_data.Options_SIGMA.postprocessing.out_2D_at_points.coordinate_source
        self.data_SIGMA.Options_SIGMA.postprocessing.out_1D_vs_times.variables = model_data.Options_SIGMA.postprocessing.out_1D_vs_times.variables
        self.data_SIGMA.Options_SIGMA.postprocessing.out_1D_vs_times.time = model_data.Options_SIGMA.postprocessing.out_1D_vs_times.time
        self.data_SIGMA.Options_SIGMA.postprocessing.out_2D_at_points.map2d = model_data.Options_SIGMA.postprocessing.out_2D_at_points.map2d

        self.data_SIGMA.Options_SIGMA.postprocessing.out_1D_vs_all_times.variables = model_data.Options_SIGMA.postprocessing.out_1D_vs_all_times.variables

        self.data_SIGMA.Options_SIGMA.quench_heaters.quench_heater_positions = model_data.Options_SIGMA.quench_heaters.quench_heater_positions
        self.data_SIGMA.Options_SIGMA.quench_heaters.th_coils = model_data.Options_SIGMA.quench_heaters.th_coils
