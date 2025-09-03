import unittest

from steam_sdk.utils.utils_PC import calculate_t_PC_off


class Test_utils_PC(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        print('')


    def test_t_PC_1(self):
        t_PC_off = calculate_t_PC_off(t_start=0, I_start=0, I_end=56.5+100, dI_dt=0.5, dI_dt_2=0.25, t_plateau=10, I_off=56.5)
        self.assertEqual(114, t_PC_off)

    def test_t_PC_2(self):
        t_PC_off = calculate_t_PC_off(t_start=10, I_start=0, I_end=56.5+100, dI_dt=0.5, dI_dt_2=0.25, t_plateau=10, I_off=56.5)
        self.assertEqual(124, t_PC_off)

    def test_t_PC_3(self):
        t_PC_off = calculate_t_PC_off(t_start=0, I_start=0, I_end=56.5+100, dI_dt=0.2, dI_dt_2=0.25, t_plateau=10, I_off=13)
        self.assertEqual(65.4, t_PC_off)

    def test_t_PC_3(self):
        t_PC_off = calculate_t_PC_off(t_start=100, I_start=5, I_end=[20, 50], dI_dt=[0.5, 0.125], dI_dt_2=[0.25, 0.125], t_plateau=[10, 10], I_off=49)
        self.assertEqual(374.5, t_PC_off)