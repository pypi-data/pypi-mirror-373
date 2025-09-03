###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Source code checker, to be used in unittests (original written by agroszer)

$Id: checker.py 5660 2025-09-02 12:49:03Z roger.ineichen $
"""

from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object

import re
import sys
import os
import os.path
import zlib
import string
import logging
import polib
import lxml.etree
import subprocess
try:
    from io import StringIO
    from io import BytesIO
    from codecs import open as fOpen
except ImportError:
    from io import StringIO
    from io import BytesIO
    from io import open as fOpen

try:
    unicode             # p01.checker.silence
    basestring          # p01.checker.silence
except Exception:
    unicode = str       # p01.checker.silence
    basestring = str    # p01.checker.silence

PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode                   # p01.checker.silence
    string_types = (basestring, unicode)  # p01.checker.silence
else:
    text_type = str
    string_types = (str,)

import lxml.etree

from p01.checker.pyflakes import checkPYFlakes


###############################################################################
#
# checker classes
#
###############################################################################

class BaseChecker(object):
    """Checker base class"""

    error = None

    def log(self, idx, line=None, pos=None, error=None):
        if error is None:
            error = self.error
        return {
            'checker': self,
            'error': error,
            'idx': idx,
            'line': line,
            'pos': pos,
            }

    def check(self, basename, filename, content, lines):
        return


class TabChecker(BaseChecker):
    """Text tabulator checker"""

    error = 'tab found in file'

    def check(self, basename, filename, content, lines):
        for idx, line in enumerate(lines):
            if '\t' in line:
                yield self.log(idx, line)


VALIDCHARS = string.printable


def replaceUnicode(line):
    try:
        return line.encode('utf-8', 'replace')
    except UnicodeEncodeError:
        return line

class NonASCIIChecker(BaseChecker):
    """Non ascii text checker"""

    error = "non ASCII char found"

    def check(self, basename, filename, content, lines):
        for idx, line in enumerate(lines):
            for cidx, c in enumerate(line):
                if c not in VALIDCHARS and not 'p01.checker.silence' in line:
                    yield self.log(idx, replaceUnicode(line), cidx)
                    break


class BreakPointChecker(BaseChecker):
    """Debug break point checker"""

    error = 'debug break point found'
    parts = ['pdb.set_trace', 'from pub.dbgpclient import brk'] # p01.checker.silence

    def check(self, basename, filename, content, lines):
        for part in self.parts:
            for idx, line in enumerate(lines):
                if part in line \
                    and not (-1 < line.find('#') < line.find(part)) \
                    and not '# p01.checker.silence' in line:
                    line = '%s # p01.checker.silence' % line
                    yield self.log(idx, line)


class OpenInBrowserChecker(BaseChecker):
    """Open in browser method checker"""

    error = 'openInBrowser found'

    def check(self, basename, filename, content, lines):
        key = '.open' + 'InBrowser'
        for idx, line in enumerate(lines):
            if (key in line
                and not (-1 < line.find('#') < line.find(key))):
                yield self.log(idx, line)


class PYFlakesChecker(BaseChecker):
    """Pyflakes checker"""

    error = 'pyflakes warning'

    def fixcontent(self, lines):
        #pyflakes does not like CRLF linefeeds
        #and files ending with comments
        idx = len(lines)-1
        lastline = lines[idx].strip()
        while idx >= 1 and (lastline == '' or lastline.startswith('#')):
            del lines[idx]
            idx -= 1
            lastline = lines[idx].strip()

        content = '\n'.join(lines)
        return content

    def check(self, basename, filename, content, lines):
        if "##skip pyflakes##" in content:
            return
        content = self.fixcontent(lines)
        try:
            result = checkPYFlakes(content, filename)
        except Exception as e:
            result = "Fatal PyFlakes exception: %s" % e

        if isinstance(result, string_types):
            #something fatal occurred
            self.error = result
            self.log(0)
        else:
            # there are messages
            for warning in result:
                if isinstance(warning, string_types):
                    yield self.log(warning, 0)
                elif ('undefined name' in warning.message
                    and not 'unable to detect undefined names' in warning.message):
                    self.error = warning.message % warning.message_args
                    line = lines[warning.lineno-1]
                    if isinstance(line, string_types) and not \
                        'p01.checker.silence' in line:
                        yield self.log(warning.lineno-1, line)


class ConsoleLogChecker(BaseChecker):
    """Javascript console log checker"""

    error = 'javascript console.log found'

    def check(self, basename, filename, content, lines):
        for idx, line in enumerate(lines):
            if 'console.log' in line \
                and not (-1 < line.find('//') < line.find('console.log')) \
                and not 'p01.checker.silence' in line:
                yield self.log(idx, line)


class AlertChecker(BaseChecker):
    """Javascript alert checker"""

    error = 'javascript alert found'

    def check(self, basename, filename, content, lines):
        for idx, line in enumerate(lines):
            if 'alert(' in line \
                and not (-1 < line.find('//') < line.find('alert(')) \
                and not 'p01.checker.silence' in line:
                yield self.log(idx, line)


class CSSLogger(object):
    # this is a fake logger that redirects the actual logging calls to us

    errors = []

    def __init__(self):
        self.errors = []

    def noop(self, *args, **kw):
        pass

    debug = noop
    info = noop
    setLevel = noop
    getEffectiveLevel = noop
    addHandler = noop
    removeHandler = noop

    def error(self, msg):
        try:
            error = str(msg)
        except UnicodeEncodeError:
            error = msg.encode('ascii', 'replace')
        error = error.strip()
        # can't add much help, all info is encoded in msg
        self.errors.append((0, None, None, error))

    warn = error
    critical = error
    fatal = error


class CSSChecker(BaseChecker):
    """CSS checker based on cssutils with lazy import

    NOTE: you must inlcude cssutils extras_require in your buildout with:

    p01.checker [csstuils]

    for include the cssutils dependencies. Otherwise we don't depend on
    cssutils
    """

    error = 'CSS'

    def check(self, basename, filename, content, lines):
        logger = CSSLogger()
        import cssutils.parse
        parser = cssutils.parse.CSSParser(log=logger, loglevel=logging.INFO,
            validate=True)
        parser.parseString(content)
        for idx, line, pos, error in logger.errors:
            yield self.log(idx, line, pos, error)


CSS_LINT_ALL_RULES = [
    'adjoining-classes',
    'box-model',
    'box-sizing',
    'compatible-vendor-prefixes',
    'display-property-grouping',
    'duplicate-background-images',
    'duplicate-properties',
    'empty-rules',
    'errors',
    'fallback-colors',
    'floats',
    'font-faces',
    'font-sizes',
    'gradients',
    'ids',
    'import',
    'important',
    'known-properties',
    'outline-none',
    'overqualified-elements',
    'qualified-headings',
    'regex-selectors',
    'rules-count',
    'shorthand',
    'star-property-hack',
    'text-indent',
    'underscore-property-hack',
    'unique-headings',
    'universal-selector',
    'unqualified-attributes',
    'vendor-prefix',
    'zero-units',
    ]

CSS_LINT_ERROR_RULES = [
    'empty-rules',
    'errors',
    'known-properties',
]


class CSSLintChecker(BaseChecker):
    """CSSLint checker based on rhino and css lint.

    See: https://github.com/stubbornella/csslint/wiki/Command-line-interface

    The css lint checker can get used with the following command line options:

    ge: csslint [options]* [file|dir]*

    Global Options
      --help                    Displays this information.
      --format=<format>         Indicate which format to use for output.
      --list-rules              Outputs all of the rules available.
      --quiet                   Only output when errors are present.
      --errors=<rule[,rule]+>   Indicate which rules to include as errors.
      --warnings=<rule[,rule]+> Indicate which rules to include as warnings.
      --ignore=<rule,[,rule]+>  Indicate which rules to ignore completely.
      --version                 Outputs the current version number.

    The output format from csslint with the --format=checkstyle-xml looks like:

    <?xml version="1.0" encoding="utf-8"?>
    <checkstyle>
      <file name="...\\p01.checker\\src\\p01\\checker\\sample\\bad.css">
        <error
            line="9"
            column="1"
            severity="warning"
            message="Element (div.bad_width) is overqualified, just use
                     .bad_width without element name."
            source="net.csslint.Disallowoverqualifiedelements"/>
        <error
            line="13"
            column="1"
            severity="warning"
            message="Element (div.missing_coma) is overqualified, just use
                     .missing_coma without element name."
            source="net.csslint.Disallowoverqualifiedelements"/>
        <error
            line="14"
            column="5"
            severity="warning"
            message="Expected end of value but found 'height'."
            source="net.csslint.Requireuseofknownproperties"/>
        <error
            line="15"
            column="11"
            severity="error"
            message="Expected RBRACE at line 15, col 11."
            source="net.csslint.ParsingErrors"/>
        <error
            line="19"
            column="1"
            severity="warning" message="Element (div.bad_value) is
                      overqualified, just use .bad_value without element name."
            source="net.csslint.Disallowoverqualifiedelements"/>
        <error
            line="20"
            column="5"
            severity="warning"
            message="Expected (&lt;absolute-size&gt; | &lt;relative-size&gt; |
                     &lt;length&gt; | &lt;percentage&gt; | inherit) but found
                     'inline-block'."
            source="net.csslint.Requireuseofknownproperties"/>
        <error
            line="26"
            column="1"
            severity="error"
            message="Expected LBRACE at line 26, col 1."
            source="net.csslint.ParsingErrors"/>
      </file>
    </checkstyle>

    available rules:

        adjoining-classes
          Don't use adjoining classes.

        box-model
          Don't use width or height when using padding or border.

        box-sizing
          The box-sizing properties isn't supported in IE6 and IE7.

        compatible-vendor-prefixes
          Include all compatible vendor prefixes to reach a wider range of users.

        display-property-grouping
          Certain properties shouldn't be used with certain display property values.

        duplicate-background-images
          Every background-image should be unique. Use a common class for e.g. sprites.

        duplicate-properties
          Duplicate properties must appear one after the other.

        empty-rules
          Rules without any properties specified should be removed.

        errors
          This rule looks for recoverable syntax errors.

        fallback-colors
          For older browsers that don't support RGBA, HSL, or HSLA, provide a fallback color.

        floats
          This rule tests if the float property is used too many times

        font-faces
          Too many different web fonts in the same stylesheet.

        font-sizes
          Checks the number of font-size declarations.

        gradients
          When using a vendor-prefixed gradient, make sure to use them all.

        ids
          Selectors should not contain IDs.

        import
          Don't use @import, use <link> instead.

        important
          Be careful when using !important declaration

        known-properties
          Properties should be known (listed in CSS3 specification) or be a vendor-prefixed property.

        outline-none
          Use of outline: none or outline: 0 should be limited to :focus rules.

        overqualified-elements
          Don't use classes or IDs with elements (a.foo or a#foo).

        qualified-headings
          Headings should not be qualified (namespaced).

        regex-selectors
          Selectors that look like regular expressions are slow and should be avoided.

        rules-count
          Track how many rules there are.

        shorthand
          Use shorthand properties where possible.

        star-property-hack
          Checks for the star property hack (targets IE6/7)

        text-indent
          Checks for text indent less than -99px

        underscore-property-hack
          Checks for the underscore property hack (targets IE6)

        unique-headings
          Headings should be defined only once.

        universal-selector
          The universal selector (*) is known to be slow.

        unqualified-attributes
          Unqualified attribute selectors are known to be slow.

        vendor-prefix
          When using a vendor-prefixed property, make sure to include the standard one.

        zero-units
          You don't need to specify units when a value is 0.

    """

    _rules = []
    error = 'CSSLint'

    def __init__(self, rules=None):
        # indicate which rules to include in check
        self._rules = []
        if rules is None:
            rules = CSS_LINT_ALL_RULES
        self.rules = CSS_LINT_ERROR_RULES

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, values):
        self._rules = values
        # remove given rules from ignore rules
        ignore = list(CSS_LINT_ALL_RULES)
        for rule in values:
            # remove rule from ignore
            ignore.remove(rule)
        self.ignore = ignore

    def check(self, basename, filename, content, lines):
        """Process css lint command

        java -jar js.jar csslint-rhino.js --format=lint-xml path/to/file.css

        """
        here = os.path.dirname(__file__)
        lintDir = os.path.join(here, 'csslint')
        os.chdir(lintDir)

        # setup java options and friends
        JAVA_HOME = os.environ.get('JAVA_HOME')
        if JAVA_HOME is not None and os.path.exists(JAVA_HOME):
            JAVA_BIN = os.path.join(JAVA_HOME, 'bin', 'java')
        else:
            JAVA_BIN = 'java'
        cmd = [
            JAVA_BIN,
            "-jar",
            "js.jar",
            "csslint-rhino.js",
            "--format=checkstyle-xml",
        ]
        if self.rules is not None:
            if isinstance(self.rules, (list, tuple)):
                rules = ','.join(self.rules)
            else:
                rules = self.rules
            cmd += ['--errors=%s' % rules]
        if self.ignore is not None:
            if isinstance(self.ignore, (list, tuple)):
                ignore = ','.join(self.ignore)
            else:
                ignore = self.ignore
            cmd += ['--ignore=%s' % ignore]
        # append filename
        cmd += [filename]

        try:
            pro = subprocess.Popen(cmd, cwd=lintDir, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = pro.communicate()
            code = pro.returncode
            if stderr:
                code = 1
        except Exception as e:
            raise Exception("CSSLint subprocess error: %s" % e)

        # setup lines for report them later
        idx = 0
        code = {}
        #f = open(filename, 'rb')
        # f = open(filename, 'rb')
        # for line in f:
        #     code[idx] = line
        #     idx += 1
        # f.close()
        with fOpen(filename, 'r', encoding='utf-8') as f:
            for line in f:
                code[idx] = line
                idx += 1

        # parse checkstyle xml
        etree = lxml.etree.fromstring(stdout,
            parser=lxml.etree.XMLParser(resolve_entities=False))

        for issue in etree.xpath('//checkstyle/file/error'):
            idx = issue.get('line')
            try:
                idx = int(idx) -1
                line = code.get(idx)
            except (TypeError, ValueError):
                idx = 0
                line = None
            error = issue.get('message')
            yield self.log(idx, line, None, error)


class ImageChecker(BaseChecker):
    """Image compression checker"""

    error = 'image bloat found'

    def check(self, basename, filename, content, lines):
        
        if b"ns.adobe.com" in content:
            yield self.log(0, "Adobe Photoshop bloat found")
            return

        if b"<rdf:RDF" in content:
            yield self.log(0, "RDF bloat found")
            return

        if len(content) < 500:
            return

        compressed = zlib.compress(content)
        #compressed = zlib.compress(content)
        ratio = len(compressed) / float(len(content)-200)
        #200= circa static header length

        if ratio < 0.8:
            line = "Some other bloat found, compression ratio: %s" %ratio
            yield self.log(0, line)


class JPGChecker(ImageChecker):
    """JPG image compression checker"""


class PNGChecker(ImageChecker):
    """PNG image compression checker"""


class POChecker(BaseChecker):
    """PO fuzzy counter checker"""

    error = 'fuzzy/untranslated found'

    def check(self, basename, filename, content, lines):
        pos = polib.pofile(filename)
        untrans = pos.untranslated_entries()
        fuzzy = pos.fuzzy_entries()

        if len(untrans) > 0:
            error = 'untranslated found'
            line = "%s items" % len(untrans)
            yield self.log(0, line, None, error)

        if len(fuzzy) > 0:
            error = 'fuzzy found'
            line = "%s items" % len(fuzzy)
            yield self.log(0, line, None, error)


class BadI18nDomainChecker(BaseChecker):
    """Bad i18n domain checker"""

    error = 'bad i18n domain found'

    def __init__(self, pattern, pathPart, domains=()):
        self.pattern = pattern
        self.pathPart = pathPart
        self.domains = domains

    def check(self, basename, filename, content, lines):
        # make it linux-ish
        error = self.error
        filename = filename.replace('\\', '/')

        if self.pathPart in filename:
            for idx, line in enumerate(lines):
                if 'i18n:domain=""' in line:
                    error = 'empty i18n:domain="" found'
                    yield self.log(idx, line, None, error)
                if 'i18n_domain=""' in line:
                    error = 'empty i18n_domain="" found'
                    yield self.log(idx, line, None, error)
                if self.pattern.search(content):
                    for fdomain in self.pattern.findall(line):
                        if fdomain == '' or fdomain not in self.domains:
                            error = 'bad i18n domain found'
                            yield self.log(idx, line, None, error)


class ZCMLBadI18nDomainChecker(BadI18nDomainChecker):
    """Bad zcml i18n domain checker"""

    def __init__(self, pathPart, domains=()):
        pattern = re.compile(r'domain="(\w+)"')
        super(ZCMLBadI18nDomainChecker, self).__init__(pattern, pathPart,
            domains)


class PTBadI18nDomainChecker(BadI18nDomainChecker):
    """Bad pt i18n domain checker"""

    def __init__(self, pathPart, domains=()):
        pattern = re.compile(r'i18n:domain="(\w+)"')
        super(PTBadI18nDomainChecker, self).__init__(pattern, pathPart, domains)


HTML_WRAPPER = """
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:metal="http://xml.zope.org/namespaces/metal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n">
  %s
</html>

"""


class PTMissingDomainChecker(BaseChecker):
    """Missing i18n:domain checker"""

    def reprElement(self, ele):
        res = lxml.etree.tostring(ele)
        res = res.replace(b' xmlns="http://www.w3.org/1999/xhtml"', b'')
        res = res.replace(b' xmlns:tal="http://xml.zope.org/namespaces/tal"', b'')
        res = res.replace(b' xmlns:i18n="http://xml.zope.org/namespaces/i18n"', b'')
        res = res.replace(b' xmlns:metal="http://xml.zope.org/namespaces/metal"', b'')
        return res

    def checkDomain(self, ele):
        dKey = '{http://xml.zope.org/namespaces/i18n}domain'
        while ele is not None:
            if ele.attrib.get(dKey) is not None:
                return True
            ele = ele.getparent()
        return False

    def check(self, basename, filename, content, lines):
        if not 'i18n:translate' in content:
            # no translation
            return

        # checks for i18n:translate and find i18n:domain in parent elements
        # if no domain get found report line and element content
        lineCorrector = 0
        if not (content.startswith('<html') or \
                content.startswith('<!DOCTYPE') or \
                content.startswith('<!doctype') or \
                content.startswith('<?xml')):
            content = HTML_WRAPPER % content
            lineCorrector = 6
        sc = BytesIO(content.encode('utf-8'))
        try:
            for event, element in lxml.etree.iterparse(sc):
                # check if we have an i18n:translate without a i18n:domain
                # parent
                if '{http://xml.zope.org/namespaces/i18n}translate' in element.attrib:
                    # find i18n:domain in parent elements
                    if not self.checkDomain(element):
                        idx = element.sourceline - lineCorrector
                        line = self.reprElement(element)
                        error = "needs i18n:domain"
                        yield self.log(idx, line, None, error)
        except lxml.etree.XMLSyntaxError as e:
            # we do not validate XML in this check, see PTXHTMLChecker
            pass

class PTXHTMLChecker(BaseChecker):
    """Chameleon template checker

    Chameleon defines the following namespaces by default:

    xmlns:tal="http://xml.zope.org/namespaces/tal"
    xmlns:metal="http://xml.zope.org/namespaces/metal"
    xmlns:i18n="http://xml.zope.org/namespaces/i18n"

    This means the document does not have to define them. We will wrap the
    content with this namespaces if the document does not start with <html
    or <!DOCTYPE.

    """
    allowedErrorMassageStarts = [
        # umlaut
        "Entity 'Auml' not defined",
        "Entity 'auml' not defined",
        "Entity 'Ouml' not defined",
        "Entity 'ouml' not defined",
        "Entity 'Uuml' not defined",
        "Entity 'uuml' not defined",
        # other often used entities
        "Entity 'nbsp' not defined",
        "Entity 'ndash' not defined",
        "Entity 'raquo' not defined",
        "Entity 'times' not defined",
        # namespace prefixes
        'Namespace prefix i18n for ',
        'Namespace prefix i18n on ',
        'Namespace prefix metal for ',
        'Namespace prefix metal on ',
        'Namespace prefix tal for ',
        'Namespace prefix tal on ',
    ]

    def validateError(self, e):
        for allowed in self.allowedErrorMassageStarts:
           if e.message.startswith(allowed):
                return False
        return True

    def formatError(self, e, lineCorrector):
        eLine = e.line
        msg = e.message
        if lineCorrector:
            # adjust error line
            eLine = e.line - lineCorrector
            # probably there is a line reference in our error, adjust them
            number = re.search("line ([0-9]+)", msg)
            if number:
                orgNum = int(number.group(1))
                newNum = orgNum - lineCorrector
                orgStr = 'line %s' % orgNum
                newStr = 'line %s' % newNum
                msg = msg.replace(orgStr, newStr)
        return '%s, line: %s, block: %s' % (msg, eLine, e.column)

    def check(self, basename, filename, content, lines, enconding="utf-8"):
        error = None
        lineCorrector = 0

        if not (content.startswith('<html') or \
                content.startswith('<!DOCTYPE') or \
                content.startswith('<!doctype') or \
                content.startswith('<?xml')):
            content = HTML_WRAPPER % content
            lineCorrector = 6
        # sc = StringIO(content)
        try:
            p = lxml.etree.XMLParser()
            if isinstance(content, string_types):
                content = content.encode('utf-8')
            else:
                content = bytes(content)
            ignored = lxml.etree.XML(content, p)
        except lxml.etree.XMLSyntaxError as e:
            msg = '\n'.join(
                [self.formatError(e, lineCorrector)
                 for e in p.error_log
                 if self.validateError(e)
                 ])
            if msg:
                error = msg

        if isinstance(error, string_types):
            # something fatal occurred, use error as line
            yield self.log(None, error, None, 'fatal error')
