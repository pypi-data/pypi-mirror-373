import os
import shutil
import subprocess
from pathlib import Path
from typing import List

from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.data.DataAnalysis import DataAnalysis
from steam_sdk.data.DataModelParsimDakota import DataModelParsimDakota
from steam_sdk.parsers.ParserYAML import yaml_to_data, model_data_to_yaml


class DriverDakota:
    """
    Driver Dakota is used for colling Dakota executable. Dakota then calls DriverAnalysis to drive STEAM tools via respective drivers in the SDK
    """
    def __init__(self,
                 analysis_yaml_path: str,
                 data_model_dakota: DataModelParsimDakota,
                 settings: DataSettings,
                 verbose: bool = True
                 ):
        """
        Initialize the driver, without running anything
        :param analysis_yaml_path: path to the analysis file to be used with Dakota
        :type analysis_yaml_path: str
        :param data_model_dakota: data class of data model dakota
        :type data_model_dakota: List[str]
        :param settings: settings object
        :type settings: DataSettings
        :param verbose: if ture more is printed to the output terminal
        :type verbose: bool
        """
        self.analysis_yaml_path = analysis_yaml_path
        self.data_model_dakota = data_model_dakota
        self.settings = settings
        self.verbose = verbose

        #self.builder_model_obj_path = os.path.join(self.settings.local_Dakota_folder, 'temp.pkl')

        self.output_path = os.path.dirname(self.analysis_yaml_path)
        self.analysis_file_name = os.path.basename(self.analysis_yaml_path)
        # this is running by default these functions at the initialization of the class
        self._run_pre_dakota_non_iterable_steps()
        self._write_driver_link()
        self._run_dakota_iterable_steps()

    def _run_pre_dakota_non_iterable_steps(self):
        """
        Execute pre Dakota non-iterable steps of the analysis before running Dakota
        :return: Nothing, just runs the analysis with the steps
        :rtype: None
        """
        initial_sim_number = 0
        init_sim_num_w_offset = self.data_model_dakota.sim_number_offset+initial_sim_number

        data_analysis: DataAnalysis = yaml_to_data(self.analysis_yaml_path, DataAnalysis)
        # data_analysis.WorkingFolders.library_path = str(Path(data_analysis.WorkingFolders.library_path).resolve())

        data_analysis.AnalysisStepSequence = self.data_model_dakota.initial_steps_list
        for step_name in self.data_model_dakota.initial_steps_list + self.data_model_dakota.iterable_steps_list: # for all steps as iterable steps need to be also edited
            # --- modify steps of analysis according to dakota variables and values ---
            step = data_analysis.AnalysisStepDefinition[step_name]
            if step.type in ['ModifyModelMultipleVariables']:
                if 'Options_FiQuS.multipole.postproc.compare_to_ROXIE' in step.variables_to_change:
                    index = step.variables_to_change.index('Options_FiQuS.multipole.postproc.compare_to_ROXIE')
                    step.variables_value[index] = [
                        os.path.abspath(os.path.join(self.settings.local_library_path, step.variables_value[index][0]))]
            elif step.type in ['ModifyModel']:
                if 'Options_FiQuS.multipole.postproc.compare_to_ROXIE' in step.variable_to_change:
                    index = step.variable_to_change.index('Options_FiQuS.multipole.postproc.compare_to_ROXIE')
                    step.variable_value[index] = os.path.abspath(
                        os.path.join(self.settings.local_library_path, step.variable_value[index][0]))

        for step_name in data_analysis.AnalysisStepSequence:
            step = data_analysis.AnalysisStepDefinition[step_name]
            if step.type in ['ModifyModel', 'ModifyModelMultipleVariables']:
                if len(step.simulation_numbers) == 0:
                    pass  # this step is not writting the model, so leave it as is
                elif len(step.simulation_numbers) == 1:
                    step.simulation_numbers = [init_sim_num_w_offset]
                else:
                    raise Exception(f'Analysis file with multiple simulation numbers can not be used in dakota. Change {step_name}.simulation_numbers={step.simulation_numbers} to a list with single entry')

            # --- change the simulation number that the model is run with, so a correct one is run for this dakota iteration ---
            if step.type in ['RunSimulation']:
                if len(step.simulation_numbers) == 0:
                    pass  # this step is not run
                elif len(step.simulation_numbers) == 1:
                    step.simulation_numbers = [init_sim_num_w_offset]
                else:
                    raise Exception(f'Analysis file with multiple simulation numbers can not be used in dakota. Change {step_name}.simulation_numbers={step.simulation_numbers} to a list with single entry')

        data_analysis.GeneralParameters.relative_path_settings = os.path.join(Path(os.path.dirname(self.analysis_yaml_path), Path(data_analysis.GeneralParameters.relative_path_settings)).resolve())

        analysis_file_path = f'{self.analysis_yaml_path[:-5]}_{init_sim_num_w_offset}.yaml'
        model_data_to_yaml(data_analysis, analysis_file_path)

        if len(self.data_model_dakota.initial_steps_list) > 0:
            a = AnalysisSTEAM(file_name_analysis=analysis_file_path, verbose=self.verbose)
            a.run_analysis(verbose=self.verbose)
            #a.store_model_objects(path_output_file=os.path.join(os.path.dirname(self.analysis_yaml_local_path), 'temp.pkl'))


    def _write_driver_link(self):
        """
        Writes driver_link.py file that is used to serve as a black box script for running Driver Analysis of SDK
        :return: Nothing, writes file on disk in the local_Dakota_folder
        :rtype: None
        """
        path_to_driver_link = os.path.join(self.output_path, 'driver_link.py')
        with open(path_to_driver_link, 'w') as f:
            f.write('from steam_sdk.drivers.DriverAnalysis import DriverAnalysis')
            f.write(f'\nda = DriverAnalysis(analysis_yaml_path=r"{self.analysis_yaml_path}", iterable_steps={self.data_model_dakota.iterable_steps_list}, sim_number_offset={self.data_model_dakota.sim_number_offset})')
            f.write('\nda.run()')


    def _run_dakota_iterable_steps(self):
        """
        Runs dakota.exe with the input file specified. This will use DriverAnalysis and iterable_steps
        """
        # Change folder to local_Dakota_folder i.e. where the driver_link.py was saved, otherwise Dakota will not find it
        os.chdir(self.output_path)
        print(f'`Changed working directory to: {self.output_path}')

        # Call dakota and give up control of the flow from now on as Dakota takes over from now on. It will call driver_link and DriverAnalysis of the SDK to be able to run the analysis.
        input_file_path = os.path.join(self.output_path, "dakota_in.in")
        print(f'Calling Dakota with {input_file_path}')
        subprocess.call([self.settings.Dakota_path, '-i', input_file_path])