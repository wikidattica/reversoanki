import os
import csv
import time
import tempfile

import requests
from aqt import mw, importing
from anki.importing import TextImporter
from bs4 import BeautifulSoup
from .reverso_model import ReversoModel


class ReversoClient:
    """This class should be easy to debug and run outside anki and qt5"""

    HOME_URL = 'https://account.reverso.net/Account/Login?returnUrl=https%3A%2F%2Fwww.reverso.net%2F'
    AUTH_URL = 'https://account.reverso.net/Account/Login?returnUrl=https%3A%2F%2Fcontext.reverso.net%2F&lang=en'
    HISTORY_URL = 'https://context.reverso.net/bst-web-user/user/history?start=0&length=1000&order=6'
    FAVOURITES_URL = 'https://context.reverso.net/bst-web-user/user/favourites?start=0&length=2000&order=10'
    DECK_NAME = 'Reverso'
    NOTE_NAME = 'Reverso'

    def __init__(self, username, password, config, verbose=False):
        """Create the simple client

        :param username: Reverso username
        :param password: Reverso password
        :param config: the dict saved in configuration
        :param verbose: print some debugging info
        """

        self.verbose = verbose
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.config = {
            'last_imported_from_history': '',
            'last_imported_from_favourites': '',
            'import_source': 'history', # may be 'favourites'
            'create_reversed': False,
            'import_only_new_words': True,
        }
        self.config.update(config)

        self.TMP_FILE = tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w+", prefix='reverso_', suffix=".csv", delete=False)
        self.notes = []
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

    def auth(self):
        
        headers = {
            'Content-Type': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        self.login_get_resp = self.session.get(self.HOME_URL, headers=headers)
        if self.verbose:
            print(f'GET Home resp {self.login_get_resp.status_code}')
        headers_post = {**headers, 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'Email': self.username,
            'Password': self.password,
            '__RequestVerificationToken': self.get_request_verification_token(self.login_get_resp.text)
        }
        self.auth_resp = self.session.post(
            self.AUTH_URL, data=data, headers=headers_post, allow_redirects=False)

        if self.verbose:
            print(f'POST AUTH resp {self.auth_resp.status_code}')
            print('AUTH Cookies', self.session.cookies.keys())

    def get_request_verification_token(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.select_one('form#account')
        __RequestVerificationToken = form.find('input', type="hidden").get('value')
        if self.verbose:
            print(__RequestVerificationToken)
        return __RequestVerificationToken

    def get_data_from_server(self, last_word=None, target='history'):
        """get the history(chronology) / favourites

        :param last_word: if present, filter only words after that
        :param target: history|favourites

        """
        if target == 'history':
            URL = self.HISTORY_URL
        else:
            URL = self.FAVOURITES_URL

        self.response = self.session.get(URL, headers=self.headers)
        jresp = self.response.json()
        data = jresp['results']

        skip_after = last_word if self.config['import_only_new_words'] else False
        if self.verbose:
            print(f'GET {target} resp {self.response.status_code}')

        if skip_after:

            for idx, item in enumerate(data):
                if item['srcText'] == skip_after:
                    break
            if self.verbose:
                print(f'History truncated: {skip_after} {idx} ')

            data = data[:idx]

        if not data:
            return []
        self.notes += data
        if target == 'history':
            self.config['last_imported_from_history'] = data[0]['srcText']
        else:
            self.config['last_imported_from_favourites'] = data[0]['srcText']
        if self.verbose:
            print("Target: {}: len: {}".format(target, len(self.notes)))
        return data

    def get_words(self, config=None):

        if config:
            self.config.update(config)
        self.notes = []
        if self.config['import_source'] == 'history':
            self.get_data_from_server(last_word=self.config['last_imported_from_history'], target="history")
        else:
            self.get_data_from_server(last_word=self.config['last_imported_from_favourites'], target="favourites")
        return self.notes

    def get_notes_as_csv(self):
        cols = [
            'id',
            'srcText',
            'translation',
            'context',
            'srcLang',
            'trgLang',
            'comment',
            'documentTitle',
            'document'
        ]
        writer = csv.writer(self.TMP_FILE, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for note in self.notes:
            if 'translation1' in note:
                # favourites have different syntax from history
                translation = f"{note['translation1']}\n{note['translation2']}\n{note['translation3']}"
                context = note['srcContext']
            else: 
                translation = note['trgText']
                context = note['srcSegment']

            writer.writerow([
                note['srcText'],
                translation,
                context,
                note['srcLang'],
                note['trgLang'],
                note['comment'],
                note['documentTitle'],
                note['document'],
                self.config.get('create_reversed') or '',
                note['id'],
            ])
        self.TMP_FILE.flush()

    def __repr__(self):
        n_notes = len(self.notes)
        return f'<Reverso: {n_notes} notes>'

    def get_model(self):
        model = ReversoModel(deck_name=None)
        if model.model:
            return model.model
        return model.create_model()

    def import_data(self, words=None, deck_name=None):
        self.notes = words

        if self.verbose:
            print("Import data to", deck_name or self.config['deck_name'])
        self.get_model()
        self.select_deck(deck_name or self.config.get('deck_name', 'Reverso'))
        self.get_notes_as_csv()
        #importing.importFile(mw, self.TMP_FILE.name)
        # if self.config['interactive']:
        #     mode = 'interactive'
        #     importing.importFile(mw, self.TMP_FILE.name)
        #     os.unlink(self.TMP_FILE.name)
        # else:
        #mode = 'non_interactive'
        self.import_notes()

    def select_deck(self, deck_name):
        """Select the deck in argument"""
        # we need to select the deck so that import will go there by default
        did = mw.col.decks.id(deck_name)
        mw.col.decks.select(did)
        # anki defaults to the last note type used in the selected deck
        m = mw.col.models.byName(self.NOTE_NAME)
        deck = mw.col.decks.get(did)
        ## mid? che è? che serve?
        deck['mid'] = m['id']
        mw.col.decks.save(deck)
        # and puts cards in the last deck used by the note type
        m['did'] = did

    def import_notes(self):
        """
        Implements `non_interactive` mode
        """
        if not self.notes:
            if self.verbose:
                print("Skip import as no notes present")
            return
        # deck has already been selected
        # import into the collection
        ti = TextImporter(mw.col, self.TMP_FILE.name)
        mw.reset()
        # TextImporter will update card with same srcText
        ti.initMapping()
        ti.run()
        os.unlink(self.TMP_FILE.name)

