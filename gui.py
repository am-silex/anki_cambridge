
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
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore
from PyQt5.QtCore import (QThread, QObject, pyqtSignal)

from aqt import mw
from aqt.utils import tooltip
from anki.hooks import addHook

from .Cambridge import (CDDownloader, word_entry, wordlist_entry)

from ._names import *
from .utils import *


icons_dir = os.path.join(mw.pm.addonFolder(), ADDON_NAME, 'icons')

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
        #self.setMaximumSize(600,200)
        #scroll = QScrollArea()        
        
        #wg = QWidget()
        #wg.setLayout(layout)
        #wg.setMaximumSize(700,700)
        #scroll.setWidget(wg)
        #scroll.setParent(self)
        layout = QVBoxLayout()
        self.setLayout(layout)
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
            l2_def_check.stateChanged.connect(self.toggle_def)
            gl.addWidget(l2_def_check, row, 0,1,-1)
            self.l2_def = word_specific
            layout.addWidget(gr)

        dialog_buttons = QDialogButtonBox(self)
        dialog_buttons.addButton(QDialogButtonBox.Cancel)
        dialog_buttons.addButton(QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.create_selected_notes)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

        # Automatic add single word with single def if in add_single mode
        if len(self.word_data) == 1:
            self.selected_defs.append(self.word_data[0])
            self.create_selected_notes()
            self.single_word = True
        self.setMaximumSize(700,300)
        self.adjustSize()

    def toggle_def(self,state):
        sender = self.sender()
        word = sender.word
        if self.sender():
            if word in self.selected_defs:
                self.selected_defs.remove(word)
            else:
                self.selected_defs.append(word)

    def create_selected_notes(self):

        if not self.selected_defs:
            mw.cddownloader.clean_up()
            self.word_data = []
            self.word = None
            self.selected_defs = [] # list of selected defs (l1_word)
            return

        for word_to_save in self.selected_defs:
            #self.add_note(word_to_save)
            add_word(word_to_save, self.model)
        #word_to_add = self.word_data
        #for next_def in self.selected_defs:
        #    for l1_word in self.word_data:
        #        for l2_key, l2_value in l1_word['meanings'].items():
        #            for l3_specific_def, l3_examples in l2_value.items():
        #                if l3_specific_def == next_def:
        #                    word_to_save = {}
        #                    word_to_save['word_title'] = l1_word['word_title']
        #                    word_to_save['word_gram'] = l1_word['word_gram']
        #                    word_to_save['word_pro_uk'] = l1_word['word_pro_uk']
        #                    word_to_save['word_uk_media'] = l1_word['word_uk_media']
        #                    word_to_save['word_pro_us'] = l1_word['word_pro_us']
        #                    word_to_save['word_us_media'] = l1_word['word_us_media']
        #                    word_to_save['word_general'] = l2_key
        #                    word_to_save['word_specific'] = l3_specific_def
        #                    word_to_save['word_examples'] = "<br> ".join(l3_examples)
        #                    word_to_save['word_image'] = l1_word['word_image']
        #                    self.add_note(word_to_save)
                            
        #for sel_def in self.selected_defs:
        #    if self.word_data[sel_def]:
        #mw.cddownloader.clean_up()
        #self.close(QDialog.Accepted)
        self.deletion_mark = True
        self.done(0)
       
    def set_model(self):
        self.model = prepare_model(mw.col, fields, styles.model_css)

    def add_note(self, word_to_add):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread

        """
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
        # Some useful varibale go here
        auth_layout = QHBoxLayout()
        auth_label = QLabel()
        auth_label.setText('Auorization status:')
        auth_layout.addWidget(auth_label)
        auth_label_status = QLabel()
        auth_label_status.setText('Unknown')
        auth_layout.addWidget(auth_label_status)
        auth_btn = QPushButton()
        auth_btn.setText('Authorize via Google')
        auth_btn.clicked.connect(self.btn_auth_clicked)
        auth_layout.addWidget(auth_btn)
        layout.addLayout(auth_layout)        

        # Cookie - for semi authorization
        h_layout = QHBoxLayout()
        h_label = QLabel()
        h_label.setText('Cookie:')
        h_layout.addWidget(h_label)
        h_layout.addStretch()        
        self.ledit_cookie = QLineEdit()
        self.ledit_cookie.setText(self.config['cookie'] if self.config['cookie'] else '')
        h_layout.addWidget(self.ledit_cookie,QtCore.Qt.AlignRight)
        layout.addLayout(h_layout,QtCore.Qt.AlignTop)
        
        # Wordlist IDs
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
        QMessageBox.information(self,'Auth','Auth')

    def btn_Ok(self):
        # Fill config dict with current settings and write them to file
        self.config['cookie'] = self.ledit_cookie.text()
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

class WordListLinkDialogue(QDialog):
    """
    A Dialog to let the user enter link for word list.
    """
    def __init__(self, parent=None):
        self.user_url = ''
        QDialog.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(_(u'Anki – Word list link'))
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
        # Options
        self.ck_skip_multidef_words = QCheckBox('Skip milti-def words')
        layout.addWidget(self.ck_skip_multidef_words)

        dialog_buttons = QDialogButtonBox(self)
        dialog_buttons.addButton(QDialogButtonBox.Cancel)
        dialog_buttons.addButton(QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.parse_word_list_from_link)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)
        self.link_editor.setFocus()

    def parse_word_list_from_link(self):

        self.user_url = self.link_editor.text()
        if not self.user_url:
            QMessageBox.warning(mw,'Link is not provided','Please, provide a link for you word list')
            return

        downloader = mw.cddownloader
        downloader.clear_wordlist()
        downloader.get_all_words_in_list(self.user_url)
        all_words_in_list = downloader.wordlist
        if all_words_in_list:
            for wl_entry in all_words_in_list:
                downloader.clean_up()
                downloader.user_url = wl_entry.word_url
                downloader.word_id  = wl_entry.word_id
                downloader.get_word_defs(wl_entry.word_l2_meaning)
                if downloader.word_data:
                    sd = WordDefDialogue(downloader.word_data,downloader.word,wl_entry.word_l2_meaning)
                    if sd.single_word:
                        downloader.delete_word_from_wordlist()
                        continue
                    if self.ck_skip_multidef_words.checkState() == QtCore.Qt.Checked:
                        continue
                    sd.exec_()
                    if sd.deletion_mark:
                        downloader.delete_word_from_wordlist()
            self.close()
                        

        self.setResult(QDialog.Accepted)
        self.done(QDialog.Accepted)

class WParseSavedWL(QObject):

    def __init__(self):
        super(WParseSavedWL, self).__init__()
        self.config = get_config()
        mw.wordlist_queue = queue.Queue()
        self.collection = mw.col
        self.word_to_fetch = '0'
        self.fetched = 0

    def parse(self):

        if 'wordlist_ids' not in self.config:
            return

        t = self.thread = FetchThread(0,True)
        t._event.connect(self.onEvent)
        t._add_word_event.connect(self.on_add_word)        
        t._msg.connect(self.show_message)
        self.thread.start()
        #while not self.thread.isFinished():
        #    self.thread.wait(100)
        #    tooltip(
        #        _('Fetching is working, wait...'),
        #        parent=mw,
        #    )


    def onEvent(self, evt, *args):
        n = 1
        if evt == 'spawn_other_threads':
            self.word_to_fetch = args[0]
            for n in range(1,10):
                t = FetchThread(5)
                t._event.connect(self.onEvent)
                t._add_word_event.connect(self.on_add_word)        
                t._msg.connect(self.show_message)
                setattr(self, 'thread'+str(n), t)
                thread_to_start = getattr(self, 'thread'+str(n))
                thread_to_start.start()
                n += 1
        if evt == 'thread_finished': 
            if mw.wordlist_queue.empty():
                return
            for n in range(1,10):
                thread_to_restart = getattr(self, 'thread'+str(n), None)
                if thread_to_restart != None and thread_to_restart.isFinished():
                    thread_to_restart.start(5)

    def show_message(self, msg):
        tooltip(
                _(str(msg)),
                parent=mw,
            )

    def on_add_word(self, word_entry, wordlist_entry):
        add_word_to_collection(word_entry,self.collection)
        mw.cddownloader.delete_word_from_wordlist(wordlist_entry)
        self.fetched += 1
        tooltip(
                _(str(self.fetched) +' / '+str(self.word_to_fetch)),
                parent=mw,
            )

class FetchThread(QThread):

    _event = pyqtSignal(str, str)
    _msg = pyqtSignal(str)
    _add_word_event = pyqtSignal(word_entry, wordlist_entry)

    def __init__(self, max_words = 5, fetch_wordlist = False):
        QThread.__init__(self)
        self.config = get_config()
        self.downloader = CDDownloader()
        self.max_words = max_words
        self.fetch_wordlist = fetch_wordlist

    def run(self):
        if self.fetch_wordlist:
            self.sendMessage('Starting fetching wordlists')
            self.downloader = CDDownloader()
            self.downloader.clean_up()
            for wordlist_id in self.config['wordlist_ids']:
                self.downloader.fetch_wordlist_entries(wordlist_id)
        
            for wl_entry in self.downloader.wordlist:
                mw.wordlist_queue.put(wl_entry)
            self.fireEvent('spawn_other_threads',str(mw.wordlist_queue.qsize()))

        #self.sendMessage('Starting fetching ' + str(mw.wordlist_queue.qsize())+' entries')
        n = 0
        while n < self.max_words and  not mw.wordlist_queue.empty():
            wl_entry = mw.wordlist_queue.get()
            self.downloader.clean_up()
            self.downloader.wordlist_entry = wl_entry 
            self.downloader.user_url = wl_entry.word_url
            self.downloader.word_id  = wl_entry.word_id
            self.downloader.get_word_defs(wl_entry.definition)
            if self.downloader.word_data:
                wd_entry = self.downloader.find_word_by_definition(wl_entry.definition)
                if wd_entry != None:
                    self.addWordEvent(wd_entry, wl_entry)
            n += 1


        self.fireEvent('thread_finished')

    def fireEvent(self, evt, args=''):
        self._event.emit(evt, args)

    def sendMessage(self, msg):
        self._msg.emit(msg)

    def addWordEvent(self,wd_entry, wl_entry):
        self._add_word_event.emit(wd_entry, wl_entry)

