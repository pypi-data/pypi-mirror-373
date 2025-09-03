#!/usr/bin/env python3
"""Convert mitutoyo output into CSV."""
import io
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


from petal_qc.metrology import DataFile
#from .analyze_locking_points import analyze_locking_point_data

def get_data_chunck(flist, data_type, ofile):
    """Get one data type chunk from file

    Args:
        fname: input file
        data_tyle: data type
        ofile: file object for output.

    """
    rgx = "Step Name:\\s+({}).*?=".format(data_type)
    print("Regex: {}\n".format(rgx))
    start = re.compile(rgx, re.DOTALL)
        
    for fname in flist:
        ifile = Path(fname).expanduser().resolve()
        print(ifile)
        ss = None
        with  open(ifile, 'r', encoding='ISO-8859-1') as fin:
            ss = fin.read()

        if not ss:
            return
                
        for txt in start.finditer(ss):
            print(txt.group(1))
            if ofile:
                ofile.write(txt.group(0)+'\n')
    

def read_smartscope(fnam, ofile, data_type, keep=False):
    """Convert a SmartScope txt file into CVS

    Args:
        fnam: Input file pat
        ofile: Output file
        data_type: Data label in file
        keep (optional): keep the label in the output table. Defaults to False.

    """
    ifile = Path(fnam).expanduser().resolve()
    fin = open(ifile, 'r', encoding='ISO-8859-1')

    is_file = False
    if isinstance(ofile, io.IOBase):
        fout = ofile
    else:
        try:
            fout = open(ofile, 'w', encoding="utf-8")
        except TypeError:
            fout = ofile

        is_file = True

    if keep:
        fout.write("X,Y,Z, label\n")
    else:
        fout.write("X,Y,Z\n")

    rgx = "^Step Name:\\s+{}".format(data_type)
    start = re.compile(rgx, re.DOTALL)
    finder = re.compile("^Finder Name")

    while True:
        line = fin.readline()
        if not line:
            break

        r = start.match(line)
        if not r:
            continue

        eof = False
        while True:
            line = fin.readline()
            if not line:
                eof = True
                break

            r = finder.match(line)
            if r:
                break

        # Read the header line and to the numbers
        while not eof:
            line = fin.readline()
            if not line:
                break

            if line[0] == '-':
                continue

            if line[0] == "=":
                break

            items = line.split()
            values = [ float(x) for x in items[2:5]]
            fout.write("{:6f}, {:6f}, {:6f}\n".format(values[1], values[0], values[2]))

    if is_file:
        fout.close()
    
def get_smarscope_locator_positions(fnam, ofile, data_type, keep=False):
    """REad DESY 2D file.

    Args:
        fnam: Input file
        ofile: Output file
        data_type: Label to search
        keep (bool, optional): If tre keep label. Defaults to False.
    """
    ifile = Path(fnam).expanduser().resolve()
    
    is_file = False
    if isinstance(ofile, io.IOBase):
        fout = ofile
    else:
        try:
            fout = open(ofile, 'w', encoding="utf-8")
        except TypeError:
            fout = ofile

        is_file = True

    if keep:
        fout.write("X,Y,Z, label\n")
    else:
        fout.write("X,Y,Z\n")

    rgx = "^Step Name:\\s+(?P<label>{})".format(data_type)
    start = re.compile(rgx, re.DOTALL)
    finder = re.compile("^Finder Name")

    out = {}
    with open(ifile, 'r', encoding='ISO-8859-1') as fin:
        while True:
            line = fin.readline()
            if not line:
                break

            r = start.match(line)
            if not r:
                continue
            
            label = r.group('label').strip()
            eof = False
            out[label] = [0. for i in range(3)]
            for i in range(3):
                line = fin.readline()
            
            while True:
                line = fin.readline().strip()
                if len(line)==0:
                    break
            
                values = line.split()
                val = float(values[3])
                if values[0] in ["Diame", "Width"]:
                    out[label][2] = val
                elif values[0] == "X":
                    out[label][1] = val
                elif values[0] == "Y":
                    out[label][0] = val
                    
    lbls = ["BottomPL", "SlotPL", "OversizedPL", "Bottom_Fiducial", "Slot_Fiducial"]
    for L in lbls:
        try:
            V = [float(x) for x in out[L]]
            fout.write("{:.6f}, {:.6f}, {:.6f}".format(V[0], V[1], V[2]))
            if keep:
                fout.write(", {}".format(L))
            fout.write('\n')
        except KeyError:
            continue
                          
    if is_file:
        fout.close()

def do_locking_points(args):
    ifile = args.smartscope_files[0]
    flatness_data = DataFile.read(ifile, "PetalPlane")
    locator_data = DataFile.read(ifile, ".*_FineFlatness")

    data = np.concatenate((flatness_data, locator_data))
    analyze_locking_point_data(data, document=None, nbins=50, plane_fit=True)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='*',
                        help="The SmartScope files to parse")
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--out", help="Output CSV file", default="out.csv")
    parser.add_argument("--keep_label", dest="keep", default=False, action="store_true", help="Store label in output")

    args = parser.parse_args()
    if len(args.files) == 0:
        print("I need an input file")
        sys.exit()



    # do_locking_points(args)
    
    #fout = open(Path(args.out).expanduser().resolve(), 'w')
    #get_data_chunck(args.smartscope_files, args.label, fout)
    #fout.close()
    
    
    #read_smartscope(args.smartscope_files[0], args.out, args.label, args.keep)

    get_smarscope_locator_positions(args.files[0], args.out, args.label)

    plt.show()
