from aqt import qt 
from . import client


class Reverso(qt.QObject):
    """There willl be two instances of this class, one run from the main thread
    that gets the words from revereso and the other that adds
    the notes to the sql db and that needs to be done in the main thread.

    As connection to reverso is very fast, all this can be done from the main
    thread (that implies easier debug). I'm leaving this structure as
    it can be usefull in other similar situations
    """
    Busy = qt.pyqtSignal(bool)
    Error = qt.pyqtSignal(str)
    AuthorizationStatus = qt.pyqtSignal(bool)
    Words = qt.pyqtSignal(list)
    UpdateConfig = qt.pyqtSignal(dict)

    def __init__(self, email, password, config):
        qt.QObject.__init__(self)
        self.email = email
        self.password = password
        self.msg = ''
        self.tried_ssl_fix = False
        self.client = client.ReversoClient(email, password, config, verbose=False)

    @qt.pyqtSlot()
    def authorize(self):
        self.Busy.emit(True)
        self.AuthorizationStatus.emit(self.get_connection())
        self.Busy.emit(False)

    def get_connection(self):
        try:
            self.resp_auth = self.client.auth()
            return True
        except client.AuthenticationError as e:
            self.Error.emit(str(e))
            return False

    @qt.pyqtSlot(str, list, dict)
    def get_words_to_add(self, status, wordsets, config):
        self.Busy.emit(True)
        words = self.client.get_words(config)
        self.Words.emit(words)
        self.Busy.emit(False)
        self.UpdateConfig.emit(self.client.config)

