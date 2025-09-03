#!/usr/bin/env python3
"""Read JSon files an produces a summary."""

import sys
import json
from pathlib import Path


def testSummary(files, options):
    """PRoduces the summary."""
    ofile = open(Path(options.out).expanduser().resolve(), "w")
    for i, ifile in enumerate(files):
        P = Path(ifile).expanduser().resolve()
        ofile.write(P.stem + '\n')

        with open(P, "r") as inp:
            Js = json.load(inp)

            for D in Js["defects"]:
                ofile.write("{}: {}\n".format(D["name"], D["description"]))

            ofile.write("\n")


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--out", default="testSummary.txt")

    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    testSummary(options.files, options)
