import shutil
import unittest
import os
import math

from steam_sdk.data.DataAnalysis import DefaultParsimEventKeys
from steam_sdk.data.DataEventMagnet import DataEventMagnet
from steam_sdk.parsims.ParsimEventMagnet import ParsimEventMagnet
from tests.TestHelpers import assert_equal_readable_files


class TestParsimEventMagnet(unittest.TestCase):

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


    def test_ParsimEventMagnet_Initialize(self):
        pem = ParsimEventMagnet()

    def test_ParsimEventMagnet_ReadCsv(self):
        # arrange
        pem = ParsimEventMagnet()
        path_csv = os.path.join('input', 'TEST_ParsimEventMagnet_ReadCsv.csv')

        # act
        pem.read_from_input(path_input_file=path_csv, flag_append=False, rel_quench_heater_trip_threshold=1)

        # assert
        self.assertEqual(3, len(pem.list_events))
        self.assertEqual(DataEventMagnet, type(pem.list_events[0]))
        self.assertEqual(1.9, pem.list_events[0].GeneralParameters.initial_temperature)
        self.assertEqual(4.5, pem.list_events[1].GeneralParameters.initial_temperature)
        self.assertEqual(12047, pem.list_events[0].Powering.PowerSupply.I_initial)
        self.assertEqual(7948, pem.list_events[1].Powering.PowerSupply.I_initial)
        self.assertEqual(0.002, pem.list_events[0].QuenchProtection.CLIQ.t_trigger)
        self.assertEqual(994.8, pem.list_events[0].QuenchProtection.CLIQ.U0)
        self.assertEqual(0.04, pem.list_events[0].QuenchProtection.CLIQ.C)
        self.assertTrue(math.isnan(pem.list_events[1].QuenchProtection.CLIQ.C))
        self.assertEqual(str, type(pem.list_events[1].GeneralParameters.type))
        self.assertEqual(float, type(pem.list_events[0].GeneralParameters.initial_temperature))
        self.assertEqual(919.7, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].U0)
        self.assertEqual(906.7, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater3'].U0)
        self.assertEqual(913.2, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater8'].U0)
        self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].t_trigger)
        self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater4'].t_trigger)
        self.assertEqual(0.00241, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater7'].t_trigger)
        self.assertEqual(199.3, pem.list_events[2].QuenchProtection.Quench_Heaters['U (YT221)'].U0)
        self.assertEqual(-1.318, pem.list_events[2].QuenchProtection.Quench_Heaters['U (YT221)'].t_trigger)

    def test_ParsimEventMagnet_ReadCsv_interpolate(self):
        # arrange
        pem = ParsimEventMagnet()
        path_csv = os.path.join('input', 'TEST_ParsimEventMagnet_ReadCsv.csv')

        # act
        pem.read_from_input(path_input_file=path_csv, flag_append=False, rel_quench_heater_trip_threshold=0.99)

        # assert
        self.assertEqual(3, len(pem.list_events))
        self.assertEqual(DataEventMagnet, type(pem.list_events[0]))
        self.assertEqual(1.9, pem.list_events[0].GeneralParameters.initial_temperature)
        self.assertEqual(4.5, pem.list_events[1].GeneralParameters.initial_temperature)
        self.assertEqual(12047, pem.list_events[0].Powering.PowerSupply.I_initial)
        self.assertEqual(7948, pem.list_events[1].Powering.PowerSupply.I_initial)
        self.assertEqual(0.002, pem.list_events[0].QuenchProtection.CLIQ.t_trigger)
        self.assertEqual(994.8, pem.list_events[0].QuenchProtection.CLIQ.U0)
        self.assertEqual(0.04, pem.list_events[0].QuenchProtection.CLIQ.C)
        self.assertTrue(math.isnan(pem.list_events[1].QuenchProtection.CLIQ.C))
        self.assertEqual(str, type(pem.list_events[1].GeneralParameters.type))
        self.assertEqual(float, type(pem.list_events[0].GeneralParameters.initial_temperature))
        self.assertEqual(919.7 / 0.99, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].U0)
        self.assertEqual(906.7 / 0.99, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater3'].U0)
        self.assertEqual(913.2 / 0.99, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater8'].U0)
        self.assertEqual(0.002469638119978685, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].t_trigger)
        self.assertEqual(0.0024774607586889145, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater4'].t_trigger)
        self.assertEqual(0.0020625580000813125, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater7'].t_trigger)
        self.assertEqual(199.3 / 0.99, pem.list_events[2].QuenchProtection.Quench_Heaters['U (YT221)'].U0)
        self.assertEqual(-1.318467807716597, pem.list_events[2].QuenchProtection.Quench_Heaters['U (YT221)'].t_trigger)


    def test_ParsimEventMagnet_ReadCsv_append(self):
        # arrange
        pem = ParsimEventMagnet()
        path_csv = os.path.join('input', 'TEST_ParsimEventMagnet_ReadCsv.csv')

        # act
        pem.read_from_input(path_input_file=path_csv, flag_append=False, rel_quench_heater_trip_threshold=None)
        pem.read_from_input(path_input_file=path_csv, flag_append=True, rel_quench_heater_trip_threshold=None)

        # assert
        self.assertEqual(6, len(pem.list_events))
        self.assertEqual(DataEventMagnet, type(pem.list_events[4]))
        self.assertEqual(1.9, pem.list_events[3].GeneralParameters.initial_temperature)
        self.assertEqual(4.5, pem.list_events[4].GeneralParameters.initial_temperature)
        self.assertEqual(float, type(pem.list_events[3].GeneralParameters.initial_temperature))
        self.assertEqual(12047, pem.list_events[3].Powering.PowerSupply.I_initial)
        self.assertEqual(7948, pem.list_events[4].Powering.PowerSupply.I_initial)
        self.assertEqual(919.7, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].U0)
        self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].t_trigger)
        self.assertEqual(919.7, pem.list_events[3].QuenchProtection.Quench_Heaters['U_Heater1'].U0)
        self.assertEqual(0.00281, pem.list_events[3].QuenchProtection.Quench_Heaters['U_Heater1'].t_trigger)


    def test_ParsimEventMagnet_ReadXlsx(self):
        # arrange
        pem = ParsimEventMagnet()
        path_csv = os.path.join('input', 'TEST_ParsimEventMagnet_ReadXlsx.xlsx')

        # act
        pem.read_from_input(path_input_file=path_csv, flag_append=False, rel_quench_heater_trip_threshold=None)

        # assert
        self.assertEqual(2, len(pem.list_events))
        self.assertEqual(DataEventMagnet, type(pem.list_events[0]))
        self.assertEqual(91.9, pem.list_events[0].GeneralParameters.initial_temperature)
        self.assertEqual(94.5, pem.list_events[1].GeneralParameters.initial_temperature)
        self.assertEqual(120479, pem.list_events[0].Powering.PowerSupply.I_initial)
        self.assertEqual(79489, pem.list_events[1].Powering.PowerSupply.I_initial)
        self.assertEqual(0.002, pem.list_events[0].QuenchProtection.CLIQ.t_trigger)
        self.assertEqual(919.7, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].U0)
        self.assertEqual(906.7, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater3'].U0)
        self.assertEqual(913.2, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater8'].U0)
        self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].t_trigger)
        self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater4'].t_trigger)
        self.assertEqual(0.00241, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater7'].t_trigger)


    def test_ParsimEventMagnet_ReadXlsx_2(self):
        '''
        test by reading another, more challenging file with a few exceptions (missing "QH name" value, QH values with floats and not lists)
        '''
        # arrange
        pem = ParsimEventMagnet()
        path_csv = os.path.join('input', 'TEST_ParsimEventMagnet_ReadXlsx_2.xlsx')

        # act
        pem.read_from_input(path_input_file=path_csv, flag_append=False, rel_quench_heater_trip_threshold=None)

        # assert
        self.assertEqual(69, len(pem.list_events))
        self.assertEqual(DataEventMagnet, type(pem.list_events[0]))
        self.assertEqual(1.94, pem.list_events[1].GeneralParameters.initial_temperature)
        self.assertEqual(1.91, pem.list_events[2].GeneralParameters.initial_temperature)
        self.assertEqual(1504, pem.list_events[2].Powering.PowerSupply.I_initial)
        self.assertEqual(13235, pem.list_events[13].Powering.PowerSupply.I_initial)
        # self.assertEqual(0.002, pem.list_events[0].QuenchProtection.CLIQ.t_trigger)
        self.assertEqual(904.1, pem.list_events[13].QuenchProtection.Quench_Heaters['U (YT211)'].U0)
        # self.assertEqual(906.7, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater3'].U0)
        # self.assertEqual(913.2, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater8'].U0)
        # self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater1'].t_trigger)
        # self.assertEqual(0.00281, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater4'].t_trigger)
        # self.assertEqual(0.00241, pem.list_events[0].QuenchProtection.Quench_Heaters['U_Heater7'].t_trigger)

    def test_ParsimEventMagnet_setUpViewer(self):
        # arrange
        ref_viewer_csv = os.path.join('references', 'run_parsim_event', 'setUpViewer_reference_1.csv')
        pem = ParsimEventMagnet()
        path_csv = os.path.join('input', 'TEST_EVENT_LIST_ParsimEventMagnet_SetUpViewer.csv')
        folder_viewer_csv = os.path.join('output', 'ParsimEventMagnet_setUpViewer')
        path_viewer_csv = os.path.join(folder_viewer_csv, 'setUpViewer_output_1.csv')
        dict_default_keys = {
            'local_LEDET_folder': 'C:\\tempLEDET\LEDET',
            'path_config_file': 'input/run_parsim_event/TEST_parsim_configuration.yaml',
            'default_configs': ['config_advanced_HF', 'config_advanced', 'config_HF_MF', 'config_simple', 'config_only_sim'],  # most_detailed_to_least_detailed_configs_to_use
            'path_tdms_files': '../viewers/input/SM18_TDMS_REPO_READ_ONLY',
            'path_output_measurement_files': '../viewers/input/csvMeasurementDatabase',
            'path_output': 'output/figures',
            }
        default_keys = DefaultParsimEventKeys.parse_obj(dict_default_keys)
        simulation_numbers = [11, 102, 11, 103, 104, 105, 106, 111]
        simulation_name = 'DUMMY_simu_name'
        software = 'LEDET'
        
        # Delete file if existing (the test will re-generate it)
        if os.path.exists(folder_viewer_csv) and os.path.isdir(folder_viewer_csv):
            shutil.rmtree(folder_viewer_csv)
            print('Folder {} already existed. It was removed. This test will re-make it.'.format(folder_viewer_csv))
    
        # act
        pem.read_from_input(path_input_file=path_csv, flag_append=False, rel_quench_heater_trip_threshold=None)
        pem.set_up_viewer(path_viewer_csv, default_keys, simulation_numbers, simulation_name, software)

        # assert
        self.assertTrue(os.path.isfile(path_viewer_csv))
        assert_equal_readable_files(ref_viewer_csv, path_viewer_csv)
