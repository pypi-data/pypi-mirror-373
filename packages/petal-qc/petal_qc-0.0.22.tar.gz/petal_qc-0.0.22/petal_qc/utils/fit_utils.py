#!/usr/bin/env python3
"""A number of utils to make fits with numpy."""
import matplotlib.pyplot as plt
import numpy as np
from lmfit.models import GaussianModel
from scipy.signal import find_peaks
# from scipy.stats import moyal as landau

log2 = np.log(2)
s2pi = np.sqrt(2*np.pi)
spi = np.sqrt(np.pi)
s2 = np.sqrt(2.0)
tiny = np.finfo(np.float64).eps


def fit_gaussian(n, X, center, width=5.0, amplitude=1):
    """Fit a gaussion.

    Args:
    ----
        n: The bins
        X: the bin edges
        center: The center (or mean) of the gaussian.
        width: the sigma estimate of the gaussion. Defaults to 5.0.
        amplitude: the estimae of the amplitude. Defaults to 1.

    Returns
    -------
        the fit result and a legend

    """
    model = GaussianModel()
    params = model.make_params(amplitude=amplitude, center=center, sigma=width)
    result = model.fit(n, params, x=X)
    legend = r'$\mu$=%.3f $\sigma$=%.3f' % (result.best_values['center'], result.best_values['sigma'])
    return result, legend


def create_multi_peak(peaks):
    """Create a multi gaussan model.

    input is an array of (amplitude, center, width) tuples
    """
    def create_single_peak(ipeak, center, width=5.0, amplitude=1):
        """Create a single gaussian with initial values as given.

        Parameter:
            ipeak   - label for hte peak (a decimal number)
            center    - center of hte peak
            width     - width of the peak
            amplitude - amplitude of the peak

        """
        pref = "f{0}_".format(ipeak)
        model = GaussianModel(prefix=pref)
        model.set_param_hint(pref+'amplitude', value=amplitude)
        model.set_param_hint(pref+'center', value=center)
        model.set_param_hint(pref+'sigma', value=width)
        return model

    ipeak = 0
    mod = None
    for ampl, center, sigma in peaks:
        this_mod = create_single_peak(ipeak, center, sigma, ampl)
        if mod is None:
            mod = this_mod
        else:
            mod = mod + this_mod

        ipeak += 1

    return mod


def fit_multi_gaus(hints, n, bins):
    """Fit a a number of gaussians as defined by the hints.

    Parameter:
        hints: an array of (ampl, mean, sigma)
        n: histogram bin  contents
        bins: bin limits

    Returns
    -------
        result: The fit result object
        out: an array of (mean, std) tuples, one per peak
        legend: a lengend.

    """
    width = (bins[1] - bins[0])
    X = bins[:-1] + (0.5*width)

    model = create_multi_peak(hints)
    if model is None:
        return None, None, None

    # do the fit
    result = model.fit(n, x=X)
    legend = r""
    out = []
    for i in range(len(hints)):
        pref = "f{0}_".format(i)
        if i:
            legend += '\n'
        legend += r"$\mu$={:.3f} $\sigma$={:.3f}".format(result.best_values[pref + 'center'],
                                                         result.best_values[pref + 'sigma'])

        out.append((result.best_values[pref + 'center'], result.best_values[pref + 'sigma']))

    return result, out, legend


def fit_peak_model(n, bins, distance=None, height=None, debug=None):
    """Fit a multigaussian model from the number of peaks found.

    TODO: need to compute the distance from the noise and step

    Parameter:
    ---------
        n: histogram bin  contents
        bins: bin limits
        distance: distance parameter find_peak
        height: the cut on the peak height
        debug: set to true to see extra information

    Returns
    -------
        result: The fit result object
        out: an array of (mean, std) tuples, one per peak
        legend: a lengend

    """
    width = (bins[1] - bins[0])
    ntot = np.sum(n)
    thrs = 0.01*ntot
    if height is not None:
        thrs = height

    if debug:
        print("ntot:", ntot)
        print("thrs:", thrs)
        print("width:", width)

    peaks, prop = find_peaks(n, thrs, distance=distance)
    if debug:
        print("== Peaks")
        for peak, ampl in zip(peaks, prop['peak_heights']):
            print("\t height {:.3f} peak {:.3f} width {:.3f}".format(ampl, bins[peak], width))

    hints = []
    for peak, ampl in zip(peaks, prop['peak_heights']):
        hints.append((ampl, bins[peak], width))

    return fit_multi_gaus(hints, n, bins)


def draw_best_fit_orig(ax, result, bins, legend=None):
    """Draw the best fit."""
    step = 0.5 * (bins[1] - bins[0])
    X = bins[:-1] + step
    ax.plot(X, result.best_fit)
    if legend is not None:
        ax.legend([legend], loc=1)


def draw_best_fit(ax, result, bins, npts=100, legend=None, color="#fa6e1e"):
    """Draw the best fit."""
    X = np.linspace(bins[0], bins[:-1], num=npts)
    Y = result.eval(param=result.params, x=X)
    ax.plot(X, Y, color=color)
    if legend is not None:
        ax.legend([legend], loc=1)


if __name__ == "__main__":
    nevts = 10000
    fig, ax = plt.subplots(nrows=1, ncols=2)

    # Double peak gauss
    peak1 = np.random.default_rng().normal(10.0, 0.5, nevts)
    values = np.append(peak1, np.random.default_rng().normal(7.5, 0.75, int(0.75*nevts)))

    count, bins, ignored = ax[0].hist(values, 50)
    result, out, legend = fit_peak_model(count, bins, debug=True)
    ax[0].legend([legend], loc=1)
    draw_best_fit(ax[0], result, bins)

    plt.show()
