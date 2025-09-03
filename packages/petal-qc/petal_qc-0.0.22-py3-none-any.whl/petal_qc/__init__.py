"""petal_qc python module."""
__version__ = "0.0.22"


def coreMetrology():
    """Launches the Core metrology analysis ahd PDB script."""
    from .metrology.coreMetrology import main
    main()

def doMetrology():
    """Launches the Core metrology analysis in the command line."""
    from .metrology.do_Metrology import main
    main()

def coreMetrologyTTY():
    """Launches the Core metrology analysis in the command line."""
    from .metrology.do_Metrology import analyze_core_metrology
    analyze_core_metrology()

def coreThermal():
    """Launches the Core thermal analysis ahd PDB script."""
    from .thermal.coreThermal import main
    main()

def bustapeReport():
    """Creates the bustape report and uplades to PDB."""
    from .BTreport.CheckBTtests import main
    # from .BTreport.bustapeReport import main
    main()

def uploadPetalInformation():
    """Read files from AVS nd create Petal core in PDB."""
    from .metrology.uploadPetalInformation import main
    main()

def createCoreThermalReport():
    """Create a petal core thermal report."""
    from .thermal.create_core_report import main
    main()

def analyzeIRCore():
    """Create a petal core thermal report."""
    from .thermal.analyze_IRCore import main
    main()

def petalReceptionTests():
    """GND/VI tests."""
    from .PetalReceptionTests import main
    main()

def petalCoreTestSummary():
    """GND/VI tests."""
    from .getPetalCoreTestSummary import main
    main()

def readReceptionTests():
    """Read tamplate table with results of REception tests."""
    from .readTemplateTable import main
    main()

def dashBoard():
    """Launches the Core thermal analysis ahd PDB script."""
    from .dashBoard import main
    main()
