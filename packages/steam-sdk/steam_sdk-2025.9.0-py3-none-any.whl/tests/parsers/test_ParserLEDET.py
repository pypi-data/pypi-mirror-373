import os
import unittest
from pathlib import Path
import numpy as np

from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.parsers.ParserLEDET import ParserLEDET, check_for_differences
from steam_sdk.parsers.ParserLEDET import copy_map2d, copy_modified_map2d_ribbon_cable
from steam_sdk.parsers.ParserMap2d import ParserMap2dFile
from steam_sdk.utils.delete_if_existing import delete_if_existing
from tests.TestHelpers import assert_two_parameters


class TestParserLEDET(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """
        This function is executed once before any tests in this class
        """
        delete_if_existing(os.path.join(os.path.dirname(__file__), 'output', 'LEDET'), verbose=True)

    def setUp(self) -> None:
        """
            This function is executed before each test in this class
        """
        self.current_path = os.getcwd()
        os.chdir(os.path.dirname(__file__))  # move to the directory where this file is located
        print('\nCurrent folder:          {}'.format(self.current_path))
        print('\nTest is run from folder: {}'.format(os.getcwd()))

        # Define Inputs parameters that are equal to input file
        self.local_Inputs = {
            'T00': 1.9,
            'l_magnet': 7.15,
            'I00': 10e3,
            'M_m': np.arange(16).reshape(4, 4) / 57,
            'fL_I': [i * 10e3 for i in range(10)],
            'fL_L': [i / 12 + 0.01 for i in range(10)],
            'GroupToCoilSection': [1, 2, 1, 2],
            'polarities_inGroup': [+1, +1, -1, -1],
            'nT': 4 * [40],
            'nStrands_inGroup': 4 * [40],
            'l_mag_inGroup': 4 * [7.15],
            'ds_inGroup': 4 * [0.8],
            'f_SC_strand_inGroup': 4 * [0.54],
            'f_ro_eff_inGroup': 4 * [1],
            'Lp_f_inGroup': 4 * [0.019],
            'RRR_Cu_inGroup': 4 * [100],
            'SCtype_inGroup': 4 * [1],
            'STtype_inGroup': 4 * [1],
            'insulationType_inGroup': 4 * [1],
            'internalVoidsType_inGroup': 4 * [1],
            'externalVoidsType_inGroup': 4 * [1],
            'wBare_inGroup': 4 * [1],
            'hBare_inGroup': 4 * [1],
            'wIns_inGroup': 4 * [1],
            'hIns_inGroup': 4 * [1],
            'Lp_s_inGroup': 4 * [1],
            'R_c_inGroup': 4 * [1],
            'Tc0_NbTi_ht_inGroup': 4 * [1],
            'Bc2_NbTi_ht_inGroup': 4 * [1],
            'c1_Ic_NbTi_inGroup': 4 * [1],
            'c2_Ic_NbTi_inGroup': 4 * [1],
            'Tc0_Nb3Sn_inGroup': 4 * [1],
            'Bc2_Nb3Sn_inGroup': 4 * [1],
            'Jc_Nb3Sn0_inGroup': 4 * [1],
            'el_order_half_turns': list(range(1, 160 + 1)),
            'alphasDEG': 160 * [1],
            'rotation_block': 160 * [1],
            'mirror_block': 160 * [1],
            'mirrorY_block': 160 * [1],
            'iContactAlongWidth_From': 4 * [1],
            'iContactAlongWidth_To': 4 * [1],
            'iContactAlongHeight_From': 4 * [1],
            'iContactAlongHeight_To': 4 * [1],
            'iStartQuench': 4 * [1],
            'tStartQuench': 4 * [1],
            'lengthHotSpot_iStartQuench': 4 * [1],
            'fScaling_vQ_iStartQuench': 4 * [1],
            'R_circuit': 1e-3,
            'R_crowbar': 1E-3,
            'Ud_crowbar': 0.7,
            't_PC': 0,
            't_PC_LUT': [-0.02, 0, 0 + 0.01],
            'I_PC_LUT': [10e3, 10e3, 0],
            'tEE': 99999,
            'R_EE_triggered': .0125,
            'tCLIQ': 0.5e-3,
            'directionCurrentCLIQ': [1, -1],
            'nCLIQ': 1,
            'U0': 1000,
            'C': 0.04,
            'Rcapa': 0.05,
            'tQH': 8 * [0.001],
            'U0_QH': 8 * [1],
            'C_QH': 8 * [1],
            'R_warm_QH': 8 * [1],
            'w_QH': 8 * [1],
            'h_QH': 8 * [1],
            's_ins_QH': 8 * [1],
            'type_ins_QH': 8 * [2],
            's_ins_QH_He': 8 * [1],
            'type_ins_QH_He': 8 * [2],
            'l_QH': 8 * [1],
            'f_QH': 8 * [0.25],
            'iQH_toHalfTurn_From': [1 for i in range(100)],
            'iQH_toHalfTurn_To': [2 for i in range(100)],
            'tQuench': -.02,
            'initialQuenchTemp': 10,
            'HalfTurnToInductanceBlock': list(range(1, 400 + 1)),
            'M_InductanceBlock_m': np.arange(400).reshape(20, 20) / 57
        }

        # Define Options parameters that are equal to input file
        self.local_Options = {
            'time_vector_params': [-0.02, 0.0025, 0],
            'Iref': 16471,
            'flagIron': 1,
            'flagSelfField': 1,
            'headerLines': 1,
            'columnsXY': 4,
            'columnsBxBy': 6,
            'flagPlotMTF': 0,
            'flag_calculateInductanceMatrix': 0,
            'flag_useExternalInitialization': 0,
            'flag_initializeVar': 0,
            'flag_fastMode': 1,
            'flag_controlCurrent': 0,
            'flag_automaticRefinedTimeStepping': 1,
            'flag_IronSaturation': 1,
            'flag_InvertCurrentsAndFields': 0,
            'flag_ScaleDownSuperposedMagneticField': 1,
            'flag_HeCooling': 2,
            'fScaling_Pex': 1,
            'fScaling_Pex_AlongHeight': 1,
            'fScaling_MR': 1,
            'flag_scaleCoilResistance_StrandTwistPitch': 2,
            'flag_separateInsulationHeatCapacity': 0,
            'flag_ISCL': 1,
            'fScaling_Mif': 1,
            'fScaling_Mis': 1,
            'flag_StopIFCCsAfterQuench': 0,
            'flag_StopISCCsAfterQuench': 0,
            'tau_increaseRif': 0.005,
            'tau_increaseRis': 0.01,
            'fScaling_RhoSS': 1.09,
            'maxVoltagePC': 10,
            'flag_symmetricGroundingEE': 0,
            'flag_removeUc': 0,
            'BtX_background': 0,
            'BtY_background': 0,
            'flag_showFigures': 0,
            'flag_saveFigures': 0,
            'flag_saveMatFile': 1,
            'flag_saveTxtFiles': 0,
            'flag_generateReport': 1,
            'flag_hotSpotTemperatureInEachGroup': 0,
        }

        # Define Plots parameters that are equal to input file
        self.local_Plots = {
            'suffixPlot': 0,
            'typePlot': 0,
            'outputPlotSubfolderPlot': 0,
            'variableToPlotPlot': 0,
            'selectedStrandsPlot': 0,
            'selectedTimesPlot': 0,
            'labelColorBarPlot': 0,
            'minColorBarPlot': 0,
            'maxColorBarPlot': 0,
            'MinMaxXYPlot': 0,
            'flagSavePlot': 0,
            'flagColorPlot': 0,
            'flagInvisiblePlot': 0
        }

        # Define Variables parameters that are equal to input file
        self.local_Variables = {
            'variableToSaveTxt': ['time_vector', 'Ia', 'Ib'],
            'typeVariableToSaveTxt': [2, 2, 2],
            'variableToInitialize': ['Ia', 'Ib', 'T_ht']
        }

    def tearDown(self) -> None:
        """
            This function is executed after each test in this class
        """
        os.chdir(self.current_path)  # go back to initial folder

    def test_readFromExcel(self):
        # arrange
        file_name = os.path.join('references', 'TestFile_readLEDETExcel.xlsx')
        builder_ledet = BuilderLEDET(flag_build=False)

        # act
        pl = ParserLEDET(builder_ledet)
        pl.readFromExcel(file_name, verbose=True)

        # print(pl.builder_ledet.Inputs.el_order_half_turns)  # example to access a specific LEDET variable from its data structure

        # assert
        # TODO: Add check of the read file

    def test_write2Excel(self):
        # arrange
        file_name = os.path.join('output', 'LEDET', 'test_write2Excel', 'MQXF_V2_TEST.xlsx')
        builder_ledet = BuilderLEDET(flag_build=False)

        # act
        pl = ParserLEDET(builder_ledet)
        pl.writeLedet2Excel(file_name, verbose=True)

        # assert
        # TODO: Add check of the read file

    def test_readLEDETExcel(self):
        """
            **Test if the method readLEDETExcel() reads correct values from input file to parametersLEDET object**
            Returns error if any of the values read from file differs from what they should be
            Note: the input file is a read-only file such that the local parameter values and input file are equal.
            This test requires that getAttribute() works as intended
        """
        # Define default parameters
        file_name = os.path.join('references', 'TestFile_readLEDETExcel.xlsx')
        pl = ParserLEDET(BuilderLEDET(flag_build=False))

        # act
        bLEDET = pl.readFromExcel(file_name, verbose=True)

        # assert
        # check that the parameters read from file are equal to those initialized locally
        for attribute in self.local_Inputs:
            self.assertIn(attribute, {**bLEDET.Inputs.__annotations__})
            assert_two_parameters(self.local_Inputs[attribute], bLEDET.getAttribute('Inputs', attribute))
        for attribute in self.local_Options:
            self.assertIn(attribute, {**bLEDET.Options.__annotations__})
            assert_two_parameters(self.local_Options[attribute], bLEDET.getAttribute('Options', attribute))
        for attribute in self.local_Variables:
            self.assertIn(attribute, {**bLEDET.Variables.__annotations__})
            assert_two_parameters(self.local_Variables[attribute], bLEDET.getAttribute('Variables', attribute))
        for attribute in self.local_Plots:
            self.assertIn(attribute, {**bLEDET.Plots.__annotations__})
            assert_two_parameters(self.local_Plots[attribute], bLEDET.getAttribute('Plots', attribute))

    def test_copy_map2d(self):
        """
            **Test if the method copy_map2d() ....
            check that the map2d file is correctly copied/pasted with the correct name
        """

        # Arrange
        flagIron = 1
        flagSelfField = 1

        magnet_name = 'MS_1AP'
        map2d_file_name = os.path.join('input', magnet_name + '.map2d')
        output_path = os.path.join('output', 'LEDET', 'test_copy_map2d')
        suffix = "_All_test_copy"

        # Act
        file_new_name = copy_map2d(magnet_name, map2d_file_name, output_path, flagIron, flagSelfField, suffix, verbose=True)

        # Assert
        print("Name of copied map2d-file: " + file_new_name)
        map2d_file_name_GENERATED = os.path.join(output_path, file_new_name)
        # checks correct name
        self.assertEqual(map2d_file_name_GENERATED, os.path.join(output_path, magnet_name + suffix + '_WithIron' + '_WithSelfField' + '.map2d'))

        # checks correct content
        values_REFERENCE = ParserMap2dFile(map2dFile=Path(map2d_file_name)).parseRoxieMap2d(headerLines=1)
        values_GENERATED = ParserMap2dFile(map2dFile=Path(map2d_file_name_GENERATED)).parseRoxieMap2d(headerLines=1)
        np.testing.assert_allclose(values_GENERATED, values_REFERENCE, rtol=1e-5, atol=0)


    def test_copy_modified_map2d_ribbon_cable(self):
        """
             **Test if the method copy_modify_map2d_ribbon_cable() ....
        """
        # check that the map2d file is correctly changed by comparing it to a known reference
        # INPUT:  MS_1AP_ROXIE_All_WithIron_WithSelfField.map2d
        # REFERENCE: MS_1AP_All_WithIron_WithSelfField.map2d

        # Arrange
        flagIron = 1
        flagSelfField = 1
        list_flag_ribbon = [True] * 96

        geometry_ribbon_cable = [[8,14]]*12
        magnet_name = 'MS_1AP'
        map2d_file_name = os.path.join('input', magnet_name + '.map2d')
        output_path = os.path.join('output', 'LEDET', 'test_copy_modified_map2d_ribbon_cable')
        suffix = "_All"

        # Act
        file_name_output = copy_modified_map2d_ribbon_cable(magnet_name, map2d_file_name, output_path, geometry_ribbon_cable,
                                                            flagIron, flagSelfField, list_flag_ribbon, suffix)

        # Assert
        map2d_file_name_REFERENCE = os.path.join('references', magnet_name + "_REFERENCE.map2d")
        map2d_file_name_GENERATED = os.path.join(output_path, file_name_output)

        print("Name of modified map2d-file: " + file_name_output)
        # checks correct name
        self.assertEqual(map2d_file_name_GENERATED, os.path.join(output_path, magnet_name + suffix + '_WithIron' + '_WithSelfField' + '.map2d'))

        # checks correct content
        values_REFERENCE = ParserMap2dFile(map2dFile=Path(map2d_file_name_REFERENCE)).parseRoxieMap2d(headerLines=1)
        values_GENERATED = ParserMap2dFile(map2dFile=Path(map2d_file_name_GENERATED)).parseRoxieMap2d(headerLines=1)
        np.testing.assert_allclose(values_GENERATED, values_REFERENCE, rtol=1e-5, atol=0)


    def test_readFromJson_readFromYaml(self, max_relative_error=1E-5, verbose=True):
        '''
        Test to read one json file, one yaml file, and compare that the acquired dataclasses are the same
        :return:
        '''
        # arrange
        file_name_yaml = os.path.join('input', 'read_yaml_to_LEDET', 'TestFile_readLEDETYaml.yaml')
        file_name_json = os.path.join('input', 'read_json_to_LEDET', 'TestFile_readLEDETJson.json')

        # act - json
        builder_ledet_j = BuilderLEDET(flag_build=False)
        pl_j = ParserLEDET(builder_ledet_j)
        pl_j.read_from_json(file_name_json, verbose=True)

        # act - yaml
        builder_ledet_y = BuilderLEDET(flag_build=False)
        pl_y = ParserLEDET(builder_ledet_y)
        pl_y.read_from_yaml(file_name_yaml, verbose=True)

        # assert
        self.assertEqual(0, check_for_differences(pl_j, pl_y, max_relative_error=max_relative_error, verbose=verbose))