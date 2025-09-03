import math

import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist


def rotatePoint(point, origin, rotation_angle):
    """
       **Returns 2-element tuple with the point coordinates after rotating by rotation_angle radians around origin point**

        Function to find point coordinates

        :param point: 2-element tuple with x/y coordinates of the point to rotate
        :type point: tuple
        :param origin: 2-element tuple with x/y coordinates of the point around which to rotate
        :type origin: tuple
        :param rotation_angle: rotation angle in radians
        :type rotation_angle: float

        :return: tuple
    """

    x = point[0]
    y = point[1]
    x0 = origin[0]
    y0 = origin[1]

    xRotated = x0 + (x - x0) * math.cos(rotation_angle) - (y - y0) * math.sin(rotation_angle)
    yRotated = y0 + (x - x0) * math.sin(rotation_angle) + (y - y0) * math.cos(rotation_angle)

    return xRotated, yRotated


def mirrorPointAboutLine(point, line):
    """
        **Mirror a point about a line**

        Function returns a 2-element list defining the x and y coordinates of the mirrored points

        :param point: 2-element list defining the x and y coordinates of the mirrored points
        :type point: list
        :param line: 3-element list defining the A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
        :type line: list

        :return: list
    """

    x = point[0]
    y = point[1]
    A = line[0]
    B = line[1]
    C = line[2]

    xMirrored = ((B ** 2 - A ** 2) * x - 2 * A * B * y - 2 * A * C) / (A ** 2 + B ** 2)
    yMirrored = ((A ** 2 - B ** 2) * y - 2 * A * B * x - 2 * B * C) / (A ** 2 + B ** 2)

    return [xMirrored, yMirrored]


def intersectTwoLines(line1: list, line2: list, verbose: bool = False) -> list:
    """
    **Find coordinates of the intersection point between two lines**

    Function returns a list:
    - 1st element:  x
    - 2nd element:  y

    :param line1: 3-element list defining the A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
    :type line1: list
    :param line2: 3-element list defining the A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
    :type line2: list
    :param verbose: flag that determines whether the output are printed
    :type verbose: bool
    :return: list
    """
    if line1[1] == 0.0:
        x = - line1[2] / line1[0]
        y = - (line2[0] * x + line2[2]) / line2[1]
    elif line2[1] == 0.0:
        x = - line2[2] / line2[0]
        y = - (line1[0] * x + line1[2]) / line1[1]
    else:
        a = - line1[0] / line1[1]
        c = - line1[2] / line1[1]
        b = - line2[0] / line2[1]
        d = - line2[2] / line2[1]
        x = (d - c) / (a - b)
        y = a * x + c

    if verbose:
        print('A1 = {}'.format(line1[0]))
        print('B1 = {}'.format(line1[1]))
        print('C1 = {}'.format(line1[2]))
        print('A2 = {}'.format(line2[0]))
        print('B2 = {}'.format(line2[1]))
        print('C2 = {}'.format(line2[2]))

    return [x, y]


def intersectLineCircle(line: list, circle: list, verbose: bool = False) -> list:
    """
    **Find coordinates of the zero, one, or two points where a line intersects a circle**

    Function returns a 2-element list:
    - 1st element:  2-element lists definining x and y positions of [x1,y1] point solution
    - 2nd element:  2-element lists definining x and y positions of [x2,y2] point solution

    :param line: 3-element list defining the A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
    :type line: list
    :param circle: 3-element list defining the R, x0, and y0 coefficients of the circle, as in: (x-x0)**2 + (y-y0)**2 = R**2
    :type circle: list
    :param verbose: flag that determines whether the output are printed
    :type verbose: bool
    :return: list
    """

    A = line[0]
    B = line[1]
    C = line[2]
    R = circle[0]
    x0 = circle[1]
    y0 = circle[2]

    # Input checks
    if R <= 0:
        raise ValueError('R must be > 0! Instead, it is {}'.format(R))

    if A == 0 and B == 0:
        raise ValueError('A and B cannot both be 0')

    if verbose:
        print('A = {}'.format(A))
        print('B = {}'.format(B))
        print('C = {}'.format(C))
        print('R = {}'.format(R))
        print('x0 = {}'.format(x0))
        print('y0 = {}'.format(y0))
        print('Line equation: {}*x+{}*y+{}=0'.format(A, B, C))
        print('Circle equation: (x-{})^2+(y-{})^2={}^2'.format(x0, y0, R))

    det = R ** 2 * (A ** 2 + B ** 2) - (A * x0 + B * y0 + C) ** 2

    if det < 0:
        if verbose:
            print('det = {} < 0 : Line does not intersect the circle!'.format(det))
        xIntersect1 = None
        yIntersect1 = None
        xIntersect2 = None
        yIntersect2 = None
    elif det == 0:
        xIntersect1 = (x0 * B ** 2 - A * B * y0 - A * C) / (A ** 2 + B ** 2)
        yIntersect1 = (y0 * A ** 2 - A * B * x0 - B * C) / (A ** 2 + B ** 2)
        xIntersect2 = None
        yIntersect2 = None
        if verbose:
            print('det = {} = 0 : Line is tangent to the circle in a single point: [{},{}]'.format(det, xIntersect1,
                                                                                                   yIntersect1))
    else:
        xIntersect1 = (x0 * B ** 2 - A * B * y0 - A * C + B * math.sqrt(det)) / (A ** 2 + B ** 2)
        xIntersect2 = (x0 * B ** 2 - A * B * y0 - A * C - B * math.sqrt(det)) / (A ** 2 + B ** 2)
        yIntersect1 = (y0 * A ** 2 - A * B * x0 - B * C - A * math.sqrt(det)) / (A ** 2 + B ** 2)
        yIntersect2 = (y0 * A ** 2 - A * B * x0 - B * C + A * math.sqrt(det)) / (A ** 2 + B ** 2)
        if verbose:
            print('det = {} > 0 : Line intersects the circle in two points: [{},{}] and [{},{}]'.format(det,
                                                                                                        xIntersect1,
                                                                                                        yIntersect1,
                                                                                                        xIntersect2,
                                                                                                        yIntersect2))

    return [[xIntersect1, yIntersect1], [xIntersect2, yIntersect2]]


def findLineThroughTwoPoints(point1: list, point2: list, verbose: bool = False) -> list:
    """
    Find coefficients of the line through two points [x1,y1] and [x2,y2]

    :param point1: 2-element list defining x/y positions of the 1st point
    :param point2: 2-element list defining x/y positions of the 2nd point
    :param verbose: flag that determines whether the output are printed
    :return: 3-element list defining the A, B, and C coefficients of the line, as in: A*x + B*y + C = 0
    """

    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]

    # Input checks
    if x1 == x2 and y1 == y2:
        raise ValueError(
            'The coefficients defining the two points must not be identical. x1=x2={} and y1=y2={}'.format(x1, y1))

    # Find parameters
    if x2 == x1:
        A = 1
        B = 0
        C = - x1
    elif y2 == y1:
        A = 0
        B = 1
        C = - y1
    else:
        A = - (y2 - y1) / (x2 - x1)
        B = + 1
        C = - (x2 * y1 - x1 * y2) / (x2 - x1)

    if verbose:
        print('A = {}'.format(A))
        print('B = {}'.format(B))
        print('C = {}'.format(C))
        print('Line equation: {}*x+{}*y+{}=0'.format(A, B, C))

    return [float(A), float(B), float(C)]


def close_pairs_ckdtree(X, max_distance):
    tree = cKDTree(X)
    pairs = tree.query_pairs(max_distance)

    return np.array(list(pairs))


def condensed_to_pair_indices(n, k):
    x = n - (4. * n ** 2 - 4 * n - 8 * k + 1) ** .5 / 2 - .5
    i = x.astype(int)
    j = k + i * (i + 3 - 2 * n) / 2 + 1
    return np.array([i, j]).T


def close_pairs_pdist(X, max_distance):
    d = pdist(X)
    k = (d < max_distance).nonzero()[0]
    return condensed_to_pair_indices(X.shape[0], k)