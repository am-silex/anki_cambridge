#from PyQt5.QtGui import QIcon, QFont
#from PyQt5.QtWidgets import * 

#from aqt import mw
#from aqt.utils import tooltip
#from anki.hooks import addHook

from aqt import mw
from aqt.qt import QAction, QMenu, QDialog
from aqt.utils import showInfo

from .gui import *
from ._names import *

from .Cambridge import CDDownloader
from .utils import *

CREATE_NEW_NOTES_SHORTCUT = "Ctrl+l"

def ask_user_for_link():
    window = LinkDialogue()
    setattr(mw, LINK_DLG_NAME, window)
    r = window.exec_()
    downloader = mw.cddownloader
    if r == QDialog.Accepted and downloader.word_data:
        sd = WordDefDialogue(downloader.word_data,downloader.word)
        sd.exec_()
        sd = None

def ask_user_for_wordlist_link():
    window = WordListLinkDialogue()
    setattr(mw, LINK_DLG_NAME, window)
    r = window.exec_()
    #downloader = mw.cddownloader
    #if r == QDialog.Accepted and downloader.word_data:
    #    sd = WordDefDialogue(downloader.word_data,downloader.word)
    #    sd.exec_()
    #    sd = None
    
def open_main_windows_addon():

    window = AddonConfigWindow()
    window.exec_()

def find_notes():
    find_notes_with_picture_for_correction()

    #if hasattr(mw, LINK_DLG_NAME):
    #    addon_window = getattr(mw, LINK_DLG_NAME, None)
    #    addon_window.activateWindow()
    #    addon_window.raise_()
    #else:
    #    #config = utils.get_config()
    #    #if config:
    #        window = gui.LinkDialogue()
    #        setattr(mw, LINK_DLG_NAME, window)
    #        window.exec_()
    #    #else:
    #    #    showInfo("Unable to load config. Make sure that config.json "
    #    #             "is present and not in use by other applications")

    
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
# Word list
mw.create_notes_from_wordlist_link_action = QAction(mw)
mw.create_notes_from_wordlist_link_action.setText("Parse user wordlist from link")
mw.create_notes_from_wordlist_link_action.setToolTip("Parse whole word list from provided link.")

mw.create_notes_from_wordlist_link_action.triggered.connect(ask_user_for_wordlist_link)
mw.edit_cambridge_submenu.addAction(mw.create_notes_from_wordlist_link_action)

#Test
mw.act1 = QAction(mw)
mw.act1.setText("Find notes")
mw.act1.setToolTip("Parse whole word list from provided link.")

mw.act1.triggered.connect(find_notes)
mw.edit_cambridge_submenu.addAction(mw.act1)


# Addon settings
mw.edit_cambridge_submenu.addSeparator()
mw.open_main_windows_action = QAction(mw)
mw.open_main_windows_action.setText("Cambridge Addon")
mw.open_main_windows_action.setToolTip("Open Cambridge Addon main window.")

mw.open_main_windows_action.triggered.connect(open_main_windows_addon)
mw.edit_cambridge_submenu.addAction(mw.open_main_windows_action)

mw.cddownloader = CDDownloader()

#mw.test_create_utils = QAction(mw)
#mw.test_create_utils.setText("Test: create note (utils)")
##mw.test_create_utils.setToolTip("Fetch word definitions from provided link.")
#mw.test_create_utils.triggered.connect(create_selected_notes)
#mw.edit_cambridge_submenu.addAction(mw.test_create_utils)