#!/usr/bin/env python3
"""Uploads data from AVS pdf."""
import json
import sys
from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import dateutil.parser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

try:
    import petal_qc

except ImportError:
    cwd = Path(__file__).parent.parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import ITkDBlogin, ITkDButils, dbGtkUtils
from petal_qc.metrology import readAVSdata

__HELP_LINK__="https://petal-qc.docs.cern.ch/uploadPetalInformation.html"

def create_scrolled_dictdialog(the_dict, hidden=("component", "testType")):
    """Create a DictDialog within a scrolled window.

    Return:
    ------
        scrolled: the scrolled window
        gM: the DictDialog

    """
    gM = dbGtkUtils.DictDialog(the_dict, hidden)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(gM)
    return scrolled, gM


def get_type(child):
    """Return object type

    Args:
        child (): object

    Returns:
        str: object type

    """
    if child["type"] is not None:
        ctype = child["type"]["code"]
    else:
        ctype = child["componentType"]["code"]

    return ctype

class AVSPanel(dbGtkUtils.ITkDBWindow):
    """Dialog for interaction with DB."""

    def __init__(self, session, options):
        """Initialization."""
        super().__init__(session=session, title="Upload AVS Data", show_search="Click to search SN in DB", help_link=__HELP_LINK__)
        self.test_uploaded = {}
        self.test_list = []
        self.test_index = {}
        self.test_panel = {}
        self.test_map = {}
        self.petal_core = None
        self.alias = None
        self.petal_weight = -1
        self.DESY_comp = {}
        # self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #
        # Prepare HeaderBar
        self.hb.props.title = "DB Upload Petal Data"

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test shown in notebook.")
        button.connect("clicked", self.upload_current_test)
        self.hb.pack_end(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="emblem-documents-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload AVS files.")
        button.connect("clicked", self.upload_avs_files)
        self.hb.pack_end(button)

        # PS file entry and search button
        self.btnPSF = Gtk.FileChooserButton()
        self.btnPSF.connect("file-set", self.on_psf_set)
        if options.PS:
            ifile = Path(options.PS).expanduser().resolve().as_posix()
            self.btnPSF.set_filename(ifile)
            self.on_psf_set()

        # FAT file entry and seach buttin
        self.btnFAT = Gtk.FileChooserButton()
        self.btnFAT.connect("file-set", self.on_fat_set)
        if options.FAT:
            ifile = Path(options.FAT).expanduser().resolve().as_posix()
            self.btnFAT.set_filename(ifile)

        # The Serial number
        self.SN = Gtk.Entry()
        # self.SN.connect("changed", self.SN_changed)
        if options.SN:
            self.SN.set_text(options.SN)

        # Put the 3 objects in a Grid
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, False, True, 0)

        self.btn_state = Gtk.Button(label="Undef")
        self.btn_state.set_name("btnState")
        self.btn_state.connect("clicked", self.show_state)
        self.btn_state.set_tooltip_text("If green all good. Click to see commnets and defects.")

        grid.attach(Gtk.Label(label="Serial No."), 0, 0, 1, 1)
        grid.attach(self.SN, 1, 0, 1, 1)
        grid.attach(self.btn_state, 2, 0, 1, 1)


        grid.attach(Gtk.Label(label="Prod. Sheet"), 0, 1, 1, 1)
        grid.attach(self.btnPSF, 1, 1, 1, 1)

        btn = Gtk.Button(label="Reset")
        btn.connect("clicked", self.on_reset)
        grid.attach(btn, 2, 1, 1, 1)

        grid.attach(Gtk.Label(label="FAT file"), 0, 2, 1, 1)
        grid.attach(self.btnFAT, 1, 2, 1, 1)

        # Add a Separator
        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, True, 0)

        # The notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.mainBox.pack_start(self.notebook, True, True, 20)

        # Create the Notebook pages
        defaults = {
            "institution": "AVS",
            "runNumber": 1,
        }

        self.manufacture = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.session, "CORE_PETAL", "MANUFACTURING", defaults),
            "manufacture", "Manufacture")

        self.weights = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.session, "CORE_PETAL", "WEIGHING", defaults),
            "weights", "Weights")

        self.delamination = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.session, "CORE_PETAL", "DELAMINATION", defaults),
            "delamination", "Delamination")

        self.grounding = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.session, "CORE_PETAL", "GROUNDING_CHECK", defaults),
            "grounding", "Grounding")

        self.metrology = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.session, "CORE_PETAL", "METROLOGY_AVS", defaults),
            "metrology", "Metrology")

        self.visual_inspection = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.session, "CORE_PETAL", "VISUAL_INSPECTION", defaults),
            "visual_inspection", "Visual Inspection")

        # List componentes
        self.components = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.components.set_border_width(5)
        self.notebook.append_page(self.components, Gtk.Label(label="Components"))

        # The button box
        btnBox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)

        # btn = Gtk.Button(label="Reload AVS files")
        # btn.connect("clicked", self.read_avs_files)
        # btnBox.add(btn)

        btn = Gtk.Button(label="Assemble")
        btn.set_tooltip_text("Assemble components in DB")
        btn.connect("clicked", self.on_assembly)
        btnBox.add(btn)

        btn = Gtk.Button(label="Check Components")
        btn.set_tooltip_text("Check components in DB")
        btn.connect("clicked", self.on_check_components)
        btnBox.add(btn)

        btn = Gtk.Button(label="Check Tests")
        btn.set_tooltip_text("Check test results")
        btn.connect("clicked", self.on_check_tests)
        btnBox.add(btn)

        btn = Gtk.Button(label="Upload Tests")
        btn.set_tooltip_text("Upload all tests")

        btn.connect("clicked", self.on_upload)
        btnBox.add(btn)

        self.mainBox.pack_start(btnBox, False, True, 0)
        self.connect("destroy", Gtk.main_quit)


        # The text view
        self.mainBox.pack_start(self.message_panel.frame, True, True, 5)

        self.show_all()


    def show_state(self, *arg):
        """Shows the status"""
        msg = ""
        for test in self.test_list:
            values = test.values
            ndef = len(values["defects"])
            ncomm = len(values["comments"])
            if ndef==0 and ncomm==0:
                continue

            msg += "{}\n".format(values["testType"])
            if ndef:
                msg += "Defects\n"

            for D in values["defects"]:
                msg += "{}: {}\n".format(D["name"], D["description"])

            if ncomm:
                msg += "Comments\n"

            for C in values["comments"]:
                msg += "{}\n".format(C)

            msg += "\n"

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

    def on_reset(self, *args):
        """Reset SN"""
        self.petal_core = None
        self.alias = None
        self.SN.set_text("")
        self.btnPSF.unselect_all()
        self.btnFAT.unselect_all()
        self.btn_state.set_label("Undef")
        dbGtkUtils.set_button_color(self.btn_state, "azure", "black")


    def create_test_window(self, test_json, test_name, label):
        """Create the dialog for a DB test and add it to the notebook.

        Args:
            test_json: The JSon-like dict with the values
            test_name: The name of the test for internal indexing
            label: The label for the Notebook

        Returns:
            The box containing the data.

        """
        scrolled, gM = create_scrolled_dictdialog(test_json)
        self.test_list.append(gM)
        self.test_index[test_name] = len(self.test_list) - 1
        self.test_map[test_json["testType"]] = test_name

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        box.pack_end(scrolled, True, True, 0)
        box.dict_dialog = gM
        gM.box = box
        self.test_panel[test_name] = box
        self.notebook.append_page(box, Gtk.Label(label=label))

        return box

    def update_scroll_window(self, key, data):
        """Update panel for a given test."""
        scrolled, gM = create_scrolled_dictdialog(data, ("component", "testType"))
        self.test_list[self.test_index[key]] = gM
        dbGtkUtils.replace_in_container(self.test_panel[key], scrolled)

    def check_register_petal(self, SN):
        """Register petal core in DB.

        Args:
            SN: The petal Serial Number.

        """
        if self.petal_core:
            return

        self.find_petal(SN, silent=True)
        if self.petal_core and self.petal_core["alternativeIdentifier"] is not None:
            if len(self.petal_core["batches"])==0:
                ITkDButils.set_petal_core_batch(self.session, self.petal_core)
                
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            text="Register Petal Core\n{}".format(SN)
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_border_width(10)
        dialog.format_secondary_text("Enter Petal Core Alias")
        alias = Gtk.Entry(text=self.alias)
        box = dialog.get_content_area()
        box.add(alias)
        dialog.show_all()
        out = dialog.run()
        if out == Gtk.ResponseType.OK:
            petal_alias = alias.get_text().strip()
            if len(petal_alias) == 0:
                petal_alias = self.alias

            rc = ITkDButils.registerPetalCore(self.session, SN, petal_alias, petal_core=self.petal_core)
            if rc is None:
                dbGtkUtils.complain("Could not Register petal {} ({})".format(SN, petal_alias))

        dialog.hide()
        dialog.destroy()

    def get_app_petal_serial_number(self):
        """Get the SN from the text box."""
        txt_SN = self.SN.get_text().strip()
        return txt_SN

    def check_petal_serial_number(self, SN):
        """Check tha the given SN is consistent."""
        txt_SN = self.get_app_petal_serial_number()
        if txt_SN and len(txt_SN):
            if txt_SN != SN.strip():
                return False

            else:
                return True

        else:
            self.check_register_petal(SN)
            self.SN.set_text(SN)
            return True

    def on_psf_set(self, *args):
        """Production Sheet file selected."""
        PSF = self.btnPSF.get_filename()
        if PSF is None or not Path(PSF).exists():
            dbGtkUtils.complain("Could not find Production File", PSF, parent=self)
            return

        try:
            manuf_json, weights_json, self.DESY_comp, self.alias = readAVSdata.readProductionSheet(self.session, PSF, "SNnnnn")
            if self.petal_weight > 0:
                weights_json["results"]["WEIGHT_CORE"] = self.petal_weight

        except readAVSdata.AVSDataException as E:
            dbGtkUtils.complain("Wrong Production Sheet file", str(E))
            self.btnPSF.unselect_all()
            return

        SN = manuf_json["component"]
        if not self.check_petal_serial_number(SN):
            dbGtkUtils.complain("Inconsistent Serial number found.",
                     "Wrong Serial number extracted from the Production Sheet document.\n{}".format(PSF))
            self.btnPSF.unselect_all()
            return

        scrolled, gM = create_scrolled_dictdialog(manuf_json, ("component", "testType"))
        self.test_list[self.test_index["manufacture"]] = gM
        dbGtkUtils.replace_in_container(self.manufacture, scrolled)

        scrolled, gM = create_scrolled_dictdialog(weights_json, ("component", "testType"))
        self.test_list[self.test_index["weights"]] = gM
        dbGtkUtils.replace_in_container(self.weights, scrolled)

        gD = dbGtkUtils.DictDialog(self.DESY_comp)
        dbGtkUtils.replace_in_container(self.components, gD)

        # Check if we need to assemble the module
        self.check_assembly(self.DESY_comp)

        self.check_components()

    def on_fat_set(self, *args):
        """FAT file selected."""
        FAT = self.btnFAT.get_filename()
        if FAT is None or not Path(FAT).exists():
            dbGtkUtils.complain("Could not find FAT File", FAT, parent=self)

        try:
            SN = self.get_app_petal_serial_number()
            if SN and not SN.startswith("20USEBC"):
                SN = None

            j_vi, j_del, j_gnd, j_mtr, batch, self.petal_weight = readAVSdata.readFATfile(self.session, FAT, SN)
            self.test_list[self.test_index["weights"]].set_value("results.WEIGHT_CORE", self.petal_weight)

        except readAVSdata.AVSDataException as E:
            dbGtkUtils.complain("Wrong FAT file", str(E))
            self.btnFAT.unselect_all()
            return

        SN = j_vi["component"]
        if not self.check_petal_serial_number(SN):
            dbGtkUtils.complain("Inconsistent Serial number found.",
                     "Wrong Serial number extracted from the FAT document.\n{}".format(FAT))
            self.btnFAT.unselect_all()
            return

        self.update_scroll_window("visual_inspection", j_vi)
        self.update_scroll_window("delamination", j_del)
        self.update_scroll_window("grounding", j_gnd)
        self.update_scroll_window("metrology", j_mtr)

        self.check_tests(True)

    def read_avs_files(self, widgets):
        """Read AVS files."""
        PSF = self.btnPSF.get_filename()
        if PSF is not None:
            self.on_psf_set(None)

        FAT = self.btnFAT.get_filename()
        if FAT is not None:
            self.on_fat_set(None)

        return

    def find_petal(self, SN, silent=False):
        """Finds petal with given SN."""
        try:
            self.petal_core = ITkDButils.get_DB_component(self.session, SN)

        except Exception as E:
            if not silent:
                dbGtkUtils.complain("Could not find Petal Core in DB", str(E))

            self.petal_core = None
            return

        if self.petal_core is None:
            return

        try:
            if self.petal_core["type"]["code"] != "CORE_AVS":
                dbGtkUtils.complain("Wrong component type", "This is not an AVS petal core")

            if self.petal_core["currentStage"]["code"] != "ASSEMBLY":
                dbGtkUtils.complain("Wrong component stage", "Wrong stage: {}".format(self.petal_core["currentStage"]["code"]))

            self.write_message("{}\n".format(json.dumps(self.petal_core, indent=3)))

        except KeyError:
            # Petal is not there
            self.petal_core = None

    def query_db(self, *args):
        """Called when QueryDB button clicked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Empty Serial number",
                     "You should enter a valid Serial number for the petal core.",
                     parent=self)
            self.petal_core = None
            return

        # if not checkSerialNumber(SN):
        #     dbGtkUtils.complain("Wrong Serial number",
        #              "You should enter a valid Serial number for the petal core.",
        #              parent=self)
        #     return
        self.find_petal(SN)

        if self.btnFAT.get_filename() is None and self.btnPSF.get_filename() is None:
            # update tests from DB
            for test in self.petal_core["tests"]:
                latest = None
                latest_time = datetime(year=1, month=1, day=1, tzinfo=timezone.utc)
                testType = test["code"]
                for T in test["testRuns"]:
                    test_date = dateutil.parser.parse(T["cts"])
                    if test_date > latest_time:
                        latest_time = test_date
                        latest = T["id"]

                dbT = ITkDButils.get_testrun(self.session, latest)
                testDB = ITkDButils.from_full_test_to_test_data(dbT)
                self.update_scroll_window(self.test_map[testType], testDB)

    def on_check_components(self, *args):
        """Button clicked."""
        self.check_components()

    def check_components(self):
        """Check that components are in DB."""
        for cmp, cmp_SN in self.DESY_comp.items():
            if not (isinstance(cmp_SN, str) and cmp_SN.startswith("20U")):
                continue

            out = ITkDButils.get_DB_component(self.session, cmp_SN)
            if out is None:
                self.write_message("{}: not in DB\n".format(cmp))
            else:
                self.write_message("{}: in {}\n".format(cmp, out["currentLocation"]["code"]))


    def check_assembly(self, components):
        """Check if we need to assemble components to core."""
        if self.petal_core is None:
            self.query_db()
            if self.petal_core is None:
                return

        this_petal = self.SN.get_text()
        # Check for HonneyComb set
        for P in self.petal_core["properties"]:
            if P["code"] == "HC_ID" and P["value"] is None:
                if dbGtkUtils.is_iterable(components["HoneyCombSet"]):
                    val = ','.join([str(x) for x in components["HoneyCombSet"]])
                else:
                    val = str(components["HoneyCombSet"])
                rc = ITkDButils.set_component_property(self.session,
                                                        this_petal,
                                                        "HC_ID",
                                                        val)
                if rc is None:
                    error_txt.append("Problems setting HoneyCombSet ID.\n")

                break

        comp_map = {
            "BT_PETAL_FRONT": "FacingFront",
            "BT_PETAL_BACK": "FacingBack",
            "COOLING_LOOP_PETAL": "CoolingLoop",
            "THERMALFOAMSET_PETAL": "AllcompSet"
        }
        final_stage = {
            "BT_PETAL_FRONT": "COMPLETED",
            "BT_PETAL_BACK": "COMPLETED",
            "COOLING_LOOP_PETAL": "CLINCORE",
            "THERMALFOAMSET_PETAL": "IN_CORE"
        }
        missing = []
        for child in self.petal_core["children"]:
            if child["component"] is None:
                if child["type"] is not None:
                    ctype = child["type"]["code"]
                else:
                    ctype = child["componentType"]["code"]

                missing.append(ctype)

        if len(missing) == 0:
            return

        error_txt = []
        txt = "Click OK to add\n\t{}".format("\n\t".join(missing))
        if dbGtkUtils.ask_for_confirmation("Missing components", txt, parent=self):
            for cmp in missing:
                SN = components[comp_map[cmp]]
                if SN[0:5] == "20USE":
                    rc = ITkDButils.assemble_component(self.session, this_petal, SN)
                    if rc is None:
                        error_txt.append("Problem assembling {} into Petal\n".format(cmp))

                    # Check for child stage
                    cobj = ITkDButils.get_DB_component(self.session, SN)
                    ctype = get_type(cobj)
                    cstage = cobj["currentStage"]['code']
                    if cstage != final_stage[ctype]:
                        rc = ITkDButils.set_object_stage(self.session, SN, final_stage[ctype])
                        if rc is None:
                            print("Could not set final stage of {} [{}]".format(ctype, SN))

            # Check the final stage of the assembled objects
            # for child in self.petal_core["children"]:
            #     if child["component"]:
            #         cSN = child["component"]["serialNumber"]
            #         ctype = get_type(child)
            #         cobj = ITkDButils.get_DB_component(self.session, cSN)
            #         cstage = cobj["currentStage"]['code']
            #         if cstage != final_stage[ctype]:
            #             rc = ITkDButils.set_object_stage(self.session, cSN, final_stage[ctype])
            #             if rc is None:
            #                 print("Could not set final stage of {}".format(cSN))
            #
            if len(error_txt)>0:
                dbGtkUtils.complain("Assembly of {} could not be completeed:".format(this_petal),
                         "\n".join(error_txt))

    def upload_current_test(self, *args):
        """Called with upload button clcked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Petal SN is empty")
            return

        def find_children(W):
            try:
                for c in W.get_children():
                    if "DictDialog" in c.get_name():
                        return c

                    else:
                        return find_children(c)

            except Exception:
                return None

            return None

        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        dctD = find_children(page)
        if dctD is None:
            return

        values = dctD.values
        values["component"] = SN
        print(json.dumps(values, indent=2))
        rc = ITkDButils.upload_test(self.session, values)
        if rc is not None:
            dbGtkUtils.complain("Could not upload test", rc)

        else:
            dbGtkUtils.ask_for_confirmation("Test uploaded.",
                                 "{} - {}".format(values["component"], values["testType"]))

    def upload_avs_files(self, *args):
        """Called when upload AVS files clicked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Petal SN is empty")
            return

        def upload_file(file_path, title, desc):
            if file_path is not None:
                if not Path(file_path).exists():
                    dbGtkUtils.complain("Could not find {}".format(title))

                else:
                    try:
                        ITkDButils.create_component_attachment(self.session, SN, file_path, description=desc)

                    except Exception as e:
                        dbGtkUtils.complain("Could not Upload {}".format(desc), str(e))

        PSF = self.btnPSF.get_filename()
        upload_file(PSF, "Production File", "AVS Production file")

        FAT = self.btnFAT.get_filename()
        upload_file(FAT, "FAT file", "AVS FAT file")

    def on_check_tests(self, *args):
        """Button clicked."""
        self.check_tests(True)

    def check_tests(self, do_write=False):
        """Check whether all tests are find"""
        nbad = 0
        bad = []
        for test in self.test_list:
            values = test.values
            if not values["passed"]:
                nbad +=1
                bad.append(values["testType"])

        if nbad:
            dbGtkUtils.set_button_color(self.btn_state, "red", "white")
            self.btn_state.set_label("FAILED")
        else:
            dbGtkUtils.set_button_color(self.btn_state, "green", "white")
            self.btn_state.set_label("PASSED")

        if do_write:
            if nbad:
                self.write_message("Petal Failed:\n")
                for T in bad:
                    self.write_message("\t{}\n".format(T))
            else:
                if len(self.test_list)>0:
                    self.write_message("All tests are PASSED\n")

        return nbad

    def on_assembly(self, widget):
        """Assembly button clicked."""
        self.check_assembly(self.DESY_comp)

    def on_upload(self, widget):
        """Upload tests to DB."""
        if self.petal_core is None:
            self.query_db()
            if self.petal_core is None:
                return

        # First Visual Inspection
        for test in self.test_list:
            values = test.values
            if values["testType"] != "VISUAL_INSPECTION":
                continue
            
            self.write_message("{}\n".format(values["testType"]))
            res = ITkDButils.upload_test(self.session, values, check_runNumber=True)
            if res is not None:
                dbGtkUtils.complain("Could not upload test {}".format(values["testType"]), res)

        # Then the rest
        for test in self.test_list:
            values = test.values
            if values["testType"] == "VISUAL_INSPECTION":
                continue
            
            self.write_message("{}\n".format(values["testType"]))
            res = ITkDButils.upload_test(self.session, values, check_runNumber=True)
            if res is not None:
                dbGtkUtils.complain("Could not upload test {}".format(values["testType"]), res)


class AVSOptions:
    def __init__(self):
        self.PS = None
        self.FAT = None
        self.SN = None

def main():
    """The main entry."""
    # Parse command line options
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--SN", dest="SN", type=str, default=None,
                        help="Module serial number")
    parser.add_argument("--PS", dest="PS", type=str, default=None,
                        help="Produc tion Sheet file")
    parser.add_argument("--FAT", dest="FAT", type=str, default=None,
                        help="FAT file")

    options = parser.parse_args()

    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    session = dlg.get_client()

    # Start the Application
    win = AVSPanel(session, options)
    win.show_all()
    win.set_accept_focus(True)
    win.present()
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("Arrggggg !!!")

    print("Bye !!")
    dlg.die()
    sys.exit()

if __name__ == "__main__":
    main()
