#!/usr/bin/env python3
"""Do the thermal analysis of the petal core."""
import os
import subprocess
import sys
import tempfile
from argparse import Action
from argparse import ArgumentParser
from pathlib import Path
from pathlib import PurePath

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.thermal import contours
from petal_qc.thermal import IRBFile
from petal_qc.thermal import IRPetal
from petal_qc.thermal import PipeFit
from petal_qc.thermal.Petal_IR_Analysis import show_2D_image
from petal_qc.thermal.PetalColorMaps import HighContrast

import petal_qc.utils.Progress as Progress
import petal_qc.utils.utils as utils
from petal_qc.utils.ArgParserUtils import CommaSeparatedListAction

def get_min_max(values, step=1.0):
    """Return min and max.

    The values are alined with step.

    Args:
    ----
        values: Array of values
        step (optional): The step_. Defaults to 1.0.

    Returns
    -------
        min, max.

    """
    vmax = np.amax(values)
    vmin = np.amin(values)
    ivmax = round(vmax)
    if ivmax < vmax:
        ivmax += step
        if abs(ivmax-vmax) < 0.25*step:
            ivmax += step

    ivmin = np.round(vmin)
    if ivmin > vmin:
        ivmin -= step
        if abs(ivmin-vmin) < 0.25*step:
            ivmin -= step

    return ivmin, ivmax


def find_ffmpeg():
    """Returns the path of ffmpeg."""
    folders = os.environ['PATH'].split(':')

    ffmpeg = None
    for p in folders:
        exe = Path(PurePath(p, "ffmpeg"))
        if exe.exists():
            ffmpeg = exe
            break

    if not ffmpeg:
        raise Exception("Could not find ffmpeg")

    return ffmpeg


def create_movie(template, fout):
    """Creates a movie frm a set of files.

    The name of the files should be passed as a template, ej.,

    <dir_name>/fig%3d.png

    """
    pout = utils.find_out_file_name(fout)
    ffmpeg = find_ffmpeg()

    try:
        out = subprocess.run([ffmpeg, '-r', "10", '-i', template, '-c:v', "libx264", pout],
                             capture_output=True,
                             text=True,
                             timeout=1,
                             shell=False)
        print(out)
        print("Movie is ready.")

    except subprocess.CalledProcessError as xx:
        print("Error")
        print("create_movie: error rc=%d.\n%s" % (xx.returncode, xx.output))

    except Exception as xx:
        print("Error")
        print("create_movie: error rc=%d.\n%s" % (xx.returncode, xx.output))


def show_cycle(irbf):
    """Show thermal cycle.

    Args:
    ----
        irbf: IRB file with sequence.

    """
    # Thermal cycle
    T = []
    D = []
    prg = Progress.ShowProgress(irbf.n_images(), width=20)
    prg.start()
    for i, img in enumerate(irbf.images()):
        prg.increase(1, True)
        T.append(np.min(img.image))
        D.append(img.timestamp)

    prg.stop
    fig, ax = plt.subplots(1, 1)
    ax.plot(D, T, 'o-')


def save_frame_data(the_frame, path_length, path_temp, sensor_avg, sensor_std):
    """Save the frame data.

    The input data are 2D arrays.
        i=0 corresponds to the left image
        i=1 corresponds to the right image

    Args:
    ----
        the_frame: frams index in IRBFile
        path_length: array with positions along the pipe
        path_temp: array with temperatures in path_length positions
        sensor_avg: Average T in sensor areas.
        sensor_std: Temperature std in sensor area.

    """
    onam = "pipe_temp_{}.csv".format(the_frame)
    ofile = open(onam, 'w')
    ofile.write("x, T, x, T\n")
    ll = [len(path_length[0]), len(path_length[1])]
    nitems = max(ll[0], ll[1])
    for i in range(nitems):
        for j in range(2):
            if i < ll[j]:
                ofile.write("{:.4f}, {:.4f},".format(path_length[j][i], path_temp[j][i]))
            else:
                ofile.write(",,")

        ofile.write('\n')
    ofile.close()

    onam = "sensor_temp_{}.csv".format(the_frame)
    ofile = open(onam, 'w')
    ofile.write("T, std, T, std\n")
    ll = [len(sensor_avg[0]), len(sensor_avg[1])]
    nitems = max(ll[0], ll[1])
    for i in range(nitems):
        for j in range(2):
            if i < ll[j]:
                ofile.write("{:.4f}, {:.4f},".format(sensor_avg[j][i], sensor_std[j][i]))
            else:
                ofile.write(",,")

        ofile.write('\n')
    ofile.close()


def analyze_petal(ifileS, options):
    """Main entry."""
    from IRDataGetter import IRDataGetter
    # Obtain the Data getter.
    try:
        getter = IRDataGetter.factory(options.institute, options)

    except NotImplemented:
        print("*** Invalid institute name. ***")
        return
    
    # Load parameters from IRPetalParam
    params = IRPetal.IRPetalParam(options)
    params.debug = False

    # Check if we are going to save the images
    tmp_dir = None
    if options.save_fig:
        tmp_dir = tempfile.TemporaryDirectory()

    # Open the sequence file
    irbf = IRBFile.open_file(ifileS)

    # Find first image below the threshold
    # we will use the pipe obtained from here as the reference
    # for the next
    try:
        min_T, i_min, values = getter.find_reference_image(irbf, params.thrs, nframes=2)
        print("Image size: {} x {}".format(values[0].shape[0], values[0].shape[1]))

        if options.debug:
            show_2D_image(values)

    except LookupError as e:
        print(e)
        sys.exit()

    # Get the pipes
    print("Extract pipes.")
    pipes = getter.extract_pipe_path(values, params)
    npipes = len(pipes)

    # plot pipe paths on top of image
    imgs = IRPetal.get_last_images()
    nimgs = len(imgs)
    if options.debug:
        fig, ax = plt.subplots(1, nimgs, tight_layout=True)
        if nimgs == 1:
            ax = [ax, ]

        for i, img in enumerate(imgs):
            ax[i].imshow(imgs[i], origin="lower", cmap="jet")
            ax[i].plot(pipes[i][:, 0], pipes[i][:, 1], linewidth=3, color="black")

    # We now need to fit to the reference pipes to get the proper distance along
    # the pipe.
    transforms = [None, None]
    fitter = [None, None]
    sensors = [None, None]
    ordered_pipes = [None, None]

    print("Fit pipes and find sensor positions.")
    for i in range(npipes):
        # Fit the points to the "pipes"
        pipe_type = PipeFit.PipeFit.guess_pipe_type(pipes[i])

        PF = PipeFit.PipeFit(pipe_type)
        R = PF.fit_ex(pipes[i])

        transforms[pipe_type] = R
        fitter[pipe_type] = PF

        # Reorder points in pipe contour so that first point corresponds to
        # the U-shape pipe minimum.
        pipes[i] = IRPetal.reorder_pipe_points(pipes[i], pipe_type, R)
        if ordered_pipes[pipe_type] is not None:
            print("### Expect probles. 2 pipes of sme type")

        ordered_pipes[pipe_type] = pipes[i]

        # Now make the inverse transform of the area of sernsors and EoS
        S = []
        for s in PF.sensors:
            o = PF.transform_inv(s, R)
            S.append(o)
        sensors[pipe_type] = S

    pipes = ordered_pipes
    if pipes[0] is None and pipes[1] is not None:
        pipes[0] = pipes[1]
        pipes[1] = None

        sensors[0] = sensors[1]
        sensors[1] = None

        fitter[0] = fitter[1]
        fitter[1] = None

        transforms[0] = transforms[1]
        transforms[1] = None

    if options.debug:
        fig, ax = plt.subplots(1, npipes, tight_layout=True)
        if npipes == 1:
            if fitter[0]:
                ax = [ax, ]
            else:
                ax = [None, ax]

        fig.suptitle("Fit result")
        for i, F in enumerate(fitter):
            if F is None:
                continue

            ax[i].plot(F.pipe[:, 0], F.pipe[:, 1])

            out = F.transform_data(F.data, transforms[i])
            ax[i].plot(out[:, 0], out[:, 1], 'o')

    # Now go again through all the sequence and get the temperature along the pipes.
    panels = [['P1', 'P2', 'T1', 'S1', 'SP1'],
              ['P1', 'P2', 'T2', 'S2', 'SP2']]
    labels = ["left", "right"]
    tick_labels = ["R0", "R1", "R2", "R3", "R3", "R4", "R4", "R5", "R5", "EoS"]
    fig, ax = plt.subplot_mosaic(panels,
                                 tight_layout=True,
                                 figsize=(10, 5),
                                 gridspec_kw={'width_ratios': (0.25, 0.25, 0.17, 0.16, 0.17)})

    print("Let's go")
    for j, img in enumerate(irbf.images(options.first_frame, nframes=options.nframe)):
        the_frame = options.first_frame + j
        tmin = np.min(img[0].image)

        sss = "Image {} - T {:.2f}".format(the_frame, tmin)
        fig.suptitle(sss)
        print(sss)
        values = getter.get_IR_data(img, rotate=True)
        results = getter.analyze_IR_image(values, pipes, sensors, 0, params)

        # TODO: re-implement this with AnalysisResults
        # if the_frame in options.frames:
        #    save_frame_data(the_frame, path_length, path_temp, sensor_avg, sensor_std)

        ii = 0
        for i in range(2):
            try:
                if results[i] is None:
                    continue
            except IndexError:
                continue

            pmn, pmx = get_min_max(results[i].path_temp)
            spmn, spmx = get_min_max(results[i].path_spread)
            smn, smx = get_min_max(results[i].sensor_avg)

            pan = "P{}".format(i+1)
            cpan = "T{}".format(i+1)
            span = "S{}".format(i+1)
            sspan = "SP{}".format(i+1)
            ax[pan].clear()
            ax[pan].set_title("Image {}".format(labels[i]))
            ax[pan].imshow(imgs[ii], origin='lower', cmap=HighContrast.reversed())   # , cmap='jet')
            ax[pan].plot(pipes[ii][:, 0], pipes[ii][:, 1], linewidth=2, color="#000000")
            for s in sensors[ii]:
                ax[pan].plot(s[:, 0], s[:, 1], linewidth=2, color="#000000")

            ax[cpan].clear()
            ax[cpan].yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax[cpan].set_ylim(pmn, pmx)
            ax[cpan].set_title("Pipe {}".format(labels[i]))
            ax[cpan].plot(results[i].path_length, results[i].path_temp)

            ax[sspan].clear()
            ax[sspan].yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax[sspan].set_ylim(spmn, spmx)
            ax[sspan].set_title("Spread {}".format(labels[i]))
            ax[sspan].plot(results[i].path_length, results[i].path_spread)

            ax[span].clear()
            ax[span].yaxis.set_major_locator(ticker.MultipleLocator(1))
            ax[span].set_ylim(smn, smx)
            ax[span].set_xticks(range(10), labels=tick_labels)

            ax[span].set_title("Sensors {}".format(labels[i]))
            ax[span].plot(results[i].sensor_avg, 'o-')

            ii += 1

        plt.draw()
        plt.pause(0.0001)
        if the_frame in options.frames:
            ofile = "frame_{:03d}.png".format(the_frame)
            fig.savefig(ofile)

        if tmp_dir:
            ofile = "{}/fig{:03d}.png".format(tmp_dir.name, j)
            fig.savefig(ofile)

    if tmp_dir:
        print("Creating movie")
        template = "{}/fig%03d.png".format(tmp_dir.name)
        print("template {}".format(template))
        create_movie(template, options.save_fig)

    print("Min temperature is {} @ {}".format(min_T, i_min))
    for P in pipes:
        if P is not None:
            print("Pipe shape: {}".format(P.shape))

    plt.show()


if __name__ == "__main__":
    # This class contains the parameters needed for tha analysis.
    from IRPetalParam import IRPetalParam

    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--save_frames", dest="frames", default=[],
                        action=CommaSeparatedListAction,
                        help="Frames to save")
    parser.add_argument("--nframe", type=int, default=-1, help="Number of frames. (negative means all.")
    parser.add_argument('--first_frame', type=int, default=0, help="First frame to start.")
    parser.add_argument("--orig", action="store_true", default=False, help="plot the original image")
    parser.add_argument("--save_fig", default=None, help="Save all figures to make a film. Provide output file name")
    parser.add_argument("--show_cycle", action="store_true", default=False, help="Show the thermal cycle.")

    # Add default parameters to the parser
    IRPetalParam.add_parameters(parser)

    options = parser.parse_args()
    nfiles = len(options.files)
    if nfiles == 0:
        print("I need an input file")
        sys.exit()

    analyze_petal(options.files, options)
