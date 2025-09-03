import numpy as np

def __cpNbTi_cudi_mat(T, B):  # pragma: no cover

    Tc0 = 9.2
    Bc20 = 14.5
    alpha = .59
    if B >= Bc20:
        B = Bc20-10E-4
    Tc = Tc0 * (1 - B / Bc20)**alpha

    p1 = [0.00000E+00,    4.91000E+01,   0.00000E+00,   6.40000E+01,  0.00000E+00]
    p2 = [0.00000E+00,   1.62400E+01,   0.00000E+00,  9.28000E+02,   0.00000E+00]
    p3 = [-2.17700E-01,   1.19838E+01,   5.53710E+02, - 7.84610E+03,  4.13830E+04]

    if T <= Tc:
        cpNbTi = p1[0] * T**4 + p1[1] * T**3 + p1[2] * T**2 + p1[3] * T + p1[4]
    elif (T > Tc) & (T <= 20.0):
        cpNbTi = p2[0] * T**4 + p2[1] * T**3 + p2[2] * T**2 + p2[3] * T + p2[4]
    elif (T > 20) & (T <= 50):
        cpNbTi = p3[0] * T**4 + p3[1] * T**3 + p3[2] * T**2 + p3[3] * T + p3[4]

    return cpNbTi

def __cpCu_nist_mat(T):  # pragma: no cover
    density = 8960
    if T < 4:
        T = 4
    dc_a = -1.91844
    dc_b = -0.15973
    dc_c = 8.61013
    dc_d = -18.996
    dc_e = 21.9661
    dc_f = -12.7328
    dc_g = 3.54322
    dc_h = -0.3797

    logT1 = np.log10(T)
    tempVar = \
        dc_a + dc_b * (logT1) ** 1 + dc_c * (logT1) ** 2 + dc_d * (logT1) ** 3 + \
        dc_e * (logT1) ** 4 + dc_f * (logT1) ** 5 + dc_g * (logT1) ** 6 + dc_h * (logT1) ** 7
    cpCu_perMass = 10 ** tempVar

    cpCu = density * cpCu_perMass
    return cpCu

def __cpNb3Sn_alternative_mat(T, B, Tc0_Nb3Sn: float = 0.0, Bc20_Nb3Sn: float = 0.0):  # pragma: no cover
    B[B < .001] = 0.001
    alpha = 0.59
    Tc = Tc0_Nb3Sn * (1 - B / Bc20_Nb3Sn) ** alpha
    density = 8950.0  # [kg / m ^ 3]

    betaT = 1.241E-3  # [J / K ^ 4 / kg]
    gammaT = .138  # [J / K ^ 2 / kg]

    if T <= Tc:
        cpNb3Sn = (betaT + 3 * gammaT / Tc0_Nb3Sn ** 2) * T ** 3 + gammaT * B / Bc20_Nb3Sn * T
    elif (T > Tc) & (T <= 20):
        cpNb3Sn = betaT * T ** 3 + gammaT * T
    elif (T > 20) & (T <= 400):
        polyFit_20K_400K = [0.1662252, -0.6827738, -6.3977, 57.48133, -186.90995, 305.01434, -247.44839, 79.78547]
        logT = np.log10(T)
        logCp2 = np.polyval(polyFit_20K_400K, logT)
        cpNb3Sn = 10 ** logCp2

    cpNb3Sn = cpNb3Sn * density

    return cpNb3Sn

def __Jc_Nb3Sn_Summer(T, B, Jc_Nb3Sn0: float = 0.0, Tc0_Nb3Sn: float = 0.0, Bc20_Nb3Sn: float = 0.0):  # pragma: no cover

    if type(T) == int or type(T) == float:
        T = np.repeat(T, len(Jc_Nb3Sn0)).astype(float)

    B[abs(B) < .001] = 0.001
    T[T < 0.001] = 0.001
    f_T_T0 = T / Tc0_Nb3Sn
    f_T_T0[f_T_T0 > 1] = 1
    Bc2 = Bc20_Nb3Sn * (1 - f_T_T0 ** 2) * (1 - 0.31 * f_T_T0 ** 2 * (1 - 1.77 * np.log(f_T_T0)))
    f_B_Bc2 = B / Bc2
    f_B_Bc2[f_B_Bc2 > 1] = 1
    Jc_T_B = Jc_Nb3Sn0 / np.sqrt(B) * (1 - f_B_Bc2) ** 2 * (1 - f_T_T0 ** 2) ** 2
    return Jc_T_B

def __Tc_Tcs_Nb3Sn_approx(J, B, Jc_Nb3Sn0: float = 0.0, Tc0_Nb3Sn: float = 0.0, Bc20_Nb3Sn: float = 0.0):  # pragma: no cover
    J = abs(J)
    B = abs(B)

    f_B_Bc2 = B / Bc20_Nb3Sn
    f_B_Bc2[f_B_Bc2 > 1] = 1
    Tc = Tc0_Nb3Sn * (1 - f_B_Bc2)**.59

    Jc0 = __Jc_Nb3Sn_Summer(0, B, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn)
    f_J_Jc0 = J/ Jc0
    f_J_Jc0[f_J_Jc0 > 1] = 1

    Tcs = (1 - f_J_Jc0) * Tc

    return [Tc, Tcs]

def _quenchPropagationVelocity(I, B, T_bath, A_CableInsulated, f_SC, f_ST, idxNbTi, idxNb3Sn, Tc0_NbTi, Bc20_NbTi, c1_Ic_NbTi, c2_Ic_NbTi, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn):  # pragma: no cover

    """
    Function to calculate the quench propagation velocity in a cable not including cooling and insulation, form the Wilson book pages 204-217
    :param I: conductor current
    :param B: self-field and external field of the conductor
    :param A_CableInsulated: bath temperature surrounding the conductor
    :param f_SC: fraction of superconductor in the cable given including insulation
    :param f_ST: fraction of stabilizer in the cable given including insulation
    :param idxNbTi: 1 if used superconductor is Niobium-Titanium
    :param idxNb3Sn: 1 if used superconductor is Niobium3-Tin
    :param Tc0_NbTi: fitting parameter for NbTi
    :param Bc20_NbTi: fitting parameter for NbTi
    :param Bc20_Nb3Sn: fitting parameter for Nb3Sn
    :param c1_Ic_NbTi: fitting parameter for NbTi
    :param c2_Ic_NbTi: fitting parameter for NbTi
    :param Jc_Nb3Sn0: fitting parameter for Nb3Sn
    :param Tc0_Nb3Sn: fitting parameter for Nb3Sn
    :return: vQ
    """

    # Calculate Quench propagation velocity
    L0 = 2.44E-08
    A_CableBare = A_CableInsulated * (f_SC + f_ST)
    f_SC_inStrand = f_SC / (f_SC + f_ST)
    f_ST_inStrand = f_ST / (f_SC + f_ST)
    I = abs(I)
    J_op = I / A_CableBare
    A_SC = A_CableInsulated * f_SC

    if idxNbTi == 1:
        Tc = Tc0_NbTi * (1 - B / Bc20_NbTi) ** 0.59
        Tcs = (1 - I / (c1_Ic_NbTi + c2_Ic_NbTi * B)) * Tc
    if idxNb3Sn == 1:
        [Tc, Tcs] = __Tc_Tcs_Nb3Sn_approx(I / A_SC, B, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn)

    Ts = (Tcs + Tc) / 2
    cp_ST = __cpCu_nist_mat(Ts)

    if idxNbTi == 1:
        cp_SC = __cpNbTi_cudi_mat(Ts, B)
    if idxNb3Sn == 1:
        cp_SC = __cpNb3Sn_alternative_mat(Ts, B, Tc0_Nb3Sn, Bc20_Nb3Sn)

    cp = cp_ST * f_ST_inStrand + cp_SC * f_SC_inStrand
    vQ = J_op / cp * ((L0 * Ts) / (Ts - T_bath))**0.5

    return vQ