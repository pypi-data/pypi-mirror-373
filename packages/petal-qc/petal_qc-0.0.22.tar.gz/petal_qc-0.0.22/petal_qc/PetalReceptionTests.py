#!/usr/bin/env python3
"""Test dashboard."""
import sys
import copy
from pathlib import Path

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())
    import itkdb_gtk

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils
from itkdb_gtk import UploadTest, UploadMultipleTests

HELP_LINK="https://itkdb-gtk.docs.cern.ch"


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


def find_children(W):
    """Find DictDialog among the children."""
    try:
        for c in W.get_children():
            if "DictDialog" in c.get_name():
                return c

            else:
                return find_children(c)

    except Exception:
        return None

    return None


class PetalReceptionTests(dbGtkUtils.ITkDBWindow):
    """Petl Reception Test GUI."""

    def __init__(self, session, help_link=None):
        """Initialization."""
        super().__init__(title="Petal Reception Tests",
                         session=session,
                         show_search="Find object with given SN.",
                         help_link=help_link)

        # Members
        self.dbObject = None

        # action button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload ALL tests.")
        button.connect("clicked", self.upload_tests)
        self.hb.pack_end(button)

        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, False, False, 5)

        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)


        self.SN = itkdb_gtk.dbGtkUtils.TextEntry()
        self.SN.connect("text-changed", self.on_SN_changed)

        #self.SN = Gtk.Entry()
        #self.SN.connect("focus-in-event", self.on_sn_enter)
        #self.SN.connect("focus-out-event", self.on_sn_leave)
        grid.attach(self.SN.entry, 1, 0, 1, 1)

        self.alias = Gtk.Label(label="")
        grid.attach(self.alias, 2, 0, 1, 1)

        self.stage = Gtk.Label(label="")
        grid.attach(self.stage, 3, 0, 1, 1)

        lbl = Gtk.Label(label="Institute")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)

        self.institute = self.pdb_user["institutions"][0]["code"]
        inst = self.create_institute_combo(only_user=True)
        inst.connect("changed", self.new_institute)
        inst.set_tooltip_text("Select the Institute.")
        grid.attach(inst, 1, 1, 1, 1)
        self.inst_cmb = inst

        # The "Add/Remove/Send Item" buttons.
        box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_layout(Gtk.ButtonBoxStyle.END)
        self.mainBox.pack_start(box, False, False, 0)
        dbGtkUtils.add_button_to_container(box, "Upload test", "Upload this test", self.upload_single_test)
        dbGtkUtils.add_button_to_container(box, "Add Defect", "Click to add a defect", self.add_defect)
        dbGtkUtils.add_button_to_container(box, "Add Comment", "Click to add a comment", self.add_comment)

        # The notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.notebook.set_size_request(-1, 250)
        self.mainBox.pack_start(self.notebook, True, True, 0)

        # Create the Notebook pages
        self.create_test_box("Visual Inspection", "VISUAL_INSPECTION")
        self.create_test_box("Grounding", "GROUNDING_CHECK")
        self.create_test_box("Pipe bending", "BENDING120")
        self.create_test_box("Delamination", "DELAMINATION")
        self.create_test_box("Weight", "PETAL_CORE_WEIGHT")
        self.create_test_box("Metrology Template", "METROLOGY_TEMPLATE")
        self.create_test_box("X-rays", "XRAYIMAGING")


        # The text view
        self.mainBox.pack_end(self.message_panel.frame, True, True, 5)

        # Set the default institute
        dbGtkUtils.set_combo_iter(inst, self.institute)


        self.show_all()

    def on_SN_changed(self, entry, value):
        """New SN given. Ask in PDB,"""
        if len(value) <= 0:
            return None

        self.query_db()
        current_location = self.dbObject["currentLocation"]["code"]
        dbGtkUtils.set_combo_iter(self.inst_cmb, current_location, 0)

        stg = self.dbObject["currentStage"]["name"]
        self.stage.set_text(stg)

        entry.set_text(self.dbObject["serialNumber"])

        alias = self.dbObject["alternativeIdentifier"]
        self.alias.set_text(alias)

        npages = self.notebook.get_n_pages()
        for i in range(npages):
            page = self.notebook.get_nth_page(i)
            page.dict_dialog.factory_reset()


    def create_test_box(self, label, test_name, institute=None):
        """Create and add to notebook a test dialog.

        Args:
            label: The label for the Notebook
            test_name: The DB name of the test
            institute: The institute.

        """
        if institute is None:
            institute = self.institute

        defaults = {
            "institution": institute,
            "runNumber": "1",
        }
        dto = ITkDButils.get_test_skeleton(self.session, "CORE_PETAL", test_name, defaults)
        if test_name == "VISUAL_INSPECTION":
            scrolled, gM = dbGtkUtils.create_scrolled_dictdialog(dto, ("component", "testType", "results"))
        else:
            scrolled, gM = dbGtkUtils.create_scrolled_dictdialog(dto)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        box.pack_end(scrolled, True, True, 0)
        box.dict_dialog = gM
        gM.box = box

        self.notebook.append_page(box, Gtk.Label(label=label))

        return gM

    def query_db(self, *args):
        """Search button clicked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Empty Serial number",
                                "You should enter a valid Serial number for the petal core.",
                                parent=self)

        try:
            self.dbObject = ITkDButils.get_DB_component(self.session, SN)

        except Exception as E:
            self.write_message(str(E)+'\n')
            dbGtkUtils.complain("Could not find object in DB", str(E))
            self.dbObject = None
            return

        #print(json.dumps(self.dbObject, indent=3))

    def add_defect(self, btn):
        """Add a new defect."""
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        values = dbGtkUtils.get_a_list_of_values("Insert new defect", ("Type", "Description/v"))
        if len(values)>0:
            defect = {"name": values[0], "description": values[1]}
            page.dict_dialog.values["defects"].append(defect)
            page.dict_dialog.refresh()

    def add_comment(self, btn):
        """Add a new comment."""
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        comment = dbGtkUtils.get_a_value("Insert new comment", is_tv=True)
        if comment:
            page.dict_dialog.values["comments"].append(comment)
            page.dict_dialog.refresh()

    def new_institute(self, combo):
        """A new institute has been selected."""
        inst = self.get_institute_from_combo(combo)
        if inst:
            self.institute = inst

            npages = self.notebook.get_n_pages()
            for i in range(npages):
                page = self.notebook.get_nth_page(i)
                page.dict_dialog.values["institution"] = self.institute
                page.dict_dialog.refresh()

    def upload_this_test(self, values):
        """Upload a single test."""
        # print(json.dumps(values, indent=2))

        attachments = []
        if values["testType"] == "XRAYIMAGING":
            fnam = values["results"]["IMAGELINK"]
            if fnam is not None and len(fnam)>0:
                P = Path(fnam).expanduser().resolve()
                if P.exists():
                    A = ITkDButils.Attachment(path=P.as_posix(), title=P.name, desc="X-ray image")
                    values["results"]["IMAGELINK"] = P.name
                    attachments.append(A)

        # rc = ITkDButils.upload_test(self.session, values, attachments=attachments, check_runNumber=True)
        # if rc is not None:
        #     dbGtkUtils.complain("Could not upload test", rc)
        # 
        # else:
        #     self.write_message("Test uploaded. {} - {}\n".format(values["component"], values["testType"]))
        uploadW = UploadTest.UploadTest(self.session, values, attachments)


    def upload_single_test(self, *args):
        """Upload the current test."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Petal SN is empty")
            return

        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        dctD = find_children(page)
        if dctD is None:
            return

        values = copy.deepcopy(dctD.values)
        values["component"] = SN
        self.upload_this_test(values)

    def upload_tests(self, *args):
        """Upload the current test."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Petal SN is empty")
            return

        W = UploadMultipleTests.UploadMultipleTests(
            self.session,
            help_link="{}/uploadMultipleTests.html".format(HELP_LINK)
        )

        for ipage in range(self.notebook.get_n_pages()):
            page = self.notebook.get_nth_page(ipage)
            dctD = find_children(page)
            if dctD is None:
                continue

            values = dctD.values
            if values["testType"] == "XRAYIMAGING":
                if values["institution"] != "IFIC":
                    continue
                
                fnam = values["results"]["IMAGELINK"]
                if fnam is None or len(fnam)==0:
                    continue

            values["component"] = SN
            W.add_test_data_to_view(values)

def main():
    """Main entry."""
    # DB login
    HELP_LINK="https://petal-qc.docs.cern.ch/petalReceptionTests.html"

    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    gTest = PetalReceptionTests(client, help_link=HELP_LINK)

    gTest.present()
    gTest.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()
