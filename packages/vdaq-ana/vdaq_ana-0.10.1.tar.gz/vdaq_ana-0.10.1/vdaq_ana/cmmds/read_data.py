#!/usr/bin/env python3
"""Example of data analysis with python reading hdf5 data.

The example only shows how to iterate on the data.
A more complete example can be found in analyze_data.
"""
import os
import sys
from vdaq_ana import VDaqData, ShowProgress


def read_data(fname):
    """Main entry."""
    # Check the file
    if not os.path.exists(fname):
        print("Input file", fname, "does not exist")
        return

    # We open here the file
    vdaq = VDaqData(fname)

    # iterate over the modules and show some data from each of them
    # This shows how to create a module iterator.
    for m in vdaq.modules.values():
        print("Module %d: n. chips %d" % (m.id, m.nchip))
        for evt in vdaq.create_module_iterator(m, stop=10):
            print(evt.daq_time, evt.time)

    # Now print data from the first module
    # Get the first module
    the_module = list(vdaq.modules.values())[0]
    print("\nThis is module", the_module.id)
    
    # The module itself is an iterator.
    for i, evt in enumerate(the_module):
        print(evt.daq_time, evt.data)
        if i > 10:
            break

    # now we iterate on all the data in the file
    # for that we use vdaq as iterator
    prg = ShowProgress(vdaq.nevts)
    prg.start()
    print("\nIterating over all data in the file\nTime should be sorted")
    try:
        for i, evt in enumerate(vdaq):
            if i < 25:
                print(evt.mod_id, evt.daq_time)

            else:
                prg.increase(show=True)

    except KeyboardInterrupt:
        print("\nArrrrggggg !!!!")

    print("\n")


if __name__ == "__main__":
    try:
        fname = sys.argv[1]
    except IndexError:
        print("I need an input file")
        sys.exit()

    read_data(fname)
