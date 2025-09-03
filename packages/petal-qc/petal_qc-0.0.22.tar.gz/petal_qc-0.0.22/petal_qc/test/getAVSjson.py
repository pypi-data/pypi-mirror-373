import json
from itkdb_gtk import ITkDBlogin
from petal_qc.metrology import readAVSdata
dlg = ITkDBlogin.ITkDBlogin()
session  = dlg.get_client()

ofile = "weights_ppc16.json"
PSF = "/Users/lacasta/Nextcloud/ITk/5-Petal_cores/PPC.016/AVS.P052.PSH.035 - Petal 016.xlsx"

ofile = "weights_ppc17.json"
ofat = "metrology_test_ppc17.json"
PSF = "/Users/lacasta/Nextcloud/ITk/5-Petal_cores/PPC.017/AVS.P052.PSH.036 - Petal 017.xlsx"
FAT = "/Users/lacasta/Nextcloud/ITk/5-Petal_cores/PPC.017/AVS.P052.FRT.036 r0 - FAT_Serie_017.xlsx"
manuf_json, weights_json, DESY_comp, alias = readAVSdata.readProductionSheet(session, PSF, "SNnnnn")

vi_test, delamination_test, grounding_test, metrology_test, batch, petal_weight = readAVSdata.readFATfile(session, FAT, "SNnnn")

with open(ofile, "w", encoding="UTF-8") as fin:
    json.dump(weights_json, fin, indent=3)
    

with open(ofat, "w", encoding="UTF-8") as fin:
    json.dump(metrology_test, fin, indent=3)
    

print("done")
dlg.die()