import math

import pandas as pd

from steam_sdk.data import DictionaryPyBBQ
from steam_sdk.data.DataModelConductor import DataModelConductor
from steam_sdk.data.DataPyBBQ import DataPyBBQ



class BuilderPyBBQ:
    """
        Class to generate PyBBQ models
    """

    def __init__(self,
                 input_model_data: DataModelConductor = None,
                 flag_build: bool = True,
                 verbose: bool = True):
        """
            Object is initialized by defining PyBBQ variable structure and file template.
            Optionally, the argument model_data can be passed to read the variables of a BuilderModel object.
            If flagInstantBuild is set to True, the PyBBQ input file is generated.
            If verbose is set to True, additional information will be displayed
        """
        # Unpack arguments
        self.verbose: bool = verbose
        self.model_data: DataModelConductor = input_model_data

        # Data structure
        self.data_PyBBQ = DataPyBBQ()

        if not self.model_data and flag_build:
            raise Exception('Cannot build model instantly without providing DataModelMagnet')

        if flag_build:
            # Add method to translate all PyBBQ parameters from model_data to PyBBQ dataclasses
            self.translateModelDataToPyBBQ()

            # Load conductor data from DataModelMagnet keys, and calculate+set relevant parameters
            self.loadConductorData()


    def setAttribute(self, PyBBQclass, attribute: str, value):
        try:
            setattr(PyBBQclass, attribute, value)
        except:
            setattr(getattr(self, PyBBQclass), attribute, value)


    def getAttribute(self, PyBBQclass, attribute):
        try:
            return getattr(PyBBQclass, attribute)
        except:
            return getattr(getattr(self, PyBBQclass), attribute)


    def translateModelDataToPyBBQ(self):
        """"
            Translates and sets parameters in self.DataModelMagnet to DataPyBBQ if parameter exists in PyBBQ
        """
        # Transform DataModelMagnet structure to dictionary with dot-separated branches
        df = pd.json_normalize(self.model_data.model_dump(), sep='.')
        dotSepModelData = df.to_dict(orient='records')[0]

        for keyModelData, value in dotSepModelData.items():
            keyPyBBQ = DictionaryPyBBQ.lookupModelDataToPyBBQ(keyModelData)
            if keyPyBBQ:
                if keyPyBBQ in self.data_PyBBQ.__annotations__:
                    self.setAttribute(self.data_PyBBQ, keyPyBBQ, value)
                else:
                    print('Can find {} in lookup table but not in DataPyBBQ'.format(keyPyBBQ))


    def loadConductorData(self):
        '''
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        '''

        # Check inputs and unpack variables
        if len(self.model_data.Conductors) > 1:
            raise Exception('For PyBBQ models, the key Conductors cannot contain more than one entry.')
        conductor_type = self.model_data.Conductors[0].cable.type
        strand_type = self.model_data.Conductors[0].strand.type
        if conductor_type == 'Ribbon':
            raise Exception('For PyBBQ models, the cable type Ribbon is not supported.')

        # Define conductor shape and size
        if conductor_type == 'Mono' and strand_type == 'Round':
            strands = 1
            shape = 'round'
        elif conductor_type == 'Mono' and strand_type == 'Rectangular':
            strands = 1
            shape = 'rectangular'
        elif conductor_type == 'Rutherford':
            strands = self.model_data.Conductors[0].cable.n_strands
            shape = 'rectangular' # This is the shape of the rutherford cable, not the strand, used for self-field calculation.
        else:
            raise Exception('For PyBBQ models, only these combinations of cable and strand types are supported:\n'
                            'conductor_type: Rutherford \n'
                            'conductor_type: Mono and strand_type: Round \n'
                            'conductor_type: Mono and strand_type: Rectangular \n')

        # Load variables
        width   = self.model_data.Conductors[0].cable.bare_cable_width
        height   = self.model_data.Conductors[0].cable.bare_cable_height_mean

        if self.model_data.Conductors[0].strand.type == 'Round':
            strand_dmt = self.model_data.Conductors[0].strand.diameter
        elif self.model_data.Conductors[0].strand.type == 'Rectangular':
            strand_width = self.model_data.Conductors[0].strand.bare_width
            strand_height = self.model_data.Conductors[0].strand.bare_height
            strand_dmt = 2*((strand_width*strand_height)/math.pi)**0.5
        else:
            raise Exception(f'For PyBBQ models, strand type {self.model_data.Conductors[0].strand.type} is not supported.')

        material = self.model_data.Conductors[0].strand.material_superconductor
        material = 'NbTi' if material == 'Nb-Ti' else material

        RRR = self.model_data.Conductors[0].strand.RRR
        if not self.model_data.Conductors[0].cable.f_inner_voids:
            self.model_data.Conductors[0].cable.f_inner_voids = 0.0
        if not self.model_data.Conductors[0].cable.f_outer_voids:
            self.model_data.Conductors[0].cable.f_outer_voids = 0.0
        non_void = 1 - self.model_data.Conductors[0].cable.f_inner_voids - self.model_data.Conductors[0].cable.f_outer_voids
        CuSC = self.model_data.Conductors[0].strand.Cu_noCu_in_strand
        sim_name = self.model_data.GeneralParameters.conductor_name

        if self.model_data.Options_PyBBQ.physics.wetted_p is None:
            wetted_p = (1-non_void) if strands > 1 else 0.0
        else:
            wetted_p = self.model_data.Options_PyBBQ.physics.wetted_p

        # Set calculated variables
        self.setAttribute(self.data_PyBBQ, 'shape',    shape)
        self.setAttribute(self.data_PyBBQ, 'width',    width)
        self.setAttribute(self.data_PyBBQ, 'height',   height)
        self.setAttribute(self.data_PyBBQ, 'strands',   strands)
        self.setAttribute(self.data_PyBBQ, 'strand_dmt', strand_dmt)
        self.setAttribute(self.data_PyBBQ, 'material', material)
        self.setAttribute(self.data_PyBBQ, 'RRR', RRR)
        self.setAttribute(self.data_PyBBQ, 'non_void', non_void)
        self.setAttribute(self.data_PyBBQ, 'CuSC',     CuSC)
        self.setAttribute(self.data_PyBBQ, 'sim_name', str(sim_name))
        self.setAttribute(self.data_PyBBQ, 'wetted_p', wetted_p)
