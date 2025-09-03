#!/usr/bin/env python3
"""Test dashboard."""
import os
import sys
import copy
from pathlib import Path
from argparse import ArgumentParser

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())
    import itkdb_gtk

from itkdb_gtk import ITkDBlogin, ITkDButils, UploadTest
from petal_qc.utils.ArgParserUtils import RangeListAction


HOME=os.getenv("HOME")
cloud=Path("{}/Nextcloud/ITk/5-Petal_cores".format(HOME))

def uploadXrays(session, options):
    """Upload Xray tests."""
    if len(options.cores) == 0:
        print("I need a list of cores.")
        return

    defaults = {
            "institution": "IFIC",
            "runNumber": "1",
        }

    dto = ITkDButils.get_test_skeleton(session, "CORE_PETAL", "XRAYIMAGING", defaults)
    dto["properties"]["OPERATOR"]="Nico"
    dto["properties"]["MACHINEID"]="Xray"
    
    for core in options.cores:
        petal_id = "PPC.{:03d}".format(core)
        try:
            obj = ITkDButils.get_DB_component(session, petal_id)
            SN = obj["serialNumber"]

        except Exception as E:
            print("Could not find {} in DB:\n{}".format(petal_id, E))
            continue

        values = copy.deepcopy(dto)
        print("Petal {}".format(petal_id))
        values["component"] = SN

        image = cloud / petal_id / "Rx_{}.png".format(petal_id)
        if not image.exists():
            print("Xray image does not esxist.\n\t{}".format(image))
            continue

        A = ITkDButils.Attachment(path=image.as_posix(), title=image.name, desc="X-ray image")
        values["results"]["IMAGELINK"] = image.name
        uploadW = UploadTest.UploadTest(session, values, [A, ])



def main():
    """Main entry"""
    parser = ArgumentParser()
    parser.add_argument("--cores", dest="cores", action=RangeListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")
    options = parser.parse_args()

    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    session = dlg.get_client()

    try:
        uploadXrays(session, options)

    except Exception as E:
        print(E)

    dlg.die()



if __name__ == "__main__":
    main()