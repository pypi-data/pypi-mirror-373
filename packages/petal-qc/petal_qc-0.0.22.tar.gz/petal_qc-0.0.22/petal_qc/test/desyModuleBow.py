#!/usr/bin/env python3
"""Get module bow from desy metrology files"""
import sys
import re
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg as linalg


from petal_qc.utils.all_files import all_files
from petal_qc.metrology import DataFile
from petal_qc.metrology import DataFile
from petal_qc.utils.Geometry import fit_plane
from petal_qc.utils.Geometry import project_to_plane
from petal_qc.utils.Geometry import remove_outliers_indx


rgx = "serialNo =\\s+([A-Z0-9]+)"
serial_no = re.compile(rgx)

mtype = re.compile("Project Name:\\s+([A-Za-z0-9]+)_bow")


def get_array_range(A):
    """Gets mean and range of given array."""
    avg = np.mean(A)
    imin = np.argmin(A)
    vmin = A[imin]
    imax = np.argmax(A)
    vmax = A[imax]
    stdv = np.std(A)
    return avg, stdv, [vmin, vmax], [imin, imax]



def create_bow_figure(SN, mtype, pout, width) -> plt.Figure:
    """Create the sensor bow figure.

    Args:
        options: Program options.
        pout: set of points
        width: the actual bow.

    Returns:
        plt.Figure: The bow figure.
    """
    fig_bow, ax = plt.subplots(subplot_kw={'projection': '3d'})
    fig_bow.suptitle(r"{}_{} - Sensor bow {:.1f} $\mu$m".format(SN, mtype, width))

    zplt = 1000*pout[:, 2]
    # surf = ax.plot_trisurf(pout[:, 0], pout[:, 1], zplt, cmap=plt.cm.jet, edgecolor="black", linewidths=0.2)
    surf = ax.scatter(pout[:, 0], pout[:, 1], zplt, c=zplt, marker="o", edgecolor='none')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    cbar = fig_bow.colorbar(surf, shrink=0.5, aspect=5, location="left")
    cbar.set_label(r"Z ($\mu$m)")
    return fig_bow


def module_bow(ifile):
    """Compute module bow."""
    SN = None
    mod_type = None
    print(Path(ifile).name)
    with open(ifile, "r", encoding="utf-8") as fin:
        ss = fin.read()
        mtx = serial_no.search(ss)
        if mtx:
            SN = mtx.group(1)
            
        mtp = mtype.search(ss)
        if mtp:
            mod_type = mtp.group(1)

    if SN is None:
        return None, None, None
    
    print("{} - {}".format(SN, mod_type))
    
    data = DataFile.read(ifile, "(Bow|Sensor)")
    if len(data) == 0:
        return None, None, None
    
    # Try to remove locator points and get the plane
    indx = remove_outliers_indx(data[:, 2])
    M, TM, *_ = fit_plane(data[indx], use_average=False)

    # project all data to the plane
    Zmean = np.mean(M[:, 2])
    M[:, 2] -= Zmean
    
    mean, stdev, rng, irng = get_array_range(M[:, 2])
    width = 1000*(rng[1]-rng[0])
    
    # Check which one is closest to the center
    min2center = linalg.norm(M[irng[0], 0:2])
    max2center = linalg.norm(M[irng[1], 0:2])
    # If center above the top, bow negative
    if max2center < min2center:
        width = -width

    print("Sensor bow\nAverage: {:.1f} min {:.1f} max {:.1f} rng {:.1f}\n".format(
        mean, 1000*rng[0], 1000*rng[1], width))

    fig_bow = create_bow_figure(SN, mod_type, M, width)
    fig_bow.savefig("{}-{}-bow.png".format(SN, mod_type), dpi=300)
    plt.close(fig_bow)
    del fig_bow
    return SN, mod_type, width


def main(folder):
    """Main entry"""
    fout = open("module-bow.txt", "w", encoding="utf-8")
    for fnam in all_files(folder, "*.txt"):
        SN, mod_type, width = module_bow(fnam)
        if SN:
            fout.write("{}-{} : {:.3f}\n".format(SN, mod_type, width))
            
    fout.close()

if __name__ == "__main__":
    main("/Users/lacasta/Downloads/InterposerPetal")
    #main("/Users/lacasta/Downloads/kkdvk")