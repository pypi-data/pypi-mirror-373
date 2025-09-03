"""Dialog to get DESY IRB files."""
from pathlib import Path
import itkdb_gtk
import itkdb_gtk.dbGtkUtils

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class DesyData(Gtk.Dialog):
    """To get DESY data"""

    def __init__(self, files=None):
        super().__init__(title="DESY IRB files")

        self.front = None
        self.back = None

        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK)

        area = self.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.pack_start(box, True, True, 10)

        lbl = Gtk.Label(label="Choose the IRB files.")
        box.pack_start(lbl, True, True, 10)

        grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        box.pack_start(grid, True, True, 10)
        grid.attach(Gtk.Label(label="Front"), 0, 0, 1, 1)
        grid.attach(Gtk.Label(label="Back"), 0, 1, 1, 1)

        fback = Gtk.FileChooserButton()
        fback.connect("file-set", self.on_file_set, 0)
        ffront = Gtk.FileChooserButton()
        ffront.connect("file-set", self.on_file_set, 1)
        grid.attach(ffront, 1, 0, 1, 1)
        grid.attach(fback, 1, 1, 1, 1)
        
        if files is not None and len(files)==2:
            ffront.set_file(Gio.File.new_for_path(files[0]))
            fback.set_file(Gio.File.new_for_path(files[1]))

    def on_file_set(self, *args):
        """Get back side file."""
        fnam = args[0].get_filename()
        if fnam is None or not Path(fnam).exists():
            itkdb_gtk.dbGtkUtils.complain("Could not find Data File", fnam, parent=self)
            return

        if args[1] == 0:
            self.back = fnam
        elif args[1] == 1:
            self.front = fnam
        else:
            itkdb_gtk.dbGtkUtils.complain("This should not happen.", fnam, parent=self)
