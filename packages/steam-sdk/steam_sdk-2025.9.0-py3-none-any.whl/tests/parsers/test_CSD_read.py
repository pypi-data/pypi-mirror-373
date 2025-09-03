import unittest
import os
import matplotlib.pyplot as plt
import numpy as np

from steam_sdk.parsers.CSD_Reader import CSD_read
from steam_sdk.utils.misc import displayWaitAndClose


class TestCSDReader(unittest.TestCase):

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

        # Close all figures
        plt.close('all')


    def test_read_csd_timeDomain(self):
        # arrange
        file_name = os.path.join('input', 'test_csd_time.csd')
        selected_signals = ['I(r1_warm)', 'I(x_MB1.L1)']

        # act
        csd = CSD_read(file_name)
        time = csd.time
        data = csd.data
        signals = csd.signal_names
        print(signals)

        # assert
        self.assertEqual(signals[4], 'I(x_MB4.L1)')

    def test_read_csd_frequencyDomain(self):
        # arrange
        file_name = os.path.join('input', 'test_csd_frequency.csd')

        # act
        csd = CSD_read(file_name)
        freq = csd.time
        data = csd.data
        signals = csd.signal_names

        self.assertEqual(len(data[0]), 8)  # Check that Im and Re part are present for all signals present
        self.assertTrue((np.max(data)-3.4302132) < 0.1)  # Check that the max value of result does not fit anymore
        self.assertListEqual(list(data[0][0:2]), [-0.0012282481, -0.0092752867])
        self.assertEqual(signals[4], 'Re_V(E_AP1_voltage)')