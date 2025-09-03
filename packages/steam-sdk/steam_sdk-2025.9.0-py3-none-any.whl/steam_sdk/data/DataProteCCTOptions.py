from pydantic import BaseModel
from typing import List, Optional

############################
# ProteCCT options
class TimeVectorProteCCT(BaseModel):
    """
        Level 2: Class for ProteCCT time vector options
    """
    tMaxStopCondition: Optional[float] = None
    minTimeStep: Optional[float] = None


class GeometryGenerationOptionsProteCCT(BaseModel):
    """
        Level 2: Class for ProteCCT geometry generation options
    """
    totalConductorLength: Optional[float] = None
    #numTurnsPerStrandTotal: Optional[int] = None
    thFormerInsul: Optional[float] = None
    #wStrandSlot: Optional[float] = None
    #numRowStrands: Optional[int] = None
    #numColumnStrands: Optional[int] = None
    IcFactor: Optional[float] = None
    polyimideToEpoxyRatio: Optional[float] = None



class PhysicsProteCCT(BaseModel):
    """
        Level 2: Class for ProteCCT physics options
    """
    M: List[List[float]] = [[]]
    BMaxAtNominal: Optional[float] = None
    BMinAtNominal: Optional[float] = None
    INominal: Optional[float] = None
    fieldPeriodicity: Optional[float] = None
    #RRRFormer: Optional[float] = None
    #RRROuterCylinder: Optional[float] = None
    coolingToHeliumBath: Optional[int] = None
    fLoopLength: Optional[float] = None
    addedHeCpFrac: Optional[float] = None
    addedHeCoolingFrac: Optional[float] = None


class SimulationProteCCT(BaseModel):
    """
        Level 2: Class for ProteCCT physics options
    """
    tempMaxStopCondition: Optional[float] = None
    IOpFractionStopCondition: Optional[float] = None
    fracCurrentChangeMax: Optional[float] = None
    resultsAtTimeStep: Optional[float] = None
    deltaTMaxAllowed: Optional[float] = None
    turnLengthElements: Optional[int] = None
    externalWaveform: Optional[int] = None
    saveStateAtEnd: Optional[int] = None
    restoreStateAtStart: Optional[int] = None
    silentRun: Optional[int] = None


class PlotsProteCCT(BaseModel):
    """
        Level 2: Class for ProteCCT plots options
    """
    withPlots: Optional[int] = None
    plotPauseTime: Optional[float] = None


class PostProcessingProteCCT(BaseModel):
    """
        Level 2: Class for ProteCCT post-processing options
    """
    withVoltageEvaluation: Optional[int] = None
    voltageToGroundOutputSelection: Optional[str] = None  # Note: it will be written in a single cell in the ProteCCT file


class PROTECCTOptions(BaseModel):
    """
        Level 1: Class for ProteCCT options
    """
    time_vector: TimeVectorProteCCT = TimeVectorProteCCT()
    geometry_generation_options: GeometryGenerationOptionsProteCCT = GeometryGenerationOptionsProteCCT()
    simulation: SimulationProteCCT = SimulationProteCCT()
    physics: PhysicsProteCCT = PhysicsProteCCT()
    post_processing: PostProcessingProteCCT = PostProcessingProteCCT()
    plots: PlotsProteCCT = PlotsProteCCT()
