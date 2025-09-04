#!/usr/bin/env python3
"""A strip cluster."""

class Cluster:
    """This represents a strip data cluster.

    Members:
        chan: the "CoG" channel
        seed: the seed channel
        e_seed: the energy of the seed channel
        E: total energy
        first: first channel
        last: last channel.

    """
    def __init__(self, chan=-1.0, E=0.0):
        """initialization"""
        self.E = 0
        self.chan = -1
        self.seed = -1
        self.e_seed = 0.0
        self.first = 9999999
        self.last = -1
        self.values = []

        if chan >=0:
            self.add_seed(chan, E)


    def add_seed(self, chan, E):
        """Adds the  seed."""
        self.seed = chan
        self.e_seed = E
        self.add(chan, E)

    def add(self, chan, E):
        """Adds a new channel."""
        if self.E > 0:
            self.chan = ( self.chan * self.E + chan*E )/(self.E + E)
        else:
            self.chan = chan

        self.values.append(E)
        self.E += E
        self.first = min(chan, self.first)
        self.last = max(chan, self.last)



    def set_from_data(self, channels, data):
        """Sets from data-"""
        self.E = 0.0
        self.seed = channels[0]
        self.chan = channels[0]
        channels = channels.sorted()
        self.first = channels[0]
        self.last = channels[-1]
        for i in channels:
            if data[i] > 0.0:
                self.E += data[i]
                self.chan += i*data[i]

        if self.E > 0:
            self.chan /= self.E