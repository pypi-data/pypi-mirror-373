#!/usr/bin/env python3
"""List failing cores from JSon files."""
import sys
import argparse
from pathlib import Path
import json


try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.utils.ArgParserUtils import RangeListAction
from petal_qc.utils.all_files import all_files



def main(options):
    """main entry."""
    petal_cores = {}
    for fpath in options.files:
        fnam = str(fpath)
        if "PPC." not in fnam:
            continue

        ipos = fnam.find("PPC")
        lpos = fnam[ipos:].find("-")
        petal_id = fnam[ipos:ipos+lpos]
        pid = int(petal_id[4:])
        
        if len(options.cores)>0 and pid not in options.cores:
            continue

        with open(fpath, "r", encoding="utf-8") as fin:
            data = json.load(fin)

        if not data["passed"]:
            if data["component"] is None:
                print("Petal {} has bad Serial number".format(petal_id))
                continue
            
            petalId = "{}-{}".format(petal_id, data["component"])
            if petalId not in petal_cores:
                petal_cores[petalId] = {"FRONT": [], "BACK": []}

            side = "FRONT" if "FRONT" in data["testType"] else "BACK"
            for D in data["defects"]:
                petal_cores[petalId][side].append("{}: {}".format(D["name"], D["description"]))


    keys = sorted(petal_cores.keys())
    for petalId in keys:
        print(petalId)
        for side in ["FRONT","BACK"]:
            if len(petal_cores[petalId][side])>0:
                print("+-", side)
            for D in petal_cores[petalId][side]:
                print("  ", D)

        print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--cores", dest="cores", action=RangeListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")
    opts = parser.parse_args()
    
    
    #folder = Path("/tmp/petal-metrology/results")
    folder = Path("~/tmp/petal-metrology/Production/Results").expanduser()
    opts.files = []
    for fnam in all_files(folder, "*.json"):
        opts.files.append(fnam)
    
    main(opts)