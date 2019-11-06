
# -*- mode: python ; coding: utf-8 -*-
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html
"""
Anki2 add-on to download card's fields with audio from Cambridge Dictionary


"""

import os
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QAction, QMenu, QDialog, QVBoxLayout, QLabel, QLineEdit, QGridLayout, QDialogButtonBox, QCheckBox 


from aqt import mw
from aqt.utils import tooltip
from anki.hooks import addHook

#from .download_entry import DownloadEntry, Action
#from .get_fields import get_note_fields, get_side_fields
#from .language import language_code_from_card, language_code_from_editor
from .processors import processor
#from .review_gui import review_entries
#from .update_gui import update_data
from .Cambridge import CambDownloader
from .dispatcher import *
CREATE_NEW_NOTE_SHORTCUT = "t"
# DOWNLOAD_SIDE_SHORTCUT = "t"
# DOWNLOAD_MANUAL_SHORTCUT = "Ctrl+t"
icons_dir = os.path.join(mw.pm.addonFolder(), 'downloadaudio', 'icons')
# Place were we keep our megaphone icon.


#def do_download(note, field_data_list, language, hide_text=False):
#    """
#    Download audio data.

#    Go through the list of words and list of sites and download each
#    word from each site.  Then call a function that asks the user what
#    to do.
#    """
#    retrieved_entries = []
#    for field_data in field_data_list:
#        if field_data.empty:
#            continue
#        for dloader in downloaders:
#            # Use a public variable to set the language.
#            dloader.language = language
#            try:
#                # Make it easer inside the downloader.  If anything
#                # goes wrong, don't catch, or raise whatever you want.
#                dloader.download_files(field_data)
#            except:
#                # # Uncomment this raise while testing a new
#                # # downloaders.  Also use the “For testing”
#                # # downloaders list with your downloader in
#                # # downloaders.__init__
#                # raise
#                continue
#            retrieved_entries += dloader.downloads_list
#    # Significantly changed the logic.  Put all entries in one
#    # list, do stuff with that list of DownloadEntries.
#    for entry in retrieved_entries:
#        # Do the processing before the reviewing now.
#        entry.process()
#    try:
#        retrieved_entries = review_entries(note, retrieved_entries, hide_text)
#        # Now just the dialog, which sets the fields in the entries
#    except ValueError as ve:
#        tooltip(str(ve))
#    except RuntimeError as rte:
#        if 'cancel' in str(rte):
#            for entry in retrieved_entries:
#                entry.action = Action.Delete
#        else:
#            raise
#    for entry in retrieved_entries:
#        entry.dispatch(note)
#    if any(entry.action == Action.Add for entry in retrieved_entries):
#        note.flush()
#        # We have to do different things here, for download during
#        # review, we should reload the card and replay.  When we are in
#        # the add dialog, we do a field update there.
#        rnote = None
#        try:
#            rnote = mw.reviewer.card.note()
#        except AttributeError:
#            # Could not get the note of the reviewer's card.  Probably
#            # not reviewing at all.
#            return
#        if note == rnote:
#            # The note we have is the one we were reviewing, so,
#            # reload and replay
#            mw.reviewer.card.load()
#            mw.reviewer.replayAudio()

#def download_for_side():
#    """
#    Download audio for one side.

#    Download audio for all audio fields on the currently visible card
#    side.
#    """
#    card = mw.reviewer.card
#    if not card:
#        return
#    note = card.note()
#    field_data = get_side_fields(card, note)
#    do_download(
#        note, field_data, language_code_from_card(card), hide_text=True)

#def download_for_note(ask_user=False, note=None, editor=None):
#    """
#    Download audio for all fields.

#    Download audio for all fields of the note passed in or the current
#    note.  When ask_user is true, show a dialog that lets the user
#    modify these texts.
#    """
#    if not note:
#        try:
#            card = mw.reviewer.card
#            note = card.note()
#        except AttributeError:
#            return
#        language_code = language_code_from_card(card)
#    else:
#        language_code = language_code_from_editor(note, editor)
#    field_data = get_note_fields(note)
#    if not field_data:
#        # Complain before we show the empty dialog.
#        tooltip(u'Nothing to download.')
#        return

#    if ask_user:
#        try:
#            field_data, language_code = update_data(field_data, language_code)
#        except RuntimeError as rte:
#            if 'cancel' in str(rte):
#                # User canceled.  No need for the "Nothing downloaded"
#                # message.
#                return
#            else:
#                # Don't know how to handle this after all
#                raise
#    do_download(note, field_data, language_code)

#def download_manual():
#    u"""Do the download with the dialog before we go."""
#    download_for_note(ask_user=True)

#def download_off():
#    u"""Deactivate the download menus."""
#    mw.note_download_action.setEnabled(False)
#    mw.side_download_action.setEnabled(False)
#    mw.manual_download_action.setEnabled(False)

#def download_on():
#    u"""Activate the download menus."""
#    mw.note_download_action.setEnabled(True)
#    mw.side_download_action.setEnabled(True)
#    mw.manual_download_action.setEnabled(True)

#def editor_download_editing(self):
#    u"""Do the download when we are in the note editor."""
#    self.saveNow()
#    download_for_note(ask_user=True, note=self.note, editor=self)
#    # Fix for issue #10.
#    self.stealFocus = True
#    self.loadNote()
#    self.stealFocus = False

#def editor_add_download_editing_button(self):
#    """Add the download button to the editor"""
#    dl_button = self._addButton(
#        "download_audio",
#        lambda self=self: editor_download_editing(self),
#        tip=u"Download audio…")
#    dl_button.setIcon(
#        QIcon(os.path.join(icons_dir, 'download_note_audio.png')))


# Either reuse an edit-media sub-menu created by another add-on
# (probably the mhwave (ex sweep) add-on by Y.T.) or create that
# menu.  When we already have that menu, add a separator, otherwise
# create that menu.

# try:
#     mw.edit_media_submenu.addSeparator()
# except AttributeError:
class LinkDialogue(QDialog):
    """
    A Dialog to let the user edit the texts or change the language.
    """
    def __init__(self):
        self.user_url = ''
        self.word = ''
        QDialog.__init__(self)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(_(u'Anki – Download definitions'))
        self.setWindowIcon(QIcon(":/icons/anki.png"))
        layout = QVBoxLayout()
        self.setLayout(layout)
        edit_word_head = QLabel()

        edit_word_head.setText(_('''<h4>Enter link for parsing</h4>'''))
        bold_font = QFont()
        bold_font.setBold(True)
        edit_word_head.setFont(bold_font)
        layout.addWidget(edit_word_head)
        
        self.link_editor = QLineEdit()
        self.link_editor.placeholderText = 'Enter your link here'
        layout.addWidget(self.link_editor)

        dialog_buttons = QDialogButtonBox(self)
        dialog_buttons.addButton(QDialogButtonBox.Cancel)
        dialog_buttons.addButton(QDialogButtonBox.Ok)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

class WordDefDialogue(QDialog):
    """
    A Dialog to let the user edit the texts or change the language.
    """
    def __init__(self):
        self.word_data = []
        self.word = ''
        QDialog.__init__(self)
        self.initUI()

    def initUI(self):
        u"""Build the dialog box."""

        self.setWindowTitle(self.word)
        self.setWindowIcon(QIcon(":/icons/anki.png"))
        layout = QVBoxLayout()
        self.setLayout(layout)
        for word_entry in self.word_data:
            entry_checkbox = QCheckBox(word_entry.word_title)
        layout.addWidget(entry_checkbox)

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
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)


        # Now decide which help text to show.
        # First, decide if we have any split fields.
        #if any(f_data.split for f_data in self.field_data_list):
        #    if self.language_code and self.language_code.startswith('ja'):
        #        # Japanese
        #        edit_word_head.setText(kanji_et)
        #    else:
        #        # Chinese should not happen at the moment
        #        edit_word_head.setText(base_et)
        #else:
        #    edit_word_head.setText(single_et)


#        self.create_data_rows(layout)
#        line = QFrame(self)
#        line.setFrameShape(QFrame.HLine)
#        line.setFrameShadow(QFrame.Sunken)
#        layout.addWidget(line)
#        lcode_head = QLabel(_('''<h4>Language code</h4>'''))
#        layout.addWidget(lcode_head)
#        lang_hlayout = QHBoxLayout()
#        lc_label = QLabel(_(u'Language code:'), self)
#        lang_hlayout.addWidget(lc_label)
#        lc_label.setToolTip(language_help)
#        self.language_code_lineedit = QLineEdit(self)
#        try:
#            self.language_code_lineedit.setText(self.language_code)
#        except:
#            self.language_code_lineedit.setText(default_audio_language_code)
#        lang_hlayout.addWidget(self.language_code_lineedit)
#        self.language_code_lineedit.setToolTip(language_help)
#        layout.addLayout(lang_hlayout)
#        dialog_buttons = QDialogButtonBox(self)
#        dialog_buttons.addButton(QDialogButtonBox.Cancel)
#        dialog_buttons.addButton(QDialogButtonBox.Ok)
#        dialog_buttons.accepted.connect(self.accept)
#        dialog_buttons.rejected.connect(self.reject)
#        layout.addWidget(dialog_buttons)

#    def create_data_rows(self, layout):
#        u"""Build one line of the dialog box."""
#        gf_layout = QGridLayout()
#        for num, field_data in enumerate(self.field_data_list):
#            # We create all three QTextEdits for each item and hide
#            # some according to field_data.split.
#            label = QLabel(u'{0}:'.format(field_data.word_field_name))
#            label.setToolTip(_(u'Source of the request text'))
#            gf_layout.addWidget(label, num, 0)
#            ledit = QLineEdit(field_data.word)
#            self.word_lineedits.append(ledit)
#            try:
#                bedit = QLineEdit(field_data.kanji)
#            except AttributeError:
#                # Happens when FieldData is not a
#                # JapaneseFieldData. LBYL would be to use
#                # field_data.split
#                bedit = QLineEdit('')
#            self.kanji_lineedits.append(bedit)
#            try:
#                redit = QLineEdit(field_data.kana)
#            except AttributeError:
#                # dto.
#                redit = QLineEdit('')
#            self.kana_lineedits.append(redit)
#            if not field_data.split:
#                gf_layout.addWidget(ledit, num, 1, 1, 2)
#                ledit.setToolTip(
#                    _(u'''<h4>Text of the request.</h4>
#<p>Edit this as appropriate.  Clear it to not download anything for
#this line.</p>'''))
#                bedit.hide()
#                redit.hide()
#            else:
#                ledit.hide()
#                gf_layout.addWidget(bedit, num, 1)
#                kanji_tt_text = _(u'''\
#<h4>Kanji of the request.</h4>
#<p>Edit this as appropriate.  Clear this to not download anything for
#this line.  For pure kana words, enter (or keep) the kana
#here.</p>''')
#                base_tt_text = _(u'''\
#<h4>Expression of the request.</h4>
#<p>Edit this as appropriate. Clear this to not download anything for
#this line.</p>''')
#                # A bit C-ish. language_code may be None.
#                if self.language_code and self.language_code.startswith('ja'):
#                    bedit.setToolTip(kanji_tt_text)
#                else:
#                    bedit.setToolTip(base_tt_text)
#                gf_layout.addWidget(redit, num, 2)

#                kana_tt_text = _(u'''<h4>Kana of the request.</h4>
#<p>Edit this as appropriate.  For pure kana words, enter (or keep) the
#kana here or clear this field.</p>''')
#                ruby_tt_text = _(u'''<h4>Reading (ruby) of the request.</h4>
#<p>Edit this as appropriate.</p>''')
#                if self.language_code and self.language_code.startswith('ja'):
#                    redit.setToolTip(kana_tt_text)
#                else:
#                    redit.setToolTip(ruby_tt_text)
#        layout.addLayout(gf_layout)

   
def ask_user_for_link():
    link_dialog = LinkDialogue()
    if link_dialog.exec_():
        word_data = get_word_definitions_from_link(link_dialog.link_editor.text)
        if word_data:
            word_select = WordDefDialogue()
            word_select.word = '123'
            word_select.word_data = word_data
            word_select.exec_()
        #raise RuntimeError('User cancel')

# mw.side_download_action = QAction(mw)
# mw.side_download_action.setText(u"Side audio")
# mw.side_download_action.setIcon(
#     QIcon(os.path.join(icons_dir, 'download_side_audio.png')))
# mw.side_download_action.setToolTip(
#     "Download audio for audio fields currently visible.")
# mw.side_download_action.setShortcut(DOWNLOAD_SIDE_SHORTCUT)
# mw.side_download_action.triggered.connect(download_for_side)
#
# mw.manual_download_action = QAction(mw)
# mw.manual_download_action.setText(u"Manual audio")
# mw.manual_download_action.setIcon(
#     QIcon(os.path.join(icons_dir, 'download_audio_manual.png')))
# mw.manual_download_action.setToolTip(
#     "Download audio, editing the information first.")
# mw.manual_download_action.setShortcut(DOWNLOAD_MANUAL_SHORTCUT)
# mw.manual_download_action.triggered.connect(download_manual)

# Todo: switch off at start and on when we get to reviewing.
# # And start with the acitons off.
# download_off()

# addHook("setupEditorButtons", editor_add_download_editing_button)
# mw.note_download_action.setIcon(QIcon(os.path.join(icons_dir,
#                                                    'download_note_audio.png')))
#mw.create_notes_from_link_action.setShortcut(CREATE_NEW_NOTE_SHORTCUT)

mw.edit_cambridge_submenu = QMenu(u"&Cambridge Dictionary", mw)
mw.form.menuEdit.addSeparator()
mw.form.menuEdit.addMenu(mw.edit_cambridge_submenu)

mw.create_notes_from_link_action = QAction(mw)
mw.create_notes_from_link_action.setText("Create new note fromm link")
mw.create_notes_from_link_action.setToolTip("Fetch word definitions from provided link.")

mw.create_notes_from_link_action.triggered.connect(ask_user_for_link)
mw.edit_cambridge_submenu.addAction(mw.create_notes_from_link_action)
