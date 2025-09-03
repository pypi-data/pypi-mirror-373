#!/usr/bin/env python3
"""Probando."""
import sys
import json
from pathlib import Path

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())


import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

import petal_qc
from petal_qc.thermal.IRPetalParam import IRPetalParam
from petal_qc.thermal.create_IRCore import create_IR_core
from petal_qc.thermal.analyze_IRCore import analyze_IRCore, golden_from_json, get_golden_axis, plot_profile_and_golden
from petal_qc.utils.utils import output_folder


irbFile="/private/tmp/thermal/PPB08.irb"
goldenFIle = "/private/tmp/thermal/golden-PPB.json"
outFolder = "/private/tmp/thermal"

param = IRPetalParam()
param.alias = "PPB_008"
param.SN = "20USEBC1000028"
param.tco2 = -31.7
param.out = "{}.json".format(param.alias)
param.files = [irbFile, ]
param.golden = goldenFIle
param.folder = outFolder
param.create_golden = False
param.add_attachments = True

with open(goldenFIle, "r", encoding='utf-8') as fp:
    golden = golden_from_json(json.load(fp))

core = create_IR_core(param)

param.files[0] = output_folder(outFolder, param.out)
param.out = None
out = analyze_IRCore(param)
outDB = out[0] if len(out) else None
param.files = []

get_golden_axis(core, golden)

plot_profile_and_golden(golden, core, "path_temp")

plt.show()
