#!/usr/bin/env python3
"""Analize AVS metrology tests."""
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from argparse import ArgumentParser

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin
import petal_qc.utils.docx_utils as docx_utils
from petal_qc.utils.ArgParserUtils import RangeListAction


def get_value(results, code):
    """Return the value of the test parameter."""
    for param in results:
        if param["code"] == code:
            return param["value"]

    raise KeyError

def distance(P1, P2):
    """Distance between 2 points."""
    P = (P2-P1)
    S = np.sum(np.square(P))
    D = np.sqrt(S)
    return D

nominal_values = {
    "LOCATOR1": np.array([0, -3]),
    "LOCATOR2": np.array([127.916, 589.618]),
    "LOCATOR3": np.array([127.916, 589.618]),
    "FIDUCIAL1": np.array([0, 0]),
    "FIDUCIAL2": np.array([131.104, 586.526]),
}

def get_pos(results, obj):
    """Return position."""
    try:
        X = get_value(results, "{}_X".format(obj))
        Y = get_value(results, "{}_Y".format(obj))

        if abs(X) > 1000:
            X /= 1000
        if abs(Y)>1000:
            Y /= 1000
    except KeyError:
        X = 0.0
        Y = 0.0

    P = np.array([X, Y], dtype="float64")
    return P

def distance_to_nominal(results, obj):
    """Return position of given locator or fiducial."""
    P = get_pos(results, obj)
    N = nominal_values[obj]
    D = distance(P, N)
    if abs(D-3)<0.5:
        P[1] -= 3
        D = distance(P, N)
    return D

def do_metrology(results, M_values, Mould_values):
    """Accumulate metrology values."""
    points = ["LOCATOR1", "LOCATOR2", "LOCATOR3", "FIDUCIAL1", "FIDUCIAL2"]
    coord = {}
    for P in points:
        coord[P] = get_pos(results, P)

    fd1 = np.array(coord["FIDUCIAL1"], dtype="float64")
    if fd1[0]!=0.0 or fd1[1]!=0:
        for V in coord.values():
            V -= fd1

    for O, P in coord.items():
        D = distance(P, nominal_values[O])
        if D<1.0:
            M_values.setdefault(O, []).append(D)
            Mould_values.setdefault(O, []).append(D)

        else:
            print("Possibly wrong data in FAT: {} D={:.3f}".format(O, D))

def do_manufacturing(T):
    """Return mould."""
    mould_id = None
    for prop in T["properties"]:
        if prop["code"] == "MOULD_ID":
            mould_id = prop["value"]
            break

    return mould_id

def do_weighing(results, weights):
    """Accumulates weighing values to produce stack plot.

    Args:
        results (): Results from DB
        weights (): Dict with the values.
    """
    for value in results:
        ipos = value["code"].find("_")
        weights.setdefault(value["code"][ipos+1:], []).append(value["value"])


def plot_metrology(M_values, Mould_values, petal_ids, document):
    """Plot metrology values."""
    fsize = np.zeros(2)

    document.add_heading('Deviation from nominal positions', level=1)
    for key, values in M_values.items():
        fig, ax = plt.subplots(ncols=1, nrows=1, tight_layout=True)
        ax.hist(values, bins=15, range=(0, 0.150))
        ax.set_title(key)
        ax.grid(True)
        ax.set_xlabel("Distance (mm)")
        fsize = fig.get_size_inches()
        if key != "FIDUCIAL1":
            document.add_picture(fig, True, 14, caption=key)

    fsize[1] = fsize[0]/0.82
    document.add_heading('Dependency with moulds', level=1)
    for obj in M_values.keys():
        fig, ax = plt.subplots(ncols=1, nrows=4, tight_layout=True, figsize=fsize)
        fig.suptitle("{} - Mould".format(obj))
        for mould, m_values in Mould_values.items():
            im = int(mould) - 1
            ax[im].hist(m_values[obj], bins=15, range=(0, 0.150), label="Mould {}".format(mould))

        for i in range(4):
            ax[i].grid(True)
            ax[i].set_xlabel("Distance (mm)")
            ax[i].set_title("Mould {}".format(i+1))

        if obj != "FIDUCIAL1":
            document.add_picture(fig, True, 14, caption=obj)


def plot_weighing(weights, tick_labels, document, show_total=False):
    """Make the plot of weights."""
    labels = ["COOLINGLOOPASSEMBLY", "LOCATOR_A", "LOCATOR_B", "LOCATOR_C",
              "HONEYCOMBSET", "FACING_FRONT", "FACING_BACK",
              "EPOXYADHESIVE", "EPOXYPUTTY", "EPOXYCONDUCTIVE"]

    fig = plt.figure(tight_layout=True)
    fig.suptitle("Petal Core weight (gr)")
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ylabel("Weight [gr]")
    ax.set_ylim(0, 300)
    npoints = len(weights["CORE"])
    X = np.arange(npoints)

    values = [ weights[k] for k in labels]
    Y = np.vstack(values)
    ax.stackplot(X, Y, labels=labels)
    ax.set_xticks(range(npoints), labels=tick_labels, rotation="vertical")

    if not show_total:
        ax.plot(X, [225.0 for x in range(npoints)], linestyle="dashed", color="black", linewidth=1)
        ax.plot(X, [250.0 for x in range(npoints)], '-', color="black", linewidth=1, label="Nominal")
        ax.plot(X, [275.0 for x in range(npoints)], linestyle="dashed", color="black", linewidth=1,)


    ax.legend(loc="upper left", ncol=4)


def main(session, options):
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
    core_tests = ["METROLOGY_AVS", "WEIGHING", "MANUFACTURING", "DELAMINATION", "GROUNDING_CHECK", "VISUAL_INSPECTION"]

    weights = {}
    petal_ids = []
    M_values = {}
    Mould_values = {}
    mould_id = None
    i = 0
    bad_cores = {}
    counter = {"TOTAL":0}
    for T in core_tests:
        counter[T]=0

    mould_db = {}
    for core in core_list:
        SN = core["serialNumber"]
        altid = core['alternativeIdentifier']
        if "PPC" not in altid:
            continue
        
        pID = int(altid[4:])
        if len(options.cores)>0 and pID not in options.cores:
            continue

        petal_ids.append(altid)
        location = core["currentLocation"]['code']
        coreStage = core["currentStage"]['code']

        print("\nPetal {} [{}] - {}. {}".format(SN, altid, coreStage, location))
        test_list = session.get(
            "listTestRunsByComponent",
            json={
                "filterMap": {
                    "serialNumber": SN,
                    "state": "ready",
                    "testType": core_tests,
                }
            },
        )

        good_tests = {}
        for tst in test_list:
            ttype = tst["testType"]["code"]
            if ttype not in core_tests:
                print(ttype)
                continue

            T = session.get("getTestRun", json={"testRun": tst["id"]})
            if T["state"] != "ready":
                continue

            print("-- {} [{}]".format(T["testType"]["name"], T["runNumber"]))
            if ttype in good_tests:
                if good_tests[ttype]["runNumber"] < T["runNumber"]:
                    good_tests[ttype] = T
            else:
                good_tests[ttype] = T

        mould_desc = do_manufacturing(good_tests["MANUFACTURING"])
        pos = mould_desc.rfind('.')
        mould_id = mould_desc[pos+1:]
        mould_db[altid] = (SN, mould_id)
        if mould_id not in Mould_values:
            Mould_values[mould_id] = {}

        counter["TOTAL"] += 1
        for ttype, T in good_tests.items():

            if ttype == "WEIGHING":
                do_weighing(T["results"], weights)

            elif ttype == "METROLOGY_AVS":
                do_metrology(T["results"], M_values, Mould_values[mould_id])

            elif ttype == "MANUFACTURING":
                continue

            # else:
            #     if T["results"]:
            #         for value in T["results"]:
            #             print("\t{} - {}".format(value["code"], value["value"]))

            if not T["passed"]:
                print("## test {} FAILED".format(T["testType"]["code"]))
                bad_cores.setdefault(altid, []).append({ttype: T["defects"]})

            else:
                try:
                    counter[ttype] += 1
                except KeyError:
                    pass

            if len(T["defects"]):
                print("+ Defects:")
                for D in T["defects"]:
                    print("\t{} - {}".format(D["name"], D["description"]))

    document = docx_utils.Document()
    document.add_page_numbers()
    document.styles['Normal'].font.name = "Calibri"
    document.add_heading("AVS QC tests.", 0)

    document.add_heading('Results', level=1)
    document.add_paragraph("Number of bad cores: {}.".format(len(bad_cores)))
    document.add_heading("Bad cores", level=2)
    for key, lst in bad_cores.items():
        p = document.add_paragraph()
        bf = p.add_run("{}:".format(key))
        bf.bold = True
        bf.italic = True
        for item in lst:
            for ttype, defects in item.items():
                msg = "{}:".format(ttype)
                for  D in defects:
                    msg += "\r{} - {}".format(D["name"], D["description"])
                document.add_paragraph(msg, style="List Bullet")


    plot_weighing(weights, petal_ids, document)
    plot_metrology(M_values, Mould_values, petal_ids, document)
    document.save("AVStests.docx")

    with open("mould_db.csv", "w", encoding="utf-8") as fout:
        fout.write("PetalID, SerialNo, MouldID\n")
        for key, val in mould_db.items():
            fout.write("{}, {}, {}\n".format(key, val[0], val[1]))

    plt.show()

if __name__ == "__main__":
    # ITk_PB authentication
    parser = ArgumentParser()
    parser.add_argument("--cores", dest="cores", action=RangeListAction, default=[],
                        help="Create list of cores to analyze. The list is made with  numbers or ranges (ch1:ch2 or ch1:ch2:step) ")

    opts = parser.parse_args()
    dlg = ITkDBlogin.ITkDBlogin()
    session = dlg.get_client()

    main(session, opts)

    dlg.die()
