import os
import subprocess
from pathlib import Path


class DriverXYCE:
    '''
        Class to drive XYCE netlist models
    '''

    def __init__(self, path_exe=None, path_folder_XYCE=None, verbose=False):
        # Unpack arguments
        self.path_exe           = path_exe
        self.path_folder_XYCE   = path_folder_XYCE
        self.verbose            = verbose
        if verbose:
            print('path_exe:            {}'.format(path_exe))
            print('path_folder_XYCE:    {}'.format(path_folder_XYCE))

    def run_XYCE(self, nameCircuit: str, suffix: str = '', prefix: str = ''):
        '''
        ** Run XYCE model **
        :param nameCircuit: Name of the magnet model to run
        :param suffix: Number of the simulation to run
        :return:
        '''
        # Unpack arguments
        path_exe = self.path_exe
        path_folder_XYCE = self.path_folder_XYCE
        full_name_file = os.path.join(path_folder_XYCE, f'{prefix}{nameCircuit}{suffix}.cir')
        verbose = self.verbose


        if verbose:
            print('path_exe:            {}'.format(path_exe))
            print('path_folder_XYCE:    {}'.format(path_folder_XYCE))
            print('nameCircuit:         {}'.format(nameCircuit))
            print('prefix:              {}'.format(prefix))
            print('suffix:              {}'.format(suffix))
            print('full_name_file:      {}'.format(full_name_file))
            print('Absolute full_name_file: {}'.format(Path(full_name_file).resolve()))



        # Run model
        if verbose:
            self.output = subprocess.call([path_exe, full_name_file])
            print(f'Subprocess finished returning: \n{self.output}')
        else:
            self.output = subprocess.call([path_exe, full_name_file],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if self.output:
            raise Exception('XYCE failed to run successfully.')


