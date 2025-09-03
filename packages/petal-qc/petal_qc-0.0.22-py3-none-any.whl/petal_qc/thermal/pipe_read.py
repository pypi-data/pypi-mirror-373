#!/usr/bin/env python3
"""Read the real pipe and create the pipe contour to compare with.

It reads PNG files produced from the petal 3D CAD model and extracts the pipe
path and the sensor areas. It stores all this information in files that are
later read by PipeFit.

To create the files one needs to run the script twice, one for the front side
(--front) and anther for the back side (--back).

"""
import random
import sys
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import skimage

from petal_qc.thermal.contours import adjust_contour
from petal_qc.thermal.contours import contour_simplify
from petal_qc.thermal.contours import find_closest

script_path = Path(__file__).absolute().parent


def crange(start, end, modulo):
    """Circular range.

    Args:
    ----
        start: Start
        end: End
        modulo: Max value

    Yields
    ------
        int: the following value

    """
    if start > end:
        while start < modulo:
            yield start
            start += 1
        start = 0

    while start < end:
        yield start
        start += 1


def get_pipe_path(im, P1_i, P2_i, debug=False):
    """Find pipe path and save to file.

    Given the inlet and outlet point, creates the path of the pipe.

    Args:
    ----
        im: THe image with the pipe
        P1_i: Starting point
        P2_i: End point
        debug: show stuff

    """
    contours = skimage.measure.find_contours(im)
    pipe = adjust_contour(np.array(contours[0]))

    npts = len(pipe)
    i1, P1 = find_closest(P1_i[0], P1_i[1], pipe, True)
    i2, P2 = find_closest(P2_i[0], P2_i[1], pipe, True)

    indx = list(crange(i1, i2, npts))
    inner = pipe[indx, :]
    linner = len(inner)

    indx = list(crange(i2, i1, npts))
    outer = np.flipud(pipe[indx, :])
    louter = len(outer)

    if linner > louter:
        indx = random.sample(range(0, linner), linner - louter)
        inner = np.delete(inner, indx, 0)
    else:
        indx = random.sample(range(0, louter), louter - linner)
        outer = np.delete(outer, indx, 0)

    center = (inner + outer)/2.0

    small_center = contour_simplify(center - P1, 0.5)
    print("original len {}, small len {}".format(len(center), len(small_center)))

    if debug:
        fig, ax = plt.subplots(1, 2, tight_layout=True)
        ax[0].plot(inner[:, 0], inner[:, 1])
        ax[0].plot(outer[:, 0], outer[:, 1])
        ax[0].plot(center[:, 0], center[:, 1])
        ax[1].plot(center[:, 0], center[:, 1])
        ax[1].plot(small_center[:, 0], small_center[:, 1])

    return small_center, P1


def get_sensor_area(ims, P1, debug=False):
    """Find sensor area."""
    if debug:
        fig, ax = plt.subplots(1, 1, tight_layout=True)

    contours = skimage.measure.find_contours(ims)

    ncontours = len(contours)
    sensors = []
    for i in range(ncontours):
        sensor = adjust_contour(contours[i]) - P1
        sensor = contour_simplify(sensor, 1)
        sensors.append(sensor)
        if debug:
            ax.plot(sensor[:, 0], sensor[:, 1])

    return sensors


def main(opts):
    """Main entry."""
    global script_path
    front = opts.front
    if opts.folder:
        folder = Path(opts.folder).expanduser().absolute()
        if folder.exists():
            script_path = folder
        else:
            print("Folder {} does not exist.".format(opts.folder))
            sys.exit()

    if front:
        in_file = "pipe-front.png"
        in_sensors = "pipe-front-sensors-only.png"
        out_file = "pipe_front.npz"
        P1_i = [608, 817]      # [602.9, 779.5]   # [568.915, 768.52]
        P2_i = [593.5, 818.7]  # [588.7, 781.0]  # [582.9, 766.7]

    else:
        in_file = "pipe-back.png"
        in_sensors = "pipe-back-sensors-only.png"
        out_file = "pipe_back.npz"
        P1_i = [251.8, 817.9]  # [256.0, 779.0]
        P2_i = [266.1, 818.3]  # [270.5, 781.2]

    # Get the pipe
    im = skimage.io.imread(script_path.joinpath(in_file), as_gray=True)
    im = np.flipud(im)

    pipe, P1 = get_pipe_path(im, P1_i, P2_i, debug=opts.debug)

    # Now gethte sensors
    ims = skimage.io.imread(script_path.joinpath(in_sensors), as_gray=True)
    ims = np.flipud(ims)

    sensors = get_sensor_area(ims, P1, debug=opts.debug)

    # Save stuff
    np.savez_compressed(out_file, pipe=pipe, *sensors)

    fig, ax = plt.subplots(1, 1, tight_layout=True)
    ax.plot(pipe[:, 0], pipe[:, 1])

    for S in sensors:
        ax.plot(S[:, 0], S[:, 1])

    plt.show()


if __name__ == "__main__":
    parser = ArgumentParser(description="PipeContour")
    parser.add_argument("--folder", default=None, help="Folder to find the pictures.")
    parser.add_argument("--front", action="store_true", dest='front', default=True, help="Front side")
    parser.add_argument("--back", action="store_false", dest='front', help="Back side")
    parser.add_argument("--debug", action="store_true", default=False, help="Debug.")

    opts = parser.parse_args()

    main(opts)
