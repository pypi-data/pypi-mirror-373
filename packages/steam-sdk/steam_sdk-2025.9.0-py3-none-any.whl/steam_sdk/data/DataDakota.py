from pydantic import BaseModel
from typing import List

class DataDakota(BaseModel):
    """
        Class for FiQuS multipole
    """
    partitions: List = []
    lower_bounds: List = []
    upper_bounds: List = []
    #descriptors: List = []
    initial_point: List = []
    scaling: List = []