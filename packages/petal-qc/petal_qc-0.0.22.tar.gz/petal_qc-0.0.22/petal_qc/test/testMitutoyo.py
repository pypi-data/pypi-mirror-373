#!/usr/bin/env python
"""Test."""

from pathlib import Path
from petal_qc.metrology import DataFile

ifile = Path("/tmp/petals/re-measured/test-xx.txt")

data = DataFile.read(ifile, r"Punto(-|(Vision-))\d", "Punto")
print(data)
