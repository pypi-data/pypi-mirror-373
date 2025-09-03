import unittest
import os
from pathlib import Path
import shutil
from distutils.dir_util import copy_tree
import yaml
import matplotlib.pyplot as plt

from steam_sdk.builders.BuilderModel import BuilderModel
from steam_sdk.drivers.DriverPSPICE import DriverPSPICE
from steam_sdk.parsers.CSD_Reader import CSD_read
from steam_sdk.utils.misc import displayWaitAndClose
from steam_sdk.parsers.ParserPSPICE import *


class TestDriverPSPICE(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define settings file
        user_name = os.getlogin()
        name_file_settings = 'settings.' + user_name + '.yaml'
        path_settings = Path(Path('..') / name_file_settings).resolve()
        print('user_name:          {}'.format(user_name))
        print('name_file_settings: {}'.format(name_file_settings))
        print('path_settings:      {}'.format(path_settings))

        # Read PSPICE exe path from the settings file
        with open(path_settings, 'r') as stream:
            settings_dict = yaml.safe_load(stream)
        self.path_PSPICE = settings_dict['PSPICE_path']
        print('path_PSPICE:        {}'.format(self.path_PSPICE))

        if os.path.isfile(path_settings):
            print('path_settings {} exists '.format(path_settings))
        else:
            print('path_settings {} does not exist '.format(path_settings))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder


    def test_runPSPICE_simplest(self):
        '''
            This test checks that PSPICE can be run programmatically using DriverPSPICE.
            The path of PSPICE executable is set to be the one of the Gitlab runner.
            In order to run this test locally, path_exe should be changed.
        '''

        # arrange
        # Define working folder and input file information
        path_folder_PSPICE = 'input/pspice'
        nameCircuit = 'TEST'
        suffix = '_0'
        print('path_folder_PSPICE: {}'.format(path_folder_PSPICE))

        # Define expected output files, and delete them if they already exist
        expected_file_dat = str(Path(os.path.join(path_folder_PSPICE, nameCircuit + suffix + '.dat')).resolve())
        expected_file_out = str(Path(os.path.join(path_folder_PSPICE, nameCircuit + suffix + '.out')).resolve())
        if os.path.isfile(expected_file_dat):
            os.remove(expected_file_dat)
            print('File {} already existed. It was deleted now.'.format(expected_file_dat))
        if os.path.isfile(expected_file_out):
            os.remove(expected_file_out)
            print('File {} already existed. It was deleted now.'.format(expected_file_out))

        # Initialize Driver
        dPSPICE = DriverPSPICE(
            path_exe=self.path_PSPICE,
            path_folder_PSPICE=path_folder_PSPICE,
            verbose=True)

        # act - Run model
        dPSPICE.run_PSPICE(nameCircuit=nameCircuit, suffix=suffix)

        # assert - Check that simulation run without errors
        expected_successful_output = 0
        self.assertEqual(expected_successful_output, dPSPICE.output)
        # assert - Check that simulation generated expected output files
        self.assertTrue(os.path.isfile(expected_file_dat))
        self.assertTrue(os.path.isfile(expected_file_out))

    def test_runPSPICE_fromCircuitLibrary_multiple(self):
        '''
            This test runs iteratively the PSPICE netlists in the provided list.
            Each input file is copied from the local STEAM_SDK test model library.
        '''
        circuit_names = ['IPQ_2magnets', 'IPQ_4magnets', 'RCD_RCO', 'ROD', 'RQX_HL-LHC', 'RU']
        # TODO: Add RB, RQX, RCS and other updated circuits that use coil resistance interpolation
        for circuit_name in circuit_names:
            print('Circuit: {}'.format(circuit_name))
            self.test_runPSPICE_fromCircuitLibrary(circuit_name = circuit_name)


    def test_runPSPICE_fromCircuitLibrary(self, circuit_name = 'RU'):
        '''
            This test checks that PSPICE can be run programmatically using DriverPSPICE.
            The input file is copied from the local STEAM_SDK test model library.
            The path of PSPICE executable is set to be the one of the Gitlab runner.
            In order to run this test locally, path_exe should be changed.
        '''

        # arrange
        # Define working folder and make sure dedicated output folder exists
        path_folder_PSPICE = os.path.join('output', 'pspice', circuit_name)
        print('path_folder_PSPICE: {}'.format(path_folder_PSPICE))
        if not os.path.isdir(path_folder_PSPICE):
            print("Output folder {} does not exist. Making it now".format(path_folder_PSPICE))
            Path(path_folder_PSPICE).mkdir(parents=True)

        # Copy entire folder from input model in the STEAM_SDK test model library to the local test folder
        path_one_level_up = Path(os.path.dirname(__file__)).parent
        folder_input = str(Path(path_one_level_up / os.path.join('builders', 'model_library', 'circuits', circuit_name, 'output')).resolve())
        input_cir = os.path.join(folder_input, circuit_name+'.cir')
        folder_local = os.path.join(path_folder_PSPICE)
        if not os.path.isdir(folder_local):
            os.mkdir(folder_local)
        if not os.path.isdir(input_cir):
            if not os.path.isdir(folder_input):
                os.mkdir(folder_input)
            file_model_data = str(Path(path_one_level_up /os.path.join('builders','model_library', 'circuits', circuit_name,
                                                                       'input','modelData_' + circuit_name + '.yaml')).resolve())
            pPSPICE = ParserPSPICE(None)
            pPSPICE.readFromYaml(file_model_data, verbose=False)
            pPSPICE.write2pspice(input_cir, verbose=False)
        copy_tree(folder_input, folder_local)
        print('Folder {} copied to {}.'.format(folder_input, folder_local))

        # expected_file_dat = str(Path(os.path.join(path_folder_PSPICE, circuit_name + '.dat')).resolve())
        expected_file_out = str(Path(os.path.join(path_folder_PSPICE, circuit_name + '.out')).resolve())
        # if os.path.isfile(expected_file_dat):
        #     os.remove(expected_file_dat)
        #     print('File {} already existed. It was deleted now.'.format(expected_file_dat))
        if os.path.isfile(expected_file_out):
            os.remove(expected_file_out)
            print('File {} already existed. It was deleted now.'.format(expected_file_out))

        # Initialize Driver
        dPSPICE = DriverPSPICE(
            path_exe=self.path_PSPICE,
            path_folder_PSPICE=path_folder_PSPICE,
            verbose=True)

        # act - Run model
        dPSPICE.run_PSPICE(nameCircuit=circuit_name, suffix='')

        # assert - Check that simulation run without errors
        expected_successful_output = 0
        self.assertEqual(expected_successful_output, dPSPICE.output)
        # assert - Check that simulation generated expected output files
        print(f'Checking for {expected_file_out}')
        # self.assertTrue(os.path.isfile(expected_file_dat))
        self.assertTrue(os.path.isfile(expected_file_out))


    def test_runPSPICE_CSD_Plots(self, circuit_name = 'RU'):
        '''
            This test checks that PSPICE can be run programmatically using DriverPSPICE, and its .csd output file can
            be parsed and plotted.
            The netlist is generated on the fly from the yaml input in local STEAM_SDK test model library.
            The path of PSPICE executable is set to be the one of the Gitlab runner.
            In order to run this test locally, path_exe should be changed.
        '''

        # arrange
        # Define input circuit model file and make the netlist
        path_library = Path(Path('..') / 'builders' / 'model_library').resolve()
        file_model_data = os.path.join(path_library, 'circuits', circuit_name, 'input', 'modelData_' + circuit_name + '.yaml')
        path_folder_PSPICE = os.path.join('output', 'pspice_csd', circuit_name)
        print('path_folder_PSPICE: {}'.format(path_folder_PSPICE))
        input_file_GENERATED = os.path.join(path_library, 'circuits', circuit_name, 'output', circuit_name + '.cir')
        BM = BuilderModel(file_model_data=file_model_data, case_model='circuit', verbose=False)
        BM.circuit_data.PostProcess.probe.probe_type = 'CSDF'
        BM.buildPSPICE(sim_name=circuit_name, sim_number='', output_path=path_folder_PSPICE, verbose=False)  # re-write the netlist with different probe settings

        # Define expected output files, and delete them if they already exist
        expected_file_dat = os.path.join(path_folder_PSPICE, circuit_name + '.dat')
        expected_file_out = os.path.join(path_folder_PSPICE, circuit_name + '.out')
        expected_file_csd = os.path.join(path_folder_PSPICE, circuit_name + '.csd')
        if os.path.isfile(expected_file_dat):
            os.remove(expected_file_dat)
            print('File {} already existed. It was deleted now.'.format(expected_file_dat))
        if os.path.isfile(expected_file_out):
            os.remove(expected_file_out)
            print('File {} already existed. It was deleted now.'.format(expected_file_out))
        if os.path.isfile(expected_file_csd):
            os.remove(expected_file_csd)
            print('File {} already existed. It was deleted now.'.format(expected_file_csd))

        # Initialize Driver
        dPSPICE = DriverPSPICE(
            path_exe=self.path_PSPICE,
            path_folder_PSPICE=path_folder_PSPICE,
            verbose=True)

        # act - Run model
        dPSPICE.run_PSPICE(nameCircuit=circuit_name, suffix='')

        # assert - Check that simulation run without errors
        expected_successful_output = 0
        self.assertEqual(expected_successful_output, dPSPICE.output)
        # assert - Check that simulation generated expected output files
        self.assertTrue(os.path.isfile(expected_file_csd))
        self.assertTrue(os.path.isfile(expected_file_out))
        self.assertTrue(os.path.isfile(expected_file_out))

        # acquire simulation .csd output and plot the signals
        csd = CSD_read(expected_file_csd)
        time = csd.time
        data = csd.data
        signals = csd.signal_names
        print(signals)

        # assert
        selectedFont = {'fontname': 'DejaVu Sans', 'size': 14}
        plt.figure(figsize=(6, 5))
        for s, signal in enumerate(signals):
            print(s)
            print(signal)
            plt.plot(time, data[:, s], '-', linewidth=2.0, label=signals[s])
        plt.xlabel('Time [s]', **selectedFont)
        plt.ylabel('Current [A]', **selectedFont)
        plt.grid(True)
        plt.legend(loc='best')
        displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=.1)