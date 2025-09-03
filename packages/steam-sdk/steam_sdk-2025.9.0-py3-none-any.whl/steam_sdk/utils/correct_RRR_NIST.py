import os

import numpy as np
import steammaterials
from steammaterials.STEAM_materials import STEAM_materials


def correct_RRR_NIST(RRR: float, T_ref_high: float, T_ref_low: float):
    '''
    Correct the RRR to use in the NIST fit for copper electrical resistivity
    The NIST fit defines RRR as the ratio between the resistance at T_NIST_high=273 K and T_NIST_low=4 K

    :param RRR: Residual Resistivity Ratio (RRR) defined as the ratio between the resistance at T_ref_high and T_ref_low
    :param T_ref_high: Higher temperature used in the definition of RRR [K]
    :param T_ref_low: Lower temperature used in the definition of RRR [K]
    :return:
    '''
    # Re-cast arguments as floats and make them np arrays
    RRR, T_ref_high, T_ref_low = np.array([RRR]).astype(float), np.array([T_ref_high]).astype(float), np.array([
                                                                                                                   T_ref_low]).astype(float)

    # Initialize STEAM_materials object
    CFUN_rhoCuNIST = STEAM_materials('CFUN_rhoCu_NIST_v1', n_arg=3, n_points=1)

    # Calculate the correction factor for the measured RRR, and the corrected RRR
    rho_T_ref_low = CFUN_rhoCuNIST.evaluate(np.vstack((T_ref_low, 0, RRR)))[0]
    rho_T_ref_high = CFUN_rhoCuNIST.evaluate(np.vstack((T_ref_high, 0, RRR)))[0]
    f_correction_RRR = RRR[0] / (rho_T_ref_high / rho_T_ref_low)
    corrected_RRR = f_correction_RRR * RRR[0]

    return f_correction_RRR, corrected_RRR
