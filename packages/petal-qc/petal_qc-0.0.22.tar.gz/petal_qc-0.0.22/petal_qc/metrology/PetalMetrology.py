#!/usr/bin/env python3
"""Produce metrology report."""
import io
import json
import sys
import traceback
from tempfile import NamedTemporaryFile

from argparse import Action
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import petal_qc.utils.docx_utils as docx_utils
from petal_qc.utils.Geometry import project_to_plane
from petal_qc.utils.utils import output_folder
from petal_qc.metrology import DataFile
from petal_qc.metrology.analyze_locking_points import analyze_locking_point_data
from petal_qc.metrology.analyze_locking_points import locking_point_positions
from petal_qc.metrology.convert_mitutoyo import mitutoyo2cvs
from petal_qc.metrology.convert_smartscope import get_smarscope_locator_positions
from petal_qc.metrology.petal_flatness import petal_flatness


def check_spec(val, nom, fraction=0.0):
    """Checks if value is consistent with specs.

    Args:
    ----
        val (): Actual value
        nom (): Nominal value
        fraction (float, optional): Fraction of nominal allowable. Defaults to 0.05.

    Returns
    -------
        bool: true if within specs.

    """
    if val <= nom:
        return True
    else:
        rc = val <= (1+fraction)*nom
        return rc

def petal_metrology(ifile, options):
    """Do the analysis of the petal metrology data.

    Args:
        ifile: Input file from Mitutoyo.
        options: Command line options.

    Return
        Dictionary with DB values

    """
    ifile = Path(ifile).expanduser().resolve()
    if not ifile.exists():
        print("input file {} does not exist.".format(ifile))
        return

    # We infer the date of the test from the creation date of data file.
    test_date = datetime.fromtimestamp(ifile.stat().st_ctime).isoformat(timespec='milliseconds')
    if test_date[-1] not in ['zZ']:
        test_date += 'Z'

    # The JSon output
    sNames = {0: "petal", 1: "R0", 2: "R1", 3: "R2", 4: "R3S0", 5: "R3S1", 6: "R4S0", 7: "R4S1", 8: "R5S0", 9: "R5S1"}

    dbOut = {
        "component": options.SN,
        "testType": "PETAL_METROLOGY_FRONT" if options.is_front else "PETAL_METROLOGY_BACK",
        "institution": "DESYHH" if options.desy else "IFIC",
        "runNumber": "1",
        "date": test_date,
        "passed": True,
        "problems": False,
        "properties": {
            "OPERATOR": "Ohian Elesgaray",
            "MACHINETYPE": "Mitutoyo"
        },
        "comments": [],
        "defects": [],
        "results": {
            "METROLOGY": {},
        }
    }

    results = {
        "LOCATION_DELTA": {},
        "REL_POS_DELTA": {},
        "FD01_DIAM": 0,
        "FD02_DIAM": 0,
        "FLATNESS_GLOBAL": 0,
        "FLATNESS_LOCAL": [],   # a 12 element array
        "COPLANARITY_LOCATORS": 0,
        "PARALLELISM": 0,
        "CHECK_BOT_LOC_DIAM": True,
        "CHECK_SLOT_LOC_DIAM": True,
        "CHECK_OVERSIZE_LOC_DIAM": True,
        "DIAM": {"FD01": 0., "FD02":0, "PL01":0, "PL02":0, "PL03":0}
    }

    # Open the output doc.
    # Open the output document if a title is given in the options.
    document = docx_utils.Document()
    document.add_page_numbers()
    document.styles['Normal'].font.name = "Calibri"
    if options.title:
        document.add_heading(options.title, 0)

    P = document.add_paragraph(ifile.name, "Subtitle")
    P.alignment = docx_utils.paragraph_align_center()

    # Do petal flatness analysis
    Fmean = 0.0
    if options.desy:
        flatness_data = DataFile.read(ifile, "PetalPlane")
    else:
        flatness_data = DataFile.read(ifile, r"Punto(-|(Vision-))\d", "Punto")
        Fmean = np.mean(flatness_data[:, 2])
        flatness_data[:, 2] -= Fmean

    TM = None
    if not options.locking_points:
        TM, avg, Zmean, Flatness = petal_flatness(flatness_data, options, document=document)
        results["FLATNESS_GLOBAL"] = Flatness[0]
        if not check_spec(Flatness[0], 0.250):
            dbOut["comments"].append("Global flatness in sensor area {:.3f}".format(Flatness[0]))

        results["FLATNESS_LOCAL"] = Flatness[1:]
        for i, v in enumerate(Flatness[1:]):
            if not check_spec(v, 0.100):
                dbOut["defects"].append({
                    "name": "FLATNESS",
                    "description": "Flatness of {} is {:.3f} mm > 0.100 mm".format(sNames[i+1], v)
                })

    # Do locator flatness analysis
    TM = None  # TODO: fix this
    if options.desy:
        locator_data = DataFile.read(ifile, "PL[0-9]+_Plane") #".*_FineFlatness")
    else:
        locator_data = DataFile.read(ifile, "PuntoLocator", "Punto")
        locator_data[:, 2] -= Fmean

    if TM:
        M = project_to_plane(locator_data, TM, [0., 0., avg[2]])
        M[:, 2] -= Zmean
        out = analyze_locking_point_data(M, document=document, nbins=options.nbins, plane_fit=False)
    else:
        data = np.concatenate((flatness_data, locator_data))
        out = analyze_locking_point_data(data, document=document, nbins=options.nbins, plane_fit=True)

    if "defects" in out:
        for D in out["defects"]:
            dbOut["defects"].append(D)
            
        del out["defects"] 

    # SEt the percentage of deviation from nominal
    fail_allowance = 0 # 0.05
    parallelism_cut = 0.250

    for key, val in out.items():
        results[key] = val
        if key == "COPLANARITY_LOCATORS" and not check_spec(val, 0.1, fail_allowance):
            dbOut["comments"].append(
                "Coplanarity of locators: {:.3f} mm".format(val))
        elif key == "PARALLELISM" and not check_spec(abs(val), parallelism_cut, fail_allowance):
            dbOut["defects"].append({
                "name": key,
                "description": "Paralelism of locators is {:.3f} mm > {:.3f} mm".format(val, parallelism_cut)
            })
        elif key == "OFFSET" and not check_spec(abs(val), 0.100, fail_allowance):
            dbOut["comments"].append("Offset of locator plane w.r.t BT is  {:.3f} mm".format(val))

    # Analyze locking point positions
    ofile = io.StringIO()
    if not options.desy:
        mitutoyo2cvs([ifile], ofile,
                     label=r"agujero_inf|Locator\w*|Slot\w+|Fiducial\w+",
                     data_type="Círculo|Punto",
                     keep=True, fill=6)
        ofile.seek(0)

        tbl = pd.read_csv(ofile, names=["X", "Y", "Z", "D", "R", "C", "Name"], sep=',', skiprows=1, index_col="Name")
        print(tbl)

        # keywords = [n for n in tbl.index]
        # if "FiducialBot" in keywords:
        #     indx = ["agujero_inf", "LocatorTop", "FiducialBot", "FiducialTop"]
        #     offset = 0
        # else:
        #     indx = ["LocatorBot", "LocatorTop", "agujero_inf", "FiducialTop"]
        #     offset = 3

        indx = ["LocatorBot", "LocatorTop", "agujero_inf", "FiducialTop"]
        offset = 3

        # Compute Slot center (get average of diameter)
        slot_center = np.mean(tbl.loc[["SlotSup", "SlotInf"]][["X", "Y", "D"]].values, axis=0)

        print("")
        print()
        print(tbl.loc[indx][["X", "Y", "D"]])
        tvalues = tbl.loc[indx][["X", "Y", "D"]].values

        ninput = np.insert(tvalues, 1, slot_center, axis=0)
        ninput[:, 1] += offset

    else:
        get_smarscope_locator_positions(ifile, ofile, "\\w+(PL|_Fiducial)\\s+", keep=True)
        ofile.seek(0)
        tbl = pd.read_csv(ofile, names=["X", "Y", "D", "Name"], sep=',', skiprows=1, index_col="Name")
        print("")
        print()
        print(tbl)
        ninput = tbl[["X", "Y", "D"]].values
        offset = 3
        ninput[:, 1] += offset

    # Input array is
    # 0 - Bottom locator (PL01)
    # 1 - Top Slot (PL02)
    # 2 - Oversized (PL03)
    # 3 - Bottom Fid (FD01)
    # 4 - Top Fid (FD02)
    results["DIAM"]["FD01"] = ninput[3, 2]
    results["DIAM"]["FD02"] = ninput[4, 2]
    results["DIAM"]["PL01"] = ninput[0, 2]
    results["DIAM"]["PL02"] = ninput[1, 2]
    results["DIAM"]["PL03"] = ninput[2, 2]


    max_delta = 0.1 #0.075
    out = locking_point_positions(ninput, document)
    for key, val in out.items():
        results[key] = val
        if key == "LOCATION_DELTA":
            for k, v in val.items():
                delta = np.linalg.norm(v)
                if not check_spec(delta, max_delta, fail_allowance):
                    dbOut["defects"].append({
                        "name": key,
                        "description": "Delta {} is {:.3f} mm > {:.3f} mm.".format(k, delta, max_delta)
                    })

        elif key == "REL_POS_DELTA":
            for k, v in val.items():
                delta = np.linalg.norm(v)
                if not check_spec(delta, max_delta, fail_allowance):
                    dbOut["defects"].append({
                        "name": key,
                        "description": "Delta {} is {:.3f} mm > {:.3f} mm.".format(k, delta, max_delta)
                    })

        # elif "CHECK_" in key:
        #     if "OVERSIZE" in key:
        #         if not check_spec(abs(val), 0.050):
        #             dbOut["defects"].append({
        #                 "name": key,
        #                 "description": "LOC DIAM delta is {:.3f} mm > 0.050 mm.".format(abs(val))
        #             })
        #     else:
        #         if val < 0 or val > 0.012:
        #             dbOut["defects"].append({
        #                 "name": key,
        #                 "description": "LOC DIAM  is not H7  0 <= {:.3f} <= 0.012 mm.".format(val)
        #             })

        ofile.close()


    # Add a section for defects.
    document.add_heading("Comments and Defects.", level=1)
    added_defects = False
    if len(dbOut["comments"])>0:
        added_defects = True
        document.add_heading("Comments.", level=2)
        for C in dbOut["comments"]:
            document.add_paragraph(C)

    if len(dbOut["defects"])>0:
        added_defects = True
        document.add_heading("Defects.", level=2)
        for D in dbOut["defects"]:
            document.add_paragraph("{}: {}".format(D["name"], D["description"]))

    if not added_defects:
        document.add_paragraph("Petal is GOOD. No comments nor defects found.")


    # close the doc file
    ofile = output_folder(options.folder, options.out)
    document.save(ofile)

    dbOut["results"]["METROLOGY"] = results

    if len(dbOut["defects"])>0:
        dbOut["passed"] = False

    if len(dbOut["comments"])>0:
        dbOut["problems"] = True

    return dbOut

def do_petal_metrology():
    """main entry."""
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--SN", default="SNxxxx", help="Petal core serial nunber")
    parser.add_argument("--front", dest='is_front', action="store_true", default=True)
    parser.add_argument("--back", dest='is_front', action="store_false", default=True)
    parser.add_argument("--prefix", dest='prefix', default="petal_metrology")
    parser.add_argument("--desy", dest='desy', action="store_true", default=False)
    parser.add_argument("--save", dest='save', action="store_true", default=False)
    parser.add_argument("--out", dest="out", default="petal_flatness.docx",
                        type=str, help="The output fiel name")
    parser.add_argument("--title", dest="title", default=None,
                        type=str, help="Document title")
    parser.add_argument("--nbins", dest="nbins", default=25,
                        type=int, help="Number of bins")
    parser.add_argument("--folder", default=None, help="Folder to store output files. Superseeds folder in --out")
    parser.add_argument("--locking_points", action="store_true", default=False)
    # This is to convert a CMM file
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--type", default="Punto", help="The class to select")

    args = parser.parse_args()
    if len(args.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    if len(args.files) == 1:
        ifile = args.files[0]
    else:
        ifnam = NamedTemporaryFile(delete_on_close=False)
        ifile = ifnam.name
        for ff in args.files:
            with open(ff, 'rb') as F:
                ifnam.write(F.read())

        ifnam.close()


    try:
        outDB = petal_metrology(ifile, args)
        ofile = output_folder(args.folder, args.prefix + '.json')
        with open(ofile, 'w', encoding="UTF-8") as of:
            json.dump(outDB, of)

    except Exception:
        print(traceback.format_exc())

    plt.show()

if __name__ == "__main__":
    do_petal_metrology()