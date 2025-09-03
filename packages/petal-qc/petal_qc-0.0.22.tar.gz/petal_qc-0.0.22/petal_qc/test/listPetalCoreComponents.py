#!/usr/bin/env python3
"""List petal core components."""

from itkdb_gtk import ITkDBlogin
from itkdb_gtk import ITkDButils

def get_type(child):
    """Return object type.

    Args:
        child: object

    Returns
        str: object type
    """
    if child["type"] is not None:
        comp_type = child["type"]["code"]

    else:
        comp_type = child["componentType"]["code"]

    return comp_type


def listPetalCoreComponents(session):
    """List petal core components.

    Args:
        session: The itkdb session
    """
    final_stage = {
            "BT_PETAL_FRONT": "COMPLETED",
            "BT_PETAL_BACK": "COMPLETED",
            "COOLING_LOOP_PETAL": "CLINCORE",
            "THERMALFOAMSET_PETAL": "IN_CORE"
        }
    # find all cores
    # Now all the objects
    payload = {
        "filterMap": {
            "componentType": ["CORE_PETAL"],
            "type": ["CORE_AVS"],
            "currentLocation": ["IFIC"],
        },
        "sorterList": [
            {"key": "alternativeIdentifier", "descending": False }
        ],
    }
    core_list = session.get("listComponents", json=payload)

    for core in core_list:
        SN = core["serialNumber"]
        altid = core['alternativeIdentifier']
        if "PPC" not in altid:
            continue


        location = core["currentLocation"]['code']
        coreStage = core["currentStage"]['code']
        print("\n\nPetal {} [{}] - {}. {}".format(SN, altid, coreStage, location))

        for child in core["children"]:
            obj = ITkDButils.get_DB_component(session, child["component"])
            child_type = get_type(obj)
            child_stage = obj["currentStage"]["code"]
            child_sn = obj["serialNumber"]
            print("+-- {}: {} [{}]".format(child_sn, child_type, child_stage))
            if child_stage != final_stage[child_type]:
                print("Updating child stage.")
                rc = ITkDButils.set_object_stage(session, child_sn, final_stage[child_type])
                if rc is None:
                    print("Could not set final stage of {} [{}]".format(child_type, child_sn))


if __name__ == "__main__":
    # ITk PDB authentication
    dlg = None
    try:
        # We use here the Gtk GUI
        dlg = ITkDBlogin.ITkDBlogin()
        client = dlg.get_client()

    except Exception:
        # Login with "standard" if the above fails.
        client = ITkDButils.create_client()

    listPetalCoreComponents(client)
    if dlg:
        dlg.die()