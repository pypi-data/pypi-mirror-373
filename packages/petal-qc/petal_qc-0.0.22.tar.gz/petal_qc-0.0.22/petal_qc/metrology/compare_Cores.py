#!/usr/bin/env python3
"""Compare quantities."""

import sys
import re

import argparse
import glob
import json
import math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

r_petal_id = re.compile("PPC.([0-9]*)")

class PetalCoreListAction(argparse.Action):
    """Create a list from the comma sepparated numbers at imput."""

    def __call__(self, parser, namespace, values, option_string=None):
        """The actual action."""
        value = []
        for V in values.split(','):
            try:
                value.append(int(V))
            except ValueError:
                if ':' not in V:
                    continue

                items = V.split(':')
                if len(items)==1:
                    continue

                ival = list(map(int, items))
                ival[1] += 1
                for x in range(*ival):
                    value.append(int(x))


        setattr(namespace, self.dest, value)


def get_value(data, value_path):
    """Get the value from the path given."""
    a = data
    for k in value_path.split('/'):
        a = a[k]

    return a

def save_figure(fig, fnam, prefix=None, dpi=192):
    """Saves the figure

    Args:
        fig (Figure): The figure to save
        fnam (str): The name of the output file
        dpi (int, optional): The Dots por Inch. Defaults to 300.
    """
    if fnam is not None:
        if prefix:
            P = Path(fnam).expanduser().resolve()
            name = prefix + P.name
            out = P.parent / name
            fnam = out

        print("out: {}".format(fnam))
        fig.savefig(fnam, dpi=dpi)


def read_data_files(options):
    """Read the data files.

    It assumes the data file names are in the format:

    <AlternativeID>-<side>.json

    AlternativeID is PPC.nnn side is either front or back.

    Returns the values for front and back petal tests.

    The results are a dictionary with the file label as key and the requested
    value, which can be a number of an array.

    the file labels are also returned.

    """
    labels = []
    front = {}
    back = {}

    has_list = len(options.cores) != 0

    for fnam in options.files:
        ifile = Path(fnam).expanduser().resolve()
        if not ifile.exists():
            print("File does not exist: ", fnam)
            continue

        R = r_petal_id.search(fnam)
        if R is None:
            continue

        petal_id = R.group(0)
        pid = int(R.group(1))

        if has_list and pid not in options.cores:
            continue


        data = None
        with open(ifile, 'r', encoding="UTF-8") as fp:
            data = json.load(fp)

        if data is None:
            print("Problems reading ", fnam)
            continue

        tmp = ifile.name.split('-')
        label = tmp[0]
        if not label in labels:
            labels.append(label)

        try:
            val = get_value(data, options.value)
            if "front" in tmp[1].lower():
                front[label] = val
            else:
                back[label] = val
        except KeyError as E:
            print("Error in {}:\n{}".format(fnam, E))
            continue

    labels.sort()

    return front, back, labels

def draw_deltas(data, keys, fnam=None, title="Front", draw_text=True):
    """Plot the  position deltas."""
    key_table = {"Bot.": "PL01", "Slot": "PL02", "Top": "PL03",
                 "Bot-FD01": "PL01-FD01", "Bot-FD02": "PL01-FD02", "FD01-FD02": "FD01-FD02" }
    nfiles = len(data)

    P = [np.zeros([nfiles, 2]),
         np.zeros([nfiles, 2]),
         np.zeros([nfiles, 2])]
    D = [[],[],[]]
    
    fig_width = 12.0
    fig_height = 1.2*fig_width/3.0
    fig, ax = plt.subplots(nrows=1, ncols=3, tight_layout=True, figsize=(fig_width, fig_height))
    fig.suptitle(title)
    figb, bx = plt.subplots(nrows=1, ncols=3, tight_layout=True, figsize=(fig_width, fig_height))
    figb.suptitle(title)
    
    for i in range(3):
        LBL = [[],[],[]]
        ax[i].set_title(keys[i])
        ax[i].set_aspect('equal', adjustable='box')
        ax[i].set_xlim(-150, 150)
        ax[i].set_ylim(-150, 150)
        circle = plt.Circle((0,0), 100, color="red", alpha=0.25)
        ax[i].add_patch(circle)
        circle = plt.Circle((0,0), 25, color="green", alpha=0.25)
        ax[i].add_patch(circle)

        ax[i].set_xlabel("X (µm)")
        ax[i].set_ylabel("Y (µm)")
        ax[i].grid()
        
        bx[i].set_title(keys[i])
        bx[i].set_xlabel("Distance (µm)")
        bx[i].grid()
        

        for j, v in enumerate(data.items()):
            label, values = v
            for k in range(3):
                ky = key_table[keys[k]]
                point = 1000*np.array(values[ky])
                P[k][j, :] = point
                D[k].append(math.sqrt(point[0]**2+point[1]**2))
                LBL[k].append(label.split('.')[1].lstrip('0'))

        bx[i].hist(D[i], bins=15, range=(0, 150))
        ax[i].scatter(P[i][:,0], P[i][:,1])
        if draw_text:
            for j in range(len(LBL[i])):
                ax[i].text(P[i][j,0], P[i][j,1], LBL[i][j]) #, ha='center', va='top')

    ofile = Path(fnam).expanduser().resolve()
    print("* parent: ", ofile.parent)
    print("* stem: ", ofile.stem)
    bnam = ofile.parent / "{}-h.png".format(ofile.stem)
    print(bnam.as_posix())
    save_figure(fig, fnam, prefix=title)
    save_figure(figb, bnam, prefix=title)


def show_positions(options):
    """Make position plots."""

    if "LOCATION" in options.value:
        keys = ["Bot.", "Slot", "Top"]
    elif "REL_POS" in options.value:
        keys = ["Bot-FD01", "Bot-FD02", "FD01-FD02"]
    else:
        print("Invalid value")
        return

    front, back, labels = read_data_files(options)
    val_name = options.value.split('/')[-1]
    draw_text = not options.no_legend
    draw_deltas(front, keys, fnam=options.out, title="{} - Front".format(val_name), draw_text=draw_text)
    draw_deltas(back, keys, fnam=options.out, title="{} - Back".format(val_name), draw_text=draw_text)

    if not options.no_show:
        plt.show()

def show_flatness(options):
    """Show flatness plots."""
    tick_labels =  ["R0", "R1", "R2", "R3S0", "R3S1", "R4S0", "R4S1", "R5S0", "R5S1"]
    cindx = ["Front", "Back"]

    front, back, labels = read_data_files(options)
    nfiles = len(labels)
    npts = len(tick_labels)
    X = np.array([float(x) for x in range(npts)])


    fig, ax = plt.subplots(nrows=1, ncols=2, tight_layout=True, figsize=(9., 5.))
    fig.suptitle(options.value)

    P = [ np.zeros([nfiles, npts]), np.zeros([nfiles, npts]) ]
    y_lim = []
    for i, V in enumerate([front, back]):
        ax[i].set_title(cindx[i])
        ax[i].set_xticks(range(npts), labels=tick_labels)
        ax[i].grid()

        for lbl in labels:
            ax[i].plot(X, V[lbl], '-', label=lbl)

        y_lim.append(ax[i].get_ylim())

    for a in ax:
        #a.set_ylim(0, 1.2*max(y_lim[0][1], y_lim[1][1]))
        a.set_ylim(0, 0.150)
        x_lim = a.get_xlim()
        a.fill_between(x_lim, 0, 0.050, facecolor="darkseagreen", alpha=0.1)
        a.fill_between(x_lim, 0.050, 0.100, facecolor="mediumseagreen", alpha=0.1)
        if not options.no_legend:
            a.legend(ncol=3, fontsize="x-small")

    save_figure(fig, options.out, prefix=options.prefix)

def main(options):
    """Main entry."""

    if "LOCATION" in options.value or "REL_POS" in options.value:
        show_positions(options)

    elif "FLATNESS_LOCAL" in options.value:
        show_flatness(options)

    else:
        front, back, labels = read_data_files(options)

        labels.sort()
        X = np.arange(0, len(labels))
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        fig.suptitle(options.value)
        ax.set_xticks(range(len(labels)), labels=labels, rotation="vertical")
        ax.grid()

        vfront = [front[x] for x in labels]
        vback = [back[x] for x in labels]
        ax.plot(X, vfront, '*', label="Front")
        ax.plot(X, vback, 'o', label="Back")
        if not options.no_legend:
            ax.legend()

        save_figure(fig, options.out, prefix=options.prefix)

        fig, ax = plt.subplots(1, 2, tight_layout=True)
        fig.suptitle("Histogram: {}".format(options.value))
        ax[0].hist(vfront, bins=15)
        ax[0].set_title("Front")
        ax[0].grid()
        ax[1].hist(vback, bins=15)
        ax[1].set_title("Back")
        ax[1].grid()
        name = Path(options.out)
        name = name.parent / "{}-hst.png".format(name.stem)
        save_figure(fig, name, prefix=options.prefix)

    if not options.no_show:
        plt.show()


if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--value", default=None, help="Value to plot")
    parser.add_argument("--prefix", default=None, help="prefix for out file")
    parser.add_argument("--out", default=None, help="File to store the figure.")
    parser.add_argument("--no-legend", dest="no_legend", default=False, action="store_true", help="Do not draw the legend")
    parser.add_argument("--no-show", dest="no_show", default=False, action="store_true", help="Do not show the figure")
    parser.add_argument("--cores", dest="cores", action=PetalCoreListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")

    opts = parser.parse_args()
    if len(opts.files) == 0:
        print("I need at least one input file")
        sys.exit()

    elif len(opts.files) == 1:
        xxx = any(elem in opts.files[0] for elem in r"*?")
        if xxx:
            opts.files = glob.glob(opts.files[0])

    if opts.value[0] == '/':
        opts.value = opts.value[1:]
    opts.value = "results/METROLOGY/" + opts.value
    main(opts)
