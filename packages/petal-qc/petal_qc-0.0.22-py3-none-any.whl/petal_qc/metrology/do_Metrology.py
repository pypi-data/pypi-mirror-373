#!/usr/bin/env python3
"""Does metrology of all files listed at input file.

Examples:

python3 ~/cernbox/workspace/Petal-QC/do_Metrology.py ~/Desktop/petal-metrology-files.txt
python3 ~/cernbox/workspace/Petal-QC/do_Metrology.py --desy ~/Desktop/DESY-petal-metrology.txt

"""
import json
import sys
import traceback
from argparse import Action
from argparse import ArgumentParser
from pathlib import Path
import numpy as np

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from petal_qc.utils.utils import output_folder
from petal_qc.metrology.PetalMetrology import petal_metrology

def do_analysis(fnam, prefix, SN, options):
    """Perform analysis of a file.

    Args:
        fnam: Input data file
        prefix: Prefix telling if it is front or back
        SN: Core serial number
        options: Options.

    """

    is_front = prefix.lower().find("front") >= 0
    print(fnam, prefix)
    options.out = prefix + '.docx'
    options.title = prefix
    options.is_front = is_front
    if not hasattr(options, "SN"):
        options.SN = ""

    options.SN = SN
    outDB = petal_metrology(fnam, options)

    ofile = output_folder(options.folder, prefix + '.json')
    with open(ofile, 'w', encoding='UTF-8') as of:
        json.dump(outDB, of, indent=3)

    return outDB

def analyze_files(ifile, options):
    """Main entry."""
    failed_files = []
    with open(ifile, 'r', encoding='ISO-8859-1') as inp:

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

            try:
                with open(fnam, "r", encoding="ISO-8859-1") as fin:
                    ss = fin.read()
                    if ss.find("Punto:")<0:
                        options.desy=True
                    else:
                        options.desy=False

                do_analysis(fnam, prefix, SN, options)
                print("\n\n")
            except Exception as E:
                failed_files.append([fnam, E])
                continue

    if len(failed_files)>0:
        for fnam, E in failed_files:
            print("### Failed file {}\n{}".format(fnam, E))

def parse_options():
    """Parse command line options."""
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--prefix", dest='prefix', default=None, help="prefix telling if it is front or back.")
    parser.add_argument("--SN", dest='SN', default=None, help="The petal core Serial Number")
    parser.add_argument("--save", dest='save', action="store_true", default=False)
    parser.add_argument("--desy", dest='desy', action="store_true", default=False, help="True if data is from DESY's SmartScope")
    parser.add_argument("--out", dest="out", default="petal_flatness.docx",
                        type=str, help="The output file name")
    parser.add_argument("--title", dest="title", default=None,
                        type=str, help="Report Document title")
    parser.add_argument("--nbins", dest="nbins", default=25,
                        type=int, help="Number of bins in the histograms")
    parser.add_argument("--folder", default=None, help="Folder to store output files. Superseeds folder in --out")
    parser.add_argument("--locking_points", action="store_true", default=False)

    # This is to convert a CMM file
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--type", default="Punto", help="The class to select")

    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    return options

def main():
    "Main entry."
    options = parse_options()
    try:
        analyze_files(options.files[0], options)

    except Exception:
        print(traceback.format_exc())

def analyze_core_metrology():
    """Do a single file analysis."""
    options = parse_options()
    do_analysis(options.files[0], options.prefix, options.SN, options)

if __name__ == "__main__":
    main()