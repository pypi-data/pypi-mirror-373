"""Class to compute TDC value from alivata bosrds."""

class TDCcounter():
    """Computes the tdc value"""
    def __init__(self, period=25.0) -> None:
        self.period = period
        self.tdc = 0
        self.last_time = 0

    def process_event(self, evt_time):
        """Process one event and updata TDC value."""
        dt = self.get_delta_time(evt_time)
        self.last_time = evt_time
        self.tdc += dt

        return self.tdc

    def get_delta_time(self, evt_time):
        """Compute the TDC time.

        Args:
            evt_time: current TDC time
            last_time: last time
            period: clock period (ns). Defaults to the 40MHz clock of AliVata

        Return:
            dt: time since last event in micro seconds
            last_time: last absolute time

        """
        if self.last_time > 0:
            if evt_time >= self.last_time:
                dt = evt_time - self.last_time
            else:
                dt = evt_time + (0x40000000-self.last_time)
        else:
            dt = 0.0

        dt = (dt*self.period)/1000.0 # microseconds
        return dt