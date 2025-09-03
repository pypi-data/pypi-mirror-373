#!/usr/bin/env python3
"""GUI to launch metrology analysis."""
from pathlib import Path
from argparse import Action
from argparse import ArgumentParser
from contextlib import redirect_stdout
import numpy as np
from itkdb_gtk import ITkDButils, ITkDBlogin, dbGtkUtils, UploadTest

from petal_qc.metrology.do_Metrology import do_analysis

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio, GLib

__HELP__ = "https://petal-qc.docs.cern.ch/metrology.html"

class CoreMetrology(dbGtkUtils.ITkDBWindow):
    """Application window."""

    def __init__(self, options, session=None, title="",  panel_size=100):
        """Initialization.

        Args:
            title: The title of the window.
            pannel_size: size of message panel.

        """
        super().__init__(session=session, title=title, help_link=__HELP__)

        self.data_file = None
        self.folder = None
        self.petal_SN = None
        self.petal_prefix = None
        self.options = options
        self.alternativeID = None
        self.outDB = None


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
        self.btnData = Gtk.FileChooserButton()
        self.btnData.connect("file-set", self.on_file_set)
        if len(options.files) > 0 :
            ifile = Path(options.files[0]).expanduser().resolve().as_posix()
            self.btnData.set_filename(ifile)
            self.on_file_set()

        # the folder option
        self.btnFolder = Gtk.FileChooserButton()
        self.btnFolder.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.btnFolder.connect("file-set", self.on_folder_set)
        if options.folder and len(options.folder) > 0 :
            ifile = Path(options.folder).expanduser().resolve().as_posix()
            self.btnFolder.set_filename(ifile)

        # The Serial number
        self.SN = dbGtkUtils.TextEntry()
        self.SN.connect("text-changed", self.on_SN_changed)

        # The prefix
        self.prefix = Gtk.Entry()

        # The switch
        self.desy = Gtk.Switch()
        self.desy.props.halign = Gtk.Align.START

        self.back = Gtk.Switch()
        self.back.props.halign = Gtk.Align.START
        self.back.connect("state_set", self.change_to_back)

        self.run = Gtk.Button(label="Run")
        self.run.connect("clicked", self.run_analysis)

        self.btn_state = Gtk.Button(label="Undef")
        self.btn_state.set_name("btnState")
        self.btn_state.connect("clicked", self.show_state)
        self.btn_state.set_tooltip_text("If green all good. Click to see commnets and defects.")

        if options.desy:
            self.desy.set_active(True)

        # Put the 3 objects in a Grid
        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 0)

        grid.attach(Gtk.Label(label="Serial No."), 0, 0, 1, 1)
        grid.attach(self.SN.entry, 1, 0, 1, 1)

        grid.attach(self.btn_state, 2, 0, 1, 1)

        grid.attach(Gtk.Label(label="DESY"), 3, 0, 1, 1)
        grid.attach(self.desy, 4, 0, 1, 1)

        grid.attach(Gtk.Label(label="Prefix"), 0, 1, 1, 1)
        grid.attach(self.prefix, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Data File"), 0, 2, 1, 1)
        grid.attach(self.btnData, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Back"), 2, 2, 1, 1)
        grid.attach(self.back, 3, 2, 1, 1)
        grid.attach(Gtk.Label(label="Front"), 4, 2, 1, 1)



        grid.attach(Gtk.Label(label="Folder"), 0, 3, 1, 1)
        grid.attach(self.btnFolder, 1, 3, 1, 1)

        grid.attach(self.run, 0, 4, 5, 1)


        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)

        if self.options.SN:
            self.on_SN_changed(self.SN.entry, self.options.SN)

        if self.options.is_front:
            self.back.set_active(True)

        if self.options.folder:
            the_folder = Gio.File.new_for_path(self.options.folder)
            self.btnFolder.set_file(the_folder)
            self.on_folder_set(None)

        if len(self.options.files)>0:
            the_file = Gio.File.new_for_path(self.options.files[0])
            self.btnData.set_file(the_file)
            self.on_file_set(None)


    def quit(self, *args):
        """Quits the application."""
        self.hide()
        self.destroy()


    def on_file_set(self, *args):
        """File chosen from FileChooser."""
        PSF = self.btnData.get_filename()
        if PSF is None or not Path(PSF).exists():
            dbGtkUtils.complain("Could not find Data File", PSF, parent=self)
            return

        self.data_file = PSF

    def on_folder_set(self, *args):
        """Folder chosen."""
        F = self.btnFolder.get_filename()
        if F is None or not Path(F).exists():
            dbGtkUtils.complain("Could not find Output folder", F, parent=self)
            return

        self.folder = F
        self.options.folder = F

    def on_SN_changed(self, entry, value):
        """New SN given. Ask in PDB,"""
        if len(value) <= 0:
            return None


        obj = ITkDButils.get_DB_component(self.session, value)
        if obj is not None:
            entry.set_text(obj["serialNumber"])
            self.alternativeID = obj["alternativeIdentifier"]
            self.change_to_back(None)

        else:
            dbGtkUtils.complain("Invalid SN", value)

    def change_to_back(self, *args):
        """The front/back switch has changed."""
        is_front = self.back.get_active()
        if self.alternativeID is None:
            return

        if is_front:
            txt = "{}-front".format(self.alternativeID)
        else:
            txt = "{}-back".format(self.alternativeID)

        self.prefix.set_text(txt)

    def check_SN(self, SN):
        """Checks the serial number."""
        if len(SN) <= 0:
            return None

        obj = ITkDButils.get_DB_component(self.session, SN)
        if obj is None:
            return None

        if self.alternativeID is None:
            self.alternativeID = obj["alternativeIdentifier"]

        self.change_to_back(None)
        return obj["serialNumber"]

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

    def run_analysis(self, *args):
        """Run metrology."""
        if self.data_file is None:
            dbGtkUtils.complain("No data file set", "Select one", parent=self)
            return

        if self.desy.get_active():
            self.options.desy = True

        is_front = self.back.get_active()
        suffix = "back"
        if is_front:
            suffix = "front"

        self.petal_prefix = self.prefix.get_text().strip()
        if len(self.petal_prefix) == 0:
            self.petal_prefix = "{}-{}".format(self.alternativeID, suffix)
            self.prefix.set_text(self.petal_prefix)

        self.petal_SN = self.SN.get_text().strip()
        if len(self.petal_SN) == 0 or self.petal_SN is None:
            dbGtkUtils.complain("Invalid SN", "SN: {}".format(self.petal_SN), parent=self)
            return


        with redirect_stdout(self.message_panel):
            self.outDB = do_analysis(self.data_file, self.petal_prefix, self.petal_SN, self.options)

        if len(self.outDB["defects"]) > 0:
            dbGtkUtils.set_button_color(self.btn_state, "red", "white")
            self.btn_state.set_label("FAILED")
        elif len(self.outDB["comments"]) > 0:
            dbGtkUtils.set_button_color(self.btn_state, "orange", "white")
            self.btn_state.set_label("PROBLEMS")
        else:
            dbGtkUtils.set_button_color(self.btn_state, "green", "white")
            self.btn_state.set_label("PASSED")


    def show_test_gui(self, *args):
        """Show test data."""
        if self.outDB is None:
            return

        values, rc = dbGtkUtils.DictDialog.create_json_data_editor(self.outDB)
        if rc == Gtk.ResponseType.OK:
            self.outDB = values

    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        self.upload_test()

    def upload_test(self):
        """Uploads test and attachments."""
        if self.outDB is None:
            return
        uploadW = UploadTest.UploadTest(self.session, payload=self.outDB)


class CoreMetrologyOptions(object):
    """Dummy options"""
    def __init__(self):
        self.files = []
        self.SN = None
        self.desy = False
        self.is_front = False
        self.folder = None
        self.prefix = None
        self.locking_points = None
        self.title = None
        self.nbins = 25
        self.label = "\\w+"
        self.type = "Punto"

def main():
    """Entry point."""
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--prefix", dest='prefix', default=None)
    parser.add_argument("--SN", dest='SN', default=None)
    parser.add_argument("--front", dest='is_front', action="store_true", default=False)

    parser.add_argument("--save", dest='save', action="store_true", default=False)
    parser.add_argument("--desy", dest='desy', action="store_true", default=False)
    parser.add_argument("--out", dest="out", default="petal_flatness.docx",
                        type=str, help="The output fiel name")
    parser.add_argument("--title", dest="title", default=None,
                        type=str, help="Document title")
    parser.add_argument("--nbins", dest="nbins", default=25,
                        type=int, help="Number of bins")
    parser.add_argument("--folder", default=None, help="Folder to store output files. Superseeds folder in --out")
    parser.add_argument("--locking_points", action="store_true", default=False)

    # This is to convert a CMM file
    parser.add_argument("--label", default="\\w+", help="The label to select")
    parser.add_argument("--type", default="Punto", help="The class to select")

    options = parser.parse_args()


    # ITk PDB authentication
    dlg = None
    try:
        # We use here the Gtk GUI
        dlg = ITkDBlogin.ITkDBlogin()
        client = dlg.get_client()

    except Exception:
        # Login with "standard" if the above fails.
        client = ITkDButils.create_client()

    CM = CoreMetrology(options, session=client, title="Petal core metrology")
    CM.write_message("Welcome !\n")
    CM.connect("destroy", Gtk.main_quit)

    CM.show_all()
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