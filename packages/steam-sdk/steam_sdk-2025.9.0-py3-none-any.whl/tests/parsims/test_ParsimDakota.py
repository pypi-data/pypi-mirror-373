import unittest
import os
from pathlib import Path

from steam_sdk.data.DataAnalysis import DataAnalysis
from steam_sdk.data.DataModelParsimDakota import DataModelParsimDakota
from steam_sdk.parsers.ParserYAML import yaml_to_data, model_data_to_yaml
from steam_sdk.parsims.ParsimDakota import ParsimDakota

class TestParsimDakota(unittest.TestCase):
    """
    Test for testing parametric Dakota simulations with given analysis file that runs a single tool. No multiple tools or co-simulation tests are implemented for now.
    """
    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))


    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_ParsimDakota_FiQuS_MQXA_multidim_parameter_study(self):
        absolute_path_dakota_yaml = os.path.join(os.getcwd(), 'input', "TestFile_ParsimDakota_FiQuS_MQXA_multidim_parameter_study.yaml")
        ParsimDakota(input_DAKOTA_yaml=absolute_path_dakota_yaml)
        # assert TODO add sensible check

    def test_ParsimDakota_LEDET_SMC_multidim_parameter_study(self):
        absolute_path_dakota_yaml = os.path.join(os.getcwd(), 'input', "TestFile_ParsimDakota_LEDET_SMC_multidim_parameter_study.yaml")
        ParsimDakota(input_DAKOTA_yaml=absolute_path_dakota_yaml)
        # assert TODO add sensible check

    def test_ParsimDakota_XYCE_RSS_parameter_study(self): # RSS is rather well performing in XYCE
        absolute_path_dakota_yaml = os.path.join(os.getcwd(), 'input', "TestFile_ParsimDakota_XYCE_RSS_multidim_parameter_study.yaml")

        # The working directory is changed to tempDakota during the test so we can not specify the input file for
        #  run parsim event circuit with a relative path. Thats why an absolute path is specified in the analysis yaml file
        # which is adapted using the user_name so it works on differnt machines.
        # # TODO: There are still path in the analysis file that are wrong and need updating
        path_analysis_yamlfile = str(Path(os.path.join(os.path.dirname(absolute_path_dakota_yaml),
                                                       '../../analyses/input/TestFile_AnalysisSTEAM_XYCE_Dakota.yaml')).resolve())
        data_analysis: DataAnalysis = yaml_to_data(path_analysis_yamlfile, DataAnalysis)
        input_file = 'RSS.A12B2_FPA-2023-03-19-07h27-2023-03-19-08h52.csv'
        data_analysis.AnalysisStepDefinition['runParsimEvent'].input_file = os.path.join(os.path.dirname(absolute_path_dakota_yaml), input_file)
        file_path_updated_yaml = os.path.join(os.path.dirname(path_analysis_yamlfile), os.path.basename(path_analysis_yamlfile).split(".")[0] + "_updated.yaml")
        model_data_to_yaml(data_analysis, file_path_updated_yaml)
        ParsimDakota(input_DAKOTA_yaml=absolute_path_dakota_yaml)

        # assert TODO add sensible check
