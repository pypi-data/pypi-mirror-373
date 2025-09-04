#!/usr/bin/env python3
"""ScanManager is a class that helps navigating the scan data."""
import sys


class VarDefinition(object):
    """Get the information relative to a variable in the scan."""

    def __init__(self, data):
        """Initialization."""
        self.type = data[0]
        self.npoints = data[1]
        self.first = data[2]
        self.last = data[3]

    def __str__(self):
        """String representation."""
        return "Type {}, npts {} from {} to {}".format(self.type,
                                                       self.npoints,
                                                       self.first,
                                                       self.last)


class VarValue(object):
    """The value of a scan variable."""

    def __init__(self, var_type, var_value):
        """Initialization."""
        self.type = var_type
        self.value = var_value

    def __str__(self):
        """String representation."""
        return "({tp}, {val})".format(tp=self.type,
                                      val=self.value)

    def __repr__(self):
        """REpresentation."""
        return self.__str__()


class ScanPoint(object):
    """A point in the scan."""

    def __init__(self, start, end, values):
        """Initialization."""
        self.start = start
        self.end = end
        self.values = values

    def __str__(self):
        """String represetnation."""
        if self.end != sys.float_info.max:
            return "{start:6.1f}:{end:6.1f} {values}".format(start=self.start,
                                                             end=self.end,
                                                             values=self.values)
        else:
            return "{start:6.1f}:  ---- {values}".format(start=self.start,
                                                         values=self.values)


class ScanIterator(object):
    """Itarator of a scan data file."""

    def __init__(self, scm):
        """Intialization.

        Args:
            scm (ScanManager): The ScanManager.

        """
        self.scm = scm
        self.i = 0

    def __iter__(self):
        """Return iterator  object, i.e, itself."""
        self.i = 0
        return self

    def __next__(self):
        """Next ScanPoint."""
        if self.i < self.scm.npoints:
            start = self.scm.start[self.i]
            end = self.scm.end[self.i]
            if end == start:
                # this is the last point
                end = sys.float_info.max

            values = {}
            jv = self.i*self.scm.nvar
            for val in self.scm.values[jv:jv+self.scm.nvar]:
                values[val[0]] = val[1]

            self.i += 1
            return ScanPoint(start, end, values)

        else:
            raise StopIteration()


class ScanManager(object):
    """Looks at the scan information on the file."""

    def __init__(self, vdaq):
        """We pass as argument a VDaqData object."""
        try:
            self.nevts = vdaq.F["/scan/def/nevt"][0]
            self.nvar = vdaq.F["/scan/def/nvar"][0]
            self.variables = []
            for i in range(0, self.nvar):
                var = VarDefinition(vdaq.F["/scan/def/variables"][i])
                self.variables.append(var)

            self.start = vdaq.F["/scan/points/start"]
            self.end = vdaq.F["/scan/points/end"]
            self.values = vdaq.F["/scan/points/values"]
            self.npoints = int(self.values.shape/self.nvar)

        except KeyError:
            return

    def show_info(self):
        """Show Scan info."""
        print("Scan Information:")
        print("-----------------")
        print("Number of events {}".format(self.nevts))
        print("Number of variables {}.".format(self.nvar))
        print("Number of ScanPoints {}".format(self.npoints))
        for v in self.variables:
            print("+- {}".format(v))

    def iter(self):
        """Returns an iterator."""
        return ScanIterator(self)
