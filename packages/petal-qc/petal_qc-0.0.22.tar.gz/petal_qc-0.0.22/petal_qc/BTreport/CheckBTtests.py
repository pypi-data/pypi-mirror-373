#!/usr/bin/env python3
"""Check that bus tapes in petal have been tested.

Upload teh Bus Tape Summary TEst to the PDB.

To run it

python3 CheckBTtests.py petal_SN

The main routine is BTreport and can be called from anywhere else.

"""

import sys
import traceback
import json
import datetime
import dateutil.parser
import argparse

from petal_qc.utils.ArgParserUtils import RangeListAction

import itkdb
from itkdb_gtk import ITkDBlogin
from itkdb_gtk import ITkDButils

def complain(main_msg, secondary_msg=None):
    """Prints an error message

    Args:
    -----
        main (): Main message
        secondary (): Seconday message
    """
    print("**Error\n{}".format(main_msg))
    if secondary_msg:
        msg = secondary_msg.replace("\n", "\n\t")
        print("\t{}".format(msg))


def get_type(child):
    """Return object type

    Args:
    -----
        child: object

    Returns
    -------
        str: object type

    """
    if child["type"] is not None:
        comp_type = child["type"]["code"]

    else:
        comp_type = child["componentType"]["code"]

    return comp_type


def find_bus_tapes(session, petal, complain_func=complain):
    """Find Bus tapes in petal.

    Args:
    ----
        session (itkdb.Client): The DB session
        petal (Json): The petal object

    Returns
    -------
        dict: a dict with the bustapes. Key is the BT type.
    """
    bt_list = {}
    bt_valid = {}
    for child in petal["children"]:
        cstage = "Missing"
        if child["component"] is None:
            continue

        else:
            child_sn = child["component"]["serialNumber"]
            comp_type = get_type(child)
            if "BT_PETAL" not in comp_type:
                continue

            # We are left with the bus tapes
            cobj = session.get('getComponent', json={'component': child["component"]["id"]})
            bt_list[comp_type] = cobj, child['id']
            cstage = cobj["currentStage"]['code']
            if cstage != "COMPLETED":
                complain_func("Bus tape not in final stages", cstage)
                bt_valid[comp_type] = False

            else:
                bt_valid[comp_type] = True


    return bt_list, bt_valid


def find_but_tape_tests(session, petal_date, bt_sn, complain_func=complain):
    """Find tests in bus tape.

    Args:
        session (itkdb.Client): The DB session
        petal_date (DateTime): The petal date
        bt_sn (str): The bus tape SN

    Returns:
        dict: dict with all tests. key is the test type code.

    """
    test_list = session.get("listTestRunsByComponent",
                            json={"filterMap":{"serialNumber": bt_sn,
                                               "stage": "COMPLETED"}
                                  })
    bt_tests = {}
    for tst in test_list:
        test_type = tst["testType"]["name"]
        test_code = tst["testType"]["code"]

        # Create the storage for the tests. Used to sort by date in case of multiple tests
        if test_code not in bt_tests:
            bt_tests[test_code] = []

        test_date = tst["date"]
        bt_tests[test_code].append(tst)

    for key, val in bt_tests.items():
        val.sort(key=lambda a: dateutil.parser.parse(a["date"]), reverse=True)
        the_test = val[0]
        if petal_date > dateutil.parser.parse(val[0]["date"]):
            complain_func("Test on tape happened before petal", "")
            bt_tests[key] = None
        else:
            bt_tests[key] = val[0]

    return bt_tests


def date2string(the_date=None):
    """REturns date string in TTkDB format."""
    if the_date is None:
        the_date = datetime.datetime.now()
    out = the_date.isoformat(timespec='milliseconds')
    if out[-1] not in ['zZ']:
        out += 'Z'

    return out


def BTreport(session, SerialN, petal=None, complain_func=complain):
    """Makes the BTreport for a petal core.

    Args:
        session (itkdb.Client): The DB session
        SerialN (str): The Petal core SB
    """
    # get petal frm DB.
    if petal is None:
        petal = ITkDButils.get_DB_component(session, SerialN)
        if petal is None:
            complain_func(SerialN, "Could not find petal core.")
            return None

    SerialN = petal["serialNumber"]

    print("\n+++ Petal core {} [{}]".format(SerialN, petal["alternativeIdentifier"]))
    petal_date = dateutil.parser.parse(petal["stateTs"])
    comp_type = get_type(petal)
    if comp_type != "CORE_AVS":
        complain_func("This is not a petal cores", comp_type)
        return None

    # Check that the petal core is in the proper stage.
    stage = petal["currentStage"]['code']
    if stage != "AT_QC_SITE":
        complain_func("Petal core is not at QC_SITE", stage)
        return None

    # Check children
    if "children" not in petal:
        complain_func("{}[{}]".format(SerialN, id), "Not assembled")
        return None

    # Loop on children an find bustapes
    bt_list, bt_valid = find_bus_tapes(session, petal, complain_func=complain_func)

    nvalid = 0
    for valid in bt_valid.values():
        if valid:
            nvalid += 1

    if nvalid != 2:
        complain_func("no valid bustape found", "Either not assembled or in incorrect stage.")
        return None

    out = {
        "component": SerialN,
        "testType": "BTTESTING",
        "institution": petal["currentLocation"]["code"],
        "runNumber": "1",
        "date": date2string(),
        "passed": True,
        "problems": False,
        "results": {
            "PASS": [],
            "RUNS_ELECTRICALTEST": []
            # "RUNS_STRETCHTEST": []
        }
    }

    # Check the tests in the bustapes
    ngood = 0
    ntrouble = 0
    nprocess = 0
    for bt, cp_id in bt_list.values():
        bt_sn = bt["serialNumber"]
        print("bus tape {}".format(bt_sn))

        bt_ngood = 0
        bt_nprob = 0
        # get list of tests and select the latest.
        bt_tests = find_but_tape_tests(session, petal_date, bt_sn, complain_func=complain_func)
        if len(bt_tests) == 0:
            print("-> No bus tape tests available")
            continue
        
        nprocess += 1
        results = {}
        childId = {}
        for key, the_test in bt_tests.items():
            print("\t->The Test {} [{}] {}".format(the_test["testType"]["name"],
                                                   the_test["date"][0:16],
                                                   "PASSED" if the_test["passed"] else "FAILED"))

            results[the_test["testType"]["code"]] = the_test["passed"]
            childId[the_test["testType"]["code"]] = the_test['id']
            if the_test["passed"]:
                ngood += 1
                bt_ngood += 1

            if the_test["problems"]:
                ntrouble += 1
                bt_nprob += 1

        out["results"]["PASS"].append(
            {"value": (bt_ngood == 2),
             "childParentRelation": cp_id})

        out["results"]["RUNS_ELECTRICALTEST"].append(
            {"value": childId["BTELECTRICAL"],
             "childParentRelation": cp_id})

        # out["results"]["RUNS_STRETCHTEST"].append(
        #     {"value": childId["BTSTRETCHP"],
        #      "childParentRelation": cp_id})

    if nprocess == 0:
        return None

    out["passed"] = (ngood == 4)
    out["problems"] = (ntrouble > 0)
    print("BusTape Report\n\tN. good {}\n\tN. prob {}".format(ngood, ntrouble))

    return out


def check_petal_core(session, SerialN):
    """Check petal core for bt report."""
    core = ITkDButils.get_DB_component(session, SerialN)
    if core is None:
        return None
    
    test_list = session.get(
            "listTestRunsByComponent",
            json={
                "filterMap": {
                    "serialNumber": core["serialNumber"],
                    "state": "ready",
                    "testType": ["BTTESTING",],
                }
            },
        )

    ntest = 0
    for tst in test_list:
        ntest += 1
        
    if ntest>0:
        return None
    
    return core

def main():
    """Main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("args", nargs='*', help="Input cores")
    parser.add_argument("--cores", dest="cores", action=RangeListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")


    args = parser.parse_args()
    if len(args.cores)==0:
        try:
            args.cores.extend(args.args)

        except IndexError:
            print("I need a petal  core SN or AlternativeID")
            sys.exit()
            
    else:
        cores = [ "PPC.{:03d}".format(int(x)) for x in args.cores]
        args.cores = cores

    # ITk PDB authentication
    dlg = None
    try:
        # We use here the Gtk GUI
        dlg = ITkDBlogin.ITkDBlogin()
        client = dlg.get_client()

    except Exception:
        # Login with "standard" if the above fails.
        client = ITkDButils.create_client()

    # Check the Bustape tests
    for SN in args.cores:
        core = check_petal_core(client, SN)
        if core is None:
            continue
        
        try:
            out = BTreport(client, SN, petal=core)
            # Upload test
            if out:
                try:
                    db_response = client.post("uploadTestRunResults", json=out)
                except Exception as ex:
                    print("Could not upload test for {}.".format(SN))
                    print(ex)

        except KeyError as ex:
            print("Key error: {}".format(ex))

        except Exception:
            print(traceback.format_exc())

    try:
        dlg.die()

    except Exception:
        print("Bye !")

if __name__ == "__main__":
    main()
