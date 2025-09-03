import copy
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.patches as patches
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable

from steam_sdk.data import DataRoxieParser as pd
from steam_sdk.utils.misc import displayWaitAndClose


def arcCenterFromThreePoints(a, b, c):
    ab = [a.x - b.x, a.y - b.y]
    ac = [a.x - c.x, a.y - c.y]
    sac = [a.x * a.x - c.x * c.x, a.y * a.y - c.y * c.y]
    sba = [b.x * b.x - a.x * a.x, b.y * b.y - a.y * a.y]
    yy = (sac[0] * ab[0] + sac[1] * ab[0] + sba[0] * ac[0] + sba[1] * ac[0]) / \
         (2 * ((c.y - a.y) * ab[0] - (b.y - a.y) * ac[0]))
    xx = (sac[0] * ab[1] + sac[1] * ab[1] + sba[0] * ac[1] + sba[1] * ac[1]) / \
         (2 * ((c.x - a.x) * ab[1] - (b.x - a.x) * ac[1]))
    return [-xx, -yy]


def plotIronGeometry(iron, selectedFont):
    plt.figure(figsize=(7.5, 7.5))
    ax = plt.axes()

    max_x = 0
    max_y = 0

    for point_name, point in iron.key_points.items():
        max_x = max(point.x, max_x)
        max_y = max(point.y, max_y)

    for line_name, line in iron.hyper_lines.items():
        if line.type == 'line':
            ax.add_line(lines.Line2D([iron.key_points[line.kp1].x, iron.key_points[line.kp2].x],
                                     [iron.key_points[line.kp1].y, iron.key_points[line.kp2].y],
                                     color='black', linewidth=1))

        elif line.type == 'arc':
            pt1 = iron.key_points[line.kp1]
            pt2 = iron.key_points[line.kp2]
            center = arcCenterFromThreePoints(pt1, iron.key_points[line.kp3], pt2)
            radius = (np.sqrt(np.square(pt1.x - center[0]) + np.square(pt1.y - center[1])) +
                      np.sqrt(np.square(pt2.x - center[0]) + np.square(pt2.y - center[1]))) / 2
            if pt1.x < pt2.x and pt1.x < center[0] and pt1.y < pt2.y and pt1.y < center[1]:
                th1 = - np.arctan2(pt1.y - center[1], pt1.x - center[0]) * 180 / np.pi
            else:
                th1 = np.arctan2(pt1.y - center[1], pt1.x - center[0]) * 180 / np.pi
            th2 = np.arctan2(pt2.y - center[1], pt2.x - center[0]) * 180 / np.pi
            angle1 = math.atan2(pt1.y - center[1], pt1.x - center[0])
            angle2 = math.atan2(pt2.y - center[1], pt2.x - center[0])
            rotation_sign = math.copysign(1, (angle2 - angle1))
            theta1 = round(th1, 6)*rotation_sign
            theta2 = round(th2, 6)*rotation_sign
            ax.add_patch(patches.Arc((center[0], center[1]), width=2 * radius, height=2 * radius, angle=0,
                                     theta1=theta1, theta2=theta2, color='blue', linewidth=1))


        elif line.type == 'ellipticArc':
            pt1 = iron.key_points[line.kp1]
            pt2 = iron.key_points[line.kp2]
            a, b = line.arg1, line.arg2
            x1, y1 = pt1.x, pt1.y
            x2, y2 = pt2.x, pt2.y
            x3 = np.power(x1, 2.0)
            y3 = np.power(y1, 2.0)
            x4 = np.power(x2, 2.0)
            y4 = np.power(y2, 2.0)
            a2 = np.power(a, 2.0)
            b2 = np.power(b, 2.0)
            expression = (
                    -4.0 * a2 * b2 + a2 * y3 - 2.0 * a2 * y1 * y2 + a2 * y4 + b2 * x3 - 2.0 * b2 * x1 * x2 + b2 * x4)
            xc = x1 / 2.0 + x2 / 2.0 - a * np.power(-expression / (
                    a2 * y3 - 2.0 * a2 * y1 * y2 + a2 * y4 + b2 * x3 - 2.0 * b2 * x1 * x2 + b2 * x4),
                                                    0.5) * (y1 - y2) / (2.0 * b)

            yc = y1 / 2.0 + y2 / 2.0 + b * np.power(
                -expression / (a2 * y3 - 2.0 * a2 * y1 * y2 + a2 * y4 + b2 * x3 - 2.0 * b2 * x1 * x2 + b2 * x4),
                0.5) * (x1 - x2) / (2.0 * a)

            center = [xc, yc]
            th1 = np.degrees(np.arctan2(pt1.y - center[1], pt1.x - center[0]))
            th2 = np.degrees(np.arctan2(pt2.y - center[1], pt2.x - center[0]))
            arc = patches.Arc((center[0], center[1]), width=2 * line.arg1 ,
                              height=2 * line.arg2, angle=0,
                              theta1=min(th1, th2), theta2=max(th1, th2), color='purple', linewidth=1)
            ax.add_patch(arc)

        elif line.type == 'circle':
            pt1 = iron.key_points[line.kp1]
            pt2 = iron.key_points[line.kp2]
            center = [(pt1.x + pt2.x) / 2, (pt1.y + pt2.y) / 2]
            radius = (np.sqrt(np.square(pt1.x - center[0]) + np.square(pt1.y - center[1])) +
                      np.sqrt(np.square(pt2.x - center[0]) + np.square(pt2.y - center[1]))) / 2
            ax.add_patch(patches.Circle((center[0], center[1]),
                                        radius=radius, fill=False, edgecolor='green', linewidth=1))

    ax.set_xlim(0, 1.1 * max_x)
    ax.set_ylim(0, max_y + 0.1 * max_x)
    plt.xlabel('x [m]', **selectedFont)
    plt.ylabel('y [m]', **selectedFont)
    plt.title('Iron Yoke', **selectedFont)
    plt.set_cmap('jet')
    plt.rcParams.update({'font.size': 12})


def plotCoilGeometry(roxie_data, ax):
    data=roxie_data
    xPos = []
    yPos = []
    xBarePos = []
    yBarePos = []
    iPos = []
    xblockCorners = []
    yblockCorners = []
    colormap = cm.get_cmap('nipy_spectral')
    ht_coil = []
    block_coil = []

    for eo in data.coil.physical_order:
        winding = data.coil.coils[eo.coil].poles[eo.pole].layers[eo.layer].windings[eo.winding]
        block = winding.blocks[eo.block]
        arg = [(block.block_corners.iH.x,block.block_corners.iH.y),
               (block.block_corners.iL.x, block.block_corners.iL.y),
               (block.block_corners.oH.x, block.block_corners.oH.y),
               (block.block_corners.oL.x, block.block_corners.oL.y)]

        plt.scatter(arg[0][0], arg[0][1], color='b')
        plt.text(arg[0][0], arg[0][1], "iH", fontsize=12)

        plt.scatter(arg[1][0], arg[1][1], color='r')
        plt.text(arg[1][0], arg[1][1], "iL", fontsize=12)

        plt.scatter(arg[2][0], arg[2][1], color='g')
        plt.text(arg[2][0], arg[2][1], "oH", fontsize=12)

        plt.scatter(arg[3][0], arg[3][1], color='y')
        plt.text(arg[3][0], arg[3][1], "oL", fontsize=12)

        xblockCorners.append([block.block_corners.iH.x, block.block_corners.oH.x, block.block_corners.oL.x,
                              block.block_corners.iL.x])
        yblockCorners.append([block.block_corners.iH.y, block.block_corners.oH.y, block.block_corners.oL.y,
                              block.block_corners.iL.y])
        block_coil.append(eo.coil)
        # Save half turn corners
        for halfTurn_nr, halfTurn in block.half_turns.items():
            insu = halfTurn.corners.insulated
            bare = halfTurn.corners.bare
            xPos.append([insu.iH.x, insu.oH.x, insu.oL.x, insu.iL.x])
            yPos.append([insu.iH.y, insu.oH.y, insu.oL.y, insu.iL.y])
            xBarePos.append([bare.iH.x, bare.oH.x, bare.oL.x, bare.iL.x])
            yBarePos.append([bare.iH.y, bare.oH.y, bare.oL.y, bare.iL.y])
            iPos.append(block.current_sign)

    # Create normalized scale between zero and number of half turns.
    normalize = Normalize(vmin=0, vmax=len(xPos))

    # Plot blocks and block number in coil
    max_size = max(max(xblockCorners, key=max))    # Plot bare half turns
    for c, (cXBarePos, cYBarePos) in enumerate(zip(xBarePos, yBarePos)):
        pt1, pt2, pt3, pt4 = (cXBarePos[0], cYBarePos[0]), (cXBarePos[1], cYBarePos[1]), \
                             (cXBarePos[2], cYBarePos[2]), (cXBarePos[3], cYBarePos[3])
        if iPos[c] > 0:
            line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='r', edgecolor='k',
                               alpha=.25)
        else:
            line = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='b', edgecolor='k',
                               alpha=.25)
        plt.gca().add_line(line)


    for c, (xblockCorners, yblockCorners) in enumerate(zip(xblockCorners, yblockCorners)):
        pt1, pt2, pt3, pt4 = (xblockCorners[0], yblockCorners[0]), (xblockCorners[1], yblockCorners[1]), \
                             (xblockCorners[2], yblockCorners[2]), (xblockCorners[3], yblockCorners[3])
        line = lines.Line2D([pt1[0], pt2[0]], [pt1[1], pt2[1]], color='b')
        plt.gca().add_line(line)
        line = lines.Line2D([pt3[0], pt4[0]], [pt3[1], pt4[1]], color='b')
        plt.gca().add_line(line)
        bore_center_x, bore_center_y = (
        data.coil.coils[block_coil[c]].bore_center.x, data.coil.coils[block_coil[c]].bore_center.y)
        plot_arcs(pt4, pt1, (bore_center_x, bore_center_y), plt.gca())
        plot_arcs(pt3, pt2, (bore_center_x, bore_center_y), plt.gca())
        x_ave_cond, y_ave_cond = sum(xblockCorners) / len(xblockCorners), sum(yblockCorners) / len(yblockCorners)
        plt.text(x_ave_cond, y_ave_cond, '{}'.format(c + 1), color='b', fontsize=14)
    plt.title('Coil')
    # displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)

# ax = plt.axes()
    # cc = roxie_data.coil.coils[1].bore_center
    # ax.set_xlim((len(roxie_data.coil.coils) == 1) * 2 * cc.x - (1.1 * (max_x - cc.x) + cc.x),
    #             1.1 * (max_x - cc.x) + cc.x)
    # ax.set_ylim((len(roxie_data.coil.coils) == 1) * 2 * cc.y - (max_y + 0.1 * (max_x - cc.x)),
    #             max_y + 0.1 * (max_x - cc.x))


# Plot conductors and their numbers
def plotEdges(xPos, yPos, xBarePos, yBarePos, iPos, halfTurn_nr_list, selectedFont):
    plt.figure(figsize=(10, 10))
    # Plot edges
    for c, (cXPos, cYPos, halfTurn_nr) in enumerate(zip(xPos, yPos, halfTurn_nr_list)):
        pt1, pt2, pt3, pt4 = (cXPos[0], cYPos[0]), (cXPos[1], cYPos[1]), (cXPos[2], cYPos[2]), (cXPos[3], cYPos[3])
        if iPos[c] > 0:
            polygon = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='r', edgecolor='k', alpha=.25)
        else:
            polygon = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=True, facecolor='b', edgecolor='k', alpha=.25)
        plt.gca().add_patch(polygon)

        # Plot conductor numbers
        x_ave_cond, y_ave_cond = sum(cXPos) / len(cXPos), sum(cYPos) / len(cYPos)
        plt.text(x_ave_cond, y_ave_cond, '{}'.format(halfTurn_nr))

    # Plot edges of bare conductors
    for c, (cXBarePos, cYBarePos) in enumerate(zip(xBarePos, yBarePos )):
        pt1, pt2, pt3, pt4 = (cXBarePos[0], cYBarePos[0]), (cXBarePos[1], cYBarePos[1]), \
                             (cXBarePos[2], cYBarePos[2]), (cXBarePos[3], cYBarePos[3])
        if iPos[c] > 0:
            polygon = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=False, facecolor='r', edgecolor='k', alpha=.25)
        else:
            polygon = plt.Polygon([pt1, pt2, pt3, pt4], closed=True, fill=False, facecolor='b', edgecolor='k', alpha=.25)
        plt.gca().add_patch(polygon)

    plt.xlabel('x [m]', **selectedFont)
    plt.ylabel('y [m]', **selectedFont)
    plt.title('Conductors and their numbers', **selectedFont)
    plt.set_cmap('jet')
    plt.rcParams.update({'font.size': 12})
    plt.axis('equal')
    plt.grid()


def plot_all(roxie_data: pd.RoxieData):
    """
        Plot all default plots
    """
    selectedFont = {'fontname': 'DejaVu Sans', 'size': 14}

    if roxie_data.iron:
        plotIronGeometry(roxie_data.iron, selectedFont)
    # plotCoilGeometry(roxie_data, ax)

    xPos = []
    yPos = []
    xBarePos = []
    yBarePos = []
    iPos = []
    halfTurn_nr_list = []
    for eo in roxie_data.coil.physical_order:
        winding = roxie_data.coil.coils[eo.coil].poles[eo.pole].layers[eo.layer].windings[eo.winding]
        block = winding.blocks[eo.block]
        for halfTurn_nr, halfTurn in block.half_turns.items():
            insu = halfTurn.corners.insulated
            bare = halfTurn.corners.bare
            halfTurn_nr_list.append(halfTurn_nr)
            xPos.append([insu.iH.x, insu.oH.x, insu.oL.x, insu.iL.x])
            yPos.append([insu.iH.y, insu.oH.y, insu.oL.y, insu.iL.y])
            xBarePos.append([bare.iH.x, bare.oH.x, bare.oL.x, bare.iL.x])
            yBarePos.append([bare.iH.y, bare.oH.y, bare.oL.y, bare.iL.y])
            iPos.append(block.current_sign)
    plotEdges(xPos, yPos, xBarePos, yBarePos, iPos, halfTurn_nr_list, selectedFont)

    displayWaitAndClose(waitTimeBeforeMessage=.1, waitTimeAfterMessage=0.5)

def plot_arcs(start, end, center, ax, color='b'):
    """
    Plot arc using a start coordinate, end coordinate, an axis x and a color
    """

    # Define the three points
    radius = np.sqrt((start[0] - center[0]) ** 2 + (start[1] - center[1]) ** 2)

    # Calculate the start and end angles of the arc
    start_angle = np.arctan2(start[1] - center[1], start[0] - center[0])
    end_angle = np.arctan2(end[1] - center[1], end[0] - center[0])
    central_angle = end_angle - start_angle

    # Create the arc object
    arc = patches.Arc(center, 2 * radius, 2 * radius, angle=0, theta1=start_angle * 180 / np.pi,
                      theta2=end_angle * 180 / np.pi, color=color)

    # If no Axes object was specified, use the current Axes

    # Add the arc to the plot and show the points for reference
    ax.add_patch(arc)