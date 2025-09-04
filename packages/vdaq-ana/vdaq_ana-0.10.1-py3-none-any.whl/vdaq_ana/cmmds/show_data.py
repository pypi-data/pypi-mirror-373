#!/usr/bin/env python3
"""Python script to show the data in a file."""
import datetime
import os
import sys
from argparse import Action
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import numpy as np
from vdaq_ana import VDaqData
from vdaq_ana import AliVATAModule
from matplotlib.widgets import Button


def do_show_data(fname, options):
    """The main function."""
    # Check that the file exists
    if not os.path.exists(fname):
        print("Input file", fname, "does not exist")
        return

    # We open here the file with VDaqData
    vdaq = VDaqData(fname)
    vdaq.show_info(show_modules=True)

    n_mod = len(vdaq.modules)
    fig, ax = plt.subplots(nrows=1, ncols=n_mod)
    fig.set_figwidth(2.5*n_mod)
    dax = {}
    try:
        for a, m in zip(ax, vdaq.modules.values()):
            dax[m.id] = a

    except TypeError:
        m = list(vdaq.modules.values())[0]
        dax[m.id] = ax

    mod_evt = {}
    mod_dtime = {}
    for m in vdaq.modules.values():
        mod_evt[m.id] = 0.0
        mod_dtime[m.id] = 0.0

        m.seed_cut = options.seed_cut
        m.neigh_cut = options.neigh_cut

    plt.subplots_adjust(bottom=0.2)

    if options.iter_key:
        vdaq.iter_key = options.iter_key

    if options.scan_point is not None:
        vdaq_iter = vdaq.create_iterator_at_scanpoint(options.scan_point)
    elif options.start_time is not None:
        vdaq_iter = vdaq.create_iterator_at_time(options.start_time)
    elif options.start_evt is not None:
        vdaq_iter = vdaq.create_iterator_at_event(options.start_evt)
    else:
        vdaq_iter = iter(vdaq)

    def next_event(dummy):
        evt = next(vdaq_iter)
        mid = evt.mod_id
        md = vdaq.modules[mid]
        nbin = md.pedestal.shape[0]
        nchan = evt.data.shape[0]
        x = np.arange(0, nbin, 1)

        # Get the indices and build up
        if evt.romode == AliVATAModule.SPARSE_ADJ:
            indx = [i + evt.chan for i in md.adjacents]
            values = np.zeros(nbin)
            try:
                values[indx] = evt.data

            except IndexError:
                print("Bin {} out of bounds for module {}".format(indx, mid))

        elif evt.romode == AliVATAModule.SERIAL:
            values = np.array(evt.data, dtype='d')

        else:
            print("Readout mode not supported:", evt.romode)

        if options.pedestals:
            if evt.romode == AliVATAModule.SERIAL:
                values -= md.pedestal
                sn = values/md.noise
                cmmd = np.mean(values[np.nonzero(abs(sn) < 5.0)])
                values -= cmmd

            else:
                values[indx] -= md.pedestal[indx]
                sn = values/md.noise
                cmmd = np.mean(values[np.nonzero(abs(sn) < 5.0)])
                values[indx] -= cmmd


        dt = evt.time-mod_dtime[mid]
        mod_dtime[mid] = evt.time
        out = md.process_event(evt)
        clst = "".join(["({:>3d} {:>6.1f}) ".format(int(C.chan), C.E) for C in out])
        print("Module {}: daq_time {:>10.6f} evt no. {:>6d} TDC {:>10.3f} clusters {}".format(mid,
                                                                                            evt.daq_time/1.e6,
                                                                                            evt.evtno,
                                                                                            evt.tdc,
                                                                                            clst))

        ax = dax[mid]
        ax.clear()
        ax.set_title('Module %d' % mid)
        ax.step(x, values, where='mid')
        if options.fix_range:
            if options.pedestals:
                ax.set_ylim(-250, 2048)
            else:
                ax.set_ylim([0, 4096])

        ax.set_ymargin(0.2)
        ymin, ymax = ax.get_ylim()
        xmin, xmax = ax.get_xlim()
        dy = (ymax-ymin)
        dx = (xmax-xmin)
        ax.text(xmin+0.05*dx, ymax-0.05*dy, "Evt. {}".format(evt.evtcnt) )

        plt.draw()

    def loop_events(dummy):
        while options.plot:
            next_event(None)
            plt.draw()
            plt.pause(0.01)

        plt.show()

    axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
    bnext = Button(axnext, 'Next')
    bnext.on_clicked(next_event)

    # axloop = plt.axes([0.4, 0.05, 0.2, 0.075])
    # bloop = Button(axloop, 'Loop/Step')
    # bloop.on_clicked(loop_events)

    axquit = plt.axes([0.1, 0.05, 0.1, 0.075])
    bquit = Button(axquit, 'Quit')
    bquit.on_clicked(sys.exit)

    if options.plot:
        loop_events(None)

    next_event(None)
    plt.show()


class CommaSeparatedListAction(Action):
    """Create a list from the comma sepparated numbers at imput."""

    def __call__(self, parser, namespace, values, option_string=None):
        """The actual action."""
        setattr(namespace, self.dest, list(map(int, values.split(','))))


def show_data():
    """Define arguments and call main function."""

    parser = ArgumentParser()
    parser.add_argument('files', nargs='+', help="Input files")
    parser.add_argument("--pedestals",
                        dest="pedestals", action="store_true",
                        help="Remove pedestals on the plot",
                        default=False)
    parser.add_argument("--fix_range", action="store_true",
                        help="Histogram range is fixed.",
                        default=False)
    parser.add_argument("--start-time", dest="start_time", default=None, type=float,
                        help="Event time to start showing")
    parser.add_argument("--start-evt", dest="start_evt", default=None,
                        action=CommaSeparatedListAction,
                        help="Event number to start showing")
    parser.add_argument("--scan-point", dest="scan_point", type=int, default=None,
                        help="Scan point number to visit")
    parser.add_argument("--plot", dest="plot", default=False,
                        action="store_true",
                        help="Draw histograms")
    parser.add_argument("--seed_cut", dest="seed_cut", default=3.5, type=float,
                        help="Threshold of charge for a cluster seed")
    parser.add_argument("--neigh_cut", dest="neigh_cut", default=1.5, type=float,
                        help="Threshold of charge to add a neighbour to a cluster")
    parser.add_argument("--raw-data", dest="raw_data",
                        default=False, action="store_true",
                        help="Show the raw data instead of the 'digested' signal")
    parser.add_argument("--sort-by", dest="iter_key", default=None, help="Sort data by this variable.")

    options = parser.parse_args()

    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    do_show_data(options.files[0], options)


if __name__ == "__main__":
    show_data()