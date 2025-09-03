import unittest
import os
import numpy as np
import yaml
from pathlib import Path

from steam_sdk.builders.BuilderProteCCT import BuilderProteCCT
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from tests.TestHelpers import assert_two_parameters


class TestBuilderProteCCT(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # TODO: Add a test that uses actual values defined here
        # Define Inputs parameters that are equal to input file
        self.local_Inputs = {
            'TOp': 1.9,
        }

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_BuilderProteCCT_init(self):
        """
            Check that DataProteCCT object can be initialized
        """
        # arrange

        # act
        bProteCCT = BuilderProteCCT(flag_build=False)

        # assert
        self.assertEqual(hasattr(bProteCCT, 'verbose'), True)
        self.assertEqual(hasattr(bProteCCT, 'model_data'), True)
        self.assertEqual(hasattr(bProteCCT, 'Inputs'), True)

    def test_setAttribute(self):
        """
            **Test that setAttribute works**
        """
        # arrange
        bProteCCT = BuilderProteCCT(flag_build=False)

        for parameter in self.local_Inputs:
            true_value = self.local_Inputs[parameter]
            setattr(bProteCCT.Inputs, parameter, true_value)
            # act
            test_value = bProteCCT.getAttribute('Inputs', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

    def test_getAttribute(self):
        """
            **Test getAttribute works**
        """
        # arrange
        bProteCCT = BuilderProteCCT(flag_build=False)

        for parameter in self.local_Inputs:
            true_value = self.local_Inputs[parameter]
            # act
            bProteCCT.setAttribute('Inputs', parameter, true_value)
            test_value = getattr(bProteCCT.Inputs, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

    def test_translateModelDataToProteCCT(self):
        """
            Check that calcElectricalOrder calculates correctly. The test use-case if for MQXF_V2
        """
        # arrange
        model_data = DataModelMagnet()
        bProteCCT = BuilderProteCCT(input_model_data=model_data, flag_build=False)

        # act: commented out because translateModelDataToProteCCT() should be called only if flag_build=True, otherwise provide a reference object for model_data
        # bProteCCT.translateModelDataToProteCCT()

        # assert
        # TODO: Check that all keys are correctly passed

    def test_loadConductorData(self):
        """
            Test loadConductorData with content from modelData_MCBRD.yaml
        """
        # arrange
        magnet_name = 'MCBRD'
        file_model_data = os.path.join('model_library', 'magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
        dictionary = yaml.safe_load(open(file_model_data))
        inputModelData = DataModelMagnet(**dictionary)

        bProteCCT = BuilderProteCCT(input_model_data=inputModelData, flag_build=False, verbose=True)

        bProteCCT.translateModelDataToProteCCT()

        # act
        bProteCCT.loadConductorData()

        # assert
        expected_fCu   = 0.541284403669725
        calculated_fCu = bProteCCT.getAttribute('Inputs', 'CuFraction')
        self.assertAlmostEqual(expected_fCu, calculated_fCu, delta=1E-6*expected_fCu)

