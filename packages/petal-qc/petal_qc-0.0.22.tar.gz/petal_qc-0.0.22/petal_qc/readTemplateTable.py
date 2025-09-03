#!/usr/bin/env python3
"""Read Python table with reception tests."""

import sys
import math
import argparse
import pandas as pd
import json
from pathlib import Path

from itkdb_gtk import ITkDBlogin, ITkDButils

def check_value(value):
    """Check that value is valid."""
    if value is None:
        return False

    if isinstance(value, float):
        if math.isnan(value):
            return False

    return True


def string_to_boolean(s):
    """Converts a string to a boolean."""
    val = s.lower()
    if val=="pass" or val=="true" or val=="1":
        return True
    elif val=="fail" or val=="false" or val=="0":
        return False
    else:
        raise ValueError

def parse_value(value):
    """Parse value in cell."""
    try:
        spassed, comment = value.split(",")
    except ValueError:
        spassed = value
        comment = ""

    passed = string_to_boolean(spassed)
    if passed is None:
        return None, None

    return passed, comment

def create_dto(session, SN, test_name):
    """REturns the test DTO."""
    user =  ITkDButils.get_db_user(session)
    defaults = {
            "component": SN,
            "institution": user["institutions"][0]["code"],
            "runNumber": "1",
        }
    dto = ITkDButils.get_test_skeleton(session, "CORE_PETAL", test_name, defaults)
    return dto

def do_visual_inspection(session, core, value):
    """Uploads visual inspection."""
    if not check_value(value):
       return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "VISUAL_INSPECTION")

    passed, comment = parse_value(value)

    if passed is None:
        print("Wrong value fpr PASS/FAIL {} in {} for {}".format(value, "VISUAL_INSPECTION", core["alternativeIdentifier"]) )
        return None

    if passed:
        dto["passed"] = True
    else:
        dto["passed"] = False
        dto["defects"].append({
            "name": "VISUAL",
            "description": comment,
            "properties": {}
        })

    return dto

def do_grounding(session, core, value):
    """Uploads grounding check"""
    if not check_value(value):
        return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "GROUNDING_CHECK")

    fb, pipes, pipe_gnd = [float(x) for x in value.split(',')]
    if fb > 2.0:
        dto["passed"] = False
        dto["defects"].append({
            "name": "GROUND_FB",
            "description": "resistance front-back is {} > 2 Ohm".format(fb),
            "properties": {}
        })

    if pipes>0 and pipes<20.0e6:
        dto["passed"] = False
        dto["defects"].append({
            "name": "GROUND_PIPES",
            "description": "resistance between pipes is {} < 20 MOhm".format(pipes),
            "properties": {}
        })

    if pipe_gnd>0 and pipe_gnd<20.0e6:
        dto["passed"] = False
        dto["defects"].append({
            "name": "GROUND_PIPE_GND",
            "description": "resistance between pipes and GNDis {} < 20 MOhm".format(pipe_gnd),
            "properties": {}
        })

    dto["results"]["RESISTANCE_FB"] = fb
    dto["results"]["RESISTANCE_PIPES"] = pipes
    dto["results"]["RESISTANCE_PIPE_GND"] = pipe_gnd

    return dto

def do_bending(session, core, value):
    """Uploads bending."""
    if not check_value(value):
        return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "BENDING120")
    passed, comment = parse_value(value)
    if passed is None:
        print("Wrong value fpr PASS/FAIL {} in {} for {}".format(value, "BENDING120", core["alternativeIdentifier"]) )
        return None

    if passed:
        dto["passed"] = True
    else:
        dto["passed"] = False
        dto["defects"].append({
            "name": "BENDING120",
            "description": comment,
            "properties": {}
        })

    return dto

def do_weight(session, core, value):
    """Uploads weight."""
    if not check_value(value):
        return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "PETAL_CORE_WEIGHT")

    weight = float(value)
    dto["results"]["WEIGHT"] = weight
    if abs(weight-250)>25:
        dto["passed"] = False
        dto["defects"].append({
            "name": "WEIGHT",
            "description": "Petal core wights {:.1f} more than 25 gr. beyond 250.".format(weight),
            "properties": {}
        })
    else:
        dto["passed"] = True

    return dto


def do_thickness(session, core, value):
    """Uploads thickness."""
    if not check_value(value):
        return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "CORE_THICKNESS")
    thickness = float(value)
    dto["results"]["THICKNESS"] = thickness

    dto["passed"] = True
    if abs(thickness-5.9)>0.25:
        dto["problems"] = True
        dto["comments"].append("Petal core wights {:.1f} more than 25 gr. beyond 250.".format(thickness))

    return dto


def do_metrology_template(session, core, value):
    """Uploads metrology template."""
    if not check_value(value):
        return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "METROLOGY_TEMPLATE")
    passed, comment = parse_value(value)
    if passed is None:
        print("Wrong value fpr PASS/FAIL {} in {} for {}".format(value, "TEMPLATE", core["alternativeIdentifier"]) )
        return None

    if passed:
        dto["passed"] = True
    else:
        dto["passed"] = False
        dto["defects"].append({
            "name": "TEMPLATE",
            "description": comment,
            "properties": {}
        })

    return dto


def do_delamination(session, core, value):
    """Uploads delamination."""
    if not check_value(value):
        return None

    SN = core["serialNumber"]
    dto = create_dto(session, SN, "DELAMINATION")

    passed, comment = parse_value(value)
    if passed is None:
        print("Wrong value fpr PASS/FAIL {} in {} for {}".format(value, "DELAMINATION", core["alternativeIdentifier"]) )
        return None

    if passed:
        dto["passed"] = True
    else:
        dto["passed"] = False
        dto["defects"].append({
            "name": "DELAMINATION",
            "description": comment,
            "properties": {}
        })

    return dto


def readTemplateTable(session, options):
    """Main entry.

    Args:
        session (itkdb.Session): The PDB client.
        options: program options
    """

    core_tests = {
        "VISUAL_INSPECTION": do_visual_inspection,
        "GROUNDING_CHECK": do_grounding,
        "BENDING120": do_bending,
        "PETAL_CORE_WEIGHT": do_weight,
        "CORE_THICKNESS": do_thickness,
        "METROLOGY_TEMPLATE": do_metrology_template,
        "DELAMINATION": do_delamination
    }
    try:
        sheet = int(options.sheet)
    except ValueError:
        sheet = options.sheet
        
    df = pd.read_excel(options.files[0], sheet_name=sheet)
    #print(df)

    for row in df.itertuples():
        petal_id = row.CORE_ID
        if not check_value(petal_id):
            break

        print("\n\n### {}".format(petal_id))
        core = ITkDButils.get_DB_component(session, petal_id)
        for test, func in core_tests.items():
            data = func(session, core, getattr(row, test))
            if data is None:
                continue

            data["properties"]["OPERATOR"] = options.operator
            
            #print(json.dumps(data, indent=3))
            rc = ITkDButils.upload_test(session, data, check_runNumber=True)
            if rc:
                print("\n*** Could not upload test {} for {}".format(test, petal_id))
                print(rc)
                print()

def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='*', help="The template spreadsheet")
    parser.add_argument("--sheet", default="0", help="Sheet to read from excel file.")
    parser.add_argument("--operator", default="Oihan Elesgaray", help="Name of operator.")

    args = parser.parse_args()
    if len(args.files) == 0:
        print("I need an input file")
        sys.exit()

    if not Path(args.files[0]).exists():
        print("Input file does not exist.")
        sys.exit()


    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    pdb_session = dlg.get_client()

    readTemplateTable(pdb_session, args)

    dlg.die()

if __name__ == "__main__":
    main()