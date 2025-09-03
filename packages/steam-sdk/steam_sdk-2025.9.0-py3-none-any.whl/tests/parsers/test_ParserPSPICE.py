import io
import unittest

from steam_sdk.parsers.ParserPSPICE import *
from steam_sdk.utils.delete_if_existing import delete_if_existing
from tests.TestHelpers import assert_equal_readable_files


class TestParserPSPICE(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'PSPICE'), verbose=True)

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


    def test_read_netlist(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_PSPICE.cir')
        pPSPICE = ParserPSPICE(None)
        # Check that these keys are not yet present
        self.assertTrue(hasattr(pPSPICE, 'circuit_data'))  # this key should be present
        self.assertFalse(hasattr(pPSPICE.circuit_data, 'Netlist'))  # this key should not be present

        # act
        pPSPICE.read_netlist(file_name, flag_acquire_auxiliary_files=False, verbose=True)

        # assert 1 - check key presence
        self.assertTrue(hasattr(pPSPICE, 'circuit_data'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'GeneralParameters'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'InitialConditions'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'AuxiliaryFiles'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'Stimuli'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'Libraries'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'GlobalParameters'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'Netlist'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'Options'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'Analysis'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'BiasPoints'))
        self.assertTrue(hasattr(pPSPICE.circuit_data, 'PostProcess'))
        # assert 2 - check key values against manually-written items
        self.assertListEqual(['C:\GitLabRepository\steam-pspice-library\Stimuli\I_PC_RQX.stl'], pPSPICE.circuit_data.Stimuli.stimulus_files)
        self.assertListEqual([
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_PCs.lib",
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Diodes.lib",
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Busbars.lib",
            "C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Thyristors.lib"],
            pPSPICE.circuit_data.Libraries.component_libraries)
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
                             pPSPICE.circuit_data.GlobalParameters.global_parameters)
        self.assertDictEqual({'I(x_PC_1.L_parasitic_series)': 'I_start',
                              },
                             pPSPICE.circuit_data.InitialConditions.initial_conditions)
        self.assertDictEqual({  'RELTOL': '0.00011',
                                'VNTOL': '0.00001',
                                'ABSTOL': '0.0001',
                                'CHGTOL': '0.000000000000001',
                                'GMIN': '0.000000000001',
                                'ITL1': '150',
                                'ITL2': '20',
                                'ITL4': '10',
                                'TNOM': '27',
                                'NUMDGT': '8', },
                             pPSPICE.circuit_data.Options.options_simulation)
        self.assertDictEqual({  'RELTOL': '0.051',
                                'VNTOL': '0.0001',
                                'ABSTOL': '0.0001',
                                'ITL1': '1000',
                                'ITL2': '1000',
                                'ITL4': '1000',
                                'PIVTOL': '0.0000000001', },
                             pPSPICE.circuit_data.Options.options_autoconverge)
        self.assertEqual('transient', pPSPICE.circuit_data.Analysis.analysis_type)
        self.assertEqual('0.0', pPSPICE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual('2000.0', pPSPICE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual('0.1', pPSPICE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertDictEqual({  '0.0': '0.5',
                                '999.0': '1.0E-4',
                                '1000.7': '0.5', },
                             pPSPICE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual('standard', pPSPICE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pPSPICE.circuit_data.PostProcess.probe.variables)
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
        expected_netlist['E_ABM_RANDOM'].nodes = ['202', '0']
        expected_netlist['E_ABM_RANDOM'].value = 'V(204, 201)'
        expected_netlist['Vg'] = Component()
        expected_netlist['Vg'].type = 'standard component'
        expected_netlist['Vg'].nodes = ['102', '0']
        expected_netlist['Vg'].value = '0'
        expected_netlist['V_control_1'] = Component()
        expected_netlist['V_control_1'].type = 'pulsed-source component'
        expected_netlist['V_control_1'].nodes = ['0_control_1', '0']
        expected_netlist['V_control_1'].value = '100 1000 {c_par} {100} 0 1G 1G'
        expected_netlist['V_control_2'] = Component()
        expected_netlist['V_control_2'].type = 'pulsed-source component'
        expected_netlist['V_control_2'].nodes = ['0_control_2', '0']
        expected_netlist['V_control_2'].value = '200 2000 {c_par} {100} 0 1G 1G'
        expected_netlist['V_control_3'] = Component()
        expected_netlist['V_control_3'].type = 'pulsed-source component'
        expected_netlist['V_control_3'].nodes = ['0_control_3', '0']
        expected_netlist['V_control_3'].value = '300 3000 {c_par} {100} 0 1G 1G'
        expected_netlist['I_control_4'] = Component()
        expected_netlist['I_control_4'].type = 'pulsed-source component'
        expected_netlist['I_control_4'].nodes = ['0_control_4', '0']
        expected_netlist['I_control_4'].value = '400 4000 {c_par} {100} 0 1G 1G'
        self.assertDictEqual(expected_netlist, dict(pPSPICE.circuit_data.Netlist))
        self.assertEqual('DUMMY_LOAD_BIAS_POINTS_983.bsp', pPSPICE.circuit_data.BiasPoints.load_bias_points.file_path)
        self.assertEqual('DUMMY_SAVE_BIAS_POINTS_756.bsp', pPSPICE.circuit_data.BiasPoints.save_bias_points.file_path)
        self.assertEqual('transient', pPSPICE.circuit_data.BiasPoints.save_bias_points.analysis_type)
        self.assertEqual(9578, pPSPICE.circuit_data.BiasPoints.save_bias_points.save_bias_time)
        # assert 3 - check key value is empty
        self.assertEqual(0, len(pPSPICE.circuit_data.GeneralParameters.additional_files))


    def test_read_netlist_additional_files(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_PSPICE.cir')
        pPSPICE = ParserPSPICE(None)

        # act - Note that flag_acquire_auxiliary_files=True
        pPSPICE.read_netlist(file_name, flag_acquire_auxiliary_files=True, verbose=True)

        # assert - check key value corresponding to additional files
        self.assertTrue(len(pPSPICE.circuit_data.GeneralParameters.additional_files) == 6)
        self.assertListEqual(
                        [
                            'C:\GitLabRepository\steam-pspice-library\Stimuli\I_PC_RQX.stl',
                            'C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_PCs.lib',
                            'C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Diodes.lib',
                            'C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Busbars.lib',
                            'C:\GitLabRepository\steam-pspice-library\power_supply\Items\RQX_Thyristors.lib',
                            'test_file.cir',
                        ],
                        pPSPICE.circuit_data.GeneralParameters.additional_files)


    def test_read_netlist_withParametrizedComponent(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_withParametrizedComponent_PSPICE.cir')
        pPSPICE = ParserPSPICE(None)

        # act
        pPSPICE.read_netlist(file_name, verbose=False)

        # assert - check key values against manually-written items
        self.assertListEqual([], pPSPICE.circuit_data.Stimuli.stimulus_files)
        self.assertListEqual([], pPSPICE.circuit_data.Libraries.component_libraries)
        self.assertEqual(None, pPSPICE.circuit_data.GlobalParameters.global_parameters)
        self.assertDictEqual({'all options': 'default'}, pPSPICE.circuit_data.Options.options_simulation)
        self.assertEqual(None, pPSPICE.circuit_data.Options.options_autoconverge)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.analysis_type)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertEqual({}, pPSPICE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual(None, pPSPICE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pPSPICE.circuit_data.PostProcess.probe.variables)
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
        self.assertDictEqual(expected_netlist, dict(pPSPICE.circuit_data.Netlist))


    def test_read_netlist_withParametrizedComponentMultiLine(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_withParametrizedComponentMultiLine_PSPICE.cir')
        pPSPICE = ParserPSPICE(None)

        # act
        pPSPICE.read_netlist(file_name, verbose=False)

        # assert - check key values against manually-written items
        self.assertListEqual([], pPSPICE.circuit_data.Stimuli.stimulus_files)
        self.assertListEqual([], pPSPICE.circuit_data.Libraries.component_libraries)
        self.assertEqual(None, pPSPICE.circuit_data.GlobalParameters.global_parameters)
        self.assertEqual(None, pPSPICE.circuit_data.Options.options_simulation)
        self.assertDictEqual({'all options': 'default'}, pPSPICE.circuit_data.Options.options_autoconverge)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.analysis_type)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertEqual({}, pPSPICE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual(None, pPSPICE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pPSPICE.circuit_data.PostProcess.probe.variables)
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
        self.assertDictEqual(expected_netlist, dict(pPSPICE.circuit_data.Netlist))


    def test_read_netlist_withDiode(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readNetlist_withDiode.cir')
        pPSPICE = ParserPSPICE(None)

        # act
        pPSPICE.read_netlist(file_name, verbose=False)

        # assert - check key values against manually-written items
        self.assertListEqual([], pPSPICE.circuit_data.Stimuli.stimulus_files)
        self.assertListEqual([], pPSPICE.circuit_data.Libraries.component_libraries)
        self.assertEqual(None, pPSPICE.circuit_data.GlobalParameters.global_parameters)
        self.assertDictEqual({'all options': 'default'}, pPSPICE.circuit_data.Options.options_simulation)
        self.assertEqual(None, pPSPICE.circuit_data.Options.options_autoconverge)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.analysis_type)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.time_start)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.time_end)
        self.assertEqual(None, pPSPICE.circuit_data.Analysis.simulation_time.min_time_step)
        self.assertEqual({}, pPSPICE.circuit_data.Analysis.simulation_time.time_schedule)
        self.assertEqual(None, pPSPICE.circuit_data.PostProcess.probe.probe_type)
        self.assertListEqual([], pPSPICE.circuit_data.PostProcess.probe.variables)
        expected_netlist = {}
        expected_netlist['D_1'] = Component()
        expected_netlist['D_1'].type = 'Diode component'
        expected_netlist['D_1'].nodes = ['101', '104']
        expected_netlist['D_1'].value = 'Diode_model'
        expected_netlist['D_1'].parameters = {}
        self.assertDictEqual(expected_netlist, dict(pPSPICE.circuit_data.Netlist))


    def test_write2pspice_bare_minimum(self):
        # arrange - Define output file name. If file already exists, delete it
        file_name = os.path.join('output', 'PSPICE', 'test_write2pspice_bare_minimum', 'netlist_bare_minimum_TEST.cir')
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
        pp = ParserPSPICE(circuit_data=circuit_data)
        pp.write2pspice(file_name, verbose=True)

        # assert
        self.assertTrue(os.path.isfile(file_name))
        print('File {} was generated.'.format(file_name))


    def test_copy_additional_files(self):
        # arrange - Define output file name. If file already exists, delete it
        input_path  = 'input'
        output_path = os.path.join('output', 'PSPICE', 'test_copy_additional_files')
        file_names  = ['additional_file_2_TEST.stl', 'additional_file_1_TEST.stl']
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
        pp = ParserPSPICE(circuit_data=circuit_data)
        pp.copy_additional_files(output_path=output_path)

        # assert
        for file_name in file_names:
            full_path_file_name = os.path.join(output_path, file_name)
            self.assertTrue(os.path.isfile(full_path_file_name))
            print('File {} was generated.'.format(full_path_file_name))


    def test_write2spice_manual(self):
        # arrange - Define output file name. If file already exists, delete it
        file_name = os.path.join('output', 'PSPICE', 'test_write2spice_manual', 'netlist_TEST.cir')
        if os.path.isfile(file_name):
            os.remove(file_name)
            print('File {} already existed. It was deleted now.'.format(file_name))

        # arrange - Manually assign entries
        circuit_data = DataModelCircuit()
        circuit_data.Stimuli.stimulus_files = ['C:\GitLabRepository\steam-pspice-library\Stimuli\I_PC_RQX_1.stl', 'C:\GitLabRepository\steam-pspice-library\Stimuli\I_PC_RQX_2.stl']
        circuit_data.Libraries.component_libraries = ['C:\Lib_1', 'C:\Lib_2', 'C:\Lib_3']
        circuit_data.GlobalParameters.global_parameters = {'I_0': '10050', 'L_busbar': '1.2e-6', 'R_circuit': '3m'}
        circuit_data.InitialConditions.initial_conditions = {'L1': '1003', 'xD_PC_RQX.L_parasitic': 'L_busbar'}
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
        new_Component.value = 'I_pc_trimQ1'
        circuit_data.Netlist['I_PC'] = new_Component
        new_Component = Component()
        new_Component.type = 'controlled-source component'  # stimulus-controlled component
        new_Component.nodes = ['107', '108']
        new_Component.value = 'V(3, 5a)'
        circuit_data.Netlist['E_ABM'] = new_Component
        new_Component = Component()
        new_Component.type = 'pulsed-source component'  # pulsed-source component
        new_Component.nodes = ['0_control', '0']
        new_Component.value = '500 5000 {I_0} {500} 0 5G 5G'
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
        new_Component = Component()
        new_Component.type = 'Diode component'  # Diode component with dedicated model
        new_Component.nodes = ['108', '109']
        new_Component.value = 'Diode_custom_model'
        circuit_data.Netlist['D_1'] = new_Component
        circuit_data.Options.options_simulation = {'all options': 'default'}
        circuit_data.Options.options_autoconverge = {'all options': 'default'}
        circuit_data.Analysis.analysis_type = 'transient'
        circuit_data.Analysis.simulation_time.time_end = '1000'
        circuit_data.Analysis.simulation_time.min_time_step = '0.1'
        circuit_data.Analysis.simulation_time.time_schedule = {'0.0': '0.5', '999.0': '1.0E-4', '1000.7': '0.5',}
        circuit_data.BiasPoints.load_bias_points.file_path = 'DUMMY_LOAD_BIAS_POINTS.bsp'
        circuit_data.BiasPoints.save_bias_points.file_path = 'DUMMY_SAVE_BIAS_POINTS.bsp'
        circuit_data.BiasPoints.save_bias_points.analysis_type = 'transient'
        circuit_data.BiasPoints.save_bias_points.save_bias_time = 9578
        circuit_data.AuxiliaryFiles.files_to_include = ['configurationFileFrequency.cir']
        circuit_data.PostProcess.probe.probe_type = 'CSDF'
        circuit_data.PostProcess.probe.variables = ['I(V_AC)', 'V(E_total_voltage)']

        # act
        pp = ParserPSPICE(circuit_data=circuit_data)
        pp.write2pspice(file_name, verbose=True)

        # assert 1 - file was generated
        self.assertTrue(os.path.isfile(file_name))
        print('File {} was generated.'.format(file_name))

        # assert 2 - read the file that was generated and check it has the same netlist
        pPSPICE = ParserPSPICE(None)
        pPSPICE.read_netlist(file_name, flag_acquire_auxiliary_files=False, verbose=True)
        # circuit_data.Netlist.pop('comment1')  # Note: This element of circuit_data.Netlist is skipped because it is a comment and it is not parsed
        pSPICE_dict = dict(circuit_data.Netlist)
        del pSPICE_dict['comment1']# Note: This element of circuit_data.Netlist is skipped because it is a comment and it is not parsed
        self.assertDictEqual(pSPICE_dict, dict(pPSPICE.circuit_data.Netlist))


    def test_write2yaml(self, file_name='RB'):
        # arrange
        file_name_full_path = os.path.join('input', file_name + '.cir')
        pPSPICE = ParserPSPICE(None)
        # Check that these keys are not yet present
        self.assertTrue(hasattr(pPSPICE, 'circuit_data'))  # this key should be present
        self.assertFalse(hasattr(pPSPICE.circuit_data, 'Netlist'))  # this key should not be present
        # Define output file name. If file already exists, delete it
        output_file_full_path = os.path.join('output', 'PSPICE', 'test_write2yaml', file_name + '.yaml')
        if os.path.isfile(output_file_full_path):
            os.remove(output_file_full_path)
            print('File {} already existed. It was deleted now.'.format(output_file_full_path))

        # act
        pPSPICE.read_netlist(file_name_full_path, verbose=True)
        pPSPICE.write2yaml(output_file_full_path, verbose=True)

        # assert - check that the output file exists
        self.assertTrue(os.path.isfile(output_file_full_path))
        print('File {} was generated.'.format(output_file_full_path))


    def test_read_write_netlist_consistency(self, circuit_name='IPQ_2magnets'):
        '''
            This test checks the following functionalities:
            - Read an input PSPICE netlist file and store the information in a DataModelCircuit object
            - Write a PSPICE netlist from the DataModelCircuit object
            - Check that the information parsed from the input netlist and output netlist are identical
            Known issue: Comments are not parsed

            :param circuit_name: Name of the circuit to test
            :return: None
        '''

        # arrange
        file_name_full_path = os.path.join('input', circuit_name + '.cir')
        pPSPICE_1 = ParserPSPICE(None)
        # Define output file name. If file already exists, delete it
        file_name_rewritten = os.path.join('output', 'PSPICE', 'test_read_write_netlist_consistency', circuit_name + '_REWRITTEN.cir')
        if os.path.isfile(file_name_rewritten):
            os.remove(file_name_rewritten)
            print('File {} already existed. It was deleted now.'.format(file_name_rewritten))

        file_name_rewritten_yaml = os.path.join('output', 'PSPICE', 'test_read_write_netlist_consistency', circuit_name + '_modelData_REWRITTEN.yaml')
        # act
        # Read original netlist
        pPSPICE_1.read_netlist(file_name_full_path, verbose=True)
        # Re-write netlist based on the acquired information
        pPSPICE_1.write2pspice(file_name_rewritten, verbose=True)
        pPSPICE_1.write2yaml(file_name_rewritten_yaml, verbose=True)
        # Read the new netlist
        pPSPICE_2 = ParserPSPICE(None)
        pPSPICE_2.read_netlist(file_name_rewritten, verbose=True)

        # assert - check that the read information from the original and re-written files is the same
        self.assertEqual(pPSPICE_1.circuit_data, pPSPICE_2.circuit_data)  # This assert command is sufficient. The following rows can be used to debug
        # self.assertEqual(pPSPICE_1.circuit_data.GeneralParameters, pPSPICE_2.circuit_data.GeneralParameters)
        # self.assertEqual(pPSPICE_1.circuit_data.AuxiliaryFiles, pPSPICE_2.circuit_data.AuxiliaryFiles)
        # self.assertEqual(pPSPICE_1.circuit_data.Stimuli, pPSPICE_2.circuit_data.Stimuli)
        # self.assertEqual(pPSPICE_1.circuit_data.Libraries, pPSPICE_2.circuit_data.Libraries)
        # self.assertListEqual(pPSPICE_1.circuit_data.Libraries.component_libraries, pPSPICE_2.circuit_data.Libraries.component_libraries)
        # self.assertListEqual(pPSPICE_1.circuit_data.Netlist, pPSPICE_2.circuit_data.Netlist)
        # self.assertEqual(pPSPICE_1.circuit_data.Options, pPSPICE_2.circuit_data.Options)
        # self.assertEqual(pPSPICE_1.circuit_data.Analysis, pPSPICE_2.circuit_data.Analysis)
        # self.assertEqual(pPSPICE_1.circuit_data.PostProcess, pPSPICE_2.circuit_data.PostProcess)


    def test_read_write_yaml_consistency(self, circuit_name='IPQ_2magnets'):
        '''
            This test checks the following functionalities:
            - Read an input PSPICE netlist file and store the information in a DataModelCircuit object
            - Write a yaml input file from the DataModelCircuit object
            - Read the yaml file that was just generated and store the information in a new DataModelCircuit object
            - Write a PSPICE netlist from the new DataModelCircuit object
            - Check that the information parsed from the input netlist, yaml input file, and output netlist are identical
            Known issue: Comments are not parsed

            :param circuit_name: Name of the circuit to test
            :return: None
        '''
        # arrange
        file_name_full_path = os.path.join('input', circuit_name + '.cir')
        pPSPICE_1 = ParserPSPICE(None)
        # Define output file names. If files already exist, delete them
        file_name_rewritten_yaml = os.path.join('output', 'PSPICE', 'test_read_write_netlist_consistency', circuit_name + '_READ.yaml')
        file_name_rewritten_cir = os.path.join('output', 'PSPICE', 'test_read_write_netlist_consistency', circuit_name + '_REWRITTEN_fromYAML.cir')
        if os.path.isfile(file_name_rewritten_yaml):
            os.remove(file_name_rewritten_yaml)
            print('File {} already existed. It was deleted now.'.format(file_name_rewritten_yaml))

        # act
        # Read original netlist
        pPSPICE_1.read_netlist(file_name_full_path, flag_acquire_auxiliary_files=True, verbose=True)
        # Write yaml file with of the netlist
        pPSPICE_1.circuit_data.GeneralParameters.circuit_name = circuit_name
        pPSPICE_1.write2yaml(file_name_rewritten_yaml, verbose=True)
        # Read the new yaml file
        pPSPICE_2 = ParserPSPICE(None)
        pPSPICE_2.readFromYaml(file_name_rewritten_yaml, verbose=True)
        # Make a new netlist based on the new yaml file
        pPSPICE_2.write2pspice(file_name_rewritten_cir, verbose=True)
        # Read the new netlist
        pPSPICE_3 = ParserPSPICE(None)
        pPSPICE_3.read_netlist(file_name_rewritten_cir, verbose=True)

        # assert - check that the both output files contain the same information as the original file
        self.assertDictEqual(dict(pPSPICE_1.circuit_data.Netlist), dict(pPSPICE_2.circuit_data.Netlist))
        self.assertDictEqual(dict(pPSPICE_1.circuit_data.Netlist), dict(pPSPICE_3.circuit_data.Netlist))
        self.assertDictEqual(dict(pPSPICE_2.circuit_data.Netlist), dict(pPSPICE_3.circuit_data.Netlist))


    def test_read_write_netlist_consistency_multiple(self):
        '''
            Run the test test_read_write_netlist_consistency() for all the circuits in the tests/parsers/input folder
        '''
        # circuit_names = ['IPQ_2magnets', 'RQX', 'RQX_HL-LHC', 'RB']  # Manually-defined list
        circuit_names = os.listdir('input')  # List all files in the input folder
        circuit_names = [x.replace('.cir', '') for x in circuit_names if ".cir" in x]  # Keep entries with ".cir", but delete ".cir" from the string
        print('Found {} circuits: {}'.format(len(circuit_names), circuit_names))
        for circuit_name in circuit_names:
            if 'XYCE' in circuit_name: continue
            print('###################################################')
            print('Now working on circuit: {}'.format(circuit_name))
            self.test_read_write_netlist_consistency(circuit_name=circuit_name)


    def test_read_write_yaml_consistency_multiple(self):
        '''
            Run the test test_read_write_yaml_consistency() for all the circuits in the tests/parsers/input folder
        '''
        # circuit_names = ['IPQ_2magnets', 'RQX', 'RQX_HL-LHC', 'RB']  # Manually-defined list
        circuit_names = os.listdir('input')  # List all files in the input folder
        circuit_names = [x.replace('.cir', '') for x in circuit_names if ".cir" in x]  # Keep entries with ".cir", but delete ".cir" from the string
        print('Found {} circuits: {}'.format(len(circuit_names), circuit_names))
        for circuit_name in circuit_names:
            if 'XYCE' in circuit_name: continue
            print('###################################################')
            print('Now working on circuit: {}'.format(circuit_name))
            self.test_read_write_yaml_consistency(circuit_name=circuit_name)


    def test_interpolate_resistance(self):
        '''
        Test to compare the calculation of the interpolation on different current level
        '''
        path_resources = os.path.join(os.getcwd(), 'input', 'Interpolation_Resistance_RB.csv')
        # Run different current level and compare result
        df = pd.DataFrame()
        Current_Level_Trials = [11000, 11500, 6890, 12500, 470, 3320]
        for k in Current_Level_Trials:
            [time, new_R1, new_R2]  = InterpolateResistance(k, path_resources)
            entry =  pd.DataFrame.from_dict({f'time_{k}': time,f'R1_{k}': new_R1,f'R2_{k}': new_R2})
            entry = entry.fillna(0)
            df = pd.concat([df, entry], axis=1)

        output_path = os.path.join(os.getcwd(), 'references', 'RB_Reference_Interpolation.csv')
        reference_data = pd.read_csv(output_path).iloc[:, 1:]

        pd.testing.assert_frame_equal(df, reference_data)


    def test_write_resistance_stimuli(self):
        '''
        Test to compare two Stimuli files for a different set of current levels, magnets and time-shifts
        '''
        path_resources = os.path.join(os.getcwd(), 'input', 'Interpolation_Resistance_RB.csv')
        Current_Level_Trials = [5560*2, 700*2, 2650*2]
        tShifts = [0.2, 20, 250]
        magnets = [2, 50, 89]
        magnet_type = [1]*154
        outputfile = os.path.join(os.getcwd(), 'output', 'PSPICE', 'test_write_resistance_stimuli', 'TEST_Interpolation_Resistance.stl')
        if os.path.exists(outputfile): os.remove(outputfile)

        writeStimuliFromInterpolation(Current_Level_Trials, 154, 2, magnets, tShifts, outputfile, path_resources, 'Linear', 'a', 100, magnet_type)

        ref_path = os.path.join(os.getcwd(), 'references', 'Reference_Interpolation_Resistance.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)), list(io.open(ref_path)))

    def test_interpolate_resistance_IPQ(self):
        '''
        Test to compare the calculation of the interpolation on different current level in IPQ circuits
        '''
        path_resources = os.path.join(os.getcwd(),'input','Interpolation_Resistance_MQY.csv')
        # Run different current level and compare result
        df = pd.DataFrame()
        Current_Level_Trials = [150, 2000, 970, 470, 3500, 3320]
        for k in Current_Level_Trials:
            [time, new_R1]  = InterpolateResistance(k, path_resources, n_apertures=1, plot_interpolation=False)
            entry =  pd.DataFrame.from_dict({f'time_{k}': time,f'R1_{k}': new_R1})
            entry = entry.fillna(0)
            df = pd.concat([df, entry], axis=1)

        output_path = os.path.join(os.getcwd(), 'references', 'MQY_Reference_Interpolation.csv')
        reference_data = pd.read_csv(output_path).iloc[:, 1:]

        pd.testing.assert_frame_equal(df, reference_data, rtol=0.01)

    def test_write_resistance_stimuli_MQY(self):
        '''
        Test to compare two Stimuli files for a different set of current levels, magnets and time-shifts
        '''
        path_resources = os.path.join(os.getcwd(),'input','Interpolation_Resistance_MQY.csv')
        Current_Level_Trials = [150, 3320]
        tShifts = [757.1, 757.2]
        magnets = [1, 2]
        outputfile = os.path.join(os.getcwd(), 'output', 'PSPICE', 'test_write_resistance_stimuli_MQY', 'TEST_Interpolation_Resistance_MQY.stl')
        if os.path.exists(outputfile): os.remove(outputfile)

        writeStimuliFromInterpolation(Current_Level_Trials, 2, 1, magnets, tShifts, outputfile, path_resources)

        ref_path = os.path.join(os.getcwd(), 'references', 'Reference_Interpolation_Resistance_MQY.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)),list(io.open(ref_path)))


    def test_write_resistance_stimuli_general_MQY(self):
        '''
        Test to compare two Stimuli files for a different set of current levels, magnets and time-shifts
        '''
        path_resources = 2 * [os.path.join(os.getcwd(), 'input', 'Interpolation_Resistance_MQY.csv')]  # note that this is a list
        Current_Level_Trials = [150, 3320]
        tShifts = [757.1, 757.2]
        magnets = [1, 2]
        outputfile = os.path.join(os.getcwd(), 'output', 'PSPICE', 'test_write_resistance_stimuli_general_MQY', 'TEST_Interpolation_Resistance_General_MQY.stl')
        magnet_type = [1, 1]
        if os.path.exists(outputfile): os.remove(outputfile)

        writeStimuliFromInterpolation(Current_Level_Trials, 2, 1, magnets, tShifts, outputfile, path_resources, InterpolationType='Linear', type_stl='a', sparseTimeStepping=100, magnet_type=magnet_type)

        ref_path = os.path.join(os.getcwd(), 'references', 'Reference_Interpolation_Resistance_MQY.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)),list(io.open(ref_path)))


    def test_write_resistance_stimuli_general_withStringInput_MQY(self):
        '''
        Test to compare two Stimuli files for a different set of current levels, magnets and time-shifts
        '''
        path_resources = os.path.join(os.getcwd(), 'input', 'Interpolation_Resistance_MQY.csv')  # note that this is a NOT a list
        Current_Level_Trials = [150, 3320]
        tShifts = [757.1, 757.2]
        magnets = [1, 2]
        outputfile = os.path.join(os.getcwd(), 'output', 'PSPICE', 'test_write_resistance_stimuli_general_withStringInput_MQY', 'TEST_Interpolation_Resistance_General_MQY.stl')
        magnet_type = [1, 1]
        if os.path.exists(outputfile): os.remove(outputfile)

        writeStimuliFromInterpolation(Current_Level_Trials, 2, 1, magnets, tShifts, outputfile, path_resources, InterpolationType='Linear', type_stl='a', sparseTimeStepping=100, magnet_type=magnet_type)

        ref_path = os.path.join(os.getcwd(),'references', 'Reference_Interpolation_Resistance_MQY.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)),list(io.open(ref_path)))

    def test_write_resistance_stimuli_general_withStringInput_MQY_RQD_51magnets(self):
        '''
        Test to compare two Stimuli files for a different set of current levels, magnets and time-shifts with two different magnet types in same circuit
        '''
        path_resources = [os.path.join(os.getcwd(), 'input', 'Interpolation_Resistance_MQY.csv'),os.path.join(os.getcwd(), 'input', 'Interpolation_Resistance_RQD_51magnets.csv')] # note that this is a NOT a list
        Current_Level_Trials = [850, 3320]
        tShifts = [757.1, 757.2]
        magnets = [1, 2]
        outputfile = os.path.join(os.getcwd(), 'output', 'PSPICE', 'test_write_resistance_stimuli_general_withStringInput_MQY_RQD_51magnets', 'TEST_Interpolation_Resistance_General_MQY_RQD_51magnets.stl')
        magnet_type = [1, 2]
        if os.path.exists(outputfile): os.remove(outputfile)

        writeStimuliFromInterpolation(Current_Level_Trials, 2, 1, magnets, tShifts, outputfile, path_resources, InterpolationType='Linear', type_stl='a', sparseTimeStepping=100, magnet_type=magnet_type)

        ref_path = os.path.join(os.getcwd(),'references', 'Reference_MQY_RQD_51magnets.stl')
        tst_path = outputfile
        self.assertListEqual(list(io.open(tst_path)),list(io.open(ref_path)))

    def test_write_coil_resistance_interpolation_file(self):
        '''
        Test the function write_coil_resistance_interpolation_file(), which writes a coil resistance interpolation file
        with a format compatible with the function ParserPSPICE.writeStimuliFromInterpolation_general()
        '''

        # arrange
        path_csv_file = os.path.join('output', 'PSPICE', 'test_write_coil_resistance_interpolation_file', 'test_write_coil_resistance_interpolation_file.csv')
        current_levels = [11850.75, 9000.25, 3000]
        list_times = [
            [0.00E-04, 1.00E-04, 2.00E-04, 3.00E-04, 4.00E-04, 5.00E-04, 6.00E-04, 7.00E-04, 8.00E-04, 9.00E-04, ],
            [0.00E-04, 1.00E-04, 2.00E-04, 3.00E-04, 4.00E-04, 5.00E-04, 6.00E-04, 7.00E-04, 8.00E-04, 9.00E-04, ],
            [0.00E-04, 1.00E-04, 2.00E-04, 3.00E-04, 4.00E-04, 5.00E-04, 6.00E-04, 7.00E-04, 8.00E-04, 9.00E-04, ],
        ]
        list_coil_resistances = [
            [0.00E-02, 1.00E-02, 2.00E-02, 3.00E-02, 4.00E-02, 5.00E-02, 6.00E-02, 7.00E-02, 8.00E-02, 9.00E-02, ],
            [0.00E-01, 1.00E-01, 2.00E-01, 3.00E-01, 4.00E-01, 5.00E-01, 6.00E-01, 7.00E-01, 8.00E-01, 9.00E-01, ],
            [0.00E-00, 1.00E-00, 2.00E-00, 3.00E-00, 4.00E-00, 5.00E-00, 6.00E-00, 7.00E-00, 8.00E-00, 9.00E-00, ],
        ]
        if os.path.exists(path_csv_file):
            os.remove(path_csv_file)
        path_reference_file = os.path.join('references', 'reference_write_coil_resistance_interpolation_file.csv')

        # act
        write_coil_resistance_interpolation_file(path_csv_file, current_levels, list_times, list_coil_resistances)

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_csv_file)))


    def test_write_time_stimulus_file(self):
        '''
        Test the function write_time_stimulus_file(), which writes a stimulus file compatible with PSPICE
        '''

        # arrange
        path_stimulus_file = os.path.join('output', 'PSPICE', 'write_time_stimulus_file', 'test_write_time_stimulus_file.stl')
        dict_signals = {
                "tim_vec": [0.000, 0.015, 0.016, 1000.0],
                "I_power_supply": [14500.0, 14500.0, 0, 0],
                "V_cliq_control_1": [0.0, 0.0, 2.0, 2.0],
                "V_cliq_control_2": [0.0, 0.0, 1.0, 1.0]
        }
        name_time_signal = 'tim_vec'
        path_reference_file = os.path.join('references', 'PSPICE', 'test_write_time_stimulus_file.stl')

        # act
        write_time_stimulus_file(path_file=path_stimulus_file, dict_signals=dict_signals, name_time_signal=name_time_signal)

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_stimulus_file)))

    def test_write_time_stimulus_file__with_dict_translate(self):
        '''
        Test the function write_time_stimulus_file(), which writes a stimulus file compatible with PSPICE
        This test also checks the correct use of the dict_translate_signal_names argument
        '''

        # arrange
        path_stimulus_file = os.path.join('output', 'PSPICE', 'write_time_stimulus_file', 'test_write_time_stimulus_file__with_dict_translate.stl')
        dict_signals = {
                "tim_vec": [0.000, 0.015, 0.016, 1000.0],
                "I_power_supply": [14500.0, 14500.0, 0, 0],
                "V_cliq_control_1": [0.0, 0.0, 2.0, 2.0],
                "V_cliq_control_2": [0.0, 0.0, 1.0, 1.0]
        }
        dict_translate_signal_names = {'I_power_supply': 'I_power_supply_MOD', 'V_cliq_control_2': 'V_cliq_control_2_MOD'}
        name_time_signal = 'tim_vec'
        path_reference_file = os.path.join('references', 'PSPICE', 'test_write_time_stimulus_file__with_dict_translate.stl')

        # act
        write_time_stimulus_file(path_file=path_stimulus_file, dict_signals=dict_signals, name_time_signal=name_time_signal, dict_translate_signal_names=dict_translate_signal_names)

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_stimulus_file)))

    def test_write_time_stimulus_file__with_time_shift(self):
        '''
        Test the function write_time_stimulus_file(), which writes a stimulus file compatible with PSPICE
        This test also checks the correct use of the time_shift argument
        '''

        # arrange
        path_stimulus_file = os.path.join('output', 'PSPICE', 'write_time_stimulus_file', 'test_write_time_stimulus_file__with_time_shift.stl')
        dict_signals = {
                "tim_vec": [0.000, 0.015, 0.016, 1000.0],
                "I_power_supply": [14500.0, 14500.0, 0, 0],
                "V_cliq_control_1": [0.0, 0.0, 2.0, 2.0],
                "V_cliq_control_2": [0.0, 0.0, 1.0, 1.0]
        }
        dict_translate_signal_names = {}
        time_shift = 0.0075
        name_time_signal = 'tim_vec'
        path_reference_file = os.path.join('references', 'PSPICE', 'test_write_time_stimulus_file__with_time_shift.stl')

        # act
        write_time_stimulus_file(path_file=path_stimulus_file, dict_signals=dict_signals, name_time_signal=name_time_signal, dict_translate_signal_names=dict_translate_signal_names, time_shift=time_shift)

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_stimulus_file)))

    def test_write_time_stimulus_file__with_time_shift_zero(self):
        '''
        Test the function write_time_stimulus_file(), which writes a stimulus file compatible with PSPICE
        This test also checks the correct use of the time_shift argument in the case where all data points are lower than time_shift
        '''

        # arrange
        path_stimulus_file = os.path.join('output', 'PSPICE', 'write_time_stimulus_file', 'test_write_time_stimulus_file__with_time_shift_zero.stl')
        dict_signals = {
                "tim_vec": [0.000, 0.015, 0.016, 1000.0],
                "I_power_supply": [14500.0, 14500.0, 0, 0],
                "V_cliq_control_1": [0.0, 0.0, 2.0, 2.0],
                "V_cliq_control_2": [0.0, 0.0, 1.0, 1.0]
        }
        dict_translate_signal_names = {}
        time_shift = 1e4  # This is chosen to be higher than the maximum time point
        name_time_signal = 'tim_vec'
        path_reference_file = os.path.join('references', 'PSPICE', 'test_write_time_stimulus_file__with_time_shift_zero.stl')

        # act
        write_time_stimulus_file(path_file=path_stimulus_file, dict_signals=dict_signals, name_time_signal=name_time_signal, dict_translate_signal_names=dict_translate_signal_names, time_shift=time_shift)

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_stimulus_file)))


    def test_write_time_stimulus_file__individual_time_vectors(self):
        '''
        Test the function write_time_stimulus_file(), which writes a stimulus file compatible with PSPICE
        This test also checks the correct use of the mode argument
        '''

        # arrange
        path_stimulus_file = os.path.join('output', 'PSPICE', 'write_time_stimulus_file', 'test_write_time_stimulus_file__individual_time_vectors.stl')
        dict_signals = {
                "I_power_supply": {"tim_vec": [0.000, 0.015, 0.016, 1000.0], "value": [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {"tim_vec": [0.000, 0.025, 0.026, 10000.0], "value": [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {"tim_vec": [0.000, 0.15, 0.16, 1100.0], "value": [0.0, 0.0, 1.0, 1.0]},
        }
        name_time_signal = 'tim_vec'
        path_reference_file = os.path.join('references', 'PSPICE', 'test_write_time_stimulus_file__individual_time_vectors.stl')

        # act
        write_time_stimulus_file(path_file=path_stimulus_file, dict_signals=dict_signals, name_time_signal=name_time_signal,
                                 mode='individual_time_vectors')

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_stimulus_file)))

    def test_write_time_stimulus_file__with_dict_translate__individual_time_vectors(self):
        '''
        Test the function write_time_stimulus_file(), which writes a stimulus file compatible with PSPICE
        This test also checks the correct use of the dict_translate_signal_names and mode arguments
        '''

        # arrange
        path_stimulus_file = os.path.join('output', 'PSPICE', 'write_time_stimulus_file', 'test_write_time_stimulus_file__with_dict_translate__individual_time_vectors.stl')
        dict_signals = {
                "I_power_supply": {"tim_vec": [0.000, 0.015, 0.016, 1000.0], "value": [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {"tim_vec": [0.000, 0.025, 0.026, 10000.0], "value": [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {"tim_vec": [0.000, 0.15, 0.16, 1100.0], "value": [0.0, 0.0, 1.0, 1.0]},
        }
        dict_translate_signal_names = {'I_power_supply': 'I_power_supply_MOD', 'V_cliq_control_2': 'V_cliq_control_2_MOD'}
        name_time_signal = 'tim_vec'
        path_reference_file = os.path.join('references', 'PSPICE', 'test_write_time_stimulus_file__with_dict_translate__individual_time_vectors.stl')

        # act
        write_time_stimulus_file(path_file=path_stimulus_file, dict_signals=dict_signals, name_time_signal=name_time_signal, dict_translate_signal_names=dict_translate_signal_names,
                                 mode='individual_time_vectors')

        # assert
        self.assertListEqual(list(io.open(path_reference_file)), list(io.open(path_stimulus_file)))

    def test_read_time_stimulus_file(self):
        '''
        Test the function read_time_stimulus_file(), which reads a stimulus file compatible with PSPICE
        This test also checks the correct use of the dict_translate_signal_names and mode arguments
        '''

        # arrange - define a dictionary that links files to read and expected dictionary
        folder_reference_files = os.path.join('references', 'PSPICE')
        dict_pairs_to_check = {
            'test_write_time_stimulus_file.stl': {
                "I_power_supply": {"time": [0.000, 0.015, 0.016, 1000.0], "value": [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {"time": [0.000, 0.015, 0.016, 1000.0], "value": [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {"time": [0.000, 0.015, 0.016, 1000.0], "value": [0.0, 0.0, 1.0, 1.0]},
            },
            'test_write_time_stimulus_file__individual_time_vectors.stl': {
                "I_power_supply": {"time": [0.000, 0.015, 0.016, 1000.0], "value": [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {"time": [0.000, 0.025, 0.026, 10000.0], "value": [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {"time": [0.000, 0.15, 0.16, 1100.0], "value": [0.0, 0.0, 1.0, 1.0]},
            },
            'test_write_time_stimulus_file__with_time_shift_zero.stl': {
                "I_power_supply":   {"time": [0, 100000], "value": [0, 0]},
                "V_cliq_control_1": {"time": [0, 100000], "value": [0, 0]},
                "V_cliq_control_2": {"time": [0, 100000], "value": [0, 0]},
            },
        }

        # Check all entries in a loop
        for path_file, ref_dict in dict_pairs_to_check.items():
            # act
            path_stimulus_file = os.path.join(folder_reference_files, path_file)
            out_dict = read_time_stimulus_file(path_file=path_stimulus_file, name_time_signal='time', name_value_signal='value')

            # assert
            self.assertDictEqual(ref_dict, out_dict)

    def test_read_time_stimulus_file_edit_keys(self):
        '''
        Test the function read_time_stimulus_file(), which reads a stimulus file compatible with PSPICE
        This test also checks the correct use of the name_time_signal and name_value_signal arguments
        '''

        # arrange - define a dictionary that links files to read and expected dictionary
        folder_reference_files = os.path.join('references', 'PSPICE')
        name_time_signal = 'time_mod_key'
        name_value_signal = 'value_mod_key'
        dict_pairs_to_check = {
            'test_write_time_stimulus_file.stl': {
                "I_power_supply": {name_time_signal: [0.000, 0.015, 0.016, 1000.0], name_value_signal: [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {name_time_signal: [0.000, 0.015, 0.016, 1000.0], name_value_signal: [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {name_time_signal: [0.000, 0.015, 0.016, 1000.0], name_value_signal: [0.0, 0.0, 1.0, 1.0]},
            },
            'test_write_time_stimulus_file__individual_time_vectors.stl': {
                "I_power_supply": {name_time_signal: [0.000, 0.015, 0.016, 1000.0], name_value_signal: [14500.0, 14500.0, 0, 0]},
                "V_cliq_control_1": {name_time_signal: [0.000, 0.025, 0.026, 10000.0], name_value_signal: [0.0, 0.0, 2.0, 2.0]},
                "V_cliq_control_2": {name_time_signal: [0.000, 0.15, 0.16, 1100.0], name_value_signal: [0.0, 0.0, 1.0, 1.0]},
            },
            'test_write_time_stimulus_file__with_time_shift_zero.stl': {
                "I_power_supply":   {name_time_signal: [0, 100000], name_value_signal: [0, 0]},
                "V_cliq_control_1": {name_time_signal: [0, 100000], name_value_signal: [0, 0]},
                "V_cliq_control_2": {name_time_signal: [0, 100000], name_value_signal: [0, 0]},
            },
        }

        # Check all entries in a loop
        for path_file, ref_dict in dict_pairs_to_check.items():
            # act
            path_stimulus_file = os.path.join(folder_reference_files, path_file)
            out_dict = read_time_stimulus_file(path_file=path_stimulus_file, name_time_signal=name_time_signal, name_value_signal=name_value_signal)

            # assert
            self.assertDictEqual(ref_dict, out_dict)

    def test_edit_bias_file_IC_to_NODESET(self):
        '''
        Test the function edit_bias_file(), which edits a bias-point file compatible with PSPICE.
        This test checks that the function can write a new edited file in a new location.
        '''
        # arrange
        path_file_IC = os.path.join('input', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_IC.bsp')
        new_path_file_NODESET = os.path.join('output', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_NODESET_01.bsp')
        path_reference_file_NODESET = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_NODESET.bsp')
        # act
        edit_bias_file(path_file=path_file_IC, edit_file_type='.NODESET', new_path_file=new_path_file_NODESET)
        # assert
        assert_equal_readable_files(path_reference_file_NODESET, new_path_file_NODESET)

    def test_edit_bias_file_NODESET_to_IC(self):
        '''
        Test the function edit_bias_file(), which edits a bias-point file compatible with PSPICE.
        This test checks that the function can write a new edited file in a new location.
        '''
        # arrange
        path_file_NODESET = os.path.join('input', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_NODESET.bsp')
        new_path_file_IC = os.path.join('output', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_IC_01.bsp')
        path_reference_file_IC = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_IC.bsp')
        # act
        edit_bias_file(path_file=path_file_NODESET, edit_file_type='.IC', new_path_file=new_path_file_IC)
        # assert
        assert_equal_readable_files(path_reference_file_IC, new_path_file_IC)

    def test_edit_bias_file_IC_to_IC(self):
        '''
        Test the function edit_bias_file(), which edits a bias-point file compatible with PSPICE.
        This test checks that the function can write a new file in a new location, even if the original file is already of the edited_file_type.
        '''
        # arrange
        path_file_IC = os.path.join('input', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_IC.bsp')
        new_path_file_IC = os.path.join('output', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_IC_02.bsp')
        path_reference_file_IC = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_IC.bsp')
        # act
        edit_bias_file(path_file=path_file_IC, edit_file_type='.IC', new_path_file=new_path_file_IC)
        # assert
        assert_equal_readable_files(path_reference_file_IC, new_path_file_IC)

    def test_edit_bias_file_exceptionEditFileType(self):
        '''
        Test the function edit_bias_file(), which edits a bias-point file compatible with PSPICE.
        This test checks that the function correctly raises an exception when the wrong.
        '''
        # act
        with self.assertRaises(Exception) as context:
            edit_bias_file(path_file=None, edit_file_type='WRONG_EDIT_FILE_TYPE', new_path_file=None)

        # assert
        print(F'This exception was correctly raised: {context.exception}')
        self.assertEqual("The variable edit_file_type is WRONG_EDIT_FILE_TYPE, but the only allowed values are: ['.IC', '.NODESET'].", str(context.exception))

    def test_edit_bias_file_NODESET_to_IC_same_file(self):
        '''
        Test the function edit_bias_file(), which edits a bias-point file compatible with PSPICE.
        This test checks that the function can edit the same file in place.
        '''
        # arrange
        path_file_NODESET = os.path.join('input', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_NODESET.bsp')  # This file will not be changed by this test
        path_file_NODESET_to_IC = os.path.join('output', 'PSPICE', 'edit_bias_file', 'test_edit_bias_file_IC_03.bsp')
        path_reference_file_IC = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_IC.bsp')
        path_reference_file_NODESET = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_NODESET.bsp')
        # arrange - copy the input file to another location and check that it is of NODESET type (unchanged)
        make_folder_if_not_existing(os.path.dirname(path_file_NODESET_to_IC))
        shutil.copyfile(path_file_NODESET, path_file_NODESET_to_IC)
        assert_equal_readable_files(path_reference_file_NODESET, path_file_NODESET_to_IC)
        # act
        edit_bias_file(path_file=path_file_NODESET_to_IC, edit_file_type='.IC')  # Note: new_path_file not passed will be defaulted to None and the original file will be edited
        # assert - check that the file is of IC type (changed)
        assert_equal_readable_files(path_reference_file_IC, path_file_NODESET_to_IC)

    def test_check_bias_file(self):
        '''
        Test the function check_bias_file(), which checks the type of a PSPICE bias point file.
        '''
        # arrange
        path_reference_file_IC = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_IC.bsp')
        path_reference_file_NODESET = os.path.join('references', 'PSPICE', 'test_edit_bias_file_reference_NODESET.bsp')
        path_reference_file_DUMMY = os.path.join('references', 'PSPICE', 'test_check_bias_file_type_DUMMY.bsp')
        # act and assert
        self.assertEqual('.IC', check_bias_file_type(path_file=path_reference_file_IC))
        self.assertEqual('.NODESET', check_bias_file_type(path_file=path_reference_file_NODESET))
        self.assertNotEqual('.IC', check_bias_file_type(path_file=path_reference_file_DUMMY))
        self.assertNotEqual('.NODESET', check_bias_file_type(path_file=path_reference_file_DUMMY))
        self.assertEqual(None, check_bias_file_type(path_file=path_reference_file_DUMMY))
