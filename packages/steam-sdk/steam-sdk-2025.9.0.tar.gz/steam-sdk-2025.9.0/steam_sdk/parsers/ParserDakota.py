import os.path
from jinja2 import Environment, FileSystemLoader

from steam_sdk.parsers import templates
from steam_sdk.data.DataModelParsimDakota import DataModelParsimDakota
from steam_sdk.data.DataDakota import DataDakota
from steam_sdk.data.DataSettings import DataSettings
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing

class ParserDakota:

    @staticmethod
    def assemble_in_file(
            data_model_dakota: DataModelParsimDakota,
            dakota_working_folder: str = None,
            dakota_file_name: str = "dakota_in.in"
            ):
        """
        Generates Dakota compatible input file (with the .in extension) from TEAM SDK Dakota yaml file. It uses the template file of .in file.
        :param data_model_dakota: data class of data model dakota
        :type data_model_dakota: List[str]
        :param dakota_working_folder: optional output path (mostly used for testing)
        :type dakota_working_folder: str
        :param dakota_file_name: optional output path (mostly used for testing)
        :type dakota_file_name: str
        :return: Writes .in file to disk
        :rtype: None
        """

        # prepare dakota data for easier looping in the template
        dd = DataDakota()
        for name, var in data_model_dakota.study.variables.items():
            if data_model_dakota.study.type == 'multidim_parameter_study':
                dd.partitions.append(var.data_points - 1)
            elif data_model_dakota.study.type in ['optpp_q_newton','coliny_pattern_search']:
                dd.initial_point.append(var.initial_point)
                if(var.scale_type):
                    dd.scaling.append(var.scale_type)
                #dd.descriptors.append(var.descriptors)
            dd.lower_bounds.append(var.bounds.min)
            dd.upper_bounds.append(var.bounds.max)

        # load template
        loader = FileSystemLoader(templates.__path__)
        env = Environment(loader=loader, variable_start_string='<<', variable_end_string='>>',
                          trim_blocks=True, lstrip_blocks=True)
        env.globals.update(len=len)
        template = 'template_Dakota.in'
        in_template = env.get_template(template)

        # propagate data in the template
        output_from_parsed_template = in_template.render(dmd=data_model_dakota, dd=dd)

        # prepare output folder and file path
        dakota_in_output_file_path = os.path.join(dakota_working_folder, dakota_file_name)

        # save output file in the dakota_in_output_folder_path
        with open(dakota_in_output_file_path, "w") as tf:
            tf.write(output_from_parsed_template)
