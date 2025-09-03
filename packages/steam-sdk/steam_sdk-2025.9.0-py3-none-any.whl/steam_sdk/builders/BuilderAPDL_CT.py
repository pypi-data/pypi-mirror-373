import datetime

from steam_sdk.data.DataModelMagnet import DataModelMagnet
# from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.DataRoxieParser import RoxieRawData


class BuilderAPDL_CT:
    """
        Class with methods to write input file for an APDL model of a cos-theta magnet (LBNL model)
    """

    def __init__(self,
                 model_data: DataModelMagnet = None,
                 roxieData: RoxieRawData = None,
                 verbose: bool = False):
        """
        :param model_data: DataModelMagnet object
        :param roxieData: RoxieRawData object
        :param verbose: if set to True, additional information is printed
        """
        self.model_data = model_data
        self.roxieData = roxieData
        self.verbose = verbose

    def write_file(self, full_path_file_name: str, verbose: bool = False):
        '''
        ** Write an APDL .inp file **

        :param full_path_file_name:
        :param verbose:
        '''
        verbose = verbose if verbose is not None else self.verbose  # if verbose is not defined, take its value from self

        # Pre-process
        n_sections = len(self.model_data.Options_APDL_CT.groups_to_sections)

        # Assign conductor to each section, taken from the first block in each section
        temp_block, conductor_to_section = 0, []
        for s, n_blocks_this_section in enumerate(self.model_data.Options_APDL_CT.groups_to_sections):
            conductor_to_section.append(self.model_data.CoilWindings.conductor_to_group[temp_block])
            temp_block = temp_block + n_blocks_this_section

        # Add header section
        time_start = datetime.datetime.now()
        rows_header = [
            add_comment('Auxiliary f    ile for the LBNL APDL Cos-Theta model'),
            add_comment(f'Generated at {time_start} at CERN using STEAM_SDK'),
            add_comment('Authors: STEAM Team'),
            '',  # Add empty line
        ]

        # Add new section
        rows_general_parameters = [
            add_comment('General Parameters'),
            '',  # Add empty line
            add_comment('! Units, references'),
            '/UNITS,SI',
            'pi = acos(-1)',
            '*afun,deg		 ! Specifies the units for angular functions in parameter expressions',
            f'tref,{self.model_data.Options_APDL_CT.Model_Parameters.T_reference} ! Declares the temperature of reference',
            '',  # Add empty line
            add_comment('Loads Values'),
            f'temp_cd = {self.model_data.GeneralParameters.T_initial}				! Cool-Down Temperature',
            '',  # Add empty line
            add_comment('Contains geometric parameters of the analysis'),
            f'Nlayers = {n_sections}',
            '',  # Add empty line
        ]

        # Add new section
        rows_currents = [
            add_comment('Current'),
            f'current = {self.model_data.Options_LEDET.field_map_files.Iref}',
            '',  # Add empty line
        ]
        for s in range(1, n_sections + 1):
            rows_currents.append(f'current{s} = current')
        rows_currents.append('')  # Add empty line

        # Add new section
        # Reminder: Conductors in ModelMagnetData is numbered starting at 1, not 0
        rows_cables = [
            add_comment('------------------------------'),
            add_comment('- Cable Parameters'),
        ]
        for s in range(1, n_sections + 1):
            rows_cables.append(f'! Section {s}')
            rows_cables.append(f'*set,w_cable{s}_bare, {self.model_data.Conductors[conductor_to_section[s - 1] - 1].cable.bare_cable_width}')
            rows_cables.append(f'*set,t_cable{s}_in_bare, {self.model_data.Conductors[conductor_to_section[s - 1] - 1].cable.bare_cable_height_low}')
            rows_cables.append(f'*set,t_cable{s}_out_bare, {self.model_data.Conductors[conductor_to_section[s - 1] - 1].cable.bare_cable_height_high}')
            rows_cables.append(f'alpha_ks{s} = atan((t_cable{s}_out_bare-t_cable{s}_in_bare)/w_cable{s}_bare)')
            rows_cables.append('')  # Add empty line

        # Add new section
        rows_insulation = [
            add_comment('Insulation'),
        ]
        for s in range(1, n_sections + 1):
            rows_insulation.append(
                f'*set,t_ins_r{s},{self.model_data.Conductors[conductor_to_section[s - 1] - 1].cable.th_insulation_along_width}')
            rows_insulation.append(
                f'*set,t_ins_t{s},{self.model_data.Conductors[conductor_to_section[s - 1] - 1].cable.th_insulation_along_width}')
            rows_insulation.append('')  # Add empty line

        # Add new section
        rows_insulated_cables = [
            add_comment('Insulated Cable'),
        ]
        for s in range(1, n_sections + 1):
            rows_insulated_cables.append(f'w_cable{s} = w_cable{s}_bare + 2*t_ins_r{s}')
            rows_insulated_cables.append(f't_cable{s}_in = t_cable{s}_in_bare + 2*t_ins_t{s}')
            rows_insulated_cables.append('')  # Add empty line

        # Add new section
        rows_interlayer = [
            add_comment('Interlayer'),
            f'*set,t_ilay,{self.model_data.Options_APDL_CT.Model_Parameters.t_ilay}',
            f'*set,t_icoil,{self.model_data.Options_APDL_CT.Model_Parameters.t_icoil}',
            '',  # Add empty line
        ]

        # Add new section
        rows_coils = [
            add_comment('Coil Parameters'),
            add_comment('Radius'),
            f'*set,r0, {self.model_data.Options_APDL_CT.Model_Parameters.r0}',
        ]
        temp_block = 1
        for s, n_blocks_this_section in enumerate(self.model_data.Options_APDL_CT.groups_to_sections):
            rows_coils.append(
                f'*set,r{s + 1}_1, {self.roxieData.coil.blocks[str(temp_block)].radius / 1e3:.6f}')  # [mm] --> [m] Note: the format is imposed since sometimes the calculation is wrong. For example, 77.76/1000 returns 0.07776000000000001 rather than 0.07776
            rows_coils.append(f'*set,r{s + 1}_2, r{s + 1}_1+w_cable{s + 1}')
            temp_block = temp_block + n_blocks_this_section
        rows_coils.append('')  # Add empty line
        rows_coils.append(f'*set,r1,r1_1')
        rows_coils.append(f'*set,r3,r{n_sections}_2')  # TODO this doesn't seem very general
        rows_coils.append(f'*set,rout,r3')  # TODO this doesn't seem very general
        rows_coils.append('')  # Add empty line

        # Add new section
        rows_block_number = [
            add_comment('Coil Data'),
        ]
        for s, n_blocks_this_section in enumerate(self.model_data.Options_APDL_CT.groups_to_sections):
            rows_block_number.append(f'*set,Nb{s + 1},{n_blocks_this_section}')
        rows_block_number.append('')  # Add empty line

        # Add new section
        rows_blocks = [
            add_comment('Block Data'),
        ]
        temp_block = 1
        for s, n_blocks_this_section in enumerate(self.model_data.Options_APDL_CT.groups_to_sections):
            for b in range(n_blocks_this_section):
                rows_blocks.append(f'*set,Nc{s + 1}_{b + 1},{self.roxieData.coil.blocks[str(temp_block + b)].nco}')
            rows_blocks.append('')  # Add empty line
            temp_block = temp_block + n_blocks_this_section

        # Add new section
        rows_angles = [
            add_comment('Block Angles'),
            add_comment('phi: Left corner position'),
            add_comment('alpha: bottom line inclination'),
        ]
        temp_block = 1
        for s, n_blocks_this_section in enumerate(self.model_data.Options_APDL_CT.groups_to_sections):
            for b in range(n_blocks_this_section):
                current_phi = self.roxieData.coil.blocks[str(temp_block + b)].phi
                phi_to_write = current_phi if abs(
                    current_phi) > self.model_data.Options_APDL_CT.Model_Parameters.threshold_phi_angle_rounded_to_zero else 0  # Option to round to zero small phi angles (to avoid meshing a thin layer at the mid-plane)
                rows_angles.append(f'*set,phi{s + 1}_{b + 1},{phi_to_write}')
            for b in range(n_blocks_this_section):
                rows_angles.append(f'*set,alpha{s + 1}_{b + 1},{self.roxieData.coil.blocks[str(temp_block + b)].alpha}')
            rows_angles.append('')  # Add empty line
            temp_block = temp_block + n_blocks_this_section

        # Add new section
        rows_filler = [
            add_comment('Filler'),
            f'*set,fillerth,{self.model_data.Options_APDL_CT.Model_Parameters.fillerth}',
            '',  # Add empty line
        ]

        # Add new section
        rows_yoke = [
            add_comment('Yoke'),
            f'*set,rin_yoke,rout+fillerth',
            f'*set,yoketh,{self.model_data.Options_APDL_CT.Model_Parameters.t_yoke}',
            f'*set,rout_yoke,rin_yoke+yoketh',
            '',  # Add empty line
        ]

        # Add new section
        rows_contacts = [
            add_comment('---- For Mechanics - Interlay Contact - Filler is Nlayers+1'),
            add_comment('Glue = 5 , Sliding = 0'),
            add_comment('First number coil number, second number mandrel number'),
        ]
        for key, value in self.model_data.Options_APDL_CT.Contacts.dict_contacts.items():
            idx1 = key.split('-')[0]
            idx2 = key.split('-')[1]
            rows_contacts.append(f'ilay_{idx1}_{idx2} = {value}')
        rows_contacts.append('')  # Add empty line

        # Add new section
        n_cw_switch = len(self.model_data.Options_APDL_CT.flags_CoilWedgeSwitch)
        if n_cw_switch != n_sections:
            raise Exception(
                f'The length of the key self.model_data.Options_APDL_CT.flags_CoilWedgeSwitch is {n_cw_switch}, but it must match the length of the key self.model_data.Options_APDL_CT.groups_to_sections, which is {n_sections}.')
        rows_coil_wedges = [
            add_comment('Coil/wedge switch'),
        ]
        for s in range(n_sections):
            rows_coil_wedges.append(f'cw_{s + 1} = {self.model_data.Options_APDL_CT.flags_CoilWedgeSwitch[s]}')
        rows_coil_wedges.append('')  # Add empty line

        # Add new section
        rows_mesh_parameters = [
            add_comment('Mesh Parameters'),
            f'mpar = {self.model_data.Options_APDL_CT.Mesh_Parameters.f_scaling_mesh}  ! This will scale all the others below',
            '',  # Add empty line
            f'mesh_azim_size = mpar*{self.model_data.Options_APDL_CT.Mesh_Parameters.mesh_size_coil_azimuthal}  ! Coil Azimuthal',
            f'mesh_radial_size = mpar*{self.model_data.Options_APDL_CT.Mesh_Parameters.mesh_size_coil_radial}  ! Coil Radial',
            '',  # Add empty line
            f'msize_aperture = mpar*{self.model_data.Options_APDL_CT.Mesh_Parameters.mesh_size_aperture}',
            f'msize_filler = mpar*{self.model_data.Options_APDL_CT.Mesh_Parameters.mesh_size_filler}',
            f'msize_yoke = mpar*{self.model_data.Options_APDL_CT.Mesh_Parameters.mesh_size_yoke}',
            '',  # Add empty line
        ]

        # Add new section
        rows_friction_parameters = [
            add_comment('Friction Parameters'),
        ]
        for key, value in self.model_data.Options_APDL_CT.Friction_Parameters.dict_mu.items():
            rows_friction_parameters.append(f'{key} = {value}')
        rows_friction_parameters.append('')  # Add empty line

        # Assemble all rows to write
        rows_to_write = \
            rows_header + \
            rows_general_parameters + \
            rows_currents + \
            rows_cables + \
            rows_insulation + \
            rows_insulated_cables + \
            rows_interlayer + \
            rows_coils + \
            rows_block_number + \
            rows_blocks + \
            rows_angles + \
            rows_filler + \
            rows_yoke + \
            rows_contacts + \
            rows_coil_wedges + \
            rows_mesh_parameters + \
            rows_friction_parameters

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


#######################  Helper functions - START  #######################
def add_comment(text: str):
    ''' Format comment row '''
    if text[0] == '!':
        return text  # If the input string starts with a "!", leave it unchanged (it is already a comment)
    formatted_text = '! ' + text
    return formatted_text

#######################  Helper functions - END  #######################
