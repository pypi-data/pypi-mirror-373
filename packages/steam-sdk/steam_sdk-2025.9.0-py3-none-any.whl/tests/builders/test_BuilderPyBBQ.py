import unittest
import os
import numpy as np
import yaml
from pathlib import Path

from steam_sdk.data.DataModelMagnet import *
from steam_sdk.builders.BuilderPyBBQ import BuilderPyBBQ
from tests.TestHelpers import assert_two_parameters


class TestBuilderPyBBQ(unittest.TestCase):

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
            'insulation_thickness': 0.0012,
        }

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_BuilderPyBBQ_init(self):
        """
            Check that DataPyBBQ object can be initialized
        """
        # arrange

        # act
        bPyBBQ = BuilderPyBBQ(flag_build=False)

        # assert
        self.assertEqual(hasattr(bPyBBQ, 'verbose'), True)
        self.assertEqual(hasattr(bPyBBQ, 'model_data'), True)
        self.assertEqual(hasattr(bPyBBQ, 'data_PyBBQ'), True)


    def test_setAttribute(self):
        """
            **Test that setAttribute works**
        """
        # arrange
        bPyBBQ = BuilderPyBBQ(flag_build=False)

        for parameter in self.local_Inputs:
            true_value = self.local_Inputs[parameter]
            setattr(bPyBBQ.data_PyBBQ, parameter, true_value)
            # act
            test_value = bPyBBQ.getAttribute('data_PyBBQ', parameter)
            # assert
            assert_two_parameters(true_value, test_value)


    def test_getAttribute(self):
        """
            **Test getAttribute works**
        """
        # arrange
        bPyBBQ = BuilderPyBBQ(flag_build=False)

        for parameter in self.local_Inputs:
            true_value = self.local_Inputs[parameter]
            # act
            bPyBBQ.setAttribute('data_PyBBQ', parameter, true_value)
            test_value = getattr(bPyBBQ.data_PyBBQ, parameter)
            # assert
            assert_two_parameters(true_value, test_value)


    def test_translateModelDataToPyBBQ(self):
        """
            Check that calcElectricalOrder calculates correctly. The test use-case if for MQXF_V2
        """
        # arrange
        model_data = DataModelMagnet()
        bPyBBQ = BuilderPyBBQ(input_model_data=model_data, flag_build=False)

        # act
        bPyBBQ.translateModelDataToPyBBQ()

        # assert
        self.assertEqual(hasattr(bPyBBQ.data_PyBBQ, 'B0_dump'), True)
        self.assertEqual(hasattr(bPyBBQ.data_PyBBQ, 'uniquify_path'), True)
        # TODO: Add all keys
