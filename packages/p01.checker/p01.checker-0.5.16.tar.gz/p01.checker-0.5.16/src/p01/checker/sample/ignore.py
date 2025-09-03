##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Sample module which get ignored from checking

$Id: ignore.py 5170 2025-03-06 00:12:58Z felipe.souza $
"""

# p01.checker.ignore


from __future__ import absolute_import
from builtins import object
class Foo(object):
    """A sample class forcing pyflake troubles"""

    def undefined_name(self):
        foo = False
        return bar

    def non_ascii(self):
        return u'ö'
