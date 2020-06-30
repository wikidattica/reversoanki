# import the main window object (mw) from aqt
from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo
from anki.hooks import addHook
from aqt.utils import tooltip
from anki.lang import _

from . import gui
from . import utils
from ._name import ADDON_NAME
from ._version import VERSION

def activate():
    # Not to run multiple copies of a plugin window,
    # we create an attribute in the mw object
    if hasattr(mw, ADDON_NAME):
        addon_window = getattr(mw, ADDON_NAME, None)
        addon_window.activateWindow()
        addon_window.raise_()
    else:
        config = utils.get_config()
        if config:
            window = gui.PluginWindow(mw)
            setattr(mw, ADDON_NAME, window)
            window.exec_()
        else:
            showInfo("Unable to load config. Make sure that config.json "
                     "is present and not in use by other applications")



addHook("browser.setupMenus", utils.setupMenu)
addHook("browser.onContextMenu", utils.setupMenu)
# create a new menu item
action = QAction(f"Import from Reverso - v{VERSION}", mw)
# set it to call a function when it's clicked
action.triggered.connect(activate)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
