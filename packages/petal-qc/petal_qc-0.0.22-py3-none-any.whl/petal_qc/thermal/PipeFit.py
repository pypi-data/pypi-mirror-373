#!/usr/bin/env python3
"""Fit the thermal path to the petal pipe."""
import math
import random
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

from petal_qc.thermal import contours

# This is an ugly hack to see the fits
dbg_ax = None
dbg_fig = None
n_fig = 0


class PipeFit(object):
    """Align Pipe from CAD and thermal pipe."""

    __center = []
    __pipe = []
    __sensors = []
    __cpipe = []
    __insiders = []
    __path = []
    __bb = []

    def __init__(self, is_front, debug=False):
        """Initialization."""
        if len(PipeFit.__center) == 0:
            PipeFit.prepare_data()

        self.data = None
        self.R = None
        self.set_front(is_front)
        self.set_debug(debug)
        self.par_names = ["theta", "Sx", "Sy", "Tx", "Ty"]
        self.bounds = [[-math.pi, 0.8, 0.8, -np.inf, -np.inf],
                       [math.pi, 3.0, 3.0, np.inf, np.inf]]

        self.core_center = None
        self.core_band = None

    def set_front(self, is_front=True):
        """Sets for a front image.

        TODO: this needs optimization. Probably implementing a cache with the
              sides already defined.

        """
        self.front = is_front

        iside = 0 if not is_front else 1
        self.pipe = PipeFit.__pipe[iside]
        self.sensors = PipeFit.__sensors[iside]
        self.center = PipeFit.__center[iside]
        self.cpipe = PipeFit.__cpipe[iside]
        self.insiders = PipeFit.__insiders[iside]
        self.pipe_path = PipeFit.__path[iside]
        self.pipe_bb = PipeFit.__bb[iside]

    def set_debug(self, debug):
        """Sets debug."""
        global dbg_fig, dbg_ax, n_fig
        if debug and dbg_ax is None:
            self.debug = True
            dbg_fig, dbg_ax = plt.subplots(1, 1, tight_layout=True)
            n_fig = dbg_fig.number

        self.debug = debug

        if debug:
            plt.figure(dbg_fig.number)

    @staticmethod
    def prepare_data():
        """Generate the global data."""
        script_path = Path(__file__).absolute().parent
        for iside in range(2):
            if iside:
                pipe_file = script_path.joinpath("pipe_front.npz")
            else:
                pipe_file = script_path.joinpath("pipe_back.npz")

            pipe, sensors = PipeFit.read_pipe_data(pipe_file)
            PipeFit.__pipe.append(pipe)
            PipeFit.__sensors.append(sensors)

            if iside:
                center = np.mean(pipe[pipe[:, 0] < -100], axis=0)
            else:  # back
                center = np.mean(pipe[pipe[:, 0] > 100], axis=0)

            PipeFit.__center.append(center)

            cpipe = pipe - center
            PipeFit.__cpipe.append(cpipe)

            insiders = contours.generate_points_inside_contour(cpipe, 1000)
            PipeFit.__insiders.append(insiders)
            PipeFit.__path.append(mplPath.Path(pipe))
            PipeFit.__bb.append(contours.contour_bounds(pipe))

    @staticmethod
    def read_pipe_data(pipe_file):
        """Reads pipe data from given file.

        Args:
        ----
            pipe_file: the path of the file wit hpipe data

        Returns
        -------
            pipe : the path of the pipe
            sensors: the path of the 9 sensors on a petal side.

        """
        DB = np.load(pipe_file)
        sensors = []
        pipe = []
        for key, val in DB.items():
            if key == "pipe":
                pipe = val
            else:
                sensors.append(val)

        return pipe, sensors

    @staticmethod
    def transform_data(data, M):
        """Apply the transform to the data.

        Args:
        ----
            data: The data. It is a Nx2 array.
            M: The transform. (theta, Sx, Sy, Tx, Ty, Ox, Oy)
               theta is the rotation
               Sx, Sy the scale
               Tx, Ty the translation
               Ox, Ox the final offset. This is not used in the fit.

        Returns
        -------
            _type_: _description_

        """
        # The rotation
        ct = math.cos(M[0])
        st = math.sin(M[0])
        offset = np.array([M[3], M[4]])
        # T = [(1.0-ct)*offset[0] + st*offset[1], -st*offset[0] + (1.0-ct)*offset[1]]
        D = np.zeros(data.shape)
        for i in range(len(data)):
            X = data[i, :] + offset

            P = np.array([M[1]*(ct * X[0] - st * X[1]),
                          M[2]*(st * X[0] + ct * X[1])])

            # The perspective transform
            # delta = (P[0]*M[5]-1)*(P[1]*M[6]-1) - P[0]*P[1]*M[5]*M[6]
            # P = P/delta
            D[i, :] = P

        if len(M) > 5:
            D += np.array([M[5], M[6]])

        return D

    @staticmethod
    def transform_inv(data, M):
        """Inverse transform.

        Args:
        ----
            data: The data. It is a Nx2 array.
            M: The original transform.

        Returns
        -------
            data transformed by the inverse of M.


        """
        out = np.zeros(data.shape)
        O = np.array([M[5], M[6]])

        ct = math.cos(-M[0])
        st = math.sin(-M[0])
        offset = np.array([M[3], M[4]])
        scale = np.array([M[1], M[2]])
        for i in range(len(data)):
            X = data[i, :] - O
            X = X/scale

            P = np.array([(ct * X[0] - st * X[1]),
                          (st * X[0] + ct * X[1])])

            P -= offset

            out[i, :] = P

        return out

    @staticmethod
    def print_transform(M):
        """Print transform."""
        print("Rotation {:.4f} rad".format(M[0]))
        print("Scale X {:.3f} Y {:.3f}".format(M[1], M[2]))
        print("Trans. {:5.3f}, {:5.3f}".format(M[3], M[4]))

        if len(M) > 5:
            print("Center {:5.3f}, {:5.3f}".format(M[5], M[6]))

    @staticmethod
    def get_data_center(data, fraction=0.5, y0=None, min_pts=5):
        """Compute the data center.

        Assumes it is in the half height, and the X is the average of the points
        in a stripe around that value of Y.
        """
        if y0 is None:
            bounding_box = contours.contour_bounds(data)
            y0 = bounding_box[1] + fraction*(bounding_box[3]-bounding_box[1])

        window = 10
        while True:
            stripe = data[np.abs(data[:, 1] - y0) < window]
            if len(stripe) > min_pts:
                break

            window += 1

        m0 = np.mean(stripe, axis=0)
        center = np.array([m0[0], y0])
        return center, (np.min(stripe[:, 0]), np.max(stripe[:, 0]))

    @staticmethod
    def guess_pipe_type(data, fraction=0.25) -> int:
        """Make a guess about the pipe type.

        Args:
        ----
            data (np.ndarray): The data
            fraction: The hight in the pipe where to get the average.
                      Defaults to 0.25.

        Returns
        -------
            pipe type: =0 if looks like back
                       =1 if looks like front

        """
        ix = np.argmin(data[:, 1])
        P0 = data[ix, :]

        D = data[:, 0:2] - P0
        m0 = np.mean(D, axis=0)
        center, _ = PipeFit.get_data_center(D, y0=m0[1])
        # fig, ax = plt.subplots(1,1)
        # ax.plot(D[:,0], D[:, 1], 'o', label="Data")
        # ax.plot(center[0], center[1], '*', label="Center")
        # ax.plot(m0[0], m0[1], 's', label="Mean")
        # ax.legend()
        # plt.draw()
        # plt.pause(0.00001)

        if m0[0] > center[0]:
            return 1
        else:
            return 0

    @staticmethod
    def guess_pipe_angle(data, center):
        """Get an estimation of th epipe angle."""
        c1, _ = PipeFit.get_data_center(data, 0.)
        delta = np.abs(c1 - center)
        angle = math.atan(delta[1]/delta[0])
        while angle<0:
            angle += 2.0*math.pi

        if angle > 1.5*math.pi:
            angle -= math.pi/2.0

        angle = 0.5*math.pi - angle
        return angle

    @staticmethod
    def get_pipe_bottom(data):
        """Try to guess the bottom of pipe."""
        bb = contours.contour_bounds(data)
        stripe = data[np.abs(data[:, 1] - bb[3]) < 10]
        m0 = np.mean(stripe, axis=0)
        bottom = np.array([m0[0], bb[3]])
        return bottom

    def initial_guess(self, data):
        """Make a first guess of the transform."""
        Mdata, _ = self.get_data_center(data)
        theta = self.guess_pipe_angle(data, Mdata)
        if self.front:
            theta = -theta

        T = -Mdata
        dxd = np.amax(data, axis=0) - np.amin(data, axis=0)
        dxp = np.amax(self.cpipe, axis=0) - np.amin(self.cpipe, axis=0)
        scale = dxp/dxd

        M = np.array([theta, scale[0], scale[1], T[0], T[1]])

        if self.debug:
            self.print_transform(M)
            out = self.transform_data(data, M)
            dbg_ax.clear()
            dbg_ax.plot(self.cpipe[:, 0], self.cpipe[:, 1])
            dbg_ax.plot(out[:, 0], out[:, 1])
            dbg_ax.set_title("Initial guess")
            plt.draw()
            plt.pause(0.0001)

        return M

    def get_residuals(self, M):
        """Compute intersecting area."""
        out = self.transform_data(self.data, M)
        y_max = np.max(out[:,1])
        y_min = np.min(out[:,1])

        height = y_max - y_min
        use_area = False
        if use_area:
            path = mplPath.Path(out)
            ngood = 0.0
            ntot = float(len(self.insiders))
            for i in range(len(self.insiders)):
                P = self.insiders[i, :]
                if path.contains_point(P):
                    ngood += 1

            area = 300*(ntot - ngood)/ntot
            real_area = 100*ngood/ntot

        else:
            area = 1.0
            real_area = 1

        npts = len(self.data)
        D = np.zeros([npts, 2])
        ddd = np.zeros(npts)
        sum_weights = 0.0
        weights = np.zeros(npts)
        for i in range(npts):
            X = out[i, :]
            dst, P = contours.find_closest_point(X[0], X[1], self.cpipe)
            D[i, :] = P - X
            ddd[i] = dst
            W = 1 + 2*(y_max - X[1])/height
            weights[i] = W
            sum_weights += W

        # return value
        if use_area:
            res = D.flatten()*area

        else:
            res = np.dot(ddd, weights)/sum_weights

        if self.debug:
            dbg_ax.clear()
            dbg_ax.plot(self.cpipe[:, 0], self.cpipe[:, 1])
            dbg_ax.plot(out[:, 0], out[:, 1])
            dbg_ax.set_title("area {:3f} dist {:.3f}".format(real_area, np.sum(ddd)/npts))
            plt.draw()
            plt.pause(0.0001)

        return res

    def get_jaccard_distance(self, M):
        """Get Jaccard distance."""
        out = self.transform_data(self.data, M)
        out_bb = contours.contour_bounds(out)

        min_x = min(self.pipe_bb[0], out_bb[0])
        min_y = min(self.pipe_bb[1], out_bb[1])
        max_x = max(self.pipe_bb[2], out_bb[2])
        max_y = max(self.pipe_bb[3], out_bb[3])

        npts = 0
        n_int = 0.0
        n_union = 0.0
        out_path = mplPath.Path(out)
        while npts < 1000:
            P = [random.uniform(min_x, max_x), random.uniform(min_y, max_y)]
            in_pipe = self.pipe_path.contains_point(P)
            in_data = out_path.contains_point(P)

            valid_point = True
            if in_pipe and in_data:
                n_int += 1.0
            elif in_pipe or in_data:
                n_union += 1.0
            else:
                valid_point = False

            if valid_point:
                npts += 1

        res = 10*(1.0-n_int/(n_int + n_union))

        if self.debug:
            dbg_ax. clear()
            dbg_ax.plot(self.cpipe[:, 0], self.cpipe[:, 1])
            dbg_ax.plot(out[:, 0], out[:, 1])
            dbg_ax.set_title("res {:3f}".format(res))
            plt.draw()
            plt.pause(0.0001)

        return res

    def fit(self, data, M0=None, factor=1.0, simplify=True):
        """Do the fit.

        Args:
        ----
            data: the data to fit to the pipe contour.
            M0: if given, the initial values

        Returns
        -------
            return the thransform (theta, Sx, Sy, Tx, Ty, Ox, Oy)
               theta is the rotation
               Sx, Sy the scale
               Tx, Ty the translation
               Ox, Oy the final offset. This is not used in the fit.

        """
        if M0 is None:
            M = self.initial_guess(data)
            for i, val in enumerate(M):
                if val < self.bounds[0][i]:
                    val = 1.01 *  self.bounds[0][i]
                    M[i] = val
                elif val > self.bounds[1][i]:
                    val = 0.99 *  self.bounds[0][i]
                    M[i] = val

            if self.debug:
                print("\n** Initial guess")
                self.print_transform(M)
        else:
            M = M0[0:5]

        self.core_center, self.core_band = self.get_data_center(data)

        if simplify:
            self.data = contours.contour_simplify(data, 1.25*factor)
        else:
            self.data = np.array(data)
            
        # self.data = data
        verbose = 0
        if self.debug:
            verbose = 2

        res = least_squares(self.get_residuals, M,
                            method='trf',
                            # ftol=5e-16,
                            #xtol=1.0e-10,
                            # max_nfev=10000,
                            # diff_step=[0.05, 0.02, 0.02, 50, 50],
                            bounds=self.bounds,
                            verbose=verbose)
        self.res = res
        M = np.zeros(7)
        M[0:5] = res.x
        M[5] = self.center[0]
        M[6] = self.center[1]

        if self.debug:
            self.print_transform(M)

        self.R = M
        return M

    def fit_ex(self, data, M0=None, limit=5e6, factor=1, simplify=True):
        """Does the regular fit and tries to correct."""
        R = self.fit(data, factor=factor, M0=M0, simplify=simplify)

        # Check for an offset...
        if self.res.cost > limit:
            delta = []
            for i in [1, 3, 4]:
                x0 = max(self.bounds[0][i], 0.75*R[i])
                x1 = min(self.bounds[1][i], 1.25*R[i])
                X, Y = self.scan(i, x0, x1, 10, R)
                iax = np.argmin(Y)
                delta.append(X[iax])

            R[1] = delta[0]
            R[3] = delta[1]
            R[4] = delta[2]
            R = self.fit(data, R[0:5])

        if self.debug:
            print("\n** Result")
            self.print_transform(R)

        self.R = R
        return R

    def scan(self, ipar, vmin, vmax, npts, M):
        """Scan a parameter value.

        Args:
        ----
            ipar: The parameter index
            vmin: Min value
            vmax: Max value of parameter
            npts: Number of points
            M: transform matrix

        Returns
        -------
            X, Y: values of parameter and residuals

        """
        X = np.linspace(vmin, vmax, num=npts)
        Y = np.zeros(npts)
        M0 = np.array([x for x in M[0:5]])
        for i in range(npts):
            M0[ipar] = X[i]
            out = self.get_residuals(M0)
            out = np.atleast_1d(out)
            Y[i] = 0.5 * np.dot(out, out)

        return X, Y

    def plot(self, show_fig=True):
        """Plot result of fit and data."""
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        ax.plot(self.pipe[:, 0], self.pipe[:, 1], label="Pipe")
        if self.R is not None:
            out = self.transform_data(self.data, self.R)
        else:
            out = self.data

        ax.plot(out[:, 0], out[:, 1], 'o', label="Data")
        ax.legend()
        if show_fig:
            plt.draw()
            plt.pause(0.0001)
        return fig, ax


def main(data_file, opts):
    """The main entry.

    Args:
    ----
        pipe_file: The path of the pipe data file
        data_file: The data file contaning the IR petal path
        opts: Options from command line

    """
    # Create fitting class
    PF = PipeFit(opts.front)

    data = np.loadtxt(data_file, delimiter=',', unpack=False)
    data = contours.contour_smooth(data, 25)

    # Do the fit
    PF.set_debug(opts.debug)
    R = PF.fit_ex(data)
    PF.set_debug(False)

    # PLot results
    fig, ax = plt.subplots(1, 3, tight_layout=True)
    fign = plt.gcf().number
    ax[0].plot(PF.pipe[:, 0], PF.pipe[:, 1])
    ax[0].plot(PF.center[0], PF.center[1], 'o')
    ax[0].set_title("Pipe")

    center, _ = PF.get_data_center(data)
    ax[1].plot(data[:, 0], data[:, 1])
    ax[1].plot(center[0], center[1], 'o')
    ax[1].set_title("Data on IR")

    # Show the result of the fit
    plt.figure(fign)
    out = PF.transform_data(PF.data, R)
    aout = PF.transform_data(data, R)
    center, _ = PF.get_data_center(aout)
    ax[2].plot(PF.pipe[:, 0], PF.pipe[:, 1])
    ax[2].plot(out[:, 0], out[:, 1], 'o')
    ax[2].plot(center[0], center[1], 'o')
    ax[2].plot(aout[0, 0], aout[0, 1], 'o')
    np.savez_compressed("last_pipe.npz", pipe=aout)

    ax[2].set_title("pipe - Data (dots)")
    fig.show()

    if opts.debug:
        F, A = plt.subplots(1, 5, tight_layout=True)
        for i in range(5):
            A[i].set_title("scan {}".format(PF.par_names[i]))
            print("Scanning {}".format(i))
            X, Y = PF.scan(i, 0.75*R[i], 1.25*R[i], 50, R)
            print("done")
            A[i].plot(X-R[i], Y)

    plt.show()


if __name__ == "__main__":
    parser = ArgumentParser(description="PipeContour")
    parser = ArgumentParser()
    parser.add_argument("--front", action="store_true",
                        default=True, dest='front',
                        help="Front side")
    parser.add_argument("--back", action="store_false",
                        dest='front',
                        help="Back side")
    parser.add_argument("--debug", action="store_true",
                        default=False,
                        help="Set to debug")

    opts = parser.parse_args()
    front = opts.front
    script_path = Path(__file__).absolute().parent

    if front:
        data_file = script_path.joinpath("min_path_front.csv")

    else:
        data_file = script_path.joinpath("min_path_back.csv")

    main(data_file, opts)
