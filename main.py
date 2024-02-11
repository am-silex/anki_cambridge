# from PyQt6.QtGui import QIcon, QFont
# from PyQt6.QtWidgets import *

# from aqt import mw
# from aqt.utils import tooltip
# from anki.hooks import addHook

from aqt import mw
from aqt.qt import QAction, QMenu, QDialog
from aqt.utils import showInfo

from .gui import *
from ._names import *

from .Cambridge import CDDownloader


def ask_user_for_link():
    window = LinkDialogue()
    setattr(mw, LINK_DLG_NAME, window)
    r = window.exec()
    downloader = mw.cddownloader
    if r == QDialog.DialogCode.Accepted and downloader.word_data:
        sd = WordDefDialogue(downloader.word_data, downloader.word)
        sd.exec()
        sd = None


def open_main_windows_addon():
    window = AddonConfigWindow()
    window.exec()


def parse_saved_wl():
    mw.wl_pareser = WParseSavedWL()
    mw.wl_pareser.parse()


mw.edit_cambridge_submenu = QMenu(u"&Cambridge Dictionary", mw)
mw.form.menuEdit.addSeparator()
mw.form.menuEdit.addMenu(mw.edit_cambridge_submenu)
# Single word 
mw.create_notes_from_link_action = QAction(mw)
mw.create_notes_from_link_action.setText("Create new note(s) from link")
mw.create_notes_from_link_action.setToolTip("Fetch word definitions from provided link.")
mw.create_notes_from_link_action.setShortcut(CREATE_NEW_NOTES_SHORTCUT)

mw.create_notes_from_link_action.triggered.connect(ask_user_for_link)
mw.edit_cambridge_submenu.addAction(mw.create_notes_from_link_action)

# Word list - saved
mw.parse_saved_wl_action = QAction(mw)
mw.parse_saved_wl_action.setText("Fetch new words from user wordlists")
mw.parse_saved_wl_action.setToolTip("Fetch new words from user wordlists")
mw.parse_saved_wl_action.triggered.connect(parse_saved_wl)
mw.edit_cambridge_submenu.addAction(mw.parse_saved_wl_action)

# Addon settings
mw.edit_cambridge_submenu.addSeparator()
mw.open_main_windows_action = QAction(mw)
mw.open_main_windows_action.setText("Cambridge Addon")
mw.open_main_windows_action.setToolTip("Open Cambridge Addon main window.")

mw.open_main_windows_action.triggered.connect(open_main_windows_addon)
mw.edit_cambridge_submenu.addAction(mw.open_main_windows_action)

mw.cddownloader = CDDownloader()
