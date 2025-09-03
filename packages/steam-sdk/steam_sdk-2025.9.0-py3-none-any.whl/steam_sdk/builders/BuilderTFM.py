import numpy as np
import pandas as pd
import os
import copy
from pathlib import Path
from dataclasses import asdict
from scipy.interpolate import RegularGridInterpolator
from scipy.interpolate import interp1d
from scipy.signal import medfilt
from scipy.signal import find_peaks
import time
from types import SimpleNamespace
import matplotlib.pyplot as plt
from numba import njit, prange
# from joblib import Parallel, delayed
import io
from sympy import *

from steam_sdk.data.DataTFM import General, Turns, HalfTurns, Strands, PC, Options, IFCC, ISCC, ED, Wedge, CB, CPS, AlRing, BS, Shorts, Capacitances
from steam_sdk.data.DataTFM import lookupModelDataToTFMHalfTurns, lookupModelDataToTFMStrands
from steam_sdk.data.DataModelCircuit import Component, Magnet_TFM
from steam_sdk.parsers.ParserXYCE import ParserXYCE
from steammaterials.STEAM_materials import STEAM_materials
from steam_magnetic_calculations.Magnetic_Coil import MagneticCoil

def preprocess_complex_strings(data):
    # Replace 'i' with 'j' in the data strings for Python-compatible complex numbers
    return np.vectorize(lambda x: complex(x.replace('i', 'j')))(data)


@njit(parallel=True, fastmath=True)
def calculate_magnitudes(df_values):
    # Calculate the real part and magnitude in one go for both X and Y components
    f_mag_X = np.real(df_values[::2, :])
    f_mag_Y = np.real(df_values[1::2, :])
    f_mag = np.sqrt(f_mag_X ** 2 + f_mag_Y ** 2)
    return f_mag_X, f_mag_Y, f_mag


@njit(parallel=True, fastmath=True, cache=True)
def group_mutual_coupling_diagonal(groups: int, M_x: np.ndarray, M_y: np.ndarray, M_couplings_x: np.ndarray, M_couplings_y: np.ndarray, HalfTurns_to_sections: np.ndarray, strands_to_sections: np.ndarray, sort_on: str = 'strands'):
    """
    Optimized function for mutual coupling calculation with Numba.
    """
    # Precompute indexes for each group based on the selected sorting method
    if sort_on == 'strands':
        strand_indexes_dict = [np.where(strands_to_sections == i)[0] for i in range(1, groups + 1)]
    else:  # 'halfturns'
        strand_indexes_dict = [np.where(HalfTurns_to_sections == i)[0] for i in range(1, groups + 1)]

    # Precompute turn indexes separately as arrays for consistency
    if M_x.shape[0] == groups:
        turn_indexes_dict = [np.array([i-1]) for i in range(1, groups + 1)]
    else:
        turn_indexes_dict = [np.where(HalfTurns_to_sections == i)[0] for i in range(1, groups + 1)]

    for i in range(1, groups + 1):
        turn_indexes_inducing = turn_indexes_dict[i - 1]
        strand_indexes_inducing = strand_indexes_dict[i - 1]

        if len(turn_indexes_inducing) > 0:
            for k in range(M_x.shape[1]):
                # Process M_x for mutual coupling with a single summation step
                M_inducing_x = M_x[turn_indexes_inducing, k, :][:, strand_indexes_inducing]
                sum_M_inducing_x = np.sum(M_inducing_x, axis=0)  # Use `np.nansum` to handle nan values
                M_couplings_x[i - 1, i - 1, k] = np.sqrt(np.dot(sum_M_inducing_x, sum_M_inducing_x))

                # Process M_y similarly
                M_inducing_y = M_y[turn_indexes_inducing, k, :][:, strand_indexes_inducing]
                sum_M_inducing_y = np.sum(M_inducing_y, axis=0)
                M_couplings_y[i - 1, i - 1, k] = np.sqrt(np.dot(sum_M_inducing_y, sum_M_inducing_y))

    return M_couplings_x, M_couplings_y


@njit(parallel=True, fastmath=True, cache=True)
def group_mutual_coupling_offdiagonal(groups: int, M_x: np.ndarray, M_y: np.ndarray, M_couplings_x: np.ndarray, M_couplings_y: np.ndarray, HalfTurns_to_sections: np.ndarray, strands_to_sections: np.ndarray, sort_on: str = 'strands'):
    '''

    '''
    # Precompute turn and strand indexes
    strand_indexes_dict = []
    turn_indexes_dict = []
    if sort_on.casefold() == 'strands':
        for i in range(1, groups + 1):
            strand_indexes_dict.append(np.where(strands_to_sections == i)[0])
            turn_indexes_dict.append(np.where(HalfTurns_to_sections == i)[0])
    elif sort_on.casefold() == 'halfturns':
        for i in range(1, groups + 1):
            turn_indexes_dict.append(np.where(HalfTurns_to_sections == i)[0])
            strand_indexes_dict.append(np.where(HalfTurns_to_sections == i)[0])

    # Iterate over group pairs
    for i in prange(1, groups + 1):
        strand_indexes_inducing = strand_indexes_dict[i - 1]
        M_coup_x = M_couplings_x[i - 1, i - 1, :]
        M_coup_y = M_couplings_y[i - 1, i - 1, :]

        for j in range(i + 1, groups + 1):
            turn_indexes_receiving = turn_indexes_dict[j - 1]

            # Select the submatrices directly for efficiency
            Mxx = M_x[turn_indexes_receiving, :, :][:, :, strand_indexes_inducing]
            Myy = M_y[turn_indexes_receiving, :, :][:, :, strand_indexes_inducing]

            # Sum across frequency components
            M_inducing_x_sum = np.sum(Mxx, axis=0)
            M_inducing_y_sum = np.sum(Myy, axis=0)

            # Compute norms for mutual couplings
            sum_x = np.sum(np.multiply(M_inducing_x_sum, M_inducing_x_sum), axis=1)
            sum_y = np.sum(np.multiply(M_inducing_y_sum, M_inducing_y_sum), axis=1)

            norm_x = np.sqrt(np.sqrt(sum_x.real ** 2 + sum_x.imag ** 2))
            norm_y = np.sqrt(np.sqrt(sum_y.real ** 2 + sum_y.imag ** 2))
            # M_couplings_x[i - 1, j - 1, :] = sum_x / norm_x
            # M_couplings_y[i - 1, j - 1, :] = sum_y / norm_y

            if sort_on.casefold() == 'halfturns':
                norm_x = np.sqrt(np.sqrt(sum_x.real ** 2 + sum_x.imag ** 2))
                norm_y = np.sqrt(np.sqrt(sum_y.real ** 2 + sum_y.imag ** 2))
                M_couplings_x[i - 1, j - 1, :] = sum_x / norm_x
                M_couplings_y[i - 1, j - 1, :] = sum_y / norm_y
            elif sort_on.casefold() == 'strands':
                M_couplings_x[i - 1, j - 1, :] = np.divide(sum_x, M_coup_x)
                M_couplings_y[i - 1, j - 1, :] = np.divide(sum_y, M_coup_y)

    return M_couplings_x, M_couplings_y


@njit
def replace_below_tolerance(matrix: np.ndarray, tolerance: float =1e-8):
    """
    Replaces all values in the matrix that are below a given tolerance with 0.

    Parameters:
    - matrix: The input 2D array or matrix.
    - tolerance: The tolerance level below which values are set to zero (default is 1e-8).

    Returns:
    - The modified matrix with values below the tolerance set to 0.
    """
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if abs(matrix[i, j]) < tolerance:
                matrix[i, j] = 0.0
    return matrix


@njit(parallel=True, fastmath=True, cache=True)
def calculate_parameters_RLM_xy(w: np.ndarray, fMag_X: np.ndarray, fMag_Y: np.ndarray, tau: np.ndarray, I_base: np.ndarray, P_base: np.ndarray):
    '''

    '''
    num_w = len(w)
    num_k = fMag_X.shape[1]

    P = np.empty((2, num_w, num_k), dtype=np.complex128)
    I = np.empty((2, num_w, num_k), dtype=np.complex128)
    R = np.empty((num_w, num_k), dtype=np.float32)
    L = np.empty((num_w, num_k), dtype=np.float32)
    M = np.empty((2, num_w, num_k), dtype=np.complex128)

    for j in prange(num_w):
        w_j = w[j, 0]

        for k in range(num_k):
            tau_k = tau[k]
            I_base_k = I_base[k]
            P_base_k = P_base[k]

            # Precompute values that don't change in the inner loop
            w_tau_k = w_j * tau_k
            alpha = 1 / np.sqrt(1 + w_tau_k ** 2)
            I_base_alpha = I_base_k * alpha
            w_alpha = w_j * alpha

            fMag_X_k = fMag_X[j, k]
            fMag_Y_k = fMag_Y[j, k]

            # Current and power calculations
            I_x = (I_base_alpha * w_tau_k + 1j * I_base_alpha) * w_alpha * fMag_X_k
            I_y = (I_base_alpha * w_tau_k + 1j * I_base_alpha) * w_alpha * fMag_Y_k
            P_x = P_base_k * (w_alpha * fMag_X_k) ** 2
            P_y = P_base_k * (w_alpha * fMag_Y_k) ** 2

            I[0, j, k] = I_x
            I[1, j, k] = I_y
            P[0, j, k] = P_x
            P[1, j, k] = P_y

            # Resistance and inductance calculations
            I_x_real_conj = (I_x * I_x.conjugate()).real
            R_k = P_x / I_x_real_conj
            R[j, k] = R_k
            L_k = tau_k * R_k
            L[j, k] = L_k

            # Mutual inductance
            I_x_term = I_x * R_k
            I_y_term = I_y * R_k
            M[0, j, k] = (1j * w_j * L_k * I_x + I_x_term) / (1j * w_j)
            M[1, j, k] = (1j * w_j * L_k * I_y + I_y_term) / (1j * w_j)

    return M, R, L, I, P


@njit(parallel=True, fastmath=True, cache=True)
def calculate_parameters_RLM(w, fMag, tau, I_base, P_base):
    num_w = len(w)
    num_k = fMag.shape[0]

    P = np.empty((num_w, num_k), dtype=np.complex128)
    I = np.empty((num_w, num_k), dtype=np.complex128)
    R = np.empty((num_w, num_k), dtype=np.float32)
    L = np.empty((num_w, num_k), dtype=np.float32)
    M = np.empty((num_w, num_k), dtype=np.complex128)

    for j in prange(num_w):
        w_j = w[j, 0]

        for k in range(num_k):
            tau_k = tau[k]
            I_base_k = I_base[k]
            P_base_k = P_base[k]

            # Precompute values that don't change in the inner loop
            w_tau_k = w_j * tau_k
            alpha = 1 / np.sqrt(1 + w_tau_k ** 2)
            I_base_alpha = I_base_k * alpha
            w_alpha = w_j * alpha
            fMag_k = fMag[k, j]

            # Calculate complex current and power
            I_val = (I_base_alpha * w_tau_k + 1j * I_base_alpha) * w_alpha * fMag_k
            P_val = P_base_k * (w_alpha * fMag_k) ** 2

            # Assign to arrays
            I[j, k] = I_val
            P[j, k] = P_val

            # Calculate resistance and inductance
            I_val_real_conj = (I_val * I_val.conjugate()).real
            R_k = P_val / I_val_real_conj
            R[j, k] = R_k
            L_k = tau_k * R_k
            L[j, k] = L_k

            # Calculate mutual inductance
            M[j, k] = (1j * w_j * L_k * I_val + I_val * R_k) / (1j * w_j)

    return M, R, L, I, P


class BuilderTFM:
    """
    **TFM: A Simulation Tool for the Electrodynamics of Superconducting Magnets**

    **Overview**
    TFM is a tool for modeling the electrical behavior of magnets by representing them as **networks of LRC circuits**.
    - **Input:** A circuit model `.yaml` file defining the magnet’s characteristics.
    - **Output:** A library file describing the magnet network, which is then processed by **XYCE** to extract and
      plot the magnet’s **complex impedance** under various operating conditions.

    ---

    **Core Modeling Approach**
    - The magnet is modeled as a series of interconnected LRC sections.
    - Each turn has its own **L, R, and C values**, but multiple turns can be grouped into a single section to
      represent structures such as:
      - Blocks
      - Quadrants
      - Entire magnet apertures
    - If a section includes multiple turns, all turns must belong to the same aperture.

    ---

    **Simulating Eddy currents, Persistent Currents, Inter-filament and Inter-strands losses**
      TFM can model additional lossy effects by introducing loops with:
    - Inductance (L)
    - Current (I)
    - Resistance (R)
    These loops represent currents induced in the magnet's elements due to external magnetic field changes.
    TFM can automatically compute these parameters and include them in the network model.

    ---

    **Short Circuit Simulations**
    TFM allows resistances to be added across the inductances in the network circuit, enabling the simulation of
    **short circuits** at various locations with different resistance values.

    ---

    **Class Purpose: Generating TFM Models**
    `BuilderTFM` utilizes the `Options` data class, which includes flags for all magnet effects.
    - To implement a new effect:
      1. Create a corresponding data class in `DataTFM`.
      2. Add a flag in `Options`.
      3. Implement a function to compute the relevant loop parameters
         (refer to `calculate_Wedge` for non-conductor effects or `calculate_ISCC` for conductor effects).
      4. If the new effect is a Non-Conductor Effect, additional files from COMSOL MultiPhysics models are required as described below.

    - **Non-Conductor Effects** (e.g., Wedge, CB, CPS, AlRing, BS) must be listed before conductor loss flags in `Options`.

    ---

    **Handling Non-Conductor Effects**
    Non-conductor effects require multiple `.csv` files for loss calculation, obtained from **COMSOL MultiPhysics models**.
    Required files include:
    - Induced current data
    - Power loss data
    - Magnetic field data for each strand position

    For more details on the process, see https://cds.cern.ch/record/2917805 (Chapters 3.4 and 3.5).

    ---

    **Capacitance Modeling in TFM**
    Two approaches are available for implementing capacitance to ground (C_GND):

    **1. Approximated Model (`flag_LumpedC = True`)**
    - C_GND is added **only at three points**: beginning, middle, and end.
    - Requires specifying the total capacitance to ground in the `'C_ground'` entry of the `Magnet_TFM`
      object in the circuit YAML file.

    **2. Distributed Model (`flag_LumpedC = False`)**
    - A C_GND is placed before the inductance of ecah section, with an additional one at the end.
    - The capacitance is either:
      - Calculated within TFM (`flag_comsol = False`), using insulation geometry data from the `Capacitances` entry in the YAML file.
      - Extracted from a `.csv` file generated by a COMSOL model (`flag_comsol = True`).
    """



    def __init__(self, builder_LEDET= None, flag_build: bool = True,
                  output_path: str = None, local_library_path: str = None, TFM_inputs=None, magnet_data=None,
                 circuit_data=None, verbose: bool = True):
        """
               **BuilderTFM Initialization**

               This class initializes the TFM variable structure and default parameter descriptions.
               It starts froma defined `builder_LEDET` model.
               Depending on the flag values, the class can also compute various passive effects.

               :param builder_LEDET': `builderLEDET` object corresponding to the magnet.
               :param flag_build: Determines whether the model should be built.
               :param output_path: Path to save the generated `.lib` file.
               :param local_library_path: Path to the local library directory where the .csv files are stored.
               :param TFM_inputs: Contains key simulation parameters from `DataModelCircuit.py` in 'steam_sdk':
                    - **flag_PC**, **flag_ISCC**, **flag_IFCC**, **flag_ED**, **flag_Wedge**, **flag_CB**, **flag_BS**: Flag effects.
                    - **flag_debug**: If True, plots L, I, M and K of each effect in a loop.
                    - **flag_LumpedC**: If True, Approximated Capacitance Model.
                                        If False, Distributed Capacitance Model.
                    - **T**: Simulation temperature.
                    - **current**: Simulation current.
                    - **B_nom_center**: Magnetic field in the center of the apertures at the nominal current.

               :param Magnet_data: Magnet class from DataModelCircuit.py in steam_sdk.data, includes:

                    - **circuit_name**: Name of the circuit.
                    - **name**: Magnet name.
                    - **n_apertures**: Number of apertures.
                    - **multipole_type**: Magnet's type (Only quadrupole and dipole supported).
                    - **C_ground**: Total capacitance to ground of the magnet. (Needed only for the approximated capacitance model).
                    - **turn_to_section**: List mapping each turn to its corresponding section number. (Defaults is one section per aperture)
                    - **section_to_aperture**: List mapping each section to the corresponding aperture number.
                    - **magnet_Couplings**: Dataclass containing all the mutual couplings between the eddy currents in the different
                                        metallic components.
                    - **magnet_Wedge**: Dataclass to represent the eddy currents flowing in the Wedge.
                    - **magnet_CB**: Dataclass for the eddy currents flowing in the ColdBore.
                    - **magnet_CPS**: Dataclass for the eddy currents flowing in the Coil Protection Sheets.
                    - **magnet_AlRing**: Dataclass for the eddy currents flowing in the Aluminum Ring.
                    - **magnet_BS**: Dataclass for the eddy currents flowing in the Beam Screen.
                    - **magnet_Shorts**: Dataclass to specify the sections to be shorted and whith which resistance value.
                    - **magnet_Capacitances**: DataClass with all the values needed to evaluate the capacitance to ground
                      and the turn-to-turn capacitance of the magnet.

               """
        print('\n ***************************** BuildTFM ***************************** \n Starting buildTFM')
        start_TFM = time.time()

        self.verbose = verbose
        self.General = General()
        self.Turns = Turns()
        self.HalfTurns = HalfTurns()
        self.Strands = Strands()
        self.Options = Options()
        self.PC = PC()
        self.IFCC = IFCC()
        self.ISCC = ISCC()
        self.ED = ED()
        self.Wedge = Wedge()
        self.CB = CB()
        self.CPS = CPS()
        self.AlRing = AlRing()
        self.BS = BS()
        self.Shorts = Shorts()
        self.Capacitances = Capacitances()
        self.print_nodes = []

        # TODO: HardCoded values -> tau constant AlRing
        self.effs_cond = ['PC','ISCC','IFCC','ED']
        self.effs_components = ['Wedge','AlRing','BS','CB','CPS']
        self.effs_noDir = ['ISCC']
        frequency = np.logspace(0, 6, 120 + 1)
        self.frequency = frequency
        self.mu0 = 4 * np.pi / 1e7
        # Flag to indicate whether the capacitance calculation refers to the magnet with or without QH Heaters
        self.flag_QH = True
        # Flag to specify whether only the frequencies around the resonance peak should be used for calculating Ceq
        # If enabled, the simulation includes the first frequency, the frequency before f_peak, all frequencies between
        # f_peak and 10*f_peak, and the last frequency.
        self.flag_frequency_capacitance = True

        if flag_build:
            if not builder_LEDET or not magnet_data.name:
                 raise Exception('Cannot build model without providing BuilderLEDET object with Inputs dataclass and magnet_name')

            self.magnet_name = magnet_data.name
            self.magnet_circuit_name = magnet_data.circuit_name
            self.temperature = TFM_inputs.temperature
            # Retrieving the number of apertures from the circuit input yaml file, default: 2
            if magnet_data.n_apertures:
                self._setAttribute(self.General, 'apertures', magnet_data.n_apertures)
            else:
                self._setAttribute(self.General, 'apertures', 2)
            # Retrieving the multipole type from the circuit input yaml file, default: dipole
            if magnet_data.n_apertures:
                self._setAttribute(self.General, 'multipole_type', magnet_data.multipole_type)
            else:
                self._setAttribute(self.General, 'multipole_type', 'dipole')
            # Set-up magnet components and validate some inputs
            self.__set_magnetData(magnet_data)
            self.local_library_path = local_library_path
            self.B_nom_center = TFM_inputs.B_nom_center

            # Translate the Inputs dataclass of BuilderLEDET in a dictionary
            ledet_inputs = asdict(builder_LEDET.Inputs)
            self.ledet_inputs = ledet_inputs
            self.ledet_auxiliary = builder_LEDET.Auxiliary
            self.ledet_options = builder_LEDET.Options
            self.TFM_inputs = TFM_inputs
            self.magnet_data = magnet_data
            self.output_path = output_path
            self.flag_debug = TFM_inputs.flag_debug

            self.conductor_to_group = np.array(builder_LEDET.model_data.CoilWindings.conductor_to_group)

            self.__assignTurnsToSections()
            self.__translateModelDataToTFMGeneral()
            self.__translateModelDataToTFMHalfTurns()
            self.__translateModelDataToTFMStrands()
            self.__setOptions()
            if self.effects:
                self.__calculate_field_contributions()

            if circuit_data is not None:
                self.domain = circuit_data.Analysis.analysis_type
            else:
                self.domain = 'frequency'

            if output_path is not None and circuit_data is not None:
                library_name = circuit_data.Netlist[self.magnet_circuit_name].value
                print(f'- Writing library: {library_name}')
                print(f'- Effects considered: {self.effects}')
                self._generate_library(output_path=output_path, library_name=library_name, verbose=self.verbose)
                print(f'- Time to coupling parameter estimation: {np.round(time.time() - start_TFM,2)} s')
                if self.effects:
                    start_ccp = time.time()
                    self.change_coupling_parameter()
                    print(f'- Time for coupling parameter estimation: {np.round(time.time() - start_ccp, 2)} s')

    ####################################################################################################################
    ######################################## TFM DATACLASSES ATTRIBUTE SETTING ########################################
    def __assignTurnsToSections(self):
        '''
        This function assigns the value to turns_to_sections vector in the Turns dataclass attributes.

        This function assigns the value to turns_to_apertures vector in the Turns dataclass attributes.

        This function assigns the value to HalfTurns_to_sections vector in the HalfTurns dataclass attributes.

        turns_to_sections is a vector long as the number of turns and each element contains the id of the section to which it is assigned.

        A section is a LRC circuit inside the magnet circuit in the generated lib file
        '''
        nT = self.ledet_inputs['nT']
        n_Turns = np.sum(nT)// 2
        elPair_grouped = self.ledet_auxiliary.elPairs_GroupTogether
        elPairs_RevElOrder = self.ledet_auxiliary.elPairs_RevElOrder
        HalfTurns_to_groups = np.repeat(np.arange(len(nT)) + 1, nT)

        # the first half of elPairs_GroupTogether will be assigned to the first aperture, the second half to the second aperture
        if self.General.apertures == 2:
            idx = 0
            turns_to_apertures = np.zeros(n_Turns, dtype=int)
            for ap in range(1, 2 + 1):
                for i in range(idx, idx + len(elPair_grouped) // 2):
                    idx_group = elPair_grouped[i][0] if elPair_grouped[i][0] < elPair_grouped[i][1] else elPair_grouped[i][1]
                    idx_T = np.where(HalfTurns_to_groups == idx_group)[0]
                    turns_to_apertures[np.ix_(idx_T)] = ap
                idx = idx + len(elPair_grouped) // 2
        else:
            turns_to_apertures = np.ones((len(HalfTurns_to_groups),))
        self._setAttribute(self.Turns, 'turns_to_apertures', turns_to_apertures)
        HalfTurns_to_apertures =  np.tile(turns_to_apertures, 2)
        self._setAttribute(self.HalfTurns, 'HalfTurns_to_apertures', HalfTurns_to_apertures)

        if self.magnet_data.turn_to_section is not None: # If turn_to_section is not none, the turns_to_section vector is the one specified as input of the yaml file
            self.magnet_data.turn_to_section = np.array(self.magnet_data.turn_to_section).astype(int)
            n_sections = max(self.magnet_data.turn_to_section)
            for i in range(1,n_sections+1):
                if i in self.magnet_data.turn_to_section: continue
                else: raise Exception(f'Group {i} is not assigned to any turn. Please check!')
            turns_to_sections = np.array(self.magnet_data.turn_to_section).astype(int)
            ap_turns_to_sections = turns_to_sections
            HalfTurns_to_sections = np.tile(ap_turns_to_sections, 2).astype(int)
            turns_to_sections = ap_turns_to_sections

            sections_to_aperture = np.zeros((n_sections,))
            for i in range(1,n_sections+1):
                sections_to_aperture[i-1] = np.unique(turns_to_apertures[np.where(ap_turns_to_sections==i)[0]])[0]
            self._setAttribute(self.General, 'sections_to_aperture', sections_to_aperture.astype(int))
        else:
            conductor_to_group = self.conductor_to_group
            HalfTurns_to_sections = conductor_to_group[HalfTurns_to_groups - 1]
            turns_to_sections = HalfTurns_to_sections[:int(len(HalfTurns_to_sections)/2)]  # To get turns_to_section from Halfturns_to_sections we take one element every two elements
            if self.General.apertures==2 and max(turns_to_sections)==1:  # If we have only one conductor but two apertures we set Ap1 = Section 1 and Ap2 = Section 2
                turns_to_sections = turns_to_apertures
                sections_to_aperture = np.array([1, 2]).astype(int)
                self._setAttribute(self.General, 'sections_to_aperture', sections_to_aperture)
            else: # Else we set the first n_conductor groups in Aperture one and the 2nd n_conductor groups in Aperture 2
                turns_to_sections[np.where(turns_to_apertures == 2)[0]] += max(conductor_to_group)
                sections_to_aperture = np.array([1]*max(conductor_to_group)+[2]*max(conductor_to_group)).astype(int)
                self._setAttribute(self.General, 'sections_to_aperture', sections_to_aperture)
            HalfTurns_to_sections = np.concatenate([turns_to_sections, turns_to_sections])
            ap_turns_to_sections = turns_to_sections

        self._setAttribute(self.Turns, 'turns_to_sections', ap_turns_to_sections.astype(int))
        self._setAttribute(self.HalfTurns, 'HalfTurns_to_sections', HalfTurns_to_sections.astype(int))

        #### Assign the correct electrical order to the sections
        indexTstop = np.cumsum(nT)
        indexTstop = indexTstop.tolist()
        indexTstart = [1]
        for i in range(len(nT) - 1):
            indexTstart.extend([indexTstart[i] + nT[i]])
        el_order_half_turns = [];
        for p in range(len(elPair_grouped)):
            if nT[elPair_grouped[p][0] - 1] != nT[elPair_grouped[p][1] - 1]:
                raise Exception(
                    'Pair of groups defined by the variable elPairs_GroupTogether must have the same number of half-turns.')
            for k in range(nT[elPair_grouped[p][0] - 1]):
                if elPairs_RevElOrder[p] == 0:
                    el_order_half_turns.append(indexTstart[elPair_grouped[p][0] - 1] + k);
                    el_order_half_turns.append(indexTstart[elPair_grouped[p][1] - 1] + k);
                if elPairs_RevElOrder[p] == 1:
                    el_order_half_turns.append(indexTstop[elPair_grouped[p][0] - 1] - k);
                    el_order_half_turns.append(indexTstop[elPair_grouped[p][1] - 1] - k);
        el_order_half_turns_Array = np.int_(el_order_half_turns)
        el_order_turns_Array = el_order_half_turns_Array[::2].astype(int)
        el_order_turns_Array[np.where(el_order_turns_Array>n_Turns)[0]] = el_order_turns_Array[np.where(el_order_turns_Array>n_Turns)[0]]-n_Turns

        el_order_sections = np.zeros((len(el_order_half_turns_Array),))
        for i in range(1, len(HalfTurns_to_sections) + 1):
            el_order_sections[np.where(el_order_half_turns_Array == i)[0][0]] = HalfTurns_to_sections[i - 1]
        change_indices = np.diff(el_order_sections) != 0
        result = np.append(True, change_indices)
        el_order_sections = el_order_sections[result]
        self._setAttribute(self.General, 'el_order_turns', el_order_turns_Array)
        self._setAttribute(self.General, 'el_order_sections',
                            np.array(list(dict.fromkeys(el_order_sections))).astype(int))
        self._setAttribute(self.General, 'el_order_to_apertures',
                            sections_to_aperture[np.array(list(dict.fromkeys(el_order_sections))).astype(int) - 1])


    def __translateModelDataToTFMGeneral(self):
        '''
        This function saves the appropriate BuilderLEDET Inputs dataclass values for the General dataclass attributes.

        L_mag instead is set in the function __calculate_Inductance_Sections
        '''
        self._setAttribute(self.General, 'magnet_name', self.magnet_name)
        if self.TFM_inputs.flag_LumpedC is not None:
            self._setAttribute(self.General, 'flag_LumpedC',  self.TFM_inputs.flag_LumpedC)
        self._setAttribute(self.General, 'magnet_length', self.ledet_inputs['l_magnet'])
        self._setAttribute(self.General, 'I_magnet', self.TFM_inputs.current)
        self._setAttribute(self.General, 'local_library_path', self.local_library_path)
        nT = self.ledet_inputs['nT']
        self._setAttribute(self.General, 'num_HalfTurns', np.sum(nT))
        nStrands = sum(self.ledet_inputs['nT']*self.ledet_inputs['nStrands_inGroup'])
        self._setAttribute(self.General, 'num_Strands', nStrands)
        n_sections = max(self.Turns.turns_to_sections)
        self._setAttribute(self.General, 'sections', n_sections)
        # self._setAttribute(self.General, 'apertures', max(self.Turns.turns_to_apertures))
        C_ground = float(self.magnet_data.C_ground)
        self._setAttribute(self.General, 'C_ground', C_ground)


    def __calculate_warm_resistance(self): # Utility function to calculate R_warm in self.General and self.HalfTurns
        '''
            Function to calculate the warm resistance, both per cable and per magnet

            It saves the R_warm_cable n the HalfTurns dataclass and the R_warm in the General dataclass
        '''

        if self.Options.flag_SC:
            # If the Magnet is in SC state, let's set by default a warm resistance of 1nOhm
            R_warm = 1e-9
            R_warm_cable = np.repeat(R_warm, self.General.num_HalfTurns)
        else:
            RRR = self.HalfTurns.RRR
            T = self.temperature
            fsc = self.Strands.fsc
            dws = self.Strands.diameter
            l = self.General.magnet_length
            I = self.General.I_magnet
            HT_to_Strands = self.HalfTurns.n_strands

            B = self.Strands.f_mag_Roxie * I
            B = B[:, 0]
            # Area of the strands
            Area_strands = (1-fsc) * np.pi * (dws/2) ** 2

            cont = 0
            A_cable = []
            B_cable = []

            # For each HalfTurns, calculates the total Area as the sum of the Areas of each strand corresponding to that HalfTurn
            # For each HalfTurns, calculates the total B as the average of the B of each strand corresponding to that HalfTurn
            for i in range(self.General.num_HalfTurns):
                n_strand_cable = HT_to_Strands[i]
                A_cable_HT = np.sum(Area_strands[cont: cont+n_strand_cable])
                B_cable_HT = np.mean(B[cont: cont+n_strand_cable])
                A_cable.append(A_cable_HT)
                B_cable.append(B_cable_HT)
                cont += n_strand_cable

            rho = self.__rhoCu_nist(T=T, RRR= RRR, B=np.array(B_cable))
            # Calculates the R_warm for each HalfTurn as R_HT = rho_HT * l_mag / A_HT
            R_warm_cable = rho * l / (np.array(A_cable))
            # Calculates the total R_warm as the sum of R_warm_HT
            R_warm = np.sum(R_warm_cable)

        self._setAttribute(self.HalfTurns, 'R_warm', R_warm_cable)
        self._setAttribute(self.General, 'R_warm', R_warm)


    def __set_magnetData(self, magnet_data: Magnet_TFM, ):
        '''

        '''
        for keyMagnetData, value in magnet_data.__dict__.items():
            if ('magnet_' in keyMagnetData and keyMagnetData != 'magnet_Couplings'):
                eff = keyMagnetData.split('_')[-1]
                if value:
                    if eff == 'CPS':
                        if isinstance(value.rho_CPS, str):
                            if value.rho_CPS == 'SS':
                                value.rho_CPS = self.__rhoSS_nist(self.temperature)
                            elif 'e-' in value.rho_CPS:
                                value.rho_CPS = np.array([float(value.rho_CPS)])
                            else:
                                raise Exception(f'Do not understand rho_CPS {value.rho_CPS}')

                    obj = self._getAttribute(self, f'{eff}')
                    has_non_empty = any(
                        v is not None and v != [] and not (isinstance(v, np.ndarray) and v.size == 0) for v in
                        vars(obj).values())
                    if not has_non_empty:
                        self._setAttribute(self, f'{eff}', value)
                    else:
                        for key, val in vars(value).items():
                            if val is not None and val != [] and not (isinstance(val, np.ndarray) and val.size == 0):
                                self._setAttribute(self._getAttribute(self, f'{eff}'), f'{key}', val)
            if keyMagnetData == 'Shorts':
                self.Shorts = magnet_data['Shorts']
        return


    def __setDataCapacitanceCalculation(self):
        '''
            This function stores essential information in the `HalfTurns` class to facilitate capacitance calculation, including:

            - An array with a length equal to the number of HalfTurns, specifying the layer each HalfTurn belongs to.
            - An array listing all HalfTurns that contribute to capacitance to the ground. This includes HalfTurns
              in the outer layer and those in the inner layer that are not covered by the outer layer.
            - An array identifying the HalfTurns that contact the ground along their long side.

            Assumptions:
                1. The Turn numbering starts from the outer layer, from the mid plane to the pole
                2. If the magnet has more than one layer, the layers are numbered in increasing order going from the outer to the inner layer
                3. The numbering of the inner layer is consistent with the outer
                4. If the magnet has more than one layer, the first group of the inner layer cannot contain just 1 HT
                5. If the magnet has more than one layer, only the last two groups of the inner layer can be in contact with ground
                6. HalfTurns cannot be in contact along the height if they don't belong to the same half pole

        '''
        C_cont_height_start = self.ledet_inputs['iContactAlongHeight_From']
        C_cont_height_stop = self.ledet_inputs['iContactAlongHeight_To']
        multipole_type = self.General.multipole_type
        HalfTurns_to_groups = self.HalfTurns.HalfTurns_to_groups

        # Retrieving the number of Halfturns in each half pole
        if multipole_type == 'dipole':  # Retrieve number of HT in a pole for dipole magnets
           n_HalfPoles = 4 * self.General.apertures
        elif multipole_type == 'quadrupole':
           n_HalfPoles = 8 * self.General.apertures
        else:
            raise Exception('Unrecognized symmetry type: only dipole and quadrupole are supported')
        n_HT_HalfPole = self.General.num_HalfTurns //n_HalfPoles

        # Assuming self.General.num_HalfTurns and n_HT_HalfPole are defined
        num_HalfTurns = self.General.num_HalfTurns  # Total number of half-turns
        indices = np.arange(1, num_HalfTurns + 1)  # Create an array [1, 2, ..., num_HalfTurns]
        HalfTurns_to_HalfPoles = ((indices - 1) // n_HT_HalfPole) + 1  # Calculate pole numbers
        self._setAttribute(self.HalfTurns, 'HalfTurns_to_HalfPoles', HalfTurns_to_HalfPoles)

        # Retrieving the layer to which HalfTurn belong
        if len(C_cont_height_start) != 1:
            # If the magnet has more than one layer, then the layers are numbered from the outside to the inside (e.g. outer layer = 1, inner layer = 2)
            groups_external_layer = []
            idx_remove = []
            for i in range(len(C_cont_height_start)):
                # Add group if it's not already in the list and meets conditions
                group = HalfTurns_to_groups[C_cont_height_start[i] - 1]
                pole_start = HalfTurns_to_HalfPoles[C_cont_height_start[i] - 1]
                pole_stop = HalfTurns_to_HalfPoles[C_cont_height_stop[i] - 1]
                if pole_start == pole_stop:
                    if group not in groups_external_layer:
                        groups_external_layer.append(group)
                else:
                    idx_remove.append(i)
            HalfTurns_to_layers = np.ones(self.General.num_HalfTurns, dtype=int) * 2
            idx_external_layer = np.isin(HalfTurns_to_groups, groups_external_layer)
            HalfTurns_to_layers[idx_external_layer] = 1
            # Save the new adjusted vector for the thermal connection along the height
            self.C_cont_height_start = np.array([value for i, value in enumerate(C_cont_height_start) if i not in idx_remove])
            self.C_cont_height_stop = np.array([value for i, value in enumerate(C_cont_height_stop) if i not in idx_remove])
        else:  # If there are no HT in the thermal connection, then there is only one layer
            HalfTurns_to_layers = np.ones(self.General.num_HalfTurns).astype(int)

        if np.max(HalfTurns_to_layers) == 2:
            # Retrieving the total number of HalfTurns in the external layer for one pole
            idx_ext = np.where(HalfTurns_to_layers == 1)[0]
            HT_extLayer_1pole = len(idx_ext) //n_HalfPoles
            # Correction to apply to magnet like MQXB which has 1 HT in one group in the ext layer, not in contact to anything
            first_group_int = HalfTurns_to_groups[HT_extLayer_1pole]
            if len(np.where(HalfTurns_to_groups == first_group_int)[0]) == 1:
                for i in range(n_HalfPoles):
                    groups_external_layer.append(first_group_int + i * np.max(HalfTurns_to_groups) //n_HalfPoles)
                idx_external_layer = np.isin(HalfTurns_to_groups, groups_external_layer)
                HalfTurns_to_layers[idx_external_layer] = 1
                idx_ext = np.where(HalfTurns_to_layers == 1)[0]
                HT_extLayer_1pole = len(idx_ext) //n_HalfPoles
        self._setAttribute(self.HalfTurns, 'HalfTurns_to_layers', HalfTurns_to_layers)

        # Retrieving the HalfTurns touching the ground also along their long side
        HalfTurns_wide_ins = []
        n_HT_int = 0
        for i in range(1,n_HalfPoles + 1):
            # Adding to the wide insulation list, the last HalfTurn of each "pole"
            if np.max(HalfTurns_to_layers) == 2:
                n_HT_ext = n_HT_int + HT_extLayer_1pole
                HalfTurns_wide_ins.append(n_HT_ext)
            n_HT_int = i * n_HT_HalfPole
            HalfTurns_wide_ins.append(n_HT_int)
        self._setAttribute(self.HalfTurns, 'HalfTurns_wide_ins', np.array(HalfTurns_wide_ins))

        # Retrieving the HalfTurns contributing to the capacitance to ground
        HalfTurns_ground_ins = []
        # Retrieving the numbers of groups in each pole
        if np.max(HalfTurns_to_layers) == 1:
            HalfTurns_ground_ins = np.arange(1, self.General.num_HalfTurns+1)
        else:
            n_groups_pole = np.max(HalfTurns_to_groups) //n_HalfPoles
            # Taking the number of the last group in each pole
            last_groups = []
            for i in range(1,n_HalfPoles+1):
                last_groups.append(i*n_groups_pole)
                last_groups.append(i * n_groups_pole - 1)
            for i in range(self.General.num_HalfTurns):
                if ((HalfTurns_to_groups[i] not in groups_external_layer and i+1 not in C_cont_height_stop and HalfTurns_to_groups[i] in last_groups)
                        or HalfTurns_to_groups[i] in groups_external_layer):
                        HalfTurns_ground_ins.append(i+1)
            HalfTurns_ground_ins = np.array(HalfTurns_ground_ins)
        self._setAttribute(self.HalfTurns, 'HalfTurns_ground_ins', HalfTurns_ground_ins)


    def __translateModelDataToTFMHalfTurns(self):
        '''
        This function saves the appropriate BuilderLEDET Inputs dataclass values for the HalfTurns dataclass attributes.

        The saved data are arrays with len equal to the total number of HalfTurns
        '''
        # Values that can't be directly obtained from the Inputs dataclass
        nT = self.ledet_inputs['nT']
        HalfTurns_to_groups = np.repeat(np.arange(len(nT)) + 1, nT)
        self._setAttribute(self.HalfTurns, 'HalfTurns_to_groups', HalfTurns_to_groups)
        HalfTurns_to_conductor = self.conductor_to_group[HalfTurns_to_groups - 1]
        self._setAttribute(self.HalfTurns, 'HalfTurns_to_conductor', HalfTurns_to_conductor)
        turns_to_conductor = HalfTurns_to_conductor[::2]
        nc = np.repeat(nT, nT)
        self._setAttribute(self.HalfTurns, 'Nc', nc)
        HalfTurns_polarity = np.repeat(self.ledet_inputs['polarities_inGroup'], nT)
        self._setAttribute(self.HalfTurns, 'HalfTurns_polarity', HalfTurns_polarity)

        # Values that can be directly obtained from the Inputs dataclass
        for keyInputData, value in self.ledet_inputs.items():
            keyTFM = lookupModelDataToTFMHalfTurns(keyInputData)
            if keyTFM in self.HalfTurns.__annotations__:
                if isinstance(value, list):
                    self._setAttribute(self.HalfTurns, keyTFM, np.array(value))
                else:
                    self._setAttribute(self.HalfTurns, keyTFM, value[HalfTurns_to_groups - 1])
        # Fitting value for ISCL, varying between C=1 (Ns=8) and C=1.15 (Ns=40) [-]
        # Reference: Arjan's Thesis, Chapter 4, Page 78, Equation 4.31
        C_strand = 0.0046875 * self.HalfTurns.n_strands + 0.9625
        self._setAttribute(self.HalfTurns, 'C_strand', C_strand)

        self.__setDataCapacitanceCalculation()


    def __translateModelDataToTFMStrands(self):
        '''
        This function saves the appropriate BuilderLEDET Inputs dataclass values for the Strands dataclass attributes.

        The saved data are arrays with len equal to the total number of Strands
        '''
        strands_to_conductor = np.repeat(self.HalfTurns.HalfTurns_to_conductor, self.HalfTurns.n_strands)
        self._setAttribute(self.Strands, 'strands_to_conductor', strands_to_conductor)
        strands_to_sections = np.repeat(self.HalfTurns.HalfTurns_to_sections, self.HalfTurns.n_strands)
        self._setAttribute(self.Strands, 'strands_to_sections', strands_to_sections)
        strands_current = np.repeat(self.HalfTurns.HalfTurns_polarity, self.HalfTurns.n_strands)/np.repeat(self.HalfTurns.n_strands, self.HalfTurns.n_strands)
        self._setAttribute(self.Strands, 'strands_current', strands_current)
        self._setAttribute(self.Strands, 'strands_to_apertures', np.repeat(self.HalfTurns.HalfTurns_to_apertures, self.HalfTurns.n_strands))
        strands_to_halfturn = np.repeat(np.arange(1,self.General.num_HalfTurns+1),self.HalfTurns.n_strands)
        self._setAttribute(self.Strands, 'strands_to_halfturn', strands_to_halfturn)
        for keyLedetData, value in self.ledet_inputs.items():
            keyTFM = lookupModelDataToTFMStrands(keyLedetData)
            if keyTFM in self.Strands.__annotations__:
                repeated_value = np.repeat(value[self.HalfTurns.HalfTurns_to_groups - 1], self.HalfTurns.n_strands)
                self._setAttribute(self.Strands, keyTFM, repeated_value)


    def __setOptions(self):
        '''
        This function sets to the Option DataClass the flags to know which effects should be included in the magnet model

        :attribute flag_PC: if True includes the Persistent Current effect

        :attribute flag_IFCC: if True includes the Inter Filament Coupling Current effect

        :attribute flag_ISCC: if True includes the Inter Strands Coupling Current effect

        :attribute flag_Wedge: if True includes the Wedge effect

        :attribute flag_CB: if True includes the Cold Bore effect

        :attribute flag_ED: if True includes the Eddy Currents effect in the Copper Sheath

        :attribute flag_BS: if True includes the BeamScreen effect in the Copper Sheath

        :attribute flag_SC: set to True depending on the T (indicates if a magnet is in Superconducting state)
        '''
        if self.temperature <  min(self.ledet_inputs['Tc0_NbTi_ht_inGroup']):
            flag_SC = True
        else:
            flag_SC = False

        self._setAttribute(self.Options, 'flag_SC', flag_SC)
        self.__calculate_warm_resistance()

        effects = {}
        self.effs_notCond = []
        for keyTFMData, value in self.TFM_inputs.__dict__.items():
            if keyTFMData.startswith('flag') and keyTFMData != 'flag_debug' and keyTFMData != 'flag_LumpedC':
                if type(value) != bool and type(value) != int:
                    value = False
                self._setAttribute(self.Options, keyTFMData, value)

                if value==True:
                    # Saving in a Dictionary the effects names and the flag values
                    eff = keyTFMData.split('_')[-1]
                    effects[eff] = value
                    if eff not in self.effs_cond:
                        self.effs_notCond.append(eff)
                        self.effs_noDir.append(eff)
        self.effects = effects


    def __calculate_field_contributions(self):  # Utility function to calculate f_mag in __translateModelDataToTFMStrands
        '''
        Calculates the field in each filament of the MB magnet.

        It saves in the Strands dataclass vectors of shape [len(freq), n_strands]

        : f_mag, f_mag_X and f_mag_Y taken from Roxie

        : f_mag, f_mag_X and f_mag_Y taken from the magnet Comsol Model with no effects included
        '''

        local_library_path = os.path.join(Path(self.General.local_library_path).resolve(), 'TFM_input')
        name = self.General.magnet_name

        # Taking the excel file containing the field values of the Comsol Model without any effect
        full_file_Comsol = Path(os.path.join(local_library_path, f'Field_Map_{name}.csv')).resolve()

        if (any(item in self.effects for item in self.effs_components) and any(item in self.effects for item in self.effs_cond)
                and os.path.exists(full_file_Comsol)):
            # Load the data file
            df_Comsol = pd.read_csv(full_file_Comsol, header=None, dtype=str, na_filter=False)
            # Extract frequency values as floats
            frequency = df_Comsol.iloc[1, 2::2].astype(float).values
            if len(frequency) != len(self.frequency):
                if self.verbose: print('Interpolation frequency is different. Adjusting internal frequency.')
                self.frequency = frequency
            elif not np.allclose(frequency, self.frequency):
                if self.verbose: print('Interpolation frequency is different. Adjusting internal frequency.')
                self.frequency = frequency
            # Extract and parse complex values
            data = df_Comsol.values[2:, 2:].astype(str)
            df_Comsol_values = preprocess_complex_strings(data).T
            # Calculate the required magnitudes and real components
            f_mag_X_Comsol, f_mag_Y_Comsol, f_mag_Comsol = calculate_magnitudes(df_Comsol_values)

            self._setAttribute(self.Strands, 'f_mag_X_Comsol', f_mag_X_Comsol)
            self._setAttribute(self.Strands, 'f_mag_Y_Comsol', f_mag_Y_Comsol)
            self._setAttribute(self.Strands, 'f_mag_Comsol', f_mag_Comsol)
        elif any(item in self.effects for item in self.effs_components):
            print(f'Warning: No COMSOL field map could be found! Required location: {full_file_Comsol}')

        if any(item in self.effects for item in self.effs_cond):
            start_ROXIE = time.time()
            f_mag_Roxie, f_mag_X_Roxie, f_mag_Y_Roxie = self.__retrieve_field_contributions_Roxie()
            print(f'ROXIE and Biot-Savart calculation took: {np.round(time.time() - start_ROXIE,2)} s')
            self._setAttribute(self.Strands, 'f_mag_X_Roxie', f_mag_X_Roxie)
            self._setAttribute(self.Strands, 'f_mag_Y_Roxie', f_mag_Y_Roxie)
            self._setAttribute(self.Strands, 'f_mag_Roxie', f_mag_Roxie)

        if (any(item in self.effects for item in self.effs_components) and any(
                item in self.effects for item in self.effs_cond)
                and os.path.exists(full_file_Comsol)):
            e_field = []
            self.Strands.strands_to_apertures = np.zeros((f_mag_Comsol.shape[1],))
            for ap in range(1, self.General.apertures + 1):
                idx_sec = np.where(self.General.sections_to_aperture == ap)[0]
                idx_s = []
                for n in idx_sec:
                    idx_s.append(np.where(self.Strands.strands_to_sections == n + 1)[0])
                idx_s = [item for row in idx_s for item in row]
                e_field.append(
                    [len(np.where(np.sign(f_mag_Y_Roxie[0, idx_s]) - np.sign(f_mag_Y_Comsol[0, idx_s]) == 0)[0])])
                self.Strands.strands_to_apertures[idx_s] = ap
            if len(e_field) > 1:
                if e_field[0] > e_field[1]:
                    self.General.COMSOL_ap = 1
                else:
                    self.General.COMSOL_ap = 2
            else:
                self.General.COMSOL_ap = 1
        return


    ####################################################################################################################
    ############################################ FUNCTIONS TO READ AND ASSIGN F_MAG #####################################
    def __read_COMSOL_field_file(self, Effect: str = None, field_int_value: float = None) -> np.ndarray:
        '''
         Calculates the diff_field in each filament due to the given effect as the mutual difference between the result of the
         '__retrieve_field_contributions_COMSOL'function and the field obtained from the Comsol simulation w/o effects.
         Then returns the field in each filament as the sum of the field from Roxie and the diff_field

         :param Effect: str that indicates the corresponding Not Conductor Loss effect -> Wedge or CB or BS or CPS or AlRing
        '''
        if Effect is not None:
            f_mag_X_Roxie = self.Strands.f_mag_X_Roxie
            f_mag_Y_Roxie = self.Strands.f_mag_Y_Roxie
            f_mag_Comsol = self.Strands.f_mag_Comsol
            f_mag_X_Comsol = self.Strands.f_mag_X_Comsol
            f_mag_Y_Comsol = self.Strands.f_mag_Y_Comsol

            fMag, fMag_X, fMag_Y = self.__retrieve_field_contributions_COMSOL(Effect=Effect, field_int_value=field_int_value)

            f_X_diff = fMag_X  - f_mag_X_Comsol
            f_Y_diff = fMag_Y  - f_mag_Y_Comsol

            idx_s = np.where(self.Strands.strands_to_apertures==self.General.COMSOL_ap)[0]
            if np.any(np.isnan(f_Y_diff[:,idx_s])): raise Exception('Error in field calculation.')

            # # Fill up other aperture if not provided from COMSOL
            if (np.count_nonzero(np.isnan(f_Y_diff[0, :])) == np.count_nonzero(np.isnan(f_X_diff[0, :]))):
                if int(np.count_nonzero(np.isnan(f_Y_diff[0, :]))) == int(f_Y_diff.shape[1] / 2):
                    idx_val1 = np.where(np.isnan(f_Y_diff[0, :]))[0][0]
                    n_sections = int(len(f_Y_diff[0, :]) / idx_val1)

                    for j in range(n_sections):
                        if j % 2: continue
                        idx_start = int(len(f_Y_diff[0, :]) - (j + 1) * idx_val1)
                        idx_end = int(len(f_Y_diff[0, :]) - (j) * idx_val1)
                        idx_c_start = int(j * idx_val1)
                        idx_c_end = int((j + 1) * idx_val1)
                        f_X_diff[:, idx_start:idx_end] = f_X_diff[:, idx_c_start:idx_c_end]
                        f_Y_diff[:, idx_start:idx_end] = -1*f_Y_diff[:, idx_c_start:idx_c_end]

            return f_X_diff, f_Y_diff


    def __retrieve_field_contributions_COMSOL(self, Effect: str = None, field_int_value: float = None) -> np.ndarray:
        '''
        Extracts the magnetic field data for each filament of the MB magnet from Excel files corresponding to a specific
        Comsol Model that includes a given effect.
        Multiple files exist for each effect, with each file resulting from a simulation using a different value of a
        particular parameter (usually temperature, T).

        To select the most accurate data, the function performs an interpolation between the desired value of the parameter
        and the data from the four closest simulation values saved in the Excel files.

        :param Effect: str indicating the specific Not Conductor Loss effect (either "Wedge" or "CB").

        :return f_mag: field in each filament for a magnet that includes the specified effect.
        :return f_mag_X: field along the X-axis in each filament for a magnet that includes the specified effect.
        :return f_mag_Y: field along the Y-axis in each filament for a magnet that includes the specified effect.
        '''

        local_library_path = os.path.join(Path(self.General.local_library_path).resolve(), 'TFM_input')
        frequency = self.frequency

        Param = []
        files_Field = []
        df_array_X = []
        df_array_Y = []
        df_array_Mag = []

        # value is the desired parameter for which we want to find accurate f_mag, f_mag_X, f_mag_Y
        # usually it is the T of the simulation, if it is not it can be specified in field_interp_value
        if field_int_value:
            value = field_int_value
        else:
            value = self.temperature

        # Loop to extract all the possible parameters values for the Comsol model with effect that are presents in the excel files
        for dir in os.listdir(local_library_path):
            if dir.startswith('Field_Map'):
                if Effect in dir:
                    parameter = dir.replace('.csv','').split('_')[-1]
                    Param.append(float(parameter)) # Saving the parameter values
                    files_Field.append(dir) # Saving the file directory

        Param = np.array(Param)
        files_Field = np.array(files_Field)

        if float(value) in Param: # If there is one file performed with parameter = value no need for the interpolation
            closest_Param = np.array([value]) # Taking just the value as closest parameter
        elif(value < Param.min() or value > Param.max()):# If the value is out of bounds -> error
            raise Exception('Error: Parameter out of range')
        else:
            closest_indices = np.argsort(np.abs(Param - value))[:4] # Otherwise taking the 4 closest values of the excel files
            closest_Param = Param[closest_indices]

        for i in range(len(closest_Param)): # Reading the files of the closest parameter simulations
            file = os.path.join(local_library_path, files_Field[i])
            with pd.option_context('future.no_silent_downcasting', True):
                df_COMSOL = pd.read_csv(file, header=None, dtype=str, na_filter=False).replace({'': 0})
                df_COMSOL = df_COMSOL.loc[:, (df_COMSOL != 0).any(axis=0)]
            mapping = np.vectorize(lambda t: complex(t.replace('i', 'j')))
            df_COMSOL = mapping(df_COMSOL.values[2:, 2:]).T
            # df_X = np.real(df_COMSOL[::2, :] * np.conjugate(df_COMSOL[::2, :]))
            # df_Y = np.real(df_COMSOL[1::2, :] * np.conjugate(df_COMSOL[1::2, :]))
            df_X = np.real(df_COMSOL[::2, :])
            df_Y = np.real(df_COMSOL[1::2, :])
            df_array_X.append(df_X)
            df_array_Y.append(df_Y)

        order = np.argsort(closest_Param)
        closest_Param = closest_Param[order]
        df_array_X = np.array(df_array_X)
        df_array_X = df_array_X[order]
        df_array_Y = np.array(df_array_Y)
        df_array_Y = df_array_Y[order]

        if len(closest_Param) != 1: # If there are 4 closest parameter -> interpolation to find f_mag_X and f_mag_Y
            interp_X = RegularGridInterpolator((closest_Param, frequency), df_array_X)
            new_points_X = (np.array([value]), frequency) # value = Parameter to __interpolate for = input
            f_mag_X = interp_X(new_points_X)

            interp_Y = RegularGridInterpolator((closest_Param, frequency), df_array_Y)
            new_points_Y = (np.array([value]), frequency)
            f_mag_Y = interp_Y(new_points_Y)
        else: # If there is only 1 closest parameter -> excel file with parameter = desired value, just take f_mag_X and f_mag_Y from that file
            f_mag_X = df_array_X[0, :, :]
            f_mag_Y = df_array_Y[0, :, :]

        f_mag = np.real(np.sqrt(df_COMSOL[::2, :] * np.conjugate(df_COMSOL[::2, :]) + df_COMSOL[1::2, :] * np.conjugate(df_COMSOL[1::2, :])))
        # f_mag_X = np.sqrt(f_mag_X)
        # f_mag_Y = np.sqrt(f_mag_Y)
        return f_mag, f_mag_X, f_mag_Y


    def __retrieve_field_contributions_Roxie(self) -> np.ndarray:
        '''
        Extracts the magnetic field data for each filament of the corresponding magnet fstarting from the Magnetic field
        taken from the LEDET class attributes

        :return f_mag: field in each filament for the magnet w/o effects
        :return f_mag_X: field along the X-axis in each filament for for the magnet w/o effects
        :return f_mag_Y: field along the Y-axis in each filament for the magnet w/o effects
        '''

        ### Calculate the field from Biot-Savart
        frequency = self.frequency
        self.Strands.x_strands = self.ledet_auxiliary.x_strands
        self.Strands.y_strands = self.ledet_auxiliary.y_strands

        # Calculate the magnetic field, generated by each group and store them
        self.Strands.f_mag_X_turns = np.zeros((self.General.num_HalfTurns, len(frequency), self.General.num_Strands), dtype=np.float32)
        self.Strands.f_mag_Y_turns = np.zeros((self.General.num_HalfTurns, len(frequency), self.General.num_Strands), dtype=np.float32)
        self.HalfTurns.x_turn_ends = np.zeros((2, self.General.num_HalfTurns))
        self.HalfTurns.y_turn_ends = np.zeros((2, self.General.num_HalfTurns))
        x_mid_apertures = []
        for k in range(self.General.apertures):
            x_mid_apertures.append(np.mean(self.Strands.x_strands[np.where(self.Strands.strands_to_apertures==k+1)[0]]))

        definedMagneticCoil = MagneticCoil()
        self.definedMagneticCoil = definedMagneticCoil
        for n in range(self.General.num_HalfTurns):
            Istrands = np.zeros(self.Strands.strands_current.shape)
            Istrands[np.where(self.Strands.strands_to_halfturn==n+1)[0]] = self.Strands.strands_current[np.where(self.Strands.strands_to_halfturn==n+1)[0]]
            definedMagneticCoil.setStrandPositions(self.Strands.x_strands, self.Strands.y_strands, Istrands)
            n_Bx_strands, n_By_strands, _ = definedMagneticCoil.calculateMagneticField(self.Strands.x_strands, self.Strands.y_strands)
            self.Strands.f_mag_X_turns[n, :, :] = np.repeat(n_Bx_strands[:, np.newaxis], len(frequency), axis=1).T
            self.Strands.f_mag_Y_turns[n, :, :] = np.repeat(n_By_strands[:, np.newaxis], len(frequency), axis=1).T

            ## Calculate the position of the 2 ends of each cable
            x_turn =  self.Strands.x_strands[np.where(self.Strands.strands_to_halfturn==n+1)[0]]
            y_turn = self.Strands.y_strands[np.where(self.Strands.strands_to_halfturn == n + 1)[0]]

            layer1_points_sorted = sorted(list(zip(x_turn[::2], y_turn[::2])), key=lambda point: point[0])
            layer2_points_sorted = sorted(list(zip(x_turn[1::2], y_turn[1::2])), key=lambda point: point[0])
            # Calculate in-between points (midpoints) between corresponding points in each layer
            in_between_points = [((x1 + x2) / 2, (y1 + y2) / 2) for (x1, y1), (x2, y2) in zip(layer1_points_sorted, layer2_points_sorted)]
            end_points = [in_between_points[0], in_between_points[-1]]
            end_points = sorted(end_points, key=lambda point: abs(point[0]-x_mid_apertures[self.HalfTurns.HalfTurns_to_apertures[n]-1]))
            # Select the end points of the in-between row
            self.HalfTurns.x_turn_ends[:,n] = np.array([end_points[0][0]+x_mid_apertures[self.HalfTurns.HalfTurns_to_apertures[n]-1], end_points[1][0]])
            self.HalfTurns.y_turn_ends[:, n] = np.array([end_points[0][1]+x_mid_apertures[self.HalfTurns.HalfTurns_to_apertures[n]-1], end_points[1][1]])

        ## Calculate the field in each aperture, assuming no Iron and no crosstalk between the apertures
        fMag_X = np.zeros((self.General.num_Strands,))
        fMag_Y = np.zeros((self.General.num_Strands,))
        for i in range(self.General.apertures):
            idx_ap_turns = np.where(self.HalfTurns.HalfTurns_to_apertures==i+1)[0]
            idx_ap_strands = np.where(self.Strands.strands_to_apertures == i + 1)[0]
            sum_X = np.sum(self.Strands.f_mag_X_turns[idx_ap_turns,0,:], axis=0)
            fMag_X[idx_ap_strands] = sum_X[idx_ap_strands]
            sum_Y = np.sum(self.Strands.f_mag_Y_turns[idx_ap_turns, 0, :], axis=0)
            fMag_Y[idx_ap_strands] = sum_Y[idx_ap_strands]
        f_mag = np.sqrt(fMag_X**2+fMag_Y**2)

        fMag_X = np.repeat(fMag_X[:, np.newaxis], len(frequency), axis=1).T
        fMag_Y = np.repeat(fMag_Y[:, np.newaxis], len(frequency), axis=1).T
        f_mag = np.repeat(f_mag[:, np.newaxis], len(frequency), axis=1).T

        return f_mag, fMag_X, fMag_Y


    ###################################################################################################################
    ############################################### LIBRARY GENERATION ###############################################
    def _generate_library(self, output_path: str, library_name: str, verbose: bool = False):
        '''
        This function generates a suitable lib file for the magnet simulation in XYCE.

        It follows this structure:

         - Calculation of the magnet inductance values using the 'calculate_Inductance_Turn' function.

         - Initialization of the magnet circuit through the '__generate_magnet_circuit_library' function.

         - Setting up the '.FUNC' parameter for each effect using the '__generate_function_library' function.

         - Defining the circuit parameters for each effect and each loop via the '__generate_loop_library' function.

         - Establishing the mutual coupling between each effect with the '__generate_coupling_library' function.

         - Computing the mutual coupling between the inductance of different loops through the 'calculate_MutualInductance_Turns' function.

         :param output_path: directory where the lib file must be saved
        '''
        start_lib = time.time()
        self._setAttribute(self.General, 'lib_path', output_path)
        # The lib file is build using a Dictionary of components
        Netlist = {}
        apertures = self.General.apertures
        groups = self.General.sections
        sections_to_aperture = self.General.sections_to_aperture
        # These nodes are the ones used in the circuit yaml file as magnet nodes
        if self.General.apertures == 2:
            Nodes = ['EE_AP1_IN', 'EE_AP_MID', 'EE_AP2_OUT', '1_GND']
        else:
            Nodes = ['EE_AP1_IN', 'EE_AP2_OUT', '1_GND']

        # Comments initialization
        Comm_newline = Component(type='comment', nodes=[], value=' ')  # Introduces an empty line in the file
        Netlist['Comment_newline_b_Magnet'] = Comm_newline

        Comm = Component(type='comment', nodes=[], value='* Each section has a C_GND and a V_tap, R_warm and L in series')
        Netlist['Comm_func3'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The suffix of each element have the format _{aperture}_{group}')
        Netlist['Comm_func4'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each capacitance is calculated as C_ground /(tot_num_apertures * tot_num_groups)')
        Netlist['Comm_func5'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each V_tap = 0 since it is just used to access the current in that group')
        Netlist['Comm_func6'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each R_warm is calculated as R_warm_tot / (tot_num_apertures * tot_num_groups)')
        Netlist['Comm_func7'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each L value is taken from the the Inductance Matrix in BuilderLEDET, according to the contribute of the turns associated to that group')
        Netlist['Comm_func8'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The coupling coefficients between different L are at the end of the lib file')
        Netlist['Comm_func9'] = Comm
        Netlist['Comm_func_nl'] = Comm_newline

        Comm_space = Component(type='comment', nodes=[], value='*'*150)  # Introduces a frae of stars in the file
        Netlist['Comment_Space_B_Magnet'] = Comm_space
        Comm = Component(type='comment', nodes=[], value='*'*50 + ' MAGNET ' + '*'*80)
        Netlist['Comment_Magnet'] = Comm
        Netlist['Comment_Space_AB_Magnet'] = Comm_space
        # Comments to explain the magnet circuit
        ################################## INITIALIZE MAGNET CIRCUIT ###################################################

        # Calculation of the magnet inductance values for each turn and aperture
        L_magnet = self._calculate_Inductance_Sections()
        Netlist = self.__generate_magnet_circuit_library(Netlist=Netlist, Nodes=Nodes)

        Netlist['Comment_newline_After_Magnet1'] = Comm_newline
        Netlist['Comment_newline_After_Magnet2'] = Comm_newline

        ################################## COUPLING effects ###################################################

        Netlist['Comment_Space_B_Magnet_2'] = Comm_space
        Comm = Component(type='comment', nodes=[], value='*' * 50 + ' COUPLING OF THE effects ' + '*' * 80)
        Netlist['Comment_eff'] = Comm
        Netlist['Comment_Space_eff'] = Comm_space

        Comm = Component(type='comment', nodes=[], value='* This magnet model is taking into account all the effects that can be seen below')
        Netlist['Comm_func1_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each effect, besides of Wedge and ColdBore, has a different equivalent circuit for each aperture and for each group in that aperture ')
        Netlist['Comm_func2_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The suffix of each element have the format _{aperture}_{group}')
        Netlist['Comm_func6_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each group has a L, R, V and R_gnd')
        Netlist['Comm_func7_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each effect has a number of M FUNC. equal to the number of groups')
        Netlist['Comm_func8_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* The values of M FUNC. can be changed thanks to the function change_coupling_parameter in BuilderTFM')
        Netlist['Comm_func9_eff'] = Comm
        Comm = Component(type='comment', nodes=[], value='* Each network model of a group is coupled to all the other network models of the others effects in that group ')
        Netlist['Comm_func12_eff'] = Comm
        Netlist['Comm_func_nl_eff'] = Comm_newline
        Netlist['Comm_func_space_eff'] = Comm_space

        effs = list(self.effects.keys()) # List of all the possible effects that might be included in the magnet
        effs_notCond = self.effs_notCond  # List of the effects that are not conductor losses (Wedge, CB)


        for eff_ind in range(len(effs)): # Looping through all the effects
            eff = effs[eff_ind]
            Comm = Component(type='comment', nodes=[], value='*'*50 + f' EFFECT {eff} ' + '*'*80)
            Netlist[f'Comment_{eff}'] = Comm
            Netlist[f'Comment_{eff}_space_Aft'] = Comm_space

            # Defining the L, M and R functions for each effect and each loop
            Netlist = self.__generate_function_library(Netlist=Netlist, eff=eff, eff_ind=eff_ind)

            for ap in range(1, apertures + 1): # Looping through the apertures
                Comm_Ap = Component(type='comment', nodes=[], value='*'*50 + f' APERTURE {ap} ' + '*'*80 )
                Netlist[f'Comment_{eff}_{ap}'] = Comm_Ap

                # Setting up the Loop library and the couplings with the magnets aperture
                if eff in effs_notCond:
                    Comm_Ap_d = Component(type='comment', nodes=[], value=f'* Coupled {eff} current loop ')
                    Netlist[f'Comment_{eff}_ap_{ap}'] = Comm_Ap_d
                    Netlist = self.__generate_loop_library(Netlist=Netlist, eff=eff, ap=ap, n=ap)
                else:
                    for n in range(1, groups + 1):  # Looping through all the groups in that aperture
                        if sections_to_aperture[n-1] != ap: continue

                        # Initialize the loop comment just if the number of groups != 1 and eff != Wedge and CB
                        Comm_group = Component(type='comment', nodes=[], value='*'*6 + f' LOOP {n} ' + '*'*6)
                        Netlist[f'Comment_{eff}_group_{n}_ap_{ap}_{n}'] = Comm_group
                        Comm_Ap_d = Component(type='comment', nodes=[], value=f'* Coupled {eff} current loop ')
                        Netlist[f'Comment_{eff}_ap_{ap}_{n}'] = Comm_Ap_d

                        Netlist = self.__generate_loop_library(Netlist=Netlist, eff=eff, ap=ap, n=n)

                Netlist[f'Comment_{eff}_{ap}_space_Coup'] = Comm_newline
                # Setting up the couplings with the other effects
                # for the couplings of the components - they couple to all other components and all other sections within this aperture
                for eff_coup_ind in range(eff_ind + 1, len(effs)):
                    eff_coup = effs[eff_coup_ind]
                    Netlist = self.__generate_coupling_library(Netlist=Netlist, eff=eff, eff_coup=eff_coup, ap=ap)

                Netlist[f'Comment_newline_{eff}_ap_{ap}'] = Comm_newline


            Netlist[f'Comment_newline_{eff}_ap_final'] = Comm_newline
            Netlist[f'Comment_final_space_{eff}'] = Comm_space

        # Computing the mutual coupling between the inductance of the magnet of different groups
        Netlist['comm_mutual'] = Component(type='comment', nodes=[], value='*Mutual coupling between Magnet Inductances')
        Netlist = self.__calculate_MutualInductance_Sections(Netlist=Netlist)

        Netlist['newline_final'] = Comm_newline
        Netlist['space_final'] = Comm_space

        # Initializing the parameters that must be printed on top of the lib file
        Params = {}
        Params['T_mag'] = self.temperature
        Params['l_m'] = self.General.magnet_length
        Params['C_ground'] = self.General.C_ground
        Params['L_mag'] = self.General.L_mag
        for key, item in L_magnet.items():
            Params[f'{key}_value'] = item
        for eff, value in self.effects.items(): # Flag names and values for each effect
            Params[f'flag_{eff}'] = int(value)
        if self.domain == 'transient':
            Params['f_characteristic'] = 0

        # circuit_name = self.General.magnet_name + '_TFM'  # Initializing the circuit name as the magnet name + TFM

        # Passing everything to XYCE to write the lib file from the dict of Components
        PX = ParserXYCE(verbose = verbose)
        PX.write_library(output_path=output_path, name=library_name, nodes=Nodes, params=Params, Netlist=Netlist, verbose= verbose)
        print(f'Writing the library took {np.round(time.time() - start_lib,4)} s')


    def _calculate_Inductance_Sections(self) -> dict:
        '''
        This function initialize the inductance values for each turn for the magnet circuit of the lib file used in XYCE

        :return L: a dictionary with the name and the value of L_mag for each section (a section i a group of turns)
        '''
        M_block = np.array(self.ledet_inputs['M_InductanceBlock_m'])
        fL_L = np.array(self.ledet_inputs['fL_L'])  # Current-dependent effect of the iron on the differential inductance of the magnet
        fL_I = np.array(self.ledet_inputs['fL_I'])  # Current corresponding to fL_L
        length_mag = self.General.magnet_length
        I_magnet = self.General.I_magnet
        turns_to_sections = self.Turns.turns_to_sections
        sections = max(turns_to_sections)
        self.General.inductance_to_sections = np.zeros((sections, sections))

        if np.all(M_block == 0):
            M_block_path = os.path.join(Path(self.General.local_library_path), f'{self.General.magnet_name}_MutualInductanceMatrix_TFM.csv')
            df = pd.read_csv(M_block_path, skiprows=1, header=None)
            M_block = df.values
        self._setAttribute(self.HalfTurns, 'M_block', M_block)

        fL = np.interp(I_magnet, fL_I, fL_L)  # Interpolation to calculate the fL_L for our current
        self.fL = fL
        L = {}

        L_sum = 0

        for section in range(1, sections + 1):
            idx = np.where(turns_to_sections == section)[0]  # Finds the indexes of the turns that belong to the current section
            M = M_block[np.ix_(idx, idx)]  # Taking the correct L block corresponding to this aperture
            L_sum_ap_section = np.sum(M) * length_mag * fL
            L_sum += L_sum_ap_section
            ap = int(np.unique(self.Turns.turns_to_apertures[idx])[0])
            L[f'L_{ap}_{section}'] = L_sum_ap_section
            self.General.inductance_to_sections[section-1,section-1] = L_sum_ap_section

        self._setAttribute(self.General, 'L_mag', np.sum(M_block)* length_mag * fL)

        return L


    # TO DO
    # def __insert_sectiontosection_capacitances(self, Netlist: dict, s_nodes: dict) -> dict:
    #
    #     'This function inserts the section to section capacitances in the network model, it t'
    #
    #     type = 'standard component'
    #     C_matrix_sections = self.HalfTurns.C_matrix_sections
    #     el_order_sections = self.General.el_order_sections
    #     Comm_input_C = Component(type='comment', nodes=[], value='*********** Section to section capacitances ***********')
    #     Netlist['Comment_C'] = Comm_input_C
    #     for s1 in el_order_sections:
    #         idx_s1 = s1 - 1
    #         for idx_s2 in range(idx_s1+1, len(el_order_sections)):
    #             s2 = el_order_sections[idx_s2]
    #             if C_matrix_sections[idx_s1, idx_s2] != 0:
    #                 Netlist[f'C_sec_{s1}_{s2}'] = Component(type=type, nodes=[s_nodes[s1][0], s_nodes[s2][0]], value=f'{C_matrix_sections[idx_s1, idx_s2]}'
    #     return Netlist



    def __generate_magnet_circuit_library(self, Netlist: dict, Nodes: list) -> dict:
        '''
        This function initialize the magnet circuit for the circuit lib file used in XYCE

        :param Netlist: a dictionary of Components where the new components must be added.
        :param Nodes: a list of 4 nodes corresponding to the ones of the magnet initialization in the circuit yaml file.

        :return Netlist: it returns the updated Netlist with the magnet circuit components

        Nodes: Nodes[0] = Inout, Nodes[1] = mid, Nodes[2] = end, Nodes[3] = GND

        This function assigns the inductance values as parameters, which are sourced from `self.General.inductance_to_sections`.
        These values are set by the `__calculate_Inductance_Sections(self)` function and are written into the netlist by
        the __generate_library` function.

        The code allows for inserting capacitances to ground using either an approximate or an accurate model.
        - **Approximate Model** (`flag_LumpedC = True`):
T           The capacitances are placed at the beginning, middle, or end of the circuit with values of CGND/4,
            CGND/2, and CGND/4, respectively.

        - **Accurate Model** (`flag_LumpedC = True`)::
            Each inductance has a corresponding capacitance to ground. The value of this capacitance can be taken from
            Comsol or calculated in TFM (depending on the value of `flag_Comsol`). Additionally, there is a capacitance
            at the end of the circuit equal to the first capacitance in the network.
            In the accurate model, the function first calculates the capacitances to ground for each section using the
            `_calculate_CapacitanceToGround_sections` function. These capacitances are written as frequency-dependent
            tables at the start of the library file. Then, the function creates the components for the capacitances.

        '''

        apertures = self.General.apertures
        sections = max(self.Turns.turns_to_sections)
        frequency = self.frequency
        sections_to_aperture = self.General.sections_to_aperture
        el_order_to_apertures = self.General.el_order_to_apertures
        el_order_sections = self.General.el_order_sections
        # C_g = self.General.capacitance_to_sections if self.General.capacitance_to_sections is not None else np.repeat(self.General.C_ground/2, self.General.sections)
        C_g = self.General.C_ground / 4 #(2*self.General.sections)
        R_w = self.General.R_warm /(sections* apertures)
        type = 'standard component'
        Comm_newline = Component(type='comment', nodes=[], value=' ')
        Comm_space = Component(type='comment', nodes=[], value='*'*150)
        section_nodes = {}
        GND_node = Nodes[3] if self.General.apertures == 2 else Nodes[2]
        OUT_node = Nodes[2] if self.General.apertures == 2 else Nodes[1]
        num_Turns = self.General.num_HalfTurns // 2
        C_gnd_tot = self.General.C_ground
        flag_LumpedC = self.General.flag_LumpedC

        count_nodes = 0 # Starting the node counting

        # If `flag_LumpedC` is not set, calculate the corresponding capacitance values in TFM or extract them
        # from the Comsol files an then extract the section capacitance values from `self.General.C_ground_el_order_sections`
        # and insert them into the netlist as frequency-dependent values.
        if not flag_LumpedC:
            self.__setCapacitances()
            f_list = self.frequency_list_capacitance
            C_ground_el_order_sections = self.General.C_ground_el_order_sections
            Comm_input_cap = Component(type='comment', nodes=[], value='* Equivalent capacitances value')
            Netlist['Comm_input_cap'] = Comm_input_cap
            for i in range(len(el_order_sections)+1):
                if i == len(el_order_sections): # If it's the last capacitance, then take the value of the first one
                    C_ground_value = C_ground_el_order_sections[0]
                else:
                    C_ground_value = C_ground_el_order_sections[i]
                value = ''
                for f in range(len(f_list)):
                    if not isinstance(C_ground_value, float):
                        value += f'({f_list[f]},{C_ground_value[f]}) '
                    else:
                        if f != 0 and f != len(f_list)-1: continue
                        value += f'({f_list[f]},{C_ground_value}) '
                C_ground_el = Component(type='function', nodes=['FREQ', ], value=value)
                if i != len(el_order_sections):
                    sec = el_order_sections[i]
                    ap = sections_to_aperture[sec - 1]
                    Netlist[f'C_GND_value_{ap}_{sec}'] = C_ground_el
                else:
                    Netlist[f'C_GND_value_last'] = C_ground_el
            Netlist['Comment_newline_Cap'] = Component(type='comment', nodes=[], value=' ')


        # Initialize comments for V_ap
        Comm_input_V_ap1 = Component(type='comment', nodes=[], value='* Fake voltage source to easily access the input current')
        Netlist['Comm_input_tap'] = Comm_input_V_ap1

        # Initialize V_ap1 to easily access the input current
        V_ap1 = Component(type=type, nodes=[Nodes[0], f'EE{count_nodes:03d}'], value='0')
        Netlist['V_ap_1'] = V_ap1
        Netlist['Comm_nl_after_input_1'] = Comm_newline

        # If 'flag_LumpedC' not set, insret the first caapcitance to ground of the approximate model
        if flag_LumpedC:
            Netlist[f'C_GND_in'] = Component(type=type, nodes=[f'EE{count_nodes:03d}', GND_node], value=f'{C_gnd_tot / (2 * apertures)}')

        for ap in range(1, apertures + 1): # Looping through the apertures
            # To add the comment 'APERTURE n'
            Comm_Ap = Component(type='comment', nodes=[], value='*'*50 + f' APERTURE {ap} ' + '*'*80)
            Netlist[f'Comment_Magnet_Ap{ap}'] = Comm_Ap
            last_index = len(el_order_to_apertures) - np.flip(el_order_to_apertures).tolist().index(ap) -1
            section_count = 0

            for n in el_order_sections: # Looping for the number of sections, along their el. order
                s_nodes = []
                if sections_to_aperture[n-1] != ap: continue
                if sections != 1: # Adding Turn comment only if number of turns != 1
                    Comm_turning = Component(type='comment', nodes=[], value=f'****** Group {n} ******')
                    Netlist[f'Comment_turning_{ap}_{n}'] = Comm_turning

                # Add C_GND, R_warm, L and V_tap for each subcircuit, considering that
                if ap == 2 and section_count == 0:  # If we are are between one Aperture and the other
                    # the closest V_tap (first of the second Ap) must be attached to the central node
                    V_tap = Component(type=type, nodes=[Nodes[1], f'EE{count_nodes:03d}'], value='0')
                    # s_nodes.append(Nodes[1])
                else:
                    # Normal situation
                    V_tap = Component(type=type, nodes=[f'EE{count_nodes:03d}', f'EE{count_nodes + 1:03d}'], value='0')
                    # s_nodes.append(f'EE{count_nodes:03d}')
                    count_nodes += 1  # Update node counting
                Netlist[f'V_tap_{ap}_{n}'] = V_tap

                if not self.Options.flag_SC:
                    R_warm = Component(type=type, nodes=[f'EE{count_nodes:03d}', f'EE{count_nodes + 1:03d}'], value=f'{R_w}')
                    count_nodes += 1 # Update node counting
                    Netlist[f'R_warm_{ap}_{n}'] = R_warm


                L_mag = f'L_{ap}_{n}_value'# Take the correct value of L_mag from the input dict

                if ap == 1 and n == el_order_sections[last_index]:  # If we are are between one Aperture and the other
                    # 3) the closest L (last of the first Ap) must be attached to the central node
                    L = Component(type=type, nodes=[f'EE{count_nodes:03d}', Nodes[1]], value=f'{L_mag}')
                    s_nodes.append(f'EE{count_nodes:03d}')
                    s_nodes.append(Nodes[1])
                else:
                    L = Component(type=type, nodes=[f'EE{count_nodes:03d}', f'EE{count_nodes + 1:03d}'],
                                  value=f'{L_mag}')
                    s_nodes.append(f'EE{count_nodes:03d}')
                    s_nodes.append(f'EE{count_nodes + 1:03d}')


                Netlist[f'L_{ap}_{n}'] = L
                # If 'flag_LumpedC' is set, insert the Cpacitance to ground corresponding to the inductance
                if not flag_LumpedC:
                    Netlist[f'C_GND_{ap}_{n}'] = Component(type=type, nodes=[f'EE{count_nodes:03d}', GND_node],
                                              value=f'C_GND_value_{ap}_{n}(FREQ)')
                elif(ap == 1 and n == el_order_sections[last_index] and apertures == 2):
                    # If not 'flag_LumpedC' and we are in the middle of the apertures, insert the capacitance to ground
                    # in the middle of the network
                    Netlist[f'C_GND_mid'] = Component(type=type, nodes=[Nodes[1], GND_node],
                                                           value=f'{C_gnd_tot/apertures}')

                count_nodes += 1  # Update node counting

                Netlist[f'Comment_newline_Magnet_{ap}_{n}'] = Comm_newline
                section_nodes[n] = s_nodes
                section_count = section_count + 1


                self.print_nodes.append(f'I({self.magnet_circuit_name}:L_{ap}_{n})'.upper())
                self.print_nodes.append(f'V({self.magnet_circuit_name}:EE{count_nodes:03d})'.upper())



        # Initialize comments for the last Capacitance and V_ap2
        Netlist[f'Comment_space_Magnet_out'] = Comm_space
        # Inserting the last capacitance
        if not flag_LumpedC:
            Last_cap_ground = Component(type=type, nodes=[f'EE{count_nodes:03d}', GND_node],
                                        value='C_GND_value_last(FREQ)')
        else:
            Last_cap_ground = Component(type=type, nodes=[f'EE{count_nodes:03d}', GND_node],
                                        value=f'{C_gnd_tot / (2 * apertures)}')
        Netlist['C_GND_last'] = Last_cap_ground

        Comm_out_V_ap2 = Component(type='comment', nodes=[],
                                   value='* Fake voltage source to easily access the output current')
        Netlist['Comm_output_tap'] = Comm_out_V_ap2
        # Adding last V_ap2 to complete the circuit
        V_ap2 = Component(type=type, nodes=[f'EE{count_nodes:03d}', OUT_node], value='0')
        Netlist['V_ap_2'] = V_ap2

        # Insert the turn to turn capacitances and the layer to layer capacitances
        Netlist[f'Comment_newline_C'] = Comm_newline
        Netlist[f'Comment_space_C'] = Comm_space


        ## Introduce the short-circuits across some inductors
        if self.Shorts.sections_to_short:
            if not isinstance(self.Shorts.sections_to_short, list):
                self.Shorts.sections_to_short = [self.Shorts.sections_to_short]
            if not isinstance(self.Shorts.short_resistances, list):
                self.Shorts.short_resistances = [self.Shorts.short_resistances]
            s_count = 0
            for section in self.Shorts.sections_to_short:
                sections_split = section.split('-')
                indices = [np.where(self.General.el_order_sections == element)[0][0] for element in np.array(sections_split).astype(int)]
                sections_split = [element for _, element in sorted(zip(indices, sections_split))]
                if len(sections_split)>1:
                    nodes_short = [section_nodes[int(sections_split[0])][0],section_nodes[int(sections_split[-1])][-1]]
                else:
                    nodes_short = section_nodes[int(section)]
                R_short = self.Shorts.short_resistances[s_count]

                V_nodes = [nodes_short[0], nodes_short[0]+'_V']
                nodes_short[0] = nodes_short[0]+'_V'
                V_com = Component(type=type, nodes=V_nodes, value=f'{0}')
                Netlist[f'V_short_Section_{section}'] = V_com

                R_com = Component(type=type, nodes=nodes_short, value=f'{R_short}')
                Netlist[f'R_short_Section_{section}'] = R_com
                
                self.print_nodes.append(f'V({self.magnet_circuit_name}:{nodes_short[0]})'.upper())
                self.print_nodes.append(f'V({self.magnet_circuit_name}:{nodes_short[1]})'.upper())
                self.print_nodes.append(f'I({self.magnet_circuit_name}:V_short_Section_{section})'.upper())
                s_count += 1

        return Netlist


    def __generate_function_library(self, Netlist: dict, eff: str, eff_ind: int) -> dict:
        '''
        This function initialize the function parameter .FUNC for a given effect in the lib file used in XYCE

        :param Netlist: a dictionary of Components where the new components must be added.
        :param eff: name of the effect for which we need the .FUNC parameters
        :param eff_ind: index of this effect fin the effs list

        :return Netlist: it regroups the updated Netlist with the magnet circuit components
        '''

        effs_notCond = self.effs_notCond # effects which are not the conductor losses
        effs_noDir = self.effs_noDir
        effs = list(self.effects.keys())  # All effects
        groups = self.General.sections
        apertures = self.General.apertures
        sections_to_aperture = self.General.sections_to_aperture

        type_func = 'function'
        default_1 = Component(type=type_func, nodes=['1', ], value='(1.0,1.0) (100000.0,1.0)') # Default function for L, R (default value = 1)
        default_0 = Component(type=type_func, nodes=['1', ], value='(1.0,0.0) (100000.0,0.0)') # Default function for M (default value = 0)
        Comm_newline = Component(type='comment', nodes=[], value=' ')

        # Create the functions for the loops themselves
        for ap in range(1,apertures+1):
            # These are the components that are assumed to be symmetric. Hence, we only need one function for both apertures
            if eff in effs_notCond and eff != 'BS':
                Netlist[f'{eff}_L_1'] = default_1
                Netlist[f'{eff}_R_1'] = default_1
            #  These are the components that are NOT symmetric. Hence we need one function for each aperture
            elif eff == 'BS':
                Netlist[f'{eff}_L_{ap}'] = default_1
                Netlist[f'{eff}_R_{ap}'] = default_1
            else:
                # These are the conductor effects, that need to be created for each section
                for n in range(1,groups+1):
                    # Check if the section also has to be connected to the aperture
                    if sections_to_aperture[n-1] == ap:
                        Netlist[f'{eff}_L_{n}'] = default_1
                        if eff != 'PC': Netlist[f'{eff}_R_{n}'] = default_1
                        Netlist[f'Comment_newline_func_{eff}_{n}'] = Comm_newline
                    else:
                        continue
            if eff in effs_notCond:
                for n in range(1, groups + 1):
                    Netlist[f'{eff}_M_{n}'] = default_0
            elif eff in effs_noDir:
                for n in range(1, groups + 1):
                    for i in range(1, groups + 1):
                        # if sections_to_aperture[n - 1] == sections_to_aperture[i - 1]:
                        Netlist[f'{eff}_M_{n}_{i}'] = default_0
                        Netlist[f'{eff}_M_{n}_{i}'] = default_0
            else:
                for n in range(1, groups + 1):
                    for i in range(1, groups + 1):
                        # if sections_to_aperture[n - 1] == sections_to_aperture[i - 1]:
                        Netlist[f'{eff}_M_{n}_{i}_x'] = default_0
                        Netlist[f'{eff}_M_{n}_{i}_y'] = default_0

            Netlist[f'Comment_newline_func_{eff}_{ap}_{n}_Coupling'] = Comm_newline


        # Create the mutual couplings with all the other effect
        for eff_coup_ind in range(eff_ind + 1, len(effs)): # looping through any effect subsequent to the one given
            eff_coup = effs[eff_coup_ind]
            # These are the components that are assumed to be symmetric. Hence, we only need one function for coupling the component to section n
            if eff in effs_notCond and eff != 'BS':
                if eff_coup =='PC': continue
                for n in range(1, groups + 1):  # looping through the groups
                    if (eff_coup in effs_notCond):
                        Netlist[f'M_{eff_coup}_{eff}'] = default_0
                    elif (eff_coup in effs_noDir): # For all the others we need one M function per loop
                        Netlist[f'M_{eff_coup}_{eff}_{n}'] = default_0
                    else:
                        Netlist[f'M_{eff_coup}_{eff}_{n}_x'] = default_0
                        Netlist[f'M_{eff_coup}_{eff}_{n}_y'] = default_0
            #  These are the components that are NOT symmetric. Hence we need one function for each aperture
            elif eff == 'BS':
                if eff_coup == 'PC': continue
                # The coupling of BS with the other components is assumed to be the same
                if eff_coup in effs_notCond:
                    Netlist[f'M_{eff_coup}_{eff}'] = default_0
                elif eff_coup in effs_noDir:
                    for n in range(1, groups + 1):  # looping through the groups
                        Netlist[f'M_{eff_coup}_{eff}_{n}'] = default_0
                else:
                    for n in range(1, groups + 1):  # looping through the groups
                        Netlist[f'M_{eff_coup}_{eff}_{n}_x'] = default_0
                        Netlist[f'M_{eff_coup}_{eff}_{n}_y'] = default_0
            # These are the conductor effects, that need to be coupled with each other within their section
            else:
                for n in range(1, groups + 1):  # looping through the groups
                    Netlist[f'M_{eff_coup}_{eff}_{n}_x'] = default_0
                    Netlist[f'M_{eff_coup}_{eff}_{n}_y'] = default_0
            Netlist[f'Comment_{eff_coup}_{eff}'] = Comm_newline

        return Netlist


    def __generate_loop_library(self, Netlist: dict, eff: str, ap: int, n: int) -> dict:
        '''
        This function initialize the circuit parameter for a given effect in a given aperture and for a given loop of the lib file

        :param Netlist: a dictionary of Components where the new components must be added.
        :param eff: name of the effect for which we need the circuit parameters
        :param ap: index of the aperture
        :param n: index of the groups

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''
        effs = self.effects.items()
        type = 'standard component'
        Comm_newline = Component(type='comment', nodes=[], value=' ')
        effs_notCond = self.effs_notCond
        effs_noDir = self.effs_noDir
        groups = self.General.sections
        sections_to_aperture = self.General.sections_to_aperture

        for dir in ['x', 'y']:
            Comm_Dir = Component(type='comment', nodes=[], value=f'* Direction {dir}')
            # If eff == CB or eff == Wedge no need to have multiples circuit component names
            if eff in effs_notCond:
                suff = f'{ap}'
            elif eff in effs_noDir:
                suff = f'{n}'
            else:
                suff = f'{n}_{dir}'
                Netlist[f'Comment_{eff}_{n}_{dir}'] = Comm_Dir
            if eff == 'BS':
                suff_L = f'{ap}'
            elif eff in effs_notCond:
                suff_L = f'{1}'
            else:
                suff_L = f'{n}'

            if eff != 'PC':  # Assigning L, R, V if eff != 'PC'
                L = Component(type=type, nodes=[f'{eff}_{suff}a', f'{eff}_{suff}b'], value=f'{eff}_L_{suff_L}(1)')
                Netlist[f'L_{eff}_{suff}'] = L
                R = Component(type=type, nodes=[f'{eff}_{suff}b', f'{eff}_{suff}c'], value=f'{eff}_R_{suff_L}(1)')
                Netlist[f'R_{eff}_{suff}'] = R
                V = Component(type=type, nodes=[f'{eff}_{suff}c', f'{eff}_{suff}a'], value='0')
                Netlist[f'V_{eff}_{suff}'] = V
                self.print_nodes.append(f'V({self.magnet_circuit_name}:{eff}_{suff}c)'.upper())
            else:  # If eff == 'PC' add parameter to L and assigns B instead of L
                param = {}
                param['IC'] = f'{eff}_{n}'
                L = Component(type=type, nodes=[f'{eff}_{suff}a', f'{eff}_{suff}b'], value=f'{eff}_L_{suff_L}(1)', parameters=param)
                Netlist[f'L_{eff}_{suff}'] = L
                I = '('
                for i in range(1,self.General.sections+1):
                    if self.General.sections_to_aperture[i-1] == self.General.sections_to_aperture[n-1]:
                        I = I + f'PC_M_{n}_{i}_{dir}(1)*I(V_tap_{ap}_{i})+'
                I = I[:-1] # Remove the last '+'
                for eff_c, value in effs:
                    if eff == eff_c or not value or eff_c in effs_notCond: continue
                    if eff_c in effs_noDir:
                        I = I + f'-M_PC_{eff_c}_{suff}(1)*flag_{eff_c}*I(V_{eff_c}_{n})'
                    else:
                        I = I + f'-M_PC_{eff_c}_{suff}(1)*flag_{eff_c}*I(V_{eff_c}_{suff})'
                I = I + ')'
                B = Component(type='behavioral-current component', nodes=[f'{eff}_{suff}a', f'{eff}_{suff}b'], value=I + f'/({eff}_L_{n}(1)+1e-9)')
                Netlist[f'B_{eff}_{ap}_{suff}'] = B
                self.print_nodes.append(f'V({self.magnet_circuit_name}:{eff}_{suff}a)'.upper())
            self.print_nodes.append(f'I({self.magnet_circuit_name}:L_{eff}_{suff})'.upper())
            self.print_nodes.append(f'V({self.magnet_circuit_name}:{eff}_{suff}b)'.upper())

            # Assigning R_gnd for each effect
            R_gnd = Component(type=type, nodes=[f'{eff}_{suff}a', '0'], value='10G')
            Netlist[f'R_gnd_{eff}_{suff}'] = R_gnd
            C_gnd_eff = Component(type=type, nodes=[f'{eff}_{suff}a', '0'], value='1e-9')
            Netlist[f'C_gnd_{eff}_{suff}'] = C_gnd_eff

            Netlist[f'Comment_newline_K_{eff}_{suff}'] = Comm_newline
            Comm_Ap_K = Component(type='comment', nodes=[], value=f'* Coupling groups and magnet')
            Netlist[f'Comment_{eff}_{suff}_K'] = Comm_Ap_K

            # Assigning the coupling coefficient between the eff and the inductances of the magnet
            if eff in effs_notCond:
                for i in range(1, groups + 1):
                    if sections_to_aperture[i - 1] != ap: continue
                    K_value = f'flag_{eff}*{eff}_M_{i}(1)/sqrt(L_{ap}_{i}_value*{eff}_L_{suff_L}(1))'
                    K = Component(type=type, nodes=[f'L_{eff}_{ap}', f'L_{ap}_{i}'], value=K_value)
                    Netlist[f'K_{eff}_{ap}_{i}'] = K
            else:
                for j in range(1, self.General.apertures+1):
                    for i in range(1, groups + 1):
                        if sections_to_aperture[i - 1] != j : continue
                        if eff == 'PC' or eff == 'IFCC':  # Assigning K_value depending on superconductive or not (PC and IFCC only exclusively superconductive effects)
                            K_value = f'flag_{eff}*{eff}_M_{i}_{suff}(1)/sqrt(L_{j}_{i}_value*{eff}_L_{n}(1))*{int(self.Options.flag_SC)}'
                        else:
                            K_value = f'flag_{eff}*{eff}_M_{i}_{suff}(1)/sqrt(L_{j}_{i}_value*{eff}_L_{n}(1))'
                        K = Component(type=type, nodes=[f'L_{eff}_{suff}', f'L_{j}_{i}'], value=K_value)
                        Netlist[f'K_{eff}_{ap}_{i}_{suff}'] = K
                Netlist[f'Comment_{n}_{eff}_{dir}_NewN'] = Comm_newline
        return Netlist


    def __generate_coupling_library(self, Netlist: dict, eff: str, eff_coup: str, ap: int) -> dict:
        '''
        This function initialize the mutual coupling coefficients between one eff and another for a given aperture and a given loop

        :param Netlist: a dictionary of Components where the new components must be added.
        :param eff: name of the first effect
        :param eff_coup: name of the coupled effect
        :param ap: index of the aperture
        :param n: index of the loop

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''

        effs = list(self.effects.keys()) # All effects
        effs_notCond = self.effs_notCond # effects not conductor losses
        type = 'standard component'
        groups = self.General.sections
        sections_to_aperture = self.General.sections_to_aperture

        # First, let's do the couplings for all component effects
        if eff in effs_notCond:
            # If eff in effs_notCond, but eff_coup in effs_Cond, we have to couple the component to all sections of this aperture
            if eff_coup not in effs_notCond:
                if eff_coup == 'PC':
                    return Netlist
                    # K_coup_value = '0'
                    # for dir in ['x', 'y']:
                    #     for i in range(1, groups + 1):
                    #         K_coup = Component(type=type, nodes=[f'L_{eff}_{ap}', f'L_{eff_coup}_{i}_{dir}'], value=K_coup_value)
                    #         Netlist[f'K_{eff_coup}_{eff}_{i}_{dir}'] = K_coup
                else:
                    for i in range(1,groups+1):
                        if sections_to_aperture[i-1] != ap: continue
                        if eff == 'BS': suff = ap
                        else: suff = 1
                        if eff_coup in self.effs_noDir:
                            K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}_{i}(1)/sqrt({eff_coup}_L_{i}(1)*{eff}_L_{suff}(1))'
                            K_coup = Component(type=type, nodes=[f'L_{eff}_{ap}', f'L_{eff_coup}_{i}'], value=K_coup_value)
                            Netlist[f'K_{eff_coup}_{eff}_{i}'] = K_coup
                        else:
                            for dir in ['x', 'y']:
                                K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}_{i}_{dir}(1)/sqrt({eff_coup}_L_{i}(1)*{eff}_L_{suff}(1))'
                                K_coup = Component(type=type, nodes=[f'L_{eff}_{ap}', f'L_{eff_coup}_{i}_{dir}'], value=K_coup_value)
                                Netlist[f'K_{eff_coup}_{eff}_{i}_{dir}'] = K_coup
            # If the other effect is also a component, we only have to couple the two aperture-wise loops together
            else:
                suff_eff = ap if eff == 'BS' else '1'
                suff_eff_c = ap if eff_coup == 'BS' else '1'

                K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}(1)/sqrt({eff_coup}_L_{suff_eff_c}(1)*{eff}_L_{suff_eff}(1))'
                K_coup = Component(type=type, nodes=[f'L_{eff}_{ap}', f'L_{eff_coup}_{ap}'], value=K_coup_value)
                Netlist[f'K_{eff_coup}_{eff}_{ap}'] = K_coup
        # Now the couplings between the non-conductor effects -> Only coupled to their own section!
        else:
            for dir in ['x', 'y']:
                for i in range(1, groups + 1):
                    if sections_to_aperture[i - 1] != ap: continue
                    K_coup_value = f'flag_{eff}*flag_{eff_coup}*M_{eff_coup}_{eff}_{i}_{dir}(1)/sqrt({eff_coup}_L_{i}(1)*{eff}_L_{i}(1))'
                    if eff in self.effs_noDir:
                        K_coup = Component(type=type, nodes=[f'L_{eff}_{i}', f'L_{eff_coup}_{i}_{dir}'], value=K_coup_value)
                    elif eff_coup in self.effs_noDir:
                        K_coup = Component(type=type, nodes=[f'L_{eff}_{i}_{dir}', f'L_{eff_coup}_{i}'], value=K_coup_value)
                    else:
                        K_coup = Component(type=type, nodes=[f'L_{eff}_{i}_{dir}', f'L_{eff_coup}_{i}_{dir}'], value=K_coup_value)
                    Netlist[f'K_{eff_coup}_{eff}_{i}_{dir}'] = K_coup

        return Netlist


    def __calculate_MutualInductance_Sections(self, Netlist: dict) -> dict:
        '''
        This function initialize the Mutual inductance Coupling coefficient values between each turn for the magnet circuit of the lib file used in XYCE

        :param Netlist: a dictionary of Components where the new components must be added

        :return Netlist: it returns the updated Netlist with the magnet circuit components
        '''
        M_block = np.array(self.ledet_inputs['M_InductanceBlock_m'])
        fL_I = np.array(self.ledet_inputs['fL_I'])
        fL_L = np.array(self.ledet_inputs['fL_L'])
        length_mag = self.General.magnet_length
        I_magnet = self.General.I_magnet
        apertures = self.General.apertures
        type = 'standard component'
        n_Turns = self.General.num_HalfTurns // 2
        turns_to_sections = self.Turns.turns_to_sections
        turns_to_apertures = self.Turns.turns_to_apertures
        sections_to_aperture = self.General.sections_to_aperture
        sections = np.max(turns_to_sections)

        if M_block.all() == 0:
            M_block_path = os.path.join(Path(self.General.local_library_path),f'{self.General.magnet_name}_MutualInductanceMatrix_TFM.csv')
            df = pd.read_csv(M_block_path, skiprows=1, header=None)
            M_block = df.values

        fL = np.interp(I_magnet, fL_I, fL_L)

        if apertures != 1 or sections != 1: # Check if either there is more than 1 Ap or more than 1 group, otherwise no coupling
            # Loop to calculate the M for the coupling of different sections in the same aperture
            for ap in range(1, apertures+1):
                # Coupling between different sections of the same aperture
                for group1 in range(1, sections+1):
                    if sections_to_aperture[group1-1] != ap: continue
                    indices1 = np.where(turns_to_sections == group1)[0] # Taking the indices corresponding to group1
                    for group2 in range(group1 + 1, sections + 1):
                        if sections_to_aperture[group2 - 1] != ap: continue
                        indices2 = np.where(turns_to_sections == group2)[0]  # Taking the indices corresponding to group2

                        M_coup = M_block[np.ix_(indices1, indices2)] # Taking the M block corresponding to orix_idx = indices1, vert_idx = indices2
                        K_coup_value = f'{np.sum(M_coup) * (length_mag*fL)}/sqrt(L_{ap}_{group1}_value*L_{ap}_{group2}_value)'
                        K_mag = Component(type=type, nodes=[f'L_{ap}_{group1}', f'L_{ap}_{group2}'], value=K_coup_value)
                        Netlist[f'K_mag_{group1}_{group2}'] = K_mag
                        self.General.inductance_to_sections[group1-1, group2-1] = np.sum(M_coup) * (length_mag * fL)
                        self.General.inductance_to_sections[group2-1, group1-1] = np.sum(M_coup) * (length_mag * fL)

        # # Coupling between sections of different apertures
        if apertures == 2: # Only if apertures == 2
            ap = 1
            for group1 in range(1, sections + 1): # All the sections of the 1st ap
                if sections_to_aperture[group1 - 1] != ap: continue
                indices1 = np.where(turns_to_sections == group1)[0] # Taking index of turns that belong to group 1
                for group2 in range(1, sections + 1): # All the sections of the 2nd Ap
                    if sections_to_aperture[group2 - 1] == ap: continue
                    indices2 = np.where(turns_to_sections == group2)[0]  # Taking index of turns that belong to group 2

                    M = M_block[np.ix_(indices1, indices2)]
                    K_coup_value = f'{np.sum(M) * (length_mag * fL)}/sqrt(L_1_{group1}_value*L_2_{group2}_value)'
                    K_mag = Component(type=type, nodes=[f'L_1_{group1}', f'L_2_{group2}'], value=K_coup_value)
                    Netlist[f'K_mag_{group1}_{group2}'] = K_mag
                    self.General.inductance_to_sections[group1 - 1, group2 - 1] = np.sum(M) * (length_mag * fL)
                    self.General.inductance_to_sections[group2 - 1, group1 - 1] = np.sum(M) * (length_mag * fL)

        return Netlist


    ####################################################################################################################
    ############################################### effects FUNCTIONS ###############################################
    def calculate_PC(self, T: float, fMag_X: np.ndarray,  fMag_Y: np.ndarray, flag_coupling:bool = True, flag_save:bool=False) -> np.ndarray:
        '''
        Function that calculates the equivalent circuit parameter for the persistent currents and save them to the
        PC dataclass

        :param frequency: Frequency vector
        :param T: temperature vector, to be used in the interaction with Eddy-currents
        :param fMag: field-factor for each strand
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the PC dataclass

        :return M_temp_x: mutual coupling along x
        :return M_temp_y: mutual coupling along y
        '''

        # Constants - Pre-compute frequently used constants
        pi_div4 = np.pi / 4
        mu0_pi_div8 = self.mu0 * np.pi / 8

        # Unpack values
        frequency = self.frequency
        l_magnet = self.General.magnet_length
        ds_filamentary = self.Strands.d_filamentary
        dws = self.Strands.diameter
        RRR = self.Strands.RRR
        n_strands = np.sum(self.HalfTurns.n_strands)
        strands_to_conductor = self.Strands.strands_to_conductor
        n_freq = len(frequency)

        # Pre-compute variables that are reused
        w = 2 * np.pi * frequency[:, np.newaxis]  # Vectorized frequency reshaping
        B = self.General.I_magnet * np.sqrt(fMag_X**2+fMag_Y**2)
        rho_el_0 = self.__rhoCu_nist(T=T, RRR=RRR, B=B[0, :])
        tb_strand = dws - ds_filamentary

        # Time constant and attenuation factor
        tau_ed = (self.mu0 / 2) * (dws / 2 * tb_strand / 2) / rho_el_0
        alpha2 = 1 / np.sqrt(1 + (w * tau_ed) ** 2) if flag_coupling else np.ones_like(w)

        # Mutual inductance (M_temp), inductance (Lm), M_IFCC_PC calculations
        M_temp_x = pi_div4 * l_magnet * ds_filamentary * fMag_X * alpha2
        M_temp_y = pi_div4 * l_magnet * ds_filamentary * fMag_Y * alpha2
        Lm = np.full(n_freq, self.mu0 * pi_div4 * l_magnet)
        M_if_Pc = mu0_pi_div8 * l_magnet  # Constant

        # Reshape and repeat arrays using broadcasting
        L_pc = Lm[:, np.newaxis].repeat(n_strands, axis=1)
        I_Pc = np.zeros((n_freq, n_strands))

        if flag_save:
            L_group, R_group = self.__group_components_LR(frequency=frequency, L=L_pc, R=None, sort_on='strands')
            self._setAttribute(self.PC, 'L', L_group)
            self._setAttribute(self.PC, 'M_PC_IFCC', M_if_Pc)

        return M_temp_x, M_temp_y


    def calculate_IFCC(self, T: float, fMag_X: np.ndarray, fMag_Y: np.ndarray, flag_coupling: bool = True, flag_save: bool = False) -> np.ndarray:
        """
        Calculates the equivalent IFCL coupling loops for a given temperature and field.

        :param T: temperature vector
        :param fMag_X: field-factor along X axis for each strand
        :param fMag_Y: field-factor along Y axis for each strand
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the IFCC dataclass

        :return M_if_x: mutual coupling along x
        :return M_if_y: mutual coupling along y
        """
        # Constants and Pre-computed Parameters
        frequency = self.frequency
        w = 2 * np.pi * frequency[:, None]  # Reshape only once
        f_ro_eff, l_mag = self.Strands.f_rho_effective, self.General.magnet_length
        dws, ds_filamentary = self.Strands.diameter, self.Strands.d_filamentary
        RRR, Lp_f = self.Strands.RRR, self.Strands.fil_twist_pitch
        mu0_eff = self.mu0
        B = self.General.I_magnet * np.sqrt(fMag_X[0, :] ** 2 + fMag_Y[0, :] ** 2)

        # Resistivity
        rho_el_0 = self.__rhoCu_nist(T=T, RRR=RRR * f_ro_eff, B=B) + 1e-12
        rho_el_Outer = self.__rhoCu_nist(T=T, RRR=RRR, B=B) + 1e-12

        # Calculating parameters
        beta_if_base = (Lp_f / (2 * np.pi)) ** 2 / rho_el_0
        tau_if = mu0_eff / 2 * beta_if_base
        tau_ed = (mu0_eff / 2) * ((ds_filamentary / 2) * (dws - ds_filamentary) / 2) / rho_el_Outer
        tau = tau_if + tau_ed if flag_coupling else tau_if
        beta_if = 2 * tau / mu0_eff if flag_coupling else beta_if_base

        # Currents and Power Calculations
        I_if_base = beta_if * ds_filamentary
        P_if_base = beta_if * (ds_filamentary / 2) ** 2 * np.pi * l_mag

        # Calculating parameters
        M_if, R_if, L_if, I_if, P_if = calculate_parameters_RLM_xy(w, fMag_X, fMag_Y, tau, I_if_base, P_if_base)

        # Final Results
        if flag_save:
            L_group, R_group = self.__group_components_LR(frequency=frequency, L=L_if, R=R_if, sort_on='strands')
            self._setAttribute(self.IFCC, 'L', L_group)
            self._setAttribute(self.IFCC, 'R', R_group)
            self._setAttribute(self.IFCC, 'P', P_if)
            self._setAttribute(self.IFCC, 'tau', tau)

        M_if_x, M_if_y = np.squeeze(M_if[0, :, :]), np.squeeze(M_if[1, :, :])
        return M_if_x, M_if_y


    def calculate_ISCC(self, T: float, fMag_X: np.ndarray, fMag_Y: np.ndarray, turn_I: int = 0, flag_coupling: bool = True, flag_save: bool = False) -> np.ndarray:
        '''
        Function that calculates the power loss and induced currents by ISCL and derives the equivalent circuit parameter

        :param T: temperature vector
        :param fMag_X: field-factor along X axis for each strand
        :param fMag_Y: field-factor along Y axis for each strand
        :param turn_I: turn ID
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the ISCC dataclass

        :return M_is: mutual coupling
        :return M_is*0:
        '''
        # Precompute values
        frequency = self.frequency
        w = 2 * np.pi * frequency.reshape(len(frequency), 1)
        l_mag = self.General.magnet_length
        n_strands = self.HalfTurns.n_strands
        n_HT = self.General.num_HalfTurns
        inverse_field = int(n_HT / 4) * [1] + int(n_HT / 4) * [-1] + int(n_HT / 4) * [1] + int(n_HT / 4) * [-1]
        inverse_field = np.repeat(inverse_field, n_strands)
        wBare, hBare, Lp_s = self.HalfTurns.bare_cable_width, self.HalfTurns.bare_cable_height_mean, self.HalfTurns.strand_twist_pitch
        dws = self.HalfTurns.diameter
        R_c = self.HalfTurns.Rc
        C = self.HalfTurns.C_strand
        Nc = self.HalfTurns.Nc
        RRR = self.HalfTurns.RRR
        fsc = self.HalfTurns.fsc
        f_ro_eff = self.HalfTurns.f_rho_effective
        f = self.frequency

        # Calculate alphas_ht
        rotation_ht = self.HalfTurns.rotation_ht / 180 * np.pi
        alphasRAD = self.HalfTurns.alphaDEG_ht * np.pi / 180
        mirror_block = self.HalfTurns.mirror_ht
        alphas_ht = np.where(mirror_block == 0, alphasRAD - rotation_ht, np.pi / 2 - alphasRAD - rotation_ht)
        alphas_ht = np.repeat(alphas_ht,self.HalfTurns.n_strands)

        # Field-factors (vectorized)
        sin_alphas, cos_alphas = np.sin(alphas_ht), np.cos(alphas_ht)
        f_magPerp = (-fMag_X * sin_alphas + fMag_Y * cos_alphas) * inverse_field
        r_magPerp = (fMag_X * cos_alphas + fMag_Y * sin_alphas)
        B_temp = np.sqrt(fMag_X ** 2 + fMag_Y ** 2)
        ## Reverse action:
        ## fMag_X = r_magPerp.T*np.cos(alphas)-f_magPerp.T*np.sin(alphas)
        ## fMag_Y = r_magPerp.T*np.sin(alphas)+f_magPerp.T*np.cos(alphas)

        # Create f_magPerp_ht, r_magPerp_ht, and B_ht arrays
        f_magPerp_ht = np.zeros((len(n_strands), len(frequency)))
        r_magPerp_ht = np.zeros((len(n_strands), len(frequency)))
        B_ht = np.zeros((len(n_strands), len(frequency)))

        tempS = 0
        for i, n in enumerate(n_strands):
            slice_indices = slice(tempS, tempS + n)
            f_magPerp_ht[i,:] = np.mean(f_magPerp[:, slice_indices], axis=1)
            r_magPerp_ht[i,:] = np.mean(r_magPerp[:, slice_indices], axis=1)
            B_ht[i, :] = self.General.I_magnet * np.mean(B_temp[:, slice_indices], axis=1)
            tempS += n

        # Precompute constants for equivalent circuit parameter calculations
        beta_is = 1 / 120 * Lp_s / R_c * n_strands * (n_strands - 1) * wBare / hBare
        alpha_c = wBare / hBare
        factor_tau = alpha_c * Nc / (alpha_c + C * (Nc - 1))  # Eq. 4.41 in Arjans Thesis p.89
        tau_is = self.mu0*beta_is
        # tau_is = 1.65e-08 * (Lp_s * (n_strands ** 2 - 4 * n_strands)) / R_c * factor_tau  # Eq. 4.31 in Arjans Thesis p.78
        # rho_C_Strands = R_c / (rho_el_Outer * (n_strands ** 2 - n_strands) / (2 * Lp_s * alpha_c)) #Eq. 4.33 in Arjans Thesis p. 78

        # Compute power and current losses
        P_base = l_mag * beta_is * wBare * hBare
        I_base = beta_is * hBare

        M_is, R_is, L_is, I_is, P_is = calculate_parameters_RLM(w, f_magPerp_ht, tau_is, I_base, P_base)

        # Calculate warm resistance of a strand-pitch
        if not self.Options.flag_SC:
            ## Add the warm part to account for ISCL in non-superconducting state
            rho_el_Outer = self.__rhoCu_nist(T, B_ht[:, 0], RRR*f_ro_eff) + 1e-12
            alpha_st = np.arctan(wBare/(Lp_s/2)) #Half twist-pitch as Lp is the full length until its back at the beginning
            l_strand = 2 * wBare / np.sin(alpha_st) + 2 * hBare  # twice as we go back AND forth
            A_strand = (1 - fsc) * np.pi * (dws / 2) ** 2
            R_strand = rho_el_Outer * l_strand / A_strand
            alpha_c = wBare / hBare
            rho_C_Strands = R_c / (rho_el_Outer * (n_strands ** 2 - n_strands) / (
                        2 * Lp_s * alpha_c))  # Eq. 4.33 in Arjans Thesis p. 78
            alpha_c = wBare / hBare

            R_c_warm = 2e-3 * rho_C_Strands * rho_el_Outer * (n_strands** 2 - n_strands) / (2 * Lp_s * alpha_c)
            R_c_N = R_c_warm + R_strand
            # fT = 1/(1.9)**0.08*T**(0.08)
            # fT = 2*1/(np.log(1.9)**0.186)*np.log(T)**0.186
            fT = 1 / (np.log(1.9) ** 0.186) * np.log(T) ** 0.186
            # fT = 1 / (np.log(1.9) ** 0.3179) * np.log(T) ** 0.3179
            R_c_warm = R_c * fT
            R_c_N = fT * (R_c_warm + R_strand)

            tau_is_N = np.zeros(Nc.shape)
            factor_tau = alpha_c * Nc / (alpha_c + C * (Nc - 1))  # Eq. 4.41 in Arjans Thesis p.89
            for i in range(len(tau_is_N)):
                if Nc[i] >= 8:
                    tau_is_N[i] = 1.65e-8 * C[i] * (Lp_s[i] * (n_strands[i] ** 2 - 4 * n_strands[i])) / R_c_N[i] * factor_tau[
                        i]  # Eq. 4.31 in Arjans Thesis p.78
                else:
                    tau_is_N[i] = self.mu0 * beta_is[i]
            # tau_is_N = 1.65e-8*C*2/(fT) * (Lp_s*(nS**2-4*nS))/R_c_N *factor_tau # Equation 4.31 in Arjans Thesis P.78 and Eq. 4.41
            # beta_is_N = tau_is_N/ self.mu0
            beta_is_N = 1 / 120 * Lp_s / R_c_N * n_strands * (n_strands - 1) * wBare / hBare  # 60 works well for 290 K

            ## Adjust the components again on the new time constant
            alpha = 1 / np.sqrt((1 + (w * tau_is_N) ** 2))
            dB = w * f_magPerp_ht.T * alpha

            P_is = l_mag * beta_is_N * dB ** 2 * wBare * hBare
            I_is = beta_is_N * hBare * dB
            # I_is = 1 / 12 * Lp_s / R_c * wBare * dB * (nS ** 2 - 1) / nS
            I_tot_im = I_is * alpha
            # I_tot_re = np.sqrt(I_is ** 2 - I_tot_im ** 2)
            I_tot_re = I_is * alpha * w * tau_is_N
            I_is = I_tot_re + 1j * I_tot_im

            # Calculate equivalent parameter
            R_is = P_is / np.real((I_is * np.conjugate(I_is)))
            L_is = np.ones((len(f), 1)) * tau_is_N * R_is[0, :]
            M_is = (1j * w.reshape(len(f), 1) * L_is * I_is + I_is * R_is) / (1j * w.reshape(len(f), 1) * 1)
            # M_is = np.sqrt(np.real(M_is) ** 2 + np.imag(M_is) ** 2)

        # ## Calculate the return field
        # Assuming a current line on each side of the cable
        # Average distance to each strand is hence: (1/2*(dws/2 + (nS/2-1)*dws)), neglecting hBare
        # Twice, as we have one line on each side -> both generating the same field
        # B_return = (2 * (self.mu0 * np.abs(I_is)) / np.pi * 1 / (1 / 2 * (dws / 2 + (n_strands / 2 - 1) * dws)))
        # dB_return = (B_return/tau_is)

        # f_mag_X_return_ht = r_magPerp_ht*np.cos(alphas_ht)-B_return.T*np.sin(alphas_ht)
        # f_mag_Y_return_ht = r_magPerp_ht*np.sin(alphas_ht)+B_return.T*np.cos(alphas_ht)
        # ratio_Breturn = B_return / B_ht.T

        if flag_coupling:
            if not turn_I: raise Exception('Please provide the turn-ID in the arguments of ISCC. ')
            definedMagneticCoil = self.definedMagneticCoil
            I_is_abs = replace_below_tolerance(np.abs(I_is),1e-3)
            idx_eval = np.where(self.Strands.strands_to_apertures==self.HalfTurns.HalfTurns_to_apertures[turn_I-1])[0]
            self.ISCC.f_mag_X_ISCCreturn[turn_I - 1, :, :] = fMag_X
            self.ISCC.f_mag_Y_ISCCreturn[turn_I - 1, :, :] = fMag_Y
            if np.any(I_is_abs):
                sign_f_magPerp_ht = np.sign(f_magPerp_ht).T
                Istrands_ISCC = np.hstack((I_is_abs * sign_f_magPerp_ht, -I_is_abs * sign_f_magPerp_ht)).T
                definedMagneticCoil.setStrandPositions(self.HalfTurns.x_turn_ends.flatten(), self.HalfTurns.y_turn_ends.flatten(), Istrands_ISCC)
                n_Bx_strands, n_By_strands, _ = definedMagneticCoil.calculateMagneticField(self.Strands.x_strands[idx_eval],self.Strands.y_strands[idx_eval])
                self.ISCC.f_mag_X_ISCCreturn[turn_I-1,:,idx_eval] += n_Bx_strands
                self.ISCC.f_mag_Y_ISCCreturn[turn_I-1,:, idx_eval] += n_By_strands

        # Final Results
        if flag_save:
            L_group, R_group = self.__group_components_LR(frequency=frequency, L=L_is, R=R_is, sort_on='halfturns')
            self._setAttribute(self.ISCC, 'L', L_group)
            self._setAttribute(self.ISCC, 'R', R_group)
            self._setAttribute(self.ISCC, 'P', P_is)
            self._setAttribute(self.ISCC, 'tau', tau_is)

        return M_is, M_is*0


    def calculate_ED(self, T: float, fMag_X: np.ndarray, fMag_Y: np.ndarray, flag_coupling: bool = True, flag_save: bool = False) -> np.ndarray:
        '''
        Calculates the equivalent coupling loops in the outer copper sheet for a given temperature and field

        :param T: temperature vector
        :param fMag_X: field-factor along X axis for each strand
        :param fMag_Y: field-factor along Y axis for each strand
        :param flag_coupling: if True it means it has to be coupled to another effect
        :param flag_save: if True saves the circuit parameter in the ED dataclass

        :return M_ed_x: mutual coupling along x
        :return M_ed_y: mutual coupling along y
        '''

        f = self.frequency
        w = 2 * np.pi * f.reshape(len(f), 1)

        l_mag = self.General.magnet_length
        RRR = self.Strands.RRR
        rws = self.Strands.diameter / 2

        if not self.Options.flag_SC:  # TODO - check if needed or not
            r_filamentary = self.Strands.d_filamentary / 2 * 0.5
        else:
            r_filamentary = self.Strands.d_filamentary / 2


        B = self.General.I_magnet * np.sqrt(fMag_X[0,:]**2+fMag_Y[0,:]**2)
        rho_el_0 = self.__rhoCu_nist(T=T, B=B, RRR=RRR) + 1e-12
        tb_strand = rws - r_filamentary
        rho_el_0 = rho_el_0 + 1e-12

        # Calculating time constant, correction factor and field derivative
        tau_ed = self.mu0 / 2 * ((rws) * tb_strand) / rho_el_0
        # tau_ed = self.mu0 / 8 * dws**2 / rho_el_0 ## Formula from Turck79
        # Skindepth
        skinDepth = np.sqrt(2 * rho_el_0 / (w * self.mu0))
        idx_s = np.argmin(abs(skinDepth - (1 - 1 / np.exp(1)) * tb_strand), axis=0) + 1

        #### Calculate the DC case
        # Calculating the power loss
        P_DC_base = 1/2 * l_mag * np.pi/(8*rho_el_0) * rws **4
        # P_DC = tau_ed/self.mu0/2 * (1-(dS_inner/dws)**2) * (dB*alpha)**2 # Formula from Turck
        # P_DC = v3 * v1v2/(v1v2+1)*beta_if*(dB*alpha)**2 # Formula from Arjan's thesis
        # Calculating the induced current
        I_DC = rws ** 3 / (3 * rho_el_0)
        # I_DC = 2 * tb_strand / (3 * rho_el_0) * (tb_strand ** 2 - 3 * tb_strand * dS_outer + 3 * dS_outer ** 2) * (dB * alpha)
        # I_DC = 2 * tau_ed / self.mu0 * dS_outer * (dB*alpha)

        # Calculating parameters
        M_ed_DC, R_ed_DC, L_ed_DC, I_ed_DC, P_ed_DC = calculate_parameters_RLM_xy(w, fMag_X, fMag_Y, tau_ed, I_DC, P_DC_base)

        #### Calculate the AC case

        # Calculating the power loss
        P_ed_AC = 1/2 * l_mag * np.pi / (2*rho_el_0) * rws * skinDepth ** 3 * (w*np.array([fMag_X,fMag_Y]))**2
        # P_AC = dB ** 2 * skinDepth/(w*4*self.mu0*dws) #Formula from Turck1979
        R_ed_AC = (P_ed_AC/np.real(I_ed_DC*np.conjugate(I_ed_DC)))
        R_ed_AC = R_ed_AC[0,:,:]
        M_ed_AC = (1j * w * L_ed_DC * I_ed_DC + I_ed_DC*R_ed_AC) / (1j * w * 1)

        ## Concatenate results
        M_ed = np.concatenate((M_ed_DC[:, :idx_s[0], :], M_ed_AC[:, idx_s[0]:, :]), axis=1)
        L_ed = L_ed_DC
        R_ed = np.concatenate((R_ed_DC[:idx_s[0], :], R_ed_AC[idx_s[0]:, :]), axis=0)
        P_ed = np.concatenate((P_ed_DC[:, :idx_s[0], :], P_ed_AC[:, idx_s[0]:, :]), axis=1)
        I_ed = I_ed_DC
        # M_ed = M_ed_DC
        # L_ed = L_ed_DC
        # R_ed = R_ed_DC
        # P_ed = P_ed_DC
        # I_ed = I_ed_DC


        if flag_save:
            self._setAttribute(self.ED, 'M', M_ed)
            self._setAttribute(self.ED, 'R', R_ed)
            self._setAttribute(self.ED, 'L', L_ed)
            self._setAttribute(self.ED, 'P', P_ed)
            self._setAttribute(self.ED, 'tau', tau_ed)

        M_ed_x, M_ed_y = np.squeeze(M_ed[0, :, :]), np.squeeze(M_ed[1, :, :])
        # I_ed_x, I_ed_y = np.squeeze(I_ed[0, :, :]), np.squeeze(I_ed[1, :, :])
        return M_ed_x, M_ed_y


    def calculate_CB(self, T: float):
        '''
        Function that calculates the equivalent parameter for eddy currents in the cold bore.
        It takes the Temperature. It then calculates the resistivity and
        __interpolates the current and power from Comsol model that includes the ColdBore effect.

        :param T: Temperature vector
        '''
        if not isinstance(self.CB.f_SS, (int,float)):
            self.CB.f_SS = 1
        if not isinstance(self.CB.r_CB, (int,float)) or not isinstance(self.CB.t_CB, (int,float)):
            raise Exception('flag_CB is on. Please provide thickness t_CB and radius r_CB')

        f = self.frequency
        w = 2 * np.pi * f
        rho_CB = self.__rhoSS_nist(T=T)*self.CB.f_SS

        r_CB = self.CB.r_CB #0.052
        t_CB = self.CB.t_CB #0.0015
        l_mag = self.General.magnet_length
        fm = self.B_nom_center / self.ledet_options.Iref

        tau_CB = self.mu0 / 2 * (r_CB) * t_CB / rho_CB
        # tau_CB = 3.3e-5

        skinDepth = np.sqrt(2 * rho_CB / (w * self.mu0))
        idx_s = np.argmin(abs(skinDepth - (1 - 1 / np.exp(1)) * t_CB), axis=0) + 1
        if idx_s >= len(f): idx_s = len(f) - 1

        dB = w * fm
        alpha = 1 / np.sqrt((1 + (w * tau_CB) ** 2))

        # Calculating the power loss
        P_DC = ((r_CB) ** 4 - (r_CB - t_CB) ** 4) / (4 * rho_CB) * (dB * alpha) ** 2 * np.pi
        P_AC = skinDepth ** 3 / (2 * rho_CB) * dB ** 2 * np.pi * (r_CB)
        P_tot = [P_DC[:idx_s], P_AC[idx_s:]]
        P_tot = 1/2 * np.concatenate(P_tot).ravel() * l_mag

        I_tot = 2 * t_CB / (3 * rho_CB) * (t_CB ** 2 - 3 * t_CB * r_CB + 3 * r_CB ** 2) * (dB * alpha)
        I_tot_im = I_tot * alpha
        I_tot_re = (I_tot * alpha * w * tau_CB)
        # I_tot_re = np.sqrt(I_tot ** 2 - I_tot_im ** 2)
        I_tot = I_tot_re + 1j * I_tot_im

        fac = np.sqrt(w[idx_s:]) / np.sqrt(w[idx_s])
        I_tot = [I_tot[:idx_s], I_tot[idx_s:] * fac]
        I_tot = np.concatenate(I_tot).ravel()

        # Calculating the coupled loop equivalent parameter
        R_cb = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_cb = tau_CB * R_cb[0]
        M_cb = (1j * w * L_cb * I_tot + I_tot * R_cb) / (1j * w * 1)
        # M_cb = np.sqrt(np.real(M_cb*np.conjugate(M_cb))) # Checked: is the same as the line below
        # M_cb = np.sqrt(np.real(M_cb) ** 2 + np.imag(M_cb) ** 2)
        M_cb = np.transpose(np.ones(M_cb.shape).transpose() * M_cb[0])
        L_cb = np.repeat(L_cb, len(R_cb))

        L_cb = np.repeat(L_cb[:, np.newaxis],self.General.apertures, axis=1)
        R_cb = np.repeat(R_cb[:, np.newaxis], self.General.apertures, axis=1)
        M_cb = np.repeat(M_cb[:, np.newaxis], self.General.apertures, axis=1)

        self._setAttribute(self.CB, 'P', P_tot)
        self._setAttribute(self.CB, 'I', I_tot)
        self._setAttribute(self.CB, 'tau', tau_CB)
        self._setAttribute(self.CB, 'L', L_cb)
        self._setAttribute(self.CB, 'R', R_cb)
        self._setAttribute(self.CB, 'M', M_cb)


    def calculate_BS(self):
        '''
        Function that calculates the equivalent parameter for eddy currents in the beam screen.
        '''
        if not isinstance(self.BS.r_BS, (int,float)):
            raise Exception('flag_BS on but no BS parameter provided.')
        if not isinstance(self.BS.f_SS, (int,float)):
            self.BS.f_SS = 1

        frequency = self.frequency
        w = 2 * np.pi * frequency

        # Setting up the required parameter for the MB-magnet
        I = self.General.I_magnet
        if isinstance(self.BS.T_BS, (int, float)):
            T = self.BS.T_BS
        else:
            T = 20
        factor_SS = self.BS.f_SS
        fm = self.B_nom_center / self.ledet_options.Iref
        l_mag = self.General.magnet_length

        apertures = ['A', 'B']
        R_BS = []
        L_BS = []
        M_BS = []
        I_BS = []
        P_BS = []
        tau_BS = []
        for aperture in apertures:
            rho_Cu_Inner = self.__rhoCu_nist(np.array([T]), np.array([self._getAttribute('BS', f'RRR_Ap{aperture}_1')]), np.array([fm * I]))
            rho_Cu_Outer = self.__rhoCu_nist(np.array([T]), np.array([self._getAttribute('BS', f'RRR_Ap{aperture}_2')]), np.array([fm * I]))
            rho_SS = self.__rhoSS_nist(T)*factor_SS
            tb_1 = self._getAttribute('BS', f't_Ap{aperture}_1')
            tb_2 = self._getAttribute('BS', f't_Ap{aperture}_2')
            tb_S = self._getAttribute('BS', f't_SS_{aperture}')
            
            R = self.BS.r_BS # - tb_1 - tb_2 - tb_S
            R_eq = self.BS.r_BS * 1.0798  ##Not the actual radius but an equivalent one, Correction factor of 1.08 valid for LHC main dipole !!!

            ## Derivation of the induced current
            # Layer 1
            skinDepth_1 = np.sqrt(2 * rho_Cu_Inner / (w * self.mu0))
            idx_s1 = min(np.argmin(abs(skinDepth_1 - (1 - 1 / np.exp(1)) * tb_1))+2, len(frequency) - 1)

            tau_DC1_dyn = self.mu0 / 2 * R_eq * skinDepth_1 * (1 - np.exp(-tb_1 / skinDepth_1)) / rho_Cu_Inner
            tau_DC1_dyn = [tau_DC1_dyn[:idx_s1], [tau_DC1_dyn[idx_s1]] * (len(frequency) - idx_s1)]
            tau_DC1_dyn = np.concatenate(tau_DC1_dyn).ravel()
            alpha_DC1_dyn = 1 / np.sqrt(1 + (w * tau_DC1_dyn) ** 2)

            tau_DC1_sta = self.mu0 / 2 * R_eq * (tb_1) / rho_Cu_Inner
            alpha_DC1_sta = 1 / np.sqrt(1 + (w * tau_DC1_sta) ** 2)
            P_DC_1 = np.pi * (fm * w * alpha_DC1_sta) ** 2 * 1 / 4 * (1 / rho_Cu_Inner * ((R) ** 4 - (R - tb_1) ** 4))
            P_AC_1 = skinDepth_1 ** 2 / (2 * rho_Cu_Inner) * (fm * w) ** 2 * np.pi * (skinDepth_1) * (R - tb_2 - tb_S)
            P_1 = [P_DC_1[:idx_s1], P_AC_1[idx_s1:]]
            P_1 = np.concatenate(P_1).ravel()

            # Layer 2
            skinDepth_2 = np.sqrt(2 * rho_Cu_Outer / (w * self.mu0))
            # idx_s2 = np.argmin(abs((tb_2)-skinDepth_2))+1
            idx_s2 = min(np.argmin(abs(skinDepth_2 - (1 - 1 / np.exp(1)) * tb_2))+3, len(frequency))

            P_DC_2a = np.pi * (fm * w * alpha_DC1_dyn) ** 2 * 1 / 4 * (1 / rho_Cu_Outer * ((R - tb_S) ** 4 - (R - tb_2 - tb_S) ** 4))
            P_DC_2b = np.pi * (fm * w * alpha_DC1_dyn[idx_s1]) ** 2 * 1 / 4 * (1 / rho_Cu_Outer * ((R - tb_S) ** 4 - (R - tb_2 - tb_S) ** 4))
            P_AC_2 = skinDepth_2 ** 2 / (2 * rho_Cu_Outer) * (fm * w )** 2 * np.pi * (skinDepth_2) * (R - tb_S)

            P_2 = [P_DC_2a[:idx_s1], P_DC_2b[idx_s1:idx_s2], P_AC_2[idx_s2:]]
            P_2 = np.concatenate(P_2).ravel()

            # Layer 3
            skinDepth_3 = np.sqrt(2 * rho_SS / (w * self.mu0))
            idx_s3a = min(np.argmin(abs(alpha_DC1_dyn - 0.05)) - 1, len(frequency) - 1)
            idx_s3b = min(np.argmin(abs(skinDepth_3 - (1 - 1 / np.exp(1)) * tb_S))+2, len(frequency))
            if idx_s3a > idx_s3b: idx_s3b = idx_s3a

            P_DC_3a = np.pi * (fm * w * alpha_DC1_dyn) ** 2 * 1 / 4 * (1 / rho_SS * ((R) ** 4 - (R - tb_S) ** 4))
            P_DC_3b = np.pi * (fm * w * alpha_DC1_dyn[idx_s3a]) ** 2 * 1 / 4 * (1 / rho_SS * ((R) ** 4 - (R - tb_S) ** 4))
            P_AC_3 = l_mag*skinDepth_3 ** 3 / (2 * rho_SS) * (fm * w) ** 2 * np.pi * R

            P_3 = [P_DC_3a[:idx_s3a], P_DC_3b[idx_s3a:idx_s3b], P_AC_3[idx_s3b:]]
            P_3 = np.concatenate(P_3).ravel()
            ###
            P_tot = P_1 + P_2 + P_3
            P_tot = l_mag * P_tot


            ## Derivation of the induced current
            I_DC1 = 2 * (tb_1) / (3 * rho_Cu_Inner) * ((tb_1) ** 2 - 3 * (tb_1) * R + 3 * R ** 2) * (fm * w * alpha_DC1_sta)
            I_DC1_im = I_DC1 * alpha_DC1_sta
            R2 = R - tb_S
            I_DC2 = 2 * (tb_2) / (3 * rho_Cu_Outer) * ((tb_2) ** 2 - 3 * (tb_2) * R2 + 3 * R2 ** 2) * (fm * w * alpha_DC1_sta)
            I_DC2_im = I_DC2 * alpha_DC1_sta

            I_DC3a = 2 * (tb_S) / (3 * rho_SS) * ((tb_S) ** 2 - 3 * (tb_S) * R + 3 * R ** 2) * (fm * w * alpha_DC1_dyn)
            I_DC3b = 2 * (tb_S) / (3 * rho_SS) * ((tb_S) ** 2 - 3 * (tb_S) * R + 3 * R ** 2) * (fm * w * alpha_DC1_dyn[idx_s3a])
            I_3 = [I_DC3a[:idx_s3a], I_DC3b[idx_s3a:]]
            I_3 = np.concatenate(I_3).ravel()
            I_3_im = I_3

            I_tot = (I_DC1 + I_DC2 + I_3)
            I_tot_im = (I_DC1_im + I_DC2_im + I_3_im)
            I_tot_re = (I_tot * alpha_DC1_sta * w * tau_DC1_sta)
            # I_tot_re = np.sqrt(I_tot ** 2 - I_tot_im ** 2)
            I_tot = (I_tot_re + 1j * I_tot_im)

            # fac = np.sqrt(w[idx_s1:]) / np.sqrt(w[idx_s1])
            # I_tot = [I_tot[:idx_s1], I_tot[idx_s1:] * fac]
            # I_tot = np.concatenate(I_tot).ravel()

            # Calculating the coupled loop equivalent parameter
            R_ap = P_tot / np.real((I_tot * np.conjugate(I_tot)))
            L_ap = tau_DC1_sta * R_ap[0]
            M_ap = (1j * w * L_ap * I_tot + I_tot * R_ap) / (1j * w * 1)
            # M_ap = np.sqrt(np.real(M_ap) ** 2 + np.imag(M_ap) ** 2)
            M_ap = np.transpose(np.ones(M_ap.shape).transpose() * M_ap[0])

            R_BS.append(R_ap)
            L_BS.append([L_ap[0]] * len(frequency))
            M_BS.append(M_ap)
            I_BS.append(I_tot)
            P_BS.append(P_tot)
            tau_BS.append(tau_DC1_sta)

        L_BS = np.array(L_BS).transpose()
        R_BS = np.array(R_BS).transpose()
        M_BS = np.array(M_BS).transpose()
        I_BS = np.array(I_BS).transpose()
        P_BS = np.array(P_BS).transpose()
        tau_BS = np.array(tau_BS).transpose()

        self._setAttribute(self.BS, 'P', P_BS)
        self._setAttribute(self.BS, 'I', I_BS)
        self._setAttribute(self.BS, 'tau', tau_BS)
        self._setAttribute(self.BS, 'L', L_BS)
        self._setAttribute(self.BS, 'R', R_BS)
        self._setAttribute(self.BS, 'M', M_BS)


    def calculate_Wedge(self, T: float):
        '''
        Function that calculates the equivalent parameter for eddy currents in the copper Wedge
        It takes the Temperature. It then calculates the resistivity and
        __interpolates the current and power from a pre-simulated Comsol model that includes the wedges effect.

        :param T: Temperature vector
        '''
        if not isinstance(self.Wedge.RRR_Wedge, (int, float)):
                raise Exception('Set flag_Wedge=True, but no RRR_Wedge provided.')
        rho_W = self.__rhoCu_nist(T=T, RRR=self.Wedge.RRR_Wedge, B=np.array([0]))
        P_tot, I_tot, tau_W, frequency = self.__interpolate(rho=rho_W, case='Wedge')

        w = 2 * np.pi * frequency
        P_tot = P_tot * self.General.magnet_length * 2

        # Calculating the coupled loop equivalent parameter
        # R_W = P_tot / I_tot ** 2
        R_W = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_W = tau_W * R_W[0]
        L_W = np.repeat(L_W, len(R_W))
        M_W = (1j * w * L_W * I_tot + I_tot * R_W) / (1j * w * 1)
        # M_W = np.sqrt(np.real(M_W*np.conjugate(M_W))) # Checked: is the same as the line below
        # M_W = np.sqrt(np.real(M_W) ** 2 + np.imag(M_W) ** 2)
        # M_W1 = M_W[:tau_index]
        # M_W2 = np.transpose(np.ones(len(M_W)-tau_index).transpose() * M_W[tau_index])
        # M_W = np.concatenate((M_W1, M_W2))
        M_W = np.transpose(np.ones(M_W.shape).transpose() * M_W[0])

        L_W = np.repeat(L_W[:, np.newaxis],self.General.apertures, axis=1)
        R_W = np.repeat(R_W[:, np.newaxis], self.General.apertures, axis=1)
        M_W = np.repeat(M_W[:, np.newaxis], self.General.apertures, axis=1)

        self._setAttribute(self.Wedge, 'P', P_tot)
        self._setAttribute(self.Wedge, 'I', I_tot)
        self._setAttribute(self.Wedge, 'tau', tau_W)
        self._setAttribute(self.Wedge, 'L', L_W)
        self._setAttribute(self.Wedge, 'R', R_W)
        self._setAttribute(self.Wedge, 'M', M_W)


    def calculate_CPS(self):
        '''
        Function that calculates the equivalent parameter for eddy currents in the coil protection sheets.
        It takes the Temperature. It then calculates the resistivity and
        __interpolates the current and power from Comsol model that includes the ColdBore effect.
        '''

        P_tot, I_tot, tau_CPS, frequency = self.__interpolate(rho=self.CPS.rho_CPS, case='CPS')
        w = 2 * np.pi * frequency
        P_tot = P_tot * self.General.magnet_length * 2

        # Calculating the coupled loop equivalent parameter
        # R_W = P_tot / I_tot ** 2
        R_CPS = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_CPS = tau_CPS * R_CPS[0]
        L_CPS = np.repeat(L_CPS, len(R_CPS))
        M_CPS = (1j * w * L_CPS * I_tot + I_tot * R_CPS) / (1j * w * 1)
        # M_W = np.sqrt(np.real(M_W*np.conjugate(M_W))) # Checked: is the same as the line below
        # M_W = np.sqrt(np.real(M_W) ** 2 + np.imag(M_W) ** 2)
        M_CPS = np.transpose(np.ones(M_CPS.shape).transpose() * M_CPS[0])

        L_CPS = np.repeat(L_CPS[:, np.newaxis],self.General.apertures, axis=1)
        R_CPS = np.repeat(R_CPS[:, np.newaxis], self.General.apertures, axis=1)
        M_CPS = np.repeat(M_CPS[:, np.newaxis], self.General.apertures, axis=1)

        self._setAttribute(self.CPS, 'P', P_tot)
        self._setAttribute(self.CPS, 'I', I_tot)
        self._setAttribute(self.CPS, 'tau', tau_CPS)
        self._setAttribute(self.CPS, 'L', L_CPS)
        self._setAttribute(self.CPS, 'R', R_CPS)
        self._setAttribute(self.CPS, 'M', M_CPS)


    def calculate_AlRing(self):
        '''
        Function that calculates the equivalent parameter for eddy currents in the coil protection sheets.
        It takes the Temperature. It then calculates the resistivity and
        __interpolates the current and power from Comsol model that includes the ColdBore effect.
        '''

        rho_AlRing = self.AlRing.rho_AlRing
        P_tot, I_tot, tau_AlRing, frequency = self.__interpolate(rho=rho_AlRing, case='AlRing')
        w = 2 * np.pi * frequency
        P_tot = P_tot * self.General.magnet_length * 2

        # Calculating the coupled loop equivalent parameter
        # R_W = P_tot / I_tot ** 2
        R_AlRing = P_tot / np.real((I_tot * np.conjugate(I_tot)))
        L_AlRing = tau_AlRing * R_AlRing[0]
        L_AlRing = np.repeat(L_AlRing, len(R_AlRing))
        M_AlRing = (1j * w * L_AlRing * I_tot + I_tot * R_AlRing) / (1j * w * 1)
        # M_W = np.sqrt(np.real(M_W*np.conjugate(M_W))) # Checked: is the same as the line below
        # M_W = np.sqrt(np.real(M_W) ** 2 + np.imag(M_W) ** 2)
        M_AlRing = np.transpose(np.ones(M_AlRing.shape).transpose() * M_AlRing[0])

        L_AlRing = np.repeat(L_AlRing[:, np.newaxis],self.General.apertures, axis=1)
        R_AlRing = np.repeat(R_AlRing[:, np.newaxis], self.General.apertures, axis=1)
        M_AlRing = np.repeat(M_AlRing[:, np.newaxis], self.General.apertures, axis=1)

        self._setAttribute(self.AlRing, 'P', P_tot)
        self._setAttribute(self.AlRing, 'I', I_tot)
        self._setAttribute(self.AlRing, 'tau', tau_AlRing)
        self._setAttribute(self.AlRing, 'L', L_AlRing)
        self._setAttribute(self.AlRing, 'R', R_AlRing)
        self._setAttribute(self.AlRing, 'M', M_AlRing)


    def __interpolate(self, rho: np.ndarray, case: str) -> np.ndarray:
        '''
        Helper function that takes a temperature, fits the respective resistivity to it and __interpolates from other resistivity values.

        :param case: name of the effect to select the excel file from (Wedge or CB)
        :param rho: resistivity of the Effect
        '''
        if not isinstance( rho, np.ndarray):
            rho = np.array([rho])

        name = self.General.magnet_name
        path = Path(self.General.local_library_path).resolve()
        # Takes the PowerLoss excel file corresponding to that effect
        df_P = pd.read_csv(os.path.join(path, 'TFM_input', f'{name}_PowerLoss_{case}_Interpolation.csv')).dropna(axis=1)
        # Takes the InducedCurrent excel file corresponding to that effect
        df_I = pd.read_csv(os.path.join(path, 'TFM_input', f'{name}_InducedCurrent_{case}_Interpolation.csv')).dropna(axis=1)
        frequency_P = df_P['f'].values[1:]
        frequency_I = df_I['f'].values[1:]

        if not np.allclose(frequency_P, frequency_I):
            raise Exception(f'Error in interpolation of {case}: Frequency for current and power are not equal.')
        else:
            frequency = frequency_P

        if len(frequency) != len(self.frequency):
            if self.verbose: print('Interpolation frequency is different. Adjusting internal frequency.')
            self.frequency = frequency
        elif not np.allclose(frequency, self.frequency):
            if self.verbose: print('Interpolation frequency is different. Adjusting internal frequency.')
            self.frequency = frequency

        # Takes all the possible resistivity values included in these files
        resistivities = np.array(df_P.iloc[0, 1:]).astype(float)
        order = np.argsort(resistivities)
        resistivities = resistivities[order]

        P_temp = np.zeros((len(frequency),))
        I_temp_real = np.zeros((len(frequency),))
        I_temp_imag = np.zeros((len(frequency),))

        # Performs interpolation between the desired resistivity value (rho[0]) and the resistivity values extracted from the file.
        # This is done to obtain accurate values of power loss and induced current corresponding to the desired resistivity.
        for i in range(len(frequency)):
            P_res = df_P.loc[df_P['f'] == frequency[i]].reset_index(drop=True).values[0][1:]
            P_res = P_res[order].astype(float)
            P_temp[i] = np.interp(rho[0], resistivities, P_res)
            I_res = df_I.loc[df_I['f'] == frequency[i]].reset_index(drop=True).values[0][1::2]
            I_res = I_res[order].astype(float)
            I_temp_real[i] = np.interp(rho[0], resistivities, I_res)
            I_res = df_I.loc[df_I['f'] == frequency[i]].reset_index(drop=True).values[0][2::2]
            I_res = I_res[order].astype(float)
            I_temp_imag[i] = np.interp(rho[0], resistivities, I_res)
        I_tot = I_temp_real + 1j * I_temp_imag
        #I_tot = np.real(np.sqrt(I_tot * np.conjugate(I_tot)))

        P_tot = P_temp
        # In order to calculate the tau, it calls the helper function
        # tau_index = __calculate_tau_index(P_tot=P_tot, frequency=frequency)
        tau =  self.__calculate_tau(P_tot=P_tot, frequency=frequency, effect=case)

        return P_tot, I_tot, tau, frequency


    ####################################################################################################################
    ############################################### MAIN FUNCTION TFM ###############################################
    def change_coupling_parameter(self):
        '''
        Main function of TFM_model. It changes the equivalent coupling loop parameters for the corresponding magnet using all the other functions.
        '''

        frequency = self.frequency
        groups = self.General.sections
        T = self.temperature
        f_mag_Roxie= self.Strands.f_mag_Roxie
        self.Mutual_dict = {}

        # Inter-Strands Coupling Currents
        if self.Options.flag_ISCC:
            print(f'# Calculating ISCC parameter.')
            start_ISCC = time.time()
            flag_coupling = False
            if any(item in self.effects and item != 'ISCC' for item in self.effs_cond):
                self.ISCC.f_mag_X_ISCCreturn = np.zeros((self.General.num_HalfTurns, len(frequency), self.General.num_Strands), dtype=np.float32)
                self.ISCC.f_mag_Y_ISCCreturn = np.zeros((self.General.num_HalfTurns, len(frequency), self.General.num_Strands), dtype=np.float32)
                flag_coupling = True

            M = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_HalfTurns)).astype(complex)
            # I = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_HalfTurns)).astype(complex)
            for i in range(self.General.num_HalfTurns):
                if i<self.General.num_HalfTurns-1: flag_save=False
                else: flag_save = True
                M[i, :, :], _ = self.calculate_ISCC(T=T, fMag_X=self.Strands.f_mag_X_turns[i, :, :], fMag_Y=self.Strands.f_mag_Y_turns[i, :, :],
                                                            turn_I= i+1, flag_coupling=flag_coupling, flag_save=flag_save)
            print(f'- Parameter estimation took {np.round(time.time()-start_ISCC,2)} s, Avg. loop-time {np.round((time.time()-start_ISCC)/self.General.num_HalfTurns,4)} s.')
            self.ISCC.M, _  = self.__group_components_M(frequency, M, np.array([]), sort_on='halfturns')
            self.ISCC.M, _ = self.__adjust_M_for_short(self.ISCC.M, _, flag_component=False)
            start_eqLoop = time.time()
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'ISCC', self.domain,
                                                          self.frequency, self.ISCC.L, self.ISCC.R, self.ISCC.M, np.array([]),
                                                          groups=groups, force_new_name=self.General.lib_path)
            print(f'Setting library took {np.round(time.time() - start_eqLoop, 2)} s.')
            print(f'#- ISCC took {np.round(time.time()-start_ISCC,4)} s')

        # Persistent currents and magnetization
        if self.Options.flag_PC:
            print(f'# Calculating PC parameter.')
            start_PC = time.time()
            M_x = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_Strands))
            M_y = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_Strands))
            for i in range(self.General.num_HalfTurns):
                if i<self.General.num_HalfTurns-1: flag_save=False
                else: flag_save = True
                M_x[i,:,:], M_y[i,:,:] = self.calculate_PC(T=T, fMag_X=self.Strands.f_mag_X_turns[i,:,:],
                                             fMag_Y=self.Strands.f_mag_Y_turns[i,:,:], flag_coupling=False, flag_save=flag_save)
            print(f'- Parameter estimation took {np.round(time.time() - start_PC, 2)} s, Avg. loop-time {np.round((time.time() - start_PC) / self.General.num_HalfTurns,4)} s.' )
            self.PC.M_x, self.PC.M_y = self.__group_components_M(frequency, M_x, M_y, sort_on='strands')
            self.PC.M_x, self.PC.M_y = self.__adjust_M_for_short(self.PC.M_x, self.PC.M_y, flag_component=False)
            start_eqLoop = time.time()
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'PC', self.domain,
                                                          self.frequency, self.PC.L, np.array([]), self.PC.M_x, self.PC.M_y,
                                                          groups=groups, force_new_name=self.General.lib_path)
            print(f'Setting library took {np.round(time.time()-start_eqLoop,2)} s.')

            if self.Options.flag_ISCC: # calculates coupling between PC and ISCC
                print(f'## Calculate PC-ISCC coupling.')
                start_PC_ISCC = time.time()
                M_x = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                M_y = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                for i in range(1, self.General.sections + 1):
                    fX_group = np.sum(self.ISCC.f_mag_X_ISCCreturn[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :],axis=0)
                    fY_group = np.sum(self.ISCC.f_mag_Y_ISCCreturn[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :],axis=0)
                    M_x[i-1, :, :], M_y[i-1, :, :] = self.calculate_PC(T=T, fMag_X=fX_group, fMag_Y=fY_group,flag_coupling=False, flag_save=False)
                M_x_PC_ISCC, M_y_PC_ISCC = self.__group_components_M(frequency, M_x, M_y, sort_on='strands', skip_off_diagonal = True)
                self.Mutual_dict['M_PC_ISCC_x'] = M_x_PC_ISCC
                self.Mutual_dict['M_PC_ISCC_y'] = M_y_PC_ISCC
                print(f'PC-ISCC coupling took {np.round(time.time()-start_PC_ISCC, 2)} s.')
            print(f'#- PC took {np.round(time.time() - start_PC, 4)} s')

        # Inter-Filament Coupling Currents
        if self.Options.flag_IFCC:
            print(f'# Calculating IFCC parameter.')
            start_IFCC = time.time()
            M_x = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_Strands)).astype(complex)
            M_y = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_Strands)).astype(complex)
            for i in range(self.General.num_HalfTurns):
                if i < self.General.num_HalfTurns - 1:
                    flag_save = False
                else:
                    flag_save = True
                M_x[i, :, :], M_y[i, :, :] = self.calculate_IFCC(T=T, fMag_X=self.Strands.f_mag_X_turns[i, :, :],
                                                               fMag_Y=self.Strands.f_mag_Y_turns[i, :, :], flag_coupling=False, flag_save=flag_save)
            print(f'- Parameter estimation took {np.round(time.time() - start_IFCC, 2)} s, Avg. loop-time {np.round((time.time() - start_IFCC) / self.General.num_HalfTurns, 4)} s.')
            self.IFCC.M_x, self.IFCC.M_y = self.__group_components_M(frequency, M_x, M_y)
            self.IFCC.M_x, self.IFCC.M_y = self.__adjust_M_for_short(self.IFCC.M_x, self.IFCC.M_y, flag_component=False)
            start_eqLoop = time.time()
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'IFCC', self.domain,
                                                           self.frequency, self.IFCC.L, self.IFCC.R, self.IFCC.M_x, self.IFCC.M_y,
                                                          groups=groups, force_new_name=self.General.lib_path)
            print(f'Setting library took {np.round(time.time() - start_eqLoop,2 )} s.')

            if self.Options.flag_ISCC: # calculates coupling between IFCC and ISCC
                print(f'## Calculate IFCC-ISCC coupling.')
                start_IFCC_ISCC = time.time()
                M_x = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                M_y = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                for i in range(1,self.General.sections+1):
                    fX_group = np.sum(self.ISCC.f_mag_X_ISCCreturn[np.where(self.HalfTurns.HalfTurns_to_sections==i)[0], :, :],axis=0)
                    fY_group = np.sum(self.ISCC.f_mag_Y_ISCCreturn[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :],axis=0)
                    M_x[i-1, :, :], M_y[i-1, :, :] = self.calculate_IFCC(T=T, fMag_X=fX_group, fMag_Y=fY_group,flag_coupling=False, flag_save=False)
                M_x_ISCC_IFCC, M_y_ISCC_IFCC = self.__group_components_M(frequency, M_x, M_y, skip_off_diagonal = True)
                self.Mutual_dict['M_IFCC_ISCC_x'] = M_x_ISCC_IFCC
                self.Mutual_dict['M_IFCC_ISCC_y'] = M_y_ISCC_IFCC
                print(f'IFCC-ISCC coupling took {np.round(time.time() - start_IFCC_ISCC,2)} s.')

            if self.Options.flag_ED: # calculates coupling between IFCC and ED
                print(f'## Calculate IFCC-ED coupling.')
                start_IFCC_ED = time.time()
                M_x = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                M_y = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                for i in range(1,self.General.sections+1):
                    fX_group = np.sum(self.Strands.f_mag_X_turns[np.where(self.HalfTurns.HalfTurns_to_sections==i)[0], :, :],axis=0)
                    fY_group = np.sum(self.Strands.f_mag_Y_turns[np.where(self.HalfTurns.HalfTurns_to_sections==i)[0], :, :],axis=0)
                    M_x[i-1, :, :], M_y[i-1, :, :] = self.calculate_IFCC(T=T, fMag_X=fX_group, fMag_Y=fY_group,flag_coupling=True, flag_save=False)
                M_x_ED_IFCC, M_y_ED_IFCC = self.__group_components_M(frequency, M_x, M_y, skip_off_diagonal = True)
                self.Mutual_dict['M_IFCC_ED_x'] = M_x_ED_IFCC
                self.Mutual_dict['M_IFCC_ED_y'] = M_y_ED_IFCC
                print(f'IFCC-ED coupling took {np.round(time.time() - start_IFCC_ED,2)} s.')
            print(f'#- IFCC took {np.round(time.time() - start_IFCC, 4)} s')

        # Eddy currents in the copper sheath
        if self.Options.flag_ED:
            print(f'# Calculating ED parameter.')
            start_ED = time.time()
            M_x = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_Strands)).astype(complex)
            M_y = np.zeros((self.General.num_HalfTurns, len(self.frequency), self.General.num_Strands)).astype(complex)
            for i in range(self.General.num_HalfTurns):
                if i < self.General.num_HalfTurns - 1:
                    flag_save = False
                else:
                    flag_save = True
                M_x[i, :, :], M_y[i, :, :] = self.calculate_ED(T=T, fMag_X=self.Strands.f_mag_X_turns[i, :, :], fMag_Y=self.Strands.f_mag_Y_turns[i, :, :], flag_coupling=False, flag_save=flag_save)
            print(f'- Parameter estimation took {np.round(time.time() - start_ED, 2)} s, Avg. loop-time {np.round((time.time() - start_ED) / self.General.num_HalfTurns, 4)} s.')
            self.ED.M_x, self.ED.M_y = self.__group_components_M(frequency, M_x, M_y)
            self.ED.M_x, self.ED.M_y = self.__adjust_M_for_short(self.ED.M_x, self.ED.M_y, flag_component=False)
            start_eqLoop = time.time()
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'ED', self.domain,
                                                          self.frequency, self.ED.L, self.ED.R, self.ED.M_x, self.ED.M_y,
                                                          groups=groups, force_new_name=self.General.lib_path)
            print(f'Setting library took {np.round(time.time() - start_eqLoop,2)} s.')
            if self.Options.flag_ISCC:  # calculates coupling between IFCC and ISCC
                print(f'## Calculate ED-ISCC coupling.')
                start_ED_ISCC = time.time()
                M_x = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                M_y = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                for i in range(1, self.General.sections + 1):
                    fX_group = np.sum(self.ISCC.f_mag_X_ISCCreturn[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :],axis=0)
                    fY_group = np.sum(self.ISCC.f_mag_Y_ISCCreturn[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :],axis=0)
                    M_x[i-1, :, :], M_y[i-1, :, :] = self.calculate_ED(T=T, fMag_X=fX_group, fMag_Y=fY_group,flag_coupling=False, flag_save=False)
                M_x_ISCC_ED, M_y_ISCC_ED = self.__group_components_M(frequency, M_x, M_y, skip_off_diagonal = True)
                self.Mutual_dict['M_ED_ISCC_x'] = M_x_ISCC_ED
                self.Mutual_dict['M_ED_ISCC_y'] = M_y_ISCC_ED
                print(f'ED-ISCC coupling took {np.round(time.time() - start_ED_ISCC, 2)} s.')

            print(f'#- ED took {np.round(time.time() - start_ED, 4)} s')

        # Eddy currents in the Wedge
        if self.Options.flag_Wedge:
            print(f'# Calculating Wedge parameter.')
            start_Wedge = time.time()
            self.calculate_Wedge(T=T)
            self.Wedge.M = self.__adjust_M_for_sections(self.Wedge.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'Wedge', self.domain,
                                                            self.frequency, self.Wedge.L, self.Wedge.R, self.Wedge.M, np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_Wedge, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate Wedge-CL coupling.')
                start_Coupling_Wedge = time.time()
                # Calculates coupling between Wedge and the conductor Losses effects
                M_W = self.__calculate_Coupling_Components(Effect='Wedge')
                self.Mutual_dict.update(M_W)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_Wedge, 2)} s')
            print(f'#- Wedge took {np.round(time.time() - start_Wedge, 4)} s')

        # Eddy currents in the Cold Bore
        if self.Options.flag_CB:
            print(f'# Calculating CB parameter.')
            start_CB = time.time()
            self.calculate_CB(T=T)
            self.CB.M = self.__adjust_M_for_sections(self.CB.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'CB', self.domain,
                                                           self.frequency, self.CB.L, self.CB.R, self.CB.M, np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_CB, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate CB-CL coupling.')
                start_Coupling_CB = time.time()
                # Calculates coupling between CB and the conductor Losses effects
                M_CB = self.__calculate_Coupling_Components(Effect='CB')
                self.Mutual_dict.update(M_CB)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_CB, 2)} s')
            print(f'#- CB took {np.round(time.time() - start_CB, 4)} s')

        # Eddy currents in the Coil Protection Sheets
        if self.Options.flag_CPS:
            print(f'# Calculating CPS parameter.')
            start_CPS = time.time()
            self.calculate_CPS()
            self.CPS.M = self.__adjust_M_for_sections(self.CPS.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'CPS', self.domain, 
                                                           self.frequency,  self.CPS.L, self.CPS.R, self.CPS.M, np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_CPS, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate CPS-CL coupling.')
                start_Coupling_CPS = time.time()
                # Calculates coupling between CPS and the conductor Losses effects
                if isinstance(self.CPS.group_CPS, (int, float)):
                    field_int_value= self.CPS.group_CPS
                else:
                    field_int_value = self.temperature
    
                M_CPS = self.__calculate_Coupling_Components(Effect='CPS', field_int_value=field_int_value)
                self.Mutual_dict.update(M_CPS)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_CPS, 2)} s')
            print(f'#- CPS took {np.round(time.time() - start_CPS, 4)} s')

        # Eddy currents in the Aluminum ring - Not redone: Needs to be implemented
        if self.Options.flag_AlRing:
            print(f'# Calculating AlRing parameter.')
            start_AlRing = time.time()
            self.calculate_AlRing()
            self.AlRing.M = self.__adjust_M_for_sections(self.AlRing.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'AlRing', self.domain,
                                                           self.frequency, self.AlRing.L, self.AlRing.R, self.AlRing.M, np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_AlRing, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate AlRing-CL coupling.')
                start_Coupling_AlRing = time.time()
                # Calculates coupling between AlRing and the conductor Losses effects
                M_AlRing = self.__calculate_Coupling_Components(Effect='AlRing')
                self.Mutual_dict.update(M_AlRing)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_AlRing, 2)} s')
            print(f'#- AlRing took {np.round(time.time() - start_AlRing, 4)} s')

        # Eddy currents in the beam screen
        if self.Options.flag_BS:
            print(f'# Calculating BS parameter.')
            start_BS = time.time()
            self.calculate_BS()
            self.BS.M = self.__adjust_M_for_sections(self.BS.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'BS', self.domain, 
                                                          self.frequency, self.BS.L, self.BS.R, self.BS.M, np.array([]), groups=self.General.apertures,
                                                              force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_BS, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate BS-CL coupling.')
                start_Coupling_BS = time.time()
                # Calculates coupling between AlRing and the conductor Losses effects
                M_BS = self.__calculate_Coupling_Components(Effect='BS')
                self.Mutual_dict.update(M_BS)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_BS, 2)} s')
            print(f'#- BS took {np.round(time.time() - start_BS, 4)} s')

        # Calculates mutual coupling coefficients using the Mutual_dict values
        if len(self.Mutual_dict) != 0:
            self.__calculate_Mutual_Coupling(self.Mutual_dict)

        if self.Options.flag_PC and self.Options.flag_IFCC: # Changes values of M_PC_IFCC in the .lib file
            M_PC_IFCC = -1 * np.repeat(self.PC.M_PC_IFCC, np.sum(self.HalfTurns.n_strands))
            M_PC_IFCC = np.tile(M_PC_IFCC[:, np.newaxis], (1, self.General.sections)).T
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'M_PC_IFCC', frequency, self.domain, M_PC_IFCC, M_PC_IFCC)
        if self.Options.flag_PC and self.Options.flag_ED:  # calculates coupling between PC and ED
            M_PC_ED = -1 * np.repeat(self.PC.M_PC_IFCC, np.sum(self.HalfTurns.n_strands))
            M_PC_ED = np.tile(M_PC_ED[:, np.newaxis], (1, self.General.sections)).T
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'M_PC_ED', frequency, self.domain, M_PC_ED, M_PC_ED)

        if self.domain=='transient':
            self.__check_magnet_component_coupling()
        # self.__check_magnet_component_coupling()

        if self.magnet_data.magnet_Couplings is not None:
            for key, value in self.magnet_data.magnet_Couplings.__dict__.items():
                if 'M_' not in key or value is None: continue
                first_effect = key.split('_')[-2]  # Taking the name of the first effect
                second_effect = key.split('_')[-1]
                if not self._getAttribute('Options', f'flag_{first_effect}') or not self._getAttribute('Options', f'flag_{second_effect}'): continue
                if isinstance(value, np.ndarray):
                    M_value = np.repeat(value, len(frequency))
                else:
                    M_value = np.array([value] * len(frequency))
                self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, key, frequency, self.domain, M_value, np.array([]))
                self.Mutual_dict[key] = M_value

                if self.flag_debug:
                    fig_path = os.path.abspath(os.path.join(self.output_path, '..'))
                    fig_path = os.path.join(fig_path, 'plots_Debug')
                    os.makedirs(fig_path, exist_ok=True)

                    list_legend = []
                    cases = [key, f'K_{first_effect}_{second_effect}']
                    fig, ax1 = plt.subplots()
                    ax2 = ax1.twinx()
                    for case in cases:
                        if case == key:
                            ax1.semilogx(frequency, np.real(M_value), color='tab:orange', marker='*')
                            list_legend.append(f'Re({key})')
                            ax1.semilogx(frequency, np.imag(M_value), color='tab:olive', marker='s')
                            list_legend.append(f'Im({key})')
                        else:
                            L1 = self._getAttribute(first_effect, 'L')
                            L2 = self._getAttribute(second_effect, 'L')
                            k_value = M_value / np.sqrt(L1 * L2.T)
                            if len(k_value.shape)>1:
                                if k_value.shape[1]>k_value.shape[0]:
                                    k_value = k_value.T
                            ax2.semilogx(frequency, np.real(k_value), color='tab:brown', marker='*')
                            list_legend.append(f'Re({case})')
                            ax2.semilogx(frequency, np.imag(k_value), color='tab:pink', marker='s')
                            list_legend.append(f'Im({case})')
                    ax1.grid(True)
                    ax1.legend(list_legend, loc='upper left')
                    ax1.set_xlabel('Frequency [Hz]')
                    ax2.set_ylabel(f'{case} [-]')
                    ax1.set_ylabel(f'{case} [H]')
                    ax1.set_title(f'{case} plot for different groups - {self.General.magnet_name}', fontweight='bold')
                    fig_path_final = os.path.join(fig_path, f'{first_effect}_{second_effect}_plot.png')
                    plt.savefig(fig_path_final)
                    plt.close()

        # _ = self.check_inductance_matrix_losses(Mutual_dict)

        if self.flag_debug:
            fig_path = os.path.abspath(os.path.join(self.output_path, '..'))
            fig_path = os.path.join(fig_path, 'plots_Debug')
            os.makedirs(fig_path, exist_ok=True)

            for eff, value in self.effects.items():
                if value:
                    fig, axes = plt.subplots(3, 3, figsize=(26, 18))

                    attributes = ['I', 'P', 'L', 'R', 'M' , 'K']
                    y_labels = ['I [A]', 'P [W]', 'L [H]', 'R [ohm]', 'M [H]', 'k [-]']
                    ax_count = 0
                    for attr, y_label in zip(attributes, y_labels):
                        ax = axes.flatten()[ax_count]
                        ax_count += 1
                        if attr == 'R' and eff == 'PC': continue
                        if attr == 'P' and eff == 'PC': continue
                        if attr != 'K':
                            data = self._getAttribute(eff, attr)
                        else:
                            M = self._getAttribute(eff, 'M')
                            L = self._getAttribute(eff, 'L')
                            if len(M.shape)>1:
                                if M.shape == np.sqrt(L * self.General.L_mag / 2).shape:
                                    data = M / np.sqrt(L * self.General.L_mag / 2)
                                else:
                                    try:
                                        data = M.T / np.sqrt(L * self.General.L_mag / 2)
                                    except:
                                        pass
                            else:
                                data = M / np.sqrt(L * self.General.L_mag / 2)
                        lns = []
                        if len(data.shape)==1:
                            data = data[:,np.newaxis].T
                        if data.shape[0] != len(frequency):
                            data = data.T
                        for i in range(data.shape[1]):
                            if attr == 'M' or attr=='K':
                                lns1 = ax.semilogx(frequency, np.real(data[:, i]), marker='*', label=f'Group {i + 1}, Re({attr})')
                                lns2 =  ax.semilogx(frequency, np.imag(data[:, i]), marker='s', label=f'Group {i + 1}, Im({attr})')
                                lns = lns + lns1 + lns2
                            else:
                                lns += ax.semilogx(frequency, data[:, i], marker='*', label=f'Group {i+1}')
                        ax.grid(True)
                        labs = [l.get_label() for l in lns]
                        ax.legend(lns, labs, loc=0)
                        ax.set_xlabel('Frequency [Hz]')
                        ax.set_ylabel(y_label)
                    plt.title(f'{eff} plot - {self.General.magnet_name}', fontweight='bold')
                    fig_path_final = os.path.join(fig_path, f'{eff}_plot.png')
                    plt.savefig(fig_path_final)
                    plt.close()

        return

    def change_coupling_parameter_from_existing(self):
        '''
        Main function of TFM_model. It changes the equivalent coupling loop parameters for the corresponding magnet using all the other functions.
        '''

        frequency = self.frequency
        groups = self.General.sections
        T = self.temperature
        f_mag_Roxie = self.Strands.f_mag_Roxie

        # Inter-Strands Coupling Currents
        if self.Options.flag_ISCC:
            self.ISCC.M, _ = self.__adjust_M_for_short(self.ISCC.M, np.array([]), flag_component=False)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'ISCC', self.domain,
                                                          self.frequency, self.ISCC.L, self.ISCC.R, self.ISCC.M,
                                                          np.array([]), groups=groups, force_new_name=self.General.lib_path)

        # Persistent currents and magnetization
        if self.Options.flag_PC:
            self.PC.M_x, self.PC.M_y = self.__adjust_M_for_short(self.PC.M_x, self.PC.M_y, flag_component=False)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'PC', self.domain,
                                                          self.frequency, self.PC.L, np.array([]), self.PC.M_x,
                                                          self.PC.M_y, groups=groups, force_new_name=self.General.lib_path)

        # Inter-Filament Coupling Currents
        if self.Options.flag_IFCC:
            self.IFCC.M_x, self.IFCC.M_y = self.__adjust_M_for_short(self.IFCC.M_x, self.IFCC.M_y, flag_component=False)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'IFCC', self.domain,
                                                          self.frequency, self.IFCC.L, self.IFCC.R, self.IFCC.M_x,
                                                          self.IFCC.M_y, groups=groups, force_new_name=self.General.lib_path)

        # Eddy currents in the copper sheath
        if self.Options.flag_ED:
            self.ED.M_x, self.ED.M_y = self.__adjust_M_for_short(self.ED.M_x, self.ED.M_y, flag_component=False)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'ED', self.domain,
                                                          self.frequency, self.ED.L, self.ED.R, self.ED.M_x,
                                                          self.ED.M_y, groups=groups, force_new_name=self.General.lib_path)

        # Eddy currents in the Wedge
        if self.Options.flag_Wedge:
            # self.Wedge.M = self.__adjust_M_for_sections(self.Wedge.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'Wedge', self.domain,
                                                          self.frequency, self.Wedge.L, self.Wedge.R, self.Wedge.M,
                                                          np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)

        # Eddy currents in the Cold Bore
        if self.Options.flag_CB:
            # self.CB.M = self.__adjust_M_for_sections(self.CB.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'CB', self.domain,
                                                          self.frequency, self.CB.L, self.CB.R, self.CB.M, np.array([]),
                                                          groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)

        # Eddy currents in the Coil Protection Sheets
        if self.Options.flag_CPS:
            print(f'# Calculating CPS parameter.')
            start_CPS = time.time()
            self.calculate_CPS()
            self.CPS.M = self.__adjust_M_for_sections(self.CPS.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'CPS', self.domain,
                                                          self.frequency, self.CPS.L, self.CPS.R, self.CPS.M,
                                                          np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_CPS, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate CPS-CL coupling.')
                start_Coupling_CPS = time.time()
                # Calculates coupling between CPS and the conductor Losses effects
                if isinstance(self.CPS.group_CPS, (int, float)):
                    field_int_value = self.CPS.group_CPS
                else:
                    field_int_value = self.temperature

                M_CPS = self.__calculate_Coupling_Components(Effect='CPS', field_int_value=field_int_value)
                self.Mutual_dict.update(M_CPS)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_CPS, 2)} s')
            print(f'#- CPS took {np.round(time.time() - start_CPS, 4)} s')

        # Eddy currents in the Aluminum ring - Not redone: Needs to be implemented
        if self.Options.flag_AlRing:
            # self.AlRing.M = self.__adjust_M_for_sections(self.AlRing.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'AlRing', self.domain,
                                                          self.frequency, self.AlRing.L, self.AlRing.R, self.AlRing.M,
                                                          np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)

        # Eddy currents in the beam screen
        if self.Options.flag_BS:
            print(f'# Calculating BS parameter.')
            start_BS = time.time()
            self.calculate_BS()
            self.BS.M = self.__adjust_M_for_sections(self.BS.M, sum_type='aperture')
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, 'BS', self.domain,
                                                          self.frequency, self.BS.L, self.BS.R, self.BS.M, np.array([]),
                                                          groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)
            print(f'- Parameter estimation took {np.round(time.time() - start_BS, 2)} s')
            if any(item in self.effects for item in self.effs_cond):
                print(f'## Calculate BS-CL coupling.')
                start_Coupling_BS = time.time()
                # Calculates coupling between AlRing and the conductor Losses effects
                M_BS = self.__calculate_Coupling_Components(Effect='BS')
                self.Mutual_dict.update(M_BS)
                print(f'Coupling took: {np.round(time.time() - start_Coupling_BS, 2)} s')
            print(f'#- BS took {np.round(time.time() - start_BS, 4)} s')

        # Calculates mutual coupling coefficients using the Mutual_dict values
        if len(self.Mutual_dict) != 0:
            self.__calculate_Mutual_Coupling(self.Mutual_dict)

        if self.Options.flag_PC and self.Options.flag_IFCC:  # Changes values of M_PC_IFCC in the .lib file
            M_PC_IFCC = -1 * np.repeat(self.PC.M_PC_IFCC, np.sum(self.HalfTurns.n_strands))
            M_PC_IFCC = np.tile(M_PC_IFCC[:, np.newaxis], (1, self.General.sections)).T
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'M_PC_IFCC', frequency,
                                                                  self.domain, M_PC_IFCC, M_PC_IFCC)
        if self.Options.flag_PC and self.Options.flag_ED:  # calculates coupling between PC and ED
            M_PC_ED = -1 * np.repeat(self.PC.M_PC_IFCC, np.sum(self.HalfTurns.n_strands))
            M_PC_ED = np.tile(M_PC_ED[:, np.newaxis], (1, self.General.sections)).T
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'M_PC_ED', frequency,
                                                                  self.domain, M_PC_ED, M_PC_ED)

        if self.domain == 'transient':
            self.__check_magnet_component_coupling()

        if self.magnet_data.magnet_Couplings is not None:
            for key, value in self.magnet_data.magnet_Couplings.__dict__.items():
                if 'M_' not in key or value is None: continue
                first_effect = key.split('_')[-2]  # Taking the name of the first effect
                second_effect = key.split('_')[-1]
                if not self._getAttribute('Options', f'flag_{first_effect}') or not self._getAttribute('Options',
                                                                                                         f'flag_{second_effect}'): continue
                if isinstance(value, np.ndarray):
                    M_value = np.repeat(value, len(frequency))
                else:
                    M_value = np.array([value] * len(frequency))
                self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, key, frequency,
                                                                      self.domain, M_value, np.array([]))
                self.Mutual_dict[key] = M_value
        return

    def call_from_existing(self, magnet_data = None, circuit_data = None, output_path = None):
        '''

        '''
        self.magnet_data = magnet_data
        self.magnet_circuit_name = magnet_data.circuit_name
        self.__set_magnetData(magnet_data)
        self.__assignTurnsToSections()
        self.__translateModelDataToTFMGeneral()
        self.__translateModelDataToTFMHalfTurns()
        self.__translateModelDataToTFMStrands()
        self.__setOptions()
        library_name = circuit_data.Netlist[self.magnet_circuit_name].value
        self._generate_library(output_path=output_path, library_name=library_name, verbose=self.verbose)
        if self.effects:
            self.change_coupling_parameter_from_existing()

    ####################################################################################################################
    ############################################### MUTUAL COUPLING CALCULATION #########################################
    def __adjust_M_for_sections(self, M_total: np.ndarray, sum_type: str = 'aperture'):
        '''
        Helper function that splits the mutual inductance of a component into its respective section

        :param M_total : it contains the total mutual coupling associated with an effect
        :param sum_type: can either be 'aperture' or 'full' and indicates how to split the mutual coupling
        '''
        if not sum_type.lower() in ['aperture','full']:
            raise Exception(f'Do not understand how to split the mutual coupling. Available: aperture, full')

        sections_to_aperture = self.General.sections_to_aperture
        sections = len(sections_to_aperture)

        if M_total.shape[1]<sections:
            M_total = np.repeat(M_total,self.General.apertures, axis=1)

        M_adj = np.zeros((M_total.shape[0], sections)).astype(np.complex_)

        L_ap = np.zeros((self.General.apertures,))
        for ap in range(1,self.General.apertures+1):
            L_ap[ap-1] = np.sum(self.General.inductance_to_sections[np.where(sections_to_aperture==ap)[0]])

        fL_sections = np.zeros((sections, ))
        for n in range(1,sections+1):
            ap = sections_to_aperture[n-1]
            fL_section = np.sum(self.General.inductance_to_sections[n-1])/(L_ap[ap-1])
            fL_sections[n-1] = fL_section
            M_adj[:, n-1] = M_total[:, ap-1]*fL_section

        if self.Shorts.sections_to_short:
            M_adj, _ = self.__adjust_M_for_short(M_adj, np.array([0]), flag_component=True)

        return M_adj.T


    def __adjust_M_for_short(self, M_adj_x: np.ndarray, M_adj_y: np.ndarray, flag_component: bool = False, flag_1D: bool = False):
        '''
            Helper function that adjusts the mutual inductance of a component by taking into account the presence of shorts.

            :param M_adj : array that contains the mutual coupling to be adjusted
            :param flag_component: if not the approach used is the one with V across coil
        '''
        # return M_adj_x, M_adj_y
        # # #
        if self.Shorts.sections_to_short:
            R_short = self.Shorts.short_resistances[0]
            sections = np.array(self.Shorts.sections_to_short[0].split('-')).astype(int)
            # ap_w_short = np.unique(self.General.sections_to_aperture[sections - 1])
            # sections_not_shorted = np.where(self.General.sections_to_aperture == ap_w_short)[0]+1
            # mask = ~np.isin(sections_not_shorted, sections)
            # sections_not_shorted = sections_not_shorted[mask]

            s = 1j*(2*np.pi*self.frequency)
            mask = np.ones(self.General.inductance_to_sections.shape[1], dtype=bool)
            mask[sections-1] = False

            MM = self.General.inductance_to_sections[sections-1][:,sections-1]
            total_sum = np.sum(MM)
            diagonal_sum = np.trace(MM)
            f_short = R_short/(s*diagonal_sum+R_short)

            ###############################
            ## Approach with V across coil
            if not flag_component:
                for z in range(len(f_short)):
                    for i in sections-1:
                        M_adj_x[i, i, z] *= 1 #f_short[z]
                        # M_adj_x[i, :, z] *= f_short[z]
                        # M_adj_x[:, i, z] *= f_short[z]
                if M_adj_y.size:
                    for z in range(len(f_short)):
                        for i in sections-1:
                            M_adj_y[i, i, z] *= 1 #f_short[z]
                            # M_adj_y[i, :, z] *= f_short[z]
                            # M_adj_y[:, i, z] *= f_short[z]
            else:
                for z in range(len(f_short)):
                    for i in sections - 1:
                        M_adj_x[z, i] *= f_short[z]

        return M_adj_x, M_adj_y


    def __calculate_Mutual_Coupling(self, Mutual_dict: dict):
        '''
        This function calculates the Mutual Coupling coefficients between two different effects and inserts this value
        in the corresponding .FUNC of the lib file

        : param Mutual_dict: dictionary containing all the Mutual Coupling values between the effects
        '''
        frequency = self.frequency
        w = 2*np.pi*frequency
        groups = self.General.sections
        sections_to_aperture = self.General.sections_to_aperture
        
        for key, value in Mutual_dict.items(): # example of key = M_IFCC_ISCC
            if key.startswith('I'): continue
            first_effect = key.split('_')[1] # Taking the name of the first effect
            second_effect = key.split('_')[2]  # Taking the name of the second effect
            # if second_effect in self.effs_notCond: continue
            if first_effect in self.effs_components and second_effect in self.effs_components:
                continue

            if first_effect == 'ISCC':
                sort_on = 'halfturns'
            else:
                sort_on = 'strands'
            if first_effect in self.effs_noDir:
                M_first_uncoupled = self._getAttribute(first_effect,f'M')  # Taking the value of M not coupled corresponding to the first effect and saved in the dataclass
                M_first_coupled = Mutual_dict[f'M_{first_effect}_{second_effect}_x']

                M_diag_coupled = np.diagonal(M_first_coupled, axis1=0, axis2=1)
                M_diag_uncoupled = np.diagonal(M_first_uncoupled, axis1=0, axis2=1)
                M_effects_x = np.multiply(1 / (1j * w[:, np.newaxis] * M_diag_coupled),(M_diag_uncoupled ** 2 - M_diag_coupled ** 2)).T
                M_effects_y = np.array([])
            else: 
                M_first_uncoupled_x = self._getAttribute(first_effect, f'M_x') # Taking the value of M not coupled corresponding to the first effect and saved in the dataclass
                M_first_uncoupled_y = self._getAttribute(first_effect,f'M_y')  # Taking the value of M not coupled corresponding to the first effect and saved in the dataclass
                M_first_coupled_x = Mutual_dict[f'M_{first_effect}_{second_effect}_x']
                M_first_coupled_y = Mutual_dict[f'M_{first_effect}_{second_effect}_y']

                M_diag_coupled_x = np.diagonal(M_first_coupled_x, axis1=0, axis2=1)
                M_diag_uncoupled_x = np.diagonal(M_first_uncoupled_x, axis1=0, axis2=1)
                M_effects_x = np.multiply(1 / (1j * w[:,np.newaxis]  * M_diag_coupled_x),(M_diag_uncoupled_x**2-M_diag_coupled_x**2)).T
                M_diag_coupled_y = np.diagonal(M_first_coupled_y, axis1=0, axis2=1)
                M_diag_uncoupled_y = np.diagonal(M_first_uncoupled_y, axis1=0, axis2=1)
                M_effects_y = np.multiply(1 / (1j * w[:,np.newaxis] * M_diag_coupled_y), (M_diag_uncoupled_y ** 2 - M_diag_coupled_y ** 2)).T

            # if first_effect=='PC' or second_effect=='PC':
            #     M_effects_x = -1*M_effects_x
            #     M_effects_y = -1 * M_effects_y
            self.General.lib_path = change_library_MutualCoupling(self.General.lib_path, f'M_{first_effect}_{second_effect}', frequency, self.domain, M_effects_x, M_effects_y)
        return


    def __calculate_Coupling_Components(self, Effect: str, field_int_value: float = None) -> dict:
        '''
        This function calculates the Mutual Coupling values between the conductor losses and the given Effect

        :param Effect: str that indicates the corresponding Not Conductor Loss effect -> Wedge or CB

        :return M_dict: dictionary with the name of the Mutual coupling and the values
        '''
        M_dict = {}

        # Retrieve f_mag, f_mag_X and f_mag_Y from the Comsol field files specific for each effect
        f_X_diff, f_Y_diff = self.__read_COMSOL_field_file(Effect, field_int_value= field_int_value)
        frequency = self.frequency
        T = self.temperature

        effs = self.effects
        effs_NotCond = self.effs_notCond   # Taking only the effects not corresponding to the conductor losses
        for eff, value in effs.items():
            if eff in effs_NotCond: continue
            if value == True:  # If the flag of an effect is set takes the name of the effect
                if eff == 'ISCC':
                    M_x = np.zeros((self.General.sections, len(self.frequency), self.General.num_HalfTurns)).astype(complex)
                    M_y = np.zeros((self.General.sections, len(self.frequency), self.General.num_HalfTurns)).astype(complex)
                    sort_on = 'halfturns'
                else:
                    M_x = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                    M_y = np.zeros((self.General.sections, len(self.frequency), self.General.num_Strands)).astype(complex)
                    sort_on = 'strands'
                for i in range(1, self.General.sections + 1):
                    fX_group = np.sum( self.Strands.f_mag_X_turns[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :], axis=0) + f_X_diff
                    fY_group = np.sum( self.Strands.f_mag_X_turns[np.where(self.HalfTurns.HalfTurns_to_sections == i)[0], :, :], axis=0) + f_Y_diff
                    M_x[i - 1, :, :], M_y[i - 1, :, :] = getattr(self, f'calculate_{eff}')(T=T, fMag_X=fX_group, fMag_Y=fY_group, flag_save=False, flag_coupling=False)
                M_x, M_y = self.__group_components_M(frequency, M_x, M_y, skip_off_diagonal=True, sort_on=sort_on)

                M_dict[f'M_{eff}_{Effect}_x'] = M_x # Save the new M in the dictionary
                M_dict[f'M_{eff}_{Effect}_y'] = M_x  # Save the new M in the dictionary

        return M_dict


    ####################################################################################################################
    ############################################ FUNCTION TO CALCULATE THE GROUPING #####################################
    def __group_components_LR(self, frequency: np.ndarray, L: np.ndarray, R: np.ndarray, sort_on: str = 'strands') -> np.ndarray:
        '''
        Helper function that groups components into n groups, based on sorting on a specific variable out of R, L

        :param frequency: frequency vector
        :param L: L-vector
        :param R: R-vector
        :param sort_on: Which variable to sort on
        :return: 2 np.ndarray in the order: L, R that are grouped into n_groups
        '''

        # Validate sort option
        avail_sort = ['strands', 'halfturns']
        sort_on = sort_on.lower()
        if sort_on not in avail_sort:
            raise ValueError(f"Invalid sort_on value. Available options: {avail_sort}")

        # Determine grouping variable
        groups = self.General.sections
        x = self.Strands.strands_to_sections if sort_on == 'strands' else self.HalfTurns.HalfTurns_to_sections

        # Initialize arrays
        n_freq = len(frequency)
        R_group = np.zeros((n_freq, groups), dtype=float)
        L_group = np.zeros((n_freq, groups), dtype=float)

        if R is None:
            R = np.zeros(L.shape)

        # Convert NaNs in R and L to zero only once
        R = np.nan_to_num(R, copy=False)
        L = np.nan_to_num(L, copy=False)

        # Group indices by section in a dictionary for fast lookup
        group_indices = {i: np.where(x == i)[0] for i in range(1, groups + 1)}

        # Vectorize averaging within each group
        for i, indices in group_indices.items():
            if len(indices) > 0:
                # Validate the correct shape
                if len(L.shape) == 1:
                    L_slice = L[indices][np.newaxis,:]
                else:
                    L_slice = L[:, indices]
                R_group[:, i - 1] = R[:, indices].mean(axis=1)
                L_group[:, i - 1] = L_slice.mean(axis=1)

        # Remove any rows where all values are zero
        R_group = R_group[~np.all(R_group == 0, axis=1)]
        L_group = L_group[~np.all(L_group == 0, axis=1)]

        return L_group, R_group


    def __group_components_M(self, frequency: np.ndarray, M_x: np.ndarray, M_y: np.ndarray,
                             I_x: np.ndarray = np.array([]), I_y: np.ndarray = np.array([]), sort_on: str = 'strands', skip_off_diagonal: bool = False) -> np.ndarray:
        '''
        Helper function that groups M components into n groups

        :param frequency: frequency vector
        :param M: M-vector
        :return: 3 np.ndarray in the order: M, I that are grouped into n_groups
        '''

        groups = self.General.sections
        f = frequency
        n_couplings = groups ** 2

        if not M_y.size:
            M_y = np.ones(M_x.shape)

        # Calculate the mutual couplings of each section with their respective coupling loop
        M_couplings_x = np.zeros((groups, groups, len(frequency)), dtype=np.complex_)
        M_couplings_y = np.zeros((groups, groups, len(frequency)), dtype=np.complex_)

        start = time.time()
        M_couplings_x, M_couplings_y = group_mutual_coupling_diagonal(groups, M_x, M_y, M_couplings_x, M_couplings_y, self.HalfTurns.HalfTurns_to_sections, self.Strands.strands_to_sections, sort_on=sort_on)
        print(f'Diagonal mutual couplings took: {np.round(time.time()-start,2)} s')

        if not skip_off_diagonal:
            # Calculate the mutual couplings of each section with the coupling loops of all other sections
            start = time.time()
            M_couplings_x, M_couplings_y = group_mutual_coupling_offdiagonal(groups, M_x, M_y, M_couplings_x, M_couplings_y, self.HalfTurns.HalfTurns_to_sections, self.Strands.strands_to_sections, sort_on=sort_on)
            M_couplings_x_full = np.zeros(M_couplings_x.shape, dtype=complex)
            M_couplings_y_full = np.zeros(M_couplings_y.shape, dtype=complex)
            for i in range(len(f)):
                M_couplings_x_full[:,:,i] = M_couplings_x[:,:,i] + M_couplings_x[:,:,i].T - np.diag(M_couplings_x[:,:,i].diagonal())
                M_couplings_y_full[:,:,i] = M_couplings_y[:,:,i] + M_couplings_y[:,:,i].T - np.diag(M_couplings_y[:,:,i].diagonal())
            print(f'Off-Diagonal mutual couplings took: {np.round(time.time()-start,2)} s')
        else:
            M_couplings_x_full = M_couplings_x
            M_couplings_y_full = M_couplings_y

        return M_couplings_x_full, M_couplings_y_full


    def __group_mutual_coupling(self, M: np.ndarray) -> np.ndarray:
        '''
        Helper function that groups components into n groups, based on a sorting on a specific variable out of R,L,M

        :param M: M_vector

        :return: 1 np.ndarray: M that are grouped into n_groups
        '''
        frequency = self.frequency
        groups = self.General.sections
        M_group = np.zeros((len(frequency), ), dtype=np.complex_)
        M_group_t = np.zeros((len(frequency),), dtype=np.complex_)
        x = self.Strands.strands_to_sections

        # Loop through the frequencies
        for j in range(len(frequency)):
            M_temp = np.nan_to_num(M[j, :]).astype(complex)
            if len(M_temp) > 0:
                # M_sel = np.sum(M_temp ** 2)
                # s_r_temp = np.sign(np.real(M_sel))
                # s_i_temp = np.sign(np.imag(M_sel))
                # M_group_t[j] = s_r_temp * np.real(np.sqrt(M_sel)) + 1j * s_i_temp * np.imag(np.sqrt(M_sel))
                M_group[j] = np.sqrt(np.sum(M_temp ** 2))
        M_group = check_smoothness(frequency, np.real(M_group))+1j*check_smoothness(frequency, np.imag(M_group))

        return M_group


    ####################################################################################################################
    ############################################ FUNCTIONS FOR L MATRX CHECKING #####################################
    def check_inductance_matrix_losses(self, Mutual_dict: dict):
        '''
        This function constructs the L Matrix containing all the effects that are selected.
        This function has in the diagonal all the L corresponding to a given effect
        On the first column and on the first row at the index corresponding to that effect it has the M of that effect
        In the crossing betwwen indices of different effects, it has the mutual coupling between these two.
        In all the other places it has 0

        :param Mutual_dict: dictionary with the Mutual coupling between all the different effects
        '''
        frequency = self.frequency
        groups = self.General.sections
        effs = list(self.effects.keys())

        effects = np.repeat(np.array(effs), groups)
        effects = np.insert(effects, 0, 'Mag').astype(str)
        L_matrix_list = []

        for freq in range(len(frequency)):
            # Creating the matrix and filling it with 0
            L_matrix = np.zeros((len(effects), len(effects))).astype(complex)
            for eff in range(len(effects)):
                if eff == 0:  # Checking if the Effect[eff] == 'Mag'
                    L_matrix[0, 0] = self.General.L_mag
                elif effects[eff]!='Mag' and self.effects[effects[eff]]:
                    if effects[eff-1] == effects[eff]: # Checking if it's not the first time that we encounter this effect in the dict
                        count_group += 1  # If it's not the first time, the group counting must be incremented
                    else:
                        count_group = 0  # If it is the first time, the group counting is set to zero

                    # Filling the matrix with the L values along the diagonal and the M values symmetrically
                    # on the first row and on the first column, selecting the right values according to count_group
                    if effects[eff] in self.effs_notCond and effects[eff] != 'BS':
                        A = self._getAttribute(effects[eff], 'M')
                        B = self._getAttribute(effects[eff], 'L')
                        L_matrix[0, eff] = self._getAttribute(effects[eff], 'M')[0,freq]
                        L_matrix[eff, 0] = self._getAttribute(effects[eff], 'M')[0,freq]
                        L_matrix[eff, eff] = self._getAttribute(effects[eff], 'L')[freq,0]
                    else:
                        A = self._getAttribute(effects[eff], 'M')
                        B = self._getAttribute(effects[eff], 'L')
                        L_matrix[0, eff] = self._getAttribute(effects[eff], 'M')[count_group, freq]
                        L_matrix[eff, 0] = self._getAttribute(effects[eff], 'M')[count_group, freq]
                        L_matrix[eff, eff] = self._getAttribute(effects[eff], 'L')[freq, count_group]

                    for key, value in Mutual_dict.items():
                        if effects[eff] in key:  # For each key of the dict, check if the current effect is contained in it
                            for l in range(len(effects)):  # If yes, find the other effect contained in the same key
                                if l != 0 and eff != l and effects[l] in key:
                                    if effects[l - 1] != effects[l] and not effects[eff] == effects[l]:
                                        # Take the first effect with that name and then select the right column index
                                        # and the right value by selecting the same count_group of the effects[eff] element
                                        if len(value.shape)>1:
                                            L_matrix[eff, l +count_group ] = value[freq, count_group]
                                            L_matrix[l +count_group , eff] = value[freq, count_group]
                                        else:
                                            L_matrix[eff, l +count_group] = value[freq]
                                            L_matrix[l+count_group, eff] = value[freq]
                else: 
                    continue
            L_matrix_list.append(L_matrix)

        for i in range(len(L_matrix_list)):
            if not is_positive_definite(L_matrix_list[i]):
                # raise Exception(f'Matrix not positive definite for frequency {frequency[i]}')
                print(f'Matrix not positive definite for frequency {frequency[i]}')
        return 1


    def __create_coupling_matrix(self, magnet_couplings):
        '''

        '''
        components = [item for item in self.effs_components if item in self.effects]
        n_components = len(components)
        n_groups = self.General.sections
        M_matrix = np.zeros((n_groups + n_components, n_groups + n_components), dtype=np.complex128)
        M_matrix[:n_groups, :n_groups] = self.General.inductance_to_sections

        M_mask = np.zeros((n_groups + n_components, n_groups + n_components), dtype=np.complex128)

        for i in range(n_groups):
            for c in range(len(components)):
                idx_comp = n_groups + c
                M = self._getAttribute(components[c], 'M')[i, 0]
                M_matrix[i, idx_comp] = M
                M_matrix[idx_comp, i] = M
                L = self._getAttribute(components[c], 'L')[i, 0]
                M_matrix[idx_comp, idx_comp] = L

        for c in range(len(components)):
            for q in range(len(components)):
                if q == c:
                    continue
                if f'M_{components[c]}_{components[q]}' in list(magnet_couplings.keys()):
                    if magnet_couplings[f'M_{components[c]}_{components[q]}'] != None:
                        x = 1
                        M_matrix[c + n_groups, q + n_groups] = magnet_couplings[f'M_{components[c]}_{components[q]}']
                        M_matrix[q + n_groups, c + n_groups] = magnet_couplings[f'M_{components[c]}_{components[q]}']
                        M_mask[c + n_groups, q + n_groups] = 1
                        M_mask[q + n_groups, c + n_groups] = 1
        return M_matrix, M_mask


    def __find_positive_definite_matrix(self, M_mask, M_matrix, limit: int = 10000):
        '''

        '''
        c = 0
        flag_error = 0
        flag_adjust_L = 0
        while not is_positive_definite(M_matrix):
            w, v = np.linalg.eig(M_matrix)
            # Step 1
            eig_vals = np.linalg.eigvals(M_matrix)
            s = np.sum(eig_vals) * 2
            t = (s) ** 2 * 100 + 1

            # Step 2
            eig_val_s = np.min(eig_vals[eig_vals > 0])
            eig_val_n = eig_vals[eig_vals < 0]

            eig_vals_new = eig_vals
            for n in eig_val_n:
                idx_n = np.argmin(abs(eig_vals - n))
                n_star = eig_val_s * (s - n) * (s - n) / t
                eig_vals_new[idx_n] = n_star

            # Step 3
            D = np.diag(eig_vals_new)
            M_new = np.dot(v, np.dot(D, np.linalg.inv(v)))

            M_diff = M_new - M_matrix
            M_matrix = M_matrix - M_mask * (M_matrix - M_new)
            c += 1
            if c>limit:
                if is_positive_definite(M_new):
                    components = [item for item in self.effs_components if item in self.effects]
                    if len(np.where(abs(M_diff)>1e-7))>2:
                        flag_error = 1
                    if not np.where(abs(M_diff)>1e-7)[0][0]==np.where(abs(M_diff)>1e-7)[1][0]:
                        flag_error = 1
                    if not np.where(abs(M_diff)>1e-7)[0][0]>self.General.sections-1:
                        flag_error = 1
                    c = 0
                    M_mask[np.where(abs(M_diff)>1e-7)[0][0],np.where(abs(M_diff)>1e-7)[1][0]]=1
                    flag_adjust_L = components[np.where(abs(M_diff)>1e-7)[0][0]-self.General.sections]
                    idx_comp = np.where(abs(M_diff)>1e-7)[0][0]
                else:
                    flag_error = 1
            if flag_error:
                break
        if flag_error:
            raise Exception(f'Error: No positive definite matrix found! The transient simulation will fail. c={c}')
        if flag_adjust_L:
            L_new = M_matrix[idx_comp,idx_comp]
            L_old = self._getAttribute(flag_adjust_L,'L')[0,0]
            f_new = L_new/L_old
            self._setAttribute(flag_adjust_L, 'L', self._getAttribute(flag_adjust_L,'L')*f_new)
            self.General.lib_path = change_library_EqLoop(self.General.lib_path, flag_adjust_L, self.domain,
                                                          self.frequency, self._getAttribute(flag_adjust_L,'L'), self._getAttribute(flag_adjust_L,'R'),
                                                          self._getAttribute(flag_adjust_L,'M'), np.array([]), groups=self.General.apertures,
                                                          force_new_name=self.General.lib_path)

        return M_matrix


    def __update_magnet_couplings(self, M_matrix):
        '''
        
        
        '''
        components = [item for item in self.effs_components if item in self.effects]
        n_components = len(components)
        n_groups = self.General.sections
        magnet_couplings = copy.deepcopy(self.magnet_data.magnet_Couplings.__dict__)

        for c in range(len(components)):
            for q in range(len(components)):
                if q == c:
                    continue
                if f'M_{components[c]}_{components[q]}' in list(magnet_couplings.keys()):
                    if magnet_couplings[f'M_{components[c]}_{components[q]}'] != None:
                        magnet_couplings[f'M_{components[c]}_{components[q]}'] = M_matrix[c + n_groups, q + n_groups]

        for key in list(magnet_couplings.keys()):
            if magnet_couplings[key] != None:
                e_diff = (self.magnet_data.magnet_Couplings.__dict__[key]-magnet_couplings[key])/self.magnet_data.magnet_Couplings.__dict__[key]*100
                print(f'Difference in {key} is {e_diff} %.')

        new_couplings = SimpleNamespace(**magnet_couplings)
        self.magnet_data.magnet_Couplings = new_couplings
        return


    def __check_magnet_component_coupling(self):
        '''
        '''

        if (any(item in self.effects for item in self.effs_components)):
            M_matrix, M_mask = self.__create_coupling_matrix(self.magnet_data.magnet_Couplings.__dict__)

            if not is_positive_definite(M_matrix):
                # We need to bend the couplings
                M_matrix  = self.__find_positive_definite_matrix(M_mask, M_matrix)
                self.__update_magnet_couplings(M_matrix)
                # Re-do the check
                M_matrix, M_mask = self.__create_coupling_matrix(self.magnet_data.magnet_Couplings.__dict__)
                flag_finished = is_positive_definite(M_matrix)
                if not flag_finished: raise Exception('Could not find conform matrix.')
                print('Magnet couplings are positive definite')

        return


    ########################################################################################################################
    ################################## FUNCTION TO CALCULATE TAU OF COMPONENTS  ########################################
    def __calculate_tau(self, P_tot: np.ndarray, frequency: np.ndarray, effect: str) -> int:
        '''
        Helper function to calculate the tau_index corresponding to the frequency vector for a specific effect

        :param P_tot: P vector used to calculate the tau

        :return: tau_index corresponding to the frequency vector
        '''

        def central_difference_log(x_values, f_values):
            h_forward = x_values[1:] - x_values[:-1]  # Spacing between successive points
            h_backward = x_values[1:] - x_values[:-1]

            derivative = np.zeros_like(f_values)
            # Central difference for interior points
            for i in range(1, len(x_values) - 1):
                h = (x_values[i + 1] - x_values[i - 1]) / 2
                derivative[i] = (f_values[i + 1] - f_values[i - 1]) / (2 * h)

            # Forward difference for the first point
            derivative[0] = (f_values[1] - f_values[0]) / h_forward[0]

            # Backward difference for the last point
            derivative[-1] = (f_values[-1] - f_values[-2]) / h_backward[-1]

            return derivative

        def split_consecutive(arr):
            # Initialize the list to hold subarrays and the first subarray
            result = []
            subarray = [arr[0]]
            # Iterate through the array starting from the second element
            for i in range(1, len(arr)):
                if arr[i] == arr[i - 1] + 1:
                    # If current element is consecutive, add it to the current subarray
                    subarray.append(arr[i])
                else:
                    # If current element is not consecutive, add the current subarray to result
                    result.append(subarray)
                    # Start a new subarray
                    subarray = [arr[i]]
            # Add the last subarray to the result
            result.append(subarray)

            return result

        frequencies_tau = np.logspace(np.log10(frequency[0]), np.log10(frequency[-1]), 1000)
        Pt = np.interp(frequencies_tau, frequency, P_tot)
        dPt = smooth_curve(central_difference_log(frequencies_tau, Pt), 21, n_pad=5)
        dPt2 = smooth_curve(central_difference_log(frequencies_tau, dPt), 21, n_pad=5)

        if frequencies_tau[np.argmin(dPt2)] < 10:
            min_tol = 1e-6
            tol = min(10 ** (np.round(np.log10(dPt2.max()), 0) - 3), min_tol)
        elif frequencies_tau[np.argmin(dPt2)] < 100:
            if effect == 'AlRing':
                tol = 3e-6
            elif effect == 'Wedge':
                tol = 1e-7
        else:
            min_tol = 1e-7
            tol = min(10 ** (np.round(np.log10(dPt2.max()), 0) - 2), min_tol)

        split_array = split_consecutive(np.where(abs(dPt2) < tol)[0])
        if len(split_array) == 3:
            idx_tau = split_consecutive(np.where(abs(dPt2) < tol)[0])[-2][0]
        else:
            idx_tau = split_consecutive(np.where(abs(dPt2) < tol)[0])[-1][0]
        tau = 1 / frequencies_tau[idx_tau]

        return tau


    ####################################################################################################################
    ############################################ RESISTIVITY FUNCTIONS CALCULATION #####################################
    def __rhoCu_nist(self, T: float, RRR: np.ndarray, B: np.ndarray) -> np.ndarray:
        '''
        Helper function to calculate resistivity of copper. Taken from steam-materials library

        :param T: Temperature
        :return: array of resistivities
        '''
        B = abs(B)
        T_ref_RRR = 273
        # Make T of the same size of B and RRR
        T_flatten = np.tile(T, (len(B), 1)).flatten()
        # Create numpy2d by stacking B, RRR, and T along axis 0
        numpy2d = np.vstack((T_flatten, B, RRR))
        sm_cp_rho = STEAM_materials('CFUN_rhoCu_NIST_v2', numpy2d.shape[0], numpy2d.shape[1])
        RhoCu = sm_cp_rho.evaluate(numpy2d)

        return RhoCu


    def __rhoSS_nist(self, T: float) -> np.ndarray:
        '''
        Helper function to calculate resistivity of copper. Taken from steam-materials library

        :param T: Temperature
        :return: array of resistivities
        '''
        T_flatten = np.tile(T, (1)).flatten()
        # Create numpy2d by stacking B, RRR, and T along axis 0
        sm_cp_rho = STEAM_materials('CFUN_rhoSS_v1', 1, 1)
        RhoSS = sm_cp_rho.evaluate(T_flatten)

        return RhoSS


    def __rhoAl_nist(self, T: float) -> np.ndarray:
        '''
        Helper function to calculate resistivity of copper. Taken from steam-materials library

        :param T: Temperature
        :return: array of resistivities
        '''
        T_flatten = np.tile(T, (1)).flatten()
        # Create numpy2d by stacking B, RRR, and T along axis 0
        sm_cp_rho = STEAM_materials('CFUN_rhoAl_v1', 1, 1)
        RhoAl = sm_cp_rho.evaluate(T_flatten)

        return RhoAl


    ####################################################################################################################
    ###################################### GET AND SET FUNCTIONS FOR THE ATTRIBUTES #####################################
    def _setAttribute(self, TFMclass, attribute: str, value):
        try:
            setattr(TFMclass, attribute, value)
        except:
            setattr(getattr(self, TFMclass), attribute, value)


    def _getAttribute(self, TFMclass, attribute: str):
        try:
            return getattr(TFMclass, attribute)
        except:
            try:
                return getattr(getattr(self, TFMclass), attribute)
            except:
                getattr(self, attribute)



    ####################################################################################################################
    #################################### FUNCTIONS FOR CAPACITANCE CALCULATION #########################################

    def __lookupCircuitDataToTFMCapacitances(self):
        """
           Capacitances: A class to store and manage capacitance-related parameters for a magnet system.

           Attributes:
               - s_ground_ins: Thickness of the ground insulation in the outer layer.
               - mat_ground_ins: Material of the ground insulation in the outer layer.
               - s_inter_layer_ins: Thickness of the interlayer insulation (if applicable).
               - mat_inter_layer_ins: Material of the interlayer insulation (if applicable).
               - dict_ins_materials: Dictionary mapping insulation materials to their relative permittivity values.
               - f_general: Multiplication factor applied to the capacitance to ground calculation for each half-turn
                            to match COMSOL values (optional).
               - f_edges: Similar to f_general, but applied only to the first and last half-turn of each group (optional).
               - f_area_short: Multiplication factor applied to the area used in layer-to-layer capacitance calculations (if applicable).
               - flag_TurnToTurn_C: Flag indicating whether to calculate turn-to-turn and layer-to-layer capacitances.
               - flag_comsol: Flag to determine the capacitance calculation method.
                              If False, capacitances are calculated in TFM. If True, capacitances are extracted from a
                              CSV file generated by a COMSOL Multiphysics capacitance model.
                              The files should be located in: 'local_library/magnets/magnet_name/input/TFM_input'
                              with the names:
                              - 'CapacitanceMatrix_NoQH_magnetName.csv'
                              - 'CapacitanceMatrix_QH_magnetName.csv'
                              TTFM then selects the corresponding values based on the value of `self.flag_QH` (False for NoQH, True for QH).


           This function retrieves the insulation materials from the YAML file, extracts their permittivity values from
           the dictionary within the file, and stores these values in the Capacitances class as 'eps_inter_layer_ins', 'eps_ground_ins'.
           """
        self._setAttribute(self, 'Capacitances', self.magnet_data.magnet_Capacitances)
        dict_ins_materials = self.magnet_data.magnet_Capacitances.dict_ins_materials

        HalfTurns_to_layers = self.HalfTurns.HalfTurns_to_layers
        mat_ground_ins = self.Capacitances.mat_ground_ins
        mat_inter_layer_ins = self.Capacitances.mat_inter_layer_ins

        if mat_ground_ins in dict_ins_materials.keys():
            eps_ground_ins = dict_ins_materials[f'{mat_ground_ins}']
            self._setAttribute(self.Capacitances, 'eps_ground_ins', eps_ground_ins)
        else:
            raise Exception(
                f'Permittivity of the ground material {mat_ground_ins} not present in the dict_ins_materials key, '
                f'please insert it.')
        if max(HalfTurns_to_layers) == 2:
            if mat_inter_layer_ins in dict_ins_materials.keys():
                eps_inter_layer_ins = dict_ins_materials[f'{mat_inter_layer_ins}']
                self._setAttribute(self.Capacitances, 'eps_inter_layer_ins', eps_inter_layer_ins)
            else:
                raise Exception(
                    f'Permittivity of the ground material {mat_inter_layer_ins} not present in the dict_ins_materials key, '
                    f'please insert it.')



    def __calculate_CapacitanceToGround(self):
        '''
            Code to calculate the capacitance to ground of each HalfTurn depending from its location in the magnet

            Assumptions:
                1. If there is more than one layer, the inter turn insulation goes all along the inner layer
                2. If there is more than one layer, the insulation along the width of the outer layer is doubled compared
                   to the thickness of the insulation inserted in the yaml file
                3. The LEDET thicknesses of the QH are given as lists, but we assume that each quench heater has the same
                   thickness.
        '''
        flag_QH = self.flag_QH
        # Looping through the turns and calculate the capacitance to Ground
        n_HalfTurns = self.General.num_HalfTurns
        l_mag = self.General.magnet_length
        h_bare = self.HalfTurns.bare_cable_height_mean
        w_bare = self.HalfTurns.bare_cable_width
        eps0 = 1 / (4 * np.pi * 1E-7 * 299792458 ** 2)  # Vacuum relative permittivity
        hIns = self.HalfTurns.insulation_height
        wIns = self.HalfTurns.insulation_width

        s_ground_ins_orig = self.Capacitances.s_ground_ins
        eps_ground_ins = self.Capacitances.eps_ground_ins
        s_inter_layer_ins = self.Capacitances.s_inter_layer_ins
        eps_inter_layer_ins = self.Capacitances.eps_inter_layer_ins
        f_general = self.Capacitances.f_general
        f_edges = self.Capacitances.f_edges

        if flag_QH:
            s_kapton_ins = self.ledet_inputs['s_ins_QH'] # Kapton insulation below the QH layer
            s_QH = self.ledet_inputs['h_QH'][0] # Layer of QH
            s_kapton_He_ins = self.ledet_inputs['s_ins_QH_He'][0]# Kapton insulation above the QH layer (between QH and ground insulation)
            s_kapton_strips = list(np.array(s_kapton_ins) + np.array(s_kapton_He_ins))[0] # Total layer of kapton insulation
            HalfTurns_QH = self.ledet_inputs['iQH_toHalfTurn_To'] # List containing turns covered by QH
            # HalfTurns_QH_number = self.ledet_inputs['iQH_toHalfTurn_From']  # List containing the QH number to which each turn in HalfTurns_QH correspond to

        HalfTurns_wide_ins = self.HalfTurns.HalfTurns_wide_ins
        HalfTurns_ground_ins = self.HalfTurns.HalfTurns_ground_ins
        HalfTurns_to_layers = self.HalfTurns.HalfTurns_to_layers

        # Initializing the C_matrix to a very low value of capacitance but not zero
        C_matrix = np.ones((n_HalfTurns, n_HalfTurns)) * 1e-12
        for i in range(len(HalfTurns_ground_ins)):
            HT_idx = HalfTurns_ground_ins[i] - 1
            A_narrow = l_mag * (h_bare[HT_idx] + 2 * hIns[HT_idx])
            C_outer_InOutIns = eps0 * eps_ground_ins * A_narrow / (s_ground_ins_orig)
            C_turn_InOutIns = eps0 * eps_ground_ins * A_narrow / wIns[HT_idx]
            # Add the capacitance related to the turn insulation and the inner layer in case it's needed
            C_HalfTurn = 1 / (1 / C_outer_InOutIns + 1 / C_turn_InOutIns)
            if HalfTurns_to_layers[HT_idx] == 2:
                # If the magnet has two layer and we are in the inner, then compute the capacitance related to the inner layer
                C_inter_layer_InOut = eps0 * eps_inter_layer_ins * A_narrow / (s_inter_layer_ins)
                C_HalfTurn = 1 / (1 / C_HalfTurn + 1 / C_inter_layer_InOut)
            elif HalfTurns_QH is not None and flag_QH:
                if HT_idx + 1 in HalfTurns_QH:
                    # Add a capacitance related to the Cu gap caused by the QH heater on the outer layer and one for the Kapton gap
                    C_Cu_outer_layer = eps0 * 1 * A_narrow / (s_QH)
                    C_K_outer_layer = eps0 * eps_ground_ins * A_narrow / (s_kapton_strips)
                    C_HalfTurn = 1 / (1 / C_HalfTurn + 1 / C_Cu_outer_layer + 1 / C_K_outer_layer)
                else:
                    # Add a capacitance related to the Kapton caused by the QH heater on the outer layer
                    C_K_outer_layer = eps0 * eps_ground_ins * A_narrow / (s_kapton_strips + s_QH)
                    C_HalfTurn = 1 / (1 / C_HalfTurn + 1 / C_K_outer_layer)

            # Extract all the indexes of the HalfTurns belonging to the same group as HT[i]
            group = self.HalfTurns.HalfTurns_to_groups[HT_idx]
            idx_group = np.where(self.HalfTurns.HalfTurns_to_groups == group)

            # If the turn touches the insulation also on the side, add the corresponding capacitances
            if HT_idx + 1 in HalfTurns_wide_ins:
                A_wide = l_mag * (w_bare[HT_idx] + 2 * wIns[HT_idx])
                C_turn_RadialIns = eps0 * eps_ground_ins * A_wide / hIns[HT_idx]
                # If the magnet has two layers and we are in the outer, then the insulation along the height is doubled
                s_ground_ins = 2 * s_ground_ins_orig if (HalfTurns_to_layers[HT_idx] == 1 and np.max(HalfTurns_to_layers)) == 2 else s_ground_ins_orig
                C_outer_RadialIns = eps0 * eps_ground_ins * A_wide / (s_ground_ins)
                # If the magnet has two layer and we are in the inner, then compute the capacitance related to the inner laye
                # Add the capacitance related to the turn insulation and the inner layer in case it's needed
                C_HalfTurn_long = 1 / (1 / C_outer_RadialIns + 1 / C_turn_RadialIns)
                if HalfTurns_to_layers[HT_idx] == 2:
                    C_inter_layer_Radial = eps0 * eps_inter_layer_ins * A_wide / (s_inter_layer_ins)
                    C_HalfTurn = 1 / (1 / C_HalfTurn + 1 / C_inter_layer_Radial)
                elif HalfTurns_QH is not None and flag_QH:
                    if HT_idx + 1 in HalfTurns_QH:
                        # Add a capacitance related to the Cu gap caused by the QH heater on the outer layer and one for the Kapton gap
                        C_Cu_outer_layer = eps0 * 1 * A_wide / (s_QH)
                        C_K_outer_layer = eps0 * eps_ground_ins * A_wide/ (s_kapton_strips)
                        C_HalfTurn_long = 1 / (1 / C_HalfTurn_long + 1 / C_Cu_outer_layer + 1 / C_K_outer_layer)
                    else:
                        # Add a capacitance related to the Kapton caused by the QH heater on the outer layer
                        C_K_outer_layer = eps0 * eps_ground_ins * A_wide/ (s_kapton_strips + s_QH)
                        C_HalfTurn_long = 1 / (1 / C_HalfTurn_long + 1 / C_K_outer_layer)
                C_HalfTurn_long = C_HalfTurn_long if HalfTurns_to_layers[HT_idx] == 1 else 1 / (1 / C_HalfTurn_long + 1 / C_inter_layer_Radial)
                # The final Capacitance is the // of the Capacitance related to the Radial and InOut directions
                C_HalfTurn = C_HalfTurn + C_HalfTurn_long


            C_HalfTurn = C_HalfTurn * f_general if f_general is not None else C_HalfTurn
            if f_edges is not None:
                C_HalfTurn = C_HalfTurn * f_edges if (HT_idx == np.min(idx_group) or HT_idx == np.max(idx_group) and HT_idx + 1 not in HalfTurns_wide_ins) else C_HalfTurn

            C_matrix[HT_idx, HT_idx] = C_HalfTurn

        self._setAttribute(self.HalfTurns, 'C_matrix', C_matrix)


    def __calculate_TurnToTurnCapacitance(self):
        '''
           Code to calculate the turn to turn capacitance tof each turn with the ones next to it

           Assumptions:
               1. If there is more than one layer, the inter turn insulation goes all along the inner layer
               2. The used array for the thermal connection along the height, is the one defined in the function
                  "__setDataCapacitanceCalculation"
        '''
        n_HalfTurns = self.General.num_HalfTurns
        l_mag = self.General.magnet_length
        h_bare = self.HalfTurns.bare_cable_height_mean
        w_bare = self.HalfTurns.bare_cable_width
        eps0 = 1 / (4 * np.pi * 1E-7 * 299792458 ** 2)  # Vacuum relative permittivity
        hIns = self.HalfTurns.insulation_height
        wIns = self.HalfTurns.insulation_width

        eps_ground_ins = self.Capacitances.eps_ground_ins
        s_inter_layer_ins = self.Capacitances.s_inter_layer_ins
        eps_inter_layer_ins = self.Capacitances.eps_inter_layer_ins
        HalfTurns_to_layers = self.HalfTurns.HalfTurns_to_layers

        C_cont_width_start = self.ledet_inputs['iContactAlongWidth_From']
        C_cont_width_stop = self.ledet_inputs['iContactAlongWidth_To']
        if np.max(HalfTurns_to_layers == 2):
            C_cont_height_start = self.C_cont_height_start
            C_cont_height_stop = self.C_cont_height_stop
        else:
            C_cont_height_start = self.ledet_inputs['iContactAlongHeight_From']
            C_cont_height_stop = self.ledet_inputs['iContactAlongHeight_To']

        C_matrix = self.HalfTurns.C_matrix if self.HalfTurns.C_matrix is not None and np.any(self.HalfTurns.C_matrix) else np.zeros((n_HalfTurns, n_HalfTurns))
        f_area_short = self.Capacitances.f_area_short if  self.Capacitances.f_area_short else 1

        ### Calculating Turn to Turn Capacitances
        for i in range(len(C_cont_width_start)):
            # Mutual capacitance using area of the first turn
            idx_start = C_cont_width_start[i] - 1
            idx_stop = C_cont_width_stop[i] - 1
            A_wide = l_mag * (w_bare[idx_start] + 2 * wIns[idx_start])
            C_turn_RadialIns = eps0 * eps_ground_ins * A_wide / (hIns[idx_start] + hIns[idx_stop])
            C_matrix[idx_stop, idx_start] = C_turn_RadialIns

            # Mutual capacitance using area of the first turn
            A_wide = l_mag * (w_bare[idx_stop] + 2 * wIns[idx_stop])
            C_turn_RadialIns = eps0 * eps_ground_ins * A_wide / (hIns[idx_start] + hIns[idx_stop])
            C_matrix[idx_start, idx_stop] = C_turn_RadialIns

        ### Calculating layer to layer capacitance
        for i in range(len(C_cont_height_start)):
            if C_cont_height_start[i] == C_cont_height_stop[i]: continue
            # Mutual capacitance using area of the first turn
            idx_start = C_cont_height_start[i] - 1
            idx_stop = C_cont_height_stop[i] - 1
            # Check which area is the smallest one and use that
            A_short_start = l_mag * (h_bare[idx_start] + 2 * hIns[idx_start])
            A_short_stop = l_mag * (h_bare[idx_stop] + 2 * hIns[idx_stop])
            A_short = A_short_start * f_area_short if A_short_start < A_short_stop else A_short_stop * f_area_short
            # Calculate the turn to turn capacitance between the layers
            C_turn_InOutIns = eps0 * eps_ground_ins * A_short / (wIns[idx_start] + wIns[idx_stop])
            C_turn_inter_layer = eps0 * eps_inter_layer_ins * A_short / (s_inter_layer_ins)
            C_matrix[idx_stop, idx_start] = 1 / (1 / C_turn_InOutIns + 1 / C_turn_inter_layer)
            C_matrix[idx_start, idx_stop] = 1 / (1 / C_turn_InOutIns + 1 / C_turn_inter_layer)

        self._setAttribute(self.HalfTurns, 'C_matrix', C_matrix)

    def _calculate_Zout(self, capacitors):
        """
            This function calculates the total impedance of the network.
            It begins by adding the first inductance and capacitance values to the Z_parallel_L and Z_parallel_C lists, respectively.
            The remaining impedance values are computed using a sequence of Delta-Wye conversions.

            :param capacitors: A list containing the capacitance values corresponding to each inductance, including
                               the final capacitance.
            :return Zout: An array representing the impedance values at each frequency.

           The inductance values are directly obtained from the M_block stored in the HalfTurns dataclass and are then
           multiplied by fL and the magnet length.

           See 'https://indico.cern.ch/event/1510984/contributions/6358964/attachments/3017372/5323228/PP_SectionMeeting_VR.pdf'
           (slides 32-40) for details

        """
        Z_series = []  # List to store series impedance values
        Z_parallel_C = []  # List to store impedance values on the C branch
        Z_parallel_L = []  # List to store impedance values on the L branch

        fL = self.fL
        l_mag = self.General.magnet_length
        M_block = self.HalfTurns.M_block
        frequency = self.frequency
        s = 1j * 2 * np.pi * frequency
        n_count = 0
        el_order_turns = self.General.el_order_turns
        n = len(M_block[0, :])

        for i in range(n):
            # For inductive and capacitive impedances
            turn_idx = el_order_turns[i] - 1
            ZL = s * np.sum(M_block[turn_idx, turn_idx]) * fL * l_mag  # Inductive impedance for this element
            ZC = 1 / (s * capacitors[turn_idx])

            if i == 0:
                Z_parallel_C.append(ZC)
                Z_parallel_L.append(ZL)
            else:
                # Handling series and parallel combinations
                turn_next_idx = el_order_turns[i + 1] - 1 if i != n - 1 else n
                ZC_2 = 1 / (s * capacitors[turn_next_idx])  # Next capacitance impedance for delta-wye conversion
                if n_count == 1:
                    ZC = Z_parallel_C.pop()
                    ZL = ZL + Z_series.pop()

                # Delta-Wye conversion to find equivalent impedances
                Z1eq = (ZL * ZC) / (ZL + ZC + ZC_2)
                Z2eq = (ZL * ZC_2) / (ZL + ZC + ZC_2)
                Z3eq = (ZC_2 * ZC) / (ZL + ZC + ZC_2)

                # Append the calculated equivalent impedances to the lists
                Z_series.append(Z2eq)
                Z_parallel_C.append(Z3eq)
                Z_parallel_L.append(Z1eq)

                n_count = 1

        # Compute total impedance for capacitors and inductors
        Z_C = sum(Z_parallel_C)  # Total capacitive impedance
        Z_L = sum(Z_parallel_L)  # Total inductive impedance
        Z_C_L = (Z_C * Z_L) / (Z_C + Z_L)  # Parallel combination of capacitive and inductive impedances
        Z_series.append(Z_C_L)  # Add combined impedance to the series list
        Zout = sum(Z_series)  # Total impedance of the circuit

        return Zout  # Return the impedance value as a complex number with just imaginary part

    def _calculate_Ceq(self, M_block: np.ndarray, el_order_turns: np.ndarray, capacitors: list, s: complex, turns: list,
                        ZCeq: symbols, turns_to_sections: np.ndarray):
        """
            Compute the Impedance with ZCeq as the Only Symbolic Element
            This function calculates the impedance of the circuit while maintaining ZCeq as the only symbolic variable.

            It starts by adding the first inductance and capacitance values to the Z_parallel_L and Z_parallel_C lists.
            The remaining impedance values are determined using a series of Delta-Wye conversions.

            Optimized computation of impedance with ZCeq as the only symbolic element.

            :param M_block: Inductance matrix.
            :param el_order_turns: Electrical sequence of turns.
            :param capacitors: List of capacitance values.
            :param s: Numerical Laplace variable (NOT symbolic).
            :param ZCeq: Symbolic capacitance impedance.
            :param turns_to_sections: Maps turns to their sections.

            :return: Impedance expression keeping ZCeq as a symbolic variable

            See 'https://indico.cern.ch/event/1510984/contributions/6358964/attachments/3017372/5323228/PP_SectionMeeting_VR.pdf'
           (slides 32-40) for details

        """

        Z_series = []  # Series impedance components
        Z_parallel_C = []
        Z_parallel_L = []  # Parallel inductive components

        l_mag = self.General.magnet_length
        fL = self.fL
        n_count = 0

        section = turns_to_sections[turns[0] - 1]
        # turns_sorted: returns a list with the same elements as in turns but ordered following the electrical order of the turns
        turns_sorted = sorted(turns, key=lambda x: np.where(el_order_turns == x)[0][0])

        n = len(M_block[0, :])
        for i in range(n):
            idx_turn = el_order_turns[i] - 1
            if idx_turn + 1 in turns:
                if idx_turn + 1 != turns_sorted[-1]:
                    continue
                # Use precomputed inductance for the section
                idx_turns = [x -1 for x in turns]
                L_tot = self.General.inductance_to_sections[section - 1, section - 1]
                ZL = s * L_tot
                ZC = ZCeq
            else:
                # Compute numerical values immediately
                ZL = s * M_block[idx_turn, idx_turn] * l_mag * fL
                ZC = 1 / (s * capacitors[idx_turn])

            if i == 0 or (idx_turn + 1 in turns and el_order_turns[0] in turns):
                Z_parallel_C.append(ZC)
                Z_parallel_L.append(ZL)
            else:
                idx_next_turn = el_order_turns[i + 1] - 1 if i != n - 1 else n
                ZC_2 = ZCeq if idx_next_turn + 1 in turns else 1 / (s * capacitors[idx_next_turn])

                if n_count == 1:
                    # Reuse existing components without simplification
                    ZC = Z_parallel_C.pop()
                    ZL += Z_series.pop()

                # Avoid intermediate simplifications

                if isinstance(ZC_2, complex) and isinstance(ZC, complex):
                    Z1eq = (ZL * ZC) / (ZL + ZC + ZC_2)
                    Z2eq = (ZL * ZC_2) / (ZL + ZC + ZC_2)
                    Z3eq = (ZC * ZC_2) / (ZL + ZC + ZC_2)
                else:
                    denom = series(ZL + ZC + ZC_2, ZCeq, n=2).removeO()

                    nom1 = series(ZL * ZC, ZCeq, n=2).removeO()
                    Z1eq = nom1 / denom

                    nom2 = series(ZL * ZC_2, ZCeq, n=2).removeO()
                    Z2eq = nom2 / denom

                    nom3 = series(ZC * ZC_2, ZCeq, n=2).removeO()
                    Z3eq = nom3 / denom

                Z_series.append(Z2eq)
                Z_parallel_C.append(Z3eq)
                Z_parallel_L.append(Z1eq)
                n_count = 1

        # Construct sums as unevaluated expressions
        # Compute total impedance for capacitors and inductors
        Z_C = sum(Z_parallel_C)  # Total capacitive impedance
        Z_L = sum(Z_parallel_L)  # Total inductive impedance
        Z_C_L = (Z_C * Z_L) / (Z_C + Z_L)  # Parallel combination of capacitive and inductive impedances
        Z_series.append(Z_C_L)  # Add combined impedance to the series list
        Zout = sum(Z_series)

        # Single strategic simplification at the end
        return Zout


    def _calculate_CapacitanceToGround_sections(self):
        '''
            Code to calculate the CapacitanceToGround of each magnet section

            Assumptions:
                1. Only consecutive sections in the el_order can be coupled together
                2. The capacitance to ground of one turn is the sum of the capacitance to ground of its HalfTurns
                3. The last Capacitance is always equal to the first capacitance
        '''
        n_sections = self.General.sections
        n_turns = self.General.num_HalfTurns // 2
        frequency = self.frequency
        apertures = self.General.apertures
        C_matrix = self.HalfTurns.C_matrix
        # Convert M_block to a numpy array for slicing, if not already
        M_block = np.array(self.HalfTurns.M_block)
        el_order_sections = self.General.el_order_sections
        turns_to_sections = self.Turns.turns_to_sections
        self.verbose = True
        flag_frequency_capacitance = self.flag_frequency_capacitance
        # Setting capacitance and inductance lists for analytical impedance calculation
        C_turns_list = [C_matrix[i, i] + C_matrix[i + n_turns, i + n_turns] for i in range(n_turns)]
        # Adding one last capacitance to the capacitance list
        C_turns_list.append(C_turns_list[el_order_sections[0] - 1])

        C_ground_sections = []
        L_sections = []

        # Analytical impedance calculation
        Zout = self._calculate_Zout(capacitors=C_turns_list)

        # Looping on the sections by following the electrical order
        first_coupled_sec = False
        for i in range(n_sections):
            C_eq_tot = []
            # Finding the turns indexes corresponding to this section
            sec = el_order_sections[i]
            n_turns_sec = np.count_nonzero(turns_to_sections == sec)
            if n_turns_sec == 1:
                # If the section contains just one turn, then its capacitance to ground and inductances are just the
                # ones of the turn
                idx_turn_sec = np.where(turns_to_sections == sec)[0][0]
                C_ground_sections.append(C_turns_list[idx_turn_sec])
                L_sections.append(self.General.inductance_to_sections[sec-1, sec-1])
                if n_sections == n_turns:
                    self.frequency_list_capacitance = frequency
            else:
                # The turns indexes are the inductances that have to be coupled together in the network
                f_count = 0
                initial_guesses = np.logspace(-11, -5, 500)
                initial_guesses = np.round(initial_guesses, 12).tolist()
                # Remove duplicates while preserving order
                initial_guesses = sorted(set(initial_guesses))
                lower_bound = min(initial_guesses)
                upper_bound = max(initial_guesses)
                initial_guesses = initial_guesses + [-1 * x for x in initial_guesses]
                initial_guesses.sort(key=lambda x: (-abs(x), x))

                if flag_frequency_capacitance:
                    f_peak = 1 / (2 * np.pi * np.sqrt(self.General.L_mag / apertures * self.General.C_ground / (2 * apertures)))
                    closest_f_index = np.abs(frequency - f_peak).argmin()
                    closest_f_value = frequency[closest_f_index]

                    frequency_list = [frequency[0], frequency[closest_f_index - 1]]
                    for i in range(closest_f_index, len(frequency)):
                        if frequency[i] <= 10 * closest_f_value:
                            frequency_list.append(frequency[i])
                        else:
                            frequency_list.append(frequency[i])
                            break
                    frequency_list.append(frequency[-1])
                    self.frequency_list_capacitance = frequency_list
                else:
                    self.frequency_list_capacitance = frequency
                    frequency_list = frequency

                ZCeq = symbols('ZCeq')

                f_count_freq_list = 0
                for f in frequency_list:
                    s_val = 1j * 2 * np.pi * f  # Calculate s for the current frequency
                    # Calculate the right side of the equation as the Zout at the current frequency, where the turns
                    # contained in idx_turn_to_sec have been substitued in the network model by one elemnt only with as
                    # Leq the sum of the individual L and Ceq the symbol
                    if not first_coupled_sec:
                        idx_turns_to_sec = np.where(turns_to_sections == sec)[0]
                        n_cell = [x + 1 for x in idx_turns_to_sec]
                        capacitors = C_turns_list

                        expr_LHS = self._calculate_Ceq(M_block=M_block, capacitors=capacitors,
                                                       el_order_turns=self.General.el_order_turns,
                                                       s=s_val, turns=n_cell, ZCeq=ZCeq,
                                                       turns_to_sections=turns_to_sections)
                    else:
                        # If a previous section has already been coupled, then we need to adjust the cpacitnace to ground and
                        # inductance list, as well as the number of the turns that have to be coupled
                        capacitors_new = []
                        idx_last_turn_previous_sec = np.where(turns_to_sections_reduced == el_order_sections[i - 1])[0][-1]
                        idx_last_turn = np.where(turns_to_sections == el_order_sections[i - 1])[0][-1]
                        idx_turns_to_sec = np.where(turns_to_sections_reduced == sec)[0]
                        n_cell = [x + 1 for x in idx_turns_to_sec]  # Ensure `n_cell` is updated correctly
                        for j in range(idx_last_turn_previous_sec + 1):
                            if isinstance(C_ground_sections[j], np.ndarray):
                                # If the capacitance is an array, then we take just the value related to the current frequency
                                capacitors_new.append(C_ground_sections[j][f_count_freq_list])
                            else:
                                capacitors_new.append(C_turns_list[j])
                        capacitors_new.extend(capacitors[idx_last_turn + 1:])

                        expr_LHS = self._calculate_Ceq(M_block=M_block_new, capacitors=capacitors_new,
                                                       el_order_turns=el_order_turns_new,
                                                       s=s_val, turns=n_cell, ZCeq=ZCeq,
                                                       turns_to_sections=turns_to_sections_reduced)

                    f_count = np.where(frequency == f)[0][0]
                    expr_RHS = Zout[f_count]
                    eq_Total = Eq(expr_LHS, expr_RHS)

                    found = False
                    for x0 in initial_guesses:
                        try:
                            solution_nsolve = nsolve(eq_Total, ZCeq, 1 / (s_val * x0), prec=8)
                            sol = complex(solution_nsolve)
                            found = True
                            break  # Exit loop if a solution is found
                        except (ValueError, SympifyError, NotImplementedError):
                            continue  # Try the next guess if this one fails

                    if found:
                        Ceq_value = 1 / (s_val * sol).real
                        if self.verbose:
                            print(f"At frequency {f} Hz, Ceq nsolve = {Ceq_value}, cont = {f_count}")
                    else:
                        if f_count != 0:
                            Ceq_value = Ceq_value
                        else:
                            idx_cells = np.array([x - 1 for x in n_cell])
                            capacitors = np.array(capacitors)  # Ensure idx_cells is a NumPy array
                            C_guess = np.sum(capacitors[idx_cells])
                            Ceq_value = C_guess
                        if self.verbose:
                            print(f"At frequency {f} Hz, NO numerical solution found with given initial guesses, "
                                  f"Ceq imposed = {Ceq_value}")


                    C_eq_tot.append(float(Ceq_value))
                    f_count_freq_list += 1


                C_ground_sections.append(np.array(C_eq_tot))

                if not first_coupled_sec:
                    M_block_new, turns_to_sections_reduced, el_order_turns_new = adjust_inputs_Ceq(matrix=M_block,
                                 turns_to_merge=n_cell, el_order_turns=self.General.el_order_turns, turns_to_sections=turns_to_sections)
                    first_coupled_sec = True
                else:
                    M_block_new, turns_to_sections_reduced, el_order_turns_new = adjust_inputs_Ceq(matrix=M_block_new,
                                 turns_to_merge=n_cell, el_order_turns=el_order_turns_new, turns_to_sections=turns_to_sections_reduced)

        # In the list C_ground_section the C_ground in position i corresponds to the section in position i of the
        # el_order_sections vector
        self._setAttribute(self.General, 'C_ground_el_order_sections', C_ground_sections)


    def __setCapacitances(self):
        '''
           Code to calculate the ground capacitance and turn to turn capacitance of each half turn

           Cpacitance to ground calculation:
            - if 'flag_comsol' is set to True, then the Capacitance Matrix is stored from the .csv file extracted from Comsol
            - if 'flag_comsol' is False, then the Capacitances to ground are calculated by the '__calculate_CapacitanceToGround' function
              and saved on the diagonal of the C_matrix in the self.HalfTurns.C_Matrix attribute

           If 'flag_TurnToTurn_C' is set to True:
            - if 'flag_comsol' is set to True, then the Capacitance Matrix is stored from the .csv file extracted from Comsol
            - if 'flag_comsol' is False, then the turn to turn capacitances are calculated by the '__calculate_TurnToTurnCapacitance' function
             and saved on the off-diagonals of the C_matrix in the self.HalfTurns.C_Matrix attribute

        '''

        self.__lookupCircuitDataToTFMCapacitances()

        if self.Capacitances.flag_comsol:
            print('Capacitances to ground extracted from Comsol inserted in the network model')
            if self.flag_QH:
                file_path = os.path.join(self.local_library_path, 'TFM_input',
                                             f'CapacitanceMatrix_QH_{self.General.magnet_name}.csv')
            else:
                file_path = os.path.join(self.local_library_path, 'TFM_input',
                                             f'CapacitanceMatrix_NoQH_{self.General.magnet_name}.csv')
            if not os.path.exists(file_path):
                    print(f'File path of the Capacitance Matrix not found {file_path}')
            else:
                C_matrix = pd.read_csv(file_path).iloc[:, 1:].values * 1e-09
                self._setAttribute(self.HalfTurns, 'C_matrix', C_matrix)
        else:
            print('Capacitances to ground analytically calculated inserted in the network model')
            self.__calculate_CapacitanceToGround()

        self._calculate_CapacitanceToGround_sections()

        if self.Capacitances.flag_TurnToTurn_C and not self.Capacitances.flag_comsol:
            print('Capacitances between turns analytically calculated inserted in the network model')
            self.__calculate_TurnToTurnCapacitance()


########################################################################################################################
########################################################################################################################
########################################################################################################################


########################################################################################################################
############################### FUNCTIONS FOR CAPACITANCE CALCULATION ##################################################

def adjust_inputs_Ceq(matrix, turns_to_merge, el_order_turns, turns_to_sections):
    """
    Reduces an n x n matrix by summing together specified rows and columns,
    and adjusts the ordered index list.

    Parameters:
    matrix (np.ndarray): The original n x n matrix.
    turns_to_merge (list of int): Turns number to be summed together.
    ordered_indices (list of int): The original ordered indices.

    Returns:
    np.ndarray: The reduced (n-p) x (n-p) matrix.
    list: The adjusted ordered index list.
    """
    n = matrix.shape[0]
    indices_to_merge = [x - 1 for x in turns_to_merge]

    # Identify remaining indices after merging
    remaining_indices = [i for i in range(n) if i not in indices_to_merge]
    merged_index = min(indices_to_merge)  # Choose the smallest index as the representative

    # Create new reduced matrix
    new_size = len(remaining_indices) + 1  # +1 for the merged row/column
    reduced_matrix = np.zeros((new_size, new_size))
    reduced_matrix[merged_index, merged_index] = np.sum(matrix[np.ix_(indices_to_merge, indices_to_merge)])

    # Fill the new reduced matrix
    # First, copy over elements that are fully outside the merged rows/columns
    for col_idx in remaining_indices:
        col_idx_red = col_idx - len(turns_to_merge) + 1 if col_idx > merged_index else col_idx
        reduced_matrix[merged_index, col_idx_red] = np.sum(matrix[indices_to_merge, col_idx])
        reduced_matrix[col_idx_red, merged_index] = np.sum(matrix[col_idx, indices_to_merge])
        for row_idx in remaining_indices:
            row_idx_red = row_idx - len(turns_to_merge) + 1 if row_idx > merged_index else row_idx
            reduced_matrix[row_idx_red, col_idx_red] = np.sum(matrix[row_idx, col_idx])

    # Adjust ordered indices to maintain sequence [0, 1, 2]
    turns_to_sections_reduced = []
    for i in range(len(turns_to_sections)):
        if i + 1 in turns_to_merge and i + 1 != turns_to_merge[-1]: continue
        turns_to_sections_reduced.append(turns_to_sections[i])
    turns_to_sections_reduced = np.array(turns_to_sections_reduced)

    el_order_turns_new = []
    el_order_turns_new = [x for x in list(el_order_turns) if x not in turns_to_merge]
    el_order_turns_new = np.array(el_order_turns_new)

    return reduced_matrix, turns_to_sections_reduced, el_order_turns_new


########################################################################################################################
############################### FUNCTIONS TO CHANGE .FUNC PARAMETERS IN THE LIB FILE  ###################################
def change_library_EqLoop(path_file: Path, element: str, domain: str, frequency: np.ndarray,
                          L_eq: np.ndarray, R_eq: np.ndarray, M_eq_x: np.ndarray, M_eq_y: np.ndarray, groups: int = 2, force_new_name: Path = ''):
    '''
    Helper function that changes the TFM magnet .lib file and includes in Table function the given R,L,M parameter

    element = Element, for which the RLM to be inserted e.g. BS, CPS, ED ...

    If L_eq, M_eq or R_eq are empty, they will not be written
    '''
    if domain=='frequency':
        tab_stub = '{TABLE{FREQ}='
    else:
        tab_stub = '{TABLE{f_characteristic}='

    str_L = []
    str_R = []
    #### Creating string for equivalent inductance
    if L_eq.size:
        for i in range(groups):
            group = [f'{element}_L_{i+1}(1)', tab_stub]
            str_group_L = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
            L = L_eq[:,i]
            for j in range(len(frequency)):
                str_group_L = str_group_L + f'({frequency[j]},{L[j]})     '
            str_group_L = str_group_L + '}\n'
            str_L.append(str_group_L)

    #### Creating string for equivalent resistance
    if R_eq.size:
        for i in range(groups):
            group = [f'{element}_R_{i + 1}(1)', tab_stub]
            str_group_R = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
            R = R_eq[:, i]
            for j in range(len(frequency)):
                str_group_R = str_group_R + f'({frequency[j]},{R[j]})     '
            str_group_R = str_group_R + '}\n'
            str_R.append(str_group_R)

    #### Creating string for equivalent mutual inductance
    str_M = {}
    str_M_sing = {}
    str_M_x = {}
    str_M_y = {}
    if M_eq_x.size and M_eq_y.size:
        for i in range(M_eq_x.shape[0]):
            for j in range(M_eq_x.shape[1]):
                group = [f'{element}_M_{i + 1}_{j+1}_x(1)', tab_stub]
                str_group_M = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
                M = M_eq_x[i, j, :]
                for k in range(len(frequency)):
                    str_group_M = str_group_M + f'({frequency[k]},{np.real(M[k])}+{np.imag(M[k])}J)     '
                str_group_M = str_group_M + '}\n'
                str_M_x[f'{i},{j}'] = str_group_M

        for i in range(M_eq_x.shape[0]):
            for j in range(M_eq_x.shape[1]):
                group = [f'{element}_M_{i + 1}_{j+1}_y(1)', tab_stub]
                str_group_M = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
                M = M_eq_y[i, j, :]
                for k in range(len(frequency)):
                    str_group_M = str_group_M + f'({frequency[k]},{np.real(M[k])}+{np.imag(M[k])}J)     '
                str_group_M = str_group_M + '}\n'
                str_M_y[f'{i},{j}'] = str_group_M
    elif M_eq_x.size:
        if len(M_eq_x.shape)>2:
            for i in range(M_eq_x.shape[0]):
                for j in range(M_eq_x.shape[1]):
                    group = [f'{element}_M_{i + 1}_{j + 1}(1)', tab_stub]
                    str_group_M = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
                    M = M_eq_x[i, j, :]
                    for k in range(len(frequency)):
                        str_group_M = str_group_M + f'({frequency[k]},{np.real(M[k])}+{np.imag(M[k])}J)     '
                    str_group_M = str_group_M + '}\n'
                    str_M[f'{i},{j}'] = str_group_M
        else:
            for i in range(M_eq_x.shape[0]):
                group = [f'{element}_M_{i + 1}(1)', tab_stub]
                str_group_M = f'.FUNC' + ' ' + ' '.join("{:<20}".format(g) for g in group)
                M = M_eq_x[i, :]
                for k in range(len(frequency)):
                    str_group_M = str_group_M + f'({frequency[k]},{np.real(M[k])}+{np.imag(M[k])}J)     '
                str_group_M = str_group_M + '}\n'
                str_M_sing[f'{i}'] = str_group_M

    ## Opening library file
    lib_path = path_file
    with open(lib_path) as f:
        lines = f.readlines()

    ## Changing elements in library
    patterns = {}

    for i in range(M_eq_x.shape[0]):
        if str_L and i<groups:
            patterns[f'.FUNC {element}_L_{i + 1}(1)'] = str_L[i]
        if str_R and i<groups:
            patterns[f'.FUNC {element}_R_{i + 1}(1)'] = str_R[i]
        if str_M_sing:
            patterns[f'.FUNC {element}_M_{i + 1}(1)'] = str_M_sing[f'{i}']
        for j in range(M_eq_x.shape[1]):
            if str_M:
                patterns[f'.FUNC {element}_M_{i + 1}_{j + 1}(1)'] = str_M[f'{i},{j}']
            if str_M_x:
                patterns[f'.FUNC {element}_M_{i + 1}_{j + 1}_x(1)'] = str_M_x[f'{i},{j}']
            if str_M_y:
                patterns[f'.FUNC {element}_M_{i + 1}_{j + 1}_y(1)'] = str_M_y[f'{i},{j}']

    # Use a single loop with pattern lookup
    for i, line in enumerate(lines):
        if not line.startswith('.FUNC'): continue
        line_split = '.FUNC ' + line.split(' ')[1]
        if line_split in patterns.keys():
            lines[i] = patterns[line_split]

    text_lib = ''.join(lines)

    if not force_new_name:
        new_lib_path = Path('..//lib//MB_TFM_General_Adjusted.lib').resolve()
    else:
        new_lib_path = force_new_name
    with open(new_lib_path, 'w') as f:
        f.write(text_lib)
    return new_lib_path



def change_library_MutualCoupling(path_file: Path, element: str, frequency: np.ndarray, domain: str, M_eq_x: np.ndarray = np.array([]), M_eq_y: np.array = np.array([])):
    '''
    Helper function that changes the mutual coupling values of element to M_eq. Can be multiple values, e.g. a
    changing coupling over frequency
    '''
    if domain=='frequency':
        tab_stub = '{TABLE{FREQ}='
    else:
        tab_stub = '{TABLE{f_characteristic}='

    effects = element.split('_')[1:]

    #### Creating string for equivalent mutual inductance
    str_group_Mx = []
    if M_eq_x.size:
        if len(M_eq_x.shape) > 1 and not effects[0]=='ISCC':
            for i in range(1,M_eq_x.shape[0]+1):
                M_eq = M_eq_x[i-1,:]
                str_group_M = f'.FUNC {element}_{i}_x(1)					' + tab_stub
                for j in range(len(frequency)):
                    str_group_M = str_group_M + f'({frequency[j]},{np.real(M_eq[j])}+{np.imag(M_eq[j])}J)     '
                str_group_M = str_group_M + '}\n'
                str_group_Mx.append(str_group_M)
        elif effects[0]=='ISCC':
            for i in range(1,M_eq_x.shape[0]+1):
                M_eq = M_eq_x[i - 1, :]
                str_group_M = f'.FUNC {element}_{i}(1)					' + tab_stub
                for j in range(len(frequency)):
                    str_group_M = str_group_M + f'({frequency[j]},{np.real(M_eq[j])}+{np.imag(M_eq[j])}J)     '
                str_group_M = str_group_M + '}\n'
                str_group_Mx.append(str_group_M)
        else:
            M_eq = M_eq_x
            str_group_M = f'.FUNC {element}(1)					' + tab_stub
            for j in range(len(frequency)):
                str_group_M = str_group_M + f'({frequency[j]},{np.real(M_eq[j])}+{np.imag(M_eq[j])}J)     '
            str_group_M = str_group_M + '}\n'
            str_group_Mx.append(str_group_M)
    str_group_My = []
    if M_eq_y.size:
        for i in range(1,M_eq_y.shape[0]+1):
            M_eq = M_eq_y[i-1, :]
            str_group_M = f'.FUNC {element}_{i}_y(1)					' + tab_stub
            for j in range(len(frequency)):
                str_group_M = str_group_M + f'({frequency[j]},{np.real(M_eq[j])}+{np.imag(M_eq[j])}J)     '
            str_group_M = str_group_M + '}\n'
            str_group_My.append(str_group_M)

    ## Opening library file
    lib_path = path_file
    try:
        with open(lib_path) as f:
             lines = f.readlines()
    except:
        c = 0
        while not os.access(lib_path, os.R_OK):
            time.sleep(1)
            c = c+1
            if c>10:
                break
        with open(lib_path) as f:
            lines = f.readlines()

    ## Changing elements in library
    patterns = {}

    if len(M_eq_x.shape) > 1 and not effects[0]=='ISCC':
        for i in range(M_eq_x.shape[0]):
            if str_group_Mx:
                patterns[f'.FUNC {element}_{i+1}_x(1)'] = str_group_Mx[i]
    elif effects[0]=='ISCC':
        for i in range(M_eq_x.shape[0]):
            if str_group_Mx:
                patterns[f'.FUNC {element}_{i+1}(1)'] = str_group_Mx[i]
    else:
        if str_group_Mx:
            patterns[f'.FUNC {element}(1)'] = str_group_Mx[0]
    if len(M_eq_y.shape) > 1:
        for i in range(M_eq_x.shape[0]):
            if str_group_Mx:
                patterns[f'.FUNC {element}_{i+1}_y(1)'] = str_group_My[i]

    # Use a single loop with pattern lookup
    for i, line in enumerate(lines):
        if not line.startswith('.FUNC'): continue
        line_split = line.split(')')[0]
        line_split = line_split + ')'
        if line_split in patterns.keys():
            lines[i] = patterns[line_split]

    text_lib = ''.join(lines)

    with open(path_file, 'w') as f:
        f.write(text_lib)
    return path_file

########################################################################################################################
################################################### HELPER FUNCTIONS   #################################################
def smooth_curve(y: np.ndarray, box_pts: int, n_pad: int = 20) -> np.ndarray:
    '''
    Helper function that smoothes a curve with a box filter
    :param y: np.ndarray - Array to be smoothed
    :param box_pts: int - width of the box filter (generally 3 or 5)
    :param n_pad: int - width of zero-padding
    :return: the smoothed array
    '''
    box = np.ones(box_pts) / box_pts
    if len(y.shape)>1:
        y_smooth = np.zeros(y.shape)
        for i in range(y.shape[0]):
            y_padded = np.pad(y[i,:], n_pad, mode='constant',constant_values=(y[i,0],y[i,-1]))
            y_filtered = np.convolve(y_padded, box, mode='same')
            y_smooth[i, :] = y_filtered[n_pad:-n_pad]
    else:
        y_padded = np.pad(y, n_pad, mode='constant', constant_values=(y[0], y[-1]))
        y_smooth = np.convolve(y_padded, box, mode='same')
    return y_smooth[n_pad: -n_pad]


def is_positive_definite(matrix):
    return np.all(np.linalg.eigvals(matrix) >= 0)


def check_smoothness(frequency: np.ndarray, signal: np.ndarray):
    '''

    '''
    derivative = np.diff(signal) / np.diff(frequency)
    zero_crossings = np.where(np.diff(np.sign(signal)))[0]
    for idx in zero_crossings:
        if idx > 0 and idx < len(derivative) - 1:
            derivative_diff = abs(derivative[idx + 1] - derivative[idx])
            if derivative_diff > np.median(abs(derivative)):
                signal[idx + 1:] *= -1
                derivative = np.diff(signal) / np.diff(frequency)
    smooth_signal = smooth_curve(signal, 5, n_pad=5)
    return smooth_signal


def interpolate_curve(signal: np.ndarray):
    '''

    :param signal:
    :type signal:
    :return:
    :rtype:
    '''
    def detect_spikes_in_derivative(signal, distance=5, prominence=1):
        derivative = np.diff(signal)
        peaks, _ = find_peaks(np.abs(derivative), distance=distance, prominence=0.2*np.abs(derivative).max())
        return peaks, derivative

    def smooth_signal_around_spikes(signal, spike_indices, window_size):
        smooth_signal = np.copy(signal)
        for spike_index in spike_indices:
            start_index = max(0, spike_index - window_size)
            end_index = min(len(signal), spike_index + window_size)
            x = np.arange(0, start_index).tolist() + np.arange(end_index, len(signal)).tolist()
            y = smooth_signal[:start_index].tolist() + smooth_signal[end_index:].tolist()
            f_interp = interp1d(x, y, kind='linear', fill_value="extrapolate")
            smooth_signal[start_index:end_index] = f_interp(np.arange(start_index, end_index))
        return smooth_signal

    spike_indices, derivative = detect_spikes_in_derivative(signal, distance=1, prominence=1.5)
    window_size = 10  # Number of points around the spike to interpolate
    smooth_signal = smooth_signal_around_spikes(signal, spike_indices, window_size)
    return smooth_signal
