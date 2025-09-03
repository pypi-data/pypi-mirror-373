import os
import subprocess
from pathlib import Path


class DriverPSPICE:
    '''
        Class to drive PSPICE netlist models
    '''

    def __init__(self, path_exe=None, path_folder_PSPICE=None, verbose=False, timeout_s = None):
        # Unpack arguments
        self.path_exe = path_exe
        self.path_folder_PSPICE = path_folder_PSPICE
        self.verbose = verbose
        self.timeout_s = timeout_s          #time in seconds after which the process is killed
        if verbose:
            print('path_exe:            {}'.format(path_exe))
            print('path_folder_PSPICE:  {}'.format(path_folder_PSPICE))

    def run_PSPICE(self, nameCircuit: str, suffix: str = ''):
        '''
        ** Run PSPICE model **
        :param nameCircuit: Name of the magnet model to run
        :param suffix: Number of the simulation to run
        :return:
        '''
        # Unpack arguments
        path_exe = self.path_exe
        path_folder_PSPICE = self.path_folder_PSPICE
        verbose = self.verbose

        full_name_file = os.path.join(path_folder_PSPICE, f'{nameCircuit}{suffix}.cir')

        if verbose:
            print('path_exe:            {}'.format(path_exe))
            print('path_folder_PSPICE:  {}'.format(path_folder_PSPICE))
            print('nameCircuit:         {}'.format(nameCircuit))
            print('suffix:              {}'.format(suffix))
            print('full_name_file:      {}'.format(full_name_file))
            print('Absolute full_name_file: {}'.format(Path(full_name_file).resolve()))


        # Run model
        cmd = [path_exe, full_name_file]
        timeout_s = self.timeout_s
        # Run model
        if timeout_s:
            self.output = subprocess.run(cmd, timeout=timeout_s).returncode
        else:
            self.output = subprocess.call(cmd, stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
        if verbose:
            print(f'Subprocess finished returning: \n{self.output}')
        if self.output:
            raise Exception('PSPICE failed to run successfully.')
