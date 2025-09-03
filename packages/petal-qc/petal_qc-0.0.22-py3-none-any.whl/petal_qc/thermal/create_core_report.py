#!/usr/bin/env python3
"""Creates the report of a core."""

import math
import sys
import json
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.path as mplPath
import matplotlib.pyplot as plt
import numpy as np


try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.thermal.IRPetalParam import IRPetalParam
from petal_qc.thermal.create_IRCore import create_IR_core, get_IRcore_plots
from petal_qc.thermal.analyze_IRCore import analyze_IRCore, golden_from_json, get_golden_axis, plot_profile_and_golden

import petal_qc.utils.docx_utils as docx_utils
import petal_qc.utils.utils as utils



def create_report(options):
    """Create a writen report.
    """
    ifile = Path(options.files[0]).expanduser().resolve()
    if not ifile.exists():
        print("input file {} does not exist.".format(ifile))
        return


    print("\n## {} - {}".format(options.SN, options.alias))

    # Do the core analysis.
    core = create_IR_core(options)

    if options.golden is None:
        return core

    goldenFile = Path(options.golden).expanduser().resolve()
    if not goldenFile.exists():
        goldenFile = utils.output_folder(options.folder, options.golden)
        goldenFile = Path(goldenFile).expanduser().resolve()
        if not goldenFile.exists():
            print("I need a golden file.")
            return core

    with open(goldenFile, "r", encoding='utf-8') as fp:
        golden = golden_from_json(json.load(fp))



    document = docx_utils.Document()
    document.add_page_numbers()
    document.styles['Normal'].font.name = "Calibri"
    document.add_heading(options.SN, 0)

    P = document.add_paragraph(options.alias, "Subtitle")
    P.alignment = docx_utils.paragraph_align_center()

    P = document.add_paragraph(ifile.name, "Subtitle")
    P.alignment = docx_utils.paragraph_align_center()

    P = document.add_paragraph("Golden: {}".format(goldenFile.name), "Subtitle")
    P.alignment = docx_utils.paragraph_align_center()

    figures = get_IRcore_plots()
    document.add_heading('Original image', level=1)
    document.add_picture(figures["original"], True, 14, caption="Original Thermal image.")

    document.add_heading('Sensor Position', level=1)
    document.add_picture([figures["sensors_0"], figures["sensors_1"]], True, 7.5, caption="Side 0 (left) and Side 1 (right) sensors.")

    document.add_heading('Result of Pipe Fit', level=1)
    document.add_picture([figures["fit_0"],figures["fit_1"]], True, 7.5, caption="Side 0 fit (left) and Side 1 fit (right)")

    document.add_heading('Pipe Path', level=1)
    document.add_picture([figures["pipe_path_0"], figures["pipe_path_1"]], True, 7.5, caption="Side 0 and 1 pipe temp (left, right).")

    options.add_attachments = True
    options.create_golden = False

    options.files = [utils.output_folder(options.folder, options.out)]
    options.out = None
    options.no_golden_doc = True
    out = analyze_IRCore(options, show=False)
    outDB = out[0] if len(out) else None
    options.files = []

    figures = plot_profile_and_golden(golden, core, "path_temp")
    document.add_heading('Temperature along path', level=1)
    document.add_picture(figures[0], True, 12, caption="Petal core .vs. Golden (side 0).")
    document.add_picture(figures[1], True, 12, caption="Petal core .vs. Golden (side 1).")
    for F in figures:
        plt.close(F)

    figures = plot_profile_and_golden(golden, core, "sensor_avg")
    document.add_heading('Average Temperature on sensors areas.', level=1)
    document.add_picture(figures[0], True, 12, caption="Sensors .vs. Golden (side 0).")
    document.add_picture(figures[1], True, 12, caption="Sensors .vs. Golden (side 1).")
    for F in figures:
        plt.close(F)

    figures = plot_profile_and_golden(golden, core, "sensor_std")
    document.add_heading('STD of Temperature on sensors areas.', level=1)
    document.add_picture(figures[0], True, 12, caption="Sensors .vs. Golden (side 0).")
    document.add_picture(figures[1], True, 12, caption="Sensors .vs. Golden (side 1).")
    for F in figures:
        plt.close(F)

    document.add_heading('Comments and Defects.', level=1)
    added_defects = False
    if len(outDB["comments"])>0:
        added_defects = True
        document.add_heading("Comments.", level=2)
        for C in outDB["comments"]:
            document.add_paragraph(C)

    if len(outDB["defects"])>0:
        added_defects = True
        document.add_heading("Defects.", level=2)
        for D in outDB["defects"]:
            document.add_paragraph("{}: {}".format(D["name"], D["description"]))

    if not added_defects:
        document.add_paragraph("Petal is GOOD. No comments nor defects found.")


    ofile = utils.output_folder(options.folder, "{}-thermal.docx".format(options.SN))
    document.save(ofile)

    return outDB

def main():
    """Main entry."""
    P = IRPetalParam()
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--orig", action="store_true", default=False, help="plot the original image")
    parser.add_argument('--frame', default=-1, type=int, help="Frame to analize")
    parser.add_argument("--out", default="core.json", help="Output file name")
    parser.add_argument("--alias", default="", help="Alias")
    parser.add_argument("--SN", default="", help="serial number")
    parser.add_argument("--folder", default=None, help="Folder to store output files. Superseeds folder in --out")
    parser.add_argument("--add_attachments", action="store_true", default=False, help="If true add the attachments section os DB file.")
    parser.add_argument("--golden", default=None, help="The golden to compare width")

    IRPetalParam.add_parameters(parser)

    options = parser.parse_args()

    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()
    else:
        ifile = options.files[0]

    options.debug = False
    options.report = True
    create_report(options)

if __name__ == "__main__":
    main()
