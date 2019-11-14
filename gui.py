
# -*- mode: python ; coding: utf-8 -*-
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html
"""
Anki2 add-on to download card's fields with audio from Cambridge Dictionary

"""

import os
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import * 
#QAction, QMenu, QDialog, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QDialogButtonBox, QCheckBox, QMessageBox


from aqt import mw
from aqt.utils import tooltip
from anki.hooks import addHook

from .processors import processor
from .Cambridge import CDDownloader

from ._names import *
from .utils import *

CREATE_NEW_NOTE_SHORTCUT = "t"
icons_dir = os.path.join(mw.pm.addonFolder(), 'downloadaudio', 'icons')


#from .download_entry import DownloadEntry, Action
#from .get_fields import get_note_fields, get_side_fields
#from .language import language_code_from_card, language_code_from_editor
#from .review_gui import review_entries
#from .update_gui import update_data
# DOWNLOAD_SIDE_SHORTCUT = "t"
# DOWNLOAD_MANUAL_SHORTCUT = "Ctrl+t"
# Place were we keep our megaphone icon.

class LinkDialogue(QDialog):
    """
    A Dialog to let the user edit the texts or change the language.
    """
    def __init__(self, parent=None):
        self.user_url = ''
        self.word = ''
        self.cd = CDDownloader
        QDialog.__init__(self)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(_(u'Anki – Download definitions'))
        self.setWindowIcon(QIcon(":/icons/anki.png"))
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
        #if not link:
        #    QMessageBox.warning(mw,'Link is not provided','Please, provide a link for you word or phrase.')
        #    return

        #cd = CambDownloader()
        #cd.user_url = link
        #cd.get_word_data()
        word = 'draw'
        word_data = []
        l1_word = {}
        l1_word['word_title'] = 'draw'
        l1_word['word_gram'] = 'verb'
        l1_word['word_pro_uk'] = 'Br draw'
        l1_word['word_uk_media'] = 'Br mp3'
        l1_word['word_pro_us'] = 'US draw'
        l1_word['word_us_media'] = 'US mp3'
    
        l2_word = {}
        l2_meanings = {}
        l2_meanings['to make a picture of something or someone with a pencil or pen:'] = ['Jonathan can draw very well.',
                                                                                          'The children drew pictures of their families.',
                                                                                          'Draw a line at the bottom of the page.']
        l2_word['draw verb (PICTURE)'] = l2_meanings

        l2_meanings = {}
        l2_meanings['to take something out of a container or your pocket, especially a weapon:'] = ['Suddenly he drew a gun/knife and held it to my throat.']
        l2_meanings['to cause a substance, especially blood, to come out of a body:'] = ['He bit me so hard that it drew blood.']
        l2_word['draw verb (TAKE OUT)'] = l2_meanings
        l1_word['meanings'] = l2_word
        word_data.append(l1_word)

        l1_word = {}
        l1_word['word_title'] = 'draw'
        l1_word['word_gram'] = 'noun'
        l1_word['word_pro_uk'] = 'Br draw'
        l1_word['word_uk_media'] = 'Br mp3'
        l1_word['word_pro_us'] = 'US draw'
        l1_word['word_us_media'] = 'US mp3'
    
        l2_word = {}
        l2_meanings = {}
        l2_meanings['someone or something that a lot of people are interested in:'] = ['We need someone at the event who''ll be a big draw and attract the paying public.']
        l2_word['draw noun (ATTRACTION)'] = l2_meanings

        l1_word['meanings'] = l2_word
        word_data.append(l1_word)

        sd = WordDefDialogue(word_data,word)
        self.close()
        sd.exec_()

class WordDefDialogue(QDialog):
    """
    A Dialog to let the user edit the texts or change the language.
    """
    def __init__(self,word_data,word):
        self.word_data = word_data
        self.word = word
        self.selected_defs = [] # list of selected defs (l1_word)
        self.cd = CDDownloader()
        self.set_model()
        QDialog.__init__(self)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(self.word)
        self.setWindowIcon(QIcon(":/icons/anki.png"))
        layout = QVBoxLayout()
        self.setLayout(layout)   
        # Looping through data structure 
        for l1_word in self.word_data:
            row = 0
            gl = QGridLayout()
            gr = QGroupBox()
            gr.setLayout(gl)
            word_title = QLabel('<h3>'+l1_word['word_title']+'</h3>')
            gl.addWidget(word_title,row,0)
            word_gram = QLabel('<h4>'+l1_word['word_gram']+'</h4>')
            gl.addWidget(word_gram,row,1)
            #Looping through top-level meaning
            ck_it = 0
            self.ck_dict = {}
            for l2_meaning, l2_def_and_example in l1_word['meanings'].items():
                row += 1
                mean_checkbox = QCheckBox(l2_meaning)
                mean_checkbox.l2_meaning = l2_meaning
                mean_checkbox.stateChanged.connect(self.toggle_def)
                ck_it += 1
                gl.addWidget(mean_checkbox, row, 0,1,-1)
                for l2_def in l2_def_and_example:
                    row += 1
                    l2_def_check = QLabel(l2_def)
                    gl.addWidget(l2_def_check, row, 0,1,-1)
                    for l2_examp in l2_def_and_example[l2_def]:
                        row += 1
                        l2_def_label = QLabel('<i>'+l2_examp+'</i>')
                        l2_def_label.setIndent(10)
                        gl.addWidget(l2_def_label, row, 0,1,-1)
            layout.addWidget(gr)
        #edit_word_head.setText(_('''<h4>Enter link for parsing</h4>'''))
        #bold_font = QFont()
        #bold_font.setBold(True)
        #edit_word_head.setFont(bold_font)
        #layout.addWidget(edit_word_head)
        
        #link_editor = QLineEdit()
        #link_editor.placeholderText = 'Enter your link here'
        #layout.addWidget(link_editor)
        #self.user_url = link_editor.text

        dialog_buttons = QDialogButtonBox(self)
        dialog_buttons.addButton(QDialogButtonBox.Cancel)
        dialog_buttons.addButton(QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.create_selected_notes)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

    def toggle_def(self,state):
        sender = self.sender()
        l2_meaning  = sender.l2_meaning
        if self.sender():
            if l2_meaning in self.selected_defs:
                self.selected_defs.remove(l2_meaning)
            else:
                self.selected_defs.append(l2_meaning)

    def create_selected_notes(self):

        word_to_add = self.word_data
        for next_def in self.selected_defs:
            for l1_word in self.word_data:
                for l2_key, l2_value in l1_word['meanings'].items():
                    if l2_key == next_def:
                        for l3_specific_def, l3_examples in l2_value.items():
                            word_to_save = {}
                            word_to_save['word_title']      = l1_word['word_title']
                            word_to_save['word_gram']       = l1_word['word_gram']
                            word_to_save['word_pro_uk']     = l1_word['word_pro_uk']
                            word_to_save['word_uk_media']   = l1_word['word_uk_media']
                            word_to_save['word_pro_us']     = l1_word['word_pro_us']
                            word_to_save['word_us_media']   = l1_word['word_us_media']
                            word_to_save['word_general']    = l2_key
                            word_to_save['word_specific']   = l3_specific_def
                            word_to_save['word_examples']   = list(l3_examples)
                            self.add_note(word_to_save)
                            #QMessageBox.information(mw,'Word added',str(word_to_save))
        #for sel_def in self.selected_defs:
        #    if self.word_data[sel_def]:
        self.close()
        
       
    def set_model(self):
        self.model = prepare_model(mw.col, fields, styles.model_css)

    def add_note(self, word_to_add):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread

        'word_title'
        'word_gram'
        'word_pro_uk'
        'word_uk_media'
        'word_pro_us'
        'word_us_media'
        'word_general'
        'word_specific'
        'word_examples'
        
        """

        word = {}
        word['Word'] = word_to_add['word_title']
        word['Grammar'] = word_to_add['word_gram']
        word['Pronunciation'] = word_to_add['word_pro_uk'] +' '+ word_to_add['word_pro_us']
        word['Meaning'] = word_to_add['word_general']
        word['Definition'] = word_to_add['word_specific']
        word['Examples'] = word_to_add['word_examples']
        word['Audio'] = None
        word['Picture'] = None

        add_word(word, self.model)


