import os
import yaml

class ToolDefaultReader(object):
    """
        Class to access tool default information
    """
    @staticmethod
    def getResourceContent(fileName):
        resourceFilePath = ToolDefaultReader.getResourcePath(fileName)

        with open(resourceFilePath, 'r') as file:
            return file.read()

    @staticmethod
    def getResourcePath(fileName):
        localDirectory = os.path.dirname(__file__)
        return os.path.join(localDirectory, fileName)


def read_yaml(type_str, elem_name):
    """
        Reads yaml file and returns it as dictionary
        :param type_str: type of file, e.g.: quench, coil, wire
        :param elem_name: file name, e.g. ColSol.1
        :return: dictionary for file named: type.name.yam
    """

    rfyft = ['options', 'plots', 'store']               # resources folder yaml file types, i.e. steam-notebook-api\steam_nb_api\resources\ledet\Inputs
    yaml_file_name = f"{type_str}.{elem_name}.yaml"
    if type_str in rfyft:
        file_path = os.path.join('LEDET', 'Inputs', yaml_file_name)
        fullfileName = ToolDefaultReader.getResourcePath(file_path)
    else:                   # every other yaml file type is loaded from current directory.
        fullfileName = os.path.join(os.getcwd(), yaml_file_name)
    with open(fullfileName, 'r') as stream:
        data = yaml.safe_load(stream)
    return data