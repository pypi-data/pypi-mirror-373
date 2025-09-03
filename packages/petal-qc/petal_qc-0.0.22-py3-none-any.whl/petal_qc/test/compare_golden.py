#!/usr/bin/env python3
"""Compara golden files."""
import json
import sys
from pathlib import Path
from argparse import ArgumentParser
import numpy as np
import matplotlib.pyplot as plt


def compare_golden(files):
    """Go through files."""
    fig, ax = plt.subplots(2, 1, tight_layout=True)
    for ff in files:
        ifile = Path(ff).expanduser().resolve()
        if not ifile.exists():
            print("ff does not exist.")
            continue
        
        js = None
        with open(ifile, "r", encoding="utf-8") as fp:
            js = json.load(fp)
            
        if js is None:
            print("Cannot load {}".format(ff))
            continue
        
        for iside in range(2):
            ax[iside].plot(js[iside]["path_length"], js[iside]["path_temp"], '-', label=ifile.name)
    
    for iside in range(2):   
        ax[iside].legend()
    plt.show()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")

    options = parser.parse_args()
    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    compare_golden(options.files)
