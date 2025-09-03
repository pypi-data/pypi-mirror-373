import unittest as unittest
import os
import numpy as np
import copy
from pathlib import Path
from sympy import *


from steam_sdk.builders.BuilderModel import BuilderModel
from tests.TestHelpers import assert_two_parameters

class TestBuilderTFM(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """

        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define General parameters that are equal to the ones taken from the input file
        self.local_General = {
            'COMSOL_ap': None,
            'C_ground': 2.5e-07,
            'I_magnet': 1.0,
            'R_warm': 1e-09,
            'apertures': 2,
            'el_order_sections': [1, 2],
            'el_order_to_apertures': [1, 2],
            'flag_LumpedC': True,
            'sections': 2,
            'local_library_path': 'model_library\\magnets\\MBRD\\input',
            'magnet_length': 7.78,
            'magnet_name': 'MBRD',
            'num_HalfTurns': 248,
            'sections_to_aperture': [1, 2]
        }

        # Define HalfTurns parameters that are equal to the ones taken from the input file
        self.local_HalfTurns = {
            'C_strand': np.array([1.13125]*248),
            'HalfTurns_to_apertures': np.array([1.0]*62 + [2.0]*62 + [1.0]*62 + [2.0]*62),
            'HalfTurns_to_conductor': np.array([1]*248),
            'HalfTurns_to_groups': np.array([1.0]*15 + [2.0]*6 + [3.0]*4 + [4.0]*4 + [5.0]*2 + [6.0]*15 + [7.0]*6 + [8.0]*4
                                           + [9.0]*4 + [10.0]*2 + [11.0]*15 + [12.0]*6 + [13.0]*4 + [14.0]*4 + [15.0]*2
                                           + [16.0]*15 + [17.0]*6 + [18.0]*4 + [19.0]*4 + [20.0]*2 + [21.0]*15 + [22.0]*6
                                           + [23.0]*4 + [24.0]*4 + [25.0]*2 + [26.0]*15 + [27.0]*6 + [28.0]*4 + [29.0]*4
                                           + [30.0]*2 + [31.0]*15 + [32.0]*6 + [33.0]*4 + [34.0]*4 + [35.0]*2 + [36.0]*15
                                           + [37.0]*6 + [38.0]*4 + [39.0]*4 + [40.0]*2),
            'HalfTurns_to_sections': np.array([1.0]*62 + [2.0]*62 + [1.0]*62 + [2.0]*62),
            'Nc': np.tile(np.array([15.0]*15 + [6.0]*6 + [4.0]*8 + [2.0]*2), 8),
            'RRR': np.array([200.0]*248),
            'R_warm': np.array([1e-09]*248),
            'Rc': np.array([0.0001]*248),
            'alphaDEG_ht': np.array([0.,0.8464,1.6928,2.5392,3.3856,4.232,5.0784,5.9248,6.7712,7.6176,8.464,9.3104,10.1568,11.0032,
                            11.8496,36.227,37.0734,37.9198,38.7662,39.6126,40.459,41.6,42.4464,43.2928,44.1392,54.629,55.4754,
                            56.3218,57.1682,71.053,71.8994,0.,0.8464,1.6928,2.5392,3.3856,4.232,5.0784,5.9248,6.7712,7.6176,
                            8.464,9.3104,10.1568,11.0032,11.8496,33.537,34.3834,35.2298,36.0762,36.9226,37.769,45.218,46.0644,
                            46.9108,47.7572,50.549,51.3954,52.2418,53.0882,72.573,73.4194,0.,0.8464,1.6928,2.5392,3.3856,
                            4.232,5.0784,5.9248,6.7712,7.6176,8.464,9.3104,10.1568,11.0032,11.8496,36.227,37.0734,37.9198,
                            38.7662,39.6126,40.459,41.6,42.4464,43.2928,44.1392,54.629,55.4754,56.3218,57.1682,71.053,
                            71.8994,0.,0.8464,1.6928,2.5392,3.3856,4.232,5.0784,5.9248,6.7712,7.6176,8.464,9.3104,10.1568,
                            11.0032,11.8496,33.537,34.3834,35.2298,36.0762,36.9226,37.769,45.218,46.0644,46.9108,47.7572,
                            50.549,51.3954,52.2418,53.0882,72.573,73.4194,0.,0.8464,1.6928,2.5392,3.3856,4.232,5.0784,
                            5.9248,6.7712,7.6176,8.464,9.3104,10.1568,11.0032,11.8496,36.227,37.0734,37.9198,38.7662,
                            39.6126,40.459,41.6,42.4464,43.2928,44.1392,54.629,55.4754,56.3218,57.1682,71.053,71.8994,
                            0.,0.8464,1.6928,2.5392,3.3856,4.232,5.0784,5.9248,6.7712,7.6176,8.464,9.3104,10.1568,11.0032,
                            11.8496,33.537,34.3834,35.2298,36.0762,36.9226,37.769,45.218,46.0644,46.9108,47.7572,50.549,
                            51.3954,52.2418,53.0882,72.573,73.4194,0.,0.8464,1.6928,2.5392,3.3856,4.232,5.0784,5.9248,
                            6.7712,7.6176,8.464,9.3104,10.1568,11.0032,11.8496,36.227,37.0734,37.9198,38.7662,39.6126,
                            40.459,41.6,42.4464,43.2928,44.1392,54.629,55.4754,56.3218,57.1682,71.053,71.8994,0.,0.8464,
                            1.6928,2.5392,3.3856,4.232,5.0784,5.9248,6.7712,7.6176,8.464,9.3104,10.1568,11.0032,11.8496,
                            33.537,34.3834,35.2298,36.0762,36.9226,37.769,45.218,46.0644,46.9108,47.7572,50.549,51.3954,
                            52.2418,53.0882,72.573,73.4194]),
            'bare_cable_height_mean': np.array([0.001476]*248),
            'bare_cable_width': np.array([0.0151]*248),
            'diameter': np.array([0.000825]*248),
            'f_rho_effective': np.array([2.]*248),
            'fsc': np.array([0.3389830508474576]*248),
            'mirror_ht': np.array([0]*124 + [1]*124),
            'n_strands': np.array([36]*248),
            'rotation_ht': np.array([0.0]*31 + [180.0]*31 + [0.0]*31 + [180.0]*31 + [90.0]*31 + [270.0]*31 + [90.0]*31 + [270.0]*31),
            'strand_twist_pitch': np.array([0.12]*248)
        }

        # Define Strands parameters that are equal to the ones taken from the input file
        self.local_Strands = {
            'RRR': np.array([200.0] * 8928),
            'd_core': np.array([0.00033] * 8928),
            'd_filamentary': np.array([0.00066] * 8928),
            'diameter': np.array([0.000825] * 8928),
            'f_rho_effective': np.array([2.0]*8928),
            'fil_twist_pitch': np.array([0.015]*8928),
            'filament_diameter': np.array([6.0e-06]*8928),
            'fsc': np.array([0.3389830508474576] * 8928),
            'strands_to_apertures': np.array([1.0] * 2232 + [2.0] * 2232 + [1.0] * 2232 + [2.0] * 2232),
            'strands_to_conductor': np.array([1.0] * 8928),
            'strands_to_sections': np.array([1.0] * 2232 + [2.0] * 2232 + [1.0] * 2232 + [2.0] * 2232),
            'f_mag_Comsol': np.array([0.0003813306114041191, 0.00037313888279080223, 0.0003474664867921326, 0.0003442948366505535,
                               0.0003152933613789643, 0.0003141976368465479, 0.0002835221510852776, 0.0002836285892993441,
                               0.0002537732382392306, 0.00025420654050975424, 0.00022222702844891241, 0.0002238533946891957,
                               0.000191935015368674, 0.00019437848136681052, 0.00016199435929851536, 0.00016549325322905658,
                               0.00013281607634749946, 0.0001370140518234683, 0.00010466140991859808, 0.00010994698953348774,
                               7.802879817236252e-05, 8.526428880940532e-05, 5.5197467188093327e-05, 6.462079063385088e-05,
                               4.15622091e-05]),
            'f_mag_X_Comsol': np.array([-3.97e-05, -4.45e-05, -4.43e-05, -5.15e-05, -4.79e-05, -5.52e-05, -5.03e-05, -5.78e-05,
                                        -5.11e-05, -5.91e-05, -5.12e-05, -5.95e-05, -5.07e-05, -5.93e-05, -5.01e-05, -5.88e-05,
                                        -4.91e-05, -5.82e-05, -4.75e-05, -5.71e-05, -4.59e-05, -5.57e-05, -4.39e-05, -5.43e-05,
                                        -4.13e-05]),
            'f_mag_Y_Comsol': np.array([0.0003792584147963487, 0.00037047587755529784, 0.00034463091771294585, 0.00034042133385590173,
                                        0.0003116335888983185, 0.00030931070948151014, 0.0002790245870098601, 0.00027767667649252793,
                                        0.0002485752329706749, 0.0002472410872770489, 0.00021624849634906997, 0.00021580104799068245,
                                        0.00018511769262977845, 0.0001851121390359571, 0.00015405246653181666, 0.00015469510937433234,
                                        0.0001234070505941407, 0.00012403874554784908, 9.326178599055896e-05, 9.395706736311463e-05,
                                        6.310058117183458e-05, 6.455624637611516e-05, 3.3459682962942716e-05, 3.5033649283852664e-05,
                                        4.661247294186419e-06]),
            'f_mag_Roxie': np.array([0.0003605844024297672, 0.00035210940395191296, 0.0003197178772195209, 0.0003151272967125868,
                                     0.0002843084699275662, 0.0002829642244677664, 0.0002505290481773475, 0.00025137850621966923,
                                     0.0002176387420986721, 0.00022008344598564123, 0.00018545413875672217, 0.00018924158330825607,
                                     0.00015403641862932397, 0.00015912770453132473, 0.00012362298065370718, 0.0001301999064260019,
                                     8.593816473640649e-05, 9.845839078864107e-05, 4.8818072624832945e-05, 7.946999456713677e-05,
                                     4.339587550660384e-05, 5.783958571182462e-05, 5.570700678411072e-05, 6.638769342320723e-05,
                                     7.697281540289639e-05]),
            'f_mag_X_Roxie': np.array([3.544398340248963e-05, 3.989211618257261e-05, 4.137759336099585e-05, 5.260580912863071e-05,
                                       4.619087136929461e-05, 5.8912863070539415e-05, 4.898755186721992e-05, 6.214107883817427e-05,
                                       5.031535269709543e-05, 6.364315352697096e-05, 5.063900414937759e-05, 6.409128630705395e-05,
                                       5.024896265560166e-05, 6.384232365145228e-05, 4.935269709543569e-05, 6.313692946058092e-05,
                                       5.440663900414937e-05, 7.180912863070539e-05, 4.4514522821576763e-05, 7.039004149377593e-05,
                                       4.225726141078838e-05, 5.725311203319502e-05, 3.963485477178424e-05, 5.504564315352697e-05,
                                       3.654771784232365e-05]),
            'f_mag_Y_Roxie': np.array([-0.0003588381742738589, -0.0003498423236514523, -0.0003170290456431535, -0.0003107053941908714,
                                       -0.0002805311203319502, -0.00027676348547717844, -0.0002456929460580913, -0.00024357676348547716,
                                       -0.0002117427385892116, -0.0002106804979253112, -0.00017840663900414938, -0.00017805809128630705,
                                       -0.00014560995850622407, -0.00014575933609958506, -0.00011334439834024896, -0.00011386721991701246,
                                       -6.652282157676349e-05, -6.73609958506224e-05, -2.004149377593361e-05, -3.6887966804979256e-05,
                                       9.87551867219917e-06, 8.215767634854772e-06, 3.914522821576763e-05, 3.711203319502075e-05,
                                       6.774273858921162e-05])
        }

        # Define Options parameters that are equal to the ones taken from the input file
        self.local_Options = {
            'flag_AlRing': False,
            'flag_BS': False,
            'flag_CB': False,
            'flag_CPS': False,
            'flag_ED': False,
            'flag_IFCC': False,
            'flag_ISCC': False,
            'flag_PC': False,
            'flag_SC': True,
            'flag_Wedge': False
        }


    def test_BuilderTFM_init(self):
        """
            Checks that DataTFM object can be initialized
        """

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', 'MBRD', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_MBRD.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM =0, flag_build=False)

        self.assertEqual(hasattr(builderTFM, 'verbose'), True)

        self.assertEqual(hasattr(builderTFM, 'General'), True)
        self.assertEqual(hasattr(builderTFM, 'Turns'), True)
        self.assertEqual(hasattr(builderTFM, 'HalfTurns'), True)
        self.assertEqual(hasattr(builderTFM, 'Strands'), True)
        self.assertEqual(hasattr(builderTFM, 'Options'), True)

        self.assertEqual(hasattr(builderTFM, 'PC'), True)
        self.assertEqual(hasattr(builderTFM, 'IFCC'), True)
        self.assertEqual(hasattr(builderTFM, 'ISCC'), True)
        self.assertEqual(hasattr(builderTFM, 'ED'), True)
        self.assertEqual(hasattr(builderTFM, 'Wedge'), True)
        self.assertEqual(hasattr(builderTFM, 'CB'), True)
        self.assertEqual(hasattr(builderTFM, 'CPS'), True)
        self.assertEqual(hasattr(builderTFM, 'AlRing'), True)
        self.assertEqual(hasattr(builderTFM, 'BS'), True)
        self.assertEqual(hasattr(builderTFM, 'Shorts'), True)

        self.assertEqual(hasattr(builderTFM, 'effs_cond'), True)
        self.assertEqual(hasattr(builderTFM, 'frequency'), True)
        self.assertEqual(hasattr(builderTFM, 'mu0'), True)
        self.assertEqual(hasattr(builderTFM, 'print_nodes'), True)


    def test_setAttribute(self):
        """
            Test that setAttribute works
        """

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', 'MBRD', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_MBRD.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM = 0, flag_build=False)

        for parameter in self.local_General:
            true_value = self.local_General[parameter]
            setattr(builderTFM.General, parameter, true_value)
            # act
            test_value = builderTFM._getAttribute('General', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_HalfTurns:
            true_value = self.local_HalfTurns[parameter]
            setattr(builderTFM.HalfTurns, parameter, true_value)
            # act
            test_value = builderTFM._getAttribute('HalfTurns', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Strands:
            true_value = self.local_Strands[parameter]
            setattr(builderTFM.Strands, parameter, true_value)
            # act
            test_value = builderTFM._getAttribute('Strands', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Options:
            true_value = self.local_Options[parameter]
            setattr(builderTFM.Options, parameter, true_value)
            # act
            test_value = builderTFM._getAttribute('Options', parameter)
            # assert
            assert_two_parameters(true_value, test_value)


    def test_getAttribute(self):
        """
            Test getAttribute works
        """
        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', 'MBRD', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_MBRD.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM = 0, flag_build=False)

        for parameter in self.local_General:
            true_value = self.local_General[parameter]
            # act
            builderTFM._setAttribute('General', parameter, true_value)
            test_value = getattr(builderTFM.General, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_HalfTurns:
            true_value = self.local_HalfTurns[parameter]
            # act
            builderTFM._setAttribute('HalfTurns', parameter, true_value)
            test_value = getattr(builderTFM.HalfTurns, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Strands:
            true_value = self.local_Strands[parameter]
            # act
            builderTFM._setAttribute('Strands', parameter, true_value)
            test_value = getattr(builderTFM.Strands, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Options:
            true_value = self.local_Options[parameter]
            # act
            builderTFM._setAttribute('Options', parameter, true_value)
            test_value = getattr(builderTFM.Options, parameter)
            # assert
            assert_two_parameters(true_value, test_value)


    def test_assignAttribute(self):
        """
             Tests if BuilderTFM assign correctly the data to dataclasses General, Strands, HalfTurns and Options
             according to the magnet input yaml file. The following BuilderTFM function are being tested:
             - __translateModelDataToTFMGeneral()
             - __translateModelDataToTFMHalfTurns()
             - __translateModelDataToTFMStrands()
             - __setOptions()

        """
        # Taking the .yaml file of the corresponding circuit
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input', 'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM = 0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM, verbose=False)

        # Testing __translateModelDataToTFMGeneral()
        print('Starting test on function __translateModelDataToTFMGeneral(): ')
        for parameter in self.local_General:
            print(f'Test on param General.{parameter}:')
            true_value = self.local_General[parameter]
            # act
            test_value = builderTFM._getAttribute('General', parameter)
            # assert
            assert_two_parameters(true_value, test_value)
            print('PASSED')
        print('Test on function __translateModelDataToTFMGeneral() PASSED \n')

        # Testing __translateModelDataToTFMHalfTurns()
        print('Starting test on function __translateModelDataToTFMHalfTurns(): ')
        for parameter in self.local_HalfTurns:
            print(f'Test on param HalfTurns.{parameter}: ')
            true_value = self.local_HalfTurns[parameter]
            # act
            test_value = builderTFM._getAttribute('HalfTurns', parameter)
            # assert
            assert_two_parameters(true_value, test_value)
            print('PASSED')
        print('Test on function __translateModelDataToTFMHalfTurns() PASSED \n')

        # Testing __translateModelDataToTFMStrands()
        print('Starting test on function __translateModelDataToTFMStrands(): ')
        for parameter in self.local_Strands:
            print(f'Test on param Strands.{parameter}: ')
            true_value = self.local_Strands[parameter]
            # act
            test_value = builderTFM._getAttribute('Strands', parameter)
            # assert
            if 'f_mag' not in parameter:
                assert_two_parameters(true_value, test_value)
            else:
                continue
            print('PASSED')
        print('Test on function __translateModelDataToTFMStrands() PASSED \n')

        # Testing __setOptions()
        print('Starting test on function __setOptions(): ')
        for parameter in self.local_Options:
            print(f'Test on param Options.{parameter}: ')
            true_value = self.local_Options[parameter]
            # act
            test_value = builderTFM._getAttribute('Options', parameter)
            # assert
            assert_two_parameters(true_value, test_value)
            print('PASSED')
        print('Test on function __setOptions() PASSED')


    def test_assignMagnetData(self):
        """
           Tests if the effect objects, when present in the circuit .yaml file, are correctly assigned to the
           corresponding dataclass in BuilderTFM
        """
        # Taking the .yaml file of the corresponding circuit
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM=0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False)

        for key, value in magnet_TFM.__dict__.items():
            if 'magnet_' in key and key != 'magnet_Couplings' and value is not None:
                eff = key.split('_')[-1]
                print(f'Test assignment of {eff} dataclass as attribute in BuilderTFM:')
                test_value = getattr(builderTFM, eff)
                self.assertEqual(value, test_value)
                print('PASSED')
        print('\n')


    def test_generateLibFile(self):
        """
           Tests if BuilderTFM generate the corresponding .lib file when flag_build = True
           and the output_path is given
        """

        # Taking the .yaml file of the corresponding circuit
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))
        magnet_TFM_name = next(iter(TFM_data.magnets_TFM.keys()))

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        output_path = os.path.join('output', 'BuilderTFM')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f'Directory {output_path} created')
        output_path_TFM = os.path.join(output_path, f'{magnet_TFM_name}.lib')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        _,_ = bM_TFM.buildTFM(builderTFM = 0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False, flag_build=True, output_path=output_path_TFM)

        if not os.path.exists(output_path_TFM):
            raise Exception(f'Library file {output_path_TFM} NOT generated')


    def test_calculateEffect(self):
        """
             Sets the flags attribute to True in the Options dataclass and verifies that the attributes of the
             corresponding effect dataclass are properly populated.
        """
        # Taking the .yaml file of the corresponding circuit
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))
        magnet_TFM_name = next(iter(TFM_data.magnets_TFM.keys()))
        TFM_inputs.flag_CPS = True
        TFM_inputs.flag_PC = True

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM= 0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False, flag_build=True)

        output_path = os.path.join('output', 'BuilderTFM')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f'Directory {output_path} created')
        output_path_TFM = os.path.join(output_path, f'{magnet_TFM_name}.lib')
        builderTFM._generate_library(output_path=output_path_TFM, library_name='TEST')

        for key, value in builderTFM.Options.__dict__.items():
            if key == 'flag_BS' or key == 'flag_SC': continue
            setattr(builderTFM.Options, key, True)
            eff = key.split('_')[-1]
            builderTFM.change_coupling_parameter()
            dataclass = getattr(builderTFM, eff)
            for key_data, value_data in dataclass.__dict__.items():
                if value_data is None and key_data != 'group_CPS':
                    raise Exception(f'Attribute {key_data} in dataclass {eff} has not be written ({key}=True)')


    def test_assignTurnsToSections(self):
        """
            Tests if __assignTurnsToSections function works properly.
            When turns_to_sections = None:
                - HalfTurns_to_sections = HalfTurns_to_apertures
                - strands_to_sections = strands_to_apertures
             When turns_to_sections != None:
                - HalfTurns_to_sections = np.tile(turns_to_sections, 2).astype(int)
                - HalfTurns_to_apertures stays the same
                - strands_to_sections is assigned according to the new value of HalfTurns_to_sections
                - strands_to_apertures stays the same

        """
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))


        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM,_ = bM_TFM.buildTFM(builderTFM = 0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False)

        # In the model circuit yaml file turns_to_sections = None so HalfTurns_to_sections in the dataclasses should correspond
        # to HalfTurns_to_apertures vector and strands_to_sections should correspond to strands_to_apertures
        if builderTFM.HalfTurns.HalfTurns_to_sections.all() != builderTFM.HalfTurns.HalfTurns_to_apertures.all():
            raise Exception(f'Attribute HalfTurns_to_sections has to be equal to HalfTurns_to_apertures when key turn_to_section = None'
                            f' in the input circuit yaml file')
        if builderTFM.Strands.strands_to_sections.all() != builderTFM.Strands.strands_to_apertures.all():
            raise Exception(
                f'Attribute strands_to_sections has to be equal to strands_to_apertures when key turn_to_section = None'
                f' in the input circuit yaml file')

        reference_HalfTurns_to_ap = builderTFM.HalfTurns.HalfTurns_to_apertures
        reference_strands_to_ap = builderTFM.Strands.strands_to_apertures

        # Modifying turns_to_sections key to be != None
        turns_to_sections = [11]*62 + [1]*15 + [2]*6 + [3]*4 + [4]*4 + [5]*2 + [6]*13 + [7]*6 + [8]*4 + [9]*4 + [10]*2 + [11]*2
        magnet_TFM.turn_to_section = turns_to_sections
        builderTFM,_ =  bM_TFM.buildTFM(builderTFM = 0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False)
        # In the model circuit yaml file turns_to_sections != None so HalfTurns_to_sections in the dataclasses should correspond
        # to turns_to_sections repeated by 2. HalfTurns_to_apertures should instead not change comparing to the previous case.
        if builderTFM.HalfTurns.HalfTurns_to_sections.all() != np.tile(turns_to_sections, 2).astype(int).all():
            raise Exception(
                f'Attribute HalfTurns_to_sections for turns_to_sections != None does not correspond to: '
                f'{np.tile(turns_to_sections, 2).astype(int)}')
        if builderTFM.HalfTurns.HalfTurns_to_apertures.all() != reference_HalfTurns_to_ap.all():
            raise Exception(
                f'Attribute HalfTurns_to_apertures for turns_to_sections != None does not correspond to '
                f'its reference value: {reference_HalfTurns_to_ap}')
        # In the model circuit yaml file turns_to_sections != None so strands_to_sections in the dataclasses should follow
        #  the new turns_to_sections division. strands_to_apertures should instead not change comparing to the previous case.
        strands_to_sections = np.repeat(builderTFM.HalfTurns.HalfTurns_to_sections, self.local_HalfTurns['n_strands'])
        if builderTFM.HalfTurns.HalfTurns_to_sections.all() != strands_to_sections.all():
            raise Exception(
                f'Attribute strands_to_sections for turns_to_sections != None does not correspond to: '
                f'{strands_to_sections}')
        if builderTFM.Strands.strands_to_apertures.all() != reference_strands_to_ap.all():
            raise Exception(
                f'Attribute strands_to_apertures for turns_to_sections != None does not correspond to '
                f'its reference value: {reference_strands_to_ap}')


    def test_calculateInductanceSections(self):
        """
            Tests if __calculate_Inductance_Sections function works properly.
            Checks if the following data have the correct values:
                - L_mag attribute in General dataclass
                - inductance_to_section attribute in General dataclass
                - dict returned by __calculate_Inductance_Sections
        """
        L_mag_ref = 0.0366395
        inductance_to_section_ref = np.array([[0.02068383, 0.], [0., 0.02068383]])

        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM, _ = bM_TFM.buildTFM(builderTFM= 0 , local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False)

        _ = builderTFM._calculate_Inductance_Sections()
        inductance_to_sections_dict = builderTFM.General.inductance_to_sections


        if round(builderTFM.General.L_mag, 7) != L_mag_ref:
            raise Exception(f'Value of L_mag attribute in dataclass General {round(builderTFM.General.L_mag, 7)} does not correspond to its reference value: {L_mag_ref}')
        if not np.array_equal(np.round(inductance_to_sections_dict, 6), np.round(inductance_to_section_ref, 6)):
            raise Exception(
                f'Value of inductance_to_section attribute in dataclass General does not correspond to its expected value: {inductance_to_section_ref}')


    def test_Shorts(self):
        """
            Adds a section to short and its corresponding resistance value to the corresponding keys
            sections_to_short and short_resistances of the input yaml file and checks if the corresponding short is
            properly written in the output .lib file
        """
        # Taking the .yaml file of the corresponding circuit
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))
        magnet_TFM_name = next(iter(TFM_data.magnets_TFM.keys()))

        # Introduces shorts across section 1
        magnet_TFM.magnet_Shorts.sections_to_short = ['1']
        magnet_TFM.magnet_Shorts.short_resistances = ['0.01']
        magnet_TFM.circuit_name = 'x_Magnet_1'


        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        # Creates output path
        output_path = os.path.join('output', 'BuilderTFM')
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f'Directory {output_path} created')
        output_path_TFM = Path(os.path.join(output_path, f'{magnet_TFM_name}.lib')).resolve()
        # Launches TFM: build + generate library
        builderTFM, _ = bM_TFM.buildTFM(builderTFM = 0, local_library_path=local_library_path, TFM_inputs=TFM_inputs, magnet_data=magnet_TFM,
                        verbose=False, output_path=output_path_TFM, circuit_data=bM_circuit.circuit_data)

        # Check if the short resistance has been added to the .lib file
        with open(output_path_TFM, 'r') as file:
            contents_lines = file.readlines()
            flag_ShortFound = False
            flag_ShortValue = False
            for line in contents_lines:
                if f'R_short_Section_{magnet_TFM.magnet_Shorts.sections_to_short[0]}' in line:
                    flag_ShortFound = True
                    if magnet_TFM.magnet_Shorts.short_resistances[0] in line:
                        flag_ShortValue = True
                    break
            if not flag_ShortFound:
                raise Exception(f'Short R_short_Section_{magnet_TFM.magnet_Shorts.sections_to_short} not added to the output .lib file')
            else:
                if not flag_ShortValue:
                    raise Exception(f'Value of short R_short_Section_{magnet_TFM.magnet_Shorts.sections_to_short} != {magnet_TFM.magnet_Shorts.short_resistances[0]}')


    def test_calculate_CapacitanceToGround_sections(self):
        """
        Test a fictional network consisting of 4 inductances and capacitances in series.
        Verify that when combining the first two inductances, the resulting Zout is equivalent to the impedance of the
        original circuit.

        To calculate the Zout of the equivalent circuit, the function '_calculate_Ceq' is first called to derive the
        expression for Zout with Leq = L1 + L2 and Ceq as a symbol.
        Next, the equation Z_out_original = Z_out_eq is solved for ZCeq to find the value of Ceq at each frequency that
        matches the impedance of the original circuit.
        As a double check, the equivalent network (L1eq = L1 + L2, Ceq as determined, n_inductances = 3) is passed into
        '_calculate_Zout', and the resulting Zout is compared with the original impedance at each frequency.
        
        The test passes if the imaginary part of the impedance values at each frequency, rounded to three decimal places,
        are equal.
        """
        # Taking the .yaml file of the corresponding circuit
        file_model_data_circuit = os.path.join('model_library', 'circuits', 'circuit_MBRD_TFM', 'input',
                                               'modelData_circuit_MBRD_TFM.yaml')
        # Building the circuit model
        bM_circuit = BuilderModel(file_model_data=file_model_data_circuit, case_model='circuit')
        # Extracting from the circuit data the TFM ones
        TFM_data = bM_circuit.circuit_data.TFM
        # Creating a copy of the TFM object and removing the magnet entry
        TFM_inputs = copy.deepcopy(TFM_data)
        del TFM_inputs.magnets_TFM
        # Retrieving the magnet attribute from the TFM data
        magnet_TFM = next(iter(TFM_data.magnets_TFM.values()))

        # Taking the local library path corresponding to the magnet in TFM
        local_library_path = os.path.join('model_library', 'magnets', f'{magnet_TFM.name}', 'input')
        file_model_data_MBRD = os.path.join(local_library_path, f'modelData_{magnet_TFM.name}.yaml')
        bM_TFM = BuilderModel(file_model_data=file_model_data_MBRD, case_model='magnet')
        builderTFM, _ = bM_TFM.buildTFM(builderTFM=0, local_library_path=local_library_path, TFM_inputs=TFM_inputs,
                                        magnet_data=magnet_TFM, verbose=False)

        # Initializing the inductors and capacitors values of the circuit
        # Creating the capacitance matrix for the circuit
        C_matrix = np.array([ [1.05e-07/2, 0, 0, 0, 0, 0, 0, 0],
                                [0, 1.05e-07/2, 0, 0, 0, 0, 0, 0],
                                [0, 0, 1.05e-07/2, 0, 0, 0, 0, 0],
                                [0, 0, 0, 1.05e-07/2, 0, 0, 0, 0],
                                [0, 0, 0, 0, 1.05e-07/2, 0, 0, 0],
                                [0, 0, 0, 0, 0, 1.05e-07/2, 0, 0],
                                [0, 0, 0, 0, 0, 0, 1.05e-07/2, 0],
                                [0, 0, 0, 0, 0, 0, 0, 1.05e-07/2] ])
        # Define the M_block as a 4x4 matrix (for inductances only here)
        M_block = np.array([[0.00915, 0, 0, 0],
                   [0, 0.00915, 0, 0],
                   [0, 0, 0.00915, 0],
                   [0, 0, 0, 0.00915]])
        # Imposing fL = 1 and l_mag = 1
        fL = 1
        l_mag = 1
        # Imposing to have fL = 1 and l_mag = 1
        n_turns = 4
        n_sections = 3
        el_order_turns = np.array([1, 2, 3, 4])  # Initializing the turns order in the network
        turns_to_sections = [1, 1, 2, 3]
        el_order_sections = np.array([1, 2, 3])

        # Modifying the parameters in BuilderTFM to obtain the same circuit
        builderTFM.flag_frequency_capacitance = False
        builderTFM.HalfTurns.M_block = M_block
        builderTFM.HalfTurns.C_matrix = C_matrix
        builderTFM.fL = fL
        builderTFM.General.magnet_length = l_mag
        builderTFM.General.L_mag = np.sum(M_block)
        builderTFM.General.C_ground = np.sum(C_matrix)
        builderTFM.General.num_HalfTurns = n_turns * 2
        builderTFM.General.sections = n_turns
        builderTFM.General.el_order_turns = el_order_turns
        builderTFM.General.el_order_sections = el_order_sections
        builderTFM.General.inductance_to_sections = M_block
        builderTFM.Turns.turns_to_sections = el_order_turns

        # Calculating the impedance of the original circuit
        Z_out_orig_value = builderTFM._calculate_Zout(capacitors=np.array([1.05e-07, 1.05e-07, 1.05e-07, 1.05e-07, 1.05e-07]))

        # Setting the parameters for the equivalent circuit
        inductance_to_sections = np.array([[0.00915 * 2, 0, 0],
                                           [0, 0.00915, 0],
                                           [0, 0, 0.00915]])
        builderTFM.Turns.turns_to_sections = turns_to_sections
        builderTFM.General.inductance_to_sections = inductance_to_sections
        builderTFM.General.sections = n_sections

        builderTFM._calculate_CapacitanceToGround_sections()
        # Retrieving the new capacitors found
        C_sections = builderTFM.General.C_ground_el_order_sections

        # Setting the new inputs for the equivalent circuit
        builderTFM.HalfTurns.M_block = inductance_to_sections
        builderTFM.General.num_HalfTurns = n_sections * 2
        builderTFM.General.el_order_turns = np.array([1, 2, 3])
        builderTFM.Turns.turns_to_sections = np.array([1, 2, 3])

        # Calculating the impedance of the equivalent circuit (Leq = L1 + L2, C from builderTFM.General.capacitance_to_sections, 3 turns)
        C_sections.append(1.05e-07)
        Z_out_eq_value = builderTFM._calculate_Zout(capacitors=C_sections)

        count_errors = 0
        list_freq_errors = []

        for i in range(len(builderTFM.frequency_list_capacitance)):
            if round(Z_out_orig_value[i].imag, 3) != round(Z_out_eq_value[i].imag, 3):
                count_errors += 1
                list_freq_errors.append(builderTFM.frequency[i])
                if count_errors > 2:
                    raise Exception("The impedance value of the original circuit does not match that of the equivalent circuit for at least two frequency values.")
                    for freq in list_freq_errors:
                        print(f"Frequency with mismatch: {freq}\n")












