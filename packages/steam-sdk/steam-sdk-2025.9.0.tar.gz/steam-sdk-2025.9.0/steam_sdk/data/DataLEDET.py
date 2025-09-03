import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Union

"""
    These classes define the four LEDET dataclasses, which contain the variables to write in the four sheets of a LEDET 
    input file: Inputs, Options, Plots and Variables.
"""
@dataclass
class LEDETInputs:
    T00: Optional[float] = None
    l_magnet: Optional[float] = None
    I00: Optional[float] = None
    GroupToCoilSection: np.ndarray = field(default_factory=lambda: np.array([]))
    polarities_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    nT: np.ndarray = field(default_factory=lambda: np.array([]))
    nStrands_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    l_mag_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    ds_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
     # Start new keys for TFMData
    dfilamentary_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    dcore_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    # End new keys for TFMData
    f_SC_strand_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    f_ro_eff_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Lp_f_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    RRR_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    SCtype_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    STtype_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    insulationType_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    internalVoidsType_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    externalVoidsType_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    wBare_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    hBare_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    wIns_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    hIns_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Lp_s_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    R_c_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Tc0_NbTi_ht_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Bc2_NbTi_ht_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    c1_Ic_NbTi_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    c2_Ic_NbTi_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Tc0_Nb3Sn_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Bc2_Nb3Sn_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    Jc_Nb3Sn0_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    alpha_Nb3Sn_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    f_scaling_Jc_BSCCO2212_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    df_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    selectedFit_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    fitParameters_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    overwrite_f_internalVoids_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    overwrite_f_externalVoids_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    alphasDEG: np.ndarray = field(default_factory=lambda: np.array([]))
    rotation_block: np.ndarray = field(default_factory=lambda: np.array([]))
    mirror_block: np.ndarray = field(default_factory=lambda: np.array([]))
    mirrorY_block: np.ndarray = field(default_factory=lambda: np.array([]))
    el_order_half_turns: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongWidth_From: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongWidth_To: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongHeight_From: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongHeight_To: np.ndarray = field(default_factory=lambda: np.array([]))
    t_PC: Optional[float] = None
    t_PC_LUT: np.ndarray = field(default_factory=lambda: np.array([]))
    I_PC_LUT: np.ndarray = field(default_factory=lambda: np.array([]))
    R_circuit: Optional[float] = None
    R_crowbar: Optional[float] = None
    Ud_crowbar: Optional[float] = None
    tEE: Optional[float] = None
    R_EE_triggered: Union[Optional[float], np.ndarray] = None
    R_EE_power: Optional[float] = None
    R_EE_initial_energy: Optional[float] = None
    R_EE_max_energy: Optional[float] = None
    tCLIQ: np.ndarray = None
    directionCurrentCLIQ: np.ndarray = field(default_factory=lambda: np.array([]))
    nCLIQ: np.ndarray = field(default_factory=lambda: np.array([]))
    U0: np.ndarray = field(default_factory=lambda: np.array([]))
    C: np.ndarray = field(default_factory=lambda: np.array([]))
    Rcapa: np.ndarray = field(default_factory=lambda: np.array([]))
    tESC: np.ndarray = field(default_factory=lambda: np.array([]))
    U0_ESC: np.ndarray = field(default_factory=lambda: np.array([]))
    C_ESC: np.ndarray = field(default_factory=lambda: np.array([]))
    R_ESC_unit: np.ndarray = field(default_factory=lambda: np.array([]))
    R_ESC_leads: np.ndarray = field(default_factory=lambda: np.array([]))
    Ud_Diode_ESC: np.ndarray = field(default_factory=lambda: np.array([]))
    tQH: np.ndarray = field(default_factory=lambda: np.array([]))
    U0_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    C_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    R_warm_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    w_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    h_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    s_ins_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    type_ins_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    s_ins_QH_He: np.ndarray = field(default_factory=lambda: np.array([]))
    type_ins_QH_He: np.ndarray = field(default_factory=lambda: np.array([]))
    l_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    f_QH: np.ndarray = field(default_factory=lambda: np.array([]))
    iQH_toHalfTurn_From: np.ndarray = field(default_factory=lambda: np.array([]))
    iQH_toHalfTurn_To: np.ndarray = field(default_factory=lambda: np.array([]))
    tQuench: np.ndarray = field(default_factory=lambda: np.array([]))
    initialQuenchTemp: np.ndarray = field(default_factory=lambda: np.array([]))
    iStartQuench: np.ndarray = field(default_factory=lambda: np.array([1]))
    tStartQuench: np.ndarray = field(default_factory=lambda: np.array([]))
    lengthHotSpot_iStartQuench: np.ndarray = field(default_factory=lambda: np.array([]))
    fScaling_vQ_iStartQuench: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_uThreshold: Optional[float] = None
    sim3D_f_cooling_down: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_f_cooling_up: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_f_cooling_left: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_f_cooling_right: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_f_cooling_LeadEnds: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_fExToIns: Optional[float] = None
    sim3D_fExUD: Optional[float] = None
    sim3D_fExLR: Optional[float] = None
    sim3D_min_ds_coarse: Optional[float] = None
    sim3D_min_ds_fine: Optional[float] = None
    sim3D_min_nodesPerStraightPart: Optional[int] = None
    sim3D_min_nodesPerEndsPart: Optional[int] = None
    sim3D_idxFinerMeshHalfTurn: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_flag_checkNodeProximity: Optional[int] = None
    sim3D_nodeProximityThreshold: Optional[float] = None
    sim3D_Tpulse_sPosition: Optional[float] = None
    sim3D_Tpulse_peakT: Optional[float] = None
    sim3D_Tpulse_width: Optional[float] = None
    sim3D_tShortCircuit: Optional[float] = None
    sim3D_coilSectionsShortCircuit: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_R_shortCircuit: Optional[float] = None
    sim3D_shortCircuitPosition: np.ndarray = field(default_factory=lambda: np.array([]))
    sim3D_durationGIF: Optional[float] = None
    sim3D_flag_saveFigures: Optional[int] = None
    sim3D_flag_saveGIF: Optional[int] = None
    sim3D_flag_VisualizeGeometry3D: Optional[int] = None
    sim3D_flag_SaveGeometry3D: Optional[int] = None
    M_m: np.ndarray = field(default_factory=lambda: np.array([]))
    fL_I: np.ndarray = field(default_factory=lambda: np.array([]))
    fL_L: np.ndarray = field(default_factory=lambda: np.array([]))
    HalfTurnToInductanceBlock: np.ndarray = field(default_factory=lambda: np.array([]))
    M_InductanceBlock_m: np.ndarray = field(default_factory=lambda: np.array([]))

    f_RRR1_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    f_RRR2_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    f_RRR3_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    RRR1_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    RRR2_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    RRR3_Cu_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class LEDETOptions:
    time_vector_params: np.ndarray = field(default_factory=lambda: np.array([]))
    Iref: Optional[float] = None
    flagIron: Optional[int] = None
    flagSelfField: Optional[int] = None
    headerLines: Optional[int] = None
    columnsXY: np.ndarray = field(default_factory=lambda: np.array([]))
    columnsBxBy: np.ndarray = field(default_factory=lambda: np.array([]))
    flagPlotMTF: Optional[int] = None
    fieldMapNumber: Optional[int] = None
    flag_calculateMagneticField: Optional[int] = None
    flag_typeWindings: Optional[int] = None
    flag_calculateInductanceMatrix: Optional[int] = None
    flag_useExternalInitialization: Optional[int] = None
    flag_initializeVar: Optional[int] = None
    selfMutualInductanceFileNumber: Optional[int] = None
    flag_fastMode: Optional[int] = None
    flag_controlCurrent: Optional[int] = None
    flag_controlInductiveVoltages: Optional[int] = None
    flag_controlMagneticField: Optional[int] = None
    flag_controlBoundaryTemperatures: Optional[int] = None
    flag_automaticRefinedTimeStepping: Optional[int] = None
    material_properties_set: Optional[int] = None
    flag_IronSaturation: Optional[int] = None
    flag_InvertCurrentsAndFields: Optional[int] = None
    flag_ScaleDownSuperposedMagneticField: Optional[int] = None
    flag_HeCooling: Optional[int] = None
    fScaling_Pex: Optional[float] = None
    fScaling_Pex_AlongHeight: Optional[float] = None
    flag_disableHeatExchangeBetweenCoilSections: Optional[int] = None
    fScaling_MR: Optional[float] = None
    flag_scaleCoilResistance_StrandTwistPitch: Optional[int] = None
    flag_separateInsulationHeatCapacity: Optional[int] = None
    flag_persistentCurrents: Optional[int] = None
    Jc_SC_max: Optional[float] = None
    deltaB_PC: Optional[float] = None
    flag_ISCL: Optional[int] = None
    fScaling_Mif: Optional[float] = None
    fScaling_Mis: Optional[float] = None
    flag_StopIFCCsAfterQuench: Optional[int] = None
    flag_StopISCCsAfterQuench: Optional[int] = None
    tau_increaseRif: Optional[float] = None
    tau_increaseRis: Optional[float] = None
    fScaling_RhoSS: Optional[float] = None
    maxVoltagePC: Optional[float] = None
    minCurrentDiode: Optional[float] = None
    flag_symmetricGroundingEE: Optional[int] = None
    flag_removeUc: Optional[int] = None
    BtX_background: Optional[float] = None
    BtY_background: Optional[float] = None
    flag_showFigures: Optional[int] = None
    flag_saveFigures: Optional[int] = None
    flag_saveMatFile: Optional[int] = None
    flag_saveTxtFiles: Optional[int] = None
    flag_saveResultsToMesh: Optional[int] = None
    flag_generateReport: Optional[int] = None
    flag_hotSpotTemperatureInEachGroup: Optional[int] = None
    flag_importFieldWhenCalculatingHotSpotT: Optional[int] = None
    flag_3D: Optional[int] = None
    flag_adaptiveTimeStepping: Optional[int] = None
    sim3D_flag_Import3DGeometry: Optional[int] = None
    sim3D_import3DGeometry_modelNumber: Optional[int] = None

@dataclass
class LEDETPlots:
    suffixPlot: str = ''
    typePlot: Optional[int] = None
    outputPlotSubfolderPlot: str = ''
    variableToPlotPlot: np.ndarray = field(default_factory=lambda: np.array([]))
    selectedStrandsPlot: np.ndarray = field(default_factory=lambda: np.array([]))
    selectedTimesPlot: np.ndarray = field(default_factory=lambda: np.array([]))
    labelColorBarPlot: np.ndarray = field(default_factory=lambda: np.array([]))
    minColorBarPlot: Optional[float] = None
    maxColorBarPlot: Optional[float] = None
    MinMaxXYPlot: np.ndarray = field(default_factory=lambda: np.array([]))
    flagSavePlot: Optional[int] = None
    flagColorPlot: Optional[int] = None
    flagInvisiblePlot: Optional[int] = None

@dataclass
class LEDETVariables:
    variableToSaveTxt: np.ndarray = field(default_factory=lambda: np.array([]))
    typeVariableToSaveTxt: np.ndarray = field(default_factory=lambda: np.array([]))
    variableToInitialize: np.ndarray = field(default_factory=lambda: np.array([]))
    writeToMesh_fileNameMeshPositions: np.ndarray = field(default_factory=lambda: np.array([]))
    writeToMesh_suffixFileNameOutput: np.ndarray = field(default_factory=lambda: np.array([]))
    writeToMesh_selectedVariables: np.ndarray = field(default_factory=lambda: np.array([]))
    writeToMesh_selectedTimeSteps: np.ndarray = field(default_factory=lambda: np.array([]))
    writeToMesh_selectedMethod: np.ndarray = field(default_factory=lambda: np.array([]))

@dataclass
class LEDETAuxiliary:
    # The following parameters are needed for conductor ordering
    strandToHalfTurn: np.ndarray = field(default_factory=lambda: np.array([]))
    strandToGroup: np.ndarray = field(default_factory=lambda: np.array([]))
    indexTstart: np.ndarray = field(default_factory=lambda: np.array([]))
    indexTstop: np.ndarray = field(default_factory=lambda: np.array([]))
    # The following parameters are needed for conductor definition
    type_to_group: np.ndarray = field(default_factory=lambda: np.array([]))  # TODO: change name, or make it obsolete
    f_SC_strand_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))  # TODO: decide whether to implement calculation in BuilderLEDET()
    f_ST_strand_inGroup: np.ndarray = field(default_factory=lambda: np.array([]))  # TODO: decide whether to implement calculation in BuilderLEDET()
    # The following parameters are needed for thermal links calculation and options
    elPairs_GroupTogether: np.ndarray = field(default_factory=lambda: np.array([]))
    elPairs_RevElOrder: np.ndarray = field(default_factory=lambda: np.array([]))
    heat_exchange_max_distance: Optional[float] = None
    iContactAlongWidth_pairs_to_add: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongWidth_pairs_to_remove: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongHeight_pairs_to_add: np.ndarray = field(default_factory=lambda: np.array([]))
    iContactAlongHeight_pairs_to_remove: np.ndarray = field(default_factory=lambda: np.array([]))
    th_insulationBetweenLayers: np.ndarray = field(default_factory=lambda: np.array([]))
    # The following parameters are needed for by-passing self-mutual inductance calculation
    flag_calculate_inductance: Optional[bool] = None
    overwrite_inductance_coil_sections: np.ndarray = field(default_factory=lambda: np.array([[]]))
    overwrite_HalfTurnToInductanceBlock: np.ndarray = field(default_factory=lambda: np.array([[]]))
    # The following parameters are needed for self-mutual inductance calculation
    nStrands_inGroup_ROXIE: np.ndarray = field(default_factory=lambda: np.array([]))
    x_strands: np.ndarray = field(default_factory=lambda: np.array([]))  # TODO: add correct keys based on the ParserROXIE() parameters
    y_strands: np.ndarray = field(default_factory=lambda: np.array([]))  # TODO: add correct keys based on the ParserROXIE() parameters
    I_strands: np.ndarray = field(default_factory=lambda: np.array([]))  # TODO: add correct keys based on the ParserROXIE() parameters
    Bx: np.ndarray = field(default_factory=lambda: np.array([])) 
    By: np.ndarray = field(default_factory=lambda: np.array([])) 
