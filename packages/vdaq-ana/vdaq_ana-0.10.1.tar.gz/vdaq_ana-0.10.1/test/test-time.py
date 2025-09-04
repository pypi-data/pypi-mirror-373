#!/usr/bin/env python3
""" Test time in data
"""
import sys
import math
from pathlib import Path
from vdaq_ana import VDaqData, AliVATAModule
import numpy as np
import collections


class TimeCluster(object):
    """Cluster events by time."""

    def __init__(self, cut=1.0) -> None:
        """Initialization.

        Args:
            cut: Time cut. Defaults to 1.

        """
        self.cut = cut
        self.mean = 0.0
        self.n = 0.0
        self.ids = {}

    def check_event(self, mid, tdc) -> bool:
        """Check if point is compatible with cluster.

        Args:
            mid: Module id
            tdc: Module tdc

        Returns
            True if added to cluster, False otherwise
        """
        if self.n == 0.0:
            self.add(mid, tdc)
            return True
        else:
            if abs(tdc - self.mean) < self.cut:
                self.add(mid, tdc)
                return True
            else:
                return False

    def add(self, mid, tdc) -> None:
        """Add a new point.

        Args:
            mid: Module id
            tdc: Module tdc

        """
        N = self.n + 1
        self.mean = (self.mean * self.n + tdc)/N
        self.n += 1.
        self.ids[mid] = tdc

    def std(self) -> float:
        """Return standar deviation of items in cluster."""
        return np.std(list(self.ids.values()))

    def get_boards(self) -> map:
        """Get list of boards.
        
        Returns:
            a map whete the keys are the board IDs and the values, 
            an array of TDC valus for each item in the board.
            
        """
        boards = {}
        for mid, tdc in self.ids.items():
            iboard = int(mid/10)
            boards.setdefault(iboard, []).append(tdc)

        return boards

    def reset(self):
        """Resets all counters."""
        self.n = 0.0
        self.mean = 0.0
        self.x2 = 0.0
        self.ids = {}


def get_period(vdaq):
    """Measure period or period.

    WE do this with an external trigger produced by a pulse generator.
    Same pulse for all the MB.

    Args:
        vdaq: The vdaq object.

    Return
        period (dict), std(dict) - period and deviation per MB id.

    """
    avg = {}
    last_time = {}
    for ievt, evt in enumerate(vdaq):
        evt_time = int(evt.time)
        mid = evt.mod_id
        board_id = int(int(mid)/10)
        ltim = last_time.get(mid, -1)
        if mid not in avg:
            avg[mid] = []

        dt, last_time[mid] = AliVATAModule.get_delta_time(evt_time, ltim)
        if dt != 0:
            avg[mid].append(dt)

        if ievt > 200:
            break

    period = {}
    rms = {}
    for key, val in avg.items():
        period[key] = np.mean(val)
        rms[key] = np.std(val)

    return period, rms


def main(fname, options):
    """fname is the input filename"""
    inp_file_path = Path(fname)
    if not inp_file_path.exists():
        print("Input file ", inp_file_path, " does not exist")
        return

    # open the vdaq file
    vdaq = VDaqData(fname)
    vdaq.show_info()

    #  Get the ext. trigger period and guess number of boards.
    period, period_std = get_period(vdaq)
    tmp = {}
    for k in period_std.keys():
        tmp.setdefault(int(k/10), 0)

    nboard = len(tmp)
    nmodule = len(period)
    mean_period = np.mean(list(period.values()))
    std_period = np.mean(list(period_std.values()))

    print("nboard {}".format(nboard))
    print("nmodules {}".format(nmodule))
    print("avg period {:.3f}".format(mean_period))
    print("period std: {:.4f}".format(std_period))

    last_time = {}
    last_tdc = {}
    for m in list(vdaq.modules.values()):
        last_tdc[m.id] = 0.0

    # Get events sorted by TDC
    vdaq.iter_key = 'tdc'

    # Title of output
    print("   Row   mid  evtcnt          time     deltaT   deltaP")

    delta_board = []
    llog = collections.deque(maxlen=10)
    CL = TimeCluster(0.1*mean_period)
    Nevts = 0
    Nerr = 0
    N_spread = 0
    N_dist = 0
    N_both = 0
    for ievt, evt in enumerate(vdaq):
        evt_time = int(evt.time)
        mid = evt.mod_id
        board_id = int(int(mid)/10)
        ltim = last_time.get(mid, -1)

        dt, last_time[mid] = AliVATAModule.get_delta_time(evt_time, ltim)

        if options.is_pulse and dt > 0:
            offs = abs(dt - period[mid])/period[mid]
            if offs > 0.05:
                print("{:>6d} {:3d} Divergence {:>10.3f} expected {:>10.3f} [{:12X}]".format(ievt,
                                                                                             mid,
                                                                                             dt,
                                                                                             period[mid],
                                                                                             evt_time))

        # Compera with the last time for this module
        delta = evt.tdc - last_tdc[mid]                         # delta time
        delta_period = abs(delta - period[mid])     # faction of period

        # Store this tdc for next comparison.
        last_tdc[mid] = evt.tdc
        if dt == 0:
            delta_period = 0

        try:
            out = "{:>6d}   {:3d}  {:>6n} {:>12.3f} {:>10.3f}   {:.4f} [{:12X}]".format(
                ievt, mid, evt.evtcnt, evt.tdc, dt, delta_period, evt_time)

        except Exception:
            out = "{:>6d}   {:3d}  {:>6n} {:>12.3f} {:>10.3f}   {:.4f} [{:12X}]".format(
                ievt, mid, evt.evtcnt, evt.tdc, dt, 0.0, evt_time)

        llog.appendleft(out)

        # Analysis
        if not CL.check_event(mid, evt.tdc):
            if ievt/nmodule < options.show:
                print('-')
                
            # seems we are at the end of a trigger.
            Nevts += 1
            nerr = 0
            do_print = False
            msg = []
            # Complain if the std of times within cluster is large.
            if CL.std() > 1:
                N_spread += 1
                do_print = True
                nerr += 1
                msg.append("Event time spread larger than limit.")

            boards = CL.get_boards()
            btime = []
            for ib, val in boards.items():
                stdev = np.std(val)
                avg = np.mean(val)
                btime.append(avg)

            # Check the tome distance between boards
            if len(btime) > 1:
                dt_board = []
                for i in range(nboard-1):
                    for j in range(i+1, nboard):
                        dst = btime[i] - btime[j]
                        dt_board.append(abs(dst))

                mxdist = np.amax(dt_board)
                if mxdist != 0:
                    delta_board.append(mxdist)

                if mxdist > 0.1:
                    nerr += 1
                    N_dist += 1
                    do_print = True
                    msg.append("Max distance between boards: {:.6f}".format(mxdist))

            if do_print:
                Nerr += 1
                if nerr > 1:
                    N_both += 1

                print("========")
                for m in msg:
                    print("+ {}".format(m))
                print("")
                print("{} CL mean: {:.3f} std: {:.4f}".format(ievt, CL.mean, CL.std()))
                for ib, val in boards.items():
                    stdev = np.std(val)
                    avg = np.mean(val)
                    print("... board {}. mean {:.3f} std {:.4f}".format(ib, avg, stdev))

                print("... Max. Delta board: {:.4f}\n".format(mxdist))
                print("")
                print("   Row   mid  evtcnt         time     deltaT   deltaP      Register")
                print("---------------------------------------------------------------------")
                for x in reversed(llog):
                    print(x)

            # Reset the cluster and add the outsider to start again
            CL.reset()
            CL.add(mid, evt.tdc)
            
        if ievt/nmodule < options.show:
            print(out)


    print("Number of triggers: {}".format(Nevts))
    print("Number of errors {}".format(Nerr))
    print("Number of spread errors {}".format(N_spread))
    print("Number board dist {}".format(N_dist))
    print("Both errors {}".format(N_both))
    print("Average delta_board: {:.6f} - std {:.6f}".format(np.mean(delta_board), np.std(delta_board)))


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--pulse", dest='is_pulse', action="store_true", default=True)
    parser.add_argument("--source", dest='is_pulse', action="store_false", default=True)
    parser.add_argument("--show_nevts", dest="show", type=int, default=50, help="Number of events to show.")
    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()
    
    main(options.files[0], options)
