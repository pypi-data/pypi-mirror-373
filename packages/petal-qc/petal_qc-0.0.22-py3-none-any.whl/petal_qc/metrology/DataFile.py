"""Gets the Metrology data from a file."""
from tempfile import NamedTemporaryFile

import numpy as np

from .convert_mitutoyo import mitutoyo2cvs
from .convert_smartscope import read_smartscope


def read(fname, label='\\w+', type="Punto", keep=False):
    """Read a file.

    Args:
    ----
        fname: The file name
        label: the label for an mitutyyo file
        type: the entry type in a mitutoyo file
        keep: if true keeps the label
    """
    try:
        data = np.loadtxt(fname, unpack=False, skiprows=1, delimiter=',')

    except FileNotFoundError:
        print("Input file not found.")
        return None

    except Exception:
        # This might be CMM file
        is_mitutoyo = False
        with open(fname, 'r', encoding='cp1252') as fin:
            for line in fin:
                if 'Elemento' in line:
                    is_mitutoyo = True
                    break
                elif 'Quality Vision' in line:
                    is_mitutoyo = False
                    break
        
        ofile = NamedTemporaryFile()
        if is_mitutoyo:
            mitutoyo2cvs([fname], ofile.name, label=label, data_type=type, keep=keep)
        else:
            read_smartscope(fname, ofile.name, label, keep=keep)
            
        data = np.loadtxt(ofile.name, unpack=False, skiprows=1, delimiter=',')

    return data
