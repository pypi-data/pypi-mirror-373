import subprocess


class DriverLEDET:
    '''
        Class to drive LEDET models
    '''

    def __init__(self, path_exe=None, path_folder_LEDET=None, verbose=False):
        # Unpack arguments
        self.path_exe          = path_exe
        self.path_folder_LEDET = path_folder_LEDET
        self.verbose           = verbose
        if verbose:
            print('path_exe =          {}'.format(path_exe))
            print('path_folder_LEDET = {}'.format(path_folder_LEDET))

    def run_LEDET(self, nameMagnet: str, simsToRun: str, simFileType: str = '.xlsx'):
        '''
        ** Run LEDET model **
        :param nameMagnet: Name of the magnet model to run
        :param simsToRun: Number identifying the simulation to run
        :param simFileType: String identifying the type of input file (supported: .xlsx, .yaml, .json)
        :return:
        '''
        # Unpack arguments
        path_exe = self.path_exe
        path_folder_LEDET = self.path_folder_LEDET
        verbose = self.verbose
        if simFileType == None:
            simFileType = '.xlsx'  # set to default

        if verbose:
            print('path_exe =          {}'.format(path_exe))
            print('path_folder_LEDET = {}'.format(path_folder_LEDET))
            print('nameMagnet =        {}'.format(nameMagnet))
            print('simsToRun =         {}'.format(simsToRun))
            print('simFileType =       {}'.format(simFileType))

        # Run model
        subprocess.call([path_exe, path_folder_LEDET, nameMagnet, simsToRun, simFileType])

        return {'dummy_value': 123456789} # this is temporary only. It is needed for Dakota

# def RunSimulationsLEDET(LEDETFolder, LEDETExe, MagnetName, Simulations = 'All', RunSimulations = False):
#     # ExcelFolder = LEDETFolder + "//LEDET//" + MagnetName + "//Input//"  # original
#     ExcelFolder = LEDETFolder + "/LEDET/" + MagnetName + "/Input/"  # edited to pass tests on Gitlab
#     StartFile = LEDETFolder + "//startLEDET.xlsx"
#     SimNumbers = []
#
#     #1. Prepare everything
#     if len(Simulations)==3:
#         if Simulations =='All':
#             items = os.listdir(ExcelFolder)
#             for item in items:
#                 if item.startswith(MagnetName) and item.endswith('.xlsx'):
#                     if ".sys" not in item:
#                         num = item.replace('.xlsx', '')
#                         num = num.replace(MagnetName+'_', '')
#                         num = int(num)
#                         SimNumbers.append(num)
#     else:
#         SimNumbers = Simulations
#
#     df = pd.read_excel(StartFile, header=None)
#     df.rename(columns={0: 'a', 1: 'b', 2: 'c'}, inplace=True)
#     df.loc[df['b'] == 'currFolder', 'c'] = LEDETFolder + "\\LEDET"
#     df.loc[df['b'] == 'nameMagnet', 'c'] = MagnetName
#     df.loc[df['b'] == 'simsToRun',  'c'] = str(SimNumbers)
#     writer = pd.ExcelWriter(StartFile)
#     df.to_excel(writer, index=False, index_label=False, header=False, sheet_name='startLEDET')
#     writer.save()
#
#     #2. Run Executable
#     if RunSimulations:
#         os.chdir(LEDETFolder)
#         os.system(LEDETExe)
#
#
# def run_LEDET(self, LEDET_exe_full_path):
#     RunSimulationsLEDET(self.base_folder, LEDET_exe_full_path, self.nameCircuit, Simulations=self.model_no,
#                    RunSimulations=False)
#     LEDET_exe_path = os.path.join(self.base_folder, LEDET_exe_full_path)
#     os.chdir(self.base_folder)
#     subprocess.call([LEDET_exe_path])