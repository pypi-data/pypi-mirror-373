import numpy as np
from dataclasses import dataclass, field


"""
    These classes define the four ProteCCT dataclasses, which contain the variables to write in the ProteCCT 
    input file.
"""
@dataclass
class ProteCCTInputs:
    magnetIdentifier: str = ''
    totalConductorLength: float = 0.0
    numTurnsPerStrandTotal: int = 0
    CuFraction: float = 0.0
    RRRStrand: float = 0.0
    BMaxAtNominal: float = 0.0
    BMinAtNominal: float = 0.0
    INominal: float = 0.0
    fieldPeriodicity: int = 0
    magneticLength: float = 0.0
    thFormerInsul: float = 0.0
    wStrandSlot: float = 0.0
    DStrand: float = 0.0
    numRowStrands: int = 0
    numColumnStrands: int = 0
    IcFactor: float = 0.0
    polyimideToEpoxyRatio: float = 0.0
    windingOrder: np.ndarray = field(default_factory=lambda: np.array([1]))
    M: np.ndarray = field(default_factory=lambda: np.array([1]))
    innerRadiusFormers: np.ndarray = field(default_factory=lambda: np.array([1]))
    formerThicknessUnderneathCoil: float = 0.0
    innerRadiusOuterCylinder: float = 0.0
    thicknessOuterCylinder: float = 0.0
    RRRFormer: float = 0.0
    RRROuterCylinder: float = 0.0
    coolingToHeliumBath: int = 0
    tMaxStopCondition: float = 0.0
    tempMaxStopCondition: float = 0.0
    IOpFractionStopCondition: float = 0.0
    fLoopLength: float = 0.0
    TOp: float = 0.0
    IOpInitial: float = 0.0
    RCrowbar: float = 0.0
    RDumpPreconstant: float = 0.0
    RDumpPower: float = 0.0
    addedHeCpFrac: float = 0.0
    addedHeCoolingFrac: int = 0
    tSwitchDelay: float = 0.0
    coolingToHeliumBath: float = 0.0
    fracCurrentChangeMax: float = 0.0
    resultsAtTimeStep: float = 0.0
    deltaTMaxAllowed: float = 0.0
    minTimeStep: float = 0.0
    turnLengthElements: int = 0
    withPlots: int = 0
    plotPauseTime: float = 0.0
    withVoltageEvaluation: int = 0
    voltageToGroundOutputSelection: np.ndarray = field(default_factory=lambda: np.array([1]))
    externalWaveform: int = 0
    saveStateAtEnd: int = 0
    restoreStateAtStart: int = 0
    silentRun: int = 0
