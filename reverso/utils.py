import os
import json

from aqt import mw
from aqt.utils import tooltip
from ._version import VERSION
from anki.lang import _
from anki.utils import pointVersion
from aqt.operations import CollectionOp
from anki.collection import OpChangesWithCount

def get_config():
    # Load config from config.json file
    if getattr(getattr(mw, "addonManager", None), "getConfig", None):
        config = mw.addonManager.getConfig(get_module_name())
    else:
        try:
            config_file = os.path.join(get_addon_dir(), 'config.json')
            with open(config_file, 'r') as f:
                config = json.loads(f.read())
        except IOError:
            config = None
    return config


def get_addon_dir():
    root = mw.pm.addonFolder()
    addon_dir = os.path.join(root, get_module_name())
    return addon_dir


def get_version_update_notification(version_in_memory):
    """
    When a user updates add-on using Anki's built-in add-on manager,
    they need to restart Anki for changes to take effect.
    Loads add-on version from the file and compares with one in the memory.
    If they differ, notify user to restart Anki.
    :return: str with notification message or None
    """
    version_file = os.path.join(get_addon_dir(), '_version.py')
    with open(version_file, 'r') as f:
        if is_newer_version_available(f):
            return 'Please restart Anki to finish updating the Add-on'
    return None


def is_newer_version_available(lines):
    version_prefix = 'VERSION = '
    for line in lines:
        if line.startswith(version_prefix):
            version_in_file = line.split('\'')[-2]
            if version_in_file != VERSION:
                return True
    return False


def setReverseField(browser, nids):

    mw = browser.mw
    optional_anki_reverse_name = _("Add Reverse")

    def op(col):
        notes = []
        for nid in nids:
            note = col.get_note(nid)
            if 'reverse' in note and not note['reverse']:
                note['reverse'] = "1"
                notes.append(note)
            if optional_anki_reverse_name in note and not note[optional_anki_reverse_name]:
                note[optional_anki_reverse_name] = "1"
                if note not in notes:
                    notes.append(note)

        return OpChangesWithCount(changes=col.update_notes(notes), count=len(notes))

    def success(changes):
        if pointVersion() < 50:
            mw.progress.finish()
        if changes.count:
            tooltip("<b>Added</b> {0} reversed cards.".format(changes.count), parent=browser)
        else:
            msg = "No card found to reverse.\nOnly cards with field 'reverse' or '{}' are looked for"
            tooltip(msg.format(optional_anki_reverse_name), parent=browser)

    # Seems to be required in 2.1.45 at least
    if pointVersion() < 50:
        mw.progress.start(parent=mw)
    CollectionOp(browser, op).success(success).run_in_background()

def onBatchEdit(browser):
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    setReverseField(browser, nids)


def setupMenu(browser, menu=None):
    menu = menu or browser.form.menuEdit
    menu_data = [action.text() for action in menu.actions()]
    ## Both Reverso and Fleex add-on use this function that doesn't need
    ## to be repeated
    if 'add_reverse' in menu_data:
        return
    menu.addSeparator()
    a = menu.addAction('Add reverse for selected cards...')
    a.setData('add_reverse')
    #a.setShortcut(QKeySequence("Control+Alt+1"))
    a.triggered.connect(lambda _, b=browser: onBatchEdit(b))


def get_module_name():
    return __name__.split(".")[0]
