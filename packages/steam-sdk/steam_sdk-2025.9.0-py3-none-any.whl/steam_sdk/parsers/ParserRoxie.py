# import os
import copy
import math
import os
from math import *
from pathlib import Path
from typing import Dict, Union

import numpy as np
import yaml
from matplotlib.patches import Arc

# from matplotlib import cm
# from matplotlib.colors import Normalize
# from matplotlib import pyplot as plt, lines, patches
# from matplotlib.lines import Line2D
from steam_sdk.builders import geometricFunctions as gf
from steam_sdk.data import DataRoxieParser as pd
from steam_sdk.data.DataConductor import Conductor, Rutherford
from steam_sdk.data.DataModelConductor import DataModelConductor
from steam_sdk.data.DataModelMagnet import DataModelMagnet
from steam_sdk.parsers.ParserMap2d import ParserMap2dFile
from steam_sdk.parsers.ParserYAML import yaml_to_data
from steam_sdk.utils.ParserRoxieHelpers import find_iH_oH_iL_oL
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing


def arc_angle_between_point_and_abscissa(p, c):
    """
        Returns the angle of an arc with center c and endpoints at (cx + radius, cy) and (px, py)
        :param p: list of x and y coordinates of a point
        :param c: list of x and y coordinates of the arc center
    """
    theta = np.arctan2(p[1] - c[1], p[0] - c[0])
    return theta + (2 * np.pi if theta < 0 else 0)


def arcCenter(C, iH, oH, iL, oL, diff_radius=None):
    inner_radius = (np.sqrt(np.square(iH.x - C.x) + np.square(iH.y - C.y)) +
                    np.sqrt(np.square(iL.x - C.x) + np.square(iL.y - C.y))) / 2
    if diff_radius:
        outer_radius = inner_radius + diff_radius
    else:
        outer_radius = (np.sqrt(np.square(oH.x - C.x) + np.square(oH.y - C.y)) +
                        np.sqrt(np.square(oL.x - C.x) + np.square(oL.y - C.y))) / 2
    d_inner = [0.5 * abs((iL.x - iH.x)), 0.5 * abs((iH.y - iL.y))]
    d_outer = [0.5 * abs((oL.x - oH.x)), 0.5 * abs((oH.y - oL.y))]
    aa = [np.sqrt(np.square(d_inner[0]) + np.square(d_inner[1])),
          np.sqrt(np.square(d_outer[0]) + np.square(d_outer[1]))]
    bb = [np.sqrt(np.square(inner_radius) - np.square(aa[0])), np.sqrt(np.square(outer_radius) - np.square(aa[1]))]
    if iL.y < iH.y:
        M_inner = [iH.x + d_inner[0], iL.y + d_inner[1]]
        M_outer = [oH.x + d_outer[0], oL.y + d_outer[1]]
        if iL.y >= 0.:
            sign = [-1, -1]
        else:
            sign = [1, 1]
    else:
        M_inner = [iH.x + d_inner[0], iH.y + d_inner[1]]
        M_outer = [oH.x + d_outer[0], oH.y + d_outer[1]]
        if iL.y >= 0.:
            sign = [1, -1]
        else:
            sign = [-1, 1]
    inner = [M_inner[0] + sign[0] * bb[0] * d_inner[1] / aa[0], M_inner[1] + sign[1] * bb[0] * d_inner[0] / aa[0]]
    outer = [M_outer[0] + sign[0] * bb[1] * d_outer[1] / aa[1], M_outer[1] + sign[1] * bb[1] * d_outer[0] / aa[1]]
    return inner, outer


def sigDig(n):
    return np.format_float_positional(n, precision=8)


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def evalContent(s, g):
    if isFloat(s):
        value = float(s)
    else:
        if any(item in s for item in '+-*/.(^'):
            if '^' in s:
                s = s.replace('^', '**')
            value = eval(s, g)
        else:
            value = g[s]
    return value


class RoxieList:
    def __init__(self, roxie_data):
        """ Returns conductor corner positions (insulated and bare) and conductor currents in list form """
        self.x_insulated = []
        self.y_insulated = []
        self.x_bare = []
        self.y_bare = []
        self.i_conductor = []
        self.x_strand = []
        self.y_strand = []
        self.i_strand = []
        self.strand_to_halfTurn = []
        self.strand_to_group = []
        self.idx_half_turn = 0
        for idx_group, eo in enumerate(roxie_data.coil.physical_order):
            winding = roxie_data.coil.coils[eo.coil].poles[eo.pole].layers[eo.layer].windings[eo.winding]
            block = winding.blocks[eo.block]
            for halfTurn_nr, halfTurn in block.half_turns.items():
                self.idx_half_turn = self.idx_half_turn + 1
                insulated = halfTurn.corners.insulated
                bare = halfTurn.corners.bare
                self.x_insulated.append([insulated.iH.x, insulated.oH.x, insulated.oL.x, insulated.iL.x])
                self.y_insulated.append([insulated.iH.y, insulated.oH.y, insulated.oL.y, insulated.iL.y])
                self.x_bare.append([bare.iH.x, bare.oH.x, bare.oL.x, bare.iL.x])
                self.y_bare.append([bare.iH.y, bare.oH.y, bare.oL.y, bare.iL.y])
                self.i_conductor.append(block.current_sign)

                for strand_gr_nr, strand_gr in halfTurn.strand_groups.items():
                    for strand_nr, strand in strand_gr.strand_positions.items():
                        self.x_strand.append(strand.x)
                        self.y_strand.append(strand.y)
                        self.i_strand.append(block.current_sign)
                        self.strand_to_halfTurn.append(self.idx_half_turn)
                        self.strand_to_group.append(idx_group + 1)


class ParserRoxie:
    """
        Class for the roxie parser
    """

    def __init__(self):
        self.data: pd.RoxieData = pd.RoxieData()
        self.roxieData: pd.RoxieRawData = pd.RoxieRawData()
        self.rawData: pd.RoxieRawData = pd.RoxieRawData()

        self.dir_iron: Path
        self.dir_data: Path
        self.dir_cadata: Path

        self.cond_tot: int = 0
        self.no: int
        self.shift_flag: int = 0
        self.block: pd.Block = pd.Block()
        self.group: pd.Group = pd.Group()
        self.trans: pd.Trans = pd.Trans()
        self.cond_name: str
        self.conductor: pd.Cadata = pd.Cadata()
        self.cond_parameters: pd.CondPar = pd.CondPar()


        self.symmetric_coil = True
        self.windings = []
        self.iron_yoke_options = 0
        self.model_data = None

    def loadParametersFromMap2d(self, model_data: Union[DataModelMagnet, DataModelConductor],
                                path_input_file: Path = None, path_map2d: Path = None, verbose=False):
        """
            ** Returns auxiliary parameters using map2d file from ROXIE **

            :param verbose
            :param path_map2d: Input .map2d file. Note: By default, read the .map2d file defined in the yaml input file
            :param model_data: Model_data object to access parametrs
            :param path_input_file: Path to magnet folder to access params

            :type path_map2d: Path
            :type model_data: DataModelMagnet or DataModelConductor
            :type path_input_file: Path

            :return: None
        """
        # Acquire required parameters
        if path_map2d is None:
            path_map2d: Path = Path.joinpath(path_input_file,
                                             model_data.Sources.magnetic_field_fromROXIE)  # By default, read the .map2d file defined in the yaml input file
        headerLines: int = model_data.Options_LEDET.field_map_files.headerLines

        nT, nStrands_inGroup_ROXIE, polarities_inGroup, strandToHalfTurn, strandToGroup, x_strands, y_strands, I_strands, Bx, By \
            = ParserMap2dFile(map2dFile=path_map2d).getParametersFromMap2d(headerLines=headerLines)

        indexTstop = np.cumsum(nT).tolist()
        indexTstart = [1]
        for i in range(len(nT) - 1):
            indexTstart.extend([indexTstart[i] + nT[i]])

        return nT, nStrands_inGroup_ROXIE, polarities_inGroup, strandToHalfTurn, strandToGroup, indexTstart, indexTstop, x_strands, y_strands, I_strands, Bx, By

    def getIronYokeDataFromIronFile(self, iron_content: str = None, verbose: bool = False):
        """
            **Parse the content of the entire .iron file and store it in a IronDatabase object**

            Function returns a IronDatabase object that contains information about the iron yoke

            :param iron_content: .iron file content
            :type iron_content: str
            :param verbose: flag that determines whether the outputs are printed
            :type verbose: bool

            :return: IronDatabase
        """

        functions = {'Cos': cos, 'Sin': sin, 'Tan': tan, 'Acos': acos, 'Asin': asin, 'Atan': atan, 'Sqrt': sqrt}

        data = self.data.iron

        designVariables = {}
        scalarVariables = {}
        corners = []
        notches = []
        bars = []

        if iron_content:
            fileNames = [1]
        else:
            if verbose: print('File with iron database: {}'.format(self.dir_iron))
            fileNames = [self.dir_iron]
            path_iron = self.dir_iron.parent
            with open(fileNames[0]) as file:  # include .mod files
                fileContent = file.read()
                if 'include' in fileContent:
                    for i in fileContent.splitlines():  # content by row
                        if i.strip()[:7] == 'include':
                            fileNames.append(Path.joinpath(path_iron, i.strip()[8:].strip(' )')))

        if self.iron_yoke_options == 0:
            scaling = 1
        elif self.iron_yoke_options == 1:
            scaling = 0.001
        for f in fileNames:
            if isinstance(f, Path):
                file = open(f, "r")
                fileContent = file.read()
            else:
                fileContent = iron_content

            for i in fileContent.split('\n'):  # content by row
                fc = i.strip().strip(';')
                if (fc.strip()[:2] != '--' and fc != '' and fc.strip() != 'HyperMesh' and fc.strip()[:6] != 'Mirror'
                        and fc.strip()[:7] != 'include' and fc.strip()[0] != '#'):
                    if '--' in fc:  # is there a comment?
                        fc = fc[:fc.find('--')].strip().strip(';')

                    for j in fc.strip().split(';'):  # row content
                        statement = j.strip().split('=')
                        state0 = statement[0].strip()

                        if j[:3] == 'dv ':  # design variable
                            designVariables[statement[0][3:].strip()] = \
                                evalContent(statement[1].strip(),
                                            {**designVariables, **scalarVariables, **data.key_points, **functions})

                        elif j[:2] == 'kp':  # key point
                            all_global = {**designVariables, **scalarVariables, **data.key_points, **functions}
                            statement[1] = statement[1].strip()
                            if statement[1] in data.key_points:  # the point is copied from another one
                                A = [data.key_points[statement[1]].x, data.key_points[statement[1]].y]
                            else:
                                extra0, statement1 = statement[1].split('[')
                                statement1, extra1 = statement1.split(']')
                                extra0x, extra0y, extra1x, extra1y = extra0, extra0, extra1, extra1
                                for key_point in data.key_points:
                                    if key_point in extra0:
                                        extra0x = extra0x.replace(key_point, key_point + '.x')
                                        extra0y = extra0y.replace(key_point, key_point + '.y')
                                    if key_point in extra1:
                                        extra1x = extra1x.replace(key_point, key_point + '.x')
                                        extra1y = extra1y.replace(key_point, key_point + '.y')
                                if '@' in statement1:  # then the angle is specified
                                    arg = statement1.split('@')
                                    xExpr, yExpr = arg[0].strip(), arg[1].strip()
                                    A = [evalContent(f"{extra0x} (({xExpr}) * Cos({yExpr})) {extra1x}", all_global),
                                         evalContent(f"{extra0y} (({xExpr}) * Sin({yExpr})) {extra1y}", all_global)]
                                else:  # otherwise coordinates
                                    arg = statement1.split(',')
                                    A = [evalContent(f"{extra0x} ({arg[0].strip()}) {extra1x}", all_global),
                                         evalContent(f"{extra0y} ({arg[1].strip()}) {extra1y}", all_global)]

                            data.key_points[state0] = pd.Coord(x=sigDig(scaling * A[0]), y=sigDig(scaling * A[1]))

                        elif j[:2] == 'ln':  # hyper line
                            statement[1] = statement[1].strip()
                            if statement[1][:5] == 'Hyper':
                                arguments = statement[1][10:-1].split(',')
                                arg0 = arguments[0].strip()
                                arg1 = arguments[1].strip()
                                lineType = arguments[2].strip(' "')

                                if lineType == 'Line':
                                    data.hyper_lines[state0] = pd.HyperLine(type='line', kp1=arg0, kp2=arg1)

                                elif lineType[:6] == 'Corner':
                                    if data.key_points[arg0].y < data.key_points[arg1].y:
                                        lower = [data.key_points[arg0].x, data.key_points[arg0].y]
                                        higher = [data.key_points[arg1].x, data.key_points[arg1].y]
                                    else:
                                        lower = [data.key_points[arg1].x, data.key_points[arg1].y]
                                        higher = [data.key_points[arg0].x, data.key_points[arg0].y]

                                    if lineType[6:] == 'Out':
                                        arg = arg0 + arg1 + 'Out'  # intersection point
                                        data.key_points[arg] = pd.Coord(x=lower[0], y=higher[1])
                                    else:
                                        arg = arg0 + arg1 + 'In'
                                        data.key_points[arg] = pd.Coord(x=higher[0], y=lower[1])

                                    corners.append(state0)
                                    data.hyper_lines[state0 + 'b'] = pd.HyperLine(type='line', kp1=arg0, kp2=arg)
                                    data.hyper_lines[state0 + 'a'] = pd.HyperLine(type='line', kp1=arg, kp2=arg1)

                                elif lineType[:5] == 'Notch':
                                    all_global = {**designVariables, **scalarVariables, **data.key_points, **functions}
                                    A = [data.key_points[arg0].x, data.key_points[arg0].y]
                                    B = [data.key_points[arg1].x, data.key_points[arg1].y]

                                    alpha = evalContent(arguments[3].strip(), all_global)
                                    beta = evalContent(arguments[4].strip(), all_global)
                                    arg = arg0 + arg1 + 'Notch'  # intersection point

                                    if alpha != 0:
                                        case = [(abs(alpha) < np.pi / 2) & (alpha > 0),
                                                (abs(alpha) > np.pi / 2) & (alpha > 0),
                                                (abs(alpha) < np.pi / 2) & (alpha < 0),
                                                (abs(alpha) > np.pi / 2) & (alpha < 0)]
                                        line_a = gf.findLineThroughTwoPoints(
                                            A, [((case[1] | case[2]) - (case[0] | case[3])) * A[1] /
                                                np.tan((case[1] | case[3]) * np.pi +
                                                       ((case[0] | case[3]) - (case[1] | case[2])) * alpha) + A[0], 0.])
                                    else:
                                        line_a = [0., 1., - A[1]]

                                    if beta != 0:
                                        case = [(abs(beta) < np.pi / 2) & (beta > 0),
                                                (abs(beta) > np.pi / 2) & (beta > 0),
                                                (abs(beta) < np.pi / 2) & (beta < 0),
                                                (abs(beta) > np.pi / 2) & (beta < 0)]
                                        line_b = gf.findLineThroughTwoPoints(
                                            B, [((case[1] | case[2]) - (case[0] | case[3])) * B[1] /
                                                np.tan((case[1] | case[3]) * np.pi +
                                                       ((case[0] | case[3]) - (case[1] | case[2])) * beta) + B[0], 0.])
                                    else:
                                        line_b = [0., 1., - B[1]]

                                    data.key_points[arg] = pd.Coord(x=(line_a[1] * line_b[2] - line_b[1] * line_a[2]) /
                                                                      (line_a[0] * line_b[1] - line_b[0] * line_a[1]),
                                                                    y=(line_a[2] * line_b[0] - line_b[2] * line_a[0]) /
                                                                      (line_a[0] * line_b[1] - line_b[0] * line_a[1]))

                                    notches.append(state0)
                                    data.hyper_lines[state0 + 'b'] = pd.HyperLine(type='line', kp1=arg0, kp2=arg)
                                    data.hyper_lines[state0 + 'a'] = pd.HyperLine(type='line', kp1=arg, kp2=arg1)

                                elif lineType == 'Bar':
                                    arg = [arg0 + arg1 + 'a', arg0 + arg1 + 'b']  # rectangle corner points

                                    A = [data.key_points[arg1].x, data.key_points[arg1].y]
                                    B = [data.key_points[arg0].x, data.key_points[arg0].y]
                                    if A[0] - B[0] != 0.0:
                                        alpha = math.atan((A[1] - B[1]) / (B[0] - A[0]))
                                    else:  # is the bar horizontal?
                                        alpha = math.pi / 2

                                    if len(arguments) == 3:  # is the height of the bar not specified?
                                        if alpha == math.pi / 2:
                                            h = (A[1] - B[1]) / 2
                                        else:
                                            h = (B[0] - A[0]) / 2 / math.cos(alpha)
                                    else:
                                        h = (((B[0] > A[0]) | ((B[0] == A[0]) & (B[1] < A[1]))) -
                                             ((B[0] < A[0]) | ((B[0] == A[0]) & (B[1] > A[1])))) * \
                                            evalContent(arguments[3].strip(), {**designVariables, **scalarVariables,
                                                                               **data.key_points, **functions})

                                    data.key_points[arg[1]] = pd.Coord(x=sigDig(B[0] - h * math.sin(alpha)),
                                                                       y=sigDig(B[1] - h * math.cos(alpha)))
                                    data.key_points[arg[0]] = pd.Coord(
                                        x=sigDig(data.key_points[arg[1]].x + A[0] - B[0]),
                                        y=sigDig(data.key_points[arg[1]].y + A[1] - B[1]))

                                    bars.append(state0)
                                    data.hyper_lines[state0 + ('c' * (B[0] <= A[0]) + 'a' * (B[0] > A[0]))] = \
                                        pd.HyperLine(type='line', kp1=arg0, kp2=arg[1])
                                    data.hyper_lines[state0 + 'b'] = pd.HyperLine(type='line', kp1=arg[1], kp2=arg[0])
                                    data.hyper_lines[state0 + ('a' * (B[0] <= A[0]) + 'c' * (B[0] > A[0]))] = \
                                        pd.HyperLine(type='line', kp1=arg[0], kp2=arg1)

                                elif lineType == 'Arc':
                                    arg = [arg0, arg1]
                                    if arguments[3].strip()[:2] == 'kp':
                                        arg.append(arguments[3].strip())

                                    else:  # is the radius of the arc provided?
                                        arg.append(arg[0] + arg[1][2:] + 'P3')
                                        val = arguments[3].strip()
                                        D = evalContent(
                                            val, {**designVariables, **scalarVariables, **data.key_points, **functions}) * 2 * scaling  # diameter

                                        A = [data.key_points[arg[1]].x, data.key_points[arg[1]].y]
                                        B = [data.key_points[arg[0]].x, data.key_points[arg[0]].y]
                                        M = [(B[0] + A[0]) / 2, (B[1] + A[1]) / 2]  # mid point
                                        dd = np.square(A[0] - B[0]) + np.square(A[1] - B[1])  # squared distance
                                        Dd = D * D - dd

                                        if Dd > 0.0:
                                            ss = (abs(D) - np.sqrt(Dd)) / 2  # compute sagitta
                                        else:
                                            ss = D / 2

                                        if M[1] - B[1] != 0.0:
                                            alpha = math.atan((B[0] - M[0]) / (M[1] - B[1]))
                                        else:
                                            alpha = math.pi / 2

                                        if A[0] == B[0]:
                                            # if B[0] == 0.0:
                                            #     sign = np.sign(ss)
                                            # else:
                                            sign = np.sign(B[1] - A[1])
                                        elif A[1] == B[1]:
                                            sign = np.sign(A[0] - B[0])
                                        else:
                                            if A[0] > B[0]:
                                                sign = np.sign((A[0] - B[0]) / (B[1] - A[1]))
                                            else:
                                                sign = np.sign((A[0] - B[0]) / (A[1] - B[1]))

                                        data.key_points[arg[2]] = pd.Coord(x=sigDig(M[0] + sign * ss * math.cos(alpha)),
                                                                           y=sigDig(M[1] + sign * ss * math.sin(alpha)))

                                    data.hyper_lines[state0] = \
                                        pd.HyperLine(type='arc', kp1=arg[0], kp2=arg[1], kp3=arg[2])

                                elif lineType == 'Circle':
                                    data.hyper_lines[state0] = pd.HyperLine(type='circle', kp1=arg0, kp2=arg1)

                                elif lineType == 'EllipticArc':
                                    all_global = {**designVariables, **scalarVariables, **data.key_points, **functions}
                                    xExpr = arguments[3].strip()
                                    yExpr = arguments[4].strip()

                                    arg = [scaling * evalContent(xExpr, all_global),
                                           scaling * evalContent(yExpr, all_global)]  # axes of the ellipse
                                    data.hyper_lines[state0] = \
                                        pd.HyperLine(type='ellipticArc', kp1=arg0, kp2=arg1, arg1=arg[0], arg2=arg[1])

                                else:
                                    print(arguments[2].strip() + ' needs to be implemented')

                            elif statement[1][:4] == 'Line':
                                arguments = statement[1][5:-1].split(',')
                                data.hyper_lines[state0] = pd.HyperLine(type='line', kp1=arguments[0].strip(),
                                                                        kp2=arguments[1].strip())

                            else:
                                print(statement[1][:statement[1].find('(')] + ' needs to be implemented')

                        elif j[:2] == 'ar':  # area enclosed by hyper lines
                            statement[1] = statement[1].strip()
                            arguments = statement[1][10:-1].split(',')
                            arg = []
                            pre_line = []
                            for k in range(len(arguments) - 1):
                                name = arguments[k].strip()
                                if name in corners or name in notches:  # 2 lines are introduced for corners and notches
                                    if (data.hyper_lines[name + 'a'].kp1 in pre_line or
                                            data.hyper_lines[name + 'a'].kp2 in pre_line):
                                        arg.extend([name + 'a', name + 'b'])
                                    else:
                                        arg.extend([name + 'b', name + 'a'])
                                elif name in bars:  # 3 lines are introduced for bars
                                    if (data.hyper_lines[name + 'a'].kp1 in pre_line or
                                            data.hyper_lines[name + 'a'].kp2 in pre_line):
                                        arg.extend([name + 'a', name + 'b', name + 'c'])
                                    else:
                                        arg.extend([name + 'c', name + 'b', name + 'a'])
                                else:
                                    arg.append(name)
                                pre_line = [data.hyper_lines[arg[-1]].kp1, data.hyper_lines[arg[-1]].kp2]

                            data.hyper_areas[state0] = pd.HyperArea(material=arguments[-1].strip(), lines=arg)

                        elif j[:2] == 'BH':
                            print('BH')

                        elif j[:11] == 'HyperHoleOf':
                            arguments = state0[12:-1].split(',')
                            data.hyper_holes[len(data.hyper_holes) + 1] = \
                                pd.HyperHole(areas=[arguments[0].strip(), arguments[1].strip()])

                        elif j[:5] == 'Lmesh':
                            arguments = state0[6:-1].split(',')
                            name = arguments[0].strip()
                            if name in corners or name in notches:
                                data.hyper_lines[name + 'a'].elements = round(int(arguments[1].strip()) / 2)
                                data.hyper_lines[name + 'b'].elements = round(int(arguments[1].strip()) / 2)
                            elif name in bars:
                                data.hyper_lines[name + 'a'].elements = round(int(arguments[1].strip()) / 3)
                                data.hyper_lines[name + 'b'].elements = round(int(arguments[1].strip()) / 3)
                                data.hyper_lines[name + 'c'].elements = round(int(arguments[1].strip()) / 3)
                            else:
                                data.hyper_lines[name].elements = int(arguments[1].strip())

                        else:  # scalar variables
                            scalarVariables[state0] = \
                                evalContent(statement[1].strip(),
                                            {**designVariables, **scalarVariables, **data.key_points, **functions})
            if isinstance(f, Path):
                file.close()

        return data

    def getConductorDataFromCadataFile(self, cadata_content: str = None, verbose: bool = False):
        """
            **Parse the content of the entire .cadata file and store it in a CableDatabase object**

            Function returns a CableDatabase object that contains information about all conductors

            :param cadata_content: .cadata file content
            :type cadata_content: str
            :param verbose: flag that determines whether the outputs are printed
            :type verbose: bool

            :return: CableDatabase
        """

        data = self.rawData.cadata  # self.data.cadata

        if cadata_content:
            fileContent = cadata_content
        else:
            if verbose:
                print('File with cable database: {}'.format(self.dir_cadata))
            file = open(self.dir_cadata, "r")
            fileContent = file.read()
        # separate rows
        fileContentByRow = fileContent.split("\n")

        for index in range(len(fileContentByRow)):
            fc = fileContentByRow[index]

            if fc[0:5] == "CABLE":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.cable[arg[1]] = pd.Cable(height=float(arg[2]), width_i=float(arg[3]), width_o=float(arg[4]),
                                                  ns=float(arg[5]), transp=float(arg[6]), degrd=float(arg[7]),
                                                  comment=" ".join(arg[8:]))

            elif fc[0:9] == "CONDUCTOR":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.conductor[arg[1]] = pd.ConductorRoxie(conductorType=int(arg[2]), cableGeom=arg[3], strand=arg[4],
                                                               filament=arg[5], insul=arg[6], trans=arg[7], quenchMat=arg[8],
                                                               T_0=float(arg[9]), comment=" ".join(arg[10:]))
            elif fc[0:8] == "FILAMENT":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.filament[arg[1]] = pd.Filament(fildiao=float(arg[2]), fildiai=float(arg[3]), Jc_fit=arg[4],
                                                        fit=arg[5], comment=" ".join(arg[6:]))

            elif fc[0:5] == "INSUL":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.insul[arg[1]] = pd.Insulation(radial=float(arg[2]), azimut=float(arg[3]),
                                                       comment=" ".join(arg[4:]))

            elif fc[0:6] == "REMFIT":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.remfit[arg[1]] = pd.RemFit(type=float(arg[2]), C1=float(arg[3]), C2=float(arg[4]),
                                                   C3=float(arg[5]), C4=float(arg[6]), C5=float(arg[7]),
                                                   C6=float(arg[8]), C7=float(arg[9]), C8=float(arg[10]),
                                                   C9=float(arg[11]), C10=float(arg[12]), C11=float(arg[13]),
                                                       comment=" ".join(arg[14:]))

            elif fc[0:6] == "QUENCH":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.quench[arg[1]] = pd.Quench(SCHeatCapa=float(arg[2]), CuHeatCapa=float(arg[3]),
                                                    CuThermCond=float(arg[4]), CuElecRes=float(arg[5]),
                                                    InsHeatCapa=float(arg[6]), InsThermCond=float(arg[7]),
                                                    FillHeatCapa=float(arg[8]), He=float(arg[9]),
                                                    comment=" ".join(arg[10:]))
                # Add entry "NONE"
                data.quench["NONE"] = pd.Quench(SCHeatCapa=None, CuHeatCapa=None, CuThermCond=None, CuElecRes=None,
                                                InsHeatCapa=None, InsThermCond=None, FillHeatCapa=None,
                                                He=None, comment="")

            elif fc[0:6] == "STRAND":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.strand[arg[1]] = pd.Strand(diam=float(arg[2]), cu_sc=float(arg[3]), RRR=float(arg[4]),
                                                    Tref=float(arg[5]), Bref=float(arg[6]), Jc_BrTr=float(arg[7]),
                                                    dJc_dB=float(arg[8]), comment=" ".join(arg[9:]))

            elif fc[0:9] == "TRANSIENT":
                keywordAndRowNumber = fc.split()
                rowNumber = int(keywordAndRowNumber[1])
                for fcTemp in fileContentByRow[index + 1:index + 1 + rowNumber]:
                    arg = fcTemp.split()
                    data.transient[arg[1]] = pd.Transient(Rc=float(arg[2]), Ra=float(arg[3]), filTwistp=float(arg[4]),
                                                          filR0=float(arg[5]), fil_dRdB=float(arg[6]),
                                                          strandfillFac=float(arg[7]), comment=" ".join(arg[8:]))
                # Add entry "NONE"
                data.transient["NONE"] = pd.Transient(Rc=None, Ra=None, filTwistp=None, filR0=None,
                                                      fil_dRdB=None, strandfillFac=None, comment="")

            else:
                pass

        return data

    def write_cadata_file(self, output_file_name: str):
        '''
        Write a valid cadata file with the parameters (compatible with ROXIE version 11)
        :param output_file_name: path to the output file
        :return:
        '''
        make_folder_if_not_existing(os.path.dirname(output_file_name), verbose=False)

        # Unpack input
        insulations = self.rawData.cadata.insul
        remfits     = self.rawData.cadata.remfit
        filaments   = self.rawData.cadata.filament
        strands     = self.rawData.cadata.strand
        transients  = self.rawData.cadata.transient
        quenches    = self.rawData.cadata.quench
        cables      = self.rawData.cadata.cable
        conductors  = self.rawData.cadata.conductor

        # Write file
        with open(output_file_name, "w") as file:
            file.write("VERSION 11\n\n")

            # Writing INSUL section
            file.write("INSUL " + str(len(insulations)) + "\n")
            for idx, (key, value) in enumerate(insulations.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['radial']:>8.6f} {value['azimut']:>8.6f} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'Radial':>8} {'Azimut':>8}  {'Comment'}\n\n")

            # Writing REMFIT section
            file.write("REMFIT " + str(len(remfits)) + "\n")
            for idx, (key, value) in enumerate(remfits.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:3} {key:<10} {value['type']:>4} {value['C1']:>14} {value['C2']:>14} {value['C3']:>14} {value['C4']:>14} {value['C5']:>14} {value['C6']:>14} {value['C7']:>14} {value['C8']:>14} {value['C9']:>14} {value['C10']:>14} {value['C11']:<6} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'Type':<4} {'C1':>14} {'C2':>14} {'C3':>14} {'C4':>14} {'C5':>14} {'C6':>14} {'C7':>14} {'C8':>14} {'C9':>14} {'C10':>14} {'C11':>14}  {'Comment'}\n\n")

            # Writing FILAMENT section
            file.write("FILAMENT " + str(len(filaments)) + "\n")
            for idx, (key, value) in enumerate(filaments.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['fildiao']:>14} {value['fildiai']:>14} {value['Jc_fit']:>14} {value['fit']:>14} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'fildiao':>14} {'fildiao':>14} {'Jc-Fit':>14} {'fit-|':>14}  {'Comment'}\n\n")

            # Writing STRAND section
            file.write("STRAND " + str(len(strands)) + "\n")
            for idx, (key, value) in enumerate(strands.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['diam']:>14} {value['cu_sc']:>14} {value['RRR']:>14} {value['Tref']:>14} {value['Bref']:>14} {value['Jc_BrTr']:>14} {value['dJc_dB']:>14} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'diam.':>14} {'cu/sc':>14} {'RRR':>14} {'Tref':>14} {'Bref':>14} {'Jc@BrTr':>14} {'dJc/dB':>14}  {'Comment'}\n\n")

            # Writing TRANSIENT section
            if 'NONE' in transients:
                del transients['NONE']
            file.write("TRANSIENT " + str(len(transients)) + "\n")
            for idx, (key, value) in enumerate(transients.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['Rc']:>14} {value['Ra']:>14} {value['filTwistp']:>14} {value['filR0']:>14} {value['fil_dRdB']:>14} {value['strandfillFac']:>14} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'Rc':>14} {'Ra':>14} {'fil.twistp.':>14} {'fil.R0':>14} {'fil.dR/dB':>14} {'strandfill.fac.':>14}  {'Comment'}\n\n")

            # Writing QUENCH section
            if 'NONE' in quenches:
                del quenches['NONE']
            file.write("QUENCH " + str(len(quenches)) + "\n")
            for idx, (key, value) in enumerate(quenches.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['SCHeatCapa']:>14} {value['CuHeatCapa']:>14} {value['CuThermCond']:>14} {value['CuElecRes']:>14} {value['InsHeatCapa']:>14} {value['InsThermCond']:>14} {value['FillHeatCapa']:>14} {value['He']:>14} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'SCHeatCapa':>14} {'CuHeatCapa':>14} {'CuThermCond':>14} {'CuElecRes':>14} {'InsHeatCapa':>14} {'InsThermCond':>14} {'FillHeatCapa':>14} {'He':>14}  {'Comment'}\n\n")

            # Writing CABLE section
            file.write("CABLE " + str(len(cables)) + "\n")
            for idx, (key, value) in enumerate(cables.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['height']:>14} {value['width_i']:>14} {value['width_o']:>14} {value['ns']:>14} {value['transp']:>14} {value['degrd']:>14} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'height':>14} {'width_i':>14} {'width_o':>14} {'ns':>14} {'transp.':>14} {'degrd':>14}  {'Comment'}\n\n")

            # Writing CONDUCTOR section
            file.write("CONDUCTOR " + str(len(conductors)) + "\n")
            for idx, (key, value) in enumerate(conductors.items(), start=1):
                value = self.replace_none_values(dict(value))
                line = f"{idx:>3} {key:<10} {value['conductorType']:>4} {value['cableGeom']:>14} {value['strand']:>14} {value['filament']:>14} {value['insul']:>14} {value['trans']:>14} {value['quenchMat']:>14} {value['T_0']:>14} {value['comment']}\n"
                file.write(line)
            file.write(f"{'No':>3} {'Name':<10} {'Type':<4} {'CableGeom.':>14} {'Strand':>14} {'Filament':>14} {'Insul':>14} {'Trans':>14} {'QuenchMat.':>14} {'T_o':>14}  {'Comment'}\n\n")

    @staticmethod
    def replace_none_values(dictionary: dict):
        '''
        Small helper function that transforms values of a dictionary from None to the string "None"
        :param dictionary: input dictionary
        :return: edited dictionary
        '''
        for key, value in dictionary.items():
            if value is None:
                dictionary[key] = "None"
        return dictionary

    def getCoilDataFromDataFile(self, coil_content: str = None, verbose: bool = False):
        """
            **Parse the content of the entire .data file and store it in a Database object**

            Function returns a Database object that contains information about all conductors

            :param coil_content: .data file content
            :type coil_content: str
            :param verbose: flag that determines whether the outputs are printed
            :type verbose: bool

            :return: Database
        """

        data = self.rawData.coil

        # Define keywords
        keywords = {'group': {'key': 'LAYER ', 'index': 0},
                    'trans': {'key': 'EULER ', 'index': 0},
                    'block': {'key': 'BLOCK ', 'index': 0}}

        if coil_content:
            fileContent = coil_content
        else:
            if verbose: print('File with coil database: {}'.format(self.dir_data))
            with open(self.dir_data, 'r', encoding='cp1252') as file:
                fileContent = file.read()

        # Separate rows
        fileContentByRow = fileContent.split("\n")
        ironYokeOptionKey = "IRONYOKEOPTIONS"
        iron_yoke_key_present = False
        # Find group definition
        for i, row in enumerate(fileContentByRow):
            if keywords['group']['key'] in row:
                keywords['group']['index'] = i
            elif keywords['trans']['key'] in row:
                keywords['trans']['index'] = i
            elif keywords['block']['key'] in row:
                keywords['block']['index'] = i
            elif ironYokeOptionKey in row:
                ironYokeOptionIdx = i
                iron_yoke_key_present = True
            else:
                pass

        # Check valid IRONYOKEOPTIONS. only value 0 allowed (m)
        if iron_yoke_key_present:
            self.iron_yoke_options = int(fileContentByRow[ironYokeOptionIdx+1].replace(" ", ""))
        # if ironYokeOptionsValue == 1:
        #     raise ValueError(
        #         "The value of IRONYOKEOPTIONS in the .data file is set to 1 (mm), which is not supported in ParserRoxie."
        #         " Please update the .data and .iron files to use a supported unit (e.g., meters) for the IRONYOKEOPTIONS.")
        # elif ironYokeOptionsValue != 0:
        #     raise ValueError(
        #         "The value of IRONYOKEOPTIONS in the .data file have an invalid value."
        #         " Please update the .data and .iron files to use a supported unit (e.g., meters) for the IRONYOKEOPTIONS.")

        winding_correction_blocks = []
        layers = {}
        for key in keywords:
            firstRow = fileContentByRow[keywords[key]['index']]
            nRowsParameters = int(firstRow[5:])  # all keywords are 4 characters long
            if verbose:
                print('{} definition parameters have {} row(s)'.format(key, nRowsParameters))

            # Separate part of the data with group definition information
            parameters = fileContentByRow[keywords[key]['index'] + 1:keywords[key]['index'] + 1 + nRowsParameters]

            if key == 'group':
                if nRowsParameters > 0:
                    # as many concentric coils as the number of different symmetric conditions (coils with different number of poles)
                    concentric_coils = list(set([int(row.split()[1]) for row in parameters]))
                    concentric_coils.sort()
                else:
                    concentric_coils = [1]
            elif key == 'block':
                for symm in concentric_coils:
                    layers[symm] = []
                for row in parameters:
                    rowSplitStr = row.split()
                    if data.groups:
                        for group in data.groups:
                            if int(rowSplitStr[0]) in data.groups[group].blocks:
                                block_symm = data.groups[group].symm
                                break
                    else:
                        block_symm = 1
                    # as many layers as the number of different:
                    # a) Rutherford cos-theta: radii; b) Rutherford block-coil: block angles with respect to x-axis; c) Rutherford common-coil: radii; d) Ribbon cos-theta: n2
                    layers[block_symm].append(float(rowSplitStr[3 if int(rowSplitStr[1]) == 1 or (int(rowSplitStr[1]) == 2 and int(rowSplitStr[5]) == 0) else 4]))
                for symm in concentric_coils:
                    layers[symm] = list(set(layers[symm]))
                    layers[symm].sort()
                poles = list(set([row.split()[11] for row in parameters]))
                poles.sort()
            # Assign parameters to a list of parameters objects
            for row in parameters:
                rowSplitStr = row.split()

                if key == 'group':
                    data.groups[rowSplitStr[0]] = pd.Group(symm=int(rowSplitStr[1]), typexy=int(rowSplitStr[2]),
                                                           blocks=list(map(int, rowSplitStr[3:-1])))
                    if int(rowSplitStr[2]) == 0:
                        self.symmetric_coil = False  # If rows contains 0 then no symmetry - assumption but let's start from there
                elif key == 'trans':
                    data.transs[rowSplitStr[0]] = pd.Trans(x=float(rowSplitStr[1]), y=float(rowSplitStr[2]),
                                                           alph=float(rowSplitStr[3]), bet=float(rowSplitStr[4]),
                                                           string=str(rowSplitStr[5]), act=int(rowSplitStr[6]),
                                                           bcs=list(map(int, rowSplitStr[7:-1])))
                    if data.transs[rowSplitStr[0]].string == 'SHIFT2':
                        self.shift_flag += 1
                else:  # block
                    block_nr = int(rowSplitStr[0])
                    block_type = int(rowSplitStr[1])
                    nco = int(rowSplitStr[2])
                    radius = float(rowSplitStr[3])
                    phi = float(rowSplitStr[4])
                    alpha = float(rowSplitStr[5])
                    current = float(rowSplitStr[6])
                    imag = int(rowSplitStr[10])
                    turn = rowSplitStr[11]
                    common_coil = block_type == 2 and alpha == 0
                    blocks_list = []
                    if not data.groups:
                        coil = 1
                        pole = poles.index(turn) + 1 if imag == 0 or common_coil else poles[::-1].index(turn) + 1
                        layer = layers[1].index(radius if block_type == 1 or common_coil else phi) + 1
                        if imag == 1:
                            winding_correction_blocks.append(block_nr)
                    else:
                        for group in data.groups:
                            blocks_list += data.groups[group].blocks
                            if block_nr in data.groups[group].blocks:
                                group_nr = int(group)
                                if data.groups[group].typexy == 0:
                                    pole = poles.index(turn) + 1 if imag == 0 or common_coil else poles[::-1].index(turn) + 1
                                else:
                                    pole = floor(float(turn) * data.groups[group].symm / 360 + 1)
                                if self.shift_flag <= 1 and len(concentric_coils) == 1:
                                    coil = 1
                                elif self.shift_flag > 1 and len(concentric_coils) == 1:
                                    groups_list = []
                                    trans_blocks_list = []
                                    for trans in data.transs:
                                        if data.transs[trans].act == 1:
                                            groups_list += data.transs[trans].bcs
                                            if int(group) in data.transs[trans].bcs and data.transs[trans].string == 'SHIFT2':
                                                coil = int(trans)
                                        elif data.transs[trans].act == 3:
                                            trans_blocks_list += data.transs[trans].bcs
                                            if data.transs[trans].string == 'SHIFT2':
                                                coil = int(trans)
                                        else:
                                            raise Exception('Type of transformation not supported: check "ACT" under '
                                                            '"EULER" in the .data file.')
                                elif self.shift_flag <= 1 and len(concentric_coils) > 1:
                                    coil = concentric_coils.index(data.groups[group].symm) + 1
                                elif self.shift_flag > 1 and len(concentric_coils) > 1:
                                    for trans in data.transs:
                                        if data.transs[trans].string == 'SHIFT2' and (data.transs[trans].act == 1 and int(group) in data.transs[trans].bcs or data.transs[trans].act == 3):
                                            coil = int(trans) + concentric_coils.index(data.groups[group].symm) + (len(concentric_coils) - 1 if int(trans) == 2 else 0)  # assumes always two trans
                                            break
                                layer = layers[data.groups[group].symm].index(radius if block_type == 1 or common_coil else phi) + 1
                                if data.groups[group].typexy == 0 and imag == 1:
                                    winding_correction_blocks.append(block_nr)
                                break
                    if 'coil' not in locals():
                        if block_nr not in blocks_list:
                            raise Exception('The current block does not belong to any group: check "LAYER" in the .data file.')
                        else:
                            if group_nr not in groups_list and block_nr not in trans_blocks_list:
                                raise Exception('The current block is not transformed or belongs to a group that is not'
                                                'transformed: check "BCS" under "EULER" in the .data file.')

                    data.blocks[rowSplitStr[0]] = pd.Block(type=block_type, nco=int(rowSplitStr[2]),
                                                           radius=radius, phi=phi,
                                                           alpha=float(rowSplitStr[5]), current=float(rowSplitStr[6]),
                                                           condname=rowSplitStr[7], n1=int(rowSplitStr[8]),
                                                           n2=int(rowSplitStr[9]), imag=int(rowSplitStr[10]),
                                                           turn=float(turn), coil=coil, pole=pole, layer=layer,
                                                           winding=block_nr, shift2=pd.Coord(x=0., y=0.),
                                                           roll2=pd.Roll(coor=pd.Coord(x=0., y=0.), alph=0.))

        # Create keys for coils, poles, and layers
        orders = list(set([(blk.coil, blk.pole, blk.layer) for blk_name, blk in data.blocks.items()]))
        orders.sort(key=lambda x: (x[0], x[1], x[2]))
        for order in orders:
            if order[0] not in self.data.coil.coils:
                self.data.coil.coils[order[0]] = pd.Pole()
            coil = self.data.coil.coils[order[0]]
            if order[1] not in coil.poles:
                coil.poles[order[1]] = pd.Layer()
            pole = coil.poles[order[1]]
            if order[2] not in pole.layers:
                pole.layers[order[2]] = pd.Winding()

        # Correct winding key for asymmetric coils and block-coils
        for block in winding_correction_blocks:
            block_current = data.blocks[str(block)]
            for pair in self.model_data.CoilWindings.electrical_pairs.group_together:
                if block in pair:
                    block_main_nr = pair[1 if pair.index(block) == 0 else 0]
                    block_main = data.blocks[str(block_main_nr)]
                    block_current.winding = block_main.winding
                    # Create winding keys if they are not present
                    layer = self.data.coil.coils[block_main.coil].poles[block_main.pole].layers[block_main.layer]
                    if block_main.winding not in layer.windings:
                        layer.windings[block_main.winding] =\
                            pd.WindingData(conductors_number=block_main.nco, conductor_name=block_main.condname)
                    layer.windings[block_main.winding].blocks[block_main_nr] =\
                        pd.BlockData(block_corners=pd.Corner(), current_sign=int(np.sign(block_main.current)))
                    break

        if not self.symmetric_coil:
            print("NO SYMMETRY")
        # Print each parameters object in the list
        if verbose:
            for no in data.groups:
                arg = data.groups[no]  # group
                print('Parameters of group {}: (symmetry type: {}, group type: {}, block list: {}).'
                      .format(int(no), arg.symm, arg.typexy, arg.blocks))
            for no in data.transs:
                arg = data.transs[no]  # transformation
                print('Parameters of transformation {}:'
                      '(x: {}, y: {}, alpha: {}, bet: {}, string: {}, act: {}, bcs: {}).'
                      .format(int(no), arg.x, arg.y, arg.alph, arg.bet, arg.string, arg.act, arg.bcs))
            for no in data.blocks:
                arg = data.blocks[no]  # block
                print('Parameters of block {}:'
                      '(type: {}, nco: {}, radius: {}, phi: {}, alpha: {}, current: {}, condname: {},'
                      'n1: {}, n2: {}, imag: {}, turn: {}).'
                      .format(int(no), arg.type, arg.nco, arg.radius, arg.phi, arg.alpha,
                              arg.current, arg.condname, arg.n1, arg.n2, arg.imag, arg.turn))

        return data

    def applyMultipoleSymmetry(self, blocks: Dict[str, pd.Block] = None, group: pd.Group = None, verbose: bool = False):
        """
            **Apply N-order multipole symmetry to a list of blocks**

            Function returns the input list of blocks with new block appended

            :param blocks: list of blocks
            :type blocks: Dict
            :param group: group of blocks
            :type group: Group
            :param verbose: flag that determines whether the outputs are printed
            :type verbose: bool

            :return: list
        """
        if group:
            data = blocks
            self.group = group
            self.no = 1
        else:
            data = self.roxieData.coil.blocks

        # This index will increase with each added block
        nb = len(data)

        # Blocks to add to the attribute group.blocks
        blockToAddToGroup = []

        # Apply multipole geometry
        if self.group.typexy == 0:
            if verbose:
                print('typexy = {}: No symmetry action.'.format(self.group.typexy)) ## Pull winding data from yaml files.
                # here get the winding data from the yaml file. Overwrite the already defined windings in the data.
                # Function is placed outside this file.
            if self.model_data:
                self.windings = self.model_data.CoilWindings.electrical_pairs.group_together
            else:
                filename = os.path.splitext(os.path.basename(self.dir_data))[0]
                raise ValueError(f"For {filename} you must need to input a path to the yaml file because coil is asymmetric.")
        elif self.group.typexy == 1:
            if verbose:
                print('typexy = {}: All.'.format(self.group.typexy))

            for additionalBlock in self.group.blocks:
                # idxBlock = additionalBlock - 1
                if verbose:
                    print('additionalBlock = {}'.format(additionalBlock))
                    print('pole={} of {}'.format(1, self.group.symm))

                block = data[str(additionalBlock)]  # self.blockParametersList[idxBlock]
                # Add return block to the original block
                nb += 1

                data[str(nb)] = pd.Block(type=block.type, nco=block.nco, radius=block.radius, phi=block.phi,
                                         alpha=block.alpha, current=-block.current, condname=block.condname,
                                         n1=block.n1, n2=block.n2, imag=1 - block.imag,
                                         turn=block.turn + 360 / self.group.symm, coil=block.coil, pole=block.pole,
                                         layer=block.layer, winding=additionalBlock, shift2=pd.Coord(x=0., y=0.),
                                         roll2=pd.Roll(coor=pd.Coord(x=0., y=0.), alph=0.))

                # Add return-line block index to group parameter list
                blockToAddToGroup = blockToAddToGroup + [nb]

                # This variable will switch between +1 and -1 for each pole
                signCurrent = +1

                # Add symmetric blocks
                for p in range(1, self.group.symm):
                    if verbose:
                        print('pole={} of {}'.format(p + 1, self.group.symm))

                    # Update current sign for this pole
                    signCurrent = signCurrent - 2 * np.sign(signCurrent)

                    # Update pole
                    pole = int(p + 1)

                    # Create coil, pole, layer, and winding keys if they are not present
                    coil = self.data.coil.coils[block.coil]
                    if pole not in coil.poles:
                        coil.poles[pole] = pd.Layer()
                    if block.layer not in coil.poles[pole].layers:
                        coil.poles[pole].layers[block.layer] = pd.Winding()

                    # Add go-line block
                    nb += 1
                    nOriginalBlocks = nb

                    data[str(nb)] = pd.Block(type=block.type, nco=block.nco, radius=block.radius, phi=block.phi,
                                             alpha=block.alpha, current=float(block.current * signCurrent), condname=block.condname,
                                             n1=block.n1, n2=block.n2, imag=block.imag,
                                             turn=block.turn + 360 / self.group.symm * p, coil=block.coil, pole=pole,
                                             layer=block.layer, winding=nOriginalBlocks, shift2=pd.Coord(x=0., y=0.),
                                             roll2=pd.Roll(coor=pd.Coord(x=0., y=0.), alph=0.))

                    tempBlock = data[str(nb)]

                    # Add return-line block index to group parameter list
                    blockToAddToGroup = blockToAddToGroup + [nb]

                    # Add return-line block to block parameter list
                    nb += 1

                    data[str(nb)] = pd.Block(type=tempBlock.type, nco=tempBlock.nco, radius=tempBlock.radius, phi=tempBlock.phi,
                                             alpha=tempBlock.alpha, current=-tempBlock.current, condname=tempBlock.condname,
                                             n1=tempBlock.n1, n2=tempBlock.n2, imag=1 - tempBlock.imag,
                                             turn=tempBlock.turn + 360 / self.group.symm, coil=block.coil, pole=pole,
                                             layer=tempBlock.layer, winding=nOriginalBlocks, shift2=pd.Coord(x=0., y=0.),
                                             roll2=pd.Roll(coor=pd.Coord(x=0., y=0.), alph=0.))

                    # Add return-line block index to group parameter list
                    blockToAddToGroup = blockToAddToGroup + [nb]

        elif self.group.typexy == 2:
            if verbose:
                print('typexy = {}: One coil.'.format(self.group.typexy))

            for additionalBlock in self.group.blocks:
                # nOriginalBlocks = nb
                if verbose:
                    print('additionalBlock = {}'.format(additionalBlock))

                block = data[str(additionalBlock)]
                nb += 1
                data[str(nb)] = pd.Block(type=block.type, nco=block.nco, radius=block.radius, phi=block.phi,
                                         alpha=block.alpha, current=-block.current, condname=block.condname,
                                         n1=block.n1, n2=block.n2, imag=1 - block.imag,
                                         turn=block.turn + 360 / self.group.symm, coil=block.coil,
                                         pole=block.pole, layer=block.layer,
                                         winding=additionalBlock, shift2=pd.Coord(x=0., y=0.),
                                         roll2=pd.Roll(coor=pd.Coord(x=0., y=0.), alph=0.))

                # Add return-line block index to group parameter list
                blockToAddToGroup = blockToAddToGroup + [nb]

        elif self.group.typexy == 3:
            print('typexy = {}: Connection side: NOT SUPPORTED.'.format(self.group.typexy))

        else:
            print('typexy = {}: NOT SUPPORTED.'.format(self.group.typexy))

        self.group.blocks = self.group.blocks + blockToAddToGroup

        return data

    def applyCoilTransformation(self, coil: pd.Coil = None, trans: pd.Trans = None, verbose: bool = False):
        """
            **Apply shift2 transformation (shift in x and y direction) to a list of blocks,
            apply roll2 transformation (counterclockwise rotation) to a list of blocks**
            Function returns the input list of blocks with the attributes shift2 and roll2 set to new values

            :param trans: transformation data
            :type trans: Trans
            :param coil: blocks and groups data
            :type: coil: Coil
            :param verbose: flag that determines whether the outputs are printed
            :type verbose: bool

            :return: list
        """
        if trans:
            data = coil
            self.trans = trans
        else:
            data = self.roxieData.coil

        if self.trans.act == 0:
            if verbose:
                print('Act on All blocks.')
            for block in data.blocks:
                if self.trans.string == 'SHIFT2':
                    data.blocks[block].shift2.x = self.trans.x
                    data.blocks[block].shift2.y = self.trans.y
                elif self.trans.string == 'ROLL2':
                    data.blocks[block].roll2.coor.x = self.trans.x
                    data.blocks[block].roll2.coor.y = self.trans.y
                    data.blocks[block].roll2.alph = self.trans.alph

        elif self.trans.act == 1:
            if verbose:
                print('Act on All blocks of these groups: {}.'.format(self.trans.bcs))
            for group in data.groups:
                if int(group) in self.trans.bcs:
                    for block in data.blocks:
                        if int(block) in data.groups[group].blocks:
                            if self.trans.string == 'SHIFT2':
                                data.blocks[block].shift2.x = self.trans.x
                                data.blocks[block].shift2.y = self.trans.y
                            elif self.trans.string == 'ROLL2':
                                data.blocks[block].roll2.coor.x = self.trans.x
                                data.blocks[block].roll2.coor.y = self.trans.y
                                data.blocks[block].roll2.alph = self.trans.alph

        elif self.trans.act == 2:
            if verbose:
                print('Act on Parent and offspring blocks of these groups {}: Not supported!'.format(self.trans.bcs))

        elif self.trans.act == 3:
            if verbose:
                print('Act on Specified block only: Block {}'.format(self.trans.bcs))
            for block in data.blocks:
                if int(block) in self.trans.bcs:
                    if self.trans.string == 'SHIFT2':
                        data.blocks[block].shift2.x = self.trans.x
                        data.blocks[block].shift2.y = self.trans.y
                    elif self.trans.string == 'ROLL2':
                        data.blocks[block].roll2.coor.x = self.trans.x
                        data.blocks[block].roll2.coor.y = self.trans.y
                        data.blocks[block].roll2.alph = self.trans.alph

        elif self.trans.act == 4:
            print('Act on Conductors {}. Not supported!'.format(self.trans.bcs))

        else:
            print('Act on N/a: Not supported!')

        return data

    def applySymmetryConditions(self, coil: pd.Coil = None, verbose: bool = False):
        """
            **Returns updated list of blockParametersList objects, and sets attribute blockParametersList**

            Apply symmetry conditions to blocks

            :param coil: blocks, groups, and transformation data
            :type coil: Coil
            :param verbose: flag that determines whether the output are printed
            :type verbose: bool

            :return: list
        """
        if coil:
            self.roxieData.coil = coil

        data = self.roxieData.coil

        symmetryTypes = {2: 'Dipole', 4: 'Quadrupole', 6: 'Sextupole', 8: 'Octupole', 10: 'Decapole', 12: 'Dodecapole',
                         31: 'Window frame dipole', 33: 'Window frame quadrupole', 41: 'Solenoid',
                         71: 'Periodic structure (wiggler)'}

        # Apply symmetry conditions to blocks
        for g, no in enumerate(data.groups):
            if not data.transs or self.shift_flag <= 1:
                self.no = 1
            else:
                for trans in data.transs:
                    if data.transs[trans].act == 1:
                        if int(no) in data.transs[trans].bcs and data.transs[trans].string == 'SHIFT2':
                            self.no = int(trans)
                        else:
                            self.no = 1
                    elif data.transs[trans].act == 3:
                        self.no = int(trans)

            self.group = data.groups[no]
            if self.group.symm == 0:
                if verbose:
                    print('Group {} has symmetry of type {} --> No symmetry.'.format(self.no, self.group.symm))

            elif 1 < self.group.symm < 13:
                if verbose:
                    print('Group {} has symmetry of type {} --> {} symmetry.'
                          .format(self.no, self.group.symm, symmetryTypes[self.group.symm]))
                self.applyMultipoleSymmetry(verbose=verbose)

            elif self.group.symm > 13:
                if verbose:
                    print('Group {} has symmetry of type {} --> {} symmetry. Not currently supported.'
                          .format(self.no, self.group.symm, symmetryTypes[self.group.symm]))

            else:
                if verbose:
                    print('Group {} has symmetry of type {} --> Not currently supported.'.format(self.no, self.group.symm))

        if verbose:
            print('Total number of blocks: {}'.format(len(data.blocks)))
            # Print each BlockParameters object in the list
            for bValue in data.blocks:
                print(str(bValue))

        return data

    def applyTransformations(self, coil: pd.Coil = None, verbose: bool = False):
        """
            **Returns updated list of blockParametersList objects, and sets attribute blockParametersList**

            Apply transformations to blocks

            :param coil: blocks, groups, and transformation data
            :type coil: Coil
            :param verbose: flag that determines whether the output are printed
            :type verbose: bool

            :return: list
        """
        if coil:
            self.roxieData.coil = coil

        # Apply transformations to blocks/transformations/conductors
        for no in self.roxieData.coil.transs:
            self.no = int(no)
            self.trans = self.roxieData.coil.transs[no]
            if self.trans.string == 'SHIFT2':
                if verbose:
                    print('trans {} applies a transformation of type {} --> Cartesian shift of x={} mm and y={} mm.'
                          .format(self.no, self.trans.string, self.trans.x, self.trans.y))
                self.applyCoilTransformation(verbose=verbose)

            elif self.trans.string == 'ROLL2':
                if verbose:
                    print('trans {} applies a transformation of type {} -->'
                          'Counterclockwise rotation of alpha={} deg around point x={} mm and y={} mm.'
                          .format(self.no, self.trans.string, self.trans.alph, self.trans.x, self.trans.y))
                self.applyCoilTransformation(verbose=verbose)

            elif self.trans.string == 'CONN2':
                if verbose:
                    print('trans {} applies a transformation of type {} -->'
                          'Connection of block vertices. Not currently supported. '.format(self.no, self.trans.string))

            elif self.trans.string == 'CONN2P':
                if verbose:
                    print('trans {} applies a transformation of type {} -->'
                          'Connection of block vertices to point XY. Not currently supported.'
                          .format(self.no, self.trans.string))

            else:
                if verbose:
                    print('trans {} applies a transformation of type {} --> Not currently supported.'
                          .format(self.no, self.trans.string))

        if verbose:
            print('Total number of blocks: {}'.format(len(self.roxieData.coil.blocks)))

        if verbose:
            # Print each BlockParameters object in the list
            for no in self.roxieData.coil.blocks:
                print(self.roxieData.coil.blocks[no])  # modify for printing content

        return self.roxieData.coil

    def getConductorFromCableDatabase(self, cadata: pd.Cadata = None):
        """
            ** Get the parameters of the selected conductor from an existing CableDatabase object **

            Function returns an outputConductorSigma object with the parameters of the selected conductor

            return: data
        """
        data = self.conductor

        if cadata:
            self.rawData.cadata = cadata

        # Import selected conductor data from cadata dictionary
        if self.cond_name not in data.conductor:
            data.conductor[self.cond_name] = self.rawData.cadata.conductor[self.cond_name]
            cond = data.conductor[self.cond_name]
            if cond.insul not in data.insul:
                data.insul[cond.insul] = self.rawData.cadata.insul[cond.insul]
            if cond.filament not in data.filament:
                data.filament[cond.filament] = self.rawData.cadata.filament[cond.filament]
            if cond.strand not in data.strand:
                data.strand[cond.strand] = self.rawData.cadata.strand[cond.strand]
            if cond.trans not in data.transient:
                data.transient[cond.trans] = self.rawData.cadata.transient[cond.trans]
            if cond.quenchMat not in data.quench:
                data.quench[cond.quenchMat] = self.rawData.cadata.quench[cond.quenchMat]
            if cond.cableGeom not in data.cable:
                data.cable[cond.cableGeom] = self.rawData.cadata.cable[cond.cableGeom]
        else:  # Select conductor by name
            cond = data.conductor[self.cond_name]

        # # Parameters defining Filament
        # cond.parameters.dFilament = data.filament[cond.filament].fildiao * 1e-6
        #
        # # Parameters defining Strand
        # cond.parameters.dstrand = data.strand[cond.strand].diam * 1e-3
        # cond.parameters.fracCu = data.strand[cond.strand].cu_sc / (1 + data.strand[cond.strand].cu_sc)
        # cond.parameters.fracSc = 1 / (1 + data.strand[cond.strand].cu_sc)
        # cond.parameters.RRR = data.strand[cond.strand].RRR
        # cond.parameters.TupRRR = data.strand[cond.strand].Tref

        # # Parameters defining Transient
        # if cond.trans == 'NONE':
        #     cond.parameters.Rc = 0.
        #     cond.parameters.Ra = 0.
        #     cond.parameters.fRhoEff = 0.
        #     cond.parameters.lTp = 0.
        # else:
        #     cond.parameters.Rc = data.transient[cond.trans].Rc
        #     cond.parameters.Ra = data.transient[cond.trans].Ra
        #     cond.parameters.fRhoEff = 1.
        #     cond.parameters.lTp = data.transient[cond.trans].filTwistp

        # Parameters defining Insulation
        cond.parameters.wInsulNarrow = data.insul[cond.insul].radial * 1e-3
        cond.parameters.wInsulWide = data.insul[cond.insul].azimut * 1e-3

        # Parameters defining Cable
        cond.parameters.wBare = data.cable[cond.cableGeom].height * 1e-3
        cond.parameters.hInBare = data.cable[cond.cableGeom].width_i * 1e-3
        cond.parameters.hOutBare = data.cable[cond.cableGeom].width_o * 1e-3
        #cond.parameters.noOfStrands = self.block.n1 * self.block.n2  #int(data.cable[cond.cableGeom].ns)
        # Current lines, no strands
        cond.parameters.noOfStrandsPerLayer = self.block.n2
        cond.parameters.noOfLayers = self.block.n1

        # cond_type = ''
        # Find conductor if model data present
        # if self.model_data:
        #     conductors_yaml = [cond_yaml.name for cond_yaml in self.model_data.Conductors]
        #     if self.cond_name in conductors_yaml:
        #         cond_type = self.model_data.Conductors[conductors_yaml.index(self.cond_name)].cable.type
        #
        # if cond_type == "Ribbon":
        #     cond.parameters.noOfStrandsPerLayer = int(data.cable[cond.cableGeom].ns) #cond.parameters.noOfStrand
        #     cond.parameters.noOfLayers = 1

            # if cond.parameters.noOfStrands == 1:
            #     cond.parameters.noOfStrandsPerLayer = 1
            #     cond.parameters.noOfLayers = 1
            # else:  # Rutherford cable assumed
            #     cond.parameters.noOfStrandsPerLayer = int(cond.parameters.noOfStrands / 2)
            #     cond.parameters.noOfLayers = 2

        # cond.parameters.lTpStrand = data.cable[cond.cableGeom].transp * 1e-3
        # # cond.parameters.wCore = 0.
        # # cond.parameters.hCore = 0.
        # if cond.parameters.lTpStrand != 0:
        #     cond.parameters.thetaTpStrand = math.atan2((cond.parameters.wBare - cond.parameters.dstrand),
        #                                                (cond.parameters.lTpStrand / 2))
        # else:
        #     cond.parameters.thetaTpStrand = 0.
        #
        # cond.parameters.degradation = data.cable[cond.cableGeom].degrd / 100
        # cond.parameters.C1 = 0.
        # cond.parameters.C2 = 0.
        # cond.parameters.fracHe = 0.
        # cond.parameters.fracFillInnerVoids = 1.
        # cond.parameters.fracFillOuterVoids = 1.
        # cond.parameters.Top = cond.T_0

        self.cond_parameters = cond.parameters

        return data

    def findConductorPositions(self, block: pd.Block = None, conductor: pd.CondPar = None, verbose: bool = False):
        """
            **Returns conductor positions**

            Function to find conductor corner x-y positions and conductor current if the block has type "cos-theta"

            :param conductor: conductor parameters
            :type conductor: CondPar
            :param block: block data
            :type block: Block
            :param verbose: flag that determines whether the output are printed
            :type verbose: bool

            :return: CoilData
        """
        if block:
            self.block = block
            self.cond_parameters = conductor
            self.no = 1
            self.cond_tot = 0
            self.data = pd.RoxieData()
            self.data.coil.coils[self.block.coil] = pd.Pole(type='cos-theta')
            coil = self.data.coil.coils[self.block.coil]
            coil.poles[self.block.pole] = pd.Layer()
            coil.poles[self.block.pole].layers[self.block.layer] = pd.Winding()
            layer = coil.poles[self.block.pole].layers[self.block.layer]
            layer.windings[self.block.winding] = pd.WindingData(conductors_number=self.block.nco, conductor_name=self.block.condname)
            layer.windings[self.block.winding].blocks[self.no] = pd.BlockData(block_corners=pd.Corner(), current_sign=int(np.sign(self.block.current)))

        radius = self.block.radius / 1000  # in [m]
        phi = self.block.phi / 180 * math.pi  # in [rad]
        alpha = self.block.alpha / 180 * math.pi  # in [rad]
        # current = self.block.current
        # imag = block.imag
        turn = self.block.turn / 180 * math.pi  # in [rad]
        # x0Cond = block.radius / 1000  # in [m]
        y0Cond = self.block.phi / 1000  # in [m]
        # xTemp = x0Cond
        yTemp = y0Cond

        shiftX = self.block.shift2.x / 1e3  # in [m]
        shiftY = self.block.shift2.y / 1e3  # in [m]
        x0Roll = self.block.roll2.coor.x / 1e3  # in [m]
        y0Roll = self.block.roll2.coor.y / 1e3  # in [m]
        alphaRoll = self.block.roll2.alph / 180 * math.pi  # in [rad]

        wBare = self.cond_parameters.wBare
        hInBare = self.cond_parameters.hInBare
        hOutBare = self.cond_parameters.hOutBare
        # hBare = (hInBare + hOutBare) / 2
        wInsulNarrow = self.cond_parameters.wInsulNarrow
        wInsulWide = self.cond_parameters.wInsulWide
        nColumns = self.cond_parameters.noOfStrandsPerLayer
        nLayers = self.cond_parameters.noOfLayers

        # Define the coefficients of the circle on which the x2 points (bottom-left) of each conductor rest
        # R, x0, and y0 coefficients of the circle, as in: (x-x0)**2 + (y-y0)**2 = R**2
        circle = [radius, 0, 0]

        # Define x/y positions, including conductor rotation of angle=alpha around origin (x0Cond,y0Cond)
        alphaTemp = alpha
        # phiTemp = phi
        if verbose:
            print('Initial alpha = {} deg'.format(alpha / math.pi * 180))
            print('Initial phi = {} deg'.format(phi / math.pi * 180))

        # Create coil, pole, layer, and winding keys if they are not present
        if self.block.type == 1:
            self.data.coil.coils[self.block.coil].type = 'cos-theta'
        elif self.block.type == 2 and self.block.alpha > 0:
            self.data.coil.coils[self.block.coil].type = 'block-coil'
        elif self.block.type == 2 and self.block.alpha < 0:
            self.data.coil.coils[self.block.coil].type = 'reversed-block-coil'
        elif self.block.type == 2 and self.block.alpha == 0:
            self.data.coil.coils[self.block.coil].type = 'common-block-coil'
        self.data.coil.coils[self.block.coil].bore_center = pd.Coord(x=shiftX, y=shiftY)
        coil = self.data.coil.coils[self.block.coil]
        layer = coil.poles[self.block.pole].layers[self.block.layer]
        if self.block.winding not in layer.windings:
            layer.windings[self.block.winding] = \
                pd.WindingData(conductors_number=self.block.nco, conductor_name=self.block.condname)
                # pd.WindingData(nco=self.block.nco, cable_current=float(sigDig(abs(self.block.current))),
                #                conductor_name=self.block.condname,
                #                strand_current=float(sigDig(abs(self.block.current / self.cond_parameter.noOfStrands))))
        winding = layer.windings[self.block.winding]

        # Initialize object for this block
        winding.blocks[self.no] = pd.BlockData(block_corners=pd.Corner(), current_sign=int(np.sign(self.block.current)))
        block = winding.blocks[self.no]

        for c in range(1, self.block.nco + 1):
            if self.no - 2 >= 0:
                ht_nr = c + self.half_turn_number_start_index_per_block[self.no - 2]
            else:
                ht_nr = c
            block.half_turns[ht_nr] = pd.HalfTurn(corners=pd.HalfTurnCorner())

            # Calculate coordinates of four corner of bare and insulated conductor
            if self.block.type == 1:  # cos-theta
                xR = radius * math.cos(phi)
                yR = radius * math.sin(phi)
                sinAlpha = math.sin(alphaTemp)
                cosAlpha = math.cos(alphaTemp)

                xBareCable = [xR + wInsulNarrow * cosAlpha - (hInBare + wInsulWide) * sinAlpha,
                              xR + wInsulNarrow * cosAlpha - wInsulWide * sinAlpha,
                              xR + (wBare + wInsulNarrow) * cosAlpha - wInsulWide * sinAlpha,
                              xR + (wBare + wInsulNarrow) * cosAlpha - (hOutBare + wInsulWide) * sinAlpha]
                yBareCable = [yR + wInsulNarrow * sinAlpha + (hInBare + wInsulWide) * cosAlpha,
                              yR + wInsulNarrow * sinAlpha + wInsulWide * cosAlpha,
                              yR + (wBare + wInsulNarrow) * sinAlpha + wInsulWide * cosAlpha,
                              yR + (wBare + wInsulNarrow) * sinAlpha + (hOutBare + wInsulWide) * cosAlpha]

                xCable = [xR - (hInBare + 2 * wInsulWide) * sinAlpha,
                          xR,
                          xR + (wBare + 2 * wInsulNarrow) * cosAlpha,
                          xR - (hOutBare + 2 * wInsulWide) * sinAlpha + (wBare + 2 * wInsulNarrow) * cosAlpha]
                yCable = [yR + (hInBare + 2 * wInsulWide) * cosAlpha,
                          yR,
                          yR + (wBare + 2 * wInsulNarrow) * sinAlpha,
                          yR + (wBare + 2 * wInsulNarrow) * sinAlpha + (hOutBare + 2 * wInsulWide) * cosAlpha]

                # Increase inclination angle by atan( (h2-h1)/w )
                alphaTemp = alphaTemp + math.atan2((hOutBare - hInBare), (wBare + 2 * wInsulNarrow))

                # Find line through points 1 and 4 of the current conductor (top-left and top-right)
                # A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
                line = gf.findLineThroughTwoPoints([xCable[0], yCable[0]], [xCable[3], yCable[3]], verbose=verbose)

                # Find the intersection points between the circle and the line just defined
                xy = gf.intersectLineCircle(line, circle, verbose=verbose)

                # Find the one of two intersection points that is closest to the x2 point of the current conductor
                if xy[0] == [None, None] and xy[1] == [None, None]:
                    raise ValueError('No intersection points were found! [{},{}] and [{},{}].'
                                     .format(xCable[0], yCable[0], xCable[1], yCable[1]))
                elif xy[0] == [None, None] and xy[1] != [None, None]:
                    next_x2, next_y2 = xy[0][0], xy[0][1]
                    if verbose:
                        print('One intersection point was found and selected: [{},{}].'.format(next_x2, next_y2))
                else:
                    dist1 = math.sqrt((xCable[1] - xy[0][0]) ** 2 + (yCable[1] - xy[0][1]) ** 2)
                    dist2 = math.sqrt((xCable[1] - xy[1][0]) ** 2 + (yCable[1] - xy[1][1]) ** 2)
                    if dist1 <= dist2:
                        next_x2, next_y2 = xy[0][0], xy[0][1]
                    else:
                        next_x2, next_y2 = xy[1][0], xy[1][1]
                    if verbose:
                        print('Two intersection points were found: [{},{}] and [{},{}].'.format(xy[0][0], xy[0][1],
                                                                                                xy[1][0], xy[1][1]))
                        print('The closest point was selected: [{},{}].'.format(next_x2, next_y2))

                # Find new phi angle: the angle between the X-axis and the line joining [next_x2,next_y2] and [x0,y0]
                phi = math.atan2(next_y2, next_x2)

                if verbose:
                    print('phi = {} rad'.format(phi))
                    print('phi = {} deg'.format(phi / math.pi * 180))

            elif self.block.type == 2:  # block-coil
                xBareCable = [radius + wInsulNarrow, radius + wInsulNarrow,  # x0Cond + wInsulNarrow
                              radius + (wBare + wInsulNarrow), radius + (wBare + wInsulNarrow)]
                yBareCable = [yTemp + (hInBare + wInsulWide), yTemp + wInsulWide,
                              yTemp + wInsulWide, yTemp + (hInBare + wInsulWide)]

                xCable = [radius, radius,  # x0Cond
                          radius + (wBare + 2 * wInsulNarrow), radius + (wBare + 2 * wInsulNarrow)]
                yCable = [yTemp + (hInBare + 2 * wInsulWide), yTemp,
                          yTemp, yTemp + (hInBare + 2 * wInsulWide)]

                # Update xTemp and yTemp (using insulated conductor positions)
                # xTemp = xTemp
                yTemp += hInBare + 2 * wInsulWide

            else:
                raise Exception('Block {} is of unknown type: {}. Not supported'.format(self.no, self.block.type))

            if self.block.type == 2:  # block-coil
                # Apply conductor rotation of angle=alpha around origin (x0Cond,y0Cond)
                for i, arg in enumerate(xBareCable):
                    xBareCable[i], yBareCable[i] = gf.rotatePoint((xBareCable[i], yBareCable[i]), (radius, y0Cond), alpha)
                    xCable[i], yCable[i] = gf.rotatePoint((xCable[i], yCable[i]), (radius, y0Cond), alpha)

            # Mirror conductor about the X-axis
            if self.block.imag == 1:
                yBareCable = [-i for i in yBareCable]
                yCable = [-i for i in yCable]
            elif self.block.imag == 0:
                pass
            else:
                raise Exception('Value of variable imag must be either 0 or 1. It is {} instead.'.format(self.block.imag))

            for i, arg in enumerate(xBareCable):
                # Apply conductor rotation of angle=turn around the origin
                xBareCable[i], yBareCable[i] = gf.rotatePoint((xBareCable[i], yBareCable[i]), (0, 0), turn)
                xCable[i], yCable[i] = gf.rotatePoint((xCable[i], yCable[i]), (0, 0), turn)

                # Apply roll2 counterclockwise rotation transformation
                xBareCable[i], yBareCable[i] = gf.rotatePoint((xBareCable[i], yBareCable[i]), (x0Roll, y0Roll), alphaRoll)
                xCable[i], yCable[i] = gf.rotatePoint((xCable[i], yCable[i]), (x0Roll, y0Roll), alphaRoll)

                # Apply shift2 cartesian shift transformation
                xBareCable[i], yBareCable[i] = xBareCable[i] + shiftX, yBareCable[i] + shiftY
                xCable[i], yCable[i] = xCable[i] + shiftX, yCable[i] + shiftY

            # Store cable positions
            if self.block.type == 2 and self.block.alpha < 0:  # reversed-block-coil
                block.half_turns[ht_nr].corners.insulated = pd.Corner(
                    oL=pd.Coord(x=sigDig(xCable[0 if self.block.imag == 0 else 1]), y=sigDig(yCable[0 if self.block.imag == 0 else 1])),
                    oH=pd.Coord(x=sigDig(xCable[1 if self.block.imag == 0 else 0]), y=sigDig(yCable[1 if self.block.imag == 0 else 0])),
                    iH=pd.Coord(x=sigDig(xCable[2 if self.block.imag == 0 else 3]), y=sigDig(yCable[2 if self.block.imag == 0 else 3])),
                    iL=pd.Coord(x=sigDig(xCable[3 if self.block.imag == 0 else 2]), y=sigDig(yCable[3 if self.block.imag == 0 else 2])))
                block.half_turns[ht_nr].corners.bare = pd.Corner(
                    oL=pd.Coord(x=sigDig(xBareCable[0 if self.block.imag == 0 else 1]), y=sigDig(yBareCable[0 if self.block.imag == 0 else 1])),
                    oH=pd.Coord(x=sigDig(xBareCable[1 if self.block.imag == 0 else 0]), y=sigDig(yBareCable[1 if self.block.imag == 0 else 0])),
                    iH=pd.Coord(x=sigDig(xBareCable[2 if self.block.imag == 0 else 3]), y=sigDig(yBareCable[2 if self.block.imag == 0 else 3])),
                    iL=pd.Coord(x=sigDig(xBareCable[3 if self.block.imag == 0 else 2]), y=sigDig(yBareCable[3 if self.block.imag == 0 else 2])))
            else:  # block-coil
                block.half_turns[ht_nr].corners.insulated = pd.Corner(
                    iH=pd.Coord(x=sigDig(xCable[0 if self.block.imag == 0 else 1]), y=sigDig(yCable[0 if self.block.imag == 0 else 1])),
                    iL=pd.Coord(x=sigDig(xCable[1 if self.block.imag == 0 else 0]), y=sigDig(yCable[1 if self.block.imag == 0 else 0])),
                    oL=pd.Coord(x=sigDig(xCable[2 if self.block.imag == 0 else 3]), y=sigDig(yCable[2 if self.block.imag == 0 else 3])),
                    oH=pd.Coord(x=sigDig(xCable[3 if self.block.imag == 0 else 2]), y=sigDig(yCable[3 if self.block.imag == 0 else 2])))
                block.half_turns[ht_nr].corners.bare = pd.Corner(
                    iH=pd.Coord(x=sigDig(xBareCable[0 if self.block.imag == 0 else 1]), y=sigDig(yBareCable[0 if self.block.imag == 0 else 1])),
                    iL=pd.Coord(x=sigDig(xBareCable[1 if self.block.imag == 0 else 0]), y=sigDig(yBareCable[1 if self.block.imag == 0 else 0])),
                    oL=pd.Coord(x=sigDig(xBareCable[2 if self.block.imag == 0 else 3]), y=sigDig(yBareCable[2 if self.block.imag == 0 else 3])),
                    oH=pd.Coord(x=sigDig(xBareCable[3 if self.block.imag == 0 else 2]), y=sigDig(yBareCable[3 if self.block.imag == 0 else 2])))

            if c == self.block.nco and c == 1:
                corner0 = [xCable[0], yCable[0]]  # 1
                corner3 = [xCable[3], yCable[3]]  # 4
                corner1 = [xCable[1], yCable[1]]  # 2
                corner2 = [xCable[2], yCable[2]]  # 3
            elif c == self.block.nco and c == 2:
                corner0 = [xCable[0], yCable[0]]  # 1
                corner3 = [xCable[3], yCable[3]]  # 4
                corner_aux_i_next = [xCable[1], yCable[1]]
                corner_aux_o_next = [xCable[2], yCable[2]]
            elif c == self.block.nco:
                corner0 = [xCable[0], yCable[0]]  # 1
                corner3 = [xCable[3], yCable[3]]  # 4
            elif c == 2:
                corner_aux_i_next = [xCable[1], yCable[1]]
                corner_aux_o_next = [xCable[2], yCable[2]]
            elif c == 1:
                corner1 = [xCable[1], yCable[1]]  # 2
                corner2 = [xCable[2], yCable[2]]  # 3
                corner_aux_i = [xCable[0], yCable[0]]
                corner_aux_o = [xCable[3], yCable[3]]
            else:
                pass

                # pd.BlockData(corner={'1': pd.Coord(x=x[-1][0], y=y[-1][0]),
                #                      '2': pd.Coord(x=x[0][1], y=y[0][1]),
                #                      '3': pd.Coord(x=x[0][2], y=y[0][2]),
                #                      '4': pd.Coord(x=x[-1][3], y=y[-1][3])})

            # Find strand positions
            alphaS = math.atan2(yBareCable[2] - yBareCable[1], xBareCable[2] - xBareCable[1])
            sinAlphaS = math.sin(alphaS)
            cosAlphaS = math.cos(alphaS)
            # iL_x, iL_y = block.block_corners.iL.x, block.block_corners.iL.y
            # iH_x, iH_y = block.block_corners.iL.x, block.block_corners.iH.y
            # oL_x, iL_y = block.block_corners.oL.x, block.block_corners.oL.y
            # oH_x, oH_y = block.block_corners.oL.x, block.block_corners.oH.y


            for j in range(nLayers):
                block.half_turns[ht_nr].strand_groups[j + 1] = pd.StrandGroup()
                for k in range(nColumns):
                    arg = [wBare / nColumns * (k + 1 / 2),
                           (hInBare + (hOutBare - hInBare) * (k + 1 / 2) / nColumns) * (j + 1 / 2) / nLayers]
                    if self.block.imag == 0:
                        xStrand = xBareCable[1] + arg[0] * cosAlphaS - arg[1] * sinAlphaS
                        yStrand = yBareCable[1] + arg[0] * sinAlphaS + arg[1] * cosAlphaS
                    elif self.block.imag == 1:
                        xStrand = xBareCable[1] + arg[0] * cosAlphaS + arg[1] * sinAlphaS
                        yStrand = yBareCable[1] + arg[0] * sinAlphaS - arg[1] * cosAlphaS
                    else:
                        raise Exception('Value of variable imag must be either 0 or 1. It is {} instead.'
                                        .format(self.block.imag))

                    # Store strand position
                    block.half_turns[ht_nr].strand_groups[j + 1].strand_positions[k + 1] =\
                        pd.Coord(x=sigDig(xStrand), y=sigDig(yStrand))
                    # xS.append(xStrand)
                    # yS.append(yStrand)
                    # # iS.append(currentStrand)
        self.cond_tot += self.block.nco

        # Compute two new corners to make concentric blocks by intersecting a circle (having a radius equal to the
        # distance between the bore center and the starting inner/outer block corner) with the straight line
        # passing through the ending block corners that need to be replaced
        # self.ax.add_patch(patches.Circle((coil.bore_center.x, coil.bore_center.y), radius=radius, color='b'))
        # self.ax.add_line(lines.Line2D([corner0[0], corner3[0]], [corner0[1], corner3[1]], color='red'))
        # self.ax.add_line(lines.Line2D([corner3[0], corner2[0]], [corner3[1], corner2[1]], color='red'))
        # self.ax.add_line(lines.Line2D([corner2[0], corner1[0]], [corner2[1], corner1[1]], color='red'))
        # self.ax.add_line(lines.Line2D([corner1[0], corner0[0]], [corner1[1], corner0[1]], color='red'))
        # plt.show()
        if self.block.type == 2:
            half_turns_list = list(block.half_turns.keys())
            first_half_turn = half_turns_list[0]
            last_half_turn = half_turns_list[-1]
            if (corner0[0] > 0 and corner0[1]> 0) or (corner0[0] < 0 and corner0[1] < 0):
                # quadrant 1 or 3
                point_iH = [block.half_turns[first_half_turn].corners.bare.iH.x,
                            block.half_turns[first_half_turn].corners.bare.iH.y]
                point_oH = [block.half_turns[first_half_turn].corners.bare.oH.x,
                            block.half_turns[first_half_turn].corners.bare.oH.y]
                point_iL = [block.half_turns[last_half_turn].corners.bare.iL.x,
                            block.half_turns[last_half_turn].corners.bare.iL.y]
                point_oL = [block.half_turns[last_half_turn].corners.bare.oL.x,
                            block.half_turns[last_half_turn].corners.bare.oL.y]
                point_iH_ins = [block.half_turns[first_half_turn].corners.insulated.iH.x,
                                block.half_turns[first_half_turn].corners.insulated.iH.y]
                point_oH_ins = [block.half_turns[first_half_turn].corners.insulated.oH.x,
                                block.half_turns[first_half_turn].corners.insulated.oH.y]
                point_iL_ins = [block.half_turns[last_half_turn].corners.insulated.iL.x,
                                block.half_turns[last_half_turn].corners.insulated.iL.y]
                point_oL_ins = [block.half_turns[last_half_turn].corners.insulated.oL.x,
                                block.half_turns[last_half_turn].corners.insulated.oL.y]
            else:
                # quadrant 2 (corner0[0] < 0 and corner0[1] > 0) or 4 (corner0[0] > 0 and corner0[1] < 0)
                point_iH = [block.half_turns[first_half_turn].corners.bare.iL.x,
                            block.half_turns[last_half_turn].corners.bare.iL.y]
                point_oH = [block.half_turns[first_half_turn].corners.bare.oL.x,
                            block.half_turns[last_half_turn].corners.bare.oL.y]
                point_iL = [block.half_turns[last_half_turn].corners.bare.iH.x,
                            block.half_turns[first_half_turn].corners.bare.iH.y]
                point_oL = [block.half_turns[last_half_turn].corners.bare.oH.x,
                            block.half_turns[first_half_turn].corners.bare.oH.y]
                point_iH_ins = [block.half_turns[first_half_turn].corners.insulated.iL.x,
                                block.half_turns[last_half_turn].corners.insulated.iL.y]
                point_oH_ins = [block.half_turns[first_half_turn].corners.insulated.oL.x,
                                block.half_turns[last_half_turn].corners.insulated.oL.y]
                point_iL_ins = [block.half_turns[last_half_turn].corners.insulated.iH.x,
                                block.half_turns[first_half_turn].corners.insulated.iH.y]
                point_oL_ins = [block.half_turns[last_half_turn].corners.insulated.oH.x,
                                block.half_turns[first_half_turn].corners.insulated.oH.y]
        elif self.block.nco == 1:
            # block.block_corners.iH = pd.Coord(x=sigDig(corner0[0]), y=sigDig(corner0[1]))  # 1
            # block.block_corners.oH = pd.Coord(x=sigDig(corner3[0]), y=sigDig(corner3[1]))  # 4
            # block.block_corners.iL = pd.Coord(x=sigDig(corner1[0]), y=sigDig(corner1[1]))  # 2
            # block.block_corners.oL = pd.Coord(x=sigDig(corner2[0]), y=sigDig(corner2[1]))  # 3
            # block.block_corners_ins.iH = pd.Coord(x=sigDig(corner0[0]), y=sigDig(corner0[1]))  # 1
            # block.block_corners_ins.oH = pd.Coord(x=sigDig(corner3[0]), y=sigDig(corner3[1]))  # 4
            # block.block_corners_ins.iL = pd.Coord(x=sigDig(corner1[0]), y=sigDig(corner1[1]))  # 2
            # block.block_corners_ins.oL = pd.Coord(x=sigDig(corner2[0]), y=sigDig(corner2[1]))  # 3
            bore_center = (0.0, 0.0)
            p1 = (corner0[0], corner0[1])
            p2 = (corner1[0], corner1[1])
            p3 = (corner2[0], corner2[1])
            p4 = (corner3[0], corner3[1])
            point_oH, point_oL, point_iH, point_iL = find_iH_oH_iL_oL(p1, p2, p3, p4, bore_center)
            point_oH_ins, point_oL_ins, point_iH_ins, point_iL_ins = find_iH_oH_iL_oL(p1, p2, p3, p4, bore_center)
        else:
            new_corners_inner = gf.intersectLineCircle(gf.findLineThroughTwoPoints(corner0, corner3),
                                                       [radius, coil.bore_center.x, coil.bore_center.y])
            if min(abs(new_corners_inner[0][0] - corner0[0]),
                   abs(new_corners_inner[1][0] - corner0[0])) == abs(new_corners_inner[0][0] - corner0[0]):
                new_inner = new_corners_inner[0]
            else:
                new_inner = new_corners_inner[1]
            mid_inner_end = [(corner0[0] + new_inner[0]) / 2, (corner0[1] + new_inner[1]) / 2]
            inner_line_mid_point = [(corner1[0] + corner_aux_i[0]) / 2, (corner1[1] + corner_aux_i[1]) / 2]
            mid_point_next = [(corner_aux_i_next[0] + corner_aux_i[0]) / 2, (corner_aux_i_next[1] + corner_aux_i[1]) / 2]
            mid_inner_beg = gf.intersectTwoLines(gf.findLineThroughTwoPoints(mid_point_next, inner_line_mid_point),
                                                 gf.findLineThroughTwoPoints(corner1, corner2))

            # new_inner_radius = np.sqrt(np.square(mid_inner_end[0] - coil.bore_center.x) +
            #                            np.square(mid_inner_end[1] - coil.bore_center.y))
            # new_corners_inner_mid = gf.intersectLineCircle(
            #     gf.findLineThroughTwoPoints(corner1, corner2),
            #     [new_inner_radius, coil.bore_center.x, coil.bore_center.y])
            # if min(abs(new_corners_inner_mid[0][0] - corner1[0]),
            #        abs(new_corners_inner_mid[1][0] - corner1[0])) == abs(new_corners_inner_mid[0][0] - corner1[0]):
            #     mid_inner_beg = new_corners_inner_mid[0]
            # else:
            #     mid_inner_beg = new_corners_inner_mid[1]

            outer_radius = np.sqrt(np.square(corner2[0] - coil.bore_center.x) + np.square(corner2[1] - coil.bore_center.y))
            new_corners_outer = gf.intersectLineCircle(gf.findLineThroughTwoPoints(corner0, corner3),
                [outer_radius, coil.bore_center.x, coil.bore_center.y])
            if min(abs(new_corners_outer[0][0] - corner3[0]),
                   abs(new_corners_outer[1][0] - corner3[0])) == abs(new_corners_outer[0][0] - corner3[0]):
                new_outer = new_corners_outer[0]
            else:
                new_outer = new_corners_outer[1]
            mid_outer_end = [(corner3[0] + new_outer[0]) / 2, (corner3[1] + new_outer[1]) / 2]
            outer_line_mid_point = [(corner2[0] + corner_aux_o[0]) / 2, (corner2[1] + corner_aux_o[1]) / 2]
            mid_point_next = [(corner_aux_o_next[0] + corner_aux_o[0]) / 2,
                              (corner_aux_o_next[1] + corner_aux_o[1]) / 2]
            mid_outer_beg = gf.intersectTwoLines(gf.findLineThroughTwoPoints(mid_point_next, outer_line_mid_point),
                                                 gf.findLineThroughTwoPoints(corner1, corner2))
            # new_outer_radius = np.sqrt(np.square(mid_outer_end[0] - coil.bore_center.x) +
            #                            np.square(mid_outer_end[1] - coil.bore_center.y))
            # new_corners_outer_mid = gf.intersectLineCircle(
            #     gf.findLineThroughTwoPoints(corner1, corner2),
            #     [new_outer_radius, coil.bore_center.x, coil.bore_center.y])
            # if min(abs(new_corners_outer_mid[0][0] - corner2[0]),
            #        abs(new_corners_outer_mid[1][0] - corner2[0])) == abs(new_corners_outer_mid[0][0] - corner2[0]):
            #     mid_outer_beg = new_corners_outer_mid[0]
            # else:
            #     mid_outer_beg = new_corners_outer_mid[1]
            bore_center = (coil.bore_center.x, coil.bore_center.y)
            p1 = (mid_inner_end[0], mid_inner_end[1])
            p2 = (mid_outer_end[0], mid_outer_end[1])
            p3 = (mid_inner_beg[0], mid_inner_beg[1])
            p4 = (mid_outer_beg[0], mid_outer_beg[1])
            point_oH, point_oL, point_iH, point_iL = find_iH_oH_iL_oL(p1, p2, p3, p4, bore_center)
            p1 = (corner0[0], corner0[1])
            p2 = (corner1[0], corner1[1])
            p3 = (corner2[0], corner2[1])
            p4 = (corner3[0], corner3[1])
            point_oH_ins, point_oL_ins, point_iH_ins, point_iL_ins = find_iH_oH_iL_oL(p1, p2, p3, p4, bore_center)

        if point_oH is None or point_oL is None or point_iH is None or point_iL is None:
            print("Error!!!")

        block.block_corners_ins.iH = pd.Coord(x=sigDig(point_iH_ins[0]), y=sigDig(point_iH_ins[1]))  # 1
        block.block_corners_ins.oH = pd.Coord(x=sigDig(point_oH_ins[0]), y=sigDig(point_oH_ins[1]))  # 4
        block.block_corners_ins.iL = pd.Coord(x=sigDig(point_iL_ins[0]), y=sigDig(point_iL_ins[1]))  # 2
        block.block_corners_ins.oL = pd.Coord(x=sigDig(point_oL_ins[0]), y=sigDig(point_oL_ins[1]))  # 3

        block.block_corners.iH = pd.Coord(x=sigDig(point_iH[0]), y=sigDig(point_iH[1]))  # 1
        block.block_corners.oH = pd.Coord(x=sigDig(point_oH[0]), y=sigDig(point_oH[1]))  # 4
        block.block_corners.iL = pd.Coord(x=sigDig(point_iL[0]), y=sigDig(point_iL[1]))  # 2
        block.block_corners.oL = pd.Coord(x=sigDig(point_oL[0]), y=sigDig(point_oL[1]))  # 3
        # OLD CODE
            # if self.block.imag == 0:
            #     block.block_corners.iH = pd.Coord(x=sigDig(mid_inner_end[0]), y=sigDig(mid_inner_end[1]))  # 1
            #     block.block_corners.oH = pd.Coord(x=sigDig(mid_outer_end[0]), y=sigDig(mid_outer_end[1]))  # 4
            #     block.block_corners.iL = pd.Coord(x=sigDig(mid_inner_beg[0]), y=sigDig(mid_inner_beg[1]))  # 2
            #     block.block_corners.oL = pd.Coord(x=sigDig(mid_outer_beg[0]), y=sigDig(mid_outer_beg[1]))  # 3
            #     block.block_corners_ins.iH = pd.Coord(x=sigDig(corner0[0]), y=sigDig(corner0[1]))  # 1
            #     block.block_corners_ins.oH = pd.Coord(x=sigDig(corner3[0]), y=sigDig(corner3[1]))  # 4
            #     block.block_corners_ins.iL = pd.Coord(x=sigDig(corner1[0]), y=sigDig(corner1[1]))  # 2
            #     block.block_corners_ins.oL = pd.Coord(x=sigDig(corner2[0]), y=sigDig(corner2[1]))  # 3
            # else:
            #
            #
            #     block.block_corners.iL = pd.Coord(x=sigDig(mid_inner_end[0]), y=sigDig(mid_inner_end[1]))
            #     block.block_corners.oL = pd.Coord(x=sigDig(mid_outer_end[0]), y=sigDig(mid_outer_end[1]))
            #     block.block_corners.iH = pd.Coord(x=sigDig(mid_inner_beg[0]), y=sigDig(mid_inner_beg[1]))
            #     block.block_corners.oH = pd.Coord(x=sigDig(mid_outer_beg[0]), y=sigDig(mid_outer_beg[1]))
            #     block.block_corners_ins.iL = pd.Coord(x=sigDig(corner0[0]), y=sigDig(corner0[1]))  # 1
            #     block.block_corners_ins.oL = pd.Coord(x=sigDig(corner3[0]), y=sigDig(corner3[1]))  # 4
            #     block.block_corners_ins.iH = pd.Coord(x=sigDig(corner1[0]), y=sigDig(corner1[1]))  # 2
            #     block.block_corners_ins.oH = pd.Coord(x=sigDig(corner2[0]), y=sigDig(corner2[1]))  # 3

            # new_corners_inner = gf.intersectLineCircle(
            #     gf.findLineThroughTwoPoints(corner0, corner3),
            #     [radius, coil.bore_center.x, coil.bore_center.y])
            # if min(abs(new_corners_inner[0][0] - corner0[0]),
            #        abs(new_corners_inner[1][0] - corner0[0])) == abs(new_corners_inner[0][0] - corner0[0]):
            #     new_inner = new_corners_inner[0]
            # else:
            #     new_inner = new_corners_inner[1]
            # outer_radius = (np.sqrt(np.square(corner2[0] - coil.bore_center.x) +
            #                         np.square(corner2[1] - coil.bore_center.y)))
            # new_corners_outer = gf.intersectLineCircle(
            #     gf.findLineThroughTwoPoints(corner0, corner3),
            #     [outer_radius, coil.bore_center.x, coil.bore_center.y])
            # if min(abs(new_corners_outer[0][0] - corner0[0]),
            #        abs(new_corners_outer[1][0] - corner0[0])) == abs(new_corners_outer[0][0] - corner0[0]):
            #     new_outer = new_corners_outer[0]
            # else:
            #     new_outer = new_corners_outer[1]
            # if corner0[0] < corner1[0]:
            #     block.block_corners.iH = pd.Coord(x=sigDig(new_inner[0]), y=sigDig(new_inner[1]))  # 1
            #     block.block_corners.oH = pd.Coord(x=sigDig(new_outer[0]), y=sigDig(new_outer[1]))  # 4
            #     block.block_corners.iL = pd.Coord(x=sigDig(corner1[0]), y=sigDig(corner1[1]))  # 2
            #     block.block_corners.oL = pd.Coord(x=sigDig(corner2[0]), y=sigDig(corner2[1]))  # 3
            # else:
            #     block.block_corners.iL = pd.Coord(x=sigDig(new_inner[0]), y=sigDig(new_inner[1]))
            #     block.block_corners.oL = pd.Coord(x=sigDig(new_outer[0]), y=sigDig(new_outer[1]))
            #     block.block_corners.iH = pd.Coord(x=sigDig(corner1[0]), y=sigDig(corner1[1]))
            #     block.block_corners.oH = pd.Coord(x=sigDig(corner2[0]), y=sigDig(corner2[1]))

        # ((block.pole % 2 == 0) * np.sign(-I[0]) +
        #  (block.pole % 2 != 0) * np.sign(I[0])) * block.radius / 1e3]
        return self.data.coil

    def getCablePositions(self, blocks: Dict[str, pd.Block] = None, cadata: pd.Cadata = None, verbose: bool = False):
        """
            **Returns insulated and bare conductor positions, and strand positions**

            Find insulated and bare conductor positions, and strand positions

            :param cadata: conductor data
            :type cadata: Cadata
            :param blocks: blocks data
            :type blocks: Dict[str, Block]
            :param verbose: flag that determines whether the output are printed
            :type verbose: bool

            :return: list
        """
        blockTypes = {1: 'Cos-theta', 2: 'Block-coil'}

        if blocks:
            self.roxieData.coil.blocks = blocks
            self.model_data = DataModelMagnet(Conductors=[Conductor(cable=Rutherford(type='Rutherford'))])
            self.data = pd.RoxieData()

        self.half_turn_number_start_index_per_block = np.cumsum([value.nco for value in self.roxieData.coil.blocks.values()]).tolist()

        # plt.figure(figsize=(10, 10))
        # self.ax = plt.axes()
        # self.ax.set_xlim(-0.2, 0.2)
        # self.ax.set_ylim(-0.2, 0.2)
        for no, blk in self.roxieData.coil.blocks.items():
            self.no = int(no)
            self.block = self.roxieData.coil.blocks[no]
            if blocks:
                self.data.coil.coils[self.block.coil] = pd.Pole(type='cos-theta')
                coil = self.data.coil.coils[self.block.coil]
                coil.poles[self.block.pole] = pd.Layer()
                coil.poles[self.block.pole].layers[self.block.layer] = pd.Winding()
                layer = coil.poles[self.block.pole].layers[self.block.layer]
                layer.windings[self.block.winding] = pd.WindingData(conductors_number=self.block.nco, conductor_name=self.block.condname)
                layer.windings[self.block.winding].blocks[self.no] = pd.BlockData(block_corners=pd.Corner(), current_sign=int(np.sign(self.block.current)))

            if self.model_data.Conductors[0].cable.type == 'Ribbon':  # todo: check if this is actually used for ribbon
                # Double check that the winding is correct.
                index = None
                for i, sublist in enumerate(self.windings):
                    if self.no in sublist:
                        index = i
                        break
                if index:
                    self.block.winding = index + 1
                    self.roxieData.coil.blocks[str(self.no)].winding = self.block.winding

            # Get desired conductor data
            self.cond_name = self.block.condname
            self.getConductorFromCableDatabase(cadata=cadata)

            # Calculate x/y positions of the conductor corners and strands
            if verbose:
                print('Block {} is of type {} --> {}.'.format(self.no, self.block.type, blockTypes[self.block.type]))

            self.findConductorPositions(verbose=verbose)
        for no, blk in self.roxieData.coil.blocks.items():
            self.data.coil.physical_order.append(pd.Order(coil=blk.coil, pole=blk.pole, layer=blk.layer,
                                                          winding=blk.winding, block=int(no)))
        # if verbose:
        #     print('Total number of conductors (half-turns): {}'.format(len(self.xPos)))
        # plt.show()

        return self.data.coil

    def getWedgePositions(self, coil: pd.CoilData = None, verbose: bool = False):
        """
            **Returns wedge positions**

            Find wedge positions

            :param coil: coil data
            :type coil: CoilData
            :param verbose: flag that determines whether the output are printed
            :type verbose: bool

            :return: list
        """
        if coil:
            self.data = pd.RoxieData()
            self.data.coil = coil
            self.model_data = DataModelMagnet(Conductors=[Conductor(cable=Rutherford(type='Rutherford'))])

        # xPos = []
        # yPos = []
        # xBarePos = []
        # yBarePos = []
        # iPos = []
        # xblockCorners = []
        # yblockCorners = []
        # #colormap = cm.get_cmap('nipy_spectral')
        # #ht_coil = []
        # block_coil = []
        # strands = []
        # strand_blocks = []
        # #strand_blocks_non_ins = []
        # strand_blocks_ref = []
        # ht_number_list = []
        # block_number_list = []
        # for eo in self.data.coil.physical_order:
        #     winding = self.data.coil.coils[eo.coil].poles[eo.pole].layers[eo.layer].windings[eo.winding]
        #     block = winding.blocks[eo.block]
        #     xblockCorners.append([block.block_corners_ins.iH.x, block.block_corners_ins.oH.x, block.block_corners_ins.oL.x,
        #                           block.block_corners_ins.iL.x])
        #     yblockCorners.append([block.block_corners_ins.iH.y, block.block_corners_ins.oH.y, block.block_corners_ins.oL.y,
        #                           block.block_corners_ins.iL.y])
        #     block_number_list.append(eo.block)
        #     block_coil.append(eo.coil)
        #     # Save half turn corners
        #     for halfTurn_nr, halfTurn in block.half_turns.items():
        #         insu = halfTurn.corners.insulated
        #         bare = halfTurn.corners.bare
        #         xPos.append([insu.iH.x, insu.oH.x, insu.oL.x, insu.iL.x])
        #         yPos.append([insu.iH.y, insu.oH.y, insu.oL.y, insu.iL.y])
        #         xBarePos.append([bare.iH.x, bare.oH.x, bare.oL.x, bare.iL.x])
        #         yBarePos.append([bare.iH.y, bare.oH.y, bare.oL.y, bare.iL.y])
        #         iPos.append(block.current_sign)
        #         ht_number_list.append(halfTurn_nr)
        #
        # # Create normalized scale between zero and number of half turns.
        # #normalize = Normalize(vmin=0, vmax=len(xPos))
        #
        # # Plot blocks and block number in coil
        # # max_size = max(max(xblockCorners, key=max))    # Plot bare half turns
        # for c, (cXBarePos, cYBarePos, ht_number) in enumerate(zip(xBarePos, yBarePos, ht_number_list)):
        #     pt1, pt2, pt3, pt4 = (cXBarePos[0], cYBarePos[0]), (cXBarePos[1], cYBarePos[1]), \
        #                          (cXBarePos[2], cYBarePos[2]), (cXBarePos[3], cYBarePos[3])
        #     if iPos[c] > 0:
        #         line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='r', edgecolor='k', alpha=.25)
        #     else:
        #         line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='r', edgecolor='k', alpha=.25)
        #     #x_ave_cond, y_ave_cond = sum(cXBarePos) / len(cXBarePos), sum(cYBarePos) / len(cYBarePos)
        #     # plt.text(x_ave_cond, y_ave_cond, '{}'.format(ht_number), color='b', fontsize=14)
        #     plt.gca().add_line(line)
        # for c, (cXBarePos, cYBarePos, ht_number) in enumerate(zip(xPos, yPos, ht_number_list)):
        #     pt1, pt2, pt3, pt4 = (cXBarePos[0], cYBarePos[0]), (cXBarePos[1], cYBarePos[1]), \
        #                          (cXBarePos[2], cYBarePos[2]), (cXBarePos[3], cYBarePos[3])
        #     if iPos[c] > 0:
        #         line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='b', edgecolor='k', alpha=.25)
        #     else:
        #         line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='b', edgecolor='k', alpha=.25)
        #     #x_ave_cond, y_ave_cond = sum(cXBarePos) / len(cXBarePos), sum(cYBarePos) / len(cYBarePos)
        #     # plt.plot(pt1[0], pt1[1], '.', color='k' )
        #     # plt.plot(pt2[0], pt2[1], '.', color='g' )
        #     # plt.plot(pt3[0], pt3[1], '.', color='r' )
        #     # plt.plot(pt4[0], pt4[1], '.', color='b' )
        #     #plt.text(x_ave_cond, y_ave_cond, '{}'.format(ht_number), color='b', fontsize=14)
        #     plt.gca().add_line(line)
        # for c, (xblockCorners, yblockCorners, blk_number) in enumerate(zip(xblockCorners, yblockCorners, block_number_list)):
        #     pt1, pt2, pt3, pt4 = (xblockCorners[0], yblockCorners[0]), (xblockCorners[1], yblockCorners[1]), \
        #                          (xblockCorners[2], yblockCorners[2]), (xblockCorners[3], yblockCorners[3])
        #
        #     # plt.plot(pt1[0], pt1[1], '.', color='k', markersize=20 )
        #     # plt.plot(pt2[0], pt2[1], '.', color='k', markersize=20 )
        #     # plt.plot(pt3[0], pt3[1], '.', color='b', markersize=20 )
        #     # plt.plot(pt4[0], pt4[1], '.', color='b', markersize=20 )
        #     # line = Line2D([pt1[0], pt2[0]], [pt1[1], pt2[1]], color='k')
        #     # plt.gca().add_line(line)
        #     # line = Line2D([pt3[0], pt4[0]], [pt3[1], pt4[1]], color='k')
        #     # plt.gca().add_line(line)
        #     # line = Line2D([pt4[0], pt1[0]], [pt4[1], pt1[1]], color='k')
        #     # plt.gca().add_line(line)
        #     # line = Line2D([pt3[0], pt2[0]], [pt3[1], pt2[1]], color='k')
        #     # plt.gca().add_line(line)
        #     bore_center_x, bore_center_y = (
        #         self.data.coil.coils[block_coil[c]].bore_center.x, self.data.coil.coils[block_coil[c]].bore_center.y)
        #     plot_arcs(pt4, pt1, (bore_center_x, bore_center_y), plt.gca())
        #     plot_arcs(pt3, pt2, (bore_center_x, bore_center_y), plt.gca())
        #     x_ave_cond, y_ave_cond = sum(xblockCorners) / len(xblockCorners), sum(yblockCorners) / len(yblockCorners)
        #     plt.text(x_ave_cond, y_ave_cond, '{}'.format(blk_number), color='b', fontsize=14)
        # for c, (strand, strand_block) in enumerate(zip(strands, strand_blocks)):
        #     # strand = strand[0]
        #     plt.plot(strand[0], strand[1], "-o", color='red')
        #     if c != len(strand_blocks) - 1:
        #         [x_coord_oh, x_coord_ol, y_coord_oh, y_coord_ol, x_coord_ih, x_coord_il, y_coord_ih, y_coord_il ]=strand_blocks[c]
        #         # [x_coord_oh2, x_coord_ol2, y_coord_oh2, y_coord_ol2, x_coord_ih2, x_coord_il2, y_coord_ih2, y_coord_il2]=strand_blocks[c+1]
        #         [x_coord_oh_ref, x_coord_ol_ref, y_coord_oh_ref, y_coord_ol_ref ]=strand_blocks_ref[c]
        #
        #         line = Line2D([x_coord_oh, x_coord_ol], [y_coord_oh, y_coord_ol], linestyle='-.', color='k')
        #         plt.gca().add_line(line)
        #         line = Line2D([x_coord_ih, x_coord_il], [y_coord_ih, y_coord_il], linestyle='--', color='g')
        #         plt.gca().add_line(line)
        #
        #         line = Line2D([x_coord_oh_ref, x_coord_ol_ref], [y_coord_oh_ref, y_coord_ol_ref], linestyle='-', color='k')
        #         plt.gca().add_line(line)

        wedge_no = 0
        for coil_nr, coil in self.data.coil.coils.items():
            if 'block-coil' not in coil.type:
                for pole_nr, pole in coil.poles.items():
                    for layer_nr, layer in pole.layers.items():
                        for winding_key, winding in layer.windings.items():
                            if winding_key < max(layer.windings.keys()) and winding_key + 1 in layer.windings.keys():
                                for cond in self.model_data.Conductors:
                                    if cond.name == winding.conductor_name:
                                        cond_type = cond.cable.type
                                        break
                                if cond_type != 'Ribbon':
                                    adj_winding = layer.windings[winding_key + 1]
                                    blocks = list(winding.blocks.keys())
                                    adj_blocks = list(adj_winding.blocks.keys())
                                    for block_key, block in winding.blocks.items():
                                        wedge_no += 1
                                        self.data.wedges[wedge_no] = pd.Wedge()
                                        wedge = self.data.wedges[wedge_no]
                                        # Instead - start from bore center
                                        if self.symmetric_coil:
                                            if blocks.index(block_key) == 0:
                                                wedge.corners = pd.Corner(
                                                    iH=adj_winding.blocks[adj_blocks[0]].block_corners.iL,
                                                    iL=block.block_corners.iH,
                                                    oH=adj_winding.blocks[adj_blocks[0]].block_corners.oL,
                                                    oL=block.block_corners.oH)
                                                wedge.corners_ins = pd.Corner(
                                                    iH=adj_winding.blocks[adj_blocks[0]].block_corners_ins.iL,
                                                    iL=block.block_corners_ins.iH,
                                                    oH=adj_winding.blocks[adj_blocks[0]].block_corners_ins.oL,
                                                    oL=block.block_corners_ins.oH)
                                                wedge.order_l = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key, block=block_key)
                                                wedge.order_h = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key + 1, block=adj_blocks[0])
                                            else:
                                                wedge.corners = pd.Corner(
                                                    iH=block.block_corners.iL,
                                                    iL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners.iH,
                                                    oH=block.block_corners.oL,
                                                    oL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners.oH)
                                                wedge.corners_ins = pd.Corner(
                                                    iH=block.block_corners_ins.iL,
                                                    iL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners_ins.iH,
                                                    oH=block.block_corners_ins.oL,
                                                    oL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners_ins.oH)
                                                wedge.order_h = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key, block=block_key)
                                                wedge.order_l = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key + 1,
                                                                         block=adj_blocks[blocks.index(block_key)])
                                        else:
                                            p1 = (block.block_corners.iH.x, block.block_corners.iH.y)
                                            if blocks.index(block_key) == 0:
                                                p2 = (adj_winding.blocks[adj_blocks[0]].block_corners.iH.x,
                                                      adj_winding.blocks[adj_blocks[0]].block_corners.iH.y)
                                            else:
                                                p2 = (adj_winding.blocks[adj_blocks[1]].block_corners.iH.x,
                                                      adj_winding.blocks[adj_blocks[1]].block_corners.iH.y)

                                            center = (coil.bore_center.x, coil.bore_center.y)

                                            anticlockwise = self.find_orientation(p1, p2, center)

                                            if anticlockwise:
                                                wedge.corners = pd.Corner(
                                                    iH=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners.iL,
                                                    iL=block.block_corners.iH,
                                                    oH=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners.oL,
                                                    oL=block.block_corners.oH)
                                                wedge.corners_ins = pd.Corner(
                                                    iH=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners_ins.iL,
                                                    iL=block.block_corners_ins.iH,
                                                    oH=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners_ins.oL,
                                                    oL=block.block_corners_ins.oH)
                                                wedge.order_l = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key, block=block_key)
                                                wedge.order_h = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key + 1, block=adj_blocks[0])
                                            else:
                                                wedge.corners = pd.Corner(
                                                    iH=block.block_corners.iL,
                                                    iL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners.iH,
                                                    oH=block.block_corners.oL,
                                                    oL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners.oH)
                                                wedge.corners_ins = pd.Corner(
                                                    iH=block.block_corners_ins.iL,
                                                    iL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners_ins.iH,
                                                    oH=block.block_corners_ins.oL,
                                                    oL=adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners_ins.oH)
                                                wedge.order_h = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key, block=block_key)
                                                wedge.order_l = pd.Order(coil=coil_nr, pole=pole_nr, layer=layer_nr,
                                                                         winding=winding_key + 1,
                                                                         block=adj_blocks[blocks.index(block_key)])

                                        # color = 'k'
                                        # arg = [(wedge.corners.iH.x, wedge.corners.iH.y),
                                        #        (wedge.corners.iL.x, wedge.corners.iL.y),
                                        #        (wedge.corners.oH.x, wedge.corners.oH.y),
                                        #        (wedge.corners.oL.x, wedge.corners.oL.y)]
                                        # line = Line2D([arg[0][0], arg[1][0]], [arg[0][1], arg[1][1]], color=color)
                                        # plt.gca().add_line(line)
                                        # line = Line2D([arg[3][0], arg[2][0]], [arg[3][1], arg[2][1]], color=color)
                                        # plt.gca().add_line(line)
                                        # line = Line2D([arg[0][0], arg[2][0]], [arg[0][1], arg[2][1]], color=color)
                                        # plt.gca().add_line(line)
                                        # line = Line2D([arg[3][0], arg[1][0]], [arg[3][1], arg[1][1]], color=color)
                                        # plt.gca().add_line(line)
                                        # if block_key>5:
                                        #     break

                                        # ax.text(wedge.corners.iH.x, wedge.corners.iH.y, 'iH', style='italic', bbox={'facecolor': 'red', 'pad': 2})
                                        # ax.text(wedge.corners.oH.x, wedge.corners.oH.y, 'oH', style='italic', bbox={'facecolor': 'red', 'pad': 2})
                                        # ax.text(wedge.corners.iL.x, wedge.corners.iL.y, 'iL', style='italic', bbox={'facecolor': 'red', 'pad': 2})
                                        # ax.text(wedge.corners.oL.x, wedge.corners.oL.y, 'oL', style='italic', bbox={'facecolor': 'red', 'pad': 2})
                                        # if blocks.index(block_key) == 0:
                                        #     corners1 = block.block_corners
                                        #     corners2 = adj_winding.blocks[adj_blocks[0]].block_corners
                                        # else:
                                        #     corners2 = block.block_corners
                                        #     corners1 = adj_winding.blocks[adj_blocks[blocks.index(block_key)]].block_corners
                                        #
                                        # if corners1.iL.y >= 0.:
                                        #     wedge.corners = pd.Corner(iH=corners2.iL, iL=corners1.iH,
                                        #                               oH=corners2.oL, oL=corners1.oH)
                                        # else:
                                        #     wedge.corners = pd.Corner(iH=corners1.iL, iL=corners2.iH,
                                        #                               oH=corners1.oL, oL=corners2.oH)

                                        wedge.corrected_center = pd.CenterShift()
                                        wedge.corrected_center_ins = pd.CenterShift()
                                        if wedge.corners.iL.y >= 0.:
                                            inner, outer = arcCenter(C=coil.bore_center, iH=wedge.corners.iH,
                                                                     iL=wedge.corners.iL,
                                                                     oH=wedge.corners.oH, oL=wedge.corners.oL)
                                            inner_ins, outer_ins = arcCenter(C=coil.bore_center, iH=wedge.corners_ins.iH,
                                                                             iL=wedge.corners_ins.iL,
                                                                             oH=wedge.corners_ins.oH,
                                                                             oL=wedge.corners_ins.oL)
                                        else:
                                            inner, outer = arcCenter(C=coil.bore_center, iH=wedge.corners.iL,
                                                                     iL=wedge.corners.iH,
                                                                     oH=wedge.corners.oL, oL=wedge.corners.oH)
                                            inner_ins, outer_ins = arcCenter(C=coil.bore_center, iH=wedge.corners_ins.iL,
                                                                             iL=wedge.corners_ins.iH,
                                                                             oH=wedge.corners_ins.oL,
                                                                             oL=wedge.corners_ins.oH)
                                        wedge.corrected_center.inner = pd.Coord(x=float(sigDig(inner[0])),
                                                                                y=float(sigDig(inner[1])))
                                        wedge.corrected_center.outer = pd.Coord(x=float(sigDig(outer[0])),
                                                                                y=float(sigDig(outer[1])))
                                        wedge.corrected_center_ins.inner = pd.Coord(x=float(sigDig(inner_ins[0])),
                                                                                    y=float(sigDig(inner_ins[1])))
                                        wedge.corrected_center_ins.outer = pd.Coord(x=float(sigDig(outer_ins[0])),
                                                                                    y=float(sigDig(outer_ins[1])))

        # plt.show()

        return self.data if coil else self.data.wedges

    def find_orientation(self, p1, p2, center):
        """
        Take point 1 and point to and a center anc calculate the orientation going from p1-p2.
        Returns the boolean anticlockwise which indicate the resulting orientation.
        """

        Ax, Ay = (p1[0], p1[1])

        Bx, By = (p2[0], p2[1])

        Cx, Cy = (center[0], center[1])
        AC = (Cx - Ax, Cy - Ay)
        BC = (Cx - Bx, Cy - By)
        cross_product = AC[0] * BC[1] - AC[1] * BC[0]
        if cross_product > 0:
            anticlockwise = True

        else:
            anticlockwise = False
        return anticlockwise

    def rearrange_half_turns_ribbon(self):
        """
        Rearranges the half turns in the data structure to match the ribbon cable geometry
        :return:
        """
        data = self.data  # Copy coil data structure
        data_new = copy.deepcopy(self.data)
        if self.model_data is not None:

            # List describes which block belongs to which conductor and whether this is a Ribbon cable.
            list_flag_ribbon = []
            for i, cond in enumerate(self.model_data.CoilWindings.conductor_to_group):
                list_flag_ribbon.append(self.model_data.Conductors[cond - 1].cable.type == 'Ribbon')
            if all(list_flag_ribbon):  # If all cables are ribbon
                data_new.coil.physical_order = list()
                physical_order_list = []
                half_turn_count = 0
                nbr_strands_per_half_wnd = {coil_nr: {} for coil_nr, coil in data.coil.coils.items()}
                for coil_nr, coil in data.coil.coils.items():
                    first_pole = coil.poles[list(coil.poles.keys())[0]]
                    first_lyr = first_pole.layers[list(first_pole.layers.keys())[0]]
                    for winding_nr, winding in first_lyr.windings.items():
                        wnd_idx = list(first_lyr.windings.keys()).index(winding_nr)
                        first_blk = winding.blocks[list(winding.blocks.keys())[0]]
                        nbr_ht = len(first_blk.half_turns)
                        nbr_strands = sum([len(strand_group.strand_positions) for strand_group in
                                           list(first_blk.half_turns.values())[0].strand_groups.values()])
                        nbr_strands_per_half_wnd[coil_nr][wnd_idx] = nbr_ht * nbr_strands
                for coil_nr, coil in data.coil.coils.items():
                    for pole_nr, pole in coil.poles.items():
                        data_new_pole = data_new.coil.coils[coil_nr].poles[pole_nr]
                        data_new_pole.layers = dict()
                        for layer_nr, layer in pole.layers.items():
                            for winding_nr, winding in layer.windings.items():
                                wnd_idx = list(layer.windings.keys()).index(winding_nr)
                                # data_new.coil.coils[coil_nr].poles[pole_nr].layers[layer_nr].windings[winding_nr].blocks = dict()
                                for block_nr, block in winding.blocks.items():
                                    # create dict of number of new blocks following global block numbering all params copied apart from half turns which should be empty.
                                    blocks_new_in_old, layer_nr_per_blk, winding_nr_per_blk = dict(), dict(), dict()  # Create new blocks in initial block
                                    init_ht_number = 1  # Initial half turn number of original geometry
                                    current_sign = block.current_sign  # Current sign is preserved from the block
                                    nbr_ht = len(block.half_turns)
                                    nbr_strands = sum([len(strand_group.strand_positions) for strand_group in list(block.half_turns.values())[0].strand_groups.values()])
                                    half_turn_count_latest = sum([strs for wnd, strs in nbr_strands_per_half_wnd[coil_nr].items() if wnd < wnd_idx])
                                    half_turn_count_latest += (pole_nr - 1) * sum([strs for strs in nbr_strands_per_half_wnd[coil_nr].values()])
                                    if list(winding.blocks.keys()).index(block_nr) == 1:
                                        half_turn_count_latest += sum([strs for strs in nbr_strands_per_half_wnd[coil_nr].values()]) * len(coil.poles)

                                    for ht_nr, ht in block.half_turns.items():
                                        for strand_group_nr, strand_group in ht.strand_groups.items():
                                            for strand_nr, strand_position in strand_group.strand_positions.items():
                                                block_current_key = nbr_strands * (block_nr - 1) + strand_nr
                                                if strand_nr not in data_new_pole.layers:
                                                    data_new_pole.layers[strand_nr] = pd.Winding()
                                                if block_current_key not in data_new_pole.layers[strand_nr].windings and list(winding.blocks.keys()).index(block_nr) == 0:
                                                    data_new_pole.layers[strand_nr].windings[block_current_key] = pd.WindingData(
                                                        conductors_number=winding.conductors_number, conductor_name=winding.conductor_name)
                                                if block_current_key not in blocks_new_in_old:
                                                    blocks_new_in_old[block_current_key] = pd.BlockData()
                                                    layer_nr_per_blk[block_current_key] = strand_nr
                                                    winding_nr_per_blk[block_current_key] = block_current_key if list(winding.blocks.keys()).index(block_nr) == 0\
                                                        else list(data_new_pole.layers[strand_nr].windings.keys())[list(layer.windings.keys()).index(winding_nr)]
                                                block_current = blocks_new_in_old[block_current_key]  # Current block each ht

                                                # For each strand split ht into nbr_strands into a new half turn
                                                # Choose ht number to: ht+nbr_ht*(strand_nr-1)
                                                insu = ht.corners.insulated
                                                bare = ht.corners.bare
                                                il_ins_vector = (bare.iL.x - insu.iL.x, bare.iL.y - insu.iL.y)
                                                ih_ins_vector = (bare.iH.x - insu.iH.x, bare.iH.y - insu.iH.y)
                                                ol_ins_vector = (bare.oL.x - insu.oL.x, bare.oL.y - insu.oL.y)
                                                oh_ins_vector = (bare.oH.x - insu.oH.x, bare.oH.y - insu.oH.y)

                                                if strand_nr == 1:
                                                    x_coord_ih = insu.iH.x + (insu.oH.x - insu.iH.x) * (strand_nr - 1) / nbr_strands + ih_ins_vector[0]
                                                    y_coord_ih = insu.iH.y + (insu.oH.y - insu.iH.y) * (strand_nr - 1) / nbr_strands + ih_ins_vector[1]
                                                    x_coord_il = insu.iL.x + (insu.oL.x - insu.iL.x) * (strand_nr - 1) / nbr_strands + il_ins_vector[0]
                                                    y_coord_il = insu.iL.y + (insu.oL.y - insu.iL.y) * (strand_nr - 1) / nbr_strands + il_ins_vector[1]
                                                    x_coord_oh = insu.iH.x + (insu.oH.x - insu.iH.x) * (strand_nr) / nbr_strands + oh_ins_vector[0]
                                                    y_coord_oh = insu.iH.y + (insu.oH.y - insu.iH.y) * (strand_nr) / nbr_strands + oh_ins_vector[1]
                                                    x_coord_ol = insu.iL.x + (insu.oL.x - insu.iL.x) * (strand_nr) / nbr_strands + ol_ins_vector[0]
                                                    y_coord_ol = insu.iL.y + (insu.oL.y - insu.iL.y) * (strand_nr) / nbr_strands + ol_ins_vector[1]
                                                elif strand_nr == nbr_strands:
                                                    x_coord_ih = insu.iH.x + (insu.oH.x - insu.iH.x) * (strand_nr - 1) / nbr_strands + ih_ins_vector[0]
                                                    y_coord_ih = insu.iH.y + (insu.oH.y - insu.iH.y) * (strand_nr - 1) / nbr_strands + ih_ins_vector[1]
                                                    x_coord_il = insu.iL.x + (insu.oL.x - insu.iL.x) * (strand_nr - 1) / nbr_strands + il_ins_vector[0]
                                                    y_coord_il = insu.iL.y + (insu.oL.y - insu.iL.y) * (strand_nr - 1) / nbr_strands + il_ins_vector[1]
                                                    x_coord_oh = insu.iH.x + (insu.oH.x - insu.iH.x) * (strand_nr) / nbr_strands + oh_ins_vector[0]
                                                    y_coord_oh = insu.iH.y + (insu.oH.y - insu.iH.y) * (strand_nr) / nbr_strands + oh_ins_vector[1]
                                                    x_coord_ol = insu.iL.x + (insu.oL.x - insu.iL.x) * (strand_nr) / nbr_strands + ol_ins_vector[0]
                                                    y_coord_ol = insu.iL.y + (insu.oL.y - insu.iL.y) * (strand_nr) / nbr_strands + ol_ins_vector[1]
                                                else:
                                                    x_coord_ih = insu.iH.x + (insu.oH.x - insu.iH.x) * (strand_nr - 1) / nbr_strands + ih_ins_vector[0]  # +insulation_x
                                                    y_coord_ih = insu.iH.y + (insu.oH.y - insu.iH.y) * (strand_nr - 1) / nbr_strands + ih_ins_vector[1]  # -insulation_y
                                                    x_coord_il = insu.iL.x + (insu.oL.x - insu.iL.x) * (strand_nr - 1) / nbr_strands + il_ins_vector[0]  # +insulation_x
                                                    y_coord_il = insu.iL.y + (insu.oL.y - insu.iL.y) * (strand_nr - 1) / nbr_strands + il_ins_vector[1]  # +insulation_y
                                                    x_coord_oh = insu.iH.x + (insu.oH.x - insu.iH.x) * (strand_nr) / nbr_strands + oh_ins_vector[0]  # -insulation_x
                                                    y_coord_oh = insu.iH.y + (insu.oH.y - insu.iH.y) * (strand_nr) / nbr_strands + oh_ins_vector[1]  # -insulation_y
                                                    x_coord_ol = insu.iL.x + (insu.oL.x - insu.iL.x) * (strand_nr) / nbr_strands + ol_ins_vector[0]  # -insulation_x
                                                    y_coord_ol = insu.iL.y + (insu.oL.y - insu.iL.y) * (strand_nr) / nbr_strands + ol_ins_vector[1]  # +insulation_y

                                                ht_nbr_new = init_ht_number + nbr_ht * (strand_nr - 1) + half_turn_count_latest
                                                block_current.half_turns[ht_nbr_new] = pd.HalfTurn(corners=pd.HalfTurnCorner())

                                                block_current.half_turns[ht_nbr_new].corners.bare = pd.Corner(
                                                    iH=pd.Coord(x=x_coord_ih, y=y_coord_ih),
                                                    iL=pd.Coord(x=x_coord_il, y=y_coord_il),
                                                    oL=pd.Coord(x=x_coord_ol, y=y_coord_ol),
                                                    oH=pd.Coord(x=x_coord_oh, y=y_coord_oh))
                                                block_current.half_turns[ht_nbr_new].corners.insulated = pd.Corner(
                                                    iH=pd.Coord(x=x_coord_ih - ih_ins_vector[0], y=y_coord_ih - ih_ins_vector[1]),
                                                    iL=pd.Coord(x=x_coord_il - il_ins_vector[0], y=y_coord_il - il_ins_vector[1]),
                                                    oL=pd.Coord(x=x_coord_ol - ol_ins_vector[0], y=y_coord_ol - ol_ins_vector[1]),
                                                    oH=pd.Coord(x=x_coord_oh - oh_ins_vector[0], y=y_coord_oh - oh_ins_vector[1]))
                                                block_current.current_sign = current_sign
                                                block_current.half_turns[ht_nbr_new].strand_groups[1] = pd.StrandGroup()
                                                block_current.half_turns[ht_nbr_new].strand_groups[1].strand_positions[1] =\
                                                    pd.Coord(x=sigDig(strand_position.x), y=sigDig(strand_position.y))
                                                half_turn_count = half_turn_count + 1

                                        init_ht_number += 1

                                    # Block corners when applicable
                                    for new_blk_name, block_curr in blocks_new_in_old.items():
                                        first_ht_nr = list(block_curr.half_turns)[0]
                                        last_ht_nr = list(block_curr.half_turns)[-1]

                                        p1 = (block_curr.half_turns[first_ht_nr].corners.bare.iH.x, block_curr.half_turns[first_ht_nr].corners.bare.iH.y)
                                        p2 = (block_curr.half_turns[last_ht_nr].corners.bare.iH.x, block_curr.half_turns[last_ht_nr].corners.bare.iH.y)
                                        center = (coil.bore_center.x, coil.bore_center.y)

                                        anticlockwise = self.find_orientation(p1, p2, center)

                                        bare_first = block_curr.half_turns[first_ht_nr].corners.bare
                                        ins_first = block_curr.half_turns[first_ht_nr].corners.insulated
                                        bare_last = block_curr.half_turns[last_ht_nr].corners.bare
                                        ins_last = block_curr.half_turns[last_ht_nr].corners.insulated
                                        if anticlockwise:
                                            block_curr.block_corners.iH = pd.Coord(x=bare_last.iH.x, y=bare_last.iH.y)  # 1
                                            block_curr.block_corners.oH = pd.Coord(x=bare_last.oH.x, y=bare_last.oH.y)  # 1

                                            block_curr.block_corners_ins.iH = pd.Coord(x=ins_last.iH.x, y=ins_last.iH.y)  # 1
                                            block_curr.block_corners_ins.oH = pd.Coord(x=ins_last.oH.x, y=ins_last.oH.y)  # 1
                                            block_curr.block_corners.iL = pd.Coord(x=bare_first.iL.x, y=bare_first.iL.y)  # 1
                                            block_curr.block_corners.oL = pd.Coord(x=bare_first.oL.x, y=bare_first.oL.y)  # 1

                                            block_curr.block_corners_ins.iL = pd.Coord(x=ins_first.iL.x, y=ins_first.iL.y)  # 1
                                            block_curr.block_corners_ins.oL = pd.Coord(x=ins_first.oL.x, y=ins_first.oL.y)  # 1
                                        else:  # First ht in new block

                                            block_curr.block_corners.iH = pd.Coord(x=bare_first.iH.x, y=bare_first.iH.y)  # 1
                                            block_curr.block_corners.oH = pd.Coord(x=bare_first.oH.x, y=bare_first.oH.y)  # 1

                                            block_curr.block_corners_ins.iH = pd.Coord(x=ins_first.iH.x, y=ins_first.iH.y)  # 1
                                            block_curr.block_corners_ins.oH = pd.Coord(x=ins_first.oH.x, y=ins_first.oH.y)  # 1
                                            block_curr.block_corners.iL = pd.Coord(x=bare_last.iL.x, y=bare_last.iL.y)  # 1
                                            block_curr.block_corners.oL = pd.Coord(x=bare_last.oL.x, y=bare_last.oL.y)  # 1

                                            block_curr.block_corners_ins.iL = pd.Coord(x=ins_last.iL.x, y=ins_last.iL.y)  # 1
                                            block_curr.block_corners_ins.oL = pd.Coord(x=ins_last.oL.x, y=ins_last.oL.y)  # 1

                                    for new_blk_name, new_blk in blocks_new_in_old.items():
                                        data_new_pole.layers[layer_nr_per_blk[new_blk_name]].windings[
                                            winding_nr_per_blk[new_blk_name]].blocks[new_blk_name] = new_blk
                                    for new_blk_name, new_blk in blocks_new_in_old.items():
                                        physical_order_list.append([coil_nr, pole_nr, layer_nr_per_blk[new_blk_name], winding_nr_per_blk[new_blk_name], new_blk_name])
                # Assign physical order
                physical_order_list.sort(key=lambda x: x[4])
                for order in physical_order_list:
                    data_new.coil.physical_order.append(pd.Order(coil=order[0], pole=order[1], layer=order[2], winding=order[3], block=order[4]))
            elif not any(list_flag_ribbon):  # All values are false
                pass
            else:
                print("Mixed Ribbon and Rutherford cables are not supported!")

        else:
            print("model_data.yaml is not given. If running a magnet containing a ribbon cable, please provide this as an input.")

        return data_new


    def getData(self, dir_iron: Path = None, dir_data: Path = None, dir_cadata: Path = None,
                dump_yamls: bool = False, path_to_yaml_model_data: str = None, verbose: bool = False):
        """
            **Returns all data**

            :param path_to_yaml_model_data: path to model_data file
            :type dir_iron: str
            :param dir_iron: directory for .iron file
            :type dir_iron: Path
            :param dir_data: directory for .data file
            :type dir_data: Path
            :param dir_cadata: directory for .cadata file
            :type dir_cadata: Path
            :param dump_yamls: flag that determines whether the dictionary is dumped into yaml
            :type dump_yamls: bool
            :param verbose: flag that determines whether the output are printed
            :type verbose: bool

            :return: list
        """
        # Re-initialize dictionaries
        self.data: pd.RoxieData = pd.RoxieData()
        self.roxieData: pd.RoxieRawData = pd.RoxieRawData()
        self.rawData: pd.RoxieRawData = pd.RoxieRawData()
        if path_to_yaml_model_data:
            try:
                self.model_data = yaml_to_data(path_to_yaml_model_data, DataModelMagnet)
            except:
                raise ValueError("Path to model_data.yaml does not exist")
        else:
            print("ParserRoxie is executed without model_data.yaml input (only applicable for ribbon cables).")


        if dir_data and dir_cadata:
            # Acquire conductor data from the .cadata Roxie file
            self.dir_cadata = dir_cadata
            self.getConductorDataFromCadataFile(verbose=verbose)

            # Acquire coil data from the .data Roxie file
            self.dir_data = dir_data
            self.getCoilDataFromDataFile(verbose=verbose)  # TODO: alternatively, allow to read coil data from DataBuilderMagnet keys

            # Save raw data from original Roxie files
            if dump_yamls:
                with open('raw_data.yaml', 'w') as yaml_file:
                    yaml.dump(self.rawData.model_dump(), yaml_file, default_flow_style=False)

            # Apply symmetry conditions and transformations to the original winding blocks
            self.roxieData = self.rawData
            self.applySymmetryConditions(verbose=verbose)
            self.applyTransformations(verbose=verbose)

            # Save comprehensive Roxie data after manipulation (inherits from the raw data)
            if dump_yamls:
                with open('roxie_data.yaml', 'w') as yaml_file:
                    yaml.dump(self.roxieData.model_dump(), yaml_file, default_flow_style=False)

            # Compute half turn positions (bare conductors, insulated conductors, strands)
            self.getCablePositions(verbose=verbose)

            # Compute wedge positions
            self.getWedgePositions(verbose=verbose)

            self.data = self.rearrange_half_turns_ribbon()

            # Acquire iron yoke data from the .iron Roxie file
            if dir_iron:
                self.dir_iron = dir_iron
                self.getIronYokeDataFromIronFile(verbose=verbose)

            # Save data for API
            if dump_yamls:
                with open('data.yaml', 'w') as yaml_file:
                    yaml.dump(self.data.model_dump(), yaml_file, default_flow_style=False)
        return self.data


def plot_arcs(start, end, center, ax, color='b'):
    """
    Plot arc using a start coordinate, end coordinate, an axis x and a color
    """

    # Define the three points
    radius = np.sqrt((start[0] - center[0]) ** 2 + (start[1] - center[1]) ** 2)

    # Calculate the start and end angles of the arc
    start_angle = np.arctan2(start[1] - center[1], start[0] - center[0])
    end_angle = np.arctan2(end[1] - center[1], end[0] - center[0])
    # central_angle = end_angle - start_angle

    # Create the arc object
    arc = Arc(center, 2 * radius, 2 * radius, angle=0, theta1=start_angle * 180 / np.pi,
              theta2=end_angle * 180 / np.pi, color=color)

    # If no Axes object was specified, use the current Axes

    # Add the arc to the plot and show the points for reference
    ax.add_patch(arc)
