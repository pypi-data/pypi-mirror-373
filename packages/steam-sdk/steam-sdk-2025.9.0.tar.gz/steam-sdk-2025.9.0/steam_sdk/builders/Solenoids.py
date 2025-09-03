import os
import numpy as np
import yaml
import pysoleno as pysol
from steam_sdk.data import DataRoxieParser as pd
from steam_sdk.parsers.ParserRoxie import sigDig
#from steam_nb_api.resources.ResourceReader import *


class Solenoid:
    def __init__(self, sol_i, sol_dict, con_dict, force_tnt=True, force_l=True):
        """
        Class defining turns positions and numbers for input to soleno
        :param sol_i: solenoid name string
        :param sol_dict: dictionary with solenoid properties
        :param force_tnt: force total number of turns. This drives A2 and B2 dimensions from number of turns per layer and number of layers. For B2 this could be changed by force_l parameter
        :param force_l: force solenoid length (in axial dimension)  This correct insulation thickness to allow for so called loose or tight wind. Setting it for True reflect most practical scenarios
        """
        self.sol_i = sol_i
        self.sol_dict = sol_dict
        winding_cell_rad_size = con_dict.strand.bare_width + 2 * con_dict.cable.th_insulation_along_width
        strand_ins_ax_size = con_dict.strand.bare_height + 2 * con_dict.cable.th_insulation_along_height
        self.conductor_name = con_dict.name
        self.n_layers = sol_dict.nl
        self.n_turns_per_layer = sol_dict.ntpl
        self.tot_n_turns = sol_dict.ntpl * sol_dict.nl
        #f_layer_m_t_r = self.sol_dict['A1'] + strand_ins_rad_size / 2  # first layer middle turn radial position
        r_p = self.sol_dict.a1 + winding_cell_rad_size / 2 # first layer middle turn radial position
        r_pos = []
        for layer in range(sol_dict.nl):
            r_pos.append(r_p)
            r_p = r_p + winding_cell_rad_size
        # l_layer_m_t_r = f_layer_m_t_r + (self.n_layers - 1) * strand_ins_rad_size  # last layer middle turn radial position
        # r_pos = np.linspace(f_layer_m_t_r, l_layer_m_t_r, self.n_layers, endpoint=True)  # layers middle turns radial positions
        r_pos = np.array(r_pos)
        if self.sol_dict.b2 < 0:
            strand_ins_ax_size = - strand_ins_ax_size
        f_layer_m_t_z = self.sol_dict.b1 + strand_ins_ax_size / 2  # first layer middle turn axial position
        l_layer_m_t_z = f_layer_m_t_z + (sol_dict.ntpl - 1) * strand_ins_ax_size  # last layer middle turn axial position
        z_pos = np.linspace(f_layer_m_t_z, l_layer_m_t_z, sol_dict.ntpl, endpoint=True)  # layers middle turns axial positions
        self.rr_pos, self.zz_pos = np.meshgrid(r_pos, z_pos)
        self.rr_pos = self.rr_pos.T
        self.zz_pos = self.zz_pos.T
        self.Rin = np.linspace(self.sol_dict.a1, self.sol_dict.a1 + (sol_dict.nl - 1) * winding_cell_rad_size, sol_dict.nl, endpoint=True)  # layers start turns radial positions
        self.Rout = self.Rin + winding_cell_rad_size  # layers end turns radial positions
        self.Zlow = np.ones_like(self.Rin) * self.sol_dict.b1  # layers start axial positions
        self.Zhigh = np.ones_like(self.Rin) * self.sol_dict.b2  # layers end axial positions
        self.Nturns = np.ones_like(self.Rin, dtype=np.int32) * sol_dict.ntpl  # layers number of turns
        self.sec = np.ones_like(self.Rin) * self.sol_dict.section  # layers end axial positions
        self.coord_ins, self.coord_bare, self.coord_strand = {}, {}, {}
        for i, (z_layer, r_layer) in enumerate(zip(self.zz_pos, self.rr_pos), 1):
            self.coord_ins[i], self.coord_bare[i], self.coord_strand[i] = [], [], []
            for z, r in zip(z_layer, r_layer):
                self.coord_strand[i].append([z, r])
                self.coord_ins[i].append({'iH': [z - strand_ins_ax_size / 2, r - winding_cell_rad_size / 2],
                                          'iL': [z + strand_ins_ax_size / 2, r - winding_cell_rad_size / 2],
                                          'oH': [z - strand_ins_ax_size / 2, r + winding_cell_rad_size / 2],
                                          'oL': [z + strand_ins_ax_size / 2, r + winding_cell_rad_size / 2]})
                self.coord_bare[i].append({'iH': [z - con_dict.strand.bare_height / 2, r - con_dict.strand.bare_width / 2],
                                           'iL': [z + con_dict.strand.bare_height / 2, r - con_dict.strand.bare_width / 2],
                                           'oH': [z - con_dict.strand.bare_height / 2, r + con_dict.strand.bare_width / 2],
                                           'oL': [z + con_dict.strand.bare_height / 2, r + con_dict.strand.bare_width / 2]})

class Solenoid_magnet:
    def __init__(self, coils, conductors, Iref):
        self.solenoid_obj_list = [Solenoid(sol_i, sol_dict, con_dict) for sol_i, (sol_dict, con_dict) in enumerate(zip(coils, conductors))]
        self.Rins = np.concatenate([sol.Rin for sol in self.solenoid_obj_list], axis=None)
        self.Routs = np.concatenate([sol.Rout for sol in self.solenoid_obj_list], axis=None)
        self.Zlows = np.concatenate([sol.Zlow for sol in self.solenoid_obj_list], axis=None)
        self.Zhighs = np.concatenate([sol.Zhigh for sol in self.solenoid_obj_list], axis=None)
        self.Is = np.concatenate([np.ones_like(sol.Rin) * Iref for sol in self.solenoid_obj_list], axis=None)
        self.Nts = np.concatenate([sol.Nturns for sol in self.solenoid_obj_list], axis=None)
        self.ntpl = np.concatenate([np.ones(sol.n_layers, dtype=np.int32)*sol.n_turns_per_layer for sol in self.solenoid_obj_list], axis=None)
        Nloop = 6  # number of loops - higher means higher accuracy
        self.NLs = np.concatenate([np.ones_like(sol.Rin, dtype=np.int32) * Nloop for sol in self.solenoid_obj_list], axis=None)
        self.group_sets = self.Rins, self.Routs, self.Zlows, self.Zhighs, self.Is, self.Nts, self.NLs
        blocks = []
        conductors = []
        numbers = []
        currents = []
        sec_turn = []
        block_nr = 1
        cond_nr = 1
        for block in self.solenoid_obj_list:
            blocks.append(np.repeat(np.arange(block_nr, block.n_layers + block_nr, dtype=np.int32), block.n_turns_per_layer))
            conductors.append(np.arange(cond_nr, block.tot_n_turns + cond_nr, dtype=np.int32))
            numbers.append(np.arange(cond_nr, block.tot_n_turns + cond_nr, dtype=np.int32))
            currents.append(np.ones(block.tot_n_turns) * Iref)
            sec_turn.append(np.ones(block.tot_n_turns) * block.sec[0])
            block_nr = block_nr + block.n_layers
            cond_nr = cond_nr + block.tot_n_turns
        self.block = np.concatenate(blocks, axis=None)
        self.conductor = np.concatenate(conductors, axis=None)
        self.number = np.concatenate(numbers, axis=None)
        self.current = np.concatenate(currents, axis=None)
        self.sec_turns = np.concatenate(sec_turn, axis=None)
        self.area = np.zeros_like(self.number)
        self.fill_fac = np.zeros_like(self.number)
        self.rr_pos = np.concatenate([sol.rr_pos for sol in self.solenoid_obj_list], axis=None)
        self.zz_pos = np.concatenate([sol.zz_pos for sol in self.solenoid_obj_list], axis=None)
        self.wire_groups = []
        for idx, n in enumerate(np.concatenate([sol.n_layers for sol in self.solenoid_obj_list], axis=None)):
            self.wire_groups = self.wire_groups + [idx+1] * n
        self.section = np.concatenate([sol.sec for sol in self.solenoid_obj_list], axis=None)

    def calc_L_M(self):
        return pysol.PySoleno().calcM(*self.group_sets)

    def calc_L_tot(self):
        return np.sum(self.calc_L_M())

    def calc_Br_Bz(self, Is_sec):
        #Br, Bz = pysol.PySoleno().calcB(self.rr_pos, self.zz_pos, *self.group_sets)
        Br, Bz = pysol.PySoleno().calcB(self.rr_pos, self.zz_pos, self.Rins, self.Routs, self.Zlows, self.Zhighs, Is_sec, self.Nts, self.NLs)
        return self.rr_pos, self.zz_pos, Br, Bz

    def save_L_M(self, Ind_matrix_file):
        with open(Ind_matrix_file, 'w') as fp:
            fp.write("Extended self mutual inductance matrix [H/m]\n")
            np.savetxt(fp, self.calc_L_M(), '%6.16e', ',')

    def save_B_map(self, out_dir, magnet_name, fieldMapNumber):
        prefix, suffix = os.path.join(out_dir, f"{magnet_name}"), "_NoIron_NoSelfField.map2d"
        for sec in list(np.unique(self.section))+ ['All']:
            if sec == 'All':
                field_map_file = f"{prefix}_{sec}{suffix}"
                Is_sec = self.Is
                currents = self.current
            else:
                field_map_file = f"{prefix}_E{int(sec)}{suffix}"
                Is_sec = np.where(self.section == sec, self.Is, np.zeros_like(self.Is))
                currents = np.where(self.sec_turns == sec, self.current, np.zeros_like(self.current))
            rr_pos, zz_pos, Br, Bz = self.calc_Br_Bz(Is_sec)
            output = np.array(
                [self.block, self.conductor, self.number, rr_pos.flatten('F') * 1000, zz_pos.flatten('F') * 1000,
                 Br.flatten('F'), Bz.flatten('F'), self.area, currents, self.fill_fac]).T           #TODO Make sure self.currents are correct at writting to file
            with open(field_map_file, 'w') as fp:
                fp.write("BL. COND. NO. R-POS/MM Z-POS/MM BR/T BZ/T AREA/MM**2 CURRENT FILL FAC.  \n\n")
                np.savetxt(fp, output, '%d %d %d %6.5f %6.5f %6.5f %6.5f %6.5f %6.5f %6.5f', ',')

    def build_geom_object(self):
        data: pd.RoxieData = pd.RoxieData()
        for s, solenoid in enumerate(self.solenoid_obj_list, 1):
            data.coil.coils[s] = pd.Pole(type='solenoid', bore_center=pd.Coord(x=0.0, y=0.0))
            coil = data.coil.coils[s]
            coil.poles[1] = pd.Layer()
            for l in range(solenoid.n_layers):
                coil.poles[1].layers[l + 1] = pd.Winding()
                layer = coil.poles[1].layers[l + 1]
                layer.windings[l + 1] = pd.WindingData(conductors_number=solenoid.n_turns_per_layer, conductor_name=solenoid.conductor_name)
                layer.windings[l + 1].blocks[l + 1] = pd.BlockData(block_corners=pd.Corner(), block_corners_ins=pd.Corner(), current_sign=1)
                block = layer.windings[l + 1].blocks[l + 1]
                for ht in range(solenoid.n_turns_per_layer):
                    block.half_turns[ht + 1 + solenoid.n_turns_per_layer * l] = pd.HalfTurn(corners=pd.HalfTurnCorner(), strand_groups={1: pd.StrandGroup()})
                    turn = block.half_turns[ht + 1 + solenoid.n_turns_per_layer * l]
                    ht_coords_bare = solenoid.coord_bare[l + 1][ht if l % 2 == 0 else - (ht + 1)]
                    ht_coords_ins = solenoid.coord_ins[l + 1][ht if l % 2 == 0 else - (ht + 1)]
                    turn.corners.bare.iH = pd.Coord(x=sigDig(ht_coords_bare['iH'][0]), y=sigDig(ht_coords_bare['iH'][1]))
                    turn.corners.bare.iL = pd.Coord(x=sigDig(ht_coords_bare['iL'][0]), y=sigDig(ht_coords_bare['iL'][1]))
                    turn.corners.bare.oH = pd.Coord(x=sigDig(ht_coords_bare['oH'][0]), y=sigDig(ht_coords_bare['oH'][1]))
                    turn.corners.bare.oL = pd.Coord(x=sigDig(ht_coords_bare['oL'][0]), y=sigDig(ht_coords_bare['oL'][1]))
                    turn.corners.insulated.iH = pd.Coord(x=sigDig(ht_coords_ins['iH'][0]), y=sigDig(ht_coords_ins['iH'][1]))
                    turn.corners.insulated.iL = pd.Coord(x=sigDig(ht_coords_ins['iL'][0]), y=sigDig(ht_coords_ins['iL'][1]))
                    turn.corners.insulated.oH = pd.Coord(x=sigDig(ht_coords_ins['oH'][0]), y=sigDig(ht_coords_ins['oH'][1]))
                    turn.corners.insulated.oL = pd.Coord(x=sigDig(ht_coords_ins['oL'][0]), y=sigDig(ht_coords_ins['oL'][1]))
                    turn.strand_groups[1].strand_positions[ht if l % 2 == 0 else - (ht + 1)] =(
                        pd.Coord(x=sigDig(solenoid.coord_strand[l + 1][ht][0]), y=sigDig(solenoid.coord_strand[l + 1][ht][1])))
                ht_first = next(iter(block.half_turns.items()))[1]
                ht_last = next(iter(reversed(block.half_turns.items())))[1]
                ht_high = ht_first if l % 2 == 0 else ht_last
                ht_low = ht_last if l % 2 == 0 else ht_first
                block.block_corners.iH, block.block_corners.oH = ht_high.corners.bare.iH, ht_high.corners.bare.oH
                block.block_corners.iL, block.block_corners.oL = ht_low.corners.bare.iL, ht_low.corners.bare.oL
                block.block_corners_ins.iH, block.block_corners_ins.oH = ht_high.corners.insulated.iH, ht_high.corners.insulated.oH
                block.block_corners_ins.iL, block.block_corners_ins.oL = ht_low.corners.insulated.iL, ht_low.corners.insulated.oL
                data.coil.physical_order.append(pd.Order(coil=s, pole=1, layer=l + 1, winding=l + 1, block=l + 1))
        return data