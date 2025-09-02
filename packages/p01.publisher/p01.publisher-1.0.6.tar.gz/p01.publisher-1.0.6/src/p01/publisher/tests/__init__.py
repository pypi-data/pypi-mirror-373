# make a package

from __future__ import absolute_import
import re

from zope.testing import renormalizing

from p01.publisher._compat import PYTHON2


if PYTHON2:
    rules = [(re.compile("b('.*?')"), r"\1"),
             (re.compile('b(".*?")'), r"\1"),
            ]
    output_checker = renormalizing.RENormalizing(rules)
else:
    rules = [(re.compile("u('.*?')"), r"\1"),
             (re.compile('u(".*?")'), r"\1"),
             (re.compile("b('.*?')"), r"\1"),
             (re.compile('b(".*?")'), r"\1"),
            ]
    output_checker = renormalizing.RENormalizing(rules)
