import traceback
import unittest
import os
from steam_sdk.analyses.AnalysisEvent import get_circuit_name_from_eventfile, get_circuit_family_from_circuit_name
from steam_sdk.analyses.AnalysisEventLHC import get_circuit_type_from_circuit_name, steam_analyze_lhc_event
from steam_sdk.parsers.ParserYAML import yaml_to_data
class Test_All_Circuit_Types(unittest.TestCase):
    """
    Test_All_Circuit_Types is a testclass designed to validate the analysis and simulation of all LHC circuit types (models).

    The class provides the following features:
    - **setUp()**: Prepares the environment for each test by changing the working directory to the location of the test file.
    - **tearDown()**: Restores the original working directory after each test execution.
    - **test_all_circuit_types()**: The main test method that:
        - Loads configuration from a YAML settings file.
        - Iterates over a list of CSV files representing circuit events.
        - Executes the analysis of each circuit type by running a simulation via the STEAM SDK.
        - Validates that the circuit reports (.pdf), circuit simulation input files (.cir), and simulation output files
         (.csd) are generated for each test case.
        - Prints any errors or failures that occur during the simulation process.

    """

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('Test is run from folder: {}'.format(os.getcwd()))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    # def test_all_circuit_types(self):
    #     # arrange
    #     flag_run_software = True
    #     flag_run_all_models = True  # this flag can be set to False to Debug the test
    #     software = "PSPICE"
    #     file_counter = 1
    #     csv_directory = os.path.join("input", "sample_input_event_files")
    #     path_settings_file = os.path.abspath(fr"../settings.{os.getlogin()}.yaml")
    #     settings_data_object = yaml_to_data(path_settings_file)
    #     library_path = settings_data_object["local_library_path"]
    #     library_path = os.path.join('..', 'builders', 'model_library')  # settings_data_object["local_library_path"]
    #     local_software_folder = settings_data_object["local_PSPICE_folder"]
    #     csv_file_list = self.list_csv_files(csv_directory)
    #
    #     target_paths_report = [
    #         rf'{local_software_folder}\IPD\1\report__UID_RD1.L2_PLI2.f2-2021-04-10-07h44-2021-04-10-13h19__CN_RD1.L2.pdf',
    #         rf'{local_software_folder}\IPQ_RQ10_2_2xRPHGA_2xMQML\1\report__UID_RQ10.L1_FPA-2023-09-18-13h12-2023-09-18-18h01__CN_RQ10.L1.pdf',
    #         rf'{local_software_folder}\IPQ_RQ4_2_2xRPHH_2xMQY\1\report__UID_RQ4.L1_FPA-2021-05-15-15h39-2021-05-15-16h23__CN_RQ4.L1.pdf',
    #         rf'{local_software_folder}\IPQ_RQ4_4_2xRPHH_4xMQY\1\report__UID_RQ4.L2_FPA-2018-12-10-16h22-2021-02-21-13h57__CN_RQ4.L2.pdf',
    #         rf'{local_software_folder}\IPQ_RQ5_2_2xRPHGB_2xMQML\1\report__UID_RQ5.L1_FPA-2021-05-21-17h56-2021-05-21-18h43__CN_RQ5.L1.pdf',
    #         rf'{local_software_folder}\IPQ_RQ5_2_2xRPHH_2xMQY\1\report__UID_RQ5.L4_FPA-2021-03-10-20h20-2021-03-10-21h29__CN_RQ5.L4.pdf',
    #         rf'{local_software_folder}\IPQ_RQ5_4_2xRPHGB_4xMQM\1\report__UID_RQ5.L8_FPA-2021-02-12-17h44-2021-02-15-13h34__CN_RQ5.L8.pdf',
    #         rf'{local_software_folder}\IPQ_RQ5_4_2xRPHH_4xMQY\1\report__UID_RQ5.L2_PLI2.f3-2021-04-09-18h55-2021-04-09-21h37__CN_RQ5.L2.pdf',
    #         rf'{local_software_folder}\IPQ_RQ6_2_2xRPHGB_2xMQML\1\report__UID_RQ6.L1_FPA-2021-05-16-17h19-2021-05-17-11h48__CN_RQ6.L1.pdf',
    #         rf'{local_software_folder}\IPQ_RQ6_2_2xRPHGB_2xMQY\1\report__UID_RQ6.L4_FPA-2021-03-10-20h47-2021-03-10-21h39__CN_RQ6.L4.pdf',
    #         rf'{local_software_folder}\IPQ_RQ6_4_2xRPHGB_2xMQM_2xMQML\1\report__UID_RQ6.L2_FPA-2021-04-10-15h08-2021-04-11-10h29__CN_RQ6.L2.pdf',
    #         rf'{local_software_folder}\IPQ_RQ7_2_2xRPHGA_2xMQM\1\report__UID_RQ7.L4_FPA-2021-03-10-19h34-2021-03-10-20h57__CN_RQ7.L4.pdf',
    #         rf'{local_software_folder}\IPQ_RQ7_4_2xRPHGA_4xMQM\1\report__UID_RQ7.L1_FPA-2023-07-03-05h27-2023-07-03-11h36__CN_RQ7.L1.pdf',
    #         rf'{local_software_folder}\IPQ_RQ8_2_2xRPHGA_2xMQML\1\report__UID_RQ8.L1_FPA-2021-05-16-14h07-2021-05-16-16h10__CN_RQ8.L1.pdf',
    #         rf'{local_software_folder}\IPQ_RQ9_4_2xRPHGA_2xMQM_2xMQMC\1\report__UID_RQ9.L1_FPA-2023-09-18-13h12-2023-09-22-11h49__CN_RQ9.L1.pdf',
    #         rf'{local_software_folder}\RB\1\report__UID_RB.A34_FPA-2015-03-13-09h53-2022-10-14-15h24__CN_RB.A34.pdf',
    #         rf'{local_software_folder}\RCB\1\report__UID_RCBH12.L3B1_FPA-2021-09-21-19h25-2021-09-22-17h20__CN_RCBH12.L3B1.pdf',
    #         rf'{local_software_folder}\RCBC\1\report__UID_RCBCH10.R2B1_FPA-2022-03-03-07h09-2022-03-03-09h01__CN_RCBCH10.R2B1.pdf',
    #         rf'{local_software_folder}\RCBX\1\report__UID_RCBX1.L1_FPA-2021-05-06-18h12-2021-05-07-11h01__CN_RCBXH1.L1.pdf',
    #         rf'{local_software_folder}\RCBX\2\report__UID_RCBX1.L1_FPA-2021-05-06-18h12-2021-05-07-11h01__CN_RCBXV1.L1.pdf',
    #         rf'{local_software_folder}\RCBY\1\report__UID_RCBYH4.R6B1_FPA-2021-06-19-13h00-2021-06-22-12h25__CN_RCBYH4.R6B1.pdf',
    #         rf'{local_software_folder}\RCD\1\report__UID_RCD.A81B2_FPA-2023-05-26-15h17-2023-05-26-15h38__CN_RCD.A81B2.pdf',
    #         rf'{local_software_folder}\RCO\1\report__UID_RCD.A81B2_FPA-2023-05-26-15h17-2023-05-26-15h38__CN_RCO.A81B2.pdf',
    #         rf'{local_software_folder}\RCS\1\report__UID_RCS.A23B2_FPA-2021-04-08-21h06-2021-04-08-22h13__CN_RCS.A23B2.pdf',
    #         rf'{local_software_folder}\RO_13magnets\1\report__UID_ROD.A23B2_FPA-2021-04-13-21h08-2021-04-14-02h50__CN_ROD.A23B2.pdf',
    #         rf'{local_software_folder}\RO_8magnets\1\report__UID_ROD.A23B1_FPA-2022-04-14-10h39-2022-04-14-11h04__CN_ROD.A23B1.pdf',
    #         rf'{local_software_folder}\RQ6\1\report__UID_RQ6.L3B1_FPA-2021-09-24-12h47-2021-09-24-14h28__CN_RQ6.L3B1.pdf',
    #         rf'{local_software_folder}\RQSX3\1\report__UID_RQSX3.L1_FPA-2021-05-01-15h27-2021-05-02-02h57__CN_RQSX3.L1.pdf',
    #         rf'{local_software_folder}\RQS_AxxBx\1\report__UID_RQS.A12B2_FPA-2021-04-05-12h00-2021-04-05-12h50__CN_RQS.A12B2.pdf',
    #         rf'{local_software_folder}\RQS_R_LxBx\1\report__UID_RQS.L3B2_FPA-2021-04-07-21h01-2021-04-08-00h06__CN_RQS.L3B2.pdf',
    #         rf'{local_software_folder}\RQT\1\report__UID_RQTD.A23B1_FPA-2021-04-10-20h36-2021-04-11-13h45__CN_RQTD.A23B1.pdf',
    #         rf'{local_software_folder}\RQTL9\1\report__UID_RQTL9.L3B1_FPA-2021-09-23-20h27-2021-09-23-22h31__CN_RQTL9.L3B1.pdf',
    #         rf'{local_software_folder}\RQTL_7_8_10_11\1\report__UID_RQTL10.L3B2_FPA-2021-09-23-14h12-2021-09-23-18h11__CN_RQTL10.L3B2.pdf',
    #         rf'{local_software_folder}\RQT_12_13\1\report__UID_RQT12.L1B2_FPA-2021-08-20-18h30-2021-08-20-20h05__CN_RQT12.L1B2.pdf',
    #         rf'{local_software_folder}\RQX\1\report__UID_RQX.L2_FPA-2021-04-13-19h26-2021-04-13-20h55__CN_RQX.L2.pdf',
    #         rf'{local_software_folder}\RQ_47magnets\1\report__UID_RQ.A12_FPA-2021-04-22-22h34-2021-04-23-09h39__CN_RQD.A12.pdf',
    #         rf'{local_software_folder}\RQ_47magnets\2\report__UID_RQ.A12_FPA-2021-04-22-22h34-2021-04-23-09h39__CN_RQF.A12.pdf',
    #         rf'{local_software_folder}\RQ_51magnets\1\report__UID_RQ.A23_FPA-2021-05-09-14h42-2021-05-09-16h44__CN_RQD.A23.pdf',
    #         rf'{local_software_folder}\RQ_51magnets\2\report__UID_RQ.A23_FPA-2021-05-09-14h42-2021-05-09-16h44__CN_RQF.A23.pdf',
    #         rf'{local_software_folder}\RSD_11magnets\1\report__UID_RSD2.A34B1_FPA-2021-02-23-18h12-2021-02-24-17h25__CN_RSD2.A34B1.pdf',
    #         rf'{local_software_folder}\RSD_12magnets\1\report__UID_RSD1.A23B1_FPA-2021-09-24-10h47-2021-09-24-11h19__CN_RSD1.A23B1.pdf',
    #         rf'{local_software_folder}\RSF_10magnets\1\report__UID_RSF1.A23B2_FPA-2021-09-30-15h57-2021-09-30-16h39__CN_RSF1.A23B2.pdf',
    #         rf'{local_software_folder}\RSF_9magnets\1\report__UID_RSF2.A23B2_FPA-2022-03-21-18h55-2022-03-21-20h22__CN_RSF2.A23B2.pdf',
    #         rf'{local_software_folder}\RSS\1\report__UID_RSS.A12B2_FPA-2023-03-19-07h27-2023-03-19-08h52__CN_RSS.A12B2.pdf']
    #
    #     target_circuit_file_paths = [
    #         rf'{local_software_folder}\IPD\1\IPD.cir',
    #         rf'{local_software_folder}\IPQ_RQ10_2_2xRPHGA_2xMQML\1\IPQ_RQ10_2_2xRPHGA_2xMQML.cir',
    #         rf'{local_software_folder}\IPQ_RQ4_2_2xRPHH_2xMQY\1\IPQ_RQ4_2_2xRPHH_2xMQY.cir',
    #         rf'{local_software_folder}\IPQ_RQ4_4_2xRPHH_4xMQY\1\IPQ_RQ4_4_2xRPHH_4xMQY.cir',
    #         rf'{local_software_folder}\IPQ_RQ5_2_2xRPHGB_2xMQML\1\IPQ_RQ5_2_2xRPHGB_2xMQML.cir',
    #         rf'{local_software_folder}\IPQ_RQ5_2_2xRPHH_2xMQY\1\IPQ_RQ5_2_2xRPHH_2xMQY.cir',
    #         rf'{local_software_folder}\IPQ_RQ5_4_2xRPHGB_4xMQM\1\IPQ_RQ5_4_2xRPHGB_4xMQM.cir',
    #         rf'{local_software_folder}\IPQ_RQ5_4_2xRPHH_4xMQY\1\IPQ_RQ5_4_2xRPHH_4xMQY.cir',
    #         rf'{local_software_folder}\IPQ_RQ6_2_2xRPHGB_2xMQML\1\IPQ_RQ6_2_2xRPHGB_2xMQML.cir',
    #         rf'{local_software_folder}\IPQ_RQ6_2_2xRPHGB_2xMQY\1\IPQ_RQ6_2_2xRPHGB_2xMQY.cir',
    #         rf'{local_software_folder}\IPQ_RQ6_4_2xRPHGB_2xMQM_2xMQML\1\IPQ_RQ6_4_2xRPHGB_2xMQM_2xMQML.cir',
    #         rf'{local_software_folder}\IPQ_RQ7_2_2xRPHGA_2xMQM\1\IPQ_RQ7_2_2xRPHGA_2xMQM.cir',
    #         rf'{local_software_folder}\IPQ_RQ7_4_2xRPHGA_4xMQM\1\IPQ_RQ7_4_2xRPHGA_4xMQM.cir',
    #         rf'{local_software_folder}\IPQ_RQ8_2_2xRPHGA_2xMQML\1\IPQ_RQ8_2_2xRPHGA_2xMQML.cir',
    #         rf'{local_software_folder}\IPQ_RQ9_4_2xRPHGA_2xMQM_2xMQMC\1\IPQ_RQ9_4_2xRPHGA_2xMQM_2xMQMC.cir',
    #         rf'{local_software_folder}\RB\1\RB.cir',
    #         rf'{local_software_folder}\RCB\1\RCB.cir',
    #         rf'{local_software_folder}\RCBC\1\RCBC.cir',
    #         rf'{local_software_folder}\RCBX\1\RCBX.cir',
    #         rf'{local_software_folder}\RCBX\2\RCBX.cir',
    #         rf'{local_software_folder}\RCBY\1\RCBY.cir',
    #         rf'{local_software_folder}\RCD\1\RCD.cir',
    #         rf'{local_software_folder}\RCO\1\RCO.cir',
    #         rf'{local_software_folder}\RCS\1\RCS.cir',
    #         rf'{local_software_folder}\RO_13magnets\1\RO_13magnets.cir',
    #         rf'{local_software_folder}\RO_8magnets\1\RO_8magnets.cir',
    #         rf'{local_software_folder}\RQ6\1\RQ6.cir',
    #         rf'{local_software_folder}\RQSX3\1\RQSX3.cir',
    #         rf'{local_software_folder}\RQS_AxxBx\1\RQS_AxxBx.cir',
    #         rf'{local_software_folder}\RQS_R_LxBx\1\RQS_R_LxBx.cir',
    #         rf'{local_software_folder}\RQT\1\RQT.cir',
    #         rf'{local_software_folder}\RQTL9\1\RQTL9.cir',
    #         rf'{local_software_folder}\RQTL_7_8_10_11\1\RQTL_7_8_10_11.cir',
    #         rf'{local_software_folder}\RQT_12_13\1\RQT_12_13.cir',
    #         rf'{local_software_folder}\RQX\1\RQX.cir',
    #         rf'{local_software_folder}\RQ_47magnets\1\RQ_47magnets.cir',
    #         rf'{local_software_folder}\RQ_47magnets\2\RQ_47magnets.cir',
    #         rf'{local_software_folder}\RQ_51magnets\1\RQ_51magnets.cir',
    #         rf'{local_software_folder}\RQ_51magnets\2\RQ_51magnets.cir',
    #         rf'{local_software_folder}\RSD_11magnets\1\RSD_11magnets.cir',
    #         rf'{local_software_folder}\RSD_12magnets\1\RSD_12magnets.cir',
    #         rf'{local_software_folder}\RSF_10magnets\1\RSF_10magnets.cir',
    #         rf'{local_software_folder}\RSF_9magnets\1\RSF_9magnets.cir',
    #         rf'{local_software_folder}\RSS\1\RSS.cir']
    #
    #     # act
    #     for input_csv_filepath in csv_file_list:
    #         if not flag_run_all_models: continue
    #         # ==== Execute simulation ===
    #         print(f"Analyzing file: {input_csv_filepath}")
    #
    #         circuit_name = get_circuit_name_from_eventfile(input_csv_filepath)
    #         circuit_type = get_circuit_type_from_circuit_name(circuit_name, library_path)
    #
    #         input_parameter_dictionary = {
    #             'path_meas_data_folder': os.path.join(os.getcwd(), "measurement_data"),
    #             'config_file_or_dir': os.path.abspath(os.path.join(os.getcwd(), "input", "config_SIGMON.yaml")),
    #             "timeout_s": 20000,
    #             "metrics_to_calculate": ["MARE"],
    #             "flag_run_software": flag_run_software,
    #             "input_csv_file": input_csv_filepath,
    #             "software": software,
    #             "file_counter": file_counter,
    #         }
    #         try:
    #             steam_analyze_lhc_event(path_settings_file=path_settings_file,
    #                                                 input_parameter_dictionary=input_parameter_dictionary)
    #         except Exception as e:
    #             error_traceback = traceback.format_exc()
    #             print(f"=== Error: circuit type {circuit_type} failed to run ===")
    #
    #     # assert
    #     # ============================= check if the report files exist ================================================
    #     print(" ===== Checking if reports are generated =====")
    #     for i, path in enumerate(target_paths_report):
    #         exists = os.path.exists(path)
    #         print(f"=== {i+1}/44 Checking if report at {path} exist: {exists} ===")
    #         self.assertTrue(os.path.exists(path))
    #
    #     # ============================= check if the circuit files exist ===============================================
    #     print(" ===== Checking if .cir are generated =====")
    #     for i, path in enumerate(target_circuit_file_paths):
    #         exists = os.path.exists(path)
    #         print(f"=== {i + 1}/44 Checking if circuit file at {path} exist: {exists} ===")
    #         self.assertTrue(os.path.exists(path))
    #
    #     # ============================= check if the .csd output files exist ===========================================
    #     print(" ===== Checking if .csd are generated =====")
    #     for i, cir_path in enumerate(target_circuit_file_paths):
    #         csd_path =cir_path.replace(".cir", ".csd")
    #         exists = os.path.exists(csd_path)
    #         print(f"=== {i + 1}/44 Checking if csd file at {csd_path} exist: {exists} ===")
    #         self.assertTrue(os.path.exists(path))

    def list_csv_files(self, directory_to_search):
        csv_files = []
        for root, dirs, files in os.walk(directory_to_search):
            for file in files:
                if file.endswith(".csv"):
                    csv_files.append(os.path.join(root, file))
        return csv_files