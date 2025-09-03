import copy
import datetime
import os
import shutil
from pathlib import Path
from typing import Union
import time

import numpy as np

from steam_pysigma.MainPySIGMA import MainPySIGMA

from steam_sdk.builders.BuilderAPDL_CT import BuilderAPDL_CT
from steam_sdk.builders.BuilderFiQuS import BuilderFiQuS
from steam_sdk.builders.BuilderLEDET import BuilderLEDET
from steam_sdk.builders.BuilderProteCCT import BuilderProteCCT
from steam_sdk.builders.BuilderPyBBQ import BuilderPyBBQ
from steam_sdk.builders.BuilderPySIGMA import BuilderPySIGMA
from steam_sdk.builders.BuilderTFM import BuilderTFM
from steam_sdk.data.DataModelCircuit import DataModelCircuit
from steam_sdk.data.DataModelConductor import DataModelConductor
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.DataRoxieParams import RoxieParams
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.parsers.ParserCsv import find_by_position, find_column_list
from steam_sdk.parsers.ParserFiQuS import ParserFiQuS
from steam_sdk.parsers.ParserLEDET import ParserLEDET, copy_modified_map2d_ribbon_cable, copy_map2d
from steam_sdk.parsers.ParserMap2d import ParserMap2dFile
from steam_sdk.parsers.ParserPSPICE import ParserPSPICE, edit_bias_file, check_bias_file_type, write_time_stimulus_file
from steam_sdk.parsers.ParserProteCCT import ParserProteCCT
from steam_sdk.parsers.ParserPyBBQ import ParserPyBBQ
from steam_sdk.parsers.ParserPySIGMA import ParserPySIGMA
from steam_sdk.parsers.ParserRoxie import ParserRoxie, RoxieList
from steam_sdk.parsers.ParserXYCE import ParserXYCE
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.parsers.utils_ParserCircuits import read_circuit_data_from_model_data
from steam_sdk.plotters import PlotterRoxie
from steam_sdk.plotters.PlotterModel import PlotterModel
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class BuilderModel:
    """
        Class to generate STEAM models, which can be later on written to input files of supported programs
    """

    def __init__(self, file_model_data: str = None, case_model: str = 'magnet', data_settings: DataSettings = None, verbose: bool = False):
        """
        Builder object to generate models for STEAM simulation tools specified by user
        :param file_model_data: path to input yaml file
        :type file_model_data: str
        :param case_model: defines whether it is a magnet, a conductor or a circuit. Default is 'magnet
        :type case_model: str
        :param data_settings: DataSettings object containing all settings, previously read from user specific settings.SYSTEM.yaml file or from a STEAM analysis permanent settings
        :type data_settings: DataSettings
        :param verbose: if true display internal processes (output of status & error messages) for troubleshooting
        :type verbose: bool
        """

        # Unpack arguments
        if file_model_data:
            self.file_model_data: str = file_model_data
        else:
            raise Exception('No file_model_data .yaml input file provided.')
        self.case_model = case_model
        self.settings_dict = data_settings
        self.verbose: bool = verbose

        if self.verbose:
            print(f'case_model: {self.case_model}')
            print('Settings which are not empty:')
            if self.settings_dict is not None:
                for attr in self.settings_dict.__dict__.keys():
                    value = getattr(self.settings_dict, attr)
                    if value is not None:
                        print(f'{attr}: {value}')

        ### Case of a magnet model
        if self.case_model == 'magnet':
            # Initialized
            self.model_data: DataModelMagnet = DataModelMagnet()
            self.roxie_data: RoxieData = RoxieData()
            self.path_input_file = None
            self.path_data = None
            self.path_cadata = None
            self.path_iron = None
            self.path_map2d = None
            self.roxie_params = RoxieParams

            # Load model data from the input .yaml file
            self.loadModelData()

            # Set paths of input files
            self.set_input_paths()


        ### Case of a circuit model
        elif self.case_model == 'circuit':
            # Initialize
            self.circuit_data: DataModelCircuit = DataModelCircuit()

            # Load model data from the input .yaml file
            self.loadModelData()

            # Set paths of input files
            self.set_input_paths()

        ### Case of a conductor model
        elif self.case_model == 'conductor':
            # Initialize
            self.conductor_data: DataModelConductor = DataModelConductor()

            # Load model data from the input .yaml file
            self.loadModelData()

            # Set paths of input files
            self.set_input_paths()
        else:
            raise Exception(f'Selected case {self.case_model} is not supported. Supported cases: circuit, magnet, conductor.')

        # Display time stamp
        if self.verbose:
            print(f'BuilderModel ended. Time stamp: {datetime.datetime.now()}')

    def set_input_paths(self):
        """
            Sets input paths from created DataModel and displays related information
        """
        # TODO: Add test for this method

        # Find folder where the input file is located, which will be used as the "anchor" for all input files
        self.path_input_file = Path(self.file_model_data).parent
        self.path_data = None
        self.path_map2d = None
        self.path_cadata = None
        self.path_iron = None

        if self.case_model == 'magnet':
            # Set a few paths relative to the "anchor" path
            # If input paths are not defined, their value remains to their default None
            # The construct Path(x / y).resolve() allows defining relative paths in the .yaml input file
            if self.model_data.Sources.coil_fromROXIE:
                self.path_data = Path(self.path_input_file / self.model_data.Sources.coil_fromROXIE).resolve()
            if self.model_data.Sources.magnetic_field_fromROXIE:
                self.path_map2d = Path(self.path_input_file / self.model_data.Sources.magnetic_field_fromROXIE).resolve()
            if self.model_data.Sources.conductor_fromROXIE:
                self.path_cadata = Path(self.path_input_file / self.model_data.Sources.conductor_fromROXIE).resolve()
            if self.model_data.Sources.iron_fromROXIE:
                self.path_iron = Path(self.path_input_file / self.model_data.Sources.iron_fromROXIE).resolve()
            if self.model_data.Sources.BH_fromROXIE:
                self.path_bh = str(Path(self.path_input_file / self.model_data.Sources.BH_fromROXIE).resolve())
        elif self.case_model in 'circuit':
            pass  # no paths to assign
        elif self.case_model == 'conductor':
            if self.conductor_data.Sources.magnetic_field_fromROXIE:
                self.path_map2d = Path(self.path_input_file / self.conductor_data.Sources.magnetic_field_fromROXIE).resolve()
        else:
            raise Exception('case_model ({}) no supported'.format(self.case_model))

        # Display defined paths
        if self.verbose:
            print('These paths were set:')
            print('path_input_file: {}'.format(self.path_input_file))
            if self.path_cadata is not None:
                print('path_cadata:     {}'.format(self.path_cadata))
            if self.path_iron is not None:
                print('path_iron:       {}'.format(self.path_iron))
            if self.path_map2d is not None:
                print('path_map2d:      {}'.format(self.path_map2d))

    def loadModelData(self):
        """
            Loads model data from yaml file to model data object
        """
        if not self.file_model_data:
            raise Exception('No .yaml path provided.')

        if self.verbose:
            print(f'Loading {self.file_model_data} to model data object.')

        if self.case_model == 'magnet':
            self.model_data = yaml_to_data(self.file_model_data, DataModelMagnet)
        elif self.case_model == 'circuit':
            self.circuit_data = read_circuit_data_from_model_data(full_path_file_name=self.file_model_data,
                                                                  verbose=self.verbose)
        elif self.case_model == 'conductor':
            # Load yaml keys into DataModelConductor dataclass
            self.conductor_data = yaml_to_data(self.file_model_data, DataModelConductor)
        else:
            raise ValueError('results: case_model must be one of {}.'.format(['magnet', 'circuit', 'conductor']))

    def loadRoxieData(self):
        """
            Apply roxie parser to fetch magnet information for the given magnet and stores in member variable
        """
        if not self.model_data:
            raise Exception('Model data not loaded to object.')

        # TODO: add option to set a default path if no path is provided
        #######################################
        # Alternative if provided path is wrong
        if self.path_iron is not None and not os.path.isfile(self.path_iron):
            print('Cannot find {}, will attempt to proceed without file'.format(self.path_iron))
            self.path_iron = None
        if self.path_data is not None and not os.path.isfile(self.path_data):
            print('Cannot find {}, will attempt to proceed without file'.format(self.path_data))
            self.path_data = None
        if self.path_cadata is not None and not os.path.isfile(self.path_cadata):
            print('Cannot find {}, will attempt to proceed without file'.format(self.path_cadata))
            self.path_cadata = None

        ############################################################
        # Load information from ROXIE input files using ROXIE parser
        roxie_parser = ParserRoxie()
        self.roxie_data = roxie_parser.getData(dir_data=self.path_data, dir_cadata=self.path_cadata, dir_iron=self.path_iron, path_to_yaml_model_data=self.file_model_data)

        # Read these variables from ParserRoxie and assign them to model_data
        RL = RoxieList(self.roxie_data)
        self.roxie_params.x_strands = RL.x_strand
        self.roxie_params.y_strands = RL.y_strand
        self.roxie_params.i_strands = RL.i_strand
        self.roxie_params.strandToHalfTurn = RL.strand_to_halfTurn
        self.roxie_params.strandToGroup = RL.strand_to_group

        # nT (has as many elements as groups. Each element defines the number of half-turns in that group)
        counter_nT = 1
        nT = []
        for i in range(1, len(RL.strand_to_group)):
            if RL.strand_to_halfTurn[i] != RL.strand_to_halfTurn[i - 1] and RL.strand_to_group[i] == RL.strand_to_group[i - 1]:  # counts the number of half-turns in the group by counting non-equal strandsToHalfTurn
                counter_nT += 1
            if RL.strand_to_group[i] != RL.strand_to_group[i - 1] or i == len(RL.strand_to_group) - 1:  # the counted number is stored in the array and the counter restarts
                nT.append(counter_nT)
                counter_nT = 1
        if RL.strand_to_group[-1] != RL.strand_to_group[-2]:  # in case the last element is a single stranded turn
            nT.append(1)
        self.roxie_params.nT = nT

        indexTstop = np.cumsum(nT).tolist()
        indexTstart = [1]
        for i in range(len(nT) - 1):
            indexTstart.extend([indexTstart[i] + nT[i]])
        self.roxie_params.indexTstart = indexTstart
        self.roxie_params.indexTstop = indexTstop

        # nStrands_inGroup (has as many elements as groups. Each element defines the number of strands in the conductor of that group)
        counter_nStrands_inGroup = 1
        nStrands_inGroup = []
        for i in range(1, len(RL.strand_to_group)):
            if RL.strand_to_group[i] == RL.strand_to_group[i-1] and RL.strand_to_halfTurn[i] != RL.strand_to_halfTurn[i-1]:  #the number of equal strandsToHalfTurn are only counted once per group and otherwise resetted
                counter_nStrands_inGroup = 1
            elif RL.strand_to_halfTurn[i] == RL.strand_to_halfTurn[i - 1]:  #counts the number of strands in the group by counting equal strandsToHalfTurn
                counter_nStrands_inGroup += 1
            if RL.strand_to_group[i] != RL.strand_to_group[i - 1] or i == len(RL.strand_to_group) - 1:  #the counted number is stored in the array and the counter restarts
                nStrands_inGroup.append(counter_nStrands_inGroup)
                counter_nStrands_inGroup = 1
        self.roxie_params.nStrands_inGroup = nStrands_inGroup

        # sign_i = lambda x: math.copysign(1, x)
        polarities_inGroup = []
        for i in range(1, len(RL.strand_to_group)):
            if RL.strand_to_group[i] != RL.strand_to_group[i-1] or i == len(RL.strand_to_group) - 1:  #for each group the polarities is stored in the array
                polarities_inGroup.append(float(np.sign(RL.i_strand[i-1])))
        self.roxie_params.polarities_inGroup = polarities_inGroup

    def calc_electrical_order(self, flag_plot: bool = False, verbose: bool = None):
        """
            **Calculates electrical order of each half turn (for multipole magnets) or of each turn (for solenoid and CCT magnets) **
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self

        # Unpack variables
        if self.model_data.GeneralParameters.magnet_type in ['multipole', 'busbar']:
            nT                         = self.roxie_params.nT
            indexTstart                = self.roxie_params.indexTstart
            indexTstop                 = self.roxie_params.indexTstop
            strandToGroup              = self.roxie_params.strandToGroup
            strandToHalfTurn           = self.roxie_params.strandToHalfTurn

        if verbose:
            print('Setting the electrical order')

        # If the key overwrite_electrical_order is defined, the electrical order is
        if self.model_data and len(self.model_data.CoilWindings.electrical_pairs.overwrite_electrical_order) > 0:
            if verbose: print(
                'Electrical order is defined manually based on the input key CoilWindings.electrical_pairs.overwrite_electrical_order')

            el_order_half_turns = self.model_data.CoilWindings.electrical_pairs.overwrite_electrical_order
            # Assign values to the attribute in the model_data dataclass
            self.el_order_half_turns = el_order_half_turns  # TODO assign it to a better structure
            return el_order_half_turns  # stop here the function without calculating the electrical order

        el_order_half_turns = []
        if self.model_data.GeneralParameters.magnet_type in ['multipole', 'busbar']:
            if len(self.model_data.CoilWindings.electrical_pairs.reversed) != len(self.model_data.CoilWindings.electrical_pairs.group_together):
                raise Exception('Length of the vector elPairs_RevElOrder ({}) must be equal to nElPairs={}.'.format(len(self.model_data.CoilWindings.electrical_pairs.reversed), len(self.model_data.CoilWindings.electrical_pairs.group_together)))
            for p in range(len(self.model_data.CoilWindings.electrical_pairs.group_together)):
                if nT[self.model_data.CoilWindings.electrical_pairs.group_together[p][0] - 1] != nT[self.model_data.CoilWindings.electrical_pairs.group_together[p][1] - 1]:
                    raise Exception('Pair of groups defined by the variable elPairs_GroupTogether must have the same number of half-turns.')
                for k in range(nT[self.model_data.CoilWindings.electrical_pairs.group_together[p][0] - 1]):
                    if self.model_data.CoilWindings.electrical_pairs.reversed[p] == 0:
                        el_order_half_turns.append(indexTstart[self.model_data.CoilWindings.electrical_pairs.group_together[p][0] - 1] + k)
                        el_order_half_turns.append(indexTstart[self.model_data.CoilWindings.electrical_pairs.group_together[p][1] - 1] + k)
                    if self.model_data.CoilWindings.electrical_pairs.reversed[p] == 1:
                        el_order_half_turns.append(indexTstop[self.model_data.CoilWindings.electrical_pairs.group_together[p][0] - 1] - k)
                        el_order_half_turns.append(indexTstop[self.model_data.CoilWindings.electrical_pairs.group_together[p][1] - 1] - k)
        elif self.model_data.GeneralParameters.magnet_type in ['solenoid']:
            # nGroupsDefined = len(nT)
            # winding_order_groups = (nGroupsDefined * [0, 1])[:nGroupsDefined]
            # for p in range(nGroupsDefined, 0, -1):
            #     for k in range(nT[p - 1]):
            #         if winding_order_groups[p - 1] == 0:
            #             el_order_half_turns.append(indexTstart[p - 1] + k)
            #         if winding_order_groups[p - 1] == 1:
            #             el_order_half_turns.append(indexTstop[p - 1] - k)
            pass        # electrical order calculated in assignSolenoidValuesWindings method of this class
        elif self.model_data.GeneralParameters.magnet_type in ['CCT_straight']:
            wwns = self.model_data.CoilWindings.CCT_straight.winding_numRowStrands  # number of wires in width direction
            whns = self.model_data.CoilWindings.CCT_straight.winding_numColumnStrands  # number of wires in height direction
            n_turns_formers = self.model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers  # number of turns [-]
            winding_order = self.model_data.CoilWindings.CCT_straight.winding_order
            fqpl_names = [val for val, flag in zip(self.model_data.Quench_Protection.FQPCs.names, self.model_data.Quench_Protection.FQPCs.enabled) if flag]

            # ----- formers' turns -----
            all_turns_magnet = []  # list for all turns of the former
            for former_i in range(len(n_turns_formers)):  # for each former of cct
                all_turns_former = []  # list of lists of lists for actual turns positions
                former_start_offset = former_i * wwns[former_i] * whns[former_i] * n_turns_formers[former_i]  # offset for the first turn on the next former
                for channel_turn in range(n_turns_formers[former_i]):  # for number of turns in each former
                    actual_turns = []  # list to collect turn numbers
                    current_turn = channel_turn + former_start_offset + 1  # start first turn of the fist channel with the former offset
                    for i_w in range(1, wwns[former_i] + 1):  # for each turn in the width direction of the channel
                        for i_h in range(1, whns[former_i] + 1):  # for each turn in the height direction of the channel
                            actual_turns.append(current_turn)
                            current_turn = current_turn + n_turns_formers[former_i]  # next turn is 'above' i.e. in the height direction so add number of turns in the width direction
                    all_turns_former.append(actual_turns)  # collect all turns for the former
                all_turns_magnet.append(all_turns_former)  # collect all turns for the magnet windings
            all_actual_pos = []  # list for regrouped turns, so directly an electrical position index could be used
            for i in range(len(all_turns_magnet[0])):  # get the former index to extract only turns for that former
                positional_turns = []  # list to collect turn numbers in a sequence of positional turns (of length of winding order)
                for all_turns_former in all_turns_magnet:
                    positional_turns.extend(all_turns_former[i])  # put turns in groove number from inner former number and outer former number
                all_actual_pos.append(positional_turns)  # put lists together
            electrical_order = []  # list to put electrical order into
            for el_pos in winding_order:  # for each winding order positional turn
                for actual_pos in all_actual_pos:  # for each positional turn (a list of length of max integer in the winding order)
                    electrical_order.append(actual_pos[el_pos - 1])  # get turn number corresponding to position specified in the winding order (-1 due to 0 based list)

            # ----- fqpls' turns -----
            max_turn = int(np.max(electrical_order))
            for _ in range(len(fqpl_names)):  # for each fqpl
                for _ in range(2):  # for 'go' and 'return' part of fqpl
                    max_turn += 1   # increment by one, this matches fiqus postprocessing
                    electrical_order.append(max_turn)

            el_order_half_turns = electrical_order
        elif self.model_data.GeneralParameters.magnet_type in ['CWS']:
            #el_order_half_turns = self.model_data.Options_FiQuS.cws.postproc.field_map.winding_order
            el_order_half_turns = list(range(1, len(self.model_data.Options_FiQuS.cws.postproc.field_map.winding_order)+1)) # as fiqus already sets the correct electrical order in the 3D map of magnetic field this is a sequential list.
            #el_order_half_turns = self.model_data.CoilWindings.CCT_straight.winding_order
        # elif self.model_data.GeneralParameters.magnet_type in ['Pancake3D']:  # TODO
        # elif self.model_data.GeneralParameters.magnet_type in ['Racetrack']:  # TODO

        # Assign values to the attribute in the model_data dataclass
        self.el_order_half_turns = el_order_half_turns  #TODO assign it to a better structure

        if verbose:
            print('Setting electrical order was successful.')

        if flag_plot:
            PM = PlotterModel(self.roxie_data)
            if self.model_data.GeneralParameters.magnet_type not in ['CCT_straight', 'CWS']:
                PM.plot_electrical_order(el_order_half_turns, self.model_data.CoilWindings.electrical_pairs.group_together, strandToGroup, self.roxie_params.x_strands, self.roxie_params.y_strands, strandToHalfTurn, self.model_data)
        return np.array(el_order_half_turns)

    def buildAPDL_CT(self, sim_name: str, sim_number: Union[int, str], output_path: str, flag_plot_all: bool = False, verbose: bool = None):
        '''
            Write input file for an APDL model of a cos-theta magnet (LBNL model)
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param flag_plot_all: Display figures
            :param verbose: If True, display logging information
        :return:
        '''
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number  # TODO consider instead: sim_suffix = f'_{sim_number}' if sim_number else ''

        # Load model data from the input ROXIE files
        if self.model_data.GeneralParameters.magnet_type in ['multipole']:
            self.loadRoxieData()
        else:
            raise Exception(f'Selected magnet type {sim_name} is not supported for APDL_CT.')

        # Calculate half-turn electrical order
        self.calc_electrical_order(flag_plot=flag_plot_all, verbose=verbose)

        path_file = os.path.join(output_path, f'{self.model_data.GeneralParameters.magnet_name}{sim_suffix}.inp')
        make_folder_if_not_existing(os.path.dirname(path_file))

        roxie_parser = ParserRoxie()
        _ = roxie_parser.getData(dir_data=self.path_data, dir_cadata=self.path_cadata, dir_iron=self.path_iron,
                                 path_to_yaml_model_data=self.file_model_data)
        builder_APDL_CT = BuilderAPDL_CT(model_data=self.model_data, roxieData=roxie_parser.roxieData, verbose=verbose)
        builder_APDL_CT.write_file(full_path_file_name=path_file, verbose=verbose)

        if flag_plot_all:
            PlotterRoxie.plot_all(self.roxie_data)
            PM = PlotterModel(self.roxie_data)
            PM.plot_all(self.model_data)

    def buildFiQuS(self, sim_name: str, sim_number: Union[int, str], output_path: str = None,
                   flag_plot_all: bool = False, verbose: bool = None):
        """
            Building a FiQuS model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param flag_plot_all: Display figures
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if sim_number else ''

        # Load model data from the input ROXIE files
        if self.model_data.GeneralParameters.magnet_type in ['multipole', 'busbar']:
            self.loadRoxieData()
        # Calculate half-turn electrical order
        self.calc_electrical_order(flag_plot=flag_plot_all, verbose=verbose)
        #if library_path != None:
        if self.model_data.GeneralParameters.magnet_type == 'multipole':
            make_folder_if_not_existing(output_path)  # somehow sometimes the output folder does not exist so making sure it is created
            shutil.copyfile(self.path_bh, os.path.join(output_path, 'roxie.bhdata'))
            shutil.copyfile(self.path_map2d, os.path.join(output_path, f"{sim_name}{sim_suffix}_ROXIE_REFERENCE.map2d"))
        elif self.model_data.GeneralParameters.magnet_type == 'CWS' and self.model_data.Options_FiQuS.run.type in ["start_from_yaml", "geometry_only", "geometry_and_mesh"]:
            # copy all conductor files and breps to input folder, if the run type actually is going to need them
            make_folder_if_not_existing(output_path)
            for name in self.model_data.Options_FiQuS.cws.geometry.conductors.file_names + self.model_data.Options_FiQuS.cws.geometry.conductors.file_names_large:
                extension = 'cond'
                source_file = os.path.join(self.path_input_file, f'{name}.{extension}')
                destination_file = os.path.join(output_path, f'{name}.{extension}')
                print(f'Coping {source_file} to {destination_file}')
                shutil.copyfile(source_file, destination_file)
            for name in self.model_data.Options_FiQuS.cws.geometry.formers.file_names + self.model_data.Options_FiQuS.cws.geometry.shells.file_names:   ## TODO add iron file names when propagated to SDK
                extension = 'brep'
                source_file = os.path.join(self.path_input_file, f'{name}.{extension}')
                destination_file = os.path.join(output_path, f'{name}.{extension}')
                print(f'Coping {source_file} to {destination_file}')
                shutil.copyfile(source_file, destination_file)
        elif self.model_data.GeneralParameters.magnet_type == 'CACStrand' and self.model_data.Options_FiQuS.run.type in ["start_from_yaml", "geometry_only", "geometry_and_mesh"]:
            make_folder_if_not_existing(output_path)
            if self.model_data.Options_FiQuS.CACStrand.geometry.io_settings.load.load_from_yaml:
                source_file = os.path.join(self.path_input_file, self.model_data.Options_FiQuS.CACStrand.geometry.io_settings.load.filename)
                destination_file = os.path.join(output_path, self.model_data.Options_FiQuS.CACStrand.geometry.io_settings.load.filename)
                print(f'Coping {source_file} to {destination_file}')
                shutil.copyfile(source_file, destination_file)
        else:
            pass    # for CCT and Pancake3D no bhdata is needed
        builder_FiQuS = BuilderFiQuS(model_data=self.model_data, roxie_data=self.roxie_data, flag_build=True, verbose=verbose)

        # Write output files
        self.parser_FiQuS = ParserFiQuS(builder_FiQuS, verbose=verbose)
        self.parser_FiQuS.writeFiQuS2yaml(output_path=output_path, simulation_name=f'{sim_name}{sim_suffix}', append_str_to_magnet_name='_FiQuS')

        if flag_plot_all:
            PlotterRoxie.plot_all(self.roxie_data)
            PM = PlotterModel(self.roxie_data)
            PM.plot_all(self.model_data)

    def buildLEDET(self, sim_name: str, sim_number: Union[
        int, str], output_path: str, output_path_field_maps: str = None,
                   flag_json: bool = False, flag_plot_all: bool = False, verbose: bool = None):
        """
            Building a LEDET model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder for the LEDET input files (.xlsx, .yaml, .json, .csv)
            :param output_path_field_maps: Output folder for the magnetic field maps used by LEDET
            :param flag_json: When supported by the tool builder, write the model file in .json format as well - used in LEDET at the moment
            :param flag_plot_all: Display figures
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number
        make_folder_if_not_existing(output_path, verbose=verbose)
        if output_path_field_maps == None:
            output_path_field_maps = output_path
        else:
            make_folder_if_not_existing(output_path_field_maps, verbose=verbose)

        if self.case_model == 'magnet':
            magnet_name = sim_name
            suffix_inductance_file = f'_{self.model_data.Options_LEDET.input_generation_options.selfMutualInductanceFileNumber}' if self.model_data.Options_LEDET.input_generation_options.selfMutualInductanceFileNumber else ''
            suffix_map2d_files = f'_{self.model_data.Options_LEDET.field_map_files.fieldMapNumber}' if self.model_data.Options_LEDET.field_map_files.fieldMapNumber else ''

            nameFileSMIC = os.path.join(output_path, f'{magnet_name}_selfMutualInductanceMatrix{suffix_inductance_file}.csv')  # full path of the .csv file with self-mutual inductances to write

            # Load model data from the input ROXIE files
            if self.model_data.GeneralParameters.magnet_type in ['multipole', 'busbar']:
                self.loadRoxieData()
            # Calculate half-turn electrical order
            self.calc_electrical_order(flag_plot=flag_plot_all, verbose=verbose)

            # Copy/edit the ROXIE map2d file
            if self.path_map2d:
                suffix = "_All"
                if self.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == 1:
                    #     # [[...half_turn_length, Ribbon...n_strands],.....]
                    # TODO: geometry when conductor has a combination of ribbon and non-ribbon cables

                    # List of flags that are True is the cable type is "Ribbon"
                    list_flag_ribbon = []
                    for i, cond in enumerate(self.model_data.CoilWindings.conductor_to_group):
                        list_flag_ribbon.append(self.model_data.Conductors[cond - 1].cable.type == 'Ribbon')

                    nT_from_original_map2d, nStrands_inGroup_original_map2d, _, _, _, _, _, _, _, _ =\
                        ParserMap2dFile(map2dFile=self.path_map2d).getParametersFromMap2d(headerLines=self.model_data.Options_LEDET.field_map_files.headerLines)

                    n_groups_original_file = len(nT_from_original_map2d)
                    geometry_ribbon_cable = []

                    for i in range(n_groups_original_file):
                        list = [None, None]
                        list[0] = int(nStrands_inGroup_original_map2d[i])  # layers
                        list[1] = nT_from_original_map2d[
                            i]  # number of half-turns; in case it is not a ribbon cable, it is going to be ignored in the modify-ribbon-cable function
                        geometry_ribbon_cable.append(list)

                    if verbose:
                        print(f'geometry_ribbon_cable: {geometry_ribbon_cable}')

                    file_name_output = copy_modified_map2d_ribbon_cable(magnet_name,
                                                                        self.path_map2d,
                                                                        output_path_field_maps, geometry_ribbon_cable,
                                                                        self.model_data.Options_LEDET.field_map_files.flagIron,
                                                                        self.model_data.Options_LEDET.field_map_files.flagSelfField,
                                                                        list_flag_ribbon,
                                                                        suffix=suffix,
                                                                        suffix_map2d_set=suffix_map2d_files,
                                                                        verbose=verbose)

                elif self.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == 0 or self.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == None:
                    file_name_output = copy_map2d(magnet_name, self.path_map2d, output_path_field_maps,
                                                  self.model_data.Options_LEDET.field_map_files.flagIron,
                                                  self.model_data.Options_LEDET.field_map_files.flagSelfField,
                                                  suffix=suffix,
                                                  suffix_map2d_set=suffix_map2d_files,
                                                  verbose=verbose)

                self.map2d_file_modified = os.path.join(output_path_field_maps, file_name_output)
            else:
                self.map2d_file_modified = None

            # Copy the additional geometry and magnetic field csv file, if defined in the input file
            if self.model_data.Options_LEDET.simulation_3D.sim3D_flag_Import3DGeometry == 1 and self.model_data.Options_LEDET.input_generation_options.flag_copy3DGeometryFile != 0:
                name_geometry_csv_file = f'{magnet_name}_{self.model_data.Options_LEDET.simulation_3D.sim3D_import3DGeometry_modelNumber}.csv'
                input_path_full = os.path.join(self.path_input_file, name_geometry_csv_file)
                output_path_full = os.path.join(output_path, name_geometry_csv_file)
                shutil.copy2(input_path_full, output_path_full)
                if verbose:
                    print(f'File {input_path_full} copied to {output_path_full}.')

            builder_ledet = BuilderLEDET(path_input_file=self.path_input_file, input_model_data=self.model_data,
                                         input_roxie_data=self.roxie_data, input_map2d=self.map2d_file_modified,
                                         smic_write_path=nameFileSMIC, flag_build=True,
                                         flag_plot_all=flag_plot_all, verbose=verbose,
                                         case_model=self.case_model,
                                         el_order_half_turns=self.el_order_half_turns, roxie_param=self.roxie_params)

            # Copy or modify+copy magnet-name_E....map2d files
            number_input_files = len([entry for entry in os.listdir(self.path_input_file) if
                                      os.path.isfile(os.path.join(self.path_input_file, entry))])
            for file in range(number_input_files + 1):
                suffix = f'_E{file}'
                path_map2d_E = os.path.join(self.path_input_file, f'{magnet_name}{suffix}.map2d')
                if os.path.isfile(path_map2d_E):
                    if self.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == 1:
                        copy_modified_map2d_ribbon_cable(magnet_name,
                                                         path_map2d_E,
                                                         output_path_field_maps, geometry_ribbon_cable,
                                                         self.model_data.Options_LEDET.field_map_files.flagIron,
                                                         self.model_data.Options_LEDET.field_map_files.flagSelfField,
                                                         list_flag_ribbon,
                                                         suffix=suffix,
                                                         suffix_map2d_set=suffix_map2d_files,
                                                         verbose=verbose)
                    elif self.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == 0 or self.model_data.Options_LEDET.field_map_files.flag_modify_map2d_ribbon_cable == None:
                        copy_map2d(magnet_name, path_map2d_E, output_path_field_maps,
                                   self.model_data.Options_LEDET.field_map_files.flagIron,
                                   self.model_data.Options_LEDET.field_map_files.flagSelfField,
                                   suffix=suffix,
                                   suffix_map2d_set=suffix_map2d_files,
                                   verbose=verbose)

            # Write output excel file
            parser_ledet = ParserLEDET(builder_ledet)
            nameFileLEDET = os.path.join(output_path, f'{magnet_name}{sim_suffix}.xlsx')  # full path of the LEDET input file to write
            parser_ledet.writeLedet2Excel(full_path_file_name=nameFileLEDET, verbose=verbose)

            # Write output yaml file
            nameFileLedetYaml = os.path.join(output_path, f'{magnet_name}{sim_suffix}.yaml')  # full path of the LEDET input file to write
            parser_ledet.write2yaml(full_path_file_name=nameFileLedetYaml, verbose=verbose)

            # Write output json file
            if flag_json:
                nameFileLedetJson = os.path.join(output_path, f'{magnet_name}{sim_suffix}.json')  # full path of the LEDET input file to write
                parser_ledet.write2json(full_path_file_name=nameFileLedetJson, verbose=verbose)

            if flag_plot_all:
                PlotterRoxie.plot_all(self.roxie_data)
                PM = PlotterModel(self.roxie_data)
                PM.plot_all(self.model_data)

        elif self.case_model == 'conductor':
            conductor_name = sim_name

            suffix_map2d_files = f'_{self.conductor_data.Options_LEDET.field_map_files.fieldMapNumber}' if self.conductor_data.Options_LEDET.field_map_files.fieldMapNumber else ''

            # Copy the ROXIE map2d file, if defined in the input file
            if self.path_map2d:
                suffix = "_All"
                file_name_output = copy_map2d(conductor_name,
                                              self.path_map2d,
                                              output_path_field_maps,
                                              self.conductor_data.Options_LEDET.field_map_files.flagIron,
                                              self.conductor_data.Options_LEDET.field_map_files.flagSelfField,
                                              suffix=suffix,
                                              suffix_map2d_set=suffix_map2d_files,
                                              verbose=verbose)
                self.map2d_file_modified = os.path.join(output_path_field_maps, file_name_output)
            else:
                self.map2d_file_modified = None
                if verbose:
                    print('Map2d file {} not present, hence it will not be copied.'.format(self.path_map2d))

            # Copy the additional geometry and magnetic field csv file, if defined in the input file
            if self.conductor_data.Options_LEDET.simulation_3D.sim3D_flag_Import3DGeometry == 1:
                name_geometry_csv_file = f'{conductor_name}_{self.conductor_data.Options_LEDET.simulation_3D.sim3D_import3DGeometry_modelNumber}.csv'
                input_path_full = os.path.join(self.path_input_file, name_geometry_csv_file)
                output_path_full = os.path.join(output_path, name_geometry_csv_file)
                shutil.copy2(input_path_full, output_path_full)
                if verbose:
                    print(f'File {input_path_full} copied to {output_path_full}.')

            builder_ledet = BuilderLEDET(path_input_file=self.path_input_file, input_model_data=self.conductor_data,
                                         input_map2d=self.map2d_file_modified,
                                         flag_build=True, flag_plot_all=flag_plot_all,
                                         verbose=verbose,
                                         case_model=self.case_model)

            # Write output excel file
            parser_ledet = ParserLEDET(builder_ledet)
            nameFileLEDET = os.path.join(output_path, f'{conductor_name}{sim_suffix}.xlsx')  # full path of the LEDET input file to write
            parser_ledet.writeLedet2Excel(full_path_file_name=nameFileLEDET, verbose=verbose)

            # Write output yaml file
            nameFileLedetYaml = os.path.join(output_path, f'{conductor_name}{sim_suffix}.yaml')  # full path of the LEDET input file to write
            parser_ledet.write2yaml(full_path_file_name=nameFileLedetYaml, verbose=verbose)

            # Write output json file
            if flag_json:
                nameFileLedetJson = os.path.join(output_path, f'{conductor_name}{sim_suffix}.json')  # full path of the LEDET input file to write
                parser_ledet.write2json(full_path_file_name=nameFileLedetJson, verbose=verbose)

        else:
            raise Exception('Case model {} is not supported when building a LEDET model.'.format(self.case_model))

    def buildProteCCT(self, sim_name: str, sim_number: Union[int, str], output_path: str, verbose: bool = None):
        """
            Building a ProteCCT model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number
        make_folder_if_not_existing(output_path, verbose=verbose)

        builder_protecct = BuilderProteCCT(input_model_data=self.model_data, flag_build=True, verbose=verbose)

        # Write output excel file
        parser_protecct = ParserProteCCT(builder_protecct)
        path_file_name = os.path.join(output_path, f'{sim_name}{sim_suffix}.xlsx')  # full path of the ProteCCT input file to write
        parser_protecct.writeProtecct2Excel(full_path_file_name=path_file_name, verbose=verbose)

    def buildPSPICE(self, sim_name: str, sim_number: Union[int, str], output_path: str, verbose: bool = None):
        """
            Build a PSPICE circuit netlist model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number
        make_folder_if_not_existing(output_path, verbose=verbose)

        # Write output .cir file
        parser_pspice = ParserPSPICE(circuit_data=self.circuit_data, path_input=self.path_input_file)
        path_file_name = os.path.join(output_path, f'{sim_name}{sim_suffix}.cir')  # full path of the PSPICE netlist to write
        parser_pspice.write2pspice(full_path_file_name=path_file_name, verbose=verbose)
        if verbose: print(f'Simulation file {path_file_name} generated.')

        # Copy additional files
        parser_pspice.copy_additional_files(output_path=output_path, verbose=verbose)

        # Make sure that the bias-point file is of ".IC" type, i.e. that it can be used to set initial conditions
        if self.circuit_data.BiasPoints.load_bias_points.flag_check_load_bias_files:
            if not os.path.isabs(self.circuit_data.BiasPoints.load_bias_points.file_path):
                full_path_bias_points_file = os.path.join(output_path, self.circuit_data.BiasPoints.load_bias_points.file_path)
            else:
                full_path_bias_points_file = self.circuit_data.BiasPoints.load_bias_points.file_path
            if os.path.isfile(full_path_bias_points_file) and check_bias_file_type(full_path_bias_points_file) == '.NODESET':
                edit_bias_file(path_file=full_path_bias_points_file, edit_file_type='.IC', new_path_file=None)  # Note: new_path_file is not passed and it will be defaulted to None, hence the original file will be edited
                print(f'WARNING. The load-bias-points file {full_path_bias_points_file} was of type ".NODESET" and was edited to make it of type ".IC" so that it can be used to set initial conditions.')

        # Check whether each stimulus file included in the netlist exists. If it doesn't exist, generate such a file with a dummy entry. This action will prevent PSPICE from returning error during runtime.
        if self.circuit_data.Stimuli.flag_check_existence_stimulus_files:
            for file_path in self.circuit_data.Stimuli.stimulus_files:
                if not os.path.isabs(file_path):
                    full_path_stimulus_file = os.path.join(output_path, file_path)
                else:
                    full_path_stimulus_file = file_path
                if not os.path.isfile(full_path_stimulus_file):
                    # Write dummy stimulus file
                    write_time_stimulus_file(path_file=full_path_stimulus_file, dict_signals={'time': [0], 'DUMMY': [0]}, name_time_signal='time')
                    print(f'WARNING. Stimulus file {full_path_stimulus_file} did not exist, and a dummy file was generated.')


    def buildPyBBQ(self, sim_name: str, sim_number: Union[int, str], output_path: str, verbose: bool = None):
        """
            Build a PyBBQ model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number
        make_folder_if_not_existing(output_path, verbose=verbose)

        conductor_name = sim_name  # self.conductor_data.GeneralParameters.conductor_name
        builder_PyBBQ = BuilderPyBBQ(input_model_data=self.conductor_data, flag_build=True, verbose=verbose)

        # Write output yaml file
        parser_PyBBQ = ParserPyBBQ(builder_PyBBQ)
        path_file_name = os.path.join(output_path, f'{conductor_name}{sim_suffix}.yaml')  # full path of the PyBBQ input file to write
        parser_PyBBQ.writePyBBQ2yaml(full_path_file_name=path_file_name, verbose=verbose)

    def buildPySIGMA(self, sim_name: str, sim_number: Union[int, str], output_path: str,
                     flag_plot_all: bool = False, verbose: bool = None):
        """
        Write PySIGMA input files
        :param sim_name: Simulation name that will be used to write the output file
        :type sim_name: str
        :param sim_number: Simulation number or string that will be used to write the output file
        :type sim_number: Union[int, str]
        :param output_path: Output folder
        :type output_path: str
        :param flag_plot_all: Display figures
        :type flag_plot_all: bool
        :param verbose: If True, display logging information
        :type verbose: bool
        :return: Nothing, writes PySIGMA yaml input file and all other required files
        :rtype: None
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number  # TODO DISCUSS
        make_folder_if_not_existing(output_path, verbose=verbose)

        # Load model data from the input ROXIE files
        if self.model_data.GeneralParameters.magnet_type in ['multipole', 'busbar']:
            self.loadRoxieData()
        # Calculate half-turn electrical order
        self.calc_electrical_order(flag_plot=flag_plot_all, verbose=verbose)

        # output_path = os.path.join(self.settings_dict.local_SIGMA_folder, f'{sim_name}{sim_suffix}')

        builder_PySIGMA = BuilderPySIGMA(model_data=self.model_data, roxie_data=self.roxie_data, path_model_folder=self.path_input_file)
        self.parser_SIGMA = ParserPySIGMA(builder_PySIGMA, output_path=output_path)
        self.parser_SIGMA.writeSIGMA2yaml(simulation_name=f'{sim_name}{sim_suffix}')  # TODO DISCUSS
        coordinate_file_path = self.parser_SIGMA.coordinate_file_preprocess(model_data=self.model_data)
        # Call mainPySIGMA which generates the Java files.
        input_yaml_file_path = os.path.join(output_path, f'{sim_name}{sim_suffix}.yaml')  # TODO DISCUSS
        mps = MainPySIGMA(model_folder=output_path)  # TODO DISCUSS
        mps.build(input_yaml_file_path=input_yaml_file_path, input_coordinates_path=coordinate_file_path, results_folder_name='output', settings=self.settings_dict)  # TODO DISCUSS

        if flag_plot_all:
            PlotterRoxie.plot_all(self.roxie_data)
            PM = PlotterModel(self.roxie_data)
            PM.plot_all(self.model_data)

    def buildTFM(self, builderTFM: BuilderTFM = None, output_path: str = None,  local_library_path: str = None,  TFM_inputs = None, magnet_data = None,
                 circuit_data = None, verbose: bool = True, flag_build: bool = True):
        """
            Building a TFM model
        """
        bTFM = copy.deepcopy(builderTFM)
        if (builderTFM == 0) or (builderTFM is None):
            builder_ledet = BuilderLEDET(path_input_file=self.path_input_file, input_model_data=self.model_data,
                                         input_map2d=self.path_map2d, flag_build=True, input_roxie_data=self.roxie_data,
                                         smic_write_path='skip', verbose=verbose)
            builderTFM = BuilderTFM(builder_LEDET=builder_ledet, output_path=output_path,
                                    local_library_path=local_library_path,
                                    TFM_inputs=TFM_inputs, magnet_data=magnet_data, circuit_data=circuit_data,
                                    flag_build=flag_build, verbose=verbose)
            bTFM = builderTFM
        elif (bool(magnet_data.magnet_Shorts)):
            builder_ledet = BuilderLEDET(path_input_file=self.path_input_file, input_model_data=self.model_data,
                                         input_map2d=self.path_map2d, flag_build=True, input_roxie_data=self.roxie_data,
                                         smic_write_path='skip', verbose=verbose)
            _ = BuilderTFM(builder_LEDET=builder_ledet, output_path=output_path,
                                    local_library_path=local_library_path,
                                    TFM_inputs=TFM_inputs, magnet_data=magnet_data, circuit_data=circuit_data,
                                    flag_build=flag_build, verbose=verbose)
        else:
            builderTFM.call_from_existing(magnet_data=magnet_data, circuit_data=circuit_data, output_path=output_path)
            bTFM = builderTFM
        print_nodes = builderTFM.print_nodes
        return bTFM, print_nodes

    def buildXYCE(self, sim_name: str, sim_number: Union[int, str], output_path: str, verbose: bool = None):
        """
            Build a XYCE circuit netlist model
            :param sim_name: Simulation name that will be used to write the output file
            :param sim_number: Simulation number or string that will be used to write the output file
            :param output_path: Output folder
            :param verbose: If True, display logging information
        """
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self
        sim_suffix = f'_{sim_number}' if isinstance(sim_number, int) else sim_number
        make_folder_if_not_existing(output_path, verbose=verbose)


        if self.circuit_data.TFM != None:
            if not self.circuit_data.TFM.skip_TFM:
                TFM = self.circuit_data.TFM
                # Save each element inside TFM which is not Magnet (flags, T, M_IF_PC) inside the GlobalParameters class of circuit_data
                # format: 'flag_PC' = value
                for key, value in TFM.__dict__.items():
                    if key == 'magnets_TFM' or key == 'simulation_type' or value is None: continue
                    if key == 'temperature':
                        if value is not None:
                            T = value
                        else:
                            T = 1.9
                        self.circuit_data.GlobalParameters.global_parameters[key] = T
                    else:
                        self.circuit_data.GlobalParameters.global_parameters[key] = value
                TFM_general = copy.deepcopy(TFM)
                del TFM_general.magnets_TFM  # Taking of the magnets_TFM dictionary from the TFM class in order to pass it to builderTFM

                magnets_TFM = self.circuit_data.TFM.magnets_TFM
                builderTFM = 0
                for key, m_TFM in magnets_TFM.items():
                    # For each magnet_TFM element, retrieves the corresponding yaml file path
                    local_library_path = os.path.join(self.settings_dict.local_library_path,  'magnets', m_TFM.name, 'input')
                    file_model_data_TFM = os.path.join(local_library_path, f'modelData_{m_TFM.name}.yaml')
                    # For each magnet_TFM element, calls BuilderModel to get the data for that specific magnet
                    start = time.time()
                    BM_TFM = BuilderModel(file_model_data=file_model_data_TFM, verbose=verbose)
                    output_path_TFM = os.path.join(output_path, 'TFM_' + key + '.lib')
                    m_TFM.circuit_name = key
                    # For each magnet_TFM element, calls BuildTFM to create the lib file for that magnet, according to the values specified in the circuit yaml file
                    builderTFM, print_nodes = BM_TFM.buildTFM(builderTFM = builderTFM, output_path=output_path_TFM, local_library_path=local_library_path, TFM_inputs=TFM_general, magnet_data=m_TFM,
                                                  circuit_data = self.circuit_data, verbose=verbose)
                    end = time.time()
                    print(f'TFM took {np.round(end-start,2)} s.')
                    # Update the nodes to be printed in the circuit .csd
                    print_variables = self.circuit_data.PostProcess.probe.variables
                    print_variables = [item for item in print_variables if not key.upper() in item]
                    print_variables.extend([item for item in print_nodes if item not in print_variables])
                    self.circuit_data.PostProcess.probe.variables = print_variables
                    # Save the library in which the magnet models have been created
                    if output_path_TFM not in self.circuit_data.Libraries.component_libraries:
                        self.circuit_data.Libraries.component_libraries.append(output_path_TFM)
                    if output_path_TFM not in self.circuit_data.GeneralParameters.additional_files:
                        self.circuit_data.GeneralParameters.additional_files.append(output_path_TFM)

                    for key_TFM, value in TFM_general.__dict__.items():
                        if value is None or key_TFM == 'simulation_type': continue
                        # Add for each magnet the corresponding flags to the netlist parameters in the format  'flag_PC' = 'flag_PC'
                        self.circuit_data.Netlist[key].parameters[key_TFM] = key_TFM

        # Write output .cir file
        parser_xyce = ParserXYCE(circuit_data=self.circuit_data, path_input=self.path_input_file, output_path=output_path)
        path_file_name = os.path.join(output_path, f'{sim_name}{sim_suffix}.cir')# full path of the XYCE netlist to write

        parser_xyce.write2XYCE(path_file_name, flag_resolve_library_paths=True, flag_copy_additional_files=True, verbose=verbose)


    def load_circuit_parameters_from_csv(self, input_file_name: str, selected_circuit_name: str = None, verbose: bool = False):
        '''
            Load circuit parameters from a csv file into a case=circuit object
            :param input_file_name: full path to the csv file
            :param selected_circuit_name: name of the circuit name whose parameters will be loaded
        '''
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self

        # Check that the model case is circuit
        if self.case_model != 'circuit':
            raise Exception(f'This method can only be used for circuit models, but case_model={self.case_model}')

        # TODO: Think on whether this is good to add as a default option
        # if selected_circuit_name is None:
        #     selected_circuit_name = self.circuit_data.GeneralParameters.circuit_name

        circuit_param = find_by_position(input_file_name, 0, selected_circuit_name)  # TODO make it more robust by referring to a key rather than the first column
        # del circuit_param[0]
        param_names = find_column_list(input_file_name)
        # del param_names[0]
        dict_circuit = {k: v for k, v in zip(param_names, circuit_param)}

        for key, value in dict_circuit.items():
            if key in self.circuit_data.GlobalParameters.global_parameters:
                if self.circuit_data.GlobalParameters.global_parameters[key] != value:
                    if verbose:
                        print(f'Circuit {self.circuit_data.GeneralParameters.circuit_name}: Value of parameter {key} was changed from {self.circuit_data.GlobalParameters.global_parameters[key]} to {value}')
                    self.circuit_data.GlobalParameters.global_parameters[key] = value


