import os
import json

from aqt import mw

from ._version import VERSION


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


def get_module_name():
    return __name__.split(".")[0]
