##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Sourcecode checker, to be used in unittests (by agroszer)

$Id: __init__.py 5622 2025-08-26 11:37:23Z roger.ineichen $
"""

from __future__ import absolute_import
from __future__ import print_function

from builtins import str
from builtins import object
import os.path
import sys

try:
    from codecs import open as fOpen
except ImportError:
    from io import open as fOpen

from p01.checker.checker import AlertChecker
from p01.checker.checker import BadI18nDomainChecker
from p01.checker.checker import BreakPointChecker
from p01.checker.checker import CSSChecker
from p01.checker.checker import CSSLintChecker
from p01.checker.checker import ConsoleLogChecker
from p01.checker.checker import JPGChecker
from p01.checker.checker import NonASCIIChecker
from p01.checker.checker import OpenInBrowserChecker
from p01.checker.checker import PNGChecker
from p01.checker.checker import POChecker
from p01.checker.checker import PTBadI18nDomainChecker
from p01.checker.checker import PTMissingDomainChecker
from p01.checker.checker import PTXHTMLChecker
from p01.checker.checker import PYFlakesChecker
from p01.checker.checker import TabChecker
from p01.checker.checker import ZCMLBadI18nDomainChecker


PY2 = sys.version_info[0] == 2
if PY2:
    string_types = (str, unicode)  # p01.checker.silence
else:
    string_types = (str,)


###############################################################################
#
# p01.checker.silence
#
# p01.checker.silence is not a variable, it's just a hint that you can
# silence output given from Checker classes. Just add the following
# comment behind a line of code if you like to
# skip checker alerts:
#
# import pdb;pdb.set_trace() # p01.checker.silence
#
# for HTML, javascript and page templates, you can use the phrase
# p01.checker.silence in the same line as the error message will get
# reported e.g.
#
# <!-- p01.checker.silence -->
#
# or
#
# // p01.checker.silence
#


###############################################################################
#
# p01.checker.ignore
#
# This line somewhere in a file will force to ignore checking the file at all
#


PY_CHECKERS = {
    'TabChecker': TabChecker(),
    'NonASCIIChecker': NonASCIIChecker(),
    'BreakPointChecker': BreakPointChecker(),
    'OpenInBrowserChecker': OpenInBrowserChecker(),
    'PYFlakesChecker': PYFlakesChecker(),
}
PT_CHECKERS = {
    'TabChecker': TabChecker(),
    'NonASCIIChecker': NonASCIIChecker(),
    'ConsoleLogChecker': ConsoleLogChecker(),
    'AlertChecker': AlertChecker(),
    # see checker.txt for how to add a page template domain checker
    #PTBadI18nDomainChecker('/p01/', ('p01',)),
    'PTXHTMLChecker': PTXHTMLChecker(),
    'PTMissingDomainChecker': PTMissingDomainChecker(),
}
JS_CHECKERS = {
    'TabChecker': TabChecker(),
    'ConsoleLogChecker': ConsoleLogChecker(),
    'AlertChecker': AlertChecker(),
}
CSS_CHECKERS = {
    # CSSChecker does not really produce usefull output, every second style
    # get reported as wrong e.g. -moz-border-radius, zoom, -ms-box-sizing
    #CSSChecker(),
    'CSSLintChecker': CSSLintChecker(),
    'NonASCIIChecker': NonASCIIChecker(),
}
TXT_CHECKERS = {
    'TabChecker': TabChecker(),
    'BreakPointChecker': BreakPointChecker(),
    'OpenInBrowserChecker': OpenInBrowserChecker(),
}
PO_CHECKERS = {
    'POChecker': POChecker(),
}
JPG_CHECKERS = {
    'JPGChecker': JPGChecker(),
}
PNG_CHECKERS = {
    'PNGChecker': PNGChecker(),
}
ZCML_CHECKERS = {
    # see checker.txt for how to add a zcml domain checker
    #ZCMLBadI18nDomainChecker('/p01/', ('p01',)),
}

CHECKERS = {
    'css': CSS_CHECKERS,
    'html': PT_CHECKERS,
    'jpg': JPG_CHECKERS,
    'png': PNG_CHECKERS,
    'js': JS_CHECKERS,
    'po': PO_CHECKERS,
    'pt': PT_CHECKERS,
    'py': PY_CHECKERS,
    'txt': TXT_CHECKERS,
    'zcml': ZCML_CHECKERS,
}


def replaceUnicode(txt):
    if isinstance(txt, bytes):
        return txt.decode('utf-8', 'replace')
    return txt

def sortErrors(error):
    return error.get('idx', 0)

class Checker(object):
    """Checker implementation"""

    intend = '      '
    intro = False
    filename = None
    basename = None

    def __init__(self, checkers=CHECKERS, intend=None):
        self.checkers = checkers
        if intend is not None:
            self.intend = intend

    def addChecker(self, ext, checker):
        """Add custom checker for given file name extension

        This is usefull for simply add a checker with a custom setup
        """
        checkers = self.checkers.setdefault(ext, {})
        checkers[checker.__class__.__name__] = checker

    def removeChecker(self, ext, name):
        """Remove checker for given file name extension"""
        checkers = self.checkers.get(ext, {})
        if name in checkers:
            del checkers[name]

    def start(self, basename, filename):
        """Log file intro"""
        # always slash please
        filename = filename.replace('\\','/')
        filename = filename[len(basename)+1:]
        print(('-'* (len(filename))))
        print(filename)
        print(('-'* (len(filename))))

    def log(self, data):
        idx = data.get('idx')
        line = data.get('line')
        pos = data.get('pos')
        error = data.get('error')

        # print(line no and error msg)
        if not idx:
            idx = '0: '
        else:
            idx = str(idx+1)+': '
        print(("%s%s" % (idx, error)))

        if line:
            # calculate strip lenght
            l = len(line)
            line = line.strip()
            skip = l - len(line)
            # print(line)
            for l in line.splitlines():
                print(("%s%s" % (self.intend, replaceUnicode(l).strip())))
                # print("%s%s" % (self.intend, l.strip()))
            # optional mark position
            if pos is not None and pos -skip <= len(line):
                print(("%s%s^" % (self.intend, ' '*(pos -skip))))

    def summary(self, basename, filename, errors=[]):
        """Report errors per file"""
        if len(errors):
            self.start(basename, filename)
            for data in sorted(errors, key=sortErrors):
                # log data per checker
                self.log(data)

    def check(self, module, skipFileNames=[], skipCheckerFileNames={},
        skipFolderNames=[]):
        """Thread save checker method"""
        basename = os.path.dirname(module.__file__)
        for root, dirs, files in os.walk(basename, topdown=True):
            # keep the name order
            dirs.sort()
            files.sort()

            # remove skipped folders from walk list
            for dname in skipFolderNames:
                if dname in dirs:
                    dirs.remove(dname)

            for name in files:
                if not name in skipFileNames:
                    errors = []
                    append = errors.append
                    justname, ext = os.path.splitext(name)
                    filename = os.path.join(root, name)
                    ext = ext.replace('.','')
                    checkers = self.checkers.get(ext)
                    if checkers:
                        # read file once, pass the content to checkers
                        mode = 'r'
                        encoding = 'utf-8'
                        if ext in ['jpg', 'jpeg', 'png']:
                            encoding = None
                            mode = 'rb'
                        with fOpen(filename, mode, encoding=encoding) as f:
                            content = f.read()
                            if isinstance(content, string_types) and \
                                'p01.checker.ignore' in content:
                                # ignore this file
                                continue

                        lines = content.splitlines()
                        for checker in list(checkers.values()):
                            if not name in skipCheckerFileNames.get(ext, []):
                                for data in checker.check(basename, filename,
                                    content, lines):
                                    append(data)

                    # report found errors per file
                    self.summary(basename, filename, errors)
