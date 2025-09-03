#!/usr/bin/env python3

import numpy as np
import time
from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull


def flatness_LSPL(M):
    """Compute flatness according to least squares reference plane method.

    ISO/TS 12781-1

    Args:
        M (np.ndarray): The data nx3 array

    Return
        (float) - the computed flatness
    """

    # calculate the center of mass and translate all points
    com = np.sum(M, axis=0) / len(M)
    q = M - com

    # calculate 3x3 matrix. The inner product returns total sum of 3x3 matrix
    Q = np.dot(q.T, q)

    # Calculate eigenvalues and eigenvectors
    la, vectors = np.linalg.eig(Q)

    # Extract the eigenvector of the minimum eigenvalue
    n = vectors.T[np.argmin(la)]

    e = np.dot(q, n)

    eplus = abs(np.amax(e[np.where(e > 0)]))
    eminus = abs(np.amin(e[np.where(e < 0)]))

    flatness = eplus + eminus
    return flatness


def flatness_conhull(M):
    """Compute (MZPL) flatness by convex hull algorithm.

    Robust Convex Hull-based Algoritm for Straightness and Flatness
    Determination in Coordinate Measuring (Gyula Hermann)

    Args:
        M: point array of size (npoints, ndim)

    Returns
    -------
        flatness - the computed flatness

    """
    X = M[:, 0]
    Y = M[:, 1]
    Z = M[:, 2]
    ch = Delaunay(M).convex_hull

    N = ch.shape[0]
    max_dis_local = np.zeros([N, 1])
    for i in range(0, N):
        P1 = np.array([X[ch[i, 0]], Y[ch[i, 0]], Z[ch[i, 0]]])
        P2 = np.array([X[ch[i, 1]], Y[ch[i, 1]], Z[ch[i, 1]]])
        P3 = np.array([X[ch[i, 2]], Y[ch[i, 2]], Z[ch[i, 2]]])

        normal = np.cross(P1-P2, P1-P3)

        D = -normal[0] * P3[0] - normal[1] * P3[1] - normal[2] * P3[2]

        plane_0 = np.array([normal[0], normal[1], normal[2], D])
        plane = plane_0 / np.sqrt(np.sum(plane_0**2))

        dis = np.abs(plane[0] * X[:] + plane[1] * Y[:] + plane[2] * Z[:] +
                     plane[3]) / np.sqrt(plane[0]**2 + plane[1]**2 + plane[2]**2)

        max_dis_local[i] = np.max(dis)

    return np.min(max_dis_local)


def flatness_conhullN(M):
    """Compute (MZPL) flatness by convex hull algorithm.

    Robust Convex Hull-based Algoritm for Straightness and Flatness
    Determination in Coordinate Measuring (Gyula Hermann)

    Args:
        M: point array of size (npoints, ndim)

    Returns
    -------
        flatness - the computed flatness

    """
    X = M[:, 0]
    Y = M[:, 1]
    Z = M[:, 2]
    max_dis_local = []
    hull = ConvexHull(M, incremental=False, qhull_options=None)
    for plane in hull.equations:
        dis = np.abs(plane[0] * X[:] + plane[1] * Y[:] + plane[2] * Z[:] + plane[3])
        max_dis_local.append(np.max(dis))

    return np.min(max_dis_local)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")

    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    try:
        data = np.loadtxt(options.files[0], unpack=False, skiprows=1, delimiter=',')

    except Exception as E:
        print("Could not open input file.")
        print(E)
        sys.exit(1)

    flatness = flatness_LSPL(data)
    print("LSPL: {:.4f}".format(flatness))

    flatness = flatness_conhull(data)
    print("convex-hull: {:.4f}".format(flatness))

    flatness = flatness_conhullN(data)
    print("convex-hullN: {:.4f}".format(flatness))

    N = 100
    tic = time.perf_counter()
    for i in range(N):
        flatness = flatness_LSPL(data)
    toc = time.perf_counter()
    print("LSPF: {:.4f}".format((toc-tic)/N))
    
    tic = time.perf_counter()
    for i in range(N):
        flatness = flatness_conhull(data)
    toc = time.perf_counter()
    print("Delauney: {:.4f}".format((toc-tic)/N))
    
    tic = time.perf_counter()
    for i in range(N):
        flatness = flatness_conhullN(data)
    toc = time.perf_counter()
    print("ConHull: {:.4f}".format((toc-tic)/N))