"""Utilities for contours.

A Contour is a a list of 2D points tha tdefine a curve or contour.
This provides aset of utilities to operate on these lists.

"""
import random
import sys

import matplotlib.path as mplPath
import matplotlib.pyplot as plt

import numpy as np

from petal_qc.utils.Geometry import Point, remove_outliers_indx


def pldist(point, start, end):
    """Return distance of point to line formed by start-end.

    Args:
    ----
        point: The point
        start: Starting point of line
        end: End point of line

    """
    if np.all(np.equal(start, end)):
        return np.linalg.norm(point - start)

    return np.divide(np.abs(np.linalg.norm(np.cross(end - start, start - point))),
                     np.linalg.norm(end - start))


def closest_segment_point(P, A, B):
    """Return distance to segment and closest point in segment.

    Args:
    ----
        P: point
        A: start of segment
        B: end of segment

    """
    try:
        M = B - A

    except TypeError:
        pass

    t0 = np.dot(P-A, M)/np.dot(M, M)
    C = A + t0*M
    dist = np.linalg.norm(P-C)

    return dist, C


def find_closest(x0, y0, cont, return_index=False):
    """Find point in contour closest to given point.

    Args:
    ----
        x0: X of point
        y0: Y of point
        cont: The contour
        return_index: if True returns the index in array

    Return:
    ------
        min_point: the coordinates of closest point

    """
    npts = len(cont)
    min_dist = sys.float_info.max
    min_point = None
    imin = -1
    for ipt in range(npts):
        x, y = cont[ipt, :]
        dist = (x-x0)**2+(y-y0)**2
        if dist < min_dist:
            imin = ipt
            min_dist = dist
            min_point = (x, y)

    if return_index:
        return imin, min_point
    else:
        return min_point


def generate_points_inside_contour(C, n, region=None):
    """Generate n points that are inside the contour.

    Args:
    ----
        C: the contour
        n: number of points to generate
        region: if given generate withing region (Xmin, Ymin, Xwidth, Ywidth)

    Returns
    -------
        Array with points

    """
    out = np.zeros([n, 2])
    if region:
        min_x = region[0]
        min_y = region[1]
        max_x = min_x + region[2]
        max_y = min_y + region[3]
    else:
        min_x, min_y, max_x, max_y = contour_bounds(C)

    npts = 0
    path = mplPath.Path(C)
    while npts < n:
        P = [random.uniform(min_x, max_x), random.uniform(min_y, max_y)]
        if path.contains_point(P):
            out[npts, :] = P
            npts += 1

    return out


def find_closest_point(x0, y0, C):
    """Find the closest point in contour."""
    P = np.array([x0, y0])
    indx, A = find_closest(x0, y0, C, return_index=True)

    i1 = indx - 1
    if indx == 0:
        i1 -= 1

    i2 = indx + 1
    if indx == len(C)-1:
        i2 = 2

    d1, P1 = closest_segment_point(P, C[i1, :], A)
    d2, P2 = closest_segment_point(P, A, C[i2, :])
    if d1 <= d2:
        return d1, P1

    else:
        return d2, P2


def contour_simplify(C, epsilon, return_mask=False):
    """Simplyfy the contour using RDP algorithm.

    Args:
    ----
        C: the contour
        epsilon: RDP alg epsilon
        return_mask: if True, return the indices of selected points
                     rather than the list of points.

    """
    stk = []

    start_index = 0
    last_index = len(C) - 1
    stk.append([start_index, last_index])

    global_start_index = start_index
    indices = np.ones(last_index - start_index + 1, dtype=bool)

    while stk:
        start_index, last_index = stk.pop()

        dmax = 0.0
        index = start_index

        for i in range(index + 1, last_index):
            if indices[i - global_start_index]:
                dist = pldist(C[i], C[start_index], C[last_index])
                if dist > dmax:
                    index = i
                    dmax = dist

        if dmax > epsilon:
            stk.append([start_index, index])
            stk.append([index, last_index])
        else:
            for i in range(start_index + 1, last_index):
                indices[i - global_start_index] = False

    if return_mask:
        return indices
    else:
        return C[indices]


def contour_smooth(C, distance):
    """Removes outliers that are at distance > distance from neighbours."""
    npts = len(C)
    for i in range(npts-2):
        dst, P = closest_segment_point(C[i, :], C[i-1, :], C[i+1, :])
        if dst > distance:
            C[i] = P

    return C


def contour_length(C):
    """Return the length of a contour."""
    n = len(C)
    dst = 0.0
    for i in range(n-1):
        dd = np.linalg.norm(C[i, :] - C[i+1, :])
        dst += dd

    return dst


def contour_path_length(C, norm=False):
    """Return the path length of a contour.

    Args:
    ----
        C: the contour
        norm: if true, the lenght wil be normalized to 1.

    Returns
    -------
        An array with the length of the contour at each points.
        0 for the first point total_length (or 1) for tha last.

    """
    npts = len(C)
    D = np.zeros(npts)
    dst = 0
    X0 = 0
    for i in range(npts):
        X = C[i, :]
        if i:
            dst += np.linalg.norm(X-X0)

        D[i] = dst
        X0 = X

    D = D/dst
    return D


def contour_area(C):
    """Return the area of a contour."""
    def Ia(i, j):
        return (C[i, 0]-C[j, 0])*(C[i, 1]+C[j, 1])

    n = len(C)
    area = Ia(0, n-1)
    for i in range(n-2):
        area += Ia(i+1, i)

    return 0.5*abs(area)


def in_contour(x, y, C):
    """Tell if it is inside the contour."""
    path = mplPath.Path(C)
    return path.contains_point(x, y, C)

def show_contour_values(img, C):
    """Creates an image of the contour values.

    Args:
    ----
        img: The image
        C: The contour


    """
    values = []
    path = mplPath.Path(C)
    my, mx = img.shape
    min_x, min_y, max_x, max_y = contour_bounds(C)
    imin_x = int(min_x)
    imin_y = int(min_y)
    chst = np.zeros([int(max_y-min_y+2), int(max_x-min_x+2)])
    for ix in range(int(min_x), int(max_x+1)):
        if ix < 0 or ix >= mx:
            continue

        for iy in range(int(min_y), int(max_y)+1):
            if iy < 0 or iy >= my:
                continue

            if path.contains_point([ix, iy]):
                chst[iy-imin_y, ix-imin_x] = img[iy, ix]
                values.append(img[iy, ix])

    values = np.array(values)
    mean = np.mean(values)
    std = np.std(values)

    fig, ax = plt.subplots(nrows=1,ncols=2)
    ax[0].hist(values, 25, range=(mean-3*std, mean+3*std))
    pcm = ax[1].imshow(chst, origin='lower', vmin=mean-3*std, vmax=mean+3*std)
    fig.colorbar(pcm, ax=ax[1])


def get_average_in_contour(img, C, tmin=sys.float_info.min, tmax=sys.float_info.max, remove_outliers=None):
    """Gets average and std of points within contour.

    We are assuming here that coordinates are integers, ie,
    indices of the matrix of values.

    Args:
    ----
        img: The image
        C: The contour
        tmin, tmax: only values in range [tmin, tmax] will be considered
        remove_outliers: If an int,

    Returns
    -------
        avg, std: averate and std.

    """
    values = []
    path = mplPath.Path(C)
    my, mx = img.shape
    min_x, min_y, max_x, max_y = contour_bounds(C)
    for ix in range(int(min_x), int(max_x+1)):
        if ix < 0 or ix >= mx:
            continue

        for iy in range(int(min_y), int(max_y)+1):
            if iy < 0 or iy >= my:
                continue

            if path.contains_point([ix, iy]):
                val = img[iy, ix]
                if val > tmin and val < tmax:
                    values.append(val)

    values = np.array(values)
    if remove_outliers is not None and isinstance(remove_outliers, (int, float)):
        indx = remove_outliers_indx(values, remove_outliers)[0]
        return np.mean(values[indx]), np.std(values[indx])

    return np.mean(values), np.std(values)


def contour_bounds(C):
    """Compute the contour bounds.

    Returns
    -------
        (min_x, min_y, max_x, maxy)

    """
    cmin = np.amin(C, axis=0)
    cmax = np.amax(C, axis=0)
    return cmin[0], cmin[1], cmax[0], cmax[1]


def contour_CM(C):
    """Return the contour center of mass."""
    return np.mean(C, axis=0)


def inset_contour(C, dist):
    """Create an inset of the controur.

    Args:
    ----
        C: Input contour
        dist: distance inwards

    Return:
    ------
        array: output contour

    """
    n = len(C)
    out = np.zeros(C.shape)
    M = Point(np.mean(C[:, 0]), np.mean([C[:, 1]]))
    for i in range(n-1):
        A = Point(C[i, :])
        B = Point(C[i+1, :])
        delta = (B - A).norm().cw()

        O = A + dist*delta
        out[i, 0] = O.x
        out[i, 1] = O.y

    out[-1, :] = out[0, :]
    return out


def adjust_contour(cont):
    """Swap contour axis (x<->y) and flip Y."""
    out = np.zeros(cont.shape)
    out[:, 0] = cont[:, 1]
    out[:, 1] = cont[:, 0]
    return out


def contour_eval(C, x):
    """Interpolate contour Y value at X.

    For this to work properly we need that the contour behaves somehow as a 1D
    as a function (monotonic).

    """
    value = np.interp(x, C[:, 0], C[:, 1])
    return value


if __name__ == "__main__":
    cntr = np.loadtxt("long_contour.csv")

    CM0 = contour_CM(cntr)
    d0, pt0 = find_closest_point(CM0[0], CM0[1], cntr)

    Cs = contour_simplify(cntr, 1.)
    CMs = contour_CM(Cs)
    ds, pts = find_closest_point(CM0[0], CM0[1], Cs)
    d = np.linalg.norm(pt0-pts)
    print("no. of points {}".format(len(cntr)))
    print("no. of points {}".format(len(Cs)))
    print(d0)
    print(ds)
    print(pt0)
    print(pts)
    print("Distance:", d)
