import os
from pathlib import Path

from steam_sdk.parsims.ParsimDakota import ParsimDakota
from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM

# this function is identical to test_ParsimDakota. However, using it give visual representation of outputs during runtime.

software = 'LEDET'
software = 'FiQuS'
#software = 'Analysis check'

if software == 'FiQuS':
    dakota_yaml_path = Path(r"input/TestFile_ParsimDakota_FiQuS_MQXA_multidim_parameter_study.yaml").resolve()
    pd = ParsimDakota(input_DAKOTA_yaml=dakota_yaml_path)
elif software == 'LEDET':
    dakota_yaml_path = Path(r"input/TestFile_ParsimDakota_LEDET_SMC_multidim_parameter_study.yaml").resolve()

    pd = ParsimDakota(input_DAKOTA_yaml=dakota_yaml_path)
else:
    analysis_yaml_path_this_iteration = r"../analyses/input/TestFile_AnalysisSTEAM_FiQuS_Multipole_Dakota.yaml"
    a = AnalysisSTEAM(file_name_analysis=analysis_yaml_path_this_iteration, relative_path_settings=os.path.dirname(analysis_yaml_path_this_iteration),
                                      file_path_list_models=None, verbose=True)
    a.run_analysis()