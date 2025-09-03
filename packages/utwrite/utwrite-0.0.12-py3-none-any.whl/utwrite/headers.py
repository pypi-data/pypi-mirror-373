r"""headers.py

File to host different headers wanted to use for the unittest test file.
Make a new header entry for your custom setup.

"""

HEADER = {}

HEADER['default'] = r"""
import sys
import os
import unittest
from utwrite.unittest_cases import *

%s
class Test_%s_AUTO(%s):
"""

HEADER['maya'] = r"""
import unittest
import sys
import os
from maya import cmds
from maya import OpenMaya
from utwrite.unittest_cases import *

%s
class Test_%s_AUTO(%s):

"""
