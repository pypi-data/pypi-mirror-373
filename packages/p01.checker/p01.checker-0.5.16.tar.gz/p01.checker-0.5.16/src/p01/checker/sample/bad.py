
from __future__ import absolute_import
from builtins import object
class Foo(object):
    """A sample class forcing pyflake troubles"""

    def pdb_import(self):
        import pdb; pdb.set_trace()
        return True

    def pdb_import2(self):
        import pdb;
        pdb.set_trace()
        return True

    def pdb_import_non_reporting(self):
        import pdb;
        pdb.set_trace() # p01.checker.silence
        return True

    def dbgpclient_import(self):
        from pub.dbgpclient import brk
        brk('127.0.0.1')
        return True

    def undefined_name(self):
        foo = False
        return bar

    def non_ascii(self):
        return u'ö'
