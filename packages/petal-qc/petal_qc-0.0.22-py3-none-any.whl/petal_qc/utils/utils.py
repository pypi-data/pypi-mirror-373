#!/usr/bin/env python3
"""A set of utilities."""
import fnmatch
import os
import re
from collections.abc import Iterable
from pathlib import Path
import numpy as np


def is_iterable(obj):
    """Tell if an object is iterable. Strings are not considered iterables."""
    if isinstance(obj, Iterable):
        if isinstance(obj, str) or isinstance(obj, bytes):
            return False
        else:
            return True
    else:
        return False


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


def find_out_file_name(fnam):
    """Get file name.

    Check wheter file already exists and build a name with
    a sequence number.

    Args:
    ----
        fnam: Input file name.

    Returns
    -------
        new file name with sequence.

    """
    R = re.compile(r'.*\(([0-9]*)\)')
    pout = Path(fnam).expanduser().absolute()
    odir = pout.parent
    orig_stem = pout.stem
    lstem = len(orig_stem)

    while pout.exists():
        version = 1
        stem = pout.stem[lstem:]
        M = R.match(stem)
        if M:
            version = int(M.group(1))
            version += 1

        fout = "{} ({}){}".format(orig_stem, version, pout.suffix)
        pout = Path(odir, fout)

    return pout


def output_folder(folder, fname):
    """Rename file to be "stored" in folder.

    Args:
    ----
        folder: The folder path
        fname: The file path

    Returns
    -------
        Path: The new file path

    """
    if folder is None:
        return fname

    ifolder = Path(folder).expanduser().resolve()
    if not ifolder.exists():
        print("Creating folder {}".format(ifolder))
        os.makedirs(ifolder)

    # Append folder to output file name
    of = Path(fname).expanduser().resolve()
    ofile = ifolder / of.name

    return ofile


def find_file(folder, fname):
    """Find file and fallback to folder if not found.

    Note: it just builds teh file name if the input file
          does not exist. Does not check for esistance of file
          within folder.

    Args:
    ----
        folder: The folder
        fname: The file name

    Returns
    -------
        Path: the new file path.

    """
    ifile = Path(fname).expanduser().resolve()
    if folder is None:
        return ifile

    if ifile.exists():
        return ifile

    else:
        ifolder = Path(folder).expanduser().resolve()
        ofile = ifolder / ifile.name
        return ofile


def get_min_max(values, step=None):
    """Return min and max.

    The values are alined with step.

    Args:
    ----
        values: Array of values
        step (optional): The step. Defaults to 1.0.

    Returns
    -------
        min, max.

    """
    vmax = np.amax(values)
    vmin = np.amin(values)

    if step is not None:
        ivmax = round(vmax)
        if ivmax < vmax:
            ivmax += step
            if abs(ivmax-vmax) < 0.25*step:
                ivmax += step

        ivmin = np.round(vmin)
        if ivmin > vmin:
            ivmin -= step
            if abs(ivmin-vmin) < 0.25*step:
                ivmin -= step

        return ivmin, ivmax, abs(ivmax-ivmin)

    else:
        return vmin, vmax, abs(vmax-vmin)
