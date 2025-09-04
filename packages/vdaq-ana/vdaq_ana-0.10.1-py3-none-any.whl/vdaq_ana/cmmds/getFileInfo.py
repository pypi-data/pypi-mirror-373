#!/usr/bin/env python3
"""Python script to show the data in a file."""

import sys
from pathlib import Path
from vdaq_ana import VDaqData


def getFileInfo():
    """Main entry."""
    try:
        # We open here the file with VDaqData
        ifile = Path(sys.argv[1])
        vdaq = VDaqData(ifile)

        print("\n++ {}".format(ifile))
        vdaq.show_info(True)

        for m in vdaq.modules.values():
            #m.save_pedestals("module_{}.ped".format(m.id))
            m.print_config()

    except KeyError:
        print("I need an input file")


if __name__ == "__main__":
    getFileInfo()