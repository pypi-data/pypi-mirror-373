#!/usr/bin/env python3
"""Convert IFIC raw data to CVS."""
import io
from metrology.convert_mitutoyo import mitutoyo2cvs
import matplotlib.pyplot as plt
import numpy as np

def data2cvs(ifile, options):
    """Read CMM file and convert to CSV.

    Args:
        ifile: Input file path
        options: Program options

    """
    ofiles = []
    odata = io.StringIO()
    mitutoyo2cvs(ifile, odata, r"Punto[-|Vision-]\w", "Punto")

    outfile = "{}-petal.csv".format(options.prefix)
    with open(outfile, mode='w') as f:
        f.write(odata.getvalue())

    ofiles.append(outfile)

    odata = io.StringIO()
    mitutoyo2cvs(ifile, odata, "PuntoLocator", "Punto")

    outfile = "{}-locators.csv".format(options.prefix)
    with open(outfile, mode='w') as f:
        f.write(odata.getvalue())

    ofiles.append(outfile)
    return ofiles

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--prefix", default="out", help="Output file")
    parser.add_argument("--show", action="store_true", default=False)

    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    ofiles = data2cvs(options.files, options)

    if options.show:
        for outfile in ofiles:
            x, y, z = np.loadtxt(outfile, unpack=True, skiprows=1, delimiter=',')
            fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
            surf = ax.scatter(x, y, z, c=z, marker='.', cmap=plt.cm.jet)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            fig.colorbar(surf, shrink=0.5, aspect=5, location="left")

        plt.show()