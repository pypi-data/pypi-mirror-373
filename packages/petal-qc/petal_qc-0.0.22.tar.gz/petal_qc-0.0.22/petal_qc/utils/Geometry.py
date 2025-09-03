"""A collection of methods t ocompute flatness or fit points to a plame."""
import math
from inspect import isfunction

import numpy as np
import numpy.linalg as linalg
from scipy.spatial import Delaunay, ConvexHull


def vector_angle(v1, v2):
    """Copmpute angle between given vectors."""
    u1 = v1 / linalg.norm(v1)
    u2 = v2 / linalg.norm(v2)

    y = u1 - u2
    x = u1 + u2

    a0 = 2 * np.arctan(linalg.norm(y) / linalg.norm(x))

    if (not np.signbit(a0)) or np.signbit(np.pi - a0):
        return a0
    elif np.signbit(a0):
        return 0.0
    else:
        return np.pi


def flatness_LSPL(M):
    """Compute flatness according to least squares reference plane method.

    ISO/TS 12781-1

    Args:
        M (np.ndarray): The data nx3 array

    Return
        (float) - the computed flatness
    """

    # calculate the center of mass and translate all points
    com = np.sum(M, axis=0) / len(M)
    q = M - com

    # calculate 3x3 matrix. The inner product returns total sum of 3x3 matrix
    Q = np.dot(q.T, q)

    # Calculate eigenvalues and eigenvectors
    la, vectors = np.linalg.eig(Q)

    # Extract the eigenvector of the minimum eigenvalue
    n = vectors.T[np.argmin(la)]

    e = np.dot(q, n)

    eplus = abs(np.amax(e[np.where(e > 0)]))
    eminus = abs(np.amin(e[np.where(e < 0)]))

    flatness = eplus + eminus
    return flatness


def flatness_conhull(M):
    """Compute (MZPL) flatness by convex hull algorithm.

    Robust Convex Hull-based Algoritm for Straightness and Flatness
    Determination in Coordinate Measuring (Gyula Hermann)

    Args:
        M: point array of size (npoints, ndim)

    Returns
    -------
        flatness - the computed flatness

    """
    X = M[:, 0]
    Y = M[:, 1]
    Z = M[:, 2]
    max_dis_local = []
    hull = ConvexHull(M, incremental=False, qhull_options=None)
    for plane in hull.equations:
        dis = np.abs(plane[0] * X[:] + plane[1] * Y[:] + plane[2] * Z[:] + plane[3])
        max_dis_local.append(np.max(dis))

    return np.min(max_dis_local)


def flatness_conhull_old(M):
    """Compute flatness by convex hull algorithm.

    Robust Convex Hull-based Algoritm for Straightness and Flatness
    Determination in Coordinate Measuring (Gyula Hermann)

    Args:
        M: point array of size (npoints, ndim)

    Returns
    -------
        flatness - the computed flatness

    """
    X = M[:, 0]
    Y = M[:, 1]
    Z = M[:, 2]
    ch = Delaunay(M).convex_hull

    N = ch.shape[0]
    max_dis_local = np.zeros([N, 1])
    for i in range(0, N):
        P1 = np.array([X[ch[i, 0]], Y[ch[i, 0]], Z[ch[i, 0]]])
        P2 = np.array([X[ch[i, 1]], Y[ch[i, 1]], Z[ch[i, 1]]])
        P3 = np.array([X[ch[i, 2]], Y[ch[i, 2]], Z[ch[i, 2]]])

        normal = np.cross(P1-P2, P1-P3)

        D = -normal[0] * P3[0] - normal[1] * P3[1] - normal[2] * P3[2]

        plano_0 = np.array([normal[0], normal[1], normal[2], D])
        plano = plano_0 / np.sqrt(np.sum(plano_0**2))

        dis = np.abs(plano[0] * X[:] + plano[1] * Y[:] + plano[2] * Z[:] +
                     plano[3]) / np.sqrt(plano[0]**2 + plano[1]**2 + plano[2]**2)

        max_dis_local[i] = np.max(dis)

        # planos(i, :) = plano(:);

    return np.min(max_dis_local)
    # plano_opt = planos(find(max_dis_local == flatness), :);


def project_to_plane(data, V, M=None):
    """Project data points to a plane.

    Args:
    ----
        data (array): Data array
        V (matrix): The transformation matrix
        M (vector): The mean value of the data

    Returns
    -------
        array: the data projectoed onto the plane.

    """
    npts = data.shape[0]
    out = np.zeros(data.shape)

    if M is not None:
        for i in range(0, npts):
            out[i, :] = np.dot(data[i, :] - M, V)

    else:
        for i in range(0, npts):
            out[i, :] = np.dot(data[i, :], V)

    return out


def fit_plane(data, use_average=7):
    """Fit plane where Z dispersion is smaller.

    This is the plane defined by the eigenvector with smaller eigenvalue
    of the covariance matrix of the data.

    Args:
    -----
        data: The data
        use_average: bitted word telling which components of average
                     should be used.

    Returns
    -------
        val: the data in the new reference
        V: the eigenvectors
        M: the "center of gravity" of the plane
        L: the eigenvalues

    """
    M = np.mean(data, 0)
    cmtx = np.cov(np.transpose(data))
    L, V = linalg.eig(cmtx)

    # We assume the rotation is not too big and unit vectors are
    # close to the original ux, uy and uz
    idx = []
    for i in range(0, V.shape[0]):
        v = np.abs(V[:, i])
        mx = np.amax(v)
        ix = np.where(v == mx)[0][0]
        idx.append(ix)

    NV = np.zeros(V.shape)
    NL = np.zeros(L.shape)
    for i, j in enumerate(idx):
        NV[:, j] = V[:, i]
        NL[j] = L[i]

    for i in range(0, 3):
        if NV[i, i] < 0:
            NV[:, i] = -NV[:, i]

    avg = np.array([0., 0., 0.])
    for i in range(0, 3):
        if (1 << i & use_average):
            avg[i] = M[i]

    return project_to_plane(data, NV, avg), NV, M, NL


def remove_outliers_indx(data, cut=2.0, debug=False):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        debug: be verbose if True.

    Returns
    -------
        index of valid pints in data array.

    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    indx = np.where(s < cut)[0]
    return indx


def remove_outliers(data, cut, zlimit=1e25):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        zlimit: limit for Z Defaults to 1e25.

    """
    # move to the
    val, V, M, L = fit_plane(data)
    npts = val.shape[0]
    ipoint = 0
    vout = np.zeros([npts, 3])
    rms = math.sqrt(L[0])
    for i in range(0, npts):
        sn = abs(val[i, 2]-M[2])/rms
        if sn < cut:
            vout[ipoint, :] = data[i, :]
            ipoint = ipoint + 1

    return vout[0:ipoint, :]


def __remove_outliers(data, cut=2.0, debug=False):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        debug: be bverbose if True

    """
    # move to the
    val, V, M, L = fit_plane(data)
    Z = val[:, 2]
    d = np.abs(Z - np.median(Z))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < cut, :]


class Point(object):
    """Represents a point in a 2D space."""

    def __init__(self, x=None, y=None, name=None):
        """Initialization of a Point object.

        Arguments are coordinates and optionally a name.
        It can be initialized with individual values of
        X and Y, with tuplles or arrays or with Point objects.

        """
        self.x = None
        self.y = None

        if name:
            self.name = name
        else:
            self.name = "Point"

        if x is not None:
            if isinstance(x, Point):
                self.x = x.x
                self.y = x.y
            else:
                try:
                    self.x = float(x[0])
                    self.y = float(x[1])
                except (TypeError, IndexError):
                    try:
                        self.x = float(x)
                    except ValueError:
                        self.x = None

                    try:
                        self.y = float(y)
                    except ValueError:
                        self.y = None

    def __sub__(self, other):
        """Defference between 2 Point objects."""
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            return NotImplemented

    def __add__(self, other):
        """Addtion of 2 Point objects."""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            return NotImplemented

    def __mul__(self, other):
        """Scalar product of 2 Point objects."""
        if isinstance(other, Point):
            return self.x * other.x + self.y * other.y
        elif isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        """Multiplication by float or int."""
        if isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other)
        else:
            return NotImplemented

    def __eq__(self, other):
        """Checks for equality."""
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented

    def __ne__(self, other):
        """Checks for non equality."""
        if isinstance(other, Point):
            return self.x != other.x or self.y != other.y
        else:
            return NotImplemented

    def __lt__(self, other):
        """Lees than operator.

        A point is smaller than other if its magnitude is smaller.
        """
        if isinstance(other, Point):
            return self.mag() < other.mag()
        else:
            return NotImplemented

    def __gt__(self, other):
        """Greater than operator.

        A point is greater than other if its magnitude is greater.
        """
        if isinstance(other, Point):
            return self.mag() > other.mag()
        else:
            return NotImplemented

    def __le__(self, other):
        """Lees or equal.

        Here equality refers to magnitude.
        """
        if isinstance(other, Point):
            return self.mag() <= other.mag()
        else:
            return NotImplemented

    def __ge__(self, other):
        """Greater or equal.

        Here equality refers to magnitude.
        """
        if isinstance(other, Point):
            return self.mag() >= other.mag()
        else:
            return NotImplemented

    def __neg__(self):
        """Unary minus."""
        return Point(-self.x, -self.y)

    def mag(self):
        """Return the length or magnitude."""
        return math.sqrt(self.x*self.x + self.y*self.y)

    def mag2(self):
        """The squared of the magnitud."""
        return self.x*self.x + self.y*self.y

    def norm(self):
        """Return unit vector."""
        v = self.mag()
        return Point(self.x/v, self.y/v)

    def angle(self, P):
        """Return angle with given point."""
        return math.atan2(P.cross(self), P.dot(self))

    def cw(self):
        """Return a point like this rotated +90 degrees."""
        return Point(-self.y, self.x)

    def ccw(self):
        """Return a point like this rotated -90 degress."""
        return Point(self.y, -self.x)

    def dot(self, a):
        """Dot product with given vector."""
        return self.x * a.x + self.y * a.y

    def cross(self, b):
        """Cross product with given vector."""
        return self.dot(b.cw())

    def phi(self):
        """Phi or azimutal angle of vector."""
        return math.atan2(self.y, self.x)

    def valid(self):
        """Tells if the point has valid values."""
        if self.x is None or self.y is None:
            return False
        else:
            return True

    def distance(self, other):
        """Distance to a Point or Line."""
        if isinstance(other, Point):
            dd = (self-other).mag()
            return dd
        elif isinstance(other, Line):
            ff = math.sqrt(other.A()**2 + other.B()**2)
            dd = other.A()*self[0] + other.B()*self[1] + other.C()
            return dd/ff
        else:
            raise ValueError

    def unit(self):
        """Returns a unit vector from this one."""
        return (1.0/self.mag())*self

    def __getitem__(self, key):
        """Implement the getitem interface."""
        if key < 0 or key > 1:
            raise IndexError
        elif key == 0:
            return self.x
        else:
            return self.y

    def __setitem__(self, key, val):
        """Implement the setitem interface."""
        if key < 0 or key > 2:
            raise IndexError
        elif key == 0:
            self.x = val
        else:
            self.y = val

    def __len__(self):
        """Return length."""
        return 2

    def __str__(self):
        """String representation."""
        return "%f,%f" % (self.x, self.y)

    def __repr__(self):
        """String representation."""
        return "Point(%f, %f)" % (self.x, self.y)


def dot(a, b):
    """Dot product."""
    return a.x*b.x + a.y*b.y


def cross(a, b):
    """Cross product."""
    return dot(a, b.cw())


class Line(object):
    """Represents a line.

    We store the slope (m) and  the intercept (b)

    """

    def __init__(self, m=None, n=None):
        """Line creation.

        We create the line in various forms:
            1) m and n are floats: the slope intercept form
            2) m is a float and n is a Point: line with that slope passing
               through the given point
            3) m and n are points: line passing through 2 points
               V = n - m
               O = m
        """
        self.P1 = None
        self.P2 = None
        if isinstance(m, Point):
            self.P1 = m
            if isinstance(n, Point):
                self.P2 = n
                delta_x = (n.x - m.x)
                delta_y = (n.y - m.y)
                if delta_x == 0.0:  # vertical line
                    self.O = Point(n.x, n.y)
                    self.V = (m-n).unit()
                    self.m = None
                    self.b = None
                    return

                self.m = delta_y/delta_x
                self.b = -self.m * n.x + n.y
                self.O = Point(m.x, m.y)
                self.delta = Point(delta_x, delta_y)
                self.V = self.delta.norm()

            else:  # n has to be a number
                self.m = n
                self.b = -self.m * m.x + m.y
                alpha = math.atan(n)
                self.O = m
                self.V = Point(math.cos(alpha), math.sin(alpha))
                self.delta = self.V

        else:  # m has to be a number
            if isinstance(n, Point):
                self.m = m
                self.b = - self.m * n.x + n.y
                alpha = math.atan(m)
                self.O = n
                self.V = Point(math.cos(alpha), math.sin(alpha))
                self.delta = self.V
            else:
                self.m = m
                self.b = n
                alpha = math.atan(m)
                self.O = Point(0., n)
                self.V = Point(math.cos(alpha), math.sin(alpha))
                self.delta = self.V

    def __str__(self):
        """Stringrerpresentation."""
        return "Line(%f, %f)" % (self.m, self.b)

    def A(self):
        """A coeff."""
        return self.m

    def B(self):
        """B coeff."""
        return -1

    def C(self):
        """C coeff."""
        return self.b

    def eval(self, x):
        """Evaluates the line."""
        if self.m:
            return self.m * x + self.b

        else:
            return self.b

    def param(self, t):
        """Return point corresponding to given parameter."""
        out = self.O + t*self.V
        if not isinstance(out, Point):
            out = Point(out)

        return out

    def __call__(self, x):
        """Line evaluation.

        Evaluates the line in parametric form x=0 gives P0, and x=1 gives P1
        """
        out = self.O + x*self.delta
        return out

    def line_perpendicular_at_point(self, P):
        """Return the line perpendicular passing by point."""
        if self.m==0:
            P0 = Point(P.x, P.y+1.0)
            L = Line(P0, P)
        else:
            L = Line(-1.0/self.m, P)

        return L

    def line_parallel_at_distance(self, d):
        """Returns the line parallel to this one which is at a distance d."""
        if not self.m:
            P = Point(self.O.x + d, 0)
            V = Point(self.O.x + d, 1)
            return Line(P, V)

        else:
            new_m = self.m
            new_b = self.b + d * math.sqrt(1 + self.m*self.m)
            return Line(new_m, new_b)

    def line_at_angle(self, angle, center=None):
        """Returns a line which forms an angle w.r.t center."""
        if not center:
            center = self.O
        else:
            res = center.y - (self.m * center.x + self.b)
            if abs(res) > 1e-10:
                raise Exception("Line.line_at_angle: center does not belong to line")

        ca = math.cos(angle)
        sa = math.sin(angle)
        bx = self.V.x * ca - self.V.y * sa
        by2 = 1.0-bx*bx
        if by2 < 0:
            bx = self.V.x * ca + self.V.y * sa
            by2 = 1.0 - bx*bx

        by = math.sqrt(by2)
        b = Point(bx, by)
        b1 = center + b
        return Line(center, b1)

    def line_angle(self, P=None):
        """Returns the angle with a given direction."""
        if not P:
            P = Point(1.0, 0.0)

        return P.angle(self.V)

    def angle(self, other):
        """Angle between 2 lines."""
        angle = math.atan((other.m-self.m)/(1+self.m*other.m))
        return angle

    def cross_point(self, other):
        """Intersection point."""
        if self.m is None:
            # vertical line
            if other.m is None:
                raise Exception("Parallel Lines")
            else:
                x = self.O.x
                y = other.m*x + other.b
                return Point(x, y)

        if other.m is None:
            return other.cross_point(self)

        D = other.m - self.m
        if D == 0.:
            raise Exception("Parallel Lines")

        x = (self.b - other.b)/D
        y = (-self.m*other.b + other.m*self.b)/D

        return Point(x, y)

    def is_parallel(self, other):
        """True if given line is parallel."""
        return self.m == other.m

    def is_perpendicular(self, other):
        """True if given line is perpendicular."""
        return self.m*other.m == -1.0

    def cross_circle(self, C, R, tmin, tmax):
        """Computes the crossing point with a circle.

        C: the center of the circle
        R: the radius
        tmin, tmax : angles limiting the crossing point or
                        tmin = function to accept a point
                        tmax ignored
        """
        a = self.m
        b = self.b
        c = C.x
        d = C.y
        func = None

        if isfunction(tmin):
            func = tmin

        else:
            if tmin < 0:
                tmin += 2*math.pi

            if tmax < 0:
                tmax += 2*math.pi

            if tmin > tmax:
                tmp = tmax
                tmax = tmin
                tmin = tmp

        xx = a*a+1.0
        det = xx*R*R - d*d + 2.0*d*(a*c+b) - a*a*c*c - 2.0*a*b*c-b*b
        if det < 0:
            return None

        det = math.sqrt(det)
        yy = a*(d-b)+c
        x1 = (det-yy)/xx
        x2 = (det+yy)/xx

        p1 = Point(x1, a*x1+b)
        p2 = Point(x2, a*x2+b)

        if func:
            if func(p1, R, C):
                return p1
            elif func(p2, R, C):
                return p2
            else:
                return None

        else:
            V = (p1-C)
            dd = V.phi()
            if dd < 0.0:
                dd += 2*math.pi

            if tmin < dd and dd < tmax:
                return p1

            V = (p2-C)
            dd = V.phi()
            if dd < 0.0:
                dd += 2*math.pi

            if tmin < dd and dd < tmax:
                return p2

            return None
