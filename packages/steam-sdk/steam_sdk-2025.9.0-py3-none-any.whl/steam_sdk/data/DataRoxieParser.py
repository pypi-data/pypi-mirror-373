from pydantic import BaseModel
from typing import Dict, List, Optional


class Coord(BaseModel):
    """
        Class for coordinates
    """
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class Roll(BaseModel):
    """
        Class for roll2 transformation
    """
    coor: Coord = Coord()
    alph: Optional[float] = None


class HyperHole(BaseModel):
    """
        Class for hyper holes
    """
    areas: List[str] = []


class HyperArea(BaseModel):
    """
        Class for hyper areas
    """
    material: Optional[str] = None
    lines: List[str] = []


class HyperLine(BaseModel):
    """
        Class for hyper lines: lines, arcs, elliptic arcs, circles
    """
    type: Optional[str] = None
    kp1: Optional[str] = None
    kp2: Optional[str] = None
    kp3: Optional[str] = None
    arg1: Optional[float] = None
    arg2: Optional[float] = None
    elements: Optional[int] = None


class CondPar(BaseModel):
    """
        Class for conductor parameters
    """
    wInsulNarrow: Optional[float] = None
    wInsulWide: Optional[float] = None
    dFilament: Optional[float] = None
    dstrand: Optional[float] = None
    fracCu: Optional[float] = None
    fracSc: Optional[float] = None
    RRR: Optional[float] = None
    TupRRR: Optional[float] = None
    Top: Optional[float] = None
    Rc: Optional[float] = None
    Ra: Optional[float] = None
    fRhoEff: Optional[float] = None
    lTp: Optional[float] = None
    wBare: Optional[float] = None
    hInBare: Optional[float] = None
    hOutBare: Optional[float] = None
    noOfStrands: Optional[int] = None
    noOfStrandsPerLayer: Optional[int] = None
    noOfLayers: Optional[int] = None
    lTpStrand: Optional[float] = None
    wCore: Optional[float] = None
    hCore: Optional[float] = None
    thetaTpStrand: Optional[float] = None
    degradation: Optional[float] = None
    C1: Optional[float] = None
    C2: Optional[float] = None
    fracHe: Optional[float] = None
    fracFillInnerVoids: Optional[float] = None
    fracFillOuterVoids: Optional[float] = None


class ConductorRoxie(BaseModel):
    """
        Container for parsed conductor information from Roxie
    """
    conductorType: Optional[int] = None
    cableGeom: Optional[str] = None
    strand: Optional[str] = None
    filament: Optional[str] = None
    insul: Optional[str] = None
    trans: Optional[str] = None
    quenchMat: Optional[str] = None
    T_0: Optional[float] = None
    comment: Optional[str] = None
    parameters: CondPar = CondPar()


class Cable(BaseModel):
    """
        Class for cable parameters
    """
    height: Optional[float] = None
    width_i: Optional[float] = None
    width_o: Optional[float] = None
    ns: Optional[int] = None
    transp: Optional[float] = None
    degrd: Optional[float] = None
    comment: Optional[str] = None


class Quench(BaseModel):
    """
        Class for quench parameters
    """
    SCHeatCapa: Optional[int] = None
    CuHeatCapa: Optional[int] = None
    CuThermCond: Optional[int] = None
    CuElecRes: Optional[int] = None
    InsHeatCapa: Optional[int] = None
    InsThermCond: Optional[int] = None
    FillHeatCapa: Optional[int] = None
    He: Optional[int] = None
    comment: Optional[str] = None


class Transient(BaseModel):
    """
        Class for transient parameters
    """
    Rc: Optional[float] = None
    Ra: Optional[float] = None
    filTwistp: Optional[float] = None
    filR0: Optional[float] = None
    fil_dRdB: Optional[float] = None
    strandfillFac: Optional[float] = None
    comment: Optional[str] = None


class Strand(BaseModel):
    """
        Class for strand parameters
    """
    diam: Optional[float] = None
    cu_sc: Optional[float] = None
    RRR: Optional[float] = None
    Tref: Optional[float] = None
    Bref: Optional[float] = None
    Jc_BrTr: Optional[float] = None
    dJc_dB: Optional[float] = None
    comment: Optional[str] = None


class Filament(BaseModel):
    """
        Class for filament parameters
    """
    fildiao: Optional[float] = None
    fildiai: Optional[float] = None
    Jc_fit: Optional[str] = None
    fit: Optional[str] = None
    comment: Optional[str] = None


class Insulation(BaseModel):
    """
        Class for insulation parameters
    """
    radial: Optional[float] = None
    azimut: Optional[float] = None
    comment: Optional[str] = None

class RemFit(BaseModel):
    """
        Class for REMFIT parameters (not used in STEAM, but still parsed)
    """
    type: Optional[int] = None
    C1: Optional[float] = None
    C2: Optional[float] = None
    C3: Optional[float] = None
    C4: Optional[float] = None
    C5: Optional[float] = None
    C6: Optional[float] = None
    C7: Optional[float] = None
    C8: Optional[float] = None
    C9: Optional[float] = None
    C10: Optional[float] = None
    C11: Optional[float] = None
    comment: Optional[str] = None


class Block(BaseModel):
    """
        Class for block list
    """
    type: Optional[int] = None
    nco: Optional[int] = None
    radius: Optional[float] = None
    phi: Optional[float] = None
    alpha: Optional[float] = None
    current: Optional[float] = None
    condname: Optional[str] = None
    n1: Optional[int] = None
    n2: Optional[int] = None
    imag: Optional[int] = None
    turn: Optional[float] = None
    coil: Optional[int] = None
    pole: Optional[int] = None
    layer: Optional[int] = None
    winding: Optional[int] = None
    shift2: Coord = Coord()
    roll2: Roll = Roll()


class Group(BaseModel):
    """
        Class for group list
    """
    symm: Optional[int] = None
    typexy: Optional[int] = None
    blocks: List[int] = []  # map


class Trans(BaseModel):
    """
        Class for transformation list
    """
    x: Optional[float] = None
    y: Optional[float] = None
    alph: Optional[float] = None
    bet: Optional[float] = None
    string: Optional[str] = None
    act: Optional[int] = None
    bcs: List[int] = []  # map


class Iron(BaseModel):
    """
        Class for the iron yoke data
    """
    key_points: Dict[str, Coord] = {}
    hyper_lines: Dict[str, HyperLine] = {}
    hyper_areas: Dict[str, HyperArea] = {}
    hyper_holes: Dict[int, HyperHole] = {}


class Cadata(BaseModel):
    """
        Class for the conductor data
    """
    insul: Dict[str, Insulation] = {}
    remfit: Dict[str, RemFit] = {}
    filament: Dict[str, Filament] = {}
    strand: Dict[str, Strand] = {}
    transient: Dict[str, Transient] = {}
    quench: Dict[str, Quench] = {}
    cable: Dict[str, Cable] = {}
    conductor: Dict[str, ConductorRoxie] = {}


class Coil(BaseModel):
    """
        Class for the coil data
    """
    blocks: Dict[str, Block] = {}
    groups: Dict[str, Group] = {}
    transs: Dict[str, Trans] = {}


class StrandGroup(BaseModel):
    """
        Class for strand group
    """
    strand_positions: Dict[int, Coord] = {}


class Corner(BaseModel):
    """
        Class for corner positions
    """
    iH: Coord = Coord()  # inner left
    iL: Coord = Coord()  # inner right
    oH: Coord = Coord()  # outer left
    oL: Coord = Coord()  # outer right


class HalfTurnCorner(BaseModel):
    """
        Class for corner type
    """
    insulated: Corner = Corner()
    bare: Corner = Corner()


class HalfTurn(BaseModel):
    """
        Class for half-turn data
    """
    corners: HalfTurnCorner = HalfTurnCorner()
    strand_groups: Dict[int, StrandGroup] = {}


class Order(BaseModel):
    """
        Class for electrical order (block location)
    """
    coil: Optional[int] = None
    pole: Optional[int] = None
    layer: Optional[int] = None
    winding: Optional[int] = None
    block: Optional[int] = None


class CenterShift(BaseModel):
    """
        Class for bore center shift
    """
    inner: Coord = Coord()
    outer: Coord = Coord()


class Wedge(BaseModel):
    """
        Class for wedge positions
    """
    corners: Corner = Corner()
    corners_ins: Corner = Corner()
    corrected_center: CenterShift = CenterShift()
    corrected_center_ins: CenterShift = CenterShift()
    order_l: Order = Order()
    order_h: Order = Order()


class BlockData(BaseModel):
    """
        Class for block data
    """
    block_corners: Corner = Corner()
    block_corners_ins: Corner = Corner()
    current_sign: Optional[int] = None
    half_turns: Dict[int, HalfTurn] = {}


class WindingData(BaseModel):
    """
        Class for winding data
    """
    blocks: Dict[int, BlockData] = {}
    conductor_name: Optional[str] = None
    conductors_number: Optional[int] = None


class Winding(BaseModel):
    """
        Class for windings
    """
    windings: Dict[int, WindingData] = {}


class Layer(BaseModel):
    """
        Class for winding layers
    """
    layers: Dict[int, Winding] = {}


class Pole(BaseModel):
    """
        Class for poles
    """
    type: Optional[str] = None
    poles: Dict[int, Layer] = {}
    bore_center: Coord = Coord()


class CoilData(BaseModel):
    """
        Class for coils
    """
    coils: Dict[int, Pole] = {}
    physical_order: List[Order] = []


class RoxieRawData(BaseModel):
    """
        Class for the raw data
    """
    cadata: Cadata = Cadata()
    coil: Coil = Coil()


class RoxieData(BaseModel):
    """
        Class for the roxie parser
    """
    iron: Iron = Iron()
    coil: CoilData = CoilData()
    wedges: Dict[int, Wedge] = {}
