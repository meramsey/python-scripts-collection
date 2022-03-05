import os
from gi import require_version

require_version("Gtk", "3.0")
require_version("Nautilus", "3.0")

from gi.repository import Gdk, Gtk, Nautilus, GObject
from gettext import gettext, bindtextdomain, textdomain

NAUTILUS_PATH = "/usr/bin/nautilus"


class NautilusAdmin(Nautilus.MenuProvider, GObject.GObject):
    """Simple Nautilus extension that adds some file path actions to
    the right-click menu, using GNOME's new admin backend."""

    def __init__(self):
        pass

    def get_file_items(self, window, files):
        """Returns the menu items to display when one or more files/folders are
        selected."""
        # Don't show when more than 1 file is selected
        if len(files) != 1:
            return
        file = files[0]

        # Add the menu items
        items = []
        self._setup_gettext()
        self.window = window
        if file.get_uri_scheme() == "file":  # must be a local file/directory
            # if file.is_directory():
            if os.path.exists(NAUTILUS_PATH):
                items += [self._create_nautilus_item(file)]
            # else:
            #     items += [self._create_nautilus_item(file)]

        return items

    def get_background_items(self, window, file):
        """Returns the menu items to display when no file/folder is selected
        (i.e. when right-clicking the background)."""

        # Add the menu items
        items = []
        self._setup_gettext()
        self.window = window
        # if file.is_directory() and file.get_uri_scheme() == "file":
        if file.get_uri_scheme() == "file":
            if os.path.exists(NAUTILUS_PATH):
                items += [self._create_nautilus_item(file)]

        return items

    def _setup_gettext(self):
        """Initializes gettext to localize strings."""
        try:  # prevent a possible exception
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass
        bindtextdomain("nautilus-admin", "/usr/share/locale")
        textdomain("nautilus-admin")

    def _create_nautilus_item(self, file):
        item = Nautilus.MenuItem(
            name="NautilusAdmin::Nautilus",
            label=gettext("Copy path"),
            tip=gettext("Copy File path to clipboard"),
        )
        item.connect("activate", self._nautilus_run, file)
        return item

    # def _create_gedit_item(self, file):
    #     """Creates the 'Edit as Administrator' menu item."""
    #     item = Nautilus.MenuItem(name="NautilusAdmin::Nautilus",
    #                              label=gettext("Edit as A_dministrator"),
    #                              tip=gettext("Open this file in the text editor with root privileges"))
    #     item.connect("activate", self._gedit_run, file)
    #     return item

    def _nautilus_run(self, menu, file):
        """'Copy File path' menu item callback."""
        uri = file.get_uri()
        file_path = uri.replace("file://", "")
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(file_path, -1)
        clipboard.store()
