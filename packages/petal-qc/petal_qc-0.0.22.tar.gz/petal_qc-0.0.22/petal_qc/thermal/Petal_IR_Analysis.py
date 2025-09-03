"""Store resutls."""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from petal_qc.thermal import IRPetal
from petal_qc.thermal import contours
from petal_qc.thermal.PetalColorMaps import HighContrast


class AnalysisResult(object):
    """Contains results of IR image analysis."""

    def __init__(self) -> None:
        """Initialization."""
        self.path_length = []  # position within pipe (0 U-bend at bottom)
        self.path_temp = []    # temperatrure at given positions
        self.path_spread = []  # spread at given positions
        self.sensor_avg = []   # average on sensors
        self.sensor_std = []   # spread on sensors

    def from_json(self, J):
        """Get values from JSon."""
        for key in self.__dict__.keys():
            try:
                if hasattr(self, key):
                    setattr(self, key, np.array(J[key]))

            except Exception:
                print("AnalysisResult.from_json: Ignoring {} component".format(key))
                continue


def show_2D_image(img, title=None, show_fig=True):
    """Show a 2D image."""
    if isinstance(img, list):
        fig, ax = plt.subplots(1, len(img))
        if title:
            fig.suptitle(title)

        if len(img) == 1:
            ax = [ax, ]

        for i, im in enumerate(img):
            pcm = ax[i].imshow(im, origin='lower', cmap=HighContrast.reversed())  # cmap="jet")
            fig.colorbar(pcm, ax=ax[i])

    else:
        fig, ax = plt.subplots(1, 1)
        if title:
            fig.suptitle(title)
        pcm = ax.imshow(img, origin='lower', cmap=HighContrast.reversed())  # cmap="jet")
        fig.colorbar(pcm, ax=ax)

    if show_fig:
        plt.draw()
        plt.pause(0.001)

    return fig, ax


def analyze_IR_image(img, pipe, sensors, iside, params) -> AnalysisResult:
    """Analyze the IR image at input.

    Args:
    ----
        img (ndarray): THe image
        pipes: The pipe
        sensors: The sensor areas
        iside: petal image with EoS on the left(0) or right (1)
        params: IRPetal parameters

    Returns
    -------
        An AnalysisResult object.

    """
    sensor_order = [
        [0, 1, 2, 4, 3, 6, 5, 9, 8, 7],
        [0, 1, 2, 3, 4, 5, 6, 8, 9, 7]
    ]
    width = 25
    if img.shape[0] > 700:
        width = 2*width

    result = AnalysisResult()
    result.path_temp, result.path_length = IRPetal.get_T_along_path(pipe, img, params.width, True)
    result.path_spread, pL = IRPetal.get_spread_along_path(pipe, img, width, True)
    Savg = []
    Sstd = []
    for S in sensors:
        avg, std = contours.get_average_in_contour(img, S, tmin=params.sensor_min, tmax=params.sensor_max)
        Savg.append(avg)
        Sstd.append(std)

    result.sensor_avg = [Savg[sensor_order[iside][j]] for j in range(10)]
    result.sensor_std = [Sstd[sensor_order[iside][j]] for j in range(10)]

    return result


def analyze_IR_image_list(imgs, pipes, sensors, params):
    """Analyze a list of IR images at input.

    Args:
    ----
        img (list(IRBImage)): THe images. Assumed to be type0, type1, type0, type1...
        pipes: The pipes
        sensors: The sensor areas
        params: IRPetal parameters

    Returns
    -------
        list of AnalysisResult objects

    """
    out = []
    for i, img in enumerate(imgs):
        j = i % 2
        res = analyze_IR_image(img, pipes[j], sensors[j], j, params)
        out.append(res)

    return out


def analyze_IR_mirrored_image(img, pipes, sensors, params):
    """Analyze the mirrored IR image at input.

    Args:
    ----
        img (IRBImage): THe image
        pipes: The pipes
        sensors: The sensor areas
        params: IRPetal parameters

    Returns
    -------
        list of AnalysisResult objects
        images: the image data

    """
    images = IRPetal.get_mirrored_petal_images(img, params)
    results = analyze_IR_image_list(images, pipes, sensors, params)
    return results, images
