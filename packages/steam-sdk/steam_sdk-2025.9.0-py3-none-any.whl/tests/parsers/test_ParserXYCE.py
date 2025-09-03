import unittest

import yaml

from steam_sdk.drivers.DriverXYCE import *
from steam_sdk.parsers.ParserXYCE import *
from steam_sdk.utils.delete_if_existing import delete_if_existing
from steam_sdk.utils.read_settings_file import read_settings_file


class TestParserXYCE(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'XYCE'), verbose=True)

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Read settings from SDK test settings file
        absolute_path_settings_folder = str(Path(os.path.join(os.getcwd(), '../')).resolve())
        self.settings = read_settings_file(absolute_path_settings_folder=absolute_path_settings_folder, verbose=True)


    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_read_netlist(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_XYCE.cir')
        pXYCE = ParserXYCE(None)
        self.maxDiff = None
        # Check that these keys are not yet present
        self.assertTrue(hasattr(pXYCE, 'circuit_data'))  # this key should be present
        self.assertFalse(hasattr(pXYCE.circuit_data, 'Netlist'))  # this key should not be present

        # act
        pXYCE.read_netlist(file_name, flag_acquire_auxiliary_files=False, verbose=True)

        # assert 1 - check key presence
        self.assertTrue(hasattr(pXYCE, 'circuit_data'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'GeneralParameters'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'InitialConditions'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'AuxiliaryFiles'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'Stimuli'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'Libraries'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'GlobalParameters'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'Netlist'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'Options'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'Analysis'))
        self.assertTrue(hasattr(pXYCE.circuit_data, 'PostProcess'))
        # assert 2 - check key values against manually-written items
        self.assertListEqual([
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_PCs.lib",
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Diodes.lib",
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Busbars.lib",
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Thyristors.lib"],
            pXYCE.circuit_data.Libraries.component_libraries)
        self.assertDictEqual({'#Magnets': '4',
                              'L_MQXA': '0.0907',
                              'L_MQXB': '0.0185',
                              'C_ground_MQXA': '5.00E-08',
                              'C_ground_MQXB': '5.00E-08',
                              'R_parallel': '1.00E+03',
                              'R1': '385u',
                              'R2': '330u',
                              'R3': '330u',
                              'R4': '240u',
                              'k_I': '1',
                              'rc_par': '10m',
                              'l_par': '2u',
                              'c_par': '300m', },
                             pXYCE.circuit_data.GlobalParameters.global_parameters)
        self.assertDictEqual({'V(2)': '3','V(3)': '6'},pXYCE.circuit_data.InitialConditions.initial_conditions)
        self.assertEqual('transient', pXYCE.circuit_data.Analysis.analysis_type)
        self.assertEqual('0.0', pXYCE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual('2000.0', pXYCE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual('0.1', pXYCE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertDictEqual({  '0.0': '0.5',
                                '999.0': '1.0E-4',
                                '1000.7': '0.5', },
                             pXYCE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual('standard', pXYCE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pXYCE.circuit_data.PostProcess.probe.variables)
        expected_netlist = {}
        expected_netlist['x_RQX'] = Component()
        expected_netlist['x_RQX'].type = 'parametrized component'
        expected_netlist['x_RQX'].nodes = ['101', '104']
        expected_netlist['x_RQX'].value = 'PC_RQX'
        expected_netlist['x_RTQX1'] = Component()
        expected_netlist['x_RTQX1'].type = 'parametrized component'
        expected_netlist['x_RTQX1'].nodes = ['101', '102']
        expected_netlist['x_RTQX1'].value = 'PC_RTQX1'
        expected_netlist['x_RTQX2'] = Component()
        expected_netlist['x_RTQX2'].type = 'parametrized component'
        expected_netlist['x_RTQX2'].nodes = ['102', '103']
        expected_netlist['x_RTQX2'].value = 'PC_RTQX2'
        expected_netlist['x_FWD'] = Component()
        expected_netlist['x_FWD'].type = 'parametrized component'
        expected_netlist['x_FWD'].nodes = ['103', '104']
        expected_netlist['x_FWD'].value = 'FWD'
        expected_netlist['R1'] = Component()
        expected_netlist['R1'].type = 'standard component'
        expected_netlist['R1'].nodes = ['101', '201']
        expected_netlist['R1'].value = 'R1'
        expected_netlist['R2'] = Component()
        expected_netlist['R2'].type = 'standard component'
        expected_netlist['R2'].nodes = ['102', '202']
        expected_netlist['R2'].value = 'R2*(5m+3m)'
        expected_netlist['R3'] = Component()
        expected_netlist['R3'].type = 'standard component'
        expected_netlist['R3'].nodes = ['103', '203']
        expected_netlist['R3'].value = 'R3'
        expected_netlist['R4'] = Component()
        expected_netlist['R4'].type = 'standard component'
        expected_netlist['R4'].nodes = ['104', '204']
        expected_netlist['R4'].value = 'R4'
        expected_netlist['L_Q1'] = Component()
        expected_netlist['L_Q1'].type = 'standard component'
        expected_netlist['L_Q1'].nodes = ['202', '201']
        expected_netlist['L_Q1'].value = 'L_MQXA'
        expected_netlist['L_Q2a'] = Component()
        expected_netlist['L_Q2a'].type = 'standard component'
        expected_netlist['L_Q2a'].nodes = ['202b', '202']
        expected_netlist['L_Q2a'].value = 'L_MQXB'
        expected_netlist['L_Q2b'] = Component()
        expected_netlist['L_Q2b'].type = 'standard component'
        expected_netlist['L_Q2b'].nodes = ['203', '202b']
        expected_netlist['L_Q2b'].value = 'L_MQXB'
        expected_netlist['L_Q3'] = Component()
        expected_netlist['L_Q3'].type = 'standard component'
        expected_netlist['L_Q3'].nodes = ['204', '203']
        expected_netlist['L_Q3'].value = 'L_MQXA'
        expected_netlist['E_ABM_RANDOM'] = Component()
        expected_netlist['E_ABM_RANDOM'].type = 'controlled-source component'
        expected_netlist['E_ABM_RANDOM'].nodes = ['202','0']
        expected_netlist['E_ABM_RANDOM'].value = 'V(204,201)'
        expected_netlist['B_ABM_1'] = Component()
        expected_netlist['B_ABM_1'].type = 'nonlinear-dependent-source component'
        expected_netlist['B_ABM_1'].nodes = ['2', '0']
        expected_netlist['B_ABM_1'].value = 'V={sqrt(V(1))}'
        expected_netlist['Vg'] = Component()
        expected_netlist['Vg'].type = 'standard component'
        expected_netlist['Vg'].nodes = ['102', '0']
        expected_netlist['Vg'].value = '0'
        expected_netlist['V_control_1'] = Component()
        expected_netlist['V_control_1'].type = 'stimulus-controlled component'
        expected_netlist['V_control_1'].nodes = ['0_control_1', '0']
        expected_netlist['V_control_1'].value = 'FILE "vpwl.txt"'
        expected_netlist['V_control_2'] = Component()
        expected_netlist['V_control_2'].type = 'pulsed-source component'
        expected_netlist['V_control_2'].nodes = ['0_control_2', '0']
        expected_netlist['V_control_2'].value = '-1 1 2ns 2ns 2ns 50ns 100ns'
        expected_netlist['V_control_3'] = Component()
        expected_netlist['V_control_3'].type = 'pulsed-source component'
        expected_netlist['V_control_3'].nodes = ['0_control_3', '0']
        expected_netlist['V_control_3'].value = '-1 1 2ns 2ns 2ns 50ns 100ns'
        expected_netlist['I_control_4'] = Component()
        expected_netlist['I_control_4'].type = 'stimulus-controlled component'
        expected_netlist['I_control_4'].nodes = ['0_control_4', '0']
        expected_netlist['I_control_4'].value = '0S 0A 2S 3A 3S 2A 4S 2A 4.01S 5A'
        expected_netlist['I_control_5'] = Component()
        expected_netlist['I_control_5'].type = 'stimulus-controlled component'
        expected_netlist['I_control_5'].nodes = ['0_control_5', '0']
        expected_netlist['I_control_5'].value = 'FILE ipwl.csv'
        self.assertDictEqual(expected_netlist, dict(pXYCE.circuit_data.Netlist))
        # assert 3 - check key value has the two desired elements
        self.assertEqual(2, len(pXYCE.circuit_data.GeneralParameters.additional_files))


    def test_read_netlist_additional_files(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_XYCE.cir')
        pXYCE = ParserXYCE(None)

        # act - Note that flag_acquire_auxiliary_files=True
        pXYCE.read_netlist(file_name, flag_acquire_auxiliary_files=True, verbose=True)

        # assert - check key value corresponding to additional files
        self.assertTrue(len(pXYCE.circuit_data.GeneralParameters.additional_files) == 6)
        self.assertListEqual(
                        [
                            'vpwl.txt',
                            'ipwl.csv',
                            'C:\\GitLabRepository\\steam-pspice-library\\power_supply\\Items\\RQX_PCs.lib',
                            'C:\\GitLabRepository\\steam-pspice-library\\power_supply\\Items\\RQX_Diodes.lib',
                            'C:\\GitLabRepository\\steam-pspice-library\\power_supply\\Items\\RQX_Busbars.lib',
                            'C:\\GitLabRepository\\steam-pspice-library\\power_supply\\Items\\RQX_Thyristors.lib',
                        ],
                        pXYCE.circuit_data.GeneralParameters.additional_files)


    def test_read_netlist_withParametrizedComponent(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_withParametrizedComponent_XYCE.cir')
        pXYCE = ParserXYCE(None)
        self.maxDiff = None

        # act
        pXYCE.read_netlist(file_name, verbose=False)

        # assert - check key values against manually-written items
        self.assertListEqual([], pXYCE.circuit_data.Stimuli.stimulus_files)
        self.assertListEqual([], pXYCE.circuit_data.Libraries.component_libraries)
        self.assertEqual(None, pXYCE.circuit_data.GlobalParameters.global_parameters)
        self.assertEqual(None, pXYCE.circuit_data.Options.options_autoconverge)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.analysis_type)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertEqual({}, pXYCE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual(None, pXYCE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pXYCE.circuit_data.PostProcess.probe.variables)
        expected_netlist = {}
        expected_netlist['x_RQX'] = Component()
        expected_netlist['x_RQX'].type = 'parametrized component'
        expected_netlist['x_RQX'].nodes = ['101', '104']
        expected_netlist['x_RQX'].value = 'PC_RQX'
        expected_netlist['x_RQX'].parameters = {}
        expected_netlist['x_Crowbar'] = Component()
        expected_netlist['x_Crowbar'].type = 'parametrized component'
        expected_netlist['x_Crowbar'].nodes = ['0', '101']
        expected_netlist['x_Crowbar'].value = 'generic_crowbar'
        expected_netlist['x_Crowbar'].parameters = {'R_crowbar': 'R_crowbar', 'L_crowbar': '1e-6', 'C_crowbar': '10m'}
        self.assertDictEqual(expected_netlist, dict(pXYCE.circuit_data.Netlist))


    def test_read_netlist_withParametrizedComponentMultiLine(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_withParametrizedComponentMultiLine_XYCE.cir')
        pXYCE = ParserXYCE(None)
        self.maxDiff = None

        # act
        pXYCE.read_netlist(file_name, verbose=False)

        # assert - check key values against manually-written items
        self.assertListEqual([], pXYCE.circuit_data.Stimuli.stimulus_files)
        self.assertListEqual([], pXYCE.circuit_data.Libraries.component_libraries)
        self.assertEqual(None, pXYCE.circuit_data.GlobalParameters.global_parameters)
        self.assertEqual(None, pXYCE.circuit_data.Options.options_simulation)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.analysis_type)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual(None, pXYCE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertEqual({}, pXYCE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual(None, pXYCE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pXYCE.circuit_data.PostProcess.probe.variables)
        expected_netlist = {}
        expected_netlist['x_RQX'] = Component()
        expected_netlist['x_RQX'].type = 'parametrized component'
        expected_netlist['x_RQX'].nodes = ['101', '104']
        expected_netlist['x_RQX'].value = 'PC_RQX'
        expected_netlist['x_RQX'].parameters = {}
        expected_netlist['x_Crowbar'] = Component()
        expected_netlist['x_Crowbar'].type = 'parametrized component'
        expected_netlist['x_Crowbar'].nodes = ['0', '101']
        expected_netlist['x_Crowbar'].value = 'generic_crowbar'
        expected_netlist['x_Crowbar'].parameters = {
            'R_crowbar': 'R_crowbar',
            'L_crowbar': '1e-6',
            'C_crowbar': '10m',
            'additional_param1': '11m',
            'additional_param1b': '11m',
            'additional_param2': '12m+3m',
            'additional_param3': '12m',
            'additional_param4': '1e8',
        }
        self.assertDictEqual(expected_netlist, dict(pXYCE.circuit_data.Netlist))


    def test_write2XYCE_bare_minimum(self):
        # arrange - Define output file name. If file already exists, delete it
        file_name = os.path.join('output', 'XYCE', 'test_write2XYCE_bare_minimum', 'netlist_bare_minimum_TEST.cir')
        if os.path.isfile(file_name):
            os.remove(file_name)
            print('File {} already existed. It was deleted now.'.format(file_name))

        # arrange - Manually assign entries
        circuit_data = DataModelCircuit()
        new_Component = Component()
        new_Component.type = 'comment'
        new_Component.value = 'This is a comment'
        circuit_data.Netlist['comment1'] = new_Component
        circuit_data.Analysis.analysis_type = 'transient'
        circuit_data.Analysis.simulation_time.time_end = '1'

        # act
        pp = ParserXYCE(circuit_data=circuit_data)
        pp.write2XYCE(file_name, verbose=True)

        # assert
        self.assertTrue(os.path.isfile(file_name))
        print('File {} was generated.'.format(file_name))


    def test_copy_additional_files(self):
        # arrange - Define output file name. If file already exists, delete it
        input_path  = 'input'
        output_path = os.path.join('output', 'XYCE', 'copy_additional_files')
        delete_if_existing(output_path)
        file_names  = ['ipwl.csv', 'pwl.txt']
        for file_name in file_names:
            full_path_file_name = os.path.join(output_path, file_name)
            if os.path.isfile(full_path_file_name):
                os.remove(full_path_file_name)
                print('File {} already existed. It was deleted now.'.format(full_path_file_name))

        # arrange - Manually assign files to copy
        circuit_data = DataModelCircuit()
        for file_name in file_names:
            circuit_data.GeneralParameters.additional_files.append(os.path.join(input_path, file_name))

        # act
        pp = ParserXYCE(circuit_data=circuit_data, output_path=output_path)
        pp._copy_additional_files()

        # assert
        for file_name in file_names:
            full_path_file_name = os.path.join(output_path, file_name)
            self.assertTrue(os.path.isfile(full_path_file_name))
            print('File {} was generated.'.format(full_path_file_name))


    def test_copy_additional_files_translated(self):
        '''
        Test that checks if additional library and stimulus files are correctly copied and ,if necessary, translated.
        '''
        self.maxDiff = None
        # arrange - Define output file name. If file already exists, delete it
        input_path  = 'input'
        output_path = os.path.join('output', 'XYCE', 'copy_additional_files_translated')
        delete_if_existing(output_path)
        reference_path = 'references'
        file_names  = ['PSPICE_reference_library.lib', 'PSPICE_test_library2.lib', 'ipwl.csv']
        flag_translate = True
        for file_name in file_names:
            full_path_file_name = os.path.join(output_path, file_name)
            if os.path.isfile(full_path_file_name):
                os.remove(full_path_file_name)
                print('File {} already existed. It was deleted now.'.format(full_path_file_name))

        # arrange - Manually assign files to copy
        circuit_data = DataModelCircuit()
        for file_name in file_names:
            circuit_data.GeneralParameters.additional_files.append(os.path.join(input_path, file_name))

        # act
        pp = ParserXYCE(circuit_data=circuit_data, output_path=output_path)
        pp._copy_additional_files(flag_translate=flag_translate)

        # assert
        for file_name in file_names:
            full_path_file_name = os.path.join(output_path, file_name).replace('PSPICE', 'XYCE')
            self.assertTrue(os.path.isfile(full_path_file_name))
            print('File {} was generated.'.format(full_path_file_name))
            full_path_ref_file = os.path.join(reference_path, file_name).replace('PSPICE', 'XYCE')

            if file_name.endswith('.lib'):
                with open(full_path_file_name,'r') as f:
                    output = f.readlines()
                    output = [x.replace('\t',' ').replace(' \n', '\n').replace(' \n', '\n') for x in output]
                    output = [x for x in output if not 'csv' in x]
                with open(full_path_ref_file,'r') as f:
                    reference = f.readlines()
                    reference = [x.replace('\t',' ').replace(' \n', '\n').replace(' \n', '\n') for x in reference]
                    reference = [x for x in reference if not 'csv' in x]

                self.assertListEqual(output, reference)


    def test_write2xyce_manual(self):
        self.maxDiff = None
        # arrange - Define output file name. If file already exists, delete it
        output_path = os.path.join('output', 'XYCE', 'write2xyce_manual')
        delete_if_existing(output_path)
        file_name = os.path.join(output_path, 'XYCE', 'test_write2xyce_manual', 'netlist_TEST.cir')
        if os.path.isfile(file_name):
            os.remove(file_name)
            print('File {} already existed. It was deleted now.'.format(file_name))

        # arrange - Manually assign entries
        circuit_data = DataModelCircuit()
        circuit_data.GeneralParameters.circuit_name = 'TEST'
        circuit_data.Libraries.component_libraries = ['C:\Lib_1', 'C:\Lib_2', 'C:\Lib_3']
        circuit_data.GlobalParameters.global_parameters = {'I_0': '10050', 'L_busbar': '1.2e-6', 'R_circuit': '3m'}
        circuit_data.InitialConditions.initial_conditions = {'2': '5', '6': '1e8'}
        new_Component = Component()
        new_Component.type = 'comment'
        new_Component.value = 'This is a comment'
        circuit_data.Netlist['comment1'] = new_Component
        new_Component = Component()
        new_Component.type = 'standard component'
        new_Component.nodes = ['0a', '3'] # standard component
        new_Component.value = 'L_circuit'
        circuit_data.Netlist['L1'] = new_Component
        new_Component = Component()
        new_Component.type = 'parametrized component'  # parametrized component without any parameter
        new_Component.nodes = ['5a', '0a']
        new_Component.value = 'TripletDiode_5V'
        circuit_data.Netlist['xD_PC_RQX'] = new_Component
        new_Component = Component()
        new_Component.type = 'stimulus-controlled component'  # stimulus-controlled component
        new_Component.nodes = ['3', '5a', 'control']
        new_Component.value = 'FILE ipwl.csv'
        circuit_data.Netlist['I_PC'] = new_Component
        new_Component = Component()
        new_Component.type = 'controlled-source component'  # stimulus-controlled component
        new_Component.nodes = ['107', '108']
        new_Component.value = 'V(3,5a)'
        circuit_data.Netlist['E_ABM'] = new_Component
        new_Component = Component()
        new_Component.type = 'pulsed-source component'  # pulsed-source component
        new_Component.nodes = ['0_control', '0']
        new_Component.value = '-1 1 2ns 2ns 2ns 50ns 100ns'
        circuit_data.Netlist['V_control'] = new_Component
        new_Component = Component()
        new_Component.type = 'parametrized component'  # parametrized component with parameters
        new_Component.nodes = ['107', '108']
        new_Component.value = 'power_converter_minitrim'
        new_Component.parameters = {'R_crow': '1e-4', 'Cfilter': '6.6uF'}
        circuit_data.Netlist['xPC_minitrim'] = new_Component
        new_Component = Component()
        new_Component.type = 'parametrized component'  # parametrized component with many parameters, which cannot fit into 132 chars
        new_Component.nodes = ['108', '109']
        new_Component.value = 'power_converter_minitrim'
        new_Component.parameters = {
            'R_crow': '1e-4', 'Cfilter1': '6.6uF', 'Cfilter3': '6.6uF', 'Cfilter3': '6.6uF', 'Cfilter4': '6.6uF',
            'Cfilter5': '6.6uF', 'Cfilter6': '6.6uF', 'Cfilter7': '6.6uF','Cfilter8': '6.6uF', 'Cfilter9': '6.6uF',
            'Cfilter10': '6.6uF', 'Cfilter11': '6.6uF', 'Cfilter12': '6.6uF', 'Cfilter13': '6.6uF', 'Cfilter14': '6.6uF',
            'Cfilter15': '6.6uF', 'Cfilter16': '6.6uF', }
        circuit_data.Netlist['xPC_minitrim_2'] = new_Component
        circuit_data.Analysis.analysis_type = 'transient'
        circuit_data.Analysis.simulation_time.time_end = '1000'
        circuit_data.Analysis.simulation_time.min_time_step = '0.1'
        circuit_data.Analysis.simulation_time.time_schedule = {'0.0': '0.5', '999.0': '1.0E-4', '1000.7': '0.5',}
        circuit_data.AuxiliaryFiles.files_to_include = ['configurationFileFrequency.cir']
        circuit_data.PostProcess.probe.probe_type = 'standard'
        circuit_data.PostProcess.probe.variables = ['I(V_AC)', 'V(E_total_voltage)']
        circuit_data.Options.options_simulation = {'RELTOL': '0.01', 'ABSTOL': '0.0000000001'}

        # act
        pp = ParserXYCE(circuit_data=circuit_data)
        pp.write2XYCE(file_name, verbose=True)

        # assert 1 - file was generated
        self.assertTrue(os.path.isfile(file_name))
        print('File {} was generated.'.format(file_name))

        # assert 2 - read the file that was generated and check it has the same netlist
        pXYCE = ParserXYCE(None)
        pXYCE.read_netlist(file_name, flag_acquire_auxiliary_files=False, verbose=True)
        # circuit_data.Netlist.pop('comment1')  # Note: This element of circuit_data.Netlist is skipped because it is a comment and it is not parsed
        XYCE_dict = dict(circuit_data.Netlist)

        # Adapted dictionary entry to use smoothbsrc=1
        # XYCE_dict['E_ABM'].value = XYCE_dict['E_ABM'].value + 'smoothbsrc1'

        del XYCE_dict['comment1']# Note: This element of circuit_data.Netlist is skipped because it is a comment and it is not parsed
        self.assertDictEqual(XYCE_dict, dict(pXYCE.circuit_data.Netlist))


    def test_write2yaml(self, file_name='IPQ_2magnets'):
        # arrange
        file_name_full_path = os.path.join('input', file_name + '_XYCE.cir')
        pXYCE = ParserXYCE(None)
        # Check that these keys are not yet present
        self.assertTrue(hasattr(pXYCE, 'circuit_data'))  # this key should be present
        self.assertFalse(hasattr(pXYCE.circuit_data, 'Netlist'))  # this key should not be present
        # Define output file name. If file already exists, delete it
        output_file_full_path = os.path.join('output', 'XYCE', 'test_write2yaml', file_name + '.yaml')
        if os.path.isfile(output_file_full_path):
            os.remove(output_file_full_path)
            print('File {} already existed. It was deleted now.'.format(output_file_full_path))

        # act
        pXYCE.read_netlist(file_name_full_path, verbose=True)
        pXYCE.write2yaml(output_file_full_path, verbose=True)

        # assert - check that the output file exists
        self.assertTrue(os.path.isfile(output_file_full_path))
        print('File {} was generated.'.format(output_file_full_path))


    def test_read_write_netlist_consistency(self, circuit_name='IPQ_2magnets'):
        '''
            This test checks the following functionalities:
            - Read an input XYCE netlist file and store the information in a DataModelCircuit object
            - Write a XYCE netlist from the DataModelCircuit object
            - Check that the information parsed from the input netlist and output netlist are identical
            Known issue: Comments are not parsed

            :param circuit_name: Name of the circuit to test
            :return: None
        '''

        # arrange
        file_name_full_path = os.path.join('input', circuit_name + '_XYCE.cir')
        pXYCE_1 = ParserXYCE(None)
        # Define output file name. If file already exists, delete it
        file_name_rewritten = os.path.join('output', 'XYCE', 'test_read_write_netlist_consistency', circuit_name + '_REWRITTEN.cir')
        if os.path.isfile(file_name_rewritten):
            os.remove(file_name_rewritten)
            print('File {} already existed. It was deleted now.'.format(file_name_rewritten))

        file_name_rewritten_yaml = os.path.join('output', 'XYCE', 'test_read_write_netlist_consistency', circuit_name + '_modelData_REWRITTEN.yaml')
        # act
        # Read original netlist
        pXYCE_1.read_netlist(file_name_full_path, verbose=True)
        # Re-write netlist based on the acquired information
        pXYCE_1.write2XYCE(file_name_rewritten, verbose=True)
        pXYCE_1.write2yaml(file_name_rewritten_yaml, verbose=True)
        # Read the new netlist
        pXYCE_2 = ParserXYCE(None)
        pXYCE_2.read_netlist(file_name_rewritten, verbose=True)

        self.maxDiff = None
        # assert - check that the read information from the original and re-written files is the same
        self.assertEqual(pXYCE_1.circuit_data, pXYCE_2.circuit_data)   # This assert command is sufficient. The following rows can be used to debug
        # self.assertEqual(pXYCE_1.circuit_data.GeneralParameters, pXYCE_2.circuit_data.GeneralParameters)
        # self.assertEqual(pXYCE_1.circuit_data.AuxiliaryFiles, pXYCE_2.circuit_data.AuxiliaryFiles)
        # self.assertEqual(pXYCE_1.circuit_data.Libraries, pXYCE_2.circuit_data.Libraries)
        # self.assertListEqual(pXYCE_1.circuit_data.Libraries.component_libraries, pXYCE_2.circuit_data.Libraries.component_libraries)
        # self.assertDictEqual(dict(pXYCE_1.circuit_data.Netlist), dict(pXYCE_2.circuit_data.Netlist))
        # self.assertEqual(pXYCE_1.circuit_data.Options, pXYCE_2.circuit_data.Options)
        # self.assertEqual(pXYCE_1.circuit_data.Analysis, pXYCE_2.circuit_data.Analysis)
        # self.assertEqual(pXYCE_1.circuit_data.PostProcess, pXYCE_2.circuit_data.PostProcess)


    def test_read_write_yaml_consistency(self, circuit_name='IPQ_2magnets'):
        '''
            This test checks the following functionalities:
            - Read an input XYCE netlist file and store the information in a DataModelCircuit object
            - Write a yaml input file from the DataModelCircuit object
            - Read the yaml file that was just generated and store the information in a new DataModelCircuit object
            - Write a XYCE netlist from the new DataModelCircuit object
            - Check that the information parsed from the input netlist, yaml input file, and output netlist are identical
            Known issue: Comments are not parsed

            :param circuit_name: Name of the circuit to test
            :return: None
        '''
        # arrange
        file_name_full_path = os.path.join('input', circuit_name + '_XYCE.cir')
        pXYCE_1 = ParserXYCE(None)
        # Define output file names. If files already exist, delete them
        file_name_rewritten_yaml = os.path.join('output', 'XYCE', 'test_read_write_netlist_consistency', circuit_name + '_READ.yaml')
        file_name_rewritten_cir = os.path.join('output', 'XYCE', 'test_read_write_netlist_consistency', circuit_name + '_REWRITTEN_fromYAML.cir')
        if os.path.isfile(file_name_rewritten_yaml):
            os.remove(file_name_rewritten_yaml)
            print('File {} already existed. It was deleted now.'.format(file_name_rewritten_yaml))

        # act
        # Read original netlist
        pXYCE_1.read_netlist(file_name_full_path, flag_acquire_auxiliary_files=True, verbose=True)
        # Write yaml file with of the netlist
        pXYCE_1.circuit_data.GeneralParameters.circuit_name = circuit_name
        pXYCE_1.write2yaml(file_name_rewritten_yaml, verbose=True)
        # Read the new yaml file
        pXYCE_2 = ParserXYCE(None)
        pXYCE_2.readFromYaml(file_name_rewritten_yaml, verbose=True)
        # Make a new netlist based on the new yaml file
        pXYCE_2.write2XYCE(file_name_rewritten_cir, verbose=True)
        # Read the new netlist
        pXYCE_3 = ParserXYCE(None)
        pXYCE_3.read_netlist(file_name_rewritten_cir, verbose=True)

        # assert - check that the both output files contain the same information as the original file
        self.assertDictEqual(dict(pXYCE_1.circuit_data.Netlist), dict(pXYCE_2.circuit_data.Netlist))
        self.assertDictEqual(dict(pXYCE_1.circuit_data.Netlist), dict(pXYCE_3.circuit_data.Netlist))
        self.assertDictEqual(dict(pXYCE_2.circuit_data.Netlist), dict(pXYCE_3.circuit_data.Netlist))


    def test_translate_model_PSPICE_2_XYCE(self):
        """
            Test function checks if PSPICE model is correctly translated
        """
        pModel = ".subckt MB_Dipole_new_A (1_pIn 1_pMid 1_pOut 1_pGND)\n+ PARAMS: \n+ L_mag = 98e-3\n+ R_parallel = 100\n**** MAGNET ****\n" \
                 "V_monitor_in (1_pIn 100) 0\n****** APERTURE 1\nL1_frac0a (100 101_A1) {L_frac1a*f_L1a}\nR1_frac0a (100 102) {R1a}\n" \
                 "*** Parallel branch\nL_par (100 100_par) {0.05*0.049}\nC_par (100_par 102) {1000e-9}\nR_par (100_par 102) {100}\n" \
                 "*Coupled eddy current loop\nL_eqv_1 (eddy_1a eddy_1b) {1.07820418e-05}\nR_eqv_1 (eddy_1b eddy_1c) {0.0022169}\n" \
                 "**** BEAM-SCREEN COUPLING ****\n* Function to approximate the field in the beam-screen with x - current_level\n" \
                 ".FUNC B_field(x) {8.33/11850*x}\n.FUNC rho_cu(T,RRR) {(rho0(T,RRR)+rhoi(T)+rhoi_ref(T,RRR))}\n.ends"

        exp_xModel = '.subckt MB_Dipole_new_A (1_pIn 1_pMid 1_pOut 1_pGND)\n+ PARAMS: \n+ L_mag = 98e-3\n+ R_parallel = 100\n**** MAGNET ****\n' \
                     'V_monitor_in 1_pIn 100 0\n****** APERTURE 1\nL1_frac0a 100 101_A1 {L_frac1a*f_L1a}\nR1_frac0a 100 102 {R1a}\n' \
                     '*** Parallel branch\nL_par 100 100_par {0.05*0.049}\nC_par 100_par 102 {1000e-9}\nR_par 100_par 102 {100}\n' \
                     '*Coupled eddy current loop\nL_eqv_1 eddy_1a eddy_1b {1.07820418e-05}\nR_eqv_1 eddy_1b eddy_1c {0.0022169}\n' \
                     '**** BEAM-SCREEN COUPLING ****\n* Function to approximate the field in the beam-screen with x - current_level\n' \
                     '.FUNC B_field(x) {8.33/11850*x}\n.FUNC rho_cu(T,RRR) {(rho0(T,RRR)+rhoi(T)+rhoi_ref(T,RRR))}\n.ends'

        xModel = translate_model_PSPICE_2_XYCE(pModel)[0]

        self.maxDiff = None
        self.assertEqual(exp_xModel, xModel)


    def test_translate_library_PSPICE_2_XYCE(self):
        '''
            Test that checks if a library is correctly translated from PSPICE to XYCE
        '''
        self.maxDiff = None
        #Prepare
        file_input = os.path.join('input', 'PSPICE_reference_library.lib')
        file_check = os.path.join('references', 'XYCE_reference_library.lib')
        file_output = os.path.join('output', 'XYCE', 'test_translate_library_PSPICE_2_XYCE', 'XYCE_test_library.lib')
        #Act
        translate_library_PSPICE_2_XYCE(file_input, file_output)
        #Assert
        with open(file_output, 'r') as f:
            output = f.readlines()
            output = [x.replace('\t', ' ').replace(' \n', '\n').replace(' \n', '\n') for x in output]
            output = [x for x in output if not 'csv' in x]
        with open(file_check, 'r') as f:
            reference = f.readlines()
            reference = [x.replace('\t', ' ').replace(' \n', '\n').replace(' \n', '\n') for x in reference]
            reference = [x for x in reference if not 'csv' in x]

        self.assertListEqual(output, reference)


    def test_translate_stimulus(self):
        """
        Test that checks the correct translation of a stimulus from PSPICE logic into XYCE csv logic
        """
        file_input = os.path.join('input', 'STL_input.stl')
        stl_name1 = 'I_FPA_300'
        stl_name2 = 'I_FPA_50'
        output_path = os.path.join(os.getcwd(), 'output', 'XYCE', 'test_translate_stimulus')

        file_out1 = os.path.join(output_path, f'{stl_name1}.csv')
        file_out2 = os.path.join(output_path, f'{stl_name2}.csv')
        if os.path.isfile(file_out1):
            os.remove(file_out1)
            print('File {} already existed. It was deleted now.'.format(file_out1))
        if os.path.isfile(file_out2):
            os.remove(file_out2)
            print('File {} already existed. It was deleted now.'.format(file_out2))

        df_ref1 = pd.DataFrame.from_dict({'Time':[0.0, 0.2, 0.201, 70.0], 'Value': [300.0, 300.0, 0,0]})
        df_ref2 = pd.DataFrame.from_dict({'Time': [0.0, 0.2, 0.201, 70.0], 'Value': [50.0, 50.0, 0.0, 0.0]})

        translate_stimulus(stl_name1, input_file_path=file_input, output_path=output_path)
        translate_stimulus(stl_name2, input_file_path=file_input, output_path=output_path)

        self.assertTrue(os.path.isfile(file_out1))
        self.assertTrue(os.path.isfile(file_out2))

        df_out1 = pd.read_csv(file_out1, header=None, names=['Time', 'Value'])
        df_out2 = pd.read_csv(file_out2, header=None, names=['Time', 'Value'])

        pd.testing.assert_frame_equal(df_out1, df_ref1)
        pd.testing.assert_frame_equal(df_out2, df_ref2)


    def test_translate_create_run_full_model(self, name='RB'):
        '''
        Test that checks the full cycle of a model conversion PSPICE - XYCE
        Create the netlist from the yaml file, translate and copy the libraries and model, incl. stimuli
        Run the model and check if output exists
        '''
        verbose = True
        file_input_data = Path(f'..//builders//model_library//circuits//{name}//input//').resolve()
        file_input_yaml = os.path.join(file_input_data, f'modelData_{name}.yaml')

        output_path = os.path.join('output', 'XYCE', 'test_translate_create_run_full_model', name)
        delete_if_existing(output_path)

        pXYCE = ParserXYCE(None,path_input=file_input_data, output_path= output_path)
        pXYCE.readFromYaml(file_input_yaml, verbose=verbose)

        output_csd = os.path.join(output_path, f'{name}_XYCE.cir.csd')
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        else:
            shutil.rmtree(output_path)
            os.mkdir(output_path)

        if os.path.exists(output_csd):
            os.remove(output_csd)

        output_path_cir = os.path.join(output_path,f'{name}_XYCE.cir')
        pXYCE.write2XYCE(output_path_cir, flag_copy_additional_files=True, flag_resolve_library_paths=True, verbose=verbose)

        # dXYCE = DriverXYCE(self.settings.XYCE_path, output_path, verbose=verbose)
        # dXYCE.run_XYCE(name, suffix='_XYCE')
        # self.assertTrue(os.path.exists(output_csd))


    def test_translate_create_run_full_model_multipleCircuits(self):
        '''
        Test that checks the full cycle of a model conversion PSPICE - XYCE
        Create the netlist from the yaml file, translate and copy the libraries and model, incl. stimuli
        Run the model and check if output exists
        '''
        # arrange
        sim_suffix = '_XYCE'
        verbose = True
        list_circuits = ['RQX_HL-LHC', 'RU']
        #'RB','RCS', 'RQX' --> TODO: Implement coil-resistances in XYCE
        #'RCD_RCO','ROD', --> Singular matrix
        #'RQD_47magnets','RQD_51magnets' --> Undefined Stimuli

        for name in list_circuits:
            print(f'Currently testing {name}')
            print('Stimulus are missing. Tests are not fully run yet.')
            file_input_data = Path(f'..//builders//model_library//circuits//{name}//input//').resolve()
            file_input_yaml = os.path.join(file_input_data, f'modelData_{name}.yaml')

            output_path = os.path.join('output', 'XYCE', 'test_translate_create_run_full_model_multipleCircuits', f'XYCE_test_{name}')
            output_csd = os.path.join(output_path, f'{name}{sim_suffix}.csd')
            delete_if_existing(output_path, verbose=verbose)

            pXYCE = ParserXYCE(None,path_input=file_input_data, output_path= output_path)
            pXYCE.readFromYaml(file_input_yaml, verbose=verbose)

            output_path_cir = os.path.join(output_path, f'{name}{sim_suffix}.cir')
            pXYCE.write2XYCE(full_path_file_name=output_path_cir, flag_copy_additional_files=True, flag_resolve_library_paths=True, verbose=verbose)

            dXYCE = DriverXYCE(self.settings.XYCE_path, output_path, verbose=verbose)
            dXYCE.run_XYCE(nameCircuit=name, suffix=sim_suffix)
            self.assertTrue(os.path.exists(output_csd))
