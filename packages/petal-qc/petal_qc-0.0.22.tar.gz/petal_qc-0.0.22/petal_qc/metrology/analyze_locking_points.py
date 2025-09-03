#!/usr/bin/env python3
"""Analyze the planarity of locking points."""
import math
import os
import sys
import re
import tempfile
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import numpy as np

import petal_qc.utils.docx_utils as docx_utils
from petal_qc.metrology import DataFile
from petal_qc.metrology.Cluster import cluster_points
from petal_qc.utils.Geometry import fit_plane
from petal_qc.utils.Geometry import flatness_conhull, flatness_LSPL
from petal_qc.utils.Geometry import project_to_plane
from petal_qc.utils.Geometry import vector_angle
from petal_qc.utils.utils import get_min_max
from petal_qc.metrology.show_data_file import show_data

figure_width = 14


def remove_outliers(data, cut=2.0, outliers=False, debug=False):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        outliers: if True, return the outliers rhater than remove them
        debug: be verbose if True.

    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    if outliers:
        indx = np.where(s > cut)[0]
    else:
        indx = np.where(s < cut)[0]

    return indx


def find_locking_point_plane(data, zplane, splane):
    """Find the locking point plane.

    Args:
    ----
        data: the data
        zplane: estimation of plane Z
        splane: band of width for plane Z

    Returns
    -------
        V: matrix to plroject plane
        M: mean value

    """
    # Select the LP points
    Z = data[:, 2]

    indx = np.where(abs(Z-zplane) < splane)[0]

    # Fit the first plane
    plane, V, M, L = fit_plane(data[indx])

    # Find the three clusters
    clst = cluster_points(plane, 10.0)

    good = []
    nclst = len(clst)
    for i in range(0, nclst):
        good_points = remove_outliers(plane[clst[i].xtra, 2], 0.025)
        G = [clst[i].xtra[j] for j in good_points]
        good.extend(G)

    goodP = [indx[j] for j in good]
    _, V, M, L = fit_plane(data[goodP])

    return V, M


def analyze_locking_points(fname, options):
    """Analyze locking points.

    Args:
    ----
        fname: Input file
        options: Program options.

    """
    document = docx_utils.Document()
    if options.title:
        document.add_heading(options.title, 0)

    # Open the file
    M = DataFile.read(fname, label=options.label, type=options.type)
    if M is None:
        print("Input file not found.")
        return

    analyze_locking_point_data(M,
                               nbins=options.nbins,
                               document=document,
                               save=options.save,
                               prefix=options.prefix)

    document.save(options.out)


def find_locator_clusters(data, distance=10, cut=2):
    """Find locators in data.

    It search for clusters in X, Y.

    Args:
    ----
        data: Input data
        distance: distance cut for cluster finding.
                  Points farther than this belowg to other cluster.
        cut: cut to remove outliers.

    Returns
    -------
        tuple with lsit of lcusters, rotation and offset

    """
    cindx = []
    # Find clusters
    clst = cluster_points(data, distance)
    # Trim list
    clst = [C for C in clst if C.N > 3]
    out = clst

    # Now find the bottom and right locking point.
    # bottom is the one farthest from the others
    nclst = len(clst)
    print("Found {} clusters".format(nclst))
    dst = []
    for i in range(0, nclst):
        D = 0
        Pi = np.array([clst[i].x, clst[i].y])
        for j in range(0, nclst):
            if i != j:
                Pj = np.array([clst[j].x, clst[j].y])
                D += np.sum(np.square(Pi-Pj))
        dst.append(D)

        # select point trully lying on the locators.
        good_points = remove_outliers(data[clst[i].xtra, 2], cut=cut)
        G = [clst[i].xtra[j] for j in good_points]
        clst[i].xtra = G

    # Now get the transform
    ibot = np.argmax(dst)
    LPb = clst[ibot]
    cindx.append(ibot)
    offset = -np.array([LPb.x, LPb.y])

    x = 0.0
    y = 0.0
    n = 0.0
    for i in range(0, nclst):
        if i == ibot:
            continue

        x += clst[i].x
        y += clst[i].y
        n += 1
        cindx.append(i)
    if n == 0:
        return [], np.array([[1, 0], [0, 1]]), offset

    top = np.array([x/n, y/n])
    angle = -math.atan2(top[1]+offset[1], top[0]+offset[0])
    ct = math.cos(angle)
    st = math.sin(angle)
    R = np.array([[ct, -st], [st, ct]])
    out = [clst[i] for i in cindx]

    return out, R, offset


def analyze_locking_point_data(orig_data, nbins=50, plane_fit=True, cut=3, document=None, save=None, prefix=None):
    """Analyze the locking point data.

    Args:
    ----
        orig_data: The data
        nbins: number of bins in histograms.
        plane_fit: if True, fit the core plane. Set to false if data
                   is already in the core plane reference
        cut: cut to remove outliers
        document: the MS word document
        save: True to save the figures
        prefix: A prefix for the figura name

    Return
    ------
        dictionary with data for DB.

    """
    outDB = {}
    if document:
        document.add_heading('Locking points', level=1)

    all_data = None
    parallelism = 0
    mean_dist = 0
    dist = []
    fig = show_data(orig_data, "All points", view=2, out_file=all_data, color_bar=True)
    if plane_fit:
        # Find locator and surface points
        # A little bit of a 'brute force' approach...
        loc_indx = []
        indx = []
        iloc_indx = [[], [], []]
        ref_pts = np.array([[0, 0], [127.916, 592.616], [-127.916, 592.616]])
        for i, P in enumerate(orig_data):
            dd = np.zeros(3)
            for j in range(3):
                dd[j] = np.linalg.norm(P[0:2] - ref_pts[j, :])

            idist = np.argmin(dd)
            dist = dd[idist]
            if dist < 7.5 and P[2] < -0.1 and i > 10:
                loc_indx.append(i)
                iloc_indx[idist].append(i)
            else:
                indx.append(i)

        # clean up locator points
        loc_indx = []
        for j in range(3):
            ilc = remove_outliers(orig_data[iloc_indx[j], 2], cut=4, outliers=True)
            iloc_indx[j] = [i for k, i in enumerate(iloc_indx[j]) if k not in ilc]
            loc_indx.extend(iloc_indx[j])

        # Fit to the core plane
        M, TM, avg, *_ = fit_plane(orig_data[indx], use_average=7)

        # project all data to the plane
        M = project_to_plane(orig_data, TM, [0., 0., avg[2]])
        Zmean = np.mean(M[indx, 2])
        M[:, 2] -= Zmean

        # Find locators.
        locators = M[loc_indx]

        # Normal
        N = np.array([0, 0, 1]).T

        # find locator distance to plane.
        vdL = np.dot(locators, N)
        mean_dist = np.mean(vdL) + 0.435
    else:
        M = orig_data
        loc_indx = remove_outliers(orig_data[:, 2], cut=10)  # , outliers=True)
        locators = M[loc_indx]

    if document is None:
        all_data = os.path.join(tempfile.gettempdir(), "all_data.png")

    # np.savetxt("all_data.csv", M, delimiter=',')
    fig = show_data(M, "All points", view=2, out_file=all_data, color_bar=True)
    ax = fig.get_axes()
    y_lim = ax[-1].get_ylim()
    ax[-1].fill_between([-0.535, -0.335], y_lim[0], y_lim[1], facecolor="grey", alpha=0.1)
    if document:
        txt = """All data: {} points. Left shows points after fit to core plane. \
                 Right shows the Z projection. Core points should be centered at 0, \
                locators should be at the left within the gray area."""
        document.add_picture(fig, True, figure_width,
                             caption=re.sub(' +', ' ', txt).format(len(M)))
        plt.close(fig)

    # Try to find the locking points and fit to their own plane.
    # Locking points are about 0.4mm below the petal plane.
    Zp = locators[:, 2]

    # Show the Z band
    Zband = Zp + 0.435
    indx = remove_outliers(Zband, 7.5)
    vmin, vmax, all_band = get_min_max(Zband[indx])
    parallelism = all_band

    print("Parallelism {:.3f} mm".format(parallelism))

    lxmin = min(vmin, -0.1)
    lxmax = max(vmax, 0.1)
    lxmin -= 0.1*abs(lxmin)
    lxmax += 0.1*abs(lxmax)
    xaxis = np.linspace(lxmin, lxmax, 50)

    parallel_fig = plt.figure(tight_layout=True)
    ax = parallel_fig.add_subplot(1, 1, 1)

    ax.plot([], [], ' ', label="All: band {:.3f} mm".format(all_band))
    max_avg = -9999
    max_par = -9999
    for i in range(3):
        pts = M[iloc_indx[i], 2] + 0.435
        vmin, vmax, band = get_min_max(pts)
        avg_pts = np.mean(pts)
        if abs(avg_pts) > max_par:
            max_par = abs(avg_pts)
            max_avg = avg_pts

        print("Loc par. {} - {:.3f} avg: {:.3f}".format(i, band, avg_pts))
        ax.hist(pts, bins=xaxis, label="Avg {:.3f} band {:.3f} mm".format(avg_pts, band))

    ax.legend(loc='upper left')
    y_lim = ax.get_ylim()
    ax.fill_between([-0.100, 0.100], y_lim[0], y_lim[1], facecolor="grey", alpha=0.1)
    ax.plot([mean_dist, mean_dist], [y_lim[0], y_lim[1]], '-')
    ax.text(1.05*mean_dist, 0.95*y_lim[1], "Offset {:.3f}".format(mean_dist))
    ax.set_xlabel("Out of plane (mm)")
    ax.grid()

    out = np.where(abs(Zband) > 0.1)
    nout = len(out[0])
    txt = "Passed"
    if nout > 0:
        txt = "Failed"

    outDB["PARALLELISM"] = parallelism
    outDB["OFFSET"] = mean_dist
    print("Parallelism test: {:.4f}.\n{}".format(parallelism, txt))
    if document:
        txt = """To study parallelism, we subtract -0.435 mm to the Z values. \
                 This is the nominal position of locator points. \
                 Valid points should be within a ±100 µm band around 0. \
                 This is shown in the plots below.\nParalelism is defined as the maximum deviation \
                 of all locator Z values. A perfect core shoud have an absolute value below 100 µm."""
        document.add_paragraph("Parallelism: {:.3f} mm".format(parallelism))
        document.add_paragraph("Parallelism: Number of points outside band {:d}".format(nout))
        document.add_paragraph(re.sub(' +', ' ', txt))
        document.add_picture(parallel_fig, True, figure_width,
                             caption="Paralelism. All points should lie withn the grey band.")
        plt.close(parallel_fig)

    parallel_fig = plt.figure(tight_layout=True)
    ax = parallel_fig.add_subplot(1, 1, 1)
    ax.plot(locators[:, 0], Zband, 'o')
    ax.fill_between(ax.get_xlim(), -0.1, 0.1, facecolor="grey", alpha=0.1)
    ax.set_xlabel("Petal X (mm)")
    ax.set_ylabel("Out of plane (mm)")
    ax.set_title("Paralellism lock points and petal core.")
    x_lim = ax.get_xlim()
    ax.plot([x_lim[0], x_lim[1]], [mean_dist, mean_dist], '-')
    ax.text(0.0, mean_dist + 0.1*abs(mean_dist), "Offset. {:.3f}".format(mean_dist))
    ax.grid()
    if document:
        document.add_picture(parallel_fig, True, figure_width,
                             caption="Paralelism. All points should lie withn the grey band.")
        plt.close(parallel_fig)

    out_file = None
    name = "LP_core_plane"
    if save is True:
        if prefix is None:
            out_file = "{}.png".format(name)
        else:
            out_file = "{}-{}.png".format(prefix, name)

        plt.savefig(out_file, dpi=300)

    # Fit the locator plane
    plane, V, X, L = fit_plane(locators, use_average=4)

    # find the parallelism.
    # We do this computing the angle between planes
    angle = vector_angle([0., 0., 1.], V[:, 2])
    print("parallelism (angle): {:.4f}".format(angle))

    if document:
        document.add_paragraph("Parallelism: angle between core plane and locator plane {:.4f} rad".format(angle))
        document.add_paragraph("Locking point distance to petal surface: {:.3f} mm".format(X[2]))

    # Cluster locator points to find the actual locators
    print("Clusters after plane fit.")
    clst, R, O = find_locator_clusters(locators, 10)
    # transform
    for C in clst:
        P = np.array([C.x, C.y])
        P = np.matmul(R, P+O)
        C.x = P[0]
        C.y = P[1]

    for i in range(locators.shape[0]):
        locators[i, 0:2] = np.matmul(R, locators[i, 0:2] + O)

    print("Cluster Z")
    good = []
    for C in clst:
        good.extend(C.xtra)
        print("{:7.3f} {:7.3f} {:7.3f}".format(C.x, C.y, C.z))

    if len(good):
        flatness = flatness_LSPL(plane[good, :])
        print("Locking point flatness (LSPL): {:.1f}".format(1000*flatness))
    else:
        print("Not enough points to compute flatness.")
        flatness = -1.e-3

    outDB["COPLANARITY_LOCATORS"] = flatness
    if document:
        document.add_paragraph("Locking point flatness (LSPL): {:.1f} µm.".format(1000*flatness))

    # Show all data
    fig = show_data(plane[good, :], "All", nbins=nbins, color_bar=True)
    if document:
        document.add_paragraph("All data points in locator plane.")
        document.add_picture(fig, True, figure_width, caption="All points in locator plane.")
        document.add_paragraph("Locator points.")
        plt.close(fig)

    print("Clusters:")
    for iclst, C in enumerate(clst):
        if save:
            if prefix is None:
                out_file = "cluster_{}.png".format(iclst)
            else:
                out_file = "{}-cluster_{}.png".format(prefix, iclst)
        else:
            out_file = None

        print("\tCluster {}: {:.3f} {:.3f} {:.3f}".format(iclst, C.x, C.y, C.z))
        fig = show_data(plane[C.xtra, :],
                        "Cluster: {:.3f}, {:.3f}".format(C.x, C.y),
                        nbins=nbins,
                        color_bar=True)
        zmean = np.mean(plane[C.xtra, 2])
        zstd = np.std(plane[C.xtra, 2])

        if len(C.xtra) < 10 or zstd>0.05:
            dl = outDB.setdefault("defects", [])
            dl.append(
                {
                    "name": "LOCATOR_CLUSTERS",
                    "description": "Cluster at {:.3f}, {:.3f} has few points [{}] or large spread {:.3f}".format(C.x, C.y, len(C.xtra), zstd)
                }
            )

        print("\t\t-> Z mean {:.3f} std {:.3f} [{}]".format(zmean, zstd, len(C.xtra)))
        if document:
            document.add_picture(fig, True, figure_width,
                                 caption="Cluster {}. Number of points {}".format(iclst, len(C.xtra)))
            plt.close(fig)

    return outDB


def locking_point_positions(positions, document=None):
    """Make a report on locking point positions.

    Args:
    ----
        positions: Measured values
        document: The document (docx). Defaults to None.

    Return
    ------
        outDB: dictionary witf DB paremeters.

    """
    # Nominal values for "front". Back have oposite sign on X.
    outDB = {}
    key_delta = ["PL01", "PL02", "PL03"]
    key_rel_pos = ["PL01-FD01", "PL01-FD02", "FD01-FD02"]
    nom_values = (None,
                  np.array((0, 0, 4)),                  # Bottom locator (PL01)
                  np.array((127.916, 592.616, 4)),      # Top slot (PL02)
                  np.array((-127.916, 592.616, 5)),     # Top Locator (PL03)
                  np.array((0, 3, 0.3)),                # Bottom Fid. (FD01)
                  np.array((131.104, 589.526, 0.3)))    # Top Fid (FFD02)

    rel_nom = [
        nom_values[1][0:2] - nom_values[4][0:2],  # PL01-FD01
        nom_values[1][0:2] - nom_values[5][0:2],  # PL01-FD02
        nom_values[4][0:2] - nom_values[5][0:2],  # FD01-FD02
    ]
    deltas = []
    factor = 1.0
    if nom_values[2][0] * positions[1, 0] < 0:
        factor = -1

    delta_pos = []
    for i, val in enumerate(nom_values):
        if val is None:
            continue

        xxx = positions[i-1, :]
        xxx[0] *= factor
        dt = val - xxx
        dt_abs = np.sqrt(dt[0]**2+dt[1]**2)
        if i != 4:
            delta_pos.append(dt)

        row = [xxx[0], xxx[1], xxx[2], abs(dt[0]), abs(dt[1]), dt_abs, dt[2]]
        deltas.append(row)

    rel_pos = [
        np.array([deltas[0][0]-deltas[3][0], deltas[0][1]-deltas[3][1]]),  # PL01-FD01
        np.array([deltas[0][0]-deltas[4][0], deltas[0][1]-deltas[4][1]]),  # PL01-FD02
        np.array([deltas[3][0]-deltas[4][0], deltas[3][1]-deltas[4][1]]),  # FD01-FD02
    ]
    outDB["LOCATION_DELTA"] = dict(zip(key_delta, [v[0:2].tolist() for v in delta_pos]))
    outDB["REL_POS_DELTA"] = dict(zip(key_rel_pos, [(rel_nom[i] - rel_pos[i]).tolist() for i in range(3)]))
    outDB["FD01_DIAM"] = deltas[3][2]
    outDB["FD02_DIAM"] = deltas[4][2]
    outDB["CHECK_BOT_LOC_DIAM"] = deltas[0][6]
    outDB["CHECK_OVERSIZE_LOC_DIAM"] = deltas[2][6]
    outDB["CHECK_SLOT_LOC_DIAM"] = deltas[1][6]

    nPL1 = np.linalg.norm(nom_values[1][0:2] - nom_values[4][0:2])
    nPL2 = np.linalg.norm(nom_values[2][0:2] - nom_values[5][0:2])

    dPL1 = np.linalg.norm(positions[0, 0:2] - positions[3, 0:2])
    dPL2 = np.linalg.norm(positions[1, 0:2] - positions[4, 0:2])
    deltaPL1 = (nPL1-dPL1)
    deltaPL2 = (nPL2-dPL2)
    fPL1 = "PASSED" if abs(deltaPL1) <= 0.075 else "FAILED"
    fPL2 = "PASSED" if abs(deltaPL2) <= 0.075 else "FAILED"

    for key, val in outDB["REL_POS_DELTA"].items():
        deltaPL = np.linalg.norm(val)
        fPL = "PASSED" if abs(deltaPL) <= 0.075 else "FAILED"
        print("Distance {}: {:.3f} mm ({})".format(key, deltaPL, fPL))

    if document:
        document.add_heading('Position of Locking Points and Fiducials', level=1)
        txt = """Position of locators and deviation from nominal positions. \
                 The table below shows the nominal positions."""
        document.add_paragraph(re.sub(' +', ' ', txt))
        table = document.insert_table(rows=6, cols=4, caption="Nominal Position of Locking Points and fiducials.")
        table.style = document.styles['Table Grid']

        header = ("", "X(mm)", "Y (mm)", "∅ (mm)")
        for i, C in enumerate(header):
            table.rows[0].cells[i].text = C

        items = ("", "Bottom Loc. (PL01)", "Top Slot (PL02)",
                 "Top Loc. (PL03)", "Bottom Fid. (FD01)", "Top Fid. (FD02)")
        for i, C in enumerate(items):
            table.rows[i].cells[0].text = C
            if nom_values[i] is not None:
                for j, v in enumerate(nom_values[i]):
                    table.rows[i].cells[j+1].text = "{:.3f}".format(v)

        document.add_paragraph("\nThe table below shows the measured positions and the actual deviations from nominal.")
        table = document.insert_table(rows=6, cols=8, caption="Measured position of Locking Points and fiducials.")
        table.style = document.styles['Table Grid']

        header = ("", "X(mm)", "Y (mm)", "∅ (µm)", "ΔX (µm)", "ΔY (µm)", "|Δ| (µm)", "Δ∅ (µm)")
        for i, C in enumerate(header):
            table.rows[0].cells[i].text = C

        items = ("", "PL01", "PL02", "PL03", "FD01", "FD02")
        for i, C in enumerate(items):
            table.rows[i].cells[0].text = C
            if i:
                for j, v in enumerate(deltas[i-1]):
                    table.rows[i].cells[j+1].text = "{:.3f}".format(v)

        document.add_paragraph("")
        for key, val in outDB["REL_POS_DELTA"].items():
            deltaPL = np.linalg.norm(val)
            fPL = "PASSED" if abs(deltaPL) <= 0.075 else "FAILED"
            document.add_paragraph("Distance {}: {:.3f} mm ({})".format(key, deltaPL, fPL))

    return outDB


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--prefix", dest='prefix', default=None)
    parser.add_argument("--save", dest='save', action="store_true", default=False)
    parser.add_argument("--Z-plane", dest='zplane', type=float,
                        default=-0.45, help="Estimated value plate Z plane")
    parser.add_argument("--W-plane", dest='splane', type=float,
                        default=0.2, help="Estimated width in Z pf points in plale")
    parser.add_argument("--out", dest="out", default="locking_points.docx",
                        type=str, help="The output fiel name")
    parser.add_argument("--title", dest="title", default=None,
                        type=str, help="Document title")
    parser.add_argument("--nbins", dest="nbins", default=50,
                        type=int, help="Number of bins")

    # This is to convert a CMM file
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--type", default="Punto", help="The class to select")

    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    analyze_locking_points(options.files[0], options)
    plt.show()
