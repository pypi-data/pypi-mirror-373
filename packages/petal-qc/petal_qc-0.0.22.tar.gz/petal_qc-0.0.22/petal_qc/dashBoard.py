"""Test dashboard."""
import sys

try:
    import petal_qc

except ImportError:
    from pathlib import Path
    cwd = Path(__file__).parent
    sys.path.append(cwd.as_posix())

from petal_qc.metrology.coreMetrology import CoreMetrology, CoreMetrologyOptions
from petal_qc.thermal.coreThermal import CoreThermal
from petal_qc.thermal.IRPetalParam import IRPetalParam
from petal_qc.PetalReceptionTests import PetalReceptionTests

from itkdb_gtk import dbGtkUtils
from itkdb_gtk import ITkDBlogin

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

HELP_LINK="https://petal-qc.docs.cern.ch"

class DashWindow(dbGtkUtils.ITkDBWindow):
    """Dashboard class."""
    PETAL_CORE_METRO = 1
    PETAL_CORE_THERMAL = 2
    PETAL_RECEPTION_TEST = 3


    def __init__(self, session):
        """Initialization."""
        super().__init__(title="Petal-QC Dashboard", session=session, help_link=HELP_LINK)
        self.mask = 0

        # set border width
        self.set_border_width(10)

        # Prepare dashboard
        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 5)

        irow = 0
        lbl = Gtk.Label()
        lbl.set_markup("<b>Tests</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        btnPetalMetrology = Gtk.Button(label="Petal Core Metrology")
        btnPetalMetrology.connect("clicked", self.petal_metrology)
        grid.attach(btnPetalMetrology, 0, irow, 1, 1)

        btnPetalThermal = Gtk.Button(label="Petal Core Thermal")
        btnPetalThermal.connect("clicked", self.petal_thermal)
        grid.attach(btnPetalThermal, 1, irow, 1, 1)


        irow += 1
        btnReception = Gtk.Button(label="Reception Tests")
        btnReception.connect("clicked", self.petal_reception_test)
        grid.attach(btnReception, 0, irow, 1, 1)

        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, True, 5)

        self.show_all()

    def petal_reception_test(self, *args):
        """Do petal reception test."""
        bitn = DashWindow.PETAL_RECEPTION_TEST
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = PetalReceptionTests(
            self.session,
            help_link="{}/petalReceptionTests.html".format(HELP_LINK)
        )
        W.connect("destroy", self.app_closed, bitn)

    def petal_metrology(self, *args):
        """Do petal metrology"""
        bitn = DashWindow.PETAL_CORE_METRO
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        opts = CoreMetrologyOptions()
        W = CoreMetrology(opts, session=self.session, title="Petal Core Metrology")
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def petal_thermal(self, *args):
        """Do petal thermal."""
        bitn = DashWindow.PETAL_CORE_THERMAL
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        opt = IRPetalParam()
        opt.files = []
        opt.golden = None
        opt.folder = None
        opt.out = None
        opt.alias = None
        opt.SN = None
        opt.desy = False
        W = CoreThermal(opt, self.session, title="Petal Thermal Test.")
        W.connect("destroy", self.app_closed, bitn)
        W.show_all()

    def app_closed(self, *args):
        """Application window closed. Clear mask."""
        bt = 1 << args[1]
        self.mask &= ~bt
        # print(bt, self.mask)

def main():
    """Main entry"""
    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    dashW = DashWindow(client)
    dashW.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()
