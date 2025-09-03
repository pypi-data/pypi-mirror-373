import os
import unittest

from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.utils.rhasattr import rhasattr


class Test_rhasattr(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_hasattr_level1_true(self):
        # arrange
        model_data = DataModelMagnet()
        var_name = 'Sources'
        # act
        result = rhasattr(model_data, var_name)
        # assert
        self.assertTrue(result)

    def test_hasattr_level1_false(self):
        # arrange
        model_data = DataModelMagnet()
        var_name = 'not_existing'
        # act
        result = rhasattr(model_data, var_name)
        # assert
        self.assertFalse(result)

    def test_hasattr_level2_true(self):
        # arrange
        model_data = DataModelMagnet()
        var_name = 'Quench_Protection.CLIQ'
        # act
        result = rhasattr(model_data, var_name)
        # assert
        self.assertTrue(result)

    def test_hasattr_level2_false(self):
        # arrange
        model_data = DataModelMagnet()
        var_name = 'Quench_Protection.not_existing'
        # act
        result = rhasattr(model_data, var_name)
        # assert
        self.assertFalse(result)

    def test_hasattr_level3_true(self):
        # arrange
        model_data = DataModelMagnet()
        var_name = 'Quench_Protection.CLIQ.U0'
        # act
        result = rhasattr(model_data, var_name)
        # assert
        self.assertTrue(result)

    def test_hasattr_level3_false(self):
        # arrange
        model_data = DataModelMagnet()
        var_name = 'Quench_Protection.CLIQ.not_existing'
        # act
        result = rhasattr(model_data, var_name)
        # assert
        self.assertFalse(result)