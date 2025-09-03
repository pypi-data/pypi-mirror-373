"""Parameters needed for the thermal analysis of the petal."""
import sys

class IRPetalParam(object):
    """Default values for IR image handling."""

    def __init__(self, values=None):
        """Initialize.

        Args:
        ----
            values: ArgParser or dict with user values-

        """
        self.institute = None     # Either IFIC or DESY to treat the different files
        self.thrs = -22.0         # the threshold
        self.tco2 = -35.0         # Inlet temperature
        self.gauss_size = 15      # Radius of gausian filtering
        self.grad_sigma = 2.5     # Sigma of grading calculation
        self.distance = 5         # Distance in contour between slices
        self.npoints = 15         # Number of points per segment
        self.min_area = 2500      # minumum area of a valid contour.
        self.contour_cut = 0.2    # Fraction of IR image range to define contour.
        self.contour_smooth = 25  # Value to smooth contour
        self.width = 2            # half widh of rectangle around point in path when getting T.
        self.do_fit = True        # True to fit the segment points.
        self.rotate = True        # Rotate to have a vertical petal in mirror image
        self.debug = False        # To debug
        self.report = False       #
        self.graphana = None      # Graphana server
        self.save_pipes = False   # If true save pipe path
        self.legend = True        # if false do not plot legend
        self.sensor_min = -sys.float_info.max # cut on lower temp for sensor contour average
        self.sensor_max = sys.float_info.max # cut on higher temp for sensor contour average


        if values is not None:
            self.set_values(values)

    def set_values(self, values):
        """Set parameters from input values."""
        if isinstance(values, dict):
            for key in self.__dict__.keys():
                if key in values:
                    setattr(self, key, values[key])

        else:
            for key in self.__dict__.keys():
                if hasattr(values, key):
                    setattr(self, key, getattr(values, key))

    def print(self):
        """Print all values."""
        print("\nParameters:")
        for key, val in self.__dict__.items():
            print("{}: {}".format(key, val))
        print("")

    @staticmethod
    def add_parameters(parser):
        """Add parameters to the ArgumentParser."""
        # Get the default value for the parameters.
        P = IRPetalParam()

        parser.add_argument("--institute", type=str,
                            default=P.institute,
                            help="Either IFIC or DESY to treat the different files")
        parser.add_argument("--thrs", type=float, default=P.thrs, help="Temperature threshold")
        parser.add_argument("--tco2", type=float, default=P.tco2, help="CO2 Inlet temperature")
        parser.add_argument("--graphana", type=str, default=None, help="Graphana server.")
        parser.add_argument("--gauss_size", type=int, default=P.gauss_size, help="Radius of gausian filtering")
        parser.add_argument("--distance", type=float, default=P.distance, help="Distance in contour beteween slices")
        parser.add_argument("--npoints", type=int, default=P.npoints, help="Number of points per segment")
        parser.add_argument("--min_area", type=float, default=P.min_area, help="minumum area of a valid contour")
        parser.add_argument("--width", type=int, default=P.width,
                            help="width of average rectangle en get_T_along_path.")
        parser.add_argument("--contour_cut", type=float, default=P.contour_cut,
                            help="Fraction of IR image range to define contour.")
        parser.add_argument("--contour_smooth", type=float, default=P.contour_smooth,
                            help="Value to smooth contour")
        parser.add_argument("--debug", action="store_true", default=False, help="Show additional information.")
        parser.add_argument("--report", action="store_true", default=False, help="True if figures kept for the report.")
        parser.add_argument("--save_pipes", default=False, action="store_true", help="SAve pipe path. Output is alias_pipe-i.txt")
        parser.add_argument("--no-legend", dest="legend", action="store_false", default=True, help="Do not show the legend in plots.")
        parser.add_argument("--sensor_min", dest="sensor_min", default=P.sensor_min, help="cut on lower temp for sensor contour average")
        parser.add_argument("--sensor_max", dest="sensor_max", default=P.sensor_max, help="cut on higher temp for sensor contour average")
