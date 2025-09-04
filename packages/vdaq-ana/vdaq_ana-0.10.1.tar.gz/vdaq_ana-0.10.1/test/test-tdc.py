import os
import sys
import numpy as np
import matplotlib.pyplot as plt

HOME = os.getenv("HOME")

try:
    import vdaq_ana

except ImportError:
    import pathlib
    the_folder = pathlib.Path(__file__).parent
    sys.path.append(the_folder.as_posix())

from vdaq_ana import VDaqData, GTimer, ShowProgress
from vdaq_ana.utils.fit_utils import fit_gaussian, draw_best_fit



#ifile = "/home/silicio/Documents/VDaq-3.0/PdC/Cracovia/MB17-4chan-slot1_slave_000.h5"
ifile = "{}/kkdvk-noclk_000.h5".format(HOME)
ifile = "/Users/lacasta/tmp/protonCT/Cracovia/Krakow/nave-6mm-100MeV_000.h5"

vdaq = VDaqData(ifile)

if vdaq is None:
    sys.exit()

for mid, M in vdaq.modules.items():
    M.set_clk_period(5)

last_time = {}
last_event = {}
nlost = 0
mod_id = 104
values = []
amplitude = []

prg = ShowProgress(vdaq.nevts, width=24)
prg.start()
max_evt = 2000
emin = 0
#vdaq_iter = vdaq.create_iterator_at_scanpoint(10)
for ievt, evt in enumerate(vdaq):
    
    evt_time = int(evt.time)
    mid = evt.mod_id
    if mid != mod_id:
        continue

    ltim = last_time.get(mid, -1)
    if ltim > 0:
        dt = evt.tdc - ltim
    else:
        dt = 0

    last_time[mid] = evt.tdc
    if dt > 0 and dt < 1000:
        values.append(dt)
    
    levent = last_event.get(mid, -1)
    if levent > 0:
        devt = evt.evtcnt - levent
        if devt > 1:
            nlost += 1

    last_event[mid] = evt.evtcnt
    
    # The single channel amplitude
    md = vdaq.modules[mid]
    data = md.process_event(evt)
    if data is not None:
        for C in data:
            if C.E > emin:
                amplitude.append(C.E)

    prg.increase(show=True)

print("\nNumber of events lost: {}".format(nlost))

print("Mean period: {:.3f} us".format(np.mean(values)))

fig, ax = plt.subplots(1, 1)
ax.hist(values, bins=50)
ax.set_title("TDC test")
ax.set_xlabel("Period (us)")


# Draw the signal
fig, ax = plt.subplots(1, 1)
n, bins, *_ = ax.hist(amplitude, bins=50)
step = 0.5 * (bins[1] - bins[0])
X = bins[:-1] + step
mean = np.mean(amplitude)
std = np.std(amplitude)
try:
    result, legend = fit_gaussian(n, X, mean, width=std)
    draw_best_fit(ax, result, bins)
    ax.legend([legend], loc=1)
    ax.set_title("Signel Channel signal")
    ax.set_xlabel("Charge (ADC)")

except Exception as ex:
    print("something went wrong woth TDC. {}".format(str(ex)))

plt.draw()
plt.pause(0.001)
plt.show()
