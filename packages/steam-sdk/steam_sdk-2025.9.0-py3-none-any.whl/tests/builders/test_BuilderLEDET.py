import unittest
import os
import numpy as np
import yaml
from pathlib import Path

from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from tests.TestHelpers import assert_two_parameters


class TestBuilderLEDET(unittest.TestCase):

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
            'dcore_inGroup': 4 * [None],
            'dfilamentary_inGroup': 4 * [None],
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

    def test_BuilderLEDET_init(self):
        """
            Check that DataLEDET object can be initialized
        """
        # arrange

        # act
        bLEDET = BuilderLEDET(flag_build=False)

        # assert
        self.assertEqual(hasattr(bLEDET, 'verbose'), True)
        self.assertEqual(hasattr(bLEDET, 'model_data'), True)
        self.assertEqual(hasattr(bLEDET, 'roxie_data'), True)

        self.assertEqual(hasattr(bLEDET, 'Inputs'), True)
        self.assertEqual(hasattr(bLEDET, 'Options'), True)
        self.assertEqual(hasattr(bLEDET, 'Plots'), True)
        self.assertEqual(hasattr(bLEDET, 'Variables'), True)
        self.assertEqual(hasattr(bLEDET, 'Auxiliary'), True)

        self.assertEqual(hasattr(bLEDET, 'descriptionsInputs'), True)
        self.assertEqual(hasattr(bLEDET, 'descriptionsOptions'), True)
        self.assertEqual(hasattr(bLEDET, 'descriptionsPlots'), True)
        self.assertEqual(hasattr(bLEDET, 'descriptionsVariables'), True)

        self.assertEqual(hasattr(bLEDET, 'smic_write_path'), True)
        self.assertEqual(hasattr(bLEDET, 'enableConductorResistanceFraction'), True)

    def test_setAttribute(self):
        """
            **Test that setAttribute works**
        """
        # arrange
        bLEDET = BuilderLEDET(flag_build=False)

        for parameter in self.local_Inputs:
            true_value = self.local_Inputs[parameter]
            setattr(bLEDET.Inputs, parameter, true_value)
            # act
            test_value = bLEDET.getAttribute('Inputs', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Options:
            true_value = self.local_Options[parameter]
            setattr(bLEDET.Options, parameter, true_value)
            # act
            test_value = bLEDET.getAttribute('Options', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Plots:
            true_value = self.local_Plots[parameter]
            setattr(bLEDET.Plots, parameter, true_value)
            # act
            test_value = bLEDET.getAttribute('Plots', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Variables:
            true_value = self.local_Variables[parameter]
            setattr(bLEDET.Variables, parameter, true_value)
            # act
            test_value = bLEDET.getAttribute('Variables', parameter)
            # assert
            assert_two_parameters(true_value, test_value)

    def test_getAttribute(self):
        """
            **Test getAttribute works**
        """
        # arrange
        bLEDET = BuilderLEDET(flag_build=False)

        for parameter in self.local_Inputs:
            true_value = self.local_Inputs[parameter]
            # act
            bLEDET.setAttribute('Inputs', parameter, true_value)
            test_value = getattr(bLEDET.Inputs, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Options:
            true_value = self.local_Options[parameter]
            # act
            bLEDET.setAttribute('Options', parameter, true_value)
            test_value = getattr(bLEDET.Options, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Plots:
            true_value = self.local_Plots[parameter]
            # act
            bLEDET.setAttribute('Plots', parameter, true_value)
            test_value = getattr(bLEDET.Plots, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

        for parameter in self.local_Variables:
            true_value = self.local_Variables[parameter]
            # act
            bLEDET.setAttribute('Variables', parameter, true_value)
            test_value = getattr(bLEDET.Variables, parameter)
            # assert
            assert_two_parameters(true_value, test_value)

    def test_localParser(self):
        """
            **Test if the method localsParser() **
            Returns error if the local parser does not change the given parameters
            Assumes that getAttribute() works
        """
        # arrange
        bLEDET = BuilderLEDET(flag_build=False)

        # act
        bLEDET.localsParser({**self.local_Inputs, **self.local_Options, **self.local_Plots, **self.local_Variables})

        # assert
        for attribute in self.local_Inputs:
            self.assertIn(attribute, {**bLEDET.Inputs.__annotations__})

            true_value = self.local_Inputs[attribute]
            test_value = bLEDET.getAttribute('Inputs', attribute)
            assert_two_parameters(true_value, test_value)
        for attribute in self.local_Options:
            self.assertIn(attribute, {**bLEDET.Options.__annotations__})

            true_value = self.local_Options[attribute]
            test_value = bLEDET.getAttribute('Options', attribute)
            assert_two_parameters(true_value, test_value)
        for attribute in self.local_Plots:
            self.assertIn(attribute, {**bLEDET.Plots.__annotations__})

            true_value = self.local_Plots[attribute]
            test_value = bLEDET.getAttribute('Plots', attribute)
            assert_two_parameters(true_value, test_value)
        for attribute in self.local_Variables:
            self.assertIn(attribute, {**bLEDET.Variables.__annotations__})

            true_value = self.local_Variables[attribute]
            test_value = bLEDET.getAttribute('Variables', attribute)
            assert_two_parameters(true_value, test_value)

    def test_loadConductorData(self):
        """
            Test loadConductorData() method with content from modelData_MQXF_V2.yaml
        """
        # arrange
        magnet_name = 'MQXF_V2'
        file_model_data = os.path.join('model_library', 'magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
        path_input_file = Path(file_model_data).parent
        dictionary = yaml.safe_load(open(file_model_data))
        inputModelData = DataModelMagnet(**dictionary)

        bLEDET = BuilderLEDET(path_input_file=path_input_file, input_model_data=inputModelData, flag_build=False,
                              verbose=True)

        bLEDET.translateModelDataToLEDET()
        bLEDET.loadParametersFromMap2dInRoxieParser()

        # act
        bLEDET.loadConductorData()

        # assert

    def test_loadParametersFromMap2d(self):
        """
            Test loadParametersFromMap2d method with content from modelData_MQXF_V2.yaml
        """
        # arrange
        magnet_name = 'MQXF_V2'
        file_model_data = os.path.join('model_library','magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
        path_input_file = Path(file_model_data).parent
        dictionary = yaml.safe_load(open(file_model_data))
        input_model_data = DataModelMagnet(**dictionary)

        expected_nT = [16, 12, 17, 5, 16, 12, 17, 5, 16, 12, 17, 5, 16, 12, 17, 5, 16, 12, 17, 5, 16, 12, 17, 5, 16, 12, 17, 5, 16, 12, 17, 5]
        expected_polarities_inGroup = [1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1]

        bLEDET = BuilderLEDET(path_input_file=path_input_file, input_model_data=input_model_data, flag_build=False)
        bLEDET.translateModelDataToLEDET()

        # act
        bLEDET.loadParametersFromMap2dInRoxieParser()

        # assert
        self.assertEqual(expected_polarities_inGroup, bLEDET.Inputs.polarities_inGroup)
        self.assertEqual(expected_nT, bLEDET.Inputs.nT)

    def test_loadParametersFromDataModel(self):
        """
            Test loadParametersFromDataModel() method with content from modelData_MQXF_V2.yaml
        """
        # arrange
        magnet_name = 'MCBRD'
        file_model_data = os.path.join('model_library', 'magnets', magnet_name, 'input', 'modelData_' + magnet_name + '.yaml')
        path_input_file = Path(file_model_data).parent
        dictionary = yaml.safe_load(open(file_model_data))
        inputModelData = DataModelMagnet(**dictionary)

        bLEDET = BuilderLEDET(path_input_file=path_input_file, input_model_data=inputModelData, flag_build=False,
                              verbose=True)

        # act
        bLEDET.loadParametersFromDataModel()

        # assert
        self.assertEqual(inputModelData.CoilWindings.polarities_in_group, bLEDET.Inputs.polarities_inGroup)
        self.assertEqual(inputModelData.CoilWindings.n_half_turn_in_group, bLEDET.Inputs.nT)

    def test_translateModelDataToLEDET(self):
        """
            Check that calcElectricalOrder calculates correctly. The test use-case if for MQXF_V2
        """
        # arrange
        model_data = DataModelMagnet()
        bLEDET = BuilderLEDET(input_model_data=model_data, flag_build=False)

        # act
        bLEDET.translateModelDataToLEDET()

        # assert
        # TODO: Check that all keys are correctly passed

    def test_addThermalConnections_alongWidth(self):
        """
            Check that addThermalConnections() works correctly. The test use-case is invented and defined manually
        """
        # arrange
        iContactAlongWidth_From_initial   = np.array([1, 2, 3, 3, 5, 6, 7, 8, 9, 10, 13])
        iContactAlongWidth_To_initial     = np.array([101, 102, 103, 104, 104, 106, 107, 108, 109, 110, 113])
        iContactAlongWidth_pairs_to_add   = [[11, 111], [12, 111], [13, 113], [13, 113]]  # Note that this will be passed by the BuilderLEDET as a list of lists and not as a np.array
        iContactAlongWidth_From_reference = np.array([1, 2, 3, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        iContactAlongWidth_To_reference   = np.array([101, 102, 103, 104, 104, 106, 107, 108, 109, 110, 111, 111, 113])  # these entries were manually written

        # Assign test variables to an empty BuilderLEDET object
        bLEDET = BuilderLEDET(flag_build=False)
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From_initial))
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongWidth_To',   np.array(iContactAlongWidth_To_initial))
        bLEDET.setAttribute(bLEDET.Auxiliary, 'iContactAlongWidth_pairs_to_add', np.array(iContactAlongWidth_pairs_to_add))

        # act - This method must add these connections and set the two LEDET parameters
        bLEDET.addThermalConnections()

        # assert - Check that the parameters were correctly set
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongWidth_From')), list(iContactAlongWidth_From_reference))
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongWidth_To')),   list(iContactAlongWidth_To_reference))

    def test_addThermalConnections_alongHeight(self):
        """
            Check that addThermalConnections() works correctly. The test use-case is invented and defined manually
        """
        # arrange
        iContactAlongHeight_From_initial   = np.array([1, 2, 3, 3, 5, 6, 7, 8, 9, 10, 13])
        iContactAlongHeight_To_initial     = np.array([101, 102, 103, 104, 104, 106, 107, 108, 109, 110, 113])
        iContactAlongHeight_pairs_to_add   =[[13, 113], [11, 111], [12, 111], [13, 113]]  # Note that this will be passed by the BuilderLEDET as a list of lists and not as a np.array
        iContactAlongHeight_From_reference = np.array([1, 2, 3, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13])
        iContactAlongHeight_To_reference   = np.array([101, 102, 103, 104, 104, 106, 107, 108, 109, 110, 111, 111, 113])  # these entries were manually written

        # Assign test variables to an empty BuilderLEDET object
        bLEDET = BuilderLEDET(flag_build=False)
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From_initial))
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongHeight_To',   np.array(iContactAlongHeight_To_initial))
        bLEDET.setAttribute(bLEDET.Auxiliary, 'iContactAlongHeight_pairs_to_add', np.array(iContactAlongHeight_pairs_to_add))

        # act - This method must add these connections and set the two LEDET parameters
        bLEDET.addThermalConnections()

        # assert - Check that the parameters were correctly set
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongHeight_From')), list(iContactAlongHeight_From_reference))
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongHeight_To')),   list(iContactAlongHeight_To_reference))

    def test_removeThermalConnections_alongWidth(self):
        """
            Check that addThermalConnections() works correctly. The test use-case is invented and defined manually
        """
        # arrange
        iContactAlongWidth_From_initial = np.array([1, 2, 3, 3, 5, 6, 7, 8, 9, 10])
        iContactAlongWidth_To_initial = np.array([101, 102, 103, 104, 105, 106, 107, 108, 109, 110])
        iContactAlongWidth_pairs_to_remove = [[8, 108], [9, 109], [10, 110], [10, 110]]  # Note that this will be passed by the BuilderLEDET as a list of lists and not as a np.array
        iContactAlongWidth_From_reference = np.array([1, 2, 3, 3, 5, 6, 7])
        iContactAlongWidth_To_reference = np.array([101, 102, 103, 104, 105, 106, 107])  # these entries were manually written

        # Assign test variables to an empty BuilderLEDET object
        bLEDET = BuilderLEDET(flag_build=False)
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From_initial))
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To_initial))
        bLEDET.setAttribute(bLEDET.Auxiliary, 'iContactAlongWidth_pairs_to_remove', np.array(iContactAlongWidth_pairs_to_remove))

        # act - This method must add these connections and set the two LEDET parameters
        bLEDET.removeThermalConnections()

        # assert - Check that the parameters were correctly set
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongWidth_From')), list(iContactAlongWidth_From_reference))
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongWidth_To')), list(iContactAlongWidth_To_reference))

    def test_removeThermalConnections_alongHeight(self):
        """
            Check that removeThermalConnections() works correctly. The test use-case is invented and defined manually
        """
        # arrange
        iContactAlongHeight_From_initial = np.array([1, 2, 3, 4, 5, 5, 7, 8, 9, 10])
        iContactAlongHeight_To_initial = np.array([101, 101, 103, 104, 105, 106, 107, 108, 109, 110])
        iContactAlongHeight_pairs_to_remove = [[10, 110], [8, 108], [9, 109], [10,
                                                                               110]]  # Note that this will be passed by the BuilderLEDET as a list of lists and not as a np.array
        iContactAlongHeight_From_reference = np.array([1, 2, 3, 4, 5, 5, 7])
        iContactAlongHeight_To_reference = np.array(
            [101, 101, 103, 104, 105, 106, 107])  # these entries were manually written

        # Assign test variables to an empty BuilderLEDET object
        bLEDET = BuilderLEDET(flag_build=False)
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From_initial))
        bLEDET.setAttribute(bLEDET.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To_initial))
        bLEDET.setAttribute(bLEDET.Auxiliary, 'iContactAlongHeight_pairs_to_remove',
                            np.array(iContactAlongHeight_pairs_to_remove))

        # act - This method must add these connections and set the two LEDET parameters
        bLEDET.removeThermalConnections()

        # assert - Check that the parameters were correctly set
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongHeight_From')),
                             list(iContactAlongHeight_From_reference))
        self.assertListEqual(list(bLEDET.getAttribute(bLEDET.Inputs, 'iContactAlongHeight_To')),
                             list(iContactAlongHeight_To_reference))

    # def test_printVariableDescNameValue(self):
    #     """
    #         Check that printVariableDescNameValue() works correctly.
    #     """
    #     # arrange
    #     bLEDET = BuilderLEDET(flag_build=False)
    #
    #     # act - Visualize variable descriptions, names, and values
    #     print('### "Inputs" variables ###')
    #     bLEDET.printVariableDescNameValue(bLEDET.Inputs, bLEDET.descriptionsInputs)
    #
    #     print('')
    #     print('### "Options" variables ###')
    #     bLEDET.printVariableDescNameValue(bLEDET.Options, bLEDET.descriptionsOptions)
    #
    #     print('')
    #     print('### "Plots" variables ###')
    #     bLEDET.printVariableDescNameValue(bLEDET.Plots, bLEDET.descriptionsPlots)
    #
    #     # Visualize variable descriptions, names, and values
    #     print('')
    #     print('### "Variables" variables ###')
    #     bLEDET.printVariableDescNameValue(bLEDET.Variables, bLEDET.descriptionsVariables)
    #
    #     # assert
    #     print('Test passed: all variables in LEDET dataclasses have a description read from the TemplateLEDET() class.')
