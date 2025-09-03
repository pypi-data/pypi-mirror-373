import os
import numpy as np
import pandas as pd
import math
from pathlib import Path
from typing import Union


class ParserMap2dFile:
    """
    Class for parsing map2d files
    """

    def __init__(
            self,
            map2dFile: Path,
            verbose: bool = True
    ):
        """
            :param map2dFile: path of map2dFile containing the content to parse
        """
        self.verbose = verbose
        # Open map2dfile
        with open(map2dFile, "r") as f:
            fileContent = f.read()
        # Split content of file in rows
        self.fileContentByRow = fileContent.split("\n")

    def parseRoxieMap2d(self, headerLines: int = 1):
        """
            **Generates array-stream of values of map2dFile**
            :param headerLines: which index the header line is at - will start to read after that
        """

        # Create array-matrix to fill in with the values of the file
        output_matrix = np.full((len(self.fileContentByRow) - headerLines - 2, 10), None, dtype=float)

        # Assign values to the matrix row by row
        for index, rowContent in enumerate(self.fileContentByRow):
            if index > headerLines and rowContent:  # without header
                row = rowContent.split()
                output_array = np.array([])  # create temp. array
                output_array = np.append(output_array, int(row[0]))  # strands to groups
                output_array = np.append(output_array, int(row[1]))  # strands to halfturn
                output_array = np.append(output_array, float(row[2]))  # idx
                output_array = np.append(output_array, float(row[3])/1000)  # x_strands in [m]
                output_array = np.append(output_array, float(row[4])/1000)  # y_strands in [m]
                output_array = np.append(output_array, float(row[5]))  # Bx
                output_array = np.append(output_array, float(row[6]))  # By
                output_array = np.append(output_array, float(row[7])/1000000)  # Area in [m^2]
                output_array = np.append(output_array, float(row[8]))  # I_strands
                output_array = np.append(output_array, float(row[9]))  # fill factor
                output_matrix[index-headerLines-1] = output_array  # assign into matrix

        return output_matrix

    def getParametersFromMap2d(self, headerLines: int = 1):
        """
            Load auxiliary parameters to self.Auxiliary parameters using magnetic field from ROXIE
            :param headerLines: which index the header line is at - will start to read after that
            :return param_dict: return dictionary with parameter names as keys and content as values
        """

        strandToGroup = np.array([])
        strandToHalfTurn = np.array([])
        idx, x_strands, y_strands, Bx, By, Area, I_strands, fillFactor = ([],) * 8

        for index, rowContent in enumerate(self.fileContentByRow):
            if index > headerLines and rowContent:
                row = rowContent.split()
                strandToGroup = np.hstack([strandToGroup, int(row[0])])
                strandToHalfTurn = np.hstack([strandToHalfTurn, int(row[1])])
                # idx = np.hstack([idx, float(row[2])])
                x_strands = np.hstack([x_strands, float(row[3]) / 1000])  # in [m]
                y_strands = np.hstack([y_strands, float(row[4]) / 1000])  # in [m]
                Bx = np.hstack([Bx, float(row[5])])
                By = np.hstack([By, float(row[6])])
                # Area = np.hstack([Area, float(row[7])])
                I_strands = np.hstack([I_strands, float(row[8])])
                # fillFactor = np.hstack([fillFactor, float(row[9])])

        strandToHalfTurn = np.int_(strandToHalfTurn)
        strandToGroup = np.int_(strandToGroup)

        # nT (has as many elements as groups. Each element defines the number of half-turns in that group)
        counter_nT = 1
        nT = []

        for i in range(1, len(strandToGroup)):
            if strandToHalfTurn[i] != strandToHalfTurn[i-1] and strandToGroup[i] == strandToGroup[i-1]: #counts the number of half-turns in the group by counting non-equal strandsToHalfTurn
                counter_nT += 1
            if strandToGroup[i] != strandToGroup[i-1] or i == len(strandToGroup) - 1: #the counted number is stored in the array and the counter restarts
                nT.append(counter_nT)
                counter_nT = 1

        # nStrands_inGroup (has as many elements as groups. Each element defines the number of strands in the conductor of that group)
        counter_nStrands_inGroup = 1
        nStrands_inGroup = []

        for i in range(1, len(strandToGroup)):
            if strandToGroup[i] == strandToGroup[i-1] and strandToHalfTurn[i] != strandToHalfTurn[i-1]:  #the number of equal strandsToHalfTurn are only counted once per group and otherwise resetted
                counter_nStrands_inGroup = 1
            elif strandToHalfTurn[i] == strandToHalfTurn[i - 1]:  #counts the number of strands in the group by counting equal strandsToHalfTurn
                counter_nStrands_inGroup += 1
            if strandToGroup[i] != strandToGroup[i - 1] or i == len(strandToGroup) - 1:  #the counted number is stored in the array and the counter restarts
                nStrands_inGroup.append(counter_nStrands_inGroup)
                counter_nStrands_inGroup = 1

        # I_strands (has as many elements as groups. Each element defines the polarity of the current in the conductor)
        sign = lambda x: math.copysign(1, x)
        polarities_inGroup = []

        for i in range(1, len(strandToGroup)):
            if strandToGroup[i] != strandToGroup[i-1] or i == len(strandToGroup) - 1:  #for each group the polarities is stored in the array
                polarities_inGroup.append(sign(I_strands[i-1]))

         # TODO: Check that the number of strands is the same as defined in the  model input .yaml file

        # print('nT:', nT)
        # print('nStrands_inGroup:', nStrands_inGroup)
        # print('polarities_inGroup:', polarities_inGroup)
        # print('strandToHalfTurn:', strandToHalfTurn)
        # print('strandToGroup:', strandToGroup)
        # print('x_strands:', x_strands)
        # print('y_strands:', y_strands)
        # print('I_strands:', I_strands)

        return nT, nStrands_inGroup, polarities_inGroup, strandToHalfTurn, strandToGroup, x_strands, y_strands, I_strands, Bx, By

        # typeWindings = DictionaryLEDET.lookupWindings(self.DataModelMagnet.Options_LEDET.input_generation_options.flag_typeWindings)
        # # Average half-turn positions
        # nHalfTurns = int(np.max(strandToHalfTurn))
        # x_ave, y_ave = [], []
        # for ht in range(1, nHalfTurns + 1):
        #     x_ave = np.hstack([x_ave, np.mean(x[np.where(strandToHalfTurn == ht)])])
        #     y_ave = np.hstack([y_ave, np.mean(y[np.where(strandToHalfTurn == ht)])])
        #
        # # Average group positions
        # x_ave_group, y_ave_group = [], []
        # nGroups = int(np.max(strandToGroup))
        # for g in range(1, nGroups + 1):
        #     x_ave_group = np.hstack([x_ave_group, np.mean(x[np.where(strandToGroup == g)])])
        #     y_ave_group = np.hstack([y_ave_group, np.mean(y[np.where(strandToGroup == g)])])

        # if typeWindings == 'multipole':
        #     # Define the magnetic coil
        #     definedMagneticCoil = MagneticCoil.MagneticCoil()
        #     xPos, yPos, iPos, xBarePos, yBarePos, xS, yS, iS = \
        #         MagneticCoil.MagneticCoil()(fileNameData, fileNameCadata, verbose=verbose)
        #     MagnetGeo = MagnetGeometry(xPos, yPos, iPos, xBarePos, yBarePos, xS, yS, iS, x, y, x_ave, y_ave,
        #                                x_ave_group, y_ave_group)

        # Reference current taken as the current in the first conductor appearing in the ROXIE .data file
        # if self.DataModelMagnet.Conductor.type.conductor_type == 'ribbon':
        #     print('Ribbon-cable conductor with {} strands selected.'.format(
        #         self.yaml_conductor_dict_leaves['n_strands_in_ribbon']))
        #     self.Magnet.Options.Iref = definedMagneticCoil.blockParametersList[0].current / \
        #                                self.yaml_conductor_dict_leaves['n_strands_in_ribbon']
        # else:
        #     self.Magnet.Options.Iref = definedMagneticCoil.blockParametersList[0].current

    def modify_map2d_ribbon_cable(self, geometry_ribbon_cable: list, list_flag_ribbon: list):
        """
            **Edit (put values at their correct position) the current ROXIE field map due to its ribbon-cable properties**
            :param geometry_ribbon_cable: defines the distribution (Number of Layers) in the conductors (half turns) of each group
             of a ribbon-type conductor -> [No. of Layers, Conductor per Group]
            :param list_flag_ribbon: list of flags defining ribbon groups
            :return NewMap2d: return modified array-matrix with values now at the correct position like the ribbon-characteristcs
        """

        # Read file and get array-matrix-stream
        output_array_old = self.parseRoxieMap2d()

        # Create new array(matrix) with same properties as input array to assign values to its correct position
        NewMap2d = np.full((len(output_array_old), 10), None, dtype=float)

        # Reorder values according to Arr_Ribbon_Dist
        # initialize counters
        counter_strands = 0
        counter_halfTurns = 0
        SumLayers = 0

        for k in range(len(geometry_ribbon_cable)):  # goes through each group of Arr_Ribbon_Dist, that defines each group--> [No. of Layers, Conductor per Group]
            for j in range(geometry_ribbon_cable[k][0]):  # goes through number of layers of each conductor
                if list_flag_ribbon[SumLayers]:  # groups
                    for i in range(geometry_ribbon_cable[k][1]):  # goes through each conductor (half turn) of group
                        fc = output_array_old[j + i * geometry_ribbon_cable[k][0] + counter_strands]
                        NewMap2d[i + j * geometry_ribbon_cable[k][1] + counter_strands, :] = fc
                        NewMap2d[i + j * geometry_ribbon_cable[k][1] + counter_strands, 0] = j + SumLayers + 1  # groups
                        NewMap2d[i + j * geometry_ribbon_cable[k][1] + counter_strands, 1] = 1 + counter_halfTurns  # half-turns
                        NewMap2d[i + j * geometry_ribbon_cable[k][1] + counter_strands, 2] = 1 + i + j * geometry_ribbon_cable[k][1] + counter_strands  # strands
                        counter_halfTurns = counter_halfTurns+1
                else:  # special case when the cable is not a ribbon cable
                    fc = output_array_old[j+counter_strands]
                    NewMap2d[counter_strands+j, :] = fc
                    NewMap2d[counter_strands+j, 0] = SumLayers + 1  # groups
                    NewMap2d[counter_strands+j, 1] = counter_halfTurns + 1  # half-turns
                    # no need to correct the strands
            if list_flag_ribbon[SumLayers]:  # groups
                counter_strands = counter_strands + geometry_ribbon_cable[k][0] * geometry_ribbon_cable[k][1]
                SumLayers = SumLayers + geometry_ribbon_cable[k][0]
            else:  # special case when the cable is not a ribbon cable
                counter_strands = counter_strands + geometry_ribbon_cable[k][0]
                counter_halfTurns = counter_halfTurns+1
                SumLayers = SumLayers + 1

        return NewMap2d


class ParserMap2dData:
    """
    Class for parsing map2d data
    """
    def __init__(
            self,
            map2d_input: Union[np.ndarray, Path],
            output_folder_path: Path,
            physical_quantity: str,
            verbose: bool = True
    ):
        """
            :param map2d_input: matrix or magnet ROXIE map2d file path
        """
        self.physical_quantities_abbreviations =\
            {'magnetic_flux_density': ('BX/T', 'BY/T'),
             'temperature':           ('T/K', '-')}
        self.physical_quantity = physical_quantity
        if self.physical_quantity not in self.physical_quantities_abbreviations:
            raise ValueError('Physical quantity not yet supported.')

        self.map2d_input = map2d_input
        self.output_folder_path = output_folder_path
        self.new_file_name = None
        self.verbose = verbose

        self.formatted_headline = "{0:>5}{1:>8}{2:>7}{3:>12}{4:>13}{5:>8}{6:>11}{7:>16}{8:>8}{9:>10}\n\n"
        self.formatted_content = "{0:>6}{1:>6}{2:>7}{3:>13}{4:>13}{5:>11}{6:>11}{7:>11}{8:>9}{9:>8}\n"
        self.map2d_headline_names = ['BL.', 'COND.', 'NO.', 'X-POS/MM', 'Y-POS/MM'] +\
                                    [abbr for abbr in self.physical_quantities_abbreviations[self.physical_quantity]] +\
                                    ['AREA/MM**2', 'CURRENT', 'FILL FAC.']
        self.df_new = pd.DataFrame(columns=self.map2d_headline_names)

        if isinstance(self.map2d_input, Path):
            self.df_reference = pd.read_csv(self.map2d_input, sep=r"\s{2,}|(?<=2) |(?<=T) ", engine='python', usecols=self.map2d_headline_names)

    def check_coordinates_consistency(self, coords: pd.DataFrame):
        """
        Checks that the coordinates at which the quantity is evaluated are the same as in ROXIE map2d
        :param coords: x and y coordinates to check
        :return:
        """
        x_tol, y_tol = 1e-10, 1e-10
        x_ref, y_ref = self.df_reference['X-POS/MM'] / 1000, self.df_reference['Y-POS/MM'] / 1000

        if ((x_ref - coords['x']).abs().max() < x_tol) and ((y_ref - coords['y']).abs().max() < y_tol):
            print("All dataframes have the same x and y coordinates.")
        else:
            raise ValueError("Error: Not all dataframes have the same x and y coordinates. Can't compare map2ds!")

    def create_map2d_from_dataframe(self):
        """
        Create map2d file from a data frame
        """
        # Create new map2d
        with open(os.path.join(self.output_folder_path, self.new_file_name), 'w') as file:
            file.write(self.formatted_headline.format(*self.df_new.columns))
            content = [self.formatted_content.format(int(row[self.map2d_headline_names[0]]),  # bl
                                                     int(row[self.map2d_headline_names[1]]),  # cond
                                                     int(row[self.map2d_headline_names[2]]),  # no
                                                     f"{row[self.map2d_headline_names[3]]:.4f}",  # x
                                                     f"{row[self.map2d_headline_names[4]]:.4f}",  # y
                                                     f"{row[self.map2d_headline_names[5]]:.4f}",  # pq_x
                                                     f"{row[self.map2d_headline_names[6]]:.4f}",  # pq_y
                                                     f"{row[self.map2d_headline_names[7]]:.4f}",  # area
                                                     f"{row[self.map2d_headline_names[8]]:.2f}",  # curr
                                                     f"{row[self.map2d_headline_names[9]]:.4f}")  # fill_fac
                       for _, row in self.df_new.iterrows()]
            file.writelines(content)

        if self.verbose:
            print(f'File {self.new_file_name} saved to {self.output_folder_path}.')

    def create_map2d_file_from_matrix(self, file_name: str):
        """
        Create map2d file from a data frame
        """
        if not isinstance(self.map2d_input, np.ndarray):
            raise ValueError('The class attribute map2d_input needs to be a numpy matrix.')

        self.df_new[self.df_new.columns] = self.map2d_input
        self.new_file_name = file_name
        self.create_map2d_from_dataframe()

    def create_map2d_file_from_SIGMA(self, results_path: Path, new_file_name: str, check_coordinates: bool = False):
        """
        Create map2d file from SIGMA output
        """
        if not isinstance(self.map2d_input, Path):
            raise ValueError('The class attribute map2d_input needs to be a Path to the ROXIE reference map2d file.')

        if self.physical_quantity == 'magnetic_flux_density':
            data_frames = {}
            for new_file_name, var in zip(["mf.Bx.txt", "mf.By.txt"], ['Bx', 'By']):
                with open(os.path.join(results_path, new_file_name)) as file:
                    lines = [line.strip().split() for line in file if "%" not in line]
                data_frames[var] = pd.DataFrame(lines, columns=["x", "y", "B"])
                data_frames[var] = data_frames[var].apply(pd.to_numeric, errors='coerce')

            if check_coordinates:
                self.check_coordinates_consistency(coords=data_frames['Bx'].loc[:, ['x', 'y']])
                self.check_coordinates_consistency(coords=data_frames['By'].loc[:, ['x', 'y']])

            self.df_new[self.df_new.columns] = self.df_reference[self.df_reference.columns]
            self.df_new[self.physical_quantities_abbreviations[self.physical_quantity][0]] = data_frames['Bx']['B']
            self.df_new[self.physical_quantities_abbreviations[self.physical_quantity][1]] = data_frames['By']['B']
            self.new_file_name = new_file_name
            self.create_map2d_from_dataframe()

    def create_map2d_file_from_FiQuS(self, results_path: Path, new_file_name: str):
        """
        Create map2d file from FiQuS output
        """
        if not isinstance(self.map2d_input, Path):
            raise ValueError('The class attribute map2d_input needs to be a Path to the ROXIE reference map2d file.')

        if self.physical_quantity == 'magnetic_flux_density':
            self.df_new = pd.read_csv(os.path.join(results_path, os.path.basename(self.output_folder_path)),
                                      sep=r"\s{2,}|(?<=2) |(?<=T) ", engine='python', usecols=self.map2d_headline_names)
            self.new_file_name = new_file_name
            self.create_map2d_from_dataframe()
