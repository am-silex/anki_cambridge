# -*- mode: python ; coding: utf-8 -*-
#
# License: GNU AGPL, version 3 or later;
# http://www.gnu.org/copyleft/agpl.html

"""
Anki-2 add-on to create notes from Cambridge Dictionary 


"""

import sys
from os.path import dirname, join

sys.path.append(join(dirname(__file__), 'lib'))

__version__ = "0.0.1"

from . import main


