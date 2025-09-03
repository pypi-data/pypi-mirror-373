"""Find point clisters."""
import math

import numpy as np


class Cluster(object):
    """A cluster."""

    def __init__(self, x=0, y=0, z=0):
        """Initialize the cluster."""
        self.x = x
        self.y = y
        self.z = z
        self.N = 0.0
        self.points = []
        self.xtra = []

    def add(self, P, xtra=None):
        """Add a new point."""
        N = self.N + 1.0
        self.x = (self.x * self.N + P[0])/N
        self.y = (self.y * self.N + P[1])/N
        try:
            self.z = (self.z * self.N + P[2])/N

        except IndexError:
            pass

        self.N += 1.0
        self.points.append(P)
        self.xtra.append(xtra)

    def get_points(self):
        """Return the array of points."""
        return np.array(self.points)

    def distance(self, P):
        """Compute distance to Point."""
        dist = math.sqrt((self.x-P[0])**2 + (self.y-P[1])**2)
        return dist

    def __lt__(self, other):
        """Sort two clusters.

        A cluster is smaller if has smaller Y.
        """
        return self.y < other.y


def cluster_points(points, distance):
    """Cluster Points.

    Group the points in clusters formed by points whose
    distance is smaller than distance

    Args:
    ----
        points (list): list of points in the for  [x, y, z] or equivalent
        distance (float): distance.

    Returns
    -------
        list: List of Clusters

    """
    # Cluster points which are closer than distance.
    clusters = []
    for ipoint, P in enumerate(points):
        if np.isnan(P[0]) or np.isnan(P[1]):
            continue

        dist_min = 1e9
        clst_min = -1
        for iclst, C in enumerate(clusters):
            dist = C.distance(P)
            if dist < dist_min:
                clst_min = iclst
                dist_min = dist

        if clst_min < 0 or dist_min > distance:
            C = Cluster()
            C.add(P, ipoint)
            clusters.append(C)

        else:
            clusters[clst_min].add(P, ipoint)

    clusters.sort(key=lambda x: x.N, reverse=True)
    return clusters
