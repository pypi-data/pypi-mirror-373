#!/usr/bin/env python3
"""VDaqData is a class that helps navigating the data."""

import os
import sys
import heapq
import datetime
from enum import Enum
import operator
import h5py

try:
    import vdaq_ana

except ImportError:
    import pathlib
    the_folder = pathlib.Path(__file__).parent.parent
    sys.path.append(the_folder.as_posix())


from vdaq_ana.AliVATAModule import AliVATAModule, ModuleDataIterator
from vdaq_ana.ScanManager import ScanManager


class VarTypes(Enum):
    """Types of Scan variables."""

    (CHANNEL, PULSE, THRESHOLD, TRIM,
     XPOSITION, YPOSITION, ZPOSITION,
     ANGLE1, ANGLE2, ANGLE3,
     USER1, USER2, USER3, USER4,
     THRS_TRIM, CAL_DAC) = range(16)


def get_run_info_time(T):
    """Convert the time struct in the data to a datetime."""
    return datetime.datetime(1900+T[5], T[4]+1, T[3], T[2], T[1], T[0])


def merge_iterators(iterables):
    """Merge iterables."""
    entries = {}  # Map from id to [front value, id, iterator].
    for id, it in enumerate(map(iter, iterables)):
        try:
            entries[id] = [next(it), id, it]
        except StopIteration:
            pass

    while entries:
        for id, entry in entries.items():
            value, _, it = entry
            yield value

            try:
                entry[0] = next(it)
            except StopIteration:
                del entries[id]
                break


class VDaqData(object):
    """VDaqData is the portal to the AliVATA data.

    It maintains a list of modules and provides an iterator for the data.

    """

    def __init__(self, fname):
        """Open the file."""
        # Open the file
        if not os.path.exists(fname):
            raise Warning("Input file", fname, "does not exist")

        self.F = h5py.File(fname, 'r')

        # Find start and stop run records
        rr = self.F["/header/run_records"]
        self.run_type = rr[0]["run_type"]

        # Key for iterator
        self.iter_key = 'evt_time'

        # Find modules
        self.nevts = 0
        self.modules = {}
        for m in self.F["/header/modules"]:
            mid = m & 0xfff
            if not AliVATAModule.is_valid_module(mid, self.F):
                continue
            
            M = AliVATAModule(mid, self.F)
            self.modules[mid] = M
            self.nevts += M.data.shape[0]

        # The ScanManager. It will be None if not a ScanRun
        self.scm = self.scan_manager()

    def show_info(self, show_modules=False):
        """Show information about the current file.

        Args:
            show_modules: If True, print list of modules.

        """
        rr = self.F["/header/run_records"]
        t0 = get_run_info_time(rr[0]['time'])
        t1 = get_run_info_time(rr[1]['time'])
        print("Run: {} of type {}".format(rr[0]['run_number'],
                                          rr[0]['run_type']))
        print("     no. of events {}".format(rr[1]['nevts']))
        print("     Started: {}".format(t0.ctime()))
        print("     Finished: {}".format(t1.ctime()))
        print("     Duration: {}".format(t1-t0))

        if show_modules:
            print("\nNumber of modules: ", len(self.modules))
            for m in self.modules.values():
                print("+ Module: ", m.id,
                      " n. evts", m.data.shape[0],
                      " fw: %d.%d" % ((m.firmware & 0xff00) >> 8, m.firmware & 0xff))

    def get_duration(self):
        """Return the run duration in seconds."""
        rr = self.F["/header/run_records"]
        t0 = get_run_info_time(rr[0]['time'])
        t1 = get_run_info_time(rr[1]['time'])
        return (t1-t0).total_seconds()

    def has_scan(self):
        """Tell if the file has scan data."""
        try:
            self.F["/scan"]
            return True
        except KeyError:
            return False

    def scan_manager(self):
        """Return a ScanManager if there is Scan data or None otherwise."""
        if self.has_scan():
            return ScanManager(self)

        else:
            return None

    def scan_iter(self):
        """Return a scan iterator."""
        if self.scm:
            return self.scm.iter()

        else:
            return None

    def __iter__(self):
        """Iterate over all the modules.

        We sort them by time. We assume that data from each module
        is already sorted.
        TODO: find a way to pass another key function
        """
        return heapq.merge(*iter(list(self.modules.values())),
                           key=operator.attrgetter(self.iter_key))

    @staticmethod
    def check_module_list(mod_ids):
        """Check the list of module identifiers."""
        mids = None
        try:
            mids = [x for x in mod_ids]
        except TypeError:
            if mod_ids is not None:
                mids = [mod_ids]

        return mids

    def create_module_iterator(self, md, start=None, stop=None):
        """Create a module iterator."""
        return ModuleDataIterator(md, start, stop)

    def create_iterator_at_time(self, T, mod_ids=None):
        """Create an iterator that starst iterating at given daq_time.

        Args:
            T: daq_time to start
            mod_ids: list of valid module ID. None for all modules.

        """
        mod_iter = []
        mids = self.check_module_list(mod_ids)

        for md in self.modules.values():
            if mids and md.id not in mids:
                continue

            ievt = md.find_time(T)
            mod_iter.append(ModuleDataIterator(md, start=ievt))

        if len(mod_iter):
            return merge_iterators(mod_iter)
        else:
            raise StopIteration

    def create_iterator_at_event(self, ievts, mod_ids=None):
        """Creatte an iterator that starts at a given event.

        Args:
            ievts: can be a single event or a tuple withe starting event
                   of each module
            mod_ids: list of valid module ID. None for all modules.

        """
        nm = len(self.modules)
        mids = self.check_module_list(mod_ids)

        try:
            ninp = len(ievts)
            if ninp == 1:
                evt_list = [ievts[0] for x in range(0, nm)]

            elif ninp != nm:
                print("I need either a single event number or a list with one per module")
                return None

            else:
                evt_list = ievts

        except TypeError:
            evt_list = [x for x in range(0, nm)]

        mod_iter = []
        for iev, md in zip(evt_list, self.modules.values()):
            if mids and md.id not in mids:
                continue

            mod_iter.append(ModuleDataIterator(md, start=iev))

        if len(mod_iter):
            return merge_iterators(mod_iter)
        else:
            raise StopIteration

    def create_iterator_at_scanpoint(self, ipoint, mod_ids=None):
        """Create an iterator that starts at the given scan point.

        Args:
            ipoint: scan point to start
            mod_ids: list of valid module ID. None for all modules.

        """
        if not self.has_scan():
            raise StopIteration

        mids = self.check_module_list(mod_ids)

        if ipoint < 0 or ipoint >= self.scm.npoints:
            raise StopIteration

        mod_iter = []
        for md in self.modules.values():
            if mids and md.id not in mids:
                continue

            mevt = self.F["/scan/points/{}".format(md.id)][ipoint]
            if ipoint < self.scm.npoints-1:
                endp = self.F["/scan/points/{}".format(md.id)][ipoint+1]
                mod_iter.append(ModuleDataIterator(md, start=int(mevt), stop=int(endp)))
            else:
                mod_iter.append(ModuleDataIterator(md, start=int(mevt)))

        if len(mod_iter):
            return merge_iterators(mod_iter)
        else:
            raise StopIteration
