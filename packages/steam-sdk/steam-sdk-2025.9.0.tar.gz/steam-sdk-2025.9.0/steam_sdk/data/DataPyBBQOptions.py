from pydantic import BaseModel
from typing import Optional

class GeometryBBQ(BaseModel):
    """
        Level 2: Class for geometry options in BBQ
    """
    thInsul: Optional[float] = None
    lenBusbar: Optional[float] = None


class SimulationBBQ(BaseModel):
    """
        Level 2: Class for simulation options in BBQ
    """
    meshSize: Optional[float] = None


class PhysicsBBQ(BaseModel):
    """
        Level 2: Class for physics options in BBQ
    """
    adiabaticZoneLength: Optional[float] = None
    aFilmBoilingHeliumII: Optional[float] = None
    aKap: Optional[float] = None
    BBackground: Optional[float] = None
    BPerI: Optional[float] = None
    IDesign: Optional[float] = None
    jointLength: Optional[float] = None
    jointResistancePerMeter: Optional[float] = None
    muTInit: Optional[float] = None
    nKap: Optional[float] = None
    QKapLimit: Optional[float] = None
    Rjoint: Optional[float] = None
    symmetryFactor: Optional[float] = None
    tauDecay: Optional[float] = None
    TInitMax: Optional[float] = None
    TInitOp: Optional[float] = None
    TLimit: Optional[float] = None
    tValidation: Optional[float] = None
    TVQRef: Optional[float] = None
    VThreshold: Optional[float] = None
    withCoolingToBath: Optional[float] = None


class QuenchInitializationBBQ(BaseModel):
    """
        Level 2: Class for quench initialization parameters in BBQ
    """
    sigmaTInit: Optional[float] = None

