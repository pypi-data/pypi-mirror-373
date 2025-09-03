#!/usr/bin/env python3
"""Analyze COLDBOX files."""
import sys
import os
from argparse import ArgumentParser
from pathlib import Path
import fnmatch

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
        A file Path

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


def bad_line(lst):
    """Fixes lines for read_csv."""
    out = [lst[i] for i in range(5)]
    out.append(" ".join(lst[5:]))
    return out


def analyze_folder(folder_list, options):
    """Analyze files in input folder."""
    for folder in folder_list:
        folder = Path(folder).expanduser().resolve()
        if not folder.exists():
            print("### Folder {} does not exist !".format(folder))
            continue
        
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        fig.suptitle("Noise .vs. channel")
        ax.set_xlabel("Channel")
        ax.set_ylabel("innse")
        meanV = []
        for F in all_files(folder, '*.txt', True):
            df = pd.read_csv(F, 
                             #names=["chan", "code", "gain", "vt50", "innse", "comment"],
                             header=None, skiprows=lambda x: x == 0,
                             delim_whitespace=True,
                             engine="python", on_bad_lines=bad_line)
            x = df[0].values
            y = df[4].values
            ymax = np.argmax(y)
            ymin = np.argmin(y)
            if y[ymax] > 2000:
                print("{} Max: {}".format(ymax, y[ymax]))
            
            if y[ymin] <= 0:
                print("{} Min: {}".format(ymin, y[ymin]))
                
            indx = np.where((y < 2500) & (y > 0))[0]
            ymean = np.mean(y[indx])
            meanV.append(ymean)
                
            ax.plot(x, y, '-', label=Path(F).name)

        yavg = np.nanmean(meanV)
        ax.set_ylim(0.5*yavg, 1.5*yavg)
        ax.grid()
        
        #ax.legend()
        
    plt.show()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    
    options = parser.parse_args()
    if len(options.files) == 0:
        print(sys.argv[0])
        print("I need an input file")
        sys.exit()

    analyze_folder(options.files, options)