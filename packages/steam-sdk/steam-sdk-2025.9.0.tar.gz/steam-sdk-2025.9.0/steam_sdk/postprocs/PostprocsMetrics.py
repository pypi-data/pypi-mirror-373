import re
from typing import List
import numpy as np
from steam_sdk.viewers.Viewer import Viewer

class PostprocsMetrics:

    """
        Class to calculate metrics
    """

    metrics_result: List = []

    def __init__(self, metrics_to_do: List[str] = [], var_to_interpolate: list = [], var_to_interpolate_ref: list = [],
                 time_vector: list = [], time_vector_ref: list = [], flag_run: bool = True):
        #TODO change argument names

        """
            Object gets initialized with the metrics which should be done, the variables and time_vectors to
            do the metrics on and a flag if the metrics should be done can be set to false
        """
        
        # Define inputs
        self.metrics_to_do = metrics_to_do
        self.var_to_interpolate = var_to_interpolate
        self.var_to_interpolate_ref = var_to_interpolate_ref
        self.time_vector = time_vector
        self.time_vector_ref = time_vector_ref

        # Convert variables to a list if needed
        self.var_to_interpolate = self._convert_to_list(self.var_to_interpolate)
        self.var_to_interpolate_ref = self._convert_to_list(self.var_to_interpolate_ref)
        self.time_vector = self._convert_to_list(self.time_vector)
        self.time_vector_ref = self._convert_to_list(self.time_vector_ref)

        if flag_run:
            self.run_metrics()

    def run_metrics(self):
        """
            Function to initiate interpolation, start the different metrics and append the result to the output
        """
        # variables which need to be interpolated
        list_metrics_that_need_interpolation = ['maximum_abs_error', 'RMSE', 'RELATIVE_RMSE', 'RMSE_ratio',
                                                'RELATIVE_RMSE_AFTER_t_PC_off','RELATIVE_RMSE_IN_INTERVAL_0_100',
                                                'MARE','MARE_1S', 'MARE_AFTER_t_PC_off']
         # For metrics that need interpolation of both simulation data and reference data:
        if any(n in self.metrics_to_do for n in set(list_metrics_that_need_interpolation)):

            # Clean arrays
            var_to_interpolate_cleaned, time_vector_cleaned = self.clean_array_touple(
                self.var_to_interpolate,
                self.time_vector)
            var_to_interpolate_ref_cleaned, time_vector_ref_cleaned = self.clean_array_touple(
                self.var_to_interpolate_ref,
                self.time_vector_ref)

            var_of_interest_overlap, time_stamps_overlap, var_ref_overlap = self.get_overlap(
                time_vector_ref=time_vector_ref_cleaned,time_vector_interest = time_vector_cleaned,
                var_ref = var_to_interpolate_ref_cleaned,var_interest = var_to_interpolate_cleaned)

            # Use only this region of the overlap to calculate the metrics:
            var_of_interest = np.array(var_of_interest_overlap)
            var_ref = np.array(var_ref_overlap)
            time_stamps_overlap = np.array(time_stamps_overlap)
            time_vector = np.array(time_vector_cleaned)
            time_vector_ref = np.array(time_vector_ref_cleaned)
        else:
            var_of_interest = np.array(self.var_to_interpolate)
            var_ref  = np.array(self.var_to_interpolate_ref)
            time_vector = np.array(self.time_vector)
            time_vector_ref = np.array(self.time_vector_ref)

        # evaluating which metrics will be done and appending results to metrics_result
        self.metrics_result = []
        for metric in self.metrics_to_do:
            if metric == 'maximum_abs_error':
                result = self._maximum_abs_error(var_of_interest,var_ref )
            elif metric == 'RMSE':
                result = self._RMSE(var_of_interest, var_ref)
            elif metric == 'RELATIVE_RMSE':
                result = self._RELATIVE_RMSE(var_of_interest, var_ref)
            elif metric == 'RELATIVE_RMSE_AFTER_t_PC_off':
                result = self._RELATIVE_RMSE_AFTER_t_PC_off(var_of_interest, var_ref,time_stamps_overlap)
            elif metric == 'RELATIVE_RMSE_IN_INTERVAL_0_100':
                result = self._RELATIVE_RMSE_IN_INTERVAL_0_100(var_of_interest, var_ref,time_stamps_overlap)
            elif metric == 'RMSE_ratio':
                result = self._RMSE_ratio(var_of_interest, var_ref)
            elif metric == 'MARE':
                result = self._MARE(var_of_interest, var_ref) # Calculate Mean Absolute Relative Error (MARE)
            elif metric == 'MARE_AFTER_t_PC_off':
                result = self._MARE_AFTER_t_PC_off(var_of_interest, var_ref,time_stamps_overlap)
            elif metric == 'MARE_1S':
                result = self._MARE_1S(var_of_interest,var_ref,time_stamps_overlap)
            elif metric == 'quench_load_error':
                result = self._quench_load_error(time_vector, var_of_interest, time_vector_ref, var_ref)
            elif metric == 'quench_load':
                result = self._quench_load(time_vector, var_of_interest)
            elif metric == 'max':
                result = self._peak_value(var_of_interest)
            else:
                raise Exception(f'Metric {metric} not understood!')
            self.metrics_result.append(result)

    # calculating metrics
    @staticmethod
    def _interpolation(linspace_time_stamps, time_vector, var_to_interpolate):

        """
            function to interpolate a variable
        """

        return np.interp(linspace_time_stamps, time_vector, var_to_interpolate) if len(
            var_to_interpolate) != 0 else []

    @staticmethod
    def _maximum_abs_error(y, y_ref)-> float:
        """
            function to calculate the absolute error between simulation and measurement
        """

        return float(max(abs(y - y_ref)))

    @staticmethod
    def _RMSE(y, y_ref)-> float:

        """
            function to calculate the RMSE between simulation and measurement
        """

        return float(np.sqrt(((y - y_ref) ** 2).mean()) )# np.sqrt(mean_squared_error(y, y_ref))

    @staticmethod
    def _RELATIVE_RMSE(y, y_ref)-> float:
        """
            function to calculate the RMSE between simulation and measurement, but normalized to the maximum reference value
        """
        avoid_zero_division = 1e-10
        max_abs_y_ref = np.max(np.abs(y_ref)) + avoid_zero_division
        RELATIVE_RMSE = np.sqrt(((y - y_ref) ** 2).mean())/max_abs_y_ref

        return float(RELATIVE_RMSE) # np.sqrt(mean_squared_error(y, y_ref))

    @staticmethod
    def _RELATIVE_RMSE_AFTER_t_PC_off(y, y_ref,time_stamps_overlap)-> float:
        """
        Calculate the relative RMSE after t_PC_off.

        Parameters:
        - y: Array-like, observed values.
        - y_ref: Array-like, reference values.
        - time_stamps_overlap: Array-like, time stamps corresponding to the overlap between y and y_ref.

        Returns:
        - float: Relative RMSE calculated after t_PC_off.

        This function calculates the relative Root Mean Square Error (RMSE) between observed values (y)
        and reference values (y_ref) after the t_PC_off time point. It considers only the data points
        occurring after t_PC_off for the calculation.
        RMSE is set into relation to the maximum value of the reference dataset.
        """
        y_after_t_PC_off = []
        y_ref_after_t_PC_off = []

        for index, timestamp in enumerate(time_stamps_overlap):
            if (0 <= timestamp):
                y_after_t_PC_off.append(y[index])
                y_ref_after_t_PC_off.append(y_ref[index])

        y_after_t_PC_off = np.array(y_after_t_PC_off)
        y_ref_after_t_PC_off = np.array(y_ref_after_t_PC_off)

        avoid_zero_division = 1e-10
        max_abs_y_ref_after_t_PC_off = np.max(np.abs(y_ref_after_t_PC_off)) + avoid_zero_division
        RELATIVE_RMSE_AFTER_t_PC_off = np.sqrt(((y_after_t_PC_off - y_ref_after_t_PC_off) ** 2).mean()) / max_abs_y_ref_after_t_PC_off

        return float(RELATIVE_RMSE_AFTER_t_PC_off)

    @staticmethod
    def _MARE_AFTER_t_PC_off(y, y_ref, time_stamps_overlap) -> float:
        """
        Calculate the Mean Average Relative Error after t_PC_off.

        Parameters:
        - y: Array-like, observed values.
        - y_ref: Array-like, reference values.
        - time_stamps_overlap: Array-like, time stamps corresponding to the overlap between y and y_ref.

        Returns:
        - float: MARE calculated after t_PC_off.

        This function calculates the MARE between observed values (y)
        and reference values (y_ref) after the t_PC_off time point. It considers only the data points
        occurring after t_PC_off for the calculation.
        """
        y_after_t_PC_off = []
        y_ref_after_t_PC_off = []

        for index, timestamp in enumerate(time_stamps_overlap):
            if (0 <= timestamp):
                y_after_t_PC_off.append(y[index])
                y_ref_after_t_PC_off.append(y_ref[index])

        y_after_t_PC_off = np.array(y_after_t_PC_off)
        y_ref_after_t_PC_off = np.array(y_ref_after_t_PC_off)

        avoid_zero_division = 1e-10
        MARE = np.abs((y_after_t_PC_off - y_ref_after_t_PC_off)/(y_ref_after_t_PC_off+avoid_zero_division)).mean()
        return float(MARE)

    @staticmethod
    def _RELATIVE_RMSE_IN_INTERVAL_0_100(y, y_ref,time_stamps_overlap)-> float:
        """
        Calculate the relative RMSE in a time interval from 0 to 100 seconds after t_PC_off.

        Parameters:
        - y: Array-like, observed values.
        - y_ref: Array-like, reference values.
        - time_stamps_overlap: Array-like, time stamps corresponding to the overlap between y and y_ref.

        Returns:
        - float: Relative RMSE calculated within the specified time interval.

        This function calculates the relative Root Mean Square Error (RMSE) between observed values (y)
        and reference values (y_ref) within a specified time interval [0, 100] seconds after t_PC_off.
        It considers only the data points within this time interval for the calculation.
        RMSE is set into relation to the maximum value of the reference dataset.
        """
        y_intervall = []
        y_ref_intervall = []

        for index, timestamp in enumerate(time_stamps_overlap):
            if (0 <= timestamp and timestamp <=100) :
                y_intervall.append(y[index])
                y_ref_intervall.append(y_ref[index])

        y_intervall = np.array(y_intervall)
        y_ref_intervall = np.array(y_ref_intervall)

        avoid_zero_division = 1e-10
        max_abs_y_ref_intervall = np.max(np.abs(y_ref_intervall)) + avoid_zero_division
        RELATIVE_RMSE_AFTER_t_PC_off = np.sqrt(((y_intervall - y_ref_intervall) ** 2).mean()) / max_abs_y_ref_intervall

        return float(RELATIVE_RMSE_AFTER_t_PC_off)  # np.sqrt(mean_squared_error(y, y_ref))

    @staticmethod
    def _MARE(y,y_ref) -> float:
        "Calculate Mean Absolute Relative Error (MARE)"
        avoid_zero_division = 1e-10
        MARE = np.abs((y - y_ref)/(y_ref+avoid_zero_division)).mean()
        return float(MARE)

    def _MARE_1S(self, y,y_ref,time_stamps_overlap)-> float:
        "Calculate Mean Absolute Relative Error (MARE) 1S arround the switchoff time t_PC_off"
        y_around_t_PC_off = []
        y_ref_around_t_PC_off = []

        for index, timestamp in enumerate(time_stamps_overlap):
            if(-1 <= timestamp <= 1):
                y_around_t_PC_off.append(y[index])
                y_ref_around_t_PC_off.append(y_ref[index])

        y_around_t_PC_off = np.array(y_around_t_PC_off)
        y_ref_around_t_PC_off = np.array(y_ref_around_t_PC_off)

        avoid_zero_division = 1e-10
        MARE_1S_AROUND_T_PC_OFF = np.abs((y_around_t_PC_off - y_ref_around_t_PC_off)/(y_ref_around_t_PC_off+avoid_zero_division)).mean()
        return float(MARE_1S_AROUND_T_PC_OFF)

    def _RMSE_ratio(self, y, y_ref)-> float:

        """
            function to calculate the RMSE divided by the peak value of the measurement between simulation and measurement
        """

        return float(np.sqrt(((y - y_ref) ** 2).mean())/self._peak_value(y_ref))

    def _quench_load_error(self, time_vector, Ia, time_vector_ref, Ia_ref)-> float:

        """
            function to calculate the quench load error between simulation and measurement
        """

        return float(self._quench_load(time_vector, Ia) - self._quench_load(time_vector_ref, Ia_ref))

    @staticmethod
    def _quench_load(time_vector, Ia)-> float:

        """
            function to calculate the quench load of a current
        """

        dt = [*np.diff(time_vector), 0]
        quench_load_sum = np.cumsum((Ia ** 2) * dt)
        quench_load = quench_load_sum[-1]

        return float(quench_load)

    @staticmethod
    def _peak_value(signal)-> float:

        """
            function to calculate the peak value of a signal
        """

        return float(max(signal))

    @staticmethod
    def clean_array_touple(array1, array2):
        # If in the touples of timestep and datapoint at least one value is NaN, then we remove the whole row from both lists
        array1_cleaned, array2_cleaned = zip(*[var_pair for var_pair in zip(array1, array2) if
                                               all((isinstance(value, (int, float)) and not np.isnan(value)) for value
                                                   in var_pair)])
        return list(array1_cleaned), list(array2_cleaned)

    @staticmethod
    def _convert_to_list(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    @staticmethod
    def get_overlap(time_vector_ref, time_vector_interest, var_ref, var_interest):
        # create a sample set of equally spaced timepoints that has the intervall and resolution of the reference data
        equally_spaced_timestamps = np.linspace(time_vector_ref[0], time_vector_ref[-1],
                                                num=len(time_vector_ref))
        # interpolate both variables to these timestamps
        var_interest_interpolatet = np.interp(equally_spaced_timestamps, time_vector_interest, var_interest)
        var_ref_interpolatet = np.interp(equally_spaced_timestamps, time_vector_ref, var_ref)
        # outside this region, the interpolation might be very wrong:
        # Determine start and end of the reference dataset
        start_ref = min(time_vector_ref)
        end_ref = max(time_vector_ref)
        # Determine start and end of the simulated dataset
        start_interest = min(time_vector_interest)
        end_interest = max(time_vector_interest)
        # Determine their overlap
        end_overlap = min(end_ref, end_interest)
        start_overlap = max(start_ref, start_interest)
        var_of_interest_overlap, time_stamps_overlap, var_ref_overlap = [], [], []
        for index, timestep in enumerate(equally_spaced_timestamps):
            if (start_overlap <= timestep and timestep <= end_overlap):
                var_of_interest_overlap.append(var_interest_interpolatet[index])
                var_ref_overlap.append(var_ref_interpolatet[index])
                time_stamps_overlap.append(equally_spaced_timestamps[index])

        return var_of_interest_overlap, time_stamps_overlap, var_ref_overlap
