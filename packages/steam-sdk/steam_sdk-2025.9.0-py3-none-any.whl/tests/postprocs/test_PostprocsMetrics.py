import unittest
import os
import numpy as np
from matplotlib import pyplot as plt

from steam_sdk.postprocs.PostprocsMetrics import PostprocsMetrics



class TestPostprocsMetrics(unittest.TestCase):

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


    def test_peak_value(self):

        """
            function to test the peak value function
        """

        # arrange
        metrics_to_do = ['max']
        var_to_interpolate = [0, 4, 6, 3.78, 2, 100.1, 6]

        # act
        metrics = PostprocsMetrics(metrics_to_do = metrics_to_do, var_to_interpolate = var_to_interpolate)
        peak_value = metrics.metrics_result

        # assert
        peak_reference = 100.1

        self.assertEqual(peak_value[0], peak_reference)
        print("The peak value is calculated correctly with {}.".format(peak_reference))

    def test_maximum_absolute_error(self):

        """
            function to test the maximum absolute error function
        """

        # arrange
        metrics_to_do = ['maximum_abs_error']
        var_to_interpolate = [0, 4, 6, 3.78, 2, 100.1, 6]
        var_to_interpolate_ref = [1, 15, 6, 200, 10, 9, 5]
        time_vector = [0, 0.5, 1, 1.5, 2, 2.5, 3]
        time_vector_ref = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        # act
        metrics = PostprocsMetrics(metrics_to_do = metrics_to_do, var_to_interpolate = var_to_interpolate, var_to_interpolate_ref = var_to_interpolate_ref, time_vector = time_vector, time_vector_ref = time_vector_ref)
        max_absolute_error = metrics.metrics_result[0]

        # assert
        max_absolute_error_reference = 196.22

        self.assertEqual(max_absolute_error, max_absolute_error_reference)
        print("The maximum_absolute_error is calculated correctly with {}.".format(max_absolute_error_reference))

    def test_RMSE(self):

        """
            function to test the RMSE function
        """

        # arrange
        metrics_to_do = ['RMSE']
        var_to_interpolate = [0.1, 1.2, 4.2, 5, 1.9, 10.1, 2.5]
        var_to_interpolate_ref = [0, 1.3, 4, 5, 2, 10, 2]
        time_vector = [0, 0.5, 1, 1.5, 2, 2.5, 3]
        time_vector_ref = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        # act
        metrics = PostprocsMetrics(metrics_to_do = metrics_to_do, var_to_interpolate = var_to_interpolate, var_to_interpolate_ref = var_to_interpolate_ref, time_vector = time_vector, time_vector_ref = time_vector_ref)
        RMSE = metrics.metrics_result[0]

        # assert
        RMSE_reference = 0.217124

        self.assertAlmostEqual(RMSE, RMSE_reference, delta = 1e-6)
        print("The RMSE is calculated correctly with {}.".format(RMSE_reference))

    def test_RMSE_ratio(self):

        """
            function to test the RMSE_ratio function
        """

        # arrange
        metrics_to_do = ['RMSE_ratio']
        var_to_interpolate = [0.1, 1.2, 4.2, 5, 1.9, 10.1, 2.5]
        var_to_interpolate_ref = [0, 1.3, 4, 5, 2, 10, 2]
        time_vector = [0, 0.5, 1, 1.5, 2, 2.5, 3]
        time_vector_ref = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        # act
        metrics = PostprocsMetrics(metrics_to_do = metrics_to_do, var_to_interpolate = var_to_interpolate, var_to_interpolate_ref = var_to_interpolate_ref, time_vector = time_vector, time_vector_ref = time_vector_ref)
        RMSE_ratio = metrics.metrics_result[0]

        # assert
        RMSE_ratio_reference = 0.0217124

        self.assertAlmostEqual(RMSE_ratio, RMSE_ratio_reference, delta = 1e-6)
        print("The RMSE_ratio is calculated correctly with {}.".format(RMSE_ratio_reference))

    def test_multiple(self):

        """
            function to test multiple functions which are part of PostprocsMetrics
        """

        # arrange
        metrics_to_do = ['quench_load', 'quench_load_error', 'RMSE']
        var_to_interpolate = [0.1, 1.2, 4.2, 5, 1.9, 10.1, 2.5]
        var_to_interpolate_ref = [0, 1.3, 4, 5, 2, 10, 2]
        time_vector = [0, 0.5, 1, 1.5, 2, 2.5, 3]
        time_vector_ref = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        # act
        metrics = PostprocsMetrics(metrics_to_do = metrics_to_do, var_to_interpolate = var_to_interpolate, var_to_interpolate_ref = var_to_interpolate_ref, time_vector = time_vector, time_vector_ref = time_vector_ref)
        metrics_result = metrics.metrics_result

        # assert
        metrics_result_reference = [74.855, 1.510001, 0.217124]

        np.testing.assert_almost_equal(metrics_result, metrics_result_reference, 6)
        print("The metric results are calculated correctly with {}.".format(metrics_result_reference))

    def test_RELATIVE_RMSE_AFTER_t_PC_off(self):
        metrics_to_do = ["RELATIVE_RMSE_AFTER_t_PC_off"]

        var_to_interpolate = [-10, -20 , "some_string", 1.2, 4.2, 5, 1.9, 10.1, 2.5, 2, 100]
        var_to_interpolate_ref = [0, 1.3, 4, 5.5, 2, 10, 2]
        time_vector = [-10, -20, 0, 0.5, 1, 1.5, "Nan", 2.5, 3, 10, 200]
        time_vector_ref = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        metrics = PostprocsMetrics(metrics_to_do=metrics_to_do, var_to_interpolate=var_to_interpolate,
                                   var_to_interpolate_ref=var_to_interpolate_ref, time_vector=time_vector,
                                   time_vector_ref=time_vector_ref)
        metrics_result = metrics.metrics_result

        print(metrics_result)

    def test_clean_array_touple(self):
        #arrange
        var_to_interpolate = [-10, -20, "some_string", 1.2, 4.2, 5, 1.9, 10.1, 2.5, 2, 100]
        var_to_interpolate_ref = [0, 1.3, 4, 5.5, 2, 10, 2]
        time_vector = [-10, -20, 0, np.nan, 1, 1.5, "Nan", 2.5, 3, 10, 200]
        time_vector_ref = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        var_to_interpolate_cleaned_TARGET = [-10, -20,  4.2, 5, 10.1, 2.5, 2, 100]
        time_vector_cleaned_TARGET = [-10, -20, 1, 1.5, 2.5, 3, 10, 200]
        var_to_interpolate_ref_cleaned_TARGET = [0, 1.3, 4, 5.5, 2, 10, 2]
        time_vector_ref_cleaned_TARGET = [0, 0.5, 1, 1.5, 2, 2.5, 3]

        #act
        var_to_interpolate_cleaned, time_vector_cleaned = PostprocsMetrics.clean_array_touple(var_to_interpolate,time_vector)
        var_to_interpolate_ref_cleaned, time_vector_ref_cleaned = PostprocsMetrics.clean_array_touple(var_to_interpolate_ref, time_vector_ref)

        #assert
        self.assertEqual(var_to_interpolate_cleaned, var_to_interpolate_cleaned_TARGET)
        self.assertEqual(var_to_interpolate_ref_cleaned ,var_to_interpolate_ref_cleaned_TARGET)

        self.assertEqual(time_vector_cleaned, time_vector_cleaned_TARGET)
        self.assertEqual(time_vector_ref_cleaned ,time_vector_ref_cleaned_TARGET)

    def test_return_time_overlap(self):
        # arrange
        Cleaned_var_to_interpolate = [-10, -20, 4.2, 5, 10.1, 2.5, 2, 100]
        Cleaned_var_to_interpolate_ref = [0, 1.3, 4, 5.5, 2, 10, 2]
        Cleaned_time_vector = [-10, -20, 1, 1.4, 2.3, 3, 10, 200]
        Cleaned_time_vector_ref = [0, 0.8, 1.2, 1.5, 2.2, 2.5, 3]

        var_of_interest_overlap_TARGET = [3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap_TARGET  = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap_TARGET = [0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]

        #act
        var_of_interest_overlap, time_stamps_overlap, var_ref_overlap = PostprocsMetrics.get_overlap(
            time_vector_ref=Cleaned_time_vector_ref, time_vector_interest=Cleaned_time_vector,
            var_ref=Cleaned_var_to_interpolate_ref, var_interest=Cleaned_var_to_interpolate)


        #assert
        self.assertEqual(var_of_interest_overlap, var_of_interest_overlap_TARGET)
        self.assertEqual(time_stamps_overlap, time_stamps_overlap_TARGET)
        self.assertEqual(var_ref_overlap, var_ref_overlap_TARGET)

        plt.plot(time_stamps_overlap, var_of_interest_overlap, marker='o', linestyle='-', color='black',
                 label='Variable of Interest --> overlap considered')
        plt.plot(time_stamps_overlap, var_ref_overlap, marker='o', linestyle='-', color='black',
                 label='Reference Variable --> overlap considered')
        plt.plot(Cleaned_time_vector, Cleaned_var_to_interpolate, marker='+', linestyle='--', color='blue',
                 label='Variable of Interest')
        plt.plot(Cleaned_time_vector_ref, Cleaned_var_to_interpolate_ref, marker='+', linestyle='--', color='green',
                 label='Reference Variable ')
        plt.legend()
        #For Debugging uncomment the following
        #plt.show()
        plt.close('all')

    def test_RELATIVE_RMSE_AFTER_t_PC_off(self):
        #arrange
        var_of_interest_overlap1 = [200, 5, 3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap1 = [-1000,- 1, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap1 = [500, 2, 0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]

        var_of_interest_overlap2 = [3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap2 = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap2 = [0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]

        Target_RMSE = 0.275937891220837 # EXPECTED Result from EXCELL

        #act
        metric1 = PostprocsMetrics._RELATIVE_RMSE_AFTER_t_PC_off(var_of_interest_overlap1, var_ref_overlap1,time_stamps_overlap1)
        metric2 = PostprocsMetrics._RELATIVE_RMSE_AFTER_t_PC_off(var_of_interest_overlap2, var_ref_overlap2,time_stamps_overlap2)

        print(metric1)
        print(metric2)

        #assert
        self.assertEqual(np.round(metric1,15), Target_RMSE)
        self.assertEqual(np.round(metric2,15), Target_RMSE)

    def test_RELATIVE_RMSE_IN_INTERVAL_0_100(self):
        # arrange
        var_of_interest_overlap1 = [500, 200, 5, 3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap1 = [1000, -1000,- 1, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap1 = [2000, 500, 2, 0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]

        var_of_interest_overlap2 = [2,3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap2 = [101,0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap2 = [1, 0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]


        Target_RMSE = 0.275937891220837  # EXPECTED Result from EXCELL

        # act
        metric1 = PostprocsMetrics._RELATIVE_RMSE_IN_INTERVAL_0_100(var_of_interest_overlap1, var_ref_overlap1,
                                                                 time_stamps_overlap1)
        metric2 = PostprocsMetrics._RELATIVE_RMSE_IN_INTERVAL_0_100(var_of_interest_overlap2, var_ref_overlap2,
                                                                 time_stamps_overlap2)

        # assert
        self.assertEqual(np.round(metric1, 15), Target_RMSE)
        self.assertEqual(np.round(metric2, 15), Target_RMSE)

    def test_MARE_AFTER_t_PC_off(self):
        #arrange
        var_of_interest_overlap1 = [200, 5, 3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap1 = [-1000,- 1, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap1 = [500, 2, 0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]

        var_of_interest_overlap2 = [3.047619047619044, 3.6238095238095234, 4.2, 5.566666666666667, 8.4, 7.928571428571427, 2.5]
        time_stamps_overlap2 = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        var_ref_overlap2 = [0.0, 0.8125, 2.6500000000000004, 5.5, 3.0000000000000004, 10.0, 2.0]

        Target_RMSE = 4.35374149750066900000E+09  # EXPECTED Result from EXCELL


        #act
        metric1 = PostprocsMetrics._MARE_AFTER_t_PC_off(var_of_interest_overlap1, var_ref_overlap1,time_stamps_overlap1)
        metric2 = PostprocsMetrics._MARE_AFTER_t_PC_off(var_of_interest_overlap2, var_ref_overlap2,time_stamps_overlap2)

        print(metric1)
        print(metric2)

        #assert
        self.assertEqual(np.round(metric1,15), Target_RMSE)
        self.assertEqual(np.round(metric2,15), Target_RMSE)


