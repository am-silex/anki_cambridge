# This Python file uses the following encoding: utf-8
#############################################################################
##
## Copyright (C) 2019 The Qt Company Ltd.
## Contact: https://www.qt.io/licensing/
##
## This file is part of Qt for Python.
##
## $QT_BEGIN_LICENSE:LGPL$
## Commercial License Usage
## Licensees holding valid commercial Qt licenses may use this file in
## accordance with the commercial license agreement provided with the
## Software or, alternatively, in accordance with the terms contained in
## a written agreement between you and The Qt Company. For licensing terms
## and conditions see https://www.qt.io/terms-conditions. For further
## information use the contact form at https://www.qt.io/contact-us.
##
## GNU Lesser General Public License Usage
## Alternatively, this file may be used under the terms of the GNU Lesser
## General Public License version 3 as published by the Free Software
## Foundation and appearing in the file LICENSE.LGPL3 included in the
## packaging of this file. Please review the following information to
## ensure the GNU Lesser General Public License version 3 requirements
## will be met: https://www.gnu.org/licenses/lgpl-3.0.html.
##
## GNU General Public License Usage
## Alternatively, this file may be used under the terms of the GNU
## General Public License version 2.0 or (at your option) the GNU General
## Public license version 3 or any later version approved by the KDE Free
## Qt Foundation. The licenses are as published by the Free Software
## Foundation and appearing in the file LICENSE.GPL2 and LICENSE.GPL3
## included in the packaging of this file. Please review the following
## information to ensure the GNU General Public License requirements will
## be met: https://www.gnu.org/licenses/gpl-2.0.html and
## https://www.gnu.org/licenses/gpl-3.0.html.
##
## $QT_END_LICENSE$
##
#############################################################################

"""
This file contains the exact signatures for all functions in module
PySide2.QtScriptTools, except for defaults which are replaced by "...".
"""

# Module PySide2.QtScriptTools
import PySide2
from PySide2.support.signature import typing
from PySide2.support.signature.mapping import (
    Virtual, Missing, Invalid, Default, Instance)

class Object(object): pass

import shiboken2 as Shiboken
Shiboken.Object = Object

import PySide2.QtCore
import PySide2.QtWidgets
import PySide2.QtScript
import PySide2.QtScriptTools


class QScriptEngineDebugger(PySide2.QtCore.QObject):

    class DebuggerAction(object): ...
    InterruptAction          : DebuggerAction = ... # 0x0
    ContinueAction           : DebuggerAction = ... # 0x1
    StepIntoAction           : DebuggerAction = ... # 0x2
    StepOverAction           : DebuggerAction = ... # 0x3
    StepOutAction            : DebuggerAction = ... # 0x4
    RunToCursorAction        : DebuggerAction = ... # 0x5
    RunToNewScriptAction     : DebuggerAction = ... # 0x6
    ToggleBreakpointAction   : DebuggerAction = ... # 0x7
    ClearDebugOutputAction   : DebuggerAction = ... # 0x8
    ClearErrorLogAction      : DebuggerAction = ... # 0x9
    ClearConsoleAction       : DebuggerAction = ... # 0xa
    FindInScriptAction       : DebuggerAction = ... # 0xb
    FindNextInScriptAction   : DebuggerAction = ... # 0xc
    FindPreviousInScriptAction: DebuggerAction = ... # 0xd
    GoToLineAction           : DebuggerAction = ... # 0xe

    class DebuggerState(object): ...
    RunningState             : DebuggerState = ... # 0x0
    SuspendedState           : DebuggerState = ... # 0x1

    class DebuggerWidget(object): ...
    ConsoleWidget            : DebuggerWidget = ... # 0x0
    StackWidget              : DebuggerWidget = ... # 0x1
    ScriptsWidget            : DebuggerWidget = ... # 0x2
    LocalsWidget             : DebuggerWidget = ... # 0x3
    CodeWidget               : DebuggerWidget = ... # 0x4
    CodeFinderWidget         : DebuggerWidget = ... # 0x5
    BreakpointsWidget        : DebuggerWidget = ... # 0x6
    DebugOutputWidget        : DebuggerWidget = ... # 0x7
    ErrorLogWidget           : DebuggerWidget = ... # 0x8

    def __init__(self, parent:typing.Optional[PySide2.QtCore.QObject]=...): ...

    def action(self, action:PySide2.QtScriptTools.QScriptEngineDebugger.DebuggerAction) -> PySide2.QtWidgets.QAction: ...
    def attachTo(self, engine:PySide2.QtScript.QScriptEngine): ...
    def autoShowStandardWindow(self) -> bool: ...
    def createStandardMenu(self, parent:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtWidgets.QMenu: ...
    def createStandardToolBar(self, parent:typing.Optional[PySide2.QtWidgets.QWidget]=...) -> PySide2.QtWidgets.QToolBar: ...
    def setAutoShowStandardWindow(self, autoShow:bool): ...
    def standardWindow(self) -> PySide2.QtWidgets.QMainWindow: ...
    def state(self) -> PySide2.QtScriptTools.QScriptEngineDebugger.DebuggerState: ...
    def widget(self, widget:PySide2.QtScriptTools.QScriptEngineDebugger.DebuggerWidget) -> PySide2.QtWidgets.QWidget: ...

# eof
