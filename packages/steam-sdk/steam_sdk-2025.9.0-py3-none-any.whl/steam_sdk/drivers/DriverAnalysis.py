import multiprocessing
import os
import sys
import traceback
import warnings
from multiprocessing import freeze_support
from pathlib import Path
import numpy as np
import re

from steam_sdk.data.DataAnalysis import DataAnalysis
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.parsers.ParserYAML import model_data_to_yaml
from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.utils.read_settings_file import read_settings_file


class DriverAnalysis:
    """
    This driver is used to run a complete analysis file with a list of steps defined that are executed during run. At the moment this is used by Parametric simulations using Dakota (via driver_link.py).
    """
    def __init__(self, analysis_yaml_path: str = None, iterable_steps: list = None, sim_number_offset: int = None):
        """
         This driver is called by driver Dakota to run specified analysis
        :param analysis_yaml_path:
        :type analysis_yaml_path:
        :param iterable_steps:
        :type iterable_steps:
        """
        self.analysis_yaml_path = analysis_yaml_path
        self.iterable_steps = iterable_steps
        self.sim_number_offset = sim_number_offset

    def run(self, parameters_file=None, results_file=None):
        """
        This method is called by Python.exe via driver_link.py called by Dakota.exe
        :return: dictionary with results of dakota (indirectly via results_for_dakota.write() call) and directly 1 for Dakota to think it all went okay
        :rtype: int
        """

        data_analysis: DataAnalysis = yaml_to_data(self.analysis_yaml_path, DataAnalysis)
        data_analysis.AnalysisStepSequence = self.iterable_steps
        for step_name in data_analysis.AnalysisStepSequence:
            # --- modify steps of analysis according to dakota variables and values ---
            step = data_analysis.AnalysisStepDefinition[step_name]
            if step.type in ['ModifyModelMultipleVariables']:
                if 'Options_FiQuS.multipole.postproc.compare_to_ROXIE' in step.variables_to_change:
                    index = step.variables_to_change.index('Options_FiQuS.multipole.postproc.compare_to_ROXIE')
                    step.variables_value[index] = [str(Path(step.variables_value[index][0]).resolve())]
            elif step.type in ['ModifyModel']:
                if 'Options_FiQuS.multipole.postproc.compare_to_ROXIE' in step.variable_to_change:
                    index = step.variable_to_change.index('Options_FiQuS.multipole.postproc.compare_to_ROXIE')
                    step.variable_value[index] = str(Path(step.variable_value[index][0]).resolve())

        if data_analysis.GeneralParameters.flag_permanent_settings:  # use settings from analysis file
            data_settings: DataSettings = DataSettings(**data_analysis.PermanentSettings.model_dump())
        else:
            data_settings = read_settings_file(
                absolute_path_settings_folder=data_analysis.GeneralParameters.relative_path_settings,
                verbose=False)  # Information will be displayed later, to verbose=False here
        path_dakota_python = os.path.join(Path(data_settings.Dakota_path).parent.parent, 'share\dakota\Python')
        print('path_dakota_python:        {}'.format(path_dakota_python))
        sys.path.insert(0, path_dakota_python)      # this is ugly, but dakota does not distribute proper python library to use and install via PyPi
        from dakota.interfacing import read_parameters_file

        params, result_for_dakota = read_parameters_file(parameters_file=parameters_file, results_file=results_file)  # inputs, outputs

        # these variables are to automatically figure out which fiqus run level (geometry, mesh, solve) is involved in Dakota iterations
        def _level_FiQuS(var_dakota):
            geometry, mesh, solution = False, False, False
            options_fiqus = 'Options_FiQuS.'
            if options_fiqus in var_dakota and '.geometry.' in var_dakota:
                geometry = True
            if options_fiqus in var_dakota and '.mesh.' in var_dakota:
                mesh = True
            if options_fiqus in var_dakota and '.solve.' in var_dakota:
                solution = True
            if sum([geometry, mesh, solution])>1:
                _raise_exception_FiQuS()
            if geometry:
                return 'geometry'
            elif mesh:
                return 'mesh'
            else:
                return 'solve'
        def _check_modify_FiQuS(str1, str2):
            if str1 == str2 or str1 is None:
                return str2
            elif str1 is None:
                return str2
            else:
                _raise_exception_FiQuS()

        def _raise_exception_FiQuS():
            raise Exception(f'Driver Dakota implementation does not support simultaneous iterations through FiQuS geometries, meshes or solutions')

        fiqus_ModifyModel = None
        fiqus_ModifyModelMultipleVariables = None

        iteration_number = self.sim_number_offset + params.eval_num
        for step_name in data_analysis.AnalysisStepSequence:
            # --- modify steps of analysis according to dakota variables and values ---
            step = data_analysis.AnalysisStepDefinition[step_name]
            if step.type in ['ModifyModel']:
                for variable_dakota, value_dakota in params.items():
                    fiqus_ModifyModel = _level_FiQuS(variable_dakota)
                    if step.variable_to_change == variable_dakota:
                        step.variable_value = [value_dakota]

            elif step.type in ['ModifyModelMultipleVariables']:
                for variable_dakota, value_dakota in params.items():
                    fiqus_ModifyModelMultipleVariables = _level_FiQuS(variable_dakota)
                    for i, variable_to_change in enumerate(step.variables_to_change):
                        if variable_dakota == variable_to_change:
                            step.variables_value[i] = [value_dakota]
            if hasattr(step, "software"):
                if any(string == 'FiQuS' for string in step.software):
                    iteration_type_FiQuS = _check_modify_FiQuS(fiqus_ModifyModel, fiqus_ModifyModelMultipleVariables)

            # --- change the simulation number that the model is written with in order not to overwrite input file for the tool ---
            if step.type in ['ModifyModel', 'ModifyModelMultipleVariables', 'RunSimulation', 'ParsimEvent']:

                if len(step.simulation_numbers) == 0:
                    pass # this step is not writting the model, so leave it as is
                elif len(step.simulation_numbers) == 1:
                    step.simulation_numbers = [iteration_number]
                else:
                    raise Exception(f'Analysis file with multiple simulation numbers can not be used in dakota. Change {step_name}.simulation_numbers={step.simulation_numbers} to a list with single entry')
                if any(string == 'FiQuS' for string in step.software):
                    if step.type in ['ModifyModel']:
                        if all(s in step.variable_to_change for s in ['Options_FiQuS.run.type', f'Options_FiQuS.run.{iteration_type_FiQuS}']):
                            index = step.variable_to_change.index(f'Options_FiQuS.run.{iteration_type_FiQuS}')
                            if index > 0:
                                step.variable_value[index] = [iteration_number]
                    elif step.type in ['ModifyModelMultipleVariables']:
                        if all(s in step.variables_to_change for s in ['Options_FiQuS.run.type', f'Options_FiQuS.run.{iteration_type_FiQuS}']):
                            index = step.variables_to_change.index(f'Options_FiQuS.run.{iteration_type_FiQuS}')
                            if index > 0:
                                step.variables_value[index] = [iteration_number]

                if step.type == 'ParsimEvent':
                    # update the path to the temp viewer input file
                    pattern = r'\\(\d+)\\'
                    old_filepath_to_viewer_input = step.filepath_to_temp_viewer_csv
                    new_filepath_to_viewer_input = re.sub(pattern, fr'\\{iteration_number}\\', old_filepath_to_viewer_input)
                    if old_filepath_to_viewer_input == new_filepath_to_viewer_input:
                        warnings.warn("Step ParsimEvent: Temporary viewer input file is not simulation number specific "
                                      "--> add a simulation number to the filepath to make it iteratable")
                    step.filepath_to_temp_viewer_csv = new_filepath_to_viewer_input

                    old_path_output_event_csv = step.path_output_event_csv
                    new_path_output_event_csv = re.sub(pattern, fr'\\{iteration_number}\\',
                                                          old_path_output_event_csv)
                    if old_path_output_event_csv == new_path_output_event_csv:
                        warnings.warn("Step ParsimEvent: The path to the parsim sweep file to be written is not simulation "
                                      "number specific --> add a simulation number to the filepath to make it iteratable")
                    step.path_output_event_csv = new_path_output_event_csv


                    old_path_output_viewer_csv = step.path_output_viewer_csv
                    new_path_output_viewer_csv = re.sub(pattern, fr'\\{iteration_number}\\',
                                                       old_path_output_viewer_csv)
                    if old_path_output_viewer_csv== new_path_output_viewer_csv:
                        warnings.warn(
                            "Step ParsimEvent: The path to the viewer csv to be written is not simulation "
                            "number specific --> add a simulation number to the filepath to make it iteratable")
                    step.path_output_viewer_csv = new_path_output_viewer_csv


            if step.type == 'RunViewer':
                # update the path to the temp viewer input file
                pattern = r'\\(\d+)\\'
                old_file_name_transients = step.file_name_transients
                new_file_name_transients = re.sub(pattern, fr'\\{iteration_number}\\', old_file_name_transients)
                if old_file_name_transients == new_file_name_transients:
                    warnings.warn("Step RunViewer: Temporary viewer input file is not simulation number specific "
                                  "--> add a simulation number to the filepath to make it iteratable")
                step.file_name_transients = new_file_name_transients

                # update the path to the report --> Note: for this to work
                pattern = r'\\(\d+)\\'
                old_filepath_to_report = step.path_output_pdf_report
                new_filepath_to_report = re.sub(pattern, fr'\\{iteration_number}\\', old_filepath_to_report)
                if old_filepath_to_report == new_filepath_to_report:
                    warnings.warn("Step RunViewer: Path to report is not simulation number specific "
                                  "--> add a simulation number to the filepath to make it iteratable")
                step.path_output_pdf_report = new_filepath_to_report

            if step.type == 'CalculateMetrics':
                # update the path to the temp viewer input file
                if step.metrics_output_filepath:
                    pattern = r'\\(\d+)\\'
                    old_metrics_output_filepath = step.metrics_output_filepath
                    new_metrics_output_filepath = re.sub(pattern, fr'\\{iteration_number}\\', old_metrics_output_filepath)
                    if old_metrics_output_filepath == new_metrics_output_filepath:
                        warnings.warn("Step CalculateMetrics: Metrics_output_filepath key is not simulation number specific "
                                      "--> add a simulation number to the filepath to make it iteratable")
                    step.metrics_output_filepath = new_metrics_output_filepath

        # file path for this analysis iteration
        analysis_yaml_path_this_iteration = f'{self.analysis_yaml_path[:-(4+len(str(self.sim_number_offset)))]}_{iteration_number}.yaml'

        # write analysis input
        model_data_to_yaml(data_analysis, analysis_yaml_path_this_iteration)

        try:
            # Run analysis
            a = AnalysisSTEAM(file_name_analysis=analysis_yaml_path_this_iteration, file_path_list_models=None,
                              verbose=True)
            a.run_analysis()
            for i, label in enumerate(result_for_dakota):
                if isinstance(a.summary, dict):  # TODO: make sure this dict is existent also for XYCE and then remove this statement
                    if result_for_dakota[label].asv.function:
                        result_for_dakota[label].function = np.format_float_positional(a.summary[label], precision=9)
                else:
                    result_for_dakota[label].function = 0
        except Exception as e:
            print(f"The following Exception occured in iteration-number {iteration_number}: {e}")
            traceback.print_exc()
            result_for_dakota.fail()
        result_for_dakota.write()

        # return 1 so Dakota knows that this driver analysis did not crash
        return 1