#!/usr/bin/env python3
"""Create  table for metrology analysis."""

import sys
import re
import json
from pathlib import Path
from argparse import ArgumentParser
from petal_qc.utils.all_files import all_files
from petal_qc.utils.ArgParserUtils import RangeListAction

r_petal_id = re.compile("PPC.([0-9]*)")

db_file = Path("/Users/lacasta/cernbox/workspace/Petal-QC/PetalMould.csv")

petal_db = {}
with open(db_file, "r", encoding="utf-8") as fin:
    for i, line in enumerate(fin):
        if i==0:
            continue

        values = [x.strip() for x in line.split(",")]
        petal_db[values[0]] = values[1:]

def main(options):
    """Main entry."""
    ifolder = Path(options.input)
    if not ifolder.exists():
        print("Input folder does not exist.\n{}".format(ifolder))
        return

    has_list = len(options.cores) != 0

    ofile = open(options.out, "w", encoding="utf-8")
    ofile.write("PetalID,SN,side,mould,fd_dx,fd_dy,paralelism,R0,R1,R2,R3S0,R3S1,R4S0,R4S1,R5S0,R5S1,flatness\n")

    for fnam in all_files(ifolder.as_posix(), "*.json"):
        fstem = fnam.stem
        if "PPC." not in fstem:
            continue

        R = r_petal_id.search(fstem)
        if R is None:
            continue

        petal_id = R.group(0)
        pid = int(R.group(1))

        if has_list and pid not in options.cores:
            continue

        SN = petal_db[petal_id][0]
        side = 1 if "back" in fstem else 0
        mould = int(petal_db[petal_id][1])

        data = None
        with open(fnam, "r", encoding="utf-8") as fin:
            data = json.load(fin)

        ofile.write("{}, {}, {}, {}".format(petal_id, SN, side, mould))
        print("data SN", data["component"])
        D = data["results"]["METROLOGY"]["REL_POS_DELTA"]["FD01-FD02"]
        ofile.write(",{:.5f}, {:.5f}".format(D[0], D[1]))

        D = data["results"]["METROLOGY"]["PARALLELISM"]
        ofile.write(",{:.5f}".format(D))

        for x in data["results"]["METROLOGY"]["FLATNESS_LOCAL"]:
            ofile.write(", {:.5f}".format(x))

        D = data["results"]["METROLOGY"]["FLATNESS_GLOBAL"]
        ofile.write(", {:.5f}".format(D))

        ofile.write("\n")

    ofile.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input-folder", dest="input", default=".", help="Input folder")
    parser.add_argument("--out", default="out.csv", help="Output table.")
    parser.add_argument("--cores", dest="cores", action=RangeListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")

    opts = parser.parse_args()
    main(opts)