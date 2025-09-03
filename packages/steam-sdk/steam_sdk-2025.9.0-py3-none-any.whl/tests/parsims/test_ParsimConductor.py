import unittest
import os

from steam_sdk.data import DataModelMagnet as md
from steam_sdk.data.DataAnalysis import StrandCriticalCurrentMeasurement
from steam_sdk.parsims.ParsimConductor import ParsimConductor
from tests.TestHelpers import assert_equal_readable_files
from steam_sdk.data.DataConductor import Conductor
from steam_sdk.data.DataParsimConductor import MagnetClass, ConductorSample, Coil, DataParsimConductor, IcMeasurement, \
    GeneralParametersClass, StrandGeometry


class TestParsimConductor(unittest.TestCase):

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

    def test_ParsimConductor_Initialize(self):
        conductors = [
            Conductor(cable={'type': 'Rutherford'}),
            Conductor(cable={'type': 'Rutherford'}),
            Conductor(cable={'type': 'Rutherford'}),
            Conductor(cable={'type': 'Rutherford'})
        ]
        groups_to_coils = {'test': [1, 2, 3, 4]}
        dict_coilName_to_conductorIndex = {
            'test': 0
        }
        model_data = md.DataModelMagnet()
        model_data.Conductors = conductors
        pc = ParsimConductor(model_data=model_data, groups_to_coils=groups_to_coils, length_to_coil={},
                             dict_coilName_to_conductorIndex=dict_coilName_to_conductorIndex, path_input_dir=None)

    def test_ParsimConductor_readInput_writeOutput1(self):

        # arrange
        CUDI1_conductors = [  # 3 instances of a CUDI conductor to test 0, 1 and 2 measurements
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'CUDI1'}, strand={'type': 'Round'}),
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'CUDI1'}, strand={'type': 'Round'}),
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'CUDI1'}, strand={'type': 'Round'}),
        ]
        for i, c in enumerate(CUDI1_conductors):
            if i == 0:  # values from MBRB/C
                c.Jc_fit.Tc0_CUDI1 = 9.2
                c.Jc_fit.Bc20_CUDI1 = 14.5
                c.Jc_fit.C1_CUDI1 = 34404.9 * 1.01  # one 1% error
                c.Jc_fit.C2_CUDI1 = -2566.9 * 1.01  # one 1% error
                c.cable.n_strands = 30
                c.strand.Cu_noCu_in_strand = 1.8
                c.cable.strand_twist_pitch = 0.11
            else:  # values form MQ
                c.Jc_fit.Tc0_CUDI1 = 9.2
                c.Jc_fit.Bc20_CUDI1 = 14.5
                c.Jc_fit.C1_CUDI1 = 65821.9 * 1.01  # one 1% error
                c.Jc_fit.C2_CUDI1 = -5042.6 * 1.01  # one 1% error
                c.cable.n_strands = 30  # will be changed to 36
                c.strand.Cu_noCu_in_strand = 1.8  # will be changed to 1.95
                c.cable.strand_twist_pitch = 0.11

        Summers_conductors = [  # validate summers fit calculation with 2 different measurements
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'Summers'}, strand={'type': 'Round'}),
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'Summers'}, strand={'type': 'Round'}),
        ]
        for c in Summers_conductors:  # values form MQXF
            c.strand.diameter = 0.000852
            c.cable.n_strands = 40
            c.Jc_fit.Jc0_Summers = 31500000000.0
            c.Jc_fit.Tc0_Summers = 18
            c.Jc_fit.Bc20_Summers = 29
            c.cable.strand_twist_pitch = 0.11
        conductors = CUDI1_conductors + Summers_conductors
        model_data = md.DataModelMagnet()
        model_data.Conductors = conductors
        model_data.CoilWindings.n_half_turn_in_group = [28, 22, 28, 22, 28, 22, 28, 22, 28, 22, 28, 22]
        model_data.CoilWindings.half_turn_length = [8.0 for _ in model_data.CoilWindings.n_half_turn_in_group]
        # model_data.Sources.magnetic_field_fromROXIE = os.path.join('input', 'run_parsim_conductor', 'test.map2d') # TODO test

        strand_critical_current_measurements = [
            StrandCriticalCurrentMeasurement(
                # MQ measurements from csv file "Strand and cable characteristics" - MCBY measurement of LHC design report (Ic=55[A]) was not working because it want Ic_cab not Ic_str
                column_name_I_critical='Ic 4.222K 6T',
                reference_mag_field=6,
                reference_temperature=4.222,
                column_name_CuNoCu_short_sample='Ave Cu/noCu in SS',
                coil_names=['CUDI1_2_meas_coil', 'CUDI1_1_meas_coil']),
            StrandCriticalCurrentMeasurement(
                # MQ measurements from csv file "Strand and cable characteristics" - MCBY measurement of LHC design report (Ic=55[A]) was not working because it want Ic_cab not Ic_str
                column_name_I_critical='Ic 1.9K 9T',
                reference_mag_field=9,
                reference_temperature=1.9,
                column_name_CuNoCu_short_sample='Ave Cu/noCu in SS',
                coil_names=['CUDI1_2_meas_coil']),
            StrandCriticalCurrentMeasurement(
                column_name_I_critical='Ic(T=4.22 K,B=12 T)',
                reference_mag_field=12,
                reference_temperature=4.22,
                column_name_CuNoCu_short_sample='Ave Cu/noCu in SS',
                coil_names=['Summers_test_coil2']),
            StrandCriticalCurrentMeasurement(
                column_name_I_critical='Ic(T=4.22 K,B=15 T)',
                reference_mag_field=15,
                reference_temperature=4.22000001,
                column_name_CuNoCu_short_sample='Ave Cu/noCu in SS',
                coil_names=['Summers_test_coil1']),
        ]
        input_path_csv = os.path.join('input', 'run_parsim_conductor', 'TEST_parsim_conductor.xlsx')
        output_path_csv = os.path.join('output', 'run_parsim_conductor', 'sweeper1.csv')
        ref_path_csv = os.path.join('references', 'run_parsim_conductor', 'sweeper_reference1.csv')
        dict_coilName_to_conductorIndex = {
            'CUDI1_no_meas_coil': 0,
            'CUDI1_1_meas_coil': 1,
            'CUDI1_2_meas_coil': 2,
            'Summers_test_coil1': 3,
            'Summers_test_coil2': 4,
        }
        groups_to_coils = {
            'CUDI1_no_meas_coil': [1, 2, 11, 12],
            'CUDI1_1_meas_coil': [3, 4],
            'CUDI1_2_meas_coil': [5, 6],
            'Summers_test_coil1': [7, 8],
            'Summers_test_coil2': [9, 10],
        }

        # act
        pc = ParsimConductor(model_data=model_data, groups_to_coils=groups_to_coils,
                             length_to_coil={}, path_input_dir=None,
                             dict_coilName_to_conductorIndex=dict_coilName_to_conductorIndex)
        pc.read_from_input(path_input_file=input_path_csv, magnet_name='TEST_MAG_NAME',
                           strand_critical_current_measurements=strand_critical_current_measurements)
        pc.write_conductor_parameter_file(path_output_file=output_path_csv, simulation_name='MAG_NAME',
                                          simulation_number=1)

        # assert
        correct_data_parsim_conductor = DataParsimConductor(
            GeneralParameters=GeneralParametersClass(magnet_name='TEST_MAG_NAME', circuit_name=None, state=None),
            Magnet=MagnetClass(coils=['CUDI1_1_meas_coil', 'CUDI1_no_meas_coil', 'CUDI1_2_meas_coil',
                                      'Summers_test_coil1',
                                 'Summers_test_coil2'], measured_inductance_versus_current=[]), Coils={
                'CUDI1_1_meas_coil': Coil(ID=None, cable_ID=None, coil_resistance_room_T=0.6831,
                                          Cu_noCu_resistance_meas=1.76369045029997, B_resistance_meas=None,
                                          T_ref_coil_resistance=293.04999999999995, T_ref_RRR_low=None,
                                          T_ref_RRR_high=None, conductorSamples=[
                        ConductorSample(ID=None, Ra=10.0, Rc=None, number_of_strands=36.0, bare_cable_width=0.0151, bare_cable_height=None,
                                        strand_twist_pitch=0.12, filament_twist_pitch=0.016, RRR=190.0, Cu_noCu=1.95,
                                        Tc0=9.2, Bc20=14.5, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=387.0, T_ref_Ic=4.222, B_ref_Ic=6.0, Cu_noCu_sample=4.4)],
                                        strand_geometry=StrandGeometry(diameter=0.000825, bare_width=None,
                                                                       bare_height=None)),
                        ConductorSample(ID=None, Ra=10.0, Rc=None, number_of_strands=36.0, bare_cable_width=0.0151, bare_cable_height=None,
                                        strand_twist_pitch=0.12, filament_twist_pitch=0.016, RRR=191.0, Cu_noCu=1.95,
                                        Tc0=9.2, Bc20=14.5, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=387.0, T_ref_Ic=4.222, B_ref_Ic=6.0, Cu_noCu_sample=4.4)],
                                        strand_geometry=StrandGeometry(diameter=0.000825, bare_width=None,
                                                                       bare_height=None)),
                        ConductorSample(ID=None, Ra=10.0, Rc=None, number_of_strands=36.0, bare_cable_width=0.0151, bare_cable_height=None,
                                        strand_twist_pitch=0.12, filament_twist_pitch=0.016, RRR=193.0, Cu_noCu=1.95,
                                        Tc0=9.2, Bc20=14.5, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=387.0, T_ref_Ic=4.222, B_ref_Ic=6.0, Cu_noCu_sample=4.4)],
                                        strand_geometry=StrandGeometry(diameter=0.000825, bare_width=None,
                                                                       bare_height=None))],
                                          weight_factors=[0.3, 0.2, 0.5]),
                'CUDI1_no_meas_coil': Coil(ID=None, cable_ID=None, coil_resistance_room_T=0.6824,
                                           Cu_noCu_resistance_meas=1.7685389441987094, B_resistance_meas=None,
                                           T_ref_coil_resistance=292.15, T_ref_RRR_low=None, T_ref_RRR_high=None,
                                           conductorSamples=[
                                               ConductorSample(ID=None, Ra=None, Rc=11.0, number_of_strands=None,
                                                               bare_cable_width=0.0152, bare_cable_height=None, strand_twist_pitch=None,
                                                               filament_twist_pitch=None, RRR=190.0, Cu_noCu=1.8,
                                                               Tc0=9.2, Bc20=16.0, f_rho_eff=None, Ic_measurements=[],
                                                               strand_geometry=StrandGeometry(
                                                                   diameter=0.0006477000000000001, bare_width=None,
                                                                   bare_height=None)),
                                               ConductorSample(ID=None, Ra=None, Rc=11.0, number_of_strands=None,
                                                               bare_cable_width=0.0152, bare_cable_height=None, strand_twist_pitch=None,
                                                               filament_twist_pitch=None, RRR=191.0, Cu_noCu=1.8,
                                                               Tc0=9.2, Bc20=16.0, f_rho_eff=None, Ic_measurements=[],
                                                               strand_geometry=StrandGeometry(
                                                                   diameter=0.0006477000000000001, bare_width=None,
                                                                   bare_height=None)),
                                               ConductorSample(ID=None, Ra=None, Rc=11.0, number_of_strands=None,
                                                               bare_cable_width=0.0152, bare_cable_height=None, strand_twist_pitch=None,
                                                               filament_twist_pitch=None, RRR=193.0, Cu_noCu=1.8,
                                                               Tc0=9.2, Bc20=16.0, f_rho_eff=None, Ic_measurements=[],
                                                               strand_geometry=StrandGeometry(
                                                                   diameter=0.0006477000000000001, bare_width=None,
                                                                   bare_height=None))], weight_factors=[0.3, 0.2, 0.5]),
                'CUDI1_2_meas_coil': Coil(ID=None, cable_ID=None, coil_resistance_room_T=0.6824,
                                          Cu_noCu_resistance_meas=1.7685389441987094, B_resistance_meas=None,
                                          T_ref_coil_resistance=293.04999999999995, T_ref_RRR_low=None,
                                          T_ref_RRR_high=None, conductorSamples=[
                        ConductorSample(ID=None, Ra=None, Rc=None, number_of_strands=36.0, bare_cable_width=0.0152, bare_cable_height=None,
                                        strand_twist_pitch=None, filament_twist_pitch=None, RRR=190.0, Cu_noCu=1.95,
                                        Tc0=9.0, Bc20=14.5, f_rho_eff=1.0, Ic_measurements=[
                                IcMeasurement(Ic=387.0, T_ref_Ic=4.222, B_ref_Ic=6.0, Cu_noCu_sample=1.2),
                                IcMeasurement(Ic=380, T_ref_Ic=1.9, B_ref_Ic=9.0, Cu_noCu_sample=1.2)],
                                        strand_geometry=StrandGeometry(diameter=0.000825, bare_width=None,
                                                                       bare_height=None)),
                        ConductorSample(ID=None, Ra=None, Rc=None, number_of_strands=36.0, bare_cable_width=0.0152, bare_cable_height=None,
                                        strand_twist_pitch=None, filament_twist_pitch=None, RRR=193.0, Cu_noCu=1.95,
                                        Tc0=9.4, Bc20=14.5, f_rho_eff=1.0, Ic_measurements=[
                                IcMeasurement(Ic=387.0, T_ref_Ic=4.222, B_ref_Ic=6.0, Cu_noCu_sample=1.2),
                                IcMeasurement(Ic=380, T_ref_Ic=1.9, B_ref_Ic=9.0, Cu_noCu_sample=1.2)],
                                        strand_geometry=StrandGeometry(diameter=0.000825, bare_width=None,
                                                                       bare_height=None))], weight_factors=[]),
                'Summers_test_coil1': Coil(ID=None, cable_ID=None, coil_resistance_room_T=0.6815,
                                           Cu_noCu_resistance_meas=1.7748278293512953, B_resistance_meas=None,
                                           T_ref_coil_resistance=293.04999999999995, T_ref_RRR_low=None,
                                           T_ref_RRR_high=None, conductorSamples=[
                        ConductorSample(ID=None, Ra=None, Rc=None, number_of_strands=36.0, bare_cable_width=0.015, bare_cable_height=None,
                                        strand_twist_pitch=0.12, filament_twist_pitch=None, RRR=184, Cu_noCu=1.9,
                                        Tc0=None, Bc20=None, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=384.0, T_ref_Ic=4.22000001, B_ref_Ic=15.0, Cu_noCu_sample=1.19)],
                                        strand_geometry=StrandGeometry(diameter=None, bare_width=None,
                                                                       bare_height=None)),
                        ConductorSample(ID=None, Ra=None, Rc=None, number_of_strands=36.0, bare_cable_width=0.015, bare_cable_height=None,
                                        strand_twist_pitch=0.12, filament_twist_pitch=None, RRR=184, Cu_noCu=2.0,
                                        Tc0=None, Bc20=None, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=384.0, T_ref_Ic=4.22000001, B_ref_Ic=15.0, Cu_noCu_sample=1.19)],
                                        strand_geometry=StrandGeometry(diameter=None, bare_width=None,
                                                                       bare_height=None))], weight_factors=[]),
                'Summers_test_coil2': Coil(ID=None, cable_ID=None, coil_resistance_room_T=0.6819,
                                           Cu_noCu_resistance_meas=1.7720251154942048, B_resistance_meas=None,
                                           T_ref_coil_resistance=293.04999999999995, T_ref_RRR_low=None,
                                           T_ref_RRR_high=None, conductorSamples=[
                        ConductorSample(ID=None, Ra=None, Rc=None, number_of_strands=36.0, bare_cable_width=0.0151, bare_cable_height=None,
                                        strand_twist_pitch=0.123, filament_twist_pitch=0.014, RRR=190.0, Cu_noCu=1.9,
                                        Tc0=None, Bc20=None, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=693, T_ref_Ic=4.22, B_ref_Ic=12.0, Cu_noCu_sample=1.2)],
                                        strand_geometry=StrandGeometry(diameter=None, bare_width=None,
                                                                       bare_height=None)),
                        ConductorSample(ID=None, Ra=None, Rc=None, number_of_strands=36.0, bare_cable_width=0.0151, bare_cable_height=None,
                                        strand_twist_pitch=0.123, filament_twist_pitch=0.014, RRR=191.0, Cu_noCu=1.9,
                                        Tc0=None, Bc20=None, f_rho_eff=None, Ic_measurements=[
                                IcMeasurement(Ic=693, T_ref_Ic=4.22, B_ref_Ic=12.0, Cu_noCu_sample=1.2)],
                                        strand_geometry=StrandGeometry(diameter=None, bare_width=None,
                                                                       bare_height=None))], weight_factors=[0.1, 0.9])})

        # Assert GeneralParameters
        self.assertEqual(
            correct_data_parsim_conductor.GeneralParameters,
            pc.data_parsim_conductor.GeneralParameters
        )

        # Assert Magnet
        self.assertEqual(
            correct_data_parsim_conductor.Magnet,
            pc.data_parsim_conductor.Magnet,
        )

        # Assert Coils
        for coil_name, correct_coil in correct_data_parsim_conductor.Coils.items():
            pc_coil = pc.data_parsim_conductor.Coils[coil_name]

            # Assert basic Coil attributes
            self.assertEqual(correct_coil.ID, pc_coil.ID)
            self.assertEqual(correct_coil.cable_ID, pc_coil.cable_ID)
            self.assertEqual(correct_coil.coil_resistance_room_T, pc_coil.coil_resistance_room_T)
            self.assertEqual(correct_coil.Cu_noCu_resistance_meas, pc_coil.Cu_noCu_resistance_meas)
            self.assertEqual(correct_coil.T_ref_coil_resistance, pc_coil.T_ref_coil_resistance)
            self.assertEqual(correct_coil.T_ref_RRR_low, pc_coil.T_ref_RRR_low)
            self.assertEqual(correct_coil.T_ref_RRR_high, pc_coil.T_ref_RRR_high)
            self.assertEqual(correct_coil.weight_factors, pc_coil.weight_factors)

            # Assert ConductorSamples
            for pc_conductor_sample, correct_conductor_sample in zip(pc_coil.conductorSamples, correct_coil.conductorSamples):
                # Assert Ic_measurements
                for pc_ic_measurement, correct_ic_measurement in zip(pc_conductor_sample.Ic_measurements, correct_conductor_sample.Ic_measurements):
                    self.assertEqual(correct_ic_measurement, pc_ic_measurement)
                # assert the rest of the conductor
                self.assertEqual(correct_conductor_sample, pc_conductor_sample)
        self.assertEqual(correct_data_parsim_conductor, pc.data_parsim_conductor)
        assert_equal_readable_files(ref_path_csv, output_path_csv)

    def test_ParsimConductor_readInput_writeOutput2(self):
        # This is a copy of the previous test to test the optimization of Cu_noCu with the resistance measurement

        # arrange
        conductors = [  # 3 instances of a CUDI conductor to test 0, 1 and 2 measurements
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'Summers'}, strand={'type': 'Round'}),
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'Summers'}, strand={'type': 'Round'}),
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'Summers'}, strand={'type': 'Rectangular'}),
            # to also test rect cables
            Conductor(cable={'type': 'Rutherford'}, Jc_fit={'type': 'Summers'}, strand={'type': 'Round'}),
        ]
        for c in conductors:  # values form MQXF
            if c.strand.type == 'Round': c.strand.diameter = 0.00085
            c.cable.n_strands = 40
            c.cable.strand_twist_pitch = 0.11
            c.strand.Cu_noCu_in_strand = 1.0
        model_data = md.DataModelMagnet()
        model_data.Conductors = conductors
        model_data.CoilWindings.n_half_turn_in_group = [28, 22, 28, 22, 28, 22, 28, 22]
        model_data.CoilWindings.half_turn_length = [8.0 for _ in model_data.CoilWindings.n_half_turn_in_group]

        input_path_csv = os.path.join('input', 'run_parsim_conductor', 'TEST_parsim_conductor.xlsx')
        output_path_csv = os.path.join('output', 'run_parsim_conductor', 'sweeper2.csv')
        ref_path_csv = os.path.join('references', 'run_parsim_conductor', 'sweeper_reference2.csv')
        dict_coilName_to_conductorIndex = {
            'coil1': 0,
            'coil2': 1,
            'coil3': 2,
            'coil4': 3,
        }
        groups_to_coils = {
            'coil1': [1, 2],
            'coil2': [3, 4],
            'coil3': [5, 6],
            'coil4': [7, 8],
        }
        length_to_coil = {
            'coil1': 224.0,
            'coil2': 176,
            'coil3': 224.002,
            'coil4': 224.0002,
        }

        # act
        pc = ParsimConductor(model_data=model_data, groups_to_coils=groups_to_coils, length_to_coil=length_to_coil,
                             dict_coilName_to_conductorIndex=dict_coilName_to_conductorIndex, path_input_dir=None)
        pc.read_from_input(path_input_file=input_path_csv, magnet_name='TEST_MAG_NAME',
                           strand_critical_current_measurements=[])
        pc.write_conductor_parameter_file(path_output_file=output_path_csv, simulation_name='MAG_NAME',
                                          simulation_number=1)

        # assert
        assert_equal_readable_files(ref_path_csv, output_path_csv)
