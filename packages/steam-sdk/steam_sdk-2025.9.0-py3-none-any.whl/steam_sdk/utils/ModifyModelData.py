from pathlib import Path
import yaml
from steam_sdk.data.DataModelMagnet import DataModelMagnet


def checkIfRightDict(macro_dict_key: str, dict_key: str, content: list, line: str, line_no: int):  # pragma: no cover
    if macro_dict_key:
        j = 1
        macro_group_line = content[line_no - j]
        while macro_group_line[line.find(dict_key) - 1] == ' ':
            j += 1
            macro_group_line = content[line_no - j]
        bool_value = ((' ' + macro_dict_key + ':' in macro_group_line) or
                      (macro_dict_key + ':' in macro_group_line and macro_group_line[0] == macro_dict_key[0]))
    else:
        bool_value = True
    return bool_value


class ModifyModelData:  # pragma: no cover
    """
        Class to change modelData.yaml keys and values
    """

    def __init__(self, models: list = None, models_path: Path = None):
        self.models: list = models
        self.models_path: Path = models_path

    def changeKey(self, dict_key: str = None, macro_dict_key: str = None, prev_key: str = None, new_key: str = None):
        for mm in self.models:
            file_model_data = Path.joinpath(self.models_path, mm, 'input', 'modelData_' + mm + '.yaml')
            with open(file_model_data, "r") as stream:
                # dictionary_yaml = yaml.safe_load(stream)
                # model_data = DataModelMagnet(**dictionary_yaml)
                content = stream.readlines()
            if dict_key:
                for i, line in enumerate(content):
                    if (' ' + dict_key + ':' in line) or (dict_key + ':' in line and line[0] == dict_key[0]):
                        if checkIfRightDict(macro_dict_key, dict_key, content, line, i):
                            j = 1
                            group_line = content[i + j]
                            while group_line[line.find(dict_key) + 1] == ' ':
                                if ((' ' + prev_key + ':' in group_line) or
                                        (prev_key + ':' in group_line and group_line[0] == prev_key[0])):
                                    content.insert(i + j, content.pop(i + j).replace(prev_key, new_key))
                                j += 1
                                group_line = content[i + j]
            else:
                for i, line in enumerate(content):
                    if line[:len(prev_key)] == prev_key:
                        content.insert(i, content.pop(i).replace(prev_key, new_key))

            with open(file_model_data, 'w') as yaml_file:
                # yaml.dump(dictionary_yaml, yaml_file, default_flow_style=False, sort_keys=False)
                yaml_file.writelines(content)

    def removeKey(self, dict_key: str = None, macro_dict_key: str = None, key_name: str = None):
        for mm in self.models:
            file_model_data = Path.joinpath(self.models_path, mm, 'input', 'modelData_' + mm + '.yaml')
            with open(file_model_data, "r") as stream:
                content = stream.readlines()
            if dict_key:
                for i, line in enumerate(content):
                    if (' ' + dict_key + ':' in line) or (dict_key + ':' in line and line[0] == dict_key[0]):
                        if checkIfRightDict(macro_dict_key, dict_key, content, line, i):
                            j = 1
                            group_line = content[i + j]
                            while group_line[line.find(dict_key) + 1] == ' ':
                                if ((' ' + key_name + ':' in group_line) or
                                        (key_name + ':' in group_line and group_line[0] == key_name[0])):
                                    key_group = content[i + j + 1]
                                    while key_group[group_line.find(key_name) + 1] == ' ' or key_group[group_line.find(key_name) + 1] == '-':
                                        content.pop(i + j + 1)
                                        key_group = content[i + j + 1]
                                    if group_line[group_line.find(key_name) - 2] == '-':
                                        content[i + j + 1] = content[i + j + 1].replace(' ', '-', 1)
                                    content.pop(i + j)
                                j += 1
                                group_line = content[i + j]
            else:
                for i, line in enumerate(content):
                    if line[:len(key_name)] == key_name:
                        key_group = content[i + 1]
                        while key_group[0] == ' ' or key_group[0] == '-':
                            content.pop(i + 1)
                            key_group = content[i + 1]
                        content.pop(i)

            with open(file_model_data, 'w') as yaml_file:
                yaml_file.writelines(content)

    def addKey(self, dict_key: str = None, macro_dict_key: str = None, key_above: str = None,
               name: str = None, key_value: str = None):
        for mm in self.models:
            file_model_data = Path.joinpath(self.models_path, mm, 'input', 'modelData_' + mm + '.yaml')
            with open(file_model_data, "r") as stream:
                content = stream.readlines()
            if dict_key:
                for i, line in enumerate(content):
                    if (' ' + dict_key + ':' in line) or (dict_key + ':' in line and line[0] == dict_key[0]):
                        if checkIfRightDict(macro_dict_key, dict_key, content, line, i):
                            indent = line.find(dict_key) * ' ' + '  '
                            j = 1
                            group_line = content[i + j]
                            if key_above:
                                while group_line[1:line.find(dict_key) + 2] == indent[1:]:
                                    if key_above + ':' in group_line:
                                        k = 1
                                        inner_group_line = content[i + j + k]
                                        while inner_group_line[line.find(dict_key) + 2] == ' ':
                                            k += 1
                                            inner_group_line = content[i + j + k]
                                        content.insert(i + j + k, indent + name + f": {key_value}\n")
                                    j += 1
                                    group_line = content[i + j]
                            else:
                                while group_line[1:line.find(dict_key) + 2] == indent[1:] and i + j <= len(content) - 2:
                                    j += 1
                                    group_line = content[i + j]
                                content.insert(i + j + 1 * (i + j == len(content) - 1),
                                               indent + name + f": {key_value}\n")
            else:
                if key_above:
                    for i, line in enumerate(content):
                        if line[:len(key_above)] == key_above:
                            j = 1
                            inner_group_line = content[i + j]
                            while inner_group_line[0] == ' ':
                                j += 1
                                inner_group_line = content[i + j]
                            content.insert(i + j, name + f": {key_value}\n")
                else:
                    content.append(name + f": {key_value}\n")

            with open(file_model_data, 'w') as yaml_file:
                yaml_file.writelines(content)

    def changeValue(self, dict_key: str = None, macro_dict_key: str = None,
                    key_name: str = None, key_value: str = None):
        for mm in self.models:
            file_model_data = Path.joinpath(self.models_path, mm, 'input', 'modelData_' + mm + '.yaml')
            with open(file_model_data, "r") as stream:
                content = stream.readlines()
            if dict_key:
                for i, line in enumerate(content):
                    if (' ' + dict_key + ':' in line) or (dict_key + ':' in line and line[0] == dict_key[0]):
                        if checkIfRightDict(macro_dict_key, dict_key, content, line, i):
                            j = 1
                            group_line = content[i + j]
                            while group_line[line.find(dict_key) + 1] == ' ':
                                if ((' ' + key_name + ':' in group_line) or
                                        (key_name + ':' in group_line and group_line[0] == key_name[0])):
                                    line_new = content.pop(i + j)
                                    content.insert(
                                        i + j, line_new.replace(line_new[line_new.find(': ') + 2:line_new.find('\n')],
                                                                key_value))
                                j += 1
                                group_line = content[i + j]
            else:
                for i, line in enumerate(content):
                    if line[:len(key_name)] == key_name:
                        line_new = content.pop(i)
                        content.insert(i, line_new.replace(line_new[line_new.find(': ') + 2:line_new.find('\n')],
                                                           key_value))

            with open(file_model_data, 'w') as yaml_file:
                yaml_file.writelines(content)


if __name__ == "__main__":  # pragma: no cover
    path_models = Path.joinpath(Path(__file__).parent.parent.parent, 'tests/builders/model_library/magnets')
    # path_models = Path.joinpath(Path(__file__).parent.parent.parent, 'C:\\Users\emm\cernbox\SWAN_projects\steam_models\magnets')
    mmd = ModifyModelData(models=[x.parts[-1] for x in Path(path_models).iterdir() if x.is_dir()],
                          models_path=path_models)

    choice = input("\nChoose either 'c' for changing a key name, or 'r' for removing a key, "
                   "or 'a' for adding a new key, or 'v' for changing the value of a key:\n")
    choices = {'c': ['change a key name', 'contains the key you want to change'],
               'r': ['remove a key', 'contains the key you want to remove'],
               'a': ['add a new key', 'will contain the new key'],
               'v': ['change the value of a key', 'contains the key whose value you want to change']}

    group_key = input(f"\nYou have chosen to {choices[choice][0]}."
                      f"\nInsert the key of the nested dictionary that {choices[choice][1]}: "
                      f"(Insert 'None' if the key is on the highest level)\n")
    if group_key == 'None':
        group_key = None
    if group_key:
        macro_group_key = \
            input(f"\nIn order to be sure about your choice, insert the key of the nested dictionary "
                  f"that contains '{group_key}': (Insert 'None' if '{group_key}' is on the highest level)\n")
        if macro_group_key == 'None':
            macro_group_key = None
    else:
        macro_group_key = None

    if choice == 'c':
        old_key = input('\nInsert the name of the key you want to change:\n')
        new_name = input('\nInsert the new name of the key:\n')
        if input(
                f"\nAre you sure you want to change the key '{old_key}'{' under ' if group_key else ''}"
                f"{group_key if group_key else ''} {'(' if macro_group_key else ''}"
                f"{macro_group_key if macro_group_key else ''}{') ' if macro_group_key else ''}"
                f"to '{new_name}' for all the models? [Y/n]\n") == 'Y':
            mmd.changeKey(dict_key=group_key, macro_dict_key=macro_group_key, prev_key=old_key, new_key=new_name)
            print('\nProcess ended successfully.')
        else:
            print('\nThe process has been interrupted.')

    elif choice == 'r':
        old_key = input('\nInsert the name of the key you want to remove:\n')
        if input(
                f"\nAre you sure you want to remove the key '{old_key}'{' under ' if group_key else ''}"
                f"{group_key if group_key else ''} {'(' if macro_group_key else ''}"
                f"{macro_group_key if macro_group_key else ''}{') ' if macro_group_key else ''}"
                f"from all the models? [Y/n]\n") == 'Y':
            mmd.removeKey(dict_key=group_key, macro_dict_key=macro_group_key, key_name=old_key)
            print('\nProcess ended successfully.')
        else:
            print('\nThe process has been interrupted.')

    elif choice == 'a':
        specific_location = input('\nWould you like to add the new key at a specific location in the nested '
                                  'dictionary? [Y/n] (Last element by default)\n')
        if specific_location == 'Y':
            above_key = input('\nInsert the key that is going to be directly above the new one AT THE SAME LEVEL:\n')
        else:
            above_key = None
        new_name = input('\nInsert the name of the new key:\n')

        value_bool = input("\nWould you like to assign a value to the new key? [Y/n] ('null' by default)\n")
        if value_bool == 'Y':
            value = input('\nInsert the value of the new key:\n')
        else:
            value = 'null'

        if input(
                f"\nAre you sure you want to add the key '{new_name}'{' under ' if group_key else ''}"
                f"{group_key if group_key else ''} {'(' if macro_group_key else ''}"
                f"{macro_group_key if macro_group_key else ''}{') ' if macro_group_key else ''}"
                f"to all the models? [Y/n]\n") == 'Y':
            mmd.addKey(dict_key=group_key, macro_dict_key=macro_group_key, key_above=above_key,
                       name=new_name, key_value=value)
            print('\nProcess ended successfully.')
        else:
            print('\nThe process has been interrupted.')

    elif choice == 'v':
        key = input('\nInsert the name of the key whose value you want to change:\n')
        new_value = input('\nInsert the new value of the key:\n')
        if input(
                f"\nAre you sure you want to change the value of the key '{key}'{' under ' if group_key else ''}"
                f"{group_key if group_key else ''} {'(' if macro_group_key else ''}"
                f"{macro_group_key if macro_group_key else ''}{') ' if macro_group_key else ''}"
                f"to '{new_value}' for all the models? [Y/n]\n") == 'Y':
            mmd.changeValue(dict_key=group_key, macro_dict_key=macro_group_key, key_name=key, key_value=new_value)
            print('\nProcess ended successfully.')
        else:
            print('\nThe process has been interrupted.')

    else:
        print('\nThe process has been interrupted: action not recognized.')
