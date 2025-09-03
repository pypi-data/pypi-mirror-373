import os
import subprocess
from pathlib import Path


class DriverPyBBQ:
    '''
        Class to drive PyBBQ models
    '''

    def __init__(self, path_exe=None, path_folder_PyBBQ=None, path_folder_PyBBQ_input=None, verbose=False):
        # Unpack arguments
        self.path_exe          = path_exe
        self.path_folder_PyBBQ = path_folder_PyBBQ
        self.path_folder_PyBBQ_input = path_folder_PyBBQ_input
        self.verbose           = verbose
        if verbose:
            print('path_exe =          {}'.format(path_exe))
            print('path_folder_PyBBQ = {}'.format(path_folder_PyBBQ))

    def run_PyBBQ(self, simFileName: str, outputDirectory: str = 'output', test='False'):
        '''
        ** Run PyBBQ model **
        :param simFileName: Name of the simulation file to run
        :param outputDirectory: Name of the output directory
        :return:
        '''
        # Unpack arguments
        path_exe = self.path_exe
        path_folder_PyBBQ = self.path_folder_PyBBQ
        path_folder_PyBBQ_input = self.path_folder_PyBBQ_input
        verbose = self.verbose

        full_path_input  = os.path.join(path_folder_PyBBQ_input, simFileName + '.yaml')
        full_path_output = os.path.join(path_folder_PyBBQ, outputDirectory)

        if not os.path.isdir(full_path_output):
            print("Output folder {} does not exist. Making it now".format(full_path_output))
            Path(full_path_output).mkdir(parents=True)

        if verbose:
            print('path_exe =             {}'.format(path_exe))
            print('path_folder_PyBBQ =    {}'.format(path_folder_PyBBQ))
            print('simFileName =          {}'.format(simFileName))
            print('outputDirectory =      {}'.format(outputDirectory))
            print('full_path_input =      {}'.format(full_path_input))
            print('full_path_output =     {}'.format(full_path_output))
        # Run model
        return subprocess.call(['py', path_exe, full_path_input, full_path_output, test])
        # The 'True' allows pybqq to make a steam_sdk specific test folder structure.
        # return subprocess.call(['py', path_exe, full_path_input, ])
