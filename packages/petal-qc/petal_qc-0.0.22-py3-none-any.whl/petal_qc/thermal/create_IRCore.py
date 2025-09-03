#!/usr/bin/env python3
"""Create IRCore object from file."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import dateutil
import numpy as np
import matplotlib.pyplot as plt

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.thermal import IRBFile
from petal_qc.thermal import IRCore
from petal_qc.thermal import IRPetal
from petal_qc.thermal import Petal_IR_Analysis
from petal_qc.thermal import PipeFit, PipeIterFit
from petal_qc.thermal.PetalColorMaps import HighContrast
from petal_qc.thermal.IRDataGetter import IRDataGetter
from petal_qc.thermal.IRPetalParam import IRPetalParam
from petal_qc.utils.readGraphana import ReadGraphana
from petal_qc.utils.utils import output_folder



def get_db_date(timestamp=None):
    """Convert a date string into the expected DB format.

    Args:
    ----
        timestamp: A date in string format

    """
    def date2string(the_date):
        out = the_date.isoformat(timespec='milliseconds')
        if out[-1] not in ['zZ']:
            out += 'Z'

        return out
        # return the_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    out = None
    if timestamp is None:
        out = date2string(datetime.now())
    elif isinstance(timestamp, datetime):
        out = date2string(timestamp)
    else:
        try:
            this_date = dateutil.parser.parse(timestamp)
            out = date2string(this_date)
        except Exception:
            out = ""

    return out


__figures__ = {}
def get_IRcore_plots():
    """Return global list of figures."""
    return __figures__

def clean_figures():
    """Clean existingfigures."""
    global __figures__
    for key, fig in __figures__.items():
        fig.clear()
        plt.close(fig)

    plt.close("all")
    __figures__ = {}

def get_inlet_temp(irbf, param):
    """Gets the value of the inlet temperature from Graphana."""

    print("# Getting the Inlet temperature. Contacting Graphana...")
    out = -9999
    getter = IRDataGetter.factory(param.institute, param)

    # TODO: get the server from thhe options
    server = None
    if param.graphana is not None:
        server = param.graphana
    else:
        server = os.getenv("GRAFANA_SERVER")

    if server is None:
        DB = ReadGraphana()
    else:
        print("Connecting to Graphana server {}".format(server))
        DB = ReadGraphana(server)

    frames = getter.get_analysis_frame(irbf)
    the_time = frames[0].timestamp
    try:
        X, val = DB.get_temperature(the_time, 5)
        for x, y in zip(X, val):
            print("{} - {:.1f}".format(x, y))

        imin = np.argmin(val)
        out = val[imin]
        print("{}: T_co2 = {:.1f}".format(X[imin], out))

    except ValueError:
        out = -9999

    return out

def create_IR_core(options):
    """Entry point."""
    global __figures__
    clean_figures()

    # Obtain the Data getter.
    try:
        getter = IRDataGetter.factory(options.institute, options)

    except NotImplementedError:
        print("*** Invalid institute name. ***")
        return None

    # Open the sequence file
    print("## ", options.files)
    irbf = IRBFile.open_file(options.files)
    if irbf is None:
        print("Could not fine input file: {}".format(options.files))
        return

    if options.tco2 <= -999:
        out = get_inlet_temp(irbf, options)
        if out <= -999:
            print("### Cannot get Tcos. Setting to default.")
            P = IRPetalParam()
            out = P.tco2

        options.tco2 = out

    # Set parameters from command line
    params = IRPetal.IRPetalParam(options)
    params.debug = False

    # FInd first image below the threshold or the corresponding frame
    # We will use the pipe obtained from here as the reference
    # for the next
    try:
        print("Get the reference image.")
        min_T, i_min, values = getter.find_reference_image(irbf, params.thrs, nframes=10)
        print("Image size: {} x {}".format(values[0].shape[0], values[0].shape[1]))

        if options.debug or options.report:
            fig, ax = Petal_IR_Analysis.show_2D_image(values, show_fig=False)
            __figures__["original"] = fig

    except LookupError as e:
        print(e)
        sys.exit()

    # Get the pipes
    print("Get the pipes.")
    pipes = getter.extract_pipe_path(values, params)
    npipes = len(pipes)
    transforms = [None, None]
    fitter = [None, None]
    sensors = [None, None]

    print("Fit pipes and find sensor positions.")
    ordered_pipes = [None, None]
    pipe_order = [0, 0]
    all_3d_points = IRPetal.get_all_3d_points()
    core_images = IRPetal.get_last_images()
    for i in range(2):
        pipe_type = PipeFit.PipeFit.guess_pipe_type(pipes[i])
        pipe_order[i] = pipe_type
        if options.save_pipes:
            prfx = options.alias if len(options.alias)>0 else "pipe"
            ofile = output_folder(options.folder, "{}_pipe_{}.txt".format(prfx, pipe_type))
            np.savetxt(ofile, pipes[i])

        #PF = PipeFit.PipeFit(pipe_type)
        #R = PF.fit_ex(pipes[i], factor=getter.factor)
        
        iPF = PipeIterFit.PipeIterFit(pipes[i])
        PF = iPF.PF
        R = iPF.fit(factor=getter.factor, threshold=12*getter.factor)
        
        if options.debug or options.report:
            _X = all_3d_points[i][:, 0]
            _Y = all_3d_points[i][:, 1]
            _Z = all_3d_points[i][:, 2]

            fig, _ = PF.plot(show_fig=False)
            __figures__["fit_{}".format(i)] = fig


            shape = core_images[i].shape
            fig_size = [6.4, 0]
            factor = fig_size[0]/shape[1]
            fig_size[1] = shape[0] * factor
            fig, ax = plt.subplots(1, 1, tight_layout=True, figsize=fig_size)
            ax.imshow(core_images[i], origin='lower', cmap=HighContrast.reversed())
            ax.plot(_X, _Y, 'o-', linewidth=1, markersize=10)
            for s in PF.sensors:
                o = PF.transform_inv(s, R)
                ax.plot(o[:,0], o[:, 1], linewidth=2, color="black")

            __figures__["sensors_{}".format(pipe_type)] = fig

            fig = plt.figure(tight_layout=True, figsize=(7, 6))
            fig.subplots_adjust(left=0.0, right=1.)

            ax = fig.add_subplot(1, 1, 1)
            sct = ax.scatter(_X, _Y, c=_Z, marker='o', cmap=plt.cm.jet)
            fig.colorbar(sct, pad=0.01, aspect=10)
            __figures__["pipe_path_{}".format(i)] = fig

        transforms[pipe_type] = R
        fitter[pipe_type] = PF



        # Reorder points in pipe contour so that first point corresponds to
        # the U-shape pipe minimum.
        pipes[i] = IRPetal.reorder_pipe_points(pipes[i], pipe_type, R)
        if ordered_pipes[pipe_type] is not None:
            print("### Expect problems. 2 pipes of same type")

        ordered_pipes[pipe_type] = pipes[i]

        # Now make the inverse transform of the area of sernsors and EoS
        S = []
        for s in PF.sensors:
            o = PF.transform_inv(s, R)
            S.append(o)

        sensors[pipe_type] = S

    pipes = ordered_pipes
    deltaT = 0.0
    if options.tco2 != 0:
        deltaT = -35.0 - options.tco2

    # get the framea from where extract the data
    # reorder if needed
    frames = getter.get_analysis_frame(irbf)
    if pipe_order[0]:
        tmp = frames[0]
        frames[0] = frames[1]
        frames[1] = tmp

    values = getter.get_IR_data(frames, rotate=True)
    results = getter.analyze_IR_image(values, pipes, sensors, 0, params)
    if options.debug:
        fig, ax = plt.subplots(2, 2, tight_layout=True)
        ax[0][0].set_title("Side 0")
        ax[0][1].set_title("Side 1")

        for iside in range(2):
            R = results[iside]
            ax[0][iside].plot(R.path_length, R.path_temp)
            ax[1][iside].plot([x for x in range(10)], R.sensor_avg)

    core = IRCore.IRCore(options.SN, options.alias, results, params)
    core.set_files(options.files)
    core.date = get_db_date(frames[0].timestamp)
    core.institute = params.institute
    core.apply_deltaT(deltaT)

    # Check if we are given an output folder
    ofile = output_folder(options.folder, options.out)
    with open(ofile, "w", encoding="utf-8") as ofile:
        core.to_json(ofile)

    if options.debug:
        plt.show()

    return core


def main():
    """Main entry."""
    from argparse import ArgumentParser

    # Argument parser
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--nframe", type=int, default=-1, help="Number of frames. (negative means all.")
    parser.add_argument('--frame', type=int, default=-1, help="First frame to start.")
    parser.add_argument("--out", default="core.json", help="Output file name")
    parser.add_argument("--alias", default="", help="Alias")
    parser.add_argument("--SN", default="", help="serial number")
    parser.add_argument("--folder", default=None, help="Folder to store output files. Superseeds folder in --out")

    IRPetalParam.add_parameters(parser)

    options = parser.parse_args()
    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    create_IR_core(options)

if __name__ == "__main__":
    main()
