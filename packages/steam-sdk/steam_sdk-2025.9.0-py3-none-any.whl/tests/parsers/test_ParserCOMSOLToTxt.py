import os
import unittest
from pathlib import Path

from steam_sdk.parsers.ParserCOMSOLToTxt import ParserCOMSOLToTxt


class TestParserROXIE(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = Path(__file__).parent  # os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_getIronYokeDataFromIronFile(self):
        """
            Test the function loadTxtCOMSOL in ParserCOMSOLToTxt.py
        """
        reference_file = str(os.path.join(self.current_path, "references", "test_ParserCOMSOLToTxt_REFERENCE.txt"))
        df = ParserCOMSOLToTxt().loadTxtCOMSOL(reference_file)
        self.assertEqual(3, (len(df.columns)))
