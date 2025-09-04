#!/usr/bin/env python3
""" Read data and cluster hits in time.
"""
import sys
from pathlib import Path
from vdaq_ana import VDaqData, Progress
from vdaq_ana.utils import fit_utils

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors

def main(fname, options):
    """ Main entry.

    Args:
        fname: the input filename
        options: the program options

    """
    inp_file_path = Path(fname)
    if not inp_file_path.exists():
        print("Input file ", inp_file_path, " does not exist")
        return

    # open the vdaq file
    vdaq = VDaqData(fname)
    vdaq.show_info()

    # setup the progress monitor
    if options.nevts is None:
        max_evts = vdaq.nevts
    else:
        max_evts = options.nevts

    prg = Progress.ShowProgress(max_evts)

    # This is to stor e theTDC of previous event
    last_tdc = {}
    for m in list(vdaq.modules.values()):
        last_tdc[m.id] = 0.0

    # Get events sorted by TDC
    vdaq.iter_key = 'tdc'

    deltaT = []
    all_events_E = []
    all_events_C = []
    all_events_dt = []
    isolated_events_E = []
    isolated_events_C = []
    prg.start()
    for ievt, evt in enumerate(vdaq):
        # monitor progress
        prg.increase(show=True)

        if ievt > max_evts:
            break

        mid = evt.mod_id
        ltdc = last_tdc.get(mid, -1)
        last_tdc[mid] = evt.tdc

        # time distnce with previous event
        dt = evt.tdc - ltdc

        # get the module
        module = vdaq.modules[mid]

        if dt > 1e5:
            continue

        if ievt < 3:
            continue

        deltaT.append(dt)

        # Analysis
        data = module.process_event(evt)
        if data is not None:
            for channel, E in data:
                if E > options.threshold:
                    all_events_E.append(E)
                    all_events_dt.append(dt)
                    all_events_C.append(channel)

        if dt > options.dtmin:
            for channel, E in data:
                if E > options.threshold:
                    isolated_events_E.append(E)
                    isolated_events_C.append(channel)


    prg.stop()
    print("")

    fig = plt.figure(figsize=[5, 8],tight_layout=True)
    fig.subplots_adjust(left=0.05, right=0.95)

    ax = fig.add_subplot(3,1,1)
    ax.set_title("Event time separation")
    ax.set_yscale("log")
    ax.set_xscale("log")

    ax.hist(deltaT, bins=10**np.arange(0,4,0.05))
    ax.set_xlabel("time sep (ns)")

    ax = fig.add_subplot(3,2,3)
    fig.suptitle(inp_file_path.name)
    n, bins, patches = ax.hist(all_events_E, bins=150)
    ax.set_title("All events")
    ax.set_xlabel("Energy (ADC)")
    if options.fit:
        imax = np.argmax(n)
        mu = bins[imax]
        sigma = np.std(all_events_E)
        print("µ {:.1f} - RMS {:.1f}".format(mu, sigma))
        result, out, legend = fit_utils.fit_landau_model(mu, sigma, n, bins)
        fit_utils.draw_best_fit(ax, result, bins)
        ax.legend([legend], loc=1)


    ax = fig.add_subplot(3,2,4)
    n, bins, patches = ax.hist(isolated_events_E, bins=150)
    ax.set_title("Isolated events\n dt>{}".format(options.dtmin))
    ax.set_xlabel("Energy (ADC)")

    ax = fig.add_subplot(3, 1, 3)
    h = ax.hist2d(all_events_E, all_events_dt,
                  bins=[50, 10**np.arange(0,4,0.05)],
                  cmap=plt.cm.jet,
                  norm=matplotlib.colors.LogNorm())
    fig.colorbar(h[3], ax=ax)
    ax.set_yscale("log")
    ax.set_xlabel("Energy (ADC)")
    ax.set_ylabel("Time sep (ns)")

    plt.show()

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--nevts", help="Read at most nevts events", default=None)
    parser.add_argument("--fit", action="store_true",
                        help="It will try a Landau-like fit to the data (default)",
                        default=False
                        )
    parser.add_argument("--threshold", help="Signal Threshold", default=-9999, type=float)
    parser.add_argument("--dtmin", help="Min time distance", default=1e5, type=float)

    opt = parser.parse_args()
    if len(opt.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    main(opt.files[0], opt)
