import numpy as np
import math

from matplotlib import pyplot as plt


def arc_angle_between_point_and_abscissa(p, c):
    """
        Returns the angle of an arc with center c and endpoints at (cx + radius, cy) and (px, py)
        :param p: list of x and y coordinates of a point
        :param c: list of x and y coordinates of the arc center
    """
    theta = np.arctan2(p[1] - c[1], p[0] - c[0])
    return theta + (2 * np.pi if theta < 0 else 0)

def arcCenter(C, iH, oH, iL, oL, diff_radius=None):
    """
    Calculates the inner and outer center points on an arc given the center and other points.

    :param C: Center point of the arc.
    :param iH: High inner point.
    :param oH: High outer point.
    :param iL: Low inner point.
    :param oL: Low outer point.
    :param diff_radius: Difference between inner and outer radii. Defaults to None.
    :return:
    """
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

def find_iH_oH_iL_oL(p1, p2, p3, p4, bore_center):
    """
    Finds the outer and inner points based on their distances and angles from the bore center.

    :param p1: Coordinates of point 1.
    :param p2: Coordinates of point 2.
    :param p3: Coordinates of point 3.
    :param p4: Coordinates of point 4.
    :param bore_center:  Coordinates of the bore center.
    :return: Four points representing the outer and inner points in the following order:
               (point_oH, point_oL, point_iH, point_iL)
    """
    point_list = [p1, p2, p3, p4]
    dis1 = math.sqrt((p1[0] - bore_center[0]) ** 2 + (p1[1] - bore_center[1]) ** 2)
    dis2 = math.sqrt((p2[0] - bore_center[0]) ** 2 + (p2[1] - bore_center[1]) ** 2)
    dis3 = math.sqrt((p3[0] - bore_center[0]) ** 2 + (p3[1] - bore_center[1]) ** 2)
    dis4 = math.sqrt((p4[0] - bore_center[0]) ** 2 + (p4[1] - bore_center[1]) ** 2)

    theta1 = arc_angle_between_point_and_abscissa(bore_center, p1)
    theta2 = arc_angle_between_point_and_abscissa(bore_center, p2)
    theta3 = arc_angle_between_point_and_abscissa(bore_center, p3)
    theta4 = arc_angle_between_point_and_abscissa(bore_center, p4)

    theta_list = [theta1, theta2, theta3, theta4]
    distance_list_bore = [dis1, dis2, dis3, dis4]

    theta_array = np.array(theta_list)
    distance_array = np.array(distance_list_bore)
    # Find indices of the two largest values in theta_list

    # Find indices of the two largest values in distance_list_bore
    distance_indices = np.argsort(distance_array)

    # Check the outer points
    high_ind1 = distance_indices[3]
    high_ind2 = distance_indices[2]

    if theta_array[high_ind1] > theta_array[high_ind2]:
        point_oH = point_list[high_ind1]
        point_oL = point_list[high_ind2]
    else:
        point_oH = point_list[high_ind2]
        point_oL = point_list[high_ind1]

    # Check the inner points
    low_ind1 = distance_indices[0]
    low_ind2 = distance_indices[1]
    if theta_array[low_ind1] > theta_array[low_ind2]:
        point_iH = point_list[low_ind1]
        point_iL = point_list[low_ind2]

    else:
        point_iH = point_list[low_ind2]
        point_iL = point_list[low_ind1]

    # color = 'k'
    # arg = [(point_iH[0], point_iH[1]),
    #        (point_iL[0], point_iL[1]),
    #        (point_oH[0], point_oH[1]),
    #        (point_oL[0], point_oL[1])]
    #
    # plt.scatter(arg[0][0],  arg[0][1], color='b')
    # plt.text(arg[0][0], arg[0][1], "iH", fontsize=12)
    #
    # plt.scatter(arg[1][0],  arg[1][1], color='r')
    # plt.text(arg[1][0], arg[1][1], "iL", fontsize=12)
    #
    # plt.scatter(arg[2][0],  arg[2][1], color='g')
    # plt.scatter(arg[3][0],  arg[3][1], color='y')

    return point_oH, point_oL, point_iH, point_iL