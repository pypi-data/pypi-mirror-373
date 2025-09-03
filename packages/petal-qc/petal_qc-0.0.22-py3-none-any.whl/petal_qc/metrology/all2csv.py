#!/usr/bin/env python3
"""Convert all files in input file to CSV (petal, locators)"""
import sys
from metrology.data2csv import data2cvs
from metrology.convert_smartscope import read_smartscope
from collections import namedtuple


class OptDict(dict):
    """https://stackoverflow.com/a/1639632/6494418"""

    def __getattr__(self, name):
        return self[name] if not isinstance(self[name], dict) \
            else OptDict(self[name])


def all2cvs(ifile):
    """Convert files listed in input to CSV."""
    with open(ifile, 'r') as inp:

        for line in inp:
            line = line.strip()
            if len(line) == 0:
                continue

            if line[0] == '#':
                continue

            SN = ""
            try:
                fnam, prefix = line.split()
            except Exception:
                fnam, prefix, SN, *_ = line.split()

            opts = OptDict({"prefix": prefix})
            print(fnam, prefix)
            if options.desy:
                read_smartscope(fnam, prefix + "-petal.csv", "PetalPlane")
                
            else:
                data2cvs([fnam, ], opts)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--desy", dest='desy', action="store_true", default=False)


    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    all2cvs(options.files[0])
