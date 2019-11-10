#from PyQt5.QtGui import QIcon, QFont
#from PyQt5.QtWidgets import * 

#from aqt import mw
#from aqt.utils import tooltip
#from anki.hooks import addHook

from aqt import mw
from aqt.qt import QAction, QMenu
from aqt.utils import showInfo

from . import gui
from ._names import *



def ask_user_for_link():
    window = gui.LinkDialogue()
    setattr(mw, LINK_DLG_NAME, window)
    window.exec_()
    
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

mw.create_notes_from_link_action = QAction(mw)
mw.create_notes_from_link_action.setText("Create new note(s) from link")
mw.create_notes_from_link_action.setToolTip("Fetch word definitions from provided link.")

mw.create_notes_from_link_action.triggered.connect(ask_user_for_link)
mw.edit_cambridge_submenu.addAction(mw.create_notes_from_link_action)