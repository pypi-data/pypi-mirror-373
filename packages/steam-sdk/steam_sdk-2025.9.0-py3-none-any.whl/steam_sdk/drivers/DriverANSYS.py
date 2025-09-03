from subprocess import call

class DriverANSYS:
    '''
        Class to run ANSYS APDL models in Windows.
        This class was written with the help of G. Vallone (LBNL).
    '''

    def __init__(self, ANSYS_path: str, input_file: str, output_file: str, directory: str,
            jobname: str = 'file', memory: str = '4096', reserve: str = '1024',
            n_processors: int = 4, verbose: bool = False):
        '''
        Initialize class to run ANSYS APDL models.

        :param ANSYS_path: Path to ANSYS executable, for example: C:\Program Files\ANSYS Inc\v222\ansys\bin\winx64\ANSYS222.exe
        :param input_file: Input file to run
        :param output_file: Output file for the simulation
        :param directory: Directory where the inputs are (usually os.path.dirname(input_file)?)
        :param jobname: Name of the ANSYS job
        :param memory: Initial allocation of memory (in megabytes) requested for the Mechanical APDL run, in MB (called Total Workspace in ANSYS manual)
        :param reserve: Portion (in megabytes) of total memory that the database will use for the initial allocation (called Database in ANSYS manual)
        :param n_processors: Number of processors to use
        :param verbose: If True, print some logging information
        '''

        # Unpack arguments
        self.ANSYS_path = ANSYS_path
        self.input_file = input_file
        self.output_file = output_file
        self.directory = directory
        self.jobname = jobname
        self.memory = memory
        self.reserve = reserve
        self.n_processors = n_processors
        self.verbose = verbose
        if verbose:
            print(f'ANSYS_path: {ANSYS_path}')
            print(f'input_file: {input_file}')
            print(f'output_file: {output_file}')
            print(f'directory: {directory}')
            print(f'jobname: {jobname}')
            print(f'memory: {memory}')
            print(f'reserve: {reserve}')
            print(f'n_processors: {n_processors}')
            print(f'verbose: {verbose}')

    def run(self, verbose: bool = None):
        '''
        Run the ANSYS APDL model
        :param verbose: If True, print some logging information
        :return: Number of errors in the ANSYS calculation
        '''
        if verbose == None:
            verbose = self.verbose
        # Define string to run
        callString = self._make_callString()
        if verbose:
            print(f'DriverANSYS - Call string:\n{callString}')

        # Run
        call(callString, shell=False)
        if verbose:
            print(f'DriverANSYS - Run finished for the called string:\n{callString}')

        # Check for errors and return
        numerrors_mech = "undetermined"
        try:
            searchfile = open(self.output_file, "r")
        except:
            for line in searchfile:
                if "NUMBER OF ERROR" in line:
                    numerrors_mech = int(line.split()[-1])
            searchfile.close()
        return (numerrors_mech)


    def _make_callString(self):
        # callString = ('\"{}\" -p ansys -dir \"{}\" -j \"{}\" -s noread '
        #               ' -m {} -db {} -t -d win32 -b -i \"{}\" -o \"{}\" -smp -np {}'
        #               ).format(ANSYS_path, directory, jobname, memory, reserve, input_file, output_file, n_processors)
        callString = (f'\"{self.ANSYS_path}\" -p ansys -dir \"{self.directory}\" -j \"{self.jobname}\" -s noread '
                      f'-m {self.memory} -db {self.reserve} -t -d win32 -b -i \"{self.input_file}\" '
                      f'-o \"{self.output_file}\" -smp -np {self.n_processors}')
        return callString