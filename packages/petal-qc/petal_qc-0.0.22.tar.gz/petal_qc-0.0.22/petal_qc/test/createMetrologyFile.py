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

def main(options):
    """Locate raw data files in input folder and copies them in out folder

    Args:
        folder_in (Path): Input folder
        folder_oyt (Path): Output folder
    """
    reg = re.compile(r"(PPC\.[0-9]+)-(\w+)")
    outF = Path(options.output).expanduser().resolve()
    with open(outF, "w", encoding="utf-8") as fout:
        for folder_in in options.files:
            inF =  Path(folder_in).expanduser().resolve()
            if not inF.exists():
                print("Input folder does not exist. {}".format(inF))
                continue

            for fnam in all_files(inF, "PPC*.txt", yield_folders=False):
                R = reg.search(fnam)
                if R is None:
                    continue
                
                petal_id = R.group(1)
                side = R.group(2)
                fout.write("{ifile} {pid}-{side} {pid}\n".format(ifile=fnam, side=side, pid=petal_id))
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--output", dest="output", help="Output file", default="out.txt")
    opts = parser.parse_args()
    if len(opts.files)==0:
        print("I need at least one input folder")
        sys.exit(-1)

    main(opts)
