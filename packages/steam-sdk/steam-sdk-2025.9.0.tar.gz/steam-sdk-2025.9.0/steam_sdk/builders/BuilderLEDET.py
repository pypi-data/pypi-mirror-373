import csv
import os
from dataclasses import asdict
from operator import itemgetter
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from steam_sdk.builders.SelfMutualInductanceCalculation import SelfMutualInductanceCalculation
from steam_sdk.builders.Solenoids import Solenoid_magnet
from steam_sdk.builders.geometricFunctions import close_pairs_ckdtree
from steam_sdk.data import DataModelMagnet, DataModelConductor
from steam_sdk.data import DictionaryLEDET
from steam_sdk.data.DataLEDET import LEDETInputs, LEDETOptions, LEDETPlots, LEDETVariables, LEDETAuxiliary
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.TemplateLEDET import get_template_LEDET_inputs_sheet, get_template_LEDET_options_sheet, \
    get_template_LEDET_plots_sheet, get_template_LEDET_variables_sheet
from steam_sdk.parsers.ParserRoxie import ParserRoxie
from steam_sdk.plotters.PlotterModel import PlotterModel



class BuilderLEDET:
    """
        Class to generate LEDET models
    """

    def __init__(self, path_input_file: Path = None, input_model_data=None,
                 input_roxie_data: RoxieData = None, input_map2d: str = None,
                 case_model: str = 'magnet',
                 flag_build: bool = True, flag_plot_all: bool = False,
                 verbose: bool = True, smic_write_path: str = '',
                 el_order_half_turns: List[float] = None, roxie_param = None):
        """
            Object is initialized by defining LEDET variable structure and default parameter descriptions.
            Optionally, the argument model_data can be passed to read the variables of a BuilderModel object.
            If flagInstantBuild is set to True, the LEDET input file is generated.
            If verbose is set to True, additional information will be displayed.
            case_model is a string defining the type of model to build (magnet or conductor)
        """

        # Initialize the model data structure.
        # Note: Different model types (defined by case_model) require a different data structure
        if case_model == 'magnet':
            self.model_data: DataModelMagnet = input_model_data
        elif case_model == 'conductor':
            self.model_data: DataModelConductor = input_model_data
        else:
            raise Exception('Case model {} is not supported when building a LEDET model.'.format(case_model))

        self.verbose: bool = verbose
        self.path_input_file: Path = path_input_file
        self.roxie_data: RoxieData = input_roxie_data
        self.input_map2d = input_map2d
        self.case_model = case_model
        self.flag_build = flag_build
        self.flag_plot_all = flag_plot_all

        # Data structures
        self.Inputs = LEDETInputs()
        self.Options = LEDETOptions()
        self.Plots = LEDETPlots()
        self.Variables = LEDETVariables()
        self.Auxiliary = LEDETAuxiliary()

        self.descriptionsInputs = {}
        self.descriptionsOptions = {}
        self.descriptionsPlots = {}
        self.descriptionsVariables = {}
        self.sectionTitles = {}

        # Misc
        self.smic_write_path: str = smic_write_path
        self.enableConductorResistanceFraction = False
        self.solenoid_layers = []
        self.nT_solenoids = []
        # Load and set the variable descriptions
        self.loadDefaultVariableDescriptions()

        if self.case_model == 'magnet':
            if (not self.model_data or not self.roxie_data) and flag_build:
                raise Exception('Cannot build model without providing DataModelMagnet and RoxieData')

            if flag_build:
                # Add method to translate all LEDET parameters from model_data to LEDET dataclasses
                self.translateModelDataToLEDET()  # TODO: fix this method (it doesn't pass the test_readFromExcel() test)

                # Find winding geometry set in the input file
                self.loadTypeWindings()
                type_windings = DictionaryLEDET.lookupWindings(self.Options.flag_typeWindings, mode='ledet2data')

                # Find STEAM Material Properties set in the input file
                self.loadMatProSet()

                # Read geometry information
                if self.input_map2d:
                    # self.get_roxie_param(roxie_param)
                    # # Read ROXIE-generated .map2d file, load some conductor parameters, and calculate other parameters
                    self.loadParametersFromMap2dInRoxieParser(path_map2d=self.input_map2d, flag_plot=self.flag_plot_all)
                else:
                    if verbose: print('Map2d file not defined. Some geometry parameters will be read from the input yaml file.')
                    self.loadParametersFromDataModel()

                # Load conductor data from DataModelMagnet keys
                if self.model_data.GeneralParameters.magnet_type in ['multipole', 'busbar']:
                    self.loadConductorData()

                # Set electrical order of the half-turns
                self.set_electrical_order(el_order_half_turns)
                # self.calcElectricalOrder(flag_plot=self.flag_plot_all)

                # Calculate thermal connections, i.e. pairs of half-turns that are in thermal contact
                if type_windings in ['multipole', 'busbar', 'CCT_straight', 'CWS']:        # for solenoid type thermal connections are set after assigning solenoid values below
                    self.setThermalConnections()

                # Add thermal connections which where manually set
                if type_windings not in ['CCT_straight', 'CWS']:  # avoid this step for CCT_straight as this reorders the thermal connections and creates issue for fqpls connection
                    self.addThermalConnections()
                else:
                    if self.Auxiliary.iContactAlongHeight_pairs_to_add or self.Auxiliary.iContactAlongWidth_pairs_to_add:   # only if any of these are specified
                        self.addThermalConnectionsCCT()

                # Remove thermal connections which where manually set
                self.removeThermalConnections(flag_plot=self.flag_plot_all)

                # If needed, convert QH parameters from strings to integers
                self.convert_QH_parameters()

                # Calculate self-mutual inductances between magnet coil sections and turns
                if self.Auxiliary.flag_calculate_inductance:
                    self.calculateSelfMutualInductance(csv_write_path=self.smic_write_path)
                else:
                    self.setSelfMutualInductances()

                if self.model_data.GeneralParameters.magnet_type in ['CWS']:
                    self.setSelfMutualInductances()  # needs to be called before assignCCTValuesWindings as assignCCTValuesWindings needs to overwrite HalfTurnToInductanceBlock
                    self.assignCWSValuesWindings()
                    self.loadConductorData()    # this needs to be called here for CCT after assigning CCT values for windings
                if self.model_data.GeneralParameters.magnet_type in ['CCT_straight']:
                    self.setSelfMutualInductances()  # needs to be called before assignCCTValuesWindings as assignCCTValuesWindings needs to overwrite HalfTurnToInductanceBlock
                    self.assignCCTValuesWindings()
                    self.loadConductorData()    # this needs to be called here for CCT after assigning CCT values for windings
                    #self.assignCCTTurnsRefinement()

                if self.model_data.GeneralParameters.magnet_type == 'solenoid':
                    self.assignSolenoidValuesWindings()
                    self.loadConductorData()
                    self.setThermalConnections()

        elif self.case_model == 'conductor':
            if not self.model_data and flag_build:
                raise Exception('Cannot build model without providing DataModelConductor')

            if flag_build:
                # Add method to translate all LEDET parameters from model_data to LEDET dataclasses
                self.translateModelDataToLEDET()
                self.Options.flag_typeWindings = DictionaryLEDET.lookupWindings('busbar', mode='data2ledet')

                # Find STEAM Material Properties set in the input file
                self.loadMatProSet()

                # Load conductor data from DataModelConductor keys
                self.loadConductorData(overwrite_conductor_to_group = [1])

                # Assign default values to LEDET variables defining coil windings parameters
                self.assignDefaultValuesWindings()

                # If needed, convert QH parameters from strings to integers
                self.convert_QH_parameters()

    def loadDefaultVariableDescriptions(self):
        """
            **Loads and sets the LEDET descriptions**

            Function to load and set the descriptions of LEDET parameters directly from the TemplateLEDET() class

            :return: None
        """

        # Import templates for LEDET input file sheets
        template_LEDET_inputs_sheet    = get_template_LEDET_inputs_sheet()
        template_LEDET_options_sheet   = get_template_LEDET_options_sheet()
        template_LEDET_plots_sheet     = get_template_LEDET_plots_sheet()
        template_LEDET_variables_sheet = get_template_LEDET_variables_sheet()

        descriptionsInputs    = {inner_list[0]: inner_list[2] for inner_list in template_LEDET_inputs_sheet}
        descriptionsOptions   = {inner_list[0]: inner_list[2] for inner_list in template_LEDET_options_sheet}
        descriptionsPlots     = {inner_list[0]: inner_list[2] for inner_list in template_LEDET_plots_sheet}
        descriptionsVariables = {inner_list[0]: inner_list[2] for inner_list in template_LEDET_variables_sheet}

        self.descriptionsInputs, self.descriptionsOptions, self.descriptionsPlots, self.descriptionsVariables = descriptionsInputs, descriptionsOptions, descriptionsPlots, descriptionsVariables

    def loadParametersFromMap2dInRoxieParser(self, path_map2d: Path =None, flag_plot: bool = False):
        """
            ** Load auxiliary parameters to self.Inputs and self.Auxiliary parameters using map2d file from ROXIE **

            :param path_map2d: Input .map2d file. Note: By default, read the .map2d file defined in the yaml input file
            :type path_map2d: Path

            :return: None
        """
        pR = ParserRoxie()
        (nT, nStrands_inGroup_ROXIE, polarities_inGroup, strandToHalfTurn, strandToGroup, indexTstart, indexTstop,
         x_strands, y_strands, I_strands, Bx, By) = pR.loadParametersFromMap2d(model_data=self.model_data,
                                                                       path_input_file=self.path_input_file,
                                                                    path_map2d=path_map2d)

        self.setAttribute(self.Inputs,    'nT', nT)
        self.setAttribute(self.Auxiliary, 'nStrands_inGroup_ROXIE', nStrands_inGroup_ROXIE)
        self.setAttribute(self.Inputs,    'polarities_inGroup', polarities_inGroup)
        self.setAttribute(self.Auxiliary, 'strandToHalfTurn', strandToHalfTurn)
        self.setAttribute(self.Auxiliary, 'strandToGroup', strandToGroup)
        self.setAttribute(self.Auxiliary, 'indexTstart', indexTstart)
        self.setAttribute(self.Auxiliary, 'indexTstop', indexTstop)
        self.setAttribute(self.Auxiliary, 'x_strands', x_strands)
        self.setAttribute(self.Auxiliary, 'y_strands', y_strands)
        self.setAttribute(self.Auxiliary, 'I_strands', I_strands)
        self.setAttribute(self.Auxiliary, 'Bx', Bx)
        self.setAttribute(self.Auxiliary, 'By', By)

        if flag_plot:
            PM = PlotterModel(self.roxie_data)
            PM.plot_conductor_numbering(self.model_data, strandToGroup, strandToHalfTurn, polarities_inGroup, x_strands, y_strands)

    def get_roxie_param(self, roxie_param=None, flag_plot: bool = False):
        """
            ** Load auxiliary parameters to self.Inputs and self.Auxiliary parameters using map2d file from ROXIE **

            :param roxie_param: Dictionary with ROXIE-derived coil parameters
            :type roxie_param: Dict

            :return: None
        """
        self.setAttribute(self.Inputs,    'nT', np.array(roxie_param['nT']))
        self.setAttribute(self.Auxiliary, 'nStrands_inGroup_ROXIE', roxie_param['nStrands_inGroup'])
        self.setAttribute(self.Inputs,    'polarities_inGroup', roxie_param['polarities_inGroup'])
        self.setAttribute(self.Auxiliary, 'strandToHalfTurn', np.int_(roxie_param['strandToHalfTurn']))
        self.setAttribute(self.Auxiliary, 'strandToGroup', np.int_(roxie_param['strandToGroup']))
        self.setAttribute(self.Auxiliary, 'indexTstart', roxie_param['indexTstart'])
        self.setAttribute(self.Auxiliary, 'indexTstop', roxie_param['indexTstop'])
        self.setAttribute(self.Auxiliary, 'x_strands', np.array(roxie_param['x_strands']))
        self.setAttribute(self.Auxiliary, 'y_strands', np.array(roxie_param['y_strands']))
        self.setAttribute(self.Auxiliary, 'I_strands', np.array(roxie_param['I_strands']))

        if flag_plot:
            PM = PlotterModel(self.roxie_data)
            PM.plot_conductor_numbering(self.model_data, roxie_param['strandToGroup'], roxie_param['strandToHalfTurn'], roxie_param['polarities_inGroup'], roxie_param['x_strands'], roxie_param['y_strands'])

    def loadParametersFromDataModel(self):
        '''
            ** Load auxiliary parameters to self.Inputs parameters using input .yaml file **
            :return: None
        '''
        # Assign key values from the DataModel keys (originally defined in the input yaml file)
        nT = self.model_data.CoilWindings.n_half_turn_in_group
        self.setAttribute(self.Inputs,    'nT', nT)
        self.setAttribute(self.Inputs,    'polarities_inGroup', self.model_data.CoilWindings.polarities_in_group)

        # Calculate auxiliary variables and set their values
        indexTstop = np.cumsum(nT).tolist()
        indexTstart = [1]
        for i in range(len(nT) - 1):
            indexTstart.extend([indexTstart[i] + nT[i]])
        self.setAttribute(self.Auxiliary, 'indexTstart', indexTstart)
        self.setAttribute(self.Auxiliary, 'indexTstop', indexTstop)

        # To make sure these variables are present and not used afterwards, they are all set to NaN
        self.setAttribute(self.Auxiliary, 'nStrands_inGroup_ROXIE', np.NaN)
        self.setAttribute(self.Auxiliary, 'strandToHalfTurn', np.NaN)
        self.setAttribute(self.Auxiliary, 'strandToGroup', np.NaN)
        self.setAttribute(self.Auxiliary, 'x_strands', np.NaN)
        self.setAttribute(self.Auxiliary, 'y_strands', np.NaN)
        self.setAttribute(self.Auxiliary, 'I_strands', np.NaN)


    def setAttribute(self, LEDETclass, attribute: str, value):
        try:
            setattr(LEDETclass, attribute, value)
        except:
            setattr(getattr(self, LEDETclass), attribute, value)


    def getAttribute(self, LEDETclass, attribute):
        try:
            return getattr(LEDETclass, attribute)
        except:
            return getattr(getattr(self, LEDETclass), attribute)


    def translateModelDataToLEDET(self):
        """"
            Translates and sets parameters in self.DataModelMagnet to DataLEDET if parameter exists in LEDET
        """
        # Transform DataModelMagnet structure to dictionary with dot-separated branches
        df = pd.json_normalize(self.model_data.model_dump(), sep='.')
        dotSepModelData = df.to_dict(orient='records')[0]

        for keyModelData, value in dotSepModelData.items():
            keyLEDET = DictionaryLEDET.lookupModelDataToLEDET(keyModelData)
            if keyLEDET:
                if keyLEDET in self.Inputs.__annotations__:
                    self.setAttribute(self.Inputs, keyLEDET, value)
                elif keyLEDET in self.Options.__annotations__:
                    self.setAttribute(self.Options, keyLEDET, value)
                elif keyLEDET in self.Plots.__annotations__:
                    self.setAttribute(self.Plots, keyLEDET, value)
                elif keyLEDET in self.Variables.__annotations__:
                    self.setAttribute(self.Variables, keyLEDET, value)
                elif keyLEDET in self.Auxiliary.__annotations__:
                    self.setAttribute(self.Auxiliary, keyLEDET, value)
                else:
                    print('Warning: Can find {} in lookup table but not in DataLEDET'.format(keyLEDET))
                    # raise KeyError('Can find {} in lookup table but not in DataLEDET'.format(keyLEDET))


    def loadTypeWindings(self):
        '''
        Assign the integer number defining the type of windings / magnet geometry in LEDET
        '''
        self.Options.flag_typeWindings = DictionaryLEDET.lookupWindings(self.model_data.GeneralParameters.magnet_type, mode='data2ledet')


    def loadMatProSet(self):
        '''
        Assign the integer number defining the STEAM Material Properties set in LEDET
        '''
        if isinstance(self.model_data.Options_LEDET.STEAM_Material_Properties.STEAM_material_properties_set, str):
            self.Options.material_properties_set = DictionaryLEDET.lookupMatProSet(self.model_data.Options_LEDET.STEAM_Material_Properties.STEAM_material_properties_set)


    def loadConductorData(self, overwrite_conductor_to_group: list = []):
        '''
            Load conductor data from DataModelMagnet keys
            overwrite_conductor_to_group is used in case the variable "overwrite_conductor_to_group" should be set manually rather than read from the data srtucture (this is always done, for example, when case_model='conductor')
        '''

        # Unpack variables
        if overwrite_conductor_to_group == []:
            conductor_to_group = self.model_data.CoilWindings.conductor_to_group  # Reminder: This key assigns to each group a conductor of one of the conductors
        else:
            conductor_to_group = overwrite_conductor_to_group  # use overwritten value

        # Initialize Cable variables that need to be set by this method
        self.nStrands_inGroup = np.array([], dtype=np.uint32)
        self.insulationType_inGroup = np.array([], dtype=np.uint32)
        self.internalVoidsType_inGroup = np.array([], dtype=np.uint32)
        self.externalVoidsType_inGroup = np.array([], dtype=np.uint32)
        self.wBare_inGroup = np.array([])
        self.hBare_inGroup = np.array([])
        self.wIns_inGroup = np.array([])
        self.hIns_inGroup = np.array([])
        self.Lp_s_inGroup = np.array([])
        self.R_c_inGroup = np.array([])
        self.overwrite_f_internalVoids_inGroup = np.array([])
        self.overwrite_f_externalVoids_inGroup = np.array([])
        # Initialize Strand variables that need to be set by this method
        self.SCtype_inGroup = np.array([], dtype=np.uint32)
        self.STtype_inGroup = np.array([], dtype=np.uint32)
        self.dcore_inGroup = np.array([])
        self.ds_inGroup = np.array([])
        self.dfilamentary_inGroup = np.array([])
        self.f_SC_strand_inGroup = np.array([])
        self.RRR_Cu_inGroup = np.array([])
        self.Lp_f_inGroup = np.array([])
        self.f_ro_eff_inGroup = np.array([])
        self.df_inGroup = np.array([])
        # Initialize Jc-fit variables that need to be set by this method
        self.Tc0_NbTi_ht_inGroup = np.array([])
        self.Bc2_NbTi_ht_inGroup = np.array([])
        self.c1_Ic_NbTi_inGroup = np.array([])
        self.c2_Ic_NbTi_inGroup = np.array([])
        self.Tc0_Nb3Sn_inGroup = np.array([])
        self.Bc2_Nb3Sn_inGroup = np.array([])
        self.Jc_Nb3Sn0_inGroup = np.array([])
        self.alpha_Nb3Sn_inGroup = np.array([])
        self.f_scaling_Jc_BSCCO2212_inGroup = np.array([])
        self.selectedFit_inGroup = np.array([], dtype=np.uint32)
        self.fitParameters_inGroup = np.empty((8, 0))  # Special case: This variable will be written as a matrix with 8 rows TODO find a solution for this special one - in LEDET this can be a matrix

        # For each group, load the cable, strand, and Jc-fit parameters according to their type
        for group, conductor_type in enumerate(conductor_to_group):
            if self.verbose: print('Group/Block #{}. Selected conductor: {}'.format(group + 1, conductor_type))
            self.loadCableData(conductor_type)
            self.loadStrandData(conductor_type)
            self.loadJcFitData(conductor_type)

        # Substitute nan with zeros in all conductor Jc-fit parameters (except selectedFit_inGroup that must always be defined)
        # This is needed to write zeros in case multiple conductors need different Jc-fit parameters and they don't use others
        # TODO adjust f_scaling_Jc_BSCCO2212_inGroup and other variables (alpha..) for all fit types
        list_conductor_vars = [
            'Tc0_NbTi_ht_inGroup',
            'Bc2_NbTi_ht_inGroup',
            'c1_Ic_NbTi_inGroup',
            'c2_Ic_NbTi_inGroup',
            'Tc0_Nb3Sn_inGroup',
            'Bc2_Nb3Sn_inGroup',
            'Jc_Nb3Sn0_inGroup',
            'alpha_Nb3Sn_inGroup',
            'f_scaling_Jc_BSCCO2212_inGroup',
            'selectedFit_inGroup',
            ]
        for var in list_conductor_vars:
            temp_var = getattr(self, var)  # not efficient coding, but it should improve readibility
            if not np.all(np.isnan(temp_var)):
                # The values will be changed from nan to 0.0 unless they are all nan (in that case, they'll remain nan)
                setattr(self, var, np.nan_to_num(temp_var, nan=0.0))

        # TODO: Check that self.nStrands_inGroup is compatible with ROXIE map2d number of strands

        # Assign loaded Cable variables
        self.setAttribute(self.Inputs, 'nStrands_inGroup', self.nStrands_inGroup)
        self.setAttribute(self.Inputs, 'internalVoidsType_inGroup', self.internalVoidsType_inGroup)
        self.setAttribute(self.Inputs, 'externalVoidsType_inGroup', self.externalVoidsType_inGroup)
        self.setAttribute(self.Inputs, 'insulationType_inGroup', self.insulationType_inGroup)
        self.setAttribute(self.Inputs, 'wBare_inGroup', self.wBare_inGroup)
        self.setAttribute(self.Inputs, 'hBare_inGroup', self.hBare_inGroup)
        self.setAttribute(self.Inputs, 'wIns_inGroup', self.wIns_inGroup)
        self.setAttribute(self.Inputs, 'hIns_inGroup', self.hIns_inGroup)
        self.setAttribute(self.Inputs, 'Lp_s_inGroup', self.Lp_s_inGroup)
        self.setAttribute(self.Inputs, 'R_c_inGroup', self.R_c_inGroup)
        self.setAttribute(self.Inputs, 'overwrite_f_internalVoids_inGroup', self.overwrite_f_internalVoids_inGroup)
        self.setAttribute(self.Inputs, 'overwrite_f_externalVoids_inGroup', self.overwrite_f_externalVoids_inGroup)
        # Assign loaded Strand variables
        self.setAttribute(self.Inputs, 'SCtype_inGroup', self.SCtype_inGroup)
        self.setAttribute(self.Inputs, 'STtype_inGroup', self.STtype_inGroup)
        self.setAttribute(self.Inputs, 'ds_inGroup', self.ds_inGroup)
        self.setAttribute(self.Inputs, 'dcore_inGroup', self.dcore_inGroup)
        self.setAttribute(self.Inputs, 'dfilamentary_inGroup', self.dfilamentary_inGroup)
        self.setAttribute(self.Inputs, 'f_SC_strand_inGroup', self.f_SC_strand_inGroup)
        self.setAttribute(self.Inputs, 'RRR_Cu_inGroup', self.RRR_Cu_inGroup)
        self.setAttribute(self.Inputs, 'Lp_f_inGroup', self.Lp_f_inGroup)
        self.setAttribute(self.Inputs, 'f_ro_eff_inGroup', self.f_ro_eff_inGroup)
        self.setAttribute(self.Inputs, 'df_inGroup', self.df_inGroup)
        # Assign loaded Jc-fit variables
        self.setAttribute(self.Inputs, 'Tc0_NbTi_ht_inGroup', self.Tc0_NbTi_ht_inGroup)
        self.setAttribute(self.Inputs, 'Bc2_NbTi_ht_inGroup', self.Bc2_NbTi_ht_inGroup)
        self.setAttribute(self.Inputs, 'c1_Ic_NbTi_inGroup', self.c1_Ic_NbTi_inGroup)
        self.setAttribute(self.Inputs, 'c2_Ic_NbTi_inGroup', self.c2_Ic_NbTi_inGroup)
        self.setAttribute(self.Inputs, 'Tc0_Nb3Sn_inGroup', self.Tc0_Nb3Sn_inGroup)
        self.setAttribute(self.Inputs, 'Bc2_Nb3Sn_inGroup', self.Bc2_Nb3Sn_inGroup)
        self.setAttribute(self.Inputs, 'Jc_Nb3Sn0_inGroup', self.Jc_Nb3Sn0_inGroup)
        self.setAttribute(self.Inputs, 'alpha_Nb3Sn_inGroup', self.alpha_Nb3Sn_inGroup)
        self.setAttribute(self.Inputs, 'f_scaling_Jc_BSCCO2212_inGroup', self.f_scaling_Jc_BSCCO2212_inGroup)
        self.setAttribute(self.Inputs, 'selectedFit_inGroup', self.selectedFit_inGroup)
        self.setAttribute(self.Inputs, 'fitParameters_inGroup', self.fitParameters_inGroup)
        #TODO: CUDI3


    def loadCableData(self, conductor_id):
        '''
            Load the cable parameters for one group from DataModelMagnet keys, and append them to the respective self variables
        '''

        conductor = self.model_data.Conductors[conductor_id - 1]
        type_cable = conductor.cable.type
        if self.verbose: print('Conductor type: #{}. type_cable = {}'.format(conductor_id, type_cable))

        if type_cable == 'Rutherford':
            self.nStrands_inGroup                  = np.append(self.nStrands_inGroup                 , conductor.cable.n_strands)
            self.internalVoidsType_inGroup         = np.append(self.internalVoidsType_inGroup        , DictionaryLEDET.lookupInsulation(conductor.cable.material_inner_voids))
            self.externalVoidsType_inGroup         = np.append(self.externalVoidsType_inGroup        , DictionaryLEDET.lookupInsulation(conductor.cable.material_outer_voids))
            self.insulationType_inGroup            = np.append(self.insulationType_inGroup           , DictionaryLEDET.lookupInsulation(conductor.cable.material_insulation))
            self.wBare_inGroup                     = np.append(self.wBare_inGroup                    , conductor.cable.bare_cable_width)
            self.hBare_inGroup                     = np.append(self.hBare_inGroup                    , conductor.cable.bare_cable_height_mean)
            self.wIns_inGroup                      = np.append(self.wIns_inGroup                     , conductor.cable.th_insulation_along_width)
            self.hIns_inGroup                      = np.append(self.hIns_inGroup                     , conductor.cable.th_insulation_along_height)
            self.Lp_s_inGroup                      = np.append(self.Lp_s_inGroup                     , conductor.cable.strand_twist_pitch)
            self.R_c_inGroup                       = np.append(self.R_c_inGroup                      , conductor.cable.Rc)
            if conductor.cable.f_inner_voids != None:
                self.overwrite_f_internalVoids_inGroup = np.append(self.overwrite_f_internalVoids_inGroup, conductor.cable.f_inner_voids)
            if conductor.cable.f_outer_voids != None:
                self.overwrite_f_externalVoids_inGroup = np.append(self.overwrite_f_externalVoids_inGroup, conductor.cable.f_outer_voids)
        elif type_cable == 'Mono':
            self.nStrands_inGroup = np.append(self.nStrands_inGroup, 1)  # Note: The conductor is made of one single wire
            self.internalVoidsType_inGroup = np.append(self.internalVoidsType_inGroup, DictionaryLEDET.lookupInsulation(conductor.cable.material_inner_voids))
            self.externalVoidsType_inGroup = np.append(self.externalVoidsType_inGroup, DictionaryLEDET.lookupInsulation(conductor.cable.material_outer_voids))
            self.insulationType_inGroup = np.append(self.insulationType_inGroup, DictionaryLEDET.lookupInsulation(conductor.cable.material_insulation))
            self.wBare_inGroup = np.append(self.wBare_inGroup, conductor.cable.bare_cable_width)
            self.hBare_inGroup = np.append(self.hBare_inGroup, conductor.cable.bare_cable_height_mean)
            self.wIns_inGroup = np.append(self.wIns_inGroup, conductor.cable.th_insulation_along_width)
            self.hIns_inGroup = np.append(self.hIns_inGroup, conductor.cable.th_insulation_along_height)
            self.Lp_s_inGroup = np.append(self.Lp_s_inGroup, 0)  # Mono cables do not have strands
            self.R_c_inGroup = np.append(self.R_c_inGroup, 0)  # Mono cables do not have strands
            if conductor.cable.f_inner_voids != None:
                self.overwrite_f_internalVoids_inGroup = np.append(self.overwrite_f_internalVoids_inGroup, conductor.cable.f_inner_voids)
            if conductor.cable.f_outer_voids != None:
                self.overwrite_f_externalVoids_inGroup = np.append(self.overwrite_f_externalVoids_inGroup, conductor.cable.f_outer_voids)
        elif type_cable == 'Ribbon':
            self.nStrands_inGroup                  = np.append(self.nStrands_inGroup, 1)  # Note: "Strands" in ribbon-cables are connected in series, so the conductor is made of one single wire
            self.internalVoidsType_inGroup         = np.append(self.internalVoidsType_inGroup        , DictionaryLEDET.lookupInsulation(conductor.cable.material_inner_voids))
            self.externalVoidsType_inGroup         = np.append(self.externalVoidsType_inGroup        , DictionaryLEDET.lookupInsulation(conductor.cable.material_outer_voids))
            self.insulationType_inGroup            = np.append(self.insulationType_inGroup           , DictionaryLEDET.lookupInsulation(conductor.cable.material_insulation))
            self.wBare_inGroup                     = np.append(self.wBare_inGroup                    , conductor.cable.bare_cable_width)
            self.hBare_inGroup                     = np.append(self.hBare_inGroup                    , conductor.cable.bare_cable_height_mean)
            self.wIns_inGroup                      = np.append(self.wIns_inGroup                     , conductor.cable.th_insulation_along_width)
            self.hIns_inGroup                      = np.append(self.hIns_inGroup                     , conductor.cable.th_insulation_along_height)
            self.Lp_s_inGroup                      = np.append(self.Lp_s_inGroup                     , 0)  # Mono cables do not have strands
            self.R_c_inGroup                       = np.append(self.R_c_inGroup                      , 0)  # Mono cables do not have strands
            if conductor.cable.f_inner_voids != None:
                self.overwrite_f_internalVoids_inGroup = np.append(self.overwrite_f_internalVoids_inGroup, conductor.cable.f_inner_voids)
            if conductor.cable.f_outer_voids != None:
                self.overwrite_f_externalVoids_inGroup = np.append(self.overwrite_f_externalVoids_inGroup, conductor.cable.f_outer_voids)
        else:
            raise Exception('Group #{}. Selected cable type ({}) is not supported.'.format(conductor_id, type_cable))


    def loadStrandData(self, conductor_id):
        '''
            Load the strand parameters for one group from DataModelMagnet keys, and append them to the respective self variables
        '''

        conductor = self.model_data.Conductors[conductor_id - 1]
        type_strand = conductor.strand.type
        if self.verbose: print(f'Conductor type: #{conductor_id}. type_strand = {type_strand}')

        if type_strand == 'Round':
            if conductor.strand.material_superconductor in ['Nb3Sn','NB3SN'] and conductor.Jc_fit.type == 'Summers':  # Special case: this material definition is ambiguous since it could refer to Nb3Sn with Summers' fit or with Bordini's fit. Hence, a dedicated logic is implemented
                self.SCtype_inGroup = np.append(self.SCtype_inGroup, 2)
            elif conductor.strand.material_superconductor in ['Nb3Sn','NB3SN'] and conductor.Jc_fit.type == 'Bordini':  # Special case: this material definition is ambiguous since it could refer to Nb3Sn with Summers' fit or with Bordini's fit. Hence, a dedicated logic is implemented
                self.SCtype_inGroup = np.append(self.SCtype_inGroup, 4)
            else:
                self.SCtype_inGroup = np.append(self.SCtype_inGroup, DictionaryLEDET.lookupSuperconductor(conductor.strand.material_superconductor))
            self.STtype_inGroup      = np.append(self.STtype_inGroup,      DictionaryLEDET.lookupStabilizer(conductor.strand.material_stabilizer))
            self.ds_inGroup          = np.append(self.ds_inGroup,          conductor.strand.diameter)
            self.f_SC_strand_inGroup = np.append(self.f_SC_strand_inGroup, 1 / (1 + conductor.strand.Cu_noCu_in_strand))  # f_SC=1/(1+Cu_noCu)
            self.RRR_Cu_inGroup      = np.append(self.RRR_Cu_inGroup,      conductor.strand.RRR)
            self.Lp_f_inGroup        = np.append(self.Lp_f_inGroup,        conductor.strand.fil_twist_pitch)
            self.f_ro_eff_inGroup    = np.append(self.f_ro_eff_inGroup,    conductor.strand.f_Rho_effective)
            self.df_inGroup          = np.append(self.df_inGroup,          conductor.strand.filament_diameter)
            self.dcore_inGroup       = np.append(self.dcore_inGroup,       np.array(conductor.strand.diameter_core, dtype=float))
            self.dfilamentary_inGroup= np.append(self.dfilamentary_inGroup,np.array(conductor.strand.diameter_filamentary, dtype=float))
        elif type_strand == 'Rectangular':
            if conductor.strand.material_superconductor in ['Nb3Sn','NB3SN'] and conductor.Jc_fit.type == 'Summers':  # Special case: this material definition is ambiguous since it could refer to Nb3Sn with Summers' fit or with Bordini's fit. Hence, a dedicated logic is implemented
                self.SCtype_inGroup = np.append(self.SCtype_inGroup, 2)
            elif conductor.strand.material_superconductor in ['Nb3Sn','NB3SN'] and conductor.Jc_fit.type == 'Bordini':  # Special case: this material definition is ambiguous since it could refer to Nb3Sn with Summers' fit or with Bordini's fit. Hence, a dedicated logic is implemented
                self.SCtype_inGroup = np.append(self.SCtype_inGroup, 4)
            else:
                self.SCtype_inGroup = np.append(self.SCtype_inGroup, DictionaryLEDET.lookupSuperconductor(conductor.strand.material_superconductor))
            self.STtype_inGroup      = np.append(self.STtype_inGroup,      DictionaryLEDET.lookupStabilizer(conductor.strand.material_stabilizer))
            if conductor.strand.bare_corner_radius:     # if bare corner radius is specified take it into account
                wire_area = (conductor.strand.bare_width * conductor.strand.bare_height) - ((4 - np.pi) * conductor.strand.bare_corner_radius ** 2)
            else:   # if it is None, treat it as zero and and conductor as perfectly rectangular
                wire_area = conductor.strand.bare_width * conductor.strand.bare_height
            self.ds_inGroup          = np.append(self.ds_inGroup,          np.sqrt(wire_area * 4 / np.pi))
            self.f_SC_strand_inGroup = np.append(self.f_SC_strand_inGroup, 1 / (1 + conductor.strand.Cu_noCu_in_strand))  # f_SC=1/(1+Cu_noCu)
            self.RRR_Cu_inGroup      = np.append(self.RRR_Cu_inGroup,      conductor.strand.RRR)
            self.Lp_f_inGroup        = np.append(self.Lp_f_inGroup,        conductor.strand.fil_twist_pitch)
            self.f_ro_eff_inGroup    = np.append(self.f_ro_eff_inGroup,    conductor.strand.f_Rho_effective)
            self.df_inGroup          = np.append(self.df_inGroup,          conductor.strand.filament_diameter)
            # self.dfilamentary_inGroup = np.append(self.dfilamentary_inGroup, conductor.strand.diameter_filamentary)
            # self.dcore_inGroup = np.append(self.dcore_inGroup, conductor.strand.diameter_core)
        else:
            raise Exception(f'Group #{conductor_id}. Selected strand type ({type_strand}) is not supported.')


    def loadJcFitData(self, conductor_id):
        '''
            Load the Jc-fit parameters for one group from DataModelMagnet keys, and append them to the respective self variables
        '''

        conductor = self.model_data.Conductors[conductor_id - 1]
        type_JcFit = conductor.Jc_fit.type
        if self.verbose: print('Conductor type: #{}. type_JcFit = {}'.format(conductor_id, type_JcFit))

        # TODO: ConstantJc to enable for quench protection simulations
        if type_JcFit == 'ConstantJc':
            self.selectedFit_inGroup = np.append(self.selectedFit_inGroup, 1)
            temp_fitParam = np.array([conductor.Jc_fit.Jc_constant, 0, 0, 0, 0, 0, 0, 0])  # Last values not needed for this fit and set to 0
            self.fitParameters_inGroup = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
            raise Exception('Group #{}. Selected Jc-fit type ({}) is currently not supported by LEDET.'.format(conductor_id, type_JcFit))
        elif type_JcFit == 'CUDI1':
            self.Tc0_NbTi_ht_inGroup  = np.append(self.Tc0_NbTi_ht_inGroup, conductor.Jc_fit.Tc0_CUDI1)
            self.Bc2_NbTi_ht_inGroup  = np.append(self.Bc2_NbTi_ht_inGroup, conductor.Jc_fit.Bc20_CUDI1)
            self.c1_Ic_NbTi_inGroup   = np.append(self.c1_Ic_NbTi_inGroup  , conductor.Jc_fit.C1_CUDI1)
            self.c2_Ic_NbTi_inGroup   = np.append(self.c2_Ic_NbTi_inGroup  , conductor.Jc_fit.C2_CUDI1)
            self.Tc0_Nb3Sn_inGroup    = np.append(self.Tc0_Nb3Sn_inGroup, 0)
            self.Bc2_Nb3Sn_inGroup    = np.append(self.Bc2_Nb3Sn_inGroup, 0)
            self.Jc_Nb3Sn0_inGroup    = np.append(self.Jc_Nb3Sn0_inGroup, 0)
            self.alpha_Nb3Sn_inGroup  = np.append(self.alpha_Nb3Sn_inGroup, np.nan)
            self.f_scaling_Jc_BSCCO2212_inGroup = np.append(self.f_scaling_Jc_BSCCO2212_inGroup, np.nan)
            self.selectedFit_inGroup = np.append(self.selectedFit_inGroup, 6)  # TODO: not yet supported by LEDET
            temp_fitParam = np.array([conductor.Jc_fit.Tc0_CUDI1, conductor.Jc_fit.Bc20_CUDI1, conductor.Jc_fit.C1_CUDI1, conductor.Jc_fit.C2_CUDI1, 0, 0, 0, 0])  # Last values not needed for this fit and set to 0
            self.fitParameters_inGroup = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
        # TODO: CUDI3 to enable for quench protection simulations
        elif type_JcFit == 'CUDI3':
            self.selectedFit_inGroup = np.append(self.selectedFit_inGroup, 3)  # TODO: not yet supported by LEDET
            temp_fitParam = np.array([
                conductor.Jc_fit.Tc0_CUDI3, conductor.Jc_fit.Bc20_CUDI3, conductor.Jc_fit.c1_CUDI3,
                conductor.Jc_fit.c2_CUDI3, conductor.Jc_fit.c3_CUDI3, conductor.Jc_fit.c4_CUDI3,
                conductor.Jc_fit.c5_CUDI3, conductor.Jc_fit.c6_CUDI3])
            self.fitParameters_inGroup = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
            raise Exception('Group #{}. Selected Jc-fit type ({}) is currently not supported by LEDET.'.format(conductor_id, type_JcFit))
        # TODO: Bottura to enable for quench protection simulations
        elif type_JcFit == 'Bottura':
            self.selectedFit_inGroup = np.append(self.selectedFit_inGroup, 2)  # TODO: not yet supported by LEDET
            temp_fitParam = np.array([
                conductor.Jc_fit.Tc0_Bottura, conductor.Jc_fit.Bc20_Bottura, conductor.Jc_fit.Jc_ref_Bottura,
                conductor.Jc_fit.C0_Bottura, conductor.Jc_fit.alpha_Bottura, conductor.Jc_fit.beta_Bottura,
                conductor.Jc_fit.gamma_Bottura, 0])  # Last values not needed for this fit and set to 0
            self.fitParameters_inGroup = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
            raise Exception('Group #{}. Selected Jc-fit type ({}) is currently not supported by LEDET.'.format(conductor_id, type_JcFit))
        elif type_JcFit == 'Summers':
            self.Tc0_NbTi_ht_inGroup            = np.append(self.Tc0_NbTi_ht_inGroup  , 0)
            self.Bc2_NbTi_ht_inGroup            = np.append(self.Bc2_NbTi_ht_inGroup  , 0)
            self.c1_Ic_NbTi_inGroup             = np.append(self.c1_Ic_NbTi_inGroup   , 0)
            self.c2_Ic_NbTi_inGroup             = np.append(self.c2_Ic_NbTi_inGroup   , 0)
            self.Tc0_Nb3Sn_inGroup              = np.append(self.Tc0_Nb3Sn_inGroup    , conductor.Jc_fit.Tc0_Summers)
            self.Bc2_Nb3Sn_inGroup              = np.append(self.Bc2_Nb3Sn_inGroup    , conductor.Jc_fit.Bc20_Summers)
            self.Jc_Nb3Sn0_inGroup              = np.append(self.Jc_Nb3Sn0_inGroup    , conductor.Jc_fit.Jc0_Summers)
            self.alpha_Nb3Sn_inGroup            = np.append(self.alpha_Nb3Sn_inGroup, np.nan)
            self.f_scaling_Jc_BSCCO2212_inGroup = np.append(self.f_scaling_Jc_BSCCO2212_inGroup, np.nan)
            self.selectedFit_inGroup = np.append(self.selectedFit_inGroup             , 4)
            temp_fitParam = np.array([conductor.Jc_fit.Tc0_Summers, conductor.Jc_fit.Bc20_Summers, conductor.Jc_fit.Jc0_Summers, 0, 0, 0, 0, 0])  # Last values not needed for this fit and set to 0
            self.fitParameters_inGroup          = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
        elif type_JcFit == 'Bordini':
            self.Tc0_NbTi_ht_inGroup            = np.append(self.Tc0_NbTi_ht_inGroup  , 0)
            self.Bc2_NbTi_ht_inGroup            = np.append(self.Bc2_NbTi_ht_inGroup  , 0)
            self.c1_Ic_NbTi_inGroup             = np.append(self.c1_Ic_NbTi_inGroup   , 0)
            self.c2_Ic_NbTi_inGroup             = np.append(self.c2_Ic_NbTi_inGroup   , 0)
            self.Tc0_Nb3Sn_inGroup              = np.append(self.Tc0_Nb3Sn_inGroup    , conductor.Jc_fit.Tc0_Bordini)
            self.Bc2_Nb3Sn_inGroup              = np.append(self.Bc2_Nb3Sn_inGroup    , conductor.Jc_fit.Bc20_Bordini)
            self.Jc_Nb3Sn0_inGroup              = np.append(self.Jc_Nb3Sn0_inGroup    , conductor.Jc_fit.C0_Bordini)
            self.alpha_Nb3Sn_inGroup            = np.append(self.alpha_Nb3Sn_inGroup , conductor.Jc_fit.alpha_Bordini)
            self.f_scaling_Jc_BSCCO2212_inGroup = np.append(self.f_scaling_Jc_BSCCO2212_inGroup, np.nan)
            self.selectedFit_inGroup            = np.append(self.selectedFit_inGroup  , 5)  # TODO: not yet supported by LEDET
            temp_fitParam = np.array([conductor.Jc_fit.Tc0_Bordini, conductor.Jc_fit.Bc20_Bordini, conductor.Jc_fit.C0_Bordini, conductor.Jc_fit.alpha_Bordini, 0, 0, 0, 0])  # Last values not needed for this fit and set to 0
            self.fitParameters_inGroup          = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
        elif type_JcFit == 'BSCCO_2212_LBNL':
            self.Tc0_NbTi_ht_inGroup            = np.append(self.Tc0_NbTi_ht_inGroup  , 0)
            self.Bc2_NbTi_ht_inGroup            = np.append(self.Bc2_NbTi_ht_inGroup  , 0)
            self.c1_Ic_NbTi_inGroup             = np.append(self.c1_Ic_NbTi_inGroup   , 0)
            self.c2_Ic_NbTi_inGroup             = np.append(self.c2_Ic_NbTi_inGroup   , 0)
            self.Tc0_Nb3Sn_inGroup              = np.append(self.Tc0_Nb3Sn_inGroup    , 0)
            self.Bc2_Nb3Sn_inGroup              = np.append(self.Bc2_Nb3Sn_inGroup    , 0)
            self.Jc_Nb3Sn0_inGroup              = np.append(self.Jc_Nb3Sn0_inGroup    , 0)
            self.alpha_Nb3Sn_inGroup            = np.append(self.alpha_Nb3Sn_inGroup, np.nan)
            self.f_scaling_Jc_BSCCO2212_inGroup = np.append(self.f_scaling_Jc_BSCCO2212_inGroup, conductor.Jc_fit.f_scaling_Jc_BSCCO2212)  # TODO problem when only some conductors have BSCO2212
            self.selectedFit_inGroup            = np.append(self.selectedFit_inGroup  , 51)  # TODO: not yet supported by LEDET
            temp_fitParam = np.array([conductor.Jc_fit.f_scaling_Jc_BSCCO2212, 0, 0, 0, 0, 0, 0, 0])  # Last values not needed for this fit and set to 0
            self.fitParameters_inGroup          = np.column_stack((self.fitParameters_inGroup, temp_fitParam))  # At each step, add one more column to the matrix
        else:
            raise Exception('Group #{}. Selected Jc-fit type ({}) is not supported.'.format(conductor_id, type_JcFit))

    def set_electrical_order(self, el_order_half_turns: List[float]):
        '''
        Get electrical order from BuilderModel and set them to LEDET Input
        '''
        # Assign values to the attribute in the LEDET Inputs dataclass
        self.setAttribute(self.Inputs, 'el_order_half_turns', np.array(el_order_half_turns))


    def setThermalConnections(self):
        """
        Function calculates thermal connections between turns that are considered to thermally touch.
        The output is 4 lists of lists named:
        iContactAlongWidth_From
        iContactAlongWidth_To
        iContactAlongHeight_From
        iContactAlongHeight_To
        and these are assigned to input section of LEDET input file.
        """
        flag_typeWindings = self.Options.flag_typeWindings
        typeWindings = DictionaryLEDET.lookupWindings(flag_typeWindings, mode='ledet2data')

        if typeWindings in ['multipole', 'busbar']:

            # Unpack variables
            nT = self.Inputs.nT
            max_distance = self.Auxiliary.heat_exchange_max_distance
            indexTstart = self.Auxiliary.indexTstart
            indexTstop = self.Auxiliary.indexTstop
            strandToHalfTurn = self.Auxiliary.strandToHalfTurn
            strandToGroup = self.Auxiliary.strandToGroup
            x_strands = self.Auxiliary.x_strands
            y_strands = self.Auxiliary.y_strands
            nGroups = int(len(nT))

            if self.verbose:
                print('Setting thermal connections')

            iContactAlongWidth_From = []
            iContactAlongWidth_To = []

            for g in range(nGroups):
                iContactAlongWidth_From.extend(range(indexTstart[g], indexTstop[g]))
                iContactAlongWidth_To.extend(range(indexTstart[g] + 1, indexTstop[g] + 1))

            if len(iContactAlongWidth_From) < 1:
                iContactAlongWidth_From.append(1)
                iContactAlongWidth_To.append(1)

            self.setAttribute(self.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From, np.int32))
            self.setAttribute(self.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To, np.int32))

            # Prepare input for the function close_pairs_ckdtree
            X = np.column_stack((x_strands, y_strands))

            # find all pairs of strands closer than a distance of max_d
            pairs_close = close_pairs_ckdtree(X, max_distance)

            # find pairs that belong to half-turns located in different groups
            contact_pairs = set([])
            for p in pairs_close:
                if not strandToGroup[p[0]] == strandToGroup[p[1]]:
                    contact_pairs.add((strandToHalfTurn[p[0]], strandToHalfTurn[p[1]]))

            # assign the pair values to two distinct vectors
            iContactAlongHeight_From = []
            iContactAlongHeight_To = []
            for p in contact_pairs:
                iContactAlongHeight_From.append(p[0])
                iContactAlongHeight_To.append(p[1])
            # Keep arrays Non-empty
            if len(iContactAlongHeight_From) < 1:
                iContactAlongHeight_From.append(1)
                iContactAlongHeight_To.append(1)

            # find indices to order the vector iContactAlongHeight_From
            idxSort = [i for (v, i) in sorted((v, i) for (i, v) in enumerate(iContactAlongHeight_From))]

            # reorder both iContactAlongHeight_From and iContactAlongHeight_To using the indices
            iContactAlongHeight_From = [iContactAlongHeight_From[i] for i in idxSort]
            iContactAlongHeight_To   = [iContactAlongHeight_To[i] for i in idxSort]

            self.setAttribute(self.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From, np.int32))
            self.setAttribute(self.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To, np.int32))

        elif typeWindings in ['CCT_straight']:
            # --- get inputs used for windings and fqpls ---
            wwns = self.model_data.CoilWindings.CCT_straight.winding_numRowStrands  # number of wires in width direction
            whns = self.model_data.CoilWindings.CCT_straight.winding_numColumnStrands  # number of wires in height direction
            n_turns_formers = self.model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers  # number of turns [-]
            # get variables used here from model data
            fqpl_names = [val for val, flag in zip(self.model_data.Quench_Protection.FQPCs.names, self.model_data.Quench_Protection.FQPCs.enabled) if flag]  # trim only to enabled fqpls
            fqpl_th_conns_def_bool = [val for val, flag in zip(self.model_data.Quench_Protection.FQPCs.th_conns_def, self.model_data.Quench_Protection.FQPCs.enabled) if flag]  # trim only to enabled fqpls
            #fqpl_th_conns_def_bool = self.model_data.Quench_Protection.FQPLs.th_conns_def # not trimming here to FQPLs enabled, but later after expanding into a full set.
            gr_dict = {0: 'go', 1: 'return'}  # go-return dictionary used for printing helpful error messages
            tb_dict = {0: 'bottom', 1: 'top'}  # top-bottom dictionary used for printing helpful error messages

            # ----- windings thermal connections ------
            # define the connections on general position in turn, on 1-based numbering as in ProteCCT (to avoid confusion)
            th_conns_h_def_1 = []
            for winding_i in range(1):  # range(len(n_turns_formers)):
                for i_w in range(wwns[winding_i] - 1):
                    for i_h in range(whns[winding_i]):
                        th_conns_h_def_1.append([i_h + i_w * whns[winding_i] + 1, i_h + i_w * whns[winding_i] + 1 + whns[winding_i]])
            # print(th_conns_h_def_1)
            th_conns_w_def_1 = []
            for winding_i in range(1):  # range(len(n_turns_formers)):
                for i_w in range(wwns[winding_i]):
                    for i_h in range(whns[winding_i] - 1):
                        th_conns_w_def_1.append([i_h + 1 + i_w * whns[winding_i], i_h + 2 + i_w * whns[winding_i]])
            # recalculate for 0-based for python
            th_conns_h_def = []  # 0-based in python
            for tch in th_conns_h_def_1:
                th_conns_h_def.append([t - 1 for t in tch])
            th_conns_w_def = []  # 0-based in python
            for tch in th_conns_w_def_1:
                th_conns_w_def.append([t - 1 for t in tch])

            turns_dict = {}             # this is created below in a loop for windings, but used later in fqpl connections
            th_conns_height = []        # results for windings for connections along height go to this list
            th_conns_width = []         # results for windings for connections along width go to this list
            # all_turns = []
            max_turn = 0
            for winding_i in range(len(n_turns_formers)):       # for each winding layer of CCT
                winding_dict = {}
                for i_t in range(int(n_turns_formers[winding_i])):  # for each turn in a winding layer
                    turns_in_channel = []
                    turn = max_turn + i_t + 1
                    for _ in range(wwns[winding_i]):
                        for _ in range(whns[winding_i]):
                            turns_in_channel.append(int(turn))
                            turn += n_turns_formers[winding_i]      # add number of turns in a former to create turn numbers in electrical order
                    for tch in th_conns_h_def:
                        th_conns_height.append(list(itemgetter(*tch)(turns_in_channel)))        # use positional tch channel to get the turns in electrical order for thermal connection
                    for tcw in th_conns_w_def:
                        th_conns_width.append(list(itemgetter(*tcw)(turns_in_channel)))         # use positional tch channel to get the turns in electrical order for thermal connection
                    winding_dict[i_t] = turns_in_channel
                turns_dict[winding_i] = winding_dict                                            # update turns dict for fqpls
                max_turn = np.max(turns_in_channel)                                             # update max turn in a layer before going to the next winding layer

            # ------ FQPLs thermal connections -----
            # this only assumes that FQPL can exist at the top or bottom or both of the channel. So in LEDET definition only thermal connections along the width are possible
            """
            # theses are only useful for debugging
            # L1 below ------- [FQPL1, FQPL2]                       # for go and return and all windings
            fqpl_th_conns_def_bool = [True, True]  # boolean for each fqpl and for all windings
            # L2 below ------ [[F1_Go, F1_Re], [F2_Go, F2_Re]]     # for all windings
            fqpl_th_conns_def_bool = [[True, False], [True, False]]  # boolean list for each fqpl to specify 'go' and 'return' wire connections to all windings
            # L3 below ----- [[[F1_G_W1, F1_G_W2], [F1_R_W1, F1_R_W2]], [[F2_G_W1, F2_G_W2], [F2_R_W1, F2_R_W2]]]      # for top and bottom of specified windings
            fqpl_th_conns_def_bool = [[[True, False], [True, False]], [[True, False], [True, False]]]  # boolean list for each fqpl to specify 'go' and 'return' for each fqpl to specify which winding to connect to
            # L4 below --- [[[[F1_G_W1_B, F1_G_W1_T], [F1_G_W2_B, F1_G_W2_T]], [[F1_R_W1_B, F1_R_W1_T], [F1_R_W2_B, F1_R_W2_T]]], [[[F2_G_W1_B, F2_G_W1_T], [F2_G_W2_B, F2_G_W2_T]], [[F2_R_W1_B, F2_R_W1_T], [F2_R_W2_B, F2_R_W2_T]]]]      # specify top and bottom of specified windings, but all wires in the horizontal channel direction
            fqpl_th_conns_def_bool = [[[[True, True], [False, False]], [[True, True], [False, False]]], [[[True, True], [False, False]], [[True, True], [False, False]]]]  # boolean list of lists for each fqpl to specify which winding to connect to and if at top or bottom or both
            # L5 below       [[[[[F1_G_W1_B_C0, F1_G_W1_B_C1], [F1_G_W1_T_C0, F1_G_W1_T_C1]], [[F1_G_W2_B_C0, F1_G_W2_B_C1], [F1_G_W2_T_C0, F1_G_W2_T_C1]]], [[[F1_R_W1_B_C0, F1_R_W1_B_C1], [F1_R_W1_T_C0, F1_R_W1_T_C1]], [[F1_R_W2_B_C0, F1_R_W2_B_C1], [F1_R_W2_T_C0, F1_R_W2_T_C1]]]], [[[[F2_G_W1_B_C0, F2_G_W1_B_C1], [F2_G_W1_T_C0, F2_G_W1_T_C1]], [[F2_G_W2_B_C0, F2_G_W2_B_C1], [F2_G_W2_T_C0, F2_G_W2_T_C1]]], [[[F2_R_W1_B_C0, F2_R_W1_B_C1], [F2_R_W1_T_C0, F2_R_W1_T_C1]], [[F2_R_W2_B_C0, F2_R_W2_B_C1], [F2_R_W2_T_C0, F2_R_W2_T_C1]]]]]      # specify which wires in the column to connect
            fqpl_th_conns_def_bool = [[[[[True, True], [False, False]], [[False, False], [False, False]]], [[[False, False], [False, False]], [[False, False], [False, False]]]],
                                      [[[[False, False], [False, False]], [[True, True], [False, False]]], [[[False, False], [False, False]], [[False, False], [False, False]]]]]  # boolean list of lists for each fqpl to specify which winding to connect to and if at top or bottom or both
            """
            if len(fqpl_names)>0:   # only if any fqpls have been defined and/or are enabled
                # Check if the thermal connections definition boolean top level list is the same length as number of fqpls
                if len(fqpl_names) != len(fqpl_th_conns_def_bool):
                    raise ValueError(f'Length of th_conns_def most outer list is {len(fqpl_th_conns_def_bool)} but does not match number of enabled FQPLs: {len(fqpl_names)}!')

                def __depth_count(lst):     # helper function used here only
                    """
                    takes an arbitrarily nested list as a parameter and returns the maximum depth to which the list has nested sub-lists.
                    """
                    if isinstance(lst, list):
                        return 1 + max(__depth_count(x) for x in lst)
                    else:
                        return 0
                    # end of helper function

                # check for depth of list supplied as an input
                if __depth_count(fqpl_th_conns_def_bool) == 0:  # return an error if it is not a list
                    raise ValueError('FQPLs to windings thermal connection needs to be a list of depth a least 1')
                elif __depth_count(fqpl_th_conns_def_bool) == 1:  # this means that a boolean for FQPL was provided. This connects or not that FQPL to all windings (not a typical case)
                    if self.verbose:
                        print(f'Level 1 thermal connections definition specified.')
                    fqpl_th_conns_def = []
                    for fqpl_i in range(len(fqpl_th_conns_def_bool)):  # for each fqpl
                        parts_fqpl_th_conn = []
                        for p_go_ret_i in range(2):
                            winding_th_conns = []
                            for winding_i in range(len(n_turns_formers)):  # for each winding
                                tb_list = []
                                for tb_i in range(2):  # for top and bottom of the channel
                                    turn_list = []
                                    for wwn_i in range(wwns[winding_i]):  # for each turn in horizontal direction in the channel
                                        turn_list.append(fqpl_th_conns_def_bool[fqpl_i])
                                    tb_list.append(turn_list)
                                winding_th_conns.append(tb_list)
                            parts_fqpl_th_conn.append(winding_th_conns)
                        fqpl_th_conns_def.append(parts_fqpl_th_conn)
                elif __depth_count(fqpl_th_conns_def_bool) == 2:  # this means that a boolean for each winding for each FQPL was provided. Allows to specify which FQPL is connected or not to which winding. This is most typical case.
                    if self.verbose:
                        print(f'Level 2 thermal connections definition specified.')
                    fqpl_th_conns_def = []
                    for fqpl_i in range(len(fqpl_th_conns_def_bool)):  # for each fqpl
                        parts_fqpl_th_conn = []
                        for p_go_ret_i in range(2):
                            winding_th_conns = []
                            for winding_i in range(len(n_turns_formers)):  # for each winding
                                tb_list = []
                                for tb_i in range(2):  # for top and bottom of the channel
                                    turn_list = []
                                    for wwn_i in range(wwns[winding_i]):  # for each turn in horizontal direction in the channel
                                        turn_list.append(fqpl_th_conns_def_bool[fqpl_i][p_go_ret_i])
                                    tb_list.append(turn_list)
                                winding_th_conns.append(tb_list)
                            parts_fqpl_th_conn.append(winding_th_conns)
                        fqpl_th_conns_def.append(parts_fqpl_th_conn)
                elif __depth_count(fqpl_th_conns_def_bool) == 3:  # this means that a boolean for each winding for each FQPL was provided. Allows to specify which FQPL is connected or not to which winding. This is most typical case.
                    if self.verbose:
                        print(f'Level 3 thermal connections definition specified.')
                    fqpl_th_conns_def = []
                    for fqpl_i in range(len(fqpl_th_conns_def_bool)):  # for each fqpl
                        parts_fqpl_th_conn = []
                        for p_go_ret_i in range(2):
                            winding_th_conns = []
                            for winding_i in range(len(n_turns_formers)):  # for each winding
                                tb_list = []
                                for tb_i in range(2):  # for top and bottom of the channel
                                    turn_list = []
                                    for wwn_i in range(wwns[winding_i]):  # for each turn in horizontal direction in the channel
                                        turn_list.append(fqpl_th_conns_def_bool[fqpl_i][p_go_ret_i][winding_i])  # [tb_i])
                                    tb_list.append(turn_list)
                                winding_th_conns.append(tb_list)
                            parts_fqpl_th_conn.append(winding_th_conns)
                        fqpl_th_conns_def.append(parts_fqpl_th_conn)
                elif __depth_count(fqpl_th_conns_def_bool) == 4:  # this means that a boolean for each winding for each FQPL was provided. Allows to specify which FQPL is connected or not to which winding. This is most typical case.
                    if self.verbose:
                        print(f'Level 4 thermal connections definition specified.')
                    fqpl_th_conns_def = []
                    for fqpl_i in range(len(fqpl_th_conns_def_bool)):  # for each fqpl
                        parts_fqpl_th_conn = []
                        for p_go_ret_i in range(2):
                            winding_th_conns = []
                            for winding_i in range(len(n_turns_formers)):  # for each winding
                                tb_list = []
                                for tb_i in range(2):  # for top and bottom of the channel
                                    turn_list = []
                                    for wwn_i in range(wwns[winding_i]):  # for each turn in horizontal direction in the channel
                                        turn_list.append(fqpl_th_conns_def_bool[fqpl_i][p_go_ret_i][winding_i][tb_i])
                                    tb_list.append(turn_list)
                                winding_th_conns.append(tb_list)
                            parts_fqpl_th_conn.append(winding_th_conns)
                        fqpl_th_conns_def.append(parts_fqpl_th_conn)
                elif __depth_count(fqpl_th_conns_def_bool) == 5:
                    print(f'Level 5 thermal connections definition specified.')
                    fqpl_th_conns_def = []
                    for fqpl_i in range(len(fqpl_th_conns_def_bool)):  # for each fqpl
                        for p_go_ret_i in range(2):
                            for winding_i in range(len(n_turns_formers)):  # for each winding
                                for tb_i in range(2):  # for top and bottom of the channel
                                    if len(fqpl_th_conns_def_bool[fqpl_i][p_go_ret_i][winding_i][tb_i]) != wwns[winding_i]:
                                        raise ValueError(
                                            f'List: {fqpl_th_conns_def_bool[fqpl_i][p_go_ret_i][winding_i][tb_i]} for fqpl: {fqpl_i}: {fqpl_names[fqpl_i]}, for {gr_dict[p_go_ret_i]} part, for winding: {winding_i}, for {tb_dict[tb_i]} turns has length {len(fqpl_th_conns_def_bool[fqpl_i][winding_i][tb_i])} and is not matching number of wires in channel: {wwns[winding_i]}')
                        fqpl_th_conns_def = fqpl_th_conns_def_bool

                # check if the above function produced fqpl_th_conns_def that is of the right shape
                for fqpl_i in range(len(fqpl_th_conns_def_bool)):  # for each fqpl
                    for winding_i, n_wires_width in enumerate(wwns):
                        for p_go_ret_i in range(2):
                            for tb_i in range(2):  # for top and bottom i.e. tb
                                if n_wires_width != len(fqpl_th_conns_def[fqpl_i][p_go_ret_i][winding_i][tb_i]):
                                    raise ValueError(f'Length of list {fqpl_th_conns_def[winding_i][tb_i]} in list {fqpl_th_conns_def} is {len(fqpl_th_conns_def[winding_i][tb_i])} and does not match {n_wires_width} wires in the width direction.')

                # make a list of lists of lists with fqpls electrical turns number (electrical and positional are the same for fqpls)
                turns_for_fqpl = []
                for fqpl_i in range(len(fqpl_names)):   # for each fqpl
                    parts_fqpl_th_conn = []
                    for p_go_ret_i in range(2):     # for go and return part of each fqpl
                        winding_layer = []
                        for winding_i, (n_w, n_h) in enumerate(zip(wwns, whns)):        # for each winding layer
                            top_bottom = []
                            for tb in range(2):                                         # for top and bottom of the channel
                                col_list = []
                                for i_w in range(n_w):                                  # for each column of wires in the channel
                                    col_list.append(i_w * n_h + 1 + tb * (n_h - 1) + n_w * n_h * winding_i)
                                top_bottom.append(col_list)
                            winding_layer.append(top_bottom)
                        parts_fqpl_th_conn.append(winding_layer)
                    turns_for_fqpl.append(parts_fqpl_th_conn)
                # print(th_conns_fqpl_def_1)

                # reshape turns_dict for more convenient looping later.
                for w_i in range(len(n_turns_formers)):
                    all_turns_list = []
                    for f_i in range(n_turns_formers[w_i]):
                        turns_for_turn = []
                        for w_i, w_turns in turns_dict.items():
                            turns_for_turn.extend(turns_dict[w_i][f_i])
                        all_turns_list.append(turns_for_turn)

                # print(all_turns_list)
                # print(th_conns_height)

                # combine thermal connections to a more convenient form to be used later.
                fqpl_th_conns_comb = []
                for fqpl_th_conn in fqpl_th_conns_def:
                    tb_cons = []
                    for cons in fqpl_th_conn:
                        tb_cons.extend(cons)
                    fqpl_th_conns_comb.append(tb_cons)

                fqpl_turn = 0
                for n_t, n_w, n_h in zip(n_turns_formers, wwns, whns):
                    fqpl_turn += n_t * n_w * n_h
                # print(fqpl_turn)
                self.fqpl_turns_refinement = []
                fqpl_turns_all = []
                for fqpl_i in range(len(fqpl_names)):
                    parts_fqpl_th_conn = []
                    for p_go_ret_i in range(2):
                        fqpl_turn += 1
                        parts_fqpl_th_conn.append(fqpl_turn)
                        self.fqpl_turns_refinement.append(fqpl_turn)
                    fqpl_turns_all.append(parts_fqpl_th_conn)
                # print(fqpl_turns_all)
                # print(fqpl_th_conns_def)
                # loop through windings and fqpls and get the turns that are connected from the fqpl_th_conns_def
                th_conns_width_fqpl = []       # set to self to make it available for assignCCTValuesWindings function
                for fqpl_turns, pos_turns_gr, fqpl_th_conns_gr in zip(fqpl_turns_all, turns_for_fqpl, fqpl_th_conns_def):
                    for winding_i, (fqpl_turn, pos_turns_winding, fqpl_th_conns_winding) in enumerate(zip(fqpl_turns, pos_turns_gr, fqpl_th_conns_gr)):
                        for pos_turns_tb, fqpl_th_conns_tb in zip(pos_turns_winding, fqpl_th_conns_winding):
                            for pos_turns_col, fqpl_th_conns_col in zip(pos_turns_tb, fqpl_th_conns_tb):
                                for pos_turn, fqpl_th_con_turn in zip(pos_turns_col, fqpl_th_conns_col):
                                    if fqpl_th_con_turn:
                                        for turn_number in range(n_turns_formers[winding_i]):
                                            turn_connected = all_turns_list[turn_number][pos_turn - 1]
                                            th_conns_width_fqpl.append([fqpl_turn, turn_connected])
            else:
                th_conns_width_fqpl = []
                self.fqpl_turns_refinement =[]  # no fqpls are defined or enabled so an empty array for looping below
            """
            These print statements contain all the connection pairs generated for CCT_straight.
            print(th_conns_width)
            print(th_conns_height)
            print(th_conns_width_fqpl)
            """
            # ---- connections along the width for windings and fqpls go together ----
            iContactAlongWidth_From = []
            iContactAlongWidth_To = []
            for contactPairAlongWidth in th_conns_width_fqpl:
                iContactAlongWidth_From.append(contactPairAlongWidth[0])
                iContactAlongWidth_To.append(contactPairAlongWidth[1])
            for contactPairAlongWidth in th_conns_width:
                iContactAlongWidth_From.append(contactPairAlongWidth[0])
                iContactAlongWidth_To.append(contactPairAlongWidth[1])


            self.setAttribute(self.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From, np.int32))
            self.setAttribute(self.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To, np.int32))

            # ---- connections along the height for windings only as not possible for fqpls ----
            iContactAlongHeight_From = []
            iContactAlongHeight_To = []
            for contactPairAlongHeight in th_conns_height:
                iContactAlongHeight_From.append(contactPairAlongHeight[0])
                iContactAlongHeight_To.append(contactPairAlongHeight[1])

            self.setAttribute(self.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From, np.int32))
            self.setAttribute(self.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To, np.int32))

        elif typeWindings in ['solenoid']:

            max_turn = 1
            physical_turns = []
            for ntpl in self.nT_solenoids:
                physical_turns.append(range(max_turn, max_turn+ntpl))
                max_turn = max_turn + ntpl

            iContactAlongWidth_From = []
            iContactAlongWidth_To = []
            for layer in physical_turns:
                for t_i in range(len(layer)-1):
                    iContactAlongWidth_From.append(layer[t_i])
                    iContactAlongWidth_To.append(layer[t_i+1])
            self.setAttribute(self.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From, np.int32))
            self.setAttribute(self.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To, np.int32))

            iContactAlongHeight_From = []
            iContactAlongHeight_To = []
            for l_i in range(len(physical_turns)-1):
                for t_i in range(len(physical_turns[l_i])):
                    iContactAlongHeight_From.append(physical_turns[l_i][t_i])
                    iContactAlongHeight_To.append(physical_turns[l_i+1][t_i])
            self.setAttribute(self.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From, np.int32))
            self.setAttribute(self.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To, np.int32))
        elif typeWindings in ['CWS']:
            # only initialize as connection are set manually in the input file
            iContactAlongWidth_From = []
            iContactAlongWidth_To = []
            iContactAlongHeight_From = []
            iContactAlongHeight_To = []
            self.fqpl_turns_refinement = []

        if self.verbose:
            print('Thermal links are set.')
            print('Heat exchange along the cable narrow side - Calculated indices:')
            print('iContactAlongWidth_From = ')
            print(iContactAlongWidth_From)
            print('iContactAlongWidth_To = ')
            print(iContactAlongWidth_To)
            print('iContactAlongHeight_From = ')
            print(iContactAlongHeight_From)
            print('iContactAlongHeight_To = ')
            print(iContactAlongHeight_To)

    def addThermalConnectionsCCT(self):
        """
        Function allowing to iContactAlongHeight_pairs_to_add and iContactAlongWidth_pairs_to_add to CCT magnets.
        These aditional thermal connection are not typically needed as BuilderLEDET takes care of setting them up for CCT mangtes.
        However if a manual addition is required this function provides this functionality. The pairs_to_add are added in frontt of existing connections.
        """
        iContactAlongHeight_From = []
        iContactAlongHeight_To = []
        for f, t in self.Auxiliary.iContactAlongHeight_pairs_to_add:
            iContactAlongHeight_From.append(f)
            iContactAlongHeight_To.append(t)
        iContactAlongWidth_From = []
        iContactAlongWidth_To = []
        for f, t in self.Auxiliary.iContactAlongWidth_pairs_to_add:
            iContactAlongWidth_From.append(f)
            iContactAlongWidth_To.append(t)
        iContactAlongHeight_From = iContactAlongHeight_From + self.Inputs.iContactAlongHeight_From.tolist()
        iContactAlongHeight_To = iContactAlongHeight_To + self.Inputs.iContactAlongHeight_To.tolist()
        iContactAlongWidth_From = iContactAlongWidth_From + self.Inputs.iContactAlongWidth_From.tolist()
        iContactAlongWidth_To = iContactAlongWidth_To + self.Inputs.iContactAlongWidth_To.tolist()
        self.setAttribute(self.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To, np.int32))

    def addThermalConnections(self):
        '''
            **Adding manually set thermal connections to the ones which where automatically calculated before**
        '''
        # Unpack variables
        pairs_to_add_along_height = self.Auxiliary.iContactAlongHeight_pairs_to_add
        pairs_to_add_along_width  = self.Auxiliary.iContactAlongWidth_pairs_to_add
        iContactAlongHeight_From  = self.Inputs.iContactAlongHeight_From
        iContactAlongHeight_To    = self.Inputs.iContactAlongHeight_To
        iContactAlongWidth_From   = self.Inputs.iContactAlongWidth_From
        iContactAlongWidth_To     = self.Inputs.iContactAlongWidth_To

        # check for pair repetition
        pairs_to_add_along_height = list(set(map(tuple, pairs_to_add_along_height)))
        pairs_to_add_along_width = list(set(map(tuple, pairs_to_add_along_width)))
        pairs_to_add_along_height.sort()
        pairs_to_add_along_width.sort()

        # Splitting pairs in two lists
        iContactAlongHeight_From_to_add = []
        iContactAlongHeight_To_to_add = []
        if len(pairs_to_add_along_height) != 0:
            for p in pairs_to_add_along_height:
                iContactAlongHeight_From_to_add.append(p[0])
                iContactAlongHeight_To_to_add.append(p[1])
        iContactAlongWidth_From_to_add = []
        iContactAlongWidth_To_to_add = []
        if len(pairs_to_add_along_width) != 0:
            for p in pairs_to_add_along_width:
                iContactAlongWidth_From_to_add.append(p[0])
                iContactAlongWidth_To_to_add.append(p[1])

        # Appending manually set thermal connections
        iContactAlongHeight_From = np.append(iContactAlongHeight_From, iContactAlongHeight_From_to_add)
        iContactAlongHeight_To = np.append(iContactAlongHeight_To, iContactAlongHeight_To_to_add)
        iContactAlongWidth_From = np.append(iContactAlongWidth_From, iContactAlongWidth_From_to_add)
        iContactAlongWidth_To = np.append(iContactAlongWidth_To, iContactAlongWidth_To_to_add)


        # Reorder both sets of indices
        idxSort = [i for (v, i) in sorted((v, i) for (i, v) in enumerate(iContactAlongWidth_From))]
        # reorder both iContactAlongWidth_From and iContactAlongHeight_To using the indices
        iContactAlongWidth_From = [iContactAlongWidth_From[i] for i in idxSort]
        iContactAlongWidth_To   = [iContactAlongWidth_To[i] for i in idxSort]

        idxSort = [i for (v, i) in sorted((v, i) for (i, v) in enumerate(iContactAlongHeight_From))]
        # reorder both iContactAlongHeight_From and iContactAlongHeight_To using the indices
        iContactAlongHeight_From = [iContactAlongHeight_From[i] for i in idxSort]
        iContactAlongHeight_To   = [iContactAlongHeight_To[i] for i in idxSort]

        # Remove duplicate pairs from both sets to avoid adding thermal links twice
        if len(iContactAlongWidth_From) == 0:
            iContactAlongWidth_From_without_duplicates = iContactAlongWidth_From
            iContactAlongWidth_To_without_duplicates   = iContactAlongWidth_To
        else:
            iContactAlongWidth_From_without_duplicates = [iContactAlongWidth_From[0]]
            iContactAlongWidth_To_without_duplicates   = [iContactAlongWidth_To[0]]
            for i in range(1, len(iContactAlongWidth_From)):  # Note: first element skipped
                if [iContactAlongWidth_From[i], iContactAlongWidth_To[i]] != [iContactAlongWidth_From[i-1], iContactAlongWidth_To[i-1]]:
                    iContactAlongWidth_From_without_duplicates.append(iContactAlongWidth_From[i])
                    iContactAlongWidth_To_without_duplicates.append(iContactAlongWidth_To[i])
        if len(iContactAlongHeight_From) == 0:
            iContactAlongHeight_From_without_duplicates = iContactAlongHeight_From
            iContactAlongHeight_To_without_duplicates   = iContactAlongHeight_To
        else:
            iContactAlongHeight_From_without_duplicates = [iContactAlongHeight_From[0]]
            iContactAlongHeight_To_without_duplicates   = [iContactAlongHeight_To[0]]
            for i in range(1, len(iContactAlongHeight_From)):  # Note: first element skipped
                if [iContactAlongHeight_From[i], iContactAlongHeight_To[i]] != [iContactAlongHeight_From[i-1], iContactAlongHeight_To[i-1]]:
                    iContactAlongHeight_From_without_duplicates.append(iContactAlongHeight_From[i])
                    iContactAlongHeight_To_without_duplicates.append(iContactAlongHeight_To[i])


        # Assign variables
        #if True:
        self.setAttribute(self.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From_without_duplicates, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To_without_duplicates, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From_without_duplicates, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To_without_duplicates, np.int32))

        if len(pairs_to_add_along_height) != 0:
            if self.verbose: print('Selected thermal links are added.')


    def removeThermalConnections(self, flag_plot: bool = False):
        '''
            *Removing manually set thermal connections from the ones which where automatically calculated before*
        '''
        # Unpack variables
        pairs_to_remove_along_height = self.Auxiliary.iContactAlongHeight_pairs_to_remove
        pairs_to_remove_along_width  = self.Auxiliary.iContactAlongWidth_pairs_to_remove
        iContactAlongHeight_From     = self.Inputs.iContactAlongHeight_From
        iContactAlongHeight_To       = self.Inputs.iContactAlongHeight_To
        iContactAlongWidth_From      = self.Inputs.iContactAlongWidth_From
        iContactAlongWidth_To        = self.Inputs.iContactAlongWidth_To

        # check for pair repetition
        pairs_to_remove_along_height = list(set(map(tuple, pairs_to_remove_along_height)))
        pairs_to_remove_along_width = list(set(map(tuple, pairs_to_remove_along_width)))
        pairs_to_remove_along_height.sort()
        pairs_to_remove_along_width.sort()

        # Splitting pairs in two lists
        iContactAlongHeight_From_to_remove = []
        iContactAlongHeight_To_to_remove = []
        if len(pairs_to_remove_along_height) != 0:
            for p in pairs_to_remove_along_height:
                iContactAlongHeight_From_to_remove.append(p[0])
                iContactAlongHeight_To_to_remove.append(p[1])
        iContactAlongWidth_From_to_remove = []
        iContactAlongWidth_To_to_remove = []
        if len(pairs_to_remove_along_width) != 0:
            for p in pairs_to_remove_along_width:
                iContactAlongWidth_From_to_remove.append(p[0])
                iContactAlongWidth_To_to_remove.append(p[1])

        # removing manually set thermal connections
        for i in range(len(pairs_to_remove_along_height)):
            for j in range(len(iContactAlongHeight_From)):
                if iContactAlongHeight_From[j-1] == pairs_to_remove_along_height[i][0] and iContactAlongHeight_To[j-1] == pairs_to_remove_along_height[i][1]:
                    iContactAlongHeight_From = np.delete(iContactAlongHeight_From, j-1)
                    iContactAlongHeight_To = np.delete(iContactAlongHeight_To, j-1)
        for i in range(len(pairs_to_remove_along_width)):
            for j in range(len(iContactAlongWidth_From)):
                if iContactAlongWidth_From[j-1] == pairs_to_remove_along_width[i][0] and iContactAlongWidth_To[j-1] == pairs_to_remove_along_width[i][1]:
                    iContactAlongWidth_From = np.delete(iContactAlongWidth_From, j-1)
                    iContactAlongWidth_To = np.delete(iContactAlongWidth_To, j-1)

        # Assign variables
        self.setAttribute(self.Inputs, 'iContactAlongHeight_From', np.array(iContactAlongHeight_From, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongHeight_To', np.array(iContactAlongHeight_To, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongWidth_From', np.array(iContactAlongWidth_From, np.int32))
        self.setAttribute(self.Inputs, 'iContactAlongWidth_To', np.array(iContactAlongWidth_To, np.int32))


        if len(pairs_to_remove_along_height) != 0:
            if self.verbose: print('Selected thermal links are removed.')

        if flag_plot:
            if self.model_data.GeneralParameters.magnet_type not in ['CCT_straight', 'CWS']:
                PM = PlotterModel(self.roxie_data)
                PM.plot_heat_connections(iContactAlongHeight_From, iContactAlongHeight_To, iContactAlongWidth_From, iContactAlongWidth_To, self.Auxiliary.x_strands, self.Auxiliary.y_strands, self.Auxiliary.strandToHalfTurn, self.model_data)


    def convert_QH_parameters(self, list_vars_to_convert: List[str] = ['type_ins_QH', 'type_ins_QH_He']):
        '''
        The material type of QH insulation layers can be defined either as string or as integer.
        If it is defined as string, this method will convert the values into integers.
        Values that are already numeric will not be converted.
        :param list_vars_to_convert: List of variables to convert. Bu default, the QH insulation layers on both sides
        are included.
        '''
        for var_name in list_vars_to_convert:
            var_value = getattr(self.Inputs, var_name)

            if isinstance(var_value[0], list):  # case 1: list of lists of strings
                for row, row_values in enumerate(var_value):
                    for col, col_value in enumerate(row_values):
                        if col_value.isnumeric():
                            var_value[row][col] = int(col_value)
                        else:
                            var_value[row][col] = DictionaryLEDET.lookupInsulation(col_value)
            else:  # case 2: list of strings
                for col, col_value in enumerate(var_value):
                    if col_value.isnumeric():
                        var_value[col] = int(col_value)
                    else:
                        var_value[col] = DictionaryLEDET.lookupInsulation(col_value)

            self.setAttribute(self.Inputs, var_name, np.array(var_value, np.int32))


    def calculateSelfMutualInductance(self, csv_write_path: str = ''):
        """
            Calculate the self-mutual inductance matrix
            Calculation based on the SMIC code (https://cernbox.cern.ch/index.php/s/37F87v3oeI2Gkp3)
        """
        # TODO: since many parameters, maybe access as .self when used instead of unpacking
        # TODO: however, should be stated, e.g. in docstring, which parameters needed from the outside in order to run
        name_magnet        = self.model_data.GeneralParameters.magnet_name
        nT                 = self.Inputs.nT
        nStrands_inGroup   = self.Auxiliary.nStrands_inGroup_ROXIE  # Note: This vector of number of strands in each group/block is read from the ROXIE map2d file, and it might differ from self.Inputs.nStrands_inGroup in case of Rutherford cables with an odd number of strands
        ds_inGroup         = self.Inputs.ds_inGroup
        hBare_inGroup      = self.Inputs.hBare_inGroup
        GroupToCoilSection = self.Inputs.GroupToCoilSection
        polarities_inGroup = self.Inputs.polarities_inGroup  # from map2d input file
        polarities_inGroup_from_yaml = self.model_data.CoilWindings.polarities_in_group  # from yaml input file
        if not polarities_inGroup == polarities_inGroup_from_yaml:
            raise Exception (f'polarities_inGroup differs from polarities_inGroup_from_yaml. {polarities_inGroup} versus {polarities_inGroup_from_yaml}')
        indexTstart        = self.Auxiliary.indexTstart
        indexTstop         = self.Auxiliary.indexTstop
        x_strands          = self.Auxiliary.x_strands
        y_strands          = self.Auxiliary.y_strands
        strandToHalfTurn   = self.Auxiliary.strandToHalfTurn
        nGroups, nHalfTurns, nStrands  = len(GroupToCoilSection), max(strandToHalfTurn), len(x_strands)

        # Set options
        flag_strandCorrection = 0
        flag_sumTurnToTurn = 1
        flag_writeOutput = 0

        # Calculate group to which each half-turn belongs
        HalfTurnToGroup = np.zeros((1, nHalfTurns), dtype=int)
        HalfTurnToGroup = HalfTurnToGroup[0]
        HalfTurnToCoilSection = np.zeros((1, nHalfTurns), dtype=int)
        HalfTurnToCoilSection = HalfTurnToCoilSection[0]
        for g in range(1, nGroups + 1):
            HalfTurnToGroup[indexTstart[g - 1] - 1:indexTstop[g - 1]] = g
            HalfTurnToCoilSection[indexTstart[g - 1] - 1:indexTstop[g - 1]] = GroupToCoilSection[g - 1]

        # Calculate group to which each strand belongs
        nS = np.repeat(nStrands_inGroup, nT)
        indexSstart = np.hstack([1, 1 + np.cumsum(nS[:-1])]).astype(int)
        indexSstop = np.cumsum(nS).astype(int)
        strandToGroup = np.zeros((1, nStrands), dtype=int)
        strandToGroup = strandToGroup[0]
        strandToCoilSection = np.zeros((1, nStrands), dtype=int)
        strandToCoilSection = strandToCoilSection[0]
        for ht in range(1, nHalfTurns + 1):
            strandToGroup[indexSstart[ht - 1] - 1:indexSstop[ht - 1]] = HalfTurnToGroup[ht - 1]
            strandToCoilSection[indexSstart[ht - 1] - 1:indexSstop[ht - 1]] = HalfTurnToCoilSection[ht - 1]

        polarities = np.repeat(polarities_inGroup, nT)
        polarities = np.repeat(polarities, nS.astype(int))
        for i in range(2):
            # Calculate diameter of each strand
            Ds = np.zeros((1, nStrands), dtype=float)
            Ds = Ds[0]
            for g in range(1, nGroups + 1):
                if i == 0: Ds[np.where(strandToGroup == g)] = ds_inGroup[g - 1]
                if i == 1: Ds[np.where(strandToGroup == g)] = hBare_inGroup[g - 1]

            # Define self-mutual inductance calculation object
            coil = SelfMutualInductanceCalculation(x_strands, y_strands, polarities,
                                                   nS, Ds, strandToHalfTurn, strandToCoilSection,
                                                   flag_strandCorrection, flag_sumTurnToTurn, flag_writeOutput,
                                                   name_magnet, verbose=self.verbose)

            # Calculate self-mutual inductance between half-turns, turns, and coil-sections, per unit length [H/m]
            M_halfTurns, M_turns, M_coilSections, L_magnet = \
                coil.calculateInductance(x_strands, y_strands, polarities,
                                         nS, Ds, strandToHalfTurn, strandToCoilSection,
                                         flag_strandCorrection=0)

            L_turns = M_turns
            L_turns_diag = np.diagonal(L_turns)
            L_turns_diag_rep = np.tile(L_turns_diag, (len(L_turns), 1))  # this replicates the effect of L_xx[i][i]
            denom_turns = np.sqrt(L_turns_diag_rep.T * L_turns_diag_rep)
            k_turns = L_turns / denom_turns  # matrix alt to k_turns[i][j]=L_turns[i][j]/np.sqrt(L_turns[j][j]*L_turns[i][i])

            # Check that the coupling factors are all higher than 1
            if len(k_turns[np.where(k_turns > 1)]) == 0:
                break
            else:
                assert max(nStrands_inGroup) == 1, 'Wires are not single stranded but mutual coupling factors k>1'
                print('Mutual coupling factors of some turns is k>1, re-calculate with hBare.')

        # Self-mutual inductances between coil sections, per unit length [H/m]
        self.setAttribute(self.Inputs, 'M_m', M_coilSections)

        # Self-mutual inductances between turns, per unit length [H/m]
        self.setAttribute(self.Inputs, 'M_InductanceBlock_m', M_turns)

        # Total magnet self-mutual inductance, per unit length [H/m]
        # L_magnet

        # Defining to which inductive block each half-turn belongs
        HalfTurnToInductanceBlock = np.concatenate((np.linspace(1, int(nHalfTurns / 2), int(nHalfTurns/2)),
                                                       np.linspace(1, int(nHalfTurns / 2), int(nHalfTurns/2))))
        self.setAttribute(self.Inputs, 'HalfTurnToInductanceBlock', HalfTurnToInductanceBlock)

        if self.verbose:
            print('')
            print('Total magnet self-inductance per unit length: ' + str(L_magnet) + ' H/m')

        # If self-mutual inductance matrix too large, set M_m to 0 and LEDET will read from the .csv file instead
        if M_turns.shape[0] >= 201:
            M_InductanceBlock_m = np.array([0])
            self.setAttribute(self.Inputs, 'M_InductanceBlock_m', M_InductanceBlock_m)  # TODO: change test_BuilderModel to reflect this change

        # If the csv_write_path is set to 'skip', no csv file will be written if M_turns.shape[0] >= 201.
        if str(csv_write_path).casefold()=='skip':
            if not M_turns.shape[0] >= 201:
                return
            else:
                csv_write_path = None

        # If not provided, use standard path - otherwise the provided path
        if not csv_write_path:
            csv_write_path = os.path.join(name_magnet + '_selfMutualInductanceMatrix.csv')
        with open(csv_write_path, 'w', newline='') as file:
            reader = csv.writer(file)
            reader.writerow(["Self- and mutual inductances per unit length between each turn [H/m]"])
            for i in range(M_turns.shape[0]):
                reader.writerow(M_turns[i])

    def setSelfMutualInductances(self):
        '''
        Assign self-mutual inductance parameters (this is used when inductance calculation is not enabled
        :return:
        '''

        # Defining to which inductive block each half-turn belongs
        nHalfTurns = sum(self.Inputs.nT)
        magnet_type = self.model_data.GeneralParameters.magnet_type
        if self.Auxiliary.overwrite_HalfTurnToInductanceBlock:
            HalfTurnToInductanceBlock = self.Auxiliary.overwrite_HalfTurnToInductanceBlock
        else:
            if magnet_type == 'multipole':
                HalfTurnToInductanceBlock = np.concatenate((np.linspace(1, int(nHalfTurns / 2), int(nHalfTurns / 2)), np.linspace(1, int(nHalfTurns / 2), int(nHalfTurns / 2))))
            elif (magnet_type == 'solenoid') or (magnet_type == 'busbar'):
                HalfTurnToInductanceBlock = np.linspace(1, int(nHalfTurns), int(nHalfTurns))
            elif magnet_type in ['CCT_straight']:
                # selfMutualInductanceMatrix_csv = Path.joinpath(self.path_input_file,
                #                                                f'{self.model_data.GeneralParameters.magnet_name}_selfMutualInductanceMatrix_{str(self.model_data.Options_LEDET.input_generation_options.selfMutualInductanceFileNumber)}.csv')
                # df = pd.read_csv(selfMutualInductanceMatrix_csv, delimiter=',', engine='python', skiprows = 1, header = None)
                # self.Auxiliary.overwrite_inductance_coil_sections = float(df.to_numpy().sum())  # [:-1] to remove last nan
                HalfTurnToInductanceBlock = []  # set to empty as it is later overwritten for CCT_straight by method self.assignCCTValuesWindings()
            elif magnet_type in ['CWS']:
                # selfMutualInductanceMatrix_csv = Path.joinpath(self.path_input_file,
                #                                                f'{self.model_data.GeneralParameters.magnet_name}_selfMutualInductanceMatrix_{str(self.model_data.Options_LEDET.input_generation_options.selfMutualInductanceFileNumber)}.csv')
                # df = pd.read_csv(selfMutualInductanceMatrix_csv, delimiter=',', engine='python', skiprows=1, header=None)
                # self.Auxiliary.overwrite_inductance_coil_sections = df.to_numpy()  # [:-1] to remove last nan
                # fL_I_fL_L_file = Path.joinpath(self.path_input_file,
                #                                f'{self.model_data.GeneralParameters.magnet_name}_fL_I_fL_L_{str(self.model_data.Options_LEDET.input_generation_options.selfMutualInductanceFileNumber)}.csv')
                # df_fL_I_fL_L = pd.read_csv(fL_I_fL_L_file, delimiter=',', engine='python')
                # self.setAttribute(self.Inputs, 'fL_I', df_fL_I_fL_L['fL_I'].to_numpy())
                # self.setAttribute(self.Inputs, 'fL_L', df_fL_I_fL_L['fL_L'].to_numpy())
                HalfTurnToInductanceBlock = []  # set to empty as it is later overwritten
            else:
                raise Exception(f'Magnet type not recognized: {magnet_type}.')

        # Self-mutual inductances between coil sections, per unit length [H/m]
        self.setAttribute(self.Inputs, 'M_m', self.Auxiliary.overwrite_inductance_coil_sections)
        self.setAttribute(self.Inputs, 'HalfTurnToInductanceBlock', HalfTurnToInductanceBlock)
        self.setAttribute(self.Inputs, 'M_InductanceBlock_m', 0)  # This entry will tell LEDET to read the turn-to-turn inductances from the auxiliary .csv file

    def assignDefaultValuesWindings(self):
        '''
        Assign default values to LEDET variables defining coil windings parameters
        This is useful when defining a LEDET model of a conductor (case_model='conductor'), which does not need coil windings parameters
        '''

        self.setAttribute(self.Inputs, 'GroupToCoilSection', 1)
        self.setAttribute(self.Inputs, 'polarities_inGroup', 1)
        self.setAttribute(self.Inputs, 'nT', 1)
        self.setAttribute(self.Inputs, 'l_mag_inGroup', self.model_data.GeneralParameters.length_busbar)

        self.setAttribute(self.Inputs, 'alphasDEG', 0)
        self.setAttribute(self.Inputs, 'rotation_block', 0)
        self.setAttribute(self.Inputs, 'mirror_block', 0)
        self.setAttribute(self.Inputs, 'mirrorY_block', 0)

        self.setAttribute(self.Inputs, 'el_order_half_turns', 1)

        self.setAttribute(self.Inputs, 'iContactAlongWidth_From', 1)
        self.setAttribute(self.Inputs, 'iContactAlongWidth_To', 1)
        self.setAttribute(self.Inputs, 'iContactAlongHeight_From', 1)
        self.setAttribute(self.Inputs, 'iContactAlongHeight_To', 1)

        if self.model_data.Circuit.L_circuit:
            L_circuit = self.model_data.Circuit.L_circuit
        else:
            L_circuit = 0.000001
        self.setAttribute(self.Inputs, 'M_m', L_circuit)
        self.setAttribute(self.Inputs, 'M_InductanceBlock_m', L_circuit)
        self.setAttribute(self.Inputs, 'HalfTurnToInductanceBlock', 1)
        self.setAttribute(self.Inputs, 'fL_I', np.array([0, 10000000000]))
        self.setAttribute(self.Inputs, 'fL_L', np.array([1, 1]))

    def assignSolenoidValuesWindings(self):

        force_tnt = True
        force_l = True

        conductors = []
        for coil_i, coil_d in enumerate(self.model_data.CoilWindings.solenoid.coils):
            conductor = self.model_data.Conductors[[cond.name for cond in self.model_data.Conductors].index(coil_d.conductor_name)]
            conductor.cable.th_insulation_along_width = conductor.cable.th_insulation_along_width + coil_d.pre_preg / 2
            winding_cell_rad_size = conductor.strand.bare_width + 2 * conductor.cable.th_insulation_along_width
            strand_ins_ax_size = conductor.strand.bare_height + 2 * conductor.cable.th_insulation_along_height

            try:
                coil_d.a1 = coil_d.a1
            except:
                ref_bloc_name = coil_d.a1
                coil_d.a1 = self.model_data.CoilWindings.solenoid.coils[ref_bloc_name]['a2']
            if force_tnt:
                #self.n_layers = coil_d.nl
                #self.n_turns_per_layer = coil_d.ntpl
                coil_d.a2 = coil_d.a1 + winding_cell_rad_size + coil_d.nl
                #self.solenoid_data['blocks'][block_name]['A2'] = self.solenoid_data['blocks'][block_name]['A1'] + winding_cell_rad_size * self.n_layers  # correct A2 to allow for defined number of layers
                if force_l:
                    strand_ins_ax_size = abs((coil_d.b2 - coil_d.b1)) / coil_d.ntpl  # correct insulation thickness in axial direction to allow for loos/tight wind
                    hIns_inGroup = (strand_ins_ax_size - conductor.strand.bare_height) / 2
                    if hIns_inGroup > 0:
                        conductor.cable.th_insulation_along_height = hIns_inGroup
                    else:
                        raise Exception(
                            f"Calculated hIns_inGroup for {coil_d.name} is {hIns_inGroup} and <0. Please check number of layers in the solenoid or switch to force_l = False")
                else:
                    coil_d.b2 = coil_d.b1 + strand_ins_ax_size * coil_d.ntpl  # adjust B2 to allow for larger wire - unrealistic as winding mandrel is usually fixed
            else:
                coil_d.nl = int(np.rint((coil_d.a2 - coil_d.a1) / winding_cell_rad_size))
                coil_d.ntpl = int(np.rint((coil_d.b2 - coil_d.b1) / strand_ins_ax_size))
            conductors.append(conductor)

            self.nT_solenoids.extend([coil_d.ntpl for _ in range(coil_d.nl)]) # for all coils in solenoid magnet

        self.sol_obj = Solenoid_magnet(self.model_data.CoilWindings.solenoid.coils, conductors, self.model_data.Options_LEDET.field_map_files.Iref)
        out_dir = os.path.join(self.path_input_file.parent, 'output')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        Ind_matrix_file = os.path.join(out_dir, f"{self.model_data.GeneralParameters.magnet_name}_selfMutualInductanceMatrix.csv")
        #if self.model_data.Options_LEDET.field_map_files.flag_calculateMagneticField:
        self.sol_obj.save_B_map(out_dir, self.model_data.GeneralParameters.magnet_name, self.model_data.Options_LEDET.field_map_files.fieldMapNumber)
        self.sol_obj.save_L_M(Ind_matrix_file)
        try:
            self.Inputs.M_m = np.loadtxt(Ind_matrix_file, delimiter=',', skiprows=1)
        except:
            raise ValueError(f'The file: {Ind_matrix_file} does not exist. Set Options_LEDET.field_map_files.flag_calculateMagneticField to 1 to calculate it.')
        seq = np.arange(self.sol_obj.section.size)
        sec_uni = list(np.int_(np.unique(self.sol_obj.section)))
        M_M = np.zeros_like(np.arange(len(sec_uni) ** 2).reshape(len(sec_uni), len(sec_uni)), dtype=np.float64)
        for sec_n in sec_uni:
            for sec_m in sec_uni:
                idx_n = seq[np.isin(self.sol_obj.section, sec_n)]
                idx_m = seq[np.isin(self.sol_obj.section, sec_m)]
                chunk = self.Inputs.M_m[np.ix_(idx_n, idx_m)]
                res = np.sum(chunk)
                M_M[sec_n - 1, sec_m - 1] = res
        self.Inputs.M_InductanceBlock_m = self.Inputs.M_m
        self.Inputs.M_m = M_M

        self.model_data.CoilWindings.conductor_to_group = np.ones_like(self.nT_solenoids, np.int32)
        self.setAttribute(self.Inputs, 'GroupToCoilSection', np.ones_like(self.nT_solenoids, np.int32))
        self.setAttribute(self.Inputs, 'polarities_inGroup', np.ones_like(self.nT_solenoids, np.int32))
        self.setAttribute(self.Inputs, 'nT', np.array(self.nT_solenoids, np.int32))
        self.setAttribute(self.Inputs, 'l_mag_inGroup', np.pi * (self.sol_obj.Rins + self.sol_obj.Routs))  # Length of turns of each layer

        self.setAttribute(self.Inputs, 'alphasDEG', np.zeros(np.sum(self.nT_solenoids), np.int32))
        self.setAttribute(self.Inputs, 'rotation_block', np.zeros(np.sum(self.nT_solenoids), np.int32))
        self.setAttribute(self.Inputs, 'mirror_block', np.zeros(np.sum(self.nT_solenoids), np.int32))
        self.setAttribute(self.Inputs, 'mirrorY_block', np.zeros(np.sum(self.nT_solenoids), np.int32))

        # -- electric order --
        el_order_half_turns = []
        turn = 0
        sign = 1
        HalfTurnToInductanceBlock = []
        for layer, turns_in_layer in enumerate(self.nT_solenoids):   # for each layer
            self.solenoid_layers.append([])
            for k in range(turns_in_layer): # for each turn in a layer
                turn = turn + sign     # simply add +1 or -1 depending on direction of winding
                self.solenoid_layers[layer].append(turn)
                HalfTurnToInductanceBlock.append(layer+1)
            turn = turn + turns_in_layer + sign   # after adding all the turns in a layer, make a jump by number of layers
            sign = -sign    # flip sign to go in opposite direction in the next layer
            el_order_half_turns.extend(self.solenoid_layers[layer])

        self.setAttribute(self.Inputs, 'el_order_half_turns', np.array(el_order_half_turns, np.int32))
        self.setAttribute(self.Inputs, 'HalfTurnToInductanceBlock', np.array(HalfTurnToInductanceBlock, np.int32))

    def assignCWSValuesWindings(self):
        """
        Function is specific to CCT magnets windings.
        It assigns values listed in list_of_attr_names below + it sets self.model_data.CoilWindings.conductor_to_group
        """
        wwns = self.model_data.Options_FiQuS.cws.solve.conductors.excitation.conductors_nw  # number of wires in width direction
        whns = self.model_data.Options_FiQuS.cws.solve.conductors.excitation.conductors_nh  # number of wires in height direction
        n_turns_formers = [1] * len(wwns)  # number of turns is always 1 as a single turn continues along the lenght of the former turns

        turn_to_inductance_block = []
        turn_number = 0
        for winding_i in range(len(n_turns_formers)):
            for _ in range(n_turns_formers[winding_i]):
                turn_number += 1
                for turn in range(wwns[winding_i] * whns[winding_i]):
                    turn_to_inductance_block.append(turn_number)

        nT = []
        n_turns_total = 0
        for winding_i, n_turns in enumerate(n_turns_formers):
            nT.append(n_turns * wwns[winding_i] * whns[winding_i])
            n_turns_total += n_turns * wwns[winding_i] * whns[winding_i]
        list_of_attr_names = [
            'nT',
            'nStrands_inGroup',
            'GroupToCoilSection',
            'polarities_inGroup',
            'l_mag_inGroup',
            'HalfTurnToInductanceBlock',
            'M_InductanceBlock_m'       # set this to M_m to avoid reading it from file by LEDET, (this overwrites zero set in setSelfMutualInductances method)
        ]
        list_of_attr_values = [
            np.array(nT, np.int32),
            np.ones_like(nT, np.int32),
            np.array(list(range(len(nT))))+1,   # set each group to belong to new coil section +1 as it needs to be 1 based
            np.ones_like(nT, np.int32),
            np.ones_like(nT, np.int32) * self.model_data.GeneralParameters.magnetic_length,
            np.array(turn_to_inductance_block, np.int32),
            np.array(self.Inputs.M_m)
        ]

        for attr_name, attr_value in zip(list_of_attr_names, list_of_attr_values):
            self.setAttribute(self.Inputs, attr_name, attr_value)
        self.model_data.CoilWindings.conductor_to_group = np.ones_like(nT, np.int32)

    def assignCCTValuesWindings(self):
        """
        Function is specific to CCT magnets windings.
        It assigns values listed in list_of_attr_names below + it sets self.model_data.CoilWindings.conductor_to_group
        """
        wwns = self.model_data.CoilWindings.CCT_straight.winding_numRowStrands  # number of wires in width direction
        whns = self.model_data.CoilWindings.CCT_straight.winding_numColumnStrands  # number of wires in height direction
        n_turns_formers = self.model_data.CoilWindings.CCT_straight.winding_numberTurnsFormers  # number of turns [-]
        fqpl_names = [val for val, flag in zip(self.model_data.Quench_Protection.FQPCs.names, self.model_data.Quench_Protection.FQPCs.enabled) if flag]

        turn_to_inductance_block = []
        turn_number = 0
        for winding_i in range(len(n_turns_formers)):
            for _ in range(n_turns_formers[winding_i]):
                turn_number += 1
                for turn in range(wwns[winding_i] * whns[winding_i]):
                    turn_to_inductance_block.append(turn_number)
        for _ in fqpl_names:
            turn_number += 1
            for turn in range(2):
                turn_to_inductance_block.append(turn_number)

        nT = []
        n_turns_total = 0
        for winding_i, n_turns in enumerate(n_turns_formers):
            nT.append(n_turns * wwns[winding_i] * whns[winding_i])
            n_turns_total += n_turns * wwns[winding_i] * whns[winding_i]
        for _ in fqpl_names:
            nT.append(2)
            n_turns_total += 2
        list_of_attr_names = [
            'nT',
            'nStrands_inGroup',
            'GroupToCoilSection',
            'polarities_inGroup',
            'l_mag_inGroup',
            'sim3D_f_cooling_down',
            'sim3D_f_cooling_up',
            'sim3D_f_cooling_left',
            'sim3D_f_cooling_right',
            'HalfTurnToInductanceBlock',
            'M_InductanceBlock_m'
        ]
        list_of_attr_values = [
            np.array(nT, np.int32),
            np.ones_like(nT, np.int32),
            np.array(np.ones_like(nT), np.int32),   # put all coils in on section, if more sections are created M_m for LEDET needs to be number of coil sections in rows and columns
            np.ones_like(nT, np.int32),
            np.ones_like(nT, np.int32) * self.model_data.GeneralParameters.magnetic_length,
            np.zeros(n_turns_total, np.int32),   # commenting this out means that they are passed withouth changing from the input file
            np.zeros(n_turns_total, np.int32),
            np.zeros(n_turns_total, np.int32),
            np.zeros(n_turns_total, np.int32),
            np.array(turn_to_inductance_block, np.int32),
            np.array(self.Inputs.M_m)
        ]

        for attr_name, attr_value in zip(list_of_attr_names, list_of_attr_values):
            self.setAttribute(self.Inputs, attr_name, attr_value)
        self.model_data.CoilWindings.conductor_to_group = np.ones_like(nT, np.int32)

    def assignCCTTurnsRefinement(self):
        """
        Function calculates and assigns sim3D_idxFinerMeshHalfTurn in optimal way for CCT type windings
        """

        sim3D_Tpulse_sPosition = self.model_data.Options_LEDET.simulation_3D.sim3D_Tpulse_sPosition

        field_map_3D_csv = Path.joinpath(self.path_input_file,
                                         f'{self.model_data.GeneralParameters.magnet_name}_{str(self.model_data.Options_LEDET.simulation_3D.sim3D_import3DGeometry_modelNumber)}.csv')
        print(f'Loading 3D magnetic field from: {field_map_3D_csv}')
        df = pd.read_csv(field_map_3D_csv, delimiter=',', engine='python')
        sAvePositions = df['sAvePositions [m]'].to_numpy(dtype='float')[:-1]  # [:-1] to remove last nan
        ph_order = df['nodeToPhysicalTurn [-]'].to_numpy(dtype='int')[:-1]  # physical turns, [:-1] to remove last nan
        el_order = df['nodeToHalfTurn [-]'].to_numpy(dtype='int')[:-1]  # electric order turns, [:-1] to remove last nan
        idx_of_sAvePosition = (np.abs(sAvePositions - sim3D_Tpulse_sPosition)).argmin()  # find index in csv by using sAvePosition closest to sim3D_Tpulse_sPosition

        electric_turns_unique = np.unique(el_order, return_index=True)[1]
        el_ord_csv = np.array([ph_order[index] for index in sorted(electric_turns_unique)], dtype=self.Inputs.el_order_half_turns.dtype)
        if np.shape(self.Inputs.el_order_half_turns)[0] != np.shape(el_ord_csv)[0]:   # check if they are the same length (method below will not be able to check if they are the same if they are diffrent length)
            raise ValueError(f'There is mismatch between length of electrical order calculated by BuilderLEDET: {np.shape(self.Inputs.el_order_half_turns)[0]} and in csv file: {np.shape(el_ord_csv)[0]}')
        if (self.Inputs.el_order_half_turns != el_ord_csv).all():
            raise ValueError(f'There is mismatch between electrical order calculated by BuilderLEDET: {self.Inputs.el_order_half_turns} and use used in csv file: {field_map_3D_csv} which has is: {el_ord_csv}')

        idxs_in_csv = []
        electric_turns_Tpulse = []
        electric_turn_Tpulse = el_order[idx_of_sAvePosition]  # get electrical turn number at idx_of_sAvePosition
        for turn in [-1, 0, 1]:  # refine turn the turn matching sim3D_Tpulse_sPosition and one before and one after in electrical order
            el_turns_considered = electric_turn_Tpulse + turn
            if el_turns_considered >0:
                electric_turns_Tpulse.append(el_turns_considered)  # put electric_turn_Tpulse and electrical turn before and after into this list
                idxs_in_csv.extend(np.where(el_turns_considered == el_order)[0])  # get indexes in csv file for electrical turns from electric_turns_Tpulse
        physical_turns_Tpulse = np.unique(ph_order[idxs_in_csv]).tolist()  # get physical turns numbers for the indexes

        # get electric turns that should be refined in the height and width direction
        ph_turns_height = []
        ph_turns_width = self.fqpl_turns_refinement   # take fqpl turn list to start with, this list is empty if no fqpls are used or enabled. electrical and physical order indexes are the same.
        for ph_turn in physical_turns_Tpulse:# electric_turns_Tpulse:
            ph_turns_height.extend(np.unique(self.Inputs.iContactAlongHeight_To[np.where(ph_turn == self.Inputs.iContactAlongHeight_From)[0]]).tolist())
            ph_turns_height.extend(np.unique(self.Inputs.iContactAlongHeight_From[np.where(ph_turn == self.Inputs.iContactAlongHeight_To)[0]]).tolist())
            ph_turns_width.extend(np.unique(self.Inputs.iContactAlongWidth_To[np.where(ph_turn == self.Inputs.iContactAlongWidth_From)[0]]).tolist())
            ph_turns_width.extend(np.unique(self.Inputs.iContactAlongWidth_From[np.where(ph_turn == self.Inputs.iContactAlongWidth_To)[0]]).tolist())
        sim3D_idxFinerMeshHalfTurn = np.unique(physical_turns_Tpulse + ph_turns_height + ph_turns_width)
        print(f'sim3D_idxFinerMeshHalfTurn: {sim3D_idxFinerMeshHalfTurn}')
        self.setAttribute(self.Inputs, 'sim3D_idxFinerMeshHalfTurn', sim3D_idxFinerMeshHalfTurn)

    def localsParser(self, locals: dict):
        """
            Sets parameters in LEDET from 'locals' dictionary
            :param locals: dictionary with LEDET parameters
        """
        for attribute in locals:
            if attribute in self.Inputs.__annotations__:
                group = self.Inputs
            elif attribute in self.Options.__annotations__:
                group = self.Options
            elif attribute in self.Plots.__annotations__:
                group = self.Plots
            elif attribute in self.Variables.__annotations__:
                group = self.Variables
            else:
                continue

            tt = type(self.getAttribute(group, attribute))
            if tt == np.ndarray and isinstance(locals[attribute], list):
                self.setAttribute(group, attribute, np.array(locals[attribute]))
            elif tt == np.ndarray and not isinstance(locals[attribute], np.ndarray):
                self.setAttribute(group, attribute, np.array([locals[attribute]]))
            else:
                self.setAttribute(group, attribute, locals[attribute])

    def printVariableDescNameValue(self, variableGroup, variableLabels):
        """

           **Print variable description, variable name, and variable value**

           Function prints variable description, variable name, and variable value

           :param variableGroup: Dataclass containing all the attributes of the LEDET object
           [obsolete, but still supported: list of tuples; each tuple has two elements: the first element is a string defining
           the variable name, and the second element is either an integer, a float, a list, or a numpy.ndarray
           defining the variable value :type variableGroup: list :param variableLabels: dictionary assigning a
           description to each variable name]
           :type variableLabels: dataclass [obsolete, but still supported: dict]

           :return: None

           [Example for usage of obsolete dictionary-version]
            import numpy as np
            variableGroup = []
            variableGroup.append( ('x1', 12) )
            variableGroup.append( ('x2', 23.42) )
            variableGroup.append( ('x3', [2, 4, 6]) )
            variableGroup.append( ('x3', np.array([2, 4, 6])) )
            variableLabels = {'x1': '1st variable', 'x2': '2nd variable', 'x3': '3rd variable'}
            utils.printVariableDescNameValue(variableGroup, variableLabels)
            # >>> 					1st variable x1 12
            # >>> 					2nd variable x2 23.42
            # >>> 					3rd variable x3 [2, 4, 6]
            # >>> 					3rd variable x3 [2 4 6]

        """
        if(variableGroup == asdict(self.Inputs)):
            variableGroup = self.Inputs
        if (variableGroup == asdict(self.Options)):
            variableGroup = self.Options
        if (variableGroup == asdict(self.Plots)):
            variableGroup = self.Plots
        if (variableGroup == asdict(self.Variables)):
            variableGroup = self.Variables

        if(type(variableGroup) != dict):
            for k in variableGroup.__annotations__:
                if k == 'overwrite_f_internalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
                if k == 'overwrite_f_externalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
                print(variableLabels[k])
                print(k, self.getAttribute(variableGroup, k))
        else:
            for k in variableGroup:
                if k == 'overwrite_f_internalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
                if k == 'overwrite_f_externalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
                print(variableLabels[k])
                print(k, variableGroup[k])

########################################################################################################################
# CLASS ENDS HERE - WHAT FOLLOWS IS A COPY/PASTE FROM PARAMETERS_LEDET TO INTEGRATE
########################################################################################################################


# class ParametersLEDET:
#     '''
#         Class of LEDET parameters
#     '''
#     def setAttribute(self, LEDETclass, attribute, value):
#         try:
#             setattr(LEDETclass, attribute, value)
#         except:
#             setattr(getattr(self, LEDETclass), attribute, value)
#
#     def getAttribute(self, LEDETclass, attribute):
#         try:
#             return getattr(LEDETclass, attribute)
#         except:
#             return getattr(getattr(self, LEDETclass), attribute)
#
#     def fillAttribute(self, LEDETclass, attribute, value):
#         imitate = self.getAttribute(LEDETclass, attribute)
#         if isinstance(imitate, np.ndarray) and isinstance(value, np.ndarray):
#             if imitate.shape != value.shape:
#                 imitate.resize(value.shape, refcheck=False)
#
#         idx_v = np.where(value != 0)
#         imitate[idx_v] = value[idx_v]
#         try:
#             setattr(LEDETclass, attribute, imitate)
#         except:
#             setattr(getattr(self, LEDETclass), attribute, imitate)
#
#
#     def __cpCu_nist_mat(self, T):
#         density = 8960
#         cpCu_perMass = np.zeros(T.size)
#         T[T < 4] = 4
#         idxT1 = np.where(T < 300)
#         idxT2 = np.where(T >= 300)
#         dc_a = -1.91844
#         dc_b = -0.15973
#         dc_c = 8.61013
#         dc_d = -18.996
#         dc_e = 21.9661
#         dc_f = -12.7328
#         dc_g = 3.54322
#         dc_h = -0.3797
#
#         logT1 = np.log10(T[idxT1])
#         tempVar = \
#         dc_a + dc_b * (logT1)**1 + dc_c * (logT1)**2 + dc_d * (logT1)**3 + \
#         dc_e * (logT1)**4 + dc_f * (logT1)**5 + dc_g * (logT1)** 6 + dc_h * (logT1)**7
#         cpCu_perMass[idxT1] = 10**tempVar
#
#         cpCu_perMass[idxT2]= 361.5 + 0.093 * T[idxT2]
#         cpCu = density * cpCu_perMass
#         return cpCu
#
#     def __rhoCu_nist(self, T, B, RRR, f_MR = 1):
#         B = abs(B)
#
#         idxLowB = np.where(B < 0.1)
#         idxHighB = np.where(B >= 0.1)
#
#         rho0 = 1.553e-8 / RRR
#         rhoi = 1.171e-17 * (T** 4.49) / (1 + 4.48e-7 * (T** 3.35) * np.exp(-(50. / T)** 6.428))
#         rhoiref = 0.4531 * rho0 * rhoi / (rho0 + rhoi)
#         rhcu = rho0 + rhoi + rhoiref
#         rhoCu = np.zeros(B.shape)
#         rhoCu[idxLowB] = rhcu[idxLowB]
#
#         lgs = 0.43429 * np.log(1.553E-8 * B[idxHighB] / rhcu[idxHighB])
#         polys = -2.662 + lgs * (0.3168 + lgs * (0.6229 + lgs  * (-0.1839 + lgs * 0.01827)))
#         corrs = (10.**polys)
#         rhoCu[idxHighB] = (1. + corrs * f_MR) * rhcu[idxHighB]
#         return rhoCu
#
#     def _rhoSS(self, T):
#         LimitValidityLow = 0
#         LimitValidityHigh = 300
#
#         fit_rho_SS_CERN = np.array([-6.16E-15, 3.52E-12, 1.72E-10, 5.43E-07]) / 1.0867
#         fit_rho_SS_CERN_linearExtrapolation = np.array([7.24E-10, 5.2887E-7]) / 1.0867
#
#         rhoSS = 0
#         if T < LimitValidityLow:
#             rhoSS = np.polyval(fit_rho_SS_CERN, LimitValidityLow)
#         elif T >= LimitValidityLow and T <= LimitValidityHigh:
#             rhoSS = np.polyval(fit_rho_SS_CERN, T)
#         elif T > LimitValidityHigh:
#             rhoSS = np.polyval(fit_rho_SS_CERN_linearExtrapolation, T)
#         return rhoSS
#
#     def __kCu_WiedemannFranz(self, rhoCu, T):
#         L0 = 2.45E-8
#         kCu = L0 * T / rhoCu
#         return kCu
#
#     def __kG10(self, T):
#         kG10 = np.zeros(T.size)
#         LimitValidity = 500
#         idxT1 = np.where(T <= LimitValidity)
#         idxT2 = np.where(T > LimitValidity)
#
#         a, b, c, d, e, f, g, h = -4.1236, 13.788, -26.068, 26.272, -14.663, 4.4954, -0.6905, 0.0397
#         logT = np.log10(T[idxT1])
#         logk = a + b * logT + c * logT**2 + d * logT**3 + e * logT**4 + f * logT**5 + g * logT**6 + h * logT**7
#         kG10[idxT1] = 10**logk
#
#         logLimitValidity = np.log10(LimitValidity)
#         logkLimitValidity = a + b * logLimitValidity + c * logLimitValidity**2 + d * logLimitValidity**3 + e * logLimitValidity**4 + \
#         f * logLimitValidity**5 + g * logLimitValidity**6 + h * logLimitValidity**7;
#         kG10[idxT2] = 10**logkLimitValidity
#         return kG10
#
#     def __cpG10(self, T):
#         density, a0, a1, a2, a3, a4, a5, a6, a7 = 1900, -2.4083, 7.6006, -8.2982, 7.3301, -4.2386, 1.4294, -0.24396, 0.015236
#         logT = np.log10(T)
#         p = 10**(a7 * ((logT)**7) + a6 * ((logT)**6) + a5 * ((logT)**5) + a4 * ((logT)**4) + a3 * ((logT)**3) + a2 * (
#                     (logT)**2) + a1 * ((logT)) + a0)
#         cpG10 = density * p
#         return cpG10
#
#     def __kKapton(self, T):
#         kKapton = np.zeros(T.size)
#         idxLow = np.where(T < 4.3)
#         if idxLow:
#             kKapton[idxLow[0]] = 0.010703 - 0.00161 * (4.3 - T[idxLow[0]])
#         idxHigh = np.where(T >= 4.3)
#         if idxHigh:
#             a, b, c, d, e, f, g, h = 5.73101, -39.5199, 79.9313, -83.8572, 50.9157, -17.9835, 3.42413, -0.27133
#             logT = np.log10(T)
#             logk = a + b * logT + c * logT**2 + d * logT**3 + e * logT**4 + f * logT**5 + g * logT**6 + h * logT**7
#             kKapton[idxHigh[0]] = 10**logk[idxHigh[0]]
#         return kKapton
#
#     def __cpKapton(self, T):
#         density, a0, a1, a2, a3, a4, a5, a6, a7 = 1420, -1.3684, 0.65892, 2.8719, 0.42651, -3.0088, 1.9558, -0.51998, 0.051574
#         logT = np.log10(T)
#         p = 10**(a7 * ((logT)**7) + a6 * ((logT)**6) + a5 * ((logT)**5) + a4 * ((logT)**4) + a3 * (
#                     (logT)**3) + a2 * ((logT)**2) + a1 * ((logT)) + a0)
#         cpKapton = density * p
#         return cpKapton
#
#     def __cpNbTi_cudi_mat(self, T, B):
#         Tc0 = 9.2
#         Bc20 = 14.5
#         alpha = .59
#         B[B>= Bc20] = Bc20-10E-4
#
#         Tc = Tc0 * (1 - B / Bc20)**alpha
#         cpNbTi = np.zeros(T.size)
#
#         idxT1 = np.where(T <= Tc)
#         idxT2 = np.where((T > Tc) & (T <= 20.0))
#         idxT3 = np.where((T > 20) & (T <= 50))
#         idxT4 = np.where((T > 50) & (T <= 175))
#         idxT5 = np.where((T > 175) & (T <= 500))
#         idxT6 = np.where((T > 500) & (T <= 1000))
#         idxT7 = np.where(T > 1000)
#
#         p1 = [0.00000E+00,    4.91000E+01,   0.00000E+00,   6.40000E+01,  0.00000E+00]
#         p2 = [0.00000E+00,   1.62400E+01,   0.00000E+00,  9.28000E+02,   0.00000E+00]
#         p3 = [-2.17700E-01,   1.19838E+01,   5.53710E+02, - 7.84610E+03,  4.13830E+04]
#         p4 = [-4.82000E-03,  2.97600E+00, -7.16300E+02,  8.30220E+04,  -1.53000E+06]
#         p5 = [-6.29000E-05, 9.29600E-02, -5.16600E+01,  1.37060E+04,  1.24000E+06]
#         p6 = [0.00000E+00, 0.00000E+00,  -2.57000E-01,  9.55500E+02,  2.45000E+06]
#         p7 = [0, 0, 0, 0, 3.14850E+06]
#
#         cpNbTi[idxT1] = p1[0] * T[idxT1]**4 + p1[1] * T[idxT1]**3 + p1[2] * T[idxT1]**2 + p1[3] * T[idxT1] + p1[4]
#         cpNbTi[idxT2] = p2[0] * T[idxT2]**4 + p2[1] * T[idxT2]**3 + p2[2] * T[idxT2]**2 + p2[3] * T[idxT2] + p2[4]
#         cpNbTi[idxT3] = p3[0] * T[idxT3]**4 + p3[1] * T[idxT3]**3 + p3[2] * T[idxT3]**2 + p3[3] * T[idxT3] + p3[4]
#         cpNbTi[idxT4] = p4[0] * T[idxT4]**4 + p4[1] * T[idxT4]**3 + p4[2] * T[idxT4]**2 + p4[3] * T[idxT4] + p4[4]
#         cpNbTi[idxT5] = p5[0] * T[idxT5]**4 + p5[1] * T[idxT5]**3 + p5[2] * T[idxT5]**2 + p5[3] * T[idxT5] + p5[4]
#         cpNbTi[idxT6] = p6[0] * T[idxT6]**4 + p6[1] * T[idxT6]**3 + p6[2] * T[idxT6]**2 + p6[3] * T[idxT6] + p6[4]
#         cpNbTi[idxT7] = p7[0] * T[idxT7]**4 + p7[1] * T[idxT7]**3 + p7[2] * T[idxT7]**2 + p7[3] * T[idxT7] + p7[4]
#         return cpNbTi
#
#     def __cpNb3Sn_alternative_mat(self, T, B, Tc0_Nb3Sn, Bc20_Nb3Sn):
#         B[B < .001] = 0.001
#         cpNb3Sn = np.zeros(T.shape)
#         alpha = .59
#         Tc = Tc0_Nb3Sn * (1 - B / Bc20_Nb3Sn)** alpha
#         density = 8950.0 # [kg / m ^ 3]
#
#         idxT0 = np.where(T <= Tc)
#         idxT1 = np.where((T > Tc) & (T <= 20))
#         idxT2 = np.where((T > 20) & (T <= 400))
#         idxT3 = np.where(T > 400)
#
#
#         betaT = 1.241E-3 # [J / K ^ 4 / kg]
#         gammaT = .138 # [J / K ^ 2 / kg]
#
#         if len(B) > 1 and len(Tc0_Nb3Sn) > 1:
#             cpNb3Sn[idxT0] = (betaT + 3 * gammaT / Tc0_Nb3Sn[idxT0]** 2) * T[idxT0]** 3 + gammaT* B[idxT0] / Bc20_Nb3Sn[idxT0] * T[idxT0]
#         elif len(B) > 1:
#             cpNb3Sn[idxT0] = (betaT + 3 * gammaT / Tc0_Nb3Sn** 2) * T[idxT0]**3 + gammaT * B[idxT0] / Bc20_Nb3Sn * T[idxT0]
#         elif len(Tc0_Nb3Sn) > 1:
#             cpNb3Sn[idxT0] = (betaT + 3 * gammaT / Tc0_Nb3Sn[idxT0]** 2) * T[idxT0]**3 + gammaT * B / Bc20_Nb3Sn[idxT0] * T[idxT0]
#         elif len(B) == 1 and len(Tc0_Nb3Sn) == 1:
#             cpNb3Sn[idxT0] = (betaT + 3 * gammaT / Tc0_Nb3Sn**2) * T[idxT0]**3 + gammaT * B / Bc20_Nb3Sn * T[idxT0]
#
#         cpNb3Sn[idxT1] = betaT * T[idxT1]**3 + gammaT * T[idxT1]
#         polyFit_20K_400K = [0.1662252, -0.6827738, -6.3977, 57.48133, -186.90995, 305.01434, -247.44839, 79.78547]
#         logT = np.log10(T[idxT2])
#         logCp2 = np.polyval(polyFit_20K_400K, logT)
#         cpNb3Sn[idxT2] = 10** logCp2
#
#         log400K = np.log10(400)
#         logCp400K = np.polyval(polyFit_20K_400K, log400K)
#         cpNb3Sn[idxT3] = 10**logCp400K
#         cpNb3Sn = cpNb3Sn * density
#         return cpNb3Sn
#
#     def __Jc_Nb3Sn_Summer(self, T, B, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn):
#         if type(T)== int or type(T)== float:
#             T = np.repeat(T, len(Jc_Nb3Sn0)).astype(float)
#
#         B[abs(B) < .001] = 0.001
#         T[T < 0.001] = 0.001
#         f_T_T0 = T / Tc0_Nb3Sn
#         f_T_T0[f_T_T0 > 1] = 1
#         Bc2 = Bc20_Nb3Sn * (1 - f_T_T0**2) * (1 - 0.31 * f_T_T0**2 * (1 - 1.77 * np.log(f_T_T0)))
#         f_B_Bc2 = B / Bc2
#         f_B_Bc2[f_B_Bc2 > 1] = 1
#         Jc_T_B = Jc_Nb3Sn0 / np.sqrt(B) * (1 - f_B_Bc2)**2 * (1 - f_T_T0** 2)**2
#         return Jc_T_B
#
#     def __Tc_Tcs_Nb3Sn_approx(self, J, B, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn):
#         J = abs(J)
#         B = abs(B)
#
#         f_B_Bc2 = B / Bc20_Nb3Sn
#         f_B_Bc2[f_B_Bc2 > 1] = 1
#         Tc = Tc0_Nb3Sn * (1 - f_B_Bc2)**.59
#
#         Jc0 = self.__Jc_Nb3Sn_Summer(0, B, Jc_Nb3Sn0, Tc0_Nb3Sn, Bc20_Nb3Sn)
#         f_J_Jc0 = J/ Jc0
#         f_J_Jc0[f_J_Jc0 > 1] = 1
#
#         Tcs = (1 - f_J_Jc0) * Tc
#         return [Tc, Tcs]
#
#     def _obtainThermalConnections(self):
#         # Calculate group to which each half-turn belongs
#         nHalfTurnsDefined = len(self.Inputs.HalfTurnToInductanceBlock)
#         indexTstart = np.hstack([1, 1 + np.cumsum(self.Inputs.nT[:-1])]).astype(int)
#         indexTstop = np.cumsum(self.Inputs.nT).astype(int)
#         HalfTurnToGroup = np.zeros((1, nHalfTurnsDefined), dtype=int)
#         HalfTurnToGroup = HalfTurnToGroup[0]
#         for g in range(1, len(self.Inputs.nT) + 1):
#             HalfTurnToGroup[indexTstart[g - 1] - 1:indexTstop[g - 1]] = g
#
#         # Obtain all thermal connections of each turn and store them in dictionaries for width and height
#         # First width
#         th_con_w = {}
#         for i in range(1, len(self.Inputs.HalfTurnToInductanceBlock) + 1):
#             con_list = []
#             iWidthFrom = np.where(self.Inputs.iContactAlongWidth_From == i)
#             if iWidthFrom: con_list = con_list + self.Inputs.iContactAlongWidth_To[iWidthFrom[0]].astype(int).tolist()
#             iWidthTo = np.where(self.Inputs.iContactAlongWidth_To == i)
#             if iWidthTo: con_list = con_list + self.Inputs.iContactAlongWidth_From[iWidthTo[0]].astype(int).tolist()
#             th_con_w[str(i)] = con_list
#
#         # Then height
#         th_con_h = {}
#         for i in range(1, len(self.Inputs.HalfTurnToInductanceBlock) + 1):
#             con_list = []
#             iHeightFrom = np.where(self.Inputs.iContactAlongHeight_From == i)
#             if iHeightFrom: con_list = con_list + self.Inputs.iContactAlongHeight_To[iHeightFrom[0]].astype(
#                 int).tolist()
#             iHeightTo = np.where(self.Inputs.iContactAlongHeight_To == i)
#             if iHeightTo: con_list = con_list + self.Inputs.iContactAlongHeight_From[iHeightTo[0]].astype(int).tolist()
#             th_con_h[str(i)] = con_list
#         return [HalfTurnToGroup, th_con_w, th_con_h]
#
#     def __calculateTransversalDelay(self, cp, kIns, Tc, Tcs, T_bath):
#         [HalfTurnToGroup, th_con_w, th_con_h] = self._obtainThermalConnections()
#         # Use dictionaries to calculate the transversal quench delay into each direction based on respective properties
#         delta_t_w = {}
#         delta_t_h = {}
#         for i in range(1,len(self.Inputs.HalfTurnToInductanceBlock)+1):
#             con = th_con_h[str(i)]
#             delta_t_h_temp = []
#             for k in range(len(con)):
#                 idx_con1 = HalfTurnToGroup[k-1]-1
#                 idx_con2 = HalfTurnToGroup[con[k]-1]-1
#                 T_temp = 1
#                 delta_t = cp[idx_con2] / kIns[idx_con2] * (
#                             self.Inputs.wBare_inGroup[idx_con2] + 2 * self.Inputs.wIns_inGroup[idx_con2]) \
#                           * (self.Inputs.wIns_inGroup[idx_con2] + self.Inputs.wIns_inGroup[idx_con1]) * T_temp
#                 delta_t_h_temp.append(delta_t)
#             delta_t_h[str(i)] = delta_t_h_temp
#
#             con = th_con_w[str(i)]
#             delta_t_w_temp = []
#             for k in range(len(con)):
#                 idx_con1 = HalfTurnToGroup[k - 1] - 1
#                 idx_con2 = HalfTurnToGroup[con[k]-1]-1
#                 T_temp = (Tcs[idx_con2]-T_bath)/(Tc[idx_con1]-(Tcs[idx_con2]+T_bath)/2)
#                 delta_t = cp[idx_con2] / kIns[idx_con2] * (
#                             self.Inputs.hBare_inGroup[idx_con2] + 2 * self.Inputs.hIns_inGroup[idx_con2]) \
#                           * (self.Inputs.hIns_inGroup[idx_con2] + self.Inputs.hIns_inGroup[idx_con1]) * T_temp
#                 delta_t_w_temp.append(delta_t)
#             delta_t_w[str(i)] = delta_t_w_temp
#
#         return [HalfTurnToGroup, th_con_h, delta_t_h, th_con_w, delta_t_w]
#
#     def _quenchPropagationVelocity(self, I, B, T_bath, cable):
#         # Calculate Quench propagation velocity
#         L0 = 2.44E-08
#         A_CableBare = cable.A_CableInsulated * (cable.f_SC + cable.f_ST)
#         f_SC_inStrand = cable.f_SC / (cable.f_SC + cable.f_ST)
#         f_ST_inStrand = cable.f_ST / (cable.f_SC + cable.f_ST)
#         I = abs(I)
#         J_op = I / A_CableBare
#
#         idxNbTi = np.where(np.repeat(self.Inputs.SCtype_inGroup,self.Inputs.nT.astype(int)) == 1)[0]
#         idxNb3Sn = np.where(np.repeat(self.Inputs.SCtype_inGroup,self.Inputs.nT.astype(int)) == 2)[0]
#         idxCu_ST = np.where(np.repeat(self.Inputs.STtype_inGroup,self.Inputs.nT.astype(int)) == 1)[0]
#
#         Tc = np.zeros(B.shape)
#         Tcs = np.zeros(B.shape)
#         if len(idxNbTi)>0:
#             Tc[idxNbTi] = cable.Tc0_NbTi[idxNbTi] * (1 - B / cable.Bc20_NbTi[idxNbTi]) ** cable.alpha_NbTi
#             Tcs[idxNbTi] = (1 - I / (cable.c1_Ic_NbTi[idxNbTi] + cable.c2_Ic_NbTi[idxNbTi] * B[idxNbTi])) * Tc[idxNbTi]
#         if len(idxNb3Sn) > 0:
#             [Tc[idxNb3Sn], Tcs[idxNb3Sn]] = self.__Tc_Tcs_Nb3Sn_approx(I / cable.A_SC[idxNb3Sn], B[idxNb3Sn],
#                                                                 cable.Jc_Nb3Sn0[idxNb3Sn], cable.Tc0_Nb3Sn[idxNb3Sn],
#                                                                 cable.Bc20_Nb3Sn[idxNb3Sn])
#
#         Ts = (Tcs + Tc) / 2
#         cp_ST = np.zeros(B.shape)
#         cp_ST[idxCu_ST] = self.__cpCu_nist_mat(Ts[idxCu_ST])
#         cp_SC = np.zeros(B.shape)
#         if len(idxNbTi) > 0:
#             cp_SC[idxNbTi] = self.__cpNbTi_cudi_mat(Ts[idxNbTi], B[idxNbTi])
#         if len(idxNb3Sn) > 0:
#             cp_SC[idxNb3Sn] = self.__cpNb3Sn_alternative_mat(Ts[idxNb3Sn], B[idxNb3Sn], cable.Tc0_Nb3Sn[idxNb3Sn], cable.Bc20_Nb3Sn[idxNb3Sn])
#         cp = cp_ST * f_ST_inStrand + cp_SC * f_SC_inStrand
#         vQ = J_op / cp * ((L0 * Ts) / (Ts - T_bath))**0.5
#         idxInfQuenchVelocity=np.where(Tcs <= T_bath)
#         vQ[idxInfQuenchVelocity]=1E6
#
#         ### Calculate MPZ
#         rhoCu = np.zeros(A_CableBare.shape)
#         kCu = np.zeros(A_CableBare.shape)
#         RRR = np.repeat(self.Inputs.RRR_Cu_inGroup, self.Inputs.nT.astype(int))
#         rhoCu[idxCu_ST] = self.__rhoCu_nist(Ts[idxCu_ST], B[idxCu_ST], RRR[idxCu_ST])
#         kCu[idxCu_ST] = self.__kCu_WiedemannFranz(rhoCu[idxCu_ST], Ts[idxCu_ST])
#         l = np.zeros(A_CableBare.shape)
#         l[idxCu_ST] = np.sqrt((2 * kCu[idxCu_ST] * (Tc[idxCu_ST] - T_bath)) / (J_op[idxCu_ST]** 2 * rhoCu[idxCu_ST]))
#
#         # Calculate thermal conductivity of insulations
#         idxKapton = np.where(self.Inputs.insulationType_inGroup == 2, 1, 0)
#         idxKapton = np.where(np.repeat(idxKapton, self.Inputs.nT.astype(int))==1)[0]
#         idxG10 = np.where(self.Inputs.insulationType_inGroup == 1, 1, 0)
#         idxG10 = np.where(np.repeat(idxG10, self.Inputs.nT.astype(int))==1)[0]
#         kIns = np.zeros(Ts.size)
#         kIns[idxKapton] = self.__kKapton(Ts[idxKapton])
#         kIns[idxG10] = self.__kG10(Ts[idxG10])
#         cpIns = np.zeros(Ts.size)
#         cpIns[idxKapton] = self.__cpKapton(Ts[idxKapton])
#         cpIns[idxG10] = self.__cpG10(Ts[idxG10])
#         cp_full = (cp* (A_CableBare/cable.A_CableInsulated) + cpIns*(1-A_CableBare/cable.A_CableInsulated))/2
#
#         ### Calculate delta T transversal
#         [HalfTurnToGroup, th_con_h, delta_t_h, th_con_w, delta_t_w] = self.__calculateTransversalDelay(cp_full, kIns, Tc, Tcs, T_bath)
#         return [vQ, l, HalfTurnToGroup, th_con_h, delta_t_h, th_con_w, delta_t_w]
#
#     def __reorderROXIEFiles(self, ROXIE_File):
#         orderedROXIE = []
#         for i in range(len(ROXIE_File)-1):
#             prefix = 'E'+str(i)
#             for j in range(len(ROXIE_File)):
#                 if prefix in ROXIE_File[j]:
#                     orderedROXIE.append(ROXIE_File[j])
#         for j in range(len(ROXIE_File)):
#             if 'All_WithIron_WithSelfField' in ROXIE_File[j]:
#                 orderedROXIE.append(ROXIE_File[j])
#         return orderedROXIE
#
#     def _acquireBField(self, ROXIE_File):
#         if ROXIE_File.endswith('.map2d'):
#             ROXIE_File = [ROXIE_File]
#             N = 1
#         else:
#             ROXIE_File1 = [f for f in os.listdir(ROXIE_File) if os.path.isfile(os.path.join(ROXIE_File, f))]
#             ROXIE_File1 = [f for f in ROXIE_File1 if f.endswith('.map2d')]
#             ROXIE_File1 = [f for f in ROXIE_File1 if 'WithIron' in f]
#             ROXIE_File1 = [f for f in ROXIE_File1 if not 'ROXIE' in f]
#             for i in range(len(ROXIE_File1)):
#                 ROXIE_File1[i] = os.path.join(ROXIE_File, ROXIE_File1[i])
#             ROXIE_File = ROXIE_File1
#             ROXIE_File = self.__reorderROXIEFiles(ROXIE_File)
#             N = len(ROXIE_File)
#             if N>1:
#                 print('Reading ', N, ' Field maps. This may take a while.')
#             else:
#                 print('Reading Field map.')
#
#         for i in trange(N, file=sys.stdout, desc='Field maps'):
#             Inom = self.Options.Iref
#             reader = csv.reader(open(ROXIE_File[i]))
#             B_Field = np.array([])
#             stack = 0
#             for row in reader:
#                 if not row: continue
#                 row_s = np.array(row[0].split())
#                 if not stack:
#                     B_Field = np.array(row_s[1:])
#                     stack = 1
#                 else:
#                     B_Field = np.vstack((B_Field, np.array(row_s)))
#             B_Field = B_Field[1:].astype(float)
#             if i == 0:
#                 BX = (B_Field[:, 5].transpose()/ Inom)
#                 BY = (B_Field[:, 6].transpose()/ Inom)
#             elif i == N-1:
#                 BX_All = B_Field[:, 5].transpose()
#                 BY_All = B_Field[:, 6].transpose()
#             else:
#                 BX = BX + (B_Field[:, 5].transpose() / Inom)
#                 BY = BY + (B_Field[:, 6].transpose() / Inom)
#         f_mag = (BX** 2 + BY** 2) ** 0.5
#         if N>1:
#             B_E_All = (BX_All** 2 + BY_All** 2) ** 0.5
#             peakB_Superposition = max(f_mag * Inom)
#             peakB_Real = max(B_E_All)
#             f_peakReal_peakSuperposition = peakB_Real / peakB_Superposition
#         else: f_peakReal_peakSuperposition = 1
#
#         B = f_mag*self.Inputs.I00*f_peakReal_peakSuperposition
#
#         B[B > 10E6]=10E-6
#         return B
#
#     def __repeatCable(self, cable):
#         nT = self.Inputs.nT
#         nT = nT.astype(int)
#         newCable = Cable()
#         for attribute in cable.__annotations__:
#             if attribute == 'alpha_NbTi': continue
#             x = np.ndarray([])
#             x = getattr(cable, attribute)
#             x = np.repeat(x, nT)
#             setattr(newCable, attribute, x)
#         return newCable
#
#     def calculateQuenchDetectionTime(self, Type, B, vQ_iStartQuench, lengthHotSpot_iStartQuench, HalfTurnToGroup, th_con_h, delta_t_h, th_con_w, delta_t_w, uQuenchDetectionThreshold = 0.1):
#         if not (Type=='Short' or Type=='Long'):
#             print("Don't understand type of quench detection time calculation. Please choose either 'Short' or 'Long'[incl. transversal propagation]")
#             print("Let's continue with 'Short'.")
#             Type = 'Short'
#         # Calculate resistance of each turn at T=10 K
#         rho_Cu_10K = 1.7E-10  # [Ohm*m] Approximate Cu resistivity at T=10 K, B=0, for RRR=100
#         rho_Cu_10K_B = 4E-11  # [Ohm*m/T] Approximate Cu magneto-resistivity factor
#         Iref = self.Options.Iref
#         nStrands_inGroup = self.Inputs.nStrands_inGroup
#         ds_inGroup = self.Inputs.ds_inGroup
#         f_SC_strand_inGroup = self.Inputs.f_SC_strand_inGroup
#         nHalfTurns = len(vQ_iStartQuench)
#
#         tQuenchDetection = []
#         r_el_m = np.zeros((nHalfTurns,))
#         for ht in range(1, nHalfTurns + 1):
#             current_group = HalfTurnToGroup[ht - 1]
#             mean_B = B / Iref * self.Inputs.I00  # average magnetic field in the current half-turn
#             rho_mean = rho_Cu_10K + rho_Cu_10K_B * mean_B[ht-1]  # average resistivity in the current half-turn
#             cross_section = nStrands_inGroup[current_group - 1] * np.pi / 4 * ds_inGroup[current_group - 1] ** 2 * (1 - f_SC_strand_inGroup[current_group - 1])
#             r_el_m[ht - 1] = rho_mean / cross_section # Electrical resistance per unit length
#             if Type == 'Short':
#                 UQD_i = (self.Inputs.I00 * r_el_m[ht - 1] * lengthHotSpot_iStartQuench[ht - 1])
#                 tQD = (uQuenchDetectionThreshold - UQD_i) / (vQ_iStartQuench[ht - 1] * r_el_m[ht - 1] * self.Inputs.I00)
#                 tQuenchDetection = np.hstack([tQuenchDetection, np.array(tQD)])
#
#         r_el_m = r_el_m.transpose()
#         if Type == 'Long':
#             for ht in range(1, nHalfTurns + 1):
#                 for ht in range(1, nHalfTurns + 1):
#                     # Approximate time to reach the quench detection threshold
#                     UQD_i = (self.Inputs.I00 * r_el_m[ht - 1] * lengthHotSpot_iStartQuench[ht - 1])
#                     tQD = (uQuenchDetectionThreshold - UQD_i) / (vQ_iStartQuench[ht - 1] * r_el_m[ht - 1] * self.Inputs.I00)
#                     delay = np.concatenate((np.array(delta_t_w[str(ht)]), np.array(delta_t_h[str(ht)])), axis=None)
#                     th_con = np.concatenate((np.array(th_con_w[str(ht)]), np.array(th_con_h[str(ht)])), axis=None).astype(int)
#                     tQD_i = tQD
#                     t_i0 = 0
#                     t_i1 = 0
#                     idx_turns = np.array([ht - 1])
#                     quenched_turns = [ht]
#                     delay[delay > tQD_i] = 9999
#
#                     while np.any(delay < 999):
#                         idx = np.argmin(delay)
#                         if th_con[idx] in quenched_turns:
#                             delay[idx] = 9999
#                             continue
#                         else:
#                             quenched_turns.append(int(th_con[idx]))
#                         UQD_i = UQD_i + np.sum(self.Inputs.I00 * r_el_m[idx_turns] * (t_i1 - t_i0) * vQ_iStartQuench[idx_turns])
#                         idx_turns = np.append(idx_turns, int(th_con[idx] - 1))
#                         t_i1 = delay[idx]
#                         tQD_i = (uQuenchDetectionThreshold - UQD_i) / (
#                                 np.sum(vQ_iStartQuench[idx_turns] * r_el_m[idx_turns] * self.Inputs.I00))
#                         t_i0 = t_i1
#                         delay = np.concatenate((delay, np.array(delta_t_w[str(int(th_con[idx]))] + t_i1),
#                                                     np.array(delta_t_h[str(int(th_con[idx]))] + t_i1)), axis=None)
#                         th_con = np.concatenate((th_con, np.array(th_con_w[str(int(th_con[idx]))]),
#                                                  np.array(th_con_h[str(int(th_con[idx]))])),axis=None)
#                         delay[delay > tQD_i] = 9999
#                         delay[idx] = 9999
#                 tQuenchDetection = np.hstack([tQuenchDetection, np.array(tQD_i)])
#         print('Minimum quench detection time would be {} ms [{} calculation]'.format(round(min(tQuenchDetection),3)*1000, Type))
#         return min(tQuenchDetection)
#
#     def getBField(self, ROXIE_File):
#         B = self._acquireBField(ROXIE_File)
#         strandCount = 0
#         GroupCount = 0
#         nStrands_inGroup = self.Inputs.nStrands_inGroup
#         ds_inGroup = self.Inputs.ds_inGroup
#         if any(nStrands_inGroup % 2 == 1) and any(nStrands_inGroup != 1):
#             for g in range(len(self.Inputs.nT)):
#                 if (nStrands_inGroup[g] % 2 == 1) & (nStrands_inGroup[g] > 1):
#                     ds_inGroup[g] = ds_inGroup[g] * np.sqrt(nStrands_inGroup[g] / (nStrands_inGroup[g] - 1))
#                     nStrands_inGroup[g] = nStrands_inGroup[g] - 1
#
#         Bcopy = np.zeros(int(sum(self.Inputs.nT)))
#         for i in range(int(sum(self.Inputs.nT))):
#             Bcopy[i] = sum(B[int(strandCount):int(strandCount + nStrands_inGroup[GroupCount])]) / nStrands_inGroup[
#                 int(GroupCount)]
#             TurnSum = sum(self.Inputs.nT[0:GroupCount + 1])
#             strandCount = strandCount + nStrands_inGroup[GroupCount]
#             if i > TurnSum: GroupCount = GroupCount + 1
#         return Bcopy
#
#     def adjust_vQ(self, ROXIE_File, Transversaldelay  = False, ManualB = '', CurrentsInCoilsections = []):
#         cable = Cable()
#         cable.A_CableInsulated = (self.Inputs.wBare_inGroup+2*self.Inputs.wIns_inGroup) \
#                                * (self.Inputs.hBare_inGroup+2*self.Inputs.hIns_inGroup)
#         if len(ManualB)==0: B = self._acquireBField(ROXIE_File)
#         else: B = ManualB
#
#         if max(self.Inputs.nStrands_inGroup) > 1:
#             strandCount = 0
#             GroupCount = 0
#             nStrands_inGroup = self.Inputs.nStrands_inGroup
#             ds_inGroup = self.Inputs.ds_inGroup
#             if any(nStrands_inGroup % 2 == 1) and any(nStrands_inGroup != 1):
#                 for g in range(len(self.Inputs.nT)):
#                     if (nStrands_inGroup[g] % 2 == 1) & (nStrands_inGroup[g] > 1):
#                         ds_inGroup[g] = ds_inGroup[g] * np.sqrt(nStrands_inGroup[g] / (nStrands_inGroup[g] - 1))
#                         nStrands_inGroup[g] = nStrands_inGroup[g] - 1
#             if len(ManualB)==0:
#                 Bcopy = np.zeros(int(sum(self.Inputs.nT)))
#                 for i in range(int(sum(self.Inputs.nT))):
#                     Bcopy[i] = sum(B[int(strandCount):int(strandCount+nStrands_inGroup[GroupCount])])/nStrands_inGroup[int(GroupCount)]
#                     TurnSum = sum(self.Inputs.nT[0:GroupCount+1])
#                     strandCount = strandCount + nStrands_inGroup[GroupCount]
#                     if i>TurnSum: GroupCount = GroupCount + 1
#                 B = Bcopy
#
#             cable.f_SC = self.Inputs.f_SC_strand_inGroup * \
#                          (nStrands_inGroup* (np.pi/4)*(ds_inGroup**2)) / cable.A_CableInsulated
#             cable.f_ST = (1 - self.Inputs.f_SC_strand_inGroup) * \
#                          (nStrands_inGroup* (np.pi/4)*(ds_inGroup**2)) / cable.A_CableInsulated
#         else:
#             cable.f_SC = self.Inputs.f_SC_strand_inGroup * \
#                          (self.Inputs.wBare_inGroup * self.Inputs.hBare_inGroup) / cable.A_CableInsulated
#             cable.f_ST = (1 - self.Inputs.f_SC_strand_inGroup) * \
#                          (self.Inputs.wBare_inGroup * self.Inputs.hBare_inGroup) / cable.A_CableInsulated
#
#         T_bath = self.Inputs.T00
#         cable.A_SC =cable.A_CableInsulated * cable.f_SC
#         cable.SCtype = self.Inputs.SCtype_inGroup
#         cable.STtype = self.Inputs.STtype_inGroup
#         cable.Tc0_NbTi = self.Inputs.Tc0_NbTi_ht_inGroup
#         cable.Bc20_NbTi = self.Inputs.Bc2_NbTi_ht_inGroup
#         cable.c1_Ic_NbTi = self.Inputs.c1_Ic_NbTi_inGroup
#         cable.c2_Ic_NbTi = self.Inputs.c2_Ic_NbTi_inGroup
#         cable.alpha_NbTi = .59
#         cable.Jc_Nb3Sn0 = self.Inputs.Jc_Nb3Sn0_inGroup
#         cable.Tc0_Nb3Sn = self.Inputs.Tc0_Nb3Sn_inGroup
#         cable.Bc20_Nb3Sn = self.Inputs.Bc2_Nb3Sn_inGroup
#         cable = self.__repeatCable(cable)
#
#         th_con_h = []
#         th_con_w = []
#         if len(CurrentsInCoilsections)>0:
#             if np.max(self.Inputs.GroupToCoilSection) != len(CurrentsInCoilsections):
#                 print('You assigned ', len(CurrentsInCoilsections),' currents in the coilsections, but there are ',
#                       np.max(self.Inputs.GroupToCoilSection), ' Coil-sections. Abort!')
#                 return
#
#             vQ_copy = np.linspace(0, len(cable.A_CableInsulated), len(cable.A_CableInsulated))
#             TurnToCoilSection = np.repeat(self.Inputs.GroupToCoilSection, self.Inputs.nT.astype(int))
#             for i in range(len(CurrentsInCoilsections)):
#                 I = CurrentsInCoilsections[i]
#                 B_copy = B/ self.Inputs.I00 * I
#                 [vQ, l, HalfTurnToGroup, th_con_h, delta_t_h, th_con_w, delta_t_w] = \
#                     self._quenchPropagationVelocity(I, B_copy, T_bath, cable)
#
#                 idx_cs = np.where(TurnToCoilSection == i+1)[0]
#                 vQ_copy[idx_cs] = vQ[idx_cs]
#             vQ = vQ_copy
#         else:
#             I = self.Inputs.I00
#             [vQ, l, HalfTurnToGroup, th_con_h, delta_t_h, th_con_w, delta_t_w] = self._quenchPropagationVelocity(I, B, T_bath, cable)
#
#         # self.setAttribute(getattr(self, "Inputs"), "vQ_iStartQuench", vQ)
#         # self.setAttribute(getattr(self, "Inputs"), "lengthHotSpot_iStartQuench", l)
#         self.setAttribute(getattr(self, "Inputs"), "fScaling_vQ_iStartQuench", np.ones(len(vQ)))
#
#         if Transversaldelay:
#             if len(CurrentsInCoilsections)>0:
#                 print('Multiple currents in the coilsections are not supported for calculation of quench detection times. I use I_nom.')
#             tQD = self.calculateQuenchDetectionTime(Transversaldelay, B, vQ, l, HalfTurnToGroup, th_con_h, delta_t_h,
#                                               th_con_w, delta_t_w, uQuenchDetectionThreshold = 0.1)
#             return [l, tQD]
#         else:
#             return vQ, l
#
#     def adjust_vQ_QuenchHeater(self, th_con_h, th_con_w, NHeatingStations):
#         idx_turns_2x = np.array([])
#         activatedStrips = np.where(self.Inputs.tQH < 999)[0]+1
#         idx_turns_2x = np.append(idx_turns_2x, activatedStrips)
#
#         for i in activatedStrips:
#             idx_new_turns = np.where(self.Inputs.iQH_toHalfTurn_From == i)[0]
#             idx_turns_2x = np.append(idx_turns_2x, self.Inputs.iQH_toHalfTurn_To[idx_new_turns])
#         idx_turns_2x = idx_turns_2x.astype(int)
#         for j in range(5):
#             for i in idx_turns_2x:
#                 if str(i) in th_con_h.keys():
#                     for k in th_con_h[str(i)]:
#                         if k not in idx_turns_2x:
#                             idx_turns_2x = np.append(idx_turns_2x, k)
#                 if str(i) in th_con_w.keys():
#                     for k in th_con_w[str(i)]:
#                         if k not in idx_turns_2x:
#                             idx_turns_2x = np.append(idx_turns_2x, k)
#         idx_turns_2x = idx_turns_2x.astype(int)-1
#         self.Inputs.vQ_iStartQuench[idx_turns_2x] = self.Inputs.vQ_iStartQuench[idx_turns_2x] * NHeatingStations * 2
#         if len(self.Inputs.lengthHotSpot_iStartQuench) != len(self.Inputs.vQ_iStartQuench):
#             self.Inputs.lengthHotSpot_iStartQuench = np.array([0.01]*len(self.Inputs.vQ_iStartQuench))
#         if type(self.Inputs.lengthHotSpot_iStartQuench) != np.ndarray:
#             self.Inputs.lengthHotSpot_iStartQuench = np.array(self.Inputs.lengthHotSpot_iStartQuench)
#         #self.Inputs.lengthHotSpot_iStartQuench[idx_turns_2x] = np.array([0.01*NHeatingStations]*len(idx_turns_2x))
#         self.Inputs.lengthHotSpot_iStartQuench[idx_turns_2x] = np.array([self.Inputs.l_magnet*self.Inputs.f_QH[0]]*len(idx_turns_2x))
#         return
#
#     def setConductorResistanceFraction(self, f_RRR1_Cu_inGroup=0.3, f_RRR2_Cu_inGroup=0.3, f_RRR3_Cu_inGroup=0.2,
#               RRR1_Cu_inGroup=100, RRR2_Cu_inGroup=100, RRR3_Cu_inGroup=100):
#         """
#             **enables and sets values for resistance parameters. Afterwards, will be included when writing to file**
#         """
#
#         print('Conductor resistance fraction enabled.')
#
#         self.enableConductorResistanceFraction = True
#
#         self.Inputs.f_RRR1_Cu_inGroup = f_RRR1_Cu_inGroup
#         self.Inputs.f_RRR2_Cu_inGroup = f_RRR2_Cu_inGroup
#         self.Inputs.f_RRR3_Cu_inGroup = f_RRR3_Cu_inGroup
#
#         self.Inputs.RRR1_Cu_inGroup = RRR1_Cu_inGroup
#         self.Inputs.RRR2_Cu_inGroup = RRR2_Cu_inGroup
#         self.Inputs.RRR3_Cu_inGroup = RRR3_Cu_inGroup
#
#         self.descriptionsInputs['f_RRR1_Cu_inGroup'] = 'Description ...'
#         self.descriptionsInputs['f_RRR2_Cu_inGroup'] = 'Description ...'
#         self.descriptionsInputs['f_RRR3_Cu_inGroup'] = 'Description ...'
#
#         self.descriptionsInputs['RRR1_Cu_inGroup'] = 'Description ...'
#         self.descriptionsInputs['RRR2_Cu_inGroup'] = 'Description ...'
#         self.descriptionsInputs['RRR3_Cu_inGroup'] = 'Description ...'
#
#     def setHeliumFraction(self, PercentVoids):
#         if np.max(self.Inputs.nStrands_inGroup)==1:
#             print('You are about to set a helium-fraction for a single-stranded wire!')
#
#         if not isinstance(self.Inputs.wBare_inGroup, np.ndarray):
#             self.Inputs.wBare_inGroup = np.array(self.Inputs.wBare_inGroup)
#         if not isinstance(self.Inputs.hBare_inGroup, np.ndarray):
#             self.Inputs.hBare_inGroup = np.array(self.Inputs.hBare_inGroup)
#         if not isinstance(self.Inputs.wIns_inGroup, np.ndarray):
#             self.Inputs.wIns_inGroup = np.array(self.Inputs.wIns_inGroup)
#         if not isinstance(self.Inputs.hIns_inGroup, np.ndarray):
#             self.Inputs.hIns_inGroup = np.array(self.Inputs.hIns_inGroup)
#         if not isinstance(self.Inputs.ds_inGroup, np.ndarray):
#             self.Inputs.ds_inGroup = np.array(self.Inputs.ds_inGroup)
#         if not isinstance(self.Inputs.nStrands_inGroup, np.ndarray):
#             self.Inputs.nStrands_inGroup = np.array(self.Inputs.nStrands_inGroup)
#
#         cs_bare = self.Inputs.wBare_inGroup*self.Inputs.hBare_inGroup
#         cs_ins = (self.Inputs.wBare_inGroup +2*self.Inputs.wIns_inGroup)* \
#                 (self.Inputs.hBare_inGroup +2*self.Inputs.hIns_inGroup)
#         cs_strand = self.Inputs.nStrands_inGroup*np.pi*(self.Inputs.ds_inGroup**2)/4
#         strand_total = cs_strand/cs_ins
#         ins_total = (cs_ins - cs_bare)/cs_ins
#         VoidRatio = (cs_bare - cs_strand)/cs_ins
#         extVoids = VoidRatio - (PercentVoids/100.0)
#         if any(sV < 0 for sV in extVoids):
#             print("Negative externalVoids calculated. Abort, please check.")
#             return
#         nGroups = len(self.Inputs.nT)
#         self.Inputs.overwrite_f_externalVoids_inGroup = extVoids
#         self.Inputs.overwrite_f_internalVoids_inGroup = np.ones((nGroups,)).transpose()*(PercentVoids/100.0)
#
#         self.descriptionsInputs['overwrite_f_externalVoids_inGroup'] = 'Helium fraction in the external cable voids'
#         self.descriptionsInputs['overwrite_f_internalVoids_inGroup'] = 'Helium fraction in the internal cable voids'
#
#     def preparePersistentCurrents(self, I_PC_LUT, dIdt, timeStep):
#         # LUT controlling power supply, Current [A]. Two cycles of ramping from 0 to nominal current and back to zero
#         if isinstance(I_PC_LUT,list):
#             I_PC_LUT = np.array(I_PC_LUT)
#         self.Inputs.I_PC_LUT = I_PC_LUT
#         self.Inputs.I00 = 0
#
#         # LUT controlling power supply, Time [s]
#         t_PC_LUT = np.zeros(len(self.Inputs.I_PC_LUT))
#         # Generates a time LUT that is dependent on the ramp rate of the current.
#         for x in range(len(self.Inputs.I_PC_LUT)):
#             if x == 0:  t_PC_LUT[x] = 0
#             elif x == 1: t_PC_LUT[x] = 0.1
#             elif x % 2 == 1: t_PC_LUT[x] = t_PC_LUT[x - 1] + 1
#             elif x % 4 == 0:
#                 t_PC_LUT[x] = t_PC_LUT[x - 1] - (self.Inputs.I_PC_LUT[x] - self.Inputs.I_PC_LUT[x - 1]) / dIdt
#             elif (x + 2) % 4 == 0:
#                 t_PC_LUT[x] = t_PC_LUT[x - 1] + (self.Inputs.I_PC_LUT[x] - self.Inputs.I_PC_LUT[x - 1]) / dIdt
#             else: continue
#         self.Inputs.t_PC_LUT =  t_PC_LUT
#
#         # time vector - Generates a time vector with finer timestepping when the ramp rate of the current changes
#         nElements = (len(self.Inputs.I_PC_LUT)-2)*6+3
#         time_vector_params = np.zeros(nElements)
#         every_sixth_element = range(nElements-3)[::6]
#         for x in every_sixth_element:
#             time_vector_params[x] = time_vector_params[x - 1] + timeStep
#             time_vector_params[x + 1] = timeStep
#             time_vector_params[x + 2] = t_PC_LUT[(x // 6) + 1] - 0.02
#             time_vector_params[x + 3] = time_vector_params[x + 2] + 0.001
#             time_vector_params[x + 4] = 0.001
#             time_vector_params[x + 5] = time_vector_params[x + 2] + 0.04
#         time_vector_params[0] = 0
#         time_vector_params[1] = 0.010
#         time_vector_params[-1] = t_PC_LUT[-1]
#         time_vector_params[-2] = timeStep
#         time_vector_params[-3] = time_vector_params[-4]+timeStep
#         self.Options.time_vector_params = time_vector_params
#
#         # Changes in options
#         if np.all(self.Inputs.f_SC_strand_inGroup == self.Inputs.f_SC_strand_inGroup[0]):
#             self.Options.flag_hotSpotTemperatureInEachGroup = 0
#         else:
#             self.Options.flag_hotSpotTemperatureInEachGroup = 0
#         self.Options.minCurrentDiode = 0
#         self.Options.flag_persistentCurrents = 1
#
#         # Changes in input
#         self.Inputs.t_PC = 99999
#         self.Inputs.tQH = np.array([99999]*len(self.Inputs.tQH))
#         self.Inputs.tEE = 99999
#         self.Inputs.tQuench = np.array([t_PC_LUT[-2]]*len(self.Inputs.M_m))
#         self.Inputs.tStartQuench = np.array([99999]*len(self.Inputs.tStartQuench))
#
#         selectedFont = {'fontname': 'DejaVu Sans', 'size': 14}
#         plt.figure(figsize=(5, 5))
#         plt.plot(self.Inputs.t_PC_LUT, self.Inputs.I_PC_LUT, 'ro-', label='LUT')
#         plt.xlabel('Time [s]', **selectedFont)
#         plt.ylabel('Current [A]', **selectedFont)
#         plt.title('Look-up table controlling power supply', **selectedFont)
#         plt.grid(True)
#         plt.rcParams.update({'font.size': 12})
#         plt.show()
#
#
#     def printVariableDescNameValue(self, variableGroup, variableLabels):
#         """
#
#            **Print variable description, variable name, and variable value**
#
#            Function prints variable description, variable name, and variable value
#
#            :param variableGroup: Dataclass containing all the attributes of the LEDET object
#            [obsolete, but still supported: list of tuples; each tuple has two elements: the first element is a string defining
#            the variable name, and the second element is either an integer, a float, a list, or a numpy.ndarray
#            defining the variable value :type variableGroup: list :param variableLabels: dictionary assigning a
#            description to each variable name]
#            :type variableLabels: dataclass [obsolete, but still supported: dict]
#
#            :return: None
#
#            [Example for usage of obsolete dictionary-version]
#             import numpy as np
#             variableGroup = []
#             variableGroup.append( ('x1', 12) )
#             variableGroup.append( ('x2', 23.42) )
#             variableGroup.append( ('x3', [2, 4, 6]) )
#             variableGroup.append( ('x3', np.array([2, 4, 6])) )
#             variableLabels = {'x1': '1st variable', 'x2': '2nd variable', 'x3': '3rd variable'}
#             utils.printVariableDescNameValue(variableGroup, variableLabels)
#             # >>> 					1st variable x1 12
#             # >>> 					2nd variable x2 23.42
#             # >>> 					3rd variable x3 [2, 4, 6]
#             # >>> 					3rd variable x3 [2 4 6]
#
#         """
#         if(variableGroup == asdict(self.Inputs)):
#             variableGroup = self.Inputs
#         if (variableGroup == asdict(self.Options)):
#             variableGroup = self.Options
#         if (variableGroup == asdict(self.Plots)):
#             variableGroup = self.Plots
#         if (variableGroup == asdict(self.Variables)):
#             variableGroup = self.Variables
#
#         if(type(variableGroup) != dict):
#             for k in variableGroup.__annotations__:
#                 if k == 'overwrite_f_internalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
#                 if k == 'overwrite_f_externalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
#                 print(variableLabels[k])
#                 print(k, self.getAttribute(variableGroup, k))
#         else:
#             for k in variableGroup:
#                 if k == 'overwrite_f_internalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
#                 if k == 'overwrite_f_externalVoids_inGroup' and len(self.getAttribute(variableGroup, k))==0: continue
#                 print(variableLabels[k])
#                 print(k, variableGroup[k])

