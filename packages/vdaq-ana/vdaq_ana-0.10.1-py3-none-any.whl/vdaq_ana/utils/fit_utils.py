#!/usr/bin/env python3
"""A number of utils to make fits with numpy."""
import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model
from lmfit import Parameters
from lmfit.models import GaussianModel
from scipy.signal import find_peaks
from scipy.stats import moyal as landau

log2 = np.log(2)
s2pi = np.sqrt(2*np.pi)
spi = np.sqrt(np.pi)
s2 = np.sqrt(2.0)
tiny = np.finfo(np.float64).eps


def fLandau(x, norm, mode, width):
    """Approximate the landau distribution with the Moyal distribution.

    Fit model Parameters:
        p[0] = normalization
        p[1] = mode
        p[2] = width

    """
    L = (x-mode)/width
    r = norm*np.exp(-0.5*(L+np.exp(-L)))/2.506628274631001
    return r



def fStaturation(x, Csat, tau):
    """A saturation model.

    It is something like

    Csat * (1-exp(-x/tau))

    Args:
        x (): The data
        Csat (): Teh plateau
        tau (): the tau
    """
    F = Csat * (1.0 -np.exp(-x/tau))
    print(Csat, tau)
    print(F)
    return F




def fTwoPeak(x, A1, A2, center, sigma, separation):
    """Two gausians, same width separated by an adjustable amount."""
    std2 = sigma**2
    factor = max(tiny, s2pi*std2)
    factor2 = max(tiny, 2.0*std2)
    shft = separation/2.0
    c1 = center - shft
    c2 = center + shft
    out = (A1/factor)*np.exp(-(x-c1)**2/factor2) + (A2/factor)*np.exp(-(x-c2)**2/factor2)

    return out


def create_multi_peak(peaks):
    """Create a multi gaussan model.

    input is an array of (amplitude, center, width) tuples.
    """
    def create_single_peak(ipeak, center, width=5.0, amplitude=1):
        """Create a single gaussian with initial values as given."""
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


def fit_two_peaks(n, bins, center, sigma, separation):
    """Fit 2 gausians with same width.

    Fit Parameters:
        n: histogram bin  contents
        bins: bin limits
        A1, A2: estimated amplitudes of the peaks
        center: estimated center of the reference peak
        sigma: estimated sigma, same for both peaks
        separation: separation between peaks

    Returns
    -------
        result: The fit result object
        out: a (center, sigma, separation) tuple
        legend: a lengend

    """
    width = (bins[1] - bins[0])
    X = bins[:-1] + (0.5*width)

    weights = np.sqrt(n)
    # weights = np.ones(n.shape[0])
    model = Model(fTwoPeak)
    sum = np.sum(n)/2.0
    params = Parameters()
    params.add('A1', value=sum)
    params.add('A2', value=sum)
    params.add('center', value=center)
    params.add('sigma', value=sigma, min=0.5*sigma, max=1.5*sigma)
    params.add('separation', value=separation, min=0.5*separation, max=1.5*separation)
    result = model.fit(n, params, x=X, weights=weights)

    center = result.best_values['center']
    sigma = result.best_values['sigma']
    separation = result.best_values['separation']
    legend = r'center=%.3f $\sigma$=%.1f sep=%.3f' % (center, sigma, separation)
    return result, (center, sigma, separation), legend


def fit_landau_model(mu, sigma, n, bins, debug=None):
    """Fit a Landau model.

    Fit Parameters:
        mu: estimated mean
        sigma: estimated sigma
        n: histogram bin  contents
        bins: bin limits

    Returns
    -------
        result: The fit result object
        out: a (mode, std) tuple
        legend: a lengend

    """
    width = (bins[1] - bins[0])
    X = bins[:-1] + (0.5*width)

    model = Model(fLandau)
    params = model.make_params(norm=np.sum(n), mode=mu, width=sigma)
    result = model.fit(n, params, x=X, weights=np.sqrt(n))

    mode = result.best_values['mode']
    width = result.best_values['width']
    legend = r'mode=%.3f $\sigma$=%.1f' % (mode, width)
    return result, (mode, width), legend


def fit_gaussian(n, bins, center, width=5.0, amplitude=1):
    """Fit a gaussion.

    Args:
        n: The bins
        bins: the bin edges
        center: The center (or mean) of the gaussian.
        width: the sigma estimate of the gaussion. Defaults to 5.0.
        amplitude: the estimae of the amplitude. Defaults to 1.

    Returns
        the fit result and a legend

    """
    step = 0.5 * (bins[1] - bins[0])
    X = bins[:-1] + step

    model = GaussianModel()
    params = model.make_params(amplitude=amplitude, center=center, sigma=width)
    result = model.fit(n, params, x=X)
    legend = r'$\mu$=%.3f $\sigma$=%.3f' % (result.best_values['center'], result.best_values['sigma'])
    return result, (result.best_values['center'], result.best_values['sigma']), legend


def fit_multi_gaus(hints, n, bins):
    """Fit a a number of gaussians as defined by the hints.

    Fit Parameters:
        hints: an array of (ampl, mean, sigma)
        n: histogram bin  contents
        bins: bin limits

    Returns
    -------
        result: The fit result object
        out: an array of (mean, std) tuples, one per peak
        legend: a lengend

    """
    width = (bins[1] - bins[0])
    X = bins[:-1] + (0.5*width)

    model = create_multi_peak(hints)
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


def fit_peak_model(n, bins, distance=10, debug=None):
    """Fits a multigaussian model from the number of peaks found.

    TODO: need to compute the distance from the noise and step

    Fit Parameters:
        n: histogram bin  contents
        bins: bin limits

    Returns
    -------
        result: The fit result object
        out: an array of (mean, std) tuples, one per peak
        legend: a lengend

    """
    width = (bins[1] - bins[0])
    ntot = np.sum(n)
    thrs = 0.01*ntot

    if debug:
        print("ntot:", ntot)
        print("thrs:", thrs)
        print("width:", width)

    peaks, prop = find_peaks(n, thrs, distance=distance)
    if debug:
        print("== Peaks")
        for peak, ampl in zip(peaks, prop['peak_heights']):
            print("\t height {:.1f} peak {:.1f} width {:.1f}".format(ampl, bins[peak], 3.46*width))

    hints = []
    for peak, ampl in zip(peaks, prop['peak_heights']):
        hints.append((ampl, bins[peak], 3.46 * width))

    return fit_multi_gaus(hints, n, bins)


def fit_saturation_model(X, Y, Csat=1, tau=1, debug=False):
    """Fits a saturation model.

    Csat * (1-exp(-x/tau))

    """
    model = Model(fStaturation)
    params = Parameters()
    params.add("Csat", value=Csat)
    params.add("tau", value=tau)
    result = model.fit(Y, params, x=X)

    rCsat = result.best_values["Csat"]
    rtau = result.best_values["tau"]
    legend = r'Csat=%.3f tau=%.3f' % (rCsat, rtau)
    return result, (rCsat, rtau), legend


def draw_best_fit(ax, result, bins, npts=100, legend=None, color="#fa6e1e"):
    """Draw the best fit.

    Args:
        ax: Axis to draw in.
        result: Result object from fit.
        bins: the histogram bins
        npts: number of points to evaluate fit function
        legend (optional): A legend for the plot. Defaults to None.
        color (optionan): color of fit curve

    """
    if npts < len(bins)+1:
        npts = len(bins)

    X = np.linspace(bins[0], bins[-1], num=npts)
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

    # The landau distributions
    r = 2.5*landau.rvs(size=nevts) + 10.0
    count, bins, ignored = ax[1].hist(r, 50)
    result, out, legend = fit_landau_model(np.mean(r), np.std(r), count, bins)
    ax[1].legend([legend], loc=1)
    draw_best_fit(ax[1], result, bins)

    plt.show()
