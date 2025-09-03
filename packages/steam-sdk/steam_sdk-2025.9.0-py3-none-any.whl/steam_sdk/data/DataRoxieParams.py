from dataclasses import dataclass

@dataclass
class RoxieParams:

    nT: int
    indexTstart: int
    indexTstop: int
    strandToGroup: int
    strandToHalfTurn: int
    x_strand: list
    y_strand: list
    i_strand: list