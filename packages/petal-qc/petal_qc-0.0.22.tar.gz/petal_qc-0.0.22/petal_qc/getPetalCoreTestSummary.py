#!/usr/bin/env python3
"""Get a summery of Petal core TEsts."""
import json
import sys
import re
import copy
from argparse import ArgumentParser


from pathlib import Path
try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin, ITkDButils
from itkdb_gtk.dbGtkUtils import replace_in_container, DictDialog, ask_for_confirmation
from petal_qc.utils.ArgParserUtils import RangeListAction

r_petal_id = re.compile("PPC.([0-9]*)")

def petalCoreTest(session, options):
    """Main entry point."""

    # find all cores
    # Now all the objects
    payload = {
        "filterMap": {
            #"componentType": ["BT"],
            "componentType": ["CORE_PETAL"],
            "type": ["CORE_AVS"],
            # "currentLocation": ["IFIC"],
        },
        "sorterList": [
            {"key": "alternativeIdentifier", "descending": False }
        ],
    }
    suff = "ALL"
    if options.institute:
        payload["filterMap"]["currentLocation"] = options.institute
        suff = options.institute

    core_list = session.get("listComponents", json=payload)

    # We want details about these tests
    core_tests = [
        "PETAL_METROLOGY_FRONT",
        "PETAL_METROLOGY_BACK",
        "XRAYIMAGING",
        "THERMAL_EVALUATION",
        "BTTESTING",
        "METROLOGY_TEMPLATE",
        "PETAL_CORE_WEIGHT"
    ]

    # this is the full list
    at_qc_tests = [
        "VISUAL_INSPECTION",
        "BTTESTING",
        "GROUNDING_CHECK",
        "BENDING120",
        "THERMAL_EVALUATION",
        "XRAYIMAGING",
        "METROLOGY_TEMPLATE",
        "PETAL_METROLOGY_FRONT",
        "PETAL_METROLOGY_BACK",
        "PETAL_CORE_WEIGHT",
        "CORE_THICKNESS",
        "DELAMINATION",
    ]

    do_check_stage = "AT_QC_SITE"
    do_check_stage = None
    petal_id_db = {}

    has_list = len(options.cores) != 0

    for core in core_list:
        SN = core["serialNumber"]
        altid = core['alternativeIdentifier']
        if "PPC" not in altid:
            continue

        R = r_petal_id.search(altid)
        if R is None:
            continue

        pid = int(R.group(1))

        if has_list and pid not in options.cores:
            continue

        petal_id_db[altid] = SN
        location = core["currentLocation"]['code']
        coreStage = core["currentStage"]['code']
        if do_check_stage:
            if coreStage != do_check_stage:
                rc = ITkDButils.set_object_stage(session, SN, do_check_stage)
                if rc is None:
                    print("Could not change stage")
                    return False

        print("\n\nPetal {} [{}] - {}. {}".format(SN, altid, coreStage, location))
        test_status = {}
        test_list = session.get("listTestRunsByComponent", json={"filterMap":{"serialNumber": SN, "state": "ready", "stage": "AT_QC_SITE", "testType":at_qc_tests}})
        missing_tests = copy.deepcopy(at_qc_tests)
        for tst in test_list:
            ttype = tst["testType"]["code"]
            if ttype in missing_tests:
                missing_tests.remove(ttype)

            #if ttype not in core_tests:
            #    print(ttype)
            #    continue

            T = session.get("getTestRun", json={"testRun": tst["id"]})
            if T["state"] != "ready":
                print(T)


            if ttype in test_status:
                try:
                    if int(T["runNumber"]) > int(test_status[ttype]["runNumber"]):
                        test_status[ttype] = T
                
                except ValueError:
                    if T["date"] > test_status[ttype]["date"]:
                        test_status[ttype] = T
                        
            else:
                test_status[ttype] = T

            print("-- {} [{}]".format(T["testType"]["name"], T["runNumber"]))
            if not T["passed"]:
                print("\t## test FAILED")

            for D in T["defects"]:
                print("\t{} - {}".format(D["name"], D["description"]))

        if len(test_status):
            passed = True
            for ttype, T in test_status.items():
                if not T["passed"]:
                    passed = False
                    break

            if passed:
                print("\n--- PASSED")
            else:
                print("\n*** FAILED")

        if options.show_missing:
            print("missing tests:")
            for tst in missing_tests:
                print("-- {}".format(tst))

    with open("petal_ID_db_{}.json".format(suff), "w", encoding="utf-8") as fOut:
        json.dump(petal_id_db, fOut, indent=3)

def main():
    """Main entry"""
    parser = ArgumentParser()
    parser.add_argument("--show_missing", default=False, action="store_true", help="Show missing tests.")
    parser.add_argument("--institute", default=None, help="The petal current location")
    parser.add_argument("--cores", dest="cores", action=RangeListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")
    options = parser.parse_args()

    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    session = dlg.get_client()

    try:
        petalCoreTest(session, options)

    except Exception as E:
        print(E)

    dlg.die()

if __name__ == "__main__":
    main()
