#!/usr/bin/env python3
"""Analyze ThermaCAM data."""
import math
import sys
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import polynomial as Polynomial
from scipy import ndimage
from scipy.optimize import minimize
from skimage import measure

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.thermal import contours
from petal_qc.thermal import CSVImage
from petal_qc.thermal import DebugPlot
from petal_qc.thermal import IRBFile
from petal_qc.thermal import PipeFit
from petal_qc.utils.Geometry import Line
from petal_qc.utils.Geometry import Point
from petal_qc.thermal.IRPetalParam import IRPetalParam

# Create a global instance of DebugPLot
debug_plot = DebugPlot.DebugPlot()

the_segments = None  # global variable to store the last segments found.
the_contours = None  # Global variable to store the last contours found
the_images = None
the_3d_points = None

class DebugTempProfile(object):
    """Stores Debug data."""

    def __init__(self):
        """Initialization."""
        self._x = None   # The x along the segment (From A to B)
        self._P = None   # The 2D points along the segment
        self._T = None   # The temperature values along thre segment
        self._xF = None  # X where fit function is evaluated
        self._pF = None  # 2D points where fit func is evaluaed
        self._Fn = None  # Fit function values at _xF.

    def set_data(self, data):
        """Get data returned be create_profile."""
        self._x = np.copy(data[:, 2])
        self._P = np.copy(data[:, 0:2])
        self._T = np.copy(data[:, 3])

    def set_function(self, x, line, pfunc):
        """Sets the fit data."""
        self._xF = np.copy(x)
        self._Fn = pfunc(x)
        self._pF = np.zeros([len(x), 2])
        for i, v in enumerate(x):
            P = line.param(v)
            self._pF[i, 0:2] = P


T_profile = None      # Global to store the temp. profile.


def get_all_3d_points():
    """Return all pipe path 3D points."""
    return the_3d_points

def set_all_3d_points(all_3d_points):
    """Set all pipe path 3D points."""
    global the_3d_points
    the_3d_points = all_3d_points


def get_last_segments():
    """Return the last segments found."""
    global the_segments
    return the_segments


def get_last_contours():
    """Return last contours."""
    global the_contours
    return the_contours


def get_last_images():
    """Return left and right images."""
    if the_images is None:
        return None

    return the_images


def set_images(img_list):
    """Set global list with images."""
    global the_images
    the_images = img_list


class Segment(object):
    """Values in a contour segment.

    A and B are the edges of the slice
    Pmin is the list of points with minimum temperature
    Tmin is the list of minimum temperature
    distance is the distance from the start of the contour.
    """

    the_segmens = None

    def __init__(self, A, B, Pmin, distance, Tmin, Spread):
        """Initialization."""
        self.A = A
        self.B = B
        self.Pmin = Pmin
        self.distance = distance
        self.Tmin = Tmin
        self.Spread = Spread

    @staticmethod
    def get_points_in_list(segments):
        """Return a list with all the points in the list of segments.

        Args:
        ----
            segments (list[Segment]): The list of segments

        Returns
        -------
            np.array: array of points.

        """
        # Count the number of points
        npts = 0
        for S in segments:
            if S.Pmin is not None:
                npts += len(S.Pmin)

        points = np.zeros([npts, 2])
        ipoint = 0
        for S in segments:
            if S.Pmin is None:
                continue

            for Pmin in S.Pmin:
                points[ipoint, :] = Pmin
                ipoint += 1

        return points

    @staticmethod
    def get_3d_points_in_list(segments):
        """Return a list with all the 3D points (x,y,T) in the list of segments.

        Args:
        ----
            segments (list[Segment]): The list of segments

        Returns
        -------
            np.array: array of points.

        """
        # Count the number of points
        npts = 0
        for S in segments:
            if S.Pmin is not None:
                npts += len(S.Pmin)

        points = np.zeros([npts, 3])
        ipoint = 0
        for S in segments:
            if S.Pmin is None:
                continue

            for i, Pmin in enumerate(S.Pmin):
                points[ipoint, 0] = Pmin.x
                points[ipoint, 1] = Pmin.y
                points[ipoint, 2] = S.Tmin[i]
                ipoint += 1

        return points

    @staticmethod
    def get_spread_in_list(segments):
        """Return an array with spread values."""
        # Count the number of points
        npts = 0
        for S in segments:
            if S.Pmin is not None:
                npts += len(S.Pmin)

        values = np.zeros([npts])
        ipoint = 0
        for S in segments:
            if S.Pmin is None:
                continue

            values[ipoint] = S.Spread
            ipoint += 1

        return values


def reorder_pipe_points(in_data, is_front, T=None, image=None, cut=15):
    """Reorder the pipe points.

    Points are ordered so that the first point is the minimum at the bottom
    bending of the pipe. The points will run clockwise for thre  "front" view
    (EoS at the right) and anti-clockwise to the other view.

    Args:
    ----
        data: The original pipe path is_front (bool): Tells about he petal side.
        is_front: tells whether it is a "front view" (EoS)
        T: the transform to move to petal coordinates (result of fit)
        image: The IR image. This will trigger all the debug activity.

    Returns
    -------
        out: Contains the points ordered. It will contain an additional point,
             the one at the bottom of the petal pipe bend. This will be the
             very first one

    """
    out = np.zeros(in_data.shape)
    npts = len(in_data)
    indx = np.zeros(npts, dtype=int)
    if T is not None:
        data = PipeFit.PipeFit.transform_data(in_data, T)

    else:
        data = np.copy(in_data)

    if image is not None:
        fig, ax = plt.subplots(1, 3, tight_layout=True,
                               gridspec_kw={'width_ratios': (0.25, 0.25, 0.5)},
                               figsize=(7, 4), dpi=300)
        fig.suptitle("pipe {}".format(is_front))

    # find point of lower Y. This is the bend at tehe bottom of the petal
    ix = np.argmin(data, axis=0)
    i0 = ix[1]
    X = data[i0-3:i0+4, 0]
    Y = data[i0-3:i0+4, 1]
    dbg_XY = np.vstack([X, Y]).T
    c, stats = Polynomial.polyfit(X, Y, 2, full=True)
    pfunc = Polynomial.Polynomial(c)
    fmin = minimize(pfunc, data[i0, 0])

    X0 = fmin.x[0]
    Y0 = pfunc(X0)

    # Now insert the minimum into both arrays
    if X0 > data[i0, 0]:
        data = np.insert(data, i0, [X0, Y0], axis=0)
    else:
        data = np.insert(data, i0+1, [X0, Y0], axis=0)
        i0 += 2

    if image is not None:
        x = np.linspace(X[0], X[-1], 50)
        dbg_XF = np.vstack([x, pfunc(x)]).T
        ax[0].plot(X, Y, 'o-', X0, Y0, 'o', dbg_XF[:, 0], dbg_XF[:, 1], '-')
        ax[1].plot(data[:, 0], data[:, 1], 'o-', dbg_XF[:, 0], dbg_XF[:, 1], '-')

    # Copy the data into the output array
    n1 = npts-i0
    out[:n1, :] = data[i0:npts, :]
    out[n1:, :] = data[:i0, :]

    if not is_front:
        out = np.flipud(out)
        indx = np.flipud(indx)

    if T is not None:
        out = PipeFit.PipeFit.transform_inv(out, T)

    if image is not None:
        if T is not None:
            dbg_XY = PipeFit.PipeFit.transform_inv(dbg_XY, T)
            dbg_XF = PipeFit.PipeFit.transform_inv(dbg_XF, T)

        ax[2].imshow(image, origin='lower', cmap='jet')
        ax[2].plot(out[:, 0], out[:, 1], 'o-', dbg_XF[:, 0], dbg_XF[:, 1], '-', out[0:5, 0], out[0:5, 1], 'o')
        ax[2].set_xlim([0.8*np.min(dbg_XY[:, 0]), 1.2*np.max(dbg_XY[:, 0])])
        ax[2].set_ylim([0.8*np.min(dbg_XY[:, 1]), 1.2*np.max(dbg_XY[:, 1])])

    return out


def find_reference_image(irbf, T_min):
    """Find first image in sequence with T < T_min.

    Args:
    ----
        irbf: The sequence of IR images
        T_min: The temperature threshold

    Returns
    -------
        min_T, i_min, values: The actual temperature of the image,
                              the sequence nubmer
                              and the array of values

    """
    # find the image with smalowestllest temperature. This will be used to define the pipe
    min_T = sys.float_info.max
    i_min = -1
    for i, img in enumerate(irbf.images()):
        temp = np.min(img[0].image)
        print("Image {}. Min temp {:.3f} C".format(i, temp))
        if temp < min_T:
            min_T = temp
            if min_T < T_min:
                i_min = i
                break

    if i_min < 0:
        raise LookupError("No frame below {} C found. Quitting.".format(T_min))

    ref_img = irbf.getImage(i_min)
    # values = get_IR_data(ref_img)

    return min_T, i_min, ref_img


def extract_pipe_path(image, params):
    """Extract the "pipe path"  in a petal IR image.

    Args:
    ----
        image: The 2D array containing the 2 specular images
        params: IRPetalPam object with options.

    Returns
    -------
        pipe: the pipe contour or path.

    """
    global the_images

    the_images = [image, ]
    pipe = get_IR_pipe(image, params)
    pipe = contours.contour_smooth(pipe, params.contour_smooth)
    return pipe


def extract_mirrored_pipe_path(values, params):
    """Extract the path of the 2 pipes in a 2 petal image.

    Args:
    ----
        values: The 2D array containing the 2 specular images
        params: IRPetalPam object with options.

    Returns
    -------
        (left_pipe, right_pipe): The 2 paths.

    """
    global the_images, the_3d_points
    if params.rotate:
        rotated = rotate_full_image(values)
    else:
        rotated = values

    imgs = split_IR_image(rotated)
    pipes = []
    points_3d = []
    for img in imgs:
        pipe = extract_pipe_path(img, params)
        pipes.append(pipe)
        points_3d.append(get_all_3d_points())

    the_images = imgs
    the_3d_points = points_3d
    return list(pipes)


def get_mirrored_petal_images(img, params):
    """Return the images in a mirrored petal image.

    Args:
    ----
        img (IRBImage): The image of the mirror image
        params: IRBPetalParam object

    Returns
    -------
        tuple of images

    """
    if isinstance(img, IRBFile.IRBImage):
        values = get_IR_data(img, rotate=params.rotate)
    else:
        values = img

    images = split_IR_image(values)
    return images


def get_IR_data(ref_img, rotate=False):
    """Get the data from the image in the proper orientation.

    Proper orientation means that petals are vertical (in the  mirror image).
    It will eventually try to rotate the image to compensate a camera rotation.

    Args:
    ----
        ref_img: IRBimage
        rotate: True to make the rotation compensation.

    Returns
    -------
        2d array: The 2d array wit the temperature data.

    """
    nrow, ncol = ref_img.image.shape
    landscape = (ncol > nrow)

    if landscape:
        values = ref_img.image.T
    else:
        values = ref_img.image

    if rotate:
        values = rotate_full_image(values)

    return values


def rotate_full_image(data):
    """Rotates full image.

    The idea is to make the line produced by the actual petal vertical.
    This should correct rotations of the camera.

    Args:
    ----
        data: The image.

    Returns
    -------
        The image rotated.

    """
    nrow, ncol = data.shape
    delta = 100 * nrow/1280
    npts = int(20 * nrow/1280 + 1)
    Y = np.linspace(nrow, nrow-delta, npts)

    npX = 20 * ncol/960
    first_row = data[nrow-1, :]
    indx = np.argmin(first_row)
    A = np.zeros([len(Y), 2])
    A[:, 0] = indx - npX  # ncol/2 - npX
    A[:, 1] = Y

    B = np.zeros([len(Y), 2])
    B[:, 0] = indx + npX  # ncol/2 + npX
    B[:, 1] = Y

    # Get segments along vertical
    segments = slice_contours(data, A, B, distance=abs(Y[1]-Y[0]), do_fit=True, show=False)
    points = Segment.get_points_in_list(segments)
    points -= np.array([ncol/2, nrow])

    # Fit the poitns to a straight line to get the angle.
    c = Polynomial.polyfit(points[:, 0], points[:, 1], 1)
    angle = -math.atan(c[1])

    # Rotate image
    rotated = ndimage.rotate(data, angle=angle)
    return rotated


def find_slice_minimum(T, X):
    """Find the position of the minimum value.

    Args:
    ----
        T: array with values
        X: array with positions

    Returns
    -------
        Tmin, Pmin: min value and position of minimum.

    """
    indx = np.argmin(T)
    i = j = int(indx)
    Tmin = T[indx]
    while i > 0:
        if T[i-1] == Tmin:
            i -= 1
        else:
            break

    while j < len(T)-1:
        if T[j+1] == Tmin:
            j += 1

        else:
            break

    Pmin = (X[i] + X[j])/2
    return Tmin, Pmin


def get_T_profile(data, A, B, npts=10, do_fit=False, npdim=6, debug=False):
    """Get the temperature profile between A and B.

    Args:
    ----
        data: the data
        A: First point in segment
        B: Last point in segment
        npts: number of points in segment
        do_fit: True if fit rather that takng minimum value
        npdim: the degree of the polynomialused to fit.
        debug: if True, show debug information.

    Return:
    ------
        Tmin, Pmin, S: Tmin is the minimum temperature.
                       Pmin the point of the minimum.
                       S the Temperature spread
                       In case of prblems both are None.

    """
    global debug_plot, T_profile
    if debug:
        debug_plot.setup_debug('TProf')

    T_profile = DebugTempProfile()

    mx_dist = A.distance(B)
    L, T, X, _data = create_profile(data, A, B, npts)
    spread = np.sqrt(np.cov(X, aweights=np.abs(T)))

    T_profile.set_data(_data)

    spread = np.std(T)
    # If we just want the minimum temperature or we have something close to a flat line
    if not do_fit or spread < 0.35:
        Tmin, Pmin = find_slice_minimum(T, X)
        if debug:
            debug_plot.plot('TProf', X, T, 'o', [Pmin], [Tmin], 'o')

        return [Tmin], [L.param(Pmin)], spread

    else:
        ndof = len(X)
        T_min = np.min(T)
        x_min = np.min(X)
        x_max = np.max(X)

        # TODO: get rid of the IF below...
        if ndof < npdim and ndof > 4:
            npdim = 4

        # Do the polinomialfit.
        if ndof > npdim:
            indx = remove_outliers(np.array(T), 6, indx=True)
            TT = np.array(T)
            XX = np.array(X)
            c, stats = Polynomial.polyfit(XX[indx], TT[indx], npdim, full=True)
            pfunc = Polynomial.Polynomial(c)

            # Get the polinomial derivative roots and curvature.
            # This is done to catch double minimums

            valid_roots, valid_values, valid_curv = get_derivatives(T_min, X[1], X[-1], c)

            #
            # TODO: temporary remove the search for double minima in the segment.
            valid_roots, valid_values, valid_curv = [], [], []

            if len(valid_roots) > 1:
                print("--- Multi-minimum segment.")
                for r, v, crv in zip(valid_roots, valid_values, valid_curv):
                    print("{} -> {} [{}]".format(r, v, crv))
                    
                x = np.linspace(x_min, x_max, 3*npts)
                debug_plot.plot('TProf', X, T, 'o', x, pfunc(x), '-', valid_roots, valid_values, 'o')
                if len(valid_roots) > 1:
                    debug_plot.setup_debug('TProfMulti')
                    debug_plot.plot('TProfMulti', X, T, 'o', x, pfunc(x), '-', valid_roots, valid_values, 'o')
                    debug_plot.set_title('TProfMulti', "Curvature: {}".format(str(valid_curv)))

            # Find the polynomial minimum with `minimize` (redundant, probably)
            X0 = X[np.argmin(T)]
            fmin = minimize(pfunc, X0)
            x = np.linspace(x_min, x_max, 3*npts)

            if not fmin.success and len(fmin.x):
                for V in valid_roots:
                    if abs(fmin.x[0] - V) < 1e-3:
                        fmin.success = True
                        break

            # If there is a clear minimum within the segment
            if fmin.success and fmin.x[0] > 0 and fmin.x[0] < mx_dist:
                # This should no happen. if minimize returns we should have found
                # at least a valid root.
                if len(valid_roots) == 0:
                    valid_roots = np.array([fmin.x[0]])
                    valid_values = np.array([fmin.fun])

                # Prepare the resould
                Tmin = valid_values
                Pmin = [L.param(x) for x in valid_roots]
                T_profile.set_function(x, L, pfunc)
                if debug:
                    debug_plot.plot('TProf', X, T, 'o', x, pfunc(x), '-', valid_roots, valid_values, 'o')

                    if len(valid_roots) > 1:
                        debug_plot.setup_debug('TProfMulti')
                        debug_plot.plot('TProfMulti', X, T, 'o', x, pfunc(x), '-', valid_roots, valid_values, 'o')
                        debug_plot.set_title('TProfMulti', "Curvature: {}".format(str(valid_curv)))

                return Tmin, Pmin, spread

            else:
                # No good minimum
                Tmin, Pmin = find_slice_minimum(T, X)
                if debug:
                    debug_plot.plot("TProf", X, T, 'o', [Pmin], [Tmin], 'o')
                    debug_plot.set_title('TProf', "Could not find the minimum")

                return None, None, spread

        else:
            return None, None, spread


def create_profile(data, A, B, npts):
    """Create a T profile along the line connecting A and B.

    Args:
    ----
        data (array): The data array
        A (Point): Start point
        B (Point): The end point
        npts: Number of points

    Returns
    -------
        L, T, X, _data: Line connecting A and B, T values, distance along line, data.
                        data contains information about the points in the profile:
                            0:1 Point coordinates
                            2: path length along segment,
                            3: mean temperature

    """
    # Sample the data between the 2 given points, A and B. The data is smeared
    # around the corresponging point by averaing the neighbors.
    dst = A.distance(B)
    step = dst/npts
    L = Line(A, B)
    T = []
    X = []
    _data = np.zeros([npts, 4])
    _i = 0
    for i in range(npts):
        lmd = i * step
        p = L.param(lmd)
        ix = int(p.x)
        iy = int(p.y)

        # Get the average
        M = data[iy-2:iy+2, ix-2:ix+2]
        indx = np.nonzero(M)
        if not np.any(indx):
            continue

        S = M[indx].mean()

        # Store values for fit and debug.
        if S != 0 and not np.isnan(S):
            _data[_i, 0:2] = p
            _data[_i, 2] = lmd
            _data[_i, 3] = S
            _i += 1
            T.append(S)
            X.append(i*step)

    if _i < npts:
        _data = _data[0:_i, :]

    return L, T, X, _data


def get_derivatives(T_min, x_min, x_max, coeff):
    """Get valid roots and values of a polinomial in the  given range.

    Args:
    ----
        T_min: Min value of Temperature
        x_min: Lower edge of interval
        x_max: Upper edge of interval
        coeff: Polinomial coefficients

    Returns
    -------
        List: roots, values@roots, curvature@roots

    """
    npdim = len(coeff)
    pfunc = Polynomial.Polynomial(coeff)
    fact = np.array([x for x in range(1, npdim)])
    cderiv = fact*coeff[1:]
    cderiv2 = fact[:-1]*cderiv[1:]

    deriv = Polynomial.Polynomial(cderiv)
    deriv2 = Polynomial.Polynomial(cderiv2)
    roots = Polynomial.polyroots(cderiv)

    indx = np.where((np.isreal(roots)) & (roots > x_min) &
                    (roots < x_max) &
                    (pfunc(roots) < 0.5*T_min))

    valid_roots = np.real(roots[indx])
    valid_values = pfunc(valid_roots)
    valid_curv = deriv2(valid_roots)

    indx = np.where(valid_curv > 1e-3)
    valid_roots = valid_roots[indx]
    valid_values = valid_values[indx]
    valid_curv = valid_curv[indx]

    return valid_roots, valid_values, valid_curv


def show_profile(debug_plot, title=None):
    """Plot a profile."""
    debug_plot.setup_debug("Slices", is_3d=True)
    if T_profile:
        if T_profile._x is not None:
            debug_plot.plot("Slices", T_profile._P[:, 0], T_profile._P[:, 1], T_profile._T, 'ro')
        if T_profile._pF is not None:
            debug_plot.plotx("Slices", T_profile._pF[:, 0], T_profile._pF[:, 1], T_profile._Fn, 'b-')

        if title:
            debug_plot.set_title("Slices", title)


__call_id__ = 0
__img_num__ = 0

def slice_contours(data, inner, outer, distance=50, npoints=15, do_fit=False, show=False) -> list[Segment]:
    """Make slices between contours.

    Args:
    ----
        data: the data
        inner: Inner contour
        outer: Outer contour
        distance: distance between slices
        npoints: number of points in segment
        do_fit: if True do fit values to get the minimum
        show: if True show result of fits

    Returns
    -------
        A list of Segments.

    """
    global debug_plot, __call_id__, __img_num__

    __call_id__ += 1
    __img_num__ = 0
    #show=True
    segments = []
    dist = 0
    npts = len(outer)
    dist = 0

    # First point in outer contour. Find closest point in inner contour
    # and the minimum along the segment.
    x0, y0 = outer[0, :]
    last_x, last_y = x0, y0
    U = contours.find_closest(x0, y0, inner)
    Tmin, Pmin, spread = get_T_profile(data, Point(x0, y0), Point(U[0], U[1]), npts=npoints, do_fit=do_fit, debug=False)
    if show:
        show_profile(debug_plot, "Dist {:.3f}, Tmin {:.2f} ({:.1f}, {:.1f})".format(dist, Tmin[0], Pmin[0].x, Pmin[0].y))
        debug_plot.savefig("Slices", "/tmp/img_{}_{}.png".format(__call_id__, __img_num__))
        __img_num__ += 1
        try:
            ax = debug_plot.get_ax("Contours")
            ax.plot([x0, U[0]], [y0, U[1]], '-')
            ax.plot(Pmin[0].x, Pmin[0].y, 'o')
        except KeyError:
            pass

    # store results: distance along segment and temperature
    T = []
    D = []
    for val in Tmin:
        T.append(val)
        D.append(dist)

    # segments.append(((x0, y0), U, Pmin, (dist, Tmin)))
    segments.append(Segment((x0, y0), U, Pmin, dist, Tmin, spread))

    # Now loop on all the points
    path_length = 0
    for ipt in range(npts):
        x, y = outer[ipt, :]
        point_sep = math.sqrt((x-last_x)**2+(y-last_y)**2)
        dist += point_sep
        path_length += dist
        last_x, last_y = x, y
        if dist >= distance:
            V = contours.find_closest(x, y, inner)
            if V is None:
                break

            # Store point
            x0, y0 = x, y

            # Get the minimum on the slice
            Tmin, Pmin, spread = get_T_profile(data, Point(x0, y0), Point(V[0], V[1]),
                                               npts=npoints, do_fit=do_fit, debug=False)
            if Tmin is not None:
                for val in Tmin:
                    T.append(val)
                    D.append(path_length)

                segments.append(Segment((x0, y0), V, Pmin, path_length, Tmin, spread))
                if show:
                    show_profile(debug_plot, "Dist {:.3f} Tmin {:.2f} ({:.1f}, {:.1f})".format(path_length, Tmin[0], Pmin[0].x, Pmin[0].y))
                    debug_plot.savefig("Slices", "/tmp/img_{}_{}.png".format(__call_id__, __img_num__))
                    __img_num__ += 1
                    
                    try:
                        ax = debug_plot.get_ax("Contours")
                        ax.plot([x0, V[0]], [y0, V[1]], '-')
                        ax.plot(Pmin[0].x, Pmin[0].y, 'o')
                    except KeyError:
                        pass

            dist = 0

    # Now plot the temperature along the pipe.
    if show:
        debug_plot.setup_debug("SlicePipe")
        debug_plot.plot("SlicePipe", D, T, '-o')
        debug_plot.savefig("SlicePipe", "/tmp/slice_pipe_{}.png".format(__call_id__))

    return segments


def find_image_contours(data, params):
    """Find the image contours to get the pipe position.

    The idea is to find 2 contours so that the pipe lies between the outer and
    inner contour.

    The contours are found from the minimum value in the image and adding a
    percentage (params.countour.cut) of the image value range (max-min).

    The image is blurred before with a median filter.

    Args:
    ----
        data: The IR image.
        params (IRPetalParams): An IRPetalParam object.

    Returns
    -------
        list of contours. Order is [inner, outer]. None if not doog contours
        found.

    """
    # make a gaus filtering to smooth theimage
    filtered = ndimage.median_filter(data, size=params.gauss_size)

    # Get the actual absolute value for the contours.
    min_T = np.min(filtered)
    max_T = np.max(filtered)
    target_T = min_T + params.contour_cut*(max_T-min_T)

    # Get the contours
    contour_list = measure.find_contours(filtered, target_T)
    out = []

    # Filter out the contours.
    for contour in contour_list:
        # Accept only closed contours
        if np.any(contour[0, :] != contour[-1, :]):
            continue

        tmpC = contours.adjust_contour(contour)
        area = contours.contour_area(tmpC)
        if area < params.min_area:
            continue

        # Smooth th econtour.
        tmpC = contours.contour_smooth(tmpC, 25)
        out.append(tmpC)

        if params.debug:
            print("contour area: {:.3f}".format(area))

    if params.debug:
        debug_plot.setup_debug("Contours", 1, 1)
        colors = ["#ff9b54", "#ff7f51"]  # ["#540b0e", "#9e2a2b"]
        print("Number of countours:", len(out))

        ax = debug_plot.get_ax("Contours")
        ax.clear()
        ax.imshow(data, origin='lower', cmap='jet')
        for i, cnt in enumerate(out):
            ax.plot(cnt[:, 0], cnt[:, 1], linewidth=3, color=colors[i % 2])

        ax.set_title("Contours")

    # Order the contours
    if len(out) != 2:
        return None

    outer_path = mplPath.Path(out[0])
    inner_path = mplPath.Path(out[1])
    if outer_path.contains_path(inner_path):
        inner = out[1]
        outer = out[0]
    else:
        inner = out[0]
        outer = out[1]

    global the_contours
    the_contours = inner, outer
    return inner, outer


def get_segments(data, params) -> list[Segment]:
    """Compute the pipe segments.

    Args:
    ----
        data: The IR image.
        params (IRPetalParams): An IRPetalParam object.

    Returns
    -------
        list of segments. See `slice_contours`

    """
    global the_3d_points
    cntrs = find_image_contours(data, params)
    if cntrs is None:
        return None

    global the_segments
    the_segments = slice_contours(data, cntrs[0], cntrs[1],
                                  distance=params.distance,
                                  npoints=params.npoints,
                                  do_fit=params.do_fit,
                                  show=params.debug)

    the_3d_points = Segment.get_3d_points_in_list(the_segments)
    return the_segments


def get_IR_pipe(data, params):
    """Return the pipe path in the IR image.

    Args:
    ----
        data: The IR image.
        params (IRPetalParams): An IRPetalParam object.

    Returns
    -------
        The contour of the pipe amd the list of segments.
        None in case of problems.

    """
    segments = get_segments(data, params)
    if segments is None:
        return None

    min_path = Segment.get_points_in_list(segments)
    return min_path


def remove_outliers(data, cut=2.0, indx=False, debug=False):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        indx: if True return indices rather than a new array
        debug: be bverbose if True

    """
    # move to the
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    if indx:
        return np.where(s < cut)[0]
    else:
        return data[s < cut]


def get_T_along_path(irpath, data, width, norm=True):
    """Get the mean T along the IRpath.

    Temperature is computed as the average in a widthxwidth square
    around the points in the path.

    Args:
    ----
        irpath: coordinates in image reference of the points
                defining the path.
        data: the 2D data matrix
        width: half width of rectangle around point to compute the average.
        norm: if True will normalize teh X coordinates to go fro m0 to 1.
              Otherwise they will represen the path length.

    Returns
    -------
        values, D: values are the temperature.
                   D is the path legnth at this point.
                   If norm is True, it will be normalized to a total distance of 1.

    """
    npts = len(irpath)
    values = np.zeros(npts)
    shape = data.shape
    D = np.linspace(0, npts-1, npts)
    dst = 0
    X0 = 0
    for i in range(npts):
        X = irpath[i, :]
        ix1 = int(round(max(0, X[0]-width)))
        ix2 = int(round(min(shape[1], X[0]+width)))
        iy1 = int(round(max(0, X[1]-width)))
        iy2 = int(round(min(shape[0], X[1]+width)))

        the_region = data[iy1:iy2, ix1:ix2]
        values[i] = np.mean(the_region)
        std = np.std(the_region)

        if std > 1.0:
            # print("Expect problems.")
            # print("--- ({})".format(X))
            # print(the_region)
            # print("avg: {:.4f} std {:.4f} sample {}". format(values[i], std, the_region.size))
            val = remove_outliers(the_region, 1.5)
            values[i] = np.mean(val)
            std = np.std(val)
            # print("avg: {:.4f} std {:.4f} sample {}". format(values[i], std, len(val)))

        if i:
            dst += np.linalg.norm(X-X0)

        D[i] = dst
        X0 = X

    if norm:
        D = D/dst

    return values, D


def find_edge(data, i0, half, indices):
    """Find edges."""
    i1 = i0
    last = -1
    for i in indices:
        x = data[i]
        if indices[0] <= indices[-1]:
            if x > half:
                break

        else:
            if x < half:
                break

        if last < 0:
            i1 = x
            last = x
            continue

        else:
            if abs(x-last) <= 2:
                i1 = x
                last = x

    return i1


def get_spread_along_path(irpath, data, width, norm=True, debug=False):
    """Get the T spread along the IRpath.

    At each point we build the line perpendicular to the path
    and compute the temperature spread in this line.

    Args:
    ----
        irpath: coordinates in image reference of the points
                defining the path.
        data: the 2D data matrix
        width: half width of rectangle around point to compute the average.
        norm: if True will normalize teh X coordinates to go fro m0 to 1.
              Otherwise they will represen the path length.

    Returns
    -------
        values, D: values are the temperature spread.
                   D is the path length at this point.
                   If norm is True, it will be normalized to a total distance of 1.

    """
    npts = len(irpath)
    values = np.zeros(npts)
    shape = data.shape

    # GEt the path length
    D = contours.contour_path_length(irpath, norm)

    # Start with the spread calculation
    if debug:
        dbg_pts = [None, None]

    for i in range(npts):
        X = Point(irpath[i, :])

        try:
            L = Line(X, Point(irpath[i+1, :]))
        except Exception as E:
            L = Line(X, Point(irpath[0, :]))

        # Get the line perpendicular.
        pL = L.line_perpendicular_at_point(X)
        xp = np.linspace(-width, width, 2*width+1)
        xt = np.zeros(xp.shape)
        for j, ix in enumerate(xp):
            p = X + ix*pL.V
            if debug:
                dbg_pts[1 if j else 0] = p

            ix1 = int(round(max(0, p[0]-1)))
            ix2 = int(round(min(shape[1], p[0]+1)))
            iy1 = int(round(max(0, p[1]-1)))
            iy2 = int(round(min(shape[0], p[1]+1)))

            the_region = data[iy1:iy2, ix1:ix2]
            xt[j] = np.mean(the_region)

        npts = len(xt)
        xta = np.abs(xt)
        grd = np.gradient(xta)

        edges = np.where(abs(grd) > 2)[0]
        nedg = len(edges)
        half = int(npts/2)

        i1 = 0
        i2 = npts-1
        if nedg == 1:
            if edges[0] < half:
                i1 = edges[0]
                i2 = npts-1
            else:
                i1 = 0
                i2 = edges[0]
        elif nedg:
            i1 = find_edge(edges, 0, half, [x for x in range(nedg)])
            i2 = find_edge(edges, npts-1, half, [x for x in range(nedg-1, -1, -1)])

        try:
            qtl = np.quantile(xta[i1:i2], [0.25, 0.5, 0.75, 1])
            iqr = qtl[2]-qtl[0]
            values[i] = iqr

        except Exception as e:
            print("Problems.\n{}".format(repr(e)))
            pass

        # Debugging.
        if debug:
            xxx = np.get_printoptions()
            np.set_printoptions(precision=2)
            print("{} -> {:.2f}".format(qtl, iqr))
            np.set_printoptions(precision=xxx['precision'])
            debug_plot.setup_debug("TSpread", 1, 3,
                                   fig_kw={"figsize": (10, 5),
                                           "gridspec_kw": {'width_ratios': (0.35, 0.35, 0.3)}})
            ax = debug_plot.get_ax("TSpread")
            ax[0].clear()
            ax[0].plot(D[:i+1], values[:i+1], 'o-')

            ax[1].clear()
            ax[1].plot(xp, xt, 'o-')
            xx = [xp[i1], xp[i2]]
            yy = [-qtl[3], -qtl[3]]
            ax[1].plot(xx, yy, 'o-')

            xl = ax[1].get_xlim()
            yl = ax[1].get_ylim()
            ax[1].text(0.5*(xl[0]+xl[1]), yl[1]-0.1*abs(yl[1]-yl[0]),
                       "IQR: {:.2f}".format(iqr),
                       horizontalalignment="center")

            debug_plot.setup_debug("TSpread", 1, 2)
            ax = debug_plot.get_ax("TSpread")
            ax[2].clear()
            ax[2].imshow(data, origin="lower", cmap='jet')
            ax[2].plot(irpath[:, 0], irpath[:, 1], '-o')
            ax[2].plot([dbg_pts[0][0], dbg_pts[1][0]], [dbg_pts[0][1], dbg_pts[1][1]], '-', linewidth=2, color="black")
            plt.draw()
            plt.pause(0.0001)

    return values, D


def show_data(data, params, fname=None, id=0):
    """Show the data histograms.

    Args:
    ----
        data: The data array
        params: a IRPetalParam object or equivalent with parameters
        fname : Name of output file with images. Defaults to None.
        id: tells whether it is front (0) or back (1)

    """
    min_path = get_IR_pipe(data, params)
    segments = get_last_segments()
    cntrs = get_last_contours()  # find_image_contours(data, params)

    nrow, ncol = data.shape
    colors = ["#540b0e", "#9e2a2b"]
    fig, ax = plt.subplots(1, 1, tight_layout=True, dpi=300, figsize=(3, 4.5))  # figsize=(ncol/200, nrow/300))

    ax.set_title("Contours - {}".format(id))
    pcm = ax.imshow(data, origin='lower', cmap="jet")
    fig.colorbar(pcm, ax=ax)
    fig.savefig("single-petal-{}.png".format(id))

    for i, cnt in enumerate(cntrs):
        ax.plot(cnt[:, 0], cnt[:, 1], linewidth=3, color=colors[i % 2])

    fig.savefig("single-petal-contours-{}.png".format(id))

    for S in segments:
        ax.plot([S.A[0], S.B[0]], [S.A[1], S.B[1]], 'o-', linewidth=1, markersize=2, color="#788aa3")
        for P in S.Pmin:
            ax.plot(P[0], P[1], 'o', linewidth=1, markersize=2, color="#788aa3")

    fig.savefig("single-petal-segments-{}.png".format(id))

    ax.plot(min_path[:, 0], min_path[:, 1], linewidth=1, color="black")
    fig.savefig("single-petal-all-{}.png".format(id))

    np.savetxt("min_path_{}.csv".format(id), min_path, delimiter=',', fmt='%.4f')
    if fname:
        fig.savefig(fname, dpi=300)


def split_IR_image(values, fraction=0.5):
    """Split the image in 2 halves.

    Args:
    ----
        values: origina matrix with image values
        fraction: Tell fraction of left over right parts of image

    """
    nrow, ncol = values.shape
    half = int(fraction*ncol)

    left = values[:, 0:half]
    right = values[:, half:]

    return left, right


def get_image_from_irb(irbf, frame, thrs):
    """Return image.

    Args:
    ----
        irbf: the IRBFile object.
        frame: if >=0, it will return the frame number given here.
        thrs: if frame is <0, it will return the first image whose
              the lower temperature is smaller than this value

    Returns
    -------
        if the conditions are mot met (frame or threshold) it will
        raise LookupError.

        img: the image
        i_min: the index of the image in the sequence.

    """
    img = None
    i_min = frame
    if irbf.nimages == 0:
        print("Input file does not contain images.")

    else:
        if frame >= 0:
            img = irbf.getImage(frame)
            if img is None:
                raise LookupError("Frame {} not found in [0, {}]".format(frame, irbf.n_images()))

        else:
            min_T, i_min, *_ = find_reference_image(irbf, thrs)
            img = irbf.getImage(i_min)

            print("min_T {:.1f}".format(min_T))

    return img, i_min


def read_image(fnam, frame=-1, thrs=-20):
    """Open the data file and returns an image.

    Args:
    ----
        fnam: The file path
        indx (int, optional): If an IRB file, this is the image index.

    Returns
    -------
        An image

    """
    ifile = Path(fnam).expanduser().resolve()
    if not ifile.exists():
        print("Input file does not exist.")
        return None, None

    suffix = ifile.suffix.lower()
    img = None, None
    if suffix == ".csv":
        img = CSVImage.CSVImage(ifile), 0

    elif suffix == ".irb":
        irbf = IRBFile.IRBFile(ifile)
        img = get_image_from_irb(irbf, frame, thrs)

    else:
        try:
            irb = IRBFile.IRBFile.load(ifile)
            img = get_image_from_irb(irbf, frame, thrs)

        except Exception as eee:
            print(eee)

    return img


def main(fnam, options):
    """Read data and plot edges."""
    params = IRPetalParam(options)
    params.debug = False

    print("Open file")
    img, _ = read_image(fnam, options.frame, options.thrs)
    if img is None:
        sys.exit()

    # Show original Image
    fig, ax = plt.subplots(1, 1)
    values = get_IR_data(img, False)
    min_T = np.min(values)
    fig.suptitle("Original image - Temp. {:.1f}".format(min_T))
    pcm = ax.imshow(values, origin='lower', cmap="jet")
    fig.colorbar(pcm, ax=ax)
    fig.savefig("original-IR-img.png")

    # Show rotated image
    values = get_IR_data(img, True)
    min_T = np.min(values)
    fig, ax = plt.subplots(1, 1)
    fig.suptitle("Rotated image - Temp. {:.1f}".format(min_T))
    pcm = ax.imshow(values, origin='lower', cmap="jet")
    fig.colorbar(pcm, ax=ax)
    fig.savefig("rotated-IR-image.png")

    # Split image
    left, right = split_IR_image(values)

    # anad show
    print("Draw")
    show_data(left, params, fname="front.png", id=1)
    show_data(right, params, fname="back.png", id=2)

    plt.show()


if __name__ == "__main__":
    P = IRPetalParam()
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument('--frame', default=-1, type=int, help="Frame to analize")
    parser.add_argument("--thrs", type=float, default=-22, help="Temperature threshold")
    parser.add_argument("--distance", type=float,
                        default=P.distance, help="Distance in contour beteween slices")
    parser.add_argument("--npoints", type=int,
                        default=P.npoints, help="Number of points per segment")
    parser.add_argument("--orig", action="store_true",
                        default=False, help="plot the original image")
    parser.add_argument("--do_fit", action="store_true",
                        default=P.do_fit,
                        help="Do a fit to find the minimum in a slice rather than looking returning the minimum value.")
    parser.add_argument("--do_min", dest="do_fit", action="store_false",
                        help="Use the minimum valueo in a slice rather than fitting.")
    parser.add_argument("--debug", action="store_true",
                        default=False,
                        help="debug")

    options = parser.parse_args()
    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()
    else:
        ifile = options.files[0]

    main(ifile, options)
