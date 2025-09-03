#!/usr/bin/envp python3
"""Class encapsulating debug plots."""
import matplotlib.pyplot as plt


class DebugPlot(object):
    """Handles debugging figures and plots."""

    def __init__(self):
        """Initialization."""
        self.ax = {}
        self.fig = {}
        n_fig = 0

    def setup_debug(self, f_id, nrow=1, ncol=1, is_3d=False, fig_kw={}):
        """Prepare debug figure with given identifier.

        Args:
        ----
            f_id (): Identifier. Use it later to get the figure associated.
            nrow (int, optional): Number of rows. Defaults to 1.
            ncol (int, optional): Number of columns. Defaults to 1.
            is_3d (boolean): if True prepares a 3D figure.
            fig_kw: rest of keywords for plt.subplots or figure.

        """
        if f_id not in self.ax:
            if is_3d:
                fig = plt.figure(tight_layout=True, **fig_kw)
                ax = fig.add_subplot(1, 1, 1, projection='3d')
            else:
                fig, ax = plt.subplots(nrow, ncol, tight_layout=True, **fig_kw)

            self.ax[f_id] = ax
            self.fig[f_id] = fig

    def get_ax(self, f_id):
        """Return the axes associated to f_id."""
        return self.ax[f_id]

    def get_fig(self, f_id):
        """Return the Figure associated to f_id."""
        return self.fig[f_id]

    def plot(self, f_id, *args):
        """Plot in axes associated to f_id."""
        if f_id not in self.ax:
            return

        self.ax[f_id].clear()
        self.ax[f_id].plot(*args)
        plt.draw()
        plt.pause(0.001)

    def plotx(self, f_id, *args):
        """Draws."""
        if f_id not in self.ax:
            return

        self.ax[f_id].plot(*args)
        plt.draw()
        plt.pause(0.001)

    def set_title(self, f_id, title):
        """Set title to axes."""
        if f_id not in self.ax:
            return

        self.ax[f_id].set_title(title)

    def savefig(self, f_id, fname, **kwargs):
        """Saves the figure."""
        if f_id not in self.ax:
            return

        self.fig[f_id].savefig(fname, **kwargs)
