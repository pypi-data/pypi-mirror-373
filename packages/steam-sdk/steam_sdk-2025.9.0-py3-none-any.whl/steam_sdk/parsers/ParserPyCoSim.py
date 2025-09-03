from steam_sdk.data.DataModelCosim import DataModelCosim
from steam_sdk.data.DataPyCoSim import DataPyCoSim
from steam_sdk.parsers.ParserYAML import model_data_to_yaml


class ParserPyCoSim:
    """
        Class with methods to write PyCoSim input files
    """

    def __init__(self, cosim_data: DataModelCosim = None):
        '''
        :param cosim_data: DataModelCosim object containing co-simulation parameter structure
        '''

        # Load co-simulation data from the BuilderModel object
        self.cosim_data = cosim_data

        # Translate from DataModelCosim to DataPyCoSim
        self.translateDataModelCosimToDataPyCoSim()

    def translateDataModelCosimToDataPyCoSim(self):
        '''
        Assign keys from DataModelCosim to DataPyCoSim
        '''
        self.pycosim_data: DataPyCoSim = DataPyCoSim()
        self.pycosim_data.GeneralParameters = self.cosim_data.GeneralParameters
        self.pycosim_data.Simulations = self.cosim_data.Simulations
        self.pycosim_data.Start_from_s_t_i = self.cosim_data.Options_PyCoSim.Start_from_s_t_i
        self.pycosim_data.PostProcess = self.cosim_data.Options_PyCoSim.PostProcess


    def write_cosim_model(self, full_path_file_name: str, verbose: bool = False):
        '''
        Write input file for PyCoSim
        :param full_path_file_name: Full path of the output file
        :param verbose: Display logging info
        :return:
        '''

        model_data_to_yaml(self.pycosim_data, name_output_file=full_path_file_name, list_exceptions=[])
        if verbose: print(f'File {full_path_file_name} written.')
