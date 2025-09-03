from typing import List, Optional

from pydantic import BaseModel


class TimeVectorSolutionSIGMA(BaseModel):
    time_step: Optional[List[List[float]]] = None


class Simulation(BaseModel):
    generate_study: Optional[bool] = None
    study_type: Optional[str] = None
    make_batch_mode_executable: Optional[bool] = None
    nbr_elements_mesh_width: Optional[int] = None
    nbr_elements_mesh_height: Optional[int] = None


class Physics(BaseModel):
    FLAG_M_pers: Optional[int] = None
    FLAG_ifcc: Optional[int] = None
    FLAG_iscc_crossover: Optional[int] = None
    FLAG_iscc_adjw: Optional[int] = None
    FLAG_iscc_adjn: Optional[int] = None
    tauCC_PE: Optional[int] = None


class QuenchInitialization(BaseModel):
    PARAM_time_quench: Optional[float] = None
    FLAG_quench_all: Optional[int] = None
    FLAG_quench_off: Optional[int] = None
    num_qh_div: Optional[List[int]] = None
    quench_init_heat: Optional[float] = None
    quench_init_HT: Optional[List[str]] = None
    quench_stop_temp: Optional[float] = None


class Out2DAtPoints(BaseModel):
    coordinate_source: Optional[str] = None
    variables: Optional[List[str]] = None
    time: Optional[List[List[float]]] = None
    map2d: Optional[str] = None


class Out1DVsTimes(BaseModel):
    variables: Optional[List[str]] = None
    time: Optional[List[List[float]]] = None


class Out1DVsAllTimes(BaseModel):
    variables: Optional[List[str]] = None


class Postprocessing(BaseModel):
    out_2D_at_points: Out2DAtPoints = Out2DAtPoints()
    out_1D_vs_times: Out1DVsTimes = Out1DVsTimes()
    out_1D_vs_all_times: Out1DVsAllTimes = Out1DVsAllTimes()


class QuenchHeatersSIGMA(BaseModel):
    quench_heater_positions: Optional[List[List[int]]] = None
    th_coils: Optional[List[float]] = None


class PySIGMAOptions(BaseModel):
    time_vector_solution: TimeVectorSolutionSIGMA = TimeVectorSolutionSIGMA()
    simulation: Simulation = Simulation()
    physics: Physics = Physics()
    quench_initialization: QuenchInitialization = QuenchInitialization()
    postprocessing: Postprocessing = Postprocessing()
    quench_heaters: QuenchHeatersSIGMA = QuenchHeatersSIGMA()
