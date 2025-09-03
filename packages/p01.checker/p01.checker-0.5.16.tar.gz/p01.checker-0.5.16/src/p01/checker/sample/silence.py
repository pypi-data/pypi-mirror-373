##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Sample module supporting p01.checker.silence

$Id: silence.py 5170 2025-03-06 00:12:58Z felipe.souza $
"""

from __future__ import absolute_import
from builtins import object
class Foo(object):
    """A sample class forcing pyflake troubles"""

    def undefined_name(self):
        foo = False
        return bar

    def non_ascii_silence(self):
        return u'ö' # p01.checker.silence

    def non_ascii(self):
        return u'ö'
