import os
import unittest

from steam_sdk.utils.correct_RRR_NIST import correct_RRR_NIST


class Test_correct_RRR_NIST(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define number of digits to check in the assertAlmostEqual() function calls
        self.n_digits = 12

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_correct_RRR_NIST_01(self):
        RRR, T_ref_high, T_ref_low = 100, 273, 4
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_high, T_ref_low=T_ref_low)
        print(f'RRR={RRR}. T_ref_high={T_ref_high} K. T_ref_low={T_ref_low} K. f_correction_RRR={f_correction_RRR}. Corrected RRR={corrected_RRR}.')
        self.assertAlmostEqual(0.997013122011184, f_correction_RRR, self.n_digits)
        self.assertAlmostEqual(99.7013122011184, corrected_RRR, self.n_digits)

    def test_correct_RRR_NIST_02(self):
        RRR, T_ref_high, T_ref_low = 200, 273, 4
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_high, T_ref_low=T_ref_low)
        print(f'RRR={RRR}. T_ref_high={T_ref_high} K. T_ref_low={T_ref_low} K. f_correction_RRR={f_correction_RRR}. Corrected RRR={corrected_RRR}.')
        self.assertAlmostEqual(1.004308870008823, f_correction_RRR, self.n_digits)
        self.assertAlmostEqual(200.8617740017645, corrected_RRR, self.n_digits)

    def test_correct_RRR_NIST_03(self):
        RRR, T_ref_high, T_ref_low = 200, 293, 4
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_high, T_ref_low=T_ref_low)
        print(f'RRR={RRR}. T_ref_high={T_ref_high} K. T_ref_low={T_ref_low} K. f_correction_RRR={f_correction_RRR}. Corrected RRR={corrected_RRR}.')
        self.assertAlmostEqual(0.924132844845484, f_correction_RRR, self.n_digits)
        self.assertAlmostEqual(184.8265689690968, corrected_RRR, self.n_digits)

    def test_correct_RRR_NIST_04(self):
        RRR, T_ref_high, T_ref_low = 200, 293, 14
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_high, T_ref_low=T_ref_low)
        print(f'RRR={RRR}. T_ref_high={T_ref_high} K. T_ref_low={T_ref_low} K. f_correction_RRR={f_correction_RRR}. Corrected RRR={corrected_RRR}.')
        self.assertAlmostEqual(0.952195177694472, f_correction_RRR, self.n_digits)
        self.assertAlmostEqual(190.4390355388943, corrected_RRR, self.n_digits)

    def test_correct_RRR_NIST_05(self):
        RRR, T_ref_high, T_ref_low = 200, 273, 14
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_high, T_ref_low=T_ref_low)
        print(f'RRR={RRR}. T_ref_high={T_ref_high} K. T_ref_low={T_ref_low} K. f_correction_RRR={f_correction_RRR}. Corrected RRR={corrected_RRR}.')
        self.assertAlmostEqual(1.034805838004902, f_correction_RRR, self.n_digits)
        self.assertAlmostEqual(206.9611676009803, corrected_RRR, self.n_digits)

    def test_correct_RRR_NIST_06(self):
        RRR, T_ref_high, T_ref_low = 10, 283, 2
        f_correction_RRR, corrected_RRR = correct_RRR_NIST(RRR=RRR, T_ref_high=T_ref_high, T_ref_low=T_ref_low)
        print(f'RRR={RRR}. T_ref_high={T_ref_high} K. T_ref_low={T_ref_low} K. f_correction_RRR={f_correction_RRR}. Corrected RRR={corrected_RRR}.')
        self.assertAlmostEqual(0.852497948102330, f_correction_RRR, self.n_digits)
        self.assertAlmostEqual(8.524979481023305, corrected_RRR, self.n_digits)
