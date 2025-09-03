#!/usr/bin/env python3
"""Test Paralelism."""
import sys
import traceback
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from petal_qc.metrology import DataFile
from petal_qc.metrology.analyze_locking_points import analyze_locking_point_data


def do_paralelism(ifile, options):
    """Calculate paralelism locator-core

    Args:
    ----
        files (): Input files
        options (): Options.

    """
    ifile = Path(ifile).expanduser().resolve()
    if not ifile.exists():
        print("input file {} does not exist.".format(ifile))
        return

    # Do petal flatness analysis
    Zmean = 0
    if options.desy:
        flatness_data = DataFile.read(ifile, "PetalPlane")
    else:
        flatness_data = DataFile.read(ifile, r"Punto[-|Vision-]\w", "Punto")
        Zmean = np.mean(flatness_data[:, 2])
        flatness_data -= Zmean

    # Do locator flatness analysis
    TM = None  # TODO: fix this
    if options.desy:
        locator_data = DataFile.read(ifile, ".*_FineFlatness")
    else:
        locator_data = DataFile.read(ifile, "PuntoLocator", "Punto")
        locator_data -= Zmean

    data = np.concatenate((flatness_data, locator_data))
    out = analyze_locking_point_data(data, nbins=options.nbins, cut=4, plane_fit=True)

    for key, val in out.items():
        print("{:10} -> {}".format(key, val))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--desy", dest='desy', action="store_true", default=False)
    parser.add_argument("--nbins", dest="nbins", default=25,
                        type=int, help="Number of bins")

    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    try:
        do_paralelism(options.files[0], options)
        plt.show()
        
    except Exception:
        print(traceback.format_exc())
