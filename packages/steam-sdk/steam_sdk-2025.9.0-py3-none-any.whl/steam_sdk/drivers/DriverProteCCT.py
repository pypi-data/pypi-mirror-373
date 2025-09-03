import os
import subprocess
from pathlib import Path


class DriverProteCCT:
    '''
        Class to drive ProteCCT models
    '''

    def __init__(self, path_exe=None, path_folder_ProteCCT=None, verbose=False):
        # Unpack arguments
        self.path_exe          = path_exe
        self.path_folder_ProteCCT = path_folder_ProteCCT
        self.verbose           = verbose
        if verbose:
            print('path_exe =          {}'.format(path_exe))
            print('path_folder_ProteCCT = {}'.format(path_folder_ProteCCT))

    def run_ProteCCT(self, simFileName: str, inputDirectory: str = 'input', outputDirectory: str = 'output'):
        '''
        ** Run ProteCCT model **
        :param simFileName: Name of the simulation file to run
        :param outputDirectory: Relative path of the input directory with respect to path_folder_ProteCCT
        :param outputDirectory: Relative path of the output directory with respect to path_folder_ProteCCT
        :return:
        '''

        # Quick workaround to allow running the simulation no matter whether simFileName contains ".xlsx" or not
        if simFileName.endswith('.xlsx'):
            simFileName = simFileName.strip('.xlsx')

        full_path_input  = os.path.join(self.path_folder_ProteCCT, inputDirectory, simFileName + '.xlsx')
        full_path_output = os.path.join(self.path_folder_ProteCCT, outputDirectory)

        if not os.path.isdir(full_path_output):
            print("Output folder {} does not exist. Making it now".format(full_path_output))
            Path(full_path_output).mkdir(parents=True)

        if self.verbose:
            print('path_exe =             {}'.format(self.path_exe))
            print('path_folder_ProteCCT = {}'.format(self.path_folder_ProteCCT))
            print('simFileName =          {}'.format(simFileName))
            print('inputDirectory =       {}'.format(inputDirectory))
            print('outputDirectory =      {}'.format(outputDirectory))
            print('full_path_input =      {}'.format(full_path_input))
            print('full_path_output =     {}'.format(full_path_output))
        # Run model
        return subprocess.call([self.path_exe, full_path_input, full_path_output])
