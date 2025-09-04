#!/usr/bin/env python3
"""AliVATA module data class."""
import sys
import pathlib
import numpy as np
from collections import namedtuple


try:
    import vdaq_ana
except ImportError:
    the_folder = pathlib.Path(__file__).parent
    sys.path.append(the_folder.as_posix())

from vdaq_ana import Cluster
from vdaq_ana.utils.remove_outliers import remove_outliers
from vdaq_ana.TDCAliVATA import TDCcounter

def __dummy_cond__(xx):
    return True


class AliVATAModule(object):
    """Module data handling class."""

    SERIAL, SPARSE, SPARSE_ADJ = (1, 2, 4)

    def __init__(self, module, data_file, polarity=1.0, do_cluster=False):
        """INitialize.

        Args:
            module: The module daq ID.
            data_file: The hdf5 data file object.
            polarity (optional): Polarity of the signal. Defaults to 1.0.
            do_cluster (optional): If cluster analysis is done. Defaults to False.

        """
        path = "/modules/%s/data/maddaq" % module
        self.data = data_file[path]
        path = "/modules/%s/data/time" % module
        self.time = data_file[path]

        self.polarity = polarity
        self.do_cluster = do_cluster
        names = ['mod_id', 'evt_time', 'tdc', 'evtno']
        names.extend(self.data.dtype.names)
        self.type = namedtuple("AliVATAModuleData", names)

        # Get pedeestals
        self.P = data_file["/modules/%s/pedestal/pedestal" % module]
        self.N = data_file["/modules/%s/pedestal/noise" % module]
        self.Ptime = data_file["/modules/%s/pedestal/evt_time" % module]

        # This is the pedestal and noise values used by default
        self.pedestal = self.P[-1]
        self.noise = self.N[-1]
        self.ntot = self.pedestal.shape[0]
        self.full_noise = [[] for i in range(0, self.ntot)]

        # Get module configuration from header
        self.id = int(module)
        self.nchip = -1
        modules = data_file["/header/modules"]
        for m in modules:
            mid = m & 0xffff
            if mid == int(module):
                self.nchip = (m >> 20) & 0xff
                break

        # Read configuration record
        config = data_file["/modules/%s/configuration" % module]
        self.firmware = config[0] | config[1] >> 16
        self.threshold = config[2]
        self.ro_mode = config[3]
        self.nadj = config[4]
        self.hold_delay = config[5]
        self.ctw = config[6]
        self.trg_type = config[7]

        self.nbias = config[8]
        self.mbias = [config[9:9+self.nbias]]
        self.clk_period = 25.0

        try:
            self.version = config[9+self.nbias]
        except IndexError:
            self.version = 0

        self.adjacents = [0]

        for ch in range(1, self.nadj+1):
            self.adjacents.extend((ch, -ch))

        self.adjacents = np.array(self.adjacents)
        self.debug = False
        self.evdisplay = None
        self.cnvs = None

        self.seed_cut = 5.0
        self.neigh_cut = 3.0

    @staticmethod
    def is_valid_module(modid, data_file):
        """Checks that the module is one of ours."""
        path = "/modules/%s/data/maddaq" % modid
        if path in data_file:
            return True
        else:
            return False

    def print_config(self):
        """Print module configuration."""
        ROmode = {
            1: "Serial",
            2: "Sparse",
            4: "Sparse+Adj"
        }
        fw_major = (self.firmware & 0xff00) >> 8
        fw_minor = self.firmware & 0xff
        print("Module {}".format(self.id))
        print("-----------")
        print("Firmware  : {}.{}".format(fw_major, fw_minor))
        print("Threshold : {}".format(self.threshold))
        print("ro_mode   : {}".format(ROmode[self.ro_mode]) )
        print("nadj      : {}".format(self.nadj))
        print("mbias     : {}".format(self.mbias))
        print("ctw       : {}".format(self.ctw))

    def set_clk_period(self, period):
        """Set TDC clock period in ns.

        Args:
            period: clock period in ns.

        """
        self.clk_period = period

    def is_serial(self):
        """Tell if this is 'serial' data."""
        return self.ro_mode == AliVATAModule.SERIAL

    def compute_pedestals(self, fnam=None):
        """Computes pedestals and noise.

        Args:
            fnam: if given pedestals are saved in this file.
        """
        if self.ro_mode != AliVATAModule.SERIAL:
            raise NotImplementedError

        print("Computing pedestals of module {}".format(self.id))
        md_data = self.data[:]
        nchan = md_data[0][6].shape[0]
        nevt = md_data.shape[0]

        data = np.zeros((nevt, nchan))
        for ievt, evt in enumerate(md_data):
            data[ievt] = evt[6]

        # Cpmpute and remove pedestals.
        ped = np.mean(data, axis=0)
        for evt in data:
            evt -= ped

        noise = np.zeros(nchan)
        for i in range(nchan):
            chanData = data[:, i]
            indx = remove_outliers(chanData, 10)
            noise[i] = np.std(chanData[indx])

        self.pedestal = ped
        self.noise = noise
        if fnam is not None:
            self.save_pedestals(fnam)


    def set_current_pedestal(self, which=-1):
        """Set the default pedestals from the file."""
        self.pedestal = self.P[which]
        self.noise = self.N[which]

    def set_pedestals(self, pedestals, noise):
        """Set pedestal and noise."""
        self.pedestal = pedestals
        self.noise = noise

    def get_pedestal(self, which=-1):
        """Return pedestal."""
        return self.P[which]

    def get_noise(self, which=-1):
        """Return noise."""
        return self.N[which]

    def read_pedestals(self, file_name):
        """Load pedestals from file.

        Args:
            file_name: The pedestal file
        """
        if not pathlib.Path(file_name).exists():
            return

        print("Reading pedestals for {} from {}".format(self.id, file_name))
        with open(file_name, "r", encoding="utf-8") as fin:
            for line in fin:
                values = line.split(',')
                i = int(values[0])
                self.pedestal[i] = float(values[1])
                self.noise[i] = float(values[2])


    def save_pedestals(self, file_name, which=None):
        """Saves pedestals and noise to file.

        Args:
            file_name: the output file name
            which: the pedestals to save. if None, save default pedestals.
                   otherwise, the corresponding pedestal set in the data file.
        """
        if which is not None:
            ped = self.get_pedestal(which)
            noise = self.get_noise(which)
        else:
            ped = self.pedestal
            noise = self.noise

        with open(file_name, "wt", encoding="utf-8") as ofile:
            i = 0
            for P, N in zip(ped, noise):
                ofile.write("{}, {:.2f}, {:.2f}\n".format(i, P, N))
                i = i+1


    def set_debug(self, dbg):
        """Set debug flag."""
        self.debug = dbg
        self.evdisplay = None

    def find_clusters(self, data, sn, hint=None, seed_cut=5.0, neigh_cut=3.0):
        """Do cluster analysis."""
        out = []

        #
        # find the clusters
        #
        used = [False for x in range(0, self.ntot)]

        # Get the list of channels with signal over noise > 5
        if hint is None:
            channels = np.nonzero(sn > seed_cut)[0]

        else:
            channels = [int(hint)]

        for ch in channels:
            if used[ch]:
                continue

            C = Cluster.Cluster()
            C.add_seed(ch, data[ch])
            used[ch] = True

            j = ch-1
            while True:
                if j < 0:
                    break

                if sn[j] > neigh_cut and not used[j]:
                    C.add(j, data[j])
                    used[j] = True
                    j = j - 1
                else:
                    break

            j = ch + 1
            while True:
                if j > self.ntot - 1:
                    break

                if sn[j] > neigh_cut and not used[j]:
                    C.add(j, data[j])
                    used[j] = True
                    j = j + 1
                else:
                    break

            if C.E > 0:
                out.append(C)

        return out

    def analyze_serial(self, evt):
        """Analysis of data in serial."""
        # subtract pedestals
        try:
            data = evt.data - self.pedestal
        except ValueError:
            # Sometimes it says we are serial, but we aren't
            return []

        if self.polarity < 0.0:
            data *= -1.0

        # compute signal over noise
        sn = data/self.noise

        # compute common mode and remove it
        # TODO: This is better done on a chip by chip basis
        cmmd = np.mean(data[np.nonzero(abs(sn) < 5.0)])
        data -= cmmd

        #
        # find the clusters
        #
        out = self.find_clusters(data, sn, seed_cut=self.seed_cut, neigh_cut=self.neigh_cut)

        return out

    def analyze_sparse(self, evt):
        """Analysis of sparse + adjacent data."""
        #
        # TODO: think something smarter than rejecting
        #       events with naighbours outside the range
        #
        try:
            if evt.chan < self.nadj or evt.chan + self.nadj >= self.ntot:
                val = evt.data[0] - self.pedestal[evt.chan]
                return [Cluster.Cluster(0, val), ]

        except Exception as w:
            print("chan {} nadj {} - {}".format(evt.chan, self.nadj, str(w)))
            return []

        if evt.chan < 0 or evt.chan > self.ntot:
            print("chan {} nadj {}".format(evt.chan, self.nadj))
            return []

        # Get the indices for the pedestals ans subtract pedestals
        indx = [indx + evt.chan for indx in self.adjacents]
        data = evt.data - self.pedestal[indx]
        if self.polarity < 0.0:
            data *= -1.0

        #
        # Subtract Common mode
        # Ideally this has to be done on a chip by chip basis
        #
        if self.nadj > 3:
            cmmd = np.mean(data[1:])
            data -= cmmd
        else:
            cmmd = 0.0

        out = []
        C = Cluster.Cluster()
        if evt.romode == AliVATAModule.SPARSE_ADJ and self.do_cluster:
            vsn = data/self.noise[indx]
            i = 0
            while i < len(data):
                if i == 0:
                    val = data[i]
                    C.add_seed(indx[i], val)
                    i += 1

                else:
                    ngood = 0
                    for j in (i, i+1):
                        if vsn[j] > 5.0:
                            val = data[j]
                            C.add(indx[j], val)
                            ngood += 1

                    i += 2
                    if ngood == 0:
                        break

            if C.E > 0:
                out.append(C)

        else:
            if data[0] > 0:
                C.add_seed(evt.chan, data[0])
                out.append(C)

        return out

    def process_event(self, evt):
        """Very simple event processing."""
        if evt.romode == AliVATAModule.SERIAL:
            return self.analyze_serial(evt)

        elif evt.romode == AliVATAModule.SPARSE_ADJ:
            return self.analyze_sparse(evt)

        elif evt.romode == AliVATAModule.SPARSE:
            print("SPARSE not implemented")
            return None

    def find_time(self, T):
        """Find the event with DAQ time closest to the given."""
        ntot = self.time.shape[0]
        aa = 0
        bb = ntot-1
        faa = self.time[aa]
        fbb = self.time[bb]
        last_indx = -1
        while True:
            indx = aa+int((bb-aa)/2)
            # print("[{} {}] f(a) {}".format(aa, bb, faa))
            if indx == aa:
                return aa

            val = self.time[indx]

            if val > T:
                bb = indx
                fbb = val

            elif val < T:
                aa = indx
                faa = val

            if abs(aa-bb) < 1:
                return aa

    def __iter__(self):
        """Return the iterator."""
        # return self.navigate()
        return ModuleDataIterator(self)

    def navigate(self, start=None, stop=None, condition=__dummy_cond__):
        """The actual iterator routine..

        If start and stop are the first and last event we want read
        condition is a boolean function that receives the module data.
        navigate will only return the events for which condition
        returns true.
        """
        nevts = self.data.shape[0]

        # chunk size os the same for data and time
        chunk_size = 10*self.data.chunks[0]

        if start is None:
            start = 0

        if stop is None:
            stop = nevts

        if stop > nevts:
            stop = nevts

        first_chunk = start/chunk_size
        last_chunk = stop/chunk_size + 1
        current_chunk = first_chunk

        offs = 0
        for indx in range(start, stop):
            if indx % chunk_size == 0:
                TS = self.time[indx:indx+chunk_size]
                DS = self.data[indx:indx+chunk_size]
                offs = indx

            values = [self.id, TS[indx-offs]]
            values.extend(DS[indx-offs])
            obj = self.type._make(values)
            if condition(obj):
                yield obj


class ModuleDataIterator(object):
    """Iterator for module data."""
    board_last_time = {}

    def __init__(self, module, start=None, stop=None, condition=__dummy_cond__):
        """The actual iterator.

        start and stop are the first and last event we want to read
        condition is a boolean function that receives the module data.
        The iterator will only return the events for which condition
        returns true.
        """
        self.M = module
        self.start = start
        self.stop = stop
        self.condition = condition
        self.nevts = self.M.data.shape[0]
        self.chunk_size = 20*self.M.data.chunks[0]
        self.first_chunk = None
        self.last_chunk = None
        self.current_chunk = None

        self.TS = None
        self.DS = None
        self.first_in_chunck = 0
        self.indx = 0

        self.last_time = -1
        self.the_time = 0.0
        self.first_evt = np.int16(-1)
        self.last_evtcnt = -1
        self.last_evtno = 0
        self.evtno = 0


        self.init_iter()

    def init_iter(self):
        """Inititalize the iterator."""
        if self.indx > 0:
            return

        if self.start is None:
            self.start = 0

        if self.stop is None or self.stop > self.nevts:
            self.stop = self.nevts

        self.first_chunk = int(self.start/self.chunk_size)
        self.last_chunk = int(self.stop/self.chunk_size) + 1
        self.current_chunk = self.first_chunk
        self.end_of_chunk = (self.current_chunk + 1) * self.chunk_size
        if self.end_of_chunk > self.stop:
            self.end_of_chunk = self.stop

        # offs is the beginning of the chuck
        self.first_in_chunck = int(self.current_chunk*self.chunk_size)
        self.indx = self.start
        self.TS = None
        self.DS = None

        self.last_time = -1
        self.the_time = 0.0
        self.last_evtcnt = -1
        self.last_evtno = 0
        self.evtno = 0

        evt = self.M.data[0]
        self.first_evt = -np.int16(evt[3])

    def __iter__(self):
        """Return iterator."""
        self.init_iter()
        return self

    def __next__(self):
        """Iterator ext method."""
        if self.indx >= self.stop:
            raise StopIteration

        else:
            while True:
                # index within chunck
                ii = self.indx - self.first_in_chunck

                if self.TS is None or ii % self.chunk_size == 0:
                    self.first_in_chunck = self.indx
                    if self.TS is not None:
                        self.current_chunk += 1
                        self.end_of_chunk = (self.current_chunk + 1) * self.chunk_size
                        if self.end_of_chunk > self.stop:
                            self.end_of_chunk = self.stop

                    self.TS = self.M.time[self.first_in_chunck:self.end_of_chunk]
                    self.DS = self.M.data[self.first_in_chunck:self.end_of_chunk]
                    ii = 0

                try:
                    # the event counter
                    new_evtcnt = self.DS[ii][3]
                    incr = 0
                    if new_evtcnt < self.last_evtcnt:
                        self.first_evt = np.int16(self.last_evtno + 1 - new_evtcnt)
                        self.DS[ii][3] += self.first_evt
                        incr = (self.DS[ii][3] - self.last_evtno) + (0xffff-self.last_evtcnt)
                    else:
                        self.DS[ii][3] += self.first_evt
                        if self.last_evtno == 0xffff:
                            incr = self.DS[ii][3] +1
                        else:
                            incr = self.DS[ii][3] - self.last_evtno

                    self.evtno += int(incr)
                    self.last_evtcnt = new_evtcnt
                    self.last_evtno = self.DS[ii][3]

                    # The TDC
                    board = int(self.M.id/10)
                    if board not in self.board_last_time:
                        self.board_last_time[board] = TDCcounter(self.M.clk_period)

                    self.the_time = self.board_last_time[board].process_event(int(self.DS[ii][2]))

                    # Create the event object
                    values = [self.M.id, self.TS[ii], self.the_time, self.evtno]
                    values.extend(self.DS[ii])
                    obj = self.M.type._make(values)

                except IndexError as exc:
                    raise StopIteration from exc

                self.indx += 1
                if self.indx >= self.stop:
                    # print("ultimo {}".format(self.M.id))
                    raise StopIteration

                if self.condition(obj):
                    return obj
