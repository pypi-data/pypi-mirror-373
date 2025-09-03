def lookupModelDataToLEDET(key: str, mode: str = 'data2ledet'):
    """
        Retrieves the correct LEDET parameter name for a DataModelMagnet input
        The argument mode is used to define the direction, either "data2ledet" or "ledet2data"
    """
    lookup = {
        'GeneralParameters.T_initial': 'T00',
        'GeneralParameters.magnetic_length': 'l_magnet',  # useful when case_model='magnet'
        'GeneralParameters.length_busbar': 'l_magnet',  # useful when case_model='conductor'

        'CoilWindings.conductor_to_group': 'type_to_group',  # TODO: change name, or make it obsolete
        # Note that nT is NOT defined here (at the moment it is read from map2d file)
        'CoilWindings.group_to_coil_section': 'GroupToCoilSection',
        'CoilWindings.polarities_in_group': 'polarities_inGroup',  # TODO Consider removing if removed from DataModelMagnet
        'CoilWindings.half_turn_length': 'l_mag_inGroup',
        'CoilWindings.electrical_pairs.group_together': 'elPairs_GroupTogether',
        'CoilWindings.electrical_pairs.reversed': 'elPairs_RevElOrder',

        # TODO: pancake, solenoid, CCT_Straight, CCT_curve parameters
        # TODO: how to deal with the persistent-currents variables that appear as a matrix in LEDET input file?
        # TODO: how to deal with the fact that Tc0_Nb3Sn_inGroup changes meaning in LEDET depending on the fit type?
        # TODO: how to deal with the fact that Bc2_Nb3Sn_inGroup changes meaning in LEDET depending on the fit type?
        # TODO: how to deal with the fact that Jc_Nb3Sn0_inGroup changes meaning in LEDET depending on the fit type?

        'Circuit.R_circuit': 'R_circuit',
        'Circuit.L_circuit': '',
        'Circuit.R_parallel': '',

        'Power_Supply.I_initial': 'I00',
        'Power_Supply.t_off': 't_PC',
        'Power_Supply.t_control_LUT': 't_PC_LUT',
        'Power_Supply.I_control_LUT': 'I_PC_LUT',
        'Power_Supply.R_crowbar': 'R_crowbar',
        'Power_Supply.Ud_crowbar': 'Ud_crowbar',

        'Quench_Protection.Energy_Extraction.t_trigger': 'tEE',
        'Quench_Protection.Energy_Extraction.R_EE': 'R_EE_triggered',
        'Quench_Protection.Energy_Extraction.power_R_EE': 'R_EE_power',
        'Quench_Protection.Energy_Extraction.initial_energy': 'R_EE_initial_energy',
        'Quench_Protection.Energy_Extraction.max_energy': 'R_EE_max_energy',
        'Quench_Protection.Energy_Extraction.L': '',
        'Quench_Protection.Energy_Extraction.C': '',

        'Quench_Protection.Quench_Heaters.N_strips': '',
        # TODO: change logic to avoid relying on "Heater strips per type", i.e. type_QH
        'Quench_Protection.Quench_Heaters.t_trigger': 'tQH',
        'Quench_Protection.Quench_Heaters.U0': 'U0_QH',
        'Quench_Protection.Quench_Heaters.C': 'C_QH',
        'Quench_Protection.Quench_Heaters.R_warm': 'R_warm_QH',
        'Quench_Protection.Quench_Heaters.w': 'w_QH',
        'Quench_Protection.Quench_Heaters.h': 'h_QH',
        'Quench_Protection.Quench_Heaters.s_ins': 's_ins_QH',
        'Quench_Protection.Quench_Heaters.type_ins': 'type_ins_QH',
        'Quench_Protection.Quench_Heaters.s_ins_He': 's_ins_QH_He',
        'Quench_Protection.Quench_Heaters.type_ins_He': 'type_ins_QH_He',
        'Quench_Protection.Quench_Heaters.l': 'l_QH',
        'Quench_Protection.Quench_Heaters.f_cover': 'f_QH',
        'Quench_Protection.Quench_Heaters.iQH_toHalfTurn_From': 'iQH_toHalfTurn_From',
        'Quench_Protection.Quench_Heaters.iQH_toHalfTurn_To': 'iQH_toHalfTurn_To',

        'Quench_Protection.CLIQ.t_trigger': 'tCLIQ',
        'Quench_Protection.CLIQ.current_direction': 'directionCurrentCLIQ',
        'Quench_Protection.CLIQ.sym_factor': '',
        'Quench_Protection.CLIQ.N_units': 'nCLIQ',
        'Quench_Protection.CLIQ.U0': 'U0',
        'Quench_Protection.CLIQ.C': 'C',
        'Quench_Protection.CLIQ.R': 'Rcapa',
        'Quench_Protection.CLIQ.L': '',
        'Quench_Protection.CLIQ.I0': '',

        'Quench_Protection.ESC.t_trigger': 'tESC',
        'Quench_Protection.ESC.U0': 'U0_ESC',
        'Quench_Protection.ESC.C': 'C_ESC',
        'Quench_Protection.ESC.R_unit': 'R_ESC_unit',
        'Quench_Protection.ESC.R_leads': 'R_ESC_leads',
        'Quench_Protection.ESC.Ud_Diode': 'Ud_Diode_ESC',

        'Options_LEDET.time_vector.time_vector_params': 'time_vector_params',

        'Options_LEDET.magnet_inductance.flag_calculate_inductance': 'flag_calculate_inductance',
        'Options_LEDET.magnet_inductance.overwrite_inductance_coil_sections': 'overwrite_inductance_coil_sections',
        'Options_LEDET.magnet_inductance.overwrite_HalfTurnToInductanceBlock': 'overwrite_HalfTurnToInductanceBlock',
        'Options_LEDET.magnet_inductance.LUT_DifferentialInductance_current': 'fL_I',
        'Options_LEDET.magnet_inductance.LUT_DifferentialInductance_inductance': 'fL_L',

        'Options_LEDET.heat_exchange.heat_exchange_max_distance': 'heat_exchange_max_distance',
        'Options_LEDET.heat_exchange.iContactAlongWidth_pairs_to_add': 'iContactAlongWidth_pairs_to_add',
        'Options_LEDET.heat_exchange.iContactAlongWidth_pairs_to_remove': 'iContactAlongWidth_pairs_to_remove',
        'Options_LEDET.heat_exchange.iContactAlongHeight_pairs_to_add': 'iContactAlongHeight_pairs_to_add',
        'Options_LEDET.heat_exchange.iContactAlongHeight_pairs_to_remove': 'iContactAlongHeight_pairs_to_remove',
        'Options_LEDET.heat_exchange.th_insulationBetweenLayers': 'th_insulationBetweenLayers',

        'Options_LEDET.conductor_geometry_used_for_ISCL.alphaDEG_ht': 'alphasDEG',
        'Options_LEDET.conductor_geometry_used_for_ISCL.rotation_ht': 'rotation_block',
        'Options_LEDET.conductor_geometry_used_for_ISCL.mirror_ht': 'mirror_block',
        'Options_LEDET.conductor_geometry_used_for_ISCL.mirrorY_ht': 'mirrorY_block',

        'Options_LEDET.field_map_files.Iref': 'Iref',
        'Options_LEDET.field_map_files.flagIron': 'flagIron',
        'Options_LEDET.field_map_files.flagSelfField': 'flagSelfField',
        'Options_LEDET.field_map_files.headerLines': 'headerLines',
        'Options_LEDET.field_map_files.columnsXY': 'columnsXY',
        'Options_LEDET.field_map_files.columnsBxBy': 'columnsBxBy',
        'Options_LEDET.field_map_files.flagPlotMTF': 'flagPlotMTF',
        'Options_LEDET.field_map_files.fieldMapNumber': 'fieldMapNumber',
        'Options_LEDET.field_map_files.flag_calculateMagneticField': 'flag_calculateMagneticField',

        'Options_LEDET.input_generation_options.flag_typeWindings': 'flag_typeWindings',
        'Options_LEDET.input_generation_options.flag_calculateInductanceMatrix': 'flag_calculateInductanceMatrix',
        'Options_LEDET.input_generation_options.flag_useExternalInitialization': 'flag_useExternalInitialization',
        'Options_LEDET.input_generation_options.flag_initializeVar': 'flag_initializeVar',
        'Options_LEDET.input_generation_options.selfMutualInductanceFileNumber': 'selfMutualInductanceFileNumber',

        'Options_LEDET.simulation.flag_fastMode': 'flag_fastMode',
        'Options_LEDET.simulation.flag_controlCurrent': 'flag_controlCurrent',
        'Options_LEDET.simulation.flag_controlInductiveVoltages': 'flag_controlInductiveVoltages', 
        'Options_LEDET.simulation.flag_controlMagneticField': 'flag_controlMagneticField',
        'Options_LEDET.simulation.flag_controlBoundaryTemperatures': 'flag_controlBoundaryTemperatures',
        'Options_LEDET.simulation.flag_automaticRefinedTimeStepping': 'flag_automaticRefinedTimeStepping',

        'Options_LEDET.STEAM_Material_Properties.STEAM_material_properties_set': 'material_properties_set',

        'Options_LEDET.physics.flag_IronSaturation': 'flag_IronSaturation',
        'Options_LEDET.physics.flag_InvertCurrentsAndFields': 'flag_InvertCurrentsAndFields',
        'Options_LEDET.physics.flag_ScaleDownSuperposedMagneticField': 'flag_ScaleDownSuperposedMagneticField',
        'Options_LEDET.physics.flag_HeCooling': 'flag_HeCooling',
        'Options_LEDET.physics.fScaling_Pex': 'fScaling_Pex',
        'Options_LEDET.physics.fScaling_Pex_AlongHeight': 'fScaling_Pex_AlongHeight',
        'Options_LEDET.physics.flag_disableHeatExchangeBetweenCoilSections': 'flag_disableHeatExchangeBetweenCoilSections',
        'Options_LEDET.physics.fScaling_MR': 'fScaling_MR',
        'Options_LEDET.physics.flag_scaleCoilResistance_StrandTwistPitch': 'flag_scaleCoilResistance_StrandTwistPitch',
        'Options_LEDET.physics.flag_separateInsulationHeatCapacity': 'flag_separateInsulationHeatCapacity',
        'Options_LEDET.physics.flag_persistentCurrents': 'flag_persistentCurrents',
        'Options_LEDET.physics.flag_ISCL': 'flag_ISCL',
        'Options_LEDET.physics.fScaling_Mif': 'fScaling_Mif',
        'Options_LEDET.physics.fScaling_Mis': 'fScaling_Mis',
        'Options_LEDET.physics.flag_StopIFCCsAfterQuench': 'flag_StopIFCCsAfterQuench',
        'Options_LEDET.physics.flag_StopISCCsAfterQuench': 'flag_StopISCCsAfterQuench',
        'Options_LEDET.physics.tau_increaseRif': 'tau_increaseRif',
        'Options_LEDET.physics.tau_increaseRis': 'tau_increaseRis',
        'Options_LEDET.physics.fScaling_RhoSS': 'fScaling_RhoSS',
        'Options_LEDET.physics.maxVoltagePC': 'maxVoltagePC',
        'Options_LEDET.physics.minCurrentDiode': 'minCurrentDiode',
        'Options_LEDET.physics.flag_symmetricGroundingEE': 'flag_symmetricGroundingEE',
        'Options_LEDET.physics.flag_removeUc': 'flag_removeUc',
        'Options_LEDET.physics.BtX_background': 'BtX_background',
        'Options_LEDET.physics.BtY_background': 'BtY_background',

        'Options_LEDET.quench_initiation.iStartQuench': 'iStartQuench',
        'Options_LEDET.quench_initiation.tStartQuench': 'tStartQuench',
        'Options_LEDET.quench_initiation.lengthHotSpot_iStartQuench': 'lengthHotSpot_iStartQuench',
        'Options_LEDET.quench_initiation.fScaling_vQ_iStartQuench': 'fScaling_vQ_iStartQuench',

        'Options_LEDET.post_processing.flag_showFigures': 'flag_showFigures',
        'Options_LEDET.post_processing.flag_saveFigures': 'flag_saveFigures',
        'Options_LEDET.post_processing.flag_saveMatFile': 'flag_saveMatFile',
        'Options_LEDET.post_processing.flag_saveTxtFiles': 'flag_saveTxtFiles',
        'Options_LEDET.post_processing.flag_saveResultsToMesh': 'flag_saveResultsToMesh',
        'Options_LEDET.post_processing.flag_generateReport': 'flag_generateReport',
        'Options_LEDET.post_processing.tQuench': 'tQuench',
        'Options_LEDET.post_processing.initialQuenchTemp': 'initialQuenchTemp',
        'Options_LEDET.post_processing.flag_hotSpotTemperatureInEachGroup': 'flag_hotSpotTemperatureInEachGroup',
        'Options_LEDET.post_processing.flag_importFieldWhenCalculatingHotSpotT': 'flag_importFieldWhenCalculatingHotSpotT',

        'Options_LEDET.simulation_3D.flag_3D': 'flag_3D',
        'Options_LEDET.simulation_3D.flag_adaptiveTimeStepping': 'flag_adaptiveTimeStepping',
        'Options_LEDET.simulation_3D.sim3D_flag_Import3DGeometry': 'sim3D_flag_Import3DGeometry',
        'Options_LEDET.simulation_3D.sim3D_import3DGeometry_modelNumber': 'sim3D_import3DGeometry_modelNumber',
        'Options_LEDET.simulation_3D.sim3D_uThreshold': 'sim3D_uThreshold',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_down': 'sim3D_f_cooling_down',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_up': 'sim3D_f_cooling_up',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_left': 'sim3D_f_cooling_left',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_right': 'sim3D_f_cooling_right',
        'Options_LEDET.simulation_3D.sim3D_f_cooling_LeadEnds': 'sim3D_f_cooling_LeadEnds',
        'Options_LEDET.simulation_3D.sim3D_fExToIns': 'sim3D_fExToIns',
        'Options_LEDET.simulation_3D.sim3D_fExUD': 'sim3D_fExUD',
        'Options_LEDET.simulation_3D.sim3D_fExLR': 'sim3D_fExLR',
        'Options_LEDET.simulation_3D.sim3D_min_ds_coarse': 'sim3D_min_ds_coarse',
        'Options_LEDET.simulation_3D.sim3D_min_ds_fine': 'sim3D_min_ds_fine',
        'Options_LEDET.simulation_3D.sim3D_min_nodesPerStraightPart': 'sim3D_min_nodesPerStraightPart',
        'Options_LEDET.simulation_3D.sim3D_min_nodesPerEndsPart': 'sim3D_min_nodesPerEndsPart',
        'Options_LEDET.simulation_3D.sim3D_idxFinerMeshHalfTurn': 'sim3D_idxFinerMeshHalfTurn',
        'Options_LEDET.simulation_3D.sim3D_flag_checkNodeProximity': 'sim3D_flag_checkNodeProximity',
        'Options_LEDET.simulation_3D.sim3D_nodeProximityThreshold': 'sim3D_nodeProximityThreshold',
        'Options_LEDET.simulation_3D.sim3D_Tpulse_sPosition': 'sim3D_Tpulse_sPosition',
        'Options_LEDET.simulation_3D.sim3D_Tpulse_peakT': 'sim3D_Tpulse_peakT',
        'Options_LEDET.simulation_3D.sim3D_Tpulse_width': 'sim3D_Tpulse_width',
        'Options_LEDET.simulation_3D.sim3D_tShortCircuit': 'sim3D_tShortCircuit',
        'Options_LEDET.simulation_3D.sim3D_coilSectionsShortCircuit': 'sim3D_coilSectionsShortCircuit',
        'Options_LEDET.simulation_3D.sim3D_R_shortCircuit': 'sim3D_R_shortCircuit',
        'Options_LEDET.simulation_3D.sim3D_shortCircuitPosition': 'sim3D_shortCircuitPosition',
        'Options_LEDET.simulation_3D.sim3D_durationGIF': 'sim3D_durationGIF',
        'Options_LEDET.simulation_3D.sim3D_flag_saveFigures': 'sim3D_flag_saveFigures',
        'Options_LEDET.simulation_3D.sim3D_flag_saveGIF': 'sim3D_flag_saveGIF',
        'Options_LEDET.simulation_3D.sim3D_flag_VisualizeGeometry3D': 'sim3D_flag_VisualizeGeometry3D',
        'Options_LEDET.simulation_3D.sim3D_flag_SaveGeometry3D': 'sim3D_flag_SaveGeometry3D',

        'Options_LEDET.plots.suffixPlot': 'suffixPlot',
        'Options_LEDET.plots.typePlot': 'typePlot',
        'Options_LEDET.plots.outputPlotSubfolderPlot': 'outputPlotSubfolderPlot',
        'Options_LEDET.plots.variableToPlotPlot': 'variableToPlotPlot',
        'Options_LEDET.plots.selectedStrandsPlot': 'selectedStrandsPlot',
        'Options_LEDET.plots.selectedTimesPlot': 'selectedTimesPlot',
        'Options_LEDET.plots.labelColorBarPlot': 'labelColorBarPlot',
        'Options_LEDET.plots.minColorBarPlot': 'minColorBarPlot',
        'Options_LEDET.plots.maxColorBarPlot': 'maxColorBarPlot',
        'Options_LEDET.plots.MinMaxXYPlot': 'MinMaxXYPlot',
        'Options_LEDET.plots.flagSavePlot': 'flagSavePlot',
        'Options_LEDET.plots.flagColorPlot': 'flagColorPlot',
        'Options_LEDET.plots.flagInvisiblePlot': 'flagInvisiblePlot',

        'Options_LEDET.variables_to_save.variableToSaveTxt': 'variableToSaveTxt',
        'Options_LEDET.variables_to_save.typeVariableToSaveTxt': 'typeVariableToSaveTxt',
        'Options_LEDET.variables_to_save.variableToInitialize': 'variableToInitialize',
        'Options_LEDET.variables_to_save.writeToMesh_fileNameMeshPositions': 'writeToMesh_fileNameMeshPositions',
        'Options_LEDET.variables_to_save.writeToMesh_suffixFileNameOutput': 'writeToMesh_suffixFileNameOutput',
        'Options_LEDET.variables_to_save.writeToMesh_selectedVariables': 'writeToMesh_selectedVariables',
        'Options_LEDET.variables_to_save.writeToMesh_selectedTimeSteps': 'writeToMesh_selectedTimeSteps',
        'Options_LEDET.variables_to_save.writeToMesh_selectedMethod': 'writeToMesh_selectedMethod',
    }

    if mode == 'data2ledet':
        returned_key = lookup[key] if key in lookup else None
    elif mode == 'ledet2data':
        # Generate an inverted dictionary
        lookup_inverted = {v: k for k, v in lookup.items()}
        returned_key = lookup_inverted[key] if key in lookup_inverted else None

    return returned_key


def lookupWindings(key: int, mode: str = 'data2ledet'):
    """
        Retrieves the correct LEDET parameter name for a DataModelMagnet input
    """
    magnet_type = {
        'multipole': 0,
        'solenoid' : 1,
        'CCT_straight': 2,
        'CWS': 3,
        'busbar'   : 101
    }

    if mode == 'data2ledet':
        returned_key = magnet_type[key] if key in magnet_type else None
    elif mode == 'ledet2data':
        # Generate an inverted dictionary
        lookup_inverted = {v: k for k, v in magnet_type.items()}
        returned_key = lookup_inverted[key] if key in lookup_inverted else None

    return returned_key


def lookupSuperconductor(key: str):
    """
        Retrieves the correct numerical value for a superconductor input string
    """
    superconductor = {
        "Nb-Ti": 1, "NbTi": 1,
        "Nb3Sn (Summer's fit)": 2, "Nb3Sn (Summers' fit)": 2, "Nb3Sn (Summers's fit)": 2,
        "Nb3Sn": 2, "NB3SN": 2, # TODO: Note that these entries "Nb3Sn" and "NB3SN" are ambiguous (since they could refer to Nb3Sn with Summers' fit or with Bordini's fit) and they are dealt with in the method BuilderLEDET.loadStrandData()
        "BSCCO2212": 3,
        "Nb3Sn(Bordini's fit)": 4, "Nb3Sn (Bordini's fit)": 4
    }
    return superconductor[key] if key in superconductor else None


def lookupStabilizer(key: str):
    """
        Retrieves the correct numerical value for a stabilizer input string
    """
    stabilizer = {
        'Cu': 1,
        'Ag': 2,
        'SS': 3, 'Stainless steel': 3, 'stainless steel': 3, 'Stainless Steel': 3,
        'Fe': 4,
        'BeCu': 5
    }
    return stabilizer[key] if key in stabilizer else None


def lookupInsulation(key: str):
    """
        Retrieves the correct numerical value for a insulation input string
    """
    insulation = {
        'G10': 1,
        'Kapton': 2, 'kapton': 2, 'KAPTON': 2,
        'Helium': 3, 'helium': 3, 'HELIUM': 3,
        'Void': 4, 'void': 4, 'VOID': 4
    }
    return insulation[key] if key in insulation else None


def lookupFitCableForPersistentCurrents(key: str):
    """
        Retrieves the correct numerical value for a persistent-currents Jc fit input string
    """
    fitcablepc = {
        'Jc=constant': 1, 'Jc = constant': 1, 'Jc=const': 1, 'Jc = const': 1,
        'Nb-Ti Bottura': 2, 'NbTi Bottura': 2,
        'Nb-Ti CUDI': 3, 'Nb-Ti CUDI1': 3, 'NbTi CUDI': 3, 'NbTi CUDI1': 3,
        'Nb3Sn (Summer\'s fit)': 4
    }
    return fitcablepc[key] if key in fitcablepc else None


def lookupMatProSet(key: str):
    """
        Retrieves the correct numerical value for a STEAM Material Properties input string
    """
    dict_input = {
        'm': 1, '.m': 1,
        'mex': 2, '.mex': 2,
    }
    return dict_input[key] if key in dict_input else None
