"""Thermal result of core."""
import json

import numpy as np

from petal_qc.thermal import Petal_IR_Analysis
from petal_qc.thermal import IRPetalParam


class NumpyArrayEncoder(json.JSONEncoder):
    """Encoder to dump in JSon."""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return vars(obj)


class IRCore(object):
    """All the thermal data needed for one core."""

    def __init__(self, SN, alias="", results=None, params=None) -> None:
        """Initializarion.

        Args:
            SN (str): Serial number of the core
            alias (str): Alternative ID for the core
            params (IRPetalParam): Parameters

        """
        self.coreID = SN
        self.aliasID = alias
        self.date = None
        self.institute = params.institute if params is not None else None
        self.params = params
        self.files = []
        self.results = [] if results is None else results  # list of AnalysisResults. One per side
        self.golden = []                                    # list of Golden results. One per side.
        self.inlet = params.tco2

    def set_files(self, files):
        """Set the input files."""
        self.files = []
        for F in files:
            self.files.append(F)

        print(self.files)

    def set_results(self, results):
        """Set results.

        Args:
            results (list): list of AnalysisResults

        """
        self.results = results

    def add_file(self, fnam):
        """Add a new file path."""
        self.files.append(fnam)

    def to_json(self, pf=None):
        """Dumps to JSon."""
        out = json.dumps(self, indent=3, cls=NumpyArrayEncoder)
        if pf:
            pf.write(out)

        return out

    def apply_deltaT(self, deltaT):
        """Applies a delta T correction."""
        for i in range(2):
            self.results[i].path_temp = np.array(self.results[i].path_temp) + deltaT
            self.results[i].sensor_avg = np.array(self.results[i].sensor_avg) + deltaT

    @staticmethod
    def read_json(fnam):
        """Read a JSon file."""
        js = None
        with open(fnam, 'r', encoding='UTF-8') as ifp:
            js = json.load(ifp)

        return IRCore.from_json(js)

    @staticmethod
    def from_json(J):
        """Loads a JSon object."""
        param = IRPetalParam.IRPetalParam(J["params"])
        results = []
        for o in J["results"]:
            r = Petal_IR_Analysis.AnalysisResult()
            r.from_json(o)
            results.append(r)

        C = IRCore(J["coreID"], J["aliasID"], results=results, params=param)
        C.date = J["date"]
        for F in J["files"]:
            C.add_file(F)

        return C


if __name__ == "__main__":
    with open("core.json", "r", encoding="UTF-8") as ifp:
        O = IRCore.from_json(json.load(ifp))
        print(O)
