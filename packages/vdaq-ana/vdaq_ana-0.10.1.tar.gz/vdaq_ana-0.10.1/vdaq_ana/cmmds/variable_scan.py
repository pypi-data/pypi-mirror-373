#!/usr/bin/env python3
"""Analizes a pulse scan There should be at least one channel."""
import sys
import io
import matplotlib.pyplot as plt
import numpy as np


try:
    import vdaq_ana

except ImportError:
    import pathlib
    the_folder = pathlib.Path(__file__).parent.parent.parent
    sys.path.append(the_folder.as_posix())

from vdaq_ana import VDaqData
from vdaq_ana import ShowProgress
from vdaq_ana.utils import fit_utils
from vdaq_ana.utils.remove_outliers import remove_outliers

def name2var(name):
    """Convert variable name to variable code."""
    table = {
        "channel": 0,
        "pulse": 1,
        "threshold": 2,
        "trim": 3,
        "bias": 4,
        "xposition": 5,
        "yposition": 6,
        "zposition": 7,
        "angle1": 8,
        "angle2": 9,
        "angle3": 10,
        "user1": 11,
        "user2": 12,
        "user3": 13,
        "user4": 14,
        "thrs_trim": 15,
        "cal_dac": 16,
    }
    return table[name]


class VarData:
    """Data of a variable"""
    def __init__(self, value=0.0):
        self.value = value
        self.point_values = []
        self.point_mean = []
        self.point_std = []

def analyze_pulse_scan(fname, options):
    """Main entry."""
    # Open file
    vdaq = VDaqData(fname)
    vdaq.show_info(True)

    scm = vdaq.scan_manager()
    if scm is None:
        print("This is not a scan run.")
        sys.exit()

    if scm.nvar > 2:
        print("Too many scan varibles. Max is 2.")
        sys.exit()

    print()
    scm.show_info()

    # get the iterator of the Scan data
    prg = ShowProgress(vdaq.nevts)
    keys = list(vdaq.modules.keys())
    if options.mid in keys:
        mid = options.mid
    else:
        mid = keys[0]

    md = vdaq.modules[mid]
    point_values = []
    point_mean = []
    point_std = []
    var_id = name2var(options.variable)

    if options.debug:
        dbg_fig, dbg_ax = plt.subplots(1, 1, tight_layout=True)
    else:
        dbg_ax = None
        
    results = {}

    for ipoint, scP in enumerate(vdaq.scan_iter()):
        block = results.setdefault(scP.values[var_id], VarData(scP.values[var_id]))
        point_data = []
        for evt in vdaq.create_iterator_at_scanpoint(ipoint, options.mid):
            data = md.process_event(evt)
            if data is not None:
                for C in data:
                    if C.E > options.threshold:
                        point_data.append(C.E)

            prg.increase(show=True)


        if len(point_data) < 3.0:
            continue

        block.point_values.append(scP.values[var_id])

        point_data = np.array(point_data)
        mean = np.mean(point_data)
        indx = remove_outliers(point_data, 5)
        std = np.std(point_data[indx])

        if dbg_ax:
            dbg_ax.clear()
            n, bins, *_ = dbg_ax.hist(point_data, bins=options.nbin, range=(mean-5*std, mean+5*std))
        else:
            n, bins, *_ = np.histogram(point_data, bins=options.nbin, range=(mean-5*std, mean+5*std))    
            
        #result, out, legend = fit_utils.fit_gaussian(n, bins, mean, width=std)
        result, out, legend = fit_utils.fit_two_peaks(n, bins, mean, std/2.0, std)

        block.point_mean.append(result.best_values["center"])
        block.point_std.append(result.best_values["sigma"])

        if dbg_ax:
            fit_utils.draw_best_fit(dbg_ax, result, bins)
            dbg_ax.legend([legend], loc=1)
            dbg_ax.set_title("Signel Channel signal")
            dbg_ax.set_xlabel("Charge (ADC)")
            plt.draw()
            plt.pause(0.0001)

    prg.stop()
    print("")
    fig, ax = plt.subplots(1, 2)
    fig.suptitle("Pulse scan.")
    if scm.nvar > 1:
        for key, block in results.items():
            ax[0].plot(block.point_values, block.point_mean, 'o-', label="{:d}".format(int(key)))
            ax[0].set_title("Signal average")
            ax[0].set_xlabel("Pulse (V)")

            ax[1].plot(block.point_values, block.point_std, 'o-', label="{:d}".format(int(key)))
            ax[1].set_title("Signal sigma")
            ax[1].set_xlabel("Pulse (V)")
            
        ax[0].legend()
        ax[1].legend()

        with open(options.out, "w", encoding="utf-8") as fout:
            first_value = next(iter(results.values()), None)
            header = "pulse"
            for key, block in results.items():
                header += ",{:d}".format(int(key))

            fout.write("{}\n".format(header))
            for i, val in enumerate(first_value.point_values):
                out = "{}".format(val)
                
                try:
                    for key, block in results.items():
                        out += ",{}".format(block.point_mean[i])
                
                    out += "\n"
                    fout.write(out)
                except IndexError:
                    pass
    else:
        point_values = []
        point_mean = []
        point_std = []
        for key, block in results.items():
            if len(block.point_mean) == 0:
                continue
            
            point_values.append(key)
            point_mean.append(block.point_mean[0])
            point_std.append(block.point_std[0])

        ax[0].plot(point_values, point_mean, 'o-', label="{:d}".format(int(key)))
        ax[0].set_title("Signal average")
        ax[0].set_xlabel("Pulse (V)")

        ax[1].plot(point_values, point_std, 'o-', label="{:d}".format(int(key)))
        ax[1].set_title("Signal sigma")
        ax[1].set_xlabel("Pulse (V)")
    
        with open(options.out, "w", encoding="utf-8") as fout:

            first_value = next(iter(results.values()), None)
            header = "pulse, value"
            fout.write("{}\n".format(header))
            for pulse, value in zip(point_values, point_mean):
                fout.write("{}, {}\n".format(pulse, value))

    print("\nOutput in {}".format(options.out))
    plt.show()


def main():
    """Main entry."""
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--mid", dest="mid", default=None, type=int, help="The module ID")
    parser.add_argument("--threshold", default=0.0, type=float, help="Min E to show in histogram")
    parser.add_argument("--nbin", default=50, type=int, help="Number of bins in histogram to fit.")
    parser.add_argument("--out", default="out.csv", help="Output file with gain curve.")
    parser.add_argument("--variable", default="pulse", help="Scan Variable")
    parser.add_argument("--debug", default=False, action="store_true", help="Show fits.")


    opts = parser.parse_args()

    if len(opts.files) == 0:
        print("I need an input file")
        sys.exit()

    analyze_pulse_scan(opts.files[0], opts)

if __name__ == "__main__":
    main()
