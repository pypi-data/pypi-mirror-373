import unittest
import os

class TestParserSIGMA(unittest.TestCase):

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


    def test_dummy(self):
        """
            This is a dummy test to check the correct running of the CI pipeline
        """
        # arrange
        a = 1
        b = 1

        # act
        c = a == b

        # assert
        self.assertTrue(c)