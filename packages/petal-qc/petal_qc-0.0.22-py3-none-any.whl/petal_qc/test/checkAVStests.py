#!/usr/bin/env python3
"""Analize AVS metrology tests."""
import sys
from pathlib import Path
import numpy as np

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin, ITkDButils
from petal_qc.metrology.readAVSdata import readFATfile


def set_pos(V, results, obj):
    """Update positions."""
    results["{}_X".format(obj)] = V[0]
    results["{}_Y".format(obj)] = V[1]


def get_pos(results, obj):
    """Return position."""
    try:
        X = results["{}_X".format(obj)]
        Y = results["{}_Y".format(obj)]

        if abs(X) > 1000:
            X /= 1000
        if abs(Y)>1000:
            Y /= 1000
    except KeyError:
        X = 0.0
        Y = 0.0

    P = np.array([X, Y], dtype="float64")
    return P


def check_locators(results):
    """Accumulate metrology values."""
    points = ["LOCATOR1", "LOCATOR2", "LOCATOR3", "FIDUCIAL1", "FIDUCIAL2"]
    coord = {}
    for P in points:
        coord[P] = get_pos(results, P)

    changed = False
    fd1 = np.array(coord["FIDUCIAL1"], dtype="float64")
    if fd1[0]!=0.0 or fd1[1]!=0:
        changed = True
        for V in coord.values():
            V -= fd1

        for O, P in coord.items():
            set_pos(coord[O], results, O)

    return changed

ROOT_DIR = Path("/Users/lacasta/Nextcloud/ITk/5-Petal_cores")



def analyze_avs_metrology(session, SN, altid):
    """Regenerate test json from FAT file."""
    P = ROOT_DIR / altid
    files = list(P.glob("AVS.P052.FRT.*.xlsx"))
    if len(files)==0:
        print("Cannot find FAT file for {}".format(altid))
        return None
    elif len(files)>1:
        print("More than one FAT file for {}".format(altid))
        for i, f in enumerate(files):
            print("{} - {}".format(i, Path/f).name)

        ifile = int(input("Choose file (-1 to discard): "))
        if ifile < 0:
            return None

        the_file = files[ifile]

    else:
        the_file = files[0]


    tests = readFATfile(session, the_file, SN)
    the_test = tests[3]
    check_locators(the_test["results"])
    the_test["isRetroactive"] = True
    the_test["stage"] = "ASSEMBLY"
    
    return the_test

def main(session):
    """Entry point"""
    # find all cores
    # Now all the objects
    payload = {
        "filterMap": {
            "componentType": ["CORE_PETAL"],
            "type": ["CORE_AVS"],
            #"currentLocation": ["IFIC"],
        },
        "sorterList": [
            {"key": "alternativeIdentifier", "descending": False }
        ],
    }

    core_list = session.get("listComponents", json=payload)
    core_tests = ["METROLOGY_AVS"]

    petal_ids = []
    for core in core_list:
        SN = core["serialNumber"]
        altid = core['alternativeIdentifier']
        if "PPC" not in altid:
            continue

        petal_ids.append(altid)

        location = core["currentLocation"]['code']
        coreStage = core["currentStage"]['code']

        print("\nPetal {} [{}] - {}. {}".format(SN, altid, coreStage, location))
        test_list = session.get("listTestRunsByComponent", json={"filterMap":{"serialNumber": SN, "state": "ready", "testType":core_tests}})

        good_tests = {}
        for tst in test_list:
            ttype = tst["testType"]["code"]
            if ttype not in core_tests:
                print(ttype)
                continue

            T = session.get("getTestRun", json={"testRun": tst["id"]})
            if T["state"] != "ready":
                continue

            if ttype in good_tests:
                if good_tests[ttype]["runNumber"] < T["runNumber"]:
                    good_tests[ttype] = T
            else:
                good_tests[ttype] = T

        for ttype, T in good_tests.items():
            if ttype != "METROLOGY_AVS":
                continue

            found = False
            for value in T["results"]:
                if  value["code"] == "LOCATOR1_X":
                    found = True
                    break

            if not found:
                print("LOCATOR1 is not here")
                the_test = analyze_avs_metrology(session, SN, altid)
                if the_test is None:
                    continue
                
                rc = ITkDButils.upload_test(session, the_test, check_runNumber=True)
                if rc:
                    print(rc)


if __name__ == "__main__":
    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()

    try:
        main(client)
        # the_test = analyze_avs_metrology(client, "20USEBC1000124", "PPC.015")
        #rc = ITkDButils.upload_test(client, the_test, check_runNumber=True)
        #if rc:
        #    print(rc)

    except Exception as E:
        print(E)

    dlg.die()