
# -*- mode: python ; coding: utf-8 -*-
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html
"""
Anki2 add-on to download card's fields with audio from Cambridge Dictionary

"""

import os
import time
import queue
import traceback
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore
from PyQt5.QtCore import (QThread, QObject, pyqtSignal, QUrl, Qt)
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineProfile
from PyQt5.QtNetwork import QNetworkCookie

from aqt import mw
from aqt.utils import askUserDialog, showInfo, showText, showWarning, tooltip
from anki.hooks import addHook

from .Cambridge import (CDDownloader, word_entry, wordlist_entry)
from urllib.error import *

from ._names import *
from .utils import *

#ADDON_FOLDER = addon_meta['dir_name'] if addon_metaS['dir_name'] else ''

icons_dir = os.path.join(mw.pm.addonFolder(), 'icons')

# These are classes for GUI dialogues
class LinkDialogue(QDialog):
    """
    A Dialog to let the user edit the texts or change the language.
    """
    def __init__(self, parent=None):
        self.user_url = ''
        self.word = ''
        QDialog.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(_(u'Anki – Download definitions'))
        self.setWindowIcon(QIcon(os.path.join(icons_dir, 'camb_icon.png')))
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.edit_word_head = QLabel()

        self.edit_word_head.setText(_('''<h4>Enter link for parsing</h4>'''))
        bold_font = QFont()
        bold_font.setBold(True)
        self.edit_word_head.setFont(bold_font)
        layout.addWidget(self.edit_word_head)
        
        self.link_editor = QLineEdit()
        self.link_editor.placeholderText = 'Enter your link here'
        layout.addWidget(self.link_editor)

        dialog_buttons = QDialogButtonBox(self)
        dialog_buttons.addButton(QDialogButtonBox.Cancel)
        dialog_buttons.addButton(QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.get_word_definitions_from_link)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)
        self.link_editor.setFocus()

    def get_word_definitions_from_link(self):

        self.user_url = self.link_editor.text()
        if not self.user_url:
            QMessageBox.warning(mw,'Link is not provided','Please, provide a link for you word or phrase.')
            return

        downloader = mw.cddownloader
        #downloader.clean_up()
        downloader.user_url = self.user_url
        downloader.get_word_defs()        
        self.setResult(QDialog.Accepted)
        self.done(QDialog.Accepted)

class WordDefDialogue(QDialog):
    """
    A Dialog to let the user to choose defs to be added.
    """
    def __init__(self,word_data,word,l2_meaning=None,wd_entry=None):
        self.word_data = word_data
        self.word = word
        self.selected_defs = [] # list of selected words (word_entry)
        self.deletion_mark = False
        self.l2_def = None
        self.single_word = False
        self.l2_meaning = l2_meaning
        self.set_model()
        QDialog.__init__(self)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(self.word)
        self.setWindowIcon(QIcon(os.path.join(icons_dir, 'camb_icon.png')))

        dialogLayout = QVBoxLayout(self)
        scrollArea = QScrollArea()
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        dialogLayout.addWidget(scrollArea)

        scrollAreaContent = QWidget()
        scrollArea.setWidget(scrollAreaContent)

        layout = QVBoxLayout(scrollAreaContent)

        word_specific = ''
        word_part_of_speech = ''
        word_dictionary = ''
        # Looping through data structure
        for word_el in self.word_data:            
            if word_dictionary != word_el.word_dictionary:
                row = 0
                gl = QGridLayout()
                gr = QGroupBox()
                gr.setTitle(word_el.word_dictionary)
                gr.setLayout(gl)            
                word_dictionary = word_el.word_dictionary

         
            if word_dictionary == word_el.word_dictionary and word_part_of_speech != word_el.word_part_of_speech:
                row += 1
                word_title = QLabel('<h3>' + word_el.word_title + '</h3>')
                gl.addWidget(word_title,row,0)
                word_gram = QLabel('<h4>' + word_el.word_part_of_speech + '</h4>')
                gl.addWidget(word_gram,row,1)                
                word_part_of_speech = word_el.word_part_of_speech

            row += 1
            word_specific = word_el.word_specific
            l2_def_check = QCheckBox(word_specific)
            l2_def_check.l2_def = word_specific
            l2_def_check.word = word_el
            l2_def_check.word_specific = word_specific
            l2_def_check.stateChanged.connect(self.toggle_def)
            gl.addWidget(l2_def_check, row, 0,1,-1)
            self.l2_def = word_specific
            layout.addWidget(gr)

        dialog_buttons = QDialogButtonBox(self)
        dialog_buttons.addButton(QDialogButtonBox.SaveAll)
        dialog_buttons.addButton(QDialogButtonBox.Cancel)
        dialog_buttons.addButton(QDialogButtonBox.Ok)
        dialog_buttons.button(QDialogButtonBox.Ok).clicked.connect(self.create_selected_notes)
        dialog_buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        dialog_buttons.button(QDialogButtonBox.SaveAll).clicked.connect(self.save_all)
        dialogLayout.addWidget(dialog_buttons)

        # Automatic add single word with single def if in add_single mode
        if len(self.word_data) == 1:
            self.selected_defs.append(self.word_data[0])
            self.create_selected_notes()
            self.single_word = True   
        
        scrollAreaContent.adjustSize() # required to get correct content area size
        scrollArea.verticalScrollBar().adjustSize() # required to get the correct scrollbar size
        scrollArea.setMinimumWidth(scrollAreaContent.size().width() + scrollArea.verticalScrollBar().width())
        

    def toggle_def(self,state):
        sender = self.sender()
        word_specific = sender.word_specific
        if self.sender():
            if word_specific in self.selected_defs:
                self.selected_defs.remove(word_specific)
            else:
                self.selected_defs.append(word_specific)

    def create_selected_notes(self):

        for wd_entry in self.word_data:
            for word_to_save in self.selected_defs:
                if wd_entry.word_specific == word_to_save:
                    add_word(wd_entry, self.model)
        self.accept()
       
    def set_model(self):
        self.model = prepare_model(mw.col, fields, styles.model_css)

    def add_note(self, word_to_add):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread

        """
        QMessageBox.warning(mw,'Link is not provided',str(word_to_add))
        word = {}
        word['Word'] = word_to_add['word_title'] 
        word['Grammar'] = word_to_add['word_gram']
        word['Pronunciation'] = word_to_add['word_pro_uk'] + ' ' + word_to_add['word_pro_us']
        word['Meaning'] = word_to_add['word_general'] if not 'UNDEFINED' in word_to_add['word_general'] else ''
        word['Definition'] = word_to_add['word_specific']
        word['Examples'] = word_to_add['word_examples']
        word['Sounds'] = [word_to_add['word_uk_media'],word_to_add['word_us_media']]
        word['Picture'] = word_to_add['word_image']

        add_word(word, self.model)

    def save_all(self):
        for wd_entry in self.word_data:
            add_word(wd_entry, self.model)
        self.done(0)

class AddonConfigWindow(QDialog):
    """
    A Dialog to let the user to choose defs to be added.
    """
    def __init__(self):
        self.config = get_config()
        QDialog.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Cambridge Addon Settings')
        self.setWindowIcon(QIcon(os.path.join(icons_dir, 'camb_icon.png')))
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Authorize and save cookies - Google OAuth2
        # Some useful variable go here
        auth_layout = QHBoxLayout()
        auth_label = QLabel()
        auth_label.setText('Authorization status:')
        auth_layout.addWidget(auth_label)
        auth_label_status = QLabel()
        auth_label_status.setText('<b>Singed in</b>' if self.config['cookie'] else 'Not signed in')
        auth_layout.addWidget(auth_label_status)
        auth_btn = QPushButton()
        auth_btn.setText('Sign in')
        auth_btn.clicked.connect(self.btn_auth_clicked)
        auth_layout.addWidget(auth_btn)
        layout.addLayout(auth_layout)        

        # Cookie - for semi authorization
        h_layout = QHBoxLayout()
        h_label = QLabel()
        h_label.setText('Cookie:')
        h_layout.addWidget(h_label)
        h_layout.addStretch()        
        self.editor_cookie = QLineEdit()
        self.editor_cookie.setClearButtonEnabled(True)
        self.editor_cookie.setText(self.config['cookie'] if self.config['cookie'] else '')
        h_layout.addWidget(self.editor_cookie,QtCore.Qt.AlignRight)
        layout.addLayout(h_layout, QtCore.Qt.AlignTop)

        # Pronunciation UK
        h_layout = QHBoxLayout()
        h_label = QLabel()
        h_label.setText('Pronunciation UK:')
        h_layout.addWidget(h_label)
        h_layout.addStretch()        
        self.cb_pronunciation_uk = QCheckBox()
        self.cb_pronunciation_uk.setChecked(self.config['pronunciation_uk'] if 'pronunciation_uk' in self.config else True)
        h_layout.addWidget(self.cb_pronunciation_uk,QtCore.Qt.AlignRight)
        layout.addLayout(h_layout,QtCore.Qt.AlignTop)

        # Pronunciation US
        h_layout = QHBoxLayout()
        h_label = QLabel()
        h_label.setText('Pronunciation US:')
        h_layout.addWidget(h_label)
        h_layout.addStretch()        
        self.cb_pronunciation_us = QCheckBox()
        self.cb_pronunciation_us.setChecked(self.config['pronunciation_us'] if 'pronunciation_us' in self.config else True)
        h_layout.addWidget(self.cb_pronunciation_us,QtCore.Qt.AlignRight)
        layout.addLayout(h_layout,QtCore.Qt.AlignTop)
        
        # word list IDs
        h_layout = QVBoxLayout()
        h_label = QLabel()
        #h_label.setText('Cookie:')
        #h_layout.addWidget(h_label)
        #h_layout.addStretch()        
        self.wordlist_list = QListWidget()
        if 'wordlist_ids' in self.config:
            links = self.config['wordlist_ids']
            for l in links:
                self.wordlist_list.addItem(l)
        self.wordlist_list.itemDoubleClicked.connect(self.wl_edit_row)
        h_layout.addWidget(self.wordlist_list)
        h_label = QLabel()
        h_label.setText('ID to add:')
        h_layout.addWidget(h_label)
        self.ledit_wl = QLineEdit()
        h_layout.addWidget(self.ledit_wl)
        btn_Add_WL = QPushButton()
        btn_Add_WL.setText('Add ID')
        btn_Add_WL.clicked.connect(self.wl_add)
        h_layout.addWidget(btn_Add_WL)
        layout.addLayout(h_layout,QtCore.Qt.AlignTop)

        #Find and fetch all pictures instead of links
        find_btn = QPushButton()
        find_btn.setText('Replace all URL with pictures in deck')
        find_btn.clicked.connect(self.find_and_fetch_pictures)
        layout.addWidget(find_btn)

        # Stretcher
        layout.addStretch()

        #Progress bar
        h_layout = QHBoxLayout()
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0,0,200,30)
        self.progress.visbile = False
        h_layout.addWidget(self.progress)
        layout.addLayout(h_layout)

        # Bottom buttons - Ok, Cancel
        btn_bottom_layout = QHBoxLayout()
        btn_bottom_layout.addStretch()        
        btn_Ok = QPushButton()
        btn_Ok.setText('Ok')
        btn_bottom_layout.addWidget(btn_Ok,QtCore.Qt.AlignRight)
        btn_Cancel = QPushButton()
        btn_Cancel.setText('Cancel')
        btn_bottom_layout.addWidget(btn_Cancel,QtCore.Qt.AlignRight)
        layout.addLayout(btn_bottom_layout)
        btn_Ok.clicked.connect(self.btn_Ok)
        btn_Cancel.clicked.connect(self.close)


    def find_and_fetch_pictures(self):
        self.progress.visible = True
        find_note_with_url_pictures(self)
        self.progress.visible = False
        

    def btn_auth_clicked(self):
        auth_window = WebPageView(AUTH_URL)
        auth_window.accepted.connect(self.onAuthCompleted)
        auth_window.exec()
        self.config['cookie'] = auth_window.get_cookie()
        update_config(self.config)
        self.editor_cookie.setText(self.config['cookie'] if self.config['cookie'] else '')

    def onAuthCompleted(self):
        QMessageBox.information(self, 'Singing in', 'Signed in successfully')


    def btn_Ok(self):
        # Fill config dict with current settings and write them to file
        self.config['cookie'] = self.editor_cookie.text()
        self.config['pronunciation_uk'] = self.cb_pronunciation_uk.isChecked()
        self.config['pronunciation_us'] = self.cb_pronunciation_us.isChecked()
        wl = []
        for i in self.iterAllItems(self.wordlist_list):
            wl.append(i.text())
        self.config['wordlist_ids'] = wl
        update_config(self.config)
        self.close()

    def btn_Cancel(self):
        self.close()

    def wl_add(self):
        self.wordlist_list.addItem(self.ledit_wl.text())

    def iterAllItems(self, iterable):
        for i in range(iterable.count()):
            yield iterable.item(i)

    def wl_edit_row(self):
        current_item = self.wordlist_list.currentItem()
        self.ledit_wl.setText(current_item.text())
        self.wordlist_list.takeItem(self.wordlist_list.currentRow())

class WParseSavedWL(QObject):

    instance = None

    def __init__(self):
        super(WParseSavedWL, self).__init__()
        self.config = get_config()
        self.collection = mw.col
        self.word_to_fetch = '0'
        self.fetched = 0
        self.need_to_stop = False
        self.wordlist_queue = queue.Queue()

    def __call__(self, *pargs, **kargs):
        if instance is None:
            instance=super().__call__(*args, **kw)
        return instance

    def parse(self):

        if 'wordlist_ids' not in self.config:
            return

        t = self.thread = FetchThread(0,True,self.wordlist_queue)
        t._event.connect(self.onEvent)
        t._add_word_event.connect(self.on_add_word)        
        self.thread.start()

    def onEvent(self, evt, *args):
        n = 1
        if evt == 'spawn_other_threads':
            self.word_to_fetch = args[0]
            for n in range(1,5):
                t = FetchThread(max_words = 5, fetch_wordlist = False,wordlist_queue=self.wordlist_queue)
                t._event.connect(self.onEvent)
                t._add_word_event.connect(self.on_add_word)        
                setattr(self, 'thread'+str(n), t)
                thread_to_start = getattr(self, 'thread'+str(n))
                thread_to_start.start()
                n += 1
        if evt == 'batch_completed': 
            if self.wordlist_queue.empty() or self.need_to_stop:
                return
            for n in range(1,5):
                thread_to_restart = getattr(self, 'thread'+str(n), None)
                if thread_to_restart != None and thread_to_restart.isFinished():
                    thread_to_restart.start()
        if evt == 'need_to_stop': 
            self.need_to_stop = True
            tooltip(
                _(str('Stopping all error')),
                parent=mw,
            )
        if evt == 'error': 
            self.need_to_stop = True
            showText(_("Fetching failed:\n%s") % self._rewriteError(args[0]))

        if evt == 'message': 
            tooltip(
                _(str(args[0])),
                parent=mw,
            )


    def on_add_word(self, word_entry):
        add_word_to_collection(word_entry,self.collection)
        self.fetched += 1
        tooltip(
                _(str(self.fetched) +' / '+str(self.word_to_fetch)),
                parent=mw,
            )

    def _rewriteError(self, err):
        if "Errno 61" in err:
            return _(
                """\
Couldn't connect to AnkiWeb. Please check your network connection \
and try again."""
            )
        elif "timed out" in err or "10060" in err:
            return _(
                """\
The connection to AnkiWeb timed out. Please check your network \
connection and try again."""
            )
        elif "403" in err:
            return _(
                """\
Authentication failed. Either your cookie expired or your are trying to delete entries from a community wordlist."""
            )
        elif "code: 500" in err:
            return _(
                """\
AnkiWeb encountered an error. Please try again in a few minutes, and if \
the problem persists, please file a bug report."""
            )
        elif "code: 501" in err:
            return _(
                """\
Please upgrade to the latest version of Anki."""
            )
        # 502 is technically due to the server restarting, but we reuse the
        # error message
        elif "code: 502" in err:
            return _("Cambridge Dictionary is under maintenance. Please try again in a few minutes.")
        elif "code: 503" in err:
            return _(
                """\
Cambridge Dictionary is too busy at the moment. Please try again in a few minutes."""
            )
        elif "code: 504" in err:
            return _(
                "504 gateway timeout error received. Please try temporarily disabling your antivirus."
            )
        elif "10061" in err or "10013" in err or "10053" in err:
            return _(
                "Antivirus or firewall software is preventing Anki from connecting to the internet."
            )
        elif "10054" in err or "Broken pipe" in err:
            return _(
                "Connection timed out. Either your internet connection is experiencing problems, or you have a very large file in your media folder."
            )
        elif "Unable to find the server" in err or "socket.gaierror" in err:
            return _(
                "Server not found. Either your connection is down, or antivirus/firewall "
                "software is blocking Anki from connecting to the internet."
            )
        elif "code: 407" in err:
            return _("Proxy authentication required.")
        elif "code: 413" in err:
            return _("Your collection or a media file is too large to sync.")
        elif "EOF occurred in violation of protocol" in err:
            return (
                _(
                    "Error establishing a secure connection. This is usually caused by antivirus, firewall or VPN software, or problems with your ISP."
                )
                + " (eof)"
            )
        elif "certificate verify failed" in err:
            return (
                _(
                    "Error establishing a secure connection. This is usually caused by antivirus, firewall or VPN software, or problems with your ISP."
                )
                + " (invalid cert)"
            )
        return err

class FetchThread(QThread):

    _event = pyqtSignal(str, str)
    _add_word_event = pyqtSignal(word_entry)

    def __init__(self, max_words = 5, fetch_wordlist = False,wordlist_queue=None):
        QThread.__init__(self)
        self.config = get_config()
        self.downloader = CDDownloader()
        self.max_words = max_words
        self.fetch_wordlist = fetch_wordlist
        self.wordlist_queue = wordlist_queue

    def run(self):
        if self.wordlist_queue == None:
            return
        try:
            if self.fetch_wordlist:
                self._fetch_wordlist()
                self.fireEvent('spawn_other_threads',str(self.wordlist_queue.qsize()))
                return
        except :
            err = traceback.format_exc()
            self.fireEvent("error", err)
            return

        try:
            self._fetch_words()
            self.fireEvent('batch_completed')
        except :
            err = traceback.format_exc()
            self.fireEvent("error", err)
            return       
        

    def fireEvent(self, evt, args=''):
        #
        self._event.emit(evt, args)

    def addWordEvent(self,wd_entry):

        self._add_word_event.emit(wd_entry)

    def _fetch_wordlist(self):
        self.fireEvent('message','Starting fetching wordlists')
        self.downloader = CDDownloader()
        self.downloader.clean_up()
        for wordlist_id in self.config['wordlist_ids']:
            self.downloader.fetch_wordlist_entries(wordlist_id)
        
        for wl_entry in self.downloader.wordlist:
            self.wordlist_queue.put(wl_entry)

    def _fetch_words(self):
        n = 0
        while n < self.max_words and  not self.wordlist_queue.empty():
            wl_entry = self.wordlist_queue.get()
            self.downloader.clean_up()
            self.downloader.wordlist_entry = wl_entry 
            self.downloader.user_url = wl_entry.word_url
            self.downloader.word_id  = wl_entry.word_id
            self.downloader.get_word_defs()
            if self.downloader.word_data:
                wd_entry = self.downloader.find_word_by_wl_entry(wl_entry)
                if wd_entry != None:
                    self.addWordEvent(wd_entry)
                    self.downloader.delete_word_from_wordlist(wl_entry)
            n += 1

class WebPageView(QDialog):
    def __init__(self, user_url=''):
        self.user_url = user_url
        QDialog.__init__(self)
        self.webview= QWebEngineView()
        self.profile = QWebEngineProfile("storage", self.webview)
        self.cookie_store = self.profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.onCookieAdded)
        self.webpage = QWebEnginePage(self.profile, self.webview)
        self.webview.setPage(self.webpage)
        self.webview.urlChanged.connect(self.onUrlChanged)
        self.cookies = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(self.webview)
        self.webview.load(QUrl(self.user_url))
        self.webview.show()

    def onCookieAdded(self, cookie):
        for c in self.cookies:
            if c.hasSameIdentifier(cookie):
                return
        self.cookies.append(QNetworkCookie(cookie))

    def get_cookie(self):
        cookie_builder = ""
        for c in self.cookies:
            # Get cookies that domain contains cambridge.org
            if "cambridge.org" not in str(c.domain()):
                continue

            name = bytearray(c.name()).decode()
            value = bytearray(c.value()).decode()
            cookie_builder = name + "=" + value + "; " + cookie_builder
        return cookie_builder
    
    def onUrlChanged(self):
        if self.webview.url().toString() != AUTH_URL:
            self.accept()


class MyQWebEngineView(QWebEngineView):
    def __init__(self):
        QWebEngineView.__init__(self)
        self.urlChanged.connect(self.url_changed)

    def createWindow(self, type=None):
        QMessageBox.warning(mw,'Link is not provided',str(type))
        wpv = WebPageView()
        wpv.exec_()

    def url_changed(self):
        QMessageBox.warning(mw,'Link is not provided','URL changed')
