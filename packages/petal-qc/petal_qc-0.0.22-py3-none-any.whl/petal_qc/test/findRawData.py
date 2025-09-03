#!/usr/bin/env python3
"""Locates all raw data files."""

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

def main(folder_in, folder_out):
    """Locate raw data files in input folder and copies them in out folder

    Args:
        folder_in (Path): Input folder
        folder_oyt (Path): Output folder
    """
    inF =  Path(folder_in).expanduser().resolve()
    if not inF.exists():
        print("Input folder does not exist. {}".format(inF))
        return
    
    reg = re.compile(r"(PPC\.[0-9]+).*metr")
    
    outF = Path(folder_out).expanduser().resolve()
    if not outF.exists():
        os.makedirs(outF.as_posix())
        
    list_file = open("{}/raw-data-metrology-cores.txt".format(outF.as_posix()), "w", encoding="UTF-8")
    for fnam in all_files(inF, "PPC*.txt", yield_folders=False):
        R = reg.search(fnam)
        if R is None:
            continue
        
        petal_id = R.group(1)
        if "back" in fnam:
            side = "{}-back".format(petal_id)
            ofile = "{}-back.txt".format(petal_id)
        elif "front" in fnam:
            side = "{}-front".format(petal_id)
            ofile = "{}-front.txt".format(petal_id)
        else:
            print("Invalid file {}".format(fnam))
            continue
        
        out_name = outF / ofile
        list_file.write("{} {} {}\n".format(out_name.as_posix(), side, petal_id))
        shutil.copy(fnam, out_name)
        
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
