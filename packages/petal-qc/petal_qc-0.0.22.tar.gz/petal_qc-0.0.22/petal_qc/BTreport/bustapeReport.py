#!/usr/bin/env python3
"""GUI for the BTtest."""
import dateutil.parser
import getpass
from itkdb_gtk import ITkDButils
from itkdb_gtk import dbGtkUtils
from itkdb_gtk import ITkDBlogin
import itkdb

from petal_qc.BTreport import CheckBTtests

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class BusTapeReport(dbGtkUtils.ITkDBWindow):
    """Makes a report of bustapes."""

    BUSTAPE, SERIAL_NO, STAGE, DATE, PASSED = range(5)

    def __init__(self, session=None, title="",  panel_size=100):
        """Initialization.

        Args:
            title: The title of the window.
            pannel_size: size of message panel.

        """
        super().__init__(session=session, title=title, show_search="SEarch for Petal CORE")
        self.petal_SN = None
        self.alternativeID = None
        self.outDB = None
        self.tree = None
        self.petal = None
        self.petal_date = None

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

        # The Serial number
        self.SN = dbGtkUtils.TextEntry()
        self.SN.connect("text-changed", self.on_SN_changed)

        # Put the 3 objects in a Grid
        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 0)

        grid.attach(Gtk.Label(label="Serial No."), 0, 0, 1, 1)
        grid.attach(self.SN.entry, 1, 0, 1, 1)


        # the list of attachments
        self.create_tree_view()
        self.mainBox.pack_start(self.tree, True, True, 5)

        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)


    def quit(self, *args):
        """Quits the application."""
        self.hide()
        self.destroy()

    def create_tree_view(self):
        """Creates the Tree vvew"""
        model = Gtk.ListStore(str, str, str, str, bool)
        self.tree = Gtk.TreeView(model=model)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tape", renderer, text=BusTapeReport.BUSTAPE)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("SN", renderer, text=BusTapeReport.SERIAL_NO)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Stage", renderer, text=BusTapeReport.STAGE)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Test Date", renderer, text=BusTapeReport.DATE)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Passed", renderer, text=BusTapeReport.PASSED)
        self.tree.append_column(column)


    def on_SN_changed(self, entry, value):
        """New SN given. Ask in PDB,"""
        if len(value) <= 0:
            return None


        obj = ITkDButils.get_DB_component(self.session, value)
        if obj is not None:
            if self.check_petal(obj):
                entry.set_text(obj["serialNumber"])
                self.alternativeID = obj["alternativeIdentifier"]
                self.petal = obj
                self.petal_date = dateutil.parser.parse(self.petal["stateTs"])

                self.query_db()

        else:
            dbGtkUtils.complain("Invalid SN", value)

    def check_petal(self, petal):
        """Check that the petal is a good one."""
        comp_type = CheckBTtests.get_type(petal)
        if comp_type != "CORE_AVS":
            dbGtkUtils.complain("This is not a petal coree", comp_type)
            return False

        # Check that the petal core is in the proper stage.
        stage = petal["currentStage"]['code']
        if stage != "AT_QC_SITE":
            dbGtkUtils.complain("Petal core is not at QC_SITE", "Current stage: {}".format(stage))
            return False

        return True
    def query_db(self, *args):
        """Search petal and bustapes."""
        if self.petal is None:
            return

        model = Gtk.ListStore(str, str, str, str, bool)
        self.tree = Gtk.TreeView(model=model)

        # Loop on children an find bustapes
        bt_list, bt_valid = CheckBTtests.find_bus_tapes(self.session,
                                                        self.petal,
                                                        complain_func=dbGtkUtils.complain)

        for btype, item in bt_list.items():
            bt_sn = item[0]["serialNumber"]
            cstage = item[0]["currentStage"]['code']
            bt_tests = CheckBTtests.find_but_tape_tests(self.session,
                                                        self.petal_date,
                                                        bt_sn,
                                                        complain_func=dbGtkUtils.complain)

            values = [btype, bt_sn, cstage]

        self.outDB = CheckBTtests.BTreport(self.session, SN, complain_func=dbGtkUtils.complain)

        if self.outDB is None:
            dbGtkUtils.complain("Could not get he report.")

    def show_test_gui(self, *args):
        """Show test data."""
        if self.outDB is None:
            return

        values, rc = dbGtkUtils.DictDialog.create_json_data_editor(self.outDB)
        if rc == Gtk.ResponseType.OK:
            self.outDB = values


    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        pass

def main():
    # ITk PDB authentication
    dlg = None
    try:
        # We use here the Gtk GUI
        dlg = ITkDBlogin.ITkDBlogin()
        client = dlg.get_client()

    except Exception:
        # Login with "standard" if the above fails.
        client = itkdb.Client()
        client.user._access_code1 = getpass.getpass("Access 1: ")
        client.user._access_code2 = getpass.getpass("Access 2: ")
        client.user.authenticate()
        print("Hello {} !".format(client.user.name))

    BT = BusTapeReport(client, title="Bustape Report")
    BT.write_message("Welcome !!\n")
    BT.connect("destroy", Gtk.main_quit)
    BT.show_all()

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