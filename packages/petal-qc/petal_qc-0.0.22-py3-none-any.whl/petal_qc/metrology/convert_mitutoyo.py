#!/usr/bin/env python3
"""Convert mitutoyo output into CSV."""
import argparse
import fnmatch
import io
import os
import re
import sys
from pathlib import Path


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


def mitutoyo2cvs(infiles, ofile, label='\\w+', data_type="Punto", keep=False, fill=-1):
    """Converts a Mityutoyo ASCII file to csv.

    Stores the X, Y and Z coordinates in the objects defined by object with
    label matching the input.

    Args:
    ----
        infiles: List of input files
        ofile: Output file
        label (optional): label of the objects to convert. Defaults to '\w+'.
        data_type (optional): Type of objects. Defaults to "Punto".
        keep (optional): keep the label in the output table. Defaults to False.
        fill (optional): if given, fill CVS lines to have up to fill items

    """
    # print("^{}:\\s+({})".format(type, label))
    rgx = "^({}):\\s+({})".format(data_type, label)
    start = re.compile(rgx, re.DOTALL)

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

    for fnam in infiles:
        ifile = Path(fnam).expanduser().resolve()
        fin = open(ifile, 'r', encoding='ISO-8859-1')

        for line in fin:
            line = line.replace("Cï¿½rculo", "Círculo") \
                       .replace("Lï¿½nea", "Linea") \
                       .replace("ï¿½ngulo", "Ángulo") \
                       .replace("Diï¿½metro", "Diámetero")
            r = start.match(line)
            if r:
                the_type = r.group(1)
                the_label = r.group(2)

            else:
                continue

            line_data = []
            while True:
                ss = fin.readline()
                if len(ss)==0 or ss[0] == '\n':
                    break

                dd = [s.strip().replace(',', '.') for s in ss.split('=')]
                try:
                    line_data.append(float(dd[1]))
                except IndexError:
                    print("Incomplete data line.")
                    print(ss)
                    print(dd)

            if fill > 0:
                while len(line_data) < fill:
                    line_data.append(0.0)

            else:
                if len(line_data)<3:
                    print("Warning: less than three data points: {}".format(','.join([str(v) for v in line_data])))
                    continue

            slin = ','.join([str(v) for v in line_data])
            fout.write(slin)
            if keep:
                fout.write(",{}\n".format(the_label))
            else:
                fout.write('\n')

        fin.close()

    if is_file:
        fout.close()


def convert_all_in_folder(indir, outdir, patterns='*', label='\\w+', data_type="Punto"):
    """Call mitutoyo2cvs to all files in folder and store them in outpuit folder.

    Args:
    ----
        indir: input folder
        outdir: output folder
        patterns (optional): ';' separted list of file patterns to match. Defaults to '*'.
        label (optional): see mitutoyo2cvs. Defaults to '\w+'.
        data_type (optional): see mitutoyo2cvs. Defaults to "Punto".

    """
    idir = ifile = Path(indir).expanduser().resolve()
    if not idir.exists():
        raise ValueError("Input folder does not exist.")

    odir = ifile = Path(outdir).expanduser().resolve()

    for ipath in all_files(idir, patterns=patterns):
        ifile = Path(ipath)
        oname = ifile.stem + '.csv'
        fdir = ifile.parent.relative_to(idir)
        fdir = Path.joinpath(odir, fdir)
        if not fdir.exists():

            Path.mkdir(fdir, parents=True)

        ofile = Path.joinpath(fdir, oname)
        mitutoyo2cvs([ifile], ofile, label, data_type)
        print(ifile)
        print(ofile)
        print('.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mitutoyo_files", nargs='*',
                        help="The Mitutoyo file to parse")
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--type", default="Punto", help="The class to select")
    parser.add_argument("--out", help="Outout CSV file", default="out.csv")
    parser.add_argument("--keep_label", dest="keep", default=False, action="store_true", help="Store label in output")

    args = parser.parse_args()
    if len(args.mitutoyo_files) == 0:
        print("I need an input file")
        sys.exit()

    mitutoyo2cvs(args.mitutoyo_files, args.out, args.label, args.type, args.keep)
