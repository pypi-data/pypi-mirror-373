#!/usr/bin/env python3
"""Show data file."""
import sys
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from petal_qc.metrology import DataFile
from petal_qc.utils.Geometry import fit_plane
from petal_qc.utils.Geometry import project_to_plane
from petal_qc.utils.Geometry import remove_outliers_indx


DEFAULT_VIEW, TOP_VIEW, FRONT_VIEW = range(0, 3)


def show_data(data, title, view=DEFAULT_VIEW, nbins=50, out_file=None, log_axis=False, surf=False, color_bar=True):
    """Show the data.

    PLot a 3D scatter and the Z distribution.
    """
    fig = plt.figure(figsize=[10, 5])
    fig.suptitle(title)
    fig.subplots_adjust(left=0.0, right=1.)
    ax = fig.add_subplot(1, 2, 1, projection='3d')
    if view == TOP_VIEW:
        ax.view_init(azim=-90, elev=90)
    elif view == FRONT_VIEW:
        ax.view_init(azim=-90, elev=0)

    Z = data[:, 2]
    if surf:
        _surf = ax.plot_trisurf(data[:, 0], data[:, 1], Z, cmap=plt.cm.jet, edgecolor="black", linewidths=0.2)   
    else:
        _surf = ax.scatter(data[:, 0], data[:, 1], Z, c=Z, marker='.', cmap=plt.cm.jet)
    
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    
    if color_bar:
        fig.colorbar(_surf, shrink=0.5, aspect=5, location="left")

    ax = fig.add_subplot(1, 2, 2)
    n, *_ = ax.hist(Z, bins=nbins)
    if log_axis:
        plt.yscale("log")

    if out_file is not None:
        plt.savefig(out_file, dpi=300)

    return fig


def show_data_file(fnam, options):
    """Plot points in data file."""
    data = DataFile.read(fnam, label=options.label, type=options.type)

    if options.outliers:
        indx = remove_outliers_indx(data[:, 2])
        data = data[indx]

    if options.fit_plane:
        data, *_ = fit_plane(data)

    # the plane
    if options.zplane != sys.float_info.max:
        zd = data[:, 2]
        cond = np.where((abs(zd-options.zplane) < options.splane))
        plane, V, M, L = fit_plane(data[cond])
        data = project_to_plane(data, V, M)
        show_data(plane, "{} - plane".format(fnam.name))

    show_data(data, fnam.name, log_axis=options.log)

    if options.fit:
        zd = data[:, 2]
        indx = np.where((abs(zd-options.zfit) < options.sfit))[0]
        Y = data[indx, 2]
        X = data[indx, 0:2]
        coeff = np.polynomial.chebyshev.chebfit(X, Y, 2)
        print(coeff)

    plt.show()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--Z-plane", dest='zplane', type=float,
                        default=sys.float_info.max, help="Estimated value plate Z plane")
    parser.add_argument("--W-plane", dest='splane', type=float,
                        default=0.2, help="Estimated width in Z pf points in plale")
    parser.add_argument("--fit", dest='fit', action="store_true", default=False)
    parser.add_argument("--fit-plane", dest='fit_plane', action="store_true", default=False,
                        help="If set, make first a plane fit projection.")
    parser.add_argument("--log", dest='log', action="store_true", default=False, help="Log Y axis")

    parser.add_argument("--Z-fit", dest='zfit', type=float,
                        default=sys.float_info.max, help="Estimated value plate Z plane")
    parser.add_argument("--W-fit", dest='sfit', type=float,
                        default=0.2, help="Estimated width in Z pf points in plale")
    parser.add_argument("--remove-outliers", dest="outliers",
                        help="Remove Outliers", default=False, action="store_true")

    # This is to convert a CMM file
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--type", default="Punto", help="The class to select")

    options = parser.parse_args()
    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    fnam = Path(options.files[0]).expanduser().resolve()
    show_data_file(fnam, options)
