#!/usr/bin/env python3
"""GUI for thermal QC of petal cores."""
import sys
import os
import copy
from pathlib import Path
from argparse import ArgumentParser
import json
import numpy as np

import itkdb_gtk
import itkdb_gtk.ITkDButils
import itkdb_gtk.dbGtkUtils
import itkdb_gtk.UploadTest

__HELP__ = "https://petal-qc.docs.cern.ch/thermal.html"

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())


from petal_qc.thermal.IRPetalParam import IRPetalParam
from petal_qc.thermal import IRBFile
from petal_qc.thermal.IRDataGetter import IRDataGetter
from petal_qc.thermal.DESYdata import DesyData

from petal_qc.thermal.analyze_IRCore import golden_from_json
from petal_qc.thermal.create_core_report import create_report
from petal_qc.utils.readGraphana import ReadGraphana

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class CoreThermal(itkdb_gtk.dbGtkUtils.ITkDBWindow):
    """Application window."""

    def __init__(self, params=None, session=None, title="",  panel_size=100):
        """Initialization

        Args:
            params (IRPetalParam, optional): Petal thermal parameters.
            session (itkdb.Client): ITk PDB session.
            title: Window title.
            panel_size: size of message pannel.
        """
        super().__init__(session=session, title=title, help_link=__HELP__ )
        self.petal_SN = None
        self.param = params if params else IRPetalParam()
        self.param.add_attachments = True
        self.param.create_golden = False
        self.irbfile = self.param.files if len(self.param.files)>0 else None
        self.folder = None
        self.golden = None
        self.results = None
        self.alternativeID = None
        self.outDB = None
        self.desy_opts = None
        self.ific_opts = None
        if self.param.institute is None:
            is_desy = False
            for site in self.pdb_user["institutions"]:
                if "DESY" in site["code"]:
                    is_desy = True
                    break

            self.param.institute = "DESY" if is_desy else "IFIC"

        if self.param.institute == "IFIC":
            self.ific_opts = copy.deepcopy(self.param)
        else:
            self.desy_opts = copy.deepcopy(self.param)

         # Active button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test_gui)
        self.hb.pack_end(button)

        # JScon edit
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="accessories-text-editor-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to see the test data")
        button.connect("clicked", self.show_test_gui)
        self.hb.pack_end(button)

        # The file chooser
        self.dataBox = Gtk.Box()
        self.btnData = Gtk.FileChooserButton()
        self.btnData.connect("file-set", self.on_file_set)

        self.desyData = Gtk.Button(label="Chose Files")
        self.desyData.connect("clicked", self.on_desy_data)

        if self.param.institute == "IFIC":
            self.dataBox.pack_start(self.btnData, False, False, 0)
        else:
            self.dataBox.pack_start(self.desyData, False, False, 0)


        # The file chooser
        self.goldenData = Gtk.FileChooserButton()
        self.goldenData.connect("file-set", self.on_golden_set)
        if self.param.golden and len(self.param.golden)>0:
            self.goldenData.set_file(Gio.File.new_for_path(self.param.golden))
            self.on_golden_set(self.goldenData)


        # The Serial number
        self.SN = itkdb_gtk.dbGtkUtils.TextEntry()
        if self.param.SN is not None and len(self.param.SN)>0:
            self.SN.set_text(self.param.SN)
        elif self.param.alias and len(self.param.alias)>0:
            self.SN.set_text(self.param.alias)
            self.on_SN_changed(self.SN.entry, self.param.alias)

        self.SN.connect("text-changed", self.on_SN_changed)

        self.btn_state = Gtk.Button(label="Undef")
        self.btn_state.set_name("btnState")
        self.btn_state.connect("clicked", self.show_state)
        self.btn_state.set_tooltip_text("If green all good. Click to see commnets and defects.")

        # Put the 3 objects in a Grid
        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 0)

        irow = 0
        grid.attach(Gtk.Label(label="Serial No."), 0, irow, 1, 1)
        grid.attach(self.SN.entry, 1, irow, 1, 1)
        grid.attach(self.btn_state, 3, irow, 1, 1)

        irow += 1
        grid.attach(Gtk.Label(label="IRB File"), 0, irow, 1, 1)
        grid.attach(self.dataBox, 1, irow, 1, 1)

        self.entryTemp = Gtk.Entry()
        self.entryTemp.set_text("{:.1f}".format(self.param.tco2))
        self.entryTemp.set_tooltip_text("CO2 inlet temperature")
        lbl = Gtk.Label(label="T<sub>CO2</sub>")
        lbl.set_use_markup(True)
        grid.attach(lbl, 2, irow, 1, 1)
        grid.attach(self.entryTemp, 3, irow, 1, 1)


        irow += 1
        grid.attach(Gtk.Label(label="Golden File"), 0, 2, 1, 1)
        grid.attach(self.goldenData, 1, 2, 1, 1)

        self.entryTHrs = Gtk.Entry()
        self.entryTHrs.set_tooltip_text("Temperature threshold.")
        self.entryTHrs.set_text("{:.1f}".format(self.param.thrs))
        lbl = Gtk.Label(label="Threshold")
        grid.attach(lbl, 2, irow, 1, 1)
        grid.attach(self.entryTHrs, 3, irow, 1, 1)


        irow += 1
        # the folder option
        self.btnFolder = Gtk.FileChooserButton()
        self.btnFolder.set_tooltip_text("Select folder for all output. If none selected, output in current folder.")
        self.btnFolder.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.btnFolder.connect("file-set", self.on_folder_set)
        if self.param.folder and len(self.param.folder) > 0 :
            ifile = Path(self.param.folder).expanduser().resolve().as_posix()
            self.btnFolder.set_filename(ifile)

        grid.attach(Gtk.Label(label="Folder"), 0, irow, 1, 1)
        grid.attach(self.btnFolder, 1, irow, 1, 1)

        self.entryDist = Gtk.Entry()
        self.entryDist.set_text("{}".format(self.param.distance))
        self.entryDist.set_tooltip_text("Distance in contour beteween slices")
        lbl = Gtk.Label(label="Distance")
        grid.attach(lbl, 2, irow, 1, 1)
        grid.attach(self.entryDist, 3, irow, 1, 1)

        irow += 1
        self.desy = Gtk.Switch()
        self.desy.props.halign = Gtk.Align.START
        self.desy.connect("state_set", self.change_institute)
        if params.desy or self.param.institute == "DESY":
            self.desy.set_active(True)
        grid.attach(Gtk.Label(label="DESY"), 0, irow, 1, 1)
        grid.attach(self.desy, 1, irow, 1, 1)

        irow += 1
        self.run = Gtk.Button(label="Run")
        self.run.connect("clicked", self.create_report)

        grid.attach(self.run, 0, irow, 5, 1)

        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)

    def on_desy_data(self, *args):
        """DESY data button clicked."""
        dlg = DesyData(self.irbfile)
        dlg.show_all()
        if dlg.run() ==  Gtk.ResponseType.OK:
            self.irbfile = [dlg.front, dlg.back]
            self.param.files = self.irbfile
            self.on_open_file()

        dlg.hide()
        dlg.destroy()


    def on_file_set(self, *args):
        """File chosen from FileChooser."""
        PSF = self.btnData.get_filename()
        if PSF is None or not Path(PSF).exists():
            itkdb_gtk.dbGtkUtils.complain("Could not find Data File", PSF, parent=self)
            return

        self.irbfile = [PSF, ]
        self.param.files = self.irbfile
        self.on_open_file()

    def on_open_file(self):
        """Open the files given in the GUI."""
        #DB = ReadGraphana("localhost")
        irbf = IRBFile.open_file(self.irbfile)
        getter = IRDataGetter.factory(self.param.institute, self.param)
        frames = getter.get_analysis_frame(irbf)

        if self.param.institute == "IFIC":
            server = os.getenv("GRAFANA_SERVER")
            if server is None:
                DB = ReadGraphana()
            else:
                DB = ReadGraphana(server)

            try:
                X, val = DB.get_temperature(frames[0].timestamp, 3)
                inlet = np.min(val)
                self.entryTemp.set_text("{:.1f}".format(inlet))

            except Exception as E:
                print(E)
                self.entryTemp.set_text("-30")


    def change_institute(self, *args):
        """Switch clicked."""
        if self.desy.get_active():
            self.param.institute = "DESY"
            upper = self.btnData.get_parent()
            if upper:
                self.dataBox.remove(self.btnData)
                self.dataBox.add(self.desyData)

            self.param.distance = 16
            self.param.width = 16

        else:
            self.param.institute = "IFIC"
            upper = self.desyData.get_parent()
            if upper:
                self.dataBox.remove(self.desyData)
                self.dataBox.add(self.btnData)

            self.param.distance = 5
            self.param.width = 2


        self.entryDist.set_text("{}".format(self.param.distance))
        self.dataBox.show_all()

    def on_golden_set(self, *args):
        """File chosen from FileChooser."""
        PSF = self.goldenData.get_filename()
        if PSF is None or not Path(PSF).exists():
            itkdb_gtk.dbGtkUtils.complain("Could not find Golden File", PSF, parent=self)
            return

        with open(PSF, "r", encoding='utf-8') as fp:
            self.golden = golden_from_json(json.load(fp))

        self.param.golden = PSF

    def on_folder_set(self, *args):
        """Folder chosen."""
        F = self.btnFolder.get_filename()
        if F is None or not Path(F).exists():
            itkdb_gtk.dbGtkUtils.complain("Could not find Output folder", F, parent=self)
            return

        self.folder = F
        self.param.folder = F

    def on_SN_changed(self, entry, value):
        """New SN given. Ask in PDB,"""
        if len(value) <= 0:
            return None


        obj = itkdb_gtk.ITkDButils.get_DB_component(self.session, value)
        if obj is not None:
            entry.set_text(obj["serialNumber"])
            self.alternativeID = obj["alternativeIdentifier"]

        else:
            itkdb_gtk.dbGtkUtils.complain("Invalid SN", value)

    def show_state(self, *arg):
        """Shows the status"""
        if self.outDB is None:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="State undefined",
                )
            dialog.format_secondary_text(
                 "No analysis data available yet."
                )
            dialog.run()
            dialog.destroy()
            return

        ndef = len(self.outDB["defects"])
        ncomm = len(self.outDB["comments"])

        if ndef+ncomm == 0:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="All good",
                )
            dialog.format_secondary_text(
                 "Petal core passed without problems."
                )
            dialog.run()
            dialog.destroy()
            return

        msg = ""
        if ndef:
            msg += "Defects\n"
        for D in self.outDB["defects"]:
            msg += "{}: {}\n".format(D["name"], D["description"])

        if ncomm:
            msg += "Comments\n"
            for C in self.outDB["comments"]:
                msg += "{}\n".format(C)


        dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Problems found",
                )

        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()


    def show_test_gui(self, *args):
        """Show test data."""
        if self.outDB is None:
            return

        values, rc = itkdb_gtk.dbGtkUtils.DictDialog.create_json_data_editor(self.outDB)
        if rc == Gtk.ResponseType.OK:
            self.outDB = values

    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        self.upload_test()

    def upload_test(self):
        """Uploads test and attachments."""
        if self.outDB is None:
            return
        uploadW = itkdb_gtk.UploadTest.UploadTest(self.session, payload=self.outDB)

    def create_report(self, *args):
        """Creates the thermal report."""
        if self.irbfile is None:
            self.write_message("Missing IRB file\n")
            return

        self.write_message("Start analysis\n.")
        self.param.out = "{}.json".format(self.alternativeID)
        self.param.alias = self.alternativeID
        self.param.SN = self.SN.get_text()
        self.param.desy = self.desy.get_active()

        self.param.tco2 = float(self.entryTemp.get_text())
        self.param.distance = int(self.entryDist.get_text())
        self.param.thrs = float(self.entryTHrs.get_text())
        self.param.debug = False
        self.param.report = True
        self.param.files = self.irbfile

        self.outDB = create_report(self.param)
        if self.outDB:
            if len(self.outDB["defects"]) > 0:
                itkdb_gtk.dbGtkUtils.set_button_color(self.btn_state, "red", "white")
                self.btn_state.set_label("FAILED")
            elif len(self.outDB["comments"]) > 0:
                itkdb_gtk.dbGtkUtils.set_button_color(self.btn_state, "orange", "white")
                self.btn_state.set_label("PROBLEMS")
            else:
                itkdb_gtk.dbGtkUtils.set_button_color(self.btn_state, "green", "white")
                self.btn_state.set_label("PASSED")

def main():
    """Entry point."""
    # Argument parser
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--nframe", type=int, default=-1, help="Number of frames. (negative means all.")
    parser.add_argument('--frame', type=int, default=-1, help="First frame to start.")
    parser.add_argument("--out", default="core.json", help="Output file name")
    parser.add_argument("--desy", dest='desy', action="store_true", default=False)

    parser.add_argument("--alias", default="", help="Alias")
    parser.add_argument("--SN", default="", help="serial number")
    parser.add_argument("--folder", default=None, help="Folder to store output files. Superseeds folder in --out")
    parser.add_argument("--golden", default=None, help="The golden to compare width")


    IRPetalParam.add_parameters(parser)

    options = parser.parse_args()
    #if len(options.files) == 0:
    #    print("I need an input file")
    #    sys.exit()

    # ITk PDB authentication
    dlg = None
    try:
        # We use here the Gtk GUI
        from itkdb_gtk import ITkDBlogin
        dlg = ITkDBlogin.ITkDBlogin()
        client = dlg.get_client()

    except Exception:
        # Login with "standard" if the above fails.
        client = itkdb_gtk.ITkDButils.create_client()

    CT = CoreThermal(options, session=client, title="Petal Thermal analysis.")
    CT.show_all()
    CT.connect("destroy", Gtk.main_quit)
    CT.write_message("Welcome !\n")

    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")


    try:
        dlg.die()

    except Exception:
        print("Bye !")

if __name__ == "__main__":
    main()