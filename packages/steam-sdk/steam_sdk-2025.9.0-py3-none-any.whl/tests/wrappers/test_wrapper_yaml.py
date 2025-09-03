import unittest
import os

from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.wrappers.wrapper_yaml import yaml_dump_with_lists


class TestWrapperYaml(unittest.TestCase):

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


    def test_wrapper_yaml(self):
        '''
        # TODO
        '''

        # arrange
        data_model = DataModelMagnet()
        data_model.GeneralParameters.magnet_name = 'test'
        data_model.GeneralParameters.model.name: 'test_model_name'
        # data_dict = DataModelMagnet().__dict__
        dump_all_full_path = os.path.join('output', 'dumped_file_horizontal_lists.yaml')

        # act
        yaml_dump_with_lists(data_model=data_model, dump_all_full_path=dump_all_full_path)