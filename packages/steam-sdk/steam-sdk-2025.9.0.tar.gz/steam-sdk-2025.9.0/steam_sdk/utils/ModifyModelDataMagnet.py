import os
from pathlib import Path
import yaml
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))) # Add the path to the steam_sdk package to the system path
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.parsers.ParserYAML import model_data_to_yaml, yaml_to_data

if __name__ == "__main__":  # pragma: no cover
    # path_models = Path.joinpath(
    #     Path(__file__).parent.parent.parent,
    #     "C:\\Users\emm\cernbox\SWAN_projects\steam_models\magnets",
    # )
    # path_models = Path.joinpath(
    #     Path(__file__).parent.parent.parent, r"E:\Python311\steam_models\magnets")

    path_models = Path.joinpath(
        Path(__file__).parent.parent.parent, "tests/builders/model_library/magnets")

    path_models = Path.joinpath(
        Path(__file__).parent.parent.parent,
        "C:\\Users\emm\cernbox\SWAN_projects\steam_models\magnets",
    )
    
    model_names = [x.parts[-1] for x in Path(path_models).iterdir() if x.is_dir()]
    print(f"model_names: {model_names}, len(model_names): {len(model_names)}")
    # model_names = ['CAC_Strand_hexFilaments']
    # model_names = ['CAC_Strand_hexFilaments', 'CCT_1', 'HTS1', 'MQXA', 'MCBRD']
    #model_names = ['CAC_Strand_hexFilaments']
    model_names = ['SMC_ESC']
    # model_names = model_names[55:]
    for model_name in model_names:
        print(f'{model_names.index(model_name)}:{model_name}')
        # Read the file:
        yaml_file = Path.joinpath(
            path_models, model_name, "input", "modelData_" + model_name + ".yaml"
        )
        if os.path.isfile(yaml_file):
            #Read the yaml file and store the date inside ruamel_yaml_object:
            # with open(yaml_file, "r") as stream:
            #     ruamel_yaml_object = yaml.safe_load(stream)
            #
            # print(f"The file has been read: {yaml_file}")

            # Create a DataModelMagnet object from the yaml file's data:
            # Note: Obsolete keys (the keys that are not in DataModelMagnet) will
            # automatically be deleted. Moreover, if new keys are added to
            # DataModelMagnet, they will be added to the YAML file. The new key's values
            # will be DataModelMagnet's default values.
            # del ruamel_yaml_object["Options_FiQuS"]["Pancake3D"]
            # model_data = DataModelMagnet(**ruamel_yaml_object)
            model_data = yaml_to_data(yaml_file, DataModelMagnet)
            # model_data.Options_FiQuS.cws.geometry.iterative_fragment = False
            # model_data.Options_FiQuS.cws.mesh.temperature_sensors.enabled = False
            # model_data.Options_FiQuS.cws.mesh.heaters.enabled = False
            # model_data.Options_FiQuS.cws.mesh.field_coils.enabled = False
            # model_data.Options_FiQuS.cws.solve.formers.use = 'function'
            # model_data.Options_FiQuS.cws.solve.shells.use = 'function'

            # Some values of the new and old keys can be changed like this:
            # model_data.Options_LEDET.magnet_inductance.flag_calculate_inductance = True
            model_data.Options_LEDET.variables_to_save.variableToSaveTxt = ['time_vector', 'Ia', 'Ib', 'T_ht', 'dT_dt_ht', 'flagQ_ht', 'flagQ_longitudinal_ht', 'IifX', 'IifY', 'Iis', 'dIifXDt', 'dIifYDt', 'dIisDt', 'Uc', 'U_QH', 'T_s_QH', 'time_vector', 'R_CoilSections', 'U_inductive_dynamic_CoilSections', 'I_CoilSections']
            model_data.Options_LEDET.variables_to_save.typeVariableToSaveTxt = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1]
            model_data.Options_LEDET.variables_to_save.variableToInitialize = ['Ia', 'Ib', 'T_ht', 'dT_dt_ht', 'flagQ_ht', 'flagQ_longitudinal_ht', 'IifX', 'IifY', 'Iis', 'dIifXDt', 'dIifYDt', 'dIisDt', 'Uc', 'U_QH', 'T_s_QH']


            # Old values of obsolete keys can be moved to new keys like this:
            # model_data.Options_LEDET.conductor_geometry_used_for_ISCL.mirrorY_ht = (
            #     ruamel_yaml_object["CoilWindings"]["multipole"]["mirrorY_ht"]
            # )

            # Set to True if you wish to test the results of this script, and False if
            # you wish to really update all yaml input files
            test = False
            if test:
                yaml_file_output = Path.joinpath(
                    path_models,
                    model_name,
                    "input",
                    "modelData_" + model_name + "_MODIFIED.yaml",
                )
            else:
                yaml_file_output = yaml_file

            addDescriptionAsComments = True
            keysAsPydanticAliases = True
            model_data_to_yaml(
                model_data,
                yaml_file_output,
                list_exceptions=["Conductors"],
                with_comments=addDescriptionAsComments,
                by_alias=keysAsPydanticAliases,
            )
            print(f"The file has been written: {yaml_file_output}")
        else:
            print(f"WARNING: {yaml_file} is not found.")
