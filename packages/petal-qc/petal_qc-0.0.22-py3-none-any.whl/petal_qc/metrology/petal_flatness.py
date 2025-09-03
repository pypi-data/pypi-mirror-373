#!/usr/bin/env python3
"""Petal flatness.

This file contains the methods to produce the metrology reports of the petal
core metrology survey.

"""
import math
import os
import sys
import tempfile
import traceback
from argparse import Action
from argparse import ArgumentParser

import petal_qc.utils.docx_utils as docx_utils
import matplotlib.pyplot as plt
import numpy as np

from petal_qc.metrology import DataFile
from petal_qc.utils.fit_utils import draw_best_fit
from petal_qc.utils.fit_utils import fit_gaussian
from petal_qc.utils.Geometry import fit_plane
from petal_qc.utils.Geometry import flatness_conhull, flatness_LSPL
from petal_qc.utils.Geometry import project_to_plane

from petal_qc.metrology.analyze_locking_points import analyze_locking_point_data, locking_point_positions
from petal_qc.metrology.analyze_locking_points import remove_outliers
from petal_qc.metrology.Cluster import cluster_points
from petal_qc.metrology.show_data_file import show_data, TOP_VIEW

figure_width = 14

def plot_sensor(Spoints, ax, marker='o', cmap='magma'):
    """Plot the points given in a scatter plot."""
    ax.scatter(Spoints[:, 0], Spoints[:, 1], Spoints[:, 2],
               c=Spoints[:, 2], cmap=cmap, marker=marker,
               linewidth=0.5)


def sensor_flatness(data, name="Sensor", prefix=None, nbins=50, do_fit=False, do_3d=False, save=False, document=None):
    """Show Sensor flatness plot.

    Args:
    ----
        data: the data array
        name: name of the sensor
        nbins: number of bins in histogram
        prefix: prefix to be added to the name if not None.
        save: Save plot if True
        document: insert figure in document if not None.

    """
    width = 0.0
    ncol = 1
    out, V, M, L = fit_plane(data)
    Z = out[:, 2]

    fig = plt.figure(figsize=[12, 6])
    fig.suptitle(name)
    fig.subplots_adjust(left=0.05, right=0.95)
    if do_3d:
        ncol = 2
        ax = fig.add_subplot(1, 2, 1, projection='3d')
        # ax.view_init(azim=-90, elev=90)
        ax.set_title("plane of min Z variance")
        surf = ax.scatter(out[:, 0], out[:, 1], Z, c=Z, marker='.', cmap=plt.cm.jet)
        # surf = ax.plot_trisurf(out[:, 0], out[:, 1], Z, cmap=plt.cm.jet, edgecolor="black", linewidths=0.2)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        fig.colorbar(surf, shrink=0.5, aspect=5, location='left')

    ax = fig.add_subplot(1, ncol, ncol)
    n, bins, *_ = ax.hist(Z, bins=nbins)
    if do_fit:
        step = 0.5 * (bins[1] - bins[0])
        X = bins[:-1] + step
        result, legend = fit_gaussian(n, X, np.mean(Z), width=np.std(Z))
        ax.legend([legend], loc=1)
        draw_best_fit(ax, result, bins)
        rms = result.best_values['sigma']
        center = result.best_values['center']
        v1 = center - 3.5*rms
        v2 = center + 3.5*rms
        width = v2 - v1
        ax.axvspan(v1, v2, alpha=0.20, facecolor='g')
        ax.set_title("Z dispersion: {:.3f}".format(width))
        # plt.yscale('log')
        print("{}: rms: {:.3f} 7xRMS {:.3f}".format(name, rms, v2-v1))

    out_file = None
    if save is True:
        if prefix is None:
            out_file = "{}.png".format(name)
        else:
            out_file = "{}-{}.png".format(prefix, name)

        plt.savefig(out_file, dpi=300)

    if document:
        document.add_picture(fig, True, figure_width, caption="{} planarity.".format(name))
        plt.close(fig)

    return width


def petal_flatness(orig_data, options, document=None):
    """Compute the petal flatness in the different sensor areas.

    Args:
    ----
        filename: CSV file with metrology values array([npoints, 3])
        options: parser options (see entry)
        document: docx document.

    """
    # SHow raw data
    show_petal_points(orig_data, "Original Input Data")

    # Try to remove locator points and get the plane
    indx = remove_outliers(orig_data[:, 2])
    M, TM, avg, *_ = fit_plane(orig_data[indx], use_average=7)

    # project all data to the plane
    M = project_to_plane(orig_data, TM, [0., 0., avg[2]])
    Zmean = np.mean(M[indx, 2])
    M[:, 2] -= Zmean
    Z = M[:, 2]

    show_petal_points(M, "On Petal plane.")

    # group points by sensors.
    sensor_dict = {0: "R0", 10: "R1", 20: "R2", 30: "R3_0", 31: "R3_1", 40: "R4_0", 41: "R4_1", 50: "R5_0", 51: "R5_1"}
    sensors, *_ = group_by_sensors(M, options.is_front, True)
    all_data = np.vstack(list(sensors.values()))

    fig = show_data(all_data, "All points in core", view=TOP_VIEW, surf=False)

    if document:
        document.add_heading('All points', level=1)
        document.add_picture(fig, True, 14, caption="All points in Petal.")
        plt.close(fig)

    #
    # Add the tables to the document
    #
    # flatness_func = flatness_conhull
    flatness_func = flatness_LSPL
    F = {}
    for key, val in sensors.items():
        try:
            F[key] = flatness_func(val)
        except ValueError as E:
            print("*** Error: Petal flatnes: key {}\n{}".format(key, E))
            print(val)
            return TM, avg, Zmean, [-9999, -9999]

    flatness_all_sensor_area = flatness_func(all_data)

    outF = [flatness_all_sensor_area, ]
    print("Is front ? {}".format(options.is_front))
    print("Flatness:")
    for i in range(6):
        if i < 3:
            id = 10*i
            lbl = sensor_dict[id]
            print("{}: {:.3f}".format(lbl, F[id]))
            outF.append(F[id])
        else:
            ids = [10*i, 10*i+1]
            lbls = [sensor_dict[i] for i in ids]
            values = [F[id] for id in ids]
            outF.extend(values)
            print("{}: {:.3f}  {}: {:.3f}".format(lbls[0], values[0], lbls[1], values[1]))

    print("All sensor area: {:.3f}".format(1000*flatness_all_sensor_area))

    # Add table in document
    if document:
        document.add_heading('Petal flatness (LSPL)', level=1)
        table = document.insert_table(rows=1, cols=3, caption="Flatness (LSPL)")
        table.style = document.styles['Table Grid']

        # populate header row --------
        heading_cells = table.rows[0].cells
        heading_cells[0].text = ""
        heading_cells[1].text = "Flatness (µm)"
        a = table.cell(0, 1)
        b = table.cell(0, 2)
        A = a.merge(b)

        heading_cells = table.add_row().cells
        heading_cells[0].text = "Area"
        heading_cells[1].text = "S0"
        heading_cells[2].text = "S1"

        for i in range(6):
            cell = table.add_row().cells
            cell[0].text = "R{}".format(i)
            cell[1].text = "{:.4f}".format(F[10*i]*1000)
            if i > 2:
                cell[2].text = "{:.4f}".format(F[10*i+1]*1000)

        # add allsensor area
        cell = table.add_row().cells
        cell[0].text = "All sensor area"
        cell[1].text = "{:.4f}".format(flatness_all_sensor_area*1000)

    return TM, avg, Zmean, outF


def show_petal_points(orig_data, title):
    """Show the given points."""
    fig = plt.figure(figsize=[5, 5])
    fig.suptitle(title)
    ax = fig.add_subplot(2, 1, 1, projection='3d')
    ax.view_init(azim=-90, elev=90)
    Z = orig_data[:, 2]
    ax.scatter(orig_data[:, 0], orig_data[:, 1], Z, c=Z, cmap='viridis', linewidth=0.5)
    ax = fig.add_subplot(2, 1, 2)
    n, bins, *_ = ax.hist(Z, bins=100)
    plt.yscale('log')


sensorR = (
    (384.5, 488.423), (489.823, 574.194), (575.594, 637.209),
    (638.609, 755.501), (756.901, 866.062), (867.462, 967.785)
)


def get_iring(P, is_front):
    """REturn ring number

    Args:
    ----
        P (3D point): A 3D point o nthe petal surface
        is_front: True if front side. Otehrwse false.

    Returns:
        int: The ring (10*iring + side)

    """
    R = np.sqrt(np.sum(P[0:2]**2))
    i = 0
    for ri, ro in sensorR:
        if ri <= R and R <= ro:
            if i < 3:
                side = 0
            else:
                side = 0 if P[0] > 0 else 1

            return 10*i + side

        i = i + 1

    return -1


def group_by_sensors(Min, is_front=True, no_outliers=False):
    """Groups data points by sensors."""
    # Now move in Y to be on the ATLAS reference
    M = np.array(Min)
    M[:, 1] = M[:, 1] + 382

    other = []
    sensors = {}

    for i in range(0, M.shape[0]):
        P = M[i, :]
        iring = get_iring(P, is_front)
        if iring < 0:
            other.append(P)

        else:
            sensors.setdefault(iring, []).append(P)

    if no_outliers:
        for key, val in sensors.items():
            points = np.vstack(val)
            indx = remove_outliers(points[:, 2])
            sensors[key] = points[indx, :]

    return sensors, np.array(other)


def do_petal_flatness(filename, options):
    """Calls petal_flatness

    Args:
    ----
        filename (): Data file name
        options (): Options
    """
    orig_data = DataFile.read(filename, label=options.label, type=options.type)
    if orig_data is None:
        print("Input file not found.")
        return

    # Open the output document if a title is given in the options.
    document = docx_utils.Document()
    document.add_page_numbers()
    document.styles['Normal'].font.name = "Calibri"
    if options.title:
        document.add_heading(options.title, 0)

    petal_flatness(orig_data, options, document=document)

    document.save(options.out)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--prefix", dest='prefix', default=None)
    parser.add_argument("--save", dest='save', action="store_true", default=False)
    parser.add_argument("--front", dest='is_front', action="store_true", default=True)
    parser.add_argument("--back", dest='is_front', action="store_false", default=True)
    parser.add_argument("--out", dest="out", default="petal_flatness.docx",
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

    try:
        do_petal_flatness(options.files[0], options)

    except Exception:
        print(traceback.format_exc())

    plt.show()
