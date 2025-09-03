import time
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gio, GLib



def complain(main_title, second_text="", parent=None):
    """Open an error dialog.

    Args:
        main_title: Main text in window
        second_text: Second text
        parent: dialog parent

    """
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        flags=0,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=main_title,
    )
    dialog.format_secondary_text(second_text)
    dialog.run()
    dialog.destroy()


def ask_for_confirmation(main_title, second_text, parent=None):
    """Ask for action cofirmation.

    Args:
        main_title: Main title in the message window
        second_text: Secondary text in the message widow
        parent (optional): The parent window. Defaults to None.

    Return:
        OK: True if OK button clicked.

    """
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        flags=0,
        message_type=Gtk.MessageType.INFO,
        text=main_title
    )
    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
    dialog.format_secondary_text(second_text)
    out = dialog.run()
    dialog.destroy()
    return (out == Gtk.ResponseType.OK)


    box.pack_start(btn, True, False, 0)

    return btn


class MessagePanel(object):
    """Encapsulates a TExtView object to show messages."""

    def __init__(self, size=100):
        """Initializarion."""
        self.frame = None
        self.text_view = Gtk.TextView()
        self.textbuffer = self.text_view.get_buffer()
        self.__create_message_panel(size)

    def __create_message_panel(self, size):
        """Creates a message panel within a frame.

        Args:
            size: size of the panel

        Returns:
            Gtk.TextBuffer, Gtk.Frame
        """
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_size_request(-1, size)
        frame.add(box)

        # The title for the tet view
        box.pack_start(Gtk.Label(label="Messages"), False, True, 0)

        # A scroll window with the text view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.text_view)
        box.pack_start(scrolled, True, True, 0)
        self.frame = frame

    def scroll_to_end(self):
        """Scrolls text view to end."""
        end = self.textbuffer.get_end_iter()
        self.text_view.scroll_to_iter(end, 0, False, 0, 0)

    def write_message(self, text, write_date=True):
        """Writes text to Text Viewer."""
        nlines = self.textbuffer.get_line_count()
        if nlines > 100:
            start = self.textbuffer.get_iter_at_line(0)
            end = self.textbuffer.get_iter_at_line(75)
            self.textbuffer.delete(start, end)

        end = self.textbuffer.get_end_iter()
        if write_date:
            msg = "[{}]  {}".format(time.strftime("%d/%m/%y %T"), text)
        else:
            msg = text

        self.textbuffer.insert(end, msg)
        GLib.idle_add(self.scroll_to_end)
        
    def write(self, txt):
        """A write method."""
        self.write_message(txt, write_date=False)

