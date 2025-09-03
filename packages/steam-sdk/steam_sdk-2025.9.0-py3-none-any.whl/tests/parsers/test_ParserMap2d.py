import unittest
import os
import sys
import numpy as np
from pathlib import Path
from steam_sdk.parsers.ParserMap2d import ParserMap2dFile

# shows complete array
# np.set_printoptions(threshold=sys.maxsize)


class TestParserMap2d(unittest.TestCase):

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

    def test_parserRoxieMap2d(self):
        """
            **Checks that the array(matrix) stream is correctly generated from the input file**
        """

        # Arrange
        # Get reference test file
        TestFile_parserRoxieMap2d = Path('references', 'TestFile_parserRoxieMap2d.map2d')

        # Get reference output array
        reference_array = np.array([[1, 1, 1, 125.7918/1000, 0.6644/1000, -0.0518, -3.4170, 0.7362/1000000, 550.0000, 0.3601],
                                    [1, 2, 2, 125.7749/1000, 1.3830/1000, -0.2249, -3.4742, 0.7362/1000000, 550.0000, 0.3601],
                                    [1, 3, 3, 125.7395/1000, 2.1015/1000, -0.4044, -3.4952, 0.7362/1000000, 550.0000, 0.3601]])

        # Act
        output = ParserMap2dFile(map2dFile=TestFile_parserRoxieMap2d).parseRoxieMap2d()

        # Assert
        np.testing.assert_allclose(reference_array, output, rtol=1e-5, atol=0)

    def test_getParametersFromMap2d(self):
        """
            **Checks that the wanted Parameters are correctly generated from the input map2d file**
        """

        # Arrange
        map2d_input = Path('references', 'MS_1AP_REFERENCE.map2d')
        nT_ref = np.array([14]*96)
        nStrands_inGroup_ref = np.array([1] * 96)
        polarities_inGroup_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'polarities_inGroup.txt')).ravel()
        strandToHalfTurn_ref = np.arange(1, 1345)
        strandToGroup_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'strandToGroup.txt')).ravel()
        y_strands_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'y_strands.txt')).ravel()
        x_strands_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'x_strands.txt')).ravel()
        I_strands_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'I_strands.txt')).ravel()
        Bx_strands_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'Bx_strands.txt')).ravel()
        By_strands_ref = np.loadtxt(Path('references', 'getParametersFromMap2d', 'By_strands.txt')).ravel()

        # Act
        nT_gen, nStrands_inGroup_gen, polarities_inGroup_gen, strandToHalfTurn_gen, strandToGroup_gen, x_strands_gen, y_strands_gen, I_strands_gen, Bx_strands_gen, By_strands_gen = \
            ParserMap2dFile(map2dFile=map2d_input).getParametersFromMap2d()

        print('nT:', nT_gen)
        print('nStrands_inGroup_gen:', nStrands_inGroup_gen)
        print('polarities_inGroup_gen:', polarities_inGroup_gen)

        #Assert
        np.testing.assert_allclose(nT_ref, nT_gen)
        np.testing.assert_allclose(nStrands_inGroup_ref, nStrands_inGroup_gen)
        np.testing.assert_allclose(polarities_inGroup_ref, polarities_inGroup_gen)
        np.testing.assert_allclose(strandToHalfTurn_ref, strandToHalfTurn_gen)
        np.testing.assert_allclose(strandToGroup_ref, strandToGroup_gen)
        np.testing.assert_allclose(x_strands_ref, x_strands_gen)
        np.testing.assert_allclose(y_strands_ref, y_strands_gen)
        np.testing.assert_allclose(I_strands_ref, I_strands_gen)
        np.testing.assert_allclose(Bx_strands_ref, Bx_strands_gen)
        np.testing.assert_allclose(By_strands_ref, By_strands_gen)

    def test_modify_map2d_ribbon_cable_only(self):
        """
            **Checks that ParserMap2d generates an array stream from a ROXIE-map2d to the same arrangement of values
            as a reference file (from notebooks) that got modified due to its ribbon properties; for only-ribbon-cables:
            Only ribbon-conductors**
        """

        # Manual written input for the array, that defines the distribution of the conductors in each group of
        # a ribbon-type conductor
        # [No. of Layers, Conductor per Group]
        # Only ribbon-conductors:
        geometry_ribbon_cable_only = [[8,14],[8,14]]*6
        list_flag_ribbon = [True] * 96

        # Get file data
        reference_file_only = Path('references', 'MS_1AP_REFERENCE.map2d')
        input_file_only = Path('input', 'MS_1AP.map2d')

        # Create modified array of the input files
        output_array_only = ParserMap2dFile(map2dFile=input_file_only).modify_map2d_ribbon_cable(
            geometry_ribbon_cable=geometry_ribbon_cable_only, list_flag_ribbon=list_flag_ribbon)

        # Create array (parser-method) of the reference file
        reference_array_only = ParserMap2dFile(map2dFile=reference_file_only).parseRoxieMap2d()

        # Test that the generated and modified array is identical to the reference array
        np.testing.assert_allclose(reference_array_only, output_array_only, rtol=1e-5, atol=0)

    def test_modify_map2d_ribbon_cable_comb(self):
        """
            **Checks that ParserMap2d generates an array stream from a ROXIE-map2d to the same arrangement of values
            as a reference file (from notebooks) that got modified due to its ribbon properties; for semi-ribbon-cables:
            Combination of ribbon-conductors and non-ribbon-conductors (only one value in list-element):**
        """

        # Manual written input for the array, that defines the distribution of the conductors in each group of
        # a ribbon-type conductor
        # [No. of Layers, Conductor per Group]
        geometry_ribbon_cable_comb = [[34,26],[34,26],[34,26],[34,26],[34,26],[34,26],[34,26],[34,26],[34,1],[34,1],[34,1],[34,1],[34,1],[34,1],[34,1],[34,1]]*2
        list_flag_ribbon = [True] * 272 + [False] * 8 + [True] * 272 + [False] * 8

        # Get file data
        reference_file_comb = Path('references', 'MU_REFERENCE.map2d')
        input_file_comb = Path('input', 'MU.map2d')

        # Create modified array of the input files
        output_array_comb = ParserMap2dFile(map2dFile=input_file_comb).modify_map2d_ribbon_cable(
            geometry_ribbon_cable=geometry_ribbon_cable_comb, list_flag_ribbon=list_flag_ribbon)

        # Create array (parser-method) of the reference file
        reference_array_comb = ParserMap2dFile(map2dFile=reference_file_comb).parseRoxieMap2d()

        # Test that the generated and modified array is identical to the reference array
        np.testing.assert_allclose(reference_array_comb, output_array_comb, rtol=1e-5, atol=0)

    def test_modify_map2d_ribbon_cable_different(self):
        """
            **Checks that ParserMap2d generates an array stream from a ROXIE-map2d to the same arrangement of values
            as a reference file (from notebooks) that got modified due to its ribbon properties; for only-ribbon-cables:
            Only ribbon-conductors with different number strands per group**
        """

        # Manual written input for the array, that defines the distribution of the conductors in each group of
        # a ribbon-type conductor
        # [No. of Layers, Conductor per Group]
        # Only ribbon-conductors:
        geometry_ribbon_cable_different = [[15,25],[15,35],[15,20],[15,9]]*4
        list_flag_ribbon = [True] * 240

        # Get file data
        reference_file_different = Path('references', 'MCBYH_1AP_REFERENCE.map2d')
        input_file_different = Path('input', 'MCBYH_1AP.map2d')

        # Create modified array of the input files
        output_array_different = ParserMap2dFile(map2dFile=input_file_different).modify_map2d_ribbon_cable(
            geometry_ribbon_cable=geometry_ribbon_cable_different, list_flag_ribbon=list_flag_ribbon)

        # Create array (parser-method) of the reference file
        reference_array_different = ParserMap2dFile(map2dFile=reference_file_different).parseRoxieMap2d()

        # Test that the generated and modified array is identical to the reference array
        np.testing.assert_allclose(reference_array_different, output_array_different, rtol=1e-5, atol=0)
