import shutil
import unittest
import os
import matplotlib.pyplot as plt
import yaml
from pathlib import Path
import io
import csv

from steam_sdk.analyses.AnalysisEvent import find_n_magnets_in_circuit, find_IPQ_circuit_type_from_IPQ_parameters_table, \
    get_circuit_name_from_eventfile, get_circuit_family_from_circuit_name, create_two_csvs_from_odd_and_even_rows, \
    get_number_of_apertures_from_circuit_family_name, get_number_of_quenching_magnets_from_layoutdetails, \
    get_magnet_types_list, get_number_of_magnets, get_magnet_name, \
    get_t_PC_off_from_PSPICE_netlist_data, get_circuit_type_from_circuit_name
from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.data.DataAnalysis import ModifyModelMultipleVariables
from steam_sdk.data.DataSignal import Configuration
from steam_sdk.parsers.ParserLEDET import ParserLEDET, CompareLEDETParameters
from steam_sdk.parsers.ParserPSPICE import ParserPSPICE
from tests.TestHelpers import assert_two_parameters, assert_equal_readable_files, assert_equal_yaml


class TestAnalysisEvent(unittest.TestCase):

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('Test is run from folder: {}'.format(os.getcwd()))

        # # Define settings file: this relative path is supposed to point to steam_sdk.tests
        # self.local_path_settings = Path(Path('..')).resolve()
        # print('local_path_settings:     {}'.format(self.local_path_settings))

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

        # Close all figures
        plt.close('all')


    def test_find_n_magnets_in_circuit(self):
        """
            Check that the function find_n_magnets_in_circuit() returns the correct number
        """
        # arrange
        path_library = os.path.join('input', 'dummy_circuit_library', 'circuit_parameters')
        dict_tests = {
            'RSD1.A45B1': {'file_name_input': os.path.join(path_library, '600A_circuit_parameters.csv'), 'target_n_magnets': '11'},
            'RCS.A12B2': {'file_name_input': os.path.join(path_library, '600A_circuit_parameters.csv'), 'target_n_magnets': '154'},
            # 'RQ4.L2': {'file_name_input': os.path.join(path_library, 'IPQ_circuit_parameters.csv'), 'target_n_magnets': None},
            'RQF_A34': {'file_name_input': os.path.join(path_library, 'RQ_circuit_parameters.csv'), 'target_n_magnets': '51'},
        }

        for circuit_name, value in dict_tests.items():
            file_name_input = value['file_name_input']
            target_n_magnets = value['target_n_magnets']
            # act
            self.try_find_n_magnets_in_circuit(file_name_input, circuit_name, target_n_magnets)

    def test_find_IPQ_circuit_type_from_IPQ_parameters_table(self):
        """
            Check that the function find_IPQ_circuit_type_from_IPQ_parameters_table returns the correct circuit type
        """
        # arrange
        file_name_input = os.path.join('input', 'dummy_circuit_library', 'circuit_parameters', 'IPQ_circuit_parameters.csv')
        dict_tests = {
            'RQ4.L1': {'target_circuit_type': 'IPQ_RQ4_2_2xRPHH_2xMQY'},
            'RQ4.L2': {'target_circuit_type': 'IPQ_RQ4_4_2xRPHH_4xMQY'},
            'RQ5.R1': {'target_circuit_type': 'IPQ_RQ5_2_2xRPHGB_2xMQML'},
            'RQ7.R2': {'target_circuit_type': 'IPQ_RQ7_4_2xRPHGA_4xMQM'},
            'RQ8.L4': {'target_circuit_type': 'IPQ_RQ8_2_2xRPHGA_2xMQML'},
            'RQ8.R5': {'target_circuit_type': 'IPQ_RQ8_2_2xRPHGA_2xMQML'},
        }

        for circuit_name, value in dict_tests.items():
            target_circuit_type = value['target_circuit_type']
            # act
            self.try_find_IPQ_circuit_type_from_IPQ_parameters_table(file_name_input, circuit_name,target_circuit_type)

    def test_get_circuit_name_from_eventfile(self):
        """
            Check that the function test_get_circuit_name_from_eventfile returns the correct circuit name for a given event file
        """
        # arrange
        path_library = os.path.join('input', 'dummy_eventfiles')
        dict_tests = {
            'RB.A12_FPA-2008-08-22-09h59-2022-12-26-21h55.csv': {'target_circuit_name': 'RB.A12'},
            'RCD.A78B2_FPA-2022-04-09-08h45-2022-04-09-14h32.csv': {'target_circuit_name': 'RCD-RCO.A78B2'},
            'RQ4.R2_FPA-2021-04-25-15h53-2021-04-26-13h42.csv': {'target_circuit_name': 'RQ4.R2'},
        }

        for event_file, value in dict_tests.items():
            target_circuit_name = value['target_circuit_name']
            # act
            self.try_get_circuit_name_from_eventfile(file_name_input = os.path.join('input', 'dummy_eventfiles',event_file ), target_circuit_name = target_circuit_name)

    def test_get_circuit_family_from_circuit_name(self):
        """
            Check that the function get_circuit_family_from_circuit_name returns the correct circuit family for a given circuit name
        """
        # arrange
        dict_tests = {
            'RB.A12': {'target_circuit_family': 'RB'},
            'RQT12.L1B2': {'target_circuit_family': '600A'},
            'RQX.L2': {'target_circuit_family': 'RQX'},
        }

        library_path = os.path.join(os.getcwd(),"input","dummy_model_library")

        for circuit_name, value in dict_tests.items():
            target_circuit_family = value['target_circuit_family']
            self.try_get_circuit_family_from_circuit_name(circuit_name = circuit_name, target_circuit_family = target_circuit_family, library_path= library_path)

    def test_create_two_csvs_from_odd_and_even_rows(self):
        """
            Check that the create_two_csvs_from_odd_and_even_rows creates the correct output files
        """
        #arrange
        target_filename_even = 'even.csv'
        target_filename_odd = 'odd.csv'

        # Create a temporary input CSV file for testing
        input_file_name = 'input_test.csv'
        with open(input_file_name, 'w', newline='') as input_file:
            writer = csv.writer(input_file)
            writer.writerow(['Name', 'Age', 'Favourite_Colour'])
            writer.writerow(['Max', '25', 'Blue'])
            writer.writerow(['Bob', '30', 'Red'])
            writer.writerow(['Paul', '28', 'Yellow'])

        #act
        output_files = create_two_csvs_from_odd_and_even_rows('input_test.csv',output_odd_file_name=target_filename_odd,output_even_file_name=target_filename_even)

        # check for their content
        with open(output_files[0], 'r') as file:
            even_rows_content = file.read()
        with open(output_files[1], 'r') as file:
            odd_rows_content = file.read()

        #assert
        # Check that the files exist
        self.assertTrue(os.path.exists(target_filename_even))
        self.assertTrue(os.path.exists(target_filename_odd))
        # Check for their content
        self.assertEqual(even_rows_content, "Name,Age,Favourite_Colour\nMax,25,Blue\nPaul,28,Yellow\n")
        self.assertEqual(odd_rows_content, "Name,Age,Favourite_Colour\nBob,30,Red\n")

        # Clean up
        os.remove(input_file_name)
        os.remove(target_filename_even)
        os.remove(target_filename_odd)

    def test_get_number_of_apertures_from_circuit_family_name(self):
        # arrange
        dict_tests ={
        "IPQ": 2,
        "RB": 2,
        "IPD": 1
        }
        #act
        for circuit_family_name,target_number_of_apertures in dict_tests.items():
            self.try_get_number_of_apertures_from_circuit_family_name(circuit_family_name=circuit_family_name, target_number_of_apertures=target_number_of_apertures)

    def test_get_number_of_quenching_magnets_from_layoutdetails(self):
        # arrange

        library_path = os.path.join(os.getcwd(),'input','dummy_model_library')

        dict_test={
            "RB": {'position': 'B8R1', 'target_Electric_circuit': 77},
            "RB": {'position': 'A12R1', 'target_Electric_circuit': 82},
            "RQ": {'position': '20R1', 'target_Electric_circuit': 19},
            "RQ": {'position': '28R1', 'target_Electric_circuit': 15}
        }

        for circuit_family_name, value in dict_test.items():
            # act
            position = value['position']
            Electric_circuit = get_number_of_quenching_magnets_from_layoutdetails(position = position, circuit_family_name = circuit_family_name , library_path = library_path)
            target_Electric_circuit = value['target_Electric_circuit']
            # assert
            self.assertEqual(target_Electric_circuit,Electric_circuit)
            print(Electric_circuit)
            print(target_Electric_circuit)
            print(f'Circuit {circuit_family_name} checked with position {position}.')

    def test_get_magnet_types_list(self):
        '''
        **Test case for the get_magnet_types_list function.The function iterates through the in dict_test predefined scenarios,
         calculates the magnet types list using the get_magnet_types_list function, and asserts
        the calculated list against the expected target list for each scenario.
        '''

        # arrange
        dict_test={
            "RQT12": {'number_of_magnets': 1, 'target_magnet_types_list': [1]},
            "RB": {'number_of_magnets': 154, 'target_magnet_types_list': [1]*154},
            "IPQ": {'number_of_magnets': 2, 'target_magnet_types_list': [1,2]},
            "RCS": {'number_of_magnets': 154, 'target_magnet_types_list': [1] + [2] * 153},
            "RSF": {'number_of_magnets': 10, 'target_magnet_types_list': [1] + [2] * 9}
        }


        for simulation_name,value in dict_test.items():
            target_magnet_types_list = value['target_magnet_types_list']
            number_of_magnets = value['number_of_magnets']

            #act
            magnet_types_list = get_magnet_types_list(number_of_magnets = number_of_magnets, simulation_name=simulation_name)

            #assert
            self.assertEqual(target_magnet_types_list, magnet_types_list)
            print(f'Simulation name {simulation_name} checked with number of magnets {number_of_magnets}.')

    def test_get_number_of_magnets(self):
        '''
        **Test case for the get_number_of_magnets function.
        The function iterates through predefined test scenarios from a dictionary, calls the get_number_of_magnets function, and asserts the calculated magnet number against the target magnet number for each scenario.
        '''

        #arrange
        test_scenarios = [
            {'circuit_name': "RCS", 'simulation_name': 'Simulation_RCS', 'circuit_type': "RCS", 'target_magnet_number': 154, 'circuit_family_name': '600A'},
            {'circuit_name': "RB", 'simulation_name': 'Simulation_RB', 'circuit_type': "RB", 'target_magnet_number': 154,'circuit_family_name': 'RB'},
            {'circuit_name': "RQ6.ABCD", 'simulation_name': 'Simulation_RQ6_ABC', 'circuit_type': "RQ6.ABC",'target_magnet_number': 6, 'circuit_family_name': '600A'},
            {'circuit_name': "RQS.RXYZ", 'simulation_name': 'Simulation_RQS_RXYZ', 'circuit_type': "RQS.R", 'target_magnet_number': 2, 'circuit_family_name': '600A'},
            {'circuit_name': "RQX", 'simulation_name': 'Simulation_RQX', 'circuit_type': "RQX", 'target_magnet_number': 4, 'circuit_family_name': 'RQX'},
            {'circuit_name': "RQTD", 'simulation_name': 'Simulation_RQTD', 'circuit_type': "RQTD", 'target_magnet_number': 8, 'circuit_family_name': '600A'},
            {'circuit_name': "RCBH", 'simulation_name': 'Simulation_60A', 'circuit_type': "60A", 'target_magnet_number': 1, 'circuit_family_name': '60A'},
            {'circuit_name': "RQ4", 'simulation_name': 'IPQ_RQ4_4_2xRPHH_4xMQY', 'circuit_type': "IPQ", 'target_magnet_number': 2, 'circuit_family_name': 'IPQ'}  # Assuming _10_ divided by 2 equals 5
        ]

        for scenario in test_scenarios:
            circuit_name = scenario['circuit_name']
            simulation_name = scenario['simulation_name']
            circuit_type = scenario['circuit_type']
            target_magnet_number = scenario['target_magnet_number']
            circuit_family_name = scenario['circuit_family_name']

            # act
            magnet_number = get_number_of_magnets(circuit_name, simulation_name, circuit_type, circuit_family_name)

            # assert
            self.assertEqual(magnet_number, target_magnet_number)
            print(f"Checked circuit name: {circuit_name} with simulation_name {simulation_name} and circuit type {circuit_type}" )

    def test_get_magnet_name(self):
        """
        **Test case for the get_magnet_name function.
        The function iterates through the test cases, calls get_magnet_name, and compares
        the result with the expected target magnet names
        """
        # Arrange
        test_cases = [
            {'circuit_name': "RQTL7", 'simulation_name': 'Simulation_RCBH', 'circuit_type': "RCBH", 'target_magnet_name': "MQTLI"},
            {'circuit_name': "RQTL9", 'simulation_name': 'Simulation_RD1', 'circuit_type': "RD", 'target_magnet_name': ["MQTLI", "MQTLI_quenchback"]},
            {'circuit_name': "RQS", 'simulation_name': 'Simulation_RCBH', 'circuit_type': "RCBH", 'target_magnet_name': ["MQS", "MQS_quenchback"]},
            {'circuit_name': "RSD", 'simulation_name': 'Simulation_RD1', 'circuit_type': "RD", 'target_magnet_name': ["MS", "MS_quenchback"]},
            {'circuit_name': "RQ", 'simulation_name': 'Simulation_RD2', 'circuit_type': "RD", 'target_magnet_name': "MQ"},
            {'circuit_name': "ABC", 'simulation_name': 'RCO', 'circuit_type': "RD", 'target_magnet_name': ["MCO", "MCO_quenchback"]},
        ]

        for scenario in test_cases:
                circuit_name = scenario['circuit_name']
                simulation_name = scenario['simulation_name']
                circuit_type = scenario['circuit_type']
                target_magnet_name = scenario['target_magnet_name']

                # Act
                magnet_name = get_magnet_name(circuit_name, simulation_name, circuit_type)

                # Assert
                self.assertEqual(magnet_name, target_magnet_name)
                print(f"Checked circuit name: {circuit_name}, with simulation name {simulation_name} and circuit type {circuit_type}")

    def test_get_circuit_type(self):
        """
        Test case for the get_circuit_type function.

        The function iterates through predefined test scenarios from a dictionary, calls the get_circuit_type() function,
        and asserts the calculated circuit type against the target circuit type for each scenario.
        """
        # Arrange

        #get library path
        # user_name = os.getlogin()
        # library_path = os.path.join(os.getcwd(), "..","..","..","steam_models")
        library_path = os.path.join(os.getcwd(),"input","dummy_model_library")

        test_scenarios = [
            {'circuit_name': "RCBH11.R8B2", 'library_path': library_path,
             'target_circuit_type': "RCB"},
            {'circuit_name': "RD1.L2", 'library_path': library_path,
             'target_circuit_type': "IPD"},
            {'circuit_name': "RQX.L1", 'library_path': library_path,
             'target_circuit_type': "RQX"},
            {'circuit_name': "RQT12.L1B1", 'library_path': library_path,
             'target_circuit_type': "RQT_12_13"},
            {'circuit_name': "RQTL9.L3B1", 'library_path': library_path,
             'target_circuit_type': "RQTL9"},
            {'circuit_name': "RQSX3.L1", 'library_path': library_path,
             'target_circuit_type': "RQSX3"},
            {'circuit_name': "RCS.A12B1", 'library_path': library_path,
             'target_circuit_type': "RCS"},
            {'circuit_name': "RB.A12", 'library_path': library_path,
             'target_circuit_type': "RB"},
            {'circuit_name': "RCBXH1.L1", 'library_path': library_path,
             'target_circuit_type': "RCBX"},
            {'circuit_name': "RCBCH10.L1B1", 'library_path': library_path,
             'target_circuit_type': "RCBC"},
            {'circuit_name': "RCBYH4.L1B1", 'library_path': library_path,
             'target_circuit_type': "RCBY"},
            {'circuit_name': "RSS.A12B1", 'library_path': library_path,
             'target_circuit_type': "RSS"},
            {'circuit_name': "RQD_A23", 'library_path': library_path,
             'target_circuit_type': "RQ_51magnets"},
            {'circuit_name': "RCD-RCO.A23B1", 'library_path': library_path,
             'target_circuit_type': "RCD_RCO"},
            {'circuit_name': "RQD_A12", 'library_path': library_path,
             'target_circuit_type': "RQ_47magnets"},
        ]

        # Act & Assert
        for scenario in test_scenarios:
            # Act
            circuit_name = scenario['circuit_name']
            library_path = scenario['library_path']
            target_circuit_type = scenario['target_circuit_type']

            # Act
            circuit_type = get_circuit_type_from_circuit_name(circuit_name, library_path)

            # Assert
            self.assertEqual(circuit_type, target_circuit_type)
            print(f"Checked circuit name: {circuit_name}, with library path {library_path}")

    def test_get_t_PC_off_from_PSPICE_netlist_data(self):
        """
        **Test case for the get_tPCoff_dictionary_from_PSPICE_netlist_data.
        The function iterates through the test cases, calls get_tPCoff_dictionary_from_PSPICE_netlist_data, and compares
        the result with the expected target dictionaries
        """
        # Arrange
        test_cases = [
            {'circuit_file_name': "IPD.cir", 'target_t_PC_off': 682.2153061979649},
            {'circuit_file_name': "IPQ_RQ4_4_2xRPHH_4xMQY.cir", 'target_t_PC_off': 324.7833333333333},
            {'circuit_file_name': "RCO.cir", 'target_t_PC_off': 15.0},
            {'circuit_file_name': "RQT.cir", 'target_t_PC_off': 369.55},
            {'circuit_file_name': "RQX.cir", 'target_t_PC_off':  169.74117647058824},
        ]

        for scenario in test_cases:
                circuit_file_name = scenario['circuit_file_name']
                target_t_PC_off = scenario['target_t_PC_off']

                path_to_circuit_file = os.path.join(os.getcwd(),"input","dummy_circuit_files",circuit_file_name)

                # Act
                t_PC_off = get_t_PC_off_from_PSPICE_netlist_data(path_to_circuit_file)

                # Assert
                self.assertEqual(t_PC_off, target_t_PC_off)
                print(f"Checked circuit file: {circuit_file_name}, and received the correct t_PC_off dictionary")

    # Helper function
    def try_find_n_magnets_in_circuit(self, file_name_input, circuit_name: str, target_n_magnets: str):
        """
            Check that the function find_n_magnets_in_circuit() returns the correct number
        """
        #act
        n_magnets = find_n_magnets_in_circuit(filename=file_name_input, circuit_name=circuit_name)
        #assert
        self.assertEqual(target_n_magnets, n_magnets)
        print(f'Circuit {circuit_name} checked.')

    def try_find_IPQ_circuit_type_from_IPQ_parameters_table(self, file_name_input, circuit_name: str ,target_circuit_type: str):
        """
            Check that the function find_IPQ_circuit_type_from_IPQ_parameters_table() returns the correct circuit type
        """
        #act
        circuit_type = find_IPQ_circuit_type_from_IPQ_parameters_table(filename=file_name_input, circuit_name=circuit_name)
        #assert
        self.assertEqual(target_circuit_type,circuit_type)
        print(f'Circuit {circuit_name} checked.')

    def try_get_circuit_name_from_eventfile(self,file_name_input, target_circuit_name: str):
        '''
        ** Check that the function try_test_get_circuit_name_from_eventfile returns the correct circuit name for a given event file
        '''
        #act
        circuit_name = get_circuit_name_from_eventfile(event_file= file_name_input)
        #assert
        self.assertEqual(target_circuit_name,circuit_name)
        print(f'File {file_name_input} checked.')

    def try_get_circuit_family_from_circuit_name(self,circuit_name: str, target_circuit_family: str, library_path: str):
        '''
        **Check that the function try_get_circuit_family_from_circuit_name returns the right circuit family for a certain circuit name
        '''
        #act
        circuit_family = get_circuit_family_from_circuit_name(circuit_name = circuit_name,library_path  = library_path)
        #assert
        self.assertEqual(target_circuit_family,circuit_family)
        print(f'Circuit name {circuit_name} checked.')

    def try_get_number_of_apertures_from_circuit_family_name(self, circuit_family_name: str, target_number_of_apertures: int):
        #act
        number_of_apertures = get_number_of_apertures_from_circuit_family_name(circuit_family_name = circuit_family_name)

        #assert
        self.assertEqual(number_of_apertures, target_number_of_apertures)







