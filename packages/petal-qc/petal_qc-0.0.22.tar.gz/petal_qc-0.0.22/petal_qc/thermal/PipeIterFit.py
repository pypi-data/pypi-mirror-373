import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt



cwd = Path(__file__).parent
if cwd.exists():
    sys.path.insert(0, cwd.as_posix())

from petal_qc.thermal import PipeFit, contours


class PipeIterFit:
    """makes an iterative fit removing outliers in each iteration."""

    def __init__(self, data):
        """Initialize class."""
        self.data = data
        ptype = PipeFit.PipeFit.guess_pipe_type(data)
        self.PF = PipeFit.PipeFit(ptype)

    def remove_outsiders(self, data, thrs):
        """Removes points which are further than thrs from the fit."""
        D = np.zeros(len(data))
        out = self.PF.transform_data(data, self.PF.R)
        i = 0
        for x, y in out:
            dst, P = contours.find_closest_point(x, y, self.PF.pipe)
            D[i] = dst
            i += 1

        indx = np.where(D < thrs)[0]
        return np.array(data[indx, :])

    def fit(self, threshold=20, factor=1.0):
        total_data = self.data
        data_size = len(total_data)

        fig, ax = plt.subplots(1, 1, tight_layout=True)

        M0 = self.PF.fit_ex(total_data, factor=factor)
        sample_data = self.remove_outsiders(self.PF.data, threshold)
        last_size = len(sample_data)

        # Adaptively determining the number of iterations
        while True:
            M0 = self.PF.fit_ex(sample_data, M0=M0, factor=factor, simplify=False)

            out = self.PF.transform_data(self.PF.data, M0)
            D = []
            for x, y in out:
                dst, P = contours.find_closest_point(x, y, self.PF.pipe)
                D.append(dst)

            ax.clear()
            ax.hist(D)
            plt.draw()
            plt.pause(0.0001)
            self.PF.plot()

            sample_data = self.remove_outsiders(self.PF.data, 20)
            sample_size = len(sample_data)
            if sample_size == last_size:
                break

            last_size = sample_size

        self.PF.plot()
        return M0

    def plot(self):
        self.PF.plot()
