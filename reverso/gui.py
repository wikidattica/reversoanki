import platform as pm

from aqt import mw
from aqt.utils import showInfo
from PyQt5 import QtCore, QtGui, QtWidgets
from aqt import qt
# TODO: change to:  import connect as connector
from . import connect
from . import utils
from anki.lang import _
from ._name import ADDON_NAME
from ._version import VERSION


CurrentDeckMessage = _("""\
Your current preference doesn't allow to choose the target deck.
You may prefere to set it to: '%s'
""")


class PluginWindow(qt.QDialog):
    Authorize = qt.pyqtSignal()
    RequestWords = qt.pyqtSignal(str, list, dict)
    CheckVersion = qt.pyqtSignal()
    StartDownload = qt.pyqtSignal(list)

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent)
        #self.resize(400,600)
        self.setMaximumSize(QtCore.QSize(400, 16777215))
        self.config = utils.get_config()
        self.is_active_download = False
        self.is_active_connection = False

        # Initialize UI
        ###############
        title = 'Import from Reverso (version {})'.format(VERSION)
        self.setWindowTitle(title)
        if pm.system() == 'Windows':
            self.setWindowIcon(qt.QIcon(utils.get_icon_path('favicon.ico')))

        login_layout = self.layout_login()
        import_layout = self.layout_import_preferences()
        deck_and_card_layout = self.layout_deck_and_card_preferences()
        actions_layout = self.layout_actions()

        # Main layout
        main_layout = qt.QVBoxLayout()
        # Add layouts to main layout
        main_layout.addLayout(login_layout)
        main_layout.addLayout(import_layout)
        main_layout.addLayout(deck_and_card_layout)
        main_layout.addLayout(actions_layout)
        # Set main layout
        self.setLayout(main_layout)

        # Disable buttons and hide progress bar
        self.progressBar.hide()

        # self.check_new_verson_availability
        self.check_deck_preferencies()
        self.update_gui_from_config()
        self.show()

    def add_frame_with_label(self, label):
        layout = qt.QVBoxLayout()
        label = qt.QLabel(label)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)
        frame = qt.QFrame()
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        layout.addWidget(label)
        layout.addWidget(frame)
        return layout, frame

    def layout_login(self):
        layout, frame = self.add_frame_with_label(_('Reverso credentials'))
        login_form = qt.QFormLayout(frame)
        loginLabel = qt.QLabel(_('Login:'))
        self.loginField = qt.QLineEdit()
        passLabel = qt.QLabel(_('Password:'))
        self.passField = qt.QLineEdit()
        self.passField.setEchoMode(qt.QLineEdit.Password)

        login_form.addRow(loginLabel, self.loginField)
        login_form.addRow(passLabel, self.passField)
        return layout

    def layout_import_preferences(self):

        layout, frame = self.add_frame_with_label(_('Import preferences'))
        form = qt.QFormLayout(frame)

        self.radioButtNewWords = qt.QRadioButton(_("After last imported word"))
        self.radioButtNewWords.setChecked(True)

        lastWordLabel = qt.QLabel(_('Last imported from history:'))
        self.radioButtAllWords = qt.QRadioButton(_("Any"))
        self.radioButtAllWords.toggled.connect(self.toggle_all_vs_new)

        self.lastWordField = qt.QLineEdit()
        lastWordFavouritesLabel = qt.QLabel(_('Last imported from favourites:'))
        self.lastWordFavouritesField = qt.QLineEdit()

        self.all_new_group = qt.QButtonGroup()
        self.all_new_group.addButton(self.radioButtAllWords, 0)
        self.all_new_group.addButton(self.radioButtNewWords, 1)

        self.radioButtHistory = qt.QRadioButton(_('History'))
        self.radioButtHistory.setChecked(True)
        self.radioButtFavourites = qt.QRadioButton(_('Favourites'))
        self.radioButtFavourites.setChecked(False)
        self.radioButtFavourites.toggled.connect(self.toggle_history_vs_favourites)

        self.hist_favourites_group = qt.QButtonGroup()
        self.hist_favourites_group.addButton(self.radioButtHistory, 0)
        self.hist_favourites_group.addButton(self.radioButtFavourites, 1)

        form.addRow(self.radioButtHistory, self.radioButtFavourites)
        form.addRow(self.radioButtNewWords, self.radioButtAllWords)
        form.addRow(lastWordLabel, self.lastWordField)
        form.addRow(lastWordFavouritesLabel, self.lastWordFavouritesField)

        return layout

    def layout_deck_and_card_preferences(self):

        layout, frame = self.add_frame_with_label(_('Card and deck preferences'))
        form = qt.QFormLayout(frame)
        deckLabel = qt.QLabel('Deck name:')
        self.deckField = qt.QComboBox()
        self.deckField.setEditable(False)
        self.deckField.addItems(mw.col.decks.allNames())

        self.checkBoxReversed = qt.QCheckBox(_('Create also reversed cards'))
        self.checkBoxReversed.setChecked(True)
        self.checkBoxReversed.toggled.connect(self.on_reversed_toggle)
        form.addRow(deckLabel, self.deckField)
        form.addRow(self.checkBoxReversed)

        return layout

    def layout_actions(self):
        layout = qt.QFormLayout()
        # Progress label and progress bar layout
        self.progressLabel = qt.QLabel('')
        self.progressBar = qt.QProgressBar()
        layout.addRow(self.progressLabel, self.progressBar)
        progress_layout = qt.QHBoxLayout()
        progress_layout.addWidget(self.progressLabel)
        progress_layout.addWidget(self.progressBar)

        # Horizontal layout for import and exit buttons
        buttons_layout = qt.QHBoxLayout()
        self.importAllButton = qt.QPushButton("Import words")
        self.importAllButton.clicked.connect(self.importAllButtonClicked)
        self.exitButton = qt.QPushButton(_("Close"))
        self.exitButton.clicked.connect(self.close)
        buttons_layout.addWidget(self.importAllButton)
        buttons_layout.addWidget(self.exitButton)
        layout.addRow(buttons_layout)
        return layout

    def update_gui_from_config(self):

        if 'last_imported_from_history' in self.config:
            self.lastWordField.setText(self.config['last_imported_from_history'])

        if 'last_imported_from_favourites' in self.config:
            self.lastWordFavouritesField.setText(self.config['last_imported_from_favourites'])

        if 'deck_name' in self.config: # set default for deck_name
            idx = self.deckField.findText(self.config['deck_name'])
            self.deckField.setCurrentIndex(idx)

        if 'import_source' in self.config:
            self.radioButtFavourites.setChecked(self.config['import_source'] == 'favourites')

        if 'reversed' in self.config:
            self.checkBoxReversed.setChecked(self.config['reversed'])

        if 'import_only_new_words' in self.config:
            self.radioButtNewWords.setChecked(self.config['import_only_new_words'])

        self.loginField.setText(self.config['email'])
        self.passField.setText(self.config['password'])
        self.toggle_history_vs_favourites()
        self.toggle_all_vs_new()
        self.on_reversed_toggle()

# Button clicks handlers and overridden events
###################################################

    def login_started(self):
        self.allow_to_close(False)
        # Read login and password
        login = self.loginField.text()
        password = self.passField.text()
        # deck = self.deckField.currentText()
        # last_imported_word = self.lastWordField.text()

        self.config['email'] = login
        self.config['password'] = password

        self.create_reverso_object(login, password, self.config)
        self.Authorize.emit()
        print('Connecting to reverso')
        self.show_progress_bar(True, 'Connecting to Reverso...')
        # Disable login button and fields
        mw.addonManager.writeConfig(__name__, self.config)

    def check_new_verson_availability(self):
        # Check for new version on disk and on github
        message = utils.get_version_update_notification(VERSION)
        if message:
            showInfo(message)
            self.setWindowTitle(message)
        # elif self.config['check_for_new_version']:
        #     self.CheckVersion.emit()

    def check_deck_preferencies(self):
        if not mw.col.conf.get('addToCur'):
            showInfo(CurrentDeckMessage % _('When adding, default to current deck'))
            self.deckField.setEnabled(False)

    def importAllButtonClicked(self):
        self.login_started()

    def reject(self):
        """
        Override reject event to handle Escape key press correctly
        """
        self.close()

    def closeEvent(self, event):
        """
        Override close event to safely close add-on window
        """
        self.update_config({})

        if hasattr(self, 'reverso_thread'):
            self.stop_thread(self.reverso_thread)
        if hasattr(self, 'download_thread'):
            self.stop_thread(self.download_thread)

        # Delete attribute before closing to allow running the add-on again
        if hasattr(mw, ADDON_NAME):
            delattr(mw, ADDON_NAME)
        mw.reset()

    def stop_thread(self, thread):
        thread.quit()
        # Wait 5 seconds for thread to quit and terminate if needed
        if not thread.wait(5000):
            thread.terminate()

    @qt.pyqtSlot(dict)
    def update_config(self, config):

        if config:  # signal from ReversoClient
            self.config.update(config)
            if 'last_imported_from_history' in config:
                self.lastWordField.setText(config['last_imported_from_history'])
            if 'last_imported_from_favourites' in config:
                self.lastWordFavouritesField.setText(config['last_imported_from_favourites'])
        else:  # from closeEvent
            self.config['deck_name'] = self.deckField.currentText()
            if self.lastWordField.text():
                self.config['last_imported_from_history'] = self.lastWordField.text()
                self.config['last_imported_from_favourites'] = self.lastWordFavouritesField.text()
                self.config['import_source'] = 'history' if self.radioButtHistory.isChecked() else 'favourites'
        mw.addonManager.writeConfig(__name__, self.config)

    def toggle_history_vs_favourites(self):

        target_is_history = self.radioButtHistory.isChecked()
        only_new = self.radioButtNewWords.isChecked()

        self.config['import_source'] = 'history' if target_is_history else 'favourites'
        if target_is_history:
            self.lastWordFavouritesField.setEnabled(False)
            self.lastWordField.setEnabled(only_new)
        else:
            self.lastWordField.setEnabled(False)
            self.lastWordFavouritesField.setEnabled(only_new)

    def toggle_all_vs_new(self):
        self.toggle_history_vs_favourites()
        status = self.radioButtNewWords.isChecked()
        self.config['import_only_new_words'] = status

    def on_reversed_toggle(self):
        self.config['create_reversed'] = self.checkBoxReversed.isChecked()

# Functions for connecting to Reverso and downloading words
###########################################################
    def create_reverso_object(self, login, password, cookies_path=None):
        """
        Creates reverso object and moves it to the designated thread
        or disconnects existing object and creates a new one
        """
        if not hasattr(self, 'reverso_thread'):
            self.reverso_thread = qt.QThread()
            self.reverso_thread.start()
        else:
            # Disconnect signals from slots
            self.reverso_thread.reverso.Error.disconnect(self.showErrorMessage)
            self.Authorize.disconnect(self.reverso_thread.reverso.authorize)
            self.reverso_thread.reverso.AuthorizationStatus.disconnect(self.process_authorization)
            self.reverso_thread.reverso.Words.disconnect(self.download_words)
            self.reverso_thread.reverso.Busy.disconnect(self.set_busy_connecting)
            self.RequestWords.disconnect(self.reverso_thread.reverso.get_words_to_add)
            # Delete previous Reverso object
            # TODO: Investigate if it should be done differently
            self.reverso_thread.reverso.deleteLater()
        reverso = connect.Reverso(login, password, self.config)
        # reverso import stay in this main thread so sqlite is happy, doesn't need to authenticate
        self.reverso_import = connect.Reverso(login, password, self.config)
        reverso.UpdateConfig.connect(self.update_config)
        ## Reverso is very fast so that use of a separate thread is not really necessary
        ## Debugg is way easier in a single thread with vscode.
        reverso.moveToThread(self.reverso_thread)
        reverso.Error.connect(self.showErrorMessage)
        self.Authorize.connect(reverso.authorize)
        reverso.AuthorizationStatus.connect(self.process_authorization)
        reverso.Words.connect(self.download_words)
        reverso.Busy.connect(self.set_busy_connecting)
        self.RequestWords.connect(reverso.get_words_to_add)
        self.reverso_thread.reverso = reverso

    @qt.pyqtSlot(bool)
    def process_authorization(self, status):
        if status:
            self.request_words([], self.last_imported_from_history, self.last_imported_from_favourites)
        else:
            self.allow_to_close(True)
        #self.show_progress_bar(False, '')

    @property
    def last_imported_from_history(self):
        if self.radioButtNewWords.isChecked():
            return self.lastWordField.text()
        return ''

    @property
    def last_imported_from_favourites(self):
        if self.radioButtNewWords.isChecked():
            return self.lastWordFavouritesField.text()
        return ''

    @qt.pyqtSlot(list)
    def request_words(self, words, last_word_from_history, last_word_from_favourites):

        self.activate_addon_window()
        status = self.get_progress_status()
        self.config['last_imported_from_history'] = self.last_imported_from_history
        self.config['last_imported_from_favourites'] = self.last_imported_from_favourites
        self.RequestWords.emit(status, words, self.config)
        self.show_progress_bar(True, 'Requesting list of words...')

    @qt.pyqtSlot(list)
    def download_words(self, words):
        self.reverso_import.client.import_data(words, deck_name=self.deckField.currentText())
        self.show_progress_bar(True, 'Found {} words'.format(len(words)))
        self.update_window()
        if not words:
            progress = self.get_progress_status()
            msg = 'No %s words to download' % progress if progress != 'all' else 'No words to download'
            showInfo(msg)
            #self.show_progress_bar(False, '')
            self.allow_to_close(True)
            self.activate_addon_window()
        self.download_finished(len(words))

    def filter_words(self, words):
        """
        Eliminates unnecessary to download words.
        We have to do it in main thread to query database for duplicates
        """
        if not words:
            return None
        # Exclude duplicates
        words = [word for word in words if not utils.is_duplicate(word.get('wordValue'))]
        return words

    def download_finished(self, final_count):
        if final_count > 0:
            mess = 'words have' if final_count != 1 else 'word has'
            showInfo("{} {} been imported".format(final_count, mess))
        self.show_progress_bar(False, '')
        mw.reset()

    def add_word(self, word):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread
        """
        utils.add_word(word, self.model)

    @qt.pyqtSlot(bool)
    def set_busy_download(self, status):
        """
        When downloading media for words
        """
        self.is_active_download = status

    @qt.pyqtSlot(bool)
    def set_busy_connecting(self, status):
        """
        When connecting to Reverso for authorization or requesting list of words or wordsets
        """
        self.is_active_connection = status
        # if not status:
        #     self.show_progress_bar(False, '')

# UI helpers
#####################################
    def show_progress_bar(self, mode, label, max_range=0):
        if mode:
            self.progressBar.setRange(0, max_range)
            self.progressBar.setValue(0)  # is it required?
            self.progressBar.show()
        else:
            self.progressBar.hide()
            
        self.progressLabel.setText(label)

    def showErrorMessage(self, msg):
        showInfo(msg)
        mw.reset()

    def update_window(self):
        """
        Update window by repainting and processing the events
        It's not recommended to call self.repaint() directly,
        but at least on MacOS Anki 2.1.16 doesn't update widget's
        window for several seconds even when self.update() is called
        TODO: Remove when it works as expected or repaint for Mac only
        """
        self.repaint()  # self.update()
        mw.app.processEvents()

    def get_progress_status(self):
        progress = 'all'
        if self.radioButtNewWords.isChecked():
            progress = 'new'
        return progress

    def set_login_form_enabled(self, mode):
        """
        Set login elements either enabled or disabled
        :param mode: bool
        """
        self.loginField.setEnabled(mode)
        self.passField.setEnabled(mode)
        self.update_window()

    def activate_addon_window(self, optional=True):
        addon_window = getattr(mw, ADDON_NAME, None)
        if addon_window:
            addon_window.activateWindow()
            addon_window.raise_()

    def allow_to_close(self, flag):
        """
        Sets attribute 'silentlyClose' to allow Anki's main window
        to automatically close add-on windows on exit
        :param flag: bool
        """
        if flag:
            setattr(self, 'silentlyClose', 1)
        elif hasattr(self, 'silentlyClose'):
            delattr(self, 'silentlyClose')


