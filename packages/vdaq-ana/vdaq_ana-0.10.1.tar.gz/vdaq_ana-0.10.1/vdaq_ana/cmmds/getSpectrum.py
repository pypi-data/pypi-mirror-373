#!/usr/bin/env python3
"""Open data file and get spectrum."""
import os
import sys
import runpy
from pathlib import Path
from argparse import Action
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np
from scipy.interpolate import CubicSpline
from vdaq_ana.utils.fit_utils import draw_best_fit, fit_gaussian, fit_two_peaks
from vdaq_ana import VDaqData
from vdaq_ana import ShowProgress

from numpy.polynomial.polynomial import polyfit, polyval
from numpy import interp, ndarray, piecewise


def interp1d(x: ndarray, xp, fp):
    """1D piecewise linear interpolation with linear extrapolation."""
    return piecewise(
        x,
        [x < xp[0], (x >= xp[0]) & (x <= xp[-1]), x > xp[-1]],
        [
            lambda xi: polyval(xi, polyfit(xp[:5], fp[:5], 1)),
            lambda xi: interp(xi, xp, fp),
            lambda xi: polyval(xi, polyfit(xp[-5:], fp[-5:], 1)),
        ],
    )


def draw_hist_and_projection(axh, axp, data, title=None, axis_title=None, x_label=None, y_label=None):
    """Plots a bar histogram and the Y projection.

    Args:
        axh: axis for the histogram
        axp: axis for the projection
        data: The monitor data
        title: the histogram title
        axis_title: title for the histogram axis
        x_label: label for the histgram X axis
        y_label: label for the Y axis

    Returns
        mean. std: a tuple with the Y maverage and std

    """
    # Draw the histogram
    y = data
    x = np.linspace(0, len(data)+1, len(data))

    axh.step(x, y)
    if axis_title:
        axh.set_title(axis_title)

    if x_label:
        axh.set_xlabel(x_label)

    if y_label:
        axh.set_ylabel(y_label)

    mean = np.mean(y)
    std = np.std(y)

    # Now the projection
    axp.hist(y, orientation="horizontal")

    return mean, std


def show_pedestals(md):
    """Show module pedestals.

    Args:
        md: Module object.

    """
    # Get the data and plot
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(ncols=2, nrows=2, width_ratios=(2, 1))

    # pedestals
    ax = fig.add_subplot(gs[0, 0])
    mped, stped = draw_hist_and_projection(
        ax, fig.add_subplot(gs[0, 1], sharey=ax),
        md.pedestal,
        axis_title="Pedestals",
        x_label="Channel"
    )
    print("Pedestal mean {:.1f} std {:.1f}".format(mped, stped))

    # noise
    ax = fig.add_subplot(gs[1, 0])
    mnoise, stnoise = draw_hist_and_projection(
        ax, fig.add_subplot(gs[1, 1], sharey=ax),
        md.noise,
        axis_title="Noise",
        x_label="Channel"
    )
    print("Noise mean {:.1f} std {:.1f}".format(mnoise, stnoise))



def channel_is_masked(C, chan_list):
    """Checks if the channel is masked"""

    for chan in range(C.first, C.last+1):
        if chan in chan_list:
            return True

    return False

def unity_E(adc, mod=-1):
    """Default calibration function."""
    return adc

def get_calib_func(options):
    """Return calibration function.
        The calibration function accepts the value and an additional parameter
        which will be the module id.
    """
    if not options.calib:
        return unity_E

    fnam = Path(options.calib).expanduser().resolve()
    if not fnam.exists():
        print("Calibration file or function does not exist.")
        return unity_E
    
    try:
        fmod = runpy.run_path(fnam)
        return fmod["get_E"]

    except Exception:
        # We read tehe pairs of adc. E from a file.
        _adc, _E = np.loadtxt(fnam, skiprows=1, delimiter=',', unpack=True)
        cs = CubicSpline(_adc, _E)
        ps = np.polyfit(_adc[:3], _E[:3], 1)
        pf = np.poly1d(ps)

        def get_E(adc, *args):
            """Transform adc into keV"""
            return piecewise(adc,
                            [adc < _adc[0], (adc >= _adc[0]) & (adc < _adc[-1]), adc >= _adc[-1]],
                            [pf, cs, lambda x : np.NaN])

        return get_E

def do_getSpectrum(files, options):
    """Main entry."""

    amplitudes = []
    channels = []

    names = []
    weights = []

    get_E = get_calib_func(options)

    mx_nchan = 0
    for fnam in files:
        # Check that the file exists
        if not os.path.exists(fnam):
            print("Input file", fnam, "does not exist")
            continue

        i1 = fnam.rfind('/')
        i2 = fnam.rfind('_')
        nam = fnam[i1+1:i2]
        names.append(nam)

        # We open here the file with VDaqData
        print("\n\n### Opening {}".format(Path(fnam).name))
        vdaq = VDaqData(fnam)
        vdaq.show_info(True)

        if options.time:
            weights.append(vdaq.get_duration())
        else:
            weights.append(1.0)

        # Find the module
        keys = list(vdaq.modules.keys())
        if options.mid in keys:
            mid = options.mid
        else:
            mid = keys[0]

        print("\n## Looking at data from module {}.".format(mid))
        md = vdaq.modules[mid]
        md.seed_cut = options.seed_cut
        md.neigh_cut = options.neigh_cut
        md.do_cluster = options.cluster
        mx_nchan = max(mx_nchan, md.ntot)

        # Show pedeswtals and noise
        if options.compute_pedestals:
            md.compute_pedestals(options.compute_pedestals)
            
        elif options.load_pedestals:
            md.read_pedestals(options.load_pedestals)
        
        if options.show_ped:
            show_pedestals(md)

        # Create the iterator
        if options.scan_point is not None:
            vdaq_iter = vdaq.create_iterator_at_scanpoint(options.scan_point, [mid])
        elif options.start_time is not None:
            vdaq_iter = vdaq.create_iterator_at_time(options.start_time, [mid])
        elif options.start_evt is not None:
            vdaq_iter = vdaq.create_iterator_at_event(options.start_evt, [mid])
        else:
            vdaq_iter = vdaq.create_module_iterator(md)

        amplitude = []
        chanlist = []
        prg = ShowProgress(vdaq.nevts, width=24)
        prg.start()

        for ievt, evt in enumerate(vdaq_iter):
            data = md.process_event(evt)
            if data is not None:
                for C in data:
                    if channel_is_masked(C, options.mask):
                        continue

                    if C.E > options.threshold and C.E < options.max_E:
                        amplitude.append(C.E)
                        chanlist.append(C.chan)

            prg.increase(show=True)

            if ievt > options.nevt:
                break

        amplitudes.append(get_E(amplitude, mid))
        channels.append(chanlist)
        prg.stop()
        print("")

    # Get the normalization factors
    if len(weights) == 0:
        print("No valid file left for analysis. Quitting")
        sys.exit(-1)

    vmax = np.amax(weights)
    weights = [vmax/W for W in weights]

    # Draw the signal
    if options.calib and options.show_calib:
        fig, ax = plt.subplots(1, 1)
        xxx = np.linspace(0, 1750, int(1750/2.5))
        yyy = get_E(xxx, mid)
        ax.plot(xxx, yyy)
        ax.grid()
        ax.set_xlabel("ADC counts")
        ax.set_ylabel("Energy (keV)")

    fig, ax = plt.subplots(1, 1)
    i = 0
    ymax = -1e100
    for A, nam in zip(amplitudes, names):
        n, bins, P = ax.hist(A, bins=options.nbin,
                             histtype='stepfilled', alpha=0.25, label=nam)

        if options.time:
            W = weights[i]
            for p in P:
                points = p.get_xy()
                new_points = np.zeros(points.shape)
                ipoint = 0
                for x in points:
                    y = W*x[1]
                    ymax = max(y, ymax)
                    new_points[ipoint, :] = [x[0], y]
                    ipoint += 1

                p.set_xy(new_points)

            i += 1

    if options.time:
        y0, y1 = ax.get_ylim()
        ax.set_ylim(y0, 1.1*ymax)

    # n, bins, *_ = ax.hist(amplitudes, bins=options.nbin, label=names)
    legends = []
    if options.fit:
        for amplitude in amplitudes:
            mean = np.mean(amplitude)
            std = np.std(amplitude)
            if options.two_peaks:
                result, out, legend = fit_two_peaks(mean, std, std, n, bins)

            else:
                result, out, legend = fit_gaussian(n, bins, mean, width=std)

            draw_best_fit(ax, result, bins)
            legends.append(legend)

        ax.legend(legends, loc=1)
    else:
        ax.legend(names, loc=1)

    ax.grid()
    ax.set_title("Signal")
    if options.calib:
        ax.set_xlabel("Energy (keV)")
    else:
        ax.set_xlabel("Charge (ADC)")

    if options.logY:
        ax.set_yscale("log")

    if options.hitmap:
        fig, ax = plt.subplots(1, 1)
        i = 0
        ymax = -1e100
        for A, nam in zip(channels, names):
            n, bins, P = ax.hist(A, bins=int(mx_nchan),
                                 histtype='stepfilled', alpha=0.25, label=nam)
        ax.set_xlabel("channel number")
        ax.set_ylabel("Number  of hits")
        ax.legend()

    plt.show()


class CommaSeparatedListAction(Action):
    """Create a list from the comma sepparated numbers at imput."""

    def __call__(self, parser, namespace, values, option_string=None):
        """The actual action."""
        setattr(namespace, self.dest, list(map(int, values.split(','))))


class ChannelMaskAction(Action):
    """Create a list from the comma sepparated numbers at imput."""

    def __call__(self, parser, namespace, values, option_string=None):
        """The actual action."""
        value = {}
        for V in values.split(','):
            try:
                value[int(V)] = 1
            except ValueError:
                if ':' not in V:
                    continue

                items = V.split(':')
                if len(items)==1:
                    continue

                ival = list(map(int, items))
                ival[1] += 1
                for x in range(*ival):
                    value[x] = 1


        setattr(namespace, self.dest, value)


def getSpectrum():
    """Main entry."""

    parser = ArgumentParser()
    parser.add_argument('files', nargs='+', help="Input files")
    parser.add_argument("--nevt", default=sys.maxsize, type=int, help="max number of events.")
    parser.add_argument("--start-time", dest="start_time", default=None, type=float,
                        help="Event time to start")
    parser.add_argument("--start-evt", dest="start_evt", default=None,
                        action=CommaSeparatedListAction,
                        help="Event number to start showing")
    parser.add_argument("--scan-point", dest="scan_point", type=int, default=None,
                        help="Scan point number to visit")
    parser.add_argument("--compute_pedestals", default=None, type=str, help="File name to store computed pedestals.")
    parser.add_argument("--load_pedestals", default=None, type=str, help="File name to read pedestal values.")
    
    parser.add_argument("--nbin", default=50, type=int, help="Number of bins in histogram.")
    parser.add_argument("--logY", default=False, action="store_true", help="Log axis")
    parser.add_argument("--threshold", default=0.0, type=float, help="Min E to show in histogram")
    parser.add_argument("--max_E", default=sys.float_info.max, type=float, help="Max E to show in histogram")
    parser.add_argument("--two_peaks", default=False, action="store_true", help="Do a 2-peak fit")
    parser.add_argument("--no-fit", dest="fit", default=True, action="store_false")
    parser.add_argument("--show-ped", action="store_true", default=False, dest="show_ped")
    parser.add_argument("--hitmap", action="store_true", default=False, help="Show hitmap")
    parser.add_argument("--mid", dest="mid", default=-1, type=int, help="The module ID")
    parser.add_argument("--calib", default=None, help="The energy calibration file. X:adc, Y:energy. CAn also be a python file implementing the get_E function.")
    parser.add_argument("--show_calib", default=False, action="store_true", help="Show the calibration curve")
    
    parser.add_argument("--time", default=False, action="store_true",
                        help="Normalize to duration of run when reading various files")
    parser.add_argument("--seed_cut", dest="seed_cut", default=3.5, type=float,
                        help="Threshold of charge for a cluster seed")
    parser.add_argument("--neigh_cut", dest="neigh_cut", default=1.5, type=float,
                        help="Threshold of charge to add a neighbour to a cluster")
    parser.add_argument("--cluster", action="store_true",
                        help="Will try to find clusters in sparse",
                        default=False)

    parser.add_argument("--mask-channels", dest="mask", action=ChannelMaskAction, default={},
                        help="Ignore list of channels. The list is made with channel numbers of channel ranges (ch1:ch2 or ch1:ch2:step) ")

    options = parser.parse_args()

    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    do_getSpectrum(options.files, options)


if __name__ == "__main__":
    getSpectrum()
