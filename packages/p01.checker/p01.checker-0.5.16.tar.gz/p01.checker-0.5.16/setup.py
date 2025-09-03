##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""setup

"""
from __future__ import absolute_import
__docformat__ = "reStructuredText"

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup (
    name='p01.checker',
    version='0.5.16',
    author = "Adam Groszer, Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "Python, ZCML, PT, HTML, JS, CSS source checking/linting",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "Zope3 z3c p01 checker pyflakes lint",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/p01.checker',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require = dict(
        test = [
            'zope.testing',
            ],
        cssutils = [
            'cssutils',
            ],
        ),
    install_requires = [
        'setuptools',
        'polib',
        'pyflakes',
        'lxml',
        'six',
        ],
    zip_safe = False,
    )
