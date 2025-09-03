import os
import unittest

from steam_sdk.parsers.ParserYAML import dict_to_yaml

from steam_sdk.data.DataAnalysis import DataAnalysis, MakeModel, ModifyModel, ModifyModelMultipleVariables, SetUpFolder, \
    AddAuxiliaryFile, CopyFile, RunSimulation, PostProcessCompare, RunCustomPyFunction, RunViewer, CalculateMetrics, \
    LoadCircuitParameters, WriteStimulusFile, ParsimEvent, ParsimConductor, ParametricSweep, \
    StrandCriticalCurrentMeasurement
from tests.TestHelpers import assert_equal_yaml


class TestDataAnalysis(unittest.TestCase):

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


    def test_writeToFile_default(self):
        """
            Check that DataAnalysis generates a yaml file with the same keys as a reference file
        """
        # arrange
        generated_file = os.path.join('output',     'data_analysis_TEST.yaml')
        reference_file = os.path.join('references', 'data_analysis_REFERENCE.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataAnalysis = DataAnalysis()
        dict_to_yaml(data.model_dump(), generated_file, list_exceptions=['Conductors'])

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))
        # Check that the generated file is identical to the reference
        assert_equal_yaml(reference_file, generated_file)


    def test_writeToFile_all_steps(self):
        """
            Check that DataAnalysis generates a yaml file with the same keys as a reference file
        """
        # arrange
        all_step_types = [
            MakeModel(type='MakeModel'),
            ModifyModel(type='ModifyModel'),
            ModifyModelMultipleVariables(type='ModifyModelMultipleVariables'),
            SetUpFolder(type='SetUpFolder'),
            AddAuxiliaryFile(type='AddAuxiliaryFile'),
            CopyFile(type='CopyFile'),
            RunSimulation(type='RunSimulation'),
            PostProcessCompare(type='PostProcessCompare'),
            RunCustomPyFunction(type='RunCustomPyFunction'),
            RunViewer(type='RunViewer'),
            CalculateMetrics(type='CalculateMetrics'),
            LoadCircuitParameters(type='LoadCircuitParameters'),
            WriteStimulusFile(type='WriteStimulusFile'),
            ParsimEvent(type='ParsimEvent'),
            ParametricSweep(type='ParametricSweep'),
            ParsimConductor(type='ParsimConductor'),
        ]

        generated_file = os.path.join('output',     'data_analysis_TEST_all_steps.yaml')
        reference_file = os.path.join('references', 'data_analysis_REFERENCE_all_steps.yaml')

        # If test output file already exists, delete it
        if os.path.isfile(generated_file) == True:
            os.remove(generated_file)

        # act
        data: DataAnalysis = DataAnalysis()
        # add all possible step types
        for s, step_type in enumerate(all_step_types):
            data.AnalysisStepDefinition[f'step_{step_type.type}'] = step_type
        data.AnalysisStepDefinition[f'step_ParsimConductor'].strand_critical_current_measurements = [StrandCriticalCurrentMeasurement()]

        dict_to_yaml(data.model_dump(), generated_file, list_exceptions=['Conductors'])

        # assert
        # Check that the generated file exists
        self.assertTrue(os.path.isfile(generated_file))
        # Check that the generated file is identical to the reference
        assert_equal_yaml(reference_file, generated_file)

