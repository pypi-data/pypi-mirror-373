#!/usr/bin/env python3
"""Test the connection with graphana to get the value at the peak."""
import sys
from pathlib import Path
import datetime
import numpy as np
try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.utils.readGraphana import ReadGraphana
from petal_qc.thermal.IRDataGetter import IRDataGetter
from petal_qc.thermal.IRPetalParam import IRPetalParam
from petal_qc.thermal import IRBFile



options = IRPetalParam()
options.institute = "IFIC"
options.files = [Path("~/tmp/thermal/IFIC-thermal/IRB_files/PPC.008.irb").expanduser().resolve()]
getter = IRDataGetter.factory(options.institute, options)
DB = ReadGraphana("localhost")
irbf = IRBFile.open_file(options.files)

frames = getter.get_analysis_frame(irbf)
print(frames[0].timestamp)
the_time = frames[0].timestamp
try:
    X, val = DB.get_temperature(the_time, 5)
    for x, y in zip(X, val):
        print("{} - {:.1f}".format(x, y))
        
    print("{:.1f}".format(np.min(val)))
except ValueError as e:
    print(e)
