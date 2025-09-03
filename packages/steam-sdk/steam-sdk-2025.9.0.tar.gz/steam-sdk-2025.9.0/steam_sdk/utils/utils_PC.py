import numpy as np
from typing import List


def func_current_time(t_start: float, I_start: float, I_end: list, dI_dt: list, dI_dt_2: list, t_plateau: list):
    '''
    Returns a function for the current vs. time of the power-cycles. Power cycles consist of:
    Plateau - Parabolic Ramp (Increase) - Linear Ramp - Parabolic Ramp (Decrease) - Plateau
    Each cycle can be defined by the input parameters in a list.

    Returns the time and current vector

    :param t_start: float, Time of the initial plateau
    :param I_start: float, Current level of the initial plateau
    :param I_end: list, List of all current levels (floats) at the end of each cycle (Current level of final plateau)
    :param dI_dt: list, List of all dI_dt (floats) for the linear ramps
    :param dI_dt_2: list, List of all dI_dt (floats) for the parabolic ramps (same dI_dt for the two par. ramps in a cycle)
    :param t_plateau: list, List of all durations of the plateaus
    :return: t, I - time and current vector
    '''

    ### Check if inputs are consistent
    # If inputs not list, convert to list
    if type(I_end) != list: I_end = [I_end]
    if type(dI_dt) != list: dI_dt = [dI_dt]
    if type(dI_dt_2) != list: dI_dt_2 = [dI_dt_2]
    if type(t_plateau) != list: t_plateau = [t_plateau]
    # All lists need to have the same size == Number of ramp cycles
    n_cycles = len(t_plateau)
    assert np.all(np.equal([len(I_end), len(dI_dt), len(dI_dt_2), len(t_plateau)], n_cycles)), \
        f'Inputs are not of equal size got: len(I_end):' f'{len(I_end)}, len(dI_dt):{len(dI_dt)}, ' \
        f'len(dI_dt_2):{len(dI_dt_2)}, ' f'len(t_plateau):{len(t_plateau)}'
    for i in range(len(I_end)-1):
        if I_end[i]>I_end[i+1]:
            n_cycles = i+1
            break

    # Define hard-coded numbers for the max. length expected + minimum time step required
    t_end = 3000
    t_step = 0.01
    t = np.linspace(0, t_end, int(t_end / t_step))
    I = np.zeros((int(t_end / t_step)), )

    # Helper functions for the parabolic and linear ramp
    def parabolic_ramp(t, dI_dt_2):
        t = t - t[0]  # to always start at 0
        return 0.5 * dI_dt_2 * t ** 2

    def linear_ramp(t, dI_dt):
        t = t - t[0]  # to always start at 0
        return dI_dt * t

    # Phase 1: Plateau at I_Start
    t_idx = int(t_start / t_step)
    I[:t_idx] = I_start

    # Loop through all cycles of Parabolic - linear - parabolic - plateau
    for k in range(n_cycles):
        # Parabolic
        t_idx_end = t_idx + int((dI_dt[k] / dI_dt_2[k]) / t_step)  # Time needed for first parabol: dI_dt/ dI_dt_2
        I[t_idx:t_idx_end] = I[t_idx - 1] + parabolic_ramp(t[t_idx:t_idx_end], dI_dt_2[k])
        t_idx = t_idx_end

        # Linear
        I_par = 0.5 * dI_dt_2[k] * (dI_dt[k] / dI_dt_2[k]) ** 2  # Current ramp, covered by the parabolic ramps
        t_idx_end = t_idx + int((I_end[k] - 2 * I_par - I_start) / dI_dt[k] / t_step)  # Time needed for linear ramp: (I_end - I_start - I_parabolic)/dI_dt
        if t_idx_end>t_idx:
            I[t_idx:t_idx_end] = I[t_idx - 1] + linear_ramp(t[t_idx:t_idx_end], dI_dt[k])
            t_idx = t_idx_end

        # Parabolic
        t_idx_end = t_idx + int((dI_dt[k] / dI_dt_2[k]) / t_step)  # Time needed for first parabol: dI_dt/ dI_dt_2
        if t_idx_end > t_idx:
            I[t_idx:t_idx_end] = I[t_idx - 1] + linear_ramp(t[t_idx:t_idx_end], dI_dt[k]) - parabolic_ramp(
                t[t_idx:t_idx_end], dI_dt_2[k])
            t_idx = t_idx_end

        # Plateau
        t_idx_end = t_idx + int(t_plateau[k] / t_step)
        I[t_idx:t_idx_end] = I[t_idx - 1]
        t_idx = t_idx_end
        I_start = I_end[k]

    # Last Phase: Plateau to the end
    I[t_idx:] = I[t_idx - 1]

    return t, I

def calc_t_PC_off(Time_Current: tuple, I_final: float):
    '''
    Helper function to find the PC switch off time within the cycles. Returns the time of t_PC_off, calculated in
    func_current_time

    :param Time_Current: tuple, tuple of time_vector and current
    :param I_final: float, Current level at which PC is supposed to switch off
    :return: t, float
    '''
    time = Time_Current[0]
    current = Time_Current[1]
    return np.round(time[np.argmin(abs(current - I_final))], 4)



def calculate_t_PC_off_one(t_start: float, I_start: float, I_end: float, dI_dt: float, dI_dt_2: float, t_plateau: float, I_off: float):
    delta_t_parabolic = abs(dI_dt / dI_dt_2)
    delta_I_parabolic = 0.5 * abs(dI_dt_2) * delta_t_parabolic ** 2
    delta_I_linear = abs(I_end - I_start) - 2 * delta_I_parabolic
    delta_t_linear = abs(delta_I_linear / dI_dt)
    delta_Ioff_Istart = abs(I_off - I_start)
    I_start, I_off, dI_dt = abs(I_start), abs(I_off), abs(dI_dt)

    if I_off < 2 * delta_I_parabolic:
        #I_off = 0
        print("Warning: I_off is less than 2 times delta_I_parabolic.")
        t_PC_off = 9999  # a very high value hard coded
    elif delta_Ioff_Istart < delta_I_parabolic:
        t_PC_off = t_start + np.sqrt( delta_Ioff_Istart / 0.5 / dI_dt_2)
    elif delta_Ioff_Istart < delta_I_parabolic + delta_I_linear:
        t_PC_off = t_start + delta_t_parabolic + (delta_Ioff_Istart - delta_I_parabolic) / dI_dt
    elif delta_Ioff_Istart < delta_I_parabolic + delta_I_linear + delta_I_parabolic:
        t_PC_off = t_start + delta_t_parabolic + delta_t_linear + np.sqrt((delta_Ioff_Istart - delta_I_parabolic - delta_I_linear) / 0.5 / dI_dt_2)
    else:
        t_PC_off = t_start + 2 * delta_t_parabolic + delta_t_linear + t_plateau
    return t_PC_off


def calculate_t_PC_off(t_start: float, I_start: float, I_end: List[float], dI_dt: List[float], dI_dt_2: List[float], t_plateau: List[float], I_off: float):
    if not isinstance(I_end, list):
        I_end = [I_end]
    if not isinstance(dI_dt, list):
        dI_dt = [dI_dt]
    if not isinstance(dI_dt_2, list):
        dI_dt_2 = [dI_dt_2]
    if not isinstance(t_plateau, list):
        t_plateau = [t_plateau]

    t_PC_off_k = t_start
    I_start_k = I_start
    # Iterate over the different defined ramps
    for k, (I_end_k, dI_dt_k, dI_dt_2_k, t_plateau_k) in enumerate(zip(I_end, dI_dt, dI_dt_2, t_plateau)):
        print(k, I_end_k, dI_dt_k, dI_dt_2_k, t_plateau_k)
        if k + 1 < len(I_end):
            t_PC_off_k = calculate_t_PC_off_one(t_start=t_PC_off_k, I_start=I_start_k, I_end=I_end_k, dI_dt=dI_dt_k, dI_dt_2=dI_dt_2_k, t_plateau=t_plateau_k, I_off=I_end_k)
            I_start_k = I_end_k
            if t_PC_off_k == 9999:
                I_start_k = 0
                continue
        else:
            # At the last ramp, check the time at which I_off is reached
            t_PC_off = calculate_t_PC_off_one(t_start=t_PC_off_k, I_start=I_start_k, I_end=I_end_k, dI_dt=dI_dt_k, dI_dt_2=dI_dt_2_k, t_plateau=t_plateau_k, I_off=I_off)
    return t_PC_off














