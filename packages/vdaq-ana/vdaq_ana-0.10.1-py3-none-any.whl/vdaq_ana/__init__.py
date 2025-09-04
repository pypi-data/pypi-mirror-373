# VDaq analysis package.

__version__ = "0.10.1"

from .GTimer import GTimer
from .VDaqData import VDaqData
from .Progress import ShowProgress
from .AliVATAModule import AliVATAModule
from .ScanManager import ScanManager

def analyze_data():
    """Analyze data."""
    from .cmmds.analyze_data import analyze_data
    analyze_data()

def show_data():
    """Analyze data."""
    from .cmmds.show_data import show_data
    show_data()

def getSpectrum():
    """Makes an spectrum."""
    from .cmmds.getSpectrum import getSpectrum
    getSpectrum()

def getFileInfo():
    """Makes an spectrum."""
    from .cmmds.getFileInfo import getFileInfo
    getFileInfo()

def variableScan():
    """Show variation of signal in a scan."""
    from .cmmds.variable_scan import main
    main()

