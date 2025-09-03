from pydantic import BaseModel
from typing import Optional, List, Dict


class Color(BaseModel):
    """
    RGB in %
    """
    r: float = None
    g: float = None
    b: float = None


class Marker(BaseModel):
    """
    matplotlib-supported marker symbol
    """
    symbol: str = None


class FontSize(BaseModel):
    """
    font size of relevant types
    """
    titles: int = None
    labels: int = None
    ticks: int = None


class DataPlot(BaseModel):
    """

    """
    Colors: Dict[str, Color] = {}
    Markers: Dict[str, Marker] = {}
    FontSizes: FontSize = FontSize()
