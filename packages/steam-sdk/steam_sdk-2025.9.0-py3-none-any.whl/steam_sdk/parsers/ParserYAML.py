import os
import ruamel.yaml
import numpy as np
from typing import Dict, Union
from pathlib import Path

from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


def yaml_to_data(full_file_path, data_class=dict):
    """
    Loads content of YAML file to data class. If data class not provided it loads into
    dictionary.

    :param full_file_path: full path to yaml file with .yaml extension
    :param data_class: data class to load yaml file to, if empty yaml is loaded as
        Python dictionary (dict)
    """

    with open(full_file_path, "r") as stream:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        yaml_str = yaml.load(stream)
    return data_class(**yaml_str)


def dict_to_yaml(
    data_dict: Dict,
    name_output_file: str,
    list_exceptions: list = [],
):
    """
    Write a dictionary to YAML with pre-set format used across STEAM YAML files.
    In particular:
    - keys order is preserved
    - lists are written in a single row

    :param dict: dict to write to into a YAML file
    :type data_dict: dict
    :param name_output_file: Full path to YAML file to write
    :type name_output_file: str
    :param list_exceptions: List of strings defining keys that will not be written in a
        single row
    :type list_exceptions: list
    :return: Nothing, writes YAML file to disc
    :rtype: None
    """

    ####################################################################################
    # Helper functions
    def my_represent_none(obj, *args):
        """
        Change data representation from empty string to "null" string
        """
        return obj.represent_scalar("tag:yaml.org,2002:null", "null")

    def flist(x):
        """
        Define a commented sequence to allow writing a list in a single row
        """
        retval = ruamel.yaml.comments.CommentedSeq(x)
        retval.fa.set_flow_style()  # fa -> format attribute
        return retval

    def list_single_row_recursively(data_dict: dict, list_exceptions: list = []):
        """
        Write lists in a single row
        :param data_dict: Dictionary to edit
        :param list_exceptions: List of strings defining keys that will not be written
        in a single row
        :return:
        """
        for key, value in data_dict.items():
            if isinstance(value, list) and (not key in list_exceptions):
                data_dict[key] = flist(value)
            elif isinstance(value, np.ndarray):
                data_dict[key] = flist(value.tolist())
            elif isinstance(value, dict):
                data_dict[key] = list_single_row_recursively(value, list_exceptions)

        return data_dict

    ####################################################################################

    # Set up YAML instance settings:
    yamlInstance = ruamel.yaml.YAML()
    yamlInstance.width = (
        268435456  # define the maximum number of characters in each line
    )
    yamlInstance.default_flow_style = False
    yamlInstance.emitter.alt_null = "Null"
    yamlInstance.representer.add_representer(type(None), my_represent_none)

    # Write lists in a single row
    data_dict = list_single_row_recursively(data_dict, list_exceptions=list_exceptions)

    # Make sure the target folder exists
    make_folder_if_not_existing(os.path.dirname(name_output_file), verbose=False)

    # Write the YAML file
    with open(name_output_file, "w") as yaml_file:
        yamlInstance.dump(data_dict, yaml_file)


def model_data_to_yaml(
    model_data: DataModelMagnet,
    name_output_file: Union[str, Path],
    list_exceptions: list = [],
    with_comments=False,
    by_alias=True,
):
    """
    Write a model data to YAML with pre-set format used across STEAM YAML files.
    In particular:
    - keys order is preserved
    - lists are written in a single row

    :param model_data: DataModelMagnet to write to into a YAML file
    :type data_dict: DataModelMagnet
    :param name_output_file: Full path to YAML file to write
    :type name_output_file: str
    :param list_exceptions: List of strings defining keys that will not be written in a
        single row
    :type list_exceptions: list
    :param with_comments: If true, write pydantic descriptions to the YAML file as
        comments next to the keys
    :type with_comments: bool
    :param by_alias: If true, use the alias of the pydantic fields as keys in the YAML
        file
    :type by_alias: bool
    :return: Nothing, writes YAML file to disc
    :rtype: None
    """
    # Set up YAML instance settings:
    yamlInstance = ruamel.yaml.YAML()

    # Convert the model_data to a ruamel.yaml object/dictionary:
    if with_comments:
        # Add pydantic descriptions to the yaml file as comments:
        if isinstance(name_output_file, Path):
            dummy_yaml_file_to_create_ruamel_object = (
                name_output_file.resolve().parent.joinpath("dummy.yaml")
            )
        else:
            # then the path is created with os
            dummy_yaml_file_to_create_ruamel_object = os.path.join(
                os.path.dirname(name_output_file), "dummy.yaml"
            )

        with open(dummy_yaml_file_to_create_ruamel_object, "w+") as stream:
            yamlInstance.dump(model_data.dict(by_alias=by_alias), stream)

        # Read the file:
        with open(dummy_yaml_file_to_create_ruamel_object, "r") as stream:
            # Read the yaml file and store the date inside ruamel_yaml_object:
            # ruamel_yaml_object is a special object that stores both the data and
            # comments. Even though the data might be changed or added, the same
            # object will be used to create the new YAML file to store the comments.
            ruamel_yaml_object = yamlInstance.load(
                stream
            )

        os.remove(dummy_yaml_file_to_create_ruamel_object)

        def iterate_fields(model, ruamel_yaml_object):
            for currentPydanticKey, value in model.__fields__.items():
                if by_alias:
                    if value.alias:
                        currentDictionaryKey = value.alias
                    else:
                        currentDictionaryKey = currentPydanticKey
                else:
                    currentDictionaryKey = currentPydanticKey

                if value.description:
                    description = value.description.replace("\n", " ")
                    ruamel_yaml_object.yaml_add_eol_comment(
                        description,
                        currentDictionaryKey,
                    )

                if hasattr(getattr(model, currentPydanticKey), "__fields__"):
                    new_ruamel_yaml_object = iterate_fields(
                        getattr(model, currentPydanticKey),
                        ruamel_yaml_object[currentDictionaryKey],
                    )

                    ruamel_yaml_object[currentDictionaryKey] = new_ruamel_yaml_object

            return ruamel_yaml_object

        for currentKey in model_data.__fields__:
            if hasattr(getattr(model_data, currentKey), "__fields__"):
                ruamel_yaml_object[currentKey] = iterate_fields(
                    getattr(model_data, currentKey),
                    ruamel_yaml_object[currentKey],
                )

        data_dict = ruamel_yaml_object

    else:
        data_dict = model_data.dict(by_alias=by_alias)

    dict_to_yaml(data_dict, name_output_file, list_exceptions=list_exceptions)
