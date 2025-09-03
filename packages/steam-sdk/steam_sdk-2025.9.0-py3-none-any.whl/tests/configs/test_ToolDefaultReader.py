import unittest
import os

from steam_sdk.configs.tools_defaults.ToolDefaultReader import ToolDefaultReader


class TestResourceReader(unittest.TestCase):

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


    def test_getResourceContent(self):
        # arrange
        resource = 'LEDET/file_used_for_testing.yaml'

        # act
        print(ToolDefaultReader.getResourceContent(resource))

    def test_getResourcePath(self):
        # arrange
        resource = 'LEDET/file_used_for_testing.yaml'

        # act
        print(ToolDefaultReader.getResourcePath(resource))