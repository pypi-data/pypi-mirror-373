import os
from pathlib import Path
import yaml

from steam_sdk.data.DataModelConductor import DataModelConductor
from steam_sdk.parsers.ParserYAML import dict_to_yaml

if __name__ == "__main__":  # pragma: no cover
    # path_models = Path.joinpath(Path(__file__).parent.parent.parent, r"D:\Code_new\steam_sdk\tests\builders\model_library\conductors")
    path_models = Path.joinpath(Path(__file__).parent.parent.parent, 'tests/builders/model_library/conductors')
    path_models = Path.joinpath(Path(__file__).parent.parent.parent,"C:\\Users\emm\cernbox\SWAN_projects\steam_models\conductors")
    models = [x.parts[-1] for x in Path(path_models).iterdir() if x.is_dir()]

    for mm in models:
        # Read file
        file_model_data = Path.joinpath(path_models, mm, 'input', 'modelData_' + mm + '.yaml')
        if os.path.isfile(file_model_data):
            # Load yaml keys into DataAnalysis dataclass
            with open(file_model_data, "r") as stream:
                dictionary_yaml = yaml.safe_load(stream)
                model_data = DataModelConductor(**dictionary_yaml)
            print(f'Read file: {file_model_data}')

            # Note: Obsolete keys in yaml file will automatically be deleted

            # Note: New keys added to DataModelMagnet will automatically be added to the yaml file (UNLESS A VALUE IS ASSIGNED BELOW, THEIR VALUES WILL BE INITIALIZED TO DEFAULT)

            # Example to assign value to new keys in model data
            # model_data.Options_LEDET.post_processing.flag_saveResultsToMesh = 0
            # model_data.Options_LEDET.simulation_3D.sim3D_f_cooling_LeadEnds = [1, 1]
            # model_data.Options_LEDET.simulation_3D.sim3D_flag_checkNodeProximity = 0
            # model_data.Options_LEDET.simulation_3D.sim3D_nodeProximityThreshold = 0.01
            model_data.Options_LEDET.variables_to_save.variableToSaveTxt = ['time_vector', 'Ia', 'Ib', 'T_ht', 'dT_dt_ht', 'flagQ_ht', 'flagQ_longitudinal_ht', 'IifX', 'IifY', 'Iis', 'dIifXDt', 'dIifYDt', 'dIisDt', 'Uc', 'U_QH', 'T_s_QH', 'time_vector', 'R_CoilSections', 'U_inductive_dynamic_CoilSections', 'I_CoilSections']
            model_data.Options_LEDET.variables_to_save.typeVariableToSaveTxt = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1]
            model_data.Options_LEDET.variables_to_save.variableToInitialize = ['Ia', 'Ib', 'T_ht', 'dT_dt_ht', 'flagQ_ht', 'flagQ_longitudinal_ht', 'IifX', 'IifY', 'Iis', 'dIifXDt', 'dIifYDt', 'dIisDt', 'Uc', 'U_QH', 'T_s_QH']

            # Example to change positions of key keeping its value (IF THIS IS NOT DONE THE INFOMRATION IN THE ORIGINAL YAML FILE WILL BE LOST!)
            # Note: The following will raise an exception if the keys do not exist in the original yaml file
            # SEE ModifyModelDataMagnet script FOR AN EXAMPLE

            # Check and reformat the key values
            model_data = DataModelConductor(**model_data.model_dump())

            # Write file
            # file_model_data_output = Path.joinpath(path_models, mm, 'input', 'modelData_' + mm + '_MODIFIED.yaml')  # use this line if you wish to test the results of this script
            file_model_data_output = file_model_data  # use this line if you wish to really update all yaml input files
            all_data_dict = {**model_data.model_dump()}
            dict_to_yaml(all_data_dict, file_model_data_output, list_exceptions=['Conductors'])
            print(f'Written file: {file_model_data_output}')
        else:
            print(f'WARNING: File {file_model_data} not found.')
