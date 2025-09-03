"""Encapsulates different data structure at DESY and IFIC.
"""
import sys
from pathlib import Path
import numpy as np

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())


from petal_qc.thermal import IRPetal
from petal_qc.thermal import Petal_IR_Analysis

HAS_GRAPHANA = False
try:
    from petal_qc.utils.readGraphana import ReadGraphana
    HAS_GRAPHANA = True

except ImportError:
    HAS_GRAPHANA = False



class IRDataGetter(object):
    """BAse class defining the interface."""

    def __init__(self):
        """Initialization."""
        self.factor = 1
        self.indx = -1
        return

    @staticmethod
    def factory(institute, params):
        """Returns the data getter corresponding to the given institute."""
        if institute == "DESY":
            out = IRDataDESY()

        elif institute == "IFIC":
            out = IRDataIFIC()

        else:
            raise NotImplementedError

        out.fine_tune_params(params)
        return out

    def fine_tune_params(self, param):
        """Set default values for the parameters."""
        param.sensor_max = -5
        return

    def get_IR_data(self, image, **kargs):
        """_summary_

        Args:
        ----
            image (IRBImage): the input IRB image
            kargs: keyword arguments to pass.

        """
        return

    def find_reference_image(self, irbf, *args, **kargs):
        """Find first image in sequence with T < T_min.

        Args:
        ----
            irbf: The sequence of IR images
            T_min: The temperature threshold
            kargs (keyword arguments): keyword arguments

        Returns
        -------
            min_T, i_min, values: The actual temperature of the image,
                                  the sequence nubmer
                                  and the array of values (a 2d array)


        """
        return 0, 0, []

    def extract_pipe_path(self, image, params) -> list:
        """Extract the "pipe path"  in a petal IR image.

        Args:
        ----
            image (mdarray): The 2D array containing the input image
            params: IRPetalPam object with options.

        Returns
        -------
            pipe: the list of pipe contours or paths.

        """
        return []

    def analyze_IR_image(self, img, pipe, sensors, iside, params):
        """Analyze the IR image at input.

        Args:
        ----
            img (IRBImage): THe image
            pipes: The pipe
            sensors: The sensor areas
            iside: petal image with EoS on the left(0) or right (1)
            params: IRPetal parameters

        Returns
        -------
            An array of AnalysisResult objects.

        """
        return

    def get_analysis_frame(self, irbf):
        """Get the frame where we want to perform the analysis."""
        return None

    def get_inlet_temperature(self):
        """REturn the inlet temperature."""
        return -9999


class IRDataIFIC(IRDataGetter):
    """Gets data for IFIC analysis."""

    def __init__(self) -> None:
        """Initialization."""
        super().__init__()
        self.analysis_frame = None
        if HAS_GRAPHANA:
            #self.DB = ReadGraphana("localhost")
            self.DB = ReadGraphana()
        else:
            self.DB = None

    def find_reference_image(self, irbf, *args, **kargs):
        """Find first image in sequence with T < T_min.

        Args:
        ----
            irbf: The sequence of IR images
            T_min: The temperature threshold
            kargs (keyword arguments): keyword arguments

        Returns
        -------
            min_T, i_min, values: The actual temperature of the image,
                                  the sequence nubmer
                                  and the array of values (a 2d array)


        """
        irbf.set_concatenate(True)
        frame = self.get_analysis_frame(irbf)
        i_min = self.indx[-1]
        min_T = np.min(frame[0].image)
        values = self.get_IR_data(frame[0])
        return min_T, i_min, [values, ]

        #  if len(args) == 0:
        #      T_min = -22.0
        #  else:
        #      T_min = args[0]
        #
        #  irbf.set_concatenate(True)
        #  min_T, i_min, ref_img = IRPetal.find_reference_image(irbf, T_min)
        #  values = self.get_IR_data(ref_img)
        #  self.factor = values.shape[0]/640
        #
        #  return min_T, i_min, [values, ]

    def get_IR_data(self, image, **kargs):
        """Get the data from the image in the proper orientation.

        Proper orientation means that petals are vertical (in the  mirror image).
        It will eventually try to rotate the image to compensate a camera rotation.

        Args:
        ----
            image: IRBimage. If a list of IRBFile objects is given, only the frist is taken.
            rotate: True to make the rotation compensation.

        Returns
        -------
            2d array: The 2d array wit the temperature data.

        """
        if isinstance(image, list) or isinstance(image, tuple):
            image = image[0]

        nrow, ncol = image.image.shape
        landscape = (ncol > nrow)

        if landscape:
            values = image.image.T
        else:
            values = image.image

        rotate = False
        if 'rotate' in kargs:
            rotate = kargs['rotate']

        if rotate:
            values = IRPetal.rotate_full_image(values)

        return values

    def extract_pipe_path(self, image, params) -> list:
        """Extract the "pipe path"  in a petal IR image.

        Args:
        ----
            image(ndarray): The 2D array containing the 2 specular images
            params: IRPetalPam object with options.

        Returns
        -------
            pipe: the list of pipe contours or paths.

        """
        try:
            pipes = IRPetal.extract_mirrored_pipe_path(image, params)
        except Exception:
            pipes = IRPetal.extract_mirrored_pipe_path(image[0], params)
        return pipes

    def analyze_IR_image(self, img, pipe, sensors, iside, params):
        """IFIC implementation.

        Analyzes an image with specular images of petal core.

        Inputs have same meaning as bas eclass but are arrays with the 2 core sides.
        """
        res, _ = Petal_IR_Analysis.analyze_IR_mirrored_image(img, pipe, sensors, params)
        return res

    @staticmethod
    def find_minimum(values):
        """Find minima in series."""
        indx = []

        for i, v in enumerate(values):
            if i == 0:
                vprev = v
                continue

            try:
                vnext = values[i+1]
            except IndexError:
                continue

            if vprev > v and vnext > v:
                indx.append(i)

            vprev = v

        return indx

    def get_analysis_frame(self, irbf):
        """Get the frame where we want to perform the analysis.

        IFIC takes the minimum of the last cycle.
        """
        # Get all the temperatures
        min_T = []
        for img in irbf.images():
            min_T.append(np.min(img[0].image))

        self.indx = IRDataIFIC.find_minimum(min_T)
        self.analysis_frame = [irbf.getImage(self.indx[-1])]
        return self.analysis_frame

    def get_inlet_temperature(self):
        """REturn the inlet temperature."""
        if self.DB:
            img = self.analysis_frame[0]
            X, T = self.DB.get_temperature(img.timestamp, 1)
            return np.min(T)

        else:
            return -9999



class IRDataDESY(IRDataGetter):
    """Gets data for DESY."""

    def __init__(self) -> None:
        """Initialization."""
        super().__init__()

    def fine_tune_params(self, param):
        """Set default values for the parameters."""
        param.distance = 16
        param.width = 16
        param.sensor_max = -5

    def get_IR_data(self, image, **kargs):
        """Get the data from the image in the proper orientation.

        Args:
        ----
            image: IRBimage
            kargs: keyword arguments

        Returns
        -------
            2d array: The 2d array wit the temperature data.

        """
        try:
            values = np.rot90(image.image)
        except Exception:
            values = []
            for img in image:
                values.append(np.rot90(img.image))

        return values

    def find_reference_image(self, irbf, *args, **kargs):
        """DESY wants the average of all images in the sequence.

        Args:
        ----
            irbf: The sequence of IR images
            args: The temperature threshold
            kargs (keyword arguments): keyword arguments

        Returns
        -------
            min_T, i_min, values: The actual temperature of the image,
                                  the sequence nubmer
                                  and the array of values (a 2d array)

        """
        if 'nframes' in kargs:
            nframes = kargs['nframes']
        else:
            nframes = -1

        min_T = 1e50
        i_min = -1
        try:
            avg_img = irbf.append_average(nframes=nframes)
            for img in avg_img:
                val = np.min(img.image)
                if val < min_T:
                    min_T = val

            i_min = irbf.nimages-1
            values = self.get_IR_data(avg_img)

        except AttributeError:
            # We have 2 files, one front y the second back
            values = []
            factors = []
            for ifile in irbf:
                val = self.get_IR_data(ifile.getImage(0))
                Tmin = np.min(val)
                if Tmin < min_T:
                    min_T = Tmin
                    i_min = 0
                values.append(val)

        factors = []
        for img in values:
            factors.append(img.shape[0]/640)
        self.factor = max(factors)

        return min_T, i_min, values

    def extract_pipe_path(self, image, params) -> list:
        """Extract the "pipe path"  in a petal IR image.

        Args:
            image(list(ndarray)): The array of 2D arrays containing the images
            params: IRPetalPam object with options.

        Returns
            pipe: the list of pipe contours or paths.

        """
        pipes = []
        points_3d = []
        for img in image:
            pipe = IRPetal.extract_pipe_path(img, params)
            points_3d.append(IRPetal.get_all_3d_points())
            pipes.append(pipe)

        IRPetal.set_all_3d_points(points_3d)
        IRPetal.set_images(image)
        return pipes

    def analyze_IR_image(self, img, pipes, sensors, iside, params):
        """DESY implementation.

        Only one petal side at imput.
        """
        if isinstance(img, list):
            res = Petal_IR_Analysis.analyze_IR_image_list(img, pipes, sensors, params)
            return res

        else:
            res = Petal_IR_Analysis.analyze_IR_image(img, pipes[0], sensors[0], iside[0], params)
            if iside[0]:
                return [None, res]
            else:
                return [res, None]

    def get_analysis_frame(self, irbf):
        """Get the frame where we want to perform the analysis.

        DESY gets the average of all frames.
        """
        try:
            if not irbf.has_average:
                irbf.append_average(nframes=5)

            return [v[-1] for v in irbf.file_images]

        except AttributeError:
            return [irbf[0].getImage(0), irbf[1].getImage(0)]