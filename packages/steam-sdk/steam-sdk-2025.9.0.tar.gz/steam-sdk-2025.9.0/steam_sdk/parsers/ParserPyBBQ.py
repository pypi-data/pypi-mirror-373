import os
from pathlib import Path
from steam_sdk.parsers.ParserYAML import yaml_to_data, dict_to_yaml

from steam_sdk.builders.BuilderPyBBQ import BuilderPyBBQ
from steam_sdk.data.DataPyBBQ import DataPyBBQ


class ParserPyBBQ:
    """
        Class with methods to read/write PyBBQ information from/to other programs
    """

    def __init__(self, builder_PyBBQ: BuilderPyBBQ = BuilderPyBBQ(flag_build=False)):
        """
            Initialization using a BuilderPyBBQ object containing PyBBQ parameter structure
        """

        self.builder_PyBBQ: BuilderPyBBQ = builder_PyBBQ


    def readFromYaml(self, file_name: str, verbose: bool = True):
        '''
        '''
        # TODO documentation

        # Load yaml keys into DataModelMagnet dataclass
        self.builder_PyBBQ.data_PyBBQ = yaml_to_data(file_name, DataPyBBQ)
        if verbose: print('File {} was loaded.'.format(file_name))


    def writePyBBQ2yaml(self, full_path_file_name: str, verbose: bool = False):
        '''
        ** Writes a PyBBQ yaml input file **

        :param full_path_file_name:
        :param verbose:
        :return:
        '''

        all_data_dict = self.builder_PyBBQ.data_PyBBQ.model_dump()

        # If the output folder is not an empty string, and it does not exist, make it
        output_path = os.path.dirname(full_path_file_name)
        if verbose: print('output_path: {}'.format(output_path))
        if output_path != '' and not os.path.isdir(output_path):
            print("Output folder {} does not exist. Making it now".format(output_path))
            Path(output_path).mkdir(parents=True)

        # Write output .yaml file
        dict_to_yaml(all_data_dict, full_path_file_name)

