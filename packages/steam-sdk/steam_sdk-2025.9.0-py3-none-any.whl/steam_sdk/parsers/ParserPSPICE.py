import ast
import csv
import datetime
import ntpath
import os
import re
import shutil
import textwrap
from itertools import zip_longest
from pathlib import Path
from typing import Union, List, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import interp1d

from steam_sdk.data.DataModelCircuit import DataModelCircuit, Component
from steam_sdk.parsers.ParserYAML import model_data_to_yaml
from steam_sdk.parsers.utils_ParserCircuits import read_circuit_data_from_model_data
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


class ParserPSPICE:
    """
        Class with methods to read/write PSPICE information from/to other programs
    """

    def __init__(self, circuit_data: DataModelCircuit, path_input: Path = None):
        """
            Initialization using a DataModelCircuit object containing circuit netlist structure
        """

        self.circuit_data: DataModelCircuit = circuit_data
        self.path_input: str = path_input


    def read_netlist(self, full_path_file_name: str, flag_acquire_auxiliary_files: bool = False, verbose: bool = False):
        '''
        ** Reads a PSPICE netlist file **

        :param full_path_file_name:
        :param flag_acquire_auxiliary_files: If True, add list of additional files to circuit_data
        :param verbose:
        :return: ModelCircuit dataclass with filled keys
        '''

        # Initialize
        self.circuit_data = DataModelCircuit()
        self.circuit_data.InitialConditions.initial_conditions = {}
        # Set flags indicating that the last read line corresponds to an item that might span to the next line
        self._set_all_flags_to_false()

        with open(full_path_file_name) as file:
            for row, line in enumerate(file):
                if verbose: print(line.rstrip())

                # Reset all flags to False if the line does not contain '+' in first position (excluding whitespaces)
                # Note: When one of these flags is set to True it indicates that this line might contain additional parameters from the previous line
                if (not '+' in line) and (not line.strip(' ')[0] == '+'):
                    self._set_all_flags_to_false()

                # If the line is a comment, skip to the next
                if '*' in line and line[0] == '*':
                    continue
                # If the line is empty, skip to the next
                if line == [] or line == [''] or line == '\n':
                    continue
                # If the line is the ending command, skip to the next
                if '.END' in line:
                    continue

                # Remove spaces before and after the "=" equal sign to make the parser more robust
                line = line.replace(' =', '=')
                line = line.replace('= ', '=')

                # Read stimuli
                if '.STMLIB' in line:
                    line_split = line.rstrip('\n').split(' ')  # Note: .rstrip('\n') removes the endline. .spolit(' ') makes a list of space-divided strings
                    value = line_split[1].strip('"')  # Note: .strip('"') removes all " sybmbols from the string
                    self.circuit_data.Stimuli.stimulus_files.append(str(value))
                    continue

                # Read libraries
                if '.LIB' in line:
                    line_split = line.rstrip('\n').split(' ')
                    value = line_split[1].strip('"')
                    self.circuit_data.Libraries.component_libraries.append(str(value))
                    continue

                # Read global parameters
                if '.PARAM' in line:  # it also covers the case where ".PARAMS" is written
                    self.flag_read_global_parameters = True
                    self.circuit_data.GlobalParameters.global_parameters = {}
                    continue
                if self.flag_read_global_parameters and '+ ' in line:
                    line_split = line.rstrip('\n').split(' ')
                    line_split = line_split[1].split('=')
                    name  = line_split[0].strip('"')
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.GlobalParameters.global_parameters[str(name)] = str(value)
                    continue

                # Read initial conditions
                # TODO: Known issue: this logic will not work if multiple initial conditions are defined in the same line
                if '.IC ' in line:
                    line_split = line.rstrip('\n').split('.IC ')
                    line_split = line_split[1].strip(' ').split(' ')  # remove whitespaces at the beginning and end of the string, then divide it at the internal whitespace
                    name  = line_split[0]
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.InitialConditions.initial_conditions[str(name)] = str(value)
                    continue

                # Read options
                if '.OPTION' in line:  # it also covers the case where ".OPTIONS" is written
                    self.flag_read_options = True
                    self.circuit_data.Options.options_simulation = {}
                    continue
                if self.flag_read_options and '+ ' in line:
                    line_split = line.rstrip('\n').strip(' ').split(' ')
                    line_split = line_split[1].split('=')
                    name  = line_split[0].strip('"')
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.Options.options_simulation[str(name)] = str(value)
                    continue

                # Read options
                if '.AUTOCONVERGE' in line:
                    self.flag_read_autoconverge = True
                    self.circuit_data.Options.options_autoconverge = {}
                    continue
                if self.flag_read_autoconverge and '+ ' in line:
                    line_split = line.rstrip('\n').strip(' ').split(' ')
                    line_split = line_split[1].split('=')
                    name  = line_split[0].strip('"')
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.Options.options_autoconverge[str(name)] = str(value)
                    continue

                # Read analysis
                if '.TRAN' in line:
                    self.circuit_data.Analysis.analysis_type = 'transient'
                    line_split = line.rstrip('\n').split(' ')
                    self.circuit_data.Analysis.simulation_time.time_start = str(line_split[1])
                    self.circuit_data.Analysis.simulation_time.time_end = str(line_split[2])
                    if len(line_split) > 3:
                        self.circuit_data.Analysis.simulation_time.min_time_step = str(line_split[3])
                    continue
                elif '.AC' in line:
                    self.circuit_data.Analysis.analysis_type = 'frequency'
                    line_split = line.rstrip('\n').split(' ')
                    self.circuit_data.Analysis.simulation_frequency.frequency_step = str(line_split[1])
                    self.circuit_data.Analysis.simulation_frequency.frequency_points = str(line_split[2])
                    self.circuit_data.Analysis.simulation_frequency.frequency_start = str(line_split[3])
                    self.circuit_data.Analysis.simulation_frequency.frequency_end = str(line_split[4])
                    continue
                elif '.STEP' in line:
                    # TODO. Parametric analysis
                    continue

                # Read time schedule
                if '+ {SCHEDULE(' in line:
                    self.flag_read_time_schedule = True
                    self.circuit_data.Analysis.simulation_time.time_schedule = {}
                    continue
                # If the line is the end of the time schedule section, skip to the next
                if '+ )}' in line or '+)}' in line:
                    continue
                if self.flag_read_time_schedule and '+ ' in line:
                    line_split = line.rstrip('\n').split('+ ')
                    line_split = line_split[1].split(',')
                    name  = line_split[0].strip(' ').strip('\t').strip(' ')
                    value = line_split[1].strip(' ').strip('\t').strip(' ')
                    self.circuit_data.Analysis.simulation_time.time_schedule[str(name)] = str(value)
                    continue

                # Read load-bias-points options
                if line.lower().startswith('.loadbias'):
                    self.circuit_data.BiasPoints.load_bias_points.file_path = line.rstrip('\n').split(' ')[1].strip('"').strip("'")
                    continue

                # Read save-bias-points options
                if line.lower().startswith('.savebias'):
                    if 'tran time=' in line.lower():  # this covers the cases "TRAN TIME=" and "tran time="
                        self.circuit_data.BiasPoints.save_bias_points.file_path = line.rstrip('\n').split(' ')[1].strip('"').strip("'")
                        self.circuit_data.BiasPoints.save_bias_points.analysis_type = 'transient'
                        self.circuit_data.BiasPoints.save_bias_points.save_bias_time = float(line.lower().rstrip('\n').split('tran time=')[1])
                        continue
                    else:
                        raise Exception(f'Error when trying to parse this line, which starts with \".savebias\" but does not contain a valid string that can be parsed to determine the analysis type (for example, \"TRAN TIME=\"). Line is: {line}')

                # Read probe
                if '.PROBE' in line:
                    if '/CSDF' in line:
                        self.circuit_data.PostProcess.probe.probe_type = 'CSDF'
                    else:
                        self.circuit_data.PostProcess.probe.probe_type = 'standard'
                    self.flag_read_probe = True
                    # TODO: Known issue: If probe variables are defined in this same line, they are ignored
                    continue
                if self.flag_read_probe and '+ ' in line:
                    line_split = line.rstrip('\n').split(' ')
                    value = line_split[1]
                    self.circuit_data.PostProcess.probe.variables.append(str(value))
                    continue

                # Read additional files
                if '.INC' in line:
                    line_split = line.rstrip('\n').split(' ')
                    value = line_split[1].strip('"')
                    self.circuit_data.AuxiliaryFiles.files_to_include.append(str(value))
                    continue

                    # TODO delete
                # # Read netlist - If this part of the code is reached without hitting "continue", it means that this
                # # line does not define a special command, and hence it defines a component of the netlist
                # if (not self.circuit_data.Netlist[0].name == None) and (not self.flag_read_parametrized_component):  # Append a new component (unless it is the first component)
                #     self.circuit_data.Netlist.append(Component_OLD())

                # Special case: Stimulus-controlled component
                if 'STIMULUS=' in line.replace(' ', ''):  # this covers the cases "STIMULUS = ", "STIMULUS=", etc
                    line_split = line.rstrip('\n').split('(')  # TODO: Improve the logic, which now fails if the value includes the character "("
                    name = str(line_split[0].strip(' '))
                    line_split = line_split[1].rstrip('\n').split(')')
                    nodes = line_split[0].split(' ')
                    line_split = line_split[1].split('=')
                    value = line_split[1].strip(' { } ')  # Strip spaces and bracket at the extremities
                    new_Component = Component()
                    new_Component.type = 'stimulus-controlled component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist[name] = new_Component
                    continue

                # Special case: Pulsed power source
                if 'PULSE' in line.replace(' ', ''):
                    # Note: The following logic works for three different syntaxes: "PULSE(value)", "PULSE (value)" and "PULSE value"
                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    line_after = line_after.partition('PULSE')[2]  # Take the part of the string after the first "VALUE " chars
                    value = line_after.strip(' ( ) ')  # Strip spaces and bracket at the extremities
                    new_Component = Component()
                    new_Component.type = 'pulsed-source component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist[name] = new_Component
                    continue

                # Special case: Controlled-source component
                # E: Voltage-controlled voltage source
                # F: Current-controlled current source
                # G: Voltage-controlled current source
                # H: Current-controlled voltage source
                # TODO Known issue: it fails to read correctly the nodes/parameters if the nodes contain brakets
                # TODO Known issue: it fails to read correctly E/F/G/H where "VALUE" is not present
                if ('VALUE' in line) and ((line[0] == 'E') or (line[0] == 'F') or (line[0] == 'G') or (line[0] == 'H')):
                    # Find the correct delimiter to cover multiple syntaxes
                    if 'VALUE = ' in line: delimiter_value = 'VALUE = '
                    elif 'VALUE =' in line: delimiter_value = 'VALUE ='
                    elif 'VALUE= ' in line: delimiter_value = 'VALUE= '
                    elif 'VALUE=' in line: delimiter_value = 'VALUE='
                    elif 'VALUE ' in line: delimiter_value = 'VALUE '

                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    line_after = line_after.partition(delimiter_value)[2]  # Take the part of the string after the first "delimiter_value" chars
                    value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                    new_Component = Component()
                    new_Component.type = 'controlled-source component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist[name] = new_Component
                    continue

                # Special case: Diode component
                if ('d' in line and line[0] == 'd') or ('D' in line and line[0] == 'D'):
                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                    self.name_last_component = name
                    new_Component = Component()
                    new_Component.type = 'Diode component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist[self.name_last_component] = new_Component
                    continue

                # Special case: Parametrized component
                if ('x' in line and line[0] == 'x') or ('X' in line and line[0] == 'X'):
                    self.flag_read_parametrized_component = True
                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                    self.name_last_component = name
                    new_Component = Component()
                    new_Component.type = 'parametrized component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist[self.name_last_component] = new_Component
                    continue

                # Special case: Parameters of a parametrized component
                if self.flag_read_parametrized_component and '+ PARAM' in line:  # This line defines parameters of the component
                    # Reminder: This type of line looks like this: + PARAMS: name1={value1} name2={value2} name3={value3}
                    line_split = line.rstrip('\n').partition(':')[2]  # Take the part of the string after the first "+" char
                    # line_split = line.rstrip('\n').split(':')  # Split line in two, before and after the "+ PARAMS:" command
                    # line_split = line_split[1].strip(' ')      # Take the second element and remove whitespaces at its extremities
                    line_split = line_split.split(' ')         # Split into different parameters

                    continue_Component = self.circuit_data.Netlist[self.name_last_component]
                    for par in line_split:                     # Loop through the parameters
                        par_split = par.split('=')             # Split into name and value of the parameter
                        if len(par_split) == 2:                # Only take into account entries with two elements (for example, avoid None)
                            name_par = str(par_split[0].strip(' '))
                            value_par = str(par_split[1].strip(' { } '))  # Strip spaces and bracket at the extremities
                            continue_Component.parameters[str(name_par)] = str(value_par)
                    self.circuit_data.Netlist[self.name_last_component] = continue_Component
                    continue
                elif self.flag_read_parametrized_component and '+' in line and line[0] == '+':  # This line defines additional parameters of the component
                    # Reminder: This type of line looks like this: + PARAMS: name1={value1} name2={value2} name3={value3}
                    line_split = line.rstrip('\n').partition('+')[2]        # Take the part of the string after the first "+" char
                    line_split = line_split.split(' ')                      # Split into different parameters
                    continue_Component = self.circuit_data.Netlist[self.name_last_component]
                    for par in line_split:                                  # Loop through the parameters
                        par_split = par.split('=')                          # Split into name and value of the parameter
                        if len(par_split) == 2:                             # Only take into account entries with two elements (for example, avoid None)
                            name_par  = str(par_split[0].strip(' '))
                            value_par = str(par_split[1].strip(' { } '))  # Strip spaces and bracket at the extremities
                            continue_Component.parameters[str(name_par)] = str(value_par)
                    self.circuit_data.Netlist[self.name_last_component] = continue_Component
                    continue

                # If this part of the code is reached, the line defines standard component
                line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                name = line_before.strip(' ')
                line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                nodes = line_before.split(' ')
                value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                new_Component = Component()
                new_Component.type = 'standard component'
                new_Component.nodes = nodes
                new_Component.value = str(value)
                self.circuit_data.Netlist[name] = new_Component

        # Simplify options keys if they have default values
        if self.circuit_data.Options.options_simulation == get_default_options():
            if verbose: print('Default simulation options are applied.')
            self.circuit_data.Options.options_simulation = {'all options': 'default'}
        if self.circuit_data.Options.options_autoconverge == get_default_autoconverge_options():
            if verbose:  print('Default simulation autoconvergence options are applied.')
            self.circuit_data.Options.options_autoconverge = {'all options': 'default'}

        if flag_acquire_auxiliary_files:
            # Read entries of required additional files and add them to the yaml dictionary
            # Add stimulus files (defined with ".STMLIB" option)
            for file in self.circuit_data.Stimuli.stimulus_files:
                self.circuit_data.GeneralParameters.additional_files.append(file)
            # Add component library files (defined with ".LIB" option)
            for file in self.circuit_data.Libraries.component_libraries:
                self.circuit_data.GeneralParameters.additional_files.append(file)
            # Add files to include (defined with ".INC" option)
            for file in self.circuit_data.AuxiliaryFiles.files_to_include:
                self.circuit_data.GeneralParameters.additional_files.append(file)
            if verbose:
                print('Option flag_acquire_auxiliary_files set to {}'.format(flag_acquire_auxiliary_files))
                for file in self.circuit_data.GeneralParameters.additional_files:
                    print('File {} added to the list of files to add to the model.'.format(file))

        return self.circuit_data


    def _set_all_flags_to_false(self):
        '''
            # Set flags indicating that the last read line corresponds to an item that might span to the next line
        '''
        self.flag_read_global_parameters = False
        self.flag_read_parametrized_component = False
        self.flag_read_options = False
        self.flag_read_autoconverge = False
        self.flag_read_time_schedule = False
        self.flag_read_probe = False
        self.name_last_component = None  # this is used to have the name of the latest added component (used to read the parameters of parametrized component over multiple rows)


    def write2pspice(self, full_path_file_name: str, verbose: bool = False):
        '''
        ** Writes a PSPICE netlist file **

        :param full_path_file_name:
        :param verbose:
        :return:
        '''
        make_folder_if_not_existing(os.path.dirname(full_path_file_name), verbose=verbose)

        # Prepare header
        time_start = datetime.datetime.now()
        rows_header = [
            add_comment('PSPICE Netlist Simulation File'),
            add_comment(f'Generated at {time_start} at CERN using STEAM_SDK'),
            add_comment('Authors: STEAM Team'),
        ]

        # Prepare stimuli
        rows_stimuli = []
        if self.circuit_data.Stimuli.stimulus_files:
            rows_stimuli.append(add_comment('**** Stimulus files ****'))  # Add header of this section
            for s in self.circuit_data.Stimuli.stimulus_files:
                rows_stimuli.append(add_stimulus(s))

        # Prepare libraries
        rows_libraries = []
        if self.circuit_data.Libraries.component_libraries:
            rows_libraries.append(add_comment('**** Component libraries ****'))  # Add header of this section
            for s in self.circuit_data.Libraries.component_libraries:
                rows_libraries.append(add_library(s))

        # Prepare global parameters
        rows_global_parameters = []
        if self.circuit_data.GlobalParameters.global_parameters:
            # Add comment and .PARAM command before the first entry
            rows_global_parameters.append(add_comment('**** Global parameters ****'))  # Add header of this section
            rows_global_parameters.append('.PARAM')  # Add header of this section
            # Add global parameter entries
            for name, value in self.circuit_data.GlobalParameters.global_parameters.items():
                rows_global_parameters.append(add_global_parameter(name, value))

        # Prepare initial conditions
        rows_initial_conditions = []
        if self.circuit_data.InitialConditions.initial_conditions:
            # Add comment and .PARAM command before the first entry
            rows_initial_conditions.append(add_comment('**** Initial conditions ****'))  # Add header of this section
            # Add initial condition entries
            for name, value in self.circuit_data.InitialConditions.initial_conditions.items():
                rows_initial_conditions.append(add_initial_condition(name, value))

        # Prepare netlist
        rows_netlist = []
        rows_netlist.append(add_comment('**** Netlist ****'))  # Add header of this section
        for s, name in enumerate(self.circuit_data.Netlist.keys()):
            # Read keys
            type = getattr(self.circuit_data.Netlist[name], 'type')
            nodes = getattr(self.circuit_data.Netlist[name], 'nodes')
            value = getattr(self.circuit_data.Netlist[name], 'value')
            parameters = getattr(self.circuit_data.Netlist[name], 'parameters')
            # name, nodes, value, parameters, type = component.name, component.nodes, component.value, component.parameters, component.type

            # Check inputs
            if not type:
                raise Exception('At least one netlist entry of known type must be added. Supported component types:\n' +
                                '- comment\n' +
                                '- standard component\n'
                                '- Diode component\n'
                                '- stimulus-controlled component\n'
                                '- controlled-source component\n'
                                '- pulsed-source component\n'
                                '- parametrized component\n'
                                '- transient-source component\n'
                                'Netlist cannot be generated.')

            # Add the relevant row depending on the component type
            if type == 'comment':
                if verbose: print('Netlist entry {} in position #{} is treated as a comment.'.format(name, s + 1))
                rows_netlist.append(add_comment(value))
            elif type == 'standard component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a standard component.'.format(name, s + 1))
                rows_netlist.append(add_standard_component(name, nodes, value))
            elif type == 'Diode component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a standard component.'.format(name, s + 1))
                rows_netlist.append(add_Diode_component(name, nodes, value))
            elif type == 'stimulus-controlled component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a stimulus-controlled component.'.format(name, s + 1))
                rows_netlist.append(add_stimulus_controlled_component(name, nodes, value))
            elif type == 'pulsed-source component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a pulsed-source component.'.format(name, s + 1))
                rows_netlist.append(add_pulsed_source_component(name, nodes, value))
            elif type == 'controlled-source component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a controlled-source component.'.format(name, s + 1))
                rows_netlist.append(add_controlled_source_component(name, nodes, value))
            elif type == 'transient-source component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a transient-source component.'.format(name, s + 1))
                rows_netlist.append(add_transient_source_component(name, nodes, value))
            elif type == 'parametrized component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a parametrized component.'.format(name, s + 1))
                rows_netlist.append(add_parametrized_component(name, nodes, value, parameters))
            else:
                raise Exception ('Netlist entry {} in position #{} has an unknown type: {}.'.format(name, s+1, type))

        keywords_Options = ['reltol', 'vntol', 'abstol', 'chgtol', 'gmin', 'itl1', 'itl2', 'itl4', 'tnom', 'numdgt']  # Not complete list, but most used
        keywords_autoConverge = ['reltol', 'vntol', 'abstol', 'itl1', 'itl2', 'itl4', 'pivtol']

        # Prepare options - Simulation options
        rows_options = []
        options = self.circuit_data.Options.options_simulation
        if options:
            if options == {'all options': 'default'}:
                if verbose: print('Default simulation options are applied.')
                options = get_default_options()

            overlap_options = [i for i in list(options.keys()) if i.casefold() in keywords_Options]
            if overlap_options:
                # Add comment and .OPTIONS command before the first entry
                rows_options.append(add_comment('**** Simulation parameters ****'))  # Add header of this section

                # Add comment and .OPTIONS command before the first entry
                rows_options.append(add_comment('**** Simulation parameters ****'))  # Add header of this section
                rows_options.append('.OPTIONS')  # Add header of this section
                # Add option entries
                for name in overlap_options:
                    rows_options.append(add_option(name, str(options[name])))

        # Prepare options - Autoconverge simulation options
        options_autoconverge = self.circuit_data.Options.options_autoconverge
        if options_autoconverge:
            if options_autoconverge == {'all options': 'default'}:
                if verbose: print('Default autoconverge simulation options_autoconverge are applied.')
                options_autoconverge = get_default_autoconverge_options()
            overlap_options_autoconverge = [i for i in list(options_autoconverge.keys()) if i.casefold() in keywords_autoConverge]
            if overlap_options_autoconverge:
                # Add comment and .AUTOCONVERGE command before the first entry
                rows_options.append(add_comment('**** Simulation autoconverge options ****'))  # Add header of this section
                rows_options.append('.AUTOCONVERGE')  # Add header of this section
                # Add option entries
                for name in overlap_options_autoconverge:
                    rows_options.append(add_option(name, str(options_autoconverge[name])))

        # Prepare analysis settings
        rows_analysis = []
        analysis_type = self.circuit_data.Analysis.analysis_type
        if analysis_type == 'transient':
            # Unpack inputs
            time_start = self.circuit_data.Analysis.simulation_time.time_start
            time_end = self.circuit_data.Analysis.simulation_time.time_end
            min_time_step = self.circuit_data.Analysis.simulation_time.min_time_step
            time_schedule = self.circuit_data.Analysis.simulation_time.time_schedule
            # Check inputs
            if time_start == None:
                time_start = '0'
                if verbose: print('Parameter time_start set to {} by default.'.format(time_start))
            if not time_end:
                raise Exception('When "transient" analysis is selected, parameter Analysis.simulation_time.time_end must be defined.')
            if not min_time_step:
                if verbose: print('Parameter min_time_step was missing and it will not be written.')
            # Add analysis entry
            rows_analysis.append(add_transient_analysis(time_start, time_end, min_time_step))
            # If defined, add time schedule (varying minimum time stepping) entry
            if time_schedule and len(time_schedule) > 0:
                rows_analysis.append(add_transient_time_schedule(time_schedule))
        elif analysis_type == 'frequency':
            # Unpack inputs
            frequency_step = self.circuit_data.Analysis.simulation_frequency.frequency_step
            frequency_points = self.circuit_data.Analysis.simulation_frequency.frequency_points
            frequency_start = self.circuit_data.Analysis.simulation_frequency.frequency_start
            frequency_end = self.circuit_data.Analysis.simulation_frequency.frequency_end
            # Check inputs
            if frequency_step not in ['DEC','LIN','OCT']:
                raise Exception('Frequency step in AC analysis has to be one of [DEC,LIN,OCT]')
            if 'Hz' not in frequency_start:
                frequency_start = str(frequency_start)+'Hz'
                if verbose: print('No unit found in AC analysis starting frequency. Added unit Hz')
            if 'Hz' not in frequency_end:
                frequency_end = str(frequency_end)+'Hz'
                if verbose: print('No unit found in AC analysis last frequency. Added unit Hz')
            if not frequency_step or not frequency_start or not frequency_end or not frequency_points:
                raise Exception('A parameter for AC analysis is missing.')
            # Add analysis entry
            rows_analysis.append(add_AC_analysis(frequency_step, frequency_points, frequency_start, frequency_end))
        elif analysis_type == None:
            pass  # netlists can exist that do not have analysis set (for example, it could be defined in an auxiliary file)
        # TODO: DC analysis
        # TODO: parametric analysis. EXAMPLE: .STEP PARAM C_PARALLEL LIST 100n 250n 500n 750n 1u
        else:
            raise Exception('Analysis entry has an unknown type: {}.'.format(analysis_type))

        # Prepare bias settings
        rows_bias_points = []
        rows_bias_points.append(add_comment('**** Load/save bias points options ****'))  # Add header of this section
        # Load bias point settings
        if self.circuit_data.BiasPoints.load_bias_points.file_path:
            if not self.circuit_data.BiasPoints.load_bias_points.file_path.endswith('.bsp'):
                print(f'WARNING. The load-bias-points file expected extension is .bsp, but the file name is {self.circuit_data.BiasPoints.load_bias_points.file_path}. Consider changing the key BiasPoints.load_bias_points.file_path')
            rows_bias_points.append(add_load_bias_points(self.circuit_data.BiasPoints.load_bias_points.file_path))
        # Save bias point settings
        if self.circuit_data.BiasPoints.save_bias_points.file_path:
            if not self.circuit_data.BiasPoints.save_bias_points.file_path.endswith('.bsp'):
                print(f'WARNING. The save-bias-points file expected extension is .bsp, but the file name is {self.circuit_data.BiasPoints.save_bias_points.file_path}. Consider changing the key BiasPoints.load_bias_points.file_path')
            rows_bias_points.append(add_save_bias_points(file_path=self.circuit_data.BiasPoints.save_bias_points.file_path,
                                                         analysis_type=self.circuit_data.BiasPoints.save_bias_points.analysis_type,
                                                         save_bias_time=self.circuit_data.BiasPoints.save_bias_points.save_bias_time))

        # Prepare post-processing settings
        rows_post_processing = []
        rows_post_processing.append(add_comment('**** Probe (output variables) options ****'))  # Add header of this section
        probe_type = self.circuit_data.PostProcess.probe.probe_type
        probe_variables = self.circuit_data.PostProcess.probe.variables
        if probe_type:
            rows_post_processing.append(add_probe(probe_type, probe_variables))

        # Prepare additional files to include
        rows_files_to_include = []
        if self.circuit_data.AuxiliaryFiles.files_to_include:
            rows_files_to_include.append(add_comment('**** Auxiliary files ****'))  # Add header of this section
            for s in self.circuit_data.AuxiliaryFiles.files_to_include:
                rows_files_to_include.append(add_auxiliary_file(s))

        # Prepare file end
        rows_file_end = [add_end_file()]

        # Assemble all rows to write
        rows_to_write = \
            rows_header + \
            rows_stimuli + \
            rows_libraries + \
            rows_global_parameters + \
            rows_initial_conditions + \
            rows_netlist + \
            rows_options + \
            rows_analysis + \
            rows_bias_points + \
            rows_post_processing + \
            rows_files_to_include + \
            rows_file_end

        # Write netlist file
        with open(full_path_file_name, 'w') as f:
            for row in rows_to_write:
                if verbose: print(row)
                f.write(row)
                f.write('\n')

        # Display time stamp
        time_written = datetime.datetime.now()
        if verbose:
            print(' ')
            print('Time stamp: ' + str(time_written))
            print('New file ' + full_path_file_name + ' generated.')


    def readFromYaml(self, full_path_file_name: str, verbose: bool = False):
        '''
        Load yaml keys into DataModelCircuit dataclass

        :param full_path_file_name: Path to the file to read
        :param verbose: If True, display logging information
        :return:
        '''
        self.circuit_data = read_circuit_data_from_model_data(full_path_file_name=full_path_file_name, verbose=verbose)


    def write2yaml(self, full_path_file_name: str, verbose: bool = False):
        '''
        ** Write netlist to yaml file **
        :param full_path_file_name:
        :param verbose:
        :return:
        '''
        # This hard-coded list defines the keys that will NOT be written in a single row in the output yaml file
        list_exceptions = [
            'additional_files',
            'files_to_include',
            'stimulus_files',
            'component_libraries',
            'variables',
            ]

        # all_data_dict = {**self.circuit_data.dict()}
        # dict_to_yaml(all_data_dict, full_path_file_name, list_exceptions=list_exceptions)
        model_data_to_yaml(self.circuit_data, full_path_file_name, list_exceptions=list_exceptions)
        if verbose:
            print('New file ' + full_path_file_name + ' generated.')

    def copy_additional_files(self, output_path: str, verbose: bool = False):
        '''
            Copy additional files
            :param output_path: Output folder
            :param verbose: If True, display logging information
        :return: Number of copied files
        '''

        make_folder_if_not_existing(output_path, verbose=verbose)

        list_files_to_copy = self.circuit_data.GeneralParameters.additional_files
        # Special case: Copy coil_resistances.stl file as well (this file is used for co-simulations)
        list_files_to_copy.append('coil_resistances.stl')

        for file_to_copy in list_files_to_copy:
            if not os.path.isabs(file_to_copy) and self.path_input:
                # If the provided path is relative, use the path_input as the root folder (if available)
                file_to_copy_relative = os.path.join(self.path_input, file_to_copy)
                file_to_copy = file_to_copy_relative
                if verbose:
                    print(f'Relative path changed from {file_to_copy} to {file_to_copy_relative}.')

            file_name = ntpath.basename(file_to_copy)
            file_to_write = os.path.join(output_path, file_name)
            if os.path.isfile(os.path.join(file_to_copy)):
                if verbose: print(f'File {file_to_copy} exists.')
            else:
                if verbose: print(f'File {file_to_copy} does not exist. Skipped.')
                continue
            if os.path.isdir(output_path):
                if verbose: print(f'Folder {output_path} exists.')
            else:
                if verbose: print(f'Folder {output_path} does not exist. Skipped.')
                continue
            shutil.copyfile(Path(file_to_copy), Path(file_to_write))

            if verbose:
                print(f'Additional file copied from {file_to_copy} to {file_to_write}.')
        return len(list_files_to_copy)


#######################  Helper functions - START  #######################
def add_comment(text: str):
    ''' Format comment row '''
    if text[0] == '*':
        return text  # If the input string starts with a "*", leave it unchanged (it is already a comment)
    formatted_text = '* ' + text
    return formatted_text

def add_stimulus(text: str):
    ''' Format stimulus row '''
    formatted_text = '.STMLIB ' + text
    return formatted_text

def add_library(text: str):
    ''' Format library row '''
    formatted_text = '.LIB \"' + text + '\"'
    return formatted_text

def add_global_parameter(name: str, value: str):
    ''' Format global parameters row '''
    formatted_text = '+ ' + name + '={' + str(value) + '}'
    return formatted_text

def add_initial_condition(name: str, value: str):
    ''' Format initial condition row '''
    formatted_text = '.IC ' + name + ' {' + str(value) + '}'
    return formatted_text

def add_standard_component(name: str, nodes: list, value: str):
    ''' Format standard component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    formatted_text = name + ' (' + str_nodes + ') ' + '{' + str(value) + '}'
    return formatted_text

def add_Diode_component(name: str, nodes: list, value: str):
    ''' Format Diode component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    formatted_text = name + ' (' + str_nodes + ') ' + str(value)
    return formatted_text

def add_stimulus_controlled_component(name: str, nodes: list, value: str):
    ''' Format stimulus-controlled component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    if '(' in value and ')' in value:
        str_stimulus = 'PWL ' + value
    else:
        str_stimulus = 'STIMULUS = ' + value
    formatted_text = name + ' (' + str_nodes + ') ' + str_stimulus
    return formatted_text

def add_pulsed_source_component(name: str, nodes: list, value: str):
    ''' Format pulsed-source component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    str_pulse = 'PULSE(' + str(value) + ')'
    formatted_text = name + ' (' + str_nodes + ') ' + str_pulse
    return formatted_text

def add_controlled_source_component(name: str, nodes: list, value: str):
    ''' Format controlled-source component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    str_stimulus = 'VALUE ' + '{' + value + '}'
    formatted_text = name + ' (' + str_nodes + ') ' + str_stimulus
    return formatted_text

def add_transient_source_component(name: str, nodes: list, value: str):
    ''' Format controlled-source component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    str_stimulus = 'AC ' + '{' + value + '}'
    formatted_text = name + ' (' + str_nodes + ') ' + str_stimulus
    return formatted_text

def add_parametrized_component(name: str, nodes: list, value: str, parameters: dict):
    ''' Format parametrized component netlist row '''
    str_nodes = " ".join(map(str, nodes))   # string with space-separated nodes
    formatted_component = name + ' (' + str_nodes + ') ' + value  # First row, which defines the component
    if parameters:
        formatted_component = formatted_component + '\n'
        formatted_parameters = '+ PARAMS:'  # First part of the string in the second row, which defines the component parameters
        # for parameter in parameters:
        #     if len(parameter) != 2:
        #         raise Exception ('All parameters entries in a parametrized element must have 2 elements (name, value), but parameter {} has {} elements.'.format(name, len(parameter)))
        #     name_parameters, value_parameters = parameter[0], parameter[1]
        #     formatted_parameters = formatted_parameters + ' ' + name_parameters + '={' + value_parameters + '}'
        for name_parameters, value_parameters in parameters.items():
            # if len(parameter) != 2:
            #     raise Exception ('All parameters entries in a parametrized element must have 2 elements (name, value), but parameter {} has {} elements.'.format(name, len(parameter)))
            formatted_parameters = formatted_parameters + ' ' + name_parameters + '={' + str(value_parameters) + '}'

        # Make sure the maximum number of characters in each row does not exceed 132, which is the maximum that PSPICE supports
        N_MAX_CHARS_PER_ROW = 130
        formatted_parameters = textwrap.fill(formatted_parameters, N_MAX_CHARS_PER_ROW)
        formatted_parameters = formatted_parameters.replace('\n', '\n+ ')  # Add "+ " at the beginning of each new line
    else:
        formatted_parameters = ''  # If no parameters are defined, empty string

    formatted_text = formatted_component + formatted_parameters  # Concatenate the two rows
    return formatted_text

def add_option(name: str, value: str):
    ''' Format option row '''
    formatted_text = '+ ' + name + '=' + value
    return formatted_text

def add_transient_analysis(time_start, time_end, min_time_step = None):
    ''' Format transient analysis row '''
    formatted_text = '.TRAN ' + str(time_start) + ' ' + str(time_end)
    if not min_time_step == None:
        formatted_text = formatted_text + ' ' + str(min_time_step)
    return formatted_text


def add_AC_analysis(frequency_step, frequency_points, frequency_start, frequency_end):
    ''' Format transient analysis row '''
    formatted_text = f'.AC {frequency_step} {str(int(frequency_points))} {str(frequency_start)} {str(frequency_end)}'
    return formatted_text

def add_transient_time_schedule(time_schedule):
    ''' Format transient time schedule rows '''
    # If time_schedule is not defined, output will be None
    if time_schedule == None or len(time_schedule) == 0:
        return None

    # If the variable is a string, convert it to a dictionary
    if isinstance(time_schedule, str):
        time_schedule = ast.literal_eval(time_schedule)

    formatted_text = '+ {SCHEDULE(\n'
    for time_window_start, time_step_in_window in time_schedule.items():
        if time_window_start == list(time_schedule.keys())[-1]:
            formatted_text = formatted_text + '+ ' + str(time_window_start) + ', ' + str(time_step_in_window) + '\n'  # the last entry must not have the comma
        else:
            formatted_text = formatted_text + '+ ' + str(time_window_start) + ', ' + str(time_step_in_window) + ',' + '\n'
    formatted_text = formatted_text + '+)}'
    return formatted_text

def add_load_bias_points(file_path: str):
    ''' Format load bias row '''
    formatted_text = f'.loadbias "{file_path}"'
    return formatted_text

def add_save_bias_points(file_path: str, analysis_type: str, save_bias_time: float):
    ''' Format save bias row '''
    if analysis_type == 'transient':
        analysis_label = 'TRAN TIME='
    else:
        raise Exception(f'Analysis type {analysis_type} is not supported for the save-bias-point option. Supported values are: \"transient\". Look at the BiasPoints.save_bias_points.analysis_type key')
    formatted_text = f'.savebias "{file_path}" {analysis_label}{save_bias_time}'
    return formatted_text

def add_probe(probe_type: str, probe_variables: list):
    ''' Format probe row '''
    if probe_type == 'standard':
        formatted_text = '.PROBE'
    elif probe_type == 'CSDF':
        formatted_text = '.PROBE/CSDF'
    elif not probe_type:
        return None
    else:
        raise Exception('Probe entry has an unknown type: {}.'.format(probe_type))

    for var in probe_variables:
        formatted_text = formatted_text + '\n' + '+ ' + var
    return formatted_text

def add_auxiliary_file(file_to_add: str):
    ''' Format auxiliary file rows '''
    formatted_text = '.INC ' + file_to_add
    return formatted_text

def add_end_file():
    formatted_text = '.END'
    return formatted_text

def get_default_options():
    options = {
        'RELTOL': '0.0001',
        'VNTOL': '0.00001',
        'ABSTOL': '0.0001',
        'CHGTOL': '0.000000000000001',
        'GMIN': '0.000000000001',
        'ITL1': '150',
        'ITL2': '20',
        'ITL4': '10',
        'TNOM': '27',
        'NUMDGT': '8',
    }
    return options

def get_default_autoconverge_options():
    options_autoconverge = {
        'RELTOL': '0.05',
        'VNTOL': '0.0001',
        'ABSTOL': '0.0001',
        'ITL1': '1000',
        'ITL2': '1000',
        'ITL4': '1000',
        'PIVTOL': '0.0000000001',
    }
    return options_autoconverge

def ComparePSPICEParameters(fileA, fileB):
    '''
        Compare all the variables imported from two PSPICE netlists
    '''

    pp_a = ParserPSPICE(None)
    pp_a.read_netlist(fileA, verbose=False)
    pp_b = ParserPSPICE(None)
    pp_b.read_netlist(fileB, verbose=False)
    print("Comparing File A: ({}) and File B: ({})".format(fileA, fileB))

    flag_equal = pp_a.circuit_data == pp_b.circuit_data
    return flag_equal

#######################  Helper functions - END  #######################

#######################  Interpolating Resistance ######################
def InterpolateResistance(current_level: float, path_resources: str, n_apertures: int = 2, Type: str = 'Linear', plot_interpolation: bool = False):
    '''
    Function to interpolate a resistance based on given, pre-calculated resistance values at different current level.
    2 different options are available: Linear or Spline interpolation. Interpolation is done at each timestep, with all
    available resistance values

    :param current_level: float, current level to be interpolated
    :param path_resources: str, path to the file with pre-calculated values
    :param n_apertures: int, Number of apertures to calculate a resistance for
    :param Type: str, either Linear or Spline, type of interpolation
    :param plot_interpolation: bool
    :return [time, new_R1, new_R2]: list of np.array, [time vector, resistance values for Ap. 1, Ap. 2]
    '''

    if Type not in ['Linear', 'Spline']:
        raise Exception(f'Type not understood. Chosen {Type} but only "Linear", "Spline" available.')

    ## Read the resistance values from a given file
    Intp_file = path_resources
    Intp_data = pd.read_csv(Intp_file, low_memory=False)
    col_t = []
    col_r1 = []
    col_r2 = []

    for col in Intp_data.columns:
        try:
            _ = float(col)
            idx = Intp_data.columns.get_loc(col)
            col_t.append(Intp_data.columns[idx]) # Time
            col_r1.append(Intp_data.columns[idx + 1]) # Aperture 1
            if n_apertures == 2: col_r2.append(Intp_data.columns[idx + 2]) # Aperture 2
        except:
            pass
    data_R1 = Intp_data[col_r1].drop([0]).to_numpy().astype(float)
    if n_apertures == 2:
        data_R2 = Intp_data[col_r2].drop([0]).to_numpy().astype(float)
    time = Intp_data[col_t[-1]].drop([0]).to_numpy().astype(float)

    ## Interpolate new current level based on given values
    new_R1 = []
    new_R2 = []
    current_level = np.array([current_level]).reshape(-1, 1)

    x = np.array(col_t).astype(float).reshape(-1, 1)

    # Loop through all time values, to obtain an interpolation for each time value
    for k in range(time.shape[0]):
        ## Start with interpolating values for R1 (aperture 1)
        # Obtain all resistance values of R1, available in the current time step (drop NaN)
        new_y = data_R1[k][~np.isnan(data_R1[k])].reshape(-1, )
        # Obtain the respective current values to the resistances
        new_x = x[~np.isnan(data_R1[k])].reshape(-1, )

        # 1. Available option: Spline interpolation (deprecated as poor performance)
        if Type == 'Spline':
            new_x = new_x[::-1]
            new_y = new_y[::-1]

            if len(new_x) <= 3:
                new_R1 = np.append(new_R1, np.nan)
            else:
                spl = UnivariateSpline(new_x, new_y)
                new_R1 = np.append(new_R1, spl(current_level))
        # 2. option: Linear interpolation
        elif Type == 'Linear':
            if current_level <= max(new_x):
                f = interp1d(new_x, new_y)
                new_R1 = np.append(new_R1, f(current_level))
            else:
                new_R1 = np.append(new_R1, np.nan)

        if n_apertures == 2:
            ## Repeat procedure for R2 (aperture 2)
            new_y = data_R2[k][~np.isnan(data_R2[k])].reshape(-1, )
            new_x = x[~np.isnan(data_R2[k])].reshape(-1, )
            if Type == 'Spline':
                new_x = new_x[::-1]
                new_y = new_y[::-1]

                if len(new_x) <= 3:
                    new_R1 = np.append(new_R1, np.nan)
                else:
                    spl = UnivariateSpline(new_x, new_y)
                    new_R2 = np.append(new_R2, spl(current_level))
            elif Type == 'Linear':
                try:
                    f = interp1d(new_x, new_y)
                    new_R2 = np.append(new_R2, f(current_level))
                except:
                    new_R2 = np.append(new_R2, np.nan)

    # Plot interpolation if wanted
    if plot_interpolation:
        f = plt.figure(figsize=(17, 8))
        plt.subplot(1, 2, 1)
        plt.plot(time, new_R1)
        leg = ["Interpolated-" + str(current_level)]
        for i in range(data_R1.shape[1]):
            plt.plot(time, data_R1[:, i])
            leg.append(x[i][0])
        plt.legend(leg)
        plt.xlabel('Time [s]')
        plt.ylabel('Resistance [Ohm]')
        plt.title('R_CoilSection 1')
        if n_apertures == 2:
            plt.subplot(1, 2, 2)
            plt.plot(time, new_R2)
            leg = ["Interpolated-" + str(current_level)]
            for i in range(data_R2.shape[1]):
                plt.plot(time, data_R2[:, i])
                leg.append(x[i][0])
            plt.legend(leg)
            plt.xlabel('Time [s]')
            plt.ylabel('Resistance [Ohm]')
            plt.title('R_CoilSection 2')
        f.suptitle(str(current_level[0][0]) + 'A', fontsize=16)
        plt.show()
    if n_apertures == 2:
        return [time, new_R1, new_R2]
    else:
        return [time, new_R1]

def writeStimuliFromInterpolation(current_level: list, n_total_magnets: int, n_apertures: int, magnets: list, tShift: list, Outputfile: str, path_resources: Union[str,list],
                                  InterpolationType: str = 'Linear', type_stl: str = 'a', sparseTimeStepping: int = 100, magnet_type: list = None,
                                  time_additional_zero_resistance: float = 1e-6):
    '''
    Function to write a resistance stimuli for n apertures of a magnet for any current level. Resistance will be interpolated
    from pre-calculated values (see InterpolateResistance for closer explanation). Stimuli is then written in a .stl file for PSPICE

    :param current_level: list, all current level that shall be used for interpolation (each magnet has 1 current level)
    :param n_total_magnets: int, Number of total magnets in the circuit (A stimuli will be written for each, non-quenching = 0)
    :param n_apertures: int, Number of apertures per magnet. A stimuli will be written for each aperture for each magnet
    :param magnets: list, magnet numbers for which the stimuli shall be written
    :param tShift: list, time shift that needs to be applied to each stimuli
    (e.g. if magnet 1 quenches at 0.05s, magnet 2 at 1s etc.), so that the stimuli are applied at the correct time in the simulation
    :param Outputfile: str, name of the stimuli-file
    :param path_resources: list, list of paths to the files with pre-calculated values
    :param magnet_type: list, contains numbers from 1 to len(path_resources) for each magnet
    (e.g. if there are three items in the path_resources list and four magnets, then magnet_type can be [2,2,1,1] or [1,2,3,3] telling us which path_resource file to use for each magnet
    :param Type: str, either Linear or Spline, type of interpolation
    :param type_stl: str, how to write the stimuli file (either 'a' (append) or 'w' (write))
    :param sparseTimeStepping: int, every x-th time value only a stimuli point is written (to reduce size of stimuli)
    : param time_additional_zero_resistance: float, this defines the time shift of an additional point that is added before the first coil resistance row
    :return:
    '''

    make_folder_if_not_existing(os.path.dirname(Outputfile), verbose=False)

    # Check inputs and set default values
    if type(path_resources) == str:
        path_resources = [path_resources] * len(magnets)  # make a list out of the string

    if not magnet_type:
        magnet_type = [1] * len(magnets)  # make a list of 1's (to maintain the same behavior as the older version fo the function)

    if n_apertures>2: raise Exception('Maximum of 2 apertures supported yet.')
    # Ensure consistency of inputs
    if len(magnets) != len(tShift): raise Exception(f'Please provide a time shift for each magnet. '
                                                    f'Size of magnet list is {len(magnets)}, but size of tShift is {len(tShift)}')
    if len(magnet_type) != n_total_magnets:
        magnet_type = [1]*n_total_magnets
        print('No full list of magnet types provided. Assuming all magnets are the same [1]')
    R1 = np.array([])
    R2 = np.array([])
    print("Interpolating Coil-Resistances")
    stlString = ''
    # Interpolate data for each current level and ensure correct data format
    current_count=-1
    for k in range(1,n_total_magnets+1):
        if k in magnets:
            current_count = current_count + 1
            current_level_mag = current_level[current_count]
            if type(current_level_mag) != list:
                current_level_mag = [current_level_mag]
            for g in current_level_mag:
                if n_apertures == 2:
                    [time, data_R1, data_R2] = InterpolateResistance(g, path_resources[magnet_type[k-1]-1], n_apertures=n_apertures, Type = InterpolationType)
                else:
                    [time, data_R1] = InterpolateResistance(g, path_resources[magnet_type[k-1]-1], n_apertures=n_apertures, Type=InterpolationType)
                if not R1.size > 0:
                    R1 = data_R1[np.newaxis, ...]
                elif "IPQ" in Outputfile:
                    if R1.size != data_R1.size:
                        R1 = data_R1[np.newaxis, ...]
                    R1 = np.vstack((R1, data_R1))
                else:
                    R1 = np.vstack((R1, data_R1))
                if n_apertures == 2:
                    if not R2.size > 0:
                        R2 = data_R2[np.newaxis, ...]
                    elif "IPQ" in Outputfile:
                        if R2.size != data_R2.size:
                            R2 = data_R2[np.newaxis, ...]
                        R2 = np.vstack((R2, data_R2))
                    else:
                        R2 = np.vstack((R2, data_R2))

            index = magnets.index(k)
            timeShift = tShift[index]
            if timeShift < 0: timeShift = 0

            # Start with generating stimulus for first aperture
            stlString = stlString + f'\n.STIMULUS R_coil_{str(1)}_M{str(magnets[index])} ' \
                                    f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
            stlString = stlString + "+ ( 0s, 0.0 )\n"
            if time[0]+timeShift-time_additional_zero_resistance > 0:
                stlString = stlString + f"+ ( {time[0]+timeShift-time_additional_zero_resistance}s, 0.0 )\n"  # additional row to fix the case where the first element of the coil resistance is non-zero
            count = 0
            # Set a resistance value in the stimuli for each sparseTimeStepping * TimeValue
            for l in range(1, R1.shape[1] - 1):
                if np.isnan(R1[current_count, l]): continue
                # Ensure starting at 0 (No negative time in PSPICE allowed
                if float(time[l]) + timeShift < 0:
                    raise Exception ("PSPICE can't process negative times, please provide a greater timeshift")
                else:
                    tt = float(time[l]) + timeShift
                # If every sparseTimeStepping* time value reached, write an entry
                if count >= sparseTimeStepping:
                    stlString = stlString + "+ ( " + str(tt) + "s, " + str(R1[current_count, l]) + " )\n"
                    count = 0
                count = count + 1
            # Write last time value to be 10000 s, with last resistance (resistance is assumed to stay constant)
            R1_last = R1[current_count]
            R1_last = R1_last[~np.isnan(R1_last)]
            R1_last = R1_last[~np.isnan(R1_last)]
            stlString = stlString + "+ ( " + str(10000) + "s," + str(R1_last[-1]) + " ) \n"
            stlString = stlString + " \n"

            if n_apertures == 2:
                # Repeat procedure for second aperture
                stlString = stlString + f'\n.STIMULUS R_coil_{str(2)}_M{str(magnets[index])} ' \
                                        f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
                stlString = stlString + "+ ( 0s, 0.0 )\n"
                if time[0] + timeShift - time_additional_zero_resistance > 0:
                    stlString = stlString + f"+ ( {time[0]+timeShift-time_additional_zero_resistance}s, 0.0 )\n"  # additional row to fix the case where the first element of the coil resistance is non-zero
                count = 0
                for h in range(1, R2.shape[1] - 1):
                    if np.isnan(R2[current_count, h]): continue
                    if float(time[h]) + timeShift < 0:
                        raise Exception("PSPICE can't process negative times, please provide a greater timeshift")
                        #tt = 0
                    else:
                        tt = float(time[h]) + timeShift
                    if count >= sparseTimeStepping:
                        stlString = stlString + "+ ( " + str(tt) + "s, " + str(R2[current_count, h]) + " )\n"
                        count = 0
                    count = count + 1
                R2_last = R2[current_count]
                R2_last = R2_last[~np.isnan(R2_last)]
                stlString = stlString + "+ ( " + str(10000) + "s," + str(R2_last[-1]) + " ) \n"
                stlString = stlString + " \n"
        else:
            stlString = stlString + f'\n.STIMULUS R_coil_{str(1)}_M{str(k)} ' \
                                    f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
            stlString = stlString + "+ ( 0s, 0.0 )\n"
            stlString = stlString + "+ ( 10000s, 0.0 )\n"

            if n_apertures == 2:
                stlString = stlString + f'\n.STIMULUS R_coil_{str(2)}_M{str(k)} ' \
                                        f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
                stlString = stlString + "+ ( 0s, 0.0 )\n"
                stlString = stlString + "+ ( 10000s, 0.0 )\n"

    # Write the stimuli as a txt(stl) file
    with open(Outputfile, type_stl) as ofile:
        ofile.write(stlString)


def write_coil_resistance_interpolation_file(path_csv_file: str, current_levels: List[float], list_times: List, list_coil_resistances: List, format: str = '{:3.10e}'):
    '''
    This function writes a coil resistance interpolation file with a format compatible with the function ParserPSPICE.writeStimuliFromInterpolation_general()

    :param path_csv_file: path to the output .csv file to write
    :param current_levels: list with defined current levels
    :param list_times: list of lists, where each list defines the time vector at one current level 
    :param list_coil_resistances: list of lists, where each list defines the time vector at one current level
    :param format: string defining the format for the written variables
    :return: 
    '''

    make_folder_if_not_existing(os.path.dirname(path_csv_file), verbose=False)

    columns_to_write = []
    for c, current in enumerate(current_levels):
        time_to_write = [format.format(t) for t in list_times[c]]
        R_to_write = [format.format(t) for t in list_coil_resistances[c]]
        columns_to_write.append([current, "time_vector"] + time_to_write)  # TODO remove the call to int() once the interpolation function can deal with it
        columns_to_write.append(["", "R_CoilSections_1"] + R_to_write)
        columns_to_write.append(["", ""] + len(list_times[c]) * [None])
    rows_to_write = zip_longest(*columns_to_write, fillvalue='')

    with open(path_csv_file, 'w', newline='') as file:
        wr = csv.writer(file)
        wr.writerows(rows_to_write)

def write_time_stimulus_file(path_file: str, dict_signals: Dict, name_time_signal: str = 'time', dict_translate_signal_names: Dict = {}, time_shift: float = 0, mode: str = 'one_time_vector', name_value_signal: str = 'value'):
    '''
    Function to write a stimulus file compatible with PSPICE.
    The function writes stimuli with the same time vector for all the signals by looking at one specific signal whose name is defined by the argument name_time_signal
    :param path_file: Full path of the stimulus file to write
    :param dict_signals: Dictionary of signals to write
    :param dict_translate_signal_names: Dictionary translating the names of the signals from the original dictionary to the target file
    :param name_time_signal: This key has a different meaning in "one_time_vector" and "individual_time_vectors" mode:
            If mode="one_time_vector": Name of the signal contained in dict_signals that will be used as time vector for all signals
            If mode="individual_time_vectors": Name of the subkey to read from the dictionary for the time vector
    :param time_shift: Time shift subtracted to the time vector [s]
    :param mode: Allowed values: "one_time_vector" and "individual_time_vectors".
            If "one_time_vector": One time vector will be used for all stimuli. The time vector will be read by the dictionary key defined by the argument name_time_signal. Each signal will be read from a different dictionary key.
            If "individual_time_vectors":  Each stimulus has an individual time vector. Each time_vector and signal value will be read from a dictionary sub-keys defined by the arguments name_time_signal and name_value_signal.
    :param name_value_signal: This key has a different meaning in "one_time_vector" and "individual_time_vectors" mode:
            If mode="one_time_vector": Ignored.
            If mode="individual_time_vectors": Name of the subkey to read from the dictionary for the values vector

    :return:
    '''

    # Check input
    allowed_modes = ['one_time_vector', 'individual_time_vectors']
    if mode not in allowed_modes:
        raise Exception(f'The mode {mode} is not supported. Supported methods are: {allowed_modes}')

    if mode == 'one_time_vector':
        # Get the time-vector signal
        if not name_time_signal in dict_signals:
            raise Exception(f'The dictionary dict_signals must include a key named name_time_signal={name_time_signal}')
        one_time_vector = dict_signals[name_time_signal]

        # Translate signal names using the dict_translate_signal_names
        if len(dict_translate_signal_names) > 0:
            translated_dict_signals = {}
            for key in dict_signals:
                new_key = dict_translate_signal_names.get(key, key)  # Use the new name if it exists, otherwise keep the old name
                translated_dict_signals[new_key] = dict_signals[key]
        else:
            translated_dict_signals = dict_signals
    elif mode == 'individual_time_vectors':
        translated_dict_signals = {}
        for key, pair_time_value in dict_signals.items():
            if not name_time_signal in pair_time_value:
                raise Exception(f'The dictionary of signal {key} must include a key named name_time_signal={name_time_signal}')
            if not name_value_signal in pair_time_value:
                raise Exception(f'The dictionary of signal {key} must include a key named name_value_signal={name_value_signal}')

            # Translate signal names using the dict_translate_signal_names (if defined, otherwise just re-assign the values)
            new_key = dict_translate_signal_names.get(key, key)  # Use the new name if it exists, otherwise keep the old name
            translated_dict_signals[new_key] = {}
            translated_dict_signals[new_key]['time'] = dict_signals[key][name_time_signal]
            translated_dict_signals[new_key]['value'] = dict_signals[key][name_value_signal]

    make_folder_if_not_existing(os.path.dirname(path_file))
    with open(path_file, 'w') as f:
        for signal_name, entries in translated_dict_signals.items():  # Note: entries is the value vector when mode=='one_time_vector', and a dictionary when mode=='individual_time_vectors'
            # Special case: do not write the time vector as a stimulus
            if signal_name == 'time' or signal_name == name_time_signal:
                continue

            # Define time vector (either one for all signals, or individual ones)
            if mode == 'one_time_vector':
                time_vector = one_time_vector
                values = entries
            elif mode == 'individual_time_vectors':
                time_vector = entries['time']
                values = entries['value']

            f.write(f".STIMULUS {signal_name} PWL\n")
            f.write("+ TIME_SCALE_FACTOR = 1\n")
            f.write("+ VALUE_SCALE_FACTOR = 1\n")

            flag_first_row = False
            for p, (time_point, value) in enumerate(zip(time_vector, values)):
                if p == 0 and time_point - time_shift < 0:  # If the first time point is lower than 0, a row will be added
                    flag_first_row = True

                if time_point - time_shift >= 0:  # PSPICE won't accept times lower than 0
                    if flag_first_row:  # Write one row with the value at the first data point higher than 0  TODO: linearly interpolate instead?
                        flag_first_row = False
                        if time_point - time_shift > 0:  # Avoid writing twice the time point of exactly 0.0s
                            f.write(f"+ ( 0.0s, {value} )\n")
                    f.write(f"+ ( {time_point - time_shift}s, {value} )\n")

            # If this flag is still true, it means all time points are lower than 0. In this case, the code writes an empty stimulus
            if flag_first_row:
                f.write(f"+ (      0.0s, 0.0 )\n")
                f.write(f"+ ( 100000.0s, 0.0 )\n")
            f.write("\n")

def read_time_stimulus_file(path_file: str, name_time_signal: str = 'time', name_value_signal: str = 'value'):
    '''
    Function to read into a dictionary a stimulus file compatible with PSPICE.
    :param path_file: Full path of the stimulus file to write
    :param name_time_signal: Name of the subkey to use in the dictionary for the time vector
    :param name_vector_signal: Name of the subkey to use in the dictionary for the values vector
    :return: Dictionary with as many keys as stimuli to read. Each key has a pair subkeys named after name_time_signal and name_value_signal with a time vector and a values vector.
    '''

    dict_signals = {}
    current_key = None

    with open(path_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('.STIMULUS'):
                # Extract the key name
                parts = line.split()
                current_key = parts[1]
                dict_signals[current_key] = {name_time_signal: [], name_value_signal: []}
            elif line.startswith('+') and current_key:
                # Extract time and value from lines starting with "+"
                # The following line is difficult to interprete and so it's explained here:
                # ([\d.]+)s?: This parses the time value, optionally followed by "s".
                # (-?[\d.]+)\s*(A|V)?: This parses the signal value, optionally followed by "A" or "V".
                match = re.match(r'\+\s*\(\s*([\d.]+)s?\s*,\s*(-?[\d.]+)\s*(A|V)?\s*\)', line)
                if match:
                    time_value = float(match.group(1))
                    value = float(match.group(2))
                    dict_signals[current_key][name_time_signal].append(time_value)
                    dict_signals[current_key][name_value_signal].append(value)

    return dict_signals

def edit_bias_file(path_file: str, edit_file_type: str, new_path_file: str = None):
    '''
    Function to edit a bias point file compatible with PSPICE.
    There are two types: ".IC" (used as input to load bias points) or ".NODESET" (output bias points written by PSPICE).
    The function looks for a line containing either ".IC" or ".NODESET" and writes the desired type of file.
    :param path_file: Full path of the bias point file to edit
    :param edit_file_type: This can either be ".IC" or "NODESET"
    :param new_path_file: Full path of the edited file to write (if not provided, the original file will be edited)
    :return:
    '''

    # Check input
    allowed_values_file_type = ['.IC', '.NODESET']
    if not edit_file_type.lower() in [i.lower() for i in allowed_values_file_type]:  # This covers the case where either small letters or capital letters are used
        raise Exception(f'The variable edit_file_type is {edit_file_type}, but the only allowed values are: {allowed_values_file_type}.')

    # If new_path_file is not provided, the original file will be edited
    if not new_path_file:
        new_path_file = path_file
    make_folder_if_not_existing(os.path.dirname(new_path_file))

    # Read the file contents
    with open(path_file, 'r') as file:
        lines = file.readlines()

    # Flag to check if replacement was done
    replacement_done = False

    # Iterate through the lines to find and replace the target line
    for i, line in enumerate(lines):
        if ".ic" in line.lower() or ".nodeset" in line.lower():
            lines[i] = edit_file_type + "\n"
            replacement_done = True
            break  # Assuming only one replacement is needed, the loop is broken

    # If replacement was done, write the new contents back to the file
    if replacement_done:
        with open(new_path_file, 'w') as file:
            file.writelines(lines)


def check_bias_file_type(path_file: str):
    '''
    Function to check the type of a PSPICE bias point file.
    There are two types: ".IC" (used as input to load bias points) or ".NODESET" (output bias points written by PSPICE).
    :param path_file: Full path of the bias point file to check
    :return: string indicating the type of the file
    '''

    # Read the file contents
    with open(path_file, 'r') as file:
        lines = file.readlines()

    # Iterate through the lines to find either the ".IC" or ".NODESET" string. Both cases with small letters or capital letters are covered
    for i, line in enumerate(lines):
        if ".ic" in line.lower():
            return ".IC"
        elif ".nodeset" in line.lower():
            return ".NODESET"

    # If this line is reached, neither string is present and the file type is unknown
    return None
