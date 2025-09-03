"""List shipments."""
import sys
from pathlib import Path
import numpy as np

from itkdb_gtk import ITkDBlogin, ITkDButils


def main(session):
    """List shipments from AVS to CERN and IFIC containing CORES."""
    
    payload = {
            "filterMap": {
                "sender": "AVS",
                "recipient": ["CERN", "IFIC"],
                "status": "delivered"
            }
        }
    shpmts = session.get("listShipmentsByInstitution", json=payload)
    for s in shpmts:
        items = session.get("listShipmentItems", json={"shipment": s["id"]})
        cores = []
        for it in items:
            if it["component"]["componentType"]['code'] == "CORE_PETAL":
                if "PPC." in it["component"]["alternativeIdentifier"]:
                    cores.append(it["component"]["alternativeIdentifier"])
                
        if len(cores) == 0:
            continue
        
        print("Shipment {}".format(s["name"]))
        print("AVS -> {}".format(s["recipient"]["code"]))
        print(":> {}".format(s["sentTs"]))
        for c in cores:
            print("\t{}".format(c))

        print("\n")

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

    
    