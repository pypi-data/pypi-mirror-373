from steam_sdk.data.DataAnalysis import AddAuxiliaryFile

def copy_input_files(aSTEAM, magnet_name, magnet_name_short_circuit, list_software, verbose):  # pragma: no cover

    # Add a step to the AnalysisSTEAM object to copy the self-mutual inductance .csv file from the STEAM models folder of the original (i.e. without short-circuit) magnet
    for software in list_software:
        if software == 'LEDET':
            step_add_inductance_file = f'add_inductance_file_{software}'
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_inductance_file] = AddAuxiliaryFile(type='AddAuxiliaryFile')
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_inductance_file].software = software
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_inductance_file].simulation_name = magnet_name_short_circuit
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_inductance_file].simulation_numbers = []  # not needed to be copied across
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_inductance_file].full_path_aux_file = f'../../steam_models/magnets/{magnet_name}/input/{magnet_name}_selfMutualInductanceMatrix.csv'
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_inductance_file].new_file_name = f'{magnet_name_short_circuit}_selfMutualInductanceMatrix.csv'
            aSTEAM.data_analysis.AnalysisStepSequence.append(step_add_inductance_file)
        else:
            raise Exception(f'Only LEDET is supported at the moment for this step.')

    # Add a step to the AnalysisSTEAM object to copy the .map2d file the STEAM models folder of the original (i.e. without short-circuit) magnet
    for software in list_software:
        if software == 'LEDET':
            step_add_field_map_file = f'add_map2d_{software}'
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_field_map_file] = AddAuxiliaryFile(type='AddAuxiliaryFile')
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_field_map_file].software = software
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_field_map_file].simulation_name = magnet_name_short_circuit
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_field_map_file].simulation_numbers = []  # not needed to be copied across
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_field_map_file].full_path_aux_file = f'input/{magnet_name}_All_WithIron_WithSelfField.map2d'
            aSTEAM.data_analysis.AnalysisStepDefinition[step_add_field_map_file].new_file_name = f'{magnet_name_short_circuit}_All_WithIron_WithSelfField.map2d'
            aSTEAM.data_analysis.AnalysisStepSequence.append(step_add_field_map_file)
        else:
            raise Exception(f'Only LEDET is supported at the moment for this step.')