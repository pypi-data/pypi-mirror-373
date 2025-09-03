#!/usr/bin/env python3
"""Prepare raw data input files from DESY so that we can use them with this code."""
import os
import sys
import fnmatch
import re
import shutil
from pathlib import Path
import argparse

def all_files(root, patterns='*', single_level=False, yield_folders=False):
    """A generator that reruns all files in the given folder.

    Args:
    ----
        root (file path): The folder
        patterns (str, optional): The pattern of the files. Defaults to '*'.
        single_level (bool, optional): If true, do not go into sub folders. Defaults to False.
        yield_folders (bool, optional): If True, return folders as well. Defaults to False.

    Yields
    ------
        str: file path name

    """
    patterns = patterns.split(';')
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)

        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break

        if single_level:
            break

class PetalCore:
    def __init__(self, front, back):
        self.front = {}
        self.back = {}

def main(folder, out_folder):
    """Main entry point.

    It takes DESY raw data files and combines them into  a single file for front
    and back metrology.

    Args:
        folder: the input folder where to find the original files.
        out_folder: the folder where the new fiels will be stored.
    """
    inF =  Path(folder).expanduser().resolve()
    if not inF.exists():
        print("Input folder does not exist. {}".format(inF))
        return
    
    print("Reading folder: {}".format(inF))
    print("output in {}".format(out_folder))
    outF = Path(out_folder).expanduser().resolve()
    if not outF.exists():
        print("creating {}".format(outF))
        os.mkdir(outF)

    rgx = re.compile(r"Project Name: (\w+)side_.*AlternativeID=PPC[-_](\d+)", re.MULTILINE|re.DOTALL)
    petal_cores = {}
    for fnam in all_files(inF, "*.txt"):
        P = Path(fnam).expanduser().resolve()
        print(P.name)
        with open(fnam, "r", encoding="UTF-8") as ff:
            R = rgx.search(ff.read())
            if R:
                petal_id = "PPC.{}".format(R.group(2))
                side = R.group(1).lower()
                if "_2D_" in P.name:
                    test_type = "2D"
                else:
                    test_type = "3D"

                if not petal_id in petal_cores:
                    petal_cores[petal_id] = {
                                             "back":{"2D":None, "3D":None},
                                             "front":{"2D":None, "3D":None},
                                             }

                petal_cores[petal_id][side][test_type] = P

    list_file = open("{}/Desy-cores.txt".format(outF.as_posix()), "w", encoding="UTF-8")
    for petal_id, sides in petal_cores.items():
        for side, values in sides.items():
            oname = "{}/{}-{}.txt".format(outF.as_posix(), petal_id, side)
            list_file.write("{} {}-{} {}\n".format(oname, petal_id, side, petal_id))
            data = ""
            for data_type, fnam in values.items():
                if fnam is None:
                    print("Missing file name for {} {} [{}]".format(petal_id, side, data_type))
                    continue

                with open(fnam, "r", encoding="UTF-8") as ifile:
                    data += ifile.read()

            with open(oname, "w", encoding="UTF-8") as ofile:
                ofile.write(data)

    list_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", dest="input", default=None, help="Input folder")
    parser.add_argument("--output-folder", dest="output", help="Outout fodler", default=None)
    opts = parser.parse_args()
    if opts.input is None or opts.output is None:
        print("I need both an input and an output folder.")
        sys.exit(-1)

    main(opts.input, opts.output)
