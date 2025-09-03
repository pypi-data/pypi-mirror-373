import os
import unittest

from steam_sdk.data.DataEventCircuit import DataEventCircuit
from steam_sdk.parsims.ParsimEventCircuit import ParsimEventCircuit


class TestParsimEventCircuit(unittest.TestCase):

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

    def test_ParsimEventCircuit_Initialize(self):
        pec = ParsimEventCircuit()

    def test_ParsimEventCircuit_Read_RCB(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RCBH12.L3B1_FPA-2021-09-21-19h25-2022-01-28-11h19.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual(56.5, pec.list_events[0].PoweredCircuits['RCBH12.L3B1'].current_at_discharge)
        self.assertEqual(0.5, pec.list_events[0].PoweredCircuits['RCBH12.L3B1'].dI_dt_at_discharge)
        self.assertEqual(0, pec.list_events[0].PoweredCircuits['RCBH12.L3B1'].plateau_duration)
        self.assertEqual(56.5, pec.list_events[0].QuenchEvents['RCBH12.L3B1'].current_at_quench)
        self.assertEqual("Unknown", pec.list_events[0].QuenchEvents['RCBH12.L3B1'].quench_cause)
        self.assertEqual("HWC 2021", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2021-09-21 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("19:25:41.580000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RQX(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RQX.L1_FPA-2021-05-11-17h59-2021-05-11-19h52.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual([6934.5, -0.2, 4649.3], pec.list_events[0].PoweredCircuits['RQX.L1'].current_at_discharge)
        self.assertEqual([6.8,0,0], pec.list_events[0].PoweredCircuits['RQX.L1'].dI_dt_at_discharge)
        self.assertEqual([0, 359.98, 237.8], pec.list_events[0].PoweredCircuits['RQX.L1'].plateau_duration)
        self.assertEqual(15, pec.list_events[0].PoweredCircuits['RQX.L1'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RQX.L1'].cause_FPA)
        self.assertEqual("RQX.L1", pec.list_events[0].PoweredCircuits['RQX.L1'].circuit_name)
        self.assertEqual("RQX", pec.list_events[0].PoweredCircuits['RQX.L1'].circuit_type)
        self.assertEqual([6934.5, -0.2, 4649.3], pec.list_events[0].QuenchEvents['RQX.L1'].current_at_quench)
        self.assertEqual("Training", pec.list_events[0].QuenchEvents['RQX.L1'].quench_cause)
        self.assertEqual(-7, pec.list_events[0].QuenchEvents['RQX.L1'].delta_t_iQPS_PIC)
        self.assertEqual("Q1", pec.list_events[0].QuenchEvents['RQX.L1'].magnet_name)
        self.assertEqual(9.91058361249999, pec.list_events[0].QuenchEvents['RQX.L1'].dU_iQPS_dt)
        self.assertEqual("RQX.L1", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2021", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2021-05-11 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("17:59:36.420000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_IPQ(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RQ4.L1_FPA-2018-12-03-14h23-2022-10-31-11h49.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual([3597.7, 3597.7], pec.list_events[0].PoweredCircuits['RQ4.L1'].current_at_discharge)
        self.assertEqual([10.8, 10.8], pec.list_events[0].PoweredCircuits['RQ4.L1'].dI_dt_at_discharge)
        self.assertEqual([0, 0], pec.list_events[0].PoweredCircuits['RQ4.L1'].plateau_duration)
        self.assertEqual(7, pec.list_events[0].PoweredCircuits['RQ4.L1'].delta_t_FGC_PIC)
        self.assertEqual(0, pec.list_events[0].PoweredCircuits['RQ4.L1'].cause_FPA)
        self.assertEqual("RQ4.L1", pec.list_events[0].PoweredCircuits['RQ4.L1'].circuit_name)
        self.assertEqual("RQ4", pec.list_events[0].PoweredCircuits['RQ4.L1'].circuit_type)
        self.assertEqual([3597.7, 3597.7], pec.list_events[0].QuenchEvents['RQ4.L1'].current_at_quench)
        self.assertEqual(0, pec.list_events[0].QuenchEvents['RQ4.L1'].quench_cause)
        self.assertEqual(-2, pec.list_events[0].QuenchEvents['RQ4.L1'].delta_t_iQPS_PIC)
        self.assertEqual("B2", pec.list_events[0].QuenchEvents['RQ4.L1'].magnet_name)
        self.assertEqual([-22.3999022,14.9536139999999], pec.list_events[0].QuenchEvents['RQ4.L1'].dU_iQPS_dt)
        self.assertEqual("RQ4.L1", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2018-2", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2018-12-03 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("14:23:04.720000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_IPD(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RD1.R8_FPA-2015-02-28-16h19-2021-01-28-19h53.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual(985.4, pec.list_events[0].PoweredCircuits['RD1.R8'].current_at_discharge)
        self.assertEqual(0, pec.list_events[0].PoweredCircuits['RD1.R8'].dI_dt_at_discharge)
        self.assertEqual(359.98, pec.list_events[0].PoweredCircuits['RD1.R8'].plateau_duration)
        self.assertEqual(10, pec.list_events[0].PoweredCircuits['RD1.R8'].delta_t_FGC_PIC)
        self.assertEqual(None, pec.list_events[0].PoweredCircuits['RD1.R8'].cause_FPA)
        self.assertEqual("RD1.R8", pec.list_events[0].PoweredCircuits['RD1.R8'].circuit_name)
        self.assertEqual("RD1", pec.list_events[0].PoweredCircuits['RD1.R8'].circuit_type)
        self.assertEqual(985.4, pec.list_events[0].QuenchEvents['RD1.R8'].current_at_quench)
        self.assertEqual(None, pec.list_events[0].QuenchEvents['RD1.R8'].quench_cause)
        self.assertEqual(1, pec.list_events[0].QuenchEvents['RD1.R8'].delta_t_iQPS_PIC)
        self.assertEqual(None, pec.list_events[0].QuenchEvents['RD1.R8'].QDS_trigger_origin)
        self.assertEqual(None, pec.list_events[0].QuenchEvents['RD1.R8'].dU_iQPS_dt)
        self.assertEqual("RD1.R8", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2015", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2015-02-28 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("16:19:30.480000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RCS(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RCS.A23B2_FPA-2023-03-18-12h36-2023-03-18-15h02.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual(379.9, pec.list_events[0].PoweredCircuits['RCS.A23B2'].current_at_discharge)
        self.assertEqual(0, pec.list_events[0].PoweredCircuits['RCS.A23B2'].dI_dt_at_discharge)
        self.assertEqual(2.23999999999999, pec.list_events[0].PoweredCircuits['RCS.A23B2'].plateau_duration)
        self.assertEqual(11, pec.list_events[0].PoweredCircuits['RCS.A23B2'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RCS.A23B2'].cause_FPA)
        self.assertEqual("RCS.A23B2", pec.list_events[0].PoweredCircuits['RCS.A23B2'].circuit_name)
        self.assertEqual("RCS", pec.list_events[0].PoweredCircuits['RCS.A23B2'].circuit_type)
        self.assertEqual(379.9, pec.list_events[0].QuenchEvents['RCS.A23B2'].current_at_quench)
        self.assertEqual("Training", pec.list_events[0].QuenchEvents['RCS.A23B2'].quench_cause)
        self.assertEqual(6, pec.list_events[0].QuenchEvents['RCS.A23B2'].delta_t_iQPS_PIC)
        self.assertEqual("QPS", pec.list_events[0].QuenchEvents['RCS.A23B2'].QDS_trigger_origin)
        self.assertEqual(62.596955675, pec.list_events[0].QuenchEvents['RCS.A23B2'].dU_iQPS_dt)
        self.assertEqual(0, pec.list_events[0].EnergyExtractionSystem['RCS.A23B2'].delta_t_EE_PIC)
        self.assertEqual(223.317, pec.list_events[0].EnergyExtractionSystem['RCS.A23B2'].U_EE_max)
        self.assertEqual("RCS.A23B2", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2023", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2023-03-18 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("12:36:00.200000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RCD(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RCD.A78B2_FPA-2022-04-09-08h45-2022-04-09-14h32.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1, len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual([0, -549.9], pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].current_at_discharge)
        self.assertEqual([0, 0], pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].dI_dt_at_discharge)
        self.assertEqual([0, 359.98], pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].plateau_duration)
        self.assertEqual(21, pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].cause_FPA)
        self.assertEqual("RCD-RCO.A78B2", pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].circuit_name)
        self.assertEqual("RCD", pec.list_events[0].PoweredCircuits['RCD-RCO.A78B2'].circuit_type)
        self.assertEqual([0, -549.9], pec.list_events[0].QuenchEvents['RCD-RCO.A78B2'].current_at_quench)
        self.assertEqual("Unknown", pec.list_events[0].QuenchEvents['RCD-RCO.A78B2'].quench_cause)
        self.assertEqual(1, pec.list_events[0].QuenchEvents['RCD-RCO.A78B2'].delta_t_iQPS_PIC)
        self.assertEqual("RCD", pec.list_events[0].QuenchEvents['RCD-RCO.A78B2'].magnet_name)
        self.assertEqual([0, -83.0349], pec.list_events[0].QuenchEvents['RCD-RCO.A78B2'].dU_iQPS_dt)
        self.assertEqual("QPS", pec.list_events[0].QuenchEvents['RCD-RCO.A78B2'].QDS_trigger_origin)
        self.assertEqual(-5, pec.list_events[0].EnergyExtractionSystem['RCD-RCO.A78B2'].delta_t_EE_PIC)
        self.assertEqual(338.809, pec.list_events[0].EnergyExtractionSystem['RCD-RCO.A78B2'].U_EE_max)
        self.assertEqual("RCD-RCO.A78B2", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("Operation 2022", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2022-04-09 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("08:45:17.660000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RCBX(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RCBX1.L1_FPA-2021-05-06-18h12-2021-05-07-11h01.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual([190.9, 362.5], pec.list_events[0].PoweredCircuits['RCBX1.L1'].current_at_discharge)
        self.assertEqual([2.1, -1.1], pec.list_events[0].PoweredCircuits['RCBX1.L1'].dI_dt_at_discharge)
        self.assertEqual([0, 0], pec.list_events[0].PoweredCircuits['RCBX1.L1'].plateau_duration)
        self.assertEqual(1, pec.list_events[0].PoweredCircuits['RCBX1.L1'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RCBX1.L1'].cause_FPA)
        self.assertEqual("RCBX1.L1", pec.list_events[0].PoweredCircuits['RCBX1.L1'].circuit_name)
        self.assertEqual("RCBX", pec.list_events[0].PoweredCircuits['RCBX1.L1'].circuit_type)
        self.assertEqual([190.9, 362.5], pec.list_events[0].QuenchEvents['RCBX1.L1'].current_at_quench)
        self.assertEqual("Training", pec.list_events[0].QuenchEvents['RCBX1.L1'].quench_cause)
        self.assertEqual(-4, pec.list_events[0].QuenchEvents['RCBX1.L1'].delta_t_iQPS_PIC)
        self.assertEqual("H", pec.list_events[0].QuenchEvents['RCBX1.L1'].magnet_name)
        self.assertEqual([92.1693524999999, 0], pec.list_events[0].QuenchEvents['RCBX1.L1'].dU_iQPS_dt)
        self.assertEqual("QPS", pec.list_events[0].QuenchEvents['RCBX1.L1'].QDS_trigger_origin)
        self.assertEqual("RCBX1.L1", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2021", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2021-05-06 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("18:12:53.680000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RCBC(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RCBCH5.L1B2_FPA-2021-04-26-18h36-2021-04-27-14h03.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(1,len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual(84.8, pec.list_events[0].PoweredCircuits['RCBCH5.L1B2'].current_at_discharge)
        self.assertEqual(0.7, pec.list_events[0].PoweredCircuits['RCBCH5.L1B2'].dI_dt_at_discharge)
        self.assertEqual(0, pec.list_events[0].PoweredCircuits['RCBCH5.L1B2'].plateau_duration)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RCBCH5.L1B2'].cause_FPA)
        self.assertEqual("RCBCH5.L1B2", pec.list_events[0].PoweredCircuits['RCBCH5.L1B2'].circuit_name)
        self.assertEqual("RCBCH", pec.list_events[0].PoweredCircuits['RCBCH5.L1B2'].circuit_type)
        self.assertEqual(84.8, pec.list_events[0].QuenchEvents['RCBCH5.L1B2'].current_at_quench)
        self.assertEqual("Training", pec.list_events[0].QuenchEvents['RCBCH5.L1B2'].quench_cause)
        self.assertEqual("RCBCH5.L1B2", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2021", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2021-04-26 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("18:36:57.060000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RQ(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RQ.A12_FPA-2021-05-02-15h07-2021-05-02-16h45.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(2, len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual([11125.3, 11125.4], pec.list_events[0].PoweredCircuits['RQ.A12'].current_at_discharge)
        self.assertEqual([10, 10], pec.list_events[0].PoweredCircuits['RQ.A12'].dI_dt_at_discharge)
        self.assertEqual([0, 0], pec.list_events[0].PoweredCircuits['RQ.A12'].plateau_duration)
        self.assertEqual(-21, pec.list_events[0].PoweredCircuits['RQ.A12'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RQ.A12'].cause_FPA)
        self.assertEqual("RQ.A12", pec.list_events[0].PoweredCircuits['RQ.A12'].circuit_name)
        self.assertEqual("RQ", pec.list_events[0].PoweredCircuits['RQ.A12'].circuit_type)
        self.assertEqual([11125, 11125], pec.list_events[0].QuenchEvents['RQ.A12'].current_at_quench)
        self.assertEqual("Training", pec.list_events[0].QuenchEvents['RQ.A12'].quench_cause)
        self.assertEqual("34R1", pec.list_events[0].QuenchEvents['RQ.A12'].magnet_electrical_position)
        self.assertEqual(-8.43947, pec.list_events[0].QuenchEvents['RQ.A12'].delta_t_iQPS_PIC)
        self.assertEqual([5, 5], pec.list_events[0].QuenchEvents['RQ.A12'].delta_t_nQPS_PIC)
        self.assertEqual("/INT", pec.list_events[0].QuenchEvents['RQ.A12'].magnet_name)
        self.assertEqual(0, pec.list_events[0].QuenchEvents['RQ.A12'].quench_order)
        self.assertEqual([0, 7.27], pec.list_events[0].QuenchEvents['RQ.A12'].dU_iQPS_dt)
        self.assertEqual("QPS", pec.list_events[0].QuenchEvents['RQ.A12'].QDS_trigger_origin)
        self.assertEqual([71, 72], pec.list_events[0].EnergyExtractionSystem['RQ.A12'].delta_t_EE_PIC)
        self.assertEqual([73.2873635, 73.5192584694], pec.list_events[0].EnergyExtractionSystem['RQ.A12'].U_EE_max)
        self.assertEqual("RQ.A12", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2021", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2021-05-02 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("15:07:07.760000", str(pec.list_events[0].GeneralParameters.time))

        self.assertEqual([11125.3, 11125.4], pec.list_events[1].PoweredCircuits['RQ.A12'].current_at_discharge)
        self.assertEqual([10, 10], pec.list_events[1].PoweredCircuits['RQ.A12'].dI_dt_at_discharge)
        self.assertEqual([0, 0], pec.list_events[1].PoweredCircuits['RQ.A12'].plateau_duration)
        self.assertEqual(-21, pec.list_events[1].PoweredCircuits['RQ.A12'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[1].PoweredCircuits['RQ.A12'].cause_FPA)
        self.assertEqual("RQ.A12", pec.list_events[1].PoweredCircuits['RQ.A12'].circuit_name)
        self.assertEqual("RQ", pec.list_events[1].PoweredCircuits['RQ.A12'].circuit_type)
        self.assertEqual([11124, 11124], pec.list_events[1].QuenchEvents['RQ.A12'].current_at_quench)
        self.assertEqual("Training", pec.list_events[1].QuenchEvents['RQ.A12'].quench_cause)
        self.assertEqual("32L2", pec.list_events[1].QuenchEvents['RQ.A12'].magnet_electrical_position)
        self.assertEqual(13.932544, pec.list_events[1].QuenchEvents['RQ.A12'].delta_t_iQPS_PIC)
        self.assertEqual([886, 886], pec.list_events[1].QuenchEvents['RQ.A12'].delta_t_nQPS_PIC)
        self.assertEqual("RQF/INT", pec.list_events[1].QuenchEvents['RQ.A12'].magnet_name)
        self.assertEqual(0, pec.list_events[1].QuenchEvents['RQ.A12'].quench_order)
        self.assertEqual([0, 19.48], pec.list_events[1].QuenchEvents['RQ.A12'].dU_iQPS_dt)
        self.assertEqual("QPS", pec.list_events[1].QuenchEvents['RQ.A12'].QDS_trigger_origin)
        self.assertEqual([71, 72], pec.list_events[1].EnergyExtractionSystem['RQ.A12'].delta_t_EE_PIC)
        self.assertEqual([73.2873635, 73.5192584694], pec.list_events[1].EnergyExtractionSystem['RQ.A12'].U_EE_max)
        self.assertEqual("RQ.A12", pec.list_events[1].GeneralParameters.name)
        self.assertEqual("HWC 2021", pec.list_events[1].GeneralParameters.period)
        self.assertEqual("2021-05-02 00:00:00", str(pec.list_events[1].GeneralParameters.date))
        self.assertEqual("15:07:07.760000", str(pec.list_events[0].GeneralParameters.time))

    def test_ParsimEventCircuit_Read_RB(self):
        # arrange
        pec = ParsimEventCircuit()
        path_file = os.path.join('input', "parsim_event_circuit", 'RB.A12_FPA-2008-08-22-09h59-2022-12-26-21h55.xlsx')

        # act
        pec.read_from_input(path_input_file=path_file, flag_append=False)

        # assert
        self.assertEqual(3, len(pec.list_events))
        self.assertEqual(DataEventCircuit, type(pec.list_events[0]))
        self.assertEqual(6998.7, pec.list_events[0].PoweredCircuits['RB.A12'].current_at_discharge)
        self.assertEqual(0, pec.list_events[0].PoweredCircuits['RB.A12'].dI_dt_at_discharge)
        self.assertEqual(509, pec.list_events[0].PoweredCircuits['RB.A12'].plateau_duration)
        self.assertEqual(31, pec.list_events[0].PoweredCircuits['RB.A12'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[0].PoweredCircuits['RB.A12'].cause_FPA)
        self.assertEqual("RB.A12", pec.list_events[0].PoweredCircuits['RB.A12'].circuit_name)
        self.assertEqual("RB", pec.list_events[0].PoweredCircuits['RB.A12'].circuit_type)
        self.assertEqual(6999, pec.list_events[0].QuenchEvents['RB.A12'].current_at_quench)
        self.assertEqual("Heater-provoked", pec.list_events[0].QuenchEvents['RB.A12'].quench_cause)
        self.assertEqual("B19R1", pec.list_events[0].QuenchEvents['RB.A12'].magnet_electrical_position)
        self.assertEqual(-13, pec.list_events[0].QuenchEvents['RB.A12'].delta_t_iQPS_PIC)
        self.assertEqual(0, pec.list_events[0].QuenchEvents['RB.A12'].delta_t_nQPS_PIC)
        self.assertEqual("EXT", pec.list_events[0].QuenchEvents['RB.A12'].magnet_name)
        self.assertEqual(1, pec.list_events[0].QuenchEvents['RB.A12'].quench_order)
        self.assertEqual(0.15, pec.list_events[0].QuenchEvents['RB.A12'].dU_iQPS_dt)
        self.assertEqual("iQPS", pec.list_events[0].QuenchEvents['RB.A12'].QDS_trigger_origin)
        self.assertEqual(0, pec.list_events[0].QuenchEvents['RB.A12'].V_symm_max)
        self.assertEqual(0, pec.list_events[0].QuenchEvents['RB.A12'].dV_symm_dt)
        self.assertEqual([-1, -1], pec.list_events[0].EnergyExtractionSystem['RB.A12'].delta_t_EE_PIC)
        self.assertEqual([485, 503], pec.list_events[0].EnergyExtractionSystem['RB.A12'].U_EE_max)
        self.assertEqual("RB.A12", pec.list_events[0].GeneralParameters.name)
        self.assertEqual("HWC 2008", pec.list_events[0].GeneralParameters.period)
        self.assertEqual("2008-08-22 00:00:00", str(pec.list_events[0].GeneralParameters.date))
        self.assertEqual("09:59:25.200000", str(pec.list_events[0].GeneralParameters.time))

        self.assertEqual(6998.7, pec.list_events[1].PoweredCircuits['RB.A12'].current_at_discharge)
        self.assertEqual(0, pec.list_events[1].PoweredCircuits['RB.A12'].dI_dt_at_discharge)
        self.assertEqual(509, pec.list_events[1].PoweredCircuits['RB.A12'].plateau_duration)
        self.assertEqual(31, pec.list_events[1].PoweredCircuits['RB.A12'].delta_t_FGC_PIC)
        self.assertEqual("Magnet quench", pec.list_events[1].PoweredCircuits['RB.A12'].cause_FPA)
        self.assertEqual("RB.A12", pec.list_events[1].PoweredCircuits['RB.A12'].circuit_name)
        self.assertEqual("RB", pec.list_events[1].PoweredCircuits['RB.A12'].circuit_type)
        self.assertEqual(4285, pec.list_events[1].QuenchEvents['RB.A12'].current_at_quench)
        self.assertEqual("GHe propagation", pec.list_events[1].QuenchEvents['RB.A12'].quench_cause)
        self.assertEqual("C19R1", pec.list_events[1].QuenchEvents['RB.A12'].magnet_electrical_position)
        self.assertEqual(51273, pec.list_events[1].QuenchEvents['RB.A12'].delta_t_iQPS_PIC)
        self.assertEqual(0, pec.list_events[1].QuenchEvents['RB.A12'].delta_t_nQPS_PIC)
        self.assertEqual("EXT", pec.list_events[1].QuenchEvents['RB.A12'].magnet_name)
        self.assertEqual(2, pec.list_events[1].QuenchEvents['RB.A12'].quench_order)
        self.assertEqual(0.37, pec.list_events[1].QuenchEvents['RB.A12'].dU_iQPS_dt)
        self.assertEqual("iQPS", pec.list_events[1].QuenchEvents['RB.A12'].QDS_trigger_origin)
        self.assertEqual(0, pec.list_events[1].QuenchEvents['RB.A12'].V_symm_max)
        self.assertEqual(0, pec.list_events[1].QuenchEvents['RB.A12'].dV_symm_dt)
        self.assertEqual([-1, -1], pec.list_events[1].EnergyExtractionSystem['RB.A12'].delta_t_EE_PIC)
        self.assertEqual([485, 503], pec.list_events[1].EnergyExtractionSystem['RB.A12'].U_EE_max)
        self.assertEqual("RB.A12", pec.list_events[1].GeneralParameters.name)
        self.assertEqual("HWC 2008", pec.list_events[1].GeneralParameters.period)
        self.assertEqual("2008-08-22 00:00:00", str(pec.list_events[1].GeneralParameters.date))
        self.assertEqual("09:59:25.200000", str(pec.list_events[1].GeneralParameters.time))

