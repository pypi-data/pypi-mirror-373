from pydantic import BaseModel, Field
from typing import List, Union, Optional

class TimeVectorLEDET(BaseModel):
    """
        Level 2: Class for simulation time vector in LEDET
    """
    time_vector_params: List[float] = []


class MagnetInductance(BaseModel):
    """
        Level 2: Class for magnet inductance assignment
    """
    flag_calculate_inductance: Optional[bool] = None
    overwrite_inductance_coil_sections: List[List[float]] = [[]]
    overwrite_HalfTurnToInductanceBlock: List[int] = []
    LUT_DifferentialInductance_current: List[float] = []
    LUT_DifferentialInductance_inductance: List[float] = []


class HeatExchange(BaseModel):
    """
        Level 2: Class for heat exchange information
    """
    heat_exchange_max_distance: Optional[float] = None  # heat exchange max_distance
    iContactAlongWidth_pairs_to_add: List[List[int]] = [[]]
    iContactAlongWidth_pairs_to_remove: List[List[int]] = [[]]
    iContactAlongHeight_pairs_to_add: List[List[int]] = [[]]
    iContactAlongHeight_pairs_to_remove: List[List[int]] = [[]]
    th_insulationBetweenLayers: Optional[float] = None


class ConductorGeometry(BaseModel):
    """
        Level 2: Class for multipole geometry parameters - ONLY USED FOR ISCC/ISCL CALCULATION
    """
    alphaDEG_ht: List[float] = []  # Inclination angle of each half-turn, alphaDEG (LEDET)
    rotation_ht: List[float] = []  # Rotation of each half-turn, rotation_block (LEDET)
    mirror_ht: List[int]   = []  # Mirror around quadrant bisector line for half-turn, mirror_block (LEDET)
    mirrorY_ht: List[int]  = []  # Mirror around Y axis for half-turn, mirrorY_block (LEDET)


class FieldMapFilesLEDET(BaseModel):
    """
        Level 2: Class for field map file parameters in LEDET
    """
    Iref: Optional[float] = None
    flagIron: Optional[int] = None
    flagSelfField: Optional[int] = None
    headerLines: Optional[int] = None
    columnsXY: List[int] = []
    columnsBxBy: List[int] = []
    flagPlotMTF: Optional[int] = None
    fieldMapNumber: Optional[int] = None
    flag_modify_map2d_ribbon_cable: Optional[int] = None
    flag_calculateMagneticField: Optional[int] = None


class InputGenerationOptionsLEDET(BaseModel):
    """
        Level 2: Class for input generation options in LEDET
    """
    # flag_typeWindings: Optional[int] = None
    flag_copy3DGeometryFile: Optional[int] = Field(default=None, description="If set to 1 the file is copied form the same location as yaml Model Data ")
    flag_calculateInductanceMatrix: Optional[int] = None
    flag_useExternalInitialization: Optional[int] = None
    flag_initializeVar: Optional[int] = None
    selfMutualInductanceFileNumber: Optional[int] = None


class SimulationLEDET(BaseModel):
    """
        Level 2: Class for simulation options in LEDET
    """
    flag_fastMode: Optional[int] = None
    flag_controlCurrent: Optional[int] = None
    flag_controlInductiveVoltages: Optional[int] = None
    flag_controlMagneticField: Optional[int] = None
    flag_controlBoundaryTemperatures: Optional[int] = None
    flag_automaticRefinedTimeStepping: Optional[int] = None


class PhysicsLEDET(BaseModel):
    """
        Level 2: Class for physics options in LEDET
    """
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


class MatProLEDET(BaseModel):
    STEAM_material_properties_set: Optional[Union[int, str]] = None


class QuenchInitializationLEDET(BaseModel):
    """
        Level 2: Class for quench initialization parameters in LEDET
    """
    iStartQuench: List[int] = []
    tStartQuench: List[float] = []
    lengthHotSpot_iStartQuench: List[float] = []
    fScaling_vQ_iStartQuench: List[float] = []


class PostProcessingLEDET(BaseModel):
    """
        Level 2: Class for post processing options in LEDET
    """
    flag_showFigures: Optional[int] = None
    flag_saveFigures: Optional[int] = None
    flag_saveMatFile: Optional[int] = None
    flag_saveTxtFiles: Optional[int] = None
    flag_generateReport: Optional[int] = None
    flag_saveResultsToMesh: Optional[int] = None
    tQuench: List[float] = []
    initialQuenchTemp: List[float] = []
    flag_hotSpotTemperatureInEachGroup: Optional[int] = None
    flag_importFieldWhenCalculatingHotSpotT: Optional[int] = None


class Simulation3DLEDET(BaseModel):
    """
        Level 2: Class for 3D simulation parameters and options in lEDET
    """
    # Variables in the "Options" sheet
    flag_3D: Optional[int] = None
    flag_adaptiveTimeStepping: Optional[int] = None
    sim3D_flag_Import3DGeometry: Optional[int] = None
    sim3D_import3DGeometry_modelNumber: Optional[int] = None

    # Variables in the "Inputs" sheet
    sim3D_uThreshold: Optional[float] = None
    sim3D_f_cooling_down: Optional[Union[float, List[float]]] = None
    sim3D_f_cooling_up: Optional[Union[float, List[float]]] = None
    sim3D_f_cooling_left: Optional[Union[float, List[float]]] = None
    sim3D_f_cooling_right: Optional[Union[float, List[float]]] = None
    sim3D_f_cooling_LeadEnds: List[int] = []
    sim3D_fExToIns: Optional[float] = None
    sim3D_fExUD: Optional[float] = None
    sim3D_fExLR: Optional[float] = None
    sim3D_min_ds_coarse: Optional[float] = None
    sim3D_min_ds_fine: Optional[float] = None
    sim3D_min_nodesPerStraightPart: Optional[int] = None
    sim3D_min_nodesPerEndsPart: Optional[int] = None
    sim3D_idxFinerMeshHalfTurn: List[int] = []
    sim3D_flag_checkNodeProximity: Optional[int] = None
    sim3D_nodeProximityThreshold: Optional[float] = None
    sim3D_Tpulse_sPosition: Optional[float] = None
    sim3D_Tpulse_peakT: Optional[float] = None
    sim3D_Tpulse_width: Optional[float] = None
    sim3D_tShortCircuit: Optional[float] = None
    sim3D_coilSectionsShortCircuit: List[int] = []
    sim3D_R_shortCircuit: Optional[float] = None
    sim3D_shortCircuitPosition: Optional[Union[float, List[List[float]]]] = None
    sim3D_durationGIF: Optional[float] = None
    sim3D_flag_saveFigures: Optional[int] = None
    sim3D_flag_saveGIF: Optional[int] = None
    sim3D_flag_VisualizeGeometry3D: Optional[int] = None
    sim3D_flag_SaveGeometry3D: Optional[int] = None


class PlotsLEDET(BaseModel):
    """
        Level 2: Class for plotting parameters in lEDET
    """
    suffixPlot: List[str] = []
    typePlot: List[int] = []
    outputPlotSubfolderPlot: List[str] = []
    variableToPlotPlot: List[str] = []
    selectedStrandsPlot: List[str] = []
    selectedTimesPlot: List[str] = []
    labelColorBarPlot: List[str] = []
    minColorBarPlot: List[str] = []
    maxColorBarPlot: List[str] = []
    MinMaxXYPlot: List[int] = []
    flagSavePlot: List[int] = []
    flagColorPlot: List[int] = []
    flagInvisiblePlot: List[int] = []


class VariablesToSaveLEDET(BaseModel):
    """
        Level 2: Class for variables to save in lEDET
    """
    variableToSaveTxt: List[str] = []
    typeVariableToSaveTxt: List[int] = []
    variableToInitialize: List[str] = []
    writeToMesh_fileNameMeshPositions: List[str] = []
    writeToMesh_suffixFileNameOutput: List[str] = []
    writeToMesh_selectedVariables: List[str] = []
    writeToMesh_selectedTimeSteps: List[str] = []
    writeToMesh_selectedMethod: List[str] = []


class LEDETOptions(BaseModel):
    """
        Level 1: Class for LEDET options
    """
    time_vector: TimeVectorLEDET = TimeVectorLEDET()
    magnet_inductance: MagnetInductance = MagnetInductance()
    heat_exchange: HeatExchange = HeatExchange()
    conductor_geometry_used_for_ISCL: ConductorGeometry = ConductorGeometry()
    field_map_files: FieldMapFilesLEDET = FieldMapFilesLEDET()
    input_generation_options: InputGenerationOptionsLEDET = InputGenerationOptionsLEDET()
    simulation: SimulationLEDET = SimulationLEDET()
    STEAM_Material_Properties: MatProLEDET = MatProLEDET()
    physics: PhysicsLEDET = PhysicsLEDET()
    quench_initiation: QuenchInitializationLEDET = QuenchInitializationLEDET()
    post_processing: PostProcessingLEDET = PostProcessingLEDET()
    simulation_3D: Simulation3DLEDET = Simulation3DLEDET()
    plots: PlotsLEDET = PlotsLEDET()
    variables_to_save: VariablesToSaveLEDET = VariablesToSaveLEDET()